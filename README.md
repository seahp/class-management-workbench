# 班级管理工作台生成器

<p align="center">
  <img src="screenshots/icon.png" width="128" alt="图标">
</p>

> **English version: [README.en.md](README.en.md)** ｜ 中文版见下

> 给中小学班主任的**单文件离线班级管理工作台**生成器。
> 一份 HTML 页面装下 12 个班级管理模块，双击即用、不联网、数据存本机，适配教室触摸大屏。

<p align="center">
  <img src="screenshots/01-seating.jpg" width="46%" alt="座位页">
  <img src="screenshots/02-points.jpg" width="46%" alt="积分页">
</p>
<p align="center">
  <img src="screenshots/04-competition.jpg" width="46%" alt="小组竞赛">
  <img src="screenshots/03-timetable.jpg" width="46%" alt="课表页">
</p>

## 功能一览

| 页面 | 能做什么 |
|---|---|
| 🪑 座位表 | 拖动排座、3 套方案随时切换、按周自动轮换、男女交替 |
| ⭐ 积分榜 | 加减分（可到负分）、等级奖章、动物头像随机认领 |
| 🏁 小组竞赛 | 按座位列自动分组、点任务点亮、全组完成发射火箭 🚀 |
| 🧹 值日表 | 岗位轮换、班级岗、教师临时调整 |
| 📅 课表 | 夏/冬两套、支持粘贴表格导入、配套校园儿歌 |
| 📝 作业 | 四象限（语文/数学/英语/其他）、每科独立字号（5 米可读） |
| 📜 古诗诵读 | 内置古诗库、今日晨读、随机一首 |
| 🧮 计算练习 | 口算 / 竖式 / 脱式，可自定义题库；除法自动整除 |
| 📚 英语单词 | 内置换词表、艾宾浩斯复习计划、三色记忆卡 |
| 🛠 工具 | 随机点名、倒计时 |
| 🏆 排行榜 | 今日/昨日/本月积分排行 |
| 🎁 抽卡奖励 | 积分兑奖、图鉴收集、保底机制 |

**界面支持中文 / English 切换** —— ⚙ 设置 → 🌐 界面语言。学生姓名、古诗、儿歌、词库等内容不翻译。

## 安装（挑最省事的一条）

| 途径 | 适合谁 | 怎么做 |
|---|---|---|
| 🌐 **网页版生成器**（零安装） | 不想装任何东西的老师 | 打开 **[在线版](https://seahp.github.io/class-management-workbench/)** 或双击本仓库 `docs/index.html` → 填班级名/名单/组数 → 点生成 → 下载成品。**全程浏览器内完成** |
| 📄 **空白班文件**（最省事） | 只想马上能用的老师 | 下载 [`examples/班级小助手-通用版.html`](examples/班级小助手-通用版.html) → 双击打开 → ⚙ 设置 → ③ 贴自己班名单 |
| 🤖 **AI 助手生成** | 有 AI 助手的老师 | `skillhub install class-management-workbench --namespace user_1db801dd` · [技能页](https://skillhub.cn/skills/class-management-workbench) → 对 AI 说"给三年级二班做个班级小助手" |
| 🧑‍💻 **源码 / 二次开发** | 开发者 | `git clone https://github.com/seahp/class-management-workbench.git`，用 `scripts/customize.py` 生成 |

> 四条路产出的文件完全一样（网页版与脚本版输出**逐字节一致**，有自动化验证保障）。

**遇到问题？** 程序右上角 **❓** 有 12 条大白话问答；完整版见 [`references/faq-for-teachers.md`](references/faq-for-teachers.md)。

## 快速开始

### 方式一：直接体验（无需任何工具）

下载 [`examples/三年级二班-示例.html`](examples/三年级二班-示例.html)（虚构班级 36 人），双击用浏览器打开即可。

### 方式二：为自己的班级生成（Python 3）

```bash
# 1) 克隆
git clone https://github.com/<你的用户名>/class-management-workbench.git
cd class-management-workbench

# 2) 生成（把 roster.txt 换成你的名单：每行「姓名 男/女」）
python3 scripts/customize.py \
  --class-name "三年级二班" \
  --names-file roster.txt \
  --cols 6 \
  --out ~/Desktop/三年级二班-班级小助手.html
```

生成的文件**双击即用**，可以直接发给同事、拷到教室电脑。

### 方式三：作为 AI 技能使用

本仓库同时是一个 Agent Skill：让 Claude Code / WorkBuddy 等支持技能的 AI 助手读取 `SKILL.md`，
然后直接对它说：

> 给三年级二班做一个班级小助手，38 人，6 个组

AI 会自动完成名单整理、生成、验证全流程。

## ⚠️ 关于数据保存（请先读这一段）

- 数据**保存在本机浏览器里**（localStorage），不上传任何服务器
- 换电脑 / 备份用页面里的「⬇ 导出全部数据」或「📄 导出换机包」
- **教室电脑如果装了还原卡（冰点还原、系统还原）**：关机后浏览器数据会被清空，
  请在程序里点一次 **⚙ 设置 → ④ 数据保存与找回 → 🔗 绑定程序文件**，
  之后每改一点都会自动写回这个 HTML 文件，第二天双击它数据自动回来
- 建议把程序和备份都放在**同一个固定文件夹**（如 D 盘），不要放在会被还原的系统盘

## 常见问题

**Q：一定要联网吗？**
不用。整份页面零外部依赖，离线完全可用，适合断网的教室环境。

**Q：教室大屏（希沃一体机）能看清吗？**
字体随屏幕宽度自动放大（≥2400px 时整体 ×1.8），作业页每科还能单独调字号，默认 5 米外可读。

**Q：能把数据同步到手机上吗？**
本工具定位是"教室大屏 + 老师电脑"的离线工具，手机端建议直接用浏览器打开同一个文件（数据各存各的）。
多端汇总请用导出/导入。

**Q：学生信息会上传吗？**
不会。整个程序不含任何网络请求，学生数据只存在你自己的电脑里。

## 目录结构

```
├── docs/index.html           # 网页版生成器（GitHub Pages 源）
├── SKILL.md                  # AI 技能说明（含完整使用/定制指引）
├── scripts/
│   ├── customize.py          # 一键定制：班级名 / 名单 / 组数 / 课表 → 生成 HTML
│   └── build_template.py     # 维护用：从主程序重新生成脱敏模板
├── templates/
│   └── class-workbench-template.html   # 脱敏模板（无任何真实班级数据）
├── examples/                 # 生成效果示例（虚构班级）
├── references/               # 模块实现说明 / 迭代纪律 / 验证清单
└── screenshots/
```

## 更新日志

- **v2.2.0** — 更好上手：新增**网页版生成器**（零安装）与**空白班文件**；程序内置 **❓ 遇到问题**问答面板；修复课表换季会重置自定义课表、写回权限失败无法自助恢复
- **v2.1.1** — 修复：生成的文件页头一直显示默认班名（现在生成时替换 + 启动时按存档同步）
- **v2.1.0** — 修复：课表 Markdown 表格导入失败；抽卡三个按钮未绑定；高积分学生抽卡报错
- **v2.0.0** — 动物头像等级系统（12 种水彩小动物、星星升级、Lv 无上限）、3480px 大屏 1.8 倍适配

## 许可

[MIT](LICENSE)

---

_Author: 粉笔与代码 · 一个一线老师写给同行的小工具_
