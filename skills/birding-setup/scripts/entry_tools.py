#!/usr/bin/env python3
"""entry_tools — 给物种条目写「正文」和「配图」的通用工具（只用标准库）。

和 setup_helper.py 配合：setup_helper 负责表格里的字段，本工具负责页面里的正文与图片。

  find-images <学名> [--n 6] [--out DIR] [--art] [--en "English name"] [--query "自由检索词"]
        在 Wikimedia Commons 找带许可证的图，下载预览图到本地（供你查看确认），并给出可直接用的署名 caption。
        默认找实拍；--art 找古画/博物画/版画（标题须含学名或英文名，否则丢弃）。
  gbif <学名>
        返回 GBIF 物种页链接（用于「分布与生态」的 bookmark）。
  write-body <page_id> <spec.json> [--replace] [--dry-run]
        按 spec 在页面里写正文：首图 → 提示框 → 各模块（标题/要点/书签/配图）。图片一律下载后上传为 Notion 托管文件，不用外链。
        页面已有正文时默认跳过（不覆盖用户内容）；--replace 先清空再写。
  empty-pages [--limit N]
        列出库里「还没有正文」的物种，用于补写。

spec.json 格式：
{
  "image":   {"path": "本地文件或 http 链接", "caption": "📷 作者 · Wikimedia Commons · CC BY 4.0", "source_url": "来源页(可选)"},
  "callout": {"emoji": "🐦", "text": "首次记录：2026-03-01 · 广州麓湖公园"},
  "sections": [
    {"title": "🧬 分类考据",
     "bullets": ["*Passer* —— 拉丁语 …", "..."],
     "subsections": [{"title": "系统位置", "bullets": ["..."]}]},
    {"title": "🌏 分布与生态", "bullets": ["..."], "bookmark": "https://www.gbif.org/species/123", "bookmark_caption": "GBIF · … · 全球出现记录"},
    {"title": "📜 文化与演化", "bullets": ["..."], "image": {"path": "...", "caption": "🎨 …"}}
  ]
}
文字里 *斜体*、**粗体** 会被渲染（学名用 *斜体*）。
"""
import html, json, mimetypes, os, re, sys, tempfile, time, urllib.parse, urllib.request, uuid

HERE = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, HERE)
import setup_helper as h  # noqa: E402

UA = {"User-Agent": "birding-notes-skill/1.0 (https://github.com/peanut8tter/birding-notes-skill)"}
IMG_EXT = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".gif": "image/gif", ".webp": "image/webp"}


def out(d): h.out(d)
def die(d): h.die(d)


# ------------------------------------------------------------ 网络（带重试，Wikimedia 会限流）
def http_get(url, binary=False, retries=4, timeout=40):
    err = None
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers=UA)
            data = urllib.request.urlopen(req, timeout=timeout).read()
            return data if binary else json.loads(data)
        except urllib.error.HTTPError as e:
            err = e
            time.sleep((3 + 3 * i) if e.code in (429, 503) else 1.5)
        except Exception as e:
            err = e; time.sleep(1.5 * (i + 1))
    raise RuntimeError(f"请求失败 {url[:90]}: {err}")


def strip_html(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", s or ""))).strip()


# ------------------------------------------------------------ find-images
BAD_PHOTO = ("egg", "nest", "skull", "skeleton", "map", "distribution", "range", "specimen", "museum", "sonogram",
             "spectrogram", "stamp", "coin", "drawing", "illustration", "plate", "painting", "feather", "chick", "taxidermy", "preserved")
ART_WORDS = ("plate", "painting", "watercolo", "lithograph", "illustration", "print", "gould", "naumann", "audubon", "drawing",
             "hand-coloured", "woodblock", "engraving", "etching", "ukiyo", "scroll", "gouache", "rijksmuseum", "rp-t-", "rp-p-",
             "nationalmuseum", "ink on", "hanging scroll", "tafel", "tab.")


def commons(query, limit=40, width=1600):
    u = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode({
        "action": "query", "format": "json", "generator": "search", "gsrsearch": query, "gsrnamespace": 6,
        "gsrlimit": limit, "prop": "imageinfo", "iiprop": "url|size|mime|extmetadata", "iiurlwidth": width})
    d = http_get(u)
    res = []
    for p in (d.get("query", {}).get("pages", {}) or {}).values():
        ii = (p.get("imageinfo") or [None])[0]
        if not ii or ii.get("mime") not in ("image/jpeg", "image/png"):
            continue
        m = ii.get("extmetadata", {})
        lic = strip_html(m.get("LicenseShortName", {}).get("value", ""))
        if not lic or "fair use" in lic.lower():
            continue
        author = strip_html(m.get("Artist", {}).get("value", "")) or "Unknown"
        res.append(dict(title=p["title"], w=ii["width"], h=ii["height"], license=lic, author=author[:80],
                        thumb=ii.get("thumburl") or ii["url"], original=ii["url"], source_url=ii["descriptionurl"],
                        desc=strip_html(m.get("ImageDescription", {}).get("value", ""))[:160],
                        cats=strip_html(m.get("Categories", {}).get("value", "")).lower()))
    return res


def score_photo(x, sci):
    t = x["title"].lower(); s = 0
    if sci.lower() in t: s += 3
    s += 2 if x["w"] >= 1600 else 1 if x["w"] >= 1000 else -2
    ratio = x["w"] / max(x["h"], 1)
    s += 1 if 1.1 <= ratio <= 1.9 else 0
    s -= 3 * sum(1 for w in BAD_PHOTO if w in t)
    if "birds &" in t or "flock" in t: s -= 1
    return s


def score_art(x, sci, en):
    hay = (x["title"] + " " + x["desc"]).lower()
    if not (sci.lower() in hay or (en and en.lower() in hay) or sci.lower() in x["cats"]):
        return None
    hay += " " + x["cats"]
    hits = sum(1 for w in ART_WORDS if w in hay)
    if hits == 0:      # 标题/描述里没有任何绘画类词汇 → 多半只是照片，丢弃
        return None
    return 3 + hits + (1 if x["w"] >= 1000 else 0)


def cmd_find_images(args):
    pos = [a for a in args if not a.startswith("--")]
    opt = lambda k, d=None: args[args.index(k) + 1] if k in args else d
    sci = (pos[0] if pos else opt("--query"))
    if not sci:
        die({"ok": False, "reason": "缺少学名"})
    n = int(opt("--n", 6)); en = opt("--en"); art = "--art" in args
    outdir = opt("--out") or tempfile.mkdtemp(prefix="birding_img_")
    os.makedirs(outdir, exist_ok=True)
    if opt("--query"):
        cands = commons(opt("--query") + " filetype:bitmap")
        ranked = [(score_art(x, sci, en) if art else score_photo(x, sci), x) for x in cands]
    elif art:
        qs = [f'"{sci}" {t} filetype:bitmap' for t in ("painting", "drawing", "print", "plate", "Rijksmuseum", "woodblock", "watercolour")]
        if en:
            qs += [f'"{en}" {t} filetype:bitmap' for t in ("painting", "plate")]
        seen, cands = set(), []
        for q in qs:
            for x in commons(q):
                if x["title"] not in seen and not x["title"].lower().endswith(".pdf"):
                    seen.add(x["title"]); cands.append(x)
        ranked = [(score_art(x, sci, en), x) for x in cands]
    else:
        cands = commons(f'incategory:"{sci}" filetype:bitmap')
        ranked = [(score_photo(x, sci), x) for x in cands]
    ranked = sorted([(s, x) for s, x in ranked if s is not None], key=lambda t: -t[0])[:n]
    items = []
    for i, (s, x) in enumerate(ranked, 1):
        ext = ".png" if x["thumb"].lower().endswith(".png") else ".jpg"
        path = os.path.join(outdir, f"{'art' if art else 'photo'}_{i}{ext}")
        try:
            open(path, "wb").write(http_get(x["thumb"], binary=True)); time.sleep(0.6)
        except Exception as e:
            path = None
        items.append(dict(rank=i, score=s, path=path, title=x["title"], size=f"{x['w']}x{x['h']}", license=x["license"],
                          author=x["author"], source_url=x["source_url"],
                          caption=f"{'🎨' if art else '📷'} {x['author']} · Wikimedia Commons · {x['license']}"))
    out({"ok": True, "kind": "art" if art else "photo", "dir": outdir, "count": len(items), "candidates": items,
         "next": ("先用看图能力逐张查看 path 对应的图片，确认：①确实是这个物种（不是别的种/幼鸟蛋巢/标本/地图）；②主体清晰、构图可作代表。"
                  "确认后把选中那张的 path / caption / source_url 填进 spec。若你无法查看图片，选 rank 最靠前且标题含学名的，并告知用户「未经目视核对」。"
                  if items else "没有找到合适的图：不要凑数，对应位置留空并在汇报里说明。")})


# ------------------------------------------------------------ gbif
def cmd_gbif(args):
    sci = " ".join(args)
    q = urllib.parse.quote(sci)
    d = http_get(f"https://api.gbif.org/v1/species/match?name={q}&kingdom=Animalia")
    key = d.get("speciesKey") if d.get("rank") == "SPECIES" else None
    if key:
        out({"ok": True, "url": f"https://www.gbif.org/species/{key}", "matched": d.get("canonicalName"),
             "match_type": d.get("matchType"), "caption": f"GBIF · {sci} · 全球出现记录"})
        return
    s = http_get(f"https://api.gbif.org/v1/species/search?q={q}&rank=SPECIES&limit=5")
    alts = [{"name": r.get("scientificName"), "url": f"https://www.gbif.org/species/{r.get('key')}"} for r in s.get("results", [])]
    out({"ok": False, "reason": "GBIF 未能在物种级精确匹配（常见于 AviList 新属名 GBIF 尚未采用）",
         "matched_rank": d.get("rank"), "alternatives": alts,
         "hint": "请用旧属名（异名）再查一次，并核对结果确为同一物种后再使用"})


# ------------------------------------------------------------ 条目版式 v2：模块 → 标准标题
MODULES = {   # key: (标题关键词, 标准 emoji, 标准标题)
    "behavior":     ("性格与行为", "🐾", "🐾 性格与行为"),
    "taxonomy":     ("分类考据",   "🧬", "🧬 分类考据"),
    "distribution": ("分布与生态", "🌏", "🌏 分布与生态"),
    "voice":        ("鸣声",       "🎵", "🎵 鸣声 / 鸣唱"),
    "culture":      ("文化与演化", "📜", "📜 文化与演化"),
    "id":           ("识别区分",   "🔍", "🔍 识别区分"),
}
DEFAULT_MODULES = ["behavior", "taxonomy", "distribution", "voice", "culture"]
_EMOJI_RE = re.compile(r"^[\u2190-\u2BFF\U0001F000-\U0001FAFF\u2600-\u27BF]")


def normalize_title(title):
    """已知模块的标题缺 emoji 就补上标准 emoji；返回 (新标题, 模块key或None)。"""
    for key, (kw, emo, std) in MODULES.items():
        if kw in title:
            return (title if _EMOJI_RE.match(title.strip()) else std), key
    return title, None


# ------------------------------------------------------------ 文本 → Notion rich_text
def rich(text):
    parts, pos = [], 0
    for m in re.finditer(r"\*\*(.+?)\*\*|\*(.+?)\*", text):
        if m.start() > pos:
            parts.append({"type": "text", "text": {"content": text[pos:m.start()]}})
        if m.group(1) is not None:
            parts.append({"type": "text", "text": {"content": m.group(1)}, "annotations": {"bold": True}})
        else:
            parts.append({"type": "text", "text": {"content": m.group(2)}, "annotations": {"italic": True}})
        pos = m.end()
    if pos < len(text):
        parts.append({"type": "text", "text": {"content": text[pos:]}})
    # Notion 单段 2000 字上限
    fixed = []
    for p in parts:
        c = p["text"]["content"]
        for i in range(0, max(len(c), 1), 1900):
            q = json.loads(json.dumps(p)); q["text"]["content"] = c[i:i + 1900]; fixed.append(q)
    return fixed or [{"type": "text", "text": {"content": ""}}]


def blk(t, **kw): return {"object": "block", "type": t, t: kw}


def upload_image(src):
    """本地路径或 http 链接 → Notion 托管 file_upload id。"""
    if re.match(r"^https?://", src):
        data = http_get(src, binary=True); name = os.path.basename(urllib.parse.urlparse(src).path) or "image.jpg"
    else:
        p = os.path.expanduser(src)
        if not os.path.exists(p):
            raise RuntimeError(f"图片不存在: {src}")
        data = open(p, "rb").read(); name = os.path.basename(p)
    ext = os.path.splitext(name)[1].lower()
    if ext not in IMG_EXT:
        ext = ".jpg"; name += ".jpg"
    ctype = IMG_EXT[ext]
    if len(data) > 4_800_000:
        raise RuntimeError(f"图片过大（{len(data)//1000}KB，免费版 Notion 单文件上限约 5MB），请换小一点的预览图")
    b = uuid.uuid4().hex
    body = (f"--{b}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"{name}\"\r\nContent-Type: {ctype}\r\n\r\n").encode() \
        + data + f"\r\n--{b}--\r\n".encode()
    last = None
    for i in range(3):          # 每次尝试都新建上传：同一个上传 ID 只能 send 一次，重试复用会被拒
        fu = h.notion("/file_uploads", {"mode": "single_part", "filename": name, "content_type": ctype})
        if "error" in fu:
            last = str(fu); time.sleep(2 + i * 2); continue
        try:
            c = h._Conn("api.notion.com", 443, timeout=90)
            c.request("POST", f"/v1/file_uploads/{fu['id']}/send", body, {
                "Authorization": "Bearer " + h.get_token(), "Notion-Version": h.NOTION_VERSION,
                "Content-Type": f"multipart/form-data; boundary={b}"})
            r = c.getresponse(); raw = r.read().decode(); c.close()
            d = json.loads(raw) if raw else {}
            if r.status < 300 and d.get("status") == "uploaded":
                return fu["id"]
            last = raw[:200]
        except Exception as e:
            last = str(e)
        time.sleep(2 + i * 2)
    raise RuntimeError("上传失败: " + str(last))


def image_block(img, warnings, label):
    try:
        fid = upload_image(img["path"])
    except Exception as e:
        warnings.append(f"{label} 配图失败：{e}"); return None
    cap = rich(img.get("caption", ""))
    if img.get("source_url"):
        cap += [{"type": "text", "text": {"content": " · "}},
                {"type": "text", "text": {"content": "来源页", "link": {"url": img["source_url"]}}}]
    return blk("image", type="file_upload", file_upload={"id": fid}, caption=cap)


def build_blocks(spec, warnings):
    B = []
    if spec.get("image"):
        b = image_block(spec["image"], warnings, "首图")
        if b: B.append(b)
    c = spec.get("callout")
    if c:
        B.append(blk("callout", rich_text=rich(c["text"]), icon={"type": "emoji", "emoji": c.get("emoji", "🐦")}, color="gray_background"))

    seen = set()

    def section(sec, level):
        ht = f"heading_{level}"
        title = sec["title"]
        if level == 2:
            title, key = normalize_title(title)
            if key: seen.add(key)
        B.append(blk(ht, rich_text=rich(title)))
        for t in sec.get("paragraphs", []):
            B.append(blk("paragraph", rich_text=rich(t)))
        for t in sec.get("bullets", []):
            B.append(blk("bulleted_list_item", rich_text=rich(t)))
        if sec.get("bookmark"):
            B.append(blk("bookmark", url=sec["bookmark"]))
            if sec.get("bookmark_caption"):
                B.append(blk("paragraph", rich_text=rich(sec["bookmark_caption"])))
        if sec.get("image"):
            b = image_block(sec["image"], warnings, sec["title"])
            if b: B.append(b)
        for sub in sec.get("subsections", []):
            section(sub, 3)
    for sec in spec.get("sections", []):
        section(sec, 2)
    # 对照用户偏好做版式核对
    prefs = (h.load_cfg().get("user_preferences") or {})
    want = prefs.get("entry_modules") or DEFAULT_MODULES
    missing = [MODULES[k][0] for k in want if k in MODULES and k not in seen]
    if missing:
        warnings.append("缺少用户启用的模块：" + "、".join(missing) + "（确实无可靠信息时请写「（暂无）」，不要整块省略）")
    if prefs.get("entry_images", "both") in ("photo", "both") and not (B and B[0]["type"] == "image"):
        warnings.append("没有首图：正文第一个 block 应为该物种的实拍图（用于认鸟与卡片缩略图）")
    return B


def append_children(page_id, blocks):
    for i in range(0, len(blocks), 90):
        r = h.notion(f"/blocks/{page_id}/children", {"children": blocks[i:i + 90]}, method="PATCH")
        if "error" in r:
            raise RuntimeError("写入正文失败: " + str(r))
        time.sleep(0.35)


def page_children(page_id):
    res, cur = [], None
    while True:
        r = h.notion(f"/blocks/{page_id}/children?page_size=100" + (f"&start_cursor={cur}" if cur else ""))
        if "error" in r: die({"ok": False, "while": "读取页面内容", "detail": r})
        res += r.get("results", [])
        if not r.get("has_more"): return res
        cur = r.get("next_cursor")


def cmd_write_body(args):
    pos = [a for a in args if not a.startswith("--")]
    if len(pos) < 2: die({"ok": False, "reason": "用法: write-body <page_id> <spec.json> [--replace] [--dry-run]"})
    page_id, spec = pos[0], json.load(open(pos[1]))
    kids = page_children(page_id)
    if kids and "--replace" not in args:
        out({"ok": True, "skipped": "页面已有内容，未改动（确需覆盖请加 --replace）", "existing_blocks": len(kids)}); return
    warnings = []
    if "--dry-run" in args:
        out({"ok": True, "dry_run": True, "sections": [s["title"] for s in spec.get("sections", [])],
             "has_first_image": bool(spec.get("image")), "has_callout": bool(spec.get("callout"))}); return
    blocks = build_blocks(spec, warnings)
    if kids and "--replace" in args:
        for k in kids:
            h.notion(f"/blocks/{k['id']}", method="DELETE"); time.sleep(0.3)
    append_children(page_id, blocks)
    out({"ok": True, "blocks_written": len(blocks),
         "first_block_is_image": bool(blocks and blocks[0]["type"] == "image"),
         "sections": [normalize_title(s["title"])[0] for s in spec.get("sections", [])], "warnings": warnings})


def cmd_empty_pages(args):
    ds, fields = h.current_ds()
    limit = int(args[args.index("--limit") + 1]) if "--limit" in args else None
    empty, total = [], 0
    for r in h._all_rows(ds["id"], limit):
        total += 1
        k = h.notion(f"/blocks/{r['id']}/children?page_size=1")
        if "error" not in k and not k.get("results"):
            empty.append({"id": r["id"], "name": h._cell(r, fields.get("name")), "sci": h._cell(r, fields.get("sci")) if fields.get("sci") else ""})
        time.sleep(0.3)
    out({"ok": True, "checked": total, "empty_count": len(empty), "empty": empty})


if __name__ == "__main__":
    a = sys.argv[1:]
    try:
        {"find-images": lambda: cmd_find_images(a[1:]), "gbif": lambda: cmd_gbif(a[1:]),
         "write-body": lambda: cmd_write_body(a[1:]), "empty-pages": lambda: cmd_empty_pages(a[1:])}[a[0]]()
    except (IndexError, KeyError):
        print(__doc__); sys.exit(2)
