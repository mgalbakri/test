#!/usr/bin/env python3
"""Merge the as-built wall linework into axis-aligned runs, so room rectangles
can be snapped to real wall faces rather than eyeballed. mm throughout."""
import json, os, sys, collections
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
G = json.load(open(os.path.join(ROOT,'logs','asbuilt_geometry.json')))
TOL = 15.0

def runs(segs, axis):
    d = collections.defaultdict(list)
    for x0,y0,x1,y1 in segs:
        if axis=='H' and abs(y1-y0)<=TOL and abs(x1-x0)>TOL:
            d[round((y0+y1)/2/TOL)*TOL].append((min(x0,x1),max(x0,x1)))
        if axis=='V' and abs(x1-x0)<=TOL and abs(y1-y0)>TOL:
            d[round((x0+x1)/2/TOL)*TOL].append((min(y0,y1),max(y0,y1)))
    out={}
    for k,v in d.items():
        v.sort(); m=[]
        for s,e in v:
            if m and s<=m[-1][1]+TOL: m[-1][1]=max(m[-1][1],e)
            else: m.append([s,e])
        m=[(round(s),round(e)) for s,e in m if e-s>150]
        if m: out[round(k)]=m
    return dict(sorted(out.items()))

tag = sys.argv[1] if len(sys.argv)>1 else 'FF'
d = G[tag]
for axis,label in (('V','VERTICAL walls  x = ... spans y'),('H','HORIZONTAL walls  y = ... spans x')):
    r = runs(d['walls'], axis)
    print(f'===== {tag} {label}  ({len(r)} positions)')
    for k,v in r.items():
        print(f'  {k:6}: ' + '  '.join(f'{s}-{e}' for s,e in v))
