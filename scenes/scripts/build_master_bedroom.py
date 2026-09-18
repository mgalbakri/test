"""Build scenes/master_bedroom.blend from the as-built DWG + BOQ R1-M.A.740-26.

Room: FF-NW-BED, first floor north-west.  Measured 3435 x 4260 mm clear.
IDENTITY IS ASSUMED - the as-built drawings carry no room names. Evidence:
this is the only first-floor bedroom whose facing walls measure exactly
4260 mm, and BOQ items 31 and 33 are both joinery runs of exactly W=4260 mm.

Run:  blender -b --factory-startup -P scenes/scripts/build_master_bedroom.py
Idempotent: clears and rebuilds the scene from scratch.
"""
import bpy, sys, os, math, json

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import villa_lib as V

Q = 'R1-M.A.740-26'
# ---- measured from the as-built DWG (mm), room-local origin at SW inside corner
W, D          = 3435, 4260          # clear width (X) x clear depth (Y)
CEIL          = 3000                # ASSUMED - see note below
EXT_T, PART_T = 240, 240            # measured external / partition thickness
WIN_X0, WIN_X1= -EXT_T, 0           # west external wall
WIN_Y0, WIN_Y1= 1450, 2450          # 1000 mm window, measured
WIN_SILL, WIN_HEAD = 900, 2400      # ASSUMED - no section/elevation supplied
DOOR_X0, DOOR_X1 = 2530, 3380       # 850 mm clear opening, measured
DOOR_H        = 2100                # ASSUMED - no section/elevation supplied
NICHE_X0, NICHE_X1 = W, W+480       # 480 mm deep wardrobe recess, measured
NICHE_Y0, NICHE_Y1 = 635, 3265      # 2630 mm wide, measured

ASSUMED_CEIL = ['ceiling height 3000 mm derived from BOQ items 31/33 (H=3000 '
                'floor-to-ceiling joinery); no section or elevation supplied']
ASSUMED_OPEN = ['window sill 900 / head 2400 mm', 'door height 2100 mm']

def build():
    V.reset_scene()
    V.setup_scene('master_bedroom')

    # ---------------------------------------------------------- materials
    paint   = V.mat_paint('PNT_Wall_Ceiling_Offwhite')
    beech   = V.mat_procedural_wood('WD_Beech_Veneer_Stain', base=(0.42,0.26,0.14))
    uphol   = V.mat_fabric('FAB_Headboard_Upholstery', base=(0.33,0.30,0.28))
    floor_m = V.mat_porcelain_tile('POR_Floor_600x1200', base=(0.74,0.71,0.67),
                                   tile_mm=(600,1200))
    glass   = V.mat_glass_clear()
    ph2_fab = V.mat_phase2('MBR_door_leaf_panel_wallpaper_or_fabric')
    ph2_lit = V.mat_phase2('MBR_lighting')

    # ---------------------------------------------------------- shell
    # The clear internal box is x 0..W, y 0..D, z 0..CEIL. Every wall is built
    # OUTSIDE that box (centreline offset by half its thickness), so the modelled
    # clear dimensions equal the measured clear dimensions.
    fl = V.floor_slab('FLR_MasterBedroom', 0, 0, W, D)
    V.assign(fl, floor_m)
    V.tag(fl, 'NONE', 'Confirmed',
          'Floor finish not in BOQ scope for this room (no flooring line item)')

    ce = V.ceiling_slab('CEIL_MasterBedroom', -EXT_T, -PART_T,
                        NICHE_X1 + PART_T, D + EXT_T, CEIL)
    V.assign(ce, paint)
    V.tag(ce, f'{Q}/NONE', 'Assumed',
          'No separate ceiling-paint line for this room in the BOQ',
          assumed=ASSUMED_CEIL)

    # name: (x0, y0, x1, y1, thickness) - coordinates are CENTRELINES
    shell = {
      'WALL_West_External':  (-EXT_T/2, 0, -EXT_T/2, D, EXT_T),
      'WALL_North_External': (0, D + EXT_T/2, W, D + EXT_T/2, EXT_T),
      'WALL_South_Partition':(0, -PART_T/2, W, -PART_T/2, PART_T),
    }
    for n, (x0, y0, x1, y1, th) in shell.items():
        w = V.wall(n, x0, y0, x1, y1, th, CEIL)
        V.assign(w, paint)
        V.tag(w, f'{Q}/NONE', 'Assumed',
              'Wall build-up measured from plan; no paint line for this room',
              assumed=ASSUMED_CEIL)

    # East side: two piers flanking the wardrobe recess, plus the recess back.
    EP = W + PART_T/2                      # pier centreline
    for n, y0, y1 in (('WALL_East_Pier_S', -PART_T, NICHE_Y0),
                      ('WALL_East_Pier_N', NICHE_Y1, D + EXT_T)):
        w = V.wall(n, EP, y0, EP, y1, PART_T, CEIL)
        V.assign(w, paint); V.tag(w, f'{Q}/NONE', 'Assumed', assumed=ASSUMED_CEIL)
    back = V.wall('WALL_East_RecessBack', NICHE_X1 + PART_T/2, NICHE_Y0,
                  NICHE_X1 + PART_T/2, NICHE_Y1, PART_T, CEIL)
    V.assign(back, paint); V.tag(back, f'{Q}/NONE', 'Assumed', assumed=ASSUMED_CEIL)

    # ---------------------------------------------------------- openings
    ww = bpy.data.objects['WALL_West_External']
    V.cut_opening(ww, -EXT_T-50, WIN_Y0, 50, WIN_Y1, WIN_SILL, WIN_HEAD, 'WIN_W')
    ww['ASSUMED'] = '; '.join(ASSUMED_OPEN)
    sw = bpy.data.objects['WALL_South_Partition']
    V.cut_opening(sw, DOOR_X0, -PART_T-50, DOOR_X1, 50, 0, DOOR_H, 'DOOR_S')
    sw['ASSUMED'] = '; '.join(ASSUMED_OPEN)

    gl = V.box('GLZ_Window_West', -EXT_T/2-8, WIN_Y0, WIN_SILL,
                                  -EXT_T/2+8, WIN_Y1, WIN_HEAD)
    V.assign(gl, glass)
    V.tag(gl, 'NONE', 'Assumed', 'Existing window, not in BOQ scope',
          assumed=ASSUMED_OPEN)

    # ------------------------------------------------- BOQ joinery (priced)
    # Item 31 - wardrobe run, BOQ W=4260 D=500 H=3000. The measured recess is
    # only 2630 mm wide and 480 mm deep, so the quoted run cannot be installed.
    # Modelled AS-MEASURED; the shortfall is carried as variance V-01.
    # "2 cabinet and upper samll cabinet and 2 side wall drawers ... solid Beech
    # wood moulding": four leaves with a separate upper tier, drawers at the ends.
    cab, cab_parts = V.cabinet_run(
        'JOI_Wardrobe_Run', W, NICHE_Y0, NICHE_X1, NICHE_Y1, CEIL, face='X-',
        leaves=4, plinth=100, plinth_set=40, gap=5, rail=70,
        panel_mat=ph2_fab, upper_band=600, drawers_at=[0, 3])
    for o in cab_parts:
        if o.data.materials: continue
        V.assign(o, beech)
    for o in cab_parts:
        V.tag(o, f'{Q}/31',
              'Phase 2' if o.name.endswith('_Panel') else 'Confirmed',
              'Door-leaf panel is wallpaper or fabric, priced separately'
              if o.name.endswith('_Panel') else
              'BOQ W=4260 D=500 H=3000; modelled to the measured 2630 x 480 mm '
              'recess. Shortfall 1630 mm - see variance V-01.')
        if o.name.endswith('_Panel'):
            o.name = o.name.replace('JOI_', 'PH2_')
    cab['boq_width_mm'] = 4260
    cab['modelled_width_mm'] = NICHE_Y1 - NICHE_Y0

    # Item 33 - TV-area run, BOQ W=4260 D=500 H=3000, on the facing wall. That
    # wall is 4260 long but carries a 1000 mm window, so the run is modelled as
    # two returns either side of the opening - variance V-02.
    HB_CLEAR = 120                      # keep the run clear of the headboard
    # "2 cabinet and lower Drawers and upper cabinet on either side of the TV"
    for n, y0, y1, dwr in (('JOI_TV_Run_S', 0, WIN_Y0, [0]),
                           ('JOI_TV_Run_N', WIN_Y1, D - HB_CLEAR, [1])):
        if y1 - y0 < 200: continue
        car, parts = V.cabinet_run(n, 0, y0, 500, y1, CEIL, face='X+',
                                   leaves=2, plinth=100, plinth_set=40, gap=5,
                                   rail=70, panel_mat=ph2_fab, upper_band=600,
                                   drawers_at=dwr)
        for o in parts:
            if not o.data.materials: V.assign(o, beech)
            V.tag(o, f'{Q}/33',
                  'Phase 2' if o.name.endswith('_Panel') else 'Confirmed',
                  'Door-leaf panel is wallpaper or fabric, priced separately'
                  if o.name.endswith('_Panel') else
                  'BOQ W=4260 D=500 H=3000 @ TV area; the west wall is 4260 '
                  'long but is interrupted by a 1000 mm window - see V-02.')
            if o.name.endswith('_Panel'): o.name = o.name.replace('JOI_', 'PH2_')
        car['boq_width_mm'] = 4260

    # Item 32 - headboard, L=2600 H=1000 upholstered, LED over. Fabric by client.
    HB_X0 = 500 + (W - 500 - 2600)/2.0  # centred on the wall clear of the TV run
    hb = V.box('JOI_Headboard', HB_X0, D-90, 400, HB_X0+2600, D-30, 1400)
    V.assign(hb, uphol)
    V.tag(hb, f'{Q}/32', 'Confirmed',
          'BOQ L=2600 H=1000 upholstered MDF/WR with LED over. Fabric supplied '
          'by client (unpriced).')
    hb['boq_length_mm'] = 2600

    led = V.add_fixture('PH2_LED_Over_Headboard', HB_X0+1300, D-140, 1460,
                        lumens=None, cct=3000, size_mm=2600,
                        boq_item=f'{Q}/32', status='Phase 2')
    led.data.shape = 'RECTANGLE'; led.data.size = 2.6; led.data.size_y = 0.05
    led.data.energy = 16.0
    led.rotation_euler = (math.radians(-25), 0, 0)   # graze the wall above

    # ------------------------------------------------- Phase 2 lighting
    for i, (lx, ly) in enumerate([(1250, 1150), (2750, 1150),
                                  (1250, 3150), (2750, 3150)], 1):
        f = V.add_fixture(f'PH2_Downlight_{i:02d}', lx, ly, CEIL-30,
                          lumens=900, cct=3000, size_mm=110,
                          boq_item='NONE', status='Phase 2')
        f.data.energy = 11.0

    # ------------------------------------------------- daylight
    # No north arrow on any supplied drawing -> plan north ASSUMED to be world
    # +Y. Flagged as conflict C-05.
    V.add_world_sky(sun_el=32.39, sun_az=257.81, strength=1.0)
    V.add_sun(north_offset_deg=0.0, strength=3.4)

    # ------------------------------------------------- cameras
    # Clear floor for standing: x 500..W (TV runs occupy 0..500), y 0..D-120.
    # Each camera keeps >= 500 mm off every joinery face.
    # Shot corner-to-corner along the diagonals. The room is only 3435 x 4260
    # with a 3000 ceiling, so a shorter standoff cannot fit the full wall height
    # in frame at the 24-28 mm lenses this package uses. The diagonals give
    # ~4.4 m of standoff, which covers 3.6 m vertically - the whole wall.
    cams = [
        # item 31 - wardrobe run, shot from the south-west corner
        V.add_camera('CAM_01_Wardrobe',   700,  500, 1600, (W,    3900, 1400), 24),
        # item 33 - TV run and window, shot from the north-east corner
        V.add_camera('CAM_02_TVWall',    3200, 3900, 1600, (300,   600, 1400), 26),
        # item 32 - headboard wall, shot from the south-east corner
        V.add_camera('CAM_03_Headboard', 3200,  500, 1600, (700,  4200, 1400), 24),
    ]
    V.add_plan_camera('CAM_PLAN', -EXT_T, -PART_T, NICHE_X1+PART_T, D+EXT_T)
    return cams

if __name__ == '__main__':
    cams = build()
    audit = V.audit_boq_tags()
    print('BOQ AUDIT untagged=%d none=%d phase2=%d assumed=%d'
          % (len(audit['untagged']), len(audit['none']),
             len(audit['phase2']), len(audit['assumed'])))
    for n in audit['untagged']: print('  UNTAGGED', n)
    for n in audit['none']:     print('  BOQ=NONE', n)
    print('exported', V.export_objects('master_bedroom'))
    p = V.save_blend(os.path.join(ROOT, 'scenes', 'master_bedroom.blend'))
    print('saved', p)
