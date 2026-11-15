# -*- coding: utf-8 -*-
"""2026-11-09 南沙十九涌 13 种 LifeList 上新（v2 版式：实拍照第一块 → callout → 🐾 → 🧬 → 🌏(GBIF) → 🎵(XC) → 📜(+博物画)）
可重入：已存在的页面跳过建行；已有正文的跳过写入。图片从 /tmp/nansha/final_images.json 读取。"""
import json, subprocess, time, os, sys

import os
TOKEN = os.environ["NOTION_TOKEN"]  # export NOTION_TOKEN=ntn_xxx
DBID = "37871355-4c9a-80db-91f4-f3480c7fa819"
DS = "37871355-4c9a-8073-b4a3-000b9cc2ea18"
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
def DIV(): return {"object": "block", "type": "divider", "divider": {}}

def upload_file(path, name):
    fu = call("POST", "/file_uploads", {"mode": "single_part", "filename": name, "content_type": "image/jpeg"})
    r = subprocess.run(["curl", "-s", "--max-time", "120"] + RESOLVE + ["-X", "POST",
        f"{BASE}/file_uploads/{fu['id']}/send", "-H", "Authorization: " + "Bearer " + TOKEN,
        "-H", "Notion-Version: 2026-03-11", "-F", f"file=@{path};type=image/jpeg"],
        capture_output=True, text=True)
    assert json.loads(r.stdout).get("status") == "uploaded", r.stdout[:200]
    return fu["id"]

def img_block(fu_id, caption):
    return {"object": "block", "type": "image", "image": {
        "type": "file_upload", "file_upload": {"id": fu_id}, "caption": T(caption)}}

PLACE = "广州南沙十九涌"
DATE = "2026-11-08"

SPECIES = [
# ============ 1 黑脸琵鹭 ============
{"cn": "黑脸琵鹭", "sci": "Platalea minor", "en": "Black-faced Spoonbill",
 "order": "鹈形目", "family": "鹮科", "res": "🔵 冬候鸟 Winter visitor",
 "iucn": "EN 濒危", "cnlv": "国家一级", "gbif": "2480805",
 "xc": ("XC134758", "日本佐贺县，call（幼鸟低哑两音节）· John Wright · CC BY-NC-SA 3.0（xeno-canto 全库唯一前景种录音）"),
 "sound": "平时十分安静；受惊时发出低沉短促的呱声，巢中雏鸟与求偶期叫声较明显",
 "blocks": [
    CO("首次记录：" + DATE + " · " + PLACE + "。"),
    H2("🐾 性格与行为"),
    B("觅食方式独特：将匙状喙半张开伸入水中左右扫动（sweep-sifting），靠触觉感应猎物后合嘴——不需要看清猎物，因此多在浑浊的浅水滩涂和鱼塘觅食"),
    B("白天随潮汐「作息」：退潮时到潮间带泥滩觅食，涨潮时飞回堤内鱼塘群栖休整，路线固定"),
    B("高度集群：迁徙、越冬、繁殖都成大群，常与白琵鹭、鹭类混群；夜栖地集中"),
    B("飞行时颈部完全伸直（区别于鹭类缩颈），白色躯体配黑翼端，队列飞行姿态平稳"),
    B("繁殖期（春）头后长出黄色饰羽，裸出的黑脸更加醒目"),
    H2("🧬 分类考据"),
    H3("拉丁名词源"),
    B("Platalea —— 古希腊语 platys「宽、扁」，指琵琶状的喙；林奈 1758 年以此建琵鹭属"),
    B("minor —— 拉丁语「较小的」：种加词直接点出它比白琵鹭体型更小、喙更短"),
    B("19 世纪曾被作为白琵鹭的亚种（Platalea leucorodia minor），20 世纪末才被普遍接受为独立种——「minor」从亚种名升格为种名"),
    B("中文名「黑脸」：眼先、额线与喙基裸区全黑（白琵鹭裸区为黄色，且不达眼先）"),
    H3("系统位置"),
    B("鹈形目 Pelecaniformes › 鹮科 Threskiornithidae › 琵鹭属 Platalea"),
    B("全球琵鹭属 6 种中唯一被 IUCN 列为濒危（EN）的种类"),
    B("鹮科成员的喙大多下弯（鹮类），琵鹭却是平直的匙形——同一科里喙形演化的两个方向"),
    H2("🌏 分布与生态"),
    B("繁殖地高度集中：主要在朝鲜半岛西海岸离岸岛屿，另有少量在中国辽东（大连形人坨）和俄罗斯远东"),
    B("越冬地：台湾西南部（曾文溪口为全球最大越冬地）、香港后海湾—米埔、澳门路氹、深圳湾、越南红河口等；华南沿海废弃鱼塘群是重要觅食地"),
    B("全球种群约 6,000 余只（每年 1 月全球同步调查），数量缓慢回升但仍属 EN"),
    B("迁徙路线纵贯中国东部沿海：黄河口、长江口、雷州半岛都是关键停歇地"),
    B("在广州为冬候鸟，11 月正值抵达期——南沙的咸淡水塘与泥滩是它稳定的越冬觅食地"),
    BM("https://www.gbif.org/species/2480805"),
    P("GBIF · Platalea minor · 全球出现记录"),
    H2("🎵 鸣声 / 鸣唱"),
    B("平时安静，受惊时发低哑的呱声；育雏期巢区鸣声连续"),
    BM("https://xeno-canto.org/134758"),
    P("xeno-canto · XC134758 · " + "日本佐贺 · call · John Wright · CC BY-NC-SA 3.0（全库唯一前景种录音）"),
    H2("📜 文化与演化"),
    B("因脸黑、姿态优雅、极度濒危，被观鸟界称为「黑面舞者」；台湾 1990 年代起的保育运动使其成为明星物种，每年 1 月的全球同步普查已持续 20 余年"),
    B("主要繁殖岛屿位于朝鲜半岛军事分界线附近海域，人迹罕至反而保全了繁殖地——「冷战意外庇护」的著名案例"),
    B("1990 年代初全球仅记录到约 300 余只，如今 6,000 余只，是东亚—澳大利西亚迁飞区（EAAF）联合保护的旗舰物种"),
 ]},
# ============ 2 白琵鹭 ============
{"cn": "白琵鹭", "sci": "Platalea leucorodia", "en": "Eurasian Spoonbill",
 "order": "鹈形目", "family": "鹮科", "res": "🔵 冬候鸟 Winter visitor",
 "iucn": "LC 无危", "cnlv": "国家二级", "gbif": "2480801",
 "xc": ("XC1042791", "法国 Saint-Jean-le-Thomas，begging call（雏鸟乞食）· Sonothèque ADVL · CC0（公有领域）"),
 "sound": "低钝的呱声与咕哝声，巢区雏鸟乞食声连续而急促",
 "blocks": [
    CO("首次记录：" + DATE + " · " + PLACE + "。"),
    H2("🐾 性格与行为"),
    B("同样以左右扫滤（sweep-feeding）觅食：浅水中边走边扫，靠触觉捕鱼虾，也会用脚搅动泥面驱赶猎物"),
    B("比黑脸琵鹭更偏爱淡水环境：沼泽、水田、河边、湖泊浅滩"),
    B("飞行时颈伸直、振翅沉稳，常松散编队；翅下白色而翼端黑"),
    B("繁殖期后枕有蓬松的黄色冠羽，胸前橙黄色饰羽——裸出的喙基与喉为黄色，不似黑脸琵鹭全黑"),
    H2("🧬 分类考据"),
    H3("拉丁名词源"),
    B("Platalea —— 古希腊语 platys「宽、扁」（琵琶状喙）；本种是林奈 1758 年命名的琵鹭属模式种"),
    B("leucorodia —— 古希腊语 leukos「白」+ rhodios（古代对一种白色水鸟的称呼），老普林尼《博物志》记载的 leucorhodios 即指琵鹭一类"),
    B("中文名的「白」是与黑脸琵鹭相对而言——它裸区其实偏黄，只是脸没有黑到眼先"),
    H3("系统位置"),
    B("鹈形目 Pelecaniformes › 鹮科 Threskiornithidae › 琵鹭属 Platalea"),
    B("全球 3 亚种，中国分布为指名亚种 P. l. leucorodia；黑脸琵鹭正是从本种「分家」出去的东亚近亲"),
    H2("🌏 分布与生态"),
    B("繁殖区从西南欧经中东、中亚到中国东北与新疆（局部），越冬于南欧、非洲、南亚及华南沿海"),
    B("在中国北部有繁殖种群，东部沿海越冬；在华南为冬候鸟，数量通常少于黑脸琵鹭，两者常混群"),
    B("全球种群约 10 万级，IUCN LC；主要威胁是湿地排水与巢区干扰"),
    B("南沙冬候鸟，冬春见于滩涂与鱼塘——常混在黑脸琵鹭群里，需要看脸才能分开"),
    BM("https://www.gbif.org/species/2480801"),
    P("GBIF · Platalea leucorodia · 全球出现记录"),
    H2("🎵 鸣声 / 鸣唱"),
    B("低钝的呱声，飞行与巢区可闻；雏鸟乞食声连续"),
    BM("https://xeno-canto.org/1042791"),
    P("xeno-canto · XC1042791 · " + "法国 Normandie · begging call · Sonothèque ADVL · CC 0（公有领域；华南暂无录音，选欧洲巢区录音）"),
    H2("📜 文化与演化"),
    B("是琵鹭属最早被科学命名的种（林奈 1758《自然系统》第 10 版），全属的「度量衡」——后来的琵鹭都以它为参照"),
    B("中世纪欧洲博物志（如 Aldrovandi《鸟类学》1603）已有琵鹭记述；传统欧洲把它与鹮混称，解剖学时代才厘清两者同科不同形"),
 ]},
# ============ 3 普通鸬鹚 ============
{"cn": "普通鸬鹚", "sci": "Phalacrocorax carbo", "en": "Great Cormorant",
 "order": "鲣鸟目", "family": "鸬鹚科", "res": "🔵 冬候鸟 Winter visitor",
 "iucn": "LC 无危", "cnlv": "三有", "gbif": "2481890",
 "xc": ("XC1099018", "香港米埔，call（觅食群低哑声）· Bo Shunqi 薄顺奇 · CC BY-NC-SA 4.0"),
 "sound": "低哑的 croak/grunt，群栖与夜栖地常闻；平时飞行多沉默",
 "blocks": [
    CO("首次记录：" + DATE + " · " + PLACE + "。"),
    H2("🐾 性格与行为"),
    B("潜水捕鱼高手：用双脚划水潜追（pursuit diving），可潜数米深、追出十几秒；传统渔猎驯化它捕鱼（颈部系绳防吞大鱼）在中国已上千年"),
    B("羽毛润湿性高（潜水时减少浮力），每次潜水后必须张翅晾晒——「晾翅」是其标志姿势"),
    B("极群栖：成排停栖于树上、桩柱、航标晾翅；夜栖地固定，粪便长期累积可致树木死亡"),
    B("体重较大，起飞需在水面上助跑「滑水起飞」；飞行时颈部伸直微下曲，区别于雁鸭"),
    B("华南见到的多为北方南下的冬候群；在河网密布的珠三角冬季常见于航标桩、竹排"),
    H2("🧬 分类考据"),
    H3("拉丁名词源"),
    B("Phalacrocorax —— 古希腊语 phalakros「秃的」+ korax「乌鸦」，「秃鸦」：指成鸟头颈裸区与通体乌黑"),
    B("carbo —— 拉丁语「炭」，指碳黑色羽色；林奈 1758 年命名"),
    B("中文「鸬鹚」为古称，《本草纲目·禽部》有鸬鹚条并记「人家养之以取鱼」；英文名 cormorant 经法语 corps corbin（乌鸦之身）来自拉丁 corvus marinus（海鸦）"),
    H3("系统位置"),
    B("鲣鸟目 Suliformes › 鸬鹚科 Phalacrocoracidae › 鸬鹚属 Phalacrocorax"),
    B("⚠️ 分类史：鸬鹚过去长期被放在「鹈形目」，分子系统学（Hackett et al. 2008 等）把它与鲣鸟、军舰鸟、蛇鹈一起独立为鲣鸟目——AviList 采此说"),
    B("中国分布的为 P. c. sinensis 亚种"),
    H2("🌏 分布与生态"),
    B("除南美内陆外全球广布；中国繁殖于东北、华北、新疆、西藏，南方多为冬候"),
    B("栖息大型水体：水库、江河、河口、海岸岩礁；广州冬季常见于珠江航道与南沙河口，成群栖于航标桩"),
    B("食量大、群栖集中，在欧洲因「与渔争鱼」曾被系统性捕杀，是渔业-鸟类冲突的代表性物种"),
    BM("https://www.gbif.org/species/2481890"),
    P("GBIF · Phalacrocorax carbo · 全球出现记录"),
    H2("🎵 鸣声 / 鸣唱"),
    B("低哑的 croak/grunt，主要在群栖地与巢区发出；飞行时基本沉默"),
    BM("https://xeno-canto.org/1099018"),
    P("xeno-canto · XC1099018 · " + "香港米埔 · call · Bo Shunqi 薄顺奇 · CC BY-NC-SA 4.0"),
    H2("📜 文化与演化"),
    B("杜甫《戏作俳谐体解闷》「家家养乌鬼，顿顿食黄鱼」——「乌鬼」即蜀地驯养捕鱼的鸬鹚，是中国渔猎文化最早的书面证据之一"),
    B("日本岐阜长良川「鹈饲」：唐代由中国传入的皇家鸬鹚捕鱼技艺，至今 1,300 余年；广西漓江的鸬鹚捕鱼今为表演项目"),
    B("演化上，鸬鹚是「用浮力换潜水」的极端案例：羽毛可润湿以减小浮力，代价是必须晾晒——同一策略也见于蛇鹈，是鲣鸟目内的趋同"),
 ]},
# ============ 4 反嘴鹬 ============
{"cn": "反嘴鹬", "sci": "Recurvirostra avosetta", "en": "Pied Avocet",
 "order": "鸻形目", "family": "反嘴鹬科", "res": "🔵 冬候鸟 Winter visitor",
 "iucn": "LC 无危", "cnlv": "三有", "gbif": "2480259",
 "xc": ("XC1099040", "香港米埔，call · Bo Shunqi 薄顺奇 · CC BY-NC-SA 4.0"),
 "sound": "响亮清脆的 kleep/klu-ip 尖哨，群飞时此起彼伏，是滩涂上最好认的声音之一",
 "blocks": [
    CO("首次记录：" + DATE + " · " + PLACE + "。"),
    H2("🐾 性格与行为"),
    B("喙向上翘，独一无二：觅食时喙尖贴着水面/泥面边走边左右扫，与琵鹭的扫滤同属「触觉觅食」，不依赖视觉"),
    B("长腿高跷体型，能涉进比多数鸻鹬更深的水；黑白羽色远看像穿燕尾服"),
    B("集群性强：越冬地动辄成百上千；夜宿开阔浅滩，警觉性高，受扰时整群起飞绕圈并连续齐鸣"),
    B("繁殖期护巢凶猛：对入侵者（人、狐狸、猛禽）佯装翅膀折断、拖着「伤翅」引开（distraction display），也会直接俯冲驱赶"),
    H2("🧬 分类考据"),
    H3("拉丁名词源"),
    B("Recurvirostra —— 拉丁语 recurvus「向后弯」+ rostrum「喙」：上翘的喙"),
    B("avosetta —— 意大利语（威尼斯方言）对这种鸟的称呼，法国博物学家 Belon 1555 年首用于书中；词根或与拉丁 avis「鸟」相关"),
    B("「反嘴」= 喙上翘，与杓鹬类的下弯喙互为镜像——中文、拉丁文、英文（avocet）三个名字全都在说同一件事"),
    H3("系统位置"),
    B("鸻形目 Charadriiformes › 反嘴鹬科 Recurvirostridae › 反嘴鹬属 Recurvirostra（全球 4 种，本种唯一广布欧亚非）"),
    B("同科近亲是长脚鹬属 Himantopus——黑翅长脚鹬与它共享「高跷+黑白」的身体方案"),
    H2("🌏 分布与生态"),
    B("繁殖于欧亚温带的盐沼、碱湖、海岸潟湖；越冬于非洲、南亚、华南沿海"),
    B("中国繁殖于新疆、内蒙古及西北盐湖带，东部沿海为越冬区；香港米埔、深圳湾是华南代表性越冬地"),
    B("偏爱咸淡水交错的浅塘与滩涂——南沙的咸淡水塘正合适，冬春稳定可见"),
    BM("https://www.gbif.org/species/2480259"),
    P("GBIF · Recurvirostra avosetta · 全球出现记录"),
    H2("🎵 鸣声 / 鸣唱"),
    B("响亮悦耳的 kleep 尖哨，群飞齐鸣；繁殖期有连续的 chattering 颤音"),
    BM("https://xeno-canto.org/1099040"),
    P("xeno-canto · XC1099040 · " + "香港米埔 · call · Bo Shunqi 薄顺奇 · CC BY-NC-SA 4.0"),
    H2("📜 文化与演化"),
    B("反嘴鹬是英国皇家鸟类保护协会（RSPB）会徽上的鸟：1947 年它在英国萨福克重新繁殖成功，被视为英国现代鸟类保护运动的开端标志"),
    B("上翘喙是「形态-行为协同演化」教科书案例：喙形+扫滤动作+触觉 Sensory- 驱动觅食构成一套完整方案——离开这套组合，翘喙毫无意义"),
 ]},
# ============ 5 灰斑鸻 ============
{"cn": "灰斑鸻", "sci": "Pluvialis squatarola", "en": "Grey Plover",
 "order": "鸻形目", "family": "鸻科", "res": "🔵 冬候鸟 Winter visitor",
 "iucn": "LC 无危", "cnlv": "三有", "gbif": "2480327",
 "xc": ("XC840935", "上海崇明横沙岛，call · Bo Shunqi 薄顺奇 · CC BY-NC-SA 4.0"),
 "sound": "清而哀的三音节哨音 too-ee…too-ee，夜间迁徙飞行时也可听到，是滩涂夜空的标志性声音",
 "blocks": [
    CO("首次记录：" + DATE + " · " + PLACE + "。"),
    H2("🐾 性格与行为"),
    B("典型「跑-停-啄」觅食：短距离冲刺后站立观察，再精准啄取泥面的螺、沙蚕、小蟹"),
    B("标志性「抖脚」行为（foot-trembling）：单脚快速抖动泥面，把小猎物惊出来再啄——鸻类中灰斑鸻做得尤其频繁"),
    B("越冬地个体间保持距离、领域性强，散布在开阔滩涂上；受惊时低飞掠滩，黑色腋斑一闪（飞行时最可靠的识别点）"),
    B("非繁殖羽通身灰色，与冬滩融为一体；春夏过境时部分个体已换成黑白分明的繁殖羽"),
    H2("🧬 分类考据"),
    H3("拉丁名词源"),
    B("Pluvialis —— 拉丁语 pluvia「雨」：金鸻类常在雨后活跃鸣叫，古人视为「报雨之鸟」，法文 pluvier 同源"),
    B("squatarola —— 意大利方言对灰斑鸻的称呼，16 世纪博物学家 Aldrovandi 记载后进入学名"),
    B("中文名「灰斑」概括了非繁殖羽的灰色与飞行时的黑色腋斑；旧英文名 Black-bellied Plover 看的是繁殖羽，现统一为 Grey Plover——同一个鸟，两套羽色各得一名"),
    H3("系统位置"),
    B("鸻形目 Charadriiformes › 鸻科 Charadriidae › 斑鸻属 Pluvialis（全球 4 种金/灰鸻）"),
    B("斑鸻属与小型鸻（Anarhynchus 等）在鸻科内分属不同支系——「鸻」这个中文名横跨了科内多个演化分支"),
    H2("🌏 分布与生态"),
    B("环北极苔原繁殖，越冬地横跨南北半球的海岸线，是分布最广的鸻之一"),
    B("中国东部沿海普遍越冬；在南沙为冬候鸟，11 月起滩涂常见，常单只或小群散布"),
    B("迁徙单程可达上万公里；阿拉斯加繁殖个体横跨太平洋到东南亚越冬的路线已由追踪研究证实"),
    BM("https://www.gbif.org/species/2480327"),
    P("GBIF · Pluvialis squatarola · 全球出现记录"),
    H2("🎵 鸣声 / 鸣唱"),
    B("清而哀的三音哨 too-ee，夜飞时持续可闻"),
    BM("https://xeno-canto.org/840935"),
    P("xeno-canto · XC840935 · " + "上海崇明横沙岛 · call · Bo Shunqi 薄顺奇 · CC BY-NC-SA 4.0"),
    H2("📜 文化与演化"),
    B("「雨鸟」词源（Pluvialis）是欧洲古代「以鸟占天气」民俗的残留——法语 pluvier 至今仍是它的名字"),
    B("北极繁殖—全球越冬的它，一生多数时间在潮间带泥滩上度过；是「潮间带连通全球海岸」这一生态现实的最直观注脚"),
 ]},
# ============ 6 环颈鸻 ============
{"cn": "环颈鸻", "sci": "Anarhynchus alexandrinus", "en": "Kentish Plover",
 "order": "鸻形目", "family": "鸻科", "res": "🔵 冬候鸟 Winter visitor",
 "iucn": "LC 无危", "cnlv": "三有", "gbif": "9372299",
 "xc": ("XC911441", "上海奉贤碧海金沙，call（集群停歇）· Bo Shunqi 薄顺奇 · CC BY-NC-SA 4.0"),
 "sound": "短促柔和的 prriep / pit 哨音，群飞与换群时连续",
 "blocks": [
    CO("首次记录：" + DATE + " · " + PLACE + "。"),
    H2("🐾 性格与行为"),
    B("小型鸻里的「短跑选手」：在沙滩泥滩快速跑动-急停-啄食，主要靠视觉捕食表层的小螺、沙蚕、蟹"),
    B("繁殖期「假伤表演」极为投入：拖翅扑地装作折翼，把捕食者从沙地浅坑巢边引开——伪装巢+行为欺骗双保险"),
    B("常做沙浴（sand-bathing），白天在高潮线附近群栖休息"),
    B("在华南沿海与白脸鸻同域混群且极相似：看脸（眼先是否白、颈环粗细）、腿色、听声都是关键识别点"),
    H2("🧬 分类考据"),
    H3("拉丁名词源"),
    B("alexandrinus ——「埃及亚历山大港的」，模式标本产地；中世纪博物书称之为 Alexandrine Plover"),
    B("英文名 Kentish Plover 得名于 19 世纪英国肯特郡海滩的繁殖种群——该种群 20 世纪中叶消失后，这个名字成了「历史化石」"),
    B("⚠️ AviList v2025：小型鸻类已整体从 Charadrius 移入 Anarhynchus（该属模式种是新西兰的弯嘴鸻），旧记法 Charadrius alexandrinus"),
    B("「白脸鸻」（A. dealbatus）曾是本种亚种，2008 年后依羽色、裸部与鸣声差异被普遍拆分为独立种——两者在华南沿海同域分布，识别是观鸟圈的经典课题"),
    H3("系统位置"),
    B("鸻形目 Charadriiformes › 鸻科 Charadriidae › 弯嘴鸻属 Anarhynchus"),
    B("与美洲的 Snowy Plover（A. nivosus）构成近缘种组，三者（含白脸鸻）曾长期被合并处理"),
    H2("🌏 分布与生态"),
    B("广布于欧亚非大陆海岸与内陆碱滩；中国繁殖于北部和东部沿海沙滩，华南沿海为冬候并部分留居"),
    B("偏好开阔沙岸、泥滩与咸水塘边缘；南沙冬季滩涂常见，与白脸鸻、蒙古沙鸻混群"),
    B("繁殖生物学研究深入：雌雄双亲轮流孵卵、换班仪式化的行为学（草地或碱滩）是行为生态学经典材料"),
    BM("https://www.gbif.org/species/9372299"),
    P("GBIF · Anarhynchus alexandrinus · 全球出现记录"),
    H2("🎵 鸣声 / 鸣唱"),
    B("短促柔和的 prriep 哨音；受惊时音更急；与白脸鸻鸣声有量化的声学差异，但人耳极难分辨"),
    BM("https://xeno-canto.org/911441"),
    P("xeno-canto · XC911441 · " + "上海奉贤碧海金沙 · call（集群停歇）· Bo Shunqi 薄顺奇 · CC BY-NC-SA 4.0"),
    H2("📜 文化与演化"),
    B("肯特郡失去了它的 Kentish Plover，这个名字却留在所有语言里——地名性鸟名的典型「错位」案例"),
    B("对繁殖交换行为（incubation exchange）的长期研究发现夫妻「换班时的仪式互动」与后续关系稳定相关，使它成为鸟类行为学论文里出镜率很高的小鸻"),
 ]},
# ============ 7 白脸鸻 ============
{"cn": "白脸鸻", "sci": "Anarhynchus dealbatus", "en": "White-faced Plover",
 "order": "鸻形目", "family": "鸻科", "res": "🟢 留鸟 Resident",
 "iucn": "LC 无危", "cnlv": "三有", "gbif": "10986978",
 "xc": ("XC739121", "广东湛江，call · 雪鼬 · CC BY-NC-SA 4.0（中国境内录音）"),
 "sound": "与环颈鸻相似的短促哨音，量化的声学差异在研究中用于支持拆分",
 "blocks": [
    CO("首次记录：" + DATE + " · " + PLACE + "。"),
    H2("🐾 性格与行为"),
    B("行为与环颈鸻几乎一致：快速跑动-啄食、群栖、沙浴，受惊先急跑再起飞"),
    B("更依赖纯净开阔的沙滩——比环颈鸻更「挑」沙岸，华南的海滨浴场开发直接压缩它的繁殖地"),
    B("华南沿海留鸟：春天在开阔沙滩求偶营巢（沙地浅坑卵）；涨潮时常与环颈鸻、蒙古沙鸻同群挤在高潮线"),
    B("非繁殖季活动范围扩大，可南至东南亚海岸；部分个体全年居留广东、海南"),
    H2("🧬 分类考据"),
    H3("拉丁名词源"),
    B("dealbatus —— 拉丁语 dealbare「涂白、刷白」，指大片的白色脸——1870 年英国博物学家郇和（Robert Swinhoe）依厦门标本命名"),
    B("「白脸」非虚名：额至眼上宽白、颈环细弱、腿偏粉——与环颈鸻（眼先暗、颈环粗）并排看，整体「白得发亮」"),
    B("2008 年起基于羽色、裸部、鸣声与分布差异被普遍接受为独立种（Kennerley et al. 2008）；AviList v2025 采纳并移入 Anarhynchus"),
    H3("系统位置"),
    B("鸻形目 Charadriiformes › 鸻科 Charadriidae › 弯嘴鸻属 Anarhynchus"),
    B("与环颈鸻构成姊妹种对——一对在华南海岸共同生活的「刚分家的兄弟」"),
    H2("🌏 分布与生态"),
    B("分布格局独特：繁殖主体在华南沿海（福建以南至广西、海南，广东为全年居留核心区），非繁殖期南扩至中南半岛海岸"),
    B("全球成熟个体估计 2.5 万–25 万，趋势未知；历史上因难以和环颈鸻区分，长期「被并入统计」，近年靠公民科学数据（eBird）与建模（Wang et al. 2019）才摸清分布"),
    B("威胁集中在华南沙滩的旅游开发与海岸硬化——它几乎只住在沙滩上"),
    BM("https://www.gbif.org/species/10986978"),
    P("GBIF · Charadrius dealbatus · 全球出现记录（GBIF 主干仍用旧属名）"),
    H2("🎵 鸣声 / 鸣唱"),
    B("短促的 plover 式哨音，与环颈鸻相似；量化声谱差异正是拆分证据之一"),
    BM("https://xeno-canto.org/739121"),
    P("xeno-canto · XC739121 · " + "广东湛江 · call · 雪鼬 · CC BY-NC-SA 4.0（中国境内录音）"),
    H2("📜 文化与演化"),
    B("一个「三段式」的物种故事：1870 年在中国海岸被西方博物学家命名 → 20 世纪被并入环颈鸻而「消失」近百年 → 2008 年重新被承认为种；IUCN 2023 年首次以独立种评估为 LC"),
    B("中国 2023 年「三有」名录未以本名单列，实践中沿用原环颈鸻名录口径按三有保护管理（媒体与执法均如此表述）"),
 ]},
# ============ 8 蒙古沙鸻 ============
{"cn": "蒙古沙鸻", "sci": "Anarhynchus mongolus", "en": "Siberian Sand Plover",
 "order": "鸻形目", "family": "鸻科", "res": "🟣 旅鸟 Passage migrant",
 "iucn": "LC 无危", "cnlv": "三有", "gbif": "9722670",
 "xc": ("XC1101476", "江苏连云港兴庄河口，call · Bo Shunqi 薄顺奇 · CC BY-NC-SA 4.0"),
 "sound": "短促柔和的 chit-it / tru-it 哨音，比灰斑鸻单薄",
 "blocks": [
    CO("首次记录：" + DATE + " · " + PLACE + "。"),
    H2("🐾 性格与行为"),
    B("结小群在潮间带快速奔跑觅食，跑动节奏快于环颈鸻，常整群同向移动如「地毯式扫描」"),
    B("与铁嘴沙鸻（A. leschenaultii）形态接近：喙长、体型、跗蹠比例是经典识别组合——「沙鸻两兄弟」是水鸟识别课必考题"),
    B("警觉时先急跑、再贴水面低飞，伴随短促哨音；迁徙季在华南沿海成群过境，部分个体继续南下至东南亚与澳洲"),
    H2("🧬 分类考据"),
    H3("拉丁名词源"),
    B("mongolus —— Pallas 1776 年依「蒙古方向」的旅鸟标本命名；而它的繁殖主区其实在东西伯利亚山地苔原——名字里的「蒙古」是历史的误置"),
    B("⚠️ 重要拆分：原「Lesser Sand Plover（蒙古沙鸻复合体）」近年拆为两种——青藏高原繁殖的西藏沙鸻 A. atrifrons（Tibetan Sand Plover）与西伯利亚繁殖的 A. mongolus（Siberian Sand Plover）；AviList v2025 采纳拆分，中文名沿用郑光美「蒙古沙鸻」对应后者"),
    B("AviList 同时将其移入 Anarhynchus；旧记法 Charadrius mongolus；xeno-canto/GBIF 尚沿用旧名检索"),
    H3("系统位置"),
    B("鸻形目 Charadriiformes › 鸻科 Charadriidae › 弯嘴鸻属 Anarhynchus"),
    B("与铁嘴沙鸻 A. leschenaultii（Greater Sand Plover）构成另一组姊妹种——两对「沙鸻」各自独立演化出类似体型"),
    H2("🌏 分布与生态"),
    B("繁殖于西伯利亚中东部山地与苔原带；越冬自南亚经东南亚至澳洲"),
    B("在中国东部沿海为普遍旅鸟（春秋两个过境高峰），华南部分个体越冬；11 月初南沙记录属秋迁尾峰与早冬个体"),
    B("长距离迁徙者：东西伯利亚—澳洲单程上万公里，华南滩涂是它的重要补给站"),
    BM("https://www.gbif.org/species/9722670"),
    P("GBIF · Charadrius mongolus · 全球出现记录（GBIF 主干仍用旧属名）"),
    H2("🎵 鸣声 / 鸣唱"),
    B("短促柔和的 chit-it 哨音，群体起飞时此起彼伏"),
    BM("https://xeno-canto.org/1101476"),
    P("xeno-canto · XC1101476 · " + "江苏连云港兴庄河口 · call · Bo Shunqi 薄顺奇 · CC BY-NC-SA 4.0"),
    H2("📜 文化与演化"),
    B("「蒙古沙鸻」这个名字比它的现代分布大了一个纬度带——分类史上的命名错位往往比名字本身更耐读"),
    B("青藏—西伯利亚的种级拆分说明：外形几乎无差的两群鸟，可能已在繁殖隔离的路上走出很远——羽色保守而繁殖地分化，是鸻类的常见演化剧本"),
 ]},
# ============ 9 青脚鹬 ============
{"cn": "青脚鹬", "sci": "Tringa nebularia", "en": "Common Greenshank",
 "order": "鸻形目", "family": "鹬科", "res": "🔵 冬候鸟 Winter visitor",
 "iucn": "LC 无危", "cnlv": "三有", "gbif": "2481726",
 "xc": ("XC844717", "上海崇明东滩，call · Bo Shunqi 薄顺奇 · CC BY-NC-SA 4.0"),
 "sound": "响亮清亮的 tyue-tyue-tyue 三连哨，受惊起飞时是全滩涂最响的警报之一",
 "blocks": [
    CO("首次记录：" + DATE + " · " + PLACE + "。"),
    H2("🐾 性格与行为"),
    B("「大高个」灰鹬：腿长、颈长、喙灰绿而略上翘——那双灰绿色的脚就是名字"),
    B("觅食活跃：快步涉水、频繁变向，甚至小跑追捕小鱼和虾——比近亲红脚鹬好动得多"),
    B("受惊起飞时响亮的三连哨音，常把全滩的水鸟带上天；飞行时背部白色楔形斑从两侧上延（white wedge）是空中识别要点"),
    B("多单独或分散小群活动，与其他鹬混群时也保持间距、占据深水边缘"),
    H2("🧬 分类考据"),
    H3("拉丁名词源"),
    B("nebularia —— 拉丁语 nebula「雾」：Gunnerus 1767 年命名，一般认为指其灰雾般的羽色（一说是对北欧雾中湿地生境的联想）"),
    B("Tringa —— 亚里士多德笔下的一种涉禽名，林奈挪作鹬属"),
    B("中文名「青脚」与英文 Greenshank（绿胫）完全同构——中外命名者都盯住了那双灰绿色的腿"),
    H3("系统位置"),
    B("鸻形目 Charadriiformes › 鹬科 Scolopacidae › 鹬属 Tringa"),
    B("近缘种小青脚鹬（T. guttifer）是国家一级保护动物——识别时须注意区分：小青脚鹬喙较短厚、脚偏黄、胁纹密而体显壮"),
    H2("🌏 分布与生态"),
    B("繁殖于欧亚大陆北部泰加林带的沼泽湿地；越冬于非洲、南亚、东南亚至澳洲"),
    B("中国东部与华南沿海普遍越冬；南沙冬候鸟，冬春见于滩涂、鱼塘与河口浅水"),
    B("全球种群大（百万级估计），IUCN LC；泥滩开发是最普遍的长期威胁"),
    BM("https://www.gbif.org/species/2481726"),
    P("GBIF · Tringa nebularia · 全球出现记录"),
    H2("🎵 鸣声 / 鸣唱"),
    B("响亮清亮的三连哨 tyue-tyue-tyue；越冬滩涂上猛禽掠过时，往往是青脚鹬先叫、全滩响应"),
    BM("https://xeno-canto.org/844717"),
    P("xeno-canto · XC844717 · " + "上海崇明东滩 · call · Bo Shunqi 薄顺奇 · CC BY-NC-SA 4.0"),
    H2("📜 文化与演化"),
    B("在华南冬季滩涂上，青脚鹬的高声警报常给观鸟人「报信」——鹗或黑翅鸢掠过时，先叫的往往是它"),
    B("鹬属在鹬科里演化出「腿长梯度」：从矶鹬的小短腿到青脚鹬的长腿，对应的正是各自占据的水深生态位——它是这一梯度靠「深水端」的代表"),
 ]},
# ============ 10 黑翅鸢 ============
{"cn": "黑翅鸢", "sci": "Elanus caeruleus", "en": "Black-winged Kite",
 "order": "鹰形目", "family": "鹰科", "res": "🟢 留鸟 Resident",
 "iucn": "LC 无危", "cnlv": "国家二级", "gbif": "2480372",
 "xc": ("XC632274", "中国台湾彰化芳苑，call · Jerome Chie-Jen Ko · CC BY-NC-SA 4.0"),
 "sound": "细短的高音哨声 / 尖叫，平时很少鸣叫",
 "blocks": [
    CO("首次记录：" + DATE + " · " + PLACE + "。"),
    H2("🐾 性格与行为"),
    B("标志行为是迎风定点悬停（wind-hovering）：锁定草丛鼠类后收翼俯冲——与红隼异曲同工，但更依赖微风中的低空定点"),
    B("白天全天活动（多数鹰类只在晨昏），因为成鸟红色虹膜+强光缩瞳的配置专为白昼强光狩猎准备"),
    B("领空巡飞时白身配黑翼斑，「背黑锅的白鸢」一眼可辨；常一雄一雌共域"),
    B("数量随鼠类丰度大幅波动（游荡性 nomadic），一地忽多忽少是常态"),
    B("近 20 年在中国显著北扩/东扩：从传统华南留鸟扩展到长江流域乃至华北开阔农田——土地利用与气候变化最直观的猛禽指标"),
    H2("🧬 分类考据"),
    H3("拉丁名词源"),
    B("Elanus —— 古希腊语「鸢」（纸鸢/风筝同源意象）；黑翅鸢属全球约 5 种，暖温带各大洲各配一种白色系鸢——同一身体方案的世界性平行分布"),
    B("caeruleus —— 拉丁语「天蓝色的」：有点冤，它并不蓝，1789 年 Desfontaines 命名时或取其翅上覆羽的蓝灰光泽"),
    B("曾用名 Elanus melanopterus（「黑翅的」）更名副其实，但在命名优先律下 caeruleus 胜出"),
    H3("系统位置"),
    B("鹰形目 Accipitriformes › 鹰科 Accipitridae › 黑翅鸢亚科 Elaninae"),
    B("鸢里最「白」的一支：与俗称「老鹰」的真鸢（Milvus，黑耳鸢等）关系较远，过去曾被视为独立亚科甚至独立科"),
    H2("🌏 分布与生态"),
    B("泛热带分布：非洲、南亚、东南亚、澳洲及欧洲西南局部"),
    B("在中国传统上是华南留鸟，2000 年代起持续北扩；栖息开阔农田、草地、湿地边缘——平原上空的白鸢越来越常见"),
    B("主食田鼠等小型啮齿类，对农田生态系统的鼠害控制有实际价值"),
    BM("https://www.gbif.org/species/2480372"),
    P("GBIF · Elanus caeruleus · 全球出现记录"),
    H2("🎵 鸣声 / 鸣唱"),
    B("细短的高音哨声，平时极安静；繁殖期巢区较常发出"),
    BM("https://xeno-canto.org/632274"),
    P("xeno-canto · XC632274 · " + "中国台湾彰化芳苑 · call · Jerome Chie-Jen Ko · CC BY-NC-SA 4.0"),
    H2("📜 文化与演化"),
    B("《诗经·大雅》「鸢飞戾天，鱼跃于渊」的「鸢」泛指鸢类——黑翅鸢这只白鸢正是现代中国天空里最常见、最容易被认成「白鹰」的鸢"),
    B("它的北扩轨迹与中国农耕区开阔化、变暖同步，被猛禽研究者称为「读气候的鸢」"),
 ]},
# ============ 11 蚁䴕 ============
{"cn": "蚁䴕", "sci": "Jynx torquilla", "en": "Eurasian Wryneck",
 "order": "䴕形目", "family": "啄木鸟科", "res": "🔵 冬候鸟 Winter visitor",
 "iucn": "LC 无危", "cnlv": "三有", "gbif": "8012314",
 "xc": ("XC1099016", "香港米埔，call（2 月越冬个体）· Bo Shunqi 薄顺奇 · CC BY-NC-SA 4.0"),
 "sound": "犬吠般的 kwee-kwee-kwee 串音（繁殖期），越冬期偶发短音",
 "blocks": [
    CO("首次记录：" + DATE + " · " + PLACE + "。"),
    H2("🐾 性格与行为"),
    B("不啄木的啄木鸟：主食蚂蚁与蚁卵，用带倒刺黏液的长舌伸入蚁巢舔食，一顿可吃上千只"),
    B("名字来自「歪脖」：受惊时头部大幅扭转、颈部羽毛蓬起、瞳孔缩小，模仿蛇头威慑（snake-mimicry）——欧洲民间就叫它 snakebird"),
    B("保护色一流：灰褐色波浪纹贴在树干上几乎隐形；遇险倾向「贴树定住」而非起飞"),
    B("常在地面觅食蚂蚁（啄木鸟类里少见的地栖倾向），行走笨拙"),
    B("利用啄木鸟旧洞营巢，自己不凿洞；是欧洲唯一全部迁徙的啄木鸟"),
    H2("🧬 分类考据"),
    H3("拉丁名词源"),
    B("Jynx —— 古希腊语 iynx：希腊神话中被爱神阿佛洛狄忒变作鸟的少女 Iynx；古典时代把蚁䴕绑在轮盘上旋转念咒施「爱情魔法」，英语 jinx（厄运/魔咒）即源于此鸟"),
    B("torquilla —— 拉丁语 torquere「扭转」：歪脖行为"),
    B("「蚁䴕」：食蚁的䴕形目鸟；2023 三有名录写法作「蚁鴷」（鴷/䴕 异体）"),
    H3("系统位置"),
    B("䴕形目 Piciformes › 啄木鸟科 Picidae › 蚁䴕属 Jynx（全球仅 2 种，另一种红喉蚁䴕 J. ruficollis 在非洲）"),
    B("啄木鸟科里最偏离「啄木」生态位的成员：不凿树、主要地栖、食性特化到蚁"),
    H2("🌏 分布与生态"),
    B("繁殖于欧亚温带开阔林地、果园与疏林（西欧到中国东北、华北山地；北京山区有繁殖）"),
    B("全部种群迁徙，越冬于非洲萨赫勒、南亚和华南"),
    B("在广州为冬候鸟，冬春见于公园疏林、果园——贴树干静立时极难发现，常被当作「树皮」走漏"),
    BM("https://www.gbif.org/species/8012314"),
    P("GBIF · Jynx torquilla · 全球出现记录"),
    H2("🎵 鸣声 / 鸣唱"),
    B("犬吠般的 kwee-kwee-kwee 串音（繁殖期广告鸣唱）；越冬期偶发单音"),
    BM("https://xeno-canto.org/1099016"),
    P("xeno-canto · XC1099016 · " + "香港米埔 · call（2 月越冬个体）· Bo Shunqi 薄顺奇 · CC BY-NC-SA 4.0"),
    H2("📜 文化与演化"),
    B("蚁䴕的「iynx 轮盘」：古希腊人把它缚在四辐轮上旋转念咒以求「拴住」意中人——品达与忒奥克里托斯的诗里都有记载；这个仪式之著名，以至于「iynx」后来泛指一切咒术轮盘"),
    B("英语 jinx（厄运、魔咒）从这只小鸟一路演化为现代口语——一只会歪脖子的鸟，在人类语言里活了 2,500 年"),
    B("演化上，蚁食特化让它在「啄木」家族里另辟生态位：不与啄木竞争树洞里的虫，改吃地面上的蚁——嘴硬（保留凿洞旧结构）舌软（舌器极端延长）的组合是活化石级的过渡形态"),
 ]},
# ============ 12 栗耳鹀 ============
{"cn": "栗耳鹀", "sci": "Emberiza fucata", "en": "Chestnut-eared Bunting",
 "order": "雀形目", "family": "鹀科", "res": "🔵 冬候鸟 Winter visitor",
 "iucn": "LC 无危", "cnlv": "三有", "gbif": "2491548",
 "xc": ("XC995396", "上海崇明东滩，song · Bo Shunqi 薄顺奇 · CC BY-NC-SA 4.0"),
 "sound": "联络为尖细 tsip；繁殖期雄鸟唱简单短曲——干涩的加速颤鸣后一记收尾",
 "blocks": [
    CO("首次记录：" + DATE + " · " + PLACE + "。"),
    H2("🐾 性格与行为"),
    B("半隐蔽型鹀：常在草丛、芦苇、农田边缘地面蹦行觅食（草籽+昆虫），受惊时低空短窜入草丛——「见首不见尾」"),
    B("头侧栗色耳羽是名字来源；胸腹的鳞状黑纹（新月形点斑串）是与小鹀、田鹀区分的关键识别点"),
    B("迁徙与越冬时常混在小鹀等群中；在华南为数量不多的冬候鸟，多单独或成对出现"),
    B("繁殖期雄鸟站上草顶或灌丛顶端鸣唱——鹀类里相对显眼的一位"),
    H2("🧬 分类考据"),
    H3("拉丁名词源"),
    B("Emberiza —— 古拉丁语对一类雀鸟的称谓（词源模糊，可能是拟声），林奈 1758 年建鹀属"),
    B("fucata —— 拉丁语 fucare「涂胭脂、上色」：Pallas 1776 年命名，指栗色耳羽像涂了红妆"),
    B("「鹀」为形声字（从鸟、巫声），泛称喙圆锥状的这一类雀——中文一名覆盖了旧大陆鹀与新大陆「鹀」两大科（见系统位置）"),
    H3("系统位置"),
    B("雀形目 Passeriformes › 鹀科 Emberizidae › 鹀属 Emberiza"),
    B("⚠️ AviList 口径：旧大陆鹀类保留为鹀科 Emberizidae；新大陆雀鹀类已拆为雀鹀科 Passerellidae——凭中文名「鹀」定科会出错，学名才是桥梁"),
    H2("🌏 分布与生态"),
    B("繁殖于东西伯利亚至堪察加、日本北部及中国东北的山地草甸、灌丛与湿地边缘"),
    B("越冬于华南、台湾及东南亚北部；在广州为偏少见的冬候鸟，见于开阔草地、田缘与苇丛"),
    B("日本列岛是其繁殖与越冬的重要区域（日文俗名カシラダカ），竹林边缘常见"),
    BM("https://www.gbif.org/species/2491548"),
    P("GBIF · Emberiza fucata · 全球出现记录"),
    H2("🎵 鸣声 / 鸣唱"),
    B("联络音尖细 tsip；繁殖期鸣唱为干涩的加速颤鸣加一记短促收尾，从草顶或电线发出"),
    BM("https://xeno-canto.org/995396"),
    P("xeno-canto · XC995396 · " + "上海崇明东滩 · song · Bo Shunqi 薄顺奇 · CC BY-NC-SA 4.0"),
    H2("📜 文化与演化"),
    B("鹀类在中国诗文与古画中存在感普遍很弱（黄胸鹀除外）——栗耳鹀几乎是纯粹的「分类学之鸟」：所有故事都写在名字与分布里"),
    B("鳞状胸纹在鹀属内多次独立演化，是「纹样模因」沿属内扩散的常见例子——也是野外识别最可靠的尺子"),
 ]},
# ============ 13 黄胸鹀 ============
{"cn": "黄胸鹀", "sci": "Emberiza aureola", "en": "Yellow-breasted Bunting",
 "order": "雀形目", "family": "鹀科", "res": "🟣 旅鸟 Passage migrant",
 "iucn": "CR 极危", "cnlv": "国家一级", "gbif": "2491518",
 "xc": ("XC836112", "中国，call / flight call · Ray Tsu 诸仁 · CC BY-NC-SA 4.0"),
 "sound": "短促的 zik；群飞时细碎接触音连成一片",
 "blocks": [
    CO("首次记录：" + DATE + " · " + PLACE + "。IUCN 极危（CR）· 国家一级保护动物。"),
    H2("🐾 性格与行为"),
    B("繁殖羽雄鸟色块鲜明（金胸+栗头+黑面罩）；冬季在华南看到的常是雌鸟与幼鸟——通体褐色、仅胸腹残留黄色"),
    B("迁徙季高度集群，停歇于稻田、芦苇荡与草滩，喜在禾草穗顶啄食草籽——「糯谷扬花它就来」正是「禾花雀」之名的由来"),
    B("曾是东亚数量最大的迁徙雀鸟之一，历史迁徙群可达数万只；如今即使在传统停歇地也只见到零散小群"),
    B("越冬主力在南亚与东南亚，华南同时是迁徙通道和少量个体的越冬区"),
    H2("🧬 分类考据"),
    H3("拉丁名词源"),
    B("aureola —— 拉丁语 aureolus「小小的金色」——「金色小鸟」直指雄鸟的金黄色胸腹"),
    B("Emberiza —— 林奈建鹀属（词源为古拉丁语雀鸟称谓，见栗耳鹀条）"),
    B("岭南俗名「禾花雀」：晚稻扬花灌浆的深秋正值其南迁高峰——名字把物候和鸟绑在了一起"),
    H3("系统位置"),
    B("雀形目 Passeriformes › 鹀科 Emberizidae › 鹀属 Emberiza——鹀属核心成员，分类稳定；它的濒危完全来自人类捕食"),
    H2("🌏 分布与生态"),
    B("繁殖于欧亚泰加林南缘至东北平原的湿草甸与灌丛（芬兰至东西伯利亚、中国东北）"),
    B("越冬于南亚次大陆与东南亚，华南是关键迁徙通道"),
    B("种群轨迹触目惊心：IUCN 2004 年评为 LC，2013 年连跳至 EN，2017 年升为 CR 极危——研究估计 1980–2013 年全球减少 84–94%"),
    B("迁徙通道上的围网盗捕（以食用为目的）是主因；农田集约化造成的停歇地缩减是叠加压力"),
    BM("https://www.gbif.org/species/2491518"),
    P("GBIF · Emberiza aureola · 全球出现记录"),
    H2("🎵 鸣声 / 鸣唱"),
    B("短促的 zik；繁殖期雄鸟唱干涩的快速颤鸣，从草顶或电线发出"),
    BM("https://xeno-canto.org/836112"),
    P("xeno-canto · XC836112 · " + "中国 · call / flight call · Ray Tsu 诸仁 · CC BY-NC-SA 4.0"),
    H2("📜 文化与演化"),
    B("「禾花雀」之殇：珠三角曾把黄胸鹀当作「天上人参」进补野味，迁徙季大规模围网捕食持续多年；媒体曝光与执法介入后仍未绝迹，直到 2017 年 IUCN 升为 CR、2021 年列入国家一级保护，盗捕才真正收敛"),
    B("它已成为全球保育教科书的标准案例：一个种群以亿计的常见鸟，可以在十几年里被吃成极危——「常见」从来不是安全的保证"),
    B("如今华南每年秋迁见到的小群黄胸鹀，都是这场崩塌的幸存者——南沙的芦苇荡对它们是真正意义上的生命补给站"),
 ]},
]

IMGS = json.load(open("/tmp/nansha/final_images.json"))

def main():
    out = {}
    for sp in SPECIES:
        cn = sp["cn"]
        q = call("POST", f"/data_sources/{DS}/query",
                 {"filter": {"property": "中文名", "title": {"equals": cn}}})
        if q["results"]:
            pid = q["results"][0]["id"]
            log(cn, "exists", pid, "→ 检查正文")
        else:
            props = {
                "中文名": {"title": T(cn)}, "学名": {"rich_text": T(sp["sci"])},
                "Common name": {"rich_text": T(sp["en"])},
                "数据来源": {"rich_text": T("AviList v2025")},
                "目": {"select": {"name": sp["order"]}}, "科": {"select": {"name": sp["family"]}},
                "居留型": {"select": {"name": sp["res"]}},
                "IUCN 等级": {"select": {"name": sp["iucn"]}},
                "中国保护等级": {"select": {"name": sp["cnlv"]}},
                "首次地点": {"rich_text": T(PLACE)}, "首次日期": {"date": {"start": DATE}},
            }
            pid = call("POST", "/pages", {"parent": {"database_id": DBID}, "properties": props})["id"]
            log(cn, "created", pid)
        out[cn] = pid

        kids = call("GET", f"/blocks/{pid}/children?page_size=100")["results"]
        if kids:
            log("  body exists (" + str(len(kids)) + " blocks), skip")
            continue

        # 1) 实拍照 = 第一块
        im = IMGS[cn]
        fu = upload_file(im["img"], cn + ".jpg")
        call("PATCH", f"/blocks/{pid}/children", {"children": [img_block(fu, im["img_cap"])]})
        log("  首图已上传")
        # 2) 正文其余块（📜 为最后一章，博物画随后追加在末尾即落在 📜 内）
        blocks = sp["blocks"]
        for i in range(0, len(blocks), 90):
            call("PATCH", f"/blocks/{pid}/children", {"children": blocks[i:i+90]})
        if im.get("art") and im.get("art_cap"):
            fu2 = upload_file(im["art"], cn + "_art.jpg")
            call("PATCH", f"/blocks/{pid}/children", {"children": [img_block(fu2, im["art_cap"])]})
            log("  博物画已追加")
        log("  正文完成")
        time.sleep(0.4)
    json.dump(out, open("/tmp/nansha/pages.json", "w"), ensure_ascii=False)
    log("ALL DONE")

if __name__ == "__main__":
    main()
