#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""为 WorkBuddy 开放平台（open.workbuddy.cn）打包技能包。

背景：两个平台的 SKILL.md frontmatter 校验要求不同 ——
  · SkillHub（skillhub.cn）：需要完整字段
      name / slug / displayName / display_name / display_name_en / summary / tags
      / description / description_zh / description_en / category / version / homepage / author
  · WorkBuddy 开放平台（open.workbuddy.cn）：按官方文档采用 **9 字段简洁格式**
      name / display_name / display_name_en / description / description_zh
      / description_en / category / version / author
    （对照官方已上架技能 class-analysis-primary 的实际 frontmatter）
    多出的字段、YAML 特殊字符（如 " & "）、macOS zip 额外字段，
    都可能导致平台"解析失败"。

本脚本做的事：
  1. 读技能目录的 SKILL.md（完整字段版，供 SkillHub 用）
  2. 只在打包时**重写 frontmatter 为 9 字段简洁版**（正文原样）
  3. 把 description_en 里的 " & " 换成 " and "（YAML 保留字符）
  4. 打**干净 zip**：无 macOS extra field、无 .DS_Store / __MACOSX / *.bak
  5. 自检：9 字段齐全、含 SKILL.md、零 extra field

用法：
  python3 pack_for_open_platform.py --out ~/Desktop/skill.zip          # 完整版
  python3 pack_for_open_platform.py --out ~/Desktop/skill-lite.zip --lite   # 精简版（去掉两个大模板）
"""
import argparse
import datetime
import io
import os
import re
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_SRC = os.path.join(HERE, '..')
ROOT_NAME = 'class-management-workbench'

#: 平台官方文档的 9 个字段（顺序也按文档）
KEEP_FIELDS = ['name', 'display_name', 'display_name_en', 'description',
               'description_zh', 'description_en', 'category', 'version', 'author']

#: 精简版剔除的大文件（AI 可按 SKILL.md 指引现场构建，功能等价）
LITE_SKIP = ('templates/ready-to-use-workbench.html',
             'templates/web-generator.html')

SKIP_NAMES = {'legacy_ids.json'}


def parse_frontmatter(text):
    m = re.match(r'^---\n([\s\S]*?)\n---\n', text)
    if not m:
        sys.exit('✗ SKILL.md 缺少规范的 frontmatter（--- 包裹）')
    fm = {}
    for line in m.group(1).split('\n'):
        if not line.strip() or ':' not in line:
            continue
        k, v = line.split(':', 1)
        fm[k.strip()] = v.strip()
    return fm, text[m.end():]


def build_simple_frontmatter(fm):
    missing = [k for k in KEEP_FIELDS if k not in fm or not fm[k]]
    if missing:
        sys.exit('✗ 缺少平台必填字段：%s' % missing)
    # YAML 保留字符清理：值内的 " & " → " and "
    def clean(v):
        v = v.replace(' & ', ' and ')
        if re.search(r':\s', v):
            v = re.sub(r':\s', '：', v)      # 半角冒号+空格 → 全角，避免被当嵌套
        return v
    lines = ['---']
    for k in KEEP_FIELDS:
        lines.append('%s: %s' % (k, clean(fm[k])))
    lines.append('---\n')
    return '\n'.join(lines)


def build_zip(src, out, body, skip_rel=()):
    n = 0
    dt = datetime.datetime.now().timetuple()[:6]
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for dirpath, dirnames, filenames in os.walk(src):
            dirnames[:] = [d for d in dirnames if not d.startswith('.') and d != '__MACOSX']
            rel = os.path.relpath(dirpath, src)
            if rel != '.':
                zi = zipfile.ZipInfo('%s/%s/' % (ROOT_NAME, rel.replace(os.sep, '/')), date_time=dt)
                zi.external_attr = (0o40755 << 16) | 0x10
                z.writestr(zi, b'')
            for fn in sorted(filenames):
                if fn.startswith('.') or fn in SKIP_NAMES or '.bak' in fn:
                    continue
                relf = fn if rel == '.' else rel.replace(os.sep, '/') + '/' + fn
                if relf in skip_rel:
                    print('  ⓘ 精简版跳过：%s' % relf)
                    continue
                if fn == 'SKILL.md' and rel == '.':
                    data = body.encode('utf-8')          # ← 写入重写后的 frontmatter
                else:
                    data = io.open(os.path.join(dirpath, fn), 'rb').read()
                zi = zipfile.ZipInfo('%s/%s' % (ROOT_NAME, relf), date_time=dt)
                zi.external_attr = 0o644 << 16
                zi.compress_type = zipfile.ZIP_DEFLATED
                z.writestr(zi, data)
                n += 1
    return n


def verify(out):
    z = zipfile.ZipFile(out)
    names = [i.filename for i in z.infolist()]
    want = '%s/SKILL.md' % ROOT_NAME
    if not any(n == want or n.endswith('/' + want) for n in names):
        sys.exit('✗ 自检失败：包内没有 %s/SKILL.md' % ROOT_NAME)
    bad_extra = [i.filename for i in z.infolist() if len(i.extra or b'')]
    if bad_extra:
        sys.exit('✗ 自检失败：%d 个条目仍含 extra field' % len(bad_extra))
    sk = z.read('%s/SKILL.md' % ROOT_NAME).decode('utf-8')
    fm, _ = parse_frontmatter(sk)
    extra = [k for k in fm if k not in KEEP_FIELDS]
    missing = [k for k in KEEP_FIELDS if k not in fm]
    if missing:
        sys.exit('✗ 自检失败：缺字段 %s' % missing)
    if extra:
        print('  ⚠ 多余字段（平台未列，建议清掉）：%s' % extra)
    top = sorted(set(n.split('/')[1] for n in names if n.count('/') > 1 and n.split('/')[1]))
    print('  ✓ 自检通过：%d 条目 / %s' % (len(z.infolist()), ', '.join(top)))
    print('  ✓ frontmatter %d 字段（平台规范 9）' % len(fm))
    return z


def main():
    ap = argparse.ArgumentParser(description='为 WorkBuddy 开放平台打包技能')
    ap.add_argument('--src', default=DEFAULT_SRC, help='技能目录（默认脚本上一级）')
    ap.add_argument('--out', required=True, help='输出 zip 路径')
    ap.add_argument('--lite', action='store_true', help='精简版：去掉两个大模板（现场可构建）')
    args = ap.parse_args()

    src = os.path.abspath(os.path.expanduser(args.src))
    if not os.path.isfile(os.path.join(src, 'SKILL.md')):
        sys.exit('✗ 找不到 %s/SKILL.md' % src)

    fm, body = parse_frontmatter(io.open(os.path.join(src, 'SKILL.md'), encoding='utf-8').read())
    simple = build_simple_frontmatter(fm)
    full_text = simple + body

    out = os.path.abspath(os.path.expanduser(args.out))
    print('打包%s → %s' % ('【精简版】' if args.lite else '【完整版】', out))
    n = build_zip(src, out, full_text, skip_rel=LITE_SKIP if args.lite else ())
    verify(out)
    print('✅ 完成：%.2f MB / %d 个文件' % (os.path.getsize(out) / 1048576, n))
    print('   上传入口：https://open.workbuddy.cn → 开发者中心 → 技能 → 上传 ZIP')


if __name__ == '__main__':
    main()
