#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""给「班级小助手」注入界面语言切换（中文 / English）。

做什么（只加不改，尽量不动原有逻辑）：
  1. 设置面板最顶部加「🌐 界面语言」区块（中文 / English 两个按钮）——第一项
  2. 注入 i18n 引擎：
     · I18N_DICT  精确匹配字典（界面文案 → English）
     · I18N_PAT   模板规则（带变量的消息，如「已切换到…」）
     · trText/trAttr/applyLang 遍历 DOM 做替换，用 __zh 属性记住原文以便切回
     · 包装 toast / alert / confirm / prompt，让动态消息也跟随语言
  3. state.lang 持久化（存进存档，下次打开保持）

用法：
  python3 add_i18n.py <目标.html> [--dict i18n-en.json] [--check]

安全约定：
  · 只做「整段精确匹配」替换，绝不会替换学生姓名或教学数据（古诗/儿歌/词库/题库）
  · 切换回中文时从 __zh 原文恢复，保证中文界面与原来逐字一致
"""
import argparse
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

# ── 1. 设置面板：语言区块（插在设置面板第一个 h3 之前） ──
LANG_BLOCK = '''    <h3>🌐 界面语言 / Language</h3>
    <div class="srow" id="langRow">
      <button class="mini-btn lang-btn" id="langZh" data-lang="zh">🇨🇳 中文</button>
      <button class="mini-btn lang-btn" id="langEn" data-lang="en">🇬🇧 English</button>
      <span class="hint" id="langHint">切换界面语言（学生姓名、古诗、儿歌、词库等内容不翻译）</span>
    </div>
'''

LANG_CSS = '''  /* ===== 界面语言切换 ===== */
  .lang-btn{font-size:calc(15px*var(--fs)) !important;padding:calc(7px*var(--fs)) calc(18px*var(--fs)) !important;}
  .lang-btn.on{background:var(--accent);color:#fff;border-color:var(--accent);}
  #langRow{gap:calc(10px*var(--fs));flex-wrap:wrap;}

'''

# ── 2. i18n 引擎 ──
ENGINE_JS = r'''
/* ===================== 界面语言（i18n） =====================
   设计：整段精确匹配替换，绝不动学生姓名与教学数据（古诗/儿歌/词库/题库）。
   原文存在节点自定义属性 __zh 上，切回中文时逐字恢复。 */
function curLang(){ try{ return (state&&state.lang)==='en' ? 'en' : 'zh'; }catch(e){ return 'zh'; } }

var I18N_DICT = __I18N_DICT__;      /* 精确匹配：界面文案 → English */
var I18N_PAT  = __I18N_PAT__;       /* 模板规则：[正则, 替换] —— 处理带变量的消息 */

/* 翻译一整段文本（保留首尾空白） */
function trText(raw){
  if(curLang()!=='en') return raw;
  if(!raw) return raw;
  var m=raw.match(/^(\s*)([\s\S]*?)(\s*)$/);
  var lead=m[1], core=m[2], tail=m[3];
  if(!core) return raw;
  var en=I18N_DICT[core];
  if(en!==undefined) return lead+en+tail;
  /* 模板规则：支持 $1..$9（捕获组）与 $D1..$D9（捕获组再过一遍字典，用于「第1节 · 数学」→ Period 1 · Math） */
  for(var i=0;i<I18N_PAT.length;i++){
    var re=new RegExp(I18N_PAT[i][0]);
    if(re.test(core)) return lead+patApply(core, re, I18N_PAT[i][1])+tail;
  }
  return raw;
}
/* 应用一条模板规则：先生成 $Dn 的字典结果，再展开 $n */
function patApply(str, re, repl){
  try{
    return str.replace(re, function(){
      var a=arguments;
      var r=repl.replace(/\$D(\d)/g, function(_, n){
        var raw=String(a[+n]==null?'':a[+n]).trim();
        return I18N_DICT[raw]!==undefined ? I18N_DICT[raw] : raw;
      });
      return r.replace(/\$(\d)/g, function(_, n){ return a[+n]==null?'':a[+n]; });
    });
  }catch(e){ return str; }
}
function trMsg(s){
  if(curLang()!=='en') return s;
  var k=String(s==null?'':s);
  if(!k) return k;
  var exact=I18N_DICT[k.trim()];
  if(exact!==undefined) return k.replace(k.trim(), exact);
  for(var i=0;i<I18N_PAT.length;i++){
    var re=new RegExp(I18N_PAT[i][0]);
    if(re.test(k)) return patApply(k, re, I18N_PAT[i][1]);
  }
  return k;
}

/* DOM 文本节点 */
function trTextNode(node){
  var raw=node.nodeValue;
  if(raw==null || raw==='') return;
  if(curLang()==='zh'){
    if(node.__zh!==undefined){ node.nodeValue=node.__zh; delete node.__zh; }
    return;
  }
  if(!/[\u4e00-\u9fff]/.test(raw)) return;
  if(node.__zh===undefined) node.__zh=raw;
  var out=trText(node.__zh);
  if(node.nodeValue!==out) node.nodeValue=out;
}
/* 元素属性（title / placeholder） */
function trAttr(el, name){
  var raw=el.getAttribute && el.getAttribute(name);
  if(!raw) return;
  var key='__zh_'+name;
  if(curLang()==='zh'){
    if(el[key]!==undefined){ el.setAttribute(name, el[key]); delete el[key]; }
    return;
  }
  if(!/[\u4e00-\u9fff]/.test(raw)) return;
  if(el[key]===undefined) el[key]=raw;
  var out=trText(el[key]);
  if(el.getAttribute(name)!==out) el.setAttribute(name, out);
}

var _langBusy=false;
function applyLang(){
  if(_langBusy) return;          /* 防自触发 */
  _langBusy=true;
  try{
    var root=document.body;
    if(root){
      var tw=document.createTreeWalker(root, NodeFilter.SHOW_TEXT, null);
      var n, batch=[];
      while((n=tw.nextNode())){
        var p=n.parentNode;
        if(!p) continue;
        if(p.id==='tplb64' || p.tagName==='SCRIPT' || p.tagName==='STYLE') continue;
        /* 安全护栏：可编辑区域（如班级名、课表格子）不翻译 —— 否则内容会被英文覆盖 */
        if(p.isContentEditable) continue;
        var anc=p.closest && p.closest('[contenteditable="true"]');
        if(anc) continue;
        batch.push(n);
      }
      for(var i=0;i<batch.length;i++) trTextNode(batch[i]);
      var els=root.querySelectorAll('[title]');
      for(var j=0;j<els.length;j++){ if(els[j].isContentEditable) continue; trAttr(els[j],'title'); }
      var ph=root.querySelectorAll('[placeholder]');
      for(var k=0;k<ph.length;k++) trAttr(ph[k],'placeholder');
    }
  }catch(e){}
  _langBusy=false;
}
var _langTimer=null;
function applyLangSoon(){
  if(_langTimer) clearTimeout(_langTimer);
  _langTimer=setTimeout(function(){ _langTimer=null; applyLang(); }, 60);
}
/* 动态渲染（切页/加分/重建列表…）后自动补译。
   仅在英文模式下工作；只对"新增节点"或"含中文的文本变化"触发；
   翻译自身不产生含中文的新节点，所以不会自激循环。 */
var _mo=null;
function ensureObserver(){
  if(_mo || !window.MutationObserver || !document.body) return;
  try{
    _mo=new MutationObserver(function(muts){
      if(curLang()!=='en') return;
      var need=false;
      for(var i=0;i<muts.length && !need;i++){
        var m=muts[i];
        if(m.type==='characterData'){ if(/[\u4e00-\u9fff]/.test(m.target.nodeValue||'')) need=true; }
        else if(m.type==='childList' && m.addedNodes && m.addedNodes.length) need=true;
      }
      if(need) applyLangSoon();
    });
    _mo.observe(document.body,{childList:true,subtree:true,characterData:true});
  }catch(e){}
}

/* 切换语言 */
function setLang(lang){
  lang=(lang==='en')?'en':'zh';
  try{ if(state){ state.lang=lang; save(); } }catch(e){}
  applyLang();
  syncLangUI();
  try{ toast(lang==='en'?'🌐 Interface language: English':'🌐 界面语言：中文'); }catch(e){}
}
function syncLangUI(){
  var z=document.getElementById('langZh'), e=document.getElementById('langEn');
  var cur=curLang();
  if(z) z.classList.toggle('on', cur==='zh');
  if(e) e.classList.toggle('on', cur==='en');
}

/* 包装动态消息：toast / alert / confirm / prompt */
(function wrapDialogs(){
  try{
    if(typeof window.toast==='function' && !window.toast.__i18n){
      var _t=window.toast;
      var w=function(msg,ms){ return _t(typeof msg==='string'?trMsg(msg):msg, ms); };
      w.__i18n=true; window.toast=w;
    }
  }catch(e){}
  try{
    var _a=window.alert;
    window.alert=function(m){ return _a(typeof m==='string'?trMsg(m):m); };
    var _c=window.confirm;
    window.confirm=function(m){ return _c(typeof m==='string'?trMsg(m):m); };
    var _p=window.prompt;
    window.prompt=function(m,d){ return _p(typeof m==='string'?trMsg(m):m, d); };
  }catch(e){}
})();

/* 界面按钮绑定 + 启动时应用 */
(function initLang(){
  function bind(){
    var z=document.getElementById('langZh'), e=document.getElementById('langEn');
    if(z) z.addEventListener('click',function(){ setLang('zh'); });
    if(e) e.addEventListener('click',function(){ setLang('en'); });
    syncLangUI();
    applyLang();
    ensureObserver();
  }
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',function(){ setTimeout(bind,120); });
  else setTimeout(bind,120);
})();
/* 测试/自检接口 */
window.__I18N__={ apply:applyLang, set:setLang, cur:curLang, dict:I18N_DICT, pat:I18N_PAT };
'''

# ── 3. rerenderAll 后重刷语言（让动态渲染的内容也跟随） ──
RERENDER_HOOK = '''function rerenderAll(){
  renderStudents(); re'''

RERENDER_HOOK_NEW = '''function rerenderAll(){
  try{ applyLangSoon(); }catch(e){}      /* 语言：重渲染后再套一遍（动态内容） */
  renderStudents(); re'''


def main():
    ap = argparse.ArgumentParser(description='给班级小助手注入界面语言切换')
    ap.add_argument('target', help='目标 HTML')
    ap.add_argument('--dict', default=os.path.join(HERE, 'i18n-en.json'), help='英文字典 JSON')
    ap.add_argument('--pat', default=os.path.join(HERE, 'i18n-en-patterns.json'), help='模板规则 JSON')
    args = ap.parse_args()

    p = os.path.abspath(os.path.expanduser(args.target))
    if not os.path.isfile(p):
        sys.exit('找不到文件：%s' % p)
    s = io.open(p, encoding='utf-8').read()

    if 'function applyLang(' in s:
        sys.exit('该文件已经注入过语言功能（发现 applyLang）。请从未注入的版本重跑。')

    dic = json.loads(io.open(args.dict, encoding='utf-8').read()) if os.path.isfile(args.dict) else {}
    # 注意：允许单字符键（如颜色字「橙」→Orange），$Dn 嵌套翻译要用到
    items = {k: v for k, v in dic.items() if not k.startswith('_') and len(k) >= 1}
    pats = json.loads(io.open(args.pat, encoding='utf-8').read()) if os.path.isfile(args.pat) else []
    pats = [x for x in pats if isinstance(x, list) and len(x) == 2]
    # ⚠️ Python 的 re.sub 用 \1 引用捕获组，而 JS 的 String.replace 用的是 $1。
    #    配置里统一写成 Python 风格（便于维护），在这里转成 JS 风格再注入。
    pats = [[x[0], re.sub(r'\\(\d+)', r'$\1', x[1])] for x in pats]
    bad = [x for x in pats if '\\1' in x[1]]
    if bad:
        sys.exit('✗ 模板规则仍含 \\1 风格引用：%s' % bad[:2])
    print('字典 %d 条；模板 %d 条' % (len(items), len(pats)))

    # ① 设置面板：语言区块插到第一个 h3 之前
    i = s.find('id="settingsMask"')
    if i < 0:
        sys.exit('找不到设置面板 settingsMask')
    j = s.find('<h3', i)
    if j < 0:
        sys.exit('设置面板里找不到 <h3>')
    s = s[:j] + LANG_BLOCK + '    ' + s[j:]
    print('  ✔ 设置面板顶部已加「界面语言」区块')

    # ② CSS
    anchor_css = '  /* ===== 常见问题面板（就地答疑） ===== */'
    if s.count(anchor_css) != 1:
        anchor_css = '  /* ===== 设置面板（齿轮收纳所有自定义项） ===== */'
    if s.count(anchor_css) != 1:
        sys.exit('找不到 CSS 插入锚点')
    s = s.replace(anchor_css, LANG_CSS + anchor_css, 1)
    print('  ✔ CSS 已注入')

    # ③ 引擎 JS（插在最后一个 </script> 之前）
    engine = ENGINE_JS.replace('__I18N_DICT__', json.dumps(items, ensure_ascii=False, separators=(',', ':')))
    engine = engine.replace('__I18N_PAT__', json.dumps(pats, ensure_ascii=False, separators=(',', ':')))
    k = s.rfind('</script>')
    if k < 0:
        sys.exit('找不到 </script>')
    s = s[:k] + engine + '\n' + s[k:]
    print('  ✔ i18n 引擎已注入（%d 字节）' % len(engine.encode('utf-8')))

    # ④ rerenderAll 钩子
    if s.count(RERENDER_HOOK) == 1:
        s = s.replace(RERENDER_HOOK, RERENDER_HOOK_NEW, 1)
        print('  ✔ rerenderAll 已挂语言刷新')
    else:
        print('  ⚠ 未找到 rerenderAll 锚点，跳过（语言仍会在切换时立即生效）')

    io.open(p, 'w', encoding='utf-8').write(s)
    print('\n✅ 完成：%s（%.1f KB）' % (p, len(s.encode('utf-8')) / 1024))


if __name__ == '__main__':
    main()
