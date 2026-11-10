#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 scripts/i18n-en.json / i18n-en-patterns.json 同步进已注入 i18n 的程序里。

为什么需要：
  `add_i18n.py` 是一次性注入器（检测到 applyLang 就拒绝再跑），所以加词条时得
  **同时**改 JSON 与 HTML 里内嵌的 `var I18N_DICT = {...}` / `var I18N_PAT = [...]`。
  两处手工同步必然漏 —— 这个脚本让 JSON 成为唯一来源。

用法：
  python3 sync_i18n.py <程序.html> [<第二个.html> ...]     # 写入
  python3 sync_i18n.py <程序.html> --check                 # 只报告是否一致（闸门用）

约定：
  · 过滤规则与 add_i18n.py 完全一致（跳过 `_` 开头的注释键；模板规则 `\\1` → `$1`）
  · 只替换这两个字面量，其它内容一字不动
"""
import argparse
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def load_entries():
    dic = json.loads(io.open(os.path.join(HERE, 'i18n-en.json'), encoding='utf-8').read())
    items = {k: v for k, v in dic.items() if not k.startswith('_') and len(k) >= 1}
    pats = json.loads(io.open(os.path.join(HERE, 'i18n-en-patterns.json'), encoding='utf-8').read())
    pats = [x for x in pats if isinstance(x, list) and len(x) == 2]
    pats = [[x[0], re.sub(r'\\(\d+)', r'$\1', x[1])] for x in pats]
    bad = [x for x in pats if '\\1' in x[1]]
    if bad:
        sys.exit('✗ 模板规则仍含 \\1 风格引用：%s' % bad[:2])
    return items, pats


def literal_span(s, anchor, open_ch, close_ch):
    """返回 anchor 之后那个 JSON 字面量在 s 里的 [start, end)（字符串感知的括号配对）。"""
    i = s.find(anchor)
    if i < 0:
        return None
    j = s.index(open_ch, i)
    depth, k, in_str, esc = 0, j, False, False
    while k < len(s):
        c = s[k]
        if in_str:
            if esc:
                esc = False
            elif c == '\\':
                esc = True
            elif c == '"':
                in_str = False
        else:
            if c == '"':
                in_str = True
            elif c == open_ch:
                depth += 1
            elif c == close_ch:
                depth -= 1
                if depth == 0:
                    return (j, k + 1)
        k += 1
    sys.exit('✗ %s 的字面量括号没配平，放弃改写' % anchor.strip())


def main():
    ap = argparse.ArgumentParser(description='同步 i18n 字典到程序 HTML')
    ap.add_argument('targets', nargs='+', help='已注入 i18n 的 HTML（可多个）')
    ap.add_argument('--check', action='store_true', help='只检查一致性，不写入')
    args = ap.parse_args()

    items, pats = load_entries()
    want_d = json.dumps(items, ensure_ascii=False, separators=(',', ':'))
    want_p = json.dumps(pats, ensure_ascii=False, separators=(',', ':'))
    print('来源：i18n-en.json %d 条 / i18n-en-patterns.json %d 条' % (len(items), len(pats)))

    drift = 0
    for t in args.targets:
        p = os.path.abspath(os.path.expanduser(t))
        if not os.path.isfile(p):
            sys.exit('✗ 找不到 %s' % p)
        s = io.open(p, encoding='utf-8').read()
        if 'function applyLang(' not in s:
            sys.exit('✗ %s 还没注入 i18n 引擎，请先跑 add_i18n.py' % os.path.basename(p))
        spans = []
        for anchor, oc, cc, want in (('var I18N_DICT = ', '{', '}', want_d),
                                     ('var I18N_PAT  = ', '[', ']', want_p)):
            sp = literal_span(s, anchor, oc, cc)
            if sp is None:
                sys.exit('✗ %s 里找不到 %r（引擎被改过？请手工核对）' % (os.path.basename(p), anchor))
            spans.append((sp, s[sp[0]:sp[1]], want))
        cur_d, cur_p = spans[0][1], spans[1][1]
        # 字典是精确查表，键序无关；模板规则是"先匹配先赢"，顺序敏感，必须逐字节比
        ok_d = json.loads(cur_d) == items
        ok_p = cur_p == want_p
        if ok_d and ok_p:
            print('  ✓ %s 已同步（字典 %d 条 / 模板 %d 条）' % (os.path.basename(p), len(items), len(pats)))
            continue
        drift += 1
        if args.check:
            print('  ❌ %s 与 JSON 不一致（字典 %s / 模板 %s）—— 跑 sync_i18n.py 写入'
                  % (os.path.basename(p), 'OK' if ok_d else '需更新', 'OK' if ok_p else '需更新'))
            continue
        diff_d = _delta(json.loads(cur_d), items)
        n_pd = len(pats) - len(json.loads(cur_p))
        out = s[:spans[0][0][0]] + want_d + s[spans[0][0][1]:spans[1][0][0]] + want_p + s[spans[1][0][1]:]
        io.open(p, 'w', encoding='utf-8').write(out)
        print('  🔧 %s 已写入：字典 %+d 条（%s），模板规则 %+d 条'
              % (os.path.basename(p), len(items) - len(json.loads(cur_d)), diff_d, n_pd))
    if args.check and drift:
        return 1
    return 0


def _delta(old_dict, new_items):
    added = [k for k in new_items if k not in old_dict]
    removed = [k for k in old_dict if k not in new_items]
    parts = []
    if added:
        parts.append('新增 %d：%s' % (len(added), '、'.join(added[:6])))
    if removed:
        parts.append('移除 %d：%s' % (len(removed), '、'.join(removed[:6])))
    changed = [k for k in new_items if k in old_dict and old_dict[k] != new_items[k]]
    if changed:
        parts.append('改译 %d：%s' % (len(changed), '、'.join(changed[:6])))
    return '；'.join(parts) or '仅顺序差异'


if __name__ == '__main__':
    sys.exit(main())
