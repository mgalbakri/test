#!/usr/bin/env python3
"""Extract as-built geometry from the DWG (converted to DXF) into metric JSON.

The DWG is the GOVERNING source for geometry (source hierarchy rule 1).
It holds BOTH floor plans side by side in one modelspace:
    FIRST FLOOR PLAN  viewport title @ x ~= 306.25
    GROUND FLOOR PLAN viewport title @ x ~= 338.70
Units are METRES - verified in verify_units() against the drawing's own
DIMENSION entities, which return the same values printed on the PDFs.

Outputs logs/asbuilt_geometry.json with per-floor, origin-normalised mm coords.
Idempotent.
"""
import ezdxf, json, math, os, collections

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DXF  = os.path.join(ROOT, 'inputs', 'drawings', 'AS-BUILT_FLOOR_PLAN.dxf')
SPLIT_X = 322.5                      # between the two viewports
M2MM = 1000.0

WALL_LAYERS    = {'A_WALL'}
DOOR_LAYERS    = {'A_DOOR'}
WINDOW_LAYERS  = {'A_WINDOW'}
STAIR_LAYERS   = {'A_STAIR'}
FIXTURE_LAYERS = {'A-FIXTURES', 'A_fixtures', 'sink'}

def verify_units(msp):
    """The drawing's own DIMENSION entities must reproduce the PDF dimension
    text. If they do, model units are metres. Two independent checks minimum."""
    dims = []
    for e in msp.query('DIMENSION'):
        try: m = e.get_measurement()
        except Exception: continue
        if isinstance(m, (int, float)) and m > 0:
            dims.append(float(m))
    known = {3.43, 4.26, 3.91, 4.95, 6.47, 5.27, 7.01, 9.55, 5.02}
    hits = sorted({round(d, 2) for d in dims} & known)
    print(f'  unit check: {len(dims)} DIMENSION entities; '
          f'{len(hits)} match known PDF dimensions exactly: {hits}')
    if len(hits) < 2:
        raise SystemExit('UNIT/SCALE CHECK FAILED - stopping per NON-NEGOTIABLES.')
    span = max(dims)
    if not (1.0 < span < 60.0):
        raise SystemExit(f'UNIT CHECK FAILED: max dimension {span} not metre-like.')
    return dims

def _iter_entities(msp, depth=3):
    """Yield modelspace entities, exploding INSERTs so block content
    (sanitary ware, door leaves, stair runs) is not lost."""
    for e in msp:
        if e.dxftype() == 'INSERT' and depth > 0:
            try: virt = list(e.virtual_entities())
            except Exception: virt = []
            for v in virt:
                if v.dxftype() == 'INSERT' and depth > 1:
                    try:
                        for w in v.virtual_entities(): yield w
                    except Exception: pass
                else:
                    yield v
        else:
            yield e

def seg_list(msp, layers, lo, hi):
    """Axis-agnostic segment extraction for LINE + LWPOLYLINE on given layers."""
    out = []
    for e in _iter_entities(msp):
        if e.dxf.layer not in layers: continue
        t = e.dxftype()
        if t == 'LINE':
            a, b = e.dxf.start, e.dxf.end
            pts = [(a.x, a.y), (b.x, b.y)]
        elif t == 'LWPOLYLINE':
            pts = [(p[0], p[1]) for p in e.get_points('xy')]
            if e.closed and len(pts) > 2: pts.append(pts[0])
        else:
            continue
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            if lo <= (x0+x1)/2 < hi:
                out.append((x0, y0, x1, y1))
    return out

def arcs(msp, layers, lo, hi):
    out = []
    for e in _iter_entities(msp):
        if e.dxftype() != 'ARC' or e.dxf.layer not in layers: continue
        c = e.dxf.center
        if lo <= c.x < hi:
            out.append({'cx': c.x, 'cy': c.y, 'r': e.dxf.radius,
                        'a0': e.dxf.start_angle, 'a1': e.dxf.end_angle})
    return out

def dims_in(msp, lo, hi):
    out = []
    for e in msp.query('DIMENSION'):
        try: m = float(e.get_measurement())
        except Exception: continue
        p = e.dxf.defpoint
        if lo <= p.x < hi:
            out.append({'value_mm': round(m*M2MM, 1), 'x': p.x, 'y': p.y})
    return out

def norm(segs, ox, oy):
    return [[round((x0-ox)*M2MM,1), round((y0-oy)*M2MM,1),
             round((x1-ox)*M2MM,1), round((y1-oy)*M2MM,1)] for x0,y0,x1,y1 in segs]

def main():
    d = ezdxf.readfile(DXF)
    msp = d.modelspace()
    print('DXF', d.dxfversion, 'entities', len(msp))
    verify_units(msp)

    floors = {'FF': (0.0, SPLIT_X), 'GF': (SPLIT_X, 1e9)}
    out = {}
    for tag, (lo, hi) in floors.items():
        walls  = seg_list(msp, WALL_LAYERS,   lo, hi)
        doors  = seg_list(msp, DOOR_LAYERS,   lo, hi)
        wins   = seg_list(msp, WINDOW_LAYERS, lo, hi)
        stairs = seg_list(msp, STAIR_LAYERS,  lo, hi)
        fixt   = seg_list(msp, FIXTURE_LAYERS,lo, hi)
        if not walls:
            print(f'[{tag}] no walls found'); continue
        xs = [v for s in walls for v in (s[0], s[2])]
        ys = [v for s in walls for v in (s[1], s[3])]
        ox, oy = min(xs), min(ys)
        out[tag] = {
            'origin_dxf': [round(ox,4), round(oy,4)],
            'extent_mm': [round((max(xs)-ox)*M2MM,1), round((max(ys)-oy)*M2MM,1)],
            'walls':   norm(walls, ox, oy),
            'doors':   norm(doors, ox, oy),
            'windows': norm(wins, ox, oy),
            'stairs':  norm(stairs, ox, oy),
            'fixtures':norm(fixt, ox, oy),
            'fixture_arcs': [{'cx': round((a['cx']-ox)*M2MM,1),
                              'cy': round((a['cy']-oy)*M2MM,1),
                              'r_mm': round(a['r']*M2MM,1),
                              'a0': round(a['a0'],1), 'a1': round(a['a1'],1)}
                             for a in arcs(msp, FIXTURE_LAYERS, lo, hi)],
            'door_arcs': [{'cx': round((a['cx']-ox)*M2MM,1),
                           'cy': round((a['cy']-oy)*M2MM,1),
                           'r_mm': round(a['r']*M2MM,1),
                           'a0': round(a['a0'],1), 'a1': round(a['a1'],1)}
                          for a in arcs(msp, DOOR_LAYERS, lo, hi)],
            'dims': [{'value_mm': dd['value_mm'],
                      'x_mm': round((dd['x']-ox)*M2MM,1),
                      'y_mm': round((dd['y']-oy)*M2MM,1)}
                     for dd in dims_in(msp, lo, hi)],
        }
        print(f'[{tag}] walls={len(walls)} doors={len(doors)} windows={len(wins)} '
              f'stairs={len(stairs)} fixtures={len(fixt)} dims={len(out[tag]["dims"])}')
        print(f'      extent {out[tag]["extent_mm"][0]:.0f} x {out[tag]["extent_mm"][1]:.0f} mm')
        leaves = sorted({a['r_mm'] for a in out[tag]['door_arcs']})
        print(f'      door leaf radii (mm): {leaves}')

    p = os.path.join(ROOT, 'logs', 'asbuilt_geometry.json')
    with open(p, 'w') as f: json.dump(out, f, indent=1)
    print('wrote', p)

if __name__ == '__main__':
    main()
