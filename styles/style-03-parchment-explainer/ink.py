"""Toolkit ilustrasi tinta + cat air di atas perkamen (semua digambar oleh kode).

Koordinat gambar selalu "logis" (kanvas 1240 x 2204). Canvas(k=...) menggambar di resolusi
fisik k kali lebih besar supaya close-up (zoom kamera) tetap tajam.
"""
import math
import random
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

FONTS = Path(__file__).resolve().parents[2] / "assets" / "fonts"
CARDO = str(FONTS / "Cardo-Regular.ttf")
CARDO_B = str(FONTS / "Cardo-Bold.ttf")
CARDO_I = str(FONTS / "Cardo-Italic.ttf")
CRIMSON = str(FONTS / "CrimsonText-SemiBold.ttf")
CRIMSON_I = str(FONTS / "CrimsonText-SemiBoldItalic.ttf")
INK_RGB = np.array([40, 28, 21], np.float32) / 255.0

_fc = {}


def font(path, size):
    k = (path, size)
    if k not in _fc:
        _fc[k] = ImageFont.truetype(path, size)
    return _fc[k]


def C(*rgb):
    return np.array(rgb, np.float32) / 255.0


# ---------------------------------------------------------------- noise & paper
def smooth_noise(w, h, scale, rng):
    sw, sh = max(2, w // scale + 2), max(2, h // scale + 2)
    a = rng.random((sh, sw)).astype(np.float32)
    im = Image.fromarray((a * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC)
    return np.asarray(im, np.float32) / 255.0


def make_paper(w, h, seed=1, tone=(234, 214, 170)):
    rng = np.random.default_rng(seed)
    base = np.array(tone, np.float32) / 255.0
    n1 = smooth_noise(w, h, 320, rng)
    n2 = smooth_noise(w, h, 70, rng)
    n3 = smooth_noise(w, h, 9, rng)
    grain = rng.random((h, w)).astype(np.float32)
    lum = 1 + 0.07 * (n1 - 0.5) + 0.05 * (n2 - 0.5) + 0.035 * (n3 - 0.5) + 0.025 * (grain - 0.5)
    img = base[None, None, :] * lum[..., None]
    # stains
    st = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(st)
    r = random.Random(seed)
    for _ in range(9):
        cx, cy = r.uniform(0, w), r.uniform(0, h)
        rr = r.uniform(60, 260)
        d.ellipse((cx - rr, cy - rr * r.uniform(0.6, 1.2), cx + rr, cy + rr * r.uniform(0.6, 1.2)), fill=r.randint(20, 55))
    st = np.asarray(st.filter(ImageFilter.GaussianBlur(70)), np.float32) / 255.0
    stain_col = np.array([0.78, 0.62, 0.40], np.float32)
    img = img * (1 - st[..., None] * (1 - stain_col))
    # fibers
    fb = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(fb)
    for _ in range(900):
        x, y = r.uniform(0, w), r.uniform(0, h)
        a = r.uniform(0, math.pi)
        L = r.uniform(6, 22)
        d.line((x, y, x + L * math.cos(a), y + L * math.sin(a)), fill=r.randint(20, 60), width=1)
    fb = np.asarray(fb.filter(ImageFilter.GaussianBlur(0.6)), np.float32) / 255.0
    img = img * (1 - 0.18 * fb[..., None])
    # edge burn
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    dx = np.minimum(xx, w - 1 - xx) / w
    dy = np.minimum(yy, h - 1 - yy) / h
    e = np.clip(1 - np.minimum(dx * 7.5, dy * 13.5), 0, 1) ** 2.2
    e = e * (0.75 + 0.5 * n2)
    burn = np.array([0.55, 0.40, 0.24], np.float32)
    img = img * (1 - e[..., None] * (1 - burn) * 0.85)
    return np.clip(img, 0, 1)


# ---------------------------------------------------------------- shapes
def ellipse(cx, cy, rx, ry, n=40, a0=0.0, a1=2 * math.pi):
    return [(cx + rx * math.cos(a0 + (a1 - a0) * k / n), cy + ry * math.sin(a0 + (a1 - a0) * k / n)) for k in range(n)]


def rect(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def rrect(x0, y0, x1, y1, r, n=5):
    pts = []
    for cx, cy, a0 in ((x1 - r, y0 + r, -90), (x1 - r, y1 - r, 0), (x0 + r, y1 - r, 90), (x0 + r, y0 + r, 180)):
        for k in range(n + 1):
            a = math.radians(a0 + 90 * k / n)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def capsule(p0, p1, r0, r1=None, n=8):
    r1 = r0 if r1 is None else r1
    (x0, y0), (x1, y1) = p0, p1
    a = math.atan2(y1 - y0, x1 - x0)
    pts = []
    for k in range(n + 1):
        t = a + math.pi / 2 + math.pi * k / n
        pts.append((x0 + r0 * math.cos(t), y0 + r0 * math.sin(t)))
    for k in range(n + 1):
        t = a - math.pi / 2 + math.pi * k / n
        pts.append((x1 + r1 * math.cos(t), y1 + r1 * math.sin(t)))
    return pts


def move(pts, dx, dy):
    return [(x + dx, y + dy) for x, y in pts]


def rot(pts, ang, cx, cy):
    c, s = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    return [(cx + (x - cx) * c - (y - cy) * s, cy + (x - cx) * s + (y - cy) * c) for x, y in pts]


class Iso:
    """Proyeksi isometrik sederhana untuk diorama potongan."""

    def __init__(self, ox, oy, s=1.0):
        self.ox, self.oy, self.s = ox, oy, s

    def p(self, x, y, z):
        s = self.s
        return (self.ox + (x - z) * 0.866 * s, self.oy + (x + z) * 0.5 * s - y * s)


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, seed=0, k=1.0):
        self.k = k
        self.lw, self.lh = w, h
        w, h = int(round(w * k)), int(round(h * k))
        self.w, self.h = w, h
        self.art = np.ones((h, w, 3), np.float32)
        self.ink = np.zeros((h, w), np.float32)
        self.rng = random.Random(seed)
        nr = np.random.default_rng(seed + 100)
        self.nfine = smooth_noise(w, h, 5, nr)
        self.nmid = smooth_noise(w, h, int(28 * k), nr)
        self.ncoarse = smooth_noise(w, h, int(110 * k), nr)

    def T(self, pts):
        k = self.k
        return [(x * k, y * k) for x, y in pts]

    # -- masks
    def _bbox(self, pts, pad):
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        x0 = max(0, int(min(xs) - pad))
        y0 = max(0, int(min(ys) - pad))
        x1 = min(self.w, int(max(xs) + pad + 1))
        y1 = min(self.h, int(max(ys) + pad + 1))
        return x0, y0, x1, y1

    def mask(self, polys, pad=14, blur=0.0):
        if polys and isinstance(polys[0], tuple):
            polys = [polys]
        polys = [self.T(poly) for poly in polys]
        pad, blur = pad * self.k, blur * self.k
        allp = [p for poly in polys for p in poly]
        x0, y0, x1, y1 = self._bbox(allp, pad)
        if x1 <= x0 or y1 <= y0:
            return None
        im = Image.new("L", (x1 - x0, y1 - y0), 0)
        d = ImageDraw.Draw(im)
        for poly in polys:
            d.polygon([(x - x0, y - y0) for x, y in poly], fill=255)
        if blur:
            im = im.filter(ImageFilter.GaussianBlur(blur))
        return (x0, y0, x1, y1), np.asarray(im, np.float32) / 255.0

    # -- paint ops
    def clear(self, m, strength=1.0):
        if m is None:
            return
        (x0, y0, x1, y1), a = m
        a = a * strength
        self.art[y0:y1, x0:x1] = self.art[y0:y1, x0:x1] * (1 - a[..., None]) + a[..., None]
        self.ink[y0:y1, x0:x1] *= (1 - a)

    def wash(self, m, color, opacity=0.85, gran=0.3, edge=0.45, var=0.25, shade=None):
        if m is None:
            return
        (x0, y0, x1, y1), a = m
        col = np.asarray(color, np.float32)
        nf = self.nfine[y0:y1, x0:x1]
        nm = self.nmid[y0:y1, x0:x1]
        nc = self.ncoarse[y0:y1, x0:x1]
        soft = np.asarray(Image.fromarray((a * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(5 * self.k)), np.float32) / 255
        e = np.clip(a - soft, 0, 1) * 2.2
        al = opacity * a * (1 - gran * nf) * (1 + var * (nm - 0.5) + 0.2 * (nc - 0.5)) + edge * e
        if shade is not None:  # vertical gradient darkening (0..1 top->bottom)
            gy = np.linspace(0, 1, y1 - y0, dtype=np.float32)[:, None]
            al = al * (1 + shade * (gy - 0.4))
        al = np.clip(al, 0, 1)[..., None]
        self.art[y0:y1, x0:x1] *= (1 - al + al * col)

    def line(self, pts, width=3.0, alpha=1.0, wobble=1.1, closed=False, taper=True, step=6):
        if len(pts) < 2:
            return
        k = self.k
        pts = self.T(pts)
        width, wobble, step = width * k, wobble * k, step * k
        P = list(pts) + ([pts[0]] if closed else [])
        # resample
        res = [P[0]]
        for (xa, ya), (xb, yb) in zip(P[:-1], P[1:]):
            L = math.hypot(xb - xa, yb - ya)
            n = max(1, int(L / step))
            for k in range(1, n + 1):
                res.append((xa + (xb - xa) * k / n, ya + (yb - ya) * k / n))
        r = self.rng
        ph1, ph2 = r.uniform(0, 6.28), r.uniform(0, 6.28)
        out = []
        N = len(res)
        for i, (x, y) in enumerate(res):
            j, k = min(i + 1, N - 1), max(i - 1, 0)
            dx, dy = res[j][0] - res[k][0], res[j][1] - res[k][1]
            L = math.hypot(dx, dy) or 1
            nx, ny = -dy / L, dx / L
            o = wobble * (0.7 * math.sin(i * 0.37 + ph1) + 0.5 * math.sin(i * 0.11 + ph2))
            out.append((x + nx * o, y + ny * o))
        x0, y0, x1, y1 = self._bbox(out, width + 4)
        if x1 <= x0 or y1 <= y0:
            return
        im = Image.new("L", (x1 - x0, y1 - y0), 0)
        d = ImageDraw.Draw(im)
        for i in range(len(out) - 1):
            t = i / max(1, len(out) - 2)
            pr = (0.55 + 0.45 * math.sin(math.pi * t)) if (taper and not closed) else 1.0
            pr *= 0.85 + 0.3 * (0.5 + 0.5 * math.sin(i * 0.5 + ph1))
            wd = max(1, int(round(width * pr)))
            (xa, ya), (xb, yb) = out[i], out[i + 1]
            d.line((xa - x0, ya - y0, xb - x0, yb - y0), fill=int(255 * alpha), width=wd)
            if wd >= 3:
                rr = wd / 2
                d.ellipse((xb - x0 - rr, yb - y0 - rr, xb - x0 + rr, yb - y0 + rr), fill=int(255 * alpha))
        a = np.asarray(im, np.float32) / 255.0
        self.ink[y0:y1, x0:x1] = np.maximum(self.ink[y0:y1, x0:x1], a)

    def outline(self, poly, width=3.0, alpha=1.0, wobble=1.1):
        self.line(poly, width=width, alpha=alpha, wobble=wobble, closed=True, taper=False)

    def hatch(self, m, spacing=8, angle=40, width=1, alpha=0.5, jitter=1.5):
        if m is None:
            return
        (x0, y0, x1, y1), a = m
        spacing, jitter = spacing * self.k, jitter * self.k
        width = max(1, int(round(width * self.k)))
        w, h = x1 - x0, y1 - y0
        im = Image.new("L", (w, h), 0)
        d = ImageDraw.Draw(im)
        ang = math.radians(angle)
        diag = int(math.hypot(w, h)) + 2
        r = self.rng
        k = -diag
        while k < diag:
            cx, cy = w / 2 + k * math.cos(ang + math.pi / 2), h / 2 + k * math.sin(ang + math.pi / 2)
            dx, dy = math.cos(ang) * diag, math.sin(ang) * diag
            d.line((cx - dx, cy - dy + r.uniform(-jitter, jitter), cx + dx, cy + dy + r.uniform(-jitter, jitter)),
                   fill=int(255 * alpha), width=width)
            k += spacing + r.uniform(-1, 1)
        hm = np.asarray(im, np.float32) / 255.0 * (a > 0.5)
        self.ink[y0:y1, x0:x1] = np.maximum(self.ink[y0:y1, x0:x1], hm)

    def text(self, xy, s, size=40, path=CARDO_B, angle=0, alpha=0.95, anchor="mm"):
        xy = (xy[0] * self.k, xy[1] * self.k)
        f = font(path, int(round(size * self.k)))
        bb = f.getbbox(s, anchor=anchor)
        pad = 10
        w, h = bb[2] - bb[0] + 2 * pad, bb[3] - bb[1] + 2 * pad
        im = Image.new("L", (w, h), 0)
        ImageDraw.Draw(im).text((pad - bb[0], pad - bb[1]), s, font=f, fill=int(255 * alpha), anchor=anchor)
        if angle:
            im = im.rotate(angle, expand=True, resample=Image.BICUBIC)
        x, y = int(xy[0] - im.width / 2), int(xy[1] - im.height / 2)
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + im.width), min(self.h, y + im.height)
        a = np.asarray(im, np.float32)[y0 - y:y1 - y, x0 - x:x1 - x] / 255.0
        self.ink[y0:y1, x0:x1] = np.maximum(self.ink[y0:y1, x0:x1], a)

    # -- composite object
    def shape(self, poly, color, opacity=0.85, outline=3.0, hatch=None, gran=0.3, shade=0.35, ink_alpha=1.0,
              offset=2.5, clear=True, edge=0.45):
        m = self.mask(poly)
        if clear:
            self.clear(m)
        r = self.rng
        if color is not None:
            mo = self.mask(move(poly, r.uniform(-offset, offset), r.uniform(-offset, offset)), blur=0.8)
            self.wash(mo, color, opacity=opacity, gran=gran, shade=shade, edge=edge)
        if hatch:
            self.hatch(m, **hatch)
        if outline:
            self.outline(poly, width=outline, alpha=ink_alpha)
        return m

    def render(self, paper, ink_blur=0.8, etch=0.32, grade=(1.0, 0.965, 0.9)):
        """Gabungkan kertas + cat + tinta. Kembalikan (gambar_jadi, gambar_tinta_saja) sebagai uint8 HxWx3."""
        k = self.k
        ink = np.asarray(Image.fromarray((self.ink * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(ink_blur * k)),
                         np.float32) / 255.0
        # arsiran "etsa" otomatis di bagian cat yang gelap (kesan ilustrasi buku cetak)
        lum = self.art.mean(axis=2)
        shade = np.clip((0.8 - lum) / 0.45, 0, 1)
        yy, xx = np.mgrid[0:self.h, 0:self.w].astype(np.float32)
        sp = 6.0 * k
        warp = (self.nmid - 0.5) * 6 * k
        h1 = np.clip(1.2 - np.abs(((xx + yy + warp) % sp) - sp / 2) / (0.55 * k), 0, 1)
        h2 = np.clip(1.2 - np.abs(((xx - yy + warp) % sp) - sp / 2) / (0.55 * k), 0, 1)
        e = etch * (h1 * np.clip(shade * 1.6, 0, 1) + h2 * np.clip(shade * 1.6 - 0.8, 0, 1))
        e *= (0.6 + 0.8 * self.nfine)
        ink = np.maximum(ink, np.clip(e, 0, 1))
        g = np.asarray(grade, np.float32)[None, None, :]
        out = paper * self.art * g
        inkc = INK_RGB[None, None, :] * (0.75 + 0.25 * paper)
        a = (ink * 0.94)[..., None]
        full = out * (1 - a) + inkc * a
        lines = paper * g * (1 - a) + inkc * a
        to8 = lambda x: (np.clip(x, 0, 1) * 255).astype(np.uint8)
        return to8(full), to8(lines)


# ---------------------------------------------------------------- building blocks
def iso_box(c, iso, x, y, z, w, h, d, color, outline=2.6, top=None, hatch_side=False, opacity=0.85):
    """Kotak isometrik: x,z di lantai, y ke atas. Menggambar sisi atas, kiri(depan-kiri), kanan."""
    P = iso.p
    top_poly = [P(x, y + h, z), P(x + w, y + h, z), P(x + w, y + h, z + d), P(x, y + h, z + d)]
    left = [P(x, y, z + d), P(x + w, y, z + d), P(x + w, y + h, z + d), P(x, y + h, z + d)]
    right = [P(x + w, y, z), P(x + w, y, z + d), P(x + w, y + h, z + d), P(x + w, y + h, z)]
    col = np.asarray(color, np.float32)
    c.shape(left, col * 0.86, opacity=opacity, outline=outline, shade=0.3)
    c.shape(right, col * 0.7, opacity=opacity, outline=outline, shade=0.3,
            hatch=dict(spacing=9, angle=-30, alpha=0.35) if hatch_side else None)
    c.shape(top_poly, top if top is not None else col, opacity=opacity, outline=outline, shade=0.1)
    return top_poly, left, right


def person(c, x, y, s=1.0, shirt=C(170, 70, 50), pants=C(70, 80, 100), hair="bowl", pose="stand",
           arms=("down", "down"), face=C(246, 232, 210), hair_col=C(30, 24, 22), skirt=False, look=0,
           hold=None, mouth="smile", shadow=True):
    """Karakter kepala bulat gaya buku cerita. (x, y) = titik di antara kaki (lantai)."""
    r = c.rng
    hr = 48 * s                     # head radius
    body_h = 108 * s
    leg_h = 52 * s
    if pose == "sit":
        leg_h = 26 * s
    if pose == "kneel":
        leg_h = 20 * s
    hip_y = y - leg_h
    sh_y = hip_y - body_h
    head_cy = sh_y - hr * 0.86
    if shadow:
        c.wash(c.mask(ellipse(x + 6 * s, y - 4 * s, 70 * s, 16 * s, n=24), blur=6 * s), C(90, 60, 40), opacity=0.35,
               gran=0.2, edge=0)
    # legs
    if pose == "stand":
        for dx in (-17 * s, 17 * s):
            c.shape(rect(x + dx - 13 * s, hip_y - 6 * s, x + dx + 13 * s, y - 8 * s), pants, outline=2.2 * s + 0.6)
            c.shape(ellipse(x + dx + 4 * s, y - 6 * s, 17 * s, 9 * s), C(60, 44, 36), outline=2.0 * s + 0.6)
    elif pose == "walk":
        for dx, a in ((-12 * s, -14), (12 * s, 14)):
            poly = rot(rect(x + dx - 13 * s, hip_y - 6 * s, x + dx + 13 * s, y - 8 * s), a, x + dx, hip_y)
            c.shape(poly, pants, outline=2.2 * s + 0.6)
    elif pose == "sit":
        for dx in (-17 * s, 17 * s):
            c.shape(rect(x + dx - 14 * s, hip_y - 4 * s, x + dx + 14 * s + 26 * s, hip_y + 22 * s), pants, outline=2.2 * s + 0.6)
    elif pose == "kneel":
        c.shape(ellipse(x, hip_y + 6 * s, 58 * s, 20 * s), pants, outline=2.2 * s + 0.6)
    # body
    bw0, bw1 = 34 * s, 50 * s
    body = [(x - bw0, sh_y + 6 * s), (x + bw0, sh_y + 6 * s), (x + bw1, hip_y + 4 * s), (x - bw1, hip_y + 4 * s)]
    if skirt:
        body = [(x - bw0, sh_y + 6 * s), (x + bw0, sh_y + 6 * s), (x + bw1 + 14 * s, y - 10 * s), (x - bw1 - 14 * s, y - 10 * s)]
    body = rrect_poly(body)
    c.shape(body, shirt, outline=2.6 * s + 0.6, hatch=dict(spacing=int(9 * s) + 2, angle=60, alpha=0.18))
    # arms
    for side, mode in ((-1, arms[0]), (1, arms[1])):
        sx, sy = x + side * 34 * s, sh_y + 16 * s
        if mode == "down":
            ex, ey = x + side * 50 * s, hip_y - 4 * s
        elif mode == "up":
            ex, ey = x + side * 58 * s, sh_y - 70 * s
        elif mode == "forward":
            ex, ey = x + side * 60 * s, sh_y + 54 * s
        elif mode == "desk":
            ex, ey = x + side * 26 * s, sh_y + 70 * s
        elif mode == "point":
            ex, ey = x + side * 92 * s, sh_y + 10 * s
        elif isinstance(mode, tuple):
            ex, ey = x + mode[0] * s, sh_y + mode[1] * s
        else:
            ex, ey = x + side * 50 * s, hip_y - 4 * s
        c.shape(capsule((sx, sy), (ex, ey), 11 * s, 9.5 * s), shirt * 0.93, outline=2.4 * s + 0.5)
        c.shape(ellipse(ex, ey + 3 * s, 9.5 * s, 9.5 * s, n=16), face, outline=2.0 * s + 0.5, gran=0.15)
    if hold is not None:
        hold(c, x, sh_y, s)
    # head
    hx = x + look * 6 * s
    c.shape(ellipse(hx, head_cy, hr, hr * 1.02, n=44), face, outline=2.8 * s + 0.6, gran=0.12, shade=0.15, edge=0.25)
    # hair
    if hair == "bowl":
        hp = ellipse(hx, head_cy - 4 * s, hr * 1.06, hr * 1.02, n=30, a0=math.pi, a1=2 * math.pi)
        hp += [(hx + hr * 1.05, head_cy + 12 * s), (hx + hr * 0.62, head_cy + 4 * s), (hx + hr * 0.62, head_cy - 10 * s),
               (hx - hr * 0.7, head_cy - 10 * s), (hx - hr * 0.72, head_cy + 4 * s), (hx - hr * 1.05, head_cy + 12 * s)]
        c.shape(hp, hair_col, opacity=0.95, outline=2.6 * s + 0.6, hatch=dict(spacing=int(6 * s) + 2, angle=80, alpha=0.4))
    elif hair == "bun":
        c.shape(ellipse(hx, head_cy - hr * 1.0, hr * 0.42, hr * 0.36, n=20), hair_col, opacity=0.95, outline=2.4 * s)
        hp = ellipse(hx, head_cy - 2 * s, hr * 1.04, hr * 1.0, n=30, a0=math.pi, a1=2 * math.pi)
        hp += [(hx + hr * 1.04, head_cy + 6 * s), (hx + hr * 0.5, head_cy - 14 * s), (hx - hr * 0.5, head_cy - 14 * s),
               (hx - hr * 1.04, head_cy + 6 * s)]
        c.shape(hp, hair_col, opacity=0.95, outline=2.6 * s + 0.6, hatch=dict(spacing=int(6 * s) + 2, angle=80, alpha=0.4))
    elif hair == "hijab":
        hp = ellipse(hx, head_cy + 4 * s, hr * 1.22, hr * 1.22, n=36, a0=math.pi * 0.85, a1=math.pi * 2.15)
        hp += [(hx + hr * 1.3, sh_y + 40 * s), (hx - hr * 1.3, sh_y + 40 * s)]
        c.shape(hp, hair_col, opacity=0.9, outline=2.6 * s + 0.6)
        c.shape(ellipse(hx, head_cy + 6 * s, hr * 0.8, hr * 0.86, n=36), face, outline=2.4 * s, gran=0.12)
    elif hair == "old":
        hp = ellipse(hx, head_cy - 6 * s, hr * 1.02, hr * 0.9, n=24, a0=math.pi * 1.05, a1=math.pi * 1.95)
        c.shape(hp + [(hx, head_cy - hr * 0.6)], C(225, 222, 214), opacity=0.7, outline=2.2 * s)
        for side in (-1, 1):
            c.shape(ellipse(hx + side * hr * 0.92, head_cy - 2 * s, hr * 0.22, hr * 0.34, n=14), C(225, 222, 214), opacity=0.7,
                    outline=2.0 * s)
    elif hair == "cap":  # topi akademik / beret
        hp = ellipse(hx, head_cy - 4 * s, hr * 1.06, hr * 1.02, n=30, a0=math.pi, a1=2 * math.pi)
        hp += [(hx + hr * 1.05, head_cy + 8 * s), (hx - hr * 1.05, head_cy + 8 * s)]
        c.shape(hp, hair_col, opacity=0.95, outline=2.6 * s + 0.6)
        c.shape(ellipse(hx + 6 * s, head_cy - hr * 0.95, hr * 1.1, hr * 0.32, n=24), C(120, 30, 40), outline=2.4 * s)
    # face details
    ey = head_cy + 8 * s
    for side in (-1, 1):
        c.shape(ellipse(hx + side * 16 * s + look * 4 * s, ey, 3.6 * s, 4.2 * s, n=10), C(25, 20, 18), opacity=1.0, outline=0,
                clear=False, gran=0.0, edge=0.0)
        c.wash(c.mask(ellipse(hx + side * 27 * s, ey + 14 * s, 8 * s, 5 * s, n=12), blur=3), C(230, 150, 140), opacity=0.35,
               gran=0.1, edge=0.0)
    if mouth == "smile":
        c.line(ellipse(hx + look * 4 * s, ey + 12 * s, 7 * s, 5 * s, n=10, a0=0.2, a1=math.pi - 0.2), width=2.0 * s + 0.4,
               wobble=0.2)
    elif mouth == "o":
        c.outline(ellipse(hx + look * 4 * s, ey + 16 * s, 4 * s, 5 * s, n=10), width=2.0 * s + 0.4, wobble=0.1)
    elif mouth == "flat":
        c.line([(hx - 6 * s, ey + 16 * s), (hx + 6 * s, ey + 16 * s)], width=2.0 * s + 0.4, wobble=0.1)
    return head_cy


def rrect_poly(quad, r=10):
    # soften quad corners a little by inserting points
    out = []
    n = len(quad)
    for i in range(n):
        p0, p1, p2 = quad[i - 1], quad[i], quad[(i + 1) % n]
        a = (p1[0] + (p0[0] - p1[0]) * 0.08, p1[1] + (p0[1] - p1[1]) * 0.08)
        b = (p1[0] + (p2[0] - p1[0]) * 0.08, p1[1] + (p2[1] - p1[1]) * 0.08)
        out += [a, b]
    return out


def book(c, x, y, w, h, col, angle=0, spine_lines=True):
    poly = rot(rect(x, y, x + w, y + h), angle, x + w / 2, y + h)
    c.shape(poly, col, outline=2.2, shade=0.2)
    if spine_lines and h > 30:
        for f in (0.18, 0.82):
            yy = y + h * f
            c.line(rot([(x + 3, yy), (x + w - 3, yy)], angle, x + w / 2, y + h), width=1.6, wobble=0.3)


def shelf_books(c, x0, x1, y_base, h0=60, h1=110, seed=0, palette=None):
    r = random.Random(seed)
    palette = palette or [C(150, 50, 40), C(60, 90, 70), C(170, 120, 50), C(70, 70, 110), C(120, 80, 50), C(160, 140, 90)]
    x = x0
    while x < x1 - 14:
        w = r.uniform(14, 28)
        h = r.uniform(h0, h1)
        ang = 0 if r.random() > 0.12 else r.uniform(-12, 12)
        book(c, x, y_base - h, min(w, x1 - x), h, r.choice(palette), angle=ang)
        x += w + r.uniform(0, 3)


def paper_slip(c, cx, cy, w=70, h=44, angle=0, lines=3, col=C(244, 236, 214)):
    poly = rot(rect(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), angle, cx, cy)
    c.shape(poly, col, opacity=0.6, outline=1.8)
    for k in range(lines):
        yy = cy - h / 2 + h * (k + 1) / (lines + 1)
        L = w * (0.75 if k < lines - 1 else 0.45)
        c.line(rot([(cx - w / 2 + 8, yy), (cx - w / 2 + 8 + L, yy)], angle, cx, cy), width=1.3, alpha=0.7, wobble=0.6)
