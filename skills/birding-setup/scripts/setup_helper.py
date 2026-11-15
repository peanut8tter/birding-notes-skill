#!/usr/bin/env python3
"""birding-setup 辅助脚本：检查配置状态、校验并保存 token、搜索 Notion 数据库。
只用标准库。所有输出为 JSON，便于 AI 解析。

用法:
  setup_helper.py status
  setup_helper.py set-notion-token <token>     # 先向 Notion 校验，通过才保存
  setup_helper.py find <关键词>                 # 搜索已共享给 integration 的页面/数据库
  setup_helper.py set <key> <value>            # 写入 config.json，key 用点号，如 notion.life_list_database_id
  setup_helper.py set-xc-key <key>             # 保存 xeno-canto API key
"""
import json, os, sys, urllib.request, urllib.error

HOME = os.path.expanduser("~")
CFG_DIR = os.path.join(HOME, ".workbuddy", "birding-notes")
CFG = os.path.join(CFG_DIR, "config.json")
SECRETS = os.path.join(HOME, ".workbuddy", "secrets")
NOTION_TOKEN_FILE = os.path.join(SECRETS, "notion.json")
XC_KEY_FILE = os.path.join(SECRETS, "xenocanto.json")
NOTION_VERSION = "2026-03-11"


def out(d):
    print(json.dumps(d, ensure_ascii=False, indent=2))


def load_cfg():
    try:
        return json.load(open(CFG))
    except Exception:
        return {}


def save_json_private(path, data):
    os.makedirs(os.path.dirname(path), mode=0o700, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.chmod(path, 0o600)


def get_token():
    t = os.environ.get("NOTION_TOKEN")
    if t:
        return t
    try:
        return json.load(open(NOTION_TOKEN_FILE))["integration_token"]
    except Exception:
        return None


def notion(path, body=None, token=None):
    req = urllib.request.Request(
        "https://api.notion.com/v1" + path,
        data=json.dumps(body).encode() if body is not None else None,
        method="POST" if body is not None else "GET",
        headers={"Authorization": "Bearer " + (token or get_token() or ""),
                 "Notion-Version": NOTION_VERSION, "Content-Type": "application/json"})
    try:
        return json.load(urllib.request.urlopen(req, timeout=20))
    except urllib.error.HTTPError as e:
        return {"error": e.code, "message": e.read().decode()[:200]}
    except Exception as e:
        return {"error": "network", "message": str(e)}


def title_of(r):
    if r.get("object") == "database" or r.get("object") == "data_source":
        return "".join(t.get("plain_text", "") for t in r.get("title", []))
    for p in r.get("properties", {}).values():
        if p.get("type") == "title":
            return "".join(t.get("plain_text", "") for t in p["title"])
    return ""


def cmd_status():
    cfg = load_cfg()
    n = cfg.get("notion", {})
    steps = {
        "notion_token": bool(get_token()),
        "life_list_database_id": bool(n.get("life_list_database_id")),
        "xenocanto_key (可选)": os.path.exists(XC_KEY_FILE),
        "user_preferences (可选)": bool(cfg.get("user_preferences")),
    }
    required_ok = steps["notion_token"] and steps["life_list_database_id"]
    out({"ready": required_ok, "steps": steps, "config_path": CFG,
         "next": None if required_ok else
         ("notion_token" if not steps["notion_token"] else "life_list_database_id")})


def cmd_set_token(tok):
    r = notion("/users/me", token=tok)
    if "error" in r:
        out({"ok": False, "reason": "token 校验失败（需以 ntn_ 或 secret_ 开头的 Internal Integration token）", "detail": r})
        sys.exit(1)
    save_json_private(NOTION_TOKEN_FILE, {"integration_token": tok})
    out({"ok": True, "integration": r.get("name"), "saved_to": NOTION_TOKEN_FILE})


def cmd_find(q):
    r = notion("/search", {"query": q, "page_size": 10})
    if "error" in r:
        out({"ok": False, "detail": r}); sys.exit(1)
    out({"ok": True, "results": [
        {"id": x["id"], "type": x["object"], "title": title_of(x)} for x in r.get("results", [])],
        "hint": "结果为空说明该页面/数据库还没共享给 integration（页面右上角 … → Connections → 添加）"})


def cmd_set(key, val):
    cfg = load_cfg()
    cur = cfg
    parts = key.split(".")
    for p in parts[:-1]:
        cur = cur.setdefault(p, {})
    cur[parts[-1]] = val
    save_json_private(CFG, cfg)
    out({"ok": True, "key": key, "config_path": CFG})


def cmd_set_xc(key):
    save_json_private(XC_KEY_FILE, {"api_key": key})
    out({"ok": True, "saved_to": XC_KEY_FILE})


if __name__ == "__main__":
    a = sys.argv[1:]
    try:
        {"status": lambda: cmd_status(),
         "set-notion-token": lambda: cmd_set_token(a[1]),
         "find": lambda: cmd_find(a[1]),
         "set": lambda: cmd_set(a[1], a[2]),
         "set-xc-key": lambda: cmd_set_xc(a[1])}[a[0]]()
    except (IndexError, KeyError):
        print(__doc__); sys.exit(2)
