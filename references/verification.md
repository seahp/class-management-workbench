# 生成后的验证方法

## 一、静态自检（必做）

```bash
awk '/<script>/{f=1;next} /<\/script>/{f=0} f' out.html > /tmp/check.js && node --check /tmp/check.js && echo "JS OK"

python3 -c "
import io,re,collections
s=io.open('out.html',encoding='utf-8').read()
c=re.search(r'<style>([\s\S]*?)</style>',s).group(1)
print('CSS braces', c.count('{'), c.count('}'))
ids=re.findall(r'\bid="([a-z][A-Za-z0-9_-]*)"',s)
print('dup ids', [k for k,v in collections.Counter(ids).items() if v>1])
print('size %.1f KB'%(len(s.encode('utf-8'))/1024))
"
```

预期：JS OK；CSS 括号相等；重复 id 只有 `saveState`（历史遗留，无影响）。

### 1b. 动画与媒体查询记数（2026-09-23 新增，防"动画全灭/布局串规则"）

```bash
grep -c '@media' 文件.html; grep -c '@keyframes' 文件.html
```
- 记下这两个数；任何一次改动后**必须与之前一致**（或能解释增减原因）
- `animation:XXX` 的每个引用都必须有同名 `@keyframes XXX`，缺失＝该动画静默失效（无报错）
- 浏览器侧复核：`[...document.styleSheets[0].cssRules].filter(r=>r instanceof CSSKeyframesRule).length`

### 1c. 交互元素绑定审计（2026-09-26 新增，抓"点了没反应"的哑按钮）

生成程序后，用脚本比对「HTML 里所有带 id 的按钮」与「JS 里是否引用过它」，把没有引用的列出来人工核对：

```python
import re
s=open('程序.html',encoding='utf-8').read()
js='\n'.join(re.findall(r'(?m)^\s*<script[^>]*>(.*?)^\s*</script>', s, re.S))
btns=re.findall(r'<button[^>]*?(?<![-\w])id="([^"]+)"', s)     # 注意排除 data-page-node-id
for b in btns:
    if ('#'+b) in js or ("'"+b+"'") in js or ('"'+b+'"') in js: continue
    print('疑似哑按钮:', b)
```
- **必须人工复核**：拼接式 id（`'seatPlan'+i`）、字典键遍历（`Object.keys(IMPORT_EXAMPLES).forEach`）、事件委托（`#tabs` / `#bottomNav`）都是正常写法，会误报
- 2026-09-26 真事故：`#gacha1`（单抽）/ `#gacha10`（十连）/ `#revealClose`（关闭开奖弹层）**从未绑定**，抽卡整条链路不可用、弹层打开后关不掉，且历史多个版本都缺，靠用户问"抽卡功能正常吗"才暴露
- 还要顺手检查"按等级/下标取数组"的地方：等级上限改成无上限后，`LEVELS[idx]` 这类固定长度数组必须 `Math.min(idx, MAX_LEVEL)` 夹一下，否则高分学生触发 `Cannot read properties of undefined`

### 1d. 运行时全量点击扫描（2026-09-26 新增，逐个按钮点一遍）

静态审计只能抓"完全没引用"的哑按钮，抓不到"绑定了但点了没效果"。生成程序后跑一遍运行时扫描：

```js
// 插入 </body> 前的探针骨架（Edge headless --dump-dom 读 <pre id="ALL">）
const tabs=[...document.querySelectorAll('section.tab')].map(s=>s.id.replace('tab-',''));
for(const tn of tabs){
  switchTab(tn); await sleep(160);
  const root=document.getElementById('tab-'+tn);
  for(const b of [...root.querySelectorAll('button')].filter(vis)){
    const f0=fp(), h0=root.innerHTML;         // ★ 用 innerHTML 全文，不要只比长度
    b.click(); await sleep(70);
    if(errs.length>e0) 记录报错;
    else if(fp()===f0 && root.innerHTML===h0) 记录"疑似无反应";
    closeMasks(); switchTab(tn);              // 有些按钮会跳页，拉回来继续
  }
}
```

**指纹 fp() 必须包含**：当前激活 tab（`section.tab.active`）+ `JSON.stringify(state).length` + toast 文本 + `.show` 元素数。
少任何一项都会大面积误报。

**"疑似无反应"的 6 种常见误报（必须人工复核，不能直接判 bug）**：

| 现象 | 真实原因 |
|---|---|
| 页面子页切换按钮没反应 | 它只改 DOM 的 `.hide`，**不写 state** → 用 state 指纹必然误判，要改比 `classList.contains('hide')` |
| 「📋 填示例」类按钮没反应 | 它写的是 `textarea.value`，**不进 innerHTML** → 要单独读 value 验证 |
| 「💾 应用/导入」类按钮没反应 | 需要**先在对应文本框填内容**，空内容时提示格式说明是正确行为 |
| 默认子页 / 当前分类按钮没反应 | 点击时已是该状态，本就无变化 |
| 「重置/清空」类按钮没反应 | `confirm` 被自动拒绝 → 要**先造出数据**再让 `confirm` 返回 true 才测得到 |
| 导航按钮全部"没反应" | 切页不改 state → 必须把激活 tab 放进指纹，并单独断言"点击后 curTab === 期望值" |

**探针自身的两个语法坑**：① `forEach` 回调里不能 `await`（改 `for` 循环）；② `(async function(){...})()` 别漏 `})();`，否则整块静默不执行、输出永远是 PENDING（先 `node --check` 校验探针块）。

**本次真产出**：靠这套扫描挖出 `parseSchedContent` 的 Bug——Markdown 表格行首尾的 `|` 会各切出一个空串，未去掉时时段标签取到空串（真正的「第1节」被挤到第 2 列），于是每一行都被跳过、整表解析失败。**「📋 填示例 → 💾 应用课表」必然失败**正是这个原因。修法：`if(hasPipe){ if(cells[0]==='') cells.shift(); if(cells.at(-1)==='') cells.pop(); }`（`toFieldRows` 本来就有这段，`splitCells` 的调用方没有）。

### 1e. 覆盖盲区提醒
- **设置面板是浮层**（`#settingsMask`，齿轮打开），不在 `section.tab` 里 → 逐页扫描会**整页漏掉**，必须单独打开后 BFS 多轮扫描（点开折叠区会冒出新按钮）
- **不是所有控件都是 button**：作业页是 `input[type=range]` ×4 + checkbox，要单独派发 `input`/`change` 事件验证
- 文件/目录选择、导出下载类按钮要跳过点击（headless 会挂起或在 Downloads 留文件），用静态引用确认即可

### 1f. 网页版生成器等价性验证（2026-10-14 新增，发版必跑）

`templates/web-generator.html` 与 `scripts/customize.py` 是**两套实现、同一产物**，改任一侧都必须验等价：

```bash
# 脚本版参照
python3 scripts/customize.py --class-name "三年级二班" --names-file roster.txt --cols 6 --out /tmp/ref.html
# Python 侧哈希（注意用 UTF-8 字节，不要用 len(str)——emoji 的码点/码元计数不同）
python3 -c "
import io
s=io.open('/tmp/ref.html',encoding='utf-8').read(); h=5381
for x in s.encode('utf-8'): h=((h*33)+x)&0xFFFFFFFF
print(len(s.encode('utf-8')), h)"
```

浏览器侧用 CDP：`Runtime.evaluate` 调 `window.__GEN_BUILD__({className,roster,cols})`，
返回 `new TextEncoder().encode(html)` 的**字节数 + 同一个 djb2 哈希**，与脚本版比对。
**两者必须完全相等**（2026-10-14 实测：978075 字节 / 哈希 3902156634，逐字节一致）。

> ⚠️ `__GEN_BUILD__` 现在返回的是**对象** `{html, roster, cols, className}`，直接 `TextEncoder().encode(返回值)` 会得到 `"[object Object]"`（15 字节）——必须对 `r.html` 取哈希。2026-11-10 实测：1097459 字节 / 哈希 2223092700，浏览器侧与 `customize.py` 侧逐字节一致。

> ⚠️ **`__GEN_BUILD__` 的入参形状是等价性测试的头号坑**（2026-11-10 在这里连踩四次）：
> `roster` 必须是 **`[["张明","F"],["李红","M"], …]` 这种「姓名 + M/F 代码」的数组**，不是「张明 女」那种原始行文本。
> 性别归一化由页面里的 `parseNames()` 完成，而 `parseNames` **封在 IIFE 内、不是全局函数**，探针调不到；
> 对外接口只有 `window.__GEN_BUILD__`。三种错法与症状（每种都能一眼认出）：
> · 传**字符串化的 JSON**（`__GEN_BUILD__("{…}")`）→ `opt.roster` 取不到 → 回落成 40 个占位名，产物**大 300 字节**；
> · 传 `["张明 女", …]`（字符串数组）→ 内部取 `r[0]`/`r[1]` 拿到的是**第 1、2 个字**，姓名被切成单字；
> · 传 `[["张明","女"], …]`（没转 M/F）→ 每个性别多 2 字节，20 人**恰好差 40 字节**。
> 判定口径：字节数只差几十/几百而 `roster.length` 对得上时，先怀疑**探针入参**，不要怀疑应用。

> ⚠️ 两个坑：① 比对要用 **UTF-8 字节 + 字节哈希**，`str.length` 在 JS（UTF-16 码元）和 Python（码点）对 emoji 计数不同，会误判"不一致"；
> ② 改模板后必须**重建生成器**（`build_web_generator.py`），否则生成器里内嵌的还是旧模板。

### 1g. 技能包发布前检查（2026-10-14 新增）

- **包内文件名必须全 ASCII**：`zip` 命令在 macOS 上不会给中文文件名打 UTF-8 标志位，Windows 解压会变乱码（实测 `references/faq-给老师.md` → `faq-τ╗ÖΦÇüσ╕ê.md`）。中文显示名写进 SKILL.md 说明即可，文件名用英文
- **本地专用文件不能进包**：`scripts/legacy_ids.json`（本机历史标识符映射）、`scripts/desensitization.local.json`（本机禁忌词清单）、`_skillhub_meta.json`（含本地路径）三份文件都**不入库、不进包**；
  `pack_for_open_platform.py` 的 `SKIP_NAMES` 已列全，手工 `zip` 时要用 `-x` 排除。仓库与包内只放 `.example` 版本
- **体积 ≤3MB**：加了大文件后要复测（当前 2.2.0：原始 3.2MB → 压缩 1.57MB）
- **解压后跑一遍端到端**：从 zip 解出 → `customize.py` 生成 → 浏览器冒烟（12 页零溢出 + 关键功能）

### 1h. 冒烟闸门 `scripts/smoke.cjs`（2026-11-10 新增，**发版必跑，不许跳过**）

上面 1c/1d 是"脚本骨架 + 人工核对"，容易凭印象跳过。1h 把它们合成一个可执行闸门，**一条命令出结论，非 0 退出码即不准发版**：

```bash
node scripts/smoke.cjs 程序.html                    # 默认 3480,2160（教室大屏）
node scripts/smoke.cjs 程序.html --size 1920,1080 --out 报告.json --keep
```

退出码：**0 全绿 / 2 只有警告 / 1 硬失败**。硬失败项只有三类，全部对应真实事故：

| 硬失败 | 抓的是什么 | 本次事故里的表现 |
|---|---|---|
| `★绑定早于节点` | 静态：`$('#id').addEventListener` 出现在该 id 的 DOM 节点**之前**（顶层 classic script 只看得到自己之前的标记） | 块0 第4830/4831 行绑定 `#dutyAnimClose`/`#dutyAnimOverlay`，节点在 9107 行 → **2 处命中** |
| `运行时未捕获错误` | 真浏览器里 `window.onerror` + `unhandledrejection` 收集（分类：`Uncaught / is not defined / before initialization / Cannot read` 等算致命；`Clipboard / permission denied / ResizeObserver` 等无头沙箱噪声只警告） | `Uncaught TypeError ... @7337行` ×1 |
| `★脚本疑似被中断` | 探针读顶层 `let` 的 `typeof`——**TDZ 就说明"声明了但没执行到"**，这是整块被中断的铁证 | `let-rhymeCat=TDZ/未初始化` |

警告项（必须扫一眼，可按已知误报表放行）：重复 id、静态哑按钮（`seatPlan1/2`、`exFill*` 是拼接 id 与字典遍历，**已知误报**）、点了没反应（1d 的 6 类误报）、导出物为空。

**闸门真正的价值是"健康版 vs 事故版"的差值**，同一份程序改前改后各跑一次对比：

```
事故版：绑定早于节点 2 / 未捕获错误 4 / 疑似无反应 42 / 导出物 6   → exit 1
修复版：绑定早于节点 0 / 未捕获错误 1(剪贴板噪声) / 疑似无反应 17 / 导出物 12 → exit 2
```

「疑似无反应 42→17」「导出物 6→12」这种跳跃，比逐条读代码可靠得多——**用户报的"三个按钮没反应"，在闸门里一眼就是整片按钮同时哑**。

**发版动作固定为六条命令**（先隐私，再静态一致性，最后冒烟；本机程序 + 出包的模板 + 网页版生成器都要跑）：

```bash
# ⓪ 隐私闸门：必须在最前面，命中真实姓名/本地路径就直接停，不要再去跑后面五条
python3 scripts/check_desensitization.py --program "/路径/班级小助手.html" templates/ ../workbench-package/
python3 scripts/sync_i18n.py "/路径/班级小助手.html" templates/class-workbench-template.html --check   # 词条一致性
python3 scripts/check_template_drift.py "/路径/班级小助手.html"                                        # 模板是否落后程序
node scripts/smoke.cjs "/路径/班级小助手.html"
node scripts/smoke.cjs templates/class-workbench-template.html
python3 scripts/customize.py --class-name 测试班 --count 40 --out /tmp/gen.html && node scripts/smoke.cjs /tmp/gen.html
```

第 ⓪ 条 exit≠0 就**不许发布**——它查的是隐私，后面五条全绿也救不回来。
前两条（词条、模板漂移）任一 exit≠0 就**先修一致性再谈冒烟**——冒烟只能证明"这一份能跑"，证明不了"三份产物是同一份"。

### 1i. 防漂移闸门（2026-11-10 新增，两个脚本）

| 脚本 | 防的是哪类漂移 | 判定 |
|---|---|---|
| `scripts/check_template_drift.py 程序.html` | **模板 ≠ 程序**：手工往模板上抄改动、或程序改完忘了重建模板 | 用 `build_template.py` 现场重算一份模板到 `/tmp`，与 `templates/` 里那份逐字节比；有差异时打印最多 12 个 difflib 块，并标出含脱敏标记的块。`--fix` 直接重建 |
| `scripts/sync_i18n.py 文件.html [第二个.html …]` | **内嵌词条 ≠ JSON 来源**：改词条只改了 HTML 里那串字面量，下次重建被打回 | 以 `scripts/i18n-en.json` / `i18n-en-patterns.json` 为唯一来源重写两处字面量；`--check` 只报告不写 |

⚠️ 两条已验证的规矩：

1. **模板只能由 `build_template.py` 从真实程序重新生成**（`check_template_drift.py` 就是这条规矩的自动执行）。产物校验（base64 一致、哈希一致）只证明**产物忠实于模板**，不证明**模板忠实于程序**——2026-11-10 就是靠这条发现模板悄悄落后本班程序 36 个代码块。
2. **i18n 词条的唯一来源是那两个 JSON 文件**。`add_i18n.py` 是一次性注入器（检测到 `applyLang` 就拒绝再跑），所以加词只能改 JSON 再 `sync_i18n.py` 写入。比较口径不同不是bug：**字典按键值语义比较**（精确查表，键序无关），**模板规则逐字节比较**（"先匹配先赢"，顺序就是语义）。
   新增规则一律**追加到末尾**，否则会遮蔽前面的规则；只有需要同族规则里"更具体的先命中"时才插到通用规则之前（例：`^（≥(\d+)分）$` 必须在 `^(\d+)分$` 前面）。

**英文补词的验收口径**：无头探针进英文模式的抽卡页，收集可见区里仍含中文的文本节点，**排除学生姓名与卡片名/说明**（内容是老师的数据，按设计不翻译）。剩下的每一条都要么补进字典、要么补进模板规则，直到只剩内容类中文。隐藏元素（如 `#gachaStats` 带 `style="display:none"`）里的死文字不算缺口。

⚠️ 探针自身的坑（已踩过）：① 错误收集脚本必须插在**第一个 `<script>` 之前**（插 `<head>` 里 `find` 返回 -1 会静默贴到文件末尾，探针永远无输出）；② 报告函数在 `run().catch()` 路径里也要补齐 probes 字段，否则 TDZ 检测器失效（本版曾因此漏判，靠"绑定早于节点"才发现）；③ 破坏性按钮（`fullReset`/`scoreReset`/`dutyReset`/`rosterApply`/`todayReset`/`pkToPerson`/`wordsReset`/`mathReset`）排在最后点，点前 `JSON.stringify(state)` 快照、点后 `(0,eval)('state=...')` 还原 + `rerenderAll()`；④ 下载与文件选择只 spy `HTMLAnchorElement.prototype.click` / `HTMLInputElement.prototype.click` 计数，**不真点**，保证 Downloads 干净。



```bash
python3 -c "
import io,re
s=io.open('out.html',encoding='utf-8').read()
for kw in ['<学校拼音缩写>', '<学校名>']:   # 换成实际学校的相关词做排查
    print(kw, s.count(kw))
m=re.search(r'const STUDENT_NAMES = \[([^\]]*)\]',s)
print('名单人数', len(re.findall(r'"([^"]+)"', m.group(1))) if m else '未找到')
print('前 5 个', re.findall(r'"([^"]+)"', m.group(1))[:5] if m else '-')
"
```

预期：学校相关词 **0**；名单人数与老师给的一致。**若发现真实学生姓名残留在模板/技能包里，立即替换**。

## 三、浏览器验证（推荐）

用无头 Edge/Chrome 注入探针，一次量测 12 页：

```python
import io, re, subprocess
EDGE = '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge'   # macOS
html = io.open('out.html', encoding='utf-8').read()
PROBE = """
<pre id="P" style="display:none"></pre>
<script>
window.addEventListener('load', function(){
  var out=[], q=function(s){return document.querySelector(s);};
  function L(k,v){out.push(k+'='+v);}
  try{
    var names=['seat','score','pk','duty','sched','homework','poem','math','word','tool','rank','gacha'];
    var ov=0;
    names.forEach(function(n){ try{ switchTab(n); }catch(e){ L('err_'+n, e.message); return; }
      if(document.documentElement.scrollHeight - window.innerHeight > 0) ov++; });
    L('overflowPages', ov);
    L('students', state.students.length);
    L('className', state.className);
    L('groups', (state.pk.groups||[]).length);
    L('jsErr', window.__errN||0);
  }catch(e){ L('EXC', e.message); }
  document.getElementById('P').textContent='@@'+out.join('|')+'@@';
});
window.__errN=0; window.addEventListener('error',function(){window.__errN=(window.__errN||0)+1;});
</script>
"""
i = html.rfind('</body>')          # ⚠️ 必须 rfind：文件内嵌 JS 含 '</body>' 字面量
io.open('/tmp/probe.html','w',encoding='utf-8').write(html[:i] + PROBE + html[i:])
r = subprocess.run([EDGE,'--headless=new','--disable-gpu','--no-sandbox','--hide-scrollbars',
  '--allow-file-access-from-files','--virtual-time-budget=5000','--window-size=1920,1080',
  '--dump-dom','file:///tmp/probe.html'], capture_output=True, timeout=200)
m = re.search(r'@@(.*?)@@', r.stdout.decode('utf-8','replace'), re.S)
print(m.group(1).replace('|','\n') if m else 'NO OUTPUT')
```

**预期**：`overflowPages=0`、`jsErr=0`、`students` / `className` / `groups` 与定制参数一致。

⚠️ **探针陷阱**：本文件内嵌 JS 含 `'<script>'` 与 `'</body>'` 字符串（导出模板用）。用 `str.replace('</body>', ...)` 会把探针插进 JS 字符串中间，造成**假崩溃**。必须用 `rfind('</body>')` 只替换最后一个。

## 四、人工抽查（有条件的做）

用 `--screenshot` 出图看几个关键页：

```bash
"$EDGE" --headless=new --disable-gpu --no-sandbox --hide-scrollbars \
  --allow-file-access-from-files --virtual-time-budget=4000 \
  --window-size=1920,1080 --screenshot=/tmp/seat.png file:///tmp/probe.html
```

重点看：座位页人数对不对、积分页姓名对不对、课表页科目对不对。

## 五、交付清单

- [ ] 12 页零溢出、零脚本报错
- [ ] 学生人数 / 班级名 / 小组数正确
- [ ] 无真实学校或学生在模板里残留
- [ ] 告知老师：名单在哪改、课表在哪改、怎么换电脑

## 数据持久化专项（第十一轮新增，必跑）

改过 `save()` / `load()` / 导出导入 / 写回文件相关的代码后，除了原有用例，还必须跑：

**静态**
- 两个内嵌 `<script>` 块分别 `node --check`（本文件有 2 个行首独立的 `<script>` 标签，
  但源码里还含 `<script>` / `</script>` 字面量，**不要用正则切块**——按行首标签配对切）
- 源码里**不应存在纯文本锚点** `<script>window.__CLASS_EMBEDDED_STATE__=`（会被文本正则误伤）；
  自检：`s.count('<script>window.__CLASS_EMBEDDED_STATE__=') == 0`

**Node 桩**
- 桩必须加载**全部**脚本块（第十一轮的新代码在第二个块里；只取第一个块会让新功能"不存在"）
- `n19` 跨日往返、`n20` 第十一轮 89 条

**真机（Edge headless，`--dump-dom` 注探针）**
| 场景 | 构造 | 期望 |
|---|---|---|
| 第二天·有存档 | 预置 localStorage | 数据完整、十二页零溢出、不误弹找回面板 |
| 第二天·本机被还原 | 源码剥掉旧注入后把数据脚本插到 `<body>` 之后 | **零操作自动读回全部数据** |
| 第二天·全空 | 什么都不给 | 自动弹出「找回数据」面板 |
| 写回程序文件 | 用探针把 `__CLASS_PACK__.diag.bound` 设成一个**假句柄**（`queryPermission/getFile/createWritable`） | 写成功、回读一致、**程序代码哨兵零缺失**、只注入一份数据、连续两次写回长度不膨胀 |
| 端到端 | 把上面写回的内容 base64 取出落盘，再当"明天的程序"打开 | 数据自动回来 + 十二页功能完好 |

注：`--dump-dom` 抓大文件时，探针里用 `btoa(unescape(encodeURIComponent(s)))` 分段塞进 DOM，Python 端再解码——
比把 80 万字符直接塞进 DOM 稳。副作用：**探针自己写的字符串也会出现在被检查的内容里**，
所以「计数」类断言要用 `'<scr'+'ipt ...'` 拼锚点，别让探针数到自己。

## 积分自检专项（第十二轮新增）

- `n21` 42 条：差额计算 / 横幅显隐 / 一键补回 / 撤销 / `#scoreReset` 可撤销 / `#todayReset` 无副作用 / 边界
- 真机：用**真实的"累计为 0 但历史有分"存档**打开 → 应自动弹横幅；点补回 → 分数回来且差额归零；
  横幅显示状态下 **12 页仍零溢出**（横幅插在积分页工具栏与网格之间，会挤压网格高度）
- 探针坑：读 `element.style.display` 不要写 `(x||'none')`——内联样式为空串时会被误判成 'none'，
  把"按钮已显示"读成"隐藏"。用 `String(x.style.display)` 原样取。

## 排行/趋势专项（第十三轮新增）

- `n22` 68 条：月度聚合（`monthsList`/`monthTotalOf`/`classMonthTotal`）、
  **恒等式**（`Σ月 == Σ日 == dailyTotalOf`）、总积分视图排序与名次、月度视图 sparkline 点位、
  两个 CSV 的表头与行数、个人趋势按日/按月的分流、老视图（今日/昨日/本周/本月）未被破坏、边界（无记录/单月）
- 真机：构造跨 3 个月、34 人的 `daily` → 断言 `rankOverflow==[]` 且 `pageOverflow==0`
  （1920×1080 + 2560×1440），并记录每个视图的实际高度（如 total 619px / monthly 787px / day 816px）
- **桩坑**：`makeEl` 的 `innerHTML=''` 必须真的清空 `children`，否则多次渲染后
  `children[0]` 还是最旧那次，断言会全错。另外老视图是 `appendChild` 建 DOM（不设 innerHTML），
  断言要用"递归收集子树文本"而不是 `.innerHTML`。

## 换机导入专项（第十四轮新增）

- `n23` 44 条：把**老师目录下所有真实历史文件**逐个丢给 `parseStateFromAny`
  （新版数据包 / 老版裸 json / 换机包 html / 含数据 html ×3 / 带 BOM 的早期备份），
  断言能解析出 34 人、古诗 73 篇、课表 5 天、历史积分合计正确；三种格式解析结果**逐字段等价**；
  垃圾内容（非 JSON / 无名单 / 空网页 / 空串）一律返回 null
- 真机端到端：拷贝程序到"新电脑"（清空 localStorage）→ 打开应弹提示面板 → 探针直接调
  `importPack(候选文件文本)` → 自动重载 → 断言重载后 `state` 与源文件**核心字段完全一致**
  （允许 `save()` 顺带补齐 `schedSets` 等容器字段）。三种候选各跑一遍
- 探针必须把第一阶段结果存 `localStorage` 带过重载；两阶段用一个自定义 key 区分

## 本机安全自检专项（第十五轮新增）

- `n24` 39 条：盘符识别（C 盘风险、D 盘安全、非 Windows 挂载路径不误报、小写盘符）、
  未绑定 / 已绑定写回成功 / 写回失败 / 浏览器禁止保存 / 无存档 五种结论分支、
  C 盘警告文案、按钮触发、结果区显示
- 真机：点「🩺 本机安全自检」→ 断言 `#savTestOut` 显示且**在视口内**
  （`getBoundingClientRect` 必须落在 `innerHeight` 之内 —— 这条曾真失败过，
  因为设置面板很长、输出块在折叠线以下，所以代码里加了 `scrollIntoView`）
- 用 mock 句柄跑"已绑定"分支：断言 `writes>=1`（真的写了一次）且结论为绿
- 真机上无法触发 C 盘分支（macOS 路径不含盘符），该分支由 n24 单元测试覆盖

## 座位方案专项（第十六轮新增）

- `n25` 75 条：三个槽的默认/补齐/裁剪、按空槽→存入的用户流程、切换、切回上一个、改名/清空、
  覆盖确认、格数校验拒绝、**积分与竞赛跟随**（逐组核对 members）、轮换基准重置、
  老 `seatTeacher` 迁移（含重复调用幂等）、存档往返、工具栏元素齐全
- 真机：按老师的真实操作顺序点 DOM（点①→点💾→换排布→点①）并对比 `#seatGrid` 的**单元格文本签名**，
  断言能切回；同时量 **座位页与 12 页的零溢出**（工具栏加了 6 个元素，最容易把座位页撑高）
- 注意：`arrangeSeat('gender')` 现在有前置检查，**测试要先给 students 填 gender**，否则它直接 return，
  会导致"两套座位相同"之类的假失败

## 模板脱敏与技能包验证（发布前必跑）

技能包里带的是**脱敏模板**，一旦模板里混入真实姓名，就等于把学生信息发布出去。发布/更新技能包前按顺序跑：

1. `scripts/build_template.py <真实程序.html>` —— 脚本做 3 项内置脱敏（名单/课表/示例姓名）
   + 历史标识符替换（映射表在 `scripts/legacy_ids.json`，不入库）+ 残留自检 + 锚点自检
   （customize.py 依赖的锚点是否齐全）。**报错就不要继续**。

   ⚠️ **模板只能由 `build_template.py` 从真实程序重新生成，不许手工往模板上抄改动。**
   2026-11-10 发现模板已悄悄落后本班程序 **36 个代码块**（抽卡页 T 型布局、值日岗位 8 列网格、
   座位行高、标签按钮尺寸、权益背包缩卡……全都没进模板），而 `ready-to-use` / `web-generator`
   是"从模板重建、逐字节校验一致"的——校验只证明**产物忠实于模板**，不证明**模板忠实于程序**，
   所以漂移一路通过所有闸门。口诀：改完程序先跑 `build_template.py`，再跑后两步；
   判断是否漂移**直接跑 `python3 scripts/check_template_drift.py 程序.html`**（它把"重算模板 + difflib 比块"
   自动化了，见 1i；`--fix` 顺手重建）。2026-11-10 那 36 处差异就是靠这套比对抓出来的。

   ⚠️ **历史标识符那一步会"静默跳过"**：`scripts/legacy_ids.json` 不存在时只打一行 `ⓘ` 就继续。
   2026-11-10 就是这样：母版程序的存储键名/IndexedDB 库名/内嵌数据全局变量都带**校名缩写**
   （形如 `xxx_grade1_class_v1`、`__XXX_EMBEDDED_STATE__`、`xxxDataScript`），而映射表文件缺失，
   结果**连续几个已发布版本**的模板、空白班、网页版生成器里都原样带着这个缩写。
   规矩：**只要本机程序的历史标识符改过名，就必须先建 `legacy_ids.json`（照 `.example` 抄）再重建模板**；
   `check_desensitization.py` 的西文禁词（把缩写本身填进 `desensitization.local.json`）负责兜底。
   跨版本还要能读旧包的地方，前缀写成字符类（`[A-Z]{2,12}`）而不是硬编码某个缩写。
2. **真实姓名与本地路径全量扫**：`python3 scripts/check_desensitization.py --program <真实程序.html> <发布目录…>`，
   必须 0 命中（exit 0）。脚本名单**直接从程序的 `STUDENT_NAMES` 读取**（所以脚本本身可以公开、不含任何真实姓名），
   额外禁忌词放 `scripts/desensitization.local.json`（学校名/班级名/盘符目录名等，**不入库**）；
   扫描时会**解开 `web-generator.html` 里的 base64 内嵌模板**一起查，并跳过 `legacy_ids.json`、`_skillhub_meta.json`
   等本机专用文件。命中就 exit 1，**不许发布**。

   ⚠️ **这条闸门是 2026-11-10 用一次真实事故换来的**：已公开的 GitHub 仓库里
   `templates/class-workbench-template.html` 在某次同步时被误换成**未脱敏的本班程序**，
   34 个真实学生姓名因此在公开仓库里躺了若干版本，而当时那套发版命令（只测功能与一致性）**全绿**。
   教训：**功能闸门测不出隐私泄漏**——隐私必须单独一条、并且放在最前面。
   若已提交过含真实姓名的版本，仅覆盖新文件不够，**历史提交仍然可见**，需要改写历史 + 强推；
   这属于影响共享状态的操作，必须先征得用户同意再动手。
3. **端到端生成**：用虚构名单跑 `customize.py` 产出示例成品，检查：班级名已写入、无 `学生01` 残留、
   两个 `<script>` 块 `node --check` 通过、CSS 括号配平。
4. **浏览器冒烟**：加载成品，断言无 JS 错误、新功能元素在位（用 `window.__CLASS_PACK__` 探针）、
   学生数与性别数正确。

⚠️ **溢出量测的对照原则**：别只看绝对值。本项目 `rank` / `gacha` 是长列表页，本来就滚动（1920 下 rank≈198px、
gacha≈2785px）。判断"有没有回归"的正确方法是对同一指标**跑一遍本班真实程序做对照**——
示例成品与本班程序数值一致＝模板忠实；只有示例成品变差才是回归。
