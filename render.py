#!/usr/bin/env python3
"""
蒔恩官網發布腳本 —— 從 site-src/ 的模板產生測試站與正式站

    python3 render.py             只更新測試站（repo 根目錄）
    python3 render.py --publish   連正式站一起更新（sheand-kol/dist/）

測試站 → https://tsiyochen.github.io/daana_test/   有「這是測試站」橫條
正式站 → https://sheandclinic.com/                 無橫條

兩邊同一份模板，不會不同步。
"""
import pathlib, re, shutil, subprocess, sys

ROOT = pathlib.Path(__file__).parent
SRC = ROOT / "site-src"
KOL = ROOT / "sheand-kol"
DIST = KOL / "dist"
IMAGES = KOL / "images"

PUBLISH = "--publish" in sys.argv

# ── 上線開關 ────────────────────────────────────────────
# 蘊膚計畫頁是否已對外。False 時正式站會：
#   1. 導航列不顯示「蘊膚計畫」（顯示但點不動會讓人以為網站壞了）
#   2. 不輸出 dist/cultivation/
# 測試站不受影響，隨時可以繼續檢視該頁。
# 該頁定稿後把這裡改成 True，跑 python3 render.py --publish 即可。
CULTIVATION_LIVE = True

# 開幕邀請卡。活動頁，不進導覽列，只靠 LINE 傳連結。
# 文案與 Google 表單都確認好之後再改成 True，跑 render.py --publish。
OPENING_LIVE = False

# 開幕活動的時間。這裡是行事曆檔與頁面上 Google 日曆連結「唯一的」來源。
# 改日期：改這三行，模板裡印出來的中文日期也要一起改 ——
# 下面的檢查會比對兩邊，只改一邊的話 render 會直接中止。
OPENING = dict(
    date_cn   = "2026.12.06",         # 模板上印的樣子，純粹用來比對有沒有改漏
    start_utc = "20261206T093000Z",   # 台北 17:30 進場（台灣沒有日光節約，固定 +8）
    end_utc   = "20261206T120000Z",   # 台北 20:00 散場
)

# ── 頁面定義 ────────────────────────────────────────────
# tpl        site-src 底下的模板
# test_out   測試站輸出路徑（相對 repo 根目錄）
# prod_out   正式站輸出路徑（相對 dist/）
PAGES = [
    dict(tpl="home.tpl.html",        route=""),              # 首頁
    dict(tpl="cultivation.tpl.html", route="cultivation/"),  # 蘊膚計畫
    dict(tpl="opening.tpl.html",     route="opening/"),      # 開幕邀請卡
]

# ── 路徑策略 ────────────────────────────────────────────
#  一律用相對路徑。GitHub Pages 的專案站在 /daana_test/ 底下，
#  正式站在根目錄，本機預覽又是另一個位置 —— 相對路徑三者皆通，
#  不需要為各環境設不同的 base。

# ── 模板裡的連結寫法 → 對應到哪一條 route ───────────────
LINKS = {
    "index.html": "",
    "treatments.html": "cultivation/",
}

# og:image 與 og:url 必須是絕對網址（LINE、FB 都不接受相對路徑）
BASEURL = {
    "test": "https://tsiyochen.github.io/daana_test/",
    "prod": "https://sheandclinic.com/",
}


def logo_svg():
    """模板的 CSS 依賴 .logo-svg 這個類名控制高度，插入時要補上"""
    svg = (IMAGES / "logo-primary.svg").read_text(encoding="utf-8").strip()
    return svg.replace(
        "<svg ",
        '<svg class="logo-svg" aria-label="蒔恩美學診所 SHE AND" ', 1)


def heading_svg(slug):
    """英文大標：從 Ivymode 轉出的向量路徑，用 currentColor 上色"""
    f = IMAGES.parent.parent / "images" / f"heading-{slug}.svg"
    if not f.exists():
        f = ROOT / "images" / f"heading-{slug}.svg"
    return f.read_text(encoding="utf-8").strip() if f.exists() else ""

def docs_html():
    """醫師卡片，來源是 site-src/docs.html"""
    f = SRC / "docs.html"
    return f.read_text(encoding="utf-8").strip() if f.exists() else ""


def ics_text(env):
    """開幕那場活動的行事曆檔。

    時間一律寫成 UTC（結尾那個 Z），這樣就不必在檔案裡附一整段時區定義，
    台灣沒有日光節約，換算永遠是 +8，不會有歧義。
    換行必須是 CRLF，這是 RFC 5545 的規定，不是排版偏好。
    """
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//SHE AND//opening//ZH-TW",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "BEGIN:VEVENT",
        # 固定值，不用 now()：每次 render 都要產出一模一樣的檔案，否則 git 會一直有變動
        "UID:opening-" + OPENING["start_utc"] + "@sheandclinic.com",
        "DTSTAMP:" + OPENING["start_utc"],
        "DTSTART:" + OPENING["start_utc"],
        "DTEND:" + OPENING["end_utc"],
        "SUMMARY:蒔恩美學診所 開幕邀請",
        "LOCATION:台北市大安區新生南路二段2號7樓",
        "DESCRIPTION:17:30 進場，18:00 開始。",
        "URL:" + BASEURL[env] + "opening/",
        "END:VEVENT",
        "END:VCALENDAR",
    ]
    return "\r\n".join(lines) + "\r\n"


def render(tpl_text, env, depth=0):
    up = "../" * depth
    s = tpl_text
    s = s.replace("{{LOGO}}", logo_svg())
    # DOCS 要先插入，它裡面也有 {{IMG}}；順序反了會留下沒換掉的佔位符
    s = s.replace("{{DOCS}}", docs_html())
    s = s.replace("{{IMG}}", up + "images/")
    s = s.replace("{{BASEURL}}", BASEURL[env])
    s = s.replace("{{EVENT_DATES}}", OPENING["start_utc"] + "/" + OPENING["end_utc"])
    s = re.sub(r"\{\{H:([a-z]+)\}\}", lambda m: heading_svg(m.group(1)), s)
    # 導覽連結改寫：換算成從目前頁面出發的相對路徑
    for src, route in LINKS.items():
        s = s.replace(f'href="{src}"', f'href="{(up + route) or "./"}"')
    # 正式站拿掉測試橫條
    if env == "prod":
        s = re.sub(r'<div class="testbar">.*?</div>\s*', "", s, flags=re.S)
        if not CULTIVATION_LIVE:
            # 整個項目移除，而不是改成 #：點不動的項目比沒有更糟
            s = re.sub(r'\s*<li><a href="cultivation/"[^>]*>[^<]*</a></li>', "", s)
    return s


def main():
    if not SRC.exists():
        sys.exit("找不到 site-src/")

    # 1. 建置 KOL 頁面（只會重建 dist/experience/，不碰其他頁）
    print("── 建置 KOL 頁面 ──")
    subprocess.run([sys.executable, "build.py"], cwd=KOL, check=True)

    # 2. 圖片：兩站都放在各自根目錄的 images/
    targets = [ROOT / "images"] + ([DIST / "images"] if PUBLISH else [])
    for dst_img in targets:
        dst_img.mkdir(parents=True, exist_ok=True)
        n = 0
        for f in IMAGES.iterdir():
            if f.suffix.lower() not in {".jpg", ".png", ".webp", ".svg", ".ico"}:
                continue
            # 未上線頁面專用的圖不要跟著進正式站
            if dst_img == DIST / "images" and (
                    (not CULTIVATION_LIVE and f.name.startswith("cult-"))
                    or (not OPENING_LIVE and f.name.startswith("invite-"))):
                continue
            shutil.copy2(f, dst_img / f.name)
            n += 1
        print(f"── 複製 {n} 張圖片到 {dst_img.relative_to(ROOT)}/ ──")

    if PUBLISH:
        shutil.copy2(IMAGES / "favicon.ico", DIST / "favicon.ico")
        print("── 複製 favicon.ico 到 dist/ 根目錄（瀏覽器的隱含請求）──")

    # 3. 渲染各頁面
    print("\n── 渲染頁面 ──")
    for p in PAGES:
        tpl = (SRC / p["tpl"]).read_text(encoding="utf-8")
        rel = (p["route"] + "index.html") if p["route"] else "index.html"

        out_test = ROOT / rel
        out_test.parent.mkdir(parents=True, exist_ok=True)
        depth = p["route"].count("/")
        html_test = render(tpl, "test", depth)
        if p["route"] == "opening/" and OPENING["date_cn"] not in html_test:
            sys.exit(f'opening.tpl.html 裡找不到 {OPENING["date_cn"]}。'
                     "邀請卡上的日期和行事曆檔對不起來了，兩邊要一起改。")
        out_test.write_text(html_test, encoding="utf-8")
        print(f"  測試站  /{p['route']:16} {out_test.stat().st_size/1024:6.0f} KB")

        if PUBLISH:
            if p["route"] == "cultivation/" and not CULTIVATION_LIVE:
                continue
            if p["route"] == "opening/" and not OPENING_LIVE:
                continue
            out_prod = DIST / rel
            out_prod.parent.mkdir(parents=True, exist_ok=True)
            out_prod.write_text(render(tpl, "prod", depth), encoding="utf-8")
            print(f"  正式站  /{p['route']:16} {out_prod.stat().st_size/1024:6.0f} KB")

    # 3b. 行事曆檔。謝卡上的「加入行事曆」按鈕指向 opening/sheand-opening.ics。
    ics_targets = [("test", ROOT)] + ([("prod", DIST)] if PUBLISH and OPENING_LIVE else [])
    for env, base in ics_targets:
        f = base / "opening" / "sheand-opening.ics"
        f.parent.mkdir(parents=True, exist_ok=True)
        # newline="" 才不會被 Python 改寫成平台換行，CRLF 必須原樣寫出去
        with f.open("w", encoding="utf-8", newline="") as fh:
            fh.write(ics_text(env))
        print(f"  行事曆  /{'opening/sheand-opening.ics':24} {env}")

    # 4. KOL 頁同步到測試站，路徑與正式站一致：/experience/
    src_exp = DIST / "experience" / "index.html"
    if src_exp.exists():
        html = src_exp.read_text(encoding="utf-8")
        # 它的 logo 連回首頁，測試站要帶上 base
        html_test = html.replace('href="/"', 'href="../"')
        out = ROOT / "experience" / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(html_test, encoding="utf-8")
        print(f"  測試站  /experience/     {out.stat().st_size/1024:6.0f} KB")

    if not PUBLISH:
        print("\n  （只更新了測試站。確認無誤後跑 --publish 推正式站）")


if __name__ == "__main__":
    main()
