"""Set kamar kos (orisinal) + tekstur 2D (layar laptop, HP, langit jendela, jam, poster).

Koordinat dunia (cm): lantai y=0, dinding jendela z=-110 (menghadap +z), dinding belakang z=+170.
Meja: permukaan y=74, x -75..75, z -105..-45. Nara duduk di z=-8 menghadap -z.
"""
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from cg import Part, R, Sc, T, chain, quad, rbox, sphere, superellipsoid, tube

FD = Path(__file__).resolve().parents[2] / "assets" / "fonts"
TEAL = (15, 118, 110)
_M, _F, _TX = {}, {}, {}


def mesh(key, fn):
    if key not in _M:
        _M[key] = fn()
    return _M[key]


def F(name, size):
    k = (name, size)
    if k not in _F:
        _F[k] = ImageFont.truetype(str(FD / f"Poppins-{name}.ttf"), size)
    return _F[k]


def tex(key, fn):
    if key not in _TX:
        if len(_TX) > 80:
            _TX.clear()
        _TX[key] = fn()
    return key, _TX[key]


# ---------------------------------------------------------------- tekstur
def sky_img(day):
    w, h = 512, 384
    y = np.linspace(0, 1, h)[:, None, None]
    night = np.array((16, 20, 52)) * (1 - y) + np.array((60, 46, 98)) * y
    morn = np.array((120, 186, 236)) * (1 - y) + np.array((255, 214, 170)) * y
    a = (night * (1 - day) + morn * day) * np.ones((1, w, 1))
    im = Image.fromarray(a.clip(0, 255).astype(np.uint8))
    d = ImageDraw.Draw(im, "RGBA")
    rng = np.random.default_rng(4)
    if day < 0.9:
        for _ in range(60):
            x, yy = rng.uniform(0, w), rng.uniform(0, h * 0.6)
            v = int(255 * (1 - day))
            d.point((x, yy), fill=(255, 255, 230, v))
        mx, my = 150, 90
        d.ellipse((mx - 30, my - 30, mx + 30, my + 30), fill=(250, 240, 200, int(255 * (1 - day))))
    if day > 0.1:
        sx, sy = 360, 300 - 120 * day
        for r, a_ in ((90, 40), (55, 90), (30, 220)):
            d.ellipse((sx - r, sy - r, sx + r, sy + r), fill=(255, 236, 180, int(a_ * day)))
        for cx, cy, s in ((120, 120, 1.0), (330, 80, 0.8), (430, 160, 0.7)):
            for dx, dy, r in ((0, 0, 28), (30, 6, 22), (-28, 8, 20), (12, -14, 20)):
                d.ellipse((cx + dx * s - r * s, cy + dy * s - r * s, cx + dx * s + r * s, cy + dy * s + r * s),
                          fill=(255, 255, 255, int(200 * day)))
    # siluet kota
    bx = 0
    while bx < w:
        bw, bh = rng.integers(30, 70), rng.integers(40, 120)
        col = tuple(int(c) for c in (np.array((14, 14, 34)) * (1 - day) + np.array((150, 170, 200)) * day))
        d.rectangle((bx, h - bh, bx + bw - 4, h), fill=col)
        if day < 0.6:
            for wy in range(h - bh + 8, h - 6, 14):
                for wx in range(bx + 6, bx + bw - 10, 12):
                    if rng.random() < 0.4:
                        d.rectangle((wx, wy, wx + 5, wy + 6), fill=(255, 210, 130, int(255 * (1 - day / 0.6))))
        bx += bw
    return im.filter(ImageFilter.GaussianBlur(1.2))


def doc_img(blink):
    im = Image.new("RGB", (640, 400), (236, 238, 242))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, 640, 34), fill=(60, 64, 76))
    d.rectangle((150, 50, 490, 400), fill=(255, 255, 255))
    d.text((320, 92), "BAB 2", font=F("Bold", 26), fill=(30, 30, 40), anchor="mm")
    d.text((320, 124), "TINJAUAN PUSTAKA", font=F("Bold", 22), fill=(30, 30, 40), anchor="mm")
    if blink:
        d.rectangle((180, 160, 183, 186), fill=(30, 30, 40))
    return im


def app_img(p):
    im = Image.new("RGB", (640, 400), (240, 250, 248))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, 640, 58), fill=TEAL)
    d.text((24, 29), "Dosenku", font=F("Bold", 30), fill=(255, 255, 255), anchor="lm")
    d.rounded_rectangle((470, 14, 620, 44), 15, fill=(20, 150, 138))
    d.text((545, 29), "Bimbingan", font=F("Medium", 16), fill=(255, 255, 255), anchor="mm")
    d.text((30, 90), "Kerangka Bab 2", font=F("Bold", 28), fill=(20, 30, 40), anchor="lm")
    rows = ["2.1 Landasan teori", "2.2 Penelitian terdahulu", "Rujukan ber-DOI: 12", "Siap bimbingan"]
    for i, r in enumerate(rows):
        q = min(1.0, max(0.0, p * 5 - i))
        if q <= 0:
            break
        y = 140 + i * 62
        d.rounded_rectangle((30, y, 30 + int(580 * q), y + 48), 14, fill=(255, 255, 255), outline=(200, 230, 225), width=2)
        if q >= 1:
            d.text((52, y + 24), r, font=F("Medium", 22), fill=(30, 40, 50), anchor="lm")
            d.ellipse((560, y + 10, 588, y + 38), fill=TEAL)
            d.line((567, y + 24, 573, y + 31, 582, y + 17), fill=(255, 255, 255), width=4)
    return im


def phone_img(on, clock="07.12"):
    im = Image.new("RGB", (360, 720), (10, 12, 18))
    if not on:
        return im
    y = np.linspace(0, 1, 720)[:, None, None]
    a = (np.array((40, 80, 120)) * (1 - y) + np.array((240, 170, 140)) * y) * np.ones((1, 360, 1))
    im = Image.fromarray(a.astype(np.uint8))
    d = ImageDraw.Draw(im)
    d.text((180, 150), clock, font=F("Medium", 76), fill=(255, 255, 255), anchor="mm")
    d.rounded_rectangle((16, 290, 344, 440), 26, fill=(250, 250, 252))
    d.ellipse((32, 312, 84, 364), fill=(109, 91, 208))
    d.text((58, 338), "PH", font=F("Bold", 20), fill=(255, 255, 255), anchor="mm")
    d.text((98, 324), "Pak Hendra (Dosbing)", font=F("Bold", 19), fill=(20, 24, 32), anchor="lm")
    d.text((98, 352), "sekarang", font=F("Regular", 15), fill=(120, 126, 140), anchor="lm")
    d.text((36, 392), "Bagus. Lanjut Bab 3.", font=F("Medium", 27), fill=(20, 24, 32), anchor="lm")
    return im


def clock_img():
    im = Image.new("RGB", (256, 256), (250, 248, 240))
    d = ImageDraw.Draw(im)
    d.ellipse((4, 4, 252, 252), outline=(60, 60, 70), width=10)
    for k in range(12):
        a = k * math.pi / 6
        d.line((128 + 100 * math.sin(a), 128 - 100 * math.cos(a), 128 + 112 * math.sin(a), 128 - 112 * math.cos(a)), fill=(60, 60, 70), width=6)
    return im


def poster_img(seed, title):
    rng = np.random.default_rng(seed)
    base = [(250, 214, 120), (140, 200, 220), (240, 160, 170)][seed % 3]
    im = Image.new("RGB", (300, 420), base)
    d = ImageDraw.Draw(im)
    for _ in range(6):
        x, y, r = rng.uniform(0, 300), rng.uniform(0, 300), rng.uniform(30, 90)
        c = tuple(int(v) for v in rng.uniform(80, 255, 3))
        d.ellipse((x - r, y - r, x + r, y + r), fill=c)
    d.rectangle((0, 330, 300, 420), fill=(30, 34, 48))
    d.text((150, 375), title, font=F("Bold", 34), fill=(255, 255, 255), anchor="mm")
    return im


# ---------------------------------------------------------------- set
WOOD = (176, 122, 78)
WALL = (232, 210, 186)
WALL2 = (214, 196, 176)


def room(ws, t):
    """ws: day (0..1), lamp (0..1), screen ('doc'/'app'/'off'), app_p, phone (0/1), clock_h (jam desimal), crumpled (0..1)."""
    far, near = [], []
    day = ws["day"]
    # dinding & lantai
    hide = ws.get("hide_front", False)
    if not hide:
        far.append(Part(mesh("wallF", lambda: rbox(360, 280, 6, 0.04, 20)), WALL, T(0, 140, -113), 1, bump=0.02))
    far.append(Part(mesh("wallB", lambda: rbox(360, 280, 6, 0.04, 20)), WALL2, T(0, 140, 173), 2, bump=0.02))
    far.append(Part(mesh("wallL", lambda: rbox(6, 280, 300, 0.04, 20)), WALL2, T(-173, 140, 30), 3, bump=0.02))
    far.append(Part(mesh("wallR", lambda: rbox(6, 280, 300, 0.04, 20)), WALL, T(173, 140, 30), 4, bump=0.02))
    near.append(Part(mesh("floor", lambda: rbox(360, 6, 300, 0.04, 20)), (150, 104, 70), T(0, -3, 30), 5, bump=0.05))
    near.append(Part(mesh("rug", lambda: superellipsoid(70, 0.6, 50, 1, 0.4, 40, 10)), (90, 120, 140), T(10, 0.5, 20), 6, bump=0.3))
    # jendela
    win = []
    win.append(Part(mesh("winframe", lambda: rbox(124, 94, 8, 0.12, 16)), (248, 246, 240), T(0, 160, -110), 7))
    sky = tex(("sky", round(day * 20)), lambda: sky_img(round(day * 20) / 20))
    win.append(Part(mesh("winsky", lambda: quad(112, 82)), (255, 255, 255), T(0, 160, -105.5), 8, emit=1.0, cast=False, tex=sky))
    win.append(Part(mesh("winbarV", lambda: rbox(4, 82, 3, 0.3, 10)), (248, 246, 240), T(0, 160, -104), 9, cast=False))
    win.append(Part(mesh("winbarH", lambda: rbox(112, 4, 3, 0.3, 10)), (248, 246, 240), T(0, 160, -104), 9, cast=False))
    for side in (-1, 1):
        cur = mesh("curtain", lambda: superellipsoid(16, 60, 6, 1, 0.5, 40, 30))
        win.append(Part(cur, (236, 150, 150), T(side * 76, 150, -102), 10, bump=0.25))
    # jam dinding
    ck = tex("clock", clock_img)
    win.append(Part(mesh("clockbody", lambda: superellipsoid(16, 16, 2.5, 1, 1, 40, 14)), (60, 60, 70), T(-110, 175, -108), 11))
    win.append(Part(mesh("clockface", lambda: quad(28, 28)), (255, 255, 255), T(-110, 175, -105.2), 12, cast=False, tex=ck, emit=0.15))
    h = ws["clock_h"]
    for ln, ang, w in ((8, (h % 12) / 12 * 360, 1.0), (11.5, (h % 1) * 360, 0.6)):
        hand = mesh(("hand", ln), lambda ln=ln, w=w: tube([(0, 0, 0), (0, ln, 0)], w, 8, smooth=False))
        win.append(Part(hand, (30, 30, 40), chain(T(-110, 175, -104.6), R("z", -ang)), 13, cast=False))
    if not hide:
        far += win
    # poster & rak di dinding belakang
    for k, (x, ttl) in enumerate(zip((-70, 60), ws.get("posters", ("SEMANGAT", "SIDANG 2027")))):
        pt = tex(("poster", k, ttl), lambda k=k, ttl=ttl: poster_img(k, ttl))
        far.append(Part(mesh("poster", lambda: quad(42, 59)), (255, 255, 255), chain(T(x, 165, 169.5), R("y", 180)), 14, cast=False, tex=pt))
    far.append(Part(mesh("shelfB", lambda: rbox(80, 3, 22, 0.2, 12)), WOOD, T(-10, 115, 160), 15))
    rng = np.random.default_rng(2)
    x = -45
    for k in range(10):
        bw, bh = rng.uniform(5, 8), rng.uniform(20, 28)
        far.append(Part(mesh(("bookB", k), lambda bw=bw, bh=bh: rbox(bw, bh, 18, 0.15, 10)),
                        [(196, 80, 80), (80, 130, 180), (230, 180, 80), (110, 160, 110)][k % 4], T(x, 116.5 + bh / 2, 160), 16))
        x += bw + 1
    # lampu tumblr di dinding belakang
    for k in range(18):
        lx = -150 + k * 17
        ly = 215 + 8 * math.sin(k * 0.9)
        on = 0.6 + 0.4 * math.sin(t * 2 + k)
        far.append(Part(mesh("bulbS", lambda: sphere(1.6, 10)), [(255, 200, 120), (255, 150, 150), (150, 210, 255)][k % 3],
                        T(lx, ly, 168), 17, emit=2.0 * on * (1 - 0.6 * day), cast=False))
    # kasur di belakang kiri
    far.append(Part(mesh("bed", lambda: rbox(100, 40, 190, 0.18, 20)), (240, 236, 228), T(-115, 20, 90), 18, bump=0.05))
    far.append(Part(mesh("blanket", lambda: superellipsoid(52, 9, 70, 0.6, 0.6, 40, 20)), (120, 150, 200), T(-112, 42, 110), 19, bump=0.25))
    far.append(Part(mesh("pillow", lambda: superellipsoid(30, 8, 18, 0.5, 0.5, 30, 16)), (250, 236, 210), T(-112, 46, 0), 20))
    # meja
    near.append(Part(mesh("desk", lambda: rbox(150, 5, 60, 0.08, 20)), WOOD, T(0, 71.5, -75), 21, bump=0.05))
    for x in (-70, 70):
        for z in (-100, -50):
            near.append(Part(mesh("leg", lambda: rbox(5, 70, 5, 0.3, 8)), (150, 100, 64), T(x, 35, z), 22))
    # kursi (di belakang Nara)
    near.append(Part(mesh("seat", lambda: rbox(46, 7, 44, 0.3, 16)), (60, 66, 80), T(0, 44, -10), 23))
    near.append(Part(mesh("back", lambda: rbox(42, 46, 6, 0.3, 16)), (60, 66, 80), chain(T(0, 74, 14), R("x", -8)), 24))
    near.append(Part(mesh("pole", lambda: tube([(0, 0, 0), (0, 40, 0)], 2.4, 10, smooth=False)), (40, 40, 46), T(0, 2, -10), 25))
    # laptop
    near.append(Part(mesh("lbase", lambda: rbox(34, 2, 23, 0.2, 14)), (186, 190, 200), T(0, 75, -62), 26, gloss=0.3))
    near.append(Part(mesh("lkeys", lambda: rbox(30, 0.4, 10, 0.3, 10)), (70, 74, 86), T(0, 76.1, -66), 26))
    LM = chain(T(0, 75.5, -73), R("x", -12), T(0, 11.5, 0))
    near.append(Part(mesh("llid", lambda: rbox(34, 23, 1.2, 0.15, 14)), (186, 190, 200), LM, 27, gloss=0.3))
    scr = ws["screen"]
    if isinstance(scr, tuple):
        stex = scr
    elif scr == "doc":
        stex = tex(("doc", int(t * 2) % 2), lambda: doc_img(int(t * 2) % 2 == 0))
    elif scr == "app":
        q = round(ws["app_p"] * 30)
        stex = tex(("app", q), lambda: app_img(q / 30))
    else:
        stex = None
    if stex:
        near.append(Part(mesh("lscr", lambda: quad(31, 20)), (255, 255, 255), chain(LM, T(0, 0.3, 0.7)), 28, emit=1.0, cast=False,
                         tex=stex))
    else:
        near.append(Part(mesh("lscr0", lambda: quad(31, 20)), (20, 22, 30), chain(LM, T(0, 0.3, 0.7)), 28, gloss=0.6, cast=False))
    # lampu meja
    near.append(Part(mesh("lampbase", lambda: superellipsoid(9, 2, 9, 0.5, 1, 30, 12)), (70, 130, 120), T(-55, 76, -88), 29))
    near.append(Part(mesh("lamparm", lambda: tube([(0, 0, 0), (2, 30, -2), (14, 46, 4)], 1.3, 10)), (70, 130, 120), T(-55, 77, -88), 30))
    near.append(Part(mesh("lampshade", lambda: superellipsoid(11, 7, 11, 0.5, 1, 30, 16)), (80, 150, 136), chain(T(-38, 120, -80), R("z", -35)), 31))
    near.append(Part(mesh("lampbulb", lambda: sphere(3.5, 16)), (255, 230, 170), T(-36, 114, -78), 32, emit=3.0 * ws["lamp"], cast=False))
    # kopi, buku, kertas, HP
    near.append(Part(mesh("mug", lambda: superellipsoid(4.5, 5.5, 4.5, 0.3, 1, 30, 20)), (236, 236, 228), T(42, 79.5, -66), 33, gloss=0.4))
    near.append(Part(mesh("coffee", lambda: superellipsoid(3.9, 0.3, 3.9, 0.5, 1, 24, 8)), (80, 46, 30), T(42, 84.4, -66), 34, gloss=0.5))
    for k, c in enumerate(((196, 80, 80), (80, 130, 180), (230, 180, 80))):
        near.append(Part(mesh(("deskbook", k), lambda: rbox(24, 3.2, 17, 0.15, 10)), c, chain(T(-48, 75.6 + k * 3.3, -60), R("y", 8 * k - 6)), 35))
    # gumpalan kertas: posisi tetap, tidak menyentuh HP/mug/laptop/kertas
    for k, (x, z) in enumerate(((-30, -52), (-64, -73), (56, -50), (60, -96), (-24, -100), (50, -84))):
        if k < round(ws["crumpled"] * 6):
            cp = mesh(("crumple", k), lambda k=k: sphere(4, 14).lumpy(0.9, k, 0.6))
            near.append(Part(cp, (248, 246, 238), T(x, 78, z), 36))
    # tumpukan kertas di kanan belakang (jauh dari HP)
    for k in range(4):
        near.append(Part(mesh("paper", lambda: rbox(21, 0.3, 29, 0.1, 8)), (252, 252, 248),
                         chain(T(29 + k * 1.2, 74.3 + k * 0.32, -91 + k * 1.5), R("y", 8 - k * 6)), 37))
    near.append(Part(mesh("phone", lambda: rbox(8, 1.0, 16, 0.25, 12)), (30, 32, 40), chain(T(28, 74.6, -54), R("y", -15)), 38, gloss=0.5))
    if isinstance(ws.get("phone_tex"), tuple):
        pt = ws["phone_tex"]
    else:
        pt = tex(("phone", int(ws["phone"])), lambda: phone_img(ws["phone"] > 0))
    near.append(Part(mesh("phonescr", lambda: quad(7.2, 14.6)), (255, 255, 255), chain(T(28, 75.16, -54), R("y", -15), R("x", -90)), 39,
                     emit=1.0 if ws["phone"] else 0.0, cast=False, tex=pt))
    return far, near
