#!/usr/bin/env python3
"""查本機快取的 Figma 節點樹，不再打 API。

    python3 figma.py tree  <node_id> [深度]   結構 + 尺寸 + 位置
    python3 figma.py spec  <node_id>          該節點的 autolayout / 字體 / 顏色
    python3 figma.py find  <關鍵字>            依名稱搜尋節點
"""
import json, sys, glob, pathlib, os
ROOT_DIR=os.path.dirname(os.path.abspath(__file__))

ROOT = pathlib.Path(__file__).parent
NODES = {}
for f in glob.glob(os.path.join(ROOT_DIR,"node_*.json")):
    d = json.load(open(f))
    for nid, wrap in d.get("nodes", {}).items():
        def walk(n, parent=None):
            n["_parent"] = parent
            NODES[n["id"]] = n
            for c in n.get("children", []):
                walk(c, n["id"])
        walk(wrap["document"])

def box(n):
    b = n.get("absoluteBoundingBox") or {}
    return b.get("x", 0), b.get("y", 0), b.get("width", 0), b.get("height", 0)

def rel(n):
    """相對父層的座標"""
    x, y, w, h = box(n)
    p = NODES.get(n.get("_parent"))
    if p:
        px, py, _, _ = box(p)
        return x - px, y - py, w, h
    return x, y, w, h

def tree(nid, maxd=3, d=0):
    n = NODES.get(nid)
    if not n: sys.exit(f"找不到 {nid}")
    rx, ry, w, h = rel(n)
    lay = ""
    if n.get("layoutMode", "NONE") != "NONE":
        pad = [n.get(k, 0) for k in ("paddingTop","paddingRight","paddingBottom","paddingLeft")]
        lay = f"  [{n['layoutMode'][:1]} gap={n.get('itemSpacing',0):g} pad={'/'.join(f'{p:g}' for p in pad)}]"
    txt = ""
    if n["type"] == "TEXT":
        s = n.get("style", {})
        txt = f"  «{s.get('fontFamily','')} {s.get('fontWeight','')} {s.get('fontSize',0):g}/{s.get('lineHeightPx',0):.0f} ls{s.get('letterSpacing',0):g}»"
    print(f"{'  '*d}{n['id']:>12} {n['type'][:9]:<9} {n['name'][:38]:<38} "
          f"@{rx:7.1f},{ry:8.1f}  {w:7.1f}x{h:8.1f}{lay}{txt}")
    if d < maxd:
        for c in n.get("children", []):
            tree(c["id"], maxd, d + 1)

def spec(nid):
    n = NODES.get(nid)
    if not n: sys.exit(f"找不到 {nid}")
    keys = ("type","name","layoutMode","itemSpacing","counterAxisSpacing","primaryAxisAlignItems",
            "counterAxisAlignItems","paddingTop","paddingRight","paddingBottom","paddingLeft",
            "layoutSizingHorizontal","layoutSizingVertical","cornerRadius","rectangleCornerRadii",
            "clipsContent","opacity","characters")
    out = {k: n[k] for k in keys if k in n}
    out["absoluteBoundingBox"] = n.get("absoluteBoundingBox")
    if "style" in n: out["style"] = n["style"]
    for k in ("fills","strokes"):
        if n.get(k): out[k] = n[k]
    if "strokeWeight" in n: out["strokeWeight"] = n["strokeWeight"]
    print(json.dumps(out, ensure_ascii=False, indent=2))

def find(kw):
    for nid, n in NODES.items():
        if kw.lower() in n["name"].lower() or kw in (n.get("characters") or ""):
            rx, ry, w, h = rel(n)
            print(f"{nid:>12} {n['type'][:9]:<9} {n['name'][:44]:<44} {w:7.1f}x{h:8.1f}  父={n.get('_parent')}")

cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
if cmd == "tree":  tree(sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 3)
elif cmd == "spec": spec(sys.argv[2])
elif cmd == "find": find(sys.argv[2])
else: print(__doc__)
