#!/usr/bin/env python3
"""批量迁移 LifeList 中所有 external 图片 block → Notion 托管文件。
自动扫描（分页查询 data_source → 逐页找 external image block），逐条：
下载(Wikimedia 直连/其他走代理) → file_uploads 上传 → PATCH block 保留 caption。
幂等：已迁移(file 类型)自然跳过；单条失败不影响其余，最后汇总。
"""
import json, subprocess, sys, time, os, mimetypes

import os
TOKEN = os.environ["NOTION_TOKEN"]  # export NOTION_TOKEN=ntn_xxx
VER = "2026-03-11"
DS = "37871355-4c9a-8073-b4a3-000b9cc2ea18"  # LifeList data_source（2026-10-24 实测有效）
CACHE = "/tmp/lifelist_migration"
os.makedirs(CACHE, exist_ok=True)
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "batch_upload_result_2026-10-25.json")

UA = "Mozilla/5.0 (nature-knowledge skill)"


def notion(path, payload=None, method="GET", raw_file=None):
    """curl 调 Notion API，带重试。2026-10-25 实测：直连+钉 IP（自动在
    208.103.161.16/.17/.2/.1 里选活的）最稳；沙箱代理和默认 DNS 第一顺位
    .1 会 000。"""
    global GOOD_IP
    for i in range(8):
        args = ["curl", "-s", "--noproxy", "*", "--max-time", "60",
                "-X", method, f"https://api.notion.com/v1/{path}",
                "-H", f"Authorization: Bearer {TOKEN}",
                "-H", f"Notion-Version: {VER}"]
        if GOOD_IP:
            args[2:2] = ["--resolve", f"api.notion.com:443:{GOOD_IP}"]
        if raw_file:
            args += ["-F", f"file=@{raw_file}"]
        else:
            args += ["-H", "Content-Type: application/json"]
            if payload is not None:
                args += ["-d", json.dumps(payload, ensure_ascii=False)]
        r = subprocess.run(args, capture_output=True, text=True, stdin=subprocess.DEVNULL)
        try:
            j = json.loads(r.stdout)
            if j.get("object") != "error":
                return j
            print(f"  api error: {j.get('code')} {j.get('message', '')[:120]}", flush=True)
        except Exception:
            pass
        # 断连：换一个 IP 重试
        for ip in NOTION_IPS:
            if ip != GOOD_IP:
                t = subprocess.run(["curl", "-s", "--noproxy", "*", "--max-time", "10",
                                    "--resolve", f"www.notion.so:443:{ip}",
                                    "-o", "/dev/null", "-w", "%{http_code}",
                                    "https://www.notion.so"], capture_output=True,
                                   text=True, stdin=subprocess.DEVNULL)
                if t.stdout.strip() in ("200", "301", "302"):
                    print(f"  switch to ip {ip}", flush=True)
                    GOOD_IP = ip
                    break
        time.sleep(2 + i)
    raise RuntimeError(f"notion {method} {path} failed: {r.stdout[:200]}")


NOTION_IPS = ["208.103.161.16", "208.103.161.17", "208.103.161.2", "208.103.161.1"]
GOOD_IP = ""


def download(url, dest):
    """Wikimedia 直连（--noproxy），其他域名走默认代理；带重试。"""
    cmd = ["curl", "-sL", "--retry", "5", "--retry-all-errors", "-A", UA, "-o", dest]
    if "upload.wikimedia.org" in url or "commons.wikimedia.org" in url:
        cmd.insert(1, "--noproxy")
        cmd.insert(2, "*")
    cmd.append(url)
    for i in range(5):
        r = subprocess.run(cmd, capture_output=True, stdin=subprocess.DEVNULL)
        if r.returncode == 0 and os.path.getsize(dest) > 1024:
            return os.path.getsize(dest)
        time.sleep(2 + i * 2)
    raise RuntimeError(f"download failed: {url}")


def thumb_url(url, width=1600):
    parts = url.split("/wikipedia/commons/", 1)
    if len(parts) != 2:
        return None
    rel = parts[1]
    name = rel.rsplit("/", 1)[-1]
    return f"https://upload.wikimedia.org/wikipedia/commons/thumb/{rel}/{width}px-{name}"


# ---- 1. 分页拉全 LifeList 条目 ----
pages, cursor = [], None
while True:
    payload = {"page_size": 100}
    if cursor:
        payload["start_cursor"] = cursor
    d = notion("data_sources/%s/query" % DS, payload, method="POST")
    pages += d.get("results", [])
    cursor = d.get("next_cursor")
    print(f"queried {len(pages)} pages...", flush=True)
    if not cursor:
        break
    time.sleep(0.4)
print(f"total pages: {len(pages)}", flush=True)


# ---- 2. 逐页找 external image block ----
targets = []
for idx, p in enumerate(pages):
    pid = p["id"]
    title = "".join(t["plain_text"] for t in p["properties"]["中文名"]["title"])
    d = notion(f"blocks/{pid}/children?page_size=100")
    found = 0
    for b in d.get("results", []):
        if b["type"] == "image" and b["image"]["type"] == "external":
            url = b["image"]["external"]["url"]
            cap = b["image"].get("caption", [])
            targets.append({"title": title, "block_id": b["id"], "url": url, "caption": cap})
            found += 1
    if found:
        print(f"  [{idx+1}/{len(pages)}] {title}: {found} external", flush=True)
    time.sleep(0.35)

print(f"\n=== {len(targets)} external image blocks to migrate ===\n", flush=True)


# ---- 3. 逐条迁移 ----
results = []
for i, t in enumerate(targets):
    name, url = t["title"], t["url"]
    print(f"[{i+1}/{len(targets)}] {name}", flush=True)
    try:
        fname = url.rsplit("/", 1)[-1].split("?")[0] or "image.jpg"
        dest = os.path.join(CACHE, f"{t['block_id'].replace('-','')[:12]}_{fname}")
        size = download(url, dest)
        if size > 18 * 1024 * 1024:
            tu = thumb_url(url)
            print(f"  {size//1024//1024}MB too big -> thumb", flush=True)
            size = download(tu, dest)
            fname = f"thumb_{fname}"
        mime = mimetypes.guess_type(fname)[0] or "image/jpeg"

        up = notion("file_uploads", {"mode": "single_part", "filename": fname,
                                     "content_type": mime}, method="POST")
        notion(f"file_uploads/{up['id']}/send", method="POST", raw_file=dest)
        notion(f"blocks/{t['block_id']}",
               {"image": {"file_upload": {"id": up["id"]},
                          "caption": t["caption"]}}, method="PATCH")
        print(f"  ✅ {size//1024} KB, fid {up['id'][:8]}", flush=True)
        results.append({**t, "status": "ok", "file_upload_id": up["id"], "size_kb": size // 1024})
        os.remove(dest)
    except Exception as e:
        print(f"  ❌ {e}", flush=True)
        results.append({**t, "status": "fail", "error": str(e)[:200]})
    time.sleep(0.6)

json.dump(results, open(OUT, "w"), ensure_ascii=False, indent=2)
ok = sum(1 for r in results if r["status"] == "ok")
fail = len(results) - ok
print(f"\n=== done: {ok} ok, {fail} fail ===")
print(f"saved: {OUT}")
