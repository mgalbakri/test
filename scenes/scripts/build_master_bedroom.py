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
    glass   = V.mat_glass_frosted()
    ph2_fab = V.mat_phase2('MBR_door_leaf_panel_wallpaper_or_fabric')
    ph2_lit = V.mat_phase2('MBR_lighting')

    # ---------------------------------------------------------- shell
    fl = V.floor_slab('FLR_MasterBedroom', 0, 0, W, D)
    V.assign(fl, floor_m)
    V.tag(fl, 'NONE', 'Confirmed',
          'Floor finish not in BOQ scope for this room (no flooring line item)')

    ce = V.ceiling_slab('CEIL_MasterBedroom', -EXT_T, -PART_T, W+480, D+EXT_T, CEIL)
    V.assign(ce, paint)
    V.tag(ce, f'{Q}/NONE', 'Assumed',
          'Ceiling paint is bundled in BOQ items 31/33 only as joinery height; '
          'no separate paint line for Master Bedroom', assumed=ASSUMED_CEIL)

    walls = {
      'WALL_West_External':  (0, 0, 0, D, EXT_T),
      'WALL_North_External': (0, D, W, D, EXT_T),
      'WALL_South_Partition':(0, 0, W, 0, PART_T),
    }
    for n, (x0,y0,x1,y1,t) in walls.items():
        w = V.wall(n, x0, y0, x1, y1, t, CEIL)
        V.assign(w, paint)
        V.tag(w, f'{Q}/NONE', 'Assumed',
              'Wall build-up measured from plan; no paint line item for this room',
              assumed=ASSUMED_CEIL)

    # East partition, built around the wardrobe recess (two piers + recess back)
    for n, y0, y1 in (('WALL_East_Pier_S', -PART_T/2, NICHE_Y0),
                      ('WALL_East_Pier_N', NICHE_Y1, D+PART_T/2)):
        w = V.wall(n, W, y0, W, y1, PART_T, CEIL)
        V.assign(w, paint); V.tag(w, f'{Q}/NONE', 'Assumed', assumed=ASSUMED_CEIL)
    back = V.wall('WALL_East_RecessBack', NICHE_X1, NICHE_Y0-PART_T/2,
                  NICHE_X1, NICHE_Y1+PART_T/2, PART_T, CEIL)
    V.assign(back, paint); V.tag(back, f'{Q}/NONE', 'Assumed', assumed=ASSUMED_CEIL)
    for n, y in (('WALL_Recess_Jamb_S', NICHE_Y0), ('WALL_Recess_Jamb_N', NICHE_Y1)):
        w = V.wall(n, NICHE_X0, y, NICHE_X1, y, PART_T, CEIL)
        V.assign(w, paint); V.tag(w, f'{Q}/NONE', 'Assumed', assumed=ASSUMED_CEIL)

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
    # Item 31 - wardrobe run, W=4260 H=3000 D=500. The measured recess is only
    # 2630 mm wide, so the specified run CANNOT be installed as quoted.
    # Modelled AS-MEASURED (2630) and the shortfall is logged as variance V-01.
    cab = V.box('JOI_Wardrobe_Run', NICHE_X0-20, NICHE_Y0, 0,
                                    NICHE_X1,    NICHE_Y1, CEIL)
    V.assign(cab, beech)
    V.tag(cab, f'{Q}/31', 'Confirmed',
          'BOQ W=4260 D=500 H=3000; modelled to the measured 2630 mm recess. '
          'Shortfall 1630 mm - see variance V-01.')
    cab['boq_width_mm'] = 4260
    cab['modelled_width_mm'] = NICHE_Y1 - NICHE_Y0

    # Item 33 - TV-area run, W=4260 H=3000 D=500, opposite the wardrobe.
    # The facing (west) wall is 4260 long but carries a 1000 mm window.
    # Modelled as two returns either side of the window opening.
    for n, y0, y1 in (('JOI_TV_Run_S', 0, WIN_Y0), ('JOI_TV_Run_N', WIN_Y1, D)):
        if y1 - y0 < 200: continue
        o = V.box(n, 0, y0, 0, 500, y1, CEIL)
        V.assign(o, beech)
        V.tag(o, f'{Q}/33', 'Confirmed',
              'BOQ W=4260 D=500 H=3000 @ TV area; west wall is 4260 long but '
              'is interrupted by a 1000 mm window - see variance V-02.')
        o['boq_width_mm'] = 4260

    # Door-leaf panels are explicitly unpriced in items 31/33
    pan = V.box('PH2_MBR_DoorLeafPanels', NICHE_X0-24, NICHE_Y0+40, 400,
                                          NICHE_X0-8,  NICHE_Y1-40, 2600)
    V.assign(pan, ph2_fab)
    V.tag(pan, f'{Q}/31', 'Phase 2',
          'BOQ: "the panel for door leaf will be wall paper or fabric the price '
          'will be separate" - unpriced')

    # Item 32 - headboard, L=2600 H=1000, upholstered, LED over. Fabric by client.
    hb = V.box('JOI_Headboard', (W-2600)/2, D-90, 400, (W-2600)/2+2600, D-30, 1400)
    V.assign(hb, uphol)
    V.tag(hb, f'{Q}/32', 'Confirmed',
          'BOQ L=2600 H=1000 upholstered MDF/WR, LED over. Fabric supplied by '
          'client (unpriced).')
    hb['boq_length_mm'] = 2600

    led = V.add_fixture('PH2_LED_Over_Headboard', W/2, D-200, 1450,
                        lumens=None, cct=3000, size_mm=2600,
                        boq_item=f'{Q}/32', status='Phase 2')
    led.data.shape = 'RECTANGLE'; led.data.size = 2.6; led.data.size_y = 0.06
    led.data.energy = 14.0
    led.rotation_euler = (math.radians(-100), 0, 0)

    # ------------------------------------------------- Phase 2 lighting
    for i, (lx, ly) in enumerate([(W*0.3, D*0.3), (W*0.7, D*0.3),
                                  (W*0.3, D*0.72), (W*0.7, D*0.72)], 1):
        f = V.add_fixture(f'PH2_Downlight_{i:02d}', lx, ly, CEIL-30,
                          lumens=900, cct=3000, size_mm=110,
                          boq_item='NONE', status='Phase 2')
        f.data.energy = 9.0

    # ------------------------------------------------- daylight
    # North arrow is ABSENT from every supplied drawing -> plan north assumed
    # to be world +Y. Flagged as conflict C-05.
    V.add_world_sky(sun_el=32.39, sun_az=257.81, strength=0.9)
    V.add_sun(north_offset_deg=0.0, strength=3.2)

    # ------------------------------------------------- cameras
    cams = [
        V.add_camera('CAM_01_Wardrobe', 420, 620, 1600, (W+300, 2100, 1500), 24),
        V.add_camera('CAM_02_Bed',      620, 900, 1600, (W*0.55, D, 1500), 26),
        V.add_camera('CAM_03_Window',  2900, 3500, 1600, (-EXT_T, 1900, 1400), 24),
    ]
    V.add_plan_camera('CAM_PLAN', -EXT_T, -PART_T, W+480, D+EXT_T)
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
