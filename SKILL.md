---
name: class-management-workbench
slug: class-management-workbench
display_name: 班级管理工作台生成器
display_name_en: Classroom Management Workbench Generator
displayName: 班级管理工作台生成器
displayNameEn: Classroom Management Workbench Generator
description: 为中小学班主任生成一套「班级管理工作台」单文件离线 HTML——含座位表、积分榜、小组竞赛、值日、课表、作业、古诗诵读、口算/竖式/脱式练习、英语单词记忆、随机点名与倒计时、排行榜、抽卡共 12 个模块，适配教室触摸大屏（希沃一体机等）。当用户说「做个班级小助手 / 班级管理工具 / 班级工作台」「给我班做一个座位表+积分+值日的工具」「要一个能排座位、加分、倒计时的网页」，或需要为某个具体班级（如「三年级二班 38 人」）定制班级管理页面时使用；也适用于在已有的班级小助手 HTML 上迭代修改功能。
description_zh: 面向中小学班主任：三条路都能拿到一份双击即用的单文件离线班级管理工作台（座位、积分、竞赛、值日、课表、作业、诵读、计算、单词、工具、排行、抽卡共 12 模块）——① 让 AI 按班级信息直接生成；② 老师自己在「网页版生成器」填三步生成（零安装）；③ 直接用「空白班」文件在设置里贴名单。内置动物头像等级系统与 3480px 教室大屏适配；程序内含「❓遇到问题」通俗问答，并教老师用「绑定程序文件」防止教室还原卡清数据。
description_en: For primary and secondary homeroom teachers, generate a ready-to-use single-file offline classroom management workbench (seating chart, points, group competition, duty roster, timetable, homework, poetry recitation, math drills, English vocabulary, random picker and countdown, leaderboard, reward cards, plus a v2.0 animal-avatar level system with 12 hand-drawn watercolor pets, star-to-level-up progression with unlimited Lv, and unified 1.8x big-screen scaling for 3480px touch displays) from a few class details, verify it in a real browser, deliver it, and teach the file-binding trick that survives classroom restore cards.
category: education
summary: 一键生成班主任专用单文件离线工作台：座位表、积分榜、小组竞赛、值日、课表、作业、古诗、口算、单词卡、抽卡共 12 个模块，适配教室触摸大屏；界面支持中英文切换
tags: [班级管理, 班主任, 座位表, 积分, 值日, 课表, 教室大屏, 教师工具, 单文件HTML, 离线, 双语]
homepage: https://github.com/seahp/class-management-workbench
version: 2.5.0
author: 粉笔与代码
---

# 教师班级管理工作台

> **获取方式**（两处内容一致，任选其一）：
> · **GitHub（源码 / 完整仓库）**：https://github.com/seahp/class-management-workbench
> · **SkillHub（技能商店，一键安装）**：https://skillhub.cn/skills/class-management-workbench
>   `skillhub install class-management-workbench --namespace user_1db801dd`

## 用途

给班主任产出一份**单文件离线 HTML**（双击即用、无需联网、数据存本机浏览器），把班级日常管理的核心场景装进一个页面：座位、积分、小组竞赛、值日、课表、作业、诵读、计算、单词、工具、排行、抽卡。面向**教室触摸大屏**（希沃一体机等）设计：一屏不翻动、按钮够大、可触摸拖拽。

## 三种用法（先问老师会不会用命令行，再选路）

| 用法 | 适合 | 怎么做 |
|---|---|---|
| **① AI 生成**（本技能主路径） | 老师身边有 AI 助手 | 老师报班级信息 → 你跑 `scripts/customize.py` 生成 → 交付前按 `references/verification.md` 验证 |
| **② 网页版生成器**（零安装） | 老师自己弄、不想碰命令行 | 打开 `templates/web-generator.html`（或在线版），填班级名/名单/组数/课表 → 点生成 → 下载成品。**纯浏览器内完成，离线也能用**。若包内没有此文件：`python3 scripts/build_web_generator.py` 现场构建（需先有模板） |
| **③ 空白班文件**（最省事） | 老师连生成都不想点 | 直接给 `templates/ready-to-use-workbench.html`，双击打开 → ⚙ 设置 → ③ 贴自己班名单 → 完事。若包内没有此文件：`python3 scripts/customize.py --class-name "一年级一班" --count 40 --out ready-to-use-workbench.html` 现场生成 |

> ⚠️ **遇到不懂命令行的老师，不要让他去装 Python、敲命令** —— 直接推 ② 或 ③。
> 判断口诀：老师愿意发名单给你 → 用 ①；老师要自己动手 → 用 ②；老师只想马上能用 → 用 ③。

**程序内置了「❓ 遇到问题」面板**（右上角）：12 条大白话问答，覆盖数据保存、换电脑、还原卡、换季课表等。老师提问前先让他点 ❓ 看看；更完整的一份在 `references/faq-for-teachers.md`。

**界面支持中文 / English 切换**（⚙ 设置 → 第一项「🌐 界面语言」）：英文环境下可整界面切英文。
翻译由 `scripts/add_i18n.py` 首次注入（词条来自 `scripts/i18n-en.json` 字典 + `i18n-en-patterns.json` 模板规则，**以后加词改这两个 JSON 后用 `scripts/sync_i18n.py` 同步**），
**学生姓名、队伍名、古诗、儿歌、词库、题库等内容一律不翻译**（可编辑区域自动跳过，防止英文覆盖用户数据）。
英文说明见仓库 `README.en.md`。

## 何时使用

- 老师要一个班级管理工具 / 班级小助手 / 班级工作台
- 老师要排座位表、小组积分榜、值日表、课表、随机点名、倒计时的网页
- 老师要为**具体班级**定制（如「三年级二班 38 人 6 组」）
- 已有一份班级小助手 HTML，要加功能或改内容

## 核心工作流（生成新班级）

### 第 1 步：问清班级信息

**逐项询问**（老师答不上来的项，先给合理默认并说明，不要卡住）：

| 必问 | 说明 | 默认 |
|---|---|---|
| 班级名 | 如「三年级二班」，显示在标题与导出文件名 | 一年级一班 |
| 学生人数 | 决定座位行数 | 40 |
| 小组数 | ＝座位列数，4~8 | 6 |
| 学生名单 | **强烈建议要**：每行 `姓名 男/女`；有名单才能用「男女交替排座」 | 占位名「学生01…」 |
| 课表 | 每天 12 节；给不出来就用默认，老师自己在设置里改 | 模板默认（语文/数学/英语…） |
| 常用模块 | 是否保留英语单词（非英语老师可能不用） | 全保留 |

询问时给老师一行示例格式，例如：
> 名单每行一人：`张明 男`（也可以只写姓名，性别后补）；课表每天一行：`周一|语文/数学/美术/英语/音乐/足球/班队会`

**年级信息**用于两处：计算页竖式难度（`#vertGrade` 1~6）与单词册别。问清年级后一并写入。

### 第 2 步：生成（AI 路线用脚本；自己动手的老师走网页版生成器）

```bash
python3 ~/.workbuddy/skills/class-management-workbench/scripts/customize.py \
  --class-name "三年级二班" \
  --names-file /path/roster.txt \
  --cols 6 \
  --schedule /path/sched.json \
  --out "~/Desktop/三年级二班-班级小助手.html"
```

参数说明见 `references/customize-params.md`。脚本会写入班级名、名单、性别、小组数、课表，并回显确认。

**老师要自己动手时**，给他 `templates/web-generator.html`（双击打开即用，不装任何软件）：
它的输出与 `customize.py` **逐字节一致**（每次发布都会做等价性验证），填三步即可拿到成品。

**默认一律用脚本改，不要直接编辑 HTML**——文件 40 万字符，手工编辑极易出错（详见 `references/iteration-rules.md`）。

### 第 3 步：交付前验证

生成后**必须**跑一遍验证（浏览器 + 名单核对），方法见 `references/verification.md`。至少确认：12 个页面都能打开、学生人数正确、无脚本报错。

### 第 4 步：告知老师怎么用

重点说四件事：
1. **双击打开即可**，不用联网；数据存在本机浏览器里。
2. ⚠️ **第一件事就做「绑定」**：⚙ 设置 → ④ 数据保存与找回 → 点「🔗 绑定程序文件」，
   选中正在用的这个 html 并允许覆盖。**这一步是防"第二天数据不见"的关键**：
   教室电脑常装系统还原（冰点还原），重启会清空浏览器数据；绑定后数据会写进 html 文件本身，
   第二天双击它数据自动回来，零操作。绑定后注意把文件放在 **D 盘 / U 盘 / 桌面**等不会被还原的位置。
3. **换名单/课表**：⚙ 设置 → ③ 学生名单 / ④ 课表。
4. **换电脑/备份**：设置④「⬇ 导出全部数据(.json)」；或顶栏 💾 导出「换机包」HTML，拷到新电脑双击。
   任何时候只要「⬆ 导入数据包(.json)」就能完整恢复（该文件含全班所有数据）。

## 迭代已有 HTML

老师要在已有版本上加功能或改内容时，先读 `references/iteration-rules.md`（改这个文件的硬性纪律）和 `references/modules.md`（12 个模块的实现要点与数据结构）。概要：

- 改动一律用 **Python `read / replace(assert count==1) / write`**，改完复核；不要依赖编辑工具的「保存成功」提示
- 改完跑 `node --check` 与 CSS 括号配平
- 涉及**派生数据**（如小组成员来自座位表）时，同步点要接在三处：全局重绘前、`save()` 开头、以及只调局部渲染的那些入口
- 提示文字：大屏页能删则删，保留的 ≤1 行 ≤28 字，详细说明进 `title` 悬浮
- **数据持久化**（第十一轮定稿）见 `iteration-rules.md` 第九章：教室电脑会「还原」，
  数据不能只靠 localStorage，必须支持「绑定程序文件后自动写回」+「全量 .json 数据包」+「开机找回」。
  三条铁律：内嵌数据脚本要插在 **`<body>` 之后**（否则 `load()` 读不到）；
  剥离旧注入**必须用 DOM 节点删除，不能用文本正则**（会删掉程序自身代码）；
  写盘前先自检生成内容，不合法就拒绝写。

## 同步维护者自己的模板（可选）

若把本地在用的「班级小助手」当母版更新技能模板，**不要手工改模板**，跑脱敏脚本：

```bash
python3 ~/.workbuddy/skills/class-management-workbench/scripts/build_template.py \
  "/path/你的班级小助手.html"
```

脚本做 8 项脱敏并自检（真实名单 → 40 个占位名；真实课表 → 中性示例；设置③ 示例姓名 → 张明/李红/王芳；
localStorage KEY、IndexedDB 名、内嵌数据全局变量、数据脚本 id 全部改为 `class_helper_v1` / `__CLASS_*` 系），
最后校验 customize.py 依赖的锚点是否齐全。**任何一项未命中就报错退出**，不会产出半成品模板。

## 2.5.0 更新（2026-11-10）· 一处脚本中断导致多按钮集体失效 + 抽卡概率回归

**本版本合并了原 2.4.2 的全部修复（未单独发布）与本轮抽卡概率改版。**
**本次修的是缺陷，不是新功能。⚠️ 2.4.0 / 2.4.1 生成的班级都带这个缺陷，请用 2.5.0 重新生成一份。**

- 现象（多位老师会遇到）：⚙ 设置里的「📦 导入数据包」、右上角「⬇ 导出换机包」、「🚀 立即生成」、竞赛页「↺ 重置比赛」等按钮**点了没有任何反应**；竞赛页看起来"还没开始就有小组加分"（其实是重置没生效）
- 根因：值日加分动画的弹层节点被插在两个 `<script>` 块**之后**，脚本顶层对它绑定事件时拿到 `null` 抛错 → **整块 717KB 脚本从那一刻中断**，之后定义的所有按钮绑定全部丢失
- 修复：弹层节点移到脚本块之前 + 绑定改成守卫式（`const el=$('#x'); if(el) el.addEventListener(...)`）
- 新增发版闸门 `scripts/smoke.cjs`（见 `references/verification.md` 1h）：静态查「绑定早于节点」、运行时抓 `window.onerror`、用顶层 `let` 的 TDZ 判定脚本是否被中断；退出码非 0 不发版
- 模板、`templates/ready-to-use-workbench.html`（空白班）、`templates/web-generator.html`（网页版生成器）三处产物均已用修复后的模板重建，逐字节校验一致
- 🆕 竞赛页新增**轮次语义**：工具栏多一枚状态牌（`⏸ 本轮未开始` / `🚀 今日 +N · 累计 M 分` / 红框 `⚠️ 有往日残留分数`、`⚠️ 已 N 天未开新一轮`），「重置比赛」改名为「🆕 开始新一轮」（清分数 + 清完成记录 + 清今天的 `pkDaily` 账本 + 记 `pk.roundStart`）。解决"跨天残留分数让人误以为没开始就有分"——现在页面自己会说清楚
- 🎒 抽卡页**权益背包**改版：单卡从 297×379 缩到 274×162（面积约为原来四成），一行固定 12 张；卡名省略号截断、说明最多两行，「使用」按钮仍保留 52px 触摸高度不缩水。同时修掉"下面的卡滚不出来"——`#gachaPriv` 原本写死 `height:35vh; overflow:hidden`，在它自己的滚动容器里又裁了一刀，39 张卡时有 27 张被切掉且滚不到；改为交给 `.gacha-bottom-scroll` 统一滚动后，滚到底末卡完整可见

- 🔤 **抽卡页英文界面补词**（+17 条字典 + 9 条模板规则）：`使用`、`宠物收藏`、`🎒 权益背包`、`🎒 权益 / 🏅 等级`、`🎲 单抽 / 🎁 十连`、`⚡ 保底`、`已收集 A/B 张（N%）`、`🎒 X 的权益背包（N 张）`、空背包提示、`NN 姓名（N分）`选项等。**卡片名/说明与学生姓名仍按设计保留中文**。加上本轮概率改版的文案，英文词条现共 **967 条字典 + 109 条模板规则**（唯一来源 `scripts/i18n-en.json` / `i18n-en-patterns.json`）
- 🛡 **新增两道防漂移闸门**：`scripts/check_template_drift.py`（模板必须等于程序重新脱敏的结果，2026-11-10 发现模板已悄悄落后本班程序 **36 个代码块**）与 `scripts/sync_i18n.py`（英文词条以两个 JSON 为唯一来源，`--check` 可当闸门）。发版命令由 3 条增至 5 条，见 `references/verification.md` 1h/1i
- 🎲 **抽卡概率回归「只看稀有度」的偏态长尾**：原先积分等级会**改写概率**——`gachaFloor()` 按等级发"保底档"，等级越高的学生 N/R 卡被一路顶成 SR，实测 Lv21 学生 SR+ 高达 98%、几乎抽不到 N 卡，与"越稀有越难抽"相反。现在删掉 `gachaFloor`/`applyFloor`，每次抽都按 `rarityWeight`（N 60 / R 27 / SR 10 / SSR 3）加权，**与各人等级无关**（800 抽 × Lv1/3/5/21 实测 SR+ 极差仅 1.6 个百分点，四档仍单调递减）
- ⚡ **保底改成与等级无关的「软保底」**：`state.pity[学生id]` 只记录**连黑次数**，连续 9 次没出 SR 及以上 → 第 10 次必出 SR/SSR（全班公共池记在 `-1`），十连仍保留"最多 1 张 SSR"上限。**Why:** 孩子连黑十几次会直接放弃抽卡，体验需要兜底，但兜底不能靠"等级高就发好卡"这种惩罚努力的反向激励。**How to apply:** 计数器跟着 `save()` 与换机包走，老存档缺 `state.pity` 时由 `draw()` 惰性补齐（首启/迁移两条路都要跑）；要调"兜底快慢"只改 `GACHA_PITY_SR`
- 👀 **概率写在明面上**：抽卡页信息条原来那枚 `⚡ 保底 SR SSR`（描述的是已经不存在的机制）换成 `⚡ 概率 N 56% R 32% SR 9.4% SSR 2.0%`，由 `rarityWeight` 实时算出——改权重不用改文案；旁边一枚 `⚡ 连黑 8/9 · 再抽 2 次必出 SR`，只剩 2 次时红底高亮，悬浮说明写明"与积分等级无关"
- 🕵️ **新增脱敏闸门 `scripts/check_desensitization.py`**：发版前扫描发布目录里的真实学生/学校/老师姓名与本地路径（`/Users/<真实名>/`、`/Volumes/<真实名>/`、`C:\Users\<真实名>\`），并**解开网页版生成器里的 base64 模板**一起扫；命中即退出码 1，**不许发布**。名单直接从程序的 `STUDENT_NAMES` 读取（脚本自身不带名单），额外禁忌词放 `scripts/desensitization.local.json`（已进 `.gitignore`，不要提交）。**Why:** 本轮排查发现已公开的 GitHub 仓库里 `templates/class-workbench-template.html` 被误换成了**未脱敏的本班程序**（含 34 个真实学生姓名），而此前 5 条发版命令全都查不出来——它只测功能，不测隐私。**How to apply:** 发版命令由 5 条增至 6 条，脱敏扫描必须**先于**冒烟与等价性通过
- 🔑 **存储标识符里的校名缩写全部清出发布物**：母版程序的 localStorage 键名、两个 IndexedDB 库名、sessionStorage 标记、内嵌数据 `<script>` 的 id 与 `window.__×××_EMBEDDED_STATE__` 等 5 个全局变量前缀，历史上都带本校缩写；而 `build_template.py` 的「历史标识符替换」一步在 `scripts/legacy_ids.json` **缺失时只会静默跳过**，于是这些缩写着连续几个版本原样出门（v2.4.0 的已上架包里就有）。现在：① 建好本机专用（不入库）的 `scripts/legacy_ids.json`，7 条映射一次替换 42 处；② 跨版本读取的前缀改成字符类 `[A-Z]{2,12}`（不再硬编码缩写，`parseMigPack` 与换机包识别同步改）；③ 脱敏闸门把缩写列为西文禁词（先抹 base64 噪声再按标识符边界匹配，避免在头像图片的随机字符里假命中）。**本机程序一个键名都没改**——改了会丢本班数据与已绑定的文件句柄，脱敏只发生在生成模板时

## 2.3.1 更新（2026-10-15）· 英文界面质量完善

1. 🔤 **模板规则支持嵌套翻译**（`$Dn`）：如「第1节 · 数学」→ `Period 1 · Math`（此前课程名会残留中文）
2. 🎨 **补齐遗漏词条**：队伍名（`Group 2 Orange`）、奖牌队名、值日标题（`Thursday duty list`）、空状态提示、单元册别前缀（`1A · …`）
3. 🐞 **修两个引擎缺陷**：① 单字符词条（如颜色字「橙」）被过滤掉导致嵌套翻译失效；② 重复的模板规则使先注册的旧规则抢先匹配
4. ✅ 复验：英文模式下 12 页仅剩**应当保留**的中文（学生姓名、古诗、儿歌、教材单元名、可编辑队伍名），其余全部英化；中英文双模式 12 页零溢出、0 异常；生成器与脚本版输出仍逐字节一致

## 2.3.0 更新（2026-10-14）· 中英文双语界面

1. 🌐 **界面语言切换**：⚙ 设置第一项可在「🇨🇳 中文 / 🇬🇧 English」之间切换，**整界面（导航、按钮、提示、弹窗、问答、toast）随语言变化**，选择记入存档（`state.lang`）
2. 🔒 **内容不翻译**：学生姓名、队伍名、古诗、儿歌、词库、题库、卡片池等**一律保持原样**；`contenteditable` 区域（班级名、课表格、队名）自动跳过，避免英文覆盖老师的数据
3. 🧩 **实现方式**：`scripts/add_i18n.py` 注入 i18n 引擎（869 条字典 + 89 条模板规则），DOM 文本节点精确匹配替换、原文存 `__zh` 属性、切回中文逐字还原；`MutationObserver` 自动补译动态渲染内容
4. 📘 **英文说明**：仓库新增 `README.en.md`

## 2.2.0 更新（2026-10-14）· 面向「好上手」的改版

针对市场审核反馈（"操作门槛高 / 提示信息要查文档 / 缺通俗问答"）做了四条：

1. 🌐 **新增「网页版生成器」**（`templates/web-generator.html`）：填班级名/名单/组数/课表 → 浏览器内生成 → 下载成品。**零安装、零命令、离线可用**；输出与 `customize.py` 逐字节一致（有等价性验证保障）
2. 📄 **新增「空白班」通用文件**（`templates/ready-to-use-workbench.html`）：双击即用，设置③贴名单即可，为完全不想折腾的老师准备
3. ❓ **程序内置「遇到问题」面板**（右上角 ❓，12 条大白话问答）+ `references/faq-for-teachers.md`
4. 💬 **老师可见文案全面体检**：提示条统一"主句 + 做法 + 原因折叠"格式；默认示例课表改为**作息对齐**（含升旗/上操，换季演示正常）

同时修复两个真实问题：

5. 🐞 **课表换季会把自定义课表重置**：首次切到另一季节时，原实现用内置默认课表生成 → 老师自排的课表被整套覆盖。现改为**由当前课表按新作息重排**（课程内容与备注全保留，只移动升旗/上操位置），并给保存按钮加上目标季节文案（「💾 保存到 ❄️ 冬季课表」）
6. 🐞 **写回权限失败无法自助恢复**：浏览器权限不跨页面重载，原自动写回失败后只提示"重新绑定"。现新增「🔓 立即恢复写入」一键按钮（打开页面时预检 + 点页面任意处自动恢复 + 恢复后自动补写）

## 2.1.1 修复（2026-10-10）

- 🐞 **生成的文件页头显示错误班名**：页头大标题是 HTML 里的静态文字，`customize.py` 此前只替换了 JS 里的默认值、没替换它 → 生成出来的文件页头一直显示模板默认的「一年级一班」，必须等老师在设置里点一次"应用"才会变。现在：① `customize.py` 同时替换页头静态文字；② **主程序启动时也会用存档里的班级名自动同步页头**（旧文件直接受益，无需重新生成）

## 2.1 版本（2026-09-26 发布；含 2.0 全部内容）

**2.1 是在 2.0 之上做了「全量按钮逐个点击回归」后的修复版**，三项实质修复：

1. 🐞 **课表导入必然失败**：Markdown 表格行首尾的 `|` 会切出空串，导致时段标签取到空值、整张表被跳过——「📋 填示例 → 💾 应用课表」点完毫无变化。现已支持 Markdown 表格 / 纯文本 / 无首尾竖线表格 / CSV 四种格式
2. 🐞 **抽卡整条链路不可用**：`#gacha1`（单抽）/`#gacha10`（十连）/`#revealClose`（收下啦）三个按钮**从未绑定过事件**（历史遗留），点了没反应、弹层打开后还关不掉。已补绑定并支持点空白 / Esc 关闭
3. 🐞 **高积分学生抽卡崩溃**：等级改成无上限后 `LEVELS[idx]` 会越界（数组只有 5 项），积分 ≥100 分必抛 `Cannot read properties of undefined`。已加 `lvName()`/`lvIdxClamped()` 安全取值

以下为 **2.0 起累计的全部增强**（2.1 均包含）：

相对 1.0 的主要变化，迭代旧版页面时可参考 `references/iteration-rules.md` 第十八章（批量改写 CSS 吃掉 @media/@keyframes 头的事故与纪律）：

1. **动物头像等级系统**：12 种水彩小动物（兔/狗/猫/象/马/熊/海豚/猴/熊猫/考拉/鹦鹉/鹿）随机认领（均衡分配、可整班重抽、带防误按确认）；积分卡＝动物头像＋星星点亮行＋Lv 徽章，`POINTS_PER_STAR` 分一颗星、`STARS_PER_LEVEL` 颗星升一级，**星数与 Lv 均无上限**；卡片底色按动物主色微调（`TINTS` 色表），升级有 toast 与光效
2. **大屏统一适配**：`:root{--fs:1}` + `@media (min-width:2400px){:root{--fs:1.8}}`，≥2400px（3480 大屏）整体 1.8 倍、1920 笔记本完全不变；按钮强制 `white-space:nowrap` 单行
3. **值日页**：删掉了大标题行（其余页面本就没有标题）；学号深蓝 #1d4f9e
4. **作业页**：四象限每科一个独立字号滑杆（放在各自彩色卡片里，12~64 基准，大屏 ×1.8，默认 36＝大屏 64.8px 约 5 米可读）；`state.hwFontSize={语文,数学,英语,其他}` + `state.hwFit` 自动适应（内容多时逐科二分缩到刚好装下，不溢出）；**输入必须即时写 state**（`flushHwInputs()` 在 `renderHomework()` 开头收回 DOM 值），否则任何一次 `rerenderAll()` 都会把输入冲掉
5. **小组竞赛**：任务分值不再固定——点任务按钮上的「+N」即可改（1~99，默认语文/数学/英语各 2 分），改后已点亮人数会按新分值重算
6. **课表导入**：修掉 `parseSchedContent` 对 Markdown 表格的解析失败——行首尾的 `|` 会各切出一个空串，须 shift/pop 去掉，否则时段标签取到空串、整表被跳过（表现为「📋 填示例 → 💾 应用课表」无反应）。现在 Markdown 表格 / 纯文本 / 无首尾竖线表格 / CSV 四种格式都能解析
7. **抽卡**：`#gacha1`/`#gacha10`/`#revealClose` 三个按钮此前从未绑定（历史遗留，抽卡整条链路不可用、弹层关不掉），已补 `bindGacha()` 并支持点空白/Esc 关闭；新增 `lvName()`/`lvIdxClamped()` 防等级无上限后 `LEVELS[idx]` 越界崩溃
8. **媒体查询纪律（重要教训）**：批量改写 CSS 前先 `grep -c '@media'` 记数，改完必须与备份一致——曾因改写吃掉 7 个 `@media` 头导致窄屏规则全局生效

## 资源

- `templates/web-generator.html` — **网页版生成器**（含内嵌模板，双击即用；由 `scripts/build_web_generator.py` 从模板构建；★ 若包内未随附，跑该脚本即可现场生成，功能完全等价）
- `templates/ready-to-use-workbench.html` — **空白班**现成文件（40 个占位名，老师贴名单即用；★ 若包内未随附，用 `scripts/customize.py --count 40` 现场生成，功能完全等价）
- `references/faq-for-teachers.md` — 给老师的通俗问答（与程序内 ❓ 面板同源）
- `scripts/i18n-en.json` + `scripts/i18n-en-patterns.json` — **界面英文词条的唯一来源**（967 条精确匹配 + 109 条模板规则）；程序与模板里内嵌的 `I18N_DICT` / `I18N_PAT` 只是它的副本，**改词条只改这两个 JSON**，再跑 `sync_i18n.py`
- `scripts/add_i18n.py` — 把中英文切换**首次注入**程序（一次性：检测到 `applyLang` 就拒绝再跑）
- `scripts/sync_i18n.py` — **防漂移闸门**：把两个 JSON 同步进程序/模板（`--check` 只报告）。字典按键值语义比、模板规则按字节比（顺序即语义）
- `scripts/check_template_drift.py` — **防漂移闸门**：现场重算模板并逐字节比对，报告程序与模板的差异块（`--fix` 重建）。模板只许由 `build_template.py` 生成，不许手抄
- `templates/class-workbench-template.html` — 脱敏后的程序模板（约 910 KB，2.0 起内嵌 12 张动物头像，无任何真实学生/学校信息）
- `scripts/customize.py` — 按班级信息定制模板（生成成品）
- `scripts/build_template.py` — 反向：把真实程序脱敏成模板（含自检）
- `scripts/check_desensitization.py` — **脱敏闸门**：扫描发布目录里的真实姓名与本地路径（含 base64 内嵌模板），命中即非 0 退出。`--program 班级小助手.html 目录…`；名单从程序读取，禁忌词另存 `desensitization.local.json`（不提交）
- `references/customize-params.md` — 脚本参数与名单/课表格式
- `references/modules.md` — 12 个模块的功能、数据结构、关键函数
- `references/iteration-rules.md` — 修改该文件的安全纪律（必读）
- `references/verification.md` — 浏览器验证与量测方法
- `scripts/smoke.cjs` — **发版闸门**：`node scripts/smoke.cjs 程序.html`，静态+运行时双重扫描（绑定顺序 / 未捕获错误 / 脚本中断 / 全量点击），退出码非 0 不许发版（见 verification.md 1h）

## 隐私红线

- 模板与技能包内**不得出现任何真实学生姓名、学校名、教师姓名**
- **发版前必须跑 `python3 scripts/check_desensitization.py --program 班级小助手.html <发布目录…>`，0 命中才允许出门**（它同时扫 base64 内嵌模板；命中即 exit 1）
- `scripts/desensitization.local.json`（本机禁忌词清单）**不入库、不进包**；`_skillhub_meta.json`、`scripts/legacy_ids.json` 同理
- 分发给其他老师前，确认名单已替换、localStorage/全局变量名不含学校缩写
- 老师自己的名单只存在他本机浏览器里，不外传
- ⚠️ 真实姓名一旦被提交进公开仓库，**覆盖文件不等于撤回**——历史提交仍然可见，需改写历史 + 强推，且要先征得用户同意
