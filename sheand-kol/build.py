#!/usr/bin/env python3
"""
季度養膚方案頁產生器

改資料只要動下面的 TREATMENTS 與 PLANS，然後執行：
    python3 build.py
會產生 plan-01.html 與 plan-02.html。

共用療程只寫一次，兩頁自動同步。
"""
import html, pathlib

# ═══════════════════════════════════════════════════════
#  療程資料 —— 共用，改一次兩頁都會更新
#  空字串會顯示成待填插槽
# ═══════════════════════════════════════════════════════
#   principle 主要原理 / effect 主要功效
#   benefits  條列補充（可留空）/ duration 治療時間 / recovery 恢復期
#   pain      痛感程度 1–3（0 = 未填）, pain_label 文字
TREATMENTS = {
    "water": dict(
        name="基礎水光", en="Skin Booster", cat="保濕・亮膚",
        principle="將透明質酸等營養物質注入皮膚",
        principle_points=[
            "使用儀器自動化施打，有的機型搭配負壓吸附技術，"
            "能將皮膚輕輕吸起後，多個微針同時均勻注射。",
            "速度快、痛感低、注射深度可調整，施打劑量更精準，修復期短。"],
        effect="深層保濕、提升皮膚彈性",
        benefits=[],
        duration="15分鐘",
        recovery="輕微(細小針孔及瘀青)",
        pain=1, pain_label="輕微",
    ),
    "pico": dict(
        name="皮秒蜂巢雷射", en="Picosecond Laser", cat="膚色・毛孔",
        principle="利用超短脈衝雷射擊碎色素",
        effect="淡化色斑、細紋、改善膚色",
        benefits=[],
        duration="15-30分鐘",
        recovery="輕微（例如短暫紅腫）",
        pain=1, pain_label="輕微",
    ),
    "dermapen": dict(
        name="Dermapen", en="Microneedling", cat="膚質・紋理",
        principle="以微針刺激膠原與彈性蛋白再生",
        effect="淡化痘疤與細紋、改善毛孔",
        benefits=[],
        duration="15分鐘", recovery="",
        pain=1, pain_label="輕微",
    ),
    "hydra": dict(
        name="海飛秀", en="HydraFacial", cat="清潔・導入",
        principle="30分鐘完成深層清潔與精華導入",
        effect="深層清潔毛孔、補水與提亮膚色",
        benefits=[],
        duration="30分鐘", recovery="沒有", pain=0, pain_label="無",
        steps=[("第一步", "溫和清潔去角質"),
               ("第二步", "深層吸附髒污與粉刺"),
               ("第三步", "精華導入與肌膚修護")],
        # ── 適合族群：暫時移除。把下面 suits 取消註解即可還原 ──
        suits_title="誰最適合做海飛秀？六大族群一次了解",
        suits=[],
        # suits=[("油性肌膚",   "幫助控油、清除粉刺與淨化毛孔"),
        #        ("乾性肌膚",   "深層補水、提升肌膚含水量與潤澤感"),
        #        ("混合性肌膚", "調理油水平衡，改善局部出油現象"),
        #        ("青春痘肌",   "減少粉刺、阻塞，舒緩發炎反應"),
        #        ("敏感肌膚",   "搭配舒緩精華，穩定膚況、降低刺激感"),
        #        ("暗沉膚色",   "均勻膚色、提亮整體肌膚光澤")],
    ),
    "hifu_eye": dict(
        name="海芙音波眼周保養", en="HIFU · Eye Area", cat="緊緻・眼周",
        principle="", effect="", benefits=[],
        duration="", recovery="", pain=0, pain_label="",
    ),
}

# ═══════════════════════════════════════════════════════
#  方案 —— 一個方案一頁
# ═══════════════════════════════════════════════════════
PLANS = [
    dict(
        file="plan-01.html", no="01", kind="package",
        desc="蒔恩美學診所養膚體驗套餐內容與各項療程說明。",
        title="養膚體驗套餐",
        sub="一季的養膚體驗",
        items=["water", "pico", "dermapen", "hydra"],
        positioning="我們認為，養好一個肌膚是讓自己變美的關鍵，當你的皮膚養好，後續的各種療程才能更好。\n"
                     "用這養膚套餐，找到你自己最喜歡的養膚模式。",
    ),
    dict(
        file="plan-02.html", no="02", kind="package",
        desc="蒔恩美學診所養膚體驗套餐內容與各項療程說明。",
        title="養膚體驗套餐",
        sub="一季的養膚體驗",
        items=["water", "pico", "dermapen", "hydra", "hifu_eye"],
        positioning="我們認為，養好一個肌膚是讓自己變美的關鍵，當你的皮膚養好，後續的各種療程才能更好。\n"
                     "用這養膚套餐，找到你自己最喜歡的養膚模式。",
    ),
    # ── 第一波合作用：不揭露套餐結構，讓 KOL 自己挑 ──
    dict(
        file="experience.html", no="", kind="experience",
        desc="蒔恩美學診所養膚體驗：從皮膚的更新週期出發，說明各項療程的作用與適合處理的狀況。",
        title="養膚體驗",
        sub="",
        items=["water", "pico", "dermapen", "hydra"],
        positioning="",
        intro_text="",   # 什麼是養膚：2–3 段
    ),
]

BRAND = dict(intro="", address="台北市大安區 ○○路 ○ 號", phone="0987167852")


# ═══════════════════════════════════════════════════════
#  版面上的固定文字 —— 區塊標題、說明句、欄位標題
# ═══════════════════════════════════════════════════════
LABELS = dict(
    intro_eyebrow="Introduction",
    intro_head="關於蒔恩",
    cultivation_eyebrow="Skin Cultivation",
    cultivation_head="什麼是養膚",
    pkg_eyebrow="Package",
    pkg_lede_tail="。以下項目各一次，由醫師依面診結果安排順序與間隔。",
    tx_eyebrow_pkg="Treatments",
    tx_head_pkg="各項療程能做到什麼",
    tx_eyebrow_exp="Menu",
    tx_head_exp="可以體驗的項目",
    tx_lede="以下說明每個項目的作用層次與適合處理的狀況。"
            "實際適用性、次數與間隔，均須經醫師面診評估後決定。",
    space_eyebrow="The Space",
    space_head="診所空間",
    space_lede="微水泥的牆、洞石的地、淺色木質與弧形的線條。我們刻意讓空間安靜下來。",
    f_principle="主要原理",
    f_effect="主要功效",
    f_steps="療程步驟",
    f_info="療程資訊",
    f_duration="治療時間",
    f_recovery="恢復期",
    f_pain="痛感程度",
)

# ═══════════════════════════════════════════════════════
#  品牌故事 —— 皮膚更新週期
# ═══════════════════════════════════════════════════════
STORY_LEAD = "品牌以「皮膚更新週期」作為核心敘事。"
STORY = [
    dict(no="01", zh="破壞", en="Disrupt",
         body="以可控能量或微創方式給予刺激，啟動皮膚修復訊號。"
              "此階段常見泛紅、緊繃或輕微腫脹，屬預期中的反應。"),
    dict(no="02", zh="修復", en="Repair",
         body="發炎反應逐步消退，纖維細胞開始活化、新的膠原蛋白進入生成階段。"
              "這段時間的保濕與防曬，決定了修復的品質。"),
    dict(no="03", zh="新生", en="Renew",
         body="角質層完成一輪更新，膚況趨於穩定。"
              "此時的狀態，才是這次療程真正的落點；接著進入下一個循環。"),
]

# ═══════════════════════════════════════════════════════
#  診所空間 —— 檔案放進 images/，找不到會退回漸層
# ═══════════════════════════════════════════════════════
SPACE = [
    dict(src="images/space-1.jpg", label="諮詢區"),
    dict(src="images/space-2.jpg", label="櫃檯"),
    dict(src="images/space-3.jpg", label="療程室"),
    dict(src="images/space-4.jpg", label="接待區"),
    dict(src="images/space-5.jpg", label="大門"),
]

# ═══════════════════════════════════════════════════════


# ═══════════════════════════════════════════════════════
#  內容來源
#  1. 填了 SHEET_CSV_URL → 抓 Google Sheet（同事改完自動生效）
#  2. 否則有 content.csv → 用本機檔案
#  3. 都沒有 → 用上面寫死的內容
#  抓不到線上資料時會自動退回 2 或 3，不會產生空白頁面。
# ═══════════════════════════════════════════════════════
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRRyqLNxt_Y1e8or4X5loLdBDYl_JFexOa02efT5-Gtaf9xmZ0KIphlNajkZsrnOztGaTplel1dknBG/pub?output=csv"

SEP = "｜"              # 分段與條列的分隔符號

def _split(v):
    return [x.strip() for x in v.split(SEP) if x.strip()]

def _apply(rows):
    """把 CSV 的內容套回上面的資料結構"""
    plans = {p["file"]: p for p in PLANS}
    n = 0
    for r in rows:
        key = (r.get("key") or "").strip()
        val = (r.get("內容") or "").strip()
        if not key:
            continue
        part = key.split(".")
        try:
            if part[0] == "brand":
                BRAND[part[1]] = val.replace(SEP, "\n")
            elif part[0] == "story":
                if part[1] == "lead":
                    globals()["STORY_LEAD"] = val
                else:
                    STORY[int(part[1]) - 1][part[2]] = val
            elif part[0] == "space":
                SPACE[int(part[1]) - 1]["label"] = val
            elif part[0] == "tx":
                t, f = TREATMENTS[part[1]], part[2]
                if f in ("principle_points", "benefits"):
                    t[f] = _split(val)
                elif f == "steps":
                    t[f] = [tuple(x.split(":", 1)) for x in _split(val)
                            if ":" in x]
                elif f == "pain":
                    t[f] = int(val or 0)
                else:
                    t[f] = val
            elif part[0] == "label":
                LABELS[part[1]] = val
            elif part[0] == "page":
                # 檔名含 "."（experience.html），要取中間全部、欄位取最後一段
                fname, field = ".".join(part[1:-1]), part[-1]
                pl = plans.get(fname)
                if pl is None:
                    print(f"  ⚠ 找不到頁面 {fname}，略過 {key}")
                    continue
                pl[field] = val.replace(SEP, "\n")
            else:
                continue
            n += 1
        except (KeyError, IndexError, ValueError) as e:
            print(f"  ⚠ 略過 {key}：{e}")
    return n

def load_content():
    import csv, io
    src = None
    if SHEET_CSV_URL:
        try:
            import urllib.request
            with urllib.request.urlopen(SHEET_CSV_URL, timeout=15) as r:
                src = r.read().decode("utf-8-sig")
            print("  內容來源：Google Sheet")
        except Exception as e:
            print(f"  ⚠ 抓不到 Google Sheet（{e}），改用本機內容")
    if src is None:
        f = pathlib.Path(__file__).parent / "content.csv"
        if f.exists():
            src = f.read_text(encoding="utf-8-sig")
            print("  內容來源：content.csv")
        else:
            print("  內容來源：build.py 內建")
            return 0
    return _apply(list(csv.DictReader(io.StringIO(src))))


def slot(label):
    return f'<div class="slot">▸ <b>待填</b>　{html.escape(label)}</div>'

def text_or_slot(value, label):
    return f"<p>{html.escape(value)}</p>" if value else slot(label)

def list_or_slot(items, label):
    if not items:
        return slot(label)
    lis = "".join(f"<li>{html.escape(i)}</li>" for i in items)
    return f'<ul class="bul">{lis}</ul>'

def spec_cell(term, value):
    v = html.escape(value) if value else '<span class="tbd">待填</span>'
    return f"<div><dt>{term}</dt><dd>{v}</dd></div>"

def paras(text, label):
    """多段文字；空值顯示插槽"""
    if not text:
        return slot(label)
    return "".join(f"<p>{html.escape(p)}</p>"
                   for p in text.split("\n") if p.strip())

def pain_meter(level, label):
    if not label:                  # 沒填標籤才是待填；level=0 代表「無」
        return '<dd><span class="tbd">待填</span></dd>'
    dots = "".join(
        f'<i class="{"on" if n <= level else ""}"></i>' for n in range(1, 4))
    return (f'<dd class="pain"><span class="dots">{dots}</span>'
            f'{html.escape(label)}</dd>')

def steps_html(steps):
    L = LABELS
    if not steps:
        return ""
    items = "".join(
        f'<li><span class="sn">{html.escape(n)}</span>'
        f'<span class="sd">{html.escape(t)}</span></li>' for n, t in steps)
    return (f'<div class="field"><h4>{L["f_steps"]}</h4>'
            f'<ol class="steps">{items}</ol></div>')

def suits_html(title, rows):
    if not rows:
        return ""
    trs = "".join(f"<tr><th>{html.escape(a)}</th><td>{html.escape(b)}</td></tr>"
                  for a, b in rows)
    cap = f'<p class="suits-t">{html.escape(title)}</p>' if title else ""
    return ('<div class="field"><h4>適合族群</h4>'
            f'{cap}<table class="suits"><tbody>{trs}</tbody></table></div>')

def treatment_block(key, only_in_this_plan=False):
    L = LABELS
    t = TREATMENTS[key]
    tag = ('　<span class="only">本方案限定</span>' if only_in_this_plan else "")
    extra = list_or_slot(t["benefits"], "") if t["benefits"] else ""
    pextra = (list_or_slot(t["principle_points"], "")
              if t.get("principle_points") else "")
    return f"""
    <article class="tx">
      <div>
        <h3>{html.escape(t['name'])}</h3>
        <div class="en">{html.escape(t['en'])}</div>
        <div class="cat">{html.escape(t['cat'])}{tag}</div>
      </div>
      <div>
        <div class="field"><h4>{L['f_principle']}</h4>
          {paras(t['principle'], f"{t['name']}：主要原理")}{pextra}</div>
        <div class="field"><h4>{L['f_effect']}</h4>
          {paras(t['effect'], f"{t['name']}：主要功效")}{extra}</div>
        {steps_html(t.get('steps'))}
        {suits_html(t.get('suits_title'), t.get('suits'))}
        <div class="field"><h4>{L['f_info']}</h4>
          <dl class="spec">
            {spec_cell(LABELS['f_duration'], t['duration'])}
            {spec_cell(LABELS['f_recovery'], t['recovery'])}
            <div><dt>{L['f_pain']}</dt>{pain_meter(t['pain'], t['pain_label'])}</div>
          </dl></div>
      </div>
    </article>"""

def logo_svg(name):
    f = pathlib.Path(__file__).parent / "images" / name
    return f.read_text(encoding="utf-8") if f.exists() else ""

def contact_line():
    parts = [BRAND.get("address", ""), BRAND.get("phone", "")]
    return "　・　".join(html.escape(p) for p in parts if p)

def story_html():
    cards = "".join(f"""
      <article class="stage">
        <p class="sno">{s['no']}</p>
        <h3>{html.escape(s['zh'])}<span>{html.escape(s['en'])}</span></h3>
        <p class="sbody">{html.escape(s['body'])}</p>
      </article>""" for s in STORY)
    return f'<div class="stages">{cards}\n    </div>'

def embed(path, max_w=1100, quality=82):
    """壓縮後轉成 data URI，讓 HTML 可單獨帶著走（不依賴 images/ 資料夾）"""
    f = pathlib.Path(__file__).parent / path
    if not f.exists():
        return None
    import io, base64
    try:
        from PIL import Image
        im = Image.open(f).convert("RGB")
        if im.width > max_w:
            im = im.resize((max_w, round(im.height * max_w / im.width)),
                           Image.LANCZOS)
        buf = io.BytesIO()
        im.save(buf, "JPEG", quality=quality, optimize=True, progressive=True)
        data = buf.getvalue()
    except ImportError:
        data = f.read_bytes()
    return "data:image/jpeg;base64," + base64.b64encode(data).decode()

def space_html():
    cells = ""
    for p in SPACE:
        uri = embed(p["src"])
        if uri:
            cells += (f'\n      <figure class="sp">'
                      f'<img src="{uri}" alt="蒔恩美學診所{html.escape(p["label"])}">'
                      f'<figcaption>{html.escape(p["label"])}</figcaption></figure>')
        else:
            cells += (f'\n      <figure class="sp empty">'
                      f'<figcaption>{html.escape(p["label"])}</figcaption></figure>')
    return f'<div class="gal">{cells}\n    </div>'

def package_section(plan, shared):
    """套餐頁專用：列出方案內容"""
    li = "".join(
        f'<li><span class="dot"></span>{html.escape(TREATMENTS[k]["name"])}'
        f'<em>×1</em></li>' for k in plan["items"])
    return f'''<section class="sec on-white"><div class="wrap">
  <div class="eyebrow">{html.escape(LABELS["pkg_eyebrow"])}</div>
  <h2 class="h2">{html.escape(plan["title"])}</h2>
  <p class="lede">{html.escape(plan["sub"] + LABELS["pkg_lede_tail"])}</p>
  <ul class="items">{li}</ul>
  <div style="margin-top:26px;max-width:620px">{paras(plan["positioning"], "方案定位一句話／適合誰")}</div>
</div></section>

'''

def pick_section(plan):
    """體驗頁專用：不揭露套餐結構，改為邀請挑選"""
    return f'''<section class="sec on-white"><div class="wrap">
  <div class="eyebrow">{html.escape(LABELS["cultivation_eyebrow"])}</div>
  <h2 class="h2">{html.escape(LABELS["cultivation_head"])}</h2>
  <div style="max-width:40em">{paras(plan.get("intro_text", ""), "養膚概念說明 2–3 段：為什麼是規律而不是單次")}</div>
</div></section>

'''

def build(plan):
    shared = {k for p in PLANS for k in p["items"] if
              sum(k in q["items"] for q in PLANS) == len(PLANS)}
    is_pkg = plan.get("kind", "package") == "package"

    blocks = "".join(
        treatment_block(k, only_in_this_plan=(is_pkg and k not in shared))
        for k in plan["items"])

    return TEMPLATE.format(
        title=html.escape(plan["title"]),
        head_desc=html.escape(plan.get("desc", "")),
        tx_eyebrow=html.escape(LABELS["tx_eyebrow_pkg" if is_pkg else "tx_eyebrow_exp"]),
        tx_head=html.escape(LABELS["tx_head_pkg" if is_pkg else "tx_head_exp"]),
        L_intro_eyebrow=html.escape(LABELS["intro_eyebrow"]),
        L_intro_head=html.escape(LABELS["intro_head"]),
        L_tx_lede=html.escape(LABELS["tx_lede"]),
        L_space_eyebrow=html.escape(LABELS["space_eyebrow"]),
        L_space_head=html.escape(LABELS["space_head"]),
        L_space_lede=html.escape(LABELS["space_lede"]),
        main_section=package_section(plan, shared) if is_pkg else pick_section(plan),
        intro=paras(BRAND["intro"], "品牌簡介 2–3 段"),
        contact=contact_line(),
        logo=logo_svg("logo-primary.svg"),
        logo_end=logo_svg("logo-primary.svg"),
        blocks=blocks,
        story_lead=html.escape(STORY_LEAD),
        stages=story_html(),
        gallery=space_html(),
    )

TEMPLATE = """<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="robots" content="noindex,nofollow,noarchive">
<meta name="googlebot" content="noindex,nofollow">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}｜蒔恩美學診所 SHE AND</title>
<meta name="description" content="{head_desc}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;1,300&family=Jost:wght@300;400&family=Noto+Sans+TC:wght@200;300;400&family=Noto+Serif+TC:wght@200;300;400&display=swap" rel="stylesheet">
<style>
:root{{
  /* ── 品牌色（目測自 CI 圖，待設計師正式 HEX 校正）── */
  /* 官方色票（來自 蒔恩 LOGO 完稿_260911.pdf）*/
  --sage-pale:#BCCFC9;   /* C31 M13 Y22 K0 */
  --sage:#8CAAA0;        /* C51 M26 Y38 K0 */
  --cream:#F3ECE6;       /* C6 M9 Y10 K0  */
  --clay:#E39782;        /* C13 M51 Y44 K0 */
  /* 以上四色推導，非官方 */
  --sage-deep:#5B7A70;
  --cream-warm:#F9F4EF;
  --ink:#33322F;
  --ink-soft:#6B6862;
  --line:rgba(51,50,47,.13);
  --serif:"Noto Serif TC",serif;
  --sans:"Noto Sans TC",sans-serif;
  --en:"Cormorant Garamond",serif;
  --util:"Jost",sans-serif;
  --gut:clamp(22px,5vw,72px);
}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--cream);color:var(--ink);
  font-family:var(--sans);font-weight:300;-webkit-font-smoothing:antialiased}}
img{{max-width:100%;display:block}}

.eyebrow{{font-family:var(--util);font-size:10.5px;letter-spacing:.24em;
  text-transform:uppercase;color:var(--sage-deep)}}
.h2{{font-family:var(--serif);font-weight:200;font-size:clamp(23px,3vw,36px);
  line-height:1.55;letter-spacing:.09em;margin:14px 0 0}}
.lede{{font-size:15px;line-height:2.1;color:var(--ink-soft);max-width:40em;margin:16px 0 0}}
.sec{{padding:clamp(46px,6vw,92px) var(--gut)}}
.wrap{{max-width:1080px;margin:0 auto}}
p{{margin:0 0 16px}}
p:last-child{{margin-bottom:0}}

.slot{{border:1px dashed var(--sage);background:rgba(143,175,162,.07);
  border-radius:5px;padding:14px 16px;margin:4px 0 0;
  font-family:var(--util);font-size:11.5px;letter-spacing:.1em;color:var(--sage-deep)}}
.slot b{{font-weight:400;color:var(--clay)}}
.tbd{{color:var(--sage-deep);opacity:.6}}

/* ── 封面 ── */
.cover{{min-height:min(74vh,580px);display:flex;flex-direction:column;
  justify-content:center;padding:clamp(52px,7vw,90px) var(--gut);
  background:linear-gradient(155deg,var(--sage-pale) 0%,var(--sage) 78%);
  color:#fff;position:relative;overflow:hidden}}
.cover::after{{content:"";position:absolute;right:-14%;bottom:-32%;
  width:min(62vw,620px);aspect-ratio:1;border-radius:50%;
  background:rgba(255,255,255,.11)}}
.cover>*{{position:relative;z-index:2}}
.logo{{width:clamp(220px,30vw,360px);color:#fff}}
.logo svg{{width:100%;height:auto;display:block}}
.logo-end{{width:clamp(170px,20vw,230px);margin:0 auto;color:rgba(255,255,255,.88)}}
.logo-end svg{{width:100%;height:auto;display:block}}
.cover .tag{{display:inline-block;align-self:flex-start;font-family:var(--util);
  font-size:11px;letter-spacing:.24em;text-transform:uppercase;
  border:1px solid rgba(255,255,255,.55);border-radius:999px;
  padding:9px 22px;margin-bottom:clamp(26px,5vw,48px)}}
.cover h1{{font-family:var(--serif);font-weight:200;
  font-size:clamp(26px,3.8vw,46px);line-height:1.55;letter-spacing:.1em;
  margin:clamp(28px,5vw,50px) 0 0}}
.cover .sub{{font-family:var(--util);font-size:12px;letter-spacing:.24em;
  text-transform:uppercase;margin-top:18px;opacity:.9}}

/* ── 方案內容 ── */
.items{{list-style:none;padding:0;margin:clamp(24px,3vw,38px) 0 0;
  border-top:1px solid var(--line);max-width:620px}}
.items li{{display:flex;align-items:baseline;gap:13px;padding:15px 0;
  border-bottom:1px solid var(--line);font-size:15.5px}}
.items .dot{{flex:none;width:5px;height:5px;border-radius:50%;
  background:var(--clay);transform:translateY(-2px)}}
.items em{{margin-left:auto;font-style:normal;font-family:var(--util);
  font-size:10.5px;letter-spacing:.14em;color:var(--ink-soft)}}

/* ── 品牌故事：破壞→修復→新生 ── */
.intro-body{{max-width:40em}}
.story-lead{{margin-top:clamp(24px,3vw,38px);padding-top:clamp(22px,2.6vw,32px);
  border-top:1px solid var(--line);color:var(--ink);font-size:16px}}
.stages{{display:grid;grid-template-columns:repeat(3,1fr);
  gap:clamp(14px,2vw,26px);margin-top:clamp(26px,3.5vw,44px);counter-reset:s}}
.stage{{background:#fff;border-radius:7px;padding:clamp(22px,2.6vw,34px);
  position:relative;border-top:2px solid var(--sage)}}
.stage:nth-child(2){{border-top-color:var(--sage-deep)}}
.stage:nth-child(3){{border-top-color:var(--clay)}}
.sno{{font-family:var(--en);font-style:italic;font-size:clamp(26px,3.4vw,42px);
  line-height:1;color:var(--sage-pale);margin:0}}
.stage:nth-child(3) .sno{{color:#EBD3C9}}
.stage h3{{font-family:var(--serif);font-weight:300;
  font-size:clamp(19px,2.2vw,25px);letter-spacing:.14em;margin:10px 0 0;
  display:flex;align-items:baseline;gap:11px;flex-wrap:wrap}}
.stage h3 span{{font-family:var(--en);font-style:italic;font-size:15px;
  letter-spacing:.03em;color:var(--clay)}}
.sbody{{font-size:14.5px;line-height:2.05;color:var(--ink-soft);margin:14px 0 0}}

/* ── 診所空間 ── */
.gal{{display:grid;grid-template-columns:1fr 1fr;gap:clamp(10px,1.6vw,18px);
  margin-top:clamp(26px,3.5vw,44px)}}
.sp{{margin:0;position:relative;aspect-ratio:16/10;overflow:hidden;
  border-radius:7px;background:var(--cream)}}
.gal .sp:last-child:nth-child(odd){{grid-column:1 / -1;aspect-ratio:21/9}}
.sp img{{width:100%;height:100%;object-fit:cover;display:block}}
.sp figcaption{{position:absolute;left:13px;bottom:11px;z-index:2;
  font-family:var(--util);font-size:10px;letter-spacing:.2em;
  text-transform:uppercase;color:#fff;text-shadow:0 1px 10px rgba(0,0,0,.55)}}
.sp.empty{{background:linear-gradient(150deg,var(--sage-pale),var(--sage) 75%)}}
.sp.empty figcaption{{opacity:.85}}
.sp.empty::after{{content:"待補";position:absolute;inset:0;display:flex;
  align-items:center;justify-content:center;font-family:var(--util);
  font-size:11px;letter-spacing:.28em;color:rgba(255,255,255,.75)}}

/* ── 療程 ── */
.tx{{border-top:1px solid var(--line);padding:clamp(26px,3.4vw,44px) 0;
  display:grid;grid-template-columns:minmax(0,4fr) minmax(0,7fr);
  gap:clamp(18px,3vw,52px);align-items:start}}
.tx:first-of-type{{border-top:0}}
.tx h3{{font-family:var(--serif);font-weight:300;font-size:clamp(19px,2.3vw,27px);
  letter-spacing:.08em;margin:0;line-height:1.5}}
.tx .en{{font-family:var(--en);font-style:italic;font-size:15px;
  color:var(--clay);margin-top:6px}}
.tx .cat{{display:inline-block;margin-top:14px;font-family:var(--util);
  font-size:10px;letter-spacing:.18em;text-transform:uppercase;
  background:var(--sage-pale);color:var(--sage-deep);
  border-radius:999px;padding:6px 14px}}
.only{{color:var(--clay)}}
.field{{margin-bottom:20px}}
.field:last-child{{margin-bottom:0}}
.field h4{{font-family:var(--util);font-size:10px;letter-spacing:.2em;
  text-transform:uppercase;color:var(--sage-deep);margin:0 0 9px;
  padding-bottom:7px;border-bottom:1px solid var(--line)}}
.field p{{margin:0;font-size:14.5px;line-height:2.05;color:var(--ink-soft)}}
.bul{{list-style:none;padding:0;margin:0}}
.bul li{{position:relative;padding:6px 0 6px 18px;font-size:14.5px;
  line-height:1.95;color:var(--ink-soft)}}
.bul li::before{{content:"";position:absolute;left:0;top:19px;
  width:7px;height:1px;background:var(--clay)}}
.spec{{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin:0}}
.spec div{{background:var(--cream);border-radius:5px;padding:13px 14px}}
.spec dt{{font-family:var(--util);font-size:9.5px;letter-spacing:.16em;
  text-transform:uppercase;color:var(--sage-deep);margin:0 0 6px}}
.spec dd{{margin:0;font-size:13.5px;color:var(--ink);line-height:1.6}}


/* 療程步驟 */
.steps{{list-style:none;padding:0;margin:0;display:grid;
  grid-template-columns:repeat(3,1fr);gap:9px}}
.steps li{{background:var(--cream);border-radius:5px;padding:14px 15px}}
.steps .sn{{display:block;font-family:var(--util);font-size:9.5px;
  letter-spacing:.18em;color:var(--clay);margin-bottom:7px}}
.steps .sd{{font-size:13.5px;line-height:1.7;color:var(--ink)}}

/* 適合族群 */
.suits-t{{font-size:14px;color:var(--ink);margin:0 0 12px}}
.suits{{width:100%;border-collapse:collapse}}
.suits th,.suits td{{text-align:left;vertical-align:top;
  padding:11px 0;border-bottom:1px solid var(--line);font-weight:300}}
.suits th{{width:32%;padding-right:14px;color:var(--sage-deep);
  font-size:13.5px;white-space:nowrap}}
.suits td{{font-size:13.5px;line-height:1.8;color:var(--ink-soft)}}
.suits tr:last-child th,.suits tr:last-child td{{border-bottom:0}}

/* 痛感程度 */
.pain{{display:flex;align-items:center;gap:9px}}
.dots{{display:inline-flex;gap:4px}}
.dots i{{width:7px;height:7px;border-radius:50%;
  background:rgba(51,50,47,.16);display:block}}
.dots i.on{{background:var(--clay)}}

.on-cream{{background:var(--cream-warm)}}
.on-sage{{background:var(--sage-pale)}}
.on-white{{background:#fff}}

.end{{background:var(--ink);color:rgba(255,255,255,.72);
  padding:clamp(30px,3.6vw,48px) var(--gut);text-align:center}}

.end .a{{font-family:var(--util);font-size:10.5px;letter-spacing:.24em;
  text-transform:uppercase;margin:14px 0 0;opacity:.72}}

@media(max-width:820px){{
  .cover{{min-height:auto;padding:clamp(46px,13vw,68px) var(--gut)}}
  .logo{{width:min(76vw,260px)}}
  .cover h1{{font-size:clamp(21px,5.6vw,28px);margin-top:24px}}
  .cover::after{{width:min(80vw,320px);right:-22%;bottom:-16%}}
  .tx{{grid-template-columns:1fr;gap:16px}}
  .spec{{grid-template-columns:1fr}}
  .steps{{grid-template-columns:1fr}}
  .suits th{{width:38%}}
  .stages{{grid-template-columns:1fr}}
  .gal{{grid-template-columns:1fr}}
}}

@page{{size:A4;margin:13mm}}
@media print{{
  body{{background:#fff}}
  .sec{{padding:14mm 0 9mm}}
  .cover{{min-height:auto;padding:26mm 14mm;break-after:page}}
  .cover::after{{display:none}}
  .tx{{break-inside:avoid;page-break-inside:avoid}}
  .stage,.sp{{break-inside:avoid}}
  .stages{{gap:8mm}}
  .slot{{border-color:#999;color:#666;background:#f6f6f6}}
  *{{-webkit-print-color-adjust:exact;print-color-adjust:exact}}
}}
</style>
</head>
<body>

<section class="cover">
  <div class="logo">{logo}</div>
  <h1>{title}</h1>
</section>

<section class="sec on-cream"><div class="wrap">
  <div class="eyebrow">{L_intro_eyebrow}</div>
  <h2 class="h2">{L_intro_head}</h2>
  <div class="intro-body">{intro}</div>
  <p class="lede story-lead">{story_lead}</p>
  {stages}
</div></section>

{main_section}<section class="sec on-cream"><div class="wrap">
  <div class="eyebrow">{tx_eyebrow}</div>
  <h2 class="h2">{tx_head}</h2>
  <p class="lede">{L_tx_lede}</p>
  <div style="margin-top:clamp(28px,4vw,48px)">{blocks}
  </div>
</div></section>

<section class="sec on-white"><div class="wrap">
  <div class="eyebrow">{L_space_eyebrow}</div>
  <h2 class="h2">{L_space_head}</h2>
  <p class="lede">{L_space_lede}</p>
  {gallery}
</div></section>

<div class="end">
  <div class="logo-end">{logo_end}</div>
  <p class="a">{contact}</p>
</div>

</body>
</html>
"""

if __name__ == "__main__":
    n = load_content()
    if n:
        print(f"  套用 {n} 個欄位")
    here = pathlib.Path(__file__).parent
    for plan in PLANS:
        out = here / plan["file"]
        out.write_text(build(plan), encoding="utf-8")
        n = build(plan).count('class="slot"')
        print(f"✓ {plan['file']}　{plan['title']}　"
              f"{len(plan['items'])} 項療程　待填 {n} 處")
