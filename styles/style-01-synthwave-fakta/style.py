"""Style 01 — Synthwave Fakta.

Video vertikal 1080x1920 @30fps: hook judul besar -> N kartu fakta -> outro polling A/B.
Semua teks diambil dari file JSON konten (lihat konten/_template.json).
Mesin ini dipakai lewat build.py di root repo.
"""
import math
import random
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H, FPS = 1080, 1920, 30
HOR = 1340  # garis horizon

ROOT = Path(__file__).resolve().parents[2]
FONT_DIR = ROOT / "assets" / "fonts"
ANTON = str(FONT_DIR / "Anton-Regular.ttf")
POP_B = str(FONT_DIR / "Poppins-Bold.ttf")
POP_M = str(FONT_DIR / "Poppins-Medium.ttf")
POP_R = str(FONT_DIR / "Poppins-Regular.ttf")

# ---------------------------------------------------------------- palet
WHITE = (255, 255, 255)
PINK = (255, 62, 165)
ORANGE = (255, 146, 62)
YELLOW = (255, 216, 92)
CYAN = (90, 232, 255)
GREEN = (60, 220, 140)
RED = (255, 72, 96)
INK = (12, 5, 28)
SOFT = (226, 214, 255)
MUTED = (178, 160, 220)

CX = 540
INNER_W = 830
CARD = (60, 330, 1020, 1300)
Y_PILL, Y_HEAD, Y_HERO, Y_BODY, Y_SRC = 408, 542, 815, 1085, 1245

_fc = {}


def F(path, size):
    k = (path, size)
    if k not in _fc:
        _fc[k] = ImageFont.truetype(path, size)
    return _fc[k]


# ---------------------------------------------------------------- easing
def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def e_out(x):
    return 1 - (1 - clamp(x)) ** 3


def e_in(x):
    return clamp(x) ** 3


def e_back(x, s=1.9):
    x = clamp(x) - 1
    return x * x * ((s + 1) * x + s) + 1


def lerp(a, b, p):
    return a + (b - a) * p


def enter(t, start, dur=14, dist=60):
    p = e_out((t - start) / dur)
    return p, (1 - p) * dist


# ---------------------------------------------------------------- helper layer
def with_alpha(img, a):
    if a >= 0.999:
        return img
    r, g, b, al = img.split()
    al = al.point(lambda v, a=a: int(v * a))
    return Image.merge("RGBA", (r, g, b, al))


def place(frame, layer, cx, cy, alpha=1.0, scale=1.0):
    """Tempel layer RGBA dengan titik tengah (cx, cy)."""
    if alpha <= 0.004 or layer is None:
        return
    if abs(scale - 1) > 1e-3:
        nw, nh = max(1, int(layer.width * scale)), max(1, int(layer.height * scale))
        layer = layer.resize((nw, nh), Image.BICUBIC)
    layer = with_alpha(layer, alpha)
    x = int(round(cx - layer.width / 2))
    y = int(round(cy - layer.height / 2))
    sx = sy = 0
    if x < 0:
        sx, x = -x, 0
    if y < 0:
        sy, y = -y, 0
    ex = min(layer.width, sx + (W - x))
    ey = min(layer.height, sy + (H - y))
    if ex <= sx or ey <= sy:
        return
    if (sx, sy, ex, ey) != (0, 0, layer.width, layer.height):
        layer = layer.crop((sx, sy, ex, ey))
    frame.alpha_composite(layer, dest=(x, y))


def vgrad(w, h, c1, c2, y0=0, y1=None):
    y1 = h if y1 is None else y1
    ys = np.clip((np.arange(h) - y0) / max(1, (y1 - y0)), 0, 1)[:, None]
    c1 = np.array(c1, np.float32)
    c2 = np.array(c2, np.float32)
    row = c1[None, :] * (1 - ys) + c2[None, :] * ys
    arr = np.repeat(row[:, None, :], w, axis=1)
    return Image.fromarray(arr.astype(np.uint8), "RGB")


def render_text(lines, font, fill=WHITE, grad=None, glow=None, glow_r=18, glow_k=1.3,
                stroke=0, stroke_fill=INK, line_h=None, pad=40):
    """Layer teks rapat & rata tengah. Titik tengah visual == titik tengah layer."""
    if isinstance(lines, str):
        lines = [lines]
    if glow:
        pad = max(pad, int(glow_r * 2.8))
    asc, desc = font.getmetrics()
    line_h = line_h or (asc + desc)
    maxw = max(font.getlength(l) for l in lines)
    M = pad + stroke + 30
    W0 = int(maxw + 2 * M)
    H0 = int(line_h * (len(lines) - 1) + asc + desc + 2 * M)

    def mk(sw):
        m = Image.new("L", (W0, H0), 0)
        d = ImageDraw.Draw(m)
        for i, l in enumerate(lines):
            d.text((W0 / 2, M + i * line_h), l, font=font, fill=255, anchor="ma",
                   stroke_width=sw, stroke_fill=255)
        return m

    tmask = mk(0)
    smask = mk(stroke) if stroke else tmask
    bb = smask.getbbox()
    box = (bb[0] - pad, bb[1] - pad, bb[2] + pad, bb[3] + pad)
    tmask = tmask.crop(box)
    smask = smask.crop(box)
    w, h = tmask.size
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    if glow:
        gm = smask.filter(ImageFilter.GaussianBlur(glow_r)).point(lambda v: min(255, int(v * glow_k)))
        g = Image.new("RGBA", (w, h), tuple(glow) + (255,))
        g.putalpha(gm)
        out.alpha_composite(g)
    if stroke:
        s = Image.new("RGBA", (w, h), tuple(stroke_fill) + (255,))
        s.putalpha(smask)
        out.alpha_composite(s)
    if grad:
        fl = vgrad(w, h, grad[0], grad[1], pad, h - pad).convert("RGBA")
    else:
        fl = Image.new("RGBA", (w, h), tuple(fill) + (255,))
    fl.putalpha(tmask)
    out.alpha_composite(fl)
    return out


def wrap(text, font, maxw):
    words, lines, cur = text.split(), [], ""
    for wd in words:
        t = (cur + " " + wd).strip()
        if font.getlength(t) <= maxw:
            cur = t
        else:
            lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


def fit_font(path, lines, maxw, start):
    if isinstance(lines, str):
        lines = [lines]
    s = start
    while s > 30:
        f = F(path, s)
        if max(f.getlength(l) for l in lines) <= maxw:
            return f
        s -= 2
    return F(path, s)


def rrect(w, h, r, fill, outline=None, ow=0):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle((0, 0, w - 1, h - 1), r, fill=fill, outline=outline, width=ow)
    return im


def pill(text, font, bg, fg, padx=30, pady=14, outline=None):
    tw = font.getlength(text)
    bb = font.getbbox(text)
    th = bb[3] - bb[1]
    w, h = int(tw + 2 * padx), int(th + 2 * pady)
    im = rrect(w, h, h // 2, bg, outline, 2 if outline else 0)
    ImageDraw.Draw(im).text((w / 2, h / 2), text, font=font, fill=fg, anchor="mm")
    return im


def icon(kind, size, color):
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse((0, 0, size - 1, size - 1), fill=color + (255,))
    lw = max(4, size // 9)
    s = size
    if kind == "check":
        d.line([(s * .27, s * .52), (s * .44, s * .68), (s * .74, s * .34)], fill=WHITE, width=lw, joint="curve")
    else:
        d.line([(s * .32, s * .32), (s * .68, s * .68)], fill=WHITE, width=lw)
        d.line([(s * .68, s * .32), (s * .32, s * .68)], fill=WHITE, width=lw)
    return im


def chip(text, ok, font, h=88, padx=26):
    color = GREEN if ok else RED
    ic = icon("check" if ok else "cross", h - 30, color)
    tw = int(font.getlength(text))
    w = padx + ic.width + 18 + tw + padx + 6
    im = rrect(w, h, 22, (255, 255, 255, 26), color + (230,), 3)
    im.alpha_composite(ic, dest=(padx, 15))
    ImageDraw.Draw(im).text((padx + ic.width + 18, h / 2 + 2), text, font=font, fill=WHITE, anchor="lm")
    return im


def fmt_id(n):
    return f"{n:,}".replace(",", ".")


# ---------------------------------------------------------------- background
def draw_palm(d, base, top, sc, col):
    bx, by = base
    tx, ty = top
    cx, cy = bx + (tx - bx) * 0.15, (by + ty) / 2
    n = 40
    pts = []
    for i in range(n + 1):
        s = i / n
        x = (1 - s) ** 2 * bx + 2 * (1 - s) * s * cx + s * s * tx
        y = (1 - s) ** 2 * by + 2 * (1 - s) * s * cy + s * s * ty
        pts.append((x, y))
    left, right = [], []
    for i, (x, y) in enumerate(pts):
        j, k = min(i + 1, n), max(i - 1, 0)
        dx, dy = pts[j][0] - pts[k][0], pts[j][1] - pts[k][1]
        L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L, dx / L
        wd = lerp(24, 12, i / n) * sc
        left.append((x + nx * wd, y + ny * wd))
        right.append((x - nx * wd, y - ny * wd))
    d.polygon(left + right[::-1], fill=col)
    for ang, ln, dr in [(-178, 1.0, .55), (-150, 1.05, .75), (-120, .8, .9), (-85, .6, 1.2),
                        (-55, .85, .85), (-25, 1.05, .7), (5, 1.0, .55), (165, .7, .4), (25, .7, .45)]:
        a = math.radians(ang)
        Lf = 250 * sc * ln
        m = 30
        cl = []
        for i in range(m + 1):
            s = i / m
            cl.append((tx + math.cos(a) * Lf * s, ty + math.sin(a) * Lf * s + dr * Lf * s * s * 0.75))
        cr = []
        for i, (x, y) in enumerate(cl):
            j, k = min(i + 1, m), max(i - 1, 0)
            dx, dy = cl[j][0] - cl[k][0], cl[j][1] - cl[k][1]
            L = math.hypot(dx, dy) or 1
            nx, ny = -dy / L, dx / L
            s = i / m
            wd = 32 * sc * (math.sin(math.pi * s) ** 0.6) * (1 - 0.35 * s)
            wd *= 1 + 0.16 * math.sin(s * 34)
            cr.append(((x + nx * wd, y + ny * wd), (x - nx * wd * 0.55, y - ny * wd * 0.55)))
        d.polygon([p[0] for p in cr] + [p[1] for p in cr[::-1]], fill=col)
    for ox, oy in [(-10, 10), (8, 14), (0, 22)]:
        r = 9 * sc
        d.ellipse((tx + ox * sc - r, ty + oy * sc - r, tx + ox * sc + r, ty + oy * sc + r), fill=col)


def build_static(seed=7):
    rnd = random.Random(seed)
    sky = vgrad(W, HOR, (9, 5, 28), (52, 14, 92), 0, 900)
    lower = vgrad(W, HOR, (52, 14, 92), (150, 34, 120), 900, HOR)
    skyarr = np.array(sky)
    skyarr[900:] = np.array(lower)[900:]
    base = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    base.paste(Image.fromarray(skyarr), (0, 0))
    st = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(st)
    for _ in range(170):
        x, y = rnd.uniform(0, W), rnd.uniform(0, 1050)
        r = rnd.choice([1, 1, 1.5, 2, 2.5])
        sd.ellipse((x - r, y - r, x + r, y + r), fill=(255, 235, 255, rnd.randint(70, 210)))
    base.alpha_composite(st)
    sx, sy, sr = 540, 1300, 330
    gl = Image.new("L", (W, H), 0)
    ImageDraw.Draw(gl).ellipse((sx - sr - 40, sy - sr - 40, sx + sr + 40, sy + sr + 40), fill=170)
    gl = gl.filter(ImageFilter.GaussianBlur(90))
    glow = Image.new("RGBA", (W, H), (255, 70, 160, 255))
    glow.putalpha(gl)
    base.alpha_composite(glow)
    sm = Image.new("L", (W, H), 0)
    sdm = ImageDraw.Draw(sm)
    sdm.ellipse((sx - sr, sy - sr, sx + sr, sy + sr), fill=255)
    for k in range(8):
        y = sy - 175 + k * 34
        sdm.rectangle((0, y, W, y + 4 + k * 2.6), fill=0)
    sdm.rectangle((0, HOR, W, H), fill=0)
    sun = vgrad(W, H, (255, 232, 128), (255, 58, 150), sy - sr, HOR).convert("RGBA")
    sun.putalpha(sm)
    base.alpha_composite(sun)
    sk = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    kd = ImageDraw.Draw(sk)
    x = -10
    while x < W:
        bw = rnd.randint(26, 70)
        bh = rnd.randint(20, 130)
        if 330 < x < 750:
            bh = int(bh * 1.25)
        kd.rectangle((x, HOR - bh, x + bw, HOR), fill=(30, 8, 52, 255))
        if rnd.random() < 0.35:
            kd.rectangle((x + bw // 2 - 2, HOR - bh - rnd.randint(14, 40), x + bw // 2 + 2, HOR - bh),
                         fill=(30, 8, 52, 255))
        x += bw + rnd.randint(-6, 6)
    for _ in range(160):
        wx, wy = rnd.randint(0, W - 1), rnd.randint(HOR - 120, HOR - 6)
        if sk.getpixel((wx, wy))[3] > 0:
            kd.rectangle((wx, wy, wx + 3, wy + 3), fill=(255, 190, 120, rnd.randint(80, 200)))
    base.alpha_composite(sk)
    base.paste(vgrad(W, H - HOR, (34, 8, 56), (6, 3, 16)), (0, HOR))
    rf = Image.new("L", (W, H), 0)
    ImageDraw.Draw(rf).ellipse((sx - 260, HOR - 30, sx + 260, HOR + 160), fill=120)
    rf = rf.filter(ImageFilter.GaussianBlur(50))
    ImageDraw.Draw(rf).rectangle((0, 0, W, HOR), fill=0)
    rfl = Image.new("RGBA", (W, H), (255, 90, 170, 255))
    rfl.putalpha(rf)
    base.alpha_composite(rfl)
    hl = Image.new("L", (W, H), 0)
    ImageDraw.Draw(hl).rectangle((0, HOR - 3, W, HOR + 3), fill=255)
    hg = Image.new("RGBA", (W, H), (255, 90, 200, 255))
    hg.putalpha(hl.filter(ImageFilter.GaussianBlur(14)))
    base.alpha_composite(hg)
    hc = Image.new("RGBA", (W, H), (255, 190, 240, 255))
    hc.putalpha(hl.point(lambda v: v * 0.9))
    base.alpha_composite(hc)
    return base


def build_palms():
    p = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(p)
    col = (8, 3, 18, 255)
    draw_palm(d, (175, H + 60), (290, 1485), 0.8, col)
    draw_palm(d, (930, H + 60), (815, 1515), 0.75, col)
    draw_palm(d, (-60, H + 60), (150, 1290), 1.3, col)
    draw_palm(d, (1140, H + 60), (925, 1315), 1.25, col)
    return p


def grid_layer(shift):
    gh = H - HOR
    lay = Image.new("RGBA", (W, gh), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    col = (255, 70, 190)
    for k in range(0, 60):
        z = 1 + k - shift
        if z <= 0.08:
            continue
        y = gh * 0.9 / z
        if y > gh + 4:
            continue
        a = int(235 * min(1.0, (1 / z) ** 0.45))
        wdt = 4 if z < 2.5 else 3 if z < 6 else 2
        d.line((0, y, W, y), fill=col + (a,), width=wdt)
    for j in range(-16, 17):
        xb = 540 + j * 150
        d.line((540 + j * 3.5, 0, xb + (xb - 540) * 0.6, gh * 1.6), fill=col + (170,), width=3)
    arr = np.array(lay).astype(np.float32)
    arr[..., 3] *= np.clip(np.linspace(0.25, 1.15, gh), 0, 1)[:, None]
    lay = Image.fromarray(arr.astype(np.uint8), "RGBA")
    glow = lay.resize((W // 4, gh // 4), Image.BILINEAR).filter(ImageFilter.GaussianBlur(3)).resize((W, gh), Image.BILINEAR)
    glow.putalpha(glow.getchannel("A").point(lambda v: min(255, int(v * 1.8))))
    out = Image.new("RGBA", (W, gh), (0, 0, 0, 0))
    out.alpha_composite(glow)
    out.alpha_composite(lay)
    return out


def build_card(static):
    x0, y0, x1, y1 = CARD
    w, h = x1 - x0, y1 - y0
    crop = static.crop((x0 - 60, y0 - 60, x1 + 60, y1 + 60)).convert("RGB").filter(ImageFilter.GaussianBlur(34))
    crop = crop.crop((60, 60, 60 + w, 60 + h))
    glass = Image.blend(crop, Image.new("RGB", (w, h), (18, 8, 44)), 0.62).convert("RGBA")
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), 46, fill=255)
    glass.putalpha(m)
    ring = Image.new("L", (w, h), 0)
    ImageDraw.Draw(ring).rounded_rectangle((0, 0, w - 1, h - 1), 46, outline=255, width=3)
    rg = vgrad(w, h, (255, 80, 190), (255, 150, 70)).convert("RGBA")
    rg.putalpha(ring.point(lambda v: int(v * 0.85)))
    glass.alpha_composite(rg)
    sheen = Image.new("RGBA", (w, h), (255, 255, 255, 255))
    sa = Image.new("L", (w, h), 0)
    ImageDraw.Draw(sa).rounded_rectangle((3, 3, w - 4, 160), 44, fill=16)
    sheen.putalpha(sa.filter(ImageFilter.GaussianBlur(20)))
    glass.alpha_composite(sheen)
    pad = 70
    sh = Image.new("L", (w + 2 * pad, h + 2 * pad), 0)
    ImageDraw.Draw(sh).rounded_rectangle((pad, pad + 24, pad + w, pad + h + 24), 46, fill=150)
    full = Image.new("RGBA", (w + 2 * pad, h + 2 * pad), (4, 0, 12, 255))
    full.putalpha(sh.filter(ImageFilter.GaussianBlur(30)))
    full.alpha_composite(glass, dest=(pad, pad))
    return full


def build_watermark(text):
    f = F(POP_B, 46)
    padx, h = 30, 76
    w = int(f.getlength(text) + 2 * padx)
    im = rrect(w, h, h // 2, (10, 4, 26, 135), (255, 255, 255, 110), 2)
    ImageDraw.Draw(im).text((w / 2, h / 2 + 2), text, font=f, fill=(255, 255, 255, 240), anchor="mm")
    return im


# ---------------------------------------------------------------- renderer
class Renderer:
    def __init__(self, cfg):
        self.cfg = cfg
        tm = cfg.get("timing", {})
        n_fact = len(cfg["facts"])
        self.n_fact = n_fact
        self.scenes = [("hook", int(round(tm.get("hook", 4.5) * FPS)))]
        for i in range(n_fact):
            self.scenes.append((f"f{i}", int(round(tm.get("fact", 6.5) * FPS))))
        self.scenes.append(("outro", int(round(tm.get("outro", 5.0) * FPS))))
        self.starts = []
        acc = 0
        for _, l in self.scenes:
            self.starts.append(acc)
            acc += l
        self.total = acc
        self._cache = {}
        static = build_static()
        palms = build_palms()
        self.bg = []
        for i in range(30):
            fr = static.copy()
            fr.alpha_composite(grid_layer(i / 30), dest=(0, HOR))
            fr.alpha_composite(palms)
            self.bg.append(fr)
        self.card = build_card(static)
        self.card_c = ((CARD[0] + CARD[2]) / 2, (CARD[1] + CARD[3]) / 2)
        wm_text = cfg.get("brand", {}).get("watermark", "")
        self.wm = build_watermark(wm_text) if wm_text else None
        rp = random.Random(11)
        self.parts = [(rp.uniform(0, W), rp.uniform(0, H), rp.uniform(0.6, 2.2), rp.uniform(0.4, 1.4),
                       rp.uniform(0, 6.28)) for _ in range(55)]

    def cut_times(self):
        """Detik pergantian scene (untuk whoosh di musik)."""
        return [s / FPS for s in self.starts[1:]]

    def C(self, key, fn):
        if key not in self._cache:
            self._cache[key] = fn()
        return self._cache[key]

    # -- elemen kecil
    def particles(self, frame, g):
        d = ImageDraw.Draw(frame)
        for x, y, r, sp, ph in self.parts:
            yy = (y - g * sp * 2.2) % (HOR - 40)
            xx = x + math.sin(g / 40 + ph) * 18
            tw = 0.55 + 0.45 * math.sin(g / 9 + ph)
            d.ellipse((xx - r, yy - r, xx + r, yy + r),
                      fill=(int(255 * tw), int(150 + 80 * tw), int(220 * tw + 30), 255))

    def progress(self, frame, active, p):
        x0, x1, y = 60, 1020, 276
        n = self.n_fact
        gap = 12
        sw = (x1 - x0 - (n - 1) * gap) / n
        lay = Image.new("RGBA", (x1 - x0, 12), (0, 0, 0, 0))
        d = ImageDraw.Draw(lay)
        for i in range(n):
            a = i * (sw + gap)
            d.rounded_rectangle((a, 0, a + sw, 10), 5, fill=(255, 255, 255, 60))
            fill = 1.0 if i < active else (p if i == active else 0.0)
            if fill > 0:
                d.rounded_rectangle((a, 0, a + max(10, sw * fill), 10), 5, fill=(255, 255, 255, 235))
        frame.alpha_composite(lay, dest=(x0, y))

    def headline(self, lines, size=108):
        f = fit_font(ANTON, lines, INNER_W, size)
        return render_text(lines, f, fill=WHITE, glow=(255, 60, 170), glow_r=16, glow_k=0.9,
                           line_h=int(f.size * 1.08), pad=34)

    def big_number(self, text, size):
        f = fit_font(ANTON, text, INNER_W, size)
        return render_text(text, f, grad=(YELLOW, ORANGE), glow=(255, 115, 40), glow_r=22, glow_k=0.82, pad=30)

    # -- hero per tipe
    def hero(self, frame, key, h, t, a_exit, dy_exit):
        kind = h["type"]
        if kind == "counter":
            p, dy = enter(t, 8)
            v = int(h["value"] * e_out((t - 8) / 46))
            txt = h.get("prefix", "") + fmt_id(v) + h.get("suffix", "")
            place(frame, self.big_number(txt, 172), CX, Y_HERO - 30 + dy + dy_exit, p * a_exit)
            if h.get("caption"):
                p2, dy2 = enter(t, 16)
                cap = self.C(key + "cap", lambda: render_text(h["caption"], fit_font(POP_B, h["caption"], INNER_W, 34),
                                                              fill=CYAN, pad=12))
                place(frame, cap, CX, Y_HERO + 92 + dy2 + dy_exit, p2 * a_exit)
        elif kind == "price":
            p, dy = enter(t, 8)
            old = self.C(key + "old", lambda: render_text(h["old"], F(POP_B, 62), fill=(205, 195, 235), pad=24))
            sp = e_out((t - 20) / 12)
            lay = old
            if sp > 0:
                lay = old.copy()
                ImageDraw.Draw(lay).line((14, lay.height / 2 + 4, 14 + sp * (lay.width - 28), lay.height / 2 + 4),
                                         fill=RED + (255,), width=9)
            place(frame, lay, CX, Y_HERO - 96 + dy + dy_exit, p * a_exit * (1 - 0.35 * sp))
            arr = self.C("arrow", lambda: render_text("↓", F(ANTON, 60), fill=MUTED, pad=8))
            pa, dya = enter(t, 26, 10, 30)
            place(frame, arr, CX, Y_HERO - 38 + dya + dy_exit, pa * a_exit)
            pn = e_back((t - 30) / 14)
            new = self.C(key + "new", lambda: self.big_number(h["new"], 140))
            place(frame, new, CX, Y_HERO + 58 + dy_exit, clamp((t - 30) / 6) * a_exit, scale=0.6 + 0.4 * pn)
        elif kind == "chips":
            f = F(POP_B, 40)
            items = h["items"]
            rows = [[it for it in items if it.get("ok", True)], [it for it in items if not it.get("ok", True)]]
            rows = [r for r in rows if r]
            ys = [Y_HERO - 72, Y_HERO + 45] if len(rows) == 2 else [Y_HERO - 10]
            k = 0
            for ri, row in enumerate(rows):
                chips = [self.C(f"{key}chip{ri}{i}", lambda it=it: chip(it["text"], it.get("ok", True), f))
                         for i, it in enumerate(row)]
                gap = 24
                tw = sum(c.width for c in chips) + gap * (len(chips) - 1)
                x = CX - tw / 2
                for c in chips:
                    st = 8 + k * 6
                    bad = ri == 1 or not row[0].get("ok", True)
                    if bad:
                        pp = e_back((t - st - 6) / 14)
                        aa = clamp((t - st - 6) / 6)
                        shake = math.sin((t - 36) * 1.9) * 16 * (1 - (t - 36) / 20) if 36 <= t <= 56 else 0
                        place(frame, c, x + c.width / 2 + shake, ys[ri] + dy_exit, aa * a_exit, scale=0.6 + 0.4 * pp)
                    else:
                        pp, dd = enter(t, st)
                        place(frame, c, x + c.width / 2, ys[ri] + dd + dy_exit, pp * a_exit)
                    x += c.width + gap
                    k += 1
        elif kind == "score":
            p, dy = enter(t, 8)
            v = int(round(h["value"] * e_out((t - 8) / 34)))
            lay = render_text(str(v), F(ANTON, 215), grad=(YELLOW, ORANGE), glow=(255, 110, 40),
                              glow_r=24, glow_k=0.85, pad=30)
            place(frame, lay, CX - 40, Y_HERO + 8 + dy + dy_exit, p * a_exit)
            of = self.C(key + "of", lambda: render_text(f"/{h.get('max', 100)}", F(POP_B, 54), fill=SOFT, pad=10))
            place(frame, of, CX + 135, Y_HERO + 70 + dy + dy_exit, p * a_exit)
            if h.get("badge"):
                pb = e_back((t - 44) / 14)
                badge = self.C(key + "badge", lambda: pill(h["badge"], F(POP_B, 34), RED + (255,), WHITE, padx=24, pady=12))
                place(frame, badge, CX + 175, Y_HERO - 58 + dy_exit, clamp((t - 44) / 6) * a_exit, scale=0.5 + 0.5 * pb)
        elif kind == "big":
            pb = e_back((t - 8) / 16)
            big = self.C(key + "big", lambda: self.big_number(h["text"], 205))
            place(frame, big, CX, Y_HERO - 18 + dy_exit, clamp((t - 8) / 6) * a_exit, scale=0.55 + 0.45 * pb)
            if h.get("caption"):
                p2, d2 = enter(t, 18)
                cap = self.C(key + "cap", lambda: render_text(h["caption"], fit_font(POP_B, h["caption"], INNER_W, 36),
                                                              fill=CYAN, pad=12))
                place(frame, cap, CX, Y_HERO + 122 + d2 + dy_exit, p2 * a_exit)
        else:
            raise ValueError(f"tipe hero tidak dikenal: {kind}")

    # -- scene
    def draw_fact(self, frame, idx, t, T):
        spec = self.cfg["facts"][idx]
        key = f"f{idx}"
        q = e_in((t - (T - 12)) / 12)
        a_exit, dy_exit = 1 - q, -q * 50
        label = spec.get("label", f"{self.cfg.get('fact_label', 'FAKTA')} #{idx + 1}")
        pl = self.C(key + "pill", lambda: pill(label, F(POP_B, 32), PINK + (255,), WHITE, padx=28, pady=13))
        p, dy = enter(t, 0, 12, 30)
        place(frame, pl, CX, Y_PILL + dy + dy_exit, p * a_exit)
        hd = self.C(key + "head", lambda: self.headline(spec["head"]))
        p, dy = enter(t, 3)
        place(frame, hd, CX, Y_HEAD + dy + dy_exit, p * a_exit)
        self.hero(frame, key, spec["hero"], t, a_exit, dy_exit)
        bf = F(POP_M, 40)
        bd = self.C(key + "body", lambda: render_text(wrap(spec["body"], bf, INNER_W - 20), bf, fill=SOFT,
                                                      line_h=int(40 * 1.38), pad=20))
        p, dy = enter(t, 22)
        place(frame, bd, CX, Y_BODY + dy + dy_exit, p * a_exit)
        if spec.get("source"):
            sr = self.C(key + "src", lambda: render_text(spec["source"], fit_font(POP_R, spec["source"], INNER_W, 25),
                                                         fill=MUTED, pad=10))
            p, dy = enter(t, 28, 12, 20)
            place(frame, sr, CX, Y_SRC + dy + dy_exit, p * 0.95 * a_exit)

    def draw_hook(self, frame, t, T):
        hk = self.cfg["hook"]
        q = e_in((t - (T - 12)) / 12)
        a_exit, dy_exit = 1 - q, -q * 60
        if hk.get("tag"):
            tag = self.C("tag", lambda: pill(hk["tag"], F(POP_B, 34), (255, 255, 255, 30), WHITE,
                                             padx=30, pady=14, outline=(255, 255, 255, 150)))
            p, dy = enter(t, 8, 14, -40)
            place(frame, tag, CX, 430 + dy + dy_exit, p * a_exit)
        title = self.C("title", lambda: render_text(hk["title"], fit_font(ANTON, hk["title"], 940, 340), fill=WHITE,
                                                    glow=(255, 50, 170), glow_r=30, glow_k=1.1, pad=50))
        place(frame, title, CX, 650 + dy_exit, a_exit, scale=lerp(1.18, 1.0, e_out(t / 9)))
        if hk.get("headline"):
            sub = self.C("akh", lambda: render_text(hk["headline"], fit_font(ANTON, hk["headline"], 940, 148),
                                                    grad=(YELLOW, ORANGE), stroke=6, stroke_fill=INK,
                                                    glow=(255, 100, 30), glow_r=20, glow_k=0.7, pad=30))
            pb = e_back((t - 10) / 14)
            place(frame, sub, CX, 885 + dy_exit, clamp((t - 10) / 5) * a_exit, scale=0.6 + 0.4 * pb)
        if hk.get("line"):
            l1 = self.C("l1", lambda: render_text(hk["line"], fit_font(POP_M, hk["line"], 960, 42), fill=WHITE,
                                                  stroke=3, stroke_fill=INK, pad=14))
            p, dy = enter(t, 22)
            place(frame, l1, CX, 1030 + dy + dy_exit, p * a_exit)
        if hk.get("pill"):
            l2 = self.C("l2", lambda: pill(hk["pill"], fit_font(POP_B, hk["pill"], 900, 38), PINK + (255,), WHITE,
                                           padx=30, pady=16))
            p, dy = enter(t, 30)
            place(frame, l2, CX, 1112 + dy + dy_exit, p * a_exit)

    def draw_outro(self, frame, t, T):
        oc = self.cfg["outro"]
        pl = self.C("opill", lambda: pill(oc.get("pill", "GILIRAN KAMU"), F(POP_B, 32), PINK + (255,), WHITE,
                                          padx=28, pady=13))
        p, dy = enter(t, 0, 12, 30)
        place(frame, pl, CX, Y_PILL + dy, p)
        hd = self.C("ohead", lambda: self.headline(oc["head"], size=116))
        p, dy = enter(t, 3)
        place(frame, hd, CX, Y_HEAD + dy, p)

        def box(letter, lines, col):
            w, h = 400, 250
            im = rrect(w, h, 34, (255, 255, 255, 22), col + (235,), 4)
            d = ImageDraw.Draw(im)
            d.text((w / 2, 74), letter, font=F(ANTON, 104), fill=col, anchor="mm")
            f = fit_font(POP_B, lines, w - 40, 36)
            for i, ln in enumerate(lines[:2]):
                d.text((w / 2, 162 + i * 46), ln, font=f, fill=WHITE, anchor="mm")
            return im

        cols = [YELLOW, CYAN]
        opts = oc.get("options", [])[:2]
        for i, o in enumerate(opts):
            b = self.C(f"box{i}", lambda o=o, i=i: box(o["letter"], o["lines"], cols[i]))
            cx = CX - 212 + 424 * i if len(opts) == 2 else CX
            st = 12 + i * 6
            pp = e_back((t - st) / 14)
            pulse = 1 + 0.025 * math.sin((t - 40 - i * 15) / 5) if t > 40 else 1
            place(frame, b, cx, 842, clamp((t - st) / 6), scale=(0.6 + 0.4 * pp) * pulse)
        if oc.get("cta"):
            k1 = self.C("k1", lambda: render_text(oc["cta"], fit_font(POP_B, oc["cta"], INNER_W, 46), fill=YELLOW, pad=14))
            p, dy = enter(t, 26)
            place(frame, k1, CX, 1090 + dy, p)
        if oc.get("follow"):
            k2 = self.C("k2", lambda: render_text(oc["follow"], fit_font(POP_M, oc["follow"], INNER_W, 36), fill=SOFT, pad=12))
            p, dy = enter(t, 32)
            place(frame, k2, CX, 1175 + dy, p)

    # -- frame lengkap
    def frame(self, g):
        si = max(i for i, s in enumerate(self.starts) if s <= g)
        name, T = self.scenes[si]
        t = g - self.starts[si]
        fr = self.bg[g % 30].copy()
        self.particles(fr, g)
        if si >= 1:
            if si == 1:
                p = e_out(t / 12)
                place(fr, self.card, self.card_c[0], self.card_c[1] + (1 - p) * 40, p, scale=0.96 + 0.04 * p)
            else:
                place(fr, self.card, *self.card_c)
            if name == "outro":
                self.progress(fr, self.n_fact, 1)
            else:
                self.progress(fr, si - 1, t / T)
        if name == "hook":
            self.draw_hook(fr, t, T)
        elif name == "outro":
            self.draw_outro(fr, t, T)
        else:
            self.draw_fact(fr, si - 1, t, T)
        if self.wm is not None:
            place(fr, self.wm, W - 50 - self.wm.width / 2, 150, 0.92)
        rgb = np.asarray(fr.convert("RGB"))
        fl = 0.0
        if name == "hook" and 1 <= t < 8:
            fl = 0.55 * (1 - (t - 1) / 7)
        elif si >= 1 and t < 5:
            fl = 0.16 * (1 - t / 5)
        if fl > 0:
            a = rgb.astype(np.float32)
            rgb = (a + (255 - a) * fl).astype(np.uint8)
        return rgb
