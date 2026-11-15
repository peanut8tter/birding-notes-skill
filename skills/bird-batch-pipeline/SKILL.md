---
name: bird-batch-pipeline
description: 批量把鸟类条目从中文名清单入库到 Notion（建行、配图、写正文）的工程执行约定。当用户一次性提供多个鸟种（如「这些鸟帮我记到 Notion」、旅行预习清单、life list 批量补全）时使用。规定执行顺序、进度管理、后台运行方式，以及 Notion API、Wikimedia 图片、网络限流的避坑做法。单物种条目写作请用 birding-notes。
agent_created: true
---

> **前置检查**：涉及 Notion 读写前，先运行 `birding-setup/scripts/setup_helper.py status`；`ready: false` 就加载 `birding-setup` 完成配置引导，再继续本任务。

# 批量入库流水线

## 目的

把一份中文鸟名清单，批量变成 Notion 里图文完整的条目。本 skill 只管**工程执行**（怎么跑通、怎么不翻车）；
**内容规范**（写哪几块、术语怎么标、配图选什么）一律查 `birding-notes`；
**学名查证**一律查 `avilist-bird-lookup`。三者关系：

```
birding-notes      写什么（四块结构、术语、配图原则）
avilist-bird-lookup 数据怎么查（中文名 → 学名/目/科）
bird-batch-pipeline 批量怎么跑通（本 skill）
```

## 何时使用

- 用户一次性给出多个鸟种要入库（旅行预习清单、life list 批量补全）
- 需要为一批物种配图、合成雌雄对比图
- 需要把几十条正文批量写进 Notion

单个物种讨论、只写一条规范条目 → 用 `birding-notes`，不要加载本 skill。

---

## 执行顺序（严格按阶段，不要边查边写）

### 阶段 1：查证与去重（先全部定完，再动手写）

1. **中文名 → 候选学名** → 本地 AviList 验证（走 `avilist-bird-lookup`，不联网）
2. **检查重复**：同一物种的不同中文异写（如「黑额凤鹛」=「黑颏凤鹛」）要合并
3. **识别用户输入错误**：语音输入/笔误常见（实测遇到过「墙角树阴」实为「强脚树莺」、「方尾翁」实为「方尾鹟」、「白腰白腰草鹬」为重复输入）
4. **存疑先攒着，一批统一问一次**，不逐条打断用户
5. 最终清单落盘为 JSON（含 中文名/学名/英文名/目/科/居留型/是否雌雄异型）

#### GBIF / xeno-canto 查证的坑

- **GBIF `species/match` 可能返回属级 key**（学名没被 GBIF 收录时静默降级匹配到属，
  返回的 name 是 "Ardea Linnaeus, 1758" 这种）——**拿到 key 后必须核对返回的
  gbif_name 是种级**，否则 GBIF 书签标题会是属名。
- **属合并后旧学名会撞号**：AviList 已把 Ixobrychus 并入 Botaurus，但 GBIF 没收录
  Botaurus eurhythmus/sinensis，两个种 match 返回**同一个 key**。解法：
  **用旧属名（Ixobrychus）重查**即可拿到各自正确的种级 key。XC 同理——
  牛背鹭（Ardea coromanda）要用 Bubulcus ibis 查、苇鳽用 Ixobrychus 查。
  **建完必须校验全清单 GBIF key 无重复。**
- 隐存种拆分在 XC/GBIF 有滞后（黄腹花蜜鸟 = Cinnyris ornatus，XC 里还在
  jugularis 名下），按旧名查到后记录实际录入的属种名。

### 阶段 2：建行填字段（快，先让库里有东西）

- 建 page 时**不要传 icon**（用户不要标题前带 emoji）
- 补缺失的目/科 select 选项，一次 PATCH 补齐
- 注意 §Notion 坑：select option 建后不可改名

### 阶段 3：配图（最慢、最容易翻车，单独跑）

见下方「Wikimedia 图片管线」。

### 阶段 4：写正文

一次 PATCH 写入全部 block（图必须是第一个 block）。

---

## Notion 坑（必读）

### 网络：国内必须走 SNI 旁路

`api.notion.com:443` 被 SNI 层阻断（直连 `SSL_ERROR_SYSCALL` / exit 35 / HTTP 000），
但 `www.notion.so` 放行且解析到同一组 IP。

```bash
curl --connect-to api.notion.com:443:www.notion.so:443 ...
```

- **Python urllib 无效**（改 Host header 会被 CF 403），只能靠 curl `--connect-to` 保 SNI
- 连接**间歇性失败**（HTTP 000）是常态，不是出错，**必须重试**：循环 15 次 + 每次 sleep 2s
- `file_uploads/.../send` 端点同样要加 `--connect-to`

### 图片上传（file_upload）

```
1. POST /v1/file_uploads {"mode":"single_part","filename":...,"content_type":"image/jpeg"} → 拿 id
2. POST /v1/file_uploads/{id}/send  -F "file=@path;type=image/jpeg"          → status: uploaded
3. 建 page / 插 image block 时用 {"type":"file_upload","file_upload":{"id":...}}
```

图片存在 Notion 自己存储，不依赖外部图床、永久可达。

### 其他

- **rich_text 的 `annotations`（bold/italic）与 `text` 平级**，写进 `text` 里会 400
- **不能在最前面插 block**：`PATCH children` 只能追加或用 `after:<block_id>`。
  要让图成为第一个 block，做法：先插入后面的内容 → 把图插到某个已知块之后 → 删掉原来排前面的块
- 写入限速 ~3 req/s，操作间 sleep ≥ 0.4s；429 要退避重试
- select option **一经创建无法改名**（PATCH 静默忽略），命名前想清楚
- **⚠️ 查询分页：`POST /databases/{id}/query` 单次最多返回 100 条**。库超过 100 条时，
  不处理 `has_more` / `next_cursor` 就会漏掉后面的条目，看起来像"条目丢了"（实测踩过：
  104 条的库只看到 100 条，误以为 3 个物种被删）。**查全库一律写 while has_more 循环**。
  同理 `GET /blocks/{id}/children` 也要翻页。

### 2026 新版 Notion API（Notion-Version 2026-03-11，实测 2026-10-25）

- **新版数据库（如「猛禽预习库」40371355-…）的 `GET /databases/{id}` 不再返回 properties**，
  schema 要查 data source：先从 database 响应拿 `data_sources[0].id`，
  再 `GET /v1/data_sources/{id}`（properties 以**数组**返回，不是 dict）。
- **建 page 用 `parent: {"type": "data_source_id", "data_source_id": …}`**，老写法 parent database_id 对新库不可靠。
- **image block 的 caption 元素 `"type"` 必须是 `"text"`**（写 `"rich_text"` 会 400 validation_error）。
- Python `subprocess` 传 JSON body 时 stdin 不会被 curl 读取——`input=json.dumps(...)` 无效，
  必须把 body 写进临时文件再 `-d @file`（否则 curl 空 body 发 PATCH，Notion 静默返回原值，看似成功实则没改）。
- 新库 select 选项全空时首次写入会自动新建 option，但建之前仍要和用户对好口径（option 不可改名）。
- **Wikimedia 检索**：`generator=search` 对热门笼养/标本污染物种（如灰脸鵟鹰会命中动物园笼照、骨骼图）效果差，
  改用 `generator=categorymembers&gcmtitle=Category:<学名>&gcmtype=file` 直接翻物种分类，质量高得多。
  BAD 正则要补 `skeleton|taxiderm|cage|zoo|composite`。

---

## Wikimedia 图片管线（重灾区）

### 三个域名，三个脾气

| 域名 | 用途 | 坑 |
|---|---|---|
| `commons.wikimedia.org/w/api.php` | 查文件、取 imageinfo | 会 403 限流 |
| `upload.wikimedia.org` | 原图 | **极易 429，且恢复极慢（>10 分钟）** |
| `thumb.wikimedia.org` | 缩略图 | **独立限流桶，基本不限** |

### 铁律

1. **永远用 `thumb.wikimedia.org` 下载，绝不直接下原图**
   取法：API 加 `iiurlwidth=1600`，读返回的 `thumburl`。
   **不要自己拼 thumb URL**（曾拼出 400）——Wikimedia 只生成特定标准尺寸（如 1920px）。
2. **原图比请求宽度小时，API 不返回 thumburl**（返回原图 URL → 撞 upload 429）。
   所以**只挑宽度 ≥ 1200px 的候选图**，既保证有缩略图，也保证清晰度够当封面。
3. **python urllib 会被优先限流，curl 不会**。查 Commons 一律用 curl + 正规 UA
   （`birding-notes/1.0 (research)`）。
   判断被限流的信号：脚本输出连续 NONE，但 curl 手动查同一物种有结果。
4. 请求间隔 ≥ 2~3s，逐种进行，不要并发梭哈。

### 挑图筛选

排除文件名含这些词的（都不是能认鸟的生态照）：
`map` `distribution` `museum` `naturalis` `specimen` `illustration` `egg` `anatomy` `range`

**不要按"面积最大"盲挑**——实测挑到过分布地图和博物馆标本照。

**文件名必须有物种语义，才可信**。实测 `File:Bird from Nepal by Krishna (60).jpg`
被上传者错放进 Anthus hodgsoni 分类，纯按尺寸挑就中招了——图上根本不是树鹨。
规则：**优先选文件名含该物种英文俗名或学名的图**；文件名无语义的（`DSC1234`、`Bird from X (N)`）
一律跳过，除非没有别的选择，且选后必须目检。

**⚠️ 关键词里不要放属名**。属名是同属物种共用的（如 *Ardea* 下牛背鹭/中白鹭/大白鹭），
文件名匹配会互窜——实测牛背鹭（*A. coromanda*）被配到 *A. intermedia*（中白鹭）的图。
keywords 只用**种本名 + 特异俗名**（如 `coromanda`、`cattle egret`），宁可候选少也不要错配。

**人名/地名关键词注意拼写变体**：Schrenck/Schrenk、blanfordi/conradi 这类一个字母之差
会让 strict 过滤漏掉全部正确结果。搜不到时放宽关键词，人工再筛。

**年份像 18xx/19xx 的文件名大概率是古董版画**（如 `...1898.jpg` = Gould 手绘）——
物种可能没错但不是生态照，预习库不用。iNaturalist 导入图（`from iNaturalist`）质量参差，须目检。

**上库前目检**。有读图能力时，批量入库的图要在写入前/后**逐张过目**——
实测 49 张里混进了 4 张问题图（完全错图 1、主体是黑点 1、近缘种 1、幼鸟缺关键特征 1），
全部是文件名筛选漏掉的。近缘种陷阱：挑"石䳭"时会命中欧洲种（英国拍摄地暴露了它），
**检查拍摄地是否在该物种的实际分布区内**（东亚种却在英国拍，必假）。
幼鸟/非繁殖羽缺成鸟标志特征（如黑枕黄鹂幼鸟无黑枕），能选成鸟就选成鸟。

**手动补图也要同步图源记录**（作者/许可证/文件名写进 imgs JSON）。
实测补图时只上传了文件、没记图源 → caption 走了 fallback（"📷 Wikimedia Commons · CC 授权"），
**CC 署名丢失**（合规问题），且这条图不参与后续目检审计。补图 = 下载 + 更新记录，缺一不可。

**「类群名 - 学名」式命名（如 `Apodidae - Aerodramus fuciphagus.JPG`）多为博物馆标本照**，
下载目检再定，别被明确的学名标注骗了。

### 替换已入库的图

替换流程：上传新图 → `PATCH children` 插入新 image block（`after: <旧图块id>`）→
`DELETE` 旧图块。新块自然顶到首位，卡片缩略图随之更新。

### 雌雄异型合成

- 找文件名标了 `male` / `female` 的配对图
- 用 `scripts/compose_pair.py` 合成（默认横版：左♂右♀，无标签无空隙，两图直接紧贴）
- **找不到明确标注雌雄的配对图时，改用单图 + 正文文字说明差异**，
  绝不强行拼两张不确定的图并标注 ♂♀（属编造，违反 birding-notes「绝不编造」原则）

---

## 后台运行（关键）

**用工具的 `run_in_background` 方式启动，不要用 `nohup ... &`**。
实测 `nohup &` 启动的进程会随 shell 返回被杀掉，导致看似启动成功实则从未执行（且日志不更新，
极具迷惑性——曾因此空跑 6 小时）。

启动后**必须验证进程真的在跑**：

```bash
pgrep -f <script>.py && echo 运行中 || echo 已结束
```

### 进度文件

长时间任务要写进度 JSON（如 `run_all_progress.json`），每完成一条就落盘。
脚本崩了重跑时会自动跳过已完成的，不重复劳动。

### 启动前必做

提交后台长任务前，先跑语法检查，避免"启动即崩"：

```bash
python3 -c "import ast;ast.parse(open('script.py').read())"
```

（曾因漏写一个括号，后台脚本启动即崩，白等 6 小时。）

### 防止电脑休眠

长时间任务前启动 caffeinate（macOS）：

```bash
nohup caffeinate -dimsu -t 28800 > /tmp/caffeinate.log 2>&1 &
```

（这条 caffeinate 本身用 nohup 是可以的，它要活过 shell 退出。）

---

## 交付前检查

跑完不要假定全部成功，逐项核对：

1. 进度文件里的完成数 vs 应完成数
2. 抽查若干 page，确认**第一个 block 是 image**（Card preview 取页面内容时，只有首图会成为卡片缩略图）
3. 把失败/跳过的条目列成清单报给用户，说明原因（无大图、无配对图等）

---

## 关联 skill

| skill | 分工 |
|---|---|
| `birding-notes` | 内容规范：四块结构、术语标注、配图原则 |
| `avilist-bird-lookup` | 分类查证：中文名 → 学名/英文名/目/科 |
| `notion-api` | Notion API 完整参考（本 skill 只记实战坑） |
