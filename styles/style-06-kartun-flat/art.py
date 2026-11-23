"""Sprite vektor datar untuk style-06 (parabel uang). Semua digambar dengan kode, 2x lalu diperkecil (anti-alias).

Setiap fungsi mengembalikan RGBA PIL. Titik jangkar (anchor) sprite = tengah bawah, kecuali disebut lain.
"""
import math
import random
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[2]
FD = ROOT / "assets" / "fonts"
S = 2  # supersample

INK = (42, 31, 26)
CREAM = (250, 238, 214)
WHITE = (255, 255, 255)
RED = (226, 72, 58)
GREEN = (36, 128, 82)
GREEN_L = (126, 210, 138)
AMBER = (246, 184, 58)
TEAL = (34, 143, 141)
SKINS = [(236, 186, 146), (222, 168, 128), (204, 148, 108), (232, 180, 140)]
SONS = [(76, 107, 152), (34, 143, 141), (243, 162, 41), (224, 74, 60)]
PANTS = (47, 53, 66)
HAIR = (43, 32, 27)
WOOD = (196, 132, 76)
WOOD_D = (150, 96, 52)

_fc = {}


def F(size, name="Bold"):
    k = (name, int(size))
    if k not in _fc:
        _fc[k] = ImageFont.truetype(str(FD / f"Poppins-{name}.ttf"), max(1, int(size)))
    return _fc[k]


class Pen:
    """Menggambar dalam satuan akhir; otomatis dikali S."""

    def __init__(self, w, h):
        self.w, self.h = w, h
        self.im = Image.new("RGBA", (int(w * S), int(h * S)), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.im)

    def _b(self, box):
        return [v * S for v in box]

    def rect(self, box, fill, r=0, ol=INK, w=4):
        self.d.rounded_rectangle(self._b(box), r * S, fill=fill, outline=ol, width=int(w * S) if ol else 0)

    def ell(self, box, fill, ol=INK, w=4):
        self.d.ellipse(self._b(box), fill=fill, outline=ol, width=int(w * S) if ol else 0)

    def circ(self, x, y, r, fill, ol=INK, w=4):
        self.ell((x - r, y - r, x + r, y + r), fill, ol, w)

    def poly(self, pts, fill, ol=INK, w=4):
        p = [(x * S, y * S) for x, y in pts]
        self.d.polygon(p, fill=fill)
        if ol:
            self.d.line(p + [p[0]], fill=ol, width=int(w * S), joint="curve")

    def line(self, pts, col=INK, w=4):
        self.d.line([(x * S, y * S) for x, y in pts], fill=col, width=int(w * S), joint="curve")
        for x, y in (pts[0], pts[-1]):
            r = w / 2
            self.d.ellipse(((x - r) * S, (y - r) * S, (x + r) * S, (y + r) * S), fill=col)

    def arc(self, box, a0, a1, col=INK, w=4):
        self.d.arc(self._b(box), a0, a1, fill=col, width=int(w * S))

    def text(self, xy, s, size, col=INK, anchor="mm", name="Bold", stroke=0, scol=None):
        self.d.text((xy[0] * S, xy[1] * S), s, font=F(size * S, name), fill=col, anchor=anchor,
                    stroke_width=int(stroke * S), stroke_fill=scol or col)

    def done(self):
        return self.im.resize((int(self.w), int(self.h)), Image.LANCZOS)


# ------------------------------------------------------------------ orang
def _head(p, cx, cy, skin, face="smile", hair=HAIR, old=False):
    p.circ(cx - 57, cy + 6, 12, skin)
    p.circ(cx + 57, cy + 6, 12, skin)
    p.circ(cx, cy, 58, skin)
    if not old:
        # topi rambut: potongan lingkaran atas + poni
        hp = Pen(p.w, p.h)
        hp.d.ellipse(((cx - 58) * S, (cy - 58) * S, (cx + 58) * S, (cy + 58) * S), fill=hair)
        m = Image.new("L", hp.im.size, 0)
        md = ImageDraw.Draw(m)
        pts = [(cx - 70, cy - 80), (cx + 70, cy - 80), (cx + 70, cy - 14), (cx + 34, cy - 20), (cx + 8, cy - 12),
               (cx - 22, cy - 18), (cx - 70, cy - 8)]
        md.polygon([(x * S, y * S) for x, y in pts], fill=255)
        hp.im.putalpha(Image.fromarray(np.minimum(
            np.asarray(hp.im.getchannel("A")), np.asarray(m))))
        p.im.alpha_composite(hp.im)
        p.ell((cx - 58, cy - 58, cx + 58, cy + 58), None)
    else:
        p.ell((cx - 58, cy - 58, cx + 58, cy + 58), None)
        for sx in (-1, 1):  # rambut putih samping
            p.poly([(cx + sx * 40, cy - 34), (cx + sx * 66, cy - 18), (cx + sx * 68, cy + 18), (cx + sx * 50, cy + 22)],
                   (240, 240, 236), w=3)
    ey = cy + 4
    _head_features(p, cx, ey, face)
    if old:
        p.poly([(cx - 40, ey + 14), (cx + 40, ey + 14), (cx + 30, ey + 52), (cx, ey + 66), (cx - 30, ey + 52)],
               (244, 244, 240), w=3)
        p.arc((cx - 14, ey + 8, cx + 14, ey + 26), 20, 160, INK, 3)
        p.line([(cx - 34, ey - 20), (cx - 8, ey - 16)], (230, 230, 226), 6)
        p.line([(cx + 34, ey - 20), (cx + 8, ey - 16)], (230, 230, 226), 6)


def _head_features(p, cx, ey, face):
    if face in ("smile", "happy", "o", "worry", "talk"):
        p.circ(cx - 19, ey, 6, INK, None)
        p.circ(cx + 19, ey, 6, INK, None)
    if face == "smile":
        p.arc((cx - 16, ey + 2, cx + 16, ey + 26), 20, 160, INK, 4)
    elif face == "happy" or face == "talk":
        p.d.chord(((cx - 16) * S, (ey + 10) * S, (cx + 16) * S, (ey + 34) * S), 0, 180, fill=(150, 44, 40),
                  outline=INK, width=3 * S)
    elif face == "o":
        p.ell((cx - 8, ey + 14, cx + 8, ey + 32), (150, 44, 40), w=3)
    elif face == "worry":
        p.line([(cx - 13, ey + 24), (cx - 5, ey + 19), (cx + 4, ey + 24), (cx + 13, ey + 19)], INK, 3.5)
        p.line([(cx - 32, ey - 13), (cx - 12, ey - 22)], INK, 4)
        p.line([(cx + 32, ey - 13), (cx + 12, ey - 22)], INK, 4)


@lru_cache(maxsize=None)
def person(i=0, face="smile", arm="down", num=True):
    """Tokoh bernomor (i: 0..3) atau 'father'. Kanvas 230x420, kaki di bawah."""
    if i == "father":
        return tokoh((154, 108, 72), 1, "old", None, None, face, arm, cane=True)
    return tokoh(SONS[i], i, "short", HAIR, str(i + 1) if num else None, face, arm)


@lru_cache(maxsize=None)
def tokoh(shirt=(76, 107, 152), skin=0, hair="short", hair_col=HAIR, badge=None, face="smile", arm="down",
          cane=False, pants=PANTS, skirt=False):
    """Tokoh umum. hair: short / long / hijab / old. badge: teks di lingkaran dada (None = polos)."""
    W_, H_ = 230, 420
    p = Pen(W_, H_)
    cx = W_ / 2
    col = shirt
    sk = SKINS[skin % len(SKINS)] if isinstance(skin, int) else skin
    hc = hair_col or HAIR
    if skirt:
        p.poly([(cx - 50, 290), (cx + 50, 290), (cx + 60, 380), (cx - 60, 380)], pants)
        for x in (cx - 30, cx + 12):
            p.rect((x, 372, x + 18, 396), sk, 6, w=3)
    else:
        for x in (cx - 32, cx + 10):
            p.rect((x, 296, x + 22, 396), pants, 6)
    p.ell((cx - 44, 386, cx - 4, 408), (34, 36, 44))
    p.ell((cx + 4, 386, cx + 44, 408), (34, 36, 44))
    if hair == "long":
        p.rect((cx - 66, 70, cx + 66, 236), hc, 40)
    def arm_up():
        p.rect((cx + 46, 84, cx + 72, 196), col, 13)
        p.circ(cx + 59, 80, 13, sk)
    if arm == "up" and hair != "hijab":
        arm_up()
    elif arm != "up":
        p.poly([(cx + 44, 190), (cx + 66, 186), (cx + 74, 286), (cx + 52, 290)], col)
        p.circ(cx + 64, 292, 12, sk)
    p.poly([(cx - 44, 190), (cx - 66, 186), (cx - 74, 286), (cx - 52, 290)], col)
    p.circ(cx - 64, 292, 12, sk)
    p.rect((cx - 54, 176, cx + 54, 304), col, 28)
    if hair != "hijab":
        p.poly([(cx - 16, 172), (cx + 16, 172), (cx + 10, 190), (cx - 10, 190)], sk, w=3)
    if hair == "old":
        p.line([(cx, 196), (cx, 300)], INK, 3)
        for yy in (214, 244, 274):
            p.circ(cx + 10, yy, 4, (90, 60, 40), None)
    if badge:
        by = 262 if hair == "hijab" else 230
        p.circ(cx, by, 23, WHITE, col, 4)
        p.text((cx, by + 1), badge, 28 if len(badge) < 2 else 20, col)
    if cane:
        p.line([(cx + 76, 290), (cx + 86, 404)], (120, 80, 50), 7)
    if hair == "hijab":
        p.poly([(cx - 64, 120), (cx + 64, 120), (cx + 80, 214), (cx + 40, 226), (cx, 230), (cx - 40, 226),
                (cx - 80, 214)], hc)
        p.circ(cx, 104, 68, hc)
        p.line([(cx - 52, 196), (cx - 30, 214)], _dark(hc), 3)
        p.line([(cx + 52, 196), (cx + 30, 214)], _dark(hc), 3)
        p.ell((cx - 44, 64, cx + 44, 166), sk)
        _face(p, cx, 114, face)
        if arm == "up":
            p.poly([(cx + 50, 196), (cx + 76, 190), (cx + 84, 96), (cx + 60, 92)], col)
            p.circ(cx + 72, 86, 13, sk)
    else:
        _head(p, cx, 110, sk, face, hair=hc, old=hair == "old")
    return p.done()


def _dark(c, k=0.78):
    return tuple(int(v * k) for v in c[:3])


def _face(p, cx, ey, face):
    _head_features(p, cx, ey, face)


# ------------------------------------------------------------------ benda
@lru_cache(maxsize=None)
def cart(label="ES TEH"):
    W_, H_ = 300, 350
    p = Pen(W_, H_)
    p.line([(28, 210), (2, 172)], (90, 96, 110), 8)  # gagang
    p.rect((150 - 5, 70, 150 + 5, 200), (150, 156, 168), 3, w=3)
    # payung belang
    cx, cy = 150, 92
    for k in range(8):
        a0, a1 = 180 + k * 22.5, 180 + (k + 1) * 22.5
        p.d.pieslice(((cx - 136) * S, (cy - 80) * S, (cx + 136) * S, (cy + 80) * S), a0, a1,
                     fill=RED if k % 2 == 0 else WHITE)
    p.d.pieslice(((cx - 136) * S, (cy - 80) * S, (cx + 136) * S, (cy + 80) * S), 180, 360, outline=INK, width=4 * S)
    for k in range(9):
        a = math.radians(180 + k * 22.5)
        p.line([(cx, cy), (cx + 136 * math.cos(a), cy + 80 * math.sin(a))], INK, 2)
    p.circ(cx, cy - 80, 7, RED, w=3)
    # meja + bodi
    p.rect((26, 196, 274, 214), WOOD, 4)
    p.rect((36, 212, 264, 300), (47, 155, 193), 14)
    p.rect((62, 226, 238, 282), CREAM, 10, w=3)
    p.text((150, 255), label, 40, RED)
    # toples teh + gelas
    p.rect((196, 132, 250, 198), (255, 255, 255, 170), 10, w=3)
    p.rect((200, 150, 246, 194), (214, 128, 44), 8, None)
    p.rect((210, 124, 236, 134), (90, 96, 110), 3, w=3)
    for k, x in enumerate((52, 92, 132)):
        cup_draw(p, x, 196, 0.62)
    for x in (88, 212):
        p.circ(x, 312, 32, (46, 52, 64))
        p.circ(x, 312, 11, (190, 196, 206), w=3)
    return p.done()


def cup_draw(p, x, y, s=1.0):
    """gelas es teh, tengah-bawah di (x, y)."""
    w0, w1, h = 30 * s, 22 * s, 64 * s
    p.poly([(x - w0 / 2, y - h), (x + w0 / 2, y - h), (x + w1 / 2, y), (x - w1 / 2, y)], (236, 246, 250), w=3 * s)
    hh = h * 0.78
    p.poly([(x - (w1 + (w0 - w1) * 0.78) / 2 + 2 * s, y - hh), (x + (w1 + (w0 - w1) * 0.78) / 2 - 2 * s, y - hh),
            (x + w1 / 2 - 2 * s, y - 2 * s), (x - w1 / 2 + 2 * s, y - 2 * s)], (214, 128, 44), None)
    p.rect((x - 8 * s, y - hh + 6 * s, x - 1 * s, y - hh + 13 * s), (255, 255, 255, 210), 2, None)
    p.rect((x + 2 * s, y - hh + 14 * s, x + 9 * s, y - hh + 21 * s), (255, 255, 255, 190), 2, None)
    p.d.chord(((x - w0 / 2 - 2 * s) * S, (y - h - 12 * s) * S, (x + w0 / 2 + 2 * s) * S, (y - h + 10 * s) * S), 180, 360,
              fill=WHITE, outline=INK, width=int(3 * s * S))
    p.line([(x + 3 * s, y - h - 6 * s), (x + 10 * s, y - h - 26 * s)], RED, 4 * s)


@lru_cache(maxsize=None)
def cup():
    p = Pen(50, 100)
    cup_draw(p, 25, 96, 1.1)
    return p.done()


@lru_cache(maxsize=None)
def crate(n):
    """keranjang dengan n gelas tersusun (piramida)."""
    W_, H_ = 300, 300
    p = Pen(W_, H_)
    rows, k = [], 0
    per = [6, 5, 4, 3, 2, 1]
    for r, m in enumerate(per):
        for c in range(m):
            if k >= n:
                break
            x = 150 + (c - (m - 1) / 2) * 40
            y = 216 - r * 40
            rows.append((x, y))
            k += 1
    for x, y in rows:
        cup_draw(p, x, y, 0.78)
    p.poly([(22, 196), (278, 196), (256, 290), (44, 290)], WOOD, w=4)
    for yy in (226, 258):
        p.line([(30 + (yy - 196) * 0.16, yy), (270 - (yy - 196) * 0.16, yy)], WOOD_D, 3)
    return p.done()


@lru_cache(maxsize=None)
def money(label="Rp1 jt"):
    p = Pen(150, 84)
    for k, (dx, dy) in enumerate(((10, 18), (5, 9), (0, 0))):
        p.rect((6 + dx, 8 + dy, 136 + dx, 66 + dy), (242, 160, 170), 8, (176, 64, 80), 3)
    p.rect((16, 16, 126, 58), None, 6, (176, 64, 80), 2)
    p.text((71, 37), label, 22, (150, 40, 58))
    return p.done()


@lru_cache(maxsize=None)
def moneybag(label="Rp36 jt"):
    p = Pen(200, 220)
    p.poly([(70, 60), (130, 60), (118, 40), (82, 40)], (176, 128, 84))
    p.ell((20, 56, 180, 214), (196, 146, 96))
    p.line([(70, 62), (130, 62)], INK, 5)
    p.circ(100, 136, 40, AMBER, w=4)
    p.text((100, 137), "Rp", 34, INK)
    p.rect((30, 180, 170, 216), AMBER, 10, w=3)
    p.text((100, 199), label, 24, INK)
    return p.done()


@lru_cache(maxsize=None)
def office(label="KANTOR"):
    p = Pen(220, 330)
    p.rect((14, 30, 206, 326), (126, 155, 181), 6)
    p.rect((4, 18, 216, 36), (96, 120, 146), 4)
    for r in range(6):
        for c in range(4):
            x, y = 34 + c * 42, 52 + r * 40
            p.rect((x, y, x + 28, y + 26), (220, 236, 246), 3, w=3)
    p.rect((88, 284, 132, 326), (80, 98, 120), 3, w=3)
    p.rect((50, 0, 170, 26), CREAM, 8, w=3)
    p.text((110, 13), label, 18, INK)
    return p.done()


@lru_cache(maxsize=None)
def bank():
    p = Pen(380, 330)
    p.poly([(20, 96), (190, 14), (360, 96)], (240, 230, 212))
    p.rect((30, 96, 350, 120), (230, 218, 196), 4)
    p.text((190, 72), "BANK", 34, INK)
    for k in range(5):
        x = 54 + k * 66
        p.rect((x, 120, x + 30, 286), (246, 238, 222), 4, w=4)
    p.rect((40, 286, 340, 306), (230, 218, 196), 4)
    p.rect((20, 304, 360, 326), (214, 200, 176), 4)
    return p.done()


@lru_cache(maxsize=None)
def contract(n=20):
    p = Pen(200, 230)
    for k, (dx, dy) in enumerate(((22, 20), (11, 10), (0, 0))):
        p.rect((10 + dx, 10 + dy, 160 + dx, 200 + dy), WHITE, 8, w=3)
    p.text((85, 40), "KONTRAK", 20, INK)
    for y in (70, 92, 114, 136):
        p.line([(30, y), (140, y)], (180, 180, 186), 4)
    p.circ(124, 170, 18, RED, w=3)
    p.rect((20, 158, 92, 186), AMBER, 8, w=3)
    p.text((56, 172), f"× {n}", 16, INK)
    return p.done()


@lru_cache(maxsize=None)
def sun():
    p = Pen(160, 160)
    for k in range(12):
        a = k * math.pi / 6
        p.line([(80 + 50 * math.cos(a), 80 + 50 * math.sin(a)), (80 + 70 * math.cos(a), 80 + 70 * math.sin(a))],
               (246, 170, 40), 7)
    p.circ(80, 80, 38, (250, 196, 64), (230, 150, 30), 4)
    return p.done()


@lru_cache(maxsize=None)
def qmark():
    p = Pen(110, 130)
    p.ell((6, 6, 104, 96), WHITE, w=4)
    p.poly([(36, 88), (58, 92), (30, 122)], WHITE, None)
    p.line([(36, 90), (30, 120), (58, 94)], INK, 4)
    p.text((55, 50), "?", 62, RED)
    return p.done()


@lru_cache(maxsize=None)
def bubble(txt, width=420, size=34, tail="left"):
    lines = wrap(txt, size, width - 50)
    lh = size * 1.25
    h = int(len(lines) * lh + 46)
    p = Pen(width, h + 40)
    p.rect((4, 4, width - 4, h), WHITE, 26, w=4)
    tx = 60 if tail == "left" else width - 60
    p.poly([(tx - 18, h - 4), (tx + 18, h - 4), (tx - 24 if tail == "left" else tx + 24, h + 34)], WHITE, None)
    p.line([(tx - 18, h - 2), (tx - 24 if tail == "left" else tx + 24, h + 34), (tx + 18, h - 2)], INK, 4)
    for k, ln in enumerate(lines):
        p.text((width / 2, 26 + lh * (k + 0.5)), ln, size, INK)
    return p.done()


def wrap(txt, size, maxw, name="Bold"):
    f = F(size, name)
    out, cur = [], ""
    for w in txt.split():
        t = (cur + " " + w).strip()
        if f.getlength(t) > maxw and cur:
            out.append(cur)
            cur = w
        else:
            cur = t
    if cur:
        out.append(cur)
    return out


@lru_cache(maxsize=None)
def sign(lines, crossed=False):
    """papan kayu. lines: tuple (teks, warna)."""
    W_, H_ = 460, 380
    p = Pen(W_, H_)
    p.rect((220, 150, 240, 376), WOOD_D, 4, w=3)
    p.rect((14, 20, 446, 50 + 72 * len(lines)), (222, 164, 100), 16)
    for k, (t, c) in enumerate(lines):
        y = 62 + k * 72
        p.text((230, y), t, 36, c)
    if crossed:
        f = F(36)
        tw = f.getlength(lines[0][0])
        p.line([(230 - tw / 2 - 12, 64), (230 + tw / 2 + 12, 60)], RED, 7)
    return p.done()


@lru_cache(maxsize=None)
def jar(label="Rp4 jt"):
    p = Pen(200, 240)
    p.rect((30, 30, 170, 234), (226, 242, 248, 220), 26, w=4)
    p.rect((40, 6, 160, 34), (120, 128, 140), 8, w=4)
    for k in range(5):
        p.rect((50 + (k % 2) * 16, 200 - k * 26, 140 + (k % 2) * 6, 222 - k * 26), (242, 160, 170), 5, (176, 64, 80), 3)
    p.rect((20, 92, 180, 132), AMBER, 10, w=3)
    p.text((100, 112), label, 24, INK)
    return p.done()


@lru_cache(maxsize=None)
def calendar(num, head="HARI"):
    p = Pen(250, 270)
    p.rect((8, 8, 242, 262), WHITE, 26, w=5)
    p.d.rounded_rectangle((8 * S, 8 * S, 242 * S, 80 * S), 26 * S, fill=RED, corners=(True, True, False, False))
    p.line([(8, 80), (242, 80)], INK, 5)
    p.rect((8, 8, 242, 262), None, 26, w=5)
    p.text((125, 46), head, 34, WHITE)
    p.text((125, 172), str(num), 92 if len(str(num)) < 4 else 72, INK)
    return p.done()


@lru_cache(maxsize=None)
def icon(kind, r=40):
    p = Pen(2 * r + 8, 2 * r + 8)
    c = r + 4
    if kind == "check":
        p.circ(c, c, r, (40, 150, 90), w=4)
        p.line([(c - r * 0.45, c), (c - r * 0.1, c + r * 0.35), (c + r * 0.5, c - r * 0.35)], WHITE, r * 0.2)
    elif kind == "cross":
        p.circ(c, c, r, RED, w=4)
        p.line([(c - r * 0.38, c - r * 0.38), (c + r * 0.38, c + r * 0.38)], WHITE, r * 0.2)
        p.line([(c - r * 0.38, c + r * 0.38), (c + r * 0.38, c - r * 0.38)], WHITE, r * 0.2)
    elif kind == "cart":
        im = cart().resize((int(2 * r * 0.9), int(2 * r * 0.9 * 350 / 300)), Image.LANCZOS)
        return im
    elif kind == "office":
        return office().resize((int(r * 1.3), int(r * 1.95)), Image.LANCZOS)
    elif kind == "cup":
        p2 = Pen(2 * r, 2 * r)
        cup_draw(p2, r, 2 * r - 4, r / 40)
        return p2.done()
    return p.done()


@lru_cache(maxsize=None)
def gauge():
    p = Pen(420, 300)
    cx, cy, R1, R0 = 210, 220, 190, 120
    cols = [(64, 170, 96), (246, 196, 64), (238, 130, 50), RED]
    for k, c in enumerate(cols):
        p.d.pieslice(((cx - R1) * S, (cy - R1) * S, (cx + R1) * S, (cy + R1) * S), 180 + k * 45, 180 + (k + 1) * 45, fill=c,
                     outline=INK, width=4 * S)
    p.circ(cx, cy, R0, CREAM, w=4)
    p.rect((cx - R0 - 2, cy + 2, cx + R0 + 2, cy + R0 + 4), (0, 0, 0, 0), 0, None)
    p.d.rectangle(((cx - R1 - 6) * S, (cy + 2) * S, (cx + R1 + 6) * S, (cy + R1 + 6) * S), fill=(0, 0, 0, 0))
    p.line([(cx - R1, cy), (cx + R1, cy)], INK, 4)
    p.text((cx, cy + 46), "RISIKO", 38, INK)
    return p.done()


# ------------------------------------------------------------------ kartu teks
@lru_cache(maxsize=None)
def pill(txt, bg=INK, fg=WHITE, size=40, pad=34, icon_kind=None):
    f = F(size)
    tw = f.getlength(txt)
    ic = 0
    if icon_kind:
        ic = size * (1.55 if icon_kind in ("cart", "office") else 1.1)
    w = tw + pad * 2 + ic
    h = size * 1.75
    p = Pen(w + 8, h + 8)
    p.rect((4, 4, w + 4, h + 4), bg, h / 2, None)
    x = 4 + pad + ic
    if icon_kind == "teh":
        cup_draw(p, 4 + pad + ic * 0.35, h * 0.86, size / 62)
    elif icon_kind == "uang":
        bx, by = 4 + pad - 6, h / 2 - size * 0.32
        for k in range(2):
            p.rect((bx + k * 4, by + k * 5, bx + size * 0.95 + k * 4, by + size * 0.55 + k * 5), (242, 160, 170), 4,
                   (176, 64, 80), 2)
    elif icon_kind == "cart":
        pass
    p.text((x + tw / 2, h / 2 + 5), txt, size, fg)
    im = p.done()
    if icon_kind == "cart":
        ci = icon("cart", int(size * 0.8))
        im.alpha_composite(ci, (int(pad * 0.7), int((im.height - ci.height) / 2)))
    if icon_kind == "office":
        ci = icon("office", int(size * 0.62))
        im.alpha_composite(ci, (int(pad * 0.8), int((im.height - ci.height) / 2)))
    return im


def eq_tokens(s):
    """pisah teks persamaan jadi token berwarna."""
    out = []
    for tok in s.split(" "):
        if tok in ("×", "÷", "+", "−", "-", "="):
            out.append((tok, RED))
        else:
            out.append((tok, INK))
    return out


@lru_cache(maxsize=None)
def eqbox(full, shown, result="", size=70, width=None):
    """kotak persamaan: `full` menentukan lebar; `shown` = bagian yang sudah diketik."""
    f = F(size)
    full_txt = full + ((" = " + result) if result else "")
    w = width or int(f.getlength(full_txt) + 90)
    h = int(size * 1.6)
    p = Pen(w + 10, h + 10)
    p.rect((5, 5, w + 5, h + 5), WHITE, 28, w=5)
    x = 50
    toks = eq_tokens(shown)
    if result and shown == full:
        toks += [("=", RED), (result, GREEN)]
    for tok, c in toks:
        if not tok:
            continue
        p.text((x, h / 2 + 7), tok, size, c, anchor="lm")
        x += f.getlength(tok + " ")
    return p.done()


@lru_cache(maxsize=None)
def resultbox(txt, size=96):
    f = F(size)
    w = int(f.getlength(txt) + 110)
    h = int(size * 1.55)
    p = Pen(w + 10, h + 10)
    p.rect((5, 5, w + 5, h + 5), AMBER, 26, w=5)
    p.text((w / 2 + 5, h / 2 + 11), txt, size, INK)
    return p.done()


@lru_cache(maxsize=None)
def stamp(txt, col=(46, 140, 112), size=52):
    f = F(size)
    w = int(f.getlength(txt) + 70)
    h = int(size * 1.7)
    p = Pen(w + 40, h + 40)
    p.rect((20, 20, w + 20, h + 20), (255, 255, 255, 120), 16, col, 6)
    p.rect((30, 30, w + 10, h + 10), None, 10, col, 3)
    p.text((w / 2 + 20, h / 2 + 26), txt, size, col)
    im = p.done()
    rnd = random.Random(hash(txt) & 0xffff)
    m = Image.new("L", im.size, 255)
    md = ImageDraw.Draw(m)
    for _ in range(int(w * h / 260)):
        x, y = rnd.uniform(0, im.width), rnd.uniform(0, im.height)
        r = rnd.uniform(1, 3.5)
        md.ellipse((x - r, y - r, x + r, y + r), fill=rnd.randint(0, 120))
    a = Image.fromarray(np.minimum(np.asarray(im.getchannel("A")),
                                                    np.asarray(m)))
    im.putalpha(a)
    return im.rotate(6, resample=Image.BICUBIC, expand=True)


@lru_cache(maxsize=None)
def label_tag(txt, col=INK):
    f = F(24)
    w = int(f.getlength(txt) + 34)
    p = Pen(w + 6, 46)
    p.rect((3, 3, w + 3, 43), col, 12, None)
    p.text((w / 2 + 3, 25), txt, 24, WHITE)
    return p.done()


@lru_cache(maxsize=None)
def price_tag(txt):
    f = F(34)
    w = int(f.getlength(txt) + 56)
    p = Pen(w + 10, 74)
    p.poly([(5, 37), (30, 6), (w + 5, 6), (w + 5, 68), (30, 68)], AMBER, w=4)
    p.circ(30, 37, 7, CREAM, w=3)
    p.text((w / 2 + 22, 39), txt, 34, INK)
    return p.done()


@lru_cache(maxsize=None)
def numcircle(n, col):
    p = Pen(104, 104)
    p.circ(52, 52, 46, col, w=5)
    p.text((52, 55), str(n), 50, WHITE)
    return p.done()


@lru_cache(maxsize=None)
def envelope(amount="Rp5 jt", label="GAJI"):
    p = Pen(230, 160)
    p.rect((8, 8, 222, 152), (222, 178, 116), 12)
    p.line([(10, 12), (115, 82), (220, 12)], (170, 120, 70), 4)
    p.rect((40, 92, 190, 144), WHITE, 10, w=3)
    p.text((115, 108), label, 20, (120, 96, 80))
    p.text((115, 130), amount, 24, GREEN)
    return p.done()


@lru_cache(maxsize=None)
def bags():
    p = Pen(250, 220)
    for (x0, col, w_, h_) in ((20, (236, 120, 150), 120, 150), (120, (52, 170, 160), 110, 130)):
        y0 = 210 - h_
        p.arc((x0 + w_ * 0.25, y0 - 40, x0 + w_ * 0.75, y0 + 30), 180, 360, INK, 6)
        p.poly([(x0, y0), (x0 + w_, y0), (x0 + w_ - 8, 210), (x0 + 8, 210)], col)
        p.circ(x0 + w_ / 2, y0 + h_ * 0.45, 16, WHITE, w=3)
    return p.done()


@lru_cache(maxsize=None)
def phone(label="CICILAN"):
    p = Pen(130, 230)
    p.rect((10, 6, 120, 224), (52, 58, 72), 20)
    p.rect((20, 26, 110, 196), (120, 200, 230), 8, None)
    p.rect((28, 90, 102, 130), WHITE, 8, w=3)
    p.text((65, 110), label, 14, RED)
    p.circ(65, 210, 7, (90, 96, 110), None)
    return p.done()


@lru_cache(maxsize=None)
def laptop(label="TOKO ONLINE"):
    p = Pen(300, 220)
    p.rect((40, 10, 260, 160), (52, 58, 72), 12)
    p.rect((52, 22, 248, 148), WHITE, 6, None)
    p.rect((52, 22, 248, 50), (36, 128, 82), 6, None)
    p.text((150, 37), label, 18, WHITE)
    for k in range(3):
        x = 70 + k * 62
        p.rect((x, 62, x + 48, 110), (250, 238, 214), 6, w=2)
        p.rect((x, 116, x + 48, 130), AMBER, 4, None)
    p.poly([(10, 166), (290, 166), (270, 204), (30, 204)], (190, 196, 206))
    return p.done()


@lru_cache(maxsize=None)
def cert(label="SERTIFIKAT"):
    p = Pen(260, 220)
    p.rect((10, 10, 250, 190), (255, 250, 236), 10, w=4)
    p.rect((22, 22, 238, 178), None, 6, AMBER, 3)
    p.text((130, 52), label, 24, INK)
    for y in (88, 110):
        p.line([(50, y), (210, y)], (190, 186, 176), 4)
    p.poly([(176, 150), (192, 214), (204, 190), (218, 214), (216, 150)], RED)
    p.circ(196, 148, 26, AMBER, w=4)
    pts = []
    for k in range(10):
        r = 15 if k % 2 == 0 else 6.5
        a = -math.pi / 2 + k * math.pi / 5
        pts.append((196 + r * math.cos(a), 148 + r * math.sin(a)))
    p.poly(pts, WHITE, None)
    return p.done()


@lru_cache(maxsize=None)
def arrow(col=GREEN, length=160):
    p = Pen(length + 20, 90)
    p.poly([(10, 32), (length - 40, 32), (length - 40, 10), (length + 10, 45), (length - 40, 80), (length - 40, 58),
            (10, 58)], col)
    return p.done()


@lru_cache(maxsize=None)
def parcel(label="ONGKIR"):
    p = Pen(230, 200)
    p.poly([(20, 60), (115, 30), (210, 60), (115, 92)], (226, 180, 120))
    p.poly([(20, 60), (115, 92), (115, 194), (20, 160)], (206, 156, 96))
    p.poly([(210, 60), (115, 92), (115, 194), (210, 160)], (190, 140, 84))
    p.poly([(62, 47), (157, 77), (157, 110), (62, 78)], (240, 224, 196), w=2)
    p.rect((130, 120, 200, 150), WHITE, 6, w=3)
    p.text((165, 135), label, 13, INK)
    return p.done()
