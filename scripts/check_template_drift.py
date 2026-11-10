#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查「技能模板」是否落后于真实程序 —— 发版前必跑，漂移即失败。

为什么需要：
  模板只能由 build_template.py 从真实程序脱敏生成。过去若干轮是"手工把改动抄到模板上"，
  抄漏了没人发现；而 ready-to-use / web-generator 的"逐字节一致"校验只证明
  **产物忠实于模板**，不证明**模板忠实于程序**，所以漂移能一路通过所有闸门。
  （2026-11-10 实测：模板落后本班程序 36 个代码块。）

做法：用同一份真实程序重新生成一份临时模板，与仓库里的模板比字节；
      不一致时列出差异块（并区分"代码块"与"班级数据块"，后者说明脱敏出了问题）。

用法：
  python3 check_template_drift.py <真实程序.html>
  python3 check_template_drift.py <真实程序.html> --fix     # 顺手重新生成模板
退出码：0 无漂移 / 1 有漂移（或 --fix 后仍需复验）/ 2 参数或脚本错误
"""
import argparse
import difflib
import io
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)
TPL = os.path.join(SKILL, 'templates', 'class-workbench-template.html')

# 出现这些字样说明差异里混进了班级真实数据，属于脱敏问题而不是代码漂移
DATA_HINTS = ('STUDENT_NAMES', 'DEFAULT_V3_SCHED', '张明', '学生01')


def gen_template(src, out):
    r = subprocess.run([sys.executable, os.path.join(HERE, 'build_template.py'), src, '--out', out],
                       capture_output=True, text=True)
    if r.returncode != 0:
        sys.stderr.write(r.stdout + r.stderr)
        sys.exit('✗ build_template.py 失败，先修脱敏再谈漂移')


def hunks(a, b):
    """返回 [(tag, a起, a止, b起, b止, 摘要)]，行号 1 基。"""
    al, bl = a.split('\n'), b.split('\n')
    sm = difflib.SequenceMatcher(None, al, bl, autojunk=False)
    out = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == 'equal':
            continue
        body = '\n'.join(bl[j1:j2])[:300] if j2 > j1 else '\n'.join(al[i1:i2])[:300]
        out.append((tag, i1 + 1, i2, j1 + 1, j2, body))
    return out


def main():
    ap = argparse.ArgumentParser(description='检查模板是否落后于真实程序')
    ap.add_argument('program', help='真实程序 HTML（如 班级小助手.html）')
    ap.add_argument('--fix', action='store_true', help='发现漂移时用 build_template.py 重新生成模板')
    args = ap.parse_args()

    prog = os.path.abspath(os.path.expanduser(args.program))
    if not os.path.isfile(prog):
        sys.exit('✗ 找不到程序文件：%s' % prog)
    if not os.path.isfile(TPL):
        sys.exit('✗ 找不到仓库模板：%s' % TPL)

    tmp = os.path.join(tempfile.gettempdir(), 'tpl.drift.check.html')
    gen_template(prog, tmp)
    fresh = io.open(tmp, encoding='utf-8').read()
    cur = io.open(TPL, encoding='utf-8').read()

    if fresh == cur:
        print('✅ 模板与程序同步（%d 字节，无漂移）' % len(cur.encode('utf-8')))
        return 0

    hs = hunks(cur, fresh)
    data = [h for h in hs if any(d in h[5] for d in DATA_HINTS)]
    print('❌ 模板漂移：%d 个差异块（模板 %d 字节 → 重新生成 %d 字节）'
          % (len(hs), len(cur.encode('utf-8')), len(fresh.encode('utf-8'))))
    for tag, i1, i2, j1, j2, body in hs[:12]:
        print('   %-8s 模板 L%d-%d / 新模板 L%d-%d ｜ %s' % (tag, i1, i2, j1, j2, body.split('\n')[0][:96]))
    if len(hs) > 12:
        print('   …另有 %d 块' % (len(hs) - 12))
    if data:
        print('   ⚠️ 其中 %d 块涉及名单/课表/占位名 —— 这是脱敏问题，别只 --fix，先查 build_template.py' % len(data))

    if args.fix:
        gen_template(prog, TPL)
        print('🔧 已用 build_template.py 重新生成模板 —— 请接着跑 build_web_generator.py + customize.py 重建产物')
        return 1
    print('   修复：python3 scripts/build_template.py "%s"  然后重建 web-generator / ready-to-use' % prog)
    return 1


if __name__ == '__main__':
    sys.exit(main())
