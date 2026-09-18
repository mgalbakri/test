#!/usr/bin/env python3
"""Annotated space key: the as-built plans with every measured space labelled.

The drawings carry no room names, so this is the sheet the owner marks up to
tell us which space is which. Idempotent.
"""
import json, os
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
G = json.load(open(os.path.join(ROOT,'logs','asbuilt_geometry.json')))
R = json.load(open(os.path.join(ROOT,'logs','room_schedule.json')))
OUT = os.path.join(ROOT,'logs')

KIND_COL = {'bedroom':'#cfe3f7','bathroom':'#d6f0dc','circulation':'#f7e8c8',
            'void':'#e2e2e2','room':'#efe0f0','open shell':'#fde2d6','wc':'#d6f0dc'}

for floor in ('GF','FF'):
    d = G[floor]
    fig, ax = plt.subplots(figsize=(19, 13))
    for r in R:
        if r['floor'] != floor: continue
        x0,y0,x1,y1 = [v/1000 for v in r['bbox_mm']]
        ax.add_patch(Rectangle((x0,y0), x1-x0, y1-y0,
                     facecolor=KIND_COL.get(r['kind'],'#eeeeee'),
                     edgecolor='#4a6fa5', lw=1.4, alpha=0.75, zorder=1))
        cx, cy = (x0+x1)/2, (y0+y1)/2
        ident = r['identity_inferred']
        label = (f"{r['id']}\n{r['size_mm'][0]} x {r['size_mm'][1]} mm\n"
                 f"{r['area_m2']:.1f} m²")
        if ident:
            label += f"\n[assumed: {ident.replace('_',' ')}]"
        ax.text(cx, cy, label, ha='center', va='center', fontsize=8.5,
                zorder=5, linespacing=1.5,
                bbox=dict(boxstyle='round,pad=0.42', fc='white', ec='#4a6fa5',
                          alpha=0.94, lw=0.9))
    for key,(c,lw) in {'walls':('#111111',1.7),'doors':('#c02020',0.8),
                       'windows':('#1060c0',1.2),'stairs':('#888888',0.7),
                       'fixtures':('#00901f',1.0)}.items():
        for x0,y0,x1,y1 in d.get(key,[]):
            ax.plot([x0/1000,x1/1000],[y0/1000,y1/1000],color=c,lw=lw,
                    zorder=3, solid_capstyle='butt')
    for k,c in (('door_arcs','#c02020'),('fixture_arcs','#00901f')):
        for a in d.get(k,[]):
            t = np.linspace(np.radians(a['a0']),
                            np.radians(a['a0']+((a['a1']-a['a0'])%360)), 24)
            ax.plot(a['cx']/1000+a['r_mm']/1000*np.cos(t),
                    a['cy']/1000+a['r_mm']/1000*np.sin(t), color=c, lw=0.8, zorder=3)
    ex = d['extent_mm']
    ax.set_xlim(-0.6, ex[0]/1000+0.6); ax.set_ylim(-0.6, ex[1]/1000+0.6)
    ax.set_aspect('equal')
    ax.set_xlabel('metres'); ax.set_ylabel('metres')
    ax.grid(True, color='#cfe0f5', lw=0.4, zorder=0)
    name = {'GF':'GROUND FLOOR','FF':'FIRST FLOOR'}[floor]
    ax.set_title(f'{name} - space key (as-built DWG, no room names in source)\n'
                 'Please mark which space is which; north is NOT given on the '
                 'drawings (conflict C-05)', fontsize=13)
    ax.text(0.01, -0.075,
            'Each box gives the space ID, its measured clear size and its floor '
            'area, taken from the as-built DWG. Colours group space types only.\n'
            'Where a space is open on one side (a cased opening, a stair, or a '
            'run of circulation), its boundary is taken from the adjoining walls; '
            'logs/room_schedule.json records how much of each side is backed by '
            'a real wall.',
            transform=ax.transAxes, fontsize=8.5, va='top', color='#333333')
    fig.tight_layout()
    p = os.path.join(OUT, f'space_key_{floor}.png')
    fig.savefig(p, dpi=105); plt.close(fig)
    print('wrote', p)
