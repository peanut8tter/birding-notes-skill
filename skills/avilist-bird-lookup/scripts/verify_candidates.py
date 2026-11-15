"""校验候选学名是否在 AviList，对未匹配项给出同属候选。
用法：编辑 candidates 列表后运行
  python3 verify_candidates.py <avilist_json> <candidates_py>
candidates_py 中应有列表 candidates = [(中文名, 学名, 备注), ...]
"""
import sys, json, importlib.util
from collections import defaultdict

avilist_json = sys.argv[1] if len(sys.argv)>1 else 'data/avilist_species.json'
cand_py = sys.argv[2] if len(sys.argv)>2 else 'data/candidates.py'

with open(avilist_json) as f:
    species = json.load(f)
by_sci = {s['sci']: s for s in species}
by_genus = defaultdict(list)
for s in species:
    by_genus[s['sci'].split()[0]].append(s)

spec = importlib.util.spec_from_file_location('cand', cand_py)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
candidates = mod.candidates

ok, miss = 0, 0
for cn, sci, note in candidates:
    if sci in by_sci:
        s = by_sci[sci]
        print(f"✅ {cn:15s} {s['sci']:35s} {s['en']:35s} {s['order']}/{s['family']}")
        ok += 1
    else:
        miss += 1
        print(f"❌ {cn:15s} 未匹配 {sci}")
        cousins = by_genus.get(sci.split()[0], [])
        for c in cousins[:5]:
            print(f"     候选: {c['sci']:35s} | {c['en']}")

print(f"\n总结: ✅{ok} ❌{miss}")
