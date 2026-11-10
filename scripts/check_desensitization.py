#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""脱敏闸门：证明"要发布的东西里没有本班真实信息"。

    python3 scripts/check_desensitization.py --program 班级小助手.html 目标目录 [目标目录2 …]
    python3 scripts/check_desensitization.py --program … --list-images   # 顺带列出需人工核查的图片

名单不用手工维护：真实姓名直接从本机程序里的 `STUDENT_NAMES` 读，所以这个脚本
本身不含任何学生信息，可以入库。学校名、历史标识符等放在
`scripts/desensitization.local.json`（**不入库**，格式见 `desensitization.example.json`）。

检查项：真实姓名 / 本地禁词 / 本地路径（macOS、Windows、挂载盘）/ 手机号 / 邮箱 /
文件名里的真实姓名。`web-generator.html`、`docs/index.html` 这类把模板压成 base64 的
产物会先解码再扫——否则整份模板逃过检查（2026-11-10 仓库模板泄露就是这么来的）。

退出码：0 干净 / 1 有命中（**不许发布**）。
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import io
import json
import os
import re
import sys

TEXT_EXT = ('.md', '.html', '.htm', '.py', '.json', '.cjs', '.js', '.txt', '.yaml', '.yml', '.css')
IMAGE_EXT = ('.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg')
# 本机专用文件：含真实值，本来就不该进包/入库，跳过但要报一句
LOCAL_ONLY = ('legacy_ids.json', '_skillhub_meta.json', 'desensitization.local.json')
# base64 内嵌模板的载体（整份模板藏在里面）
B64_ANCHOR = re.compile(r'<script id="tplb64"[^>]*>\s*([A-Za-z0-9+/=\s]+?)\s*</script>', re.S)
PHONE = re.compile(r'(?<!\d)1[3-9]\d{9}(?!\d)')
MAIL = re.compile(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}')
MAIL_OK = re.compile(r'(users\.noreply\.github\.com|example\.(com|org)|sentry\.io)$')
PATHS = [
    re.compile(r'/Users/([A-Za-z0-9._-]+)/'),
    re.compile(r'/Volumes/([\w.\u4e00-\u9fff-]+)/'),
    re.compile(r'[A-Za-z]:\\+Users\\+([^"\'\s\\]+)'),
]
# \u6587\u6863\u91cc\u5199\u5360\u4f4d\u7b26\uff08`/Users/\u2026/`\u3001`C:\Users\<\u7528\u6237\u540d>`\uff09\u662f\u8bf4\u660e\uff0c\u4e0d\u662f\u6cc4\u9732
PATH_PLACEHOLDER = set(['\u2026', '...', '<user>', '<\u7528\u6237\u540d>', 'xxx', 'XXX', 'example'])
# \u5185\u5d4c\u56fe\u7247/\u5b57\u4f53\u7684 base64 \u957f\u4e32\uff1a\u5224\u897f\u6587\u7981\u8bcd\u524d\u5148\u62b9\u6389\uff0c\u5426\u5219\u5b66\u6821\u7f29\u5199\uff08\u4e09\u4e2a\u5b57\u6bcd\u90a3\u4e00\u7c7b\uff09
# \u4f1a\u5728\u5934\u50cf PNG \u7684\u968f\u673a\u5b57\u7b26\u91cc\u53cd\u590d\u5047\u547d\u4e2d\uff08\u4e2d\u6587\u5b57\u7b26\u7981\u8bcd\u4e0d\u53d7\u5f71\u54cd\uff0cbase64 \u91cc\u6ca1\u6709\u6c49\u5b57\uff09
B64_RUN = re.compile(r'[A-Za-z0-9+/]{64,}={0,4}')


def read(path):
    return io.open(path, encoding='utf-8', errors='replace').read()


def roster_of(program):
    m = re.search(r'STUDENT_NAMES\s*=\s*\[(.*?)\]', read(program), re.S)
    if not m:
        sys.exit('✗ 在 %s 里找不到 STUDENT_NAMES，无法取得名单' % program)
    return [x.strip().strip('"\'') for x in m.group(1).split(',') if x.strip().strip('"\'')]


def payloads(path):
    """一个文件要扫的若干份文本（base64 内嵌模板单独解出来）。"""
    s = read(path)
    out = [('正文', s)]
    for m in B64_ANCHOR.finditer(s):
        try:
            out.append(('内嵌模板(base64)',
                        base64.b64decode(m.group(1)).decode('utf-8', errors='replace')))
        except Exception:
            out.append(('内嵌模板(base64)', ''))
    return out


def scan_text(text, names, forbid):
    hits = []
    for n in names:
        if n and n in text:
            hits.append(('真实姓名', n))
    ascii_forbid = [f for f in forbid if f and f.isascii()]
    other_forbid = [f for f in forbid if f and not f.isascii()]
    for f in other_forbid:
        if f in text:
            hits.append(('本地禁词', f))
    if ascii_forbid:
        # 校名缩写一类的西文禁词在 base64 噪声里到处是假命中，
        # 所以只在**去噪后的文本**里按标识符边界匹配；出现在引号里、
        # 作为存储键名或全局变量前缀的那些照样跑不掉。
        bare = B64_RUN.sub('≡', text)
        for f in ascii_forbid:
            m = re.search(r'(?<![A-Za-z0-9])%s(?![A-Za-z0-9])' % re.escape(f), bare, re.I)
            if m:
                ctx = bare[max(0, m.start() - 40):m.end() + 40].replace('\n', '⏎')
                hits.append(('本地禁词', '%s ← %s' % (f, ctx)))
    # ⚠️ 先做字面量守卫再跑正则：压缩过的 JS / base64 是**一整个超长行**，
    #    `[A-Za-z0-9._%+-]+@` 这种"长串后接锚点"在没有锚点时会逐位重试，
    #    实测把 docs/index.html 一份文件拖到 263 秒。守卫之后这类文件直接跳过。
    if '@' in text:
        for v in set(MAIL.findall(text)):
            if not MAIL_OK.search(v):
                hits.append(('邮箱', v))
    for v in set(PHONE.findall(text)):
        hits.append(('手机号', v))
    low = text.lower()
    for rx, needle in ((PATHS[0], '/users/'), (PATHS[1], '/volumes/'), (PATHS[2], '\\users')):
        if needle not in low:
            continue
        for v in set(rx.findall(text)):
            if v.strip('\\/') in PATH_PLACEHOLDER or v.startswith('<') or v.startswith('$'):
                continue
            hits.append(('本地路径', v))
    return hits


def walk(root):
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d not in ('.git', '__pycache__', 'node_modules', '.DS_Store')]
        for f in sorted(fn):
            yield os.path.join(dp, f)


def main():
    ap = argparse.ArgumentParser(description='发布前脱敏检查（真实姓名/学校/路径/联系方式）')
    ap.add_argument('--program', required=True, help='本机真实程序路径，仅用于取名单，不会被扫描')
    ap.add_argument('targets', nargs='+', help='要检查的目录或文件（将发布的那几份）')
    ap.add_argument('--forbid', default='', help='额外禁词，逗号分隔')
    ap.add_argument('--list-images', action='store_true', help='列出需人工核查的图片')
    ap.add_argument('--quiet', action='store_true')
    args = ap.parse_args()

    names = roster_of(args.program)
    forbid = [x.strip() for x in args.forbid.split(',') if x.strip()]
    local_cfg = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'desensitization.local.json')
    if os.path.exists(local_cfg):
        cfg = json.loads(read(local_cfg))
        forbid += [x for x in cfg.get('forbid', []) if x]
        names += [x for x in cfg.get('extra_names', []) if x]
        names = sorted(set(names))
    elif not args.quiet:
        print(' ⓘ 没有 %s：学校名一类只能靠 --forbid 传入' % os.path.basename(local_cfg))

    files, images, skipped, bad = [], [], [], []
    for t in args.targets:
        if os.path.isdir(t):
            files += walk(t)
        else:
            files.append(t)
    seen = set()
    for p in files:
        rp = os.path.abspath(p)
        if rp in seen or not os.path.isfile(rp):
            continue
        seen.add(rp)
        base = os.path.basename(p)
        ext = os.path.splitext(base)[1].lower()
        if ext in IMAGE_EXT:
            images.append(p)
            continue
        if base in LOCAL_ONLY:
            skipped.append(p)
            continue
        if not base.endswith(TEXT_EXT):
            continue
        for nm in names:
            if nm and nm in base:
                bad.append((p, '文件名', '真实姓名', nm))
        for tag, text in payloads(rp):
            for kind, val in scan_text(text, names, forbid):
                bad.append((p, tag, kind, val))

    print('名单来源：%s（%d 人）｜禁词 %d 个｜扫描 %d 个文本文件'
          % (os.path.basename(args.program), len(names), len(forbid), len(seen)))
    if skipped and not args.quiet:
        print(' ⓘ 跳过本机专用文件（本就不入库）：%s' % ', '.join(os.path.basename(x) for x in skipped))

    if bad:
        print('\n❌ 脱敏未通过：%d 处命中，**不许发布**' % len(bad))
        byfile = {}
        for p, tag, kind, val in bad:
            byfile.setdefault(p, []).append('%s/%s:%s' % (tag, kind, val))
        for p, items in sorted(byfile.items()):
            uniq = sorted(set(items))
            print('  %s\n     %s' % (p, '\n     '.join(uniq[:12]) + (
                '\n     (+%d 处)' % (len(uniq) - 12) if len(uniq) > 12 else '')))
        print('\n修复：模板只能由 build_template.py 从真实程序生成；文档里的示例姓名改成'
              '虚构名（张明/李红/王芳）；仓库里那份如果是手工拷进去的，用技能目录的干净模板覆盖。')
        return 1

    print('✅ 脱敏通过：0 处真实姓名 / 学校名 / 本地路径 / 联系方式')
    if args.list_images and images:
        print('\n需人工核查的图片（脚本看不了像素，只能靠眼睛）：')
        for p in sorted(images):
            h = hashlib.sha256(io.open(p, 'rb').read()).hexdigest()[:12]
            print('  %s  %d KB  sha256:%s' % (p, os.path.getsize(p) // 1024, h))
    return 0


if __name__ == '__main__':
    sys.exit(main())
