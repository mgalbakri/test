"""Paper-stage rendering engine: gouache fills, torn fringes, cardboard shadows,
crayon/pencil lines and a 'boil' that re-seeds every 3 frames (8 drawings/sec)."""
import math, zlib, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1920, 1080, 24
HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(HERE, '..', 'assets', 'fonts')


def hexc(h):
    return np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)], np.float32) / 255


def mix(a, b, k):
    return a * (1 - k) + b * k


CORAL = hexc('#E4705A'); MUSTARD = hexc('#E3A83A'); TEAL = hexc('#2F8C88')
CREAM = hexc('#F3E8CF'); CHAR = hexc('#2D2A28')
PAPER = mix(CREAM, np.ones(3, np.float32), .5)
FUEL = mix(MUSTARD, CREAM, .52)
TEALD = mix(TEAL, CHAR, .35)
TAN = mix(mix(MUSTARD, CHAR, .30), CREAM, .30)
CORALD = mix(CORAL, CHAR, .22)
SHADOW = mix(CHAR, MUSTARD, .12)
BLACK = hexc('#141212')

# ---------------------------------------------------------------- noise ----
_T = np.random.RandomState(11).rand(16384).astype(np.float32)


def vnoise(x):
    x = np.asarray(x, np.float64)
    i = np.floor(x).astype(np.int64); f = x - i
    f = f * f * (3 - 2 * f)
    a = _T[i % 16384]; b = _T[(i + 1) % 16384]
    return (a + (b - a) * f) * 2 - 1


def fbm(x):
    return vnoise(x) + .5 * vnoise(x * 2.13 + 31.7) + .25 * vnoise(x * 4.37 + 77.1)


def hkey(key):
    return zlib.crc32(str(key).encode()) % 100000


def rnd(*k):
    return (zlib.crc32(repr(k).encode()) % 100000) / 100000.0


# ------------------------------------------------------------- textures ----
PAD = 64
TH, TW = H + PAD, W + PAD


def _lowfreq(cells, seed):
    r = np.random.RandomState(seed).rand(*cells).astype(np.float32)
    im = Image.fromarray((r * 255).astype(np.uint8)).resize((TW, TH), Image.BICUBIC)
    return np.asarray(im, np.float32) / 127.5 - 1


def _textures():
    rs = np.random.RandomState(5)
    g = rs.randn(TH, TW).astype(np.float32)
    gi = Image.fromarray(np.clip(g * 40 + 128, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.8))
    grain = np.asarray(gi, np.float32) / 127.5 - 1
    grain = grain / (np.abs(grain).max() + 1e-6)
    blotch = _lowfreq((18, 32), 1) * .6 + _lowfreq((54, 96), 2) * .4
    streak = _lowfreq((300, 24), 3)          # horizontal dry-brush streaks
    fib = _lowfreq((540, 60), 4) * _lowfreq((30, 960), 6)  # paper fibres
    mod = 1 + .075 * blotch + .07 * grain + .035 * streak + .02 * fib
    wax = np.clip(.62 + .55 * grain + .5 * streak, 0, 1)
    return mod.astype(np.float32), wax.astype(np.float32)


MOD, WAX = _textures()

_FONTS = {}


def font(name, size, weight=None):
    k = (name, size, weight)
    if k not in _FONTS:
        path = {'cav': 'Caveat.ttf', 'hand': 'PatrickHand.ttf'}.get(name)
        if path:
            f = ImageFont.truetype(os.path.join(FONT_DIR, path), size)
            if weight and name == 'cav':
                try:
                    f.set_variation_by_axes([weight])
                except Exception:
                    pass
        else:
            f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf', size)
        _FONTS[k] = f
    return _FONTS[k]


# ------------------------------------------------------------- geometry ----
def rect(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def ellipse(cx, cy, rx, ry, n=48, a0=0, a1=2 * math.pi):
    return [(cx + rx * math.cos(a0 + (a1 - a0) * i / n), cy + ry * math.sin(a0 + (a1 - a0) * i / n))
            for i in range(n + (0 if a1 - a0 >= 2 * math.pi - 1e-6 else 1))]


def rrect(x0, y0, x1, y1, r, n=8):
    pts = []
    for cx, cy, a in ((x1 - r, y0 + r, -math.pi / 2), (x1 - r, y1 - r, 0), (x0 + r, y1 - r, math.pi / 2),
                      (x0 + r, y0 + r, math.pi)):
        for i in range(n + 1):
            t = a + (math.pi / 2) * i / n
            pts.append((cx + r * math.cos(t), cy + r * math.sin(t)))
    return pts


def xform(pts, cx=0, cy=0, s=1.0, ang=0.0, dx=0, dy=0, sx=None, sy=None):
    """rotate/scale about (cx,cy) then translate."""
    sx = s if sx is None else sx; sy = s if sy is None else sy
    c, si = math.cos(ang), math.sin(ang)
    out = []
    for x, y in pts:
        u, v = (x - cx) * sx, (y - cy) * sy
        out.append((cx + u * c - v * si + dx, cy + u * si + v * c + dy))
    return out


def lerp_pts(a, b, k):
    return [(x0 + (x1 - x0) * k, y0 + (y1 - y0) * k) for (x0, y0), (x1, y1) in zip(a, b)]


def resample(P, closed, step):
    P = np.asarray(P, np.float64)
    if closed:
        P = np.vstack([P, P[:1]])
    d = np.sqrt(((P[1:] - P[:-1]) ** 2).sum(1))
    s = np.concatenate([[0], np.cumsum(d)])
    L = s[-1]
    if L < 1e-6:
        return P[:1].repeat(2, 0), np.zeros(2)
    n = max(int(L / step), 8 if closed else 2)
    t = np.linspace(0, L, n, endpoint=not closed)
    x = np.interp(t, s, P[:, 0]); y = np.interp(t, s, P[:, 1])
    return np.stack([x, y], 1), t


def normals(Q, closed):
    if closed:
        tg = np.roll(Q, -1, 0) - np.roll(Q, 1, 0)
    else:
        tg = np.gradient(Q, axis=0)
    n = np.stack([tg[:, 1], -tg[:, 0]], 1)
    n /= (np.linalg.norm(n, axis=1, keepdims=True) + 1e-9)
    return n


def polyline_at(P, u):
    """point & tangent at fraction u along polyline P."""
    P = np.asarray(P, np.float64)
    d = np.sqrt(((P[1:] - P[:-1]) ** 2).sum(1)); s = np.concatenate([[0], np.cumsum(d)])
    t = np.clip(u, 0, 1) * s[-1]
    i = min(np.searchsorted(s, t, 'right') - 1, len(P) - 2)
    f = (t - s[i]) / max(d[i], 1e-9)
    p = P[i] + (P[i + 1] - P[i]) * f
    return (float(p[0]), float(p[1])), (P[i + 1] - P[i]) / max(d[i], 1e-9)


def sub_polyline(P, u0, u1, n=40):
    return [polyline_at(P, u0 + (u1 - u0) * i / n)[0] for i in range(n + 1)]


def bezier(p0, p1, p2, p3, n=40):
    out = []
    for i in range(n + 1):
        t = i / n; a = (1 - t) ** 3; b = 3 * (1 - t) ** 2 * t; c = 3 * (1 - t) * t * t; d = t ** 3
        out.append((a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0], a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1]))
    return out


# ---------------------------------------------------------------- canvas ----
class Canvas:
    def __init__(self, frame, base=None, cam=(960, 488, 1.0), track_alpha=False):
        self.f = frame
        self.bseed = frame // 3                        # boil on threes
        self.img = base.copy() if base is not None else np.zeros((H, W, 3), np.float32)
        self.alpha = np.zeros((H, W), np.float32) if track_alpha else None
        self.ox = int(rnd('tx', self.bseed % 3) * (PAD - 1)); self.oy = int(rnd('ty', self.bseed % 3) * (PAD - 1))
        self.set_cam(*cam)

    def set_cam(self, cx, cy, z):
        self.cx, self.cy, self.z = cx, cy, z

    def tf(self, P):
        P = np.asarray(P, np.float64)
        return np.stack([(P[:, 0] - self.cx) * self.z + 960, (P[:, 1] - self.cy) * self.z + 488], 1)

    def tp(self, p):
        return ((p[0] - self.cx) * self.z + 960, (p[1] - self.cy) * self.z + 488)

    # ---- low level
    def _box(self, pts_list, pad):
        allp = np.vstack(pts_list)
        x0 = int(math.floor(allp[:, 0].min() - pad)); y0 = int(math.floor(allp[:, 1].min() - pad))
        x1 = int(math.ceil(allp[:, 0].max() + pad)); y1 = int(math.ceil(allp[:, 1].max() + pad))
        x0, y0 = max(x0, 0), max(y0, 0); x1, y1 = min(x1, W), min(y1, H)
        if x1 - x0 < 1 or y1 - y0 < 1:
            return None
        return x0, y0, x1, y1

    @staticmethod
    def _raster(polys, box, ss=2):
        x0, y0, x1, y1 = box
        im = Image.new('L', ((x1 - x0) * ss, (y1 - y0) * ss), 0); d = ImageDraw.Draw(im)
        for p in polys:
            q = [((x - x0) * ss, (y - y0) * ss) for x, y in p]
            if len(q) >= 3:
                d.polygon(q, fill=255)
        return np.asarray(im.resize((x1 - x0, y1 - y0), Image.BOX), np.float32) / 255

    @staticmethod
    def _raster_lines(lines, box, width, ss=2):
        x0, y0, x1, y1 = box
        im = Image.new('L', ((x1 - x0) * ss, (y1 - y0) * ss), 0); d = ImageDraw.Draw(im)
        wpx = max(1, int(round(width * ss)))
        for p in lines:
            q = [((x - x0) * ss, (y - y0) * ss) for x, y in p]
            if len(q) >= 2:
                d.line(q, fill=255, width=wpx, joint='curve')
                r = wpx / 2
                for (x, y) in (q[0], q[-1]):
                    d.ellipse([x - r, y - r, x + r, y + r], fill=255)
        return np.asarray(im.resize((x1 - x0, y1 - y0), Image.BOX), np.float32) / 255

    def comp(self, box, a, col, textured=True):
        x0, y0, x1, y1 = box
        sl = self.img[y0:y1, x0:x1]
        if textured:
            m = MOD[y0 + self.oy:y1 + self.oy, x0 + self.ox:x1 + self.ox][..., None]
            c = np.clip(np.asarray(col, np.float32) * m, 0, 1)
        else:
            c = np.asarray(col, np.float32)
        a3 = a[..., None]
        self.img[y0:y1, x0:x1] = sl * (1 - a3) + c * a3
        if self.alpha is not None:
            al = self.alpha[y0:y1, x0:x1]
            self.alpha[y0:y1, x0:x1] = al + a * (1 - al)

    def wax(self, box):
        x0, y0, x1, y1 = box
        return WAX[y0 + self.oy:y1 + self.oy, x0 + self.ox:x1 + self.ox]

    def _blur_shadow(self, m, rad):
        h, w = m.shape
        k = 4
        im = Image.fromarray((m * 255).astype(np.uint8))
        sm = im.resize((max(1, w // k), max(1, h // k)), Image.BILINEAR).filter(ImageFilter.GaussianBlur(rad / k))
        return np.asarray(sm.resize((w, h), Image.BILINEAR), np.float32) / 255

    # ---- paper cut-out
    def paper(self, key, pts, col, shadow=1.0, fringe=1.0, edge=1.0, outline=0.0, alpha=1.0, screen=False,
              lift=1.0, holes=None):
        if alpha <= 0.003:
            return
        h = hkey(key)
        S = np.asarray(pts, np.float64) if screen else self.tf(pts)
        z = 1.0 if screen else self.z
        Q, s = resample(S, True, 5.0)
        x, y = Q[:, 0], Q[:, 1]
        area = 0.5 * np.sum(x * np.roll(y, -1) - np.roll(x, -1) * y)
        N = normals(Q, True) * (-1 if area < 0 else 1)
        sw = s / max(z, 1e-6)
        tear = fbm(sw * 0.11 + h % 997) * 1.3 * edge + fbm(sw * 0.035 + self.bseed * 5.3 + h % 331) * 0.8
        b = np.array([(rnd(h, self.bseed, 'x') - .5) * 2.4, (rnd(h, self.bseed, 'y') - .5) * 2.4])
        F = Q + N * tear[:, None] + b
        polys = [F]
        G = None
        if fringe > 0:
            G = Q + N * (1.6 + np.abs(fbm(sw * 0.23 + h % 557)) * 3.0 * fringe)[:, None] + b
        outer = G if G is not None else F
        off = np.array([5.0, 7.0]) * lift
        box = self._box([outer, outer + off], 14 + 6 * lift)
        if box is None:
            return
        hp = []
        if holes:
            for hpts in holes:
                hs = np.asarray(hpts, np.float64) if screen else self.tf(hpts)
                hp.append(hs + b)
        if shadow > 0:
            ms = self._raster([outer + off], box, 1)
            ms = self._blur_shadow(ms, 9 * lift)
            if hp:
                ms = ms * (1 - self._raster(hp, box))
            self.comp(box, ms * .24 * shadow * alpha, SHADOW, textured=False)
        if G is not None:
            mg = self._raster([G], box)
            if hp:
                mg = mg * (1 - self._raster(hp, box))
            self.comp(box, mg * alpha * .96, PAPER)
        mf = self._raster(polys, box)
        if hp:
            mf = mf * (1 - self._raster(hp, box))
        self.comp(box, mf * alpha, col)
        if outline > 0:
            self.crayon(('ol', key), F, CHAR, 1.6, alpha=outline * alpha, screen=True, closed=True, wax=.55,
                        jit=.5)

    def blob(self, key, pts, col, alpha=1.0, screen=False, shadow=0.0):
        """flat gouache shape, slight boil, no fringe (for fills inside other pieces)."""
        self.paper(key, pts, col, shadow=shadow, fringe=0, edge=.5, alpha=alpha, screen=screen, lift=.5)

    # ---- crayon / pencil
    def crayon(self, key, pts, col, w, alpha=1.0, screen=False, closed=False, dash=None, wax=0.6, jit=0.9,
               wscale=True):
        if alpha <= 0.003 or len(pts) < 2:
            return
        h = hkey(key)
        S = np.asarray(pts, np.float64) if screen else self.tf(pts)
        z = 1.0 if screen else self.z
        width = w * z if (wscale and not screen) else w
        Q, s = resample(S, closed, 3.0)
        if closed:
            Q = np.vstack([Q, Q[:1]]); s = np.append(s, s[-1] + 3)
        N = normals(Q, False)
        Q = Q + N * (fbm(s * 0.045 + self.bseed * 3.7 + h % 401) * jit)[:, None]
        Q = Q + np.array([(rnd(h, self.bseed, 'cx') - .5) * 1.6, (rnd(h, self.bseed, 'cy') - .5) * 1.6])
        segs = []
        if dash:
            on, off, ph = dash
            period = on + off
            cur = []
            for p, ss in zip(Q, s):
                if ((ss + ph) % period) < on:
                    cur.append(tuple(p))
                elif cur:
                    segs.append(cur); cur = []
            if cur:
                segs.append(cur)
            segs = [g for g in segs if len(g) >= 2]
        else:
            segs = [[tuple(p) for p in Q]]
        if not segs:
            return
        box = self._box([np.asarray(g) for g in segs], width + 6)
        if box is None:
            return
        m = self._raster_lines(segs, box, width)
        m = m * ((1 - wax) + wax * self.wax(box))
        self.comp(box, np.clip(m, 0, 1) * alpha, col)

    def pencil(self, key, pts, alpha=0.8, w=2.2, screen=False, closed=False, dash=None, col=None):
        self.crayon(key, pts, CHAR if col is None else col, w, alpha=alpha * .85, screen=screen, closed=closed,
                    dash=dash, wax=.7, jit=.7, wscale=False)

    def arrow(self, key, pts, col, w, alpha=1.0, screen=False, head=None):
        self.crayon(key, pts, col, w, alpha=alpha, screen=screen)
        S = np.asarray(pts, np.float64)
        p = S[-1]; d = S[-1] - S[-2]; d = d / (np.linalg.norm(d) + 1e-9)
        n = np.array([-d[1], d[0]])
        hl = head if head is not None else w * 3.2
        a = p - d * hl + n * hl * .7; b = p - d * hl - n * hl * .7
        self.crayon((key, 'h'), [tuple(a), tuple(p), tuple(b)], col, w, alpha=alpha, screen=screen)

    # ---- text
    def text(self, s, pos, size, col=None, fnt='cav', alpha=1.0, screen=False, angle=0.0, anchor='mm',
             weight=None, rough=True):
        if alpha <= 0.003:
            return
        col = CHAR if col is None else col
        p = pos if screen else self.tp(pos)
        sz = size if screen else size * self.z
        if sz < 7:
            return
        f = font(fnt, int(round(sz)), weight)
        l, t, r, b = f.getbbox(s, anchor='lt')
        asc, desc = f.getmetrics()
        pad = int(sz * .35) + 4
        tw, th = r - l + 2 * pad, max(b - t, asc + desc) + 2 * pad
        im = Image.new('L', (tw, th), 0)
        ImageDraw.Draw(im).text((pad - l, pad - t), s, font=f, fill=255)
        bb = im.getbbox()
        if bb is None:
            return
        im = im.crop((bb[0] - 2, pad - 2, bb[2] + 2, pad + (b - t) + 2 + max(0, bb[3] - pad - (b - t))))
        if angle:
            im = im.rotate(angle, resample=Image.BICUBIC, expand=True)
        m = np.asarray(im, np.float32) / 255
        hh, ww = m.shape
        jx = (rnd(s, self.bseed, 'tx') - .5) * 1.4; jy = (rnd(s, self.bseed, 'ty') - .5) * 1.4
        ax = {'l': 0, 'm': .5, 'r': 1}[anchor[0]]; ay = {'t': 0, 'm': .5, 'b': 1}[anchor[1]]
        x0 = int(round(p[0] - ww * ax + jx)); y0 = int(round(p[1] - hh * ay + jy))
        bx0, by0, bx1, by1 = max(x0, 0), max(y0, 0), min(x0 + ww, W), min(y0 + hh, H)
        if bx1 <= bx0 or by1 <= by0:
            return
        m = m[by0 - y0:by1 - y0, bx0 - x0:bx1 - x0]
        box = (bx0, by0, bx1, by1)
        if rough:
            m = m * (.8 + .2 * self.wax(box))
        self.comp(box, m * alpha, col)

    def text_size(self, s, size, fnt='cav', weight=None):
        f = font(fnt, int(round(size)), weight)
        l, t, r, b = f.getbbox(s, anchor='lt')
        return r - l, b - t
