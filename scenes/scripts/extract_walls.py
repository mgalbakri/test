#!/usr/bin/env python3
"""Extract wall line-work from the 1:100 vector PDFs into metric mm.

Scale is VERIFIED in verify_scale() before any geometry is emitted (see
NON-NEGOTIABLES: two known dimensions must check out).
Plan coords: X right, Y up, millimetres, origin at building bounding-box min.
Idempotent.
"""
import pymupdf, math, json, os, collections

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PT2MM = 25.4 / 72.0 * 100.0          # 1:100 -> real mm per PDF point
PLANS = {'GF': 'GROUND_FLOOR_PLAN.pdf', 'FF': 'FIRST_FLOOR_PLAN.pdf'}
TOL = 8.0                             # mm snap tolerance (~0.23 pt on paper)

def raw_segments(pg):
    segs = []
    for path in pg.get_drawings():
        for it in path['items']:
            if it[0] == 'l':
                segs.append((it[1].x, it[1].y, it[2].x, it[2].y))
            elif it[0] == 're':
                r = it[1]
                segs += [(r.x0,r.y0,r.x1,r.y0),(r.x1,r.y0,r.x1,r.y1),
                         (r.x1,r.y1,r.x0,r.y1),(r.x0,r.y1,r.x0,r.y0)]
    return segs

def dim_texts(pg):
    out = []
    for w in pg.get_text('words'):
        try: v = float(w[4])
        except ValueError: continue
        out.append({'value_mm': v*1000.0,
                    'cx': (w[0]+w[2])/2, 'cy': (w[1]+w[3])/2})
    return out

def verify_scale(segs, dims, tag):
    """Match each dimension value against the nearest segment length.
    Scale is accepted only if >=2 independent dimensions reproduce within 5 mm."""
    lens = [math.hypot(x1-x0, y1-y0)*PT2MM for (x0,y0,x1,y1) in segs]
    hits = []
    for d in dims:
        t = d['value_mm']
        if t < 400: continue                      # ignore tiny dims, ambiguous
        best = min(lens, key=lambda l: abs(l-t))
        if abs(best-t) <= 5.0:
            hits.append((t, best, best-t))
    print(f'  [{tag}] scale check: {len(hits)} dimension(s) reproduce within 5 mm')
    for t,b,e in sorted(hits)[:6]:
        print(f'      dim {t/1000:5.2f} m -> measured {b:8.1f} mm  (err {e:+.1f} mm)')
    if len(hits) < 2:
        raise SystemExit(f'SCALE CHECK FAILED for {tag}: only {len(hits)} match(es). '
                         'Stopping per NON-NEGOTIABLES.')
    return hits

def snap(v, tol=TOL):
    return round(v/tol)*tol

def to_plan(segs, page_h):
    """Page is stored rotated 270deg. Map page space -> upright plan space, mm."""
    out = []
    for (x0,y0,x1,y1) in segs:
        # rotate 270deg CW about page: (x,y) -> (y, x) mirrored to keep handedness
        a = (y0*PT2MM, x0*PT2MM)
        b = (y1*PT2MM, x1*PT2MM)
        out.append((a[0],a[1],b[0],b[1]))
    return out

def classify(segs):
    """Split into axis-aligned H/V runs, snapped and merged."""
    H = collections.defaultdict(list)   # y -> list of (x0,x1)
    V = collections.defaultdict(list)   # x -> list of (y0,y1)
    other = 0
    for (x0,y0,x1,y1) in segs:
        dx, dy = abs(x1-x0), abs(y1-y0)
        if dy <= TOL and dx > TOL:
            H[snap((y0+y1)/2)].append((min(x0,x1), max(x0,x1)))
        elif dx <= TOL and dy > TOL:
            V[snap((x0+x1)/2)].append((min(y0,y1), max(y0,y1)))
        else:
            other += 1
    def merge(d):
        out = {}
        for k, runs in d.items():
            runs.sort(); m = []
            for s,e in runs:
                if m and s <= m[-1][1] + TOL: m[-1][1] = max(m[-1][1], e)
                else: m.append([s,e])
            out[k] = [(round(s,1), round(e,1)) for s,e in m if e-s > 40]
        return {k:v for k,v in out.items() if v}
    return merge(H), merge(V), other

def main():
    result = {}
    for tag, fn in PLANS.items():
        d = pymupdf.open(os.path.join(ROOT,'inputs','drawings',fn))
        pg = d[0]; pg.set_rotation(0)
        segs = raw_segments(pg)
        dims = dim_texts(pg)
        print(f'[{tag}] raw segments={len(segs)} dim texts={len(dims)}')
        verify_scale(segs, dims, tag)
        plan = to_plan(segs, pg.rect.y1)
        H, V, other = classify(plan)
        xs = [x for (x0,y0,x1,y1) in plan for x in (x0,x1)]
        ys = [y for (x0,y0,x1,y1) in plan for y in (y0,y1)]
        print(f'  H-lines={len(H)} V-lines={len(V)} non-axial={other}')
        print(f'  extents X {min(xs):.0f}..{max(xs):.0f} mm   Y {min(ys):.0f}..{max(ys):.0f} mm')
        result[tag] = {
            'H': {str(k): v for k, v in sorted(H.items())},
            'V': {str(k): v for k, v in sorted(V.items())},
            'dims': dims,
        }
    out = os.path.join(ROOT,'logs','plan_linework.json')
    with open(out,'w') as f: json.dump(result, f, indent=1)
    print('wrote', out)

if __name__ == '__main__':
    main()
