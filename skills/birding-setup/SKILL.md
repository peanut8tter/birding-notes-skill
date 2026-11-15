---
name: birding-setup
description: 观鸟笔记的入口与向导——帮用户「开始」或「继续」观鸟记录：从零在 Notion 建好记录库、接入已有的 Notion 记录表、或把 Excel / eBird / 其他 App / 备忘录里的旧记录导入。当用户说「开始记录观鸟」「我想记鸟」「观鸟笔记怎么用」「初始化 / 配置 / 设置」「导入我的观鸟记录」「我已经有记录了」，或首次使用本套件，或其他 birding skill 发现尚未配置时使用。
---

# birding-setup — 开始或继续你的观鸟记录

你（AI）要带一位**你对他一无所知的用户**走完配置。他可能从没记过观鸟、可能已在 Notion 里有自己的表、也可能记在 Excel / eBird / 别的 App 里；他可能不懂 API、token、数据库这些词。目标：约 5 分钟后，他的 Notion 里有一个能用的观鸟记录库，并且已经记下了第一批鸟。

脚本：本目录 `scripts/setup_helper.py`（只用标准库）。下文 `HELPER` 指它，用 `python3 HELPER <命令>` 运行，所有命令输出 JSON。命令清单见 `python3 HELPER`（无参数）。

## 铁律
1. **说人话**。不甩术语：token 叫「一把钥匙」，数据库叫「一张表格」。先说**为什么需要**，再说怎么做。
2. **一次只问一件事**，等回复再继续。每一步做完确认成功（脚本返回 ok）再进下一步，并用一句话告诉用户「现在已经完成了什么」。
3. **不假设用户是谁**：不预设城市、不预设已有数据、不预设在中国。
4. **只新增，不改动用户已有的东西**：已有的列、已有的数据一律不动、不删。
5. **密钥只通过 HELPER 保存**（先向 Notion 校验，权限 600，存 `~/.config/birding-notes/secrets/`）。绝不把密钥写进项目文件、仓库，也不在回复里复述。
6. **别把原始 JSON 甩给用户**。把结果翻译成人话；出错时说清原因和下一步（见文末「排错」）。
7. 已完成的步骤不重复问；以 `status` 为准。

## 步骤 0：看现状
```bash
python3 HELPER status
```
- `ready: true` → 不要重走向导。问用户想做什么（记新鸟 / 导入旧记录 / 看现有 / 改设置），用 `list-rows` 告诉他「你库里已有 N 种」。
- `ready: false` → 看 `next`，从那一步继续，并告诉用户「上次已经配好了 X，我们接着做 Y」。
- 全新（没有 token）→ 进入步骤 1。

## 步骤 1：欢迎 + 路线图
用自己的话说清这几点（别照念）：
> 这个工具帮你把看过的鸟记到 Notion：你告诉我鸟名（或把旧记录丢给我），我负责查准学名和分类、整理成一条条记录，重复的自动跳过。先花约 5 分钟配好，之后一句话就能记。
> 要做 4 件事：① 连上你的 Notion ② 准备好存放记录的表格 ③ 问你两个小问题 ④ 一起记下第一只鸟。
> 你需要有一个 Notion 账号（免费版就够）。

没有 Notion 账号 → 先让用户去 notion.so 免费注册，注册好再继续。目前记录只支持存到 Notion，如实告知，不要假装有别的选项。

## 步骤 2：弄清他从哪儿来（只问这一个问题）
> 你现在的观鸟记录在哪？
> A. 还没开始记 / 想从头开始
> B. 已经在 Notion 里有一张记录表了
> C. 记在别的地方（Excel、eBird、某个观鸟 App、备忘录、微信、纸上……）

- 拿不准、或「就记了一点」→ 当 A，之后可导入。
- B 但其实是 Notion 页面里的一段清单（不是表格）→ 当 C。
- C → 先走 A 建一张新表，再导入（步骤 4C）。

## 步骤 3：连接 Notion（所有人都要做）
解释：「要让我能往你的 Notion 里写东西，需要你在 Notion 里创建一个『集成』，它会给你一串密钥，像一把钥匙。这把钥匙只能打开你**明确授权**的页面，别的页面它看不到。」

带用户做（Notion 界面可能是英文，两种叫法都给）：
1. 打开 https://www.notion.so/profile/integrations → 新建集成（New integration）
2. 名称随意（如「观鸟笔记」），类型选**内部 / Internal**，关联到他自己的工作空间 → 保存
3. 复制「内部集成密钥 / Internal Integration Secret」（以 `ntn_` 开头），粘贴给你

用户贴来后：
```bash
python3 HELPER set-notion-token <token>
```
成功 → 告诉他「已连上，集成名叫 XX」。失败 → 多半是没复制全，让他重贴。
保存后提醒一句：聊天记录里有这串密钥，介意的话走完向导后可到 Notion 重置。

> 你的运行环境若自带 Notion 连接器，也可以用它读写；但本套件的建库/导入脚本需要上面这把密钥，所以仍请按此配置。

## 步骤 4：准备存放记录的表格

Notion 的规则：集成默认**看不到任何页面**，要在 Notion 里逐个授权。所以每条路都有这一步（授权），请把点击路径讲清楚：
> 在 Notion 打开那个页面/表格 → 右上角「···」→「连接 / Connections」→ 选择刚创建的集成 → 确认。

### 4A 从零开始
1. 请用户在 Notion 新建一个**空白页面**，标题如「🐦 观鸟笔记」，并按上面的路径把它授权给集成。
2. `python3 HELPER find "观鸟笔记" --pages` 找到它。没找到 → 多半没授权，或刚建好 Notion 还没索引，让他确认授权、等几秒重试。
3. `python3 HELPER create-db <页面id>` 建表。脚本会自动保存配置和字段对应关系。
4. 用大白话告诉用户表里有什么，并给出链接（`url`）：
   - 核心：**中文名、学名**
   - 常用：英文名、目、科（分类）、首次观察的地点和日期
   - 可选：居留型（留鸟/候鸟）、IUCN 等级、本国保护等级、数据来源
   - 「不需要的列，之后直接在 Notion 里删掉就行，我写入时会自动略过。」

### 4B 接入他已有的 Notion 记录表
1. 请他把那张表授权给集成。
2. `python3 HELPER find "<表名>" --databases`（不知道名字就不带关键词，列出可选项让他挑）。
3. `python3 HELPER inspect <id>`，把结果**翻译成对照表**给他确认，例如：「你的『Name』列 = 物种名；『Latin name』= 学名；『Where』= 地点……」；识别不出的列要明说「这列我不会碰」。**必须让他确认**，他纠正就按他的来。
4. 缺的字段：解释每个有什么用，问是否新增（推荐：英文名、目、科、数据来源；居留型/保护等级看他是否需要）。强调「只新增列，不改你已有的列和数据」。
5. 保存：
   ```bash
   python3 HELPER set notion.life_list_database_id <database_id>
   python3 HELPER set notion.life_list_data_source_id <data_source_id>
   python3 HELPER map name=<标题列> sci=<学名列> ...      # 以用户确认的对照为准
   python3 HELPER add-fields en order family source       # 仅限用户同意新增的
   ```
6. `python3 HELPER list-rows`，告诉他「你已经有 N 种，之后重复的我会自动跳过」。
   - 若某列类型脚本不支持（复选框、人员、公式等），明说「这列我不会写」。

### 4C 从别处导入（先完成 4A 建新表；用户若想并入已有表则先完成 4B）
1. 问他数据在哪、怎么拿给你：
   - **eBird**：登录后 My eBird → Download My Data，邮件里收到 `MyEBirdData.csv`。每次观察一行，需按物种合并，取**最早**的日期及当时地点。有 `Scientific Name`、`Common Name`。
   - **Excel / 表格**：导出 CSV 或直接给文件；先看表头，和用户确认哪列是什么。
   - **其他观鸟 App**：看能否导出；不能就让他截图或复制清单（你的运行环境支持图片才处理截图）。
   - **备忘录 / 微信 / 纸质**：直接把文字贴过来。
2. 整理成 JSON 数组，**每个物种一项**，键用标准字段：`name`（物种名）、`sci`（学名）、`first_date`、`first_place`，其余可选。
   - 来源只有中文名/英文名、没有学名：你先给出候选学名，**必须**用 `skills/avilist-bird-lookup`（`verify_candidates.py`，数据 `assets/avilist_species.json`）校验。对不上、有歧义的不要猜，单独列出问用户。
   - 日期认不出就留空，不要编。
3. 给用户看**摘要**再动手：共 N 种、前 5 条示例、有问题的 M 条及原因。等他确认。
4. 先预演：`python3 HELPER add-rows <文件> --dry-run`；确认无误后正式写入 `python3 HELPER add-rows <文件>`。
   - 默认按学名自动补全英文名/目/科/数据来源（AviList v2025），并按名称/学名**去重**，重复运行安全。
   - 大批量约 0.35 秒/条，几百条要提前告诉用户需要几分钟。
5. 汇报：新增几条、跳过几条重复、哪些需要他核对（`notes`）。

## 步骤 5：两个小问题（都可跳过）
1. 「你主要在哪里观鸟？（城市/地区）」→
   ```bash
   python3 HELPER set user_preferences.primary_location <城市>
   python3 HELPER set user_preferences.regional_focus <地区>
   python3 HELPER set user_preferences.regional_focus_country <国家，如 China>
   ```
   说明用途：判断某种鸟在他那里是留鸟还是候鸟，写分布时优先本地情况。
2. 「记录里物种名想用中文还是英文？」→ `python3 HELPER set user_preferences.name_language zh`（或 `en`）。
   - 如果他不在中国观鸟，提醒「中国保护等级」那列对他没用，可在 Notion 里删掉。

鸣声查询需要 xeno-canto 的免费 key，**现在不用配**，只说一句「以后想查鸣声再告诉我」。他想配时：去 https://xeno-canto.org/account 注册，`python3 HELPER set-xc-key <key>`。

## 步骤 6：一起记下第一只鸟（让他看到成果）
- A / C：「说一种你最近见到的、或最想记的鸟，我现在记给你看。」
  1. 物种身份有歧义先问清（如「麻雀」「白鹭」这类泛称）。
  2. 用 `skills/avilist-bird-lookup` 查证学名；不凭记忆写学名。
  3. 单条写入：把一个对象放进 JSON 数组，`python3 HELPER add-rows -`（从标准输入读）或写临时文件。
  4. 给他 Notion 里这一行的链接，并说明：「这是基础记录。想要更详细的条目（分类考据、分布、鸣声、文化背景、配图），说『把这只写详细』即可。」详细版规范见 `skills/birding-notes/SKILL.md`。
- B：展示他已有的几条，并演示「记一只新的」。

## 步骤 7：收尾小抄
再跑一次 `status`。然后给他一张小抄（用他听得懂的话）：
- 「记一只鸟：XX，在 YY，ZZ 号」
- 「把这个 Excel / eBird 导出导进来」
- 「查一下 XX 的学名 / 分类」
- 「我已经记了多少种？」
- 「这批鸟帮我都记上」（批量）

并告知：配置在 `~/.config/birding-notes/`（换电脑后再说一次「初始化观鸟笔记」即可）；密钥只存在他自己的电脑上。

## 排错
| 现象 | 处理 |
|---|---|
| 搜不到页面/表格 | 99% 是没授权给集成。重讲「···→连接」；刚新建的页面等几秒再试 |
| token 校验失败 | 没复制全（应以 `ntn_` 开头），或密钥已被重置 → 重新复制 |
| 网络超时 / SSL 断开 | 脚本已自动重试多个 IP；仍失败就让他稍后重试或换网络，不要反复硬试 |
| 写入报 429 | 脚本会自动等待重试；大批量改小批 |
| 选项（目/科等）写不进去 | Notion 的选项名不能含英文逗号，脚本已替换为中文逗号 |
| `status` 说缺字段映射 | 旧版配置：对现有库跑 `inspect` → 确认 → `map` |
| 用户想换一张表 | 重走步骤 4（B 或 A），`set` 会覆盖旧的 ID |

## 其他 skill 如何接入
`birding-notes` / `avilist-bird-lookup` / `bird-batch-pipeline` / `notion-image-upload-migration` 在任何 Notion 操作前先跑 `status`；`ready: false` 就按本文件走向导，**配完回到用户原本的请求**，不要让他重新说一遍。写入 Notion 时，列名一律以 `config.json` 的 `notion.fields` 映射为准，不要硬编码列名。
