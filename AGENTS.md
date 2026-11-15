# AGENTS.md — 观鸟笔记套件入口

本仓库是一组遵循开放 **Agent Skills 标准**（`SKILL.md`）的 skill，帮用户**开始或继续**观鸟记录（记在 Notion）。**不依赖任何特定 AI 客户端。**

如果你的助手原生支持 skills（Codex、Claude Code、WorkBuddy 等），运行 `./install.sh` 即可，不需要本文件。
如果不支持，请按下面的规则工作。

## 规则
1. **用户想开始 / 继续观鸟记录、或首次使用、或说「初始化」「配置」「导入我的记录」**：读 `skills/birding-setup/SKILL.md`，按步骤走。
   - **第一条回复必须是自我介绍 + 询问用户的记录习惯**（记过吗？记在哪？想记哪些信息？要不要每种鸟一页完整资料？要哪些模块、配不配图？），再据此建表和写条目。不要上来就要 token。
   - **不要假设用户是谁**：他可能从没记过、可能已有 Notion 表、也可能记在 Excel / eBird / 别的 App 里；向导里都有对应流程。
   - 状态检查：`python3 skills/birding-setup/scripts/setup_helper.py status`
2. **写条目 / 用户说「记一只鸟」「记入 Notion」「把这只写详细」时**：读并遵守 `skills/birding-notes/SKILL.md`。条目版式固定为：**实拍首图 → 提示框 → 🐾 性格与行为 → 🧬 分类考据 → 🌏 分布与生态 → 🎵 鸣声 → 📜 文化与演化**，章节标题必须带 emoji；用户启用完整条目时，**不要只写表格字段就收工（空壳条目）**。写页面用 `skills/birding-setup/scripts/entry_tools.py write-body`，图片一律上传、不用外链。
3. **鸟类分类学与英文名**：按 `skills/avilist-bird-lookup/SKILL.md`，用 `assets/avilist_species.json`（AviList v2025）查证，不凭记忆写学名。
4. **批量建行 / 配图**：读 `skills/bird-batch-pipeline/SKILL.md`；**外链图迁移**：读 `skills/notion-image-upload-migration/SKILL.md`（进阶用法）。
5. **密钥安全**：token 只存放在 `~/.config/birding-notes/secrets/`（或环境变量 `NOTION_TOKEN`），**绝不写进仓库、项目文件或回复中**。
6. **说人话**：用户可能完全不懂 API / token / 数据库，一次只问一件事，做完一步确认成功再进下一步。
7. **找不到可靠的图或事实时如实说明，不要凑数**；来源页上无法核实的作者 / 年代不要当事实写进图注。
