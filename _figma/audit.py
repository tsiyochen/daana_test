#!/usr/bin/env python3
import json, glob, sys, os
ROOT_DIR=os.path.dirname(os.path.abspath(__file__))
NODES={}; ORDER=[]
for f in glob.glob(os.path.join(ROOT_DIR,"node_*.json")):
    d=json.load(open(f))
    for nid,w in d.get("nodes",{}).items():
        def walk(n,p=None,depth=0):
            n['_p']=p; n['_d']=depth; NODES[n["id"]]=n; ORDER.append(n["id"])
            for c in n.get("children",[]): walk(c,n["id"],depth+1)
        walk(w["document"])

def abox(n):
    b=n.get("absoluteBoundingBox") or {}
    return b.get("x",0),b.get("y",0),b.get("width",0),b.get("height",0)

def hexf(c): return '#%02X%02X%02X'%tuple(round(c.get(k,0)*255) for k in 'rgb')

def fills(n):
    out=[]
    for fl in n.get("fills",[]):
        if not fl.get("visible",True): continue
        t=fl.get("type")
        if t=="SOLID": out.append(f'{hexf(fl["color"])}@{fl.get("opacity",1):g}')
        elif t=="IMAGE": out.append(f'IMG:{fl.get("imageRef","")[:12]}/{fl.get("scaleMode")}')
        elif "GRADIENT" in (t or ""): out.append(t)
    return ','.join(out)

def desc(n):
    x,y,w,h=abox(n); s=''
    if n.get("layoutMode","NONE")!="NONE":
        pad='/'.join(f'{n.get(k,0):g}' for k in ("paddingTop","paddingRight","paddingBottom","paddingLeft"))
        s+=f' [{n["layoutMode"][0]} gap={n.get("itemSpacing",0):g} pad={pad}]'
    if n["type"]=="TEXT":
        st=n["style"]
        s+=f' «{st.get("fontFamily")} w{st.get("fontWeight")} {st.get("fontSize"):g}/{st.get("lineHeightPx",0):.0f} ls{st.get("letterSpacing",0):g}»'
        s+=f' 「{n["characters"][:70]}」'
    f=fills(n)
    if f: s+=f' fill={f}'
    if n.get("cornerRadius"): s+=f' r={n["cornerRadius"]:g}'
    return f'{n["id"]:>14} {n["type"][:9]:<9} {n["name"][:30]:<30} {w:7.1f}x{h:7.1f}{s}'

root=sys.argv[1]; maxd=int(sys.argv[2]) if len(sys.argv)>2 else 99
def rec(nid,d=0):
    n=NODES[nid]
    print('  '*d+desc(n))
    if d<maxd:
        for c in n.get("children",[]): rec(c["id"],d+1)
rec(root)
