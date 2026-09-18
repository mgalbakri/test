#!/usr/bin/env python3
"""Find enclosed rooms in the as-built plans by rasterising the wall linework
and flood-filling. Emits each room's bounding box, area and centroid in mm,
plus which sanitary fixtures fall inside it. Idempotent.
"""
import json, os, sys, collections
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
G = json.load(open(os.path.join(ROOT, 'logs', 'asbuilt_geometry.json')))
RES = 25.0                    # mm per raster cell
GAP = int(os.environ.get('GAP','2'))   # dilation radius in cells (25mm each)
MIN_AREA_M2 = 1.2

def raster(segs, W, H, pad):
    grid = np.zeros((H, W), dtype=bool)
    for x0, y0, x1, y1 in segs:
        n = int(max(abs(x1-x0), abs(y1-y0))/RES*2) + 2
        for i in range(n+1):
            t = i/n
            cx = int((x0 + (x1-x0)*t)/RES) + pad
            cy = int((y0 + (y1-y0)*t)/RES) + pad
            if 0 <= cx < W and 0 <= cy < H:
                grid[cy, cx] = True
    return grid

def dilate(g, k=1):
    out = g.copy()
    for dy in range(-k, k+1):
        for dx in range(-k, k+1):
            out |= np.roll(np.roll(g, dy, 0), dx, 1)
    return out

def flood_regions(blocked):
    H, W = blocked.shape
    lab = np.full((H, W), -1, dtype=np.int32)
    regions = []
    for sy in range(H):
        for sx in range(W):
            if blocked[sy, sx] or lab[sy, sx] >= 0: continue
            rid = len(regions)
            stack = [(sy, sx)]; lab[sy, sx] = rid
            cells = []
            while stack:
                y, x = stack.pop()
                cells.append((y, x))
                for dy, dx in ((1,0),(-1,0),(0,1),(0,-1)):
                    ny, nx = y+dy, x+dx
                    if 0 <= ny < H and 0 <= nx < W and not blocked[ny,nx] and lab[ny,nx] < 0:
                        lab[ny,nx] = rid; stack.append((ny,nx))
            regions.append(cells)
    return regions, lab

def main():
    out = {}
    for tag, d in G.items():
        # doors are included as BARRIERS: their leaf + jamb linework closes
        # the wall gaps at openings, otherwise the fill leaks between rooms.
        segs = d['walls'] + d['windows'] + d['stairs'] + d['doors']
        ex = d['extent_mm']
        pad = 4
        W = int(ex[0]/RES) + 2*pad + 2
        H = int(ex[1]/RES) + 2*pad + 2
        g = raster(segs, W, H, pad)
        for a in d.get('door_arcs', []):   # close swing gaps with the chord
            pass
        g = dilate(g, GAP)
        regions, lab = flood_regions(g)
        # outside = the region touching the border
        border = set()
        for x in range(W):
            if lab[0,x] >= 0: border.add(lab[0,x])
            if lab[H-1,x] >= 0: border.add(lab[H-1,x])
        for y in range(H):
            if lab[y,0] >= 0: border.add(lab[y,0])
            if lab[y,W-1] >= 0: border.add(lab[y,W-1])
        # fixture points (arc centres + segment midpoints)
        fx = [((a['cx']), (a['cy'])) for a in d.get('fixture_arcs', [])]
        fx += [(((s[0]+s[2])/2), ((s[1]+s[3])/2)) for s in d.get('fixtures', [])]
        rooms = []
        for rid, cells in enumerate(regions):
            if rid in border: continue
            area = len(cells)*RES*RES/1e6
            if area < MIN_AREA_M2: continue
            ys = [c[0] for c in cells]; xs = [c[1] for c in cells]
            x0 = (min(xs)-pad)*RES; x1 = (max(xs)-pad+1)*RES
            y0 = (min(ys)-pad)*RES; y1 = (max(ys)-pad+1)*RES
            cxm = (sum(xs)/len(xs)-pad)*RES; cym = (sum(ys)/len(ys)-pad)*RES
            nf = sum(1 for (px,py) in fx if x0 <= px <= x1 and y0 <= py <= y1)
            rooms.append({'id': f'{tag}-R{len(rooms)+1:02d}',
                          'bbox_mm': [round(x0), round(y0), round(x1), round(y1)],
                          'size_mm': [round(x1-x0), round(y1-y0)],
                          'area_m2': round(area, 2),
                          'rect_fill_pct': round(area/((x1-x0)*(y1-y0)/1e6)*100, 1),
                          'centroid_mm': [round(cxm), round(cym)],
                          'fixtures_inside': nf})
        rooms.sort(key=lambda r: -r['area_m2'])
        out[tag] = rooms
        print(f'===== {tag}: {len(rooms)} enclosed spaces >= {MIN_AREA_M2} m2')
        print(f'{"id":9} {"bbox (mm)":34} {"w x d":14} {"area":>7} {"fill%":>6} {"fix":>4}')
        for r in rooms:
            b = r['bbox_mm']
            print(f'{r["id"]:9} [{b[0]:6},{b[1]:6} -> {b[2]:6},{b[3]:6}] '
                  f'{r["size_mm"][0]:5} x {r["size_mm"][1]:5} {r["area_m2"]:7.2f} '
                  f'{r["rect_fill_pct"]:6.1f} {r["fixtures_inside"]:4}')
    p = os.path.join(ROOT, 'logs', 'detected_rooms.json')
    json.dump(out, open(p,'w'), indent=1)
    print('wrote', p)

if __name__ == '__main__':
    main()
