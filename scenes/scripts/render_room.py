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
ceilings = [o for o in bpy.data.objects if o.name.startswith('CEIL_')]
for c in cams:
    plan = 'PLAN' in c.name.upper()
    # The plan camera looks straight down from above the slab, so the ceiling
    # has to be hidden or every plan render is a flat grey rectangle.
    for o in ceilings:
        o.hide_render = plan
    if plan:
        name = f'{room}_plan'
        # Match the frame aspect to the room, then ortho_scale = the longer
        # side. Otherwise Blender crops whichever axis is not the long one.
        pw, ph = c.get('plan_w_m'), c.get('plan_h_m')
        if pw and ph:
            base = 1920 if draft else 3840
            if pw >= ph:
                bpy.context.scene.render.resolution_x = base
                bpy.context.scene.render.resolution_y = max(2, int(round(base*ph/pw)))
                c.data.ortho_scale = pw
            else:
                bpy.context.scene.render.resolution_y = base
                bpy.context.scene.render.resolution_x = max(2, int(round(base*pw/ph)))
                c.data.ortho_scale = ph
            plan_res = (bpy.context.scene.render.resolution_x,
                        bpy.context.scene.render.resolution_y)
        else:
            plan_res = None
    else:
        parts = c.name.split('_')
        name = f'{room}_cam{parts[1]}'
    path = os.path.join(outdir, f'{name}.png')
    t = time.time()
    if plan and plan_res:
        sc = bpy.context.scene
        sc.camera = c
        V.set_quality(draft=draft, time_limit=secs)
        sc.render.resolution_x, sc.render.resolution_y = plan_res
        os.makedirs(os.path.dirname(path), exist_ok=True)
        sc.render.filepath = path
        bpy.ops.render.render(write_still=True)
    else:
        V.render_to(c, path, draft=draft, samples=None, time_limit=secs)
    st = V.frame_stats(path)
    flag = ''
    if st['lit_pct'] < 5.0:    flag = '  **QA FAIL: frame is black**'
    elif st['blown_pct'] > 5.0: flag = '  **QA FAIL: highlights blown**'
    print(f'RENDERED {name} in {time.time()-t:.0f}s  mean={st["mean"]:.3f} '
          f'lit={st["lit_pct"]:.1f}% blown={st["blown_pct"]:.2f}%{flag} -> {path}',
          flush=True)
print('ALL_RENDERS_DONE', flush=True)
