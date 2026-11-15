---
name: notion-image-upload-migration
description: 把 Notion 页面里的外链图片（external URL，尤其 Wikimedia）迁移为 Notion 托管文件（file_upload）。适用于外链图报 "couldn't be loaded (Error 429)"、需要永久解决加载失败的场景。含本机国内网络环境的关键坑。
agent_created: true
---

> **前置检查**：涉及 Notion 读写前，先运行 `birding-setup/scripts/setup_helper.py status`；`ready: false` 就加载 `birding-setup` 完成配置引导，再继续本任务。

# Notion 外链图 → 本地上传迁移

**用户已拍板（2026-10-25）：今后所有 Notion 库新建/补充配图一律走本 skill 的上传流程，不再贴 external URL。**

## 背景判断

Notion 的 external 图片由 **Notion 服务器代抓**并缓存；Wikimedia 等源站对 Notion 抓取 IP 池限流（Error 429），用户浏览器能打开不代表 Notion 能抓到。失败结果会被 Notion 缓存一段时间，刷新无效。根治办法：下载原图 → Notion file_uploads API 上传 → 把 image block 改为 file_upload。

## 流程（参考实现：项目 data/pilot_img_upload_2026-10-24.py、批量版 data/batch_img_upload_2026-10-25.py）

新建配图时只需第 2-4 步（无需扫描）；迁移存量时先扫描：

1. **找目标**：GET `/v1/blocks/{page_id}/children`，找 `type=image` 且 `image.type=external` 的 block，记录 block_id、url、caption。
2. **下载原图**：>18MB 时改用 thumb URL（`/wikipedia/commons/thumb/<h1>/<h2>/<name>/<宽度>px-<name>`）。
3. **上传**（三步）：
   - POST `/v1/file_uploads` `{"mode":"single_part","filename":..,"content_type":..}` → 拿 `id`
   - POST `/v1/file_uploads/{id}/send`，multipart `-F file=@本地路径`
   - （single_part 无需 complete 步骤）
4. **替换 block**：PATCH `/v1/blocks/{block_id}`，body `{"image":{"file_upload":{"id":fid},"caption":<原 caption>}}`。
5. **回读验证**：GET block 确认 `image.type=="file"` 且 caption 完好。

## 本机网络关键坑（实测，必看）

- **Notion API（2026-10-25 最优解）**：`curl --noproxy '*' --resolve api.notion.com:443:208.103.161.16`——直连 + 钉活 IP。Notion 有 4 个 IP（208.103.161.16/.17/.2/.1），**.1 常死且是 DNS 第一顺位**，默认解析撞上它就全部秒断（HTTP:000）。IP 活性会漂移，批量任务要自动探测切换（依次试 .16→.17→.2→.1，用 `https://www.notion.so` 探活）。旧方案 `--connect-to api.notion.com:443:www.notion.so:443` 走沙箱代理也可用但上游不稳。
- **Wikimedia 下载：必须 `--noproxy '*'` 直连**。走代理只有 ~3KB/s 且中途断流（IncompleteRead）；直连速度正常。与 Notion 的处理方式正好相反，别搞混。
- **PATCH image block 的 body 里不能带 `"type":"file_upload"`**，只传 `file_upload` 和 `caption`，否则 `validation_error: body.image.type should be not present`。
- **shell `while read` 循环里调 curl 必须加 `< /dev/null`**，否则 curl 吃掉循环 stdin，第一次之后的请求全部拿到空响应。
- 单文件直传上限 20MB，超过用 thumb 或分片（multi_part）上传。
- 上传前抽查下载文件大小：极小（<15KB）的未必是坏文件，邮票扫描件本来就小，用 `file` 命令验一下再判断。

## caption 合规

迁移必须原样保留 caption（作者 · 来源 · CC 许可证），这是署名合规的一部分，不能丢。
