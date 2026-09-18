"""Shared Blender library for the Bakri villa (Jeddah) room models.

Every public builder tags the object it creates with a `boq_item` custom
property.  Objects with no BOQ line are tagged `NONE` and collected by
`audit_boq_tags()` so they surface in the room reconciliation log.

Units: Blender scene is Metric, unit_scale 1.0, length in METRES.
All builder APIs take MILLIMETRES and convert once, at the boundary.
"""
import bpy, bmesh, math, os, json, datetime

MM = 0.001                      # mm -> Blender metres

# ---------------------------------------------------------------- scene setup
def reset_scene():
    """Idempotent: wipe everything so a re-run rebuilds from scratch."""
    bpy.ops.wm.read_factory_settings(use_empty=True)
    for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.objects,
                 bpy.data.cameras, bpy.data.lights, bpy.data.images,
                 bpy.data.node_groups):
        for item in list(coll):
            try: coll.remove(item)
            except Exception: pass

def setup_scene(name='Room'):
    sc = bpy.context.scene
    sc.name = name
    us = sc.unit_settings
    us.system = 'METRIC'
    us.scale_length = 1.0
    us.length_unit = 'METERS'
    sc.render.engine = 'CYCLES'
    sc.cycles.device = 'CPU'
    sc.cycles.use_denoising = True
    sc.cycles.denoiser = 'OPENIMAGEDENOISE'
    sc.view_settings.view_transform = 'AgX'
    sc.view_settings.look = 'None'
    sc.render.image_settings.file_format = 'PNG'
    sc.render.film_transparent = False
    return sc

def set_quality(draft=True, samples=None, time_limit=None):
    """time_limit = seconds/frame cap. Cycles runs on 4 weak CPU cores here,
    so every frame is time-boxed and the denoiser carries the remainder."""
    sc = bpy.context.scene
    if draft:
        sc.render.resolution_x, sc.render.resolution_y = 1920, 1080
        sc.cycles.samples = samples or 512
        sc.cycles.time_limit = time_limit if time_limit is not None else 150.0
    else:
        sc.render.resolution_x, sc.render.resolution_y = 3840, 2160
        sc.cycles.samples = samples or 1024
        sc.cycles.time_limit = time_limit if time_limit is not None else 600.0
    sc.render.resolution_percentage = 100
    sc.cycles.use_adaptive_sampling = True
    sc.cycles.adaptive_threshold = 0.01
    sc.cycles.max_bounces = 8
    sc.cycles.diffuse_bounces = 4
    sc.cycles.glossy_bounces = 4
    sc.cycles.transmission_bounces = 8
    sc.cycles.caustics_reflective = False
    sc.cycles.caustics_refractive = False

# ------------------------------------------------------------------ tagging
def tag(obj, boq_item='NONE', status='Confirmed', note='', assumed=None):
    """status: Confirmed | Assumed | Phase 2. `assumed` = list of assumed dims."""
    obj['boq_item'] = boq_item
    obj['boq_status'] = status
    if note: obj['note'] = note
    if assumed: obj['ASSUMED'] = ', '.join(assumed)
    return obj

def audit_boq_tags():
    out = {'untagged': [], 'none': [], 'phase2': [], 'assumed': []}
    for o in bpy.data.objects:
        if o.type not in ('MESH', 'LIGHT'): continue
        b = o.get('boq_item')
        if b is None: out['untagged'].append(o.name)
        elif b == 'NONE': out['none'].append(o.name)
        if o.get('boq_status') == 'Phase 2': out['phase2'].append(o.name)
        if o.get('ASSUMED'): out['assumed'].append((o.name, o['ASSUMED']))
    return out

# ------------------------------------------------------------------ geometry
def _mesh_obj(name, verts, faces, collection=None):
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.validate()
    me.update()
    ob = bpy.data.objects.new(name, me)
    (collection or bpy.context.scene.collection).objects.link(ob)
    return ob

def box(name, x0, y0, z0, x1, y1, z1):
    """Axis-aligned box from mm coords (inclusive corners)."""
    X0,Y0,Z0 = x0*MM, y0*MM, z0*MM
    X1,Y1,Z1 = x1*MM, y1*MM, z1*MM
    v = [(X0,Y0,Z0),(X1,Y0,Z0),(X1,Y1,Z0),(X0,Y1,Z0),
         (X0,Y0,Z1),(X1,Y0,Z1),(X1,Y1,Z1),(X0,Y1,Z1)]
    f = [(0,1,2,3),(7,6,5,4),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)]
    ob = _mesh_obj(name, v, f)
    ob['dims_mm'] = f'{abs(x1-x0):.0f} x {abs(y1-y0):.0f} x {abs(z1-z0):.0f}'
    return ob

def wall(name, x0, y0, x1, y1, thickness, height, base=0.0):
    """Wall centred on the line (x0,y0)-(x1,y1); all mm."""
    if abs(y1-y0) < 1e-6:                      # horizontal run
        ob = box(name, min(x0,x1), y0-thickness/2, base,
                       max(x0,x1), y0+thickness/2, base+height)
    elif abs(x1-x0) < 1e-6:                    # vertical run
        ob = box(name, x0-thickness/2, min(y0,y1), base,
                       x0+thickness/2, max(y0,y1), base+height)
    else:
        raise ValueError('wall(): only axis-aligned runs supported')
    ob['thickness_mm'] = thickness
    ob['height_mm'] = height
    return ob

def cut_opening(host, x0, y0, x1, y1, z0, z1, name='opening'):
    """Boolean-subtract a box from `host`. mm. Applied immediately (idempotent)."""
    cutter = box(name + '_cutter', x0, y0, z0, x1, y1, z1)
    m = host.modifiers.new(name, 'BOOLEAN')
    m.object = cutter
    m.operation = 'DIFFERENCE'
    m.solver = 'EXACT'
    bpy.context.view_layer.objects.active = host
    bpy.ops.object.modifier_apply(modifier=m.name)
    bpy.data.objects.remove(cutter, do_unlink=True)
    return host

def floor_slab(name, x0, y0, x1, y1, thickness=40.0, top=0.0):
    return box(name, x0, y0, top-thickness, x1, y1, top)

def ceiling_slab(name, x0, y0, x1, y1, height, thickness=40.0):
    return box(name, x0, y0, height, x1, y1, height+thickness)

def cabinet_run(name, x0, y0, x1, y1, height, face,
                leaves=None, leaf_w=650, plinth=100, plinth_set=40,
                gap=5, rail=70, panel_mat=None, upper_band=None,
                drawers_at=None, drawer_rows=3, proud=18, panel_recess=10):
    """A veneered cabinet run with real articulation.

    Carcass + set-back plinth + a row of framed door leaves. Each leaf is a
    four-rail moulded frame with a panel recessed behind it, which is how the
    BOQ describes this joinery ("solid wood molding door leaf", "the panel for
    door leaf will be wall paper or fabric"). `face` is the outward direction:
    'X+', 'X-', 'Y+' or 'Y-'. All dimensions in mm.

    Returns (carcass, [all parts]).
    """
    horiz = face in ('Y+', 'Y-')          # run travels along X
    run_lo, run_hi = (x0, x1) if horiz else (y0, y1)
    run = run_hi - run_lo
    if leaves is None:
        leaves = max(1, int(round(run/float(leaf_w))))
    drawers_at = set(drawers_at or ())
    parts = []

    car = box(f'{name}_Carcass', x0, y0, plinth, x1, y1, height)
    parts.append(car)

    # plinth, set back from the visible face only
    px0, py0, px1, py1 = x0, y0, x1, y1
    if   face == 'X+': px1 -= plinth_set
    elif face == 'X-': px0 += plinth_set
    elif face == 'Y+': py1 -= plinth_set
    else:              py0 += plinth_set
    parts.append(box(f'{name}_Plinth', px0, py0, 0, px1, py1, plinth))

    # depth band the leaf occupies: d0 = outermost, d1 = carcass face
    if   face == 'X+': d0, d1 = x1 + proud, x1
    elif face == 'X-': d0, d1 = x0 - proud, x0
    elif face == 'Y+': d0, d1 = y1 + proud, y1
    else:              d0, d1 = y0 - proud, y0
    dlo, dhi = min(d0, d1), max(d0, d1)

    def part(nm, u0, u1, z0, z1, e0, e1):
        """u = along the run, z = height, e = depth."""
        if horiz: return box(nm, u0, e0, z0, u1, e1, z1)
        return box(nm, e0, u0, z0, e1, u1, z1)

    def leaf(idx, lo, hi, z0, z1, kind):
        lo, hi = lo + gap/2.0, hi - gap/2.0
        z0, z1 = z0 + gap/2.0, z1 - gap/2.0
        if hi - lo < 60 or z1 - z0 < 60: return
        r = min(rail, (hi-lo)/2.2, (z1-z0)/2.2)
        # four moulded rails
        for tagn, a, b, c, d in (('RailB', lo, hi, z0, z0+r),
                                 ('RailT', lo, hi, z1-r, z1),
                                 ('RailL', lo, lo+r, z0+r, z1-r),
                                 ('RailR', hi-r, hi, z0+r, z1-r)):
            parts.append(part(f'{name}_{kind}{idx:02d}_{tagn}', a, b, c, d, dlo, dhi))
        if panel_mat is None:
            parts.append(part(f'{name}_{kind}{idx:02d}_Panel',
                              lo+r, hi-r, z0+r, z1-r, dlo, dhi))
            return
        # panel recessed behind the frame front
        if d0 > d1: pe0, pe1 = dlo + panel_recess, dhi
        else:       pe0, pe1 = dlo, dhi - panel_recess
        pn = part(f'{name}_{kind}{idx:02d}_Panel', lo+r, hi-r, z0+r, z1-r, pe0, pe1)
        assign(pn, panel_mat)
        parts.append(pn)

    top = height - (upper_band or 0)
    step = run/float(leaves)
    for i in range(leaves):
        lo, hi = run_lo + i*step, run_lo + (i+1)*step
        if i in drawers_at:
            n = max(1, int(drawer_rows))
            for k in range(n):
                leaf(i*10+k, lo, hi,
                     plinth + k*(top-plinth)/n,
                     plinth + (k+1)*(top-plinth)/n, 'Dwr')
        else:
            leaf(i, lo, hi, plinth, top, 'Leaf')
        if upper_band:
            leaf(i, lo, hi, top, height, 'Upr')
    return car, parts


# ----------------------------------------------------------------- materials
def _principled(name, base, rough=0.5, metallic=0.0, spec=0.5,
                ior=1.45, transmission=0.0, coat=0.0):
    m = bpy.data.materials.get(name)
    if m: return m
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*base, 1.0)
    b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metallic
    b.inputs['IOR'].default_value = ior
    if 'Specular IOR Level' in b.inputs:
        b.inputs['Specular IOR Level'].default_value = spec
    if transmission and 'Transmission Weight' in b.inputs:
        b.inputs['Transmission Weight'].default_value = transmission
    if coat and 'Coat Weight' in b.inputs:
        b.inputs['Coat Weight'].default_value = coat
    return m

def _add_tex_scale(mat, size_mm_x, size_mm_y):
    """Real-world UV scale: a tile of size_mm maps to that many metres."""
    nt = mat.node_tree
    tc = nt.nodes.new('ShaderNodeTexCoord')
    mp = nt.nodes.new('ShaderNodeMapping')
    mp.inputs['Scale'].default_value = (1.0/(size_mm_x*MM), 1.0/(size_mm_y*MM), 1.0)
    nt.links.new(tc.outputs['Object'], mp.inputs['Vector'])
    mat['uv_scale_mm'] = f'{size_mm_x} x {size_mm_y}'
    return mp

def mat_procedural_wood(name, base=(0.38,0.22,0.11), rough=0.32, grain_mm=900):
    """Beech veneer stain -- procedural grain, real-world scale."""
    m = bpy.data.materials.get(name)
    if m: return m
    m = _principled(name, base, rough=rough, coat=0.25)
    nt = m.node_tree; b = nt.nodes['Principled BSDF']
    mp = _add_tex_scale(m, grain_mm, grain_mm/18.0)
    nz = nt.nodes.new('ShaderNodeTexNoise')
    nz.inputs['Scale'].default_value = 6.0
    nz.inputs['Detail'].default_value = 8.0
    nz.inputs['Roughness'].default_value = 0.6
    nt.links.new(mp.outputs['Vector'], nz.inputs['Vector'])
    ramp = nt.nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].color = (*[c*0.72 for c in base], 1)
    ramp.color_ramp.elements[1].color = (*[min(1,c*1.35) for c in base], 1)
    ramp.color_ramp.elements[0].position = 0.35
    ramp.color_ramp.elements[1].position = 0.66
    nt.links.new(nz.outputs['Fac'], ramp.inputs['Fac'])
    nt.links.new(ramp.outputs['Color'], b.inputs['Base Color'])
    bump = nt.nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.08
    nt.links.new(nz.outputs['Fac'], bump.inputs['Height'])
    nt.links.new(bump.outputs['Normal'], b.inputs['Normal'])
    return m

def mat_marble(name, base, vein, tile_mm=1100, rough=0.09):
    m = bpy.data.materials.get(name)
    if m: return m
    m = _principled(name, base, rough=rough, coat=0.6)
    nt = m.node_tree; b = nt.nodes['Principled BSDF']
    mp = _add_tex_scale(m, tile_mm, tile_mm)
    nz = nt.nodes.new('ShaderNodeTexNoise')
    nz.inputs['Scale'].default_value = 3.0
    nz.inputs['Detail'].default_value = 12.0
    nt.links.new(mp.outputs['Vector'], nz.inputs['Vector'])
    wv = nt.nodes.new('ShaderNodeTexWave')
    wv.wave_type = 'BANDS'; wv.bands_direction = 'DIAGONAL'
    wv.inputs['Scale'].default_value = 2.2
    wv.inputs['Distortion'].default_value = 18.0
    wv.inputs['Detail'].default_value = 3.0
    nt.links.new(mp.outputs['Vector'], wv.inputs['Vector'])
    ramp = nt.nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].color = (*base, 1)
    ramp.color_ramp.elements[1].color = (*vein, 1)
    ramp.color_ramp.elements[0].position = 0.42
    ramp.color_ramp.elements[1].position = 0.58
    nt.links.new(wv.outputs['Fac'], ramp.inputs['Fac'])
    nt.links.new(ramp.outputs['Color'], b.inputs['Base Color'])
    return m

def mat_porcelain_tile(name, base=(0.80,0.78,0.75), tile_mm=(600,1200), rough=0.12):
    """Porcelain with real-world tile UV scale and a grout grid."""
    m = bpy.data.materials.get(name)
    if m: return m
    m = _principled(name, base, rough=rough, coat=0.35)
    nt = m.node_tree; b = nt.nodes['Principled BSDF']
    mp = _add_tex_scale(m, tile_mm[0], tile_mm[1])
    brick = nt.nodes.new('ShaderNodeTexBrick')
    brick.inputs['Scale'].default_value = 1.0
    brick.inputs['Mortar Size'].default_value = 0.008      # ~3 mm joint
    brick.inputs['Bias'].default_value = 0.0
    brick.inputs['Brick Width'].default_value = 1.0
    brick.inputs['Row Height'].default_value = 1.0
    brick.inputs['Color1'].default_value = (*base, 1)
    brick.inputs['Color2'].default_value = (*[c*0.97 for c in base], 1)
    brick.inputs['Mortar'].default_value = (*[c*0.72 for c in base], 1)
    nt.links.new(mp.outputs['Vector'], brick.inputs['Vector'])
    nt.links.new(brick.outputs['Color'], b.inputs['Base Color'])
    bump = nt.nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.15
    bump.inputs['Distance'].default_value = 0.002
    nt.links.new(brick.outputs['Fac'], bump.inputs['Height'])
    nt.links.new(bump.outputs['Normal'], b.inputs['Normal'])
    return m

def mat_paint(name, base=(0.90,0.885,0.86), rough=0.62):
    return _principled(name, base, rough=rough)

def mat_glass_clear(name='GLS_Clear_6mm', base=(0.96,0.97,0.97)):
    """Clear glazing for windows. Frosted is for shower screens only."""
    m = bpy.data.materials.get(name)
    if m: return m
    return _principled(name, base, rough=0.02, transmission=1.0, ior=1.52)

def mat_glass_frosted(name='GLS_Frosted_10mm', base=(0.92,0.94,0.94)):
    m = bpy.data.materials.get(name)
    if m: return m
    m = _principled(name, base, rough=0.38, transmission=1.0, ior=1.52)
    m.blend_method = 'BLEND'
    return m

def mat_metal(name, base=(0.62,0.60,0.58), rough=0.22):
    return _principled(name, base, rough=rough, metallic=1.0)

def mat_mirror(name='MIR_Clear_6mm'):
    return _principled(name, (0.95,0.96,0.96), rough=0.02, metallic=1.0)

def mat_fabric(name, base=(0.36,0.33,0.30), rough=0.85):
    return _principled(name, base, rough=rough, spec=0.2)

def mat_phase2(item):
    """Neutral placeholder for unpriced (Phase 2) scope."""
    name = f'PH2_{item}'
    m = bpy.data.materials.get(name)
    if m: return m
    m = _principled(name, (0.55,0.55,0.57), rough=0.5)
    m['phase'] = 2
    m.diffuse_color = (0.55,0.55,0.57,1.0)
    return m

def assign(obj, mat):
    obj.data.materials.clear()
    obj.data.materials.append(mat)
    obj['material'] = mat.name
    return obj

# ------------------------------------------------------------------ lighting
def solar_position(lat, lon, when, tz_hours):
    """NOAA solar position. Returns (elevation_deg, azimuth_deg_from_north_CW)."""
    d = when - datetime.datetime(2000,1,1,12,0,0)
    n = d.days + d.seconds/86400.0 - tz_hours/24.0
    L = (280.460 + 0.9856474*n) % 360
    g = math.radians((357.528 + 0.9856003*n) % 360)
    lam = math.radians((L + 1.915*math.sin(g) + 0.020*math.sin(2*g)) % 360)
    eps = math.radians(23.439 - 0.0000004*n)
    ra = math.atan2(math.cos(eps)*math.sin(lam), math.cos(lam))
    dec = math.asin(math.sin(eps)*math.sin(lam))
    gmst = (18.697374558 + 24.06570982441908*n) % 24
    lmst = math.radians((gmst*15 + lon) % 360)
    ha = lmst - ra
    la = math.radians(lat)
    el = math.asin(math.sin(la)*math.sin(dec) + math.cos(la)*math.cos(dec)*math.cos(ha))
    az = math.atan2(-math.sin(ha), math.tan(dec)*math.cos(la) - math.sin(la)*math.cos(ha))
    return math.degrees(el), math.degrees(az) % 360

JEDDAH = dict(lat=21.49, lon=39.19, tz=3)

def add_sun(when=None, north_offset_deg=0.0, strength=3.4, angle_deg=0.53):
    """Daylight sun for Jeddah. `north_offset_deg` rotates plan-north to world +Y."""
    when = when or datetime.datetime(2026, 9, 18, 16, 0, 0)
    el, az = solar_position(JEDDAH['lat'], JEDDAH['lon'], when, JEDDAH['tz'])
    l = bpy.data.lights.new('SUN_Daylight', 'SUN')
    l.energy = strength
    l.angle = math.radians(angle_deg)
    l.color = (1.0, 0.94, 0.86)
    ob = bpy.data.objects.new('SUN_Daylight', l)
    bpy.context.scene.collection.objects.link(ob)
    ob.rotation_euler = (math.radians(90.0 - el), 0.0,
                         math.radians(180.0 - az + north_offset_deg))
    ob['solar_elevation_deg'] = round(el, 2)
    ob['solar_azimuth_deg'] = round(az, 2)
    ob['local_time'] = when.isoformat()
    tag(ob, 'NONE', 'Assumed', 'Daylight; site 21.49N 39.19E',
        assumed=['plan north orientation (no north arrow on drawings)'])
    return ob

def add_world_sky(turbidity=3.0, strength=1.0, sun_el=None, sun_az=None):
    w = bpy.data.worlds.new('SkyWorld')
    bpy.context.scene.world = w
    w.use_nodes = True
    nt = w.node_tree
    bg = nt.nodes['Background']
    sky = nt.nodes.new('ShaderNodeTexSky')
    sky.sky_type = 'NISHITA'
    sky.turbidity = turbidity
    sky.dust_density = 2.2                 # Jeddah coastal haze
    if sun_el is not None:
        sky.sun_elevation = math.radians(sun_el)
    if sun_az is not None:
        sky.sun_rotation = math.radians(180.0 - sun_az)
    sky.sun_disc = False
    nt.links.new(sky.outputs['Color'], bg.inputs['Color'])
    bg.inputs['Strength'].default_value = strength
    return w

def add_fixture(name, x, y, z, power_w=None, lumens=None, cct=3000,
                size_mm=120, boq_item='NONE', status='Phase 2'):
    """Ceiling luminaire. Unpriced in BOQ -> Phase 2 placeholder by default."""
    l = bpy.data.lights.new(name, 'AREA')
    l.shape = 'DISK'
    l.size = size_mm*MM
    # lumens -> watts radiometric approximation for Cycles
    if lumens: l.energy = lumens/90.0
    else:      l.energy = power_w if power_w else 12.0
    l.color = cct_to_rgb(cct)
    ob = bpy.data.objects.new(name, l)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = (x*MM, y*MM, z*MM)
    # Blender lights emit along local -Z, so identity rotation already aims the
    # luminaire at the floor. A pi rotation here pointed them at the ceiling and
    # produced black frames.
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob['cct_K'] = cct
    tag(ob, boq_item, status,
        'Lighting excluded from BOQ (note: "all lighting are not included")',
        assumed=None if lumens else [f'{cct}K residential, output ASSUMED'])
    return ob

def cct_to_rgb(k):
    k = max(1000, min(12000, k))/100.0
    if k <= 66: r = 255
    else:       r = 329.7 * ((k-60) ** -0.1332)
    if k <= 66: g = 99.47*math.log(k) - 161.1
    else:       g = 288.12 * ((k-60) ** -0.0755)
    if k >= 66: b = 255
    elif k <= 19: b = 0
    else: b = 138.52*math.log(k-10) - 305.04
    return tuple(max(0.0, min(1.0, c/255.0)) for c in (r, g, b))

# ------------------------------------------------------------------- cameras
def add_camera(name, x, y, z, target, lens_mm=24, eye_mm=1600, shift_y=None):
    """Eye-level camera with TRUE VERTICALS (no keystoning).

    The camera is kept exactly level (pitch = 90 deg in Blender's convention);
    framing above/below the horizon is done with the sensor shift, which is the
    digital equivalent of a tilt-shift lens. Verticals therefore stay vertical.
    """
    cam = bpy.data.cameras.new(name)
    cam.lens = lens_mm
    cam.sensor_fit = 'HORIZONTAL'
    cam.sensor_width = 36.0
    cam.clip_start = 0.02
    cam.clip_end = 200.0
    ob = bpy.data.objects.new(name, cam)
    bpy.context.scene.collection.objects.link(ob)
    px, py, pz = x*MM, y*MM, (z if z is not None else eye_mm)*MM
    tx, ty, tz = target[0]*MM, target[1]*MM, target[2]*MM
    yaw = math.atan2(ty-py, tx-px) - math.pi/2.0
    ob.location = (px, py, pz)
    ob.rotation_euler = (math.pi/2.0, 0.0, yaw)      # level -> verticals vertical
    if shift_y is None:
        dist = math.hypot(tx-px, ty-py)
        shift_y = 0.0 if dist < 1e-6 else max(-0.35, min(0.35, (tz-pz)/dist*(cam.lens/cam.sensor_width)))
    cam.shift_y = shift_y
    ob['eye_height_mm'] = round(pz/MM)
    ob['lens_mm'] = lens_mm
    ob['vertical_correction'] = 'level camera + sensor shift (no keystone)'
    return ob

def add_plan_camera(name, x0, y0, x1, y1, height_mm=6000, margin_mm=300):
    cam = bpy.data.cameras.new(name)
    cam.type = 'ORTHO'
    w = (abs(x1-x0) + 2*margin_mm)*MM
    h = (abs(y1-y0) + 2*margin_mm)*MM
    cam.ortho_scale = max(w, h)
    cam.clip_start = 0.01; cam.clip_end = 100.0
    ob = bpy.data.objects.new(name, cam)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = ((x0+x1)/2*MM, (y0+y1)/2*MM, height_mm*MM)
    ob.rotation_euler = (0.0, 0.0, 0.0)              # straight down
    ob['view'] = 'top-down orthographic plan'
    return ob

# -------------------------------------------------------------------- output
def render_to(cam_obj, path, draft=True, samples=None, time_limit=None):
    sc = bpy.context.scene
    sc.camera = cam_obj
    set_quality(draft=draft, samples=samples, time_limit=time_limit)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)
    return path

def export_objects(room, path=None):
    """Dump every tagged object to logs/<room>_objects.json so the finish
    schedule is generated from the model itself, never retyped."""
    import json as _json
    rows = []
    for o in bpy.data.objects:
        if o.type not in ('MESH', 'LIGHT'): continue
        dim = o.dimensions
        rows.append({
            'object': o.name,
            'type': o.type,
            'material': o.get('material') or (o.data.materials[0].name
                        if o.type=='MESH' and o.data.materials else ''),
            'boq_item': o.get('boq_item', 'NONE'),
            'status': o.get('boq_status', ''),
            'dims_mm': [round(dim.x*1000), round(dim.y*1000), round(dim.z*1000)],
            'boq_width_mm': o.get('boq_width_mm'),
            'boq_length_mm': o.get('boq_length_mm'),
            'modelled_width_mm': o.get('modelled_width_mm'),
            'assumed': o.get('ASSUMED', ''),
            'note': o.get('note', ''),
        })
    rows.sort(key=lambda r: (r['boq_item'], r['object']))
    p = path or os.path.join(os.path.dirname(os.path.dirname(
        os.path.dirname(os.path.abspath(__file__)))), 'logs', f'{room}_objects.json')
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, 'w') as f: _json.dump(rows, f, indent=1)
    return p

def frame_stats(path):
    """Mean/max luminance of a rendered PNG. Used by the self-QA pass to catch
    black or blown frames without eyeballing every one."""
    img = bpy.data.images.load(path)
    px = list(img.pixels)
    rgb = [px[i] for i in range(len(px)) if i % 4 != 3]
    bpy.data.images.remove(img)
    n = len(rgb) or 1
    return {'mean': sum(rgb)/n, 'max': max(rgb) if rgb else 0.0,
            'lit_pct': 100.0*sum(1 for v in rgb if v > 0.004)/n,
            'blown_pct': 100.0*sum(1 for v in rgb if v > 0.99)/n}

def save_blend(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=path)
    return path
