---
name: birding-notes
description: 学习与记录鸟类、植物、昆虫等自然知识的工作约定。当用户讨论物种识别、目科分类、自然观察笔记，或说出「记入到 Notion」「写进 life list」等触发词时加载。规定术语标注、数据源校验、Notion 落地、内容结构、配图规范。
---

# birding-notes — 自然知识学习与记录约定

> 本 skill 是为「在 Notion 维护 life list / 鸟类植物昆虫观察笔记」的人设计的工作流协议。
> 由 [@peanut8tter](https://github.com/peanut8tter) 沉淀，适用于任何支持 SKILL.md / AGENTS.md 的 AI 编码助手（Codex、Claude Code、WorkBuddy、Cursor 等），欢迎 fork 和改造。
>
> 一旦加载，AI 必须遵守，直到用户显式覆盖某条规则。

---

## 0. 配置（首次安装必须做）

**首次使用 / 缺配置时先走 `birding-setup`**：任何 Notion 读写之前，先运行
`python3 <birding-setup 目录>/scripts/setup_helper.py status`；返回 `ready: false` 就按 `birding-setup/SKILL.md`（同仓库 skills/ 下）完成引导，再继续用户原本的任务。

配置位置：`~/.config/birding-notes/config.json`（Notion 数据库 ID、地理偏好）；token 在 `~/.config/birding-notes/secrets/`；可用环境变量 `BIRDING_NOTES_HOME` 改位置。均不在仓库内。字段说明见 `config.example.json`。

**不要假设用户的库长什么样。** 用户可能是新建的标准库，也可能是接入他自己已有的库。因此：

- 写 Notion 时，列名一律取 `config.json` 的 `notion.fields`（标准字段 key → 该库里的实际列名），**不要硬编码**「中文名」「学名」等列名。
- 只写**已映射**的字段。「居留型」「IUCN 等级」「保护等级」「数据来源」等可选字段，没映射就不写、不报错、不自动建列（要建列须先征得用户同意，用 `setup_helper.py add-fields`）。
- 物种名列填什么语言看 `user_preferences.name_language`（`zh` 中文名 / `en` 英文名），缺省按用户当前对话语言。
- 地点相关判断（居留型、分布侧重、录音地）用 `user_preferences.primary_location / regional_focus / regional_focus_country`；**没配置就问用户或不判断，不要默认某个城市**。
- 基础条目（名称/学名/目科等字段）可直接用 `skills/birding-setup/scripts/setup_helper.py add-rows` 写入：自动按 AviList 补全、去重、适配用户的列名。详细正文（分类考据等）再用 Notion 工具追加。

最低必填：`notion.life_list_data_source_id`（或 database id）与 `notion.fields`（由 `birding-setup` 生成）。xeno-canto API key 可选，查鸣声用（环境变量 `XENOCANTO_KEY` 或 `secrets/xenocanto.json`）。

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

物种 / 目 / 科条目的「中文名 / 英文 common name / 拉丁双名」**已存在固定字段**（如 life list 的「学名」「Common name」列；实际列名以 `notion.fields` 映射为准）。

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

## 4. 条目内容结构（v2 版式）

条目页正文**自上而下固定为**下表。**每个章节标题一律带 emoji**（缺了就是错）。用户可通过 `user_preferences.entry_modules` 关掉某些模块，缺省为全开。

| 顺序 | 内容 | 模块 key | 标题（H2） |
|---|---|---|---|
| ① | 代表性**实拍图** | `photo` | 无标题。**必须是正文第一个 block** |
| ② | 首次记录提示框 | — | 🐦 灰底 callout：`首次记录：日期 · 地点`（用户没给就省略） |
| ③ | 性格与行为 | `behavior` | 🐾 性格与行为 |
| ④ | 分类考据 | `taxonomy` | 🧬 分类考据（含 H3「拉丁名词源」「系统位置」） |
| ⑤ | 分布与生态 | `distribution` | 🌏 分布与生态 |
| ⑥ | 鸣声 / 鸣唱（鸟类） | `voice` | 🎵 鸣声 / 鸣唱 |
| ⑦ | 文化与演化（含古画 / 博物画） | `culture` | 📜 文化与演化 |
| 按需 | 识别区分 | `id` | 🔍 识别区分（用户问了才写，见 §4.2） |

**为什么首图必须第一块**：Notion 画廊视图的卡片缩略图取「正文第一张图」；放在提示框或文字之后，缩略图会是空白。

**怎么写出来**：不要手拼 Notion 块。按 `assets/entry_spec.template.json` 的结构生成 spec，用 `skills/birding-setup/scripts/entry_tools.py write-body` 写入；它会上传图片、补全缺失的 emoji、对照用户启用的模块做缺漏警告。命令与找图流程见 §6、§7。

### 4.0 性格与行为【默认启用】

写作口径（作者拍板，长期生效）：

- ❌ **不拟人、不抒情**（不写「调皮」「优雅」「温柔」「像个小绅士」之类）
- ✅ **简朴的事实描述**，每条是一个可核对的观察或文献事实
- ✅ **多项内容一律用 bullet points**，一条一事，不写成长段

可写的角度（有可靠信息的才写）：社群性与活动习性、食性与觅食方式、为特定食性演化出的形态、飞行 / 行走姿态特征、迁徙习性、与近似种的行为差异。

样板（节选自凤头蜂鹰条目）：

> - 多单独活动，性隐秘，常栖于林冠层，不易观察
> - 主食蜂类：捣毁纸质蜂巢取食幼虫和蛹，也取食其他昆虫、小型爬行类及鸟卵
> - 为食蜂特化的形态：脸部密覆鳞片状小羽防蜂蜇；喙基具刚毛；爪较其他猛禽弱
> - 迁徙期聚成大群，秋季过境量大

没有可靠信息的物种：写能确证的 2–3 条，不凑数；整块真的没有就写「（暂无）」。

### 4.1 分类考据【必填】

- **拉丁名词源**（H3 小标题）：按 §2.2 词典式格式
- **系统位置**（H3 小标题）：所在目 / 科 / 属（物种）；所在纲 / 目下主要科与代表种（目 / 科条目）
- **分类沿革**（按需）：曾用学名、近年拆分合并、各名录是否一致——**只在确实有动荡时写**，无动荡可省

### 4.2 识别区分【按需触发】

**默认不写**。仅在以下情况触发：

- 用户问「这个怎么和 X 区分」「X 和 Y 怎么分」之类的对比问题
- 用户主动要求「加一段识别要点」
- 用户在野外提交了一张混淆物种的照片

触发后，**优先用对比表**而非大段文字。

### 4.3 分布与生态【必填】

- **要点（2~3 条 bullet）**：全球大致分布 + 用户所在地（`config.user_preferences.regional_focus`）的居留状况与栖息环境；用户没配置所在地就只写全球分布
- **GBIF 物种页 bookmark** 1 条（不是图）：
  - URL：`https://www.gbif.org/species/<speciesKey>`
  - bookmark **下一行单独写一段文字**：`GBIF · <Scientific name> · 全球出现记录`（不用 bookmark 自带的 caption，与既有条目保持一致）

#### **不要做**的事（实战教训）

- ❌ **不要内嵌 GBIF v2 tile API 的 PNG**：`density/0/0/0@2x.png` 是叠加层，**透明底没有底图**；高 zoom level 下小物种在 zoom-0 上只剩几个亮点
- ❌ **不要内嵌 IUCN range map**：需要登录账号
- ❌ **不要尝试 eBird Status & Trends 的 PNG 截图**：URL 不稳定，且需 Cornell 账号
- ❌ **不要写**：繁殖期、物候等——除非用户专门问。（食性、觅食等习性归 §4.0「🐾 性格与行为」，不在这里重复）

#### 不写居留型

Notion 数据库已有「居留型」固定字段，正文不复述。skill 仍按 §5 规则把居留型写进 Notion 字段。

### 4.3.5 鸣声 / 鸣唱【鸟类必填】

#### 内容（极简）

仅两件事（没配 xeno-canto key 时只写第 1 件，并在汇报里提示可补）：

1. **简短文字描述**，格式：
   ```
   情境 → 拟声词 → 频次/质感
   ```
   例：
   > *领地宣示*：刺耳金属质 *penk-penk-penk* 串叫，每分钟 8~10 次

   **拟声词必须有依据**（文献、录音页描述或你听过的录音）；没有依据就只写情境和质感，不要编拟声。

2. **xeno-canto 具体录音页 bookmark**，1 条即可：
   - URL：`https://xeno-canto.org/<XC_ID>`
   - bookmark **下一行单独写一段文字**：`xeno-canto · XC<ID> · <国家/地区> · <type> · <录音师> · CC <许可证>`

#### **不要做**的事（实战教训）

- ❌ **不要内嵌频谱图 PNG**：xeno-canto 的 sono URL 被 Anubis 反爬拦截
- ❌ **不要内嵌 Notion audio block**：external URL 当时能播但依赖 xeno-canto 永久可达；不稳
- ❌ **不要用 file_uploads 上传频谱/音频到 Notion 内部存储**：磁盘/Notion 配额成本高
- ❌ **不要给 xeno-canto 物种级页面**：用户偏好直接给具体录音页

#### 选录音的流程（用 xeno-canto API v3）

API key：环境变量 `XENOCANTO_KEY`，或 `~/.config/birding-notes/secrets/xenocanto.json`（单字段 `api_key`）。注册 key：[xeno-canto.org/account](https://xeno-canto.org/account)。

```python
import json, urllib.request, urllib.parse
import os
key = os.environ.get('XENOCANTO_KEY') or json.load(open(os.path.expanduser('~/.config/birding-notes/secrets/xenocanto.json')))['api_key']
q = f'gen:"<Genus>" sp:"<species>"'  # 必须 tag 语法
url = f"https://xeno-canto.org/api/3/recordings?query={urllib.parse.quote_plus(q)}&key={key}"
data = json.loads(urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'}), timeout=30).read())
```

**挑选优先级**（多键排序）：
1. 质量 q='A'
2. type 包含 song > call > 其他
3. 录音地优先 `config.user_preferences.regional_focus_country`（如 'China'；没配置就不偏向）

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

**绘画 / 艺术作品配图**：如该物种或类群在传统绘画、浮世绘、博物画、邮票等有具代表性的图像作品，**附图**到本块末尾，caption 以 `🎨` 开头并注明公版 / 许可。**没有可确证的就直接不放图，不写占位文字**（别用「暂无古画」凑一行）。

> 文字部分若**真的没有可靠信息**，写「（暂无）」而不是凑字。

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

**优先级 2**：用户没带位置 → 按下表读取 `config.json`。**对应 key 没配置就不要自作主张新建或乱放**：物种一律进 life list；其它类型告诉用户「还没有这类的存放位置，要我在 XX 页面下建一个吗？」再动手：

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

## 6. 配图规范（v2）

配图偏好由 `user_preferences.entry_images` 决定：`both`（默认，实拍首图 + 古画）/ `photo` / `art` / `none`。用户另有要求时以用户为准。

### 6.1 放哪些图

1. **实拍首图**（`photo`）：每个条目正文**第一个 block** 是该物种的代表性实拍。
   - 理由：认鸟需要，同时是画廊卡片缩略图。
   - 选图标准：**确认是目标物种**（不是近似种、幼鸟蛋巢、标本、地图）；主体清晰；**优先侧面 / 正面、能看到识别特征**（背面、远小、被枝叶遮挡的不选）；成鸟优先。
   - 雌雄异型的物种：尽量展示两性（首图选雄鸟，另在图后补一张雌鸟，各自 caption 标 ♂ / ♀）。
   - 用户提供了自己的实拍：优先用他的，caption 写 `📷 我的实拍`。
2. **古画 / 博物画**（`art`）：放在 📜 文化与演化 末尾。**有可确证的就放，没有就跳过，不凑数、不写占位**。
3. 其他图（解剖、系统树、鉴别特写）：只在用户要求时加（如 §4.2 识别区分）。

### 6.2 一律上传，不用外链

图片必须**下载后上传为 Notion 托管文件**（`entry_tools.py write-body` 自动完成），**不贴外链 URL**。原因：外链图由 Notion 服务器代抓，Wikimedia 会限流（HTTP 429），页面上图会随机裂开。分布图 PNG、频谱图、音频仍不内嵌（见 §4.3、§4.3.5）。

### 6.3 找图流程（工具）

```bash
# 实拍：在 Wikimedia Commons 物种分类里找，自动过滤非自由许可、标本/蛋/地图等，下载预览图
python3 <birding-setup>/scripts/entry_tools.py find-images "Genus species" --n 6

# 古画 / 博物画：标题或分类须含学名或英文名，且含绘画类特征，否则丢弃
python3 <birding-setup>/scripts/entry_tools.py find-images "Genus species" --art --en "English Name" --n 6
```

**必须看图确认**（用你的看图能力逐张打开返回的 `path`），确认后才把 `path / caption / source_url` 填进 spec。你无法看图时：选 rank 最靠前且标题含学名的，并在汇报里告诉用户「未经目视核对」。

没有合适的图：对应位置留空，汇报里说明，**绝不拿不相关或不确定的图凑数**。

### 6.4 署名与归属（强制）

- 实拍 caption：`📷 作者 · Wikimedia Commons · 许可证`（`find-images` 已生成，可直接用）
- 画作 caption：`🎨 作者 / 年代 / 现藏地 · 公版或许可 · 来源`
- **来源页标注的作者 / 年代你无法核实时，不要照抄成事实**：写「作者归属以来源页为准」，或只写能从画面确认的内容（如题款原文）。
- 许可证非自由（Commons 以外的来源）要逐张查清再用；拿不准就不用。

### 6.5 古画检索的补充渠道

`find-images --art` 只覆盖 Commons。要找更多：用搜索工具查 Smithsonian Open Access、Met Open Access、故宫 OPEN、东京国立博物馆 ColBase、大英博物馆、Rijksmuseum，关键词用 物种英文名 / 学名 + painting / woodblock / 花鸟图 / 鳥類図譜 / 传统画家名。查到后打开图片所在页面，确认 ① 页面存在 ② 物种身份正确（描述里有能确证的特征：喙色、羽色、尾形）③ 作者 / 年代 / 现藏地可读；然后下载到本地，在 spec 里用本地 `path`。

> ⚠️ Wikimedia 直链的 hash 前缀（如 `/commons/f/f5/`）不能凭文件名推断，必须从 File 页抄。用 `find-images` 时由 API 返回，不会出这个错。

#### 例外：xeno-canto 走 API v3，不走网页抓取

xeno-canto 网页有反爬，但 API v3 用 key 直连无墙。JSON 返回的 `gen` + `sp` 字段即为已验证的物种身份。

---

## 7. 工作流总览（一次完整调用的步骤）

用户说「记一只鸟」「记入 Notion」「把这只写详细」时。`HELPER` = `skills/birding-setup/scripts/setup_helper.py`，`TOOLS` = `skills/birding-setup/scripts/entry_tools.py`。

0. **先看配置**：`python3 HELPER status`；`ready: false` 就走 `birding-setup`，配完回到本任务。
1. **校验物种**：鸟用 AviList（`avilist-bird-lookup`）；歧义（「麻雀」「白鹭」等泛称）先问清。
2. **写字段**：`python3 HELPER add-rows`（自动补全英文名 / 目 / 科、按名称和学名去重），返回该条的 `page id`。
3. **生成正文内容**（按用户启用的模块，默认五块）：
   - 🐾 性格与行为（§4.0）→ 🧬 分类考据（§4.1）→ 🌏 分布与生态（§4.3，`TOOLS gbif`）→ 🎵 鸣声（§4.3.5，`xc_query.py`）→ 📜 文化与演化（§4.4）
   - §4.2 识别区分仅在用户问过相关问题后写入
4. **找图并看图确认**（§6.3）：实拍首图 + 古画（有则放）。
5. **写入页面**：按 `assets/entry_spec.template.json` 生成 spec，`python3 TOOLS write-body <page id> <spec>`；页面已有内容默认跳过，不覆盖。
6. **读回核对**：看返回的 `warnings`（缺模块、无首图、配图失败）；有就补，补不了就如实告诉用户。
7. **首次副作用**：涉及新目 / 新科 → 按 `avilist-bird-lookup` 流程补建（仅鸟类）。
8. **回报**：Notion 链接 + 简短摘要（写了哪几块、配了哪几张图、哪些没找到及原因）。

**批量**（一次几十种）：先 `add-rows` 全部入库，再按 `bird-batch-pipeline` 逐种写正文；`TOOLS empty-pages` 可随时列出还没有正文的物种，便于分批补。

---

## 8. 不要做的事

- ❌ 不要把不确定的内容写得很确定（用 ⚠️ 明示）
- ❌ 不要在没有触发词时擅自写入 Notion
- ❌ 不要为了凑模块而编造「文化演化」之类的内容；没有可靠信息就写「（暂无）」
- ❌ 不要交出「空壳条目」：只写了表格字段、正文和首图都没有——除非用户明确要求只记基础信息（`entry_depth` = basic）
- ❌ 章节标题不带 emoji；首图放在提示框或文字之后；把图放成外链
- ❌ 「性格与行为」里拟人、抒情，或写成长段而不是 bullet
- ❌ 把来源页上无法核实的作者 / 年代当事实抄进 caption
- ❌ 不要使用过时分类（如把一些雀形目科还按 90 年代体系排）
- ❌ 不要在第一次加载 skill 时就批量创建空架子 page——按需触发
- ❌ 不要内嵌音频 / 频谱图 / 分布图 PNG（除非 §4.3.5 的升级条件满足）

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
4. **条目版式随意**（缺模块、缺首图、标题风格不一）
5. **入库要反复确认**（用户说"记入到 Notion"就该直接做）

birding-notes 把这些痛点固化成规则，每次自然知识相关对话自动加载，等于把"我和 AI 之间签的协议"焊死。

**为什么用 AviList？** WGAC 在 2025 年 6 月发布的全球统一鸟类名录，整合 IOC / Clements/eBird / HBW / AOS 四大体系，是当前推荐的标准。eBird/Merlin 将在 2026 年版起切换到 AviList。

**为什么"识别区分"是按需触发？** 因为大多数物种在你已经亲眼见过的情况下，写"识别区分"是给未来的自己/不熟悉的读者看的——而你写笔记本是为了**自己学习**，按需触发更切合实际使用模式。

**为什么不内嵌音频和频谱图？** 实战中发现 xeno-canto 反爬、GBIF tile API 透明叠图、音频文件占 Notion 配额——综合权衡下，**链接外跳到原平台**反而是最稳定、信息密度最高的方案。（照片则相反：一律上传托管，因为外链会被限流裂图。）

**为什么用 Notion？** Notion 的数据库 + page 嵌套 + 富文本 + 富媒体 bookmark，对"维护一个有结构的物种知识库"是当前最便捷的工具。skill 通过 Notion REST API（v2026-03-11）写入。
