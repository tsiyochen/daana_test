#!/usr/bin/env python3
"""
把 build.py 目前的內容匯出成 content.csv

⚠️ 警告：這支程式會「覆蓋」content.csv。

    Google Sheet 上線後，Sheet 才是唯一的內容來源。
    直接跑這支會把同事在 Sheet 上的修改蓋掉。

    只有在「要新增欄位或改結構」時才用，而且用之前要先：
      1. 從 Sheet 下載最新的 CSV
      2. 把新內容同步回 build.py
      3. 再跑這支

    python3 export_csv.py --force
"""
import sys
if "--force" not in sys.argv:
    print("⚠ 這會覆蓋 content.csv，蓋掉同事在 Google Sheet 上的修改。")
    print("  確定要跑請加 --force：python3 export_csv.py --force")
    raise SystemExit(1)

import csv, pathlib
import build as B

SEP = "｜"          # 分段 / 條列的分隔符號（全形直線）

rows = []

def add(key, group, item, field, value, note=""):
    rows.append(dict(key=key, 分類=group, 項目=item, 欄位=field,
                     內容=value, 說明=note))

def join(seq):
    return SEP.join(seq)

# ── 全站 ──────────────────────────────────────────────
add("brand.intro", "全站", "品牌", "品牌簡介",
    B.BRAND["intro"], f"關於蒔恩底下那段。2–3 段，段落之間用 {SEP} 分開")
add("brand.address", "全站", "品牌", "頁尾地址",
    B.BRAND["address"], "頁面最底下那行")
add("brand.phone", "全站", "品牌", "頁尾電話",
    B.BRAND.get("phone", ""), "顯示在地址右邊，中間用間隔點分開")
add("story.lead", "全站", "品牌故事", "引言",
    B.STORY_LEAD, "三張卡片上方那一句")

for i, s in enumerate(B.STORY, 1):
    add(f"story.{i}.zh", "全站", f"品牌故事 {s['no']}", "階段名稱", s["zh"], "例如：破壞")
    add(f"story.{i}.en", "全站", f"品牌故事 {s['no']}", "英文", s["en"], "例如：Disrupt")
    add(f"story.{i}.body", "全站", f"品牌故事 {s['no']}", "說明", s["body"], "卡片內文")

# ── 診所空間 ───────────────────────────────────────────
for i, sp in enumerate(B.SPACE, 1):
    add(f"space.{i}.label", "診所空間", f"照片 {i}", "圖說", sp["label"],
        "壓在照片左下角的字。照片本身要換的話要另外給檔案")

# ── 療程 ──────────────────────────────────────────────
SKIP = {"hifu_eye"}          # 不放進 CSV 的療程（同事不編輯）

for key, t in B.TREATMENTS.items():
    if key in SKIP:
        continue
    n = t["name"]
    add(f"tx.{key}.name",      "療程", n, "名稱",     t["name"], "")
    add(f"tx.{key}.en",        "療程", n, "英文",     t["en"], "斜體小字")
    add(f"tx.{key}.cat",       "療程", n, "分類標籤", t["cat"], "綠色小圓角標籤")
    add(f"tx.{key}.principle", "療程", n, "主要原理", t["principle"],
        "一句話，12–15 字最好看")
    add(f"tx.{key}.principle_points", "療程", n, "原理補充",
        join(t.get("principle_points") or []),
        f"條列，用 {SEP} 分開。留空就不顯示")
    add(f"tx.{key}.effect",    "療程", n, "主要功效", t["effect"], "一句話")
    add(f"tx.{key}.benefits",  "療程", n, "功效補充",
        join(t.get("benefits") or []), f"條列，用 {SEP} 分開。留空就不顯示")
    add(f"tx.{key}.duration",  "療程", n, "治療時間", t["duration"], "例如：15分鐘")
    add(f"tx.{key}.recovery",  "療程", n, "恢復期",   t["recovery"], "例如：沒有")
    add(f"tx.{key}.pain",      "療程", n, "痛感等級", str(t["pain"]),
        "0=無 1=輕微 2=中等 3=較明顯。控制圓點亮幾顆")
    add(f"tx.{key}.pain_label","療程", n, "痛感說明", t["pain_label"],
        "圓點旁邊的字。留空整欄會顯示「待填」")
    if t.get("steps"):
        add(f"tx.{key}.steps", "療程", n, "療程步驟",
            join(f"{a}:{b}" for a, b in t["steps"]),
            f"格式「第一步:內容」，步驟之間用 {SEP} 分開")


# ── 版面固定文字 ────────────────────────────────────────
LABEL_NOTE = {
    "intro_eyebrow":      "「關於蒔恩」上方的英文小字",
    "intro_head":         "區塊標題",
    "cultivation_eyebrow":"「什麼是養膚」上方的英文小字（只有體驗頁）",
    "cultivation_head":   "區塊標題（只有體驗頁）",
    "pkg_eyebrow":        "方案區塊上方的英文小字（只有套餐頁）",
    "pkg_lede_tail":      "接在副標後面那段（只有套餐頁）",
    "tx_eyebrow_pkg":     "療程區塊英文小字（套餐頁）",
    "tx_head_pkg":        "療程區塊標題（套餐頁）",
    "tx_eyebrow_exp":     "療程區塊英文小字（體驗頁）",
    "tx_head_exp":        "療程區塊標題（體驗頁）",
    "tx_lede":            "療程區塊標題底下那段說明",
    "space_eyebrow":      "「診所空間」上方的英文小字",
    "space_head":         "區塊標題",
    "space_lede":         "診所空間標題底下那段",
    "f_principle":        "療程欄位標題",
    "f_effect":           "療程欄位標題",
    "f_steps":            "療程欄位標題",
    "f_info":             "療程欄位標題",
    "f_duration":         "療程資訊裡的小標",
    "f_recovery":         "療程資訊裡的小標",
    "f_pain":             "療程資訊裡的小標",
}
for k, note in LABEL_NOTE.items():
    add(f"label.{k}", "版面文字", "固定文字", k, B.LABELS.get(k, ""), note)

# ── 三個頁面 ───────────────────────────────────────────
for p in B.PLANS:
    f = p["file"]
    label = {"plan-01.html": "套餐頁 01（4 項）",
             "plan-02.html": "套餐頁 02（5 項）",
             "experience.html": "體驗頁（第一波合作）"}.get(f, f)
    add(f"page.{f}.title", "頁面", label, "頁面標題", p["title"], "封面那行大字")
    if p.get("kind", "package") == "package":
        add(f"page.{f}.sub", "頁面", label, "副標", p["sub"], "方案區塊的說明開頭")
        add(f"page.{f}.positioning", "頁面", label, "方案定位",
            p["positioning"].replace("\n", SEP),
            f"項目清單下方那段。用 {SEP} 分段")
    else:
        add(f"page.{f}.intro_text", "頁面", label, "什麼是養膚",
            (p.get("intro_text") or "").replace("\n", SEP),
            f"體驗頁專屬。用 {SEP} 分段")

out = pathlib.Path(__file__).parent / "content.csv"
with out.open("w", encoding="utf-8-sig", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=["key", "分類", "項目", "欄位", "內容", "說明"])
    w.writeheader()
    w.writerows(rows)

print(f"✓ content.csv　{len(rows)} 列")
filled = sum(1 for r in rows if r["內容"])
print(f"  已有內容 {filled} 列 ／ 空白 {len(rows)-filled} 列")
