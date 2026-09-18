#!/usr/bin/env python3
"""Canonical room schedule for the Bakri villa, derived from the as-built DWG.

IMPORTANT - the as-built drawings carry NO room-name text (verified: the DWG's
A_TEXT and ara-TEXT layers are empty; all 64 MTEXT entities are dimension
values). Room IDENTITY below is therefore INFERRED and tagged ASSUMED, with the
supporting evidence recorded per room. Room GEOMETRY is measured, not inferred.

Every rectangle is verified against the merged wall runs before use.
"""
import json, os, collections

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
G = json.load(open(os.path.join(ROOT,'logs','asbuilt_geometry.json')))
TOL = 60.0     # mm: how close a room edge must sit to a real wall run

# id: (floor, x0, y0, x1, y1, kind, inferred_identity, evidence)
SPACES = [
 ('FF-NW-BED', 'FF',   240,  6525,  3675, 10785, 'bedroom',
  'master_bedroom',
  'Two opposite walls measure exactly 4260 mm; BOQ items 31 and 33 are both '
  'joinery runs of W=4260 mm. Exact fit on both facing walls.'),
 ('FF-SW-BED', 'FF',   285,   225,  4215,  4395, 'bedroom', None,
  'Drawing dims 3.94 x 4.16. No 4260 wall -> cannot take BOQ item 31/33.'),
 ('FF-NE-BED', 'FF', 13095,  6135, 17235, 11085, 'bedroom', None,
  'Drawing dims 4.14 x 4.95.'),
 ('FF-SE-BED', 'FF', 13185,   630, 17370,  5895, 'bedroom', None,
  'Drawing dims 4.18 x 5.27. Largest bedroom on the floor.'),
 ('FF-BATH-W', 'FF',   285,  4530,  2480,  6285, 'bathroom', None,
  'Shower tray + WC + basin. Drawing dim 1.76 = measured 1755 mm.'),
 ('FF-BATH-S', 'FF',  4365,   225,  5715,  2655, 'bathroom', None,
  'Shower tray + WC + basin. Drawing dim 2.43 = measured 2430 mm.'),
 ('FF-BATH-C', 'FF',  8535,  3210, 11340,  4545, 'bathroom', None,
  'Shower tray + WC + basin. Drawing dims 2.79 / 1.33.'),
 ('FF-BATH-N', 'FF',  8685,  8130, 10245, 11085, 'bathroom', None,
  'Shower tray + WC + basin, off the stair landing.'),
 ('FF-STAIR',  'FF',  5910,  6290,  8460,  9790, 'circulation', 'hallways',
  'Stair flight on layer A_STAIR; the only vertical circulation.'),
 ('FF-VOID',   'FF',  4395,  6290,  5685,  9790, 'void', None,
  'Cross-hatched box on the plan - slab void / shaft. Not habitable.'),
 ('FF-RM-S1',  'FF',  5910,   630,  8340,  3010, 'room', None,
  'Contains a hatched square (duct/void). Drawing dim 2.47.'),
 ('FF-RM-S2',  'FF',  8535,   630,  9915,  2595, 'room', None,
  'Drawing dim 1.97 = measured 1965 mm.'),
 ('FF-RM-S3',  'FF', 10125,   630, 13035,  2595, 'room', None,
  'Drawing dims 2.92 / 1.97.'),
 ('GF-WEST',   'GF',   285,   250,  5710, 10790, 'open shell', None,
  'Unpartitioned. No internal walls drawn over 57 m2.'),
 ('GF-EAST',   'GF', 11265,   240, 17325,  9790, 'open shell', 'entrance_salon',
  'Main entrance door (1095 mm leaf, largest on the drawing) opens into this '
  'space. 5425 mm clear wall can take BOQ item 1 (cladding W=5000).'),
 ('GF-WC',     'GF',  8700,  5895, 10930,  9790, 'wc', None,
  'Red "NOT THE ACTUAL AS-BUILT" hatch covers this block - see conflict C-02.'),
 ('GF-STAIR',  'GF',  5910,  6290,  8460,  9790, 'circulation', None,
  'Stair flight, aligns with FF-STAIR.'),
]

def wall_runs(floor, axis):
    d = G[floor]; out = collections.defaultdict(list)
    for x0,y0,x1,y1 in d['walls']:
        if axis=='H' and abs(y1-y0)<=15 and abs(x1-x0)>15:
            out[(y0+y1)/2].append((min(x0,x1),max(x0,x1)))
        if axis=='V' and abs(x1-x0)<=15 and abs(y1-y0)>15:
            out[(x0+x1)/2].append((min(y0,y1),max(y0,y1)))
    return out

def edge_supported(runs, pos, lo, hi, cover=0.55):
    """Is at least `cover` of the span [lo,hi] backed by a wall near `pos`?"""
    best = 0.0
    for k, spans in runs.items():
        if abs(k-pos) > TOL: continue
        cov = sum(max(0.0, min(hi,e)-max(lo,s)) for s,e in spans)
        best = max(best, cov)
    return best/(hi-lo) if hi > lo else 0.0

def verify():
    rows = []
    for rid, fl, x0, y0, x1, y1, kind, ident, ev in SPACES:
        V = wall_runs(fl,'V'); H = wall_runs(fl,'H')
        cov = {
            'W': edge_supported(V, x0, y0, y1),
            'E': edge_supported(V, x1, y0, y1),
            'S': edge_supported(H, y0, x0, x1),
            'N': edge_supported(H, y1, x0, x1),
        }
        rows.append({'id': rid, 'floor': fl, 'kind': kind,
                     'identity_inferred': ident,
                     'bbox_mm': [x0,y0,x1,y1],
                     'size_mm': [x1-x0, y1-y0],
                     'area_m2': round((x1-x0)*(y1-y0)/1e6, 2),
                     'perimeter_m': round(2*((x1-x0)+(y1-y0))/1000, 2),
                     'wall_coverage': {k: round(v,2) for k,v in cov.items()},
                     'verified': all(v >= 0.5 for v in cov.values()),
                     'evidence': ev})
    return rows

def main():
    rows = verify()
    print(f'{"id":11} {"size mm":14} {"area":>7} {"perim":>7}  cover W/E/S/N   ok')
    for r in rows:
        c = r['wall_coverage']
        print(f'{r["id"]:11} {r["size_mm"][0]:5} x {r["size_mm"][1]:5} '
              f'{r["area_m2"]:7.2f} {r["perimeter_m"]:7.2f}  '
              f'{c["W"]:.2f}/{c["E"]:.2f}/{c["S"]:.2f}/{c["N"]:.2f}  '
              f'{"OK" if r["verified"] else "CHECK"}')
    p = os.path.join(ROOT,'logs','room_schedule.json')
    json.dump(rows, open(p,'w'), indent=1)
    print('wrote', p)

if __name__ == '__main__':
    main()
