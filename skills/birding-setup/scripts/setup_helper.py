#!/usr/bin/env python3
"""birding-setup 辅助脚本：配置状态、Notion 连接、建库/适配已有库、批量写入。
只用标准库。所有输出为 JSON，便于 AI 解析。

  status                              配置进度 + 下一步
  set-notion-token <token>            先向 Notion 校验，通过才保存
  find <关键词> [--pages|--databases]  搜索已共享给 integration 的页面 / 数据库
  inspect <id>                        读取一个已有数据库：有哪些列、行数、与标准字段的对应建议
  create-db <父页面id> [--title T]     在父页面下新建「标准结构」的 life list 数据库，并自动保存配置
  add-fields <key...>                 给当前数据库补充缺少的标准字段（不改动已有列）
  map <key>=<列名> ...                 把标准字段对应到已有数据库的某一列
  list-rows [--limit N]               列出库里已有的物种（继续记录前先看看）
  add-rows <json文件|-> [--dry-run] [--no-enrich]
                                      批量写入。JSON 为数组，每项用标准字段 key，如
                                      {"name":"树麻雀","sci":"Passer montanus","first_date":"2026-03-01"}
                                      默认按 sci 用 AviList 补全 en/order/family/source，并按名称/学名去重
  set <key> <value>                   写 config，key 用点号，如 user_preferences.primary_location
  set-xc-key <key>                    保存 xeno-canto API key（可选）

标准字段 key：name sci en order family first_place first_date residency iucn protection source
"""
import json, os, sys, time, socket, ssl, http.client

HOME = os.path.expanduser("~")
BASE = os.environ.get("BIRDING_NOTES_HOME") or os.path.join(HOME, ".config", "birding-notes")
CFG = os.path.join(BASE, "config.json")
SECRETS = os.path.join(BASE, "secrets")
NOTION_TOKEN_FILE = os.path.join(SECRETS, "notion.json")
XC_KEY_FILE = os.path.join(SECRETS, "xenocanto.json")
LEGACY_CFG = os.path.join(HOME, ".workbuddy", "birding-notes", "config.json")
LEGACY_NOTION = os.path.join(HOME, ".workbuddy", "secrets", "notion.json")
LEGACY_XC = os.path.join(HOME, ".workbuddy", "secrets", "xenocanto.json")
HERE = os.path.dirname(os.path.realpath(__file__))
AVILIST = os.path.normpath(os.path.join(HERE, "..", "..", "..", "assets", "avilist_species.json"))
NOTION_VERSION = "2026-03-11"

# ---------------------------------------------------------------- 标准字段定义
FIELDS = [
    # key / 说明 / 默认列名 / 类型 / 是否核心 / 同义列名（用于识别别人已有的库）/ 初始选项
    dict(key="name", label="名称（物种名）", col="中文名", type="title", core=True,
         syn=["名称", "name", "物种", "鸟名", "种名", "species", "title", "鸟种", "bird", "中文名", "名字"]),
    dict(key="sci", label="学名", col="学名", type="rich_text", core=True,
         syn=["scientific name", "scientific", "latin", "拉丁名", "拉丁学名", "latin name", "binomial"]),
    dict(key="en", label="英文名", col="Common name", type="rich_text",
         syn=["english name", "english", "英文名", "英文", "common name", "英文名称"]),
    dict(key="order", label="目", col="目", type="select", syn=["order"]),
    dict(key="family", label="科", col="科", type="select", syn=["family"]),
    dict(key="first_place", label="首次观察地点", col="首次地点", type="rich_text",
         syn=["地点", "location", "place", "观察地点", "where", "首次观察地点", "site", "locality", "观鸟地点"]),
    dict(key="first_date", label="首次观察日期", col="首次日期", type="date",
         syn=["日期", "date", "首次记录", "观察日期", "first seen", "首次观察", "时间", "见到日期", "observation date"]),
    dict(key="residency", label="居留型（留鸟/候鸟…，按你的观察地判定）", col="居留型", type="select",
         syn=["residency", "居留", "status", "居留类型", "迁徙类型"],
         opts=["留鸟", "夏候鸟", "冬候鸟", "旅鸟", "迷鸟", "不确定"]),
    dict(key="iucn", label="IUCN 受胁等级", col="IUCN 等级", type="select",
         syn=["iucn", "保护状态", "受胁等级", "红色名录", "conservation status"],
         opts=["LC", "NT", "VU", "EN", "CR", "DD"]),
    dict(key="protection", label="本国保护等级（中国：国家一/二级、三有）", col="中国保护等级", type="select",
         syn=["保护等级", "protection", "国家保护", "protected"],
         opts=["国家一级", "国家二级", "三有", "未列入"]),
    dict(key="source", label="分类数据来源", col="数据来源", type="select",
         syn=["source", "来源", "分类标准"], opts=["AviList v2025"]),
]
BY_KEY = {f["key"]: f for f in FIELDS}
CORE_KEYS = [f["key"] for f in FIELDS if f.get("core")]


def out(d):
    print(json.dumps(d, ensure_ascii=False, indent=2))


def die(d, code=1):
    out(d); sys.exit(code)


# ---------------------------------------------------------------- 配置读写
def load_cfg():
    for p in ((CFG,) if os.environ.get("BIRDING_NOTES_HOME") else (CFG, LEGACY_CFG)):
        try:
            return json.load(open(p))
        except Exception:
            continue
    return {}


def save_json_private(path, data):
    os.makedirs(os.path.dirname(path), mode=0o700, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.chmod(path, 0o600)


def cfg_set(key, val):
    cfg = load_cfg(); cur = cfg
    parts = key.split(".")
    for p in parts[:-1]:
        cur = cur.setdefault(p, {})
    cur[parts[-1]] = val
    save_json_private(CFG, cfg)
    return cfg


def get_token():
    t = os.environ.get("NOTION_TOKEN")
    if t:
        return t
    for p in ((NOTION_TOKEN_FILE,) if os.environ.get("BIRDING_NOTES_HOME") else (NOTION_TOKEN_FILE, LEGACY_NOTION)):
        try:
            return json.load(open(p))["integration_token"]
        except Exception:
            continue
    return None


# ---------------------------------------------------------------- Notion 请求（带重试 + 多 IP）
class _Conn(http.client.HTTPSConnection):
    """逐个尝试 api.notion.com 解析出的 IP（保留 SNI）。部分网络下首个 IP 不通会直接断开。"""
    def connect(self):
        ips = []
        try:
            ips = sorted({a[4][0] for a in socket.getaddrinfo(self.host, self.port, socket.AF_INET)})
        except Exception:
            pass
        last = None
        for ip in (ips or [self.host]):
            try:
                sock = socket.create_connection((ip, self.port), timeout=8)
                self.sock = ssl.create_default_context().wrap_socket(sock, server_hostname=self.host)
                return
            except Exception as e:
                last = e
        raise last or OSError("connect failed")


def notion(path, body=None, method=None, token=None, retries=3):
    method = method or ("POST" if body is not None else "GET")
    payload = json.dumps(body).encode() if body is not None else None
    headers = {"Authorization": "Bearer " + (token or get_token() or ""),
               "Notion-Version": NOTION_VERSION, "Content-Type": "application/json"}
    err = None
    for i in range(retries):
        try:
            c = _Conn("api.notion.com", 443, timeout=25)
            c.request(method, "/v1" + path, payload, headers)
            r = c.getresponse(); raw = r.read().decode(); c.close()
            if r.status == 429:
                time.sleep(float(r.getheader("Retry-After") or 2)); continue
            d = json.loads(raw) if raw else {}
            if r.status >= 400:
                return {"error": r.status, "message": d.get("message", raw[:200]), "code": d.get("code")}
            return d
        except Exception as e:
            err = e; time.sleep(1.2 * (i + 1))
    return {"error": "network", "message": str(err)}


def need_ok(r, what):
    if "error" in r:
        die({"ok": False, "while": what, "detail": r})
    return r


def plain(rich):
    return "".join(t.get("plain_text", "") for t in (rich or []))


def title_of(r):
    if r.get("object") in ("database", "data_source"):
        return plain(r.get("title"))
    for p in r.get("properties", {}).values():
        if p.get("type") == "title":
            return plain(p["title"])
    return ""


def resolve_ds(any_id):
    """接受 data_source id 或 database id，返回 data_source 对象。"""
    r = notion(f"/data_sources/{any_id}")
    if "error" not in r:
        return r
    db = notion(f"/databases/{any_id}")
    need_ok(db, "读取数据库")
    srcs = db.get("data_sources") or []
    if not srcs:
        die({"ok": False, "reason": "该数据库下没有数据源", "detail": db})
    return need_ok(notion(f"/data_sources/{srcs[0]['id']}"), "读取数据源")


def current_ds():
    cfg = load_cfg(); n = cfg.get("notion", {})
    i = n.get("life_list_data_source_id") or n.get("life_list_database_id")
    if not i:
        die({"ok": False, "reason": "还没有配置数据库。先走 birding-setup 向导（create-db，或 inspect + set + map）"})
    return resolve_ds(i), n.get("fields", {})


def props_summary(props):
    res = []
    for name, v in props.items():
        t = v["type"]
        item = {"name": name, "type": t}
        if t in ("select", "multi_select"):
            item["options"] = [o["name"] for o in v[t].get("options", [])][:30]
        res.append(item)
    return res


def suggest_mapping(props):
    """按列名/类型猜测 标准字段 → 已有列。返回 (mapping, missing, unmatched_cols)。"""
    used, mapping = set(), {}
    norm = lambda s: s.strip().lower()
    for f in FIELDS:
        cands = [norm(f["col"])] + [norm(s) for s in f["syn"]]
        hit = None
        for name, v in props.items():
            if name in used:
                continue
            if f["type"] == "title" and v["type"] != "title":
                continue
            if norm(name) in cands:
                hit = name; break
        if not hit and f["type"] == "title":
            hit = next((n for n, v in props.items() if v["type"] == "title"), None)  # title 列只有一个
        if hit:
            mapping[f["key"]] = hit; used.add(hit)
    missing = [f["key"] for f in FIELDS if f["key"] not in mapping]
    unmatched = [n for n in props if n not in used]
    return mapping, missing, unmatched


# ---------------------------------------------------------------- 命令
def cmd_status():
    cfg = load_cfg(); n = cfg.get("notion", {})
    has_token = bool(get_token())
    has_db = bool(n.get("life_list_data_source_id") or n.get("life_list_database_id"))
    fields = n.get("fields", {})
    steps = {
        "notion_token": has_token,
        "database_configured": has_db,
        "fields_mapped": all(k in fields for k in CORE_KEYS) if has_db else False,
        "user_preferences (可选)": bool(cfg.get("user_preferences")),
        "xenocanto_key (可选)": os.path.exists(XC_KEY_FILE) or os.path.exists(LEGACY_XC),
    }
    nxt = None
    if not has_token: nxt = "notion_token"
    elif not has_db: nxt = "database（新建 create-db，或接入已有 inspect+map）"
    elif not steps["fields_mapped"]: nxt = "map（缺少字段映射：对已有库跑 inspect 后 map）"
    out({"ready": nxt is None, "steps": steps, "next": nxt, "config_path": CFG,
         "mapping": fields or None, "preferences": cfg.get("user_preferences")})


def cmd_set_token(tok):
    r = notion("/users/me", token=tok, retries=2)
    if "error" in r:
        die({"ok": False, "reason": "token 校验失败（Notion 拒绝或网络不通）", "detail": r})
    save_json_private(NOTION_TOKEN_FILE, {"integration_token": tok})
    out({"ok": True, "integration": r.get("name"), "saved_to": NOTION_TOKEN_FILE})


def cmd_find(args):
    kind = ("page" if "--pages" in args else "data_source" if "--databases" in args else None)
    q = " ".join(a for a in args if not a.startswith("--"))
    body = {"query": q, "page_size": 20}
    if kind:
        body["filter"] = {"property": "object", "value": kind}
    r = need_ok(notion("/search", body), "搜索")
    res = []
    for x in r.get("results", []):
        item = {"id": x["id"], "type": x["object"], "title": title_of(x), "url": x.get("url")}
        if x["object"] == "data_source":
            item["data_source_id"] = x["id"]
            item["database_id"] = (x.get("parent") or {}).get("database_id")
        res.append(item)
    out({"ok": True, "count": len(res), "results": res,
         "hint": "没找到？多半是页面/数据库还没共享给 integration：在 Notion 打开它 → 右上角 ··· → 连接(Connections) → 选择你的 integration"})


def cmd_inspect(i):
    ds = resolve_ds(i)
    props = ds.get("properties", {})
    mapping, missing, unmatched = suggest_mapping(props)
    q = notion(f"/data_sources/{ds['id']}/query", {"page_size": 100})
    rows = len(q.get("results", [])) if "error" not in q else None
    out({"ok": True, "title": title_of(ds), "data_source_id": ds["id"],
         "database_id": (ds.get("parent") or {}).get("database_id"),
         "rows_sampled(最多100)": rows, "columns": props_summary(props),
         "suggested_mapping": {k: {"column": v, "label": BY_KEY[k]["label"]} for k, v in mapping.items()},
         "missing_standard_fields": [{"key": k, "label": BY_KEY[k]["label"], "default_col": BY_KEY[k]["col"],
                                      "core": bool(BY_KEY[k].get("core"))} for k in missing],
         "other_columns(不动)": unmatched,
         "next": "把 suggested_mapping 用大白话给用户确认；确认后：set notion.life_list_data_source_id / database_id，再 map 保存映射；缺的字段问用户是否 add-fields"})


def _prop_schema(f):
    t = f["type"]
    if t == "title": return {"title": {}}
    if t == "select": return {"select": {"options": [{"name": o} for o in f.get("opts", [])]}}
    if t == "date": return {"date": {}}
    return {"rich_text": {}}


def cmd_create_db(args):
    if not args or args[0].startswith("--"):
        die({"ok": False, "reason": "缺少父页面 id（先 find --pages 找到用户新建的空页面）"})
    parent = args[0]
    title = "观鸟笔记 · Life List"
    if "--title" in args:
        title = args[args.index("--title") + 1]
    props = {f["col"]: _prop_schema(f) for f in FIELDS}
    body = {"parent": {"type": "page_id", "page_id": parent},
            "title": [{"type": "text", "text": {"content": title}}],
            "initial_data_source": {"properties": props}}
    r = need_ok(notion("/databases", body), "新建数据库")
    ds_id = (r.get("data_sources") or [{}])[0].get("id")
    if not ds_id:
        die({"ok": False, "reason": "已创建但没拿到数据源 id", "detail": r})
    cfg_set("notion.life_list_database_id", r["id"])
    cfg_set("notion.life_list_data_source_id", ds_id)
    cfg_set("notion.fields", {f["key"]: f["col"] for f in FIELDS})
    cfg_set("notion.bird_root_page_id", parent)
    out({"ok": True, "database_id": r["id"], "data_source_id": ds_id, "url": r.get("url"),
         "columns": [f["col"] for f in FIELDS], "saved": "已写入配置（含字段映射）"})


def cmd_add_fields(keys):
    ds, fields = current_ds()
    props = ds.get("properties", {})
    add, newmap = {}, dict(fields)
    for k in keys:
        f = BY_KEY.get(k)
        if not f:
            die({"ok": False, "reason": f"未知字段 key: {k}", "valid": list(BY_KEY)})
        if f["type"] == "title":
            continue
        col = f["col"]
        if col in props:
            newmap[k] = col; continue
        add[col] = _prop_schema(f); newmap[k] = col
    if add:
        need_ok(notion(f"/data_sources/{ds['id']}", {"properties": add}, method="PATCH"), "新增列")
    cfg_set("notion.fields", newmap)
    out({"ok": True, "added": list(add), "mapping": newmap})


def cmd_map(pairs):
    ds, fields = current_ds()
    props = ds.get("properties", {}); fields = dict(fields)
    for p in pairs:
        k, _, col = p.partition("=")
        if k not in BY_KEY:
            die({"ok": False, "reason": f"未知字段 key: {k}", "valid": list(BY_KEY)})
        if col not in props:
            die({"ok": False, "reason": f"数据库里没有名为「{col}」的列", "columns": list(props)})
        fields[k] = col
    cfg_set("notion.fields", fields)
    missing_core = [k for k in CORE_KEYS if k not in fields]
    out({"ok": True, "mapping": fields, "missing_core": missing_core})


def _all_rows(ds_id, limit=None):
    rows, cur = [], None
    while True:
        body = {"page_size": 100}
        if cur: body["start_cursor"] = cur
        r = need_ok(notion(f"/data_sources/{ds_id}/query", body), "读取已有记录")
        rows += r.get("results", [])
        if not r.get("has_more") or (limit and len(rows) >= limit): break
        cur = r.get("next_cursor")
    return rows[:limit] if limit else rows


def _cell(page, col):
    p = page.get("properties", {}).get(col)
    if not p: return ""
    t = p["type"]
    if t in ("title", "rich_text"): return plain(p[t])
    if t == "select": return (p["select"] or {}).get("name", "")
    if t == "date": return (p["date"] or {}).get("start", "")
    return ""


def cmd_list_rows(args):
    ds, fields = current_ds()
    limit = int(args[args.index("--limit") + 1]) if "--limit" in args else None
    rows = _all_rows(ds["id"], limit)
    nc, sc = fields.get("name"), fields.get("sci")
    out({"ok": True, "count": len(rows),
         "species": [{"name": _cell(r, nc), "sci": _cell(r, sc) if sc else ""} for r in rows]})


def _build_prop(ptype, val):
    v = str(val).strip()
    if not v: return None
    if ptype == "title": return {"title": [{"text": {"content": v[:1900]}}]}
    if ptype == "rich_text": return {"rich_text": [{"text": {"content": v[:1900]}}]}
    if ptype == "select": return {"select": {"name": v.replace(",", "，")[:100]}}
    if ptype == "multi_select": return {"multi_select": [{"name": x.strip().replace(",", "，")} for x in v.split("、") if x.strip()]}
    if ptype == "date":
        s = v.replace("/", "-").replace(".", "-")
        parts = s.split("-")
        try:
            y, m, d = (int(parts[0]), int(parts[1]), int(parts[2])) if len(parts) >= 3 else (int(parts[0]), int(parts[1]), 1)
            return {"date": {"start": f"{y:04d}-{m:02d}-{d:02d}"}}
        except Exception:
            return "BADDATE"
    if ptype == "url": return {"url": v}
    if ptype == "number":
        try: return {"number": float(v)}
        except Exception: return None
    return None


def cmd_add_rows(args):
    dry = "--dry-run" in args
    enrich = "--no-enrich" not in args
    src = next((a for a in args if not a.startswith("--") or a == "-"), None)
    if not src:
        die({"ok": False, "reason": "缺少 JSON 文件路径（或用 - 读标准输入）"})
    rows_in = json.load(sys.stdin if src == "-" else open(src))
    ds, fields = current_ds()
    props = ds.get("properties", {})
    if "name" not in fields:
        die({"ok": False, "reason": "未配置 name 字段映射，先 map name=<标题列名>"})

    av = {}
    if enrich and os.path.exists(AVILIST):
        av = {s["sci"].lower(): s for s in json.load(open(AVILIST))}

    existing = _all_rows(ds["id"])
    have_name = {_cell(r, fields["name"]).strip().lower() for r in existing}
    have_sci = {_cell(r, fields["sci"]).strip().lower() for r in existing} if "sci" in fields else set()

    report = {"created": [], "skipped_duplicate": [], "failed": [], "notes": []}
    for row in rows_in:
        row = dict(row)
        sci = str(row.get("sci", "")).strip()
        if enrich and sci:
            hit = av.get(sci.lower())
            if hit:
                row.setdefault("en", hit["en"]); row.setdefault("order", hit["order"])
                row.setdefault("family", hit["family"]); row.setdefault("source", "AviList v2025")
            else:
                report["notes"].append(f"{row.get('name') or sci}: 学名「{sci}」不在 AviList v2025 中，未自动补全目/科（请核对拼写或是否为异名）")
        nm = str(row.get("name", "")).strip()
        if not nm:
            report["failed"].append({"row": row, "why": "缺少 name"}); continue
        if nm.lower() in have_name or (sci and sci.lower() in have_sci):
            report["skipped_duplicate"].append(nm); continue
        page_props, dropped = {}, []
        for k, v in row.items():
            col = fields.get(k)
            if not col or col not in props:
                if k in BY_KEY and str(v).strip(): dropped.append(k)
                continue
            built = _build_prop(props[col]["type"], v)
            if built == "BADDATE":
                report["notes"].append(f"{nm}: 日期「{v}」无法识别，已留空"); continue
            if built: page_props[col] = built
        if dropped:
            report["notes"].append(f"{nm}: 数据库里没有对应列，未写入 {dropped}")
        if dry:
            report["created"].append(nm + "（预演）"); have_name.add(nm.lower())
            if sci: have_sci.add(sci.lower())
            continue
        r = notion("/pages", {"parent": {"type": "data_source_id", "data_source_id": ds["id"]}, "properties": page_props})
        if "error" in r:
            report["failed"].append({"name": nm, "why": r.get("message")})
        else:
            report["created"].append(nm); have_name.add(nm.lower())
            if sci: have_sci.add(sci.lower())
        time.sleep(0.35)
    report["summary"] = {k: len(report[k]) for k in ("created", "skipped_duplicate", "failed")}
    report["dry_run"] = dry
    out(report)


def cmd_set_xc(key):
    save_json_private(XC_KEY_FILE, {"api_key": key})
    out({"ok": True, "saved_to": XC_KEY_FILE})


if __name__ == "__main__":
    a = sys.argv[1:]
    try:
        c = a[0]
        {"status": lambda: cmd_status(),
         "set-notion-token": lambda: cmd_set_token(a[1]),
         "find": lambda: cmd_find(a[1:]),
         "inspect": lambda: cmd_inspect(a[1]),
         "create-db": lambda: cmd_create_db(a[1:]),
         "add-fields": lambda: cmd_add_fields(a[1:]),
         "map": lambda: cmd_map(a[1:]),
         "list-rows": lambda: cmd_list_rows(a[1:]),
         "add-rows": lambda: cmd_add_rows(a[1:]),
         "set": lambda: (cfg_set(a[1], a[2]), out({"ok": True, "key": a[1], "config_path": CFG})),
         "set-xc-key": lambda: cmd_set_xc(a[1])}[c]()
    except (IndexError, KeyError):
        print(__doc__); sys.exit(2)
