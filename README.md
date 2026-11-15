# birding-notes-skill

> 让 AI 帮你**开始、或继续**观鸟记录：把看过的鸟记进 Notion，学名分类由 AI 对照 AviList 查准，不瞎编。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
&nbsp;
适用于 Codex · Claude Code · WorkBuddy · Cursor 等支持 Agent Skills（SKILL.md）的 AI 助手

---

## 30 秒上手

```bash
git clone https://github.com/peanut8tter/birding-notes-skill.git ~/birding-notes-skill
cd ~/birding-notes-skill && ./install.sh
```

然后打开你的 AI 助手（装完 skill 后需重启），对它说：

> **帮我开始观鸟记录**

它会先介绍自己，再**问你的记录习惯**（记过吗？记在哪？每次想记哪些信息？要不要每种鸟一页完整资料？要哪些模块、配不配图？），然后按你的回答把东西搭起来。约 5–10 分钟，**不需要你懂任何技术**，只需要一个 Notion 账号（免费版就够）。

## 你会得到什么

表格里每种鸟一行，列由你定（名称、学名、英文名、分类、首次观察时间地点、居留型、天气、同行者……）。点开每一行可以是一页**完整资料**：

| 顺序 | 内容 |
|---|---|
| 首图 | 一张代表性**实拍图**（署名、许可证写在图下；也是画廊视图的缩略图） |
| 提示框 | 首次记录：日期 · 地点 |
| 🐾 性格与行为 | 习性、食性、行为特征——只写可核对的事实要点 |
| 🧬 分类考据 | 拉丁名词源、系统位置 |
| 🌏 分布与生态 | 分布范围 + GBIF 全球出现记录链接 |
| 🎵 鸣声 / 鸣唱 | 鸣声描述 + xeno-canto 真实录音链接 |
| 📜 文化与演化 | 名字典故、诗词民俗、科学史；有传世古画 / 博物画的会配图 |

模块、配图都可以按你的喜好开关；只想记表格那几列也行。

## 不管你现在处于哪种情况

| 你的情况 | AI 会帮你做什么 |
|---|---|
| **还没开始记** | 按你选的字段在 Notion 里新建一张观鸟记录表，再陪你记下第一只鸟——连同完整资料页 |
| **Notion 里已经有一张记录表** | 读懂你现有的表头并和你确认对应关系；只新增缺的列，**不改你已有的列和数据**；新记的鸟沿用你的列名 |
| **记在别处**（Excel、eBird、观鸟 App、备忘录、微信、纸上） | 先建好新表，再把旧记录整理、核对学名、去重后批量导入（eBird 导出文件、CSV、直接粘贴文字都行）；完整资料可分批补 |

之后日常使用就是一句话：

```
记一只鸟：白头鹎，今天在海珠湿地见到
把这个 eBird 导出文件导进来
把这只写详细  /  补下一批
我已经记了多少种？还有几种没有完整资料？
```

## 这是什么

一份 markdown 写成的 **Agent Skill**——加载到任何支持 **Agent Skills 开放标准**（`SKILL.md`）的 AI 助手（Codex、Claude Code、WorkBuddy、Cursor 等）后，AI 在你讨论物种、观察笔记、写入 Notion 时会**自动遵守**里面的工作约定。

它不是一个软件，是 **AI 与你之间签订的工作流协议**；其中的脚本（建表、导入、找图、写页面）是给 AI 调用的，你不用碰。

套件由 5 个 skill 组成，**新手只需要关注前 3 个**，装好就行，AI 会按需调用：

| skill | 做什么 | 谁会用到 |
|---|---|---|
| `birding-setup` | 入口与向导：建表 / 接入已有表 / 导入旧记录 / 批量写入 | 所有人，第一次必用 |
| `birding-notes` | 条目写作规范：分类考据、分布、鸣声、文化背景、配图 | 所有人 |
| `avilist-bird-lookup` | 用 AviList v2025 查证学名、英文名、目、科 | 所有人 |
| `bird-batch-pipeline` | 一次记几十种的批量流水线（建行、配图、写正文） | 进阶 |
| `notion-image-upload-migration` | 把外链图迁成 Notion 托管图（避免外链 429） | 进阶 |

## 解决什么痛点

> 作者用 AI 维护鸟类 life list 时反复遇到的几个坑，本套件就是针对它们设计的：

1. **拉丁名解释啰嗦**——AI 总爱写"形容……""因……"，应当**词典式直击词根**
2. **冗余复述三件套**——中文名/英文名/学名在 Notion 字段里已有，AI 总在正文再写一遍
3. **分类过时**——AviList 在 2025 年发布、整合四大体系，AI 训练数据常停在更早版本
4. **配图填位**——用户已亲眼见过的活体照片对他**零信息增量**，但 AI 总会塞一张
5. **入库要反复确认**——用户说"记入到 Notion"就该直接做，不该再问一遍
6. **数据源不严谨**——AI 经常瞎编学名、混淆近似种、忽略地理分布

birding-notes 把上述痛点固化成规则，焊死。

## 谁该用

- 在 **Notion** 里维护鸟类 life list 或自然观察笔记
- 用 **Codex / Claude Code / WorkBuddy / Cursor** 等任一支持 Skills（或 AGENTS.md）的 AI 助手
- 偏向「按 AviList v2025 / POWO / iNaturalist 等权威数据源 + 加 Notion 自动写入」的工作流
- 希望 AI 输出**结构化、可信、信息密度高**的物种条目

## 安装

### 1. Clone 并一键链接（含 5 个 skill）

```bash
git clone https://github.com/peanut8tter/birding-notes-skill.git ~/birding-notes-skill
cd ~/birding-notes-skill
./install.sh                # 默认装到 ~/.agents/skills（Codex 等通用位置）
```

按你用的助手选目标：

| 命令 | 链接到 | 适用 |
|---|---|---|
| `./install.sh` | `~/.agents/skills` | **Codex** 及遵循通用标准的助手（推荐默认） |
| `./install.sh claude` | `~/.claude/skills` | Claude Code |
| `./install.sh workbuddy` | `~/.workbuddy/skills` | WorkBuddy |
| `./install.sh codex` | `~/.codex/skills` | Codex 旧版目录 |
| `./install.sh all` | 以上全部 | 多个助手并用 |
| `./install.sh /你的/路径` | 任意目录 | 其他 |

用软链安装，以后 `git pull` 即同步更新。

**你的助手不支持 skills？** 把仓库里的 [`AGENTS.md`](AGENTS.md) 复制到项目根目录（或让助手先读它），它会指引助手按需读取 `skills/*/SKILL.md`。

### 2. 配置：对 AI 说「帮我开始观鸟记录」

不用手写任何配置。`birding-setup` 会先问你**现在的记录在哪**，再走对应的路：

1. 连接 Notion：带你创建一个「集成」并拿到密钥（脚本会先向 Notion 校验再保存，权限 600）
2. 准备记录表：**从零新建** / **接入你已有的表**（自动识别表头、只新增缺的列）/ **从 Excel、eBird 等导入旧记录**
3. 两个小问题：你在哪观鸟、物种名用中文还是英文（都可跳过）
4. 一起记下第一只鸟

之后任何观鸟相关的请求，如果还没配置，AI 会自动进入这个向导，配完再继续你原来的请求。

存放位置（都在仓库外，不会被提交）：
- 配置：`~/.config/birding-notes/config.json`（含「标准字段 → 你的列名」对应关系）
- 密钥：`~/.config/birding-notes/secrets/notion.json`、`xenocanto.json`
- 想换位置：设置环境变量 `BIRDING_NOTES_HOME`
- 换电脑：再说一次「帮我开始观鸟记录」，AI 会识别出你已有的表并接上，不会重复建表

### 3. AviList 本地数据（无需操作）

`assets/avilist_species.json`（AviList v2025，11,131 种）已随仓库提供，`avilist-bird-lookup` 直接查询即可，无需再下载解析。

## 使用

装好并配置后，直接和 AI 对话：

```
"帮我查查红嘴蓝鹊"            → 分类考据 + 分布 + 鸣声 + 文化背景
"对比白头鹎和黑短脚鹎"        → 「识别区分」块
"记一只鸟：XX，在 YY"          → 写进你的记录表，自动补全学名分类
"导入我的 eBird 数据"          → 按物种合并、核对学名、去重后批量写入
"把这只写详细"                 → 在条目正文里补全分类考据 / 分布 / 鸣声 / 文化背景
```

## 内容结构（精简）

进 Notion 的物种 / 目 / 科条目固定 4 块（鸟类多一块鸣声）：

| 块 | 是否必填 | 内容 |
|---|---|---|
| 🧬 分类考据 | 必填 | 拉丁名词源（词典式）+ 系统位置 + 分类沿革 |
| 🔍 识别区分 | 按需触发 | 用户问对比时才写 |
| 🌏 分布与生态 | 必填 | 1~2 句话 + GBIF 物种页 bookmark |
| 🎵 鸣声 / 鸣唱 | 鸟类必填 | 拟声文字 + xeno-canto 录音页 bookmark |
| 📜 文化与演化 | 必填 | 名字典故、人类互动、演化背景；如有古画就配 |

## 数据源标准

| 类群 | 标准 |
|---|---|
| 鸟类 | AviList v2025（WGAC 2025 年 6 月发布的全球统一名录） |
| 植物 | POWO + 《中国植物志》 |
| 昆虫 | iNaturalist + Catalogue of Life |

## 文件结构

```
birding-notes-skill/
├── skills/
│   ├── birding-setup/                 # 首次配置向导（一问一答）
│   ├── birding-notes/                 # 主协议：术语、数据源、Notion 落地规范
│   ├── avilist-bird-lookup/           # AviList v2025 学名/目/科查证 + LifeList 上新流程
│   ├── bird-batch-pipeline/           # 批量建行、配图流水线（examples/ 为可复用脚本）
│   └── notion-image-upload-migration/ # 外链图迁移为 Notion 托管文件
├── assets/avilist_species.json        # AviList 本地数据
├── AGENTS.md                          # 不支持 skills 的助手入口
├── install.sh                         # 一键软链
├── config.example.json                # 配置字段说明（实际配置由向导生成，不在仓库内）
└── LICENSE
```

> examples/ 里的脚本从环境变量 `NOTION_TOKEN` 或 `~/.config/birding-notes/secrets/notion.json` 读取 token，**不要把 token 写进仓库**。

## 设计原则

1. **不复述 Notion 字段**——三件套、居留型走字段，正文不重复
2. **拉丁名词典式**——只列词根 + 含义，不写解释性补充
3. **配图遵循信息增量原则**——古画/解剖/系统树优先，普通生态摄影不放
4. **数据源严格分层**——鸟走 AviList，植物走 POWO，昆虫走 iNat/CoL
5. **入库直接执行**——触发词出现就直接写，不再追问
6. **学名身份必须验证**——古画/录音/分布图必须经 WebFetch 或 API 确认物种身份
7. **不内嵌不稳定的资源**——音频/频谱图/分布图 PNG 经实测都不可靠，统一用 bookmark 链接外跳

## 实战教训（已在 SKILL.md 内固化）

- ❌ xeno-canto sono PNG 被 Anubis 反爬拦，**不能内嵌**
- ❌ GBIF v2 tile API PNG 是透明叠加层无底图，**不能内嵌**
- ❌ Notion `<audio>url</audio>` 必须 `<audio src="url">caption</audio>`，否则不渲染播放器
- ✅ Wikimedia Commons 图片直链 + Notion external image block 是最稳的内嵌方式

## 数据来源版权

本 skill 引用的数据源各自有许可证：

- **AviList**：CC BY 4.0
- **POWO**：CC BY 3.0
- **iNaturalist** 录音/照片：各贡献者 CC 授权
- **xeno-canto** 录音：各贡献者 CC 授权（多为 BY-NC-SA）
- **Wikimedia Commons** 媒体：各文件页面查看
- **GBIF** occurrence data：CC0 / CC BY / CC BY-NC

skill 本身（本仓库）：MIT。

## 致谢

- [AviList](https://avilist.org) — 全球鸟类统一名录
- [xeno-canto](https://xeno-canto.org) — 全球鸟鸣公民科学库
- [GBIF](https://www.gbif.org) — 全球生物多样性数据
- [Wikimedia Commons](https://commons.wikimedia.org) — 公开许可的媒体
- 郑光美《中国鸟类分类与分布名录》第三版 — 中文译名标准
- Anthropic 与 OpenAI 等推动的 [Agent Skills](https://agentskills.io) 开放标准

## 贡献

欢迎 issue 和 PR。特别欢迎：

- 不同地区的「高风险物种清单」补充（华南/华北/西南/海外）
- 古画 / 博物画 / 邮票数据源扩展
- 其他权威数据库的对接（如鱼类、两栖、爬行）
- 配套脚本（识别图自动生成、对比表渲染等）

## License

MIT — see [LICENSE](LICENSE).
