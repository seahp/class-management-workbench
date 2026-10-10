#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把脱敏模板定制成某个班级专属的「班级管理工作台」HTML。

用法示例：
  # 只给人数（自动生成占位名），6 组，三年级二班
  python3 customize.py --class-name "三年级二班" --count 38 --cols 6 --out ~/Desktop/三年级二班-小助手.html

  # 给真实名单（每行「姓名 男/女」或仅姓名，也可逗号/空格分隔）
  python3 customize.py --class-name "一年级三班" --names-file roster.txt --cols 6 --out out.html

  # 连课表一起定制（JSON：{"周一":["语文","数学",...], ...}，每天 12 节，"—" 表示空）
  python3 customize.py --class-name "二年级一班" --count 36 --schedule sched.json --out out.html

  # 直接从命令行给名单
  python3 customize.py --class-name "四年级五班" --names "张明 男,李红 女,王芳 女" --out out.html

所有参数都可省略：省略的项沿用模板默认值（一年级一班 / 40 人占位名 / 6 组 / 默认课表）。
"""
import argparse
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_TEMPLATE = os.path.join(HERE, '..', 'templates', 'class-workbench-template.html')

GENDER_WORDS = ('男', '女')


def read_template(path):
    p = os.path.abspath(path)
    if not os.path.exists(p):
        sys.exit('找不到模板文件：%s' % p)
    return io.open(p, encoding='utf-8').read()


def parse_names(text):
    """把各种写法的名单解析成 [(name, gender)]，gender 为 'M' / 'F' / ''。"""
    out = []
    for raw in re.split(r'[\n,，;；、]+', text or ''):
        line = raw.strip().strip('|').strip()
        if not line:
            continue
        # 去掉序号列（| 01 | 张明 | 男 | 这种表格粘贴）
        parts = [p.strip() for p in line.replace('\t', ' ').split('|') if p.strip()]
        if not parts:
            continue
        name, gender = None, ''
        # 形式1：已按 | 分列
        if len(parts) >= 2 and parts[1] and not any(g in parts[1] for g in GENDER_WORDS):
            name = parts[1]
            if len(parts) >= 3 and parts[2]:
                gender = 'M' if '男' in parts[2] else ('F' if '女' in parts[2] else '')
        elif len(parts) >= 3:
            # 表头行 / 三列以上：取第二列，第三列判性别
            name = parts[1]
            gender = 'M' if '男' in parts[2] else ('F' if '女' in parts[2] else '')
        else:
            seg = parts[0]
            # 形式2：空格/无分隔，如「张明 男」「张明男」
            m = re.match(r'^(.*?)\s*([男女])$', seg)
            if m:
                name = m.group(1).strip()
                gender = 'M' if m.group(2) == '男' else 'F'
            else:
                name = seg
        # 过滤表头
        if name and name not in ('姓名', '名字', '学生', '序号', '编号', '性别', '班级'):
            out.append((name, gender))
    return out


def make_placeholder_names(n):
    return [('学生%02d' % (i + 1), '') for i in range(n)]


def js_str_list(names):
    return '[' + ','.join('"%s"' % n.replace('"', '\\"') for n in names) + ']'


def js_gender_list(genders):
    return '[' + ','.join('"%s"' % g for g in genders) + ']'


def main():
    ap = argparse.ArgumentParser(description='定制班级管理工作台 HTML')
    ap.add_argument('--class-name', default='一年级一班', help='班级名，如「三年级二班」')
    ap.add_argument('--count', type=int, default=0, help='学生人数（不给名单时用占位名）')
    ap.add_argument('--names', default='', help='名单字符串，逗号/换行分隔，支持「姓名 男」')
    ap.add_argument('--names-file', default='', help='名单文件路径（每行一人）')
    ap.add_argument('--cols', type=int, default=6, help='小组数＝座位列数（4~8，默认 6）')
    ap.add_argument('--schedule', default='', help='课表 JSON 文件路径，如 {"周一":["语文",...]}')
    ap.add_argument('--out', required=True, help='输出 HTML 路径')
    ap.add_argument('--template', default=DEFAULT_TEMPLATE, help='模板路径（一般不用改）')
    args = ap.parse_args()

    s = read_template(args.template)

    # ---------- 1. 班级名 ----------
    old_cn = "className: '一年级一班'"
    assert s.count(old_cn) == 1, '模板里未找到班级名占位（count=%d）' % s.count(old_cn)
    s = s.replace(old_cn, "className: '%s'" % args.class_name.replace("'", "\\'"))
    # 页头大标题的静态文字也要一起换（否则生成后页头仍显示模板默认的「一年级一班」，
    # 要等老师在设置里点一次"应用"才会变 —— 2026-10-10 修）
    old_head = 'id="className" contenteditable="true">一年级一班<'
    assert s.count(old_head) == 1, '模板里未找到页头班级名占位（count=%d）' % s.count(old_head)
    _esc = args.class_name.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    s = s.replace(old_head, 'id="className" contenteditable="true">%s<' % _esc)
    print('✓ 班级名：%s（含页头标题）' % args.class_name)

    # ---------- 2. 学生名单 ----------
    roster = []
    if args.names_file:
        roster = parse_names(io.open(args.names_file, encoding='utf-8').read())
    elif args.names:
        roster = parse_names(args.names)
    if not roster:
        n = args.count or 40
        roster = make_placeholder_names(n)
        print('✓ 名单：%d 个占位名（学生01…），老师可在设置 → ③ 学生名单 里替换' % n)
    else:
        print('✓ 名单：%d 人（%s…）' % (len(roster), '、'.join(x[0] for x in roster[:4])))
        nogen = sum(1 for _, g in roster if not g)
        if nogen:
            print('  ⓘ 有 %d 人未标性别；「男女交替排座」需要性别，可在设置里补' % nogen)

    names_js = js_str_list([n for n, _ in roster])
    m = re.search(r'const STUDENT_NAMES = \[[^\]]*\];[^\n]*', s)
    assert m, '模板里未找到 STUDENT_NAMES'
    s = s.replace(m.group(0), 'const STUDENT_NAMES = %s;' % names_js)

    # 性别：模板默认 gender:''，直接在 STUDENT_NAMES 后面追加一份性别表
    genders_js = js_gender_list([g for _, g in roster])
    anchor = 'const STUDENT_NAMES = %s;' % names_js
    assert s.count(anchor) == 1, 'STUDENT_NAMES 写入异常'
    s = s.replace(anchor,
                  anchor + '\nconst STUDENT_GENDERS = %s;   // 与 STUDENT_NAMES 一一对应（M 男 / F 女 / 空）' % genders_js, 1)

    # 让 defaultState 用上性别表（typeof 保护：未跑本脚本的模板里没有 STUDENT_GENDERS）
    old_g = "const students = STUDENT_NAMES.map((nm,i)=>({id:i, name:nm, score:0, gender:''}));"
    new_g = ("const students = STUDENT_NAMES.map((nm,i)=>({id:i, name:nm, score:0, "
             "gender:((typeof STUDENT_GENDERS!=='undefined' && STUDENT_GENDERS[i])||'')}));")
    if s.count(old_g) == 1:
        s = s.replace(old_g, new_g)
        print('✓ 性别：已写入名单（%d 男 / %d 女）' % (
            sum(1 for _, g in roster if g == 'M'), sum(1 for _, g in roster if g == 'F')))
    else:
        print('  \u26a0 未找到模板里的学生构造语句，性别未写入（模板结构可能已变，请检查 customize.py 的 old_g）')
    # ---------- 3. 小组数 ----------
    cols = args.cols
    if cols < 4 or cols > 8:
        print('  ⓘ 小组数 %d 超出 4~8，回退为 6' % cols)
        cols = 6
    old_cols = 'let COLS = 6;'
    if s.count(old_cols) == 1:
        s = s.replace(old_cols, 'let COLS = %d;' % cols)
    old_seatcols = re.search(r'seatCols:\s*\d+', s)
    if old_seatcols:
        s = s.replace(old_seatcols.group(0), 'seatCols:%d' % cols)
    print('✓ 小组数：%d 组' % cols)

    # ---------- 4. 课表 ----------
    if args.schedule:
        sched = json.load(io.open(args.schedule, encoding='utf-8'))
        day_lines = []
        for d in ['周一', '周二', '周三', '周四', '周五', '周六', '周日']:
            if d in sched:
                arr = sched[d]
                arr = list(arr) + ['—'] * (12 - len(arr)) if len(arr) < 12 else arr[:12]
                day_lines.append("  '%s':[%s]" % (d, ','.join("'%s'" % str(x).replace("'", "\\'") for x in arr)))
        if day_lines:
            new_sched = 'const DEFAULT_V3_SCHED = {\n' + ',\n'.join(day_lines) + '\n};'
            m2 = re.search(r'const DEFAULT_V3_SCHED = \{[\s\S]*?\n\};', s)
            assert m2, '模板里未找到 DEFAULT_V3_SCHED'
            s = s.replace(m2.group(0), new_sched)
            print('✓ 课表：%d 天已写入' % len(day_lines))
    else:
        print('  ⓘ 未给课表，沿用模板默认（老师可在设置 → ④ 课表 里改）')

    # ---------- 5. 输出 ----------
    out = os.path.abspath(os.path.expanduser(args.out))
    os.makedirs(os.path.dirname(out) or '.', exist_ok=True)
    io.open(out, 'w', encoding='utf-8').write(s)
    print('\n✅ 已生成：%s' % out)
    print('   %.1f KB · %d 名学生 · %d 组' % (len(s.encode('utf-8')) / 1024, len(roster), cols))
    print('   双击即可用；首次打开请在 ⚙ 设置 → ③ 学生名单 核对名单。')


if __name__ == '__main__':
    main()
