# birding-notes-skill

> 一份给 AI 用的"自然知识工作流协议"——专为**在 Notion 维护 life list 与自然观察笔记**的人设计。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
&nbsp;
Status: 个人在用 · 欢迎 fork

---

## 这是什么

一份 markdown 写成的 **Agent Skill**——加载到 WorkBuddy / Claude Code 等支持 Anthropic Skills 规范的 AI 客户端后，AI 在你讨论物种、观察笔记、写入 Notion 时会**自动遵守**里面的工作约定。

它不是一个软件，是 **AI 与你之间签订的工作流协议**。每次自然知识相关对话自动加载，免去你反复叮嘱的成本。

## 解决什么痛点

> 我用 AI 维护鸟类 life list 时反复遇到的几个坑：

1. **拉丁名解释啰嗦**——AI 总爱写"形容……""因……"，应当**词典式直击词根**
2. **冗余复述三件套**——中文名/英文名/学名在 Notion 字段里已有，AI 总在正文再写一遍
3. **分类过时**——AviList 在 2025 年发布、整合四大体系，AI 训练数据常停在更早版本
4. **配图填位**——用户已亲眼见过的活体照片对他**零信息增量**，但 AI 总会塞一张
5. **入库要反复确认**——用户说"记入到 Notion"就该直接做，不该再问一遍
6. **数据源不严谨**——AI 经常瞎编学名、混淆近似种、忽略地理分布

birding-notes 把上述痛点固化成规则，焊死。

## 谁该用

- 在 **Notion** 里维护鸟类 life list 或自然观察笔记
- 用 **WorkBuddy / Claude Code / Claude Desktop** 之类支持 Skills 的 AI
- 偏向「按 AviList v2025 / POWO / iNaturalist 等权威数据源 + 加 Notion 自动写入」的工作流
- 希望 AI 输出**结构化、可信、信息密度高**的物种条目

## 安装

### 1. Clone 到你的 skills 目录

```bash
# WorkBuddy 用户级（跨工作空间）
git clone https://github.com/peanut8tter/birding-notes-skill ~/.workbuddy/skills/birding-notes

# 或 Claude Code 用户级
git clone https://github.com/peanut8tter/birding-notes-skill ~/.claude/skills/birding-notes

# 或项目级（仅当前项目生效）
git clone https://github.com/peanut8tter/birding-notes-skill ./.workbuddy/skills/birding-notes
```

### 2. 配置 Notion Integration

在 [Notion Settings → Integrations](https://www.notion.so/profile/integrations) 创建一个 Internal Integration，得到 token（`ntn_...`）。

把以下 page / database **共享**给该 integration：
- 你的鸟类 life list database
- 你的"鸟类目录 Orders" database（如有）
- 你的"自然 / 鸟 / 百草园 / 虫"等根 page

把 token 存到 `~/.workbuddy/secrets/notion.json`：

```bash
mkdir -p ~/.workbuddy/secrets
chmod 700 ~/.workbuddy/secrets
echo '{"integration_token": "ntn_xxxxxxxxx"}' > ~/.workbuddy/secrets/notion.json
chmod 600 ~/.workbuddy/secrets/notion.json
```

### 3. 拷贝并填写 config.json

```bash
cd ~/.workbuddy/skills/birding-notes  # 或你 clone 的位置
cp config.example.json config.json
```

编辑 `config.json`，填入你的：
- Notion database / page IDs（用 `mcp__notion__notion-search` 工具或 Notion API 查到）
- 地理偏好（默认是广州 / 华南 / China，可改）

### 4. 注册 xeno-canto API key（鸟类鸣声查询）

去 [xeno-canto.org/account](https://xeno-canto.org/account) 免费注册账号，登录后底部生成 API key。

```bash
echo '{"api_key": "<your_xc_key>"}' > ~/.workbuddy/secrets/xenocanto.json
chmod 600 ~/.workbuddy/secrets/xenocanto.json
```

### 5. 安装配套 skill：avilist-bird-lookup（推荐）

鸟类专项数据查证 skill。本 skill 在写鸟类条目时会调用它做学名/英文名/目/科查证。

```bash
git clone https://github.com/peanut8tter/avilist-bird-lookup ~/.workbuddy/skills/avilist-bird-lookup
```

> 如果你只用本 skill 不写鸟，跳过这步即可。

## 使用

加载完 skill 后，直接和 AI 对话即可：

```
"帮我查查红嘴蓝鹊"            → AI 按规则给出分类考据 + 分布 + 鸣声 + 文化背景
"对比白头鹎和黑短脚鹎"        → AI 触发「识别区分」块
"记入到 Notion"               → AI 直接写到对应数据库 / page
"加进 life list，地点：白云山" → AI 写 life list 并填首次地点
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
├── SKILL.md              # 主 skill 文件，AI 加载的协议
├── README.md             # 你正在看的这个
├── LICENSE               # MIT
├── config.example.json   # 配置范例（你 cp 一份改成 config.json）
├── .gitignore
└── scripts/
    └── xc_query.py       # xeno-canto API 查询脚本（CLI）
```

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
- WorkBuddy / Claude Code 团队 — Skills 框架

## 贡献

欢迎 issue 和 PR。特别欢迎：

- 不同地区的「高风险物种清单」补充（华南/华北/西南/海外）
- 古画 / 博物画 / 邮票数据源扩展
- 其他权威数据库的对接（如鱼类、两栖、爬行）
- 配套脚本（识别图自动生成、对比表渲染等）

## License

MIT — see [LICENSE](LICENSE).
