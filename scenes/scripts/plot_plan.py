#!/usr/bin/env python3
"""Annotated metric plots of the as-built plans, for room identification & QA."""
import json, os, sys
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
G = json.load(open(os.path.join(ROOT,'logs','asbuilt_geometry.json')))
OUT = sys.argv[1] if len(sys.argv)>1 else os.path.join(ROOT,'logs')
COL = {'walls':('#111111',1.6),'doors':('#c02020',0.8),'windows':('#1060c0',1.0),
       'stairs':('#808080',0.7),'fixtures':('#00a000',0.9)}
for tag,d in G.items():
    fig,ax = plt.subplots(figsize=(20,13))
    for key,(c,lw) in COL.items():
        for x0,y0,x1,y1 in d.get(key,[]):
            ax.plot([x0/1000,x1/1000],[y0/1000,y1/1000],color=c,lw=lw,solid_capstyle='butt')
    import numpy as np
    for key,c in (('door_arcs','#c02020'),('fixture_arcs','#00a000')):
        for a in d.get(key,[]):
            t=np.linspace(np.radians(a['a0']),np.radians(a['a0']+((a['a1']-a['a0'])%360)),24)
            ax.plot(a['cx']/1000+a['r_mm']/1000*np.cos(t),
                    a['cy']/1000+a['r_mm']/1000*np.sin(t),color=c,lw=0.7)
    for dd in d.get('dims',[]):
        ax.annotate(f"{dd['value_mm']/1000:.2f}",(dd['x_mm']/1000,dd['y_mm']/1000),
                    fontsize=5.5,color='#b06000',ha='center')
    ex = d['extent_mm']
    ax.set_xticks([i*0.5 for i in range(0,int(ex[0]/500)+2)])
    ax.set_yticks([i*0.5 for i in range(0,int(ex[1]/500)+2)])
    ax.grid(True,which='major',color='#9ec8f0',lw=0.4)
    ax.set_xticklabels([f'{i*0.5:.1f}' if i%2==0 else '' for i in range(0,int(ex[0]/500)+2)],fontsize=6)
    ax.set_yticklabels([f'{i*0.5:.1f}' if i%2==0 else '' for i in range(0,int(ex[1]/500)+2)],fontsize=6)
    ax.set_aspect('equal'); ax.set_title(f'{tag} as-built (metres, origin = wall bbox min)')
    fig.tight_layout(); fig.savefig(os.path.join(OUT,f'plan_{tag}.png'),dpi=110)
    print('wrote', os.path.join(OUT,f'plan_{tag}.png'))
