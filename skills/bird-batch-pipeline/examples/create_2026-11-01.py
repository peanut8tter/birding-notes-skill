# -*- coding: utf-8 -*-
"""2026-11-01 LifeList 上新：斑鱼狗（龙洞水库）、方尾鹟（火炉山小鸟澡堂）
版式 = 凤头蜂鹰样板：callout → 性格与行为 → 分类考据 → 分布与生态 → 鸣声 → 文化与演化 → 图（上传）"""
import json, subprocess, time, os, sys

import os
def _load_token():
    if os.environ.get("NOTION_TOKEN"): return os.environ["NOTION_TOKEN"]
    base = os.environ.get("BIRDING_NOTES_HOME") or os.path.expanduser("~/.config/birding-notes")
    for p in (os.path.join(base, "secrets", "notion.json"), os.path.expanduser("~/.workbuddy/secrets/notion.json")):
        if os.path.exists(p): return json.load(open(p))["integration_token"]
    sys.exit("未找到 Notion token：设置 NOTION_TOKEN，或让 AI 运行 birding-setup 向导")
TOKEN = _load_token()  # 由 birding-setup 保存
DBID = "37871355-4c9a-80db-91f4-f3480c7fa819"
RESOLVE = ["--noproxy", "*", "--resolve", "api.notion.com:443:208.103.161.16"]
BASE = "https://api.notion.com/v1"

def log(*a): print(*a, flush=True)

def call(method, path, body=None):
    for i in range(6):
        cmd = ["curl", "-s", "--max-time", "60"] + RESOLVE + ["-X", method, BASE + path,
               "-H", "Authorization: Bearer " + TOKEN, "-H", "Notion-Version: 2026-03-11"]
        if body is not None:
            cmd += ["-H", "Content-Type: application/json", "-d", json.dumps(body, ensure_ascii=False)]
        r = subprocess.run(cmd, capture_output=True, text=True)
        try: d = json.loads(r.stdout)
        except Exception: d = None
        if d and d.get("object") != "error": return d
        log(f"  retry {i+1}: {(d or {}).get('message', r.stdout[:150])}")
        time.sleep(2 + i * 2)
    raise RuntimeError("API failed: " + path)

def T(t): return [{"type": "text", "text": {"content": t}}]
def P(t): return {"object": "block", "type": "paragraph", "paragraph": {"rich_text": T(t)}}
def H2(t): return {"object": "block", "type": "heading_2", "heading_2": {"rich_text": T(t)}}
def H3(t): return {"object": "block", "type": "heading_3", "heading_3": {"rich_text": T(t)}}
def B(t): return {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": T(t)}}
def BM(u): return {"object": "block", "type": "bookmark", "bookmark": {"url": u}}
def CO(t): return {"object": "block", "type": "callout", "callout": {
    "icon": {"type": "emoji", "emoji": "🐦"}, "color": "gray_background", "rich_text": T(t)}}

SPECIES = [
{
    "cn": "斑鱼狗", "sci": "Ceryle rudis", "en": "Pied Kingfisher",
    "order": "佛法僧目", "family": "翠鸟科", "res": "🟢 留鸟 Resident",
    "iucn": "LC 无危", "cnlv": "三有", "place": "广州龙洞水库",
    "img": "/tmp/lyd/c1.jpg",
    "cap": "📷 Charles J. Sharp · Wikimedia Commons · CC BY-SA 4.0（博茨瓦纳，指名亚种；左♂ 右♀）",
    "blocks": [
        CO("首次记录：2026-11-01 · 广州龙洞水库。"),
        H2("性格与行为"),
        B("能在水面上空振翅悬停（hovering），定位后头朝下垂直扎入水中捕鱼；是少数主要靠悬停捕猎的翠鸟，因此可在远离岸边栖枝的开阔水面觅食"),
        B("小鱼可在飞行中直接吞下，不必像多数翠鸟那样回到栖枝摔打后再吃"),
        B("常成对或小群活动，比普通翠鸟更喧闹，飞行时频繁发出尖锐叫声"),
        B("有合作繁殖：繁殖对常有「帮手」协助喂雏，帮手多为上一窝的子代雄鸟，也有无亲缘关系的雄鸟——非洲肯尼亚种群的长期研究（Reyer 1980s）是合作繁殖的经典案例"),
        B("在土崖、河岸掘洞营巢，隧道可深达 1–2 m"),
        B("雌雄可辨：雄鸟胸前两道黑色胸带（上宽下窄），雌鸟仅一道且中间常断开"),
        H2("分类考据"),
        H3("拉丁名词源"),
        B("Ceryle —— 古希腊语 kērylos，古希腊诗文中一种传说中的海鸟，常与翠鸟（halcyon）并提"),
        B("rudis —— 拉丁语「粗朴、未经雕饰」，通常解释为指其只有黑白两色、不像其他翠鸟艳丽"),
        B("中文名「鱼狗」是翠鸟类的古称，《本草纲目·禽部》即有「鱼狗」条；「斑」指黑白斑驳的羽色"),
        H3("系统位置"),
        B("佛法僧目 Coraciiformes › 翠鸟科 Alcedinidae › 鱼狗亚科 Cerylinae › 斑鱼狗属 Ceryle"),
        B("斑鱼狗属仅此一种；同亚科还有冠鱼狗属 Megaceryle（中国有冠鱼狗）与美洲的绿鱼狗属 Chloroceryle"),
        B("中国分布的为 C. r. insignis 亚种（华南至海南）"),
        H2("分布与生态"),
        B("广布于撒哈拉以南非洲、中东、南亚至中国南部与中南半岛"),
        B("中国见于长江流域及以南、海南；在广州为留鸟，局地常见"),
        B("栖于水库、河流、鱼塘、河口等开阔水域，常停在电线、竹竿、岸边枯枝上"),
        BM("https://www.gbif.org/species/2475679"),
        P("GBIF · Ceryle rudis · 全球出现记录"),
        H2("鸣声 / 鸣唱"),
        B("鸣声：尖锐、连续的 chirruk-chirruk 或 kwik-kwik 短音，飞行时与群内互相呼应时最常听到"),
        BM("https://xeno-canto.org/855532"),
        P("xeno-canto · XC855532 · Hong Kong, New Territories fish ponds · flight call · Geoff Carey · CC BY-NC-SA 4.0（C. r. insignis）"),
        H2("文化与演化"),
        B("古希腊诗人阿尔克曼（Alcman）有诗句：愿化身 kērylos，由翠鸟（halcyon）托负着掠过海浪——属名 Ceryle 即取自这一典故"),
        B("鱼狗亚科现存三属分布于新旧大陆，斑鱼狗是其中唯一广布非洲—亚洲的小型种"),
    ],
},
{
    "cn": "方尾鹟", "sci": "Culicicapa ceylonensis", "en": "Grey-headed Canary-flycatcher",
    "order": "雀形目", "family": "玉鹟科", "res": "🔵 冬候鸟 Winter visitor",
    "iucn": "LC 无危", "cnlv": "三有", "place": "广州火炉山森林公园（小鸟澡堂）",
    "img": "/tmp/lyd/c3.jpg",
    "cap": "📷 Nirmal Dulal · Wikimedia Commons · CC BY-SA 4.0（尼泊尔 Panchkhal）",
    "blocks": [
        CO("首次记录：2026-11-01 · 广州火炉山森林公园（小鸟澡堂）。"),
        H2("性格与行为"),
        B("极活跃，在枝叶间频繁跳跃，并不断从栖枝飞出空中捕捉飞虫后返回（sallying）"),
        B("停栖时姿态较直立，尾常扇开、上下弹动"),
        B("主食小型飞虫：蚊、蝇、小甲虫、蜂类等（属名即「捕蚊者」）"),
        B("常单独或成对活动，冬季多加入山雀、柳莺、绣眼等组成的混合鸟群"),
        B("有领域性；鸣叫频繁，较易循声发现"),
        B("会到林下水源饮水洗浴，城市公园的「小鸟澡堂」是近距离观察它的常见场景"),
        H2("分类考据"),
        H3("拉丁名词源"),
        B("Culicicapa —— 拉丁语 culex（蚊、蠓）+ capere（捕捉），「捕蚊者」"),
        B("ceylonensis —— 「锡兰的」，模式标本产地为斯里兰卡（旧称锡兰）"),
        B("中文名「方尾」指尾端平直；英文 Canary-flycatcher 中的 canary 指其金丝雀般的黄色下体"),
        H3("系统位置"),
        B("雀形目 Passeriformes › 玉鹟科 Stenostiridae › 方尾鹟属 Culicicapa"),
        B("⚠️ 虽名为「鹟」，但并非鹟科 Muscicapidae 成员：分子系统学研究（Beresford et al. 2005 等）将其移入玉鹟科，与非洲的仙鹟 Stenostira、冠鹟 Elminia 同科；旧名录（含郑光美 2011 第二版）曾置于鹟科"),
        B("中国分布的为 C. c. calochrysea 亚种"),
        H2("分布与生态"),
        B("分布于南亚、喜马拉雅、中国南部至东南亚及大巽他群岛"),
        B("中国：西南、华中多为夏候鸟或留鸟，云南为留鸟；广东、香港为冬候鸟"),
        B("在广州为冬候鸟，见于山地阔叶林、林缘与公园树林，数量不多"),
        B("近年东部沿海迁徙季记录增多，山西历山保护区也有省级新纪录"),
        BM("https://www.gbif.org/species/2492634"),
        P("GBIF · Culicicapa ceylonensis · 全球出现记录"),
        H2("鸣声 / 鸣唱"),
        B("鸣唱：清亮甜美的哨音 chic… chiree-chilee，末音上扬；另有 churrru 的颤音和轻柔的 pit pit 声"),
        BM("https://xeno-canto.org/1102112"),
        P("xeno-canto · XC1102112 · China, Hangzhou, Guanshan Park · song · wu555 · CC BY-NC-SA 4.0（C. c. calochrysea）"),
        H2("文化与演化"),
        B("玉鹟科是 2000 年代分子研究新建立的科，成员分散于非洲与亚洲，外形各异，过去被分别归入鹟科、王鹟科等"),
        B("2023 年列入国家「三有」保护动物名录"),
    ],
},
]

out = {}
for sp in SPECIES:
    q = call("POST", "/data_sources/37871355-4c9a-8073-b4a3-000b9cc2ea18/query",
             {"filter": {"property": "中文名", "title": {"equals": sp["cn"]}}})
    if q["results"]:
        pid = q["results"][0]["id"]; log(sp["cn"], "exists", pid)
    else:
        props = {
            "中文名": {"title": T(sp["cn"])}, "学名": {"rich_text": T(sp["sci"])},
            "Common name": {"rich_text": T(sp["en"])}, "数据来源": {"rich_text": T("AviList v2025")},
            "目": {"select": {"name": sp["order"]}}, "科": {"select": {"name": sp["family"]}},
            "居留型": {"select": {"name": sp["res"]}}, "IUCN 等级": {"select": {"name": sp["iucn"]}},
            "中国保护等级": {"select": {"name": sp["cnlv"]}},
            "首次地点": {"rich_text": T(sp["place"])}, "首次日期": {"date": {"start": "2026-11-01"}},
        }
        pid = call("POST", "/pages", {"parent": {"database_id": DBID}, "properties": props})["id"]
        log(sp["cn"], "created", pid)
    out[sp["cn"]] = pid
    kids = call("GET", f"/blocks/{pid}/children?page_size=100")["results"]
    if kids:
        log("  body exists, skip"); continue
    call("PATCH", f"/blocks/{pid}/children", {"children": sp["blocks"]})
    fu = call("POST", "/file_uploads", {"mode": "single_part", "filename": sp["cn"] + ".jpg", "content_type": "image/jpeg"})
    r = subprocess.run(["curl", "-s", "--max-time", "120"] + RESOLVE + ["-X", "POST",
        f"{BASE}/file_uploads/{fu['id']}/send", "-H", "Authorization: Bearer " + TOKEN,
        "-H", "Notion-Version: 2026-03-11", "-F", f"file=@{sp['img']};type=image/jpeg"],
        capture_output=True, text=True)
    assert json.loads(r.stdout).get("status") == "uploaded", r.stdout[:200]
    call("PATCH", f"/blocks/{pid}/children", {"children": [{"object": "block", "type": "image", "image": {
        "type": "file_upload", "file_upload": {"id": fu["id"]}, "caption": T(sp["cap"])}}]})
    log("  body + image done")
json.dump(out, open("/tmp/lyd/pages.json", "w"), ensure_ascii=False)
log("ALL DONE", out)
