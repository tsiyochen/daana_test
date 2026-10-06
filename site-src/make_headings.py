#!/usr/bin/env python3
"""
把設計稿指定的英文大標從 Ivymode 轉成 SVG 路徑

    python3 site-src/make_headings.py

為什麼不直接用字型檔：Ivymode 是 The Ivy Foundry 的商業字型，
網頁託管需要另外的 webfont 授權。這六個字是裝飾性標題、幾乎不會改，
轉成向量路徑可以完整保留設計師指定的字形，也沒有授權疑慮。

輸出到 images/heading-*.svg，用 currentColor 上色，顏色由 CSS 控制。
之後要改字就改下面的 HEADINGS 再跑一次。
"""
import pathlib, sys

ROOT = pathlib.Path(__file__).parent.parent
FONT = ROOT / "_素材原檔" / "IvyMode.42530.otf"
OUT = ROOT / "images"

HEADINGS = {
    "about":      "About",
    "concept":    "Concept",
    "treatments": "Treatments",
    "team":       "Our Team",
    "faq":        "FAQ",
    "contact":    "Contact",
}


def build(font, text):
    """把一串文字畫成單一 path，回傳 (path_d, 寬, 上緣, 下緣)"""
    from fontTools.pens.svgPathPen import SVGPathPen
    from fontTools.pens.transformPen import TransformPen
    from fontTools.pens.boundsPen import BoundsPen
    from fontTools.misc.transform import Transform

    cmap = font.getBestCmap()
    gs = font.getGlyphSet()
    hmtx = font["hmtx"]

    # 字距調整（kerning）
    kern = {}
    if "kern" in font:
        for st in font["kern"].kernTables:
            kern.update(st.kernTable)

    pen = SVGPathPen(gs)
    x = 0
    prev = None
    bounds = [None] * 4           # xMin, yMin, xMax, yMax

    for ch in text:
        if ch == " ":
            x += hmtx[cmap[ord("i")]][0] * 1.6   # 空白用 i 的寬度估
            prev = None
            continue
        name = cmap.get(ord(ch))
        if name is None:
            sys.exit(f"字型缺少字元：{ch!r}")
        if prev and (prev, name) in kern:
            x += kern[(prev, name)]

        bp = BoundsPen(gs)
        gs[name].draw(bp)
        if bp.bounds:
            x0, y0, x1, y1 = bp.bounds
            vals = (x + x0, y0, x + x1, y1)
            bounds = [v if b is None else f(b, v) for b, v, f in
                      zip(bounds, vals, (min, min, max, max))]

        # Y 軸翻轉：字型座標 Y 朝上，SVG 朝下
        gs[name].draw(TransformPen(pen, Transform(1, 0, 0, -1, x, 0)))
        x += hmtx[name][0]
        prev = name

    return pen.getCommands(), bounds


def main():
    if not FONT.exists():
        sys.exit(f"找不到字型：{FONT}")
    try:
        from fontTools.ttLib import TTFont
    except ImportError:
        sys.exit("請先安裝：pip3 install fonttools")

    font = TTFont(FONT)
    OUT.mkdir(exist_ok=True)
    pad = 4

    # 垂直範圍用字型的 em box（hhea 的 ascent/descent），六個字一致。
    # 否則各自用字框高度，同一個 CSS 高度會算出不同字級：實測 115～149px 都有。
    # 設計稿的行高 190 = 128px × (1183+300)/1000，正是這個 box，
    # 所以 SVG 高度可以直接對應設計稿的行高。
    asc, desc = font["hhea"].ascent, font["hhea"].descent

    for slug, text in HEADINGS.items():
        d, (x0, y0, x1, y1) = build(font, text)
        vb = (x0 - pad, -asc, (x1 - x0) + pad * 2, asc - desc)
        svg = (
            f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'viewBox="{vb[0]:.0f} {vb[1]:.0f} {vb[2]:.0f} {vb[3]:.0f}" '
            f'fill="currentColor" role="img" aria-label="{text}">'
            f'<title>{text}</title><path d="{d}"/></svg>'
        )
        p = OUT / f"heading-{slug}.svg"
        p.write_text(svg, encoding="utf-8")
        print(f"  heading-{slug}.svg  {len(svg)/1024:5.1f} KB  "
              f"{vb[2]:.0f}×{vb[3]:.0f}  「{text}」")


if __name__ == "__main__":
    main()
