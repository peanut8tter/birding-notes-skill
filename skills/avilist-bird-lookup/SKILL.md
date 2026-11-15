---
name: avilist-bird-lookup
description: 用 AviList v2025 官方数据为中国常见鸟类查证学名、英文 common
  name、目（Order）、科（Family）。当用户需要按 AviList 标准记录鸟类分类学信息（特别是要写入 Notion
  数据库），或验证某个中文鸟名对应的 AviList 学名/英文名/科目时使用。skill 提供本地 AviList 数据查询脚本，避免逐条联网搜索。
description_zh: AviList 鸟类查证
description_en: AviList bird lookup
agent_created: true
---

> **前置检查**：涉及 Notion 读写前，先运行 `birding-setup/scripts/setup_helper.py status`；`ready: false` 就加载 `birding-setup` 完成配置引导，再继续本任务。

# avilist-bird-lookup

## When to use

触发条件（任一满足即用）：
- 用户提到"按 AviList 标准记录鸟"、"补全鸟类目/科"、"鸟类分类学填表"
- 用户提供中文鸟名列表，要求查证学名 / 英文 common name / 目 / 科
- 需要把鸟类信息写入 Notion 数据库（看懂鸟、life list、观鸟笔记类）
- 验证某个鸟名是否符合 AviList v2025 当前分类

不要用于：
- 单纯查"这是什么鸟"这种识别问题（需要图片/特征描述）
- 鸟类生态、行为、迁徙等非分类学问题

## Background

AviList 是 WGAC 在 2025 年 6 月发布的全球统一鸟类名录，整合 IOC、Clements/eBird、HBW/BirdLife、AOS 四大体系，是当前推荐的标准。中文工作空间中，分类学和英文名都使用 AviList，中文译名使用郑光美《中国鸟类分类与分布名录》第三版。

AviList 官网（avilist.org）只提供 Excel 下载，没有 API/CSV。本 skill 提供本地查询脚本。

## Steps

### 1. 准备本地数据

**优先直接用仓库自带数据**：`<仓库根>/assets/avilist_species.json`（AviList v2025，11,131 种，已解析好）。
`verify_candidates.py` 默认就读它，**文件存在则跳过本步**。

仅当该文件缺失、或 AviList 发布新版需要更新时，才重新下载解析：

```bash
# 下载官方数据（xlsx 放临时目录即可）
curl -sL -o /tmp/avilist-v2025.xlsx \
  "https://www.avilist.org/wp-content/uploads/2025/06/AviList-v2025-11Jun-short.xlsx"

# 准备 Python 环境
VENV=~/.venvs/birding
if [ ! -d "$VENV" ]; then python3 -m venv $VENV; fi
$VENV/bin/pip install --quiet openpyxl

# 解析为 JSON（默认写到 <仓库根>/assets/avilist_species.json）
$VENV/bin/python3 scripts/parse_avilist.py /tmp/avilist-v2025.xlsx
```

参考脚本: @scripts/parse_avilist.py

### 2. 查证一批鸟名

a. 先准备候选学名列表（中文名 → 候选学名），来源可以是已有的中国鸟类知识或郑光美名录
b. 跑校验脚本：@scripts/verify_candidates.py
c. 对未匹配的：用同属其他物种或英文名搜索调整学名
d. 对高风险条目（属名变更、近年拆分、地理种）做近缘种交叉确认

### 3. 高风险条目必须做交叉确认

以下几类容易混淆，**绝不能凭中文名直接定**：
- **同名误记**：广州/华南"麻雀" = 树麻雀 *Passer montanus*，不是家麻雀
- **属名变更**：黄腹山雀 *Periparus venustulus*（不是 Pardaliparus）、棕头鸦雀 *Suthora webbiana*（不是 Sinosuthora）、矛纹草鹛 *Pterorhinus lanceolatus*（旧 Babax）、红尾水鸲 *Phoenicurus fuliginosus*（AviList v2025 已把单型属 *Rhyacornis* 并入 *Phoenicurus*；旧名 *Rhyacornis fuliginosa*）
- **属名变更**：白顶溪鸲 *Phoenicurus leucocephalus*（旧 *Chaimarrornis*，同 *Rhyacornis* 一并并入 *Phoenicurus*）
- **种级合并**：北灰鹟 **Muscicapa dauurica**（Asian Brown Flycatcher）——AviList v2025 **不收录** *M. latirostris*，已并入 *dauurica*；查东南亚/东亚记录时按 *M. dauurica* 记
- **未被承认的拆分**：东亚石䳭 AviList v2025 **不承认** *Saxicola stejnegeri*，对应种为 **S. maurus**（Siberian Stonechat）
- **已承认的拆分（斑椋鸟）**：AviList v2025 已拆出泰国种群——**曼谷斑椋鸟 = Gracupica floweri（Siamese Pied Myna）**，不是 *G. contra*（Indian Pied Myna 印度斑椋鸟，分布印度次大陆）
- **东南亚种中文名（易错，已踩坑 2026-09-18）**：*Pycnonotus blanfordi*=**纹耳鹎**（不是纹喉鹎）；*Rhipidura javanica*=**斑扇尾鹟**（不是白喉扇尾鹟）；*Pycnonotus goiavier*=**白眉黄臀鹎**（不是白喉红臀鹎）；*Microcarbo niger*=黑颈鸬鹚✓
- **拆分种**：暗绿绣眼广州 = *Z. simplex*（Swinhoe's White-eye），不是 *Z. japonicus*
- **乌鸫**：华南 = *Turdus mandarinus*（Chinese Blackbird），AviList 仍独立成种
- **大山雀**：华南 = *Parus cinereus*（Cinereous Tit）；AviList 已把 *P. minor* 合并入 *P. major*
- **喜鹊**：东亚 = *Pica serica*（Oriental Magpie），AviList 已拆分
- **金腰燕** = *Cecropis daurica*，AviList 英文名为 **Eastern Red-rumped Swallow**（拆分自原 Red-rumped Swallow）
- **斑嘴鸭**：东亚 = *Anas zonorhyncha*（拆分自 *A. poecilorhyncha*）
- **属名变更（长嘴剑鸻）**：AviList v2025 = **Thinornis placidus**（已移出 *Charadrius*；旧名 *Charadrius placidus*）
- **属名变更+拆分（牛背鹭）**：AviList v2025 = **Ardea coromanda**（Eastern Cattle Egret）——*Bubulcus* 属整体并入 *Ardea*，且东西种群拆分；GBIF 主干与 xeno-canto 检索仍用 *Bubulcus coromandus* 兜底
- **属名合并（牛背鹭）**：AviList v2025 已把 *Bubulcus* 并入 *Ardea*——东亚/东南亚 = **Ardea coromanda**（Eastern Cattle Egret），西方 = *Ardea ibis*；旧名 *Bubulcus coromandus* 查不到
- **英文名易记错（以本地 JSON 为准，勿凭印象）**：*Cinnyris jugularis* = **Garden Sunbird**（不是 Olive-backed）；*Streptopelia tranquebarica* = **Red Collared Dove**（不是 Red Turtle Dove）；*Rhipidura javanica* = **Sunda Pied Fantail**；*Acridotheres leucocephalus* = **Vinous-breasted Myna**（不是 Starling）
- **种级拆分（普通鵟，2026-10-25）**：AviList v2025 已把东亚普通鵟拆为独立种 **Buteo japonicus（Eastern Buzzard 东方鵟）**；*Buteo buteo* 仅指欧洲种群。中文名沿郑光美仍作「普通鵟」，旧记法 *B. buteo japonicus*。同属近缘：大鵟 *B. hemilasius*、喜山鵟 *B. refectus*，三者野外辨识是经典难题。
- **属级拆分（鹰，2026-11-09）**：AviList 把 *Accipiter* 的多数「鹰」拆入 **Tachyspiza**——赤腹鹰 = **Tachyspiza soloensis**（Chinese Sparrowhawk，不是 *Accipiter soloensis*）；*Accipiter* 属名下主要保留雀鹰/苍鹰系。凭「Accipiter」旧名会查不到。

- **科级迁移（方尾鹟，2026-11-01）**：*Culicicapa ceylonensis* 在 AviList v2025 属 **玉鹟科 Stenostiridae**（Fairy Flycatchers），不是鹟科——旧名录（郑光美 2011）放鹟科，凭中文名「鹟」会填错科
- **属级大迁移（小型鸻，2026-11-09）**：AviList v2025 已把 Charadrius 的多数小型鸻整体移入 **Anarhynchus**（弯嘴鸻属）——环颈鸻 = *A. alexandrinus*（Kentish Plover）、白脸鸻 = *A. dealbatus*（White-faced Plover）、蒙古沙鸻 = *A. mongolus*；GBIF/xeno-canto 主干仍用旧属名 Charadrius（查 GBIF 用 Charadrius dealbatus / C. mongolus，key=10986978 / 9722670）
- **种级拆分（沙鸻复合体，2026-11-09）**：原「Lesser Sand Plover」复合体拆为 **Anarhynchus mongolus（Siberian Sand Plover，西伯利亚繁殖）** 与 **A. atrifrons（Tibetan Sand Plover，青藏繁殖）**；郑光美中文名「蒙古沙鸻」对应 A. mongolus，AviList 英文名已不是 Mongolian Plover
- **保护等级易错（鸬鹚，2026-11-09）**：2021 名录鸬鹚科**仅黑颈鸬鹚、海鸬鹚二级**——普通鸬鹚未列入一二级，按三有填（勿凭印象填二级）
- **白脸鸻（2026-11-09）**：IUCN 2023 已按独立种评估为 LC；华南沿海留鸟；2023 三有名录未以本名单列，按原环颈鸻口径填三有并在正文注明
- **LifeList 单条上新的最新可复用脚本**：`skills/bird-batch-pipeline/examples/create_2026-11-01.py`（建行+全字段含 IUCN/中国保护等级+蜂鹰样板 bullet 正文+上传配图，可重入）

### 4. 中文目/科映射表（备用）

中国常见目/科的中文译名（基于郑光美第三版）：

```python
order_cn = {
    'Anseriformes': '雁形目', 'Galliformes': '鸡形目',
    'Caprimulgiformes': '夜鹰目', 'Cuculiformes': '鹃形目',
    'Columbiformes': '鸽形目', 'Gruiformes': '鹤形目',
    'Charadriiformes': '鸻形目', 'Pelecaniformes': '鹈形目',
    'Suliformes': '鲣鸟目', 'Podicipediformes': '䴙䴘目',
    'Strigiformes': '鸮形目', 'Coraciiformes': '佛法僧目',
    'Piciformes': '䴕形目', 'Falconiformes': '隼形目',
    'Accipitriformes': '鹰形目', 'Passeriformes': '雀形目',
}
family_cn = {
    'Anatidae': '鸭科', 'Caprimulgidae': '夜鹰科', 'Cuculidae': '杜鹃科',
    'Columbidae': '鸠鸽科', 'Rallidae': '秧鸡科', 'Ardeidae': '鹭科',
    'Podicipedidae': '䴙䴘科', 'Strigidae': '鸱鸮科', 'Alcedinidae': '翠鸟科',
    'Megalaimidae': '亚洲拟啄木鸟科', 'Pycnonotidae': '鹎科',
    'Estrildidae': '梅花雀科', 'Aegithalidae': '长尾山雀科', 'Paridae': '山雀科',
    'Paradoxornithidae': '莺鹛科', 'Passeridae': '雀科', 'Hirundinidae': '燕科',
    'Motacillidae': '鹡鸰科', 'Muscicapidae': '鹟科', 'Laniidae': '伯劳科',
    'Corvidae': '鸦科', 'Leiothrichidae': '噪鹛科', 'Dicruridae': '卷尾科',
    'Cisticolidae': '扇尾莺科', 'Sturnidae': '椋鸟科', 'Phylloscopidae': '柳莺科',
    'Fringillidae': '燕雀科', 'Zosteropidae': '绣眼鸟科', 'Turdidae': '鸫科',
}
```

### 5. 写入 Notion 时

字段建议：
- 「目」「科」：select（中文名作 option）
- 「学名」：rich_text
- 「Common name」/「英文名」：rich_text
- 「数据来源」：rich_text，统一填 `AviList v2025`

写入流程参考用户已有数据库 `naoba's life list`（data_source_id: <你的 life list data_source_id，见 config.json>）。

## Pitfalls

- ❌ 不要凭记忆给目/科——AviList 拆分/合并近年很多，记忆经常过时
- ❌ 不要对带「？」的鸟名直接定种——先和用户确认或备注"待确认"
- ❌ 不要在中文名直接对应的语义层面下结论——同一中文名可能对应多个种
- ❌ 不要忽略地理分布——*Zosterops japonicus* 在广州不可能见到
- ❌ AviList 没有官方中文，必须用学名作桥梁（中文名 → 候选学名 → AviList 验证）
- ❌ AviList 英文名用英式拼写（Grey 不是 Gray、Coloured 不是 Colored）
- ❌ Notion data source schema 改动后，已有"英文名"字段可能与"Common name"字段冲突，写入前先 GET schema 确认实际字段
- ❌ **Notion select option 名字/颜色一旦创建就改不了**：API v2025-09-03 PATCH `data_sources/{id}` 不允许重命名 select option，也不允许改 option 的 color（即便带上原 id 也不会生效，响应里返回原值，无报错）。但**新建 select 字段时可以自由设置选项名/颜色**（含 emoji、unicode 符号、`default` 色）。如果用户希望改 option 显示效果，标准重建流程：
  1. 字段重命名 旧字段名 → 旧字段名_old（**字段名是可以改的**，与 option 名不同）
  2. 用原字段名新建一个 select 字段，options 设置为目标外观
  3. 拉所有记录，把旧字段值复制到新字段
  4. PATCH data_source 删除旧字段（properties: { 旧字段名_old: null }）
- ⏱ **Notion API rate-limit ~3 req/s**：批量 PATCH 时务必加 `time.sleep(0.35)`+，否则会触发 429。Bash 工具默认 timeout 120s，58 条记录 ×0.35s ≈ 20s 应该够用，但实测过会被截到第 56 条。所以批量操作完成后总要做一次"补漏检查"（重新查询数据源，找出未完成的条目继续处理），不要假定第一遍就成功
- 🔌 **sandbox 出口对 api.notion.com 偶发 `ssl.SSLEOFError`**：3 次重试可能全失败，所有 Notion 调用应包装在 **6 次以上指数退避**重试中（`wait = 2 + i*2` 秒），否则脚本会在中途断在 SSL 错误上
- 🏷️ **写 select 值前先 GET 现有 options 精确匹配名字**：用 `{"select":{"name":"X"}}` 写入时，若 name 与现有 option **一字不差**才会复用；差一个空格/标点（如 `🟤 笼养` vs `🟤笼养`）Notion 会**静默新建一个重复 option**（且颜色随机）。所以写已知 option 前，务必先拉 schema 拿到准确 name 再用，不要凭记忆拼。误建后清理：把误填记录改回正确 option → 重发 options 列表（去掉误建项）删除之
- 🗑️ **2026-03-11 删除/归档 block 或 page 用 `in_trash: true`**：`archived: true` 会被 400 拒绝（"archived should be not present"）
- 📋 **GET data_source 返回的字段名是 `properties`**（不是旧文档的 `schema`）；其 parent 是 `{"type":"database_id","database_id":"..."}`（无 database_parent 键下的 database_id）
- 📌 **callout icon 格式**：`{"type":"emoji","emoji":"🦅"}`——只给 `name` 字段会报 validation error
- 🔍 **「缺实拍」的唯一可靠判据 = 首块是否为 image（2026-11-09 教训）**：**绝不能用「caption 含 📷」判定有实拍**——早期条目大量古画/邮票被误标 📷 前缀（山斑鸠=Fauna Japonica 图版、褐河乌=Gould 图版、火斑鸠/家麻雀=邮票），按 caption 扫会把 54 条漏成 19 条。正确口径：`first block != image` → 缺实拍（不管末尾有没有图）；首块是图但 caption 空 → 只缺署名（常是用户自己 iPhone 实拍，文件名 IMG_xxxx.heic / FullSizeRender.heic，补「📷 我的实拍」即可）。误标 📷 的古画 caption 顺手改成 🎨（改首字符即可，富文本 annotations 保留）
- 🧱 **Notion 首块插图只能 archive 重写**（append 只能加到末尾）；重写时：① 原 image 若 `type=="file"` 有 `file.url`（S3 签名链接，可直接下载原图再重传，**不会丢**）；`type=="file_upload"` 无 URL、绑定后不可二次引用——重写前先看 image type 判断；② **table 块 append 必须内嵌 `children`**（`{"type":"table","table":{"table_width":N,...,"children":[{"type":"table_row",...}]}}`），否则 400 `table.children should be defined`；③ GET block 的 rich_text 重写时要去掉只读字段 `plain_text`/`href`（保留 text.content/link/annotations）
- 🎵 **xeno-canto API v2 已下线（2026-10-25 实测）**：v3 需要 API key（xeno-canto.org/account 免费注册）。无 key 时的替代：WebFetch 抓 `https://xeno-canto.org/explore?query=学名`（空格用 %20，不要用 + ；curl 直连会被 Cloudflare 拦「Verifying visitor request...」）。**加速技巧（2026-11-09）**：query 直接加 `cnt:"China"` 只看中国录音（如 `Tringa nebularia cnt:"China"`），加 `cnt:"Taiwan"`/`cnt:"Hong Kong"` 补充；偶发被 Anubis 拦时换一次再试。**XC 物种名滞后**：XC 仍用旧属名/旧英文名（如 Lesser Sand Plover、Charadrius dealbatus），新拆分种用旧学名搜
- 🖼️ **Commons 限流绕过（2026-10-25 实测，2026-11-09 大幅更新）**：
  1. **api.php 被 403「Too Many Reqs (1862a4b)」封锁时（可能持续数小时）**：本机 curl 直连被拦，但 **WebFetch（服务端出口）调 api.php 完全可用**——一次可批量带 `titles=File:A.jpg|File:B.jpg|...`（≤50 个）拉 `prop=imageinfo&iiprop=url|extmetadata`，一次拿全 url/thumburl/Artist/License。MediaSearch 页（`Special:MediaSearch?type=image`）与 Category 页也可用 WebFetch 抓文件名（搜索词带 Gould 连写文件名无效时，改抓 Category:学名 页）
  2. **下载只走 upload.wikimedia.org 直链**（不受 api.php 封锁影响，但偶发 429 限速，重试+间隔 15s 即可）；**thumb 宽度必须用标准档 960/1280/1920px**（2025-26 起非标准宽度直接 400「Use thumbnail sizes listed」拒绝），thumb URL 结构 `upload.wikimedia.org/wikipedia/commons/thumb/{hh}/{xx}/{file}/1280px-{file}`
  3. api.php 正常时优先用它（thumburl 直接给出）
- 🖨️ **批量脚本 print 必须带 `flush=True`**：Bash 管道下 Python 是块缓冲，超时被杀时输出全丢；重试 sleep 累计容易撞 Bash 上限，长任务拆小步跑
- 🖼️ **博物画/古画检索套路（2026-11-09 实测，命中率远高于「学名+Gould」）**：
  1. **《Nederlandsche Vogelen》系列（Nozeman & Sepp，1770–1829，荷兰鸟全覆盖）命名规整可靠**：搜「Nederlandsche vogelen + 学名」即可命中 `Nederlandsche_vogelen_(KB)__-_学名_(XXXb).jpg`；荷兰有分布的欧洲鸟（琵鹭/鸬鹚/反嘴鹬/蚁䴕/环颈鸻…）基本都有
  2. **优先用历史学名搜图版**：旧属名/旧种名往往就是图版文字（Totanus glottis = 青脚鹬、Elanus melanopterus = 黑翅鸢、Yunx torquilla = 蚁䴕）；Naumann《Naturgeschichte der Vögel Deutschlands》Taf 图版、Fauna Japonica、Gould 各卷同理
  3. **Category:学名 (illustrations) 页面**直接列出全部图版（含子分类归属，防混入近缘种）
  4. **Gould 图版防坑**：Flickr/BHL 扫描件分类与 OCR 图注可能互相矛盾——双重确认；例：The Birds of Asia Plate 12 挂在 Elanus caeruleus (illustrations) 分类下，图注实为 ELANUS HYPOLEUCUS（澳洲黑肩鸢），不能用
  5. 19 世纪后命名/东亚特有/远东旅鸟（黑脸琵鹭图版未单独数字化、白脸鸻 2008 才独立、蒙古沙鸻）Commons 上常真无图版，按「有就加没有跳过」口径如实跳过

## Notion 文件上传（图片/PDF 等到内部存储）

**Notion API v2026-03-11 支持直接上传二进制文件到内部存储**（旧的"只能 external URL"知识已过期）。三步流程：

### Step 1: 创建 file_upload 对象（拿 id）
```bash
curl -X POST https://api.notion.com/v1/file_uploads \
  -H "Authorization: Bearer $TOKEN" \
  -H "Notion-Version: 2026-03-11" \
  -H "Content-Type: application/json" \
  -d '{"mode":"single_part","filename":"bird.jpg","content_type":"image/jpeg"}'
# 响应里有 "id": "<uuid>"
```
- mode: `single_part` (<20MB) / `multi_part` (>20MB) / `external_url`
- filename ≤ 900 字节
- 文件大小限制：单部分 < 20MB

### Step 2: 上传文件 bytes（multipart/form-data）
```bash
curl -X POST https://api.notion.com/v1/file_uploads/<file_upload_id>/send \
  -H "Authorization: Bearer $TOKEN" \
  -H "Notion-Version: 2026-03-11" \
  -F "file=@/local/path/to/bird.jpg"
# 上传成功后 status 变为 uploaded
```

### Step 3: 引用 file_upload_id 创建 image block
```json
{"type":"image","image":{
  "type":"file_upload",
  "file_upload":{"id":"<uuid-from-step1>"}
}}
```
**⚠️ 2026-03-11 版字段名**：引用字段是 `file_upload.id`（**不是**旧文档的 `file_upload_id`，用旧名会报 `file_upload.id should be defined`）。

**关键限制**：
- 此端点是 Notion API 中**唯一**用 multipart/form-data 的端点
- file_upload 对象有 expiry_time（默认 7 天），需在过期前用 step 3 引用绑定到某个 block，否则会被清理
- 一个 file_upload_id 一旦被附加到 block 上，就算"使用"了，永久保留
- 必须使用 Notion-Version: 2026-03-11 或更新版本

**与 external URL 对比**：
- 上传到 Notion：永久存储、占用 workspace 配额、稳定性最高
- external URL：原 URL 失效则图片消失、不占配额、批量处理快

## Verification

写入后必做的校核：
1. 抽查 5 条不同科的鸟，确认目/科/学名/英文名都写对
2. 总条目数与预期一致
3. 检查是否有重复（同中文名 + 同地点 + 同日期 = 重复，可去重）
4. 数据来源字段统一为 "AviList v2025"
