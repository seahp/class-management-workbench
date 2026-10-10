#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把一份真实的「班级小助手」HTML 脱敏成可分发的技能模板。

用法：
  python3 build_template.py <源程序.html> [--out assets/class-workbench-template.html]

脱敏项（前 3 项内置，必须命中否则报错退出）：
  1. STUDENT_NAMES  → 40 个占位名「学生01…学生40」
  2. DEFAULT_V3_SCHED → 中性示例课表（不含任何学校的真实作息）
  3. 设置③ 名单框 placeholder 的真实姓名 → 张明/李红/王芳
  4. 历史标识符（旧 localStorage/IndexedDB 键名、旧全局变量前缀等）→ 通用名，
     并做「残留即报错」自检。映射表放在同目录 legacy_ids.json —— **该文件不入库**，
     因为每位维护者的历史值各不相同；格式见 legacy_ids.example.json，文件不存在则跳过本项。

设计约定：模板必须保留 customize.py 依赖的锚点：
  className: '一年级一班' / const STUDENT_NAMES = [...] /
  const students = STUDENT_NAMES.map((nm,i)=>({id:i, name:nm, score:0, gender:''})); /
  let COLS = 6; / seatCols: 6 / const DEFAULT_V3_SCHED = {...};
"""
import argparse
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_OUT = os.path.join(HERE, '..', 'templates', 'class-workbench-template.html')

PLACEHOLDER_COUNT = 40

# 中性示例课表（5 天 × 12 节）：只用最常见的通用课程名
NEUTRAL_SCHED = """const DEFAULT_V3_SCHED = {
  '周一':['语文','数学','英语','美术','音乐','午餐','午管','体育','科学','道法','班队会','—'],
  '周二':['数学','语文','体育','英语','书法','午餐','午管','阅读','劳动','美术','—','—'],
  '周三':['语文','数学','英语','音乐','科学','午餐','午管','语文','体育','信息','—','—'],
  '周四':['数学','语文','道法','美术','英语','午餐','午管','劳动','音乐','阅读','—','—'],
  '周五':['语文','数学','体育','科学','英语','午餐','午管','书法','班队会','—','—','—']
};"""


def sub_once(s, old, new, tag):
    c = s.count(old)
    if c != 1:
        sys.exit('✗ 脱敏失败[%s]：命中 %d 次（应为 1 次）' % (tag, c))
    print('  ✓ %s' % tag)
    return s.replace(old, new, 1)


def sub_all(s, old, new, tag, expect=None):
    c = s.count(old)
    if c == 0:
        sys.exit('✗ 脱敏失败[%s]：未找到' % tag)
    if expect is not None and c != expect:
        sys.exit('✗ 脱敏失败[%s]：命中 %d 次（应为 %d 次）' % (tag, c, expect))
    print('  ✓ %s（%d 处）' % (tag, c))
    return s.replace(old, new)


def load_legacy_ids():
    """读取本机历史标识符映射（同目录 legacy_ids.json，不入库）。

    里面是本机程序用过的旧标识符（旧存储键名、旧全局变量前缀等）到通用名的映射，
    以及"出现即视为脱敏失败"的禁止残留规则。文件不存在时返回空配置——
    适用于从未改过标识符的程序，此时本步自动跳过。
    """
    path = os.path.join(HERE, 'legacy_ids.json')
    if not os.path.isfile(path):
        print('  ⓘ 未找到 legacy_ids.json，跳过历史标识符替换（新程序无需此步）')
        return {'subs': [], 'forbid': []}
    cfg = json.loads(io.open(path, encoding='utf-8').read())
    subs = [x for x in (cfg.get('subs') or []) if x.get('old') and x.get('new')]
    forbid = [x for x in (cfg.get('forbid') or []) if x.get('pat')]
    return {'subs': subs, 'forbid': forbid}


def main():
    ap = argparse.ArgumentParser(description='把真实程序脱敏成技能模板')
    ap.add_argument('src', help='源程序 html 路径')
    ap.add_argument('--out', default=DEFAULT_OUT, help='输出模板路径')
    args = ap.parse_args()

    s = io.open(args.src, encoding='utf-8').read()
    print('源文件：%s（%.1f KB）' % (args.src, len(s.encode('utf-8')) / 1024))

    # ---------- 1. 学生名单 ----------
    m = re.search(r'const STUDENT_NAMES\s*=\s*\[[^\]]*\];', s)
    if not m:
        sys.exit('✗ 未找到 STUDENT_NAMES')
    names = ['学生%02d' % (i + 1) for i in range(PLACEHOLDER_COUNT)]
    s = s.replace(m.group(0), 'const STUDENT_NAMES = [%s];' % ','.join('"%s"' % n for n in names), 1)
    print('  ✓ STUDENT_NAMES → %d 个占位名' % PLACEHOLDER_COUNT)

    # 去掉可能残留的 STUDENT_GENDERS（由 customize.py 按真实名单重新生成）
    g = re.search(r'\nconst STUDENT_GENDERS\s*=\s*\[[^\]]*\];[^\n]*', s)
    if g:
        s = s.replace(g.group(0), '', 1)
        print('  ✓ 已移除 STUDENT_GENDERS（占位模板不带性别）')

    # ---------- 2. 课表 ----------
    m = re.search(r'const DEFAULT_V3_SCHED = \{[\s\S]*?\n\};', s)
    if not m:
        sys.exit('✗ 未找到 DEFAULT_V3_SCHED')
    s = s.replace(m.group(0), NEUTRAL_SCHED, 1)
    print('  ✓ DEFAULT_V3_SCHED → 中性示例课表（5 天）')

    # ---------- 3. 设置③ 名单框 placeholder ----------
    # 判据：placeholder 里如果已经是我们自己的中性示例（张明…），就跳过；
    # 否则一律视为"真实姓名占位"，整段替换掉（不依赖任何具体姓名，避免把真实姓名写进脚本）。
    m = re.search(r'placeholder="([^"]*男&#10;[^"]*)"', s)
    if m and '张明 男' not in m.group(1):
        new_ph = ('张明 男&#10;李红 女&#10;王芳 女&#10;'
                  '（每行一个，姓名后空格＋男/女；也可粘贴「姓名 | 男」表格，纯名字也可以）')
        s = s.replace('placeholder="%s"' % m.group(1), 'placeholder="%s"' % new_ph, 1)
        print('  ✓ 设置③ placeholder → 张明/李红/王芳（原为真实姓名）')
    else:
        print('  ⓘ 设置③ placeholder 已是中性示例，跳过')

    # ---------- 4. 历史标识符脱敏（映射表见 scripts/legacy_ids.json，不入库） ----------
    legacy = load_legacy_ids()
    for it in legacy['subs']:
        s = sub_all(s, it['old'], it['new'], it.get('tag') or it['old'], it.get('expect'))

    # ---------- 5. 自检：不得残留历史标识符 ----------
    for it in legacy['forbid']:
        if re.search(it['pat'], s):
            sys.exit('✗ 自检未通过：%s' % it['msg'])
    print('  ✓ 自检：无历史标识符残留（替换 %d 项 / 禁止 %d 项）'
          % (len(legacy['subs']), len(legacy['forbid'])))

    # ---------- 6. 锚点自检（customize.py 依赖） ----------
    ANCHORS = [
        "className: '一年级一班'",
        'const STUDENT_NAMES = ',
        "const students = STUDENT_NAMES.map((nm,i)=>({id:i, name:nm, score:0, gender:''}));",
        'let COLS = 6;',
        'seatCols: 6',
        'const DEFAULT_V3_SCHED = {',
    ]
    for a in ANCHORS:
        if a not in s:
            sys.exit('✗ 锚点缺失（customize.py 会失败）：%s' % a)
    print('  ✓ 锚点齐全（定制脚本可用）')

    out = os.path.abspath(os.path.expanduser(args.out))
    os.makedirs(os.path.dirname(out) or '.', exist_ok=True)
    io.open(out, 'w', encoding='utf-8').write(s)
    print('\n✅ 模板已生成：%s（%.1f KB）' % (out, len(s.encode('utf-8')) / 1024))


if __name__ == '__main__':
    main()
