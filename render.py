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

# ── 頁面定義 ────────────────────────────────────────────
# tpl        site-src 底下的模板
# test_out   測試站輸出路徑（相對 repo 根目錄）
# prod_out   正式站輸出路徑（相對 dist/）
PAGES = [
    dict(tpl="home.tpl.html",        route=""),              # 首頁
    dict(tpl="cultivation.tpl.html", route="cultivation/"),  # 蘊膚計畫
]

# ── 站台根路徑 ──────────────────────────────────────────
#  GitHub Pages 的專案站在子路徑底下，所以兩站的 base 不同，
#  但 base 之後的路徑完全一致：/、/cultivation/
BASE = {"test": "/daana_test/", "prod": "/"}

# ── 模板裡的連結寫法 → 對應到哪一條 route ───────────────
LINKS = {
    "index.html": "",
    "treatments.html": "cultivation/",
}


def logo_svg():
    """模板的 CSS 依賴 .logo-svg 這個類名控制高度，插入時要補上"""
    svg = (IMAGES / "logo-primary.svg").read_text(encoding="utf-8").strip()
    return svg.replace(
        "<svg ",
        '<svg class="logo-svg" aria-label="蒔恩美學診所 SHE AND" ', 1)


def docs_html():
    """醫師卡片，來源是 site-src/docs.html"""
    f = SRC / "docs.html"
    return f.read_text(encoding="utf-8").strip() if f.exists() else ""


def render(tpl_text, env):
    s = tpl_text
    s = s.replace("{{LOGO}}", logo_svg())
    s = s.replace("{{IMG}}", BASE[env] + "images/")
    s = s.replace("{{DOCS}}", docs_html())
    # 導覽連結改寫
    for src, route in LINKS.items():
        s = s.replace(f'href="{src}"', f'href="{BASE[env]}{route}"')
    # 正式站拿掉測試橫條
    if env == "prod":
        s = re.sub(r'<div class="testbar">.*?</div>\s*', "", s, flags=re.S)
    return s


def main():
    if not SRC.exists():
        sys.exit("找不到 site-src/")

    # 1. 只有發布時才重建 dist —— build.py 會清空 dist/，
    #    若不發布就執行，正式站的首頁會被刪掉。
    if PUBLISH:
        print("── 建置 KOL 頁面 ──")
        subprocess.run([sys.executable, "build.py"], cwd=KOL, check=True)

    # 2. 圖片：兩站都放在各自根目錄的 images/
    targets = [ROOT / "images"] + ([DIST / "images"] if PUBLISH else [])
    for dst_img in targets:
        dst_img.mkdir(parents=True, exist_ok=True)
        n = 0
        for f in IMAGES.iterdir():
            if f.suffix.lower() in {".jpg", ".png", ".webp", ".svg"}:
                shutil.copy2(f, dst_img / f.name)
                n += 1
        print(f"── 複製 {n} 張圖片到 {dst_img.relative_to(ROOT)}/ ──")

    # 3. 渲染各頁面
    print("\n── 渲染頁面 ──")
    for p in PAGES:
        tpl = (SRC / p["tpl"]).read_text(encoding="utf-8")
        rel = (p["route"] + "index.html") if p["route"] else "index.html"

        out_test = ROOT / rel
        out_test.parent.mkdir(parents=True, exist_ok=True)
        out_test.write_text(render(tpl, "test"), encoding="utf-8")
        print(f"  測試站  /{p['route']:16} {out_test.stat().st_size/1024:6.0f} KB")

        if PUBLISH:
            out_prod = DIST / rel
            out_prod.parent.mkdir(parents=True, exist_ok=True)
            out_prod.write_text(render(tpl, "prod"), encoding="utf-8")
            print(f"  正式站  /{p['route']:16} {out_prod.stat().st_size/1024:6.0f} KB")

    if not PUBLISH:
        print("\n  （只更新了測試站。確認無誤後跑 --publish 推正式站）")


if __name__ == "__main__":
    main()
