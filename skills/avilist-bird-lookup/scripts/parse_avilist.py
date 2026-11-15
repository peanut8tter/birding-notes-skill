"""把 AviList v2025 Excel 转成 JSON 便于查询。
用法: python3 parse_avilist.py <xlsx_path> <output_json_path>
"""
import sys, json
from openpyxl import load_workbook

xlsx = sys.argv[1] if len(sys.argv)>1 else 'data/avilist-v2025.xlsx'
out = sys.argv[2] if len(sys.argv)>2 else 'data/avilist_species.json'

wb = load_workbook(xlsx, read_only=True, data_only=True)
ws = wb['AviList v2025 extended']
headers = [c.value for c in next(ws.iter_rows(min_row=1, max_row=1))]
# headers: Sequence, Taxon_rank, Order, Family, Family_English_name,
#          Scientific_name, Authority, Bibliographic_details,
#          English_name_AviList, Decision_summary, Range,
#          Extinct_or_possibly_extinct, IUCN_Red_List_Category, AvibaseID

data = []
for row in ws.iter_rows(min_row=2, values_only=True):
    if row[1] != 'species':
        continue
    data.append({
        'order': row[2],
        'family': row[3],
        'family_en': row[4],
        'sci': row[5],
        'auth': row[6],
        'en': row[8],
        'avibase': row[13],
    })

with open(out, 'w') as f:
    json.dump(data, f, ensure_ascii=False)
print(f'Saved {len(data)} species to {out}')
