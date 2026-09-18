"""Render every camera in an already-open .blend.

Usage:
  blender -b scenes/<room>.blend -P scenes/scripts/render_room.py \
      -- <room> [draft|final] [seconds_per_frame]

Frames are time-boxed (Cycles time_limit) because this box renders on 4 weak
CPU cores; adaptive sampling + OpenImageDenoise carry the remainder.
Idempotent: overwrites renders/<room>_*.png.
"""
import bpy, sys, os, time
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import villa_lib as V

argv  = sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
room  = argv[0] if argv else 'room'
mode  = argv[1] if len(argv) > 1 else 'draft'
secs  = float(argv[2]) if len(argv) > 2 else (150.0 if mode == 'draft' else 600.0)
draft = (mode == 'draft')

cams = sorted((o for o in bpy.data.objects if o.type == 'CAMERA'), key=lambda o: o.name)
outdir = os.path.join(ROOT, 'renders')
print(f'RENDERING {room} [{mode}] {len(cams)} cameras, {secs:.0f}s/frame', flush=True)
for c in cams:
    if 'PLAN' in c.name.upper():
        name = f'{room}_plan'
    else:
        parts = c.name.split('_')
        name = f'{room}_cam{parts[1]}'
    path = os.path.join(outdir, f'{name}.png')
    t = time.time()
    V.render_to(c, path, draft=draft, samples=None, time_limit=secs)
    print(f'RENDERED {name} in {time.time()-t:.0f}s -> {path}', flush=True)
print('ALL_RENDERS_DONE', flush=True)
