---
name: birding-notes
description: 学习与记录鸟类、植物、昆虫等自然知识的工作约定。当用户讨论物种识别、目科分类、自然观察笔记，或说出「记入到 Notion」「写进 life list」等触发词时加载。规定术语标注、数据源校验、Notion 落地、内容结构、配图规范。
agent_created: false
---

# birding-notes — 自然知识学习与记录约定

> 本 skill 是为「在 Notion 维护 life list / 鸟类植物昆虫观察笔记」的人设计的工作流协议。
> 由 [@peanut8tter](https://github.com/peanut8tter) 在 WorkBuddy / Claude Code 上沉淀，欢迎 fork 和改造。
>
> 一旦加载，AI 必须遵守，直到用户显式覆盖某条规则。

---

## 0. 配置（首次安装必须做）

本 skill 引用一份 `config.json`（与 SKILL.md 同目录），描述你的 Notion 工作空间结构、地理偏好等。

复制 `config.example.json` 为 `config.json`，填入你自己的值。详细字段说明见 README。

最低必填：

- `notion.life_list_database_id`
- `xenocanto.api_key_path`（默认 `~/.workbuddy/secrets/xenocanto.json`）

---

## 1. 触发条件

满足任一条件即应用本 skill：

- 用户讨论某个具体物种（鸟、植物、昆虫、菌、爬行、两栖等）
- 用户讨论某个分类阶元（目、科、属）
- 用户做物种对比、生境探讨、自然观察笔记
- 用户提到「记入到 Notion」「记到自然」「写进 life list」「入库」等**入库触发词**

---

## 2. 术语标注规范

### 2.1 名称三件套——**走 Notion 字段，不写正文**

物种 / 目 / 科条目的「中文名 / 英文 common name / 拉丁双名」**已存在固定字段**（如 life list 的「学名」「Common name」字段）。

- **不要**在条目正文里再用整段把三件套复述一遍
- 正文首段直接进入「拉丁名词源」「分类考据」等内容

### 2.2 拉丁名词源——**简洁词典式**

格式（强制）：

```
属名 + 词根：含义
种加词 + 词根：含义
```

**示例（红嘴蓝鹊 *Urocissa erythroryncha*）**：

> *Urocissa* —— *oura*：希腊语尾巴；*kissa / kitta*：鹊、喧闹的鸟。
> *erythroryncha* —— *erythros*：希腊语红色；*rhynchos*：喙。

只列词根 + 含义，**不要**写"形容……""因……"之类的解释性补充——除非该补充是**反直觉的关键信息**（如拼写演变、模式标本采自……）。

### 2.3 命名人物故事

种加词背后是人物（如 *swinhoii* 纪念 Robert Swinhoe，*davidii* 纪念谭卫道）→
- 词源行只写「*swinhoii* —— 纪念 Robert Swinhoe」
- 详细故事**放到「文化演化」块**展开

不需要写命名者、年代、模式产地等学术细节，除非用户明确要求。

---

## 3. 数据源与准确性

### 类群对应数据源（强制）

| 类群 | 主数据源 | 用途 |
|---|---|---|
| 鸟类 | **AviList v2025**（本地 json，~11,131 种） | 拉丁名 / 英文名 / 目 / 科；不联网 |
| 植物 | **POWO**（Plants of the World Online）+ **《中国植物志》** | 拉丁名 / 科 / 中文学名（中国本土植物以 FOC/植物志为准） |
| 昆虫 | **iNaturalist** + **CoL**（Catalogue of Life） | 拉丁名 / 分类 / 区域记录 |
| 其他 | iNaturalist 兜底，或与用户确认 | — |

### 校验流程

1. 写出物种条目前，**先**查上述数据源
2. 鸟类：直接读本地 json，不需要联网
3. 植物 / 昆虫：通过 WebSearch / WebFetch 查 POWO、iNaturalist、植物志官网
4. 任一字段不确定 → 在该字段后用 `（⚠️ 未确认 · 来源: X）` 标注，**绝不编造**
5. 数据源之间冲突时，按上表优先级处理；冲突需在「分类考据」块用一句话说明

### 数据源 page（可选）

`config.nature_root_page_id` 下可建一个 `📚 数据源` page，记录每个主数据源的发展史与引用规范。等首次有具体物种入库时再顺手建。

---

## 4. 条目内容结构

进入 Notion 的「学习类」条目（物种 / 目 / 科），由 **3 块必填 + 1 块按需 + 1 块鸟类专属** 组成。标题固定，子要点按条目类型自适应。

### 4.1 分类考据【必填】

- **拉丁名词源**：按 §2.2 词典式格式
- **系统位置**：所在目 / 科 / 属（物种）；所在纲 / 目下主要科与代表种（目 / 科条目）
- **分类沿革**（按需）：曾用学名、近年拆分合并、各名录是否一致——**只在确实有动荡时写**，无动荡可省

### 4.2 识别区分【按需触发】

**默认不写**。仅在以下情况触发：

- 用户问「这个怎么和 X 区分」「X 和 Y 怎么分」之类的对比问题
- 用户主动要求「加一段识别要点」
- 用户在野外提交了一张混淆物种的照片

触发后，**优先用对比表**而非大段文字。

### 4.3 分布与生态【必填】

- **简短文字描述**：1~2 句话覆盖"全球大致分布 + 用户所在地（`config.user_preferences.regional_focus`）局部状况"
- **GBIF 物种页 bookmark** 1 条（不是图）：
  - URL：`https://www.gbif.org/species/<speciesKey>`
  - caption：`GBIF · <Scientific name> · 全球出现记录`

#### **不要做**的事（实战教训）

- ❌ **不要内嵌 GBIF v2 tile API 的 PNG**：`density/0/0/0@2x.png` 是叠加层，**透明底没有底图**；高 zoom level 下小物种在 zoom-0 上只剩几个亮点
- ❌ **不要内嵌 IUCN range map**：需要登录账号
- ❌ **不要尝试 eBird Status & Trends 的 PNG 截图**：URL 不稳定，且需 Cornell 账号
- ❌ **不要写**：生境偏好、食性、繁殖期、物候等——除非用户专门问

#### 不写居留型

Notion 数据库已有「居留型」固定字段，正文不复述。skill 仍按 §5 规则把居留型写进 Notion 字段。

### 4.3.5 鸣声 / 鸣唱【鸟类必填】

#### 内容（极简）

仅两件事：

1. **简短文字描述**，格式：
   ```
   情境 → 拟声词 → 频次/质感
   ```
   例：
   > *领地宣示*：刺耳金属质 *penk-penk-penk* 串叫，每分钟 8~10 次

2. **xeno-canto 具体录音页 bookmark**，1 条即可：
   - URL：`https://xeno-canto.org/<XC_ID>`
   - caption：`xeno-canto · XC<ID> · <国家/地区> · <type> · <录音师> · CC <许可证>`

#### **不要做**的事（实战教训）

- ❌ **不要内嵌频谱图 PNG**：xeno-canto 的 sono URL 被 Anubis 反爬拦截
- ❌ **不要内嵌 Notion audio block**：external URL 当时能播但依赖 xeno-canto 永久可达；不稳
- ❌ **不要用 file_uploads 上传频谱/音频到 Notion 内部存储**：磁盘/Notion 配额成本高
- ❌ **不要给 xeno-canto 物种级页面**：用户偏好直接给具体录音页

#### 选录音的流程（用 xeno-canto API v3）

API key 文件：路径由 `config.xenocanto.api_key_path` 指定（默认 `~/.workbuddy/secrets/xenocanto.json`，单字段 `api_key`）。注册 key：[xeno-canto.org/account](https://xeno-canto.org/account)。

```python
import json, urllib.request, urllib.parse
key = json.load(open(__import__('os').path.expanduser('~/.workbuddy/secrets/xenocanto.json')))['api_key']
q = f'gen:"<Genus>" sp:"<species>"'  # 必须 tag 语法
url = f"https://xeno-canto.org/api/3/recordings?query={urllib.parse.quote_plus(q)}&key={key}"
data = json.loads(urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'}), timeout=30).read())
```

**挑选优先级**（多键排序）：
1. 质量 q='A'
2. type 包含 song > call > 其他
3. 录音地优先 `config.user_preferences.regional_focus_country`（如 'China'）

完整脚本见 `scripts/xc_query.py`。

#### 升级条件（未来再启用内嵌）

如果以后满足以下任一条件，可重新评估内嵌方案：

- xeno-canto 取消反爬或推出 CDN 直链
- 找到稳定可内嵌的替代源（如 Wikimedia Commons 有同物种的 CC 录音 + 频谱）
- Notion file_uploads 的批量自动化成本降到 ~500 token/只

### 4.4 文化与演化背景【必填】

| 条目类型 | 关注点 |
|---|---|
| 物种 | 名字典故、命名者故事、诗词典籍、民俗象征、与人类的互动史 |
| 目 / 科 | 演化历史、化石记录、近年分类学重大变动、科学史趣闻 |
| 植物特化 | 中药用途、食用、园艺品种、诗词典故 |
| 昆虫特化 | 若文化记载稀薄，可写「该类群的科学史」或「在生态系统中的角色」；可留空但不可编造 |

**绘画 / 艺术作品配图**：如该物种或类群在传统绘画、浮世绘、博物画、邮票等有具代表性的图像作品，**附图**到本块文字旁。

> 任何一块若**真的没有可靠信息**，写「（暂无）」或「（⚠️ 暂无可确证的代表性古画）」而不是凑字。

---

## 5. Notion 落地

### 5.1 入库触发词

用户说出以下任一表达即视为入库指令，**直接执行**，不再追问「要不要写」：

- 「记入到 Notion」/ 「记到 Notion」
- 「记到自然」/ 「写到自然下」
- 「写进 life list」/ 「加进 life list」
- 「入库」

### 5.2 落地位置（C 模式：用户带位置优先，没说走默认）

**优先级 1**：用户在触发词中带了位置 → 严格按用户指定

**优先级 2**：用户没带位置 → 按下表读取 `config.json`：

| 条目类型 | 默认位置（config.json key） |
|---|---|
| 鸟类**物种** | `notion.life_list_database_id` |
| 鸟类**目** | `notion.orders_database_id` |
| 鸟类**科** / 自由笔记 / 对比 / 主题探索 | `notion.bird_root_page_id` 下作为子 page |
| 植物**物种** / 笔记 | `notion.plant_root_page_id` 下作为子 page |
| 昆虫**物种** / 笔记 | `notion.insect_root_page_id` 下（首次入库时若不存在则自动新建于 `notion.nature_root_page_id` 下） |
| 其他类群 | `notion.nature_root_page_id` 下新建对应大类 page |

### 5.3 入库前确认

只有以下情况停下来问用户：

- 物种身份本身存疑
- 居留型因季节-地点矛盾无法判定
- 用户带了位置但该位置不存在（提示是否新建）

其他情况**直接执行**，不要批量提问。

### 5.4 鸟类条目的字段处理

鸟类的"分类考据"块查证流程，调用配套 skill **avilist-bird-lookup**。下面是最高频会踩的坑（无需跳转即可看到）：

#### a. AviList 高风险物种清单（华南本地化示例）

| 中文名 | 正确学名（AviList v2025） | 易错点 |
|---|---|---|
| 麻雀（华南） | *Passer montanus*（树麻雀） | **不是**家麻雀 |
| 暗绿绣眼（华南） | *Zosterops simplex*（Swinhoe's White-eye） | **不是** *Z. japonicus* |
| 乌鸫（华南） | *Turdus mandarinus*（Chinese Blackbird） | AviList 仍独立成种 |
| 大山雀（华南） | *Parus cinereus*（Cinereous Tit） | AviList 已把 *P. minor* 合并入 *P. major* |
| 喜鹊（东亚） | *Pica serica*（Oriental Magpie） | 已从 *P. pica* 拆分 |
| 金腰燕 | *Cecropis daurica* | AviList 英文名 **Eastern Red-rumped Swallow**（拆分） |
| 斑嘴鸭（东亚） | *Anas zonorhyncha* | 已从 *A. poecilorhyncha* 拆分 |
| 金眶鸻 | *Thinornis dubius* | AviList v2025 已从 *Charadrius dubius* 移入 *Thinornis* 属；GBIF 主干仍用 Charadrius（bookmark 用 Charadrius 种级 key 7937336） |
| 赤腹鹰 | *Tachyspiza soloensis* | AviList v2025 已从 *Accipiter* 移入新属 **Tachyspiza**（旧世界小鹰大拆分）；GBIF 主干仍用 Accipiter（bookmark 用 *Accipiter soloensis* 种级 key 2480588） |
| 淡眉雀鹛（华东） | *Alcippe hueti*（Huet's Fulvetta） | AviList v2025 已从灰眶雀鹛复合体独立成种；*A. morrisonia*（Grey-cheeked Fulvetta）现专指台湾种 |

> 不同地区的高风险清单不同，请按当地实情扩充。

#### b. AviList 英文名拼写规则

英式拼写、Title Case、复合修饰词用连字符：

- ✅ Grey-headed Lapwing（**不是** Gray-）
- ✅ Coloured（**不是** Colored）
- ✅ Red-whiskered Bulbul（连字符）
- ✅ Swinhoe's White-eye（人名所有格保留撇号）

#### c. Notion 写入限速

批量写入时**每次操作间 sleep ≥ 0.35s**，否则触发 429（Notion API 约 3 req/s）。批量结束后做一次"补漏检查"——不要假定第一遍就成功。

#### d. Notion select 字段的反直觉坑

API v2025-09-03 起：**select 字段的 option 名字和颜色一旦创建就改不了**（PATCH 请求会被静默忽略，响应返回原值，无报错）。**字段名本身可以改**，option 不行。

如需改 option 显示效果，必须走重建流程：

1. 老字段重命名为 `<名>_old`
2. 新建同名字段，option 设为目标外观
3. 拉记录把值复制过去
4. PATCH `data_source` 删旧字段（`properties: { <名>_old: null }`）

#### e. 数据源字段

鸟类条目的「数据来源」字段统一填 `AviList v2025`。

---

## 6. 配图规范

### 6.1 第一原则：**只放有信息增量的图**

配图必须**对用户而言有信息增量**。用户已亲眼见过本物种的普通生态/活体照片**对他没有信息增量**——不要放。

「有信息增量」的图包括但不限于：

- **古代绘画 / 浮世绘 / 博物画 / 邮票** —— 文化语境的视觉证据
- **解剖示意 / 形态对比** —— 帮助理解结构、术语、或近似种鉴别
- **系统树 / 演化关系图** —— 帮助理解分类层级与亲缘
- **关键鉴别特征的局部特写** —— 仅当用户问鉴别问题时
- **栖息地 / 极端形态变体**（冬羽、雏鸟、性别二态显著差异）—— 仅当能补充活体观察看不到的内容

**不要放**：

- ❌ 普通全身照（用户每次都见，零增量）
- ❌ "好看但说明不了任何事"的艺术摄影
- ❌ 只是为了"配一张图"而填位的图

### 6.1.1 古画 / 博物画的主动检索流程

每写一个物种 / 类群条目，**主动**尝试配古画或博物画——不要等用户提名。流程：

1. **生成候选关键词**：物种英文 / 学名 + `"painting"` / `"woodblock"` / `"花鸟图"` / `"鳥類図譜"` 等；含传统画家专名（黄筌、宋徽宗、伊藤若冲、葛饰北斋、John Gould、Audubon 等）
2. **检索数据源**（按优先级）：
   - Wikimedia Commons artwork 类目
   - Smithsonian Open Access、Met Open Access
   - 故宫 OPEN（中国画）、东京国立博物馆 ColBase（日本画）、大英博物馆 Collection Online
   - 美国国会图书馆 Bird Prints 子库（Audubon / Gould 系列）
3. **WebFetch 验证**：进入图片所在页面，确认 ① 页面存在 ② 物种身份正确 ③ 作者 / 年代 / 现藏地可读
4. **形态匹配检查**：尤其涉及"长尾蓝鸟""红尾鸟"等模糊形容时，必须在描述中找到能确证物种身份的细节（喙色、羽色、尾形）
5. **写不下结论时**：一律用「（⚠️ 暂无可确证的代表性古画）」，**绝不**用模棱两可的图凑数

### 6.2 何时放图

配图就近嵌入对应文字旁，**不是单独模块**。每个模块默认**不放图**，按下表触发：

| 位置 | 触发条件 |
|---|---|
| §4.1 分类考据 | 默认无图。仅在系统树 / 属下姊妹种比较有视觉价值时酌情加 |
| §4.2 识别区分（用户问后才写） | 必有 1 张：对比图 / 特征标注 / 解剖示意之一 |
| §4.3 分布与生态 | 仅 GBIF bookmark，**不放分布图 PNG** |
| §4.4 文化与演化 | **仅在**有代表性的绘画 / 浮世绘 / 博物画 / 邮票时附图 |
| 条目 cover | **可省略** |

### 6.3 来源优先级

| 内容 | 首选 |
|---|---|
| 古代绘画 / 艺术作品 | **Wikimedia Commons** artwork 类目 / 故宫 OPEN / 大英 / 大都会 / 东京国立博物馆开放图库 |
| 解剖 / 系统树 | Wikimedia Commons 科学插图 / 已发表论文配图（注明出处） |

### 6.4 验证（强制）

**所有图链接在输出前必须实际访问验证**：

1. 用 WebFetch 打开资源所在页面，确认页面存在、内容匹配（物种身份正确）
2. 抄录作者 / 来源 / 许可证字段
3. 对不可访问、404、内容不符的链接**立刻丢弃，重新找**
4. **绝不输出未经验证的具体资源链接**

> ⚠️ **Wikimedia 直链的 hash 前缀（如 `/commons/f/f5/`）不能凭文件名推断**——它是文件名的 MD5，只能从 File 页正文里抄。凭「文件名 + 猜测的 hash」拼出的 upload.wikimedia.org 直链几乎必然 404。每张图都要打开其 File 页，从「Original file」链接抄真实直链。

#### 例外：xeno-canto 走 API v3，不走 WebFetch

xeno-canto 网页有 Anubis 反爬，但 API v3 用 key 直连无墙。验证流程：JSON 返回的 `gen` + `sp` 字段即为已验证的物种身份（**等价于** WebFetch 验证）。

### 6.5 引用形式

Notion 的**超链接 / bookmark 形式**（带 cover 缩略图），**不上传**文件到 Notion 内部存储。

每张图下注明：

```
📷 作者 · 来源平台 · 许可证（如 CC BY-SA 4.0）· 关键元数据（年代/藏地/拍摄地）
```

绘画作品须注明**作者 + 创作年代 + 现藏地**（如已知）。

---

## 7. 工作流总览（一次完整调用的步骤）

用户说「记入到 Notion」时：

1. **校验数据源** — 鸟读本地 AviList json；植物 / 昆虫联网查
2. **生成内容**（3 块必填 + 鸟类鸣声块 + 按需识别区分）：
   - §4.1 分类考据（含拉丁名词源）
   - §4.3 分布与生态（GBIF bookmark + 一句话）
   - §4.3.5 鸣声 / 鸣唱（鸟类）：xeno-canto 录音页 bookmark + 文字
   - §4.4 文化与演化（如有代表性绘画就配图）
   - §4.2 识别区分仅在**用户问过相关问题**后写入
3. **配图就近嵌入**对应文字旁
4. **落地** — 按 §5.2 决定路径
5. **写入 Notion** — 通过 `mcp__notion__*` 工具或 Notion REST API 直接写。三件套（中文名/英文名/学名）走 Notion 字段，不写正文
6. **首次副作用**：
   - 若昆虫大类 page 不存在且本次入库是昆虫 → 自动创建
   - 若涉及新目 / 新科 → 按 `avilist-bird-lookup` 流程补建（仅鸟类）
7. **回报** — 给用户 Notion 链接 + 简短摘要

---

## 8. 不要做的事

- ❌ 不要把不确定的内容写得很确定（用 ⚠️ 明示）
- ❌ 不要在没有触发词时擅自写入 Notion
- ❌ 不要为了凑「四块」而编造「文化演化」之类的内容
- ❌ 不要使用过时分类（如把一些雀形目科还按 90 年代体系排）
- ❌ 不要在第一次加载 skill 时就批量创建空架子 page——按需触发
- ❌ 不要内嵌音频 / 频谱图 / 分布图 PNG（除非升级条件满足）

---

## 9. 关联 skill

| skill | 何时调用 |
|---|---|
| **avilist-bird-lookup** | 鸟类条目的学名/英文名/目/科查证；批量补全 life list；解析 AviList xlsx |
| **birding-notes (本 skill)** | 综合编排：术语标注、内容结构、Notion 落地、配图 |

**协作关系**：
- birding-notes 是**总编排**，决定写什么、写到哪、怎么落地
- avilist-bird-lookup 是**鸟类专项数据查证**，提供本地 AviList 数据 + 解析/校验脚本

## 10. 演化

发现规则不够用 / 需要调整 / 用户给出新偏好 → 更新本 SKILL.md，并在 commit message 里记一笔变更。

---

## 设计源起与思路

> 本 skill 是给"在 Notion 里维护 life list / 自然观察笔记的人"设计的工作流协议。

**为什么需要**？AI 在帮你写自然知识时容易：

1. **把不确定的当确定的写**（鸟类分类近年大动，AI 训练数据常停留在 2017 年代）
2. **冗余复述**（中文名/英文名/学名在 Notion 字段里已有，正文再写一遍是浪费）
3. **拉丁名解释啰嗦**（应当词典式直击词根）
4. **配图填位**（用户已见过的活体照对他零信息增量）
5. **入库要反复确认**（用户说"记入到 Notion"就该直接做）

birding-notes 把这些痛点固化成规则，每次自然知识相关对话自动加载，等于把"我和 AI 之间签的协议"焊死。

**为什么用 AviList？** WGAC 在 2025 年 6 月发布的全球统一鸟类名录，整合 IOC / Clements/eBird / HBW / AOS 四大体系，是当前推荐的标准。eBird/Merlin 将在 2026 年版起切换到 AviList。

**为什么"识别区分"是按需触发？** 因为大多数物种在你已经亲眼见过的情况下，写"识别区分"是给未来的自己/不熟悉的读者看的——而你写笔记本是为了**自己学习**，按需触发更切合实际使用模式。

**为什么不内嵌音频和频谱图？** 实战中发现 xeno-canto 反爬、GBIF tile API 透明叠图、Notion file_uploads 成本高——综合权衡下，**链接外跳到原平台**反而是最稳定、信息密度最高的方案。

**为什么用 Notion？** Notion 的数据库 + page 嵌套 + 富文本 + 富媒体 bookmark，对"维护一个有结构的物种知识库"是当前最便捷的工具。skill 通过 Notion REST API（v2026-03-11）写入。
