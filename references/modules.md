# 12 个模块 · 功能与数据结构

全部页面一屏不翻动（1920×1080 / 2560×1440 实测零溢出），触摸拖拽用 Pointer Events。

## 1. 座位
- 数据结构：`seatBase[]`（下标位存学生 id 或 `null`），`COLS`＝小组数（4~8），`rows = ceil(人数/COLS)`
- 交互：拖动换座 / 点两下交换；工具栏 `#seatArrange`（按学号 / **男女交替棋盘式** / 随机）
- 轮换：`seatRotateMode`（cycle 全体前移 / group 按组 / diag 左后斜移 / diagR 右后斜移 / front 前后 / random）+ `seatSideShift`（附加左右移 1 列），`seatRotateWeeks` 周期自动触发
- 教师快照：`state.seatTeacher`（💾 保存 / ↩ 返回）
- **男女交替是真棋盘格**：`(Math.floor(i/COLS) + i%COLS) % 2` 决定性别，不要用 `i%2`（偶数列时上下不交替）

## 2. 积分
- `students[] = {id, name, score, gender}`；id 即下标
- 两种排列：网格 / 与座位一致（`stuLayout='seat'`，横向长条卡）
- 积分可锁定（防学生误触），支持按小组批量加分

## 3. 竞赛（组装火箭赛）
- `pk.groups[] = {id, name, color, members[]}`，**成员从座位列派生**：同一列＝同一组，靠门列＝1 组红队
- `pk.done = {gid: {sid: {任务名: 1}}}`，**每人每项限一次**
- 完成整组任务 → 发射「XX火箭」动效（静音、不显示姓名）
- ⚠️ 成员同步见 `iteration-rules.md` 的「派生数据三点同步」

## 4. 值日
- 上区：值日表 `dutyGrid[r][c]`（存 id 或 -1），岗位 `dutyPositions[]` 可自定义，`dutyLock["r-c"]` 锁定
- 下区：**班级岗** `dutyCustom[] = {role, icon, sid}`（管理员 / 灯长 / 柜长 / 餐长 / 课代表）
- 名字块前带小学号（id+1，与座位学号一致）

## 5. 课表
- **夏季 / 冬季各存一整套**：`state.schedSets = {summer:{schedule,layout,note}, winter:{...}}`
- 当前显示走 `state.schedule / schedLayout / schedNote`；`schedMirror()` 在 `save()` 开头把改动落回「当前季节」
- 每天 12 节；作息行顺序由 `LAYOUT_SUMMER` / `LAYOUT_WINTER` 决定

## 6. 作业
- 按日期存 `state.homework[日期]`，分语文 / 数学 / 英语 / 其他四栏，下方显示近期作业

## 7. 诵读（古诗）
- `poems[] = {title, author, body, cat, py}`，73 篇（唐诗 50 + 蒙学童诗等）
- `py` 是逐字音节数组，与正文字符一一对齐（pypinyin 生成 + 语境覆盖词），渲染成 `<ruby>` 注音
- 每页 ≤22 字，◀▶ 翻页；分类可筛选

## 8. 计算（口算 / 竖式 / 脱式）
- 三个题库**各自独立**：`state.mathCustom[]` / `mathVert[]` / `mathMix[]`
- 设置 ⑩ 可分别导入；保存与清空只作用当前题型
- 竖式：`#vertGrade` 1~6（默认 1），可勾选加 / 减 / 乘 / 除；**除法一律整除、不出余数**（导入时除不尽的行自动跳过）
- 脱式：支持 `(12+8)×5` 这类表达式，递归下降求值

## 9. 单词（英语）
- 内置人教版 1~6 年级 12 册约 954 词；导入的词只写 `state.words.custom[册]`，**不动内置库**
- 两个子页：🃏 记忆卡 / 📋 单词表（背单词时答案不外露）
- 三色掌握度：😵 不会（红）/ 🤔 拿不准（黄）/ 😀 会了（绿·胸有成竹）
- 每页 6 张小卡，3D 翻面；艾宾浩斯复习 `WORD_STEPS=[0,1,2,4,7,15,30,60]`
- 「会了」的词在**第 2、3 天按约 30% 滚动回看**

## 10. 工具（随机点名 + 倒计时）
- 点名：公平随机，按钮 330×71（大屏易点）
- 倒计时：拖动滑块**实时显示**（绑 `input` + `change`），1/3/5/10/15 分钟预设，最后 30 秒变红闪烁

## 11. 排行
- 日 / 周 / 月 / 总榜，按积分排序

## 12. 抽卡
- 班级小权利卡（盲盒），卡池在设置 ⑨ 管理

---

## 全局能力与约定

| 能力 | 说明 |
|---|---|
| 单文件离线 | 双击即用，无需服务器/联网 |
| 数据存本机 | localStorage KEY `class_helper_v1` + 备份键，另有自动备份 |
| 换机迁移 | 顶栏 💾 导出「换机包」HTML（state 内嵌），新电脑双击自动带入；导出名带日期，与源程序文件区分 |
| 设置指纹 | 8 位指纹验证两端一致（派生字段不计入） |
| 编辑模式 | 右上 ✏️ 可改页面说明文字，存 `state.customText` |
| 主题色 | 7 色 + 自定义 hex |
| 全屏 | 右上 ⛶ |
| 浮动导航 | 右下角可拖动图标（📅🧹📜⭐） |

## 给老师的最短上手路径

1. 双击打开 → ⚙ 设置 → ③ 学生名单（粘贴名单）
2. ④ 课表（每天一行）
3. 座位页调座位 → 💾 保存调整后的座位
4. 积分 / 竞赛页日常加分


## 排行页：6 个视图（第十三轮补齐总积分与月度趋势）

页签：`#rankTabs button[data-r]` = `day / yest / week / month / total / monthly`（+ 查某一天 `#rankDate`）。

| 视图 | 渲染函数 | 数据口径 |
|---|---|---|
| 📅 今日 / ⬅ 昨日 / 📆 本周 / 🗓 本月 / 查某一天 | `renderRankings(period)`（原领奖台：个人前三 + 本周小组前三 + 3 列紧凑列表） | `periodPoints(period)` 按日期区间汇总 `state.daily` |
| 🏆 **总积分** | `renderTotalRank()` | **`dailyTotalOf(sid)` = 该生所有日期明细之和**（含今日），而不是卡片上的 `students[].score` |
| 📈 **月度趋势** | `renderMonthly()` | `monthTotalOf(sid, 'YYYY-MM')` 按月份汇总 `daily` |

`renderRankings(period)` 顶部只做分流：`period==='total'` → `renderTotalRank()`，`'monthly'` → `renderMonthly()`。
两个新视图是**叶子渲染函数**（只读数据 + 写 DOM，不反向调用其它渲染函数），符合铁律 9。

总积分视图还额外做了一件事：`scoreGap()` 的差额 > 0 时在标题旁标红提醒
「与卡片上的累计分差 N 分」，把第十二轮的积分自检暴露在老师最常看的地方。

**关键设计：总积分以 `daily` 明细为准**
卡片上的 `students[].score` 是冗余缓存，历史上被 `#scoreReset` 单独清过；
而 `daily` 是逐日流水，不可撇除。凡是"统计/排行/趋势"类展示，**一律从明细重算**，
缓存字段只用于卡片显示。这也保证了 `Σ月 == Σ日 == 总积分` 三者恒等。

### 月度趋势的呈现（为教室大屏设计）
- 上方：全班每月总积分柱状图（`monthBarsSVG`，内联 SVG，最多画最近 8 个月，超出在说明里注明）
- 下方：每人一行、三列排布——`名次 | 姓名 | 迷你月度折线(sparkSVG, 104×26) | 总积分`
  （34 人的班 = 34 行 ÷ 3 列 ≈ 12 行，正好一屏）
- 悬浮姓名可见「9月 24，10月 30…」明细；点姓名打开个人趋势弹窗
- 导出：`⬇ 月度矩阵 CSV`（`exportMonthlyCSV`）= 行=学生、列=各月、末列合计 + 全班合计行
- 导出：`⬇ 总榜 CSV`（`exportTotalCSV`）= 名次/学号/姓名/总积分/今日/本月

### 个人趋势弹窗（`#trendMask`）
`#trRange`（近 7/30/60 天）+ **`#trMode`（按日 / 按月）**：
- 按日 → `renderTrendChart(sid,n)`：每日柱状 + 全班平均虚线
- 按月 → `renderTrendChartByMonth(sid)`：每月柱状 + 合计
`renderTrendChart` 开头按 `#trMode` 分流；`syncTrendMode()` 负责切换下拉显隐与弹窗标题。

### 座位方案（第十六轮）
`state.seatPlans=[{name,base,at}|null ×3]` + `state.seatPlansTmp`。
工具栏 `#seatPlan0/1/2` + `#seatPlanSave` + `#seatPlanUndo` + `#seatPlanAsk` + `#seatPlanHint`。
关键函数：`ensureSeatPlans`（补齐/迁移老 `seatTeacher`）、`seatPlanLabel`、`sameSeat`、
`seatPlanIndexOfCurrent`（当前座位属于哪套 → 按钮变绿）、`renderSeatPlanUI`（由 `renderSeating()` 末尾调用）、
`applySeatPlan`（切换，**走 `rerenderAll()`** + 重置轮换基准 + 存 `seatPlansTmp`）、
`saveSeatPlan` / `askSaveSeatPlan` / `undoSeatPlanSwitch` / `renameSeatPlan` / `clearSeatPlan` / `seatPlanMenu`。

### ⚠️ 「男女生交替」的前置条件
`arrangeGenderAlternate()` 把**性别未知的学生并进 males**，所以名单里一个性别都没填时，
它的结果**等于「按学号排列」**（静默无效果）。`arrangeSeat('gender')` 已加前置检查：
`known===0` → 明确提示去设置③粘贴「姓名 男/女」；`0<known<total` → 提示有多少人未填。
