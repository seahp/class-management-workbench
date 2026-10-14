#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把「网页版生成器」源码 + 脱敏模板 → 打包成一个单文件网页版生成器。

用法：
  python3 build_web_generator.py [--out 输出路径]

原理：把 templates/class-workbench-template.html 以 base64 内嵌进
      scripts/web-generator-src.html 的占位符 __TEMPLATE_BASE64__，
      得到一份「打开就能用、不装任何软件、离线也能用」的生成器页面。
      老师填班级名/名单/组数/课表 → 浏览器内完成定制 → 下载成品 HTML。

为什么用 base64：模板里有 </script> 等 HTML 片段，直接内嵌脚本会截断；
      base64 只有字母数字与 +/=，绝对安全。
"""
import argparse
import base64
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(HERE, '..', 'templates', 'class-workbench-template.html')
SRC = os.path.join(HERE, 'web-generator-src.html')
DEFAULT_OUT = os.path.join(HERE, '..', 'templates', 'web-generator.html')

PLACEHOLDER = '__TEMPLATE_BASE64__'


def main():
    ap = argparse.ArgumentParser(description='构建网页版生成器（单文件）')
    ap.add_argument('--out', default=DEFAULT_OUT, help='输出路径')
    ap.add_argument('--template', default=TEMPLATE, help='模板路径')
    ap.add_argument('--src', default=SRC, help='生成器源码路径')
    args = ap.parse_args()

    tpl_path = os.path.abspath(os.path.expanduser(args.template))
    src_path = os.path.abspath(os.path.expanduser(args.src))
    if not os.path.isfile(tpl_path):
        sys.exit('找不到模板：%s' % tpl_path)
    if not os.path.isfile(src_path):
        sys.exit('找不到生成器源码：%s' % src_path)

    tpl = io.open(tpl_path, encoding='utf-8').read()
    src = io.open(src_path, encoding='utf-8').read()

    if src.count(PLACEHOLDER) != 1:
        sys.exit('生成器源码里应恰好有 1 个 %s 占位符（当前 %d 个）'
                 % (PLACEHOLDER, src.count(PLACEHOLDER)))

    b64 = base64.b64encode(tpl.encode('utf-8')).decode('ascii')
    out_html = src.replace(PLACEHOLDER, b64)

    # 自检：占位符已替换、base64 能解回原文
    if PLACEHOLDER in out_html:
        sys.exit('自检失败：占位符未被替换')
    back = base64.b64decode(b64).decode('utf-8')
    if back != tpl:
        sys.exit('自检失败：base64 往返不一致')
    if '</script>' in b64:
        sys.exit('自检失败：base64 含 </script>（不应发生）')

    out = os.path.abspath(os.path.expanduser(args.out))
    os.makedirs(os.path.dirname(out) or '.', exist_ok=True)
    io.open(out, 'w', encoding='utf-8').write(out_html)

    print('✅ 网页版生成器已生成：%s' % out)
    print('   模板 %.1f KB → 生成器 %.1f KB（含内嵌模板）'
          % (len(tpl.encode('utf-8')) / 1024, len(out_html.encode('utf-8')) / 1024))
    print('   用法：双击打开 → 填班级信息 → 生成 → 下载成品 HTML（全程离线可用）')


if __name__ == '__main__':
    main()
