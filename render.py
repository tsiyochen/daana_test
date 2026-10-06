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
    dict(tpl="home.tpl.html", test_out="index.html", prod_out="index.html"),
]

# ── 導覽連結：模板寫法 → 各環境的實際網址 ──────────────
LINKS = {
    "index.html":      {"test": "index.html",      "prod": "/"},
    "treatments.html": {"test": "treatments.html", "prod": "/cultivation/"},
}

# ── 圖片路徑前綴 ────────────────────────────────────────
IMG_PREFIX = {"test": "sheand-kol/images/", "prod": "images/"}


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
    s = s.replace("{{IMG}}", IMG_PREFIX[env])
    s = s.replace("{{DOCS}}", docs_html())
    # 導覽連結改寫
    for src, dst in LINKS.items():
        s = s.replace(f'href="{src}"', f'href="{dst[env]}"')
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

    # 2. 圖片複製進 dist（正式站用相對路徑，不再內嵌）
    if PUBLISH:
        dst_img = DIST / "images"
        dst_img.mkdir(parents=True, exist_ok=True)
        n = 0
        for f in IMAGES.iterdir():
            if f.suffix.lower() in {".jpg", ".png", ".webp", ".svg"}:
                shutil.copy2(f, dst_img / f.name)
                n += 1
        print(f"\n── 複製 {n} 張圖片到 dist/images/ ──")

    # 3. 渲染各頁面
    print("\n── 渲染頁面 ──")
    for p in PAGES:
        tpl = (SRC / p["tpl"]).read_text(encoding="utf-8")

        out_test = ROOT / p["test_out"]
        out_test.write_text(render(tpl, "test"), encoding="utf-8")
        size = out_test.stat().st_size / 1024
        print(f"  測試站  {p['test_out']:24} {size:6.0f} KB")

        if PUBLISH:
            out_prod = DIST / p["prod_out"]
            out_prod.parent.mkdir(parents=True, exist_ok=True)
            out_prod.write_text(render(tpl, "prod"), encoding="utf-8")
            size = out_prod.stat().st_size / 1024
            print(f"  正式站  dist/{p['prod_out']:19} {size:6.0f} KB")

    if not PUBLISH:
        print("\n  （只更新了測試站。確認無誤後跑 --publish 推正式站）")


if __name__ == "__main__":
    main()
