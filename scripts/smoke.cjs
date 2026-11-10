#!/usr/bin/env node
/* 班级小助手 / 班级管理工作台 —— 发布前冒烟闸门
 * 用法: node smoke.cjs <程序.html> [--size 3480,2160] [--out 报告.json] [--keep]
 * 退出码: 0=全绿 1=有未捕获错误或探针失败 2=只有"疑似无反应"告警
 * 三道检查: ①静态结构(语法/id/绑定-节点顺序/哑按钮) ②运行时逐按钮点击 ③设置浮层单独扫描
 */
'use strict';
const fs = require('fs');
const os = require('os');
const path = require('path');
const cp = require('child_process');

const argv = process.argv.slice(2);
const target = argv.find(a => !a.startsWith('--'));
if (!target) { console.error('用法: node smoke.cjs <程序.html> [--size WxH] [--out 报告.json] [--keep]'); process.exit(1); }
const getOpt = (name, dft) => { const i = argv.indexOf('--' + name); return i >= 0 && argv[i + 1] ? argv[i + 1] : dft; };
const SIZE = getOpt('size', '3480,2160');
const OUT = getOpt('out', '');
const KEEP = argv.includes('--keep');

const html = fs.readFileSync(target, 'utf8');
const R = { file: target, size: SIZE, at: new Date().toISOString(), static: {}, runtime: {} };
const fail = (arr, msg) => { arr.push(msg); };

/* ---------- ① 静态结构 ---------- */
const blocks = [...html.matchAll(/^<script[^>]*>(?:(?!^<\/script>)[\s\S])*^<\/script>/gm)]
  .map(m => ({ start: m.index, body: m[0].replace(/^<script[^>]*>/, '').replace(/<\/script>\s*$/, '') }));
if (!blocks.length) { console.error('未找到行首 <script> 块（本工具假定程序有两个行首脚本块）'); process.exit(1); }

// 1a 语法
R.static.syntax = [];
blocks.forEach((b, i) => {
  if (b.body.length < 200) return;
  const f = path.join(os.tmpdir(), `smoke_blk_${process.pid}_${i}.js`);
  fs.writeFileSync(f, b.body);
  const r = cp.spawnSync('node', ['--check', f], { encoding: 'utf8' });
  if (r.status !== 0) fail(R.static.syntax, `块${i} 语法错误: ` + r.stderr.split('\n').slice(0, 3).join(' | '));
  fs.unlinkSync(f);
});

// 1b 重复 id
const ids = [...html.matchAll(/(?<![-\w])id="([^"]+)"/g)].map(m => m[1]);
const dup = Object.entries(ids.reduce((a, id) => (a[id] = (a[id] || 0) + 1, a), {})).filter(([, n]) => n > 1);
R.static.duplicateIds = dup.filter(([id]) => id !== 'saveState').map(([id, n]) => `${id}×${n}`);

// 1c ★绑定早于节点：顶层 $('#x').addEventListener 引用的 id 必须在脚本块开始之前已解析出来
R.static.bindingBeforeMarkup = [];
blocks.forEach((b, bi) => {
  const markup = bi === 0 ? html.slice(0, b.start) : '';
  const markupIds = new Set([...markup.matchAll(/id="([^"]+)"/g)].map(m => m[1]));
  const before = bi === 0 ? '' : html.slice(0, blocks[bi - 1].start);
  const js = blocks.slice(0, bi).map(x => x.body).join('\n');
  const bodyLines = b.body.split('\n');
  bodyLines.forEach((line, li) => {
    if (/^\s/.test(line)) return;                       // 只看顶层（无缩进）
    const m = line.match(/\$\('#([A-Za-z0-9_-]+)'\)\s*\.(addEventListener|onclick|value\s*=|disabled\s*=|classList|style\.)/);
    if (!m) return;
    const id = m[1];
    const createdLater = new RegExp(`id="${id}"`).test(before);   // 由更早的脚本块动态生成（本项目罕见）
    if (!markupIds.has(id) && !createdLater) fail(R.static.bindingBeforeMarkup, `块${bi} 第${li + 1}行 绑定 #${id}，但该节点在脚本块开始时还不存在于 DOM → 顶层抛错会中断整块`);
  });
});

// 1d 哑按钮（静态：JS 里从未引用）
const jsAll = blocks.map(b => b.body).join('\n');
const btnIds = [...html.matchAll(/<button[^>]*?(?<![-\w])id="([^"]+)"/g)].map(m => m[1]);
R.static.dumbButtons = btnIds.filter(id => jsAll.indexOf('#' + id) < 0 && jsAll.indexOf(`'${id}'`) < 0 && jsAll.indexOf(`"${id}"`) < 0);
R.static.buttonTotal = btnIds.length;

/* ---------- ② 运行时 ---------- */
const browser = ['/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge',
  '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  '/Applications/Chromium.app/Contents/MacOS/Chromium'].find(p => fs.existsSync(p));
if (!browser) { console.error('未找到 Edge/Chrome/Chromium，无法跑运行时检查'); process.exit(1); }

const PROBE = String.raw`
(function(){
  var TAB_DESTRUCTIVE = {fullReset:1, scoreReset:1, dutyReset:1, rosterApply:1, todayReset:1, pkToPerson:1, wordsReset:1, mathReset:1};
  function q(s){return document.querySelector(s);}
  function sleep(ms){return new Promise(function(r){setTimeout(r,ms);});}
  function vis(el){ var r=el.getBoundingClientRect(); return r.width>0&&r.height>0&&getComputedStyle(el).visibility!=='hidden'; }
  var toasts=[];
  function hash(t){ var h=2166136261; for(var i=0;i<t.length;i+=7){ h^=t.charCodeAt(i); h=Math.imul(h,16777619); } return (h>>>0).toString(36); }
  function fp(root){
    var sz; try{ sz=(0,eval('JSON.stringify(state)').length); }catch(e){ sz=-1; }
    return [ (q('section.tab.active')||{}).id||'', sz, toasts.length+'|'+(toasts[toasts.length-1]||''),
             document.querySelectorAll('.show').length,
             document.querySelectorAll('[class~="on"],[class~="sel"],[class~="active"]').length,
             root?hash(root.innerHTML):-1, window.__P, window.__C, (window.__DL||[]).length ].join('#');
  }
  var errs=window.__ERRS||(window.__ERRS=[]), dead=[], clicked=0, skipped=[], errored=[];
  function snap(){ try{ window.__SNAP=(0,eval('JSON.stringify(state)')); }catch(e){} }
  function restore(){ try{ (0,eval)('state=JSON.parse(window.__SNAP)'); (0,eval)('rerenderAll()'); }catch(e){} }
  function tap(b, root, tag){
    var id=b.id||'', nm=(b.textContent||'').trim().slice(0,12);
    if(TAB_DESTRUCTIVE[id]){ skipped.push(tag+':'+id); }
    var f0=fp(root), e0=errs.length;
    clicked++;
    try{ b.click(); }catch(e){ errs.push('Uncaught click '+id+' -> '+e.message); }
    return new Promise(function(res){ setTimeout(function(){
      if(errs.length>e0) errored.push(tag+':'+id+' '+(errs[errs.length-1]||'').slice(0,60));
      else if(fp(root)===f0) dead.push(tag+':'+id+(nm?' «'+nm+'»':''));
      if(TAB_DESTRUCTIVE[id]) restore();
      res();
    },70); });
  }
  async function run(){
    var _t=window.toast; window.toast=function(m){ toasts.push(String(m||'').slice(0,40)); if(_t)_t.apply(null,arguments); };
    window.__C=0; window.__P=0;
    window.confirm=function(){ window.__C++; return true; }; window.prompt=function(){ window.__P++; return null; }; window.alert=function(){};
    window.__DL=[]; var _a=HTMLAnchorElement.prototype.click;
    HTMLAnchorElement.prototype.click=function(){ window.__DL.push(this.download||'(unnamed)'); };
    var _i=HTMLInputElement.prototype.click;
    HTMLInputElement.prototype.click=function(){ if(this.type==='file'){ window.__DL.push('filepicker:'+this.id); return; } return _i.apply(this,arguments); };
    try{ var r=q('#rescueLater'); if(r) r.click(); }catch(e){}
    await sleep(150); snap();
    var out0=0; var tabs=[].slice.call(document.querySelectorAll('section.tab')).map(function(s){return s.id.replace('tab-','');});
    for(var ti=0;ti<tabs.length;ti++){
      var tn=tabs[ti];
      try{ (0,eval('switchTab'))(tn); }catch(e){ errs.push('switchTab '+tn+': '+e.message); continue; }
      await sleep(160);
      var root=document.getElementById('tab-'+tn);
      var bs=[].slice.call(root.querySelectorAll('button')).filter(vis);
      bs.sort(function(a,b){ return (TAB_DESTRUCTIVE[a.id]?1:0)-(TAB_DESTRUCTIVE[b.id]?1:0); });
      for(var bi=0;bi<bs.length;bi++){ await tap(bs[bi], root, tn); }
      [].slice.call(root.querySelectorAll('input[type=range],input[type=checkbox],select')).forEach(function(el){
        var v0=el.value, ck=el.checked;
        try{ if(el.type==='checkbox'){ el.checked=!ck; el.dispatchEvent(new Event('change',{bubbles:true})); el.checked=ck; }
             else if(el.type==='range'){ el.value=String((+el.value||0)+1); el.dispatchEvent(new Event('input',{bubbles:true})); el.value=v0; }
             else { el.selectedIndex=(el.selectedIndex+1)%Math.max(1,el.options.length); el.dispatchEvent(new Event('change',{bubbles:true})); } }
        catch(e){ errs.push('控件 '+(el.id||el.type)+': '+e.message); }
      });
      try{ (0,eval('save'))(); }catch(e){}
    }
    // 设置浮层（1e 盲区：不在 section.tab 内）
    var sm=q('#settingsMask');
    if(sm){
      try{ var g=q('#btnGear'); if(g) g.click(); else sm.classList.add('show'); }catch(e){ errs.push('openSettings: '+e.message); }
      await sleep(200);
      [].slice.call(sm.querySelectorAll('details')).forEach(function(d){ d.open=true; });
      var bs2=[].slice.call(sm.querySelectorAll('button')).filter(vis);
      for(var k=0;k<bs2.length;k++){ await tap(bs2[k], sm, 'settings'); }
      [].slice.call(sm.querySelectorAll('input[type=range],select')).forEach(function(el){
        try{ if(el.tagName==='SELECT'){ el.selectedIndex=(el.selectedIndex+1)%Math.max(1,el.options.length); el.dispatchEvent(new Event('change',{bubbles:true})); }
             else { el.value=String((+el.value||0)+1); el.dispatchEvent(new Event('input',{bubbles:true})); } }catch(e){ errs.push('设置控件 '+(el.id||'')+': '+e.message); }
      });
      try{ var c=q('#settingsClose'); if(c) c.click(); }catch(e){}
    }
    // 脚本是否真的跑到了最后一行（顶层中断的检测器）
    var probes={};
    ['renderPK','resetPK','buildExportHtml','openSettings','todayGroupRanks'].forEach(function(n){
      try{ probes[n]=(0,eval('typeof '+n)); }catch(e){ probes[n]='!defined'; }
    });
    // typeof 命中 TDZ 的 let 会抛错——抛错本身就说明"声明了但没执行到"
    try{ probes['let-rhymeCat']=(0,eval('typeof rhymeCat')); }catch(e){ probes['let-rhymeCat']='TDZ/未初始化'; }
    restore();
    report(null, probes);
  }
  function report(err, probes){
    var out={clicked:clicked, dead:dead, errored:errored, skippedDestructive:skipped,
             errors:errs, downloads:window.__DL||[], probes:probes||{},
             pageOverflow:Math.max(0,document.documentElement.scrollHeight-window.innerHeight),
             probeError:(err&&(err.message||String(err)))||''};
    if(!probes){ out.probes={};
      ['renderPK','resetPK','buildExportHtml','openSettings','todayGroupRanks'].forEach(function(n){
        try{ out.probes[n]=(0,eval('typeof '+n)); }catch(e){ out.probes[n]='!defined'; } });
      try{ out.probes['let-rhymeCat']=(0,eval('typeof rhymeCat')); }catch(e){ out.probes['let-rhymeCat']='TDZ/未初始化'; } }
    var old=document.getElementById('SMOKE'); if(old) old.remove();
    var p=document.createElement('pre'); p.id='SMOKE'; p.textContent=JSON.stringify(out);
    document.body.appendChild(p);
  }
  try{ if(document.readyState==='loading') window.addEventListener('load',function(){ run().catch(report); }); else run().catch(report); }
  catch(e){ report(e); }
})();
`;

const tmpProbe = path.join(os.tmpdir(), `smoke_${process.pid}.html`);
let doc = html;
const firstScript = doc.search(/^<script/m);
const collector = '<script>window.__ERRS=[];window.addEventListener("error",function(e){window.__ERRS.push((e.message||"?")+" @"+(e.lineno||"?")+"行");});window.addEventListener("unhandledrejection",function(e){window.__ERRS.push("Promise: "+(e.reason&&e.reason.message||e.reason));});</script>\n';
doc = doc.slice(0, firstScript) + collector + doc.slice(firstScript);
const bodyEnd = doc.lastIndexOf('</body>');
doc = doc.slice(0, bodyEnd) + '<script>' + PROBE + '</script>\n' + doc.slice(bodyEnd);
fs.writeFileSync(tmpProbe, doc);

let smoke = null;
try {
  const r = cp.spawnSync(browser, ['--headless=new', '--disable-gpu', '--no-sandbox', '--allow-file-access-from-files',
    '--hide-scrollbars', '--virtual-time-budget=120000', '--window-size=' + SIZE,
    '--dump-dom', 'file://' + tmpProbe], { encoding: 'utf8', maxBuffer: 200 * 1024 * 1024, timeout: 300000 });
  const m = /<pre id="SMOKE">([\s\S]*?)<\/pre>/.exec(r.stdout || '');
  if (m) { try { smoke = JSON.parse(m[1].replace(/&quot;/g, '"').replace(/&amp;/g, '&').replace(/&lt;/g, '<').replace(/&gt;/g, '>')); } catch (e) { smoke = null; } }
  if (!smoke) R.runtime.probeFail = '未取到探针结果（探针自身语法错误 / 预算耗尽 / 页面崩溃）。stderr: ' + (r.stderr || '').split('\n').slice(-3).join(' | ');
} finally { if (KEEP) console.log('（探针副本保留在 ' + tmpProbe + '）'); else fs.unlinkSync(tmpProbe); }
R.runtime.result = smoke;

/* ---------- 判定 ---------- */
const hard = [];
const warn = [];
if (R.static.syntax.length) hard.push('语法: ' + R.static.syntax.join('; '));
if (R.static.bindingBeforeMarkup.length) hard.push('★绑定早于节点: ' + R.static.bindingBeforeMarkup.join('; '));
if (R.static.duplicateIds.length) warn.push('重复 id: ' + R.static.duplicateIds.join(', '));
if (R.static.dumbButtons.length) warn.push('静态哑按钮: ' + R.static.dumbButtons.join(', '));
if (!smoke) hard.push(R.runtime.probeFail || '运行时探针无结果');
else {
  const errsAll = smoke.errors || [];
  const FATAL = /Uncaught|is not defined|before initialization|Cannot read|is not a function|Cannot set properties|Invalid or unexpected token|Unexpected token|is not iterable|Unexpected end of input/;
  const ENV = /Clipboard|permission denied|NotAllowedError|ResizeObserver|Network Error|Failed to fetch|favicon/i;
  const fatalErrs = errsAll.filter(e => FATAL.test(e) && !ENV.test(e));
  const otherErrs = errsAll.filter(e => !FATAL.test(e) || ENV.test(e));
  if (fatalErrs.length) hard.push('运行时未捕获错误 ' + fatalErrs.length + ' 条:\n     ' + fatalErrs.slice(0, 8).join('\n     '));
  if (otherErrs.length) warn.push('其它未捕获错误 ' + otherErrs.length + ' 条（无头沙箱权限类多为环境噪声，仍需扫一眼）:\n     ' + otherErrs.slice(0, 5).join('\n     '));
  if (smoke.probeError) hard.push('探针自身异常，结论不可信: ' + smoke.probeError);
  const tdz = Object.entries(smoke.probes || {}).filter(([k, v]) => k === 'let-rhymeCat' ? /TDZ/.test(v) : v !== 'function');
  if (tdz.length) hard.push('★脚本疑似被中断（顶层中断后后续声明不生效）: ' + tdz.map(([k, v]) => k + '=' + v).join(', '));
  if (smoke.dead.length) warn.push('点了没反应 ' + smoke.dead.length + ' 个（需人工复核，见 verification.md 1d 误报表）:\n     ' + smoke.dead.slice(0, 25).join('\n     '));
  if (!smoke.downloads.length) warn.push('导出/下载类按钮没有产出任何文件名');
}

console.log('── 冒烟报告 ── ' + target + '  @' + SIZE + '  ' + R.at);
console.log('静态: 脚本块 ' + blocks.length + ' / 按钮 ' + R.static.buttonTotal +
  ' / 绑定早于节点 ' + R.static.bindingBeforeMarkup.length + ' / 静态哑按钮 ' + R.static.dumbButtons.length);
if (smoke) console.log('运行时: 点击 ' + smoke.clicked + ' / 未捕获错误 ' + (smoke.errors || []).length +
  ' / 疑似无反应 ' + smoke.dead.length + ' / 跳过破坏性 ' + smoke.skippedDestructive.length +
  ' / 导出物 ' + smoke.downloads.length + ' / 溢出 ' + smoke.pageOverflow);
hard.forEach(h => console.log('❌ ' + h));
warn.forEach(w => console.log('⚠️  ' + w));
if (!hard.length && !warn.length) console.log('✅ 全绿');
if (OUT) fs.writeFileSync(OUT, JSON.stringify(R, null, 1));
console.log(OUT ? '详细结果已写入 ' + OUT : '');
process.exit(hard.length ? 1 : (warn.length ? 2 : 0));
