# AGENTS.md — 观鸟笔记套件入口

本仓库是一组遵循开放 **Agent Skills 标准**（`SKILL.md`）的 skill，用于在 Notion 中维护鸟类 life list 与自然观察笔记。**不依赖任何特定 AI 客户端。**

如果你的助手原生支持 skills（Codex、Claude Code、WorkBuddy 等），运行 `./install.sh` 即可，不需要本文件。
如果不支持，请按下面的规则工作：

## 规则
1. **首次使用先配置**：读 `skills/birding-setup/SKILL.md`，按其中的步骤一问一答带用户配好 Notion token 与数据库 ID。状态检查命令：
   `python3 skills/birding-setup/scripts/setup_helper.py status`
2. **谈论物种 / 写 Notion 条目 / 用户说「记入 Notion」「LifeList 上新」时**，读并遵守 `skills/birding-notes/SKILL.md`。
3. **鸟类分类学与英文名**：按 `skills/avilist-bird-lookup/SKILL.md`，用 `assets/avilist_species.json`（AviList v2025）查证，不凭记忆写学名。
4. **批量建行 / 配图**：读 `skills/bird-batch-pipeline/SKILL.md`；**外链图迁移**：读 `skills/notion-image-upload-migration/SKILL.md`。
5. **密钥安全**：token 只存放在 `~/.config/birding-notes/secrets/`（或环境变量 `NOTION_TOKEN`），**绝不写进仓库、项目文件或回复中**。
