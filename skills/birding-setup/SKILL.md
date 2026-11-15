---
name: birding-setup
description: 观鸟笔记套件的首次配置向导。当用户首次使用、说「初始化/配置/设置观鸟」、或其他 birding skill 发现缺少 Notion token / life list 数据库 ID 时加载。一步步询问并保存 Notion token、数据库 ID、xeno-canto key、地理偏好。
---

# birding-setup — 首次配置向导

目标：用户装完 skill 后，**不需要手写任何 JSON**。你（AI）一问一答带他配完，每步校验后再进下一步。

脚本：`scripts/setup_helper.py`（只用标准库）。下文 `HELPER` = 本 skill 目录下的 `scripts/setup_helper.py`。

## 铁律
- **一次只问一件事**，等用户回复再继续，不要把所有问题一次性抛出。
- **token 只通过 `HELPER` 保存**（会先向 Notion 校验，权限 600 存到 `~/.config/birding-notes/secrets/`）。不要把 token 写进任何项目文件、仓库、日志或回复里复述。
- 用户贴了 token 后，保存完提醒他：聊天记录里有明文，需要的话可以事后去 Notion 重置。
- 已完成的步骤不要重复问；以 `status` 的输出为准。

## 流程

### 0. 先看状态
```bash
python3 HELPER status
```
返回 `ready: true` 就告诉用户「已配置好」并结束，不要多问。否则按 `next` 字段继续。

### 1. Notion token（必需）
向用户说明并提问：
> 需要一个 Notion Internal Integration token。获取方法：打开 https://www.notion.so/profile/integrations → 新建 integration（类型选 Internal）→ 复制「Internal Integration Secret」（以 `ntn_` 开头）。把它贴给我。

用户贴出后：
```bash
python3 HELPER set-notion-token <token>
```
- `ok: true` → 告诉用户对应的 integration 名称，进入下一步
- 失败 → 说明原因（多半是复制不全 / 贴错），让用户重贴

### 2. 共享页面给 integration，并定位 life list 数据库（必需）
告诉用户：
> 在 Notion 里打开你的鸟类 life list 数据库，右上角 `…` → `Connections` → 添加刚才创建的 integration。（没有数据库的话告诉我，我帮你按推荐字段新建一个。）

用户确认后：
```bash
python3 HELPER find "<数据库名，问用户>"
```
- 找到多个 → 列出标题让用户选
- 一个都没有 → 多半是没共享成功，回到上面那步
选定后**两个 ID 都保存**（新版 Notion 搜索返回的是数据源，结果里同时给出 `data_source_id` 和 `database_id`）：
```bash
python3 HELPER set notion.life_list_database_id <database_id>
python3 HELPER set notion.life_list_data_source_id <data_source_id>
```
保存后可用 `GET /v1/data_sources/<data_source_id>` 确认字段（中文名、学名、居留型等）存在。

### 3. 可选项（逐个问，允许跳过）
a. **目录库 / 根页面**：「你有『鸟类目录 Orders』数据库或自然根页面吗？」有就 `find` + `set notion.orders_database_id <id>`，没有跳过。
b. **xeno-canto API key**（鸣声查询用）：「要查鸟类鸣声吗？去 https://xeno-canto.org/account 免费注册拿 key。」有就 `python3 HELPER set-xc-key <key>`。
c. **地理偏好**：问常驻城市与关注区域，写入：
```bash
python3 HELPER set user_preferences.primary_location 广州
python3 HELPER set user_preferences.regional_focus 华南
```
（用于居留型判定与分布描述的默认地点。）

### 4. 收尾
再跑一次 `status`，向用户汇报：哪些已配、哪些跳过。告诉他：
> 以后直接说「LifeList 上新了 X 只鸟」就会走完整流程。配置文件在 `~/.config/birding-notes/config.json`，token 在同目录 `secrets/`，换电脑需重新配一次（再触发本向导即可）。

## 其他 skill 如何接入
birding-notes / avilist-bird-lookup / bird-batch-pipeline 在任何 Notion 操作前先跑 `status`；`ready: false` 就按本文件走向导，**完成配置后再回到用户原本的任务**，不要让用户重新提需求。
