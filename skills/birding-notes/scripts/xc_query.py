#!/usr/bin/env python3
"""
Query xeno-canto v3 API for the best recording of a bird species.

Usage:
    python3 scripts/xc_query.py "Urocissa erythroryncha"
    python3 scripts/xc_query.py "Acridotheres tristis" --top 5

Outputs JSON with id / recordist / country / type / license, ranked.

Reads API key from path specified in config.json (xenocanto.api_key_path).
Get a free key at https://xeno-canto.org/account
"""

import argparse, json, os, sys, urllib.request, urllib.parse


def load_config():
    here = os.path.dirname(os.path.abspath(__file__))
    cfg_path = os.path.join(os.path.dirname(here), "config.json")
    if not os.path.exists(cfg_path):
        print(
            "ERROR: config.json not found. Copy config.example.json to config.json and fill in your values.",
            file=sys.stderr,
        )
        sys.exit(1)
    return json.load(open(cfg_path))


def load_xc_key(cfg):
    path = os.path.expanduser(cfg["xenocanto"]["api_key_path"])
    if not os.path.exists(path):
        print(
            f"ERROR: xeno-canto key file not found at {path}.\n"
            f"Create it as: {{\"api_key\": \"<your_key>\"}}\n"
            f"Get a free key at https://xeno-canto.org/account",
            file=sys.stderr,
        )
        sys.exit(1)
    return json.load(open(path))["api_key"]


def fetch(gen, sp, key):
    q = f'gen:"{gen}" sp:"{sp}"'
    url = f"https://xeno-canto.org/api/3/recordings?query={urllib.parse.quote_plus(q)}&key={key}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (birding-notes-skill)"})
    return json.loads(urllib.request.urlopen(req, timeout=30).read())


def rank_recordings(recs, prefer_country):
    rank_q = {"A": 1, "B": 2, "C": 3, "D": 4, "E": 5, "no score": 9}

    def key(r):
        sono = r.get("sono") or {}
        sono_ok = 0 if sono.get("large") else 9  # has sonogram URL?
        q_score = rank_q.get(r.get("q", "no score"), 9)
        t = (r.get("type") or "").lower()
        type_score = 0 if "song" in t else (1 if "call" in t else 2)
        cnt = r.get("cnt", "")
        loc_score = 0 if cnt == prefer_country else 1
        return (q_score, type_score, loc_score, sono_ok)

    return sorted(recs, key=key)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("species", help='Scientific name, e.g. "Urocissa erythroryncha"')
    parser.add_argument("--top", type=int, default=3, help="Number of top recordings to return")
    args = parser.parse_args()

    parts = args.species.strip().split()
    if len(parts) != 2:
        print('ERROR: species must be "Genus species"', file=sys.stderr)
        sys.exit(1)
    gen, sp = parts

    cfg = load_config()
    key = load_xc_key(cfg)
    prefer = cfg["user_preferences"].get("regional_focus_country", "China")

    data = fetch(gen, sp, key)
    recs = data.get("recordings", [])
    if not recs:
        print(json.dumps({"error": f"no recordings for {args.species}"}, ensure_ascii=False))
        sys.exit(1)

    ranked = rank_recordings(recs, prefer)
    out = []
    for r in ranked[: args.top]:
        out.append(
            {
                "id": r.get("id"),
                "url": f"https://xeno-canto.org/{r.get('id')}",
                "scientific": f"{r.get('gen')} {r.get('sp')}",
                "english": r.get("en"),
                "recordist": r.get("rec"),
                "country": r.get("cnt"),
                "location": r.get("loc"),
                "type": r.get("type"),
                "quality": r.get("q"),
                "license": r.get("lic"),
                "duration": r.get("length"),
            }
        )

    print(
        json.dumps(
            {"species": args.species, "total": data.get("numRecordings"), "top": out},
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
