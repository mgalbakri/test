"""One continuous paper world + screen-space narrator.  All times are absolute seconds,
anchored to the narration starts in timeline.ST so picture and voice stay locked."""
import math
import numpy as np
from engine import *
from timeline import ST, DUR, END, CAPS, wrap

h, w, d, m, k, q, r = (ST[s] for s in ('hook', 'world', 'disruption', 'mechanism', 'discovery',
                                         'consequence', 'recap'))
GROUND = 700
TA, TB = (530, 750), (820, 1040)
TOP, APEX, FUEL_TOP = 440, 405, 488
FEET = 872                      # bot stands on the stage apron


def cl(x):
    return max(0.0, min(1.0, x))


def ss(t, a, b):
    u = cl((t - a) / (b - a)) if b > a else float(t >= a)
    return u * u * (3 - 2 * u)


def back(u):
    u = cl(u); c = 1.9
    return 1 + (c + 1) * (u - 1) ** 3 + c * (u - 1) ** 2


def pop(t, t0, dur=.35):
    u = cl((t - t0) / dur)
    return min(1, u * 2.5), .55 + .45 * back(u)


# ------------------------------------------------------------- camera ----
CAM = [
    (0.0, (960, 488, 1.0)), (d - 1.0, (960, 488, 1.0)), (d + 1.0, (640, 538, 2.0)),
    (m + 15.9, (640, 538, 2.0)), (k + 0.9, (620, 560, 2.0)),
    (q - 0.8, (620, 560, 2.0)), (q + 0.2, (1700, 150, 0.8)), (q + 1.3, (2800, -175, 1.6)),
    (q + 8.7, (2800, -175, 1.6)), (q + 9.4, (1900, 200, 0.85)), (r + 0.9, (960, 488, 1.0)),
    (END + 1, (960, 488, 1.0))]


def cam(t):
    for (t0, a), (t1, b) in zip(CAM, CAM[1:]):
        if t0 <= t <= t1:
            u = ss(t, t0, t1)
            # zoom interpolated in log space so moves feel even
            zz = math.exp(math.log(a[2]) * (1 - u) + math.log(b[2]) * u)
            return (a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u, zz)
    return CAM[-1][1]


def night(t):
    return ss(t, w + 10.0, d + 0.6) - ss(t, k + 4.0, k + 5.5)


# ------------------------------------------------------------- props ----
def pipe(c, key, P, hw=6.5, col=TEALD, alpha=1.0, shadow=.8):
    Q, _ = resample(P, False, 4.0)
    N = normals(Q, False)
    poly = np.vstack([Q + N * hw, (Q - N * hw)[::-1]])
    c.paper(key, poly, col, shadow=shadow, fringe=.6, edge=.5, outline=.35, alpha=alpha, lift=.6)


def flow(c, key, P, t, speed=70, col=None, alpha=1.0, w_=4.0):
    c.crayon(key, P, MUSTARD if col is None else col, w_, alpha=alpha, dash=(12 * c.z, 14 * c.z, -t * speed * c.z),
             wax=.35)


def droplet(c, key, x, y, rad, alpha=1.0, col=None):
    c.paper(key, ellipse(x, y, rad, rad * 1.1, 14), TEAL if col is None else col, shadow=0, fringe=0, edge=.2,
            alpha=alpha)


def crystal(c, key, x, y, rad, alpha=1.0):
    for i in range(3):
        a = i * math.pi / 3 + .3
        p0 = (x - math.cos(a) * rad, y - math.sin(a) * rad); p1 = (x + math.cos(a) * rad, y + math.sin(a) * rad)
        c.crayon((key, i), [p0, p1], TEAL, max(1.6, rad * .28), alpha=alpha, wax=.3, jit=.3)
        for sgn in (-1, 1):
            for e in (p0, p1):
                bx = x + (e[0] - x) * .6; by = y + (e[1] - y) * .6
                b2 = (bx + math.cos(a + sgn * 2.2) * rad * .35, by + math.sin(a + sgn * 2.2) * rad * .35)
                if e is p0:
                    b2 = (bx - math.cos(a + sgn * .95) * rad * .35, by - math.sin(a + sgn * .95) * rad * .35)
                c.crayon((key, i, sgn, e), [(bx, by), b2], TEAL, max(1.2, rad * .18), alpha=alpha, wax=.3, jit=.2)


def hourglass(c, key, cx, cy, s, ang, sand, alpha=1.0, screen=False):
    """sand: 0 = all in the top bulb, 1 = all in the bottom bulb (in hourglass frame)."""
    T = lambda P: xform(P, 0, 0, s, ang, cx, cy)
    c.paper((key, 'f'), T(rrect(-22, -40, 22, 40, 6)), PAPER, shadow=.8, fringe=.6, outline=.6, alpha=alpha,
            screen=screen)
    top = [(-18, -34), (18, -34), (2, -2), (-2, -2)]
    bot = [(-2, 2), (2, 2), (18, 34), (-18, 34)]
    c.paper((key, 'g1'), T(top), mix(CREAM, TEAL, .12), shadow=0, fringe=0, alpha=alpha, screen=screen)
    c.paper((key, 'g2'), T(bot), mix(CREAM, TEAL, .12), shadow=0, fringe=0, alpha=alpha, screen=screen)
    a = 1 - sand
    if a > .02:
        yy = -2 - 32 * math.sqrt(a)
        hx = 2 + 16 * (yy + 2) / -32
        c.blob((key, 's1'), T([(-hx, yy), (hx, yy), (2, -2), (-2, -2)]), MUSTARD, alpha=alpha, screen=screen)
    if sand > .02:
        yy = 34 - 32 * (1 - math.sqrt(1 - sand))
        hx = 18 - 16 * (34 - yy) / 32
        c.blob((key, 's2'), T([(-hx, yy), (hx, yy), (18, 34), (-18, 34)]), MUSTARD, alpha=alpha, screen=screen)
        if 0.02 < sand < .98:
            c.crayon((key, 'st'), T([(0, -2), (0, 30)]), MUSTARD, 2.0 * (1 if screen else 1), alpha=alpha,
                     screen=screen, wscale=not screen)
    c.pencil((key, 'o'), T(top[:2] + [(0, 0)] + bot[2:] + [top[0]]), alpha=.5 * alpha, screen=screen)


def jar(c, key, cx, by, s, fill, alpha=1.0, screen=False, glint=1.0, water=0.0):
    T = lambda P: xform(P, 0, 0, s, 0, cx, by)
    body = rrect(-24, -64, 24, 0, 7)
    c.paper((key, 'b'), T(body), mix(PAPER, TEAL, .06), shadow=.9, fringe=.7, outline=.7, alpha=alpha,
            screen=screen)
    if fill > .01:
        ft = -4 - 52 * fill
        c.blob((key, 'f'), T(rrect(-20, ft, 20, -4, 5)), FUEL, alpha=alpha, screen=screen)
        c.pencil((key, 'fl'), T([(-20, ft), (20, ft)]), alpha=.35 * alpha, screen=screen)
    if water > .01:
        c.blob((key, 'w'), T(rrect(-20, -4 - 14 * water, 20, -4, 4)), TEAL, alpha=alpha, screen=screen)
    c.paper((key, 'l'), T(rrect(-27, -74, 27, -62, 3)), CHAR, shadow=.4, fringe=.5, alpha=alpha, screen=screen)
    if glint > 0:
        c.blob((key, 'g1'), T(rrect(-15, -54, -10, -14, 2)), PAPER, alpha=.9 * glint * alpha, screen=screen)
        c.blob((key, 'g2'), T(rrect(-6, -54, -3, -40, 1)), PAPER, alpha=.8 * glint * alpha, screen=screen)


def tag(c, key, text, x, y, size=17, alpha=1.0, string_to=None, ang=-2.0, col=None, check=False):
    if alpha <= 0:
        return
    tw, th = c.text_size(text, size * c.z)
    tw /= c.z; th /= c.z
    if check:
        tw += size * 1.4
    pts = xform(rect(x - tw / 2 - 12, y - th / 2 - 8, x + tw / 2 + 12, y + th / 2 + 9), x, y,
                ang=math.radians(ang))
    if string_to is not None:
        c.pencil((key, 'str'), [(x - tw / 2 - 10, y), string_to], alpha=.6 * alpha)
    c.paper((key, 'p'), pts, PAPER if col is None else col, shadow=.9, fringe=.8, alpha=alpha, lift=.7)
    if check:
        c.text(text, (x - size * .7, y), size, alpha=alpha, angle=-ang)
        checkmark(c, (key, 'ck'), x + tw / 2 - size * .55, y, size * .8, alpha=alpha, wd=size * .16)
    else:
        c.text(text, (x, y), size, alpha=alpha, angle=-ang)


def checkmark(c, key, x, y, s, prog=1.0, col=None, alpha=1.0, screen=False, wd=None):
    P = [(x - .5 * s, y), (x - .1 * s, y + .4 * s), (x + .6 * s, y - .5 * s)]
    if prog < 1:
        P = sub_polyline(P, 0, prog, 12)
    c.crayon(key, P, TEAL if col is None else col, wd or s * .18, alpha=alpha, screen=screen, wax=.35)


# ------------------------------------------------------------- world ----
def backdrop(c, t):
    # high, cold sky for the cruise scene (pale teal torn paper)
    c.paper('hisky', rect(-1500, -2600, 6000, -10), mix(CREAM, TEAL, .22), shadow=.5, fringe=1, edge=2.0)
    for i, (cx, cy, rx) in enumerate([(2350, -420, 140), (3350, -480, 120), (2700, 40, 260), (3250, 70, 220),
                                      (2050, 90, 200), (3650, 30, 180), (1700, -150, 120)]):
        P = []
        for j in range(5):
            P += ellipse(cx - rx * .7 + j * rx * .35, cy - (18 if j in (1, 3) else 30 if j == 2 else 6), rx * .32,
                         rx * .3, 12)
        hull = ellipse(cx, cy, rx, rx * .32, 40)
        c.paper(('cloud', i), hull, PAPER, shadow=.6, fringe=.8, edge=1.5)
    # sun and moon
    sy = 230 + 600 * ss(t, w + 10.0, d + 0.4) - 600 * ss(t, k + 4.0, k + 5.6)
    c.paper('sun', ellipse(1560, sy, 72, 72, 40), MUSTARD, shadow=.6, fringe=1)
    na = night(t)
    if na > 0.01:
        moon = ellipse(300, 170, 46, 46, 30, -1.2, 1.2 + 2.0) + ellipse(318, 160, 40, 40, 30, 1.2 + 1.7, -1.0)[::-1]
        c.paper('moon', ellipse(300, 170 + (1 - na) * 120, 44, 44, 30), PAPER, shadow=.5, fringe=1, alpha=na)
        c.paper('moonb', ellipse(322, 158 + (1 - na) * 120, 40, 40, 30), mix(CREAM, CHAR, .30), shadow=0, fringe=0,
                alpha=na)
    # hills + cardboard ground
    hills = [(-400, 760)] + [(x, 640 - 34 * math.sin(x / 170.0) - 18 * math.sin(x / 61.0 + 1)) for x in
                             range(-400, 2401, 40)] + [(2400, 760)]
    c.paper('hills', hills, mix(MUSTARD, CREAM, .55), shadow=.5, fringe=1)
    c.paper('ground', [(-400, GROUND)] + [(x, GROUND + 3 * math.sin(x / 37.0)) for x in range(-400, 2401, 50)] +
            [(2400, 1600), (-400, 1600)], TAN, shadow=.8, fringe=1, edge=1.5)


def farm_pop(t, i):
    a, s = pop(t, w + 0.1 + i * .18, .4)
    return a, s


def draw_tank(c, key, x0, x1, t, tr, alpha, level, cut=0.0, peel=0.0, floor_k=0.0, water=0.0, label=True):
    cx = (x0 + x1) / 2
    if cut > 0:
        draw_tank_interior(c, key, x0, x1, t, floor_k, water)
    if peel < 1:
        yt = TOP + peel * (GROUND - TOP)
        c.paper((key, 'body'), tr(rect(x0, yt, x1, GROUND)), PAPER, shadow=1.0, fringe=1, outline=.5, alpha=alpha,
                lift=1.3)
        if peel <= 0.02:
            if label:
                c.paper((key, 'plate'), tr(rect(cx - 52, 560, cx + 52, 590)), CHAR, shadow=.4, fringe=.5, alpha=alpha)
                c.text('JET A-1', tr([(cx, 575)])[0], 17 * (1 if tr is None else 1), col=PAPER, fnt='cav',
                       weight=700, alpha=alpha)
            # sight gauge
            c.paper((key, 'g'), tr(rect(x1 - 18, 455, x1 - 10, 690)), mix(PAPER, CHAR, .08), shadow=0, fringe=0,
                    alpha=alpha)
            if level > .01:
                c.blob((key, 'gl'), tr(rect(x1 - 18, 690 - 235 * level, x1 - 10, 690)), MUSTARD, alpha=alpha)
            c.paper((key, 'band'), tr(rect(x0, 470, x1, 478)), TEAL, shadow=0, fringe=0, alpha=alpha * .9)
        if 0.02 < peel:
            c.paper((key, 'curl'), tr(rect(x0 - 4, yt - 10, x1 + 4, yt + 9)), mix(PAPER, CHAR, .22), shadow=1,
                    fringe=.6, outline=.5, alpha=alpha, lift=1.6)
    else:
        c.paper((key, 'wl'), rect(x0, TOP, x0 + 7, GROUND), PAPER, shadow=.6, fringe=.5, outline=.5)
        c.paper((key, 'wr'), rect(x1 - 7, TOP, x1, GROUND), PAPER, shadow=.6, fringe=.5, outline=.5)
    c.paper((key, 'roof'), tr([(x0 - 12, TOP + 3), (cx, APEX), (x1 + 12, TOP + 3)]), mix(PAPER, CHAR, .07),
            shadow=.9, fringe=1, outline=.5, alpha=alpha, lift=1.2)
    # vent
    c.paper((key, 'vs'), tr(rect(cx - 4, APEX - 12, cx + 4, APEX + 2)), CHAR, shadow=.3, fringe=.4, alpha=alpha)
    c.paper((key, 'vc'), tr([(cx - 14, APEX - 10), (cx, APEX - 20), (cx + 14, APEX - 10)]), CHAR, shadow=.3,
            fringe=.4, alpha=alpha)


def floor_y(x, fk):
    flat = GROUND - 6
    v = GROUND - 16 * min(1, abs(x - 640) / 103.0)
    return flat * (1 - fk) + v * fk


def draw_tank_interior(c, key, x0, x1, t, fk, water):
    c.paper((key, 'back'), rect(x0, TOP, x1, GROUND), mix(CREAM, CHAR, .16), shadow=0, fringe=0)
    xs = np.linspace(x0 + 7, x1 - 7, 24)
    surf = [(x, FUEL_TOP + 2.5 * math.sin(x / 19.0 + t * 1.3)) for x in xs]
    flo = [(x, floor_y(x, fk)) for x in xs[::-1]]
    c.blob((key, 'fuel'), surf + flo, FUEL)
    c.pencil((key, 'surf'), surf, alpha=.35)
    if fk > .02:
        c.pencil((key, 'floor'), [(x, floor_y(x, fk)) for x in xs], alpha=.6)
    # sump
    sa = ss(t, m + 8.2, m + 8.7) if t < r else 1.0
    if sa > 0:
        c.paper((key, 'sump'), rect(630, GROUND - 1, 650, GROUND + 13), mix(CREAM, CHAR, .25), shadow=0, fringe=0,
                alpha=sa)
    if water > 0.01:
        wl = GROUND - 1 - 9 * water
        half = (GROUND - wl) * 103.0 / 16
        wx = np.linspace(640 - half, 640 + half, 12)
        poly = [(x, wl) for x in wx] + [(x, floor_y(x, fk)) for x in wx[::-1]]
        c.blob((key, 'water'), poly, TEAL)
        if sa > 0:
            c.blob((key, 'sw'), rect(631, GROUND - 1, 649, GROUND + 12), TEAL, alpha=min(1, water * 3) * sa)


# droplet field (scene 3 -> 4)
_rs = np.random.RandomState(8)
DROPS = []
for i in range(34):
    x = _rs.uniform(548, 732); y = _rs.uniform(500, 680)
    slow = i % 5 == 0
    DROPS.append(dict(x=x, y=y, t_in=d + 4.9 + _rs.uniform(0, 3.0), r=_rs.uniform(1.8, 2.8), slow=slow,
                      t_sink=(m - 0.2 + _rs.uniform(0, .6)) if not slow else (m + 9.6 + _rs.uniform(0, .5)),
                      v=_rs.uniform(70, 110) if not slow else _rs.uniform(90, 120)))
COND = [(_rs.choice([538, 742]) + _rs.uniform(-1, 1), _rs.uniform(446, 484), _rs.uniform(1.4, 2.2),
         d + 3.4 + _rs.uniform(0, 1.6)) for _ in range(12)]


def drop_state(D, t, fk):
    """returns (x, y, alpha) of a droplet that appears, sinks, slides into the sump."""
    if t < D['t_in']:
        return None
    a = cl((t - D['t_in']) / .5)
    if t < D['t_sink']:
        return D['x'], D['y'] + .6 * math.sin(t * 2 + D['x']), a
    ts = t - D['t_sink']
    fy = floor_y(D['x'], 1.0) - 2
    fall = (fy - D['y']) / D['v']
    if ts < fall:
        u = ts / fall
        return D['x'], D['y'] + (fy - D['y']) * (u * u * .4 + u * .6), a
    s = cl((ts - fall) / .7)
    x = D['x'] + (640 - D['x']) * s
    return x, floor_y(x, 1.0) - 2, a * (1 - ss(s, .7, 1))


def water_level(t):
    # fills as droplets arrive, empties when the sump is drained
    return .55 * ss(t, m + 0.6, m + 3.4) + .45 * ss(t, m + 10.4, m + 12.4) - ss(t, k + 7.0, k + 8.2)


PIPES = dict(
    P1=[(-150, 672), (306, 672)],
    P2=[(352, 680), (530, 680)],
    P2b=[(440, 680), (440, 694), (820, 694)],
    P3=[(750, 668), (1132, 668)],
    P4=[(1268, 668), (1470, 668), (1470, 700)],
)
CERT = dict(cx=860, cy=420, w=560, h=340, ang=math.radians(-3))
CERT_ROWS = [('Density @ 15 °C', '801.4 kg/m³'), ('Freezing point', '−51 °C'), ('Flash point', '42 °C'),
             ('Appearance', 'clear & bright')]
ROW_Y = [-34, 6, 46, 86]
LINE_TO = [PIPES['P1'], PIPES['P2'], PIPES['P3'], PIPES['P4'][:2]]


def cert_tf(P, t):
    slide = 1 - ss(t, h - 0.6, h + 0.5)
    sh = 1 - ss(t, w - 1.0, w - 0.1)
    s = max(sh, .001)
    pts = xform(P, 0, 0, 1, CERT['ang'], CERT['cx'] - 900 * slide, CERT['cy'])
    return xform(pts, 330, 640, s)


def draw_cert(c, t):
    if t > w + .3:
        return
    hw, hh = CERT['w'] / 2, CERT['h'] / 2
    a = 1 - ss(t, w - 0.4, w - 0.1)
    c.paper('cert', cert_tf(rect(-hw, -hh, hw, hh), t), PAPER, shadow=1, fringe=1, outline=.5, alpha=a, lift=1.5)
    sc = 1 - ss(t, w - 1.0, w - 0.1)
    if sc > .35:
        T = lambda P: cert_tf(P, t)
        ta = a * ss(sc, .35, .7)
        c.text('CERTIFICATE OF QUALITY', T([(-40, -125)])[0], 34 * sc, fnt='cav', weight=700, alpha=ta,
               angle=3)
        c.text('Jet A-1  ·  DEF STAN 91-091 / AFQRJOS', T([(-40, -88)])[0], 22 * sc, alpha=ta * .9, angle=3)
        for (lab, val), y in zip(CERT_ROWS, ROW_Y):
            c.text(lab, T([(-232, y - 14)])[0], 21 * sc, alpha=ta, anchor='lm', angle=3)
            c.text(val, T([(118, y - 14)])[0], 21 * sc, alpha=ta, anchor='rm', angle=3, col=TEALD)
        # stamp
        sa, s2 = pop(t, h + 2.2, .3)
        if sa > 0:
            S = lambda P: T(xform(P, 0, 0, 1 + (1.6 - 1.6 * s2 + .6) * (1 - sa), 0, 200, 55))
            c.crayon('stampring', S(ellipse(0, 0, 54, 54, 40)), TEAL, 4 * sc, alpha=sa * ta * .9, screen=True,
                     closed=True, wscale=False)
            c.text('REFINERY', S([(0, -22)])[0], 15 * sc, col=TEAL, weight=700, alpha=sa * ta, angle=3)
            checkmark(c, 'stampchk', *S([(0, 12)])[0], 40 * sc, alpha=sa * ta, screen=True)
        la, ls = pop(t, h + 6.5, .35)
        if la > 0:
            L = lambda P: T(xform(P, 0, 0, ls, 0, 248, -150))
            c.crayon('shackle', L(ellipse(0, -10, 16, 18, 20, math.pi, 2 * math.pi)), CHAR, 6 * sc, alpha=la * ta,
                     screen=True, wscale=False)
            c.paper('lockbody', L(rrect(-24, -10, 24, 26, 5)), MUSTARD, shadow=1, fringe=1, outline=.5,
                    alpha=la * ta, screen=True)
            c.paper('keyhole', L(ellipse(0, 6, 4, 5, 10)), CHAR, shadow=0, fringe=0, alpha=la * ta, screen=True)


def draw_cert_lines(c, t):
    """the certificate's ruled lines stretch into the farm's pipelines."""
    u = ss(t, w - 1.2, w + 0.3)
    if u <= 0 or t > w + .9:
        return
    fade = 1 - ss(t, w + .3, w + .8)
    for i, (y, dst) in enumerate(zip(ROW_Y, LINE_TO)):
        src = cert_tf([(-232, y), (118, y)], min(t, w - 1.2))
        P = lerp_pts(src, [dst[0], dst[-1]], ss(u, i * .08, .7 + i * .08))
        c.crayon(('cl', i), P, TEALD, 3 + 9 * u, alpha=fade, screen=False, wscale=False)


def draw_farm(c, t):
    if t < w - .05:
        return
    for i, key in enumerate(['P1', 'P2', 'P2b', 'P3', 'P4']):
        pa = ss(t, w + .2, w + .6)
        pipe(c, key, PIPES[key], alpha=pa)
    # flows
    fin = ss(t, w + 1.7, w + 2.0) - ss(t, w + 3.7, w + 4.0)
    fout = ss(t, w + 6.0, w + 6.3) - ss(t, w + 8.4, w + 8.8)
    if fin > 0:
        for key in ('P1', 'P2', 'P2b'):
            flow(c, ('fl', key), PIPES[key], t, alpha=fin)
    if fout > 0:
        for key in ('P3', 'P4'):
            flow(c, ('fl', key), PIPES[key], t, alpha=fout)
    # receipt filter
    a, s = farm_pop(t, 0)
    tr = lambda P: xform(P, 330, 690, s, 0, 0, (1 - s) * -60)
    c.paper('rf', tr(rrect(306, 598, 354, 690, 12)), TEAL, shadow=1, fringe=1, outline=.5, alpha=a, lift=1.1)
    c.paper('rfcap', tr(rect(300, 594, 360, 606)), CHAR, shadow=.5, fringe=.6, alpha=a)
    # sign
    a, s = farm_pop(t, 5)
    tr = lambda P: xform(P, 236, 700, s, 0, 0, (1 - s) * -60)
    c.paper('post', tr(rect(231, 520, 241, 700)), CHAR, shadow=.8, fringe=.6, alpha=a)
    c.paper('board', tr(rect(140, 470, 332, 526)), PAPER, shadow=1, fringe=1, outline=.5, alpha=a, lift=1.1)
    c.text('JIG 2 · airport depot', tr([(236, 498)])[0], 25 * s, alpha=a)


def tank_params(t):
    peel = ss(t, d - 0.2, d + 0.8)
    cut = 1.0 if t > d - .3 and t < r - .4 else 0.0
    if t >= r - .4:        # back to the wide shot: front panel restored ("sealed")
        peel = 1 - ss(t, q + 9.0, r - .5) if t < r - .4 else 0.0
    return peel, cut


def draw_tanks(c, t):
    if t < w - .05:
        return
    a1, s1 = farm_pop(t, 1)
    a2, s2 = farm_pop(t, 2)
    lvl = .35 + .5 * ss(t, w + 3.6, w + 5.8)
    tr2 = lambda P: xform(P, 930, GROUND, s2, 0, 0, (1 - s2) * -60)
    draw_tank(c, 'TB', TB[0], TB[1], t, tr2, a2, lvl * .9)
    tr1 = lambda P: xform(P, 640, GROUND, s1, 0, 0, (1 - s1) * -60)
    in_view = d - .3 < t < q + .5
    if in_view:
        peel = ss(t, d - 0.2, d + 0.8)
        draw_tank(c, 'TA', TA[0], TA[1], t, tr1, a1, lvl, cut=1, peel=peel, floor_k=ss(t, m - 0.6, m + 0.6),
                  water=water_level(t))
    else:
        draw_tank(c, 'TA', TA[0], TA[1], t, tr1, a1, lvl)


def draw_fws(c, t):
    if t < w - .05:
        return
    a, s = farm_pop(t, 3)
    tr = lambda P: xform(P, 1200, 690, s, 0, 0, (1 - s) * -60)
    c.paper('fws', tr(rrect(1128, 632, 1272, 696, 30)), TEAL, shadow=1, fringe=1, outline=.5, alpha=a, lift=1.1)
    c.paper('fwsleg1', tr(rect(1150, 694, 1160, 702)), CHAR, shadow=.3, fringe=.3, alpha=a)
    c.paper('fwsleg2', tr(rect(1240, 694, 1250, 702)), CHAR, shadow=.3, fringe=.3, alpha=a)
    c.paper('dpg', tr(ellipse(1200, 622, 13, 13, 18)), PAPER, shadow=.6, fringe=.6, outline=.6, alpha=a)
    c.pencil('dpn', tr([(1200, 622), (1207, 615)]), alpha=a * .8)
    c.paper('fwsdrain', tr(rect(1196, 696, 1204, 702)), CHAR, shadow=.2, fringe=.2, alpha=a)


def draw_aircraft(c, t):
    if t < w - .05:
        return
    a, s = farm_pop(t, 4)
    tr = lambda P: xform(P, 1640, 640, s, 0, 0, (1 - s) * -60)
    c.paper('fin', tr([(1712, 548), (1738, 452), (1772, 452), (1772, 552)]), CORAL, shadow=1, fringe=1,
            outline=.4, alpha=a)
    c.paper('fus', tr(rrect(1500, 540, 1782, 596, 28)), PAPER, shadow=1, fringe=1, outline=.5, alpha=a, lift=1.2)
    c.paper('cockpit', tr(rrect(1512, 552, 1532, 564, 4)), TEALD, shadow=0, fringe=0, alpha=a)
    for i in range(6):
        c.paper(('win', i), tr(rrect(1552 + i * 28, 556, 1564 + i * 28, 566, 4)), TEAL, shadow=0, fringe=0,
                alpha=a)
    c.paper('wing', tr([(1590, 586), (1690, 586), (1650, 628), (1610, 628)]), mix(PAPER, CHAR, .14), shadow=1,
            fringe=.8, outline=.4, alpha=a, lift=1.3)
    c.paper('eng', tr(rrect(1592, 612, 1650, 640, 12)), CHAR, shadow=1, fringe=.6, alpha=a)
    c.paper('gear', tr(rect(1716, 596, 1722, 690)), CHAR, shadow=.4, fringe=.3, alpha=a)
    c.paper('wheel', tr(ellipse(1719, 690, 10, 10, 14)), CHAR, shadow=.6, fringe=.4, alpha=a)
    # hydrant dispenser hose from pit to wing
    c.paper('pit', tr(rect(1458, 696, 1484, 704)), CHAR, shadow=0, fringe=.4, alpha=a)
    c.crayon('hose', tr(bezier((1471, 700), (1520, 700), (1580, 660), (1622, 626), 20)), CHAR, 3.5, alpha=a)


ZONES = [('receipt', 330, 0), ('storage', 785, .5), ('issue', 1200, 1.0)]


def draw_zone_labels(c, t):
    for lab, x, dt in ZONES:
        a = ss(t, w + 9.25 + dt, w + 9.55 + dt)
        if a > 0:
            n = max(2, int(14 * a))
            c.text(lab, (x, 742), 32, alpha=a)
            c.pencil(('zl', lab), sub_polyline([(x - 60, 760), (x + 60, 757)], 0, a, n), alpha=.6)


# ---- scene 3/4/5 tank details
def draw_tank_story(c, t):
    if not (d - 1 < t < q + 1.5):
        return
    # thermometer: the night cools the air
    ta = ss(t, d - 0.6, d) * (1 - ss(t, m - 0.4, m + 0.4))
    if ta > 0:
        col = .78 - .45 * ss(t, d + 0.0, d + 2.0)
        c.paper('th', rrect(472, 462, 488, 630, 8), PAPER, shadow=.9, fringe=.8, outline=.6, alpha=ta)
        c.paper('thb', ellipse(480, 636, 14, 14, 20), CORAL, shadow=.6, fringe=.6, alpha=ta)
        c.blob('thc', rect(476, 630 - 160 * col, 484, 634), CORAL, alpha=ta)
        for i in range(6):
            c.pencil(('tk', i), [(488, 480 + i * 26), (494, 480 + i * 26)], alpha=.5 * ta)
    # vent label + damp-air wisps
    va = ss(t, d + 2.6, d + 2.9) * (1 - ss(t, m + 0.0, m + 0.6))
    if va > 0:
        c.text('vent', (690, 382), 17, alpha=va)
        c.pencil('ventarrow', [(672, 386), (652, 392)], alpha=va * .6)
    for i in range(3):
        u = (t - (d + 2.7 + i * .45)) / 1.6
        if 0 < u < 1:
            x0, y0 = 560 + i * 18, 368 - i * 8
            P = [(x0 + (640 - x0) * s_ + 5 * math.sin(s_ * 9 + i), y0 + (APEX - 14 - y0) * s_) for s_ in
                 np.linspace(max(0, u - .45), u, 10)]
            c.crayon(('wisp', i), P, TEAL, 2.5, alpha=math.sin(u * math.pi), wax=.5)
            if u > .55:   # air carries moisture inside, under the roof
                pass
    for i, (x, y, rr, t0) in enumerate(COND):
        a = ss(t, t0, t0 + .5) * (1 - ss(t, m - .3, m + .6))
        if a > 0:
            droplet(c, ('cond', i), x + (3 if x < 640 else -3), y + 18 * ss(t, m - .3, m + .6), rr, a)
    # droplets
    if t < k + 3:
        for i, D in enumerate(DROPS):
            st = drop_state(D, t, 1.0)
            if st:
                droplet(c, ('drop', i), st[0], st[1], D['r'], st[2])
    # density tags
    for i, (txt, y, ty) in enumerate([('Jet A-1  ≈ 0.80 kg/L', 520, 560), ('water  1.00 kg/L', 655, 693)]):
        a, s = pop(t, m + .6 + i * 1.0, .35)
        a *= 1 - ss(t, m + 15.5, m + 16.2)
        if a > 0:
            tag(c, ('dt', i), txt, 840, y, 16, alpha=a, string_to=(700 if i == 0 else 655, ty - 30 * (i == 0)))
    # 'JIG design' : pencil construction lines over the tank
    da = ss(t, m + 3.3, m + 5.3)
    fa = 1 - ss(t, m + 5.8, m + 6.6)
    if da > 0 and fa > 0:
        box = [(522, 432), (758, 432), (758, 708), (522, 708), (522, 432)]
        c.pencil('dbox', sub_polyline(box, 0, da, 40), alpha=.55 * fa, dash=(10, 7, 0))
        c.pencil('dctr', sub_polyline([(640, 392), (640, 720)], 0, da, 20), alpha=.4 * fa, dash=(16, 5, 0))
        c.pencil('ddim', sub_polyline([(530, 724), (750, 724)], 0, da, 20), alpha=.5 * fa)
        for x in (530, 750):
            c.pencil(('ddt', x), [(x, 718), (x, 730)], alpha=.5 * fa * da)
    # slope arrows toward the sump
    sa = ss(t, m + 6.5, m + 7.4) * (1 - ss(t, m + 12.0, m + 12.8))
    if sa > 0:
        for sgn in (-1, 1):
            x0 = 640 + sgn * 92
            P = [(x0, floor_y(x0, 1) - 8), (640 + sgn * 22, floor_y(640 + sgn * 22, 1) - 8)]
            c.arrow(('sl', sgn), sub_polyline(P, 0, sa, 10), CHAR, 2.6, alpha=.8, head=7)
    pa = ss(t, m + 8.4, m + 8.7) * (1 - ss(t, m + 10, m + 10.6))
    if pa > 0:
        c.crayon('sumpring', ellipse(640, 706, 22, 16, 30), CORAL, 2.6, alpha=pa, closed=True)
    # drain + valve, extended into the sampling path later
    dra = ss(t, m + 8.4, m + 8.9)
    if dra > 0:
        pipe(c, 'drain', [(640, 712), (640, 722), (560, 722)], hw=3.2, col=CHAR, alpha=dra, shadow=.4)
        open_ = ss(t, k + 6.8, k + 7.1)
        ang = open_ * math.pi / 2
        V = xform([(-7, -6), (7, 6), (7, -6), (-7, 6)], 0, 0, 1, ang, 560, 722)
        c.paper('valve', V, CORAL, shadow=.5, fringe=.5, alpha=dra)
    # settling hourglass: flips, then sand runs while the slow droplets sink
    ha = ss(t, m + 9.6, m + 10.0) * (1 - ss(t, k + 2.2, k + 2.8))
    if ha > 0:
        flip = ss(t, m + 10.1, m + 10.5)
        sand = ss(t, m + 10.5, m + 12.6)
        hourglass(c, 'hg', 455, 600, 1.0, math.pi * (1 - flip), sand if flip > .99 else 1 - 0, alpha=ha)
    # floating suction arm
    fa_ = ss(t, m + 12.9, m + 13.3)
    if fa_ > 0 and t < q + 1.0:
        pv = (737, 668)
        L = 196.0
        a0 = math.atan2(0, -1) + .05
        a1 = math.atan2(FUEL_TOP + 4 - pv[1], -math.sqrt(L * L - (FUEL_TOP + 4 - pv[1]) ** 2))
        ang = a0 + (a1 - a0) * back(cl((t - (m + 13.2)) / 1.1)) if t > m + 13.2 else a0
        tip = (pv[0] + L * math.cos(ang), pv[1] + L * math.sin(ang))
        pipe(c, 'arm', [pv, tip], hw=4.0, col=CHAR, alpha=fa_, shadow=.5)
        c.paper('float', xform(rrect(-20, -7, 20, 7, 6), 0, 0, 1, 0, tip[0], tip[1] - 3), CORAL, shadow=.7,
                fringe=.7, outline=.5, alpha=fa_)
        c.paper('pivot', ellipse(pv[0], pv[1], 7, 7, 12), CHAR, shadow=.4, fringe=.5, alpha=fa_)
        fl = ss(t, m + 14.3, m + 14.6) * (1 - ss(t, k + 1.0, k + 1.6))
        if fl > 0:
            flow(c, 'armflow', [tip, pv, (800, 668)], t, alpha=fl, w_=3.0)
    # ------------- discovery: gravity, the daily drain, the jar
    ga = ss(t, k + 2.4, k + 3.0) * (1 - ss(t, k + 6.0, k + 6.8))
    if ga > 0:
        c.arrow('grav', sub_polyline([(640, 506), (640, 650)], 0, ga, 12), CHAR, 7, alpha=.85, head=18)
    wk = ss(t, k + 4.6, k + 5.0) * (1 - ss(t, q - .6, q))
    if wk > 0:
        for i in range(7):
            x = 252 + i * 23
            c.paper(('day', i), rect(x, 416, x + 19, 436), PAPER, shadow=.7, fringe=.6, outline=.5, alpha=wk)
            pr = cl((t - (k + 5.0 + i * .28)) / .22)
            if pr > 0:
                checkmark(c, ('dck', i), x + 9.5, 426, 14, pr, alpha=wk, wd=2.6)
    # sampling path: drain line extends past the valve, rises to a spout
    pth = [(560, 722), (520, 722), (520, 646), (497, 646), (497, 652)]
    pa = ss(t, k - 0.6, k + 0.8)
    if pa > 0 and t < q + 1.0:
        pipe(c, 'samp', sub_polyline(pth, 0, pa, 30), hw=3.2, col=CHAR, alpha=1, shadow=.4)
    # containers: bucket first (water), then the jar slides under the spout
    bx = 497 - 70 * ss(t, k + 8.1, k + 8.5)
    jx = 497 - 140 * (1 - ss(t, k + 8.1, k + 8.5))
    ca = ss(t, k + 5.9, k + 6.3) * (1 - ss(t, q - .5, q + .3))
    if ca > 0:
        c.paper('bucket', [(bx - 20, 668), (bx + 20, 668), (bx + 16, 700), (bx - 16, 700)], mix(CREAM, CHAR, .35),
                shadow=.9, fringe=.8, outline=.6, alpha=ca)
        bw = ss(t, k + 7.1, k + 8.0)
        if bw > 0:
            c.blob('bw', [(bx - 18, 698 - 16 * bw), (bx + 18, 698 - 16 * bw), (bx + 16, 699), (bx - 16, 699)], TEAL,
                   alpha=ca)
        jf = ss(t, k + 8.6, k + 9.4)
        jar(c, 'sj', jx, 700, .62, jf, alpha=ca, glint=ss(t, k + 9.2, k + 9.5))
        # drops falling from the spout
        for i in range(10):
            tt = k + 7.0 + i * .13
            if tt < t < tt + .35 and t < k + 8.1:
                u = (t - tt) / .35
                droplet(c, ('sp', i), 497, 654 + 30 * u, 1.8, 1)
        if k + 8.6 < t < k + 9.4:
            c.crayon('stream', [(497, 654), (497, 690 - 24 * jf)], FUEL, 2.4, alpha=1)
    for i, txt in enumerate(['water detector', 'density @ 15 °C']):
        a, s = pop(t, k + 9.6 + i * .7, .3)
        a *= 1 - ss(t, q - .5, q + .1)
        if a > 0:
            tag(c, ('ck', i), txt, 432, 458 + i * 34, 14, alpha=a, ang=-2 + 3 * i, check=True)


# ---- scene 6: the drop that skipped a step
FLIGHT = bezier((800, 668), (1400, 660), (2000, -420), (2735, -224), 80)
WING_UP = bezier((2330, -205), (2420, -300), (2850, -300), (3420, -236), 50)
WING_LO = bezier((3420, -236), (2900, -196), (2460, -160), (2330, -205), 50)
FEED_X = 2760
FILTER = (FEED_X, -150)
CRY = [(FEED_X - 8, -158), (FEED_X + 7, -156), (FEED_X - 1, -147), (FEED_X - 9, -143), (FEED_X + 8, -144),
       (FEED_X, -160), (FEED_X - 4, -151), (FEED_X + 4, -150)]


def draw_flight(c, t):
    if not (q - 1.0 < t < r + 1.0):
        return
    u = ss(t, q - 0.9, q + 1.1)
    ret = ss(t, q + 8.9, r + 0.7)
    if u > 0 and ret < 1:
        c.pencil('fpath', sub_polyline(FLIGHT, 0, u * (1 - ret), 80), alpha=.7, dash=(14, 10, 0), w=2.6)


def draw_wing(c, t):
    if not (q - 1.0 < t < r + 1.0):
        return
    wing = WING_UP + WING_LO
    c.paper('wing6', wing, PAPER, shadow=1, fringe=1, outline=.6, lift=1.5)
    up = [p for p in WING_UP if 2480 < p[0] < 3180]
    lo = [p for p in WING_LO if 2480 < p[0] < 3180]
    tank = [(x, y + 7) for x, y in up] + [(x, y - 6) for x, y in lo]
    c.blob('wfuel', tank, FUEL)
    c.pencil('spar1', [(2480, -282), (2480, -178)], alpha=.6)
    c.pencil('spar2', [(3180, -277), (3180, -214)], alpha=.6)
    # pylon, nacelle, feed line with its filter
    c.paper('pylon', [(2700, -190), (2790, -190), (2770, -110), (2720, -110)], CHAR, shadow=.8, fringe=.6)
    c.paper('nac', rrect(2600, -118, 2900, -40, 36), CORAL, shadow=1, fringe=1, outline=.5, lift=1.3)
    c.paper('intake', ellipse(2608, -79, 14, 37, 20), CORALD, shadow=0, fringe=0)
    c.pencil('feed', [(FEED_X, -184), (FEED_X, -120)], alpha=.9, w=4)
    c.paper('filt', rect(FEED_X - 14, -164, FEED_X + 14, -136), PAPER, shadow=.7, fringe=.7, outline=.7)
    for i in range(5):
        c.pencil(('mx', i), [(FEED_X - 13, -162 + i * 6), (FEED_X + 13, -162 + i * 6)], alpha=.45, w=1.3)
        c.pencil(('my', i), [(FEED_X - 11 + i * 5.5, -163), (FEED_X - 11 + i * 5.5, -137)], alpha=.45, w=1.3)
    # flow to the engine slows as ice builds on the filter
    clog = ss(t, q + 6.4, q + 8.2)
    col = mix(MUSTARD, CORAL, clog)
    if clog < .98:
        c.crayon('eflow', [(FEED_X + 4, -184), (FEED_X + 4, -120), (2700, -100), (2640, -80)], col, 3.2,
                 alpha=1 - clog * .6, dash=(9, 11, -(t * 55 - 30 * clog * clog)), wax=.3)
    wa, ws = pop(t, q + 8.0, .3)
    if wa > 0:
        c.paper('warn', xform([(0, -24), (22, 14), (-22, 14)], 0, 0, ws, 0, 2840, -165), CORAL, shadow=1, fringe=1,
                outline=.6, alpha=wa)
        c.paper('warn!', rect(2838, -160, 2842, -146), CHAR, shadow=0, fringe=0, alpha=wa)
        c.paper('warn.', rect(2838, -142, 2842, -138), CHAR, shadow=0, fringe=0, alpha=wa)
    for i, (txt, x, y, t0) in enumerate([('water: ice at 0 °C', 2520, -32, q + 3.1),
                                          ('Jet A-1 stays liquid to −47 °C', 2980, -335, q + 4.0)]):
        a, s = pop(t, t0, .35)
        if a > 0:
            tag(c, ('wt', i), txt, x, y, 18, alpha=a * (1 - ss(t, q + 8.8, q + 9.4)), ang=(-2, 2)[i])


def draw_travellers(c, t):
    """droplets ride the flight path into the wing, freeze, and collect on the filter."""
    if not (q - 1.0 < t < r + 1.0):
        return
    ends = [(2735, -224), (2752, -206), (2772, -204), (2730, -206)]
    starts = [q - 0.7, q - 0.25, q + 0.15, q + 0.5]
    fade = 1 - ss(t, q + 8.8, q + 9.6)
    for i, (t0, e) in enumerate(zip(starts, ends)):
        u = ss(t, t0, t0 + 2.0)
        if u <= 0:
            continue
        if u < 1:
            p, _ = polyline_at(FLIGHT, u)
            droplet(c, ('tr', i), p[0], p[1], 3.2 if c.z < 1.5 else 2.6, 1.0)
            continue
        sink = ss(t, t0 + 2.0, t0 + 2.6)
        x, y = 2735 + (e[0] - 2735) * sink, -224 + (e[1] + 4 - -224) * sink
        frz = ss(t, q + 4.6 + i * .15, q + 5.4 + i * .15)
        mv = ss(t, q + 5.6 + i * .3, q + 6.6 + i * .3)
        cx_, cy_ = CRY[i]
        x, y = x + (cx_ - x) * mv, y + (cy_ - y) * mv
        if frz < 1:
            droplet(c, ('tr', i), x, y, 3.2 * (1 - frz * .7), (1 - frz) * fade)
        if frz > 0:
            crystal(c, ('cr', i), x, y, 6 * frz, frz * fade)
    # more crystals keep arriving from upstream, clogging the screen
    for j in range(4, 8):
        a = ss(t, q + 6.6 + (j - 4) * .35, q + 7.0 + (j - 4) * .35) * fade
        if a > 0:
            x, y = CRY[j]
            crystal(c, ('crx', j), x, y - 20 * (1 - a), 5.5, a)


# ---- scene 7: the separator in close-up + the release form
def draw_recap(c, t):
    if t < r - 0.5:
        return
    out = 1 - ss(t, r + 6.2, r + 7.0)
    ma, ms = pop(t, r + 0.0, .45)
    ma *= out
    if ma > 0:
        M = lambda P: xform(P, 0, 0, ms, 0, 1240, 300)
        c.pencil('mg1', [(1240 - 106 * ms, 300 + 106 * ms), (1160, 640)], alpha=.5 * ma)
        c.pencil('mg2', [(1240 + 106 * ms, 300 + 106 * ms), (1255, 640)], alpha=.5 * ma)
        c.paper('mag', M(ellipse(0, 0, 150, 150, 60)), PAPER, shadow=1, fringe=1, outline=.6, alpha=ma, lift=1.6)
        c.paper('mag_h', M(rrect(-120, -55, 120, 65, 46)), mix(TEAL, CREAM, .55), shadow=0, fringe=0, alpha=ma)
        for i in range(3):
            x = -60 + i * 60
            c.paper(('el', i), M(rrect(x - 16, -40, x + 16, 40, 8)), PAPER, shadow=.4, fringe=0, alpha=ma)
            for j in range(5):
                c.pencil(('elp', i, j), M([(x - 10 + j * 5, -36), (x - 10 + j * 5, 36)]), alpha=.4 * ma, w=1.4)
        c.paper('mag_sump', M(rect(-14, 64, 14, 92)), mix(TEAL, CREAM, .55), shadow=.4, fringe=0, alpha=ma)
        c.crayon('mag_flow', M([(-140, 0), (140, 0)]), MUSTARD, 3.5, alpha=ma * .9, dash=(14, 12, -t * 60),
                 wax=.3, screen=False)
        # droplets: come in small, merge on the elements, fall to the sump
        for i in range(7):
            ph = ((t - r) * .55 + i / 7.0) % 1.0
            if t - r < i * .3:
                continue
            x0 = -130 + ph * 140
            y0 = -26 + 52 * rnd('md', i)
            if ph < .55:
                p = (x0, y0); rr = 2.2 + 3 * ph
            else:
                v = (ph - .55) / .45
                p = (-130 + .55 * 140 + 10 * v, y0 + (80 - y0) * v * v); rr = 4
            pp = M([p])[0]
            droplet(c, ('md', i), pp[0], pp[1], rr * ms, ma)
        c.blob('mag_pool', M(rect(-12, 80, 12, 90)), TEAL, alpha=ma * ss(t, r + 1.5, r + 3))
    ea, es = pop(t, r + 1.2, .3)
    ea *= out
    if ea > 0:
        tag(c, 'ei', 'EI 1581', 1200, 608, 18, alpha=ea, ang=3)
    # release form on a clipboard
    fa = ss(t, r + 3.0, r + 3.6) * out
    if fa > 0:
        dy = -120 * (1 - fa)
        F = lambda P: xform(P, 0, 0, 1, math.radians(-3), 0, dy)
        c.paper('clip', F(rrect(330, 190, 570, 470, 10)), TAN, shadow=1, fringe=1, outline=.4, alpha=fa, lift=1.5)
        c.paper('sheet', F(rect(346, 214, 554, 458)), PAPER, shadow=.6, fringe=.8, alpha=fa)
        c.paper('clp', F(rrect(410, 180, 490, 206, 6)), CHAR, shadow=.6, fringe=.5, alpha=fa)
        c.text('Batch 0427 · Tank 1', F([(450, 238)])[0], 22, alpha=fa, angle=3, weight=700)
        for i, lab in enumerate(['appearance', 'water', 'density', 'filter pressure']):
            y = 274 + i * 30
            c.text(lab, F([(362, y)])[0], 19, alpha=fa, anchor='lm', angle=3)
            checkmark(c, ('fck', i), *F([(528, y)])[0], 15, cl((t - (r + 3.4 + i * .18)) / .2), alpha=fa,
                      screen=False, wd=2.6)
        c.pencil('sigline', F([(362, 430), (530, 430)]), alpha=.6 * fa)
        sp = ss(t, r + 3.7, r + 5.2)
        if sp > 0:
            sig = [(366 + i * 2.6, 420 - 10 * math.sin(i * .55) * (1 if i % 9 < 6 else .3) - 5 * math.sin(i * .21))
                   for i in range(60)]
            c.pencil('sig', F(sub_polyline(sig, 0, sp, 60)), alpha=fa, w=2.4)
        sa, s2 = pop(t, r + 5.5, .25)
        if sa > 0:
            S = lambda P: F(xform(P, 0, 0, 1 + .5 * (1 - s2), 0, 505, 400))
            c.crayon('fstamp', S(ellipse(0, 0, 26, 26, 30)), TEAL, 3.2, alpha=sa * fa * .9, closed=True)
            checkmark(c, 'fstampck', *S([(0, 2)])[0], 22, alpha=sa * fa, wd=3.2)


def draw_world(c, t):
    backdrop(c, t)
    draw_flight(c, t)
    draw_cert(c, t)
    draw_farm(c, t)
    draw_tanks(c, t)
    draw_fws(c, t)
    draw_aircraft(c, t)
    draw_cert_lines(c, t)
    draw_zone_labels(c, t)
    draw_tank_story(c, t)
    draw_wing(c, t)
    draw_travellers(c, t)
    draw_recap(c, t)


# ------------------------------------------------------------- screen space ----
BOT = ["....AA....",
       ".....K....",
       ".CCCCCCCC.",
       "CCCCCCCCCC",
       "CCEECCEECC",
       "CCEECCEECC",
       "CCCCCCCCCC",
       ".CCCCCCCC.",
       ".CC....CC.",
       ".KK....KK."]
CELL = 10
MOVES = [(w - 1.0, w - 0.1, 1480, 300), (d - 1.0, d - 0.3, 300, 330), (q - 0.6, q + 0.4, 330, 420),
         (q + 8.8, r - 0.1, 420, 300), (r + 9.4, r + 10.4, 300, 960)]


def bot_state(t):
    x, yoff = 1480, 0.0
    for t0, t1, a, b in MOVES:
        if t >= t1:
            x = b
        elif t >= t0:
            u = (t - t0) / (t1 - t0)
            x = a + (b - a) * u
            hops = max(1, round(abs(b - a) / 230))
            yoff = -abs(math.sin(math.pi * hops * u)) * 26
            break
    face = -1 if t < w - 1.0 else 1
    if r + 10.4 < t:
        face = 0
    pose = 'stand'
    for a_, b_, p in [(w + 1.5, w + 9.2, 'point'), (d + 2.6, d + 4.8, 'point'), (m + 3.2, m + 6.0, 'point'),
                      (m + 13.0, m + 15.0, 'point'), (k + 9.5, k + 11.0, 'point'), (q + 4.6, q + 7.0, 'point'),
                      (r + 0.2, r + 2.2, 'point'), (r + 10.4, END + 5, 'hold')]:
        if a_ <= t < b_:
            pose = p
    if h + 4.7 < t < h + 7.5:
        pose = 'shrug'
    return x, FEET + yoff, face, pose


def draw_bot(c, t):
    x, feet, face, pose = bot_state(t)
    x0, y0 = x - 5 * CELL, feet - 10 * CELL
    cells = {}
    for ry, row in enumerate(BOT):
        for rx, ch in enumerate(row):
            if ch != '.':
                cells[(rx, ry)] = ch
    for p in [(rx, ry) for (rx, ry), ch in cells.items() if ch == 'E']:
        cells[p] = 'C'
    arms = []
    if pose == 'point':
        arms = [(10, 5), (11, 4)] if face >= 0 else [(-1, 5), (-2, 4)]
    elif pose == 'hold':
        arms = [(-1, 3), (-1, 2), (-1, 1), (10, 3), (10, 2), (10, 1)]
    elif pose == 'shrug':
        arms = [(-1, 4), (-2, 3), (10, 4), (11, 3)]
    for p in arms:
        cells[p] = 'C'
    groups = {'C': [], 'K': [], 'A': []}
    for (rx, ry), ch in cells.items():
        jx = (rnd('b', rx, ry, c.bseed) - .5) * 1.6; jy = (rnd('b', ry, rx, c.bseed) - .5) * 1.6
        sq = rect(x0 + rx * CELL + jx - .5, y0 + ry * CELL + jy - .5, x0 + (rx + 1) * CELL + jx + .5,
                  y0 + (ry + 1) * CELL + jy + .5)
        groups[ch].append(np.asarray(sq))
    # one cardboard shadow for the whole bot + a contact shadow on the apron
    allp = [p for g in groups.values() for p in g]
    box = c._box(allp, 26)
    if box:
        ms = c._raster([p + np.array([5, 6]) for p in allp], box, 1)
        c.comp(box, c._blur_shadow(ms, 8) * .25, SHADOW, textured=False)
    c.paper('botshadow', ellipse(x, FEET + 3, 46 - min(20, -(feet - FEET) * .5), 6, 20), SHADOW, shadow=0, fringe=0,
            alpha=.3, screen=True)
    for ch, col in (('C', CORAL), ('K', CHAR), ('A', CORALD)):
        if groups[ch]:
            b2 = c._box(groups[ch], 3)
            if b2:
                c.comp(b2, c._raster(groups[ch], b2), col)
    # eyes: black, 2x2 cells, glance toward what matters; blink every ~3 s
    blink = ((t + .7) % 3.1) < .12
    gl = .35 * face
    for ex in (2, 6):
        ex0 = x0 + (ex + gl) * CELL; ey0 = y0 + 4 * CELL
        eh = 2 * CELL if not blink else .5 * CELL
        ey = ey0 + (2 * CELL - eh) / 2
        b2 = c._box([np.asarray(rect(ex0, ey, ex0 + 2 * CELL, ey + eh))], 2)
        if b2:
            c.comp(b2, c._raster([rect(ex0, ey, ex0 + 2 * CELL, ey + eh)], b2), BLACK, textured=False)
    return x, feet, pose


def draw_question(c, t, bx):
    a, s = pop(t, h + 4.7, .35)
    a *= 1 - ss(t, w - 1.3, w - 1.0)
    if a > 0:
        cx, cy = bx - 6, FEET - 165
        c.paper('qbg', xform(ellipse(0, 0, 40, 44, 30), 0, 0, s, 0, cx, cy), PAPER, shadow=1, fringe=1, alpha=a,
                screen=True)
        c.text('?', (cx, cy + 2), 70 * s, col=CORAL, fnt='cav', weight=700, alpha=a, screen=True)


def draw_icons(c, t):
    """Recap: gravity, time, testing -> regroup into the single jar the bot holds up."""
    if t < r + 6.6:
        return
    g = ss(t, r + 9.4, r + 10.8)
    hold = (960, FEET - 9 * CELL - 2)
    spots = [(760, 330), (960, 330), (1160, 330)]
    t0s = [r + 6.8, r + 7.6, r + 8.3]
    for i, (sp, t0) in enumerate(zip(spots, t0s)):
        a, s = pop(t, t0, .35)
        if a <= 0:
            continue
        tgt = (spots[2][0], spots[2][1]) if i < 2 else hold
        if i < 2:
            gg = ss(g, 0, .55)
            p = (sp[0] + (tgt[0] - sp[0]) * gg, sp[1] + (tgt[1] - sp[1]) * gg)
            s *= 1 - gg; a *= 1 - ss(gg, .7, 1)
        else:
            gg = ss(g, .35, 1)
            p = (sp[0] + (tgt[0] - sp[0]) * gg, sp[1] - 40 * math.sin(gg * math.pi) + (tgt[1] - sp[1]) * gg)
        if s < .02 or a <= 0:
            continue
        bga = a * (1 - (ss(g, .35, .8) if i == 2 else 0))
        if bga > 0:
            c.paper(('ic', i), xform(ellipse(0, 0, 66, 66, 40), 0, 0, s, 0, *p), PAPER, shadow=1, fringe=1,
                    alpha=bga, screen=True, lift=1.4)
        if i == 0:
            c.arrow('icg', [(p[0], p[1] - 34 * s), (p[0], p[1] + 32 * s)], CHAR, 7 * s, alpha=a, screen=True,
                    head=16 * s)
        elif i == 1:
            hourglass(c, 'ich', p[0], p[1], .9 * s, 0, .55, alpha=a, screen=True)
        else:
            js = 1.0 * s * (1 - gg) + .95 * gg
            jar(c, 'icj', p[0], p[1] + (40 * (1 - gg) + 0 * gg) * js / 1.0 + (0 if gg < 1 else 0), js, .82,
                alpha=a, screen=True, glint=1)


def draw_final_sheet(c, t):
    """a fresh sheet of paper slides up over the farm; the sun rises behind the jar."""
    u = ss(t, r + 9.6, r + 11.0)
    if u <= 0:
        return
    top = 880 - 790 * u
    P = [(60, 1100), (60, top)] + [(x, top + 6 * math.sin(x / 23.0) + 4 * math.sin(x / 7.3)) for x in
                                    range(60, 1871, 30)] + [(1870, 1100)]
    c.paper('sheet_f', P, CREAM, shadow=1, fringe=1, edge=1.8, screen=True, lift=1.5)
    sa = ss(t, r + 10.6, r + 12.0)
    if sa > 0:
        cy = 1000 - 360 * sa
        rr = 150
        for i in range(14):
            a = i / 14 * 2 * math.pi + .1 * math.sin(t * .4)
            r0, r1 = rr + 26, rr + 58 + 10 * (i % 2)
            c.crayon(('ray', i), [(960 + math.cos(a) * r0, cy + math.sin(a) * r0),
                                  (960 + math.cos(a) * r1, cy + math.sin(a) * r1)], MUSTARD, 6,
                     alpha=ss(t, r + 11.4, r + 12.2), screen=True, wax=.5)
        c.paper('fsun', ellipse(960, cy, rr, rr, 60), MUSTARD, shadow=.8, fringe=1, screen=True, lift=1.2)


def draw_captions(c, t):
    cap = None
    for a, b, s in CAPS:
        if a - .08 <= t <= b + .25:
            cap = (a, b, s)
    if not cap:
        return
    a, b, s = cap
    al = ss(t, a - .08, a + .06) * (1 - ss(t, b + .1, b + .25))
    lines = wrap(s)
    y = 951 - (len(lines) - 1) * 22
    for i, ln in enumerate(lines):
        c.text(ln, (960, y + i * 44), 40, fnt='hand', alpha=al, screen=True, rough=False)


# ------------------------------------------------------------- chrome ----
STAGE = (80, 100, 1840, 1032)


def _draw_chrome(c):
    hole = np.zeros((H, W), np.float32); hole[STAGE[1]:STAGE[3], STAGE[0]:STAGE[2]] = 1
    c.comp((0, 0, W, H), 1 - hole, mix(CREAM, CHAR, .10))  # desk
    win = rrect(56, 24, 1864, 1052, 14)
    c.paper('win', win, mix(PAPER, CREAM, .3), shadow=1.2, fringe=.6, edge=.5, outline=.7, screen=True, lift=2.2,
            holes=[rect(*STAGE)])
    c.pencil('titlerule', [(58, 92), (1862, 92)], alpha=.55, screen=True)
    for i, col in enumerate((CORAL, MUSTARD, TEAL)):
        c.paper(('dot', i), ellipse(92 + i * 30, 58, 9, 9, 16), col, shadow=.4, fringe=.5, screen=True, lift=.4)
    c.text('~/fuel-farm  —  jig2-depot.stage', (960, 58), 22, fnt='mono', col=mix(CHAR, CREAM, .35), screen=True,
           rough=False)
    c.text('24 fps', (1820, 58), 18, fnt='mono', col=mix(CHAR, CREAM, .5), screen=True, anchor='rm', rough=False)
    # proscenium: scalloped valance + side curtains
    val = [(80, 100), (1840, 100), (1840, 124)]
    for x in range(1840, 80, -40):
        val += [(x - 20, 138), (x - 40, 124)]
    c.paper('valance', val, MUSTARD, shadow=1, fringe=1, screen=True, lift=1.4)
    for side, (xa, xb) in (('L', (80, 122)), ('R', (1798, 1840))):
        edge_x = xb if side == 'L' else xa
        wav = [(edge_x + 4 * math.sin(y / 30.0), y) for y in range(124, 873, 24)]
        if side == 'L':
            cur = [(xa, 124)] + wav + [(xa, 872)]
        else:
            cur = [(xb, 124)] + wav + [(xb, 872)]
        c.paper(('cur', side), cur, CORAL, shadow=1, fringe=1, screen=True, lift=1.2)
        for j in range(3):
            x = xa + 9 + j * 11
            c.pencil(('cf', side, j), [(x, 140), (x + 2, 860)], alpha=.25, screen=True, col=CORALD)
    # apron
    ap = [(80, 1032), (80, 872)] + [(x, 870 + 2.5 * math.sin(x / 41.0)) for x in range(80, 1841, 40)] + [(1840, 1032)]
    c.paper('apron', ap, TAN, shadow=1.2, fringe=1, edge=1.2, screen=True, lift=1.4)
    c.pencil('apronedge', [(84, 1018), (1836, 1018)], alpha=.25, screen=True)
    c.paper('capstrip', rect(330, 900, 1590, 1004), mix(PAPER, CREAM, .2), shadow=1, fringe=1, edge=1.2, screen=True)


def build_chrome(frame):
    """desk, light terminal window, paper proscenium, cardboard apron.  Rendered over black and
    over white to recover exact coverage (shadows included)."""
    cb = Canvas(frame, base=np.zeros((H, W, 3), np.float32)); _draw_chrome(cb)
    cw = Canvas(frame, base=np.ones((H, W, 3), np.float32)); _draw_chrome(cw)
    al = np.clip(1 - (cw.img - cb.img).mean(2), 0, 1)
    rgb = cb.img  # premultiplied
    return rgb, al


_CHROME = {}


def chrome(frame):
    key = (frame // 3) % 3
    if key not in _CHROME:
        _CHROME[key] = build_chrome(key * 3)
    return _CHROME[key]


SKY_BASE = {}


def render(frame):
    t = frame / FPS
    cx, cy, z = cam(t)
    c = Canvas(frame, cam=(cx, cy, z))
    c.comp((0, 0, W, H), np.ones((H, W), np.float32), CREAM)       # sky paper
    draw_world(c, t)
    na = night(t)
    if na > 0:
        c.img = c.img * (1 - .28 * na) + mix(TEALD, CHAR, .5) * .10 * na
    draw_final_sheet(c, t)
    rgb, al = chrome(frame)
    c.img = c.img * (1 - al[..., None]) + rgb
    draw_captions(c, t)
    bx, bf, pose = draw_bot(c, t)
    draw_question(c, t, bx)
    draw_icons(c, t)
    fade = ss(t, END - .7, END)
    if fade > 0:
        c.img = c.img * (1 - fade) + CREAM * fade
    return (np.clip(c.img, 0, 1) * 255 + .5).astype(np.uint8)
