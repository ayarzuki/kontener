"""Cerita: Sejarah daftar pustaka -> Dosenku (rujukan ber-DOI yang bisa dicek).

Setiap fungsi menggambar satu adegan di kanvas logis 1240 x 2204.
Zona aman: label judul di atas (y < 330) dan subtitle di bawah (y > 1700) -> isi utama di y 330..1690.
"""
import math
import random

from ink import (C, CARDO_B, CARDO_I, Iso, book, capsule, ellipse, iso_box, paper_slip, person, rect, rot, rrect)
from props import (FLOOR, TEAL, WALL, WOOD, WOOD_D, check_stamp, column, draft_stack, ghost_slip, laptop_front,
                   magnifier, pipe, room, scissors, wall_shelf, window)

BOOKS = [C(150, 50, 40), C(60, 90, 70), C(170, 120, 50), C(120, 80, 50), C(70, 70, 110)]


def desk(c, iso, x, z, w=230, d=140, h=120):
    iso_box(c, iso, x, h, z, w, 20, d, WOOD)
    for lx, lz in ((x + 6, z + 6), (x + w - 18, z + 6), (x + 6, z + d - 18), (x + w - 18, z + d - 18)):
        iso_box(c, iso, lx, 0, lz, 12, h, 12, WOOD_D, outline=2.0)


def book_pile(c, iso, x, z, n, seed):
    r = random.Random(seed)
    yy = 0
    for _ in range(n):
        th = r.uniform(14, 22)
        iso_box(c, iso, x + r.uniform(-6, 6), yy, z + r.uniform(-6, 6), 70, th, 52, r.choice(BOOKS), outline=2.0)
        yy += th


def crumpled(c, x, y, s=1.0, seed=0):
    r = random.Random(seed)
    pts = [(x + (18 + r.uniform(-5, 5)) * s * math.cos(a), y + (15 + r.uniform(-5, 5)) * s * math.sin(a))
           for a in [k * 2 * math.pi / 9 for k in range(9)]]
    c.shape(pts, C(240, 234, 214), opacity=0.5, outline=2.0)
    for _ in range(3):
        c.line([(x + r.uniform(-12, 12) * s, y + r.uniform(-10, 10) * s), (x + r.uniform(-12, 12) * s, y + r.uniform(-10, 10) * s)],
               width=1.4, alpha=0.6)


def emblem(c, x, y, s=1.0):
    """Lambang buku terbuka bertinta teal (ilustrasi, bukan logo resmi)."""
    for side in (-1, 1):
        pg = [(x, y - 70 * s), (x + side * 150 * s, y - 100 * s), (x + side * 160 * s, y + 70 * s), (x, y + 95 * s)]
        c.shape(pg, C(246, 240, 222), opacity=0.55, outline=3.2 * s)
        for k in range(4):
            yy = y - 50 * s + k * 34 * s
            c.line([(x + side * 24 * s, yy), (x + side * 128 * s, yy - 18 * s + k * 2 * s)], width=1.8 * s, alpha=0.55)
    c.shape([(x - 172 * s, y + 80 * s), (x, y + 110 * s), (x + 172 * s, y + 80 * s), (x + 160 * s, y + 70 * s), (x, y + 95 * s),
             (x - 160 * s, y + 70 * s)], TEAL, opacity=0.9, outline=2.8 * s)
    c.line([(x, y - 70 * s), (x, y + 100 * s)], width=3 * s)


# ================================================================ adegan
def hook(c):
    iso = Iso(594, 990, 1.2)
    room(c, iso, 520, 470, 520, wall=C(196, 196, 212), floor=C(150, 112, 76))
    P = iso.p
    window(c, iso, 140, 290, 250, 430, "r", sky=C(56, 64, 110))
    mx, my = P(250, 395, 0)
    c.shape(ellipse(mx, my, 24, 24, n=24), C(250, 236, 190), opacity=0.9, outline=2.2)
    c.shape(ellipse(mx + 12, my - 6, 20, 20, n=24), C(56, 64, 110), opacity=0.9, outline=0, clear=False)
    for sx, sy in ((170, 300), (190, 390), (270, 290), (160, 410)):
        x, y = P(sx, sy, 0)
        c.shape(ellipse(x, y, 3, 3, n=8), C(250, 240, 200), opacity=1.0, outline=1.2, clear=False)
    # meja di dinding kanan + lampu
    desk(c, iso, 290, 110, w=210, d=150)
    lx, ly = P(470, 141, 130)
    c.line([(lx, ly - 82), (lx, ly)], width=4)
    c.shape([(lx - 30, ly - 80), (lx + 30, ly - 80), (lx + 16, ly - 122), (lx - 16, ly - 122)], C(60, 110, 90), outline=2.4)
    c.wash(c.mask(ellipse(lx - 60, ly - 30, 190, 120), blur=30), C(255, 222, 140), opacity=0.32, gran=0.05, edge=0)
    dx_, dy_ = P(370, 141, 190)
    for k in range(10):
        paper_slip(c, dx_ - 26 + (k % 3) * 24, dy_ - 6 - k * 10, 92, 54, angle=-12 + (k * 7) % 24)
    # mesin "AI" di dinding kiri
    iso_box(c, iso, 10, 0, 250, 150, 330, 170, C(120, 132, 122), hatch_side=True)
    fx, fy = P(85, 200, 420)
    c.shape(rrect(fx - 60, fy - 44, fx + 60, fy + 30, 10), C(170, 214, 202), opacity=0.6, outline=2.6)
    c.text((fx, fy - 8), "AI", size=42, path=CARDO_B)
    gx, gy = P(85, 105, 420)
    for dx in (-38, 0, 38):
        c.shape(ellipse(gx + dx, gy, 14, 14, n=18), C(236, 222, 180), outline=2.2)
        c.line([(gx + dx, gy), (gx + dx + 7, gy - 9)], width=2)
    tx, ty = P(85, 330, 335)
    c.shape(ellipse(tx, ty - 4, 46, 24), C(200, 120, 60), outline=2.6)
    # pipa melengkung dari mesin ke atas meja, memuntahkan kertas
    pipe(c, [(tx, ty - 8), (tx + 20, ty - 160), (tx + 200, ty - 250), (dx_ + 30, ty - 230), (dx_ + 40, dy_ - 230)], r=17)
    ex, ey = dx_ + 40, dy_ - 215
    for k, (ax, ay, an) in enumerate(((-50, 20, -30), (40, 40, 20), (-10, 70, -8), (70, 0, 35))):
        paper_slip(c, ex + ax, ey + ay, 66, 42, angle=an, lines=2)
    for k, (fx_, fz) in enumerate(((210, 330), (300, 440), (470, 420), (420, 300))):
        x, y = P(fx_, 0, fz)
        crumpled(c, x, y - 12, 1.0, k)
    # mahasiswa bingung
    iso_box(c, iso, 300, 0, 330, 76, 66, 76, WOOD_D, outline=2.0)
    px, py = P(338, 0, 368)
    person(c, px + 4, py - 30, s=1.45, shirt=C(238, 238, 232), pants=C(50, 55, 70), hair="bowl", pose="sit",
           arms=((-56, 6), "down"), mouth="o")
    for k, (qx, qy, sz) in enumerate(((px + 70, py - 450, 130), (px + 160, py - 530, 100), (px - 10, py - 540, 80))):
        c.text((qx, qy), "?", size=sz, path=CARDO_B, angle=(k - 1) * 12)


def gulungan(c):
    cx, cy, s = 620, 1020, 1.5
    c.wash(c.mask(ellipse(cx + 20, cy + 120 * s, 330 * s, 40 * s, n=40), blur=24), C(110, 80, 50), opacity=0.35, gran=0.2, edge=0)
    body = rrect(cx - 250 * s, cy - 68 * s, cx + 250 * s, cy + 68 * s, 58 * s)
    c.shape(body, C(232, 212, 166), opacity=0.75, outline=3.4, shade=0.6, hatch=dict(spacing=7, angle=-80, alpha=0.18))
    for k in range(-3, 4):
        c.line([(cx - 190 * s, cy + k * 16 * s), (cx + 190 * s - abs(k) * 10 * s, cy + k * 16 * s)], width=1.3, alpha=0.32)
    for side in (-1, 1):
        ex = cx + side * 250 * s
        c.shape(ellipse(ex, cy, 40 * s, 70 * s, n=32), C(206, 180, 134), outline=3.4, shade=0.4)
        for r_ in (28, 17):
            c.outline(ellipse(ex, cy, r_ * s * 0.57, r_ * s, n=20), width=1.6, alpha=0.6)
        c.shape(ellipse(ex, cy, 8 * s, 14 * s, n=14), C(110, 80, 50), outline=2.0)
    c.line([(cx + 140 * s, cy + 58 * s), (cx + 190 * s, cy + 150 * s), (cx + 205 * s, cy + 190 * s)], width=2.6)
    tag = rot(rect(cx + 120 * s, cy + 190 * s, cx + 290 * s, cy + 262 * s), 10, cx + 205 * s, cy + 190 * s)
    c.shape(tag, C(222, 194, 146), outline=2.8)
    c.text((cx + 208 * s, cy + 232 * s), "ΠΙΝΑΚΕΣ", size=40, path=CARDO_B, angle=-10)


def aleksandria(c):
    c.shape(rect(40, 330, 1200, 1390), C(214, 196, 160), opacity=0.6, outline=3, shade=0.35)
    x0, y0, x1, y1 = 170, 430, 1070, 1090
    cols, rows = 9, 8
    c.shape(rect(x0 - 22, y0 - 22, x1 + 22, y1 + 22), WOOD, outline=3)
    cw, ch = (x1 - x0) / cols, (y1 - y0) / rows
    r = random.Random(3)
    for i in range(cols):
        for j in range(rows):
            bx, by = x0 + i * cw, y0 + j * ch
            c.shape(rect(bx + 4, by + 4, bx + cw - 4, by + ch - 4), C(86, 60, 40), opacity=0.85, outline=2.0)
            for k in range(r.randint(2, 4)):
                ex = bx + 22 + (k % 2) * 40 + r.uniform(-4, 4)
                ey = by + ch - 22 - (k // 2) * 28
                c.shape(ellipse(ex, ey, 15, 15, n=16), C(236, 218, 176), opacity=0.8, outline=1.8)
                c.outline(ellipse(ex, ey, 5, 5, n=8), width=1.4)
            if r.random() < 0.35:
                c.shape(rect(bx + 10, by + ch - 60, bx + 42, by + ch - 44), C(200, 168, 118), outline=1.4)
    for x in (100, 1140):
        column(c, x, 330, 1390, w=74)
    c.shape(rect(0, 1390, 1240, 2204), C(196, 170, 130), opacity=0.7, outline=3, shade=0.3)
    for k in range(1, 12):
        c.line([(0, 1390 + k * 70), (1240, 1390 + k * 70)], width=1.4, alpha=0.45)
    # meja tulis + juru tulis
    c.shape(rect(470, 1400, 960, 1440), WOOD, outline=3)
    for x in (490, 930):
        c.shape(rect(x, 1440, x + 18, 1600), WOOD_D, outline=2.4)
    paper_slip(c, 690, 1384, 170, 38, angle=-3, lines=2, col=C(236, 220, 180))
    c.shape(rect(720, 1520, 860, 1600), WOOD_D, outline=2.4)
    person(c, 790, 1600, s=1.75, shirt=C(240, 236, 226), pants=C(200, 180, 140), hair="bowl", pose="sit",
           arms=((-96, 54), (-40, 66)), look=-1)
    c.line([(790 - 96 * 1.75 + 2, 1600 - 26 * 1.75 - 108 * 1.75 + 58 * 1.75), (790 - 120 * 1.75, 1600 - 26 * 1.75 - 108 * 1.75)],
           width=3)
    person(c, 300, 1650, s=1.6, shirt=C(90, 120, 160), pants=C(200, 180, 140), hair="bun", pose="stand",
           arms=((34, 58), (44, 48)), look=1,
           hold=lambda cc, x, shy, s: [cc.shape(capsule((x - 44 * s, shy + 52 * s - k * 22 * s), (x + 54 * s, shy + 46 * s - k * 22 * s),
                                                         10 * s), C(236, 218, 176), outline=2.0) for k in range(3)])


def gessner(c):
    iso = Iso(594, 1000, 1.2)
    room(c, iso, 520, 470, 520, wall=C(214, 190, 150), brick=True)
    window(c, iso, 330, 470, 260, 440, "r")
    wall_shelf(c, iso, 30, 300, 380, seed=2, wall="r")
    wall_shelf(c, iso, 30, 300, 240, seed=3, wall="r")
    wall_shelf(c, iso, 60, 420, 330, seed=5, wall="l")
    for bx, bz, n in ((40, 330, 5), (90, 400, 3), (400, 370, 4)):
        book_pile(c, iso, bx, bz, n, bx)
    desk(c, iso, 180, 150)
    P = iso.p
    for k, (px, pz) in enumerate(((230, 180), (280, 210), (330, 190))):
        x, y = P(px, 141, pz)
        paper_slip(c, x, y - 4, 80, 46, angle=-20 + k * 14)
    cx, cy = P(380, 141, 170)
    c.shape(rect(cx - 10, cy - 70, cx + 10, cy), C(240, 230, 200), outline=2.2)
    c.shape(ellipse(cx, cy - 84, 9, 16, n=14), C(250, 190, 80), outline=1.8)
    c.wash(c.mask(ellipse(cx, cy - 84, 90, 90), blur=26), C(255, 220, 140), opacity=0.35, gran=0.05, edge=0)
    iso_box(c, iso, 236, 0, 316, 70, 70, 70, WOOD_D, outline=2.0)
    sx, sy = P(271, 0, 351)
    person(c, sx + 8, sy - 50, s=1.4, shirt=C(80, 60, 110), pants=C(70, 60, 50), hair="cap", hair_col=C(60, 44, 36),
           pose="sit", arms=((-46, 40), (50, 30)), look=-1,
           hold=lambda cc, x, shy, s: scissors(cc, x - 46 * s, shy + 40 * s, s))
    r = random.Random(9)
    for _ in range(18):
        x, y = r.uniform(150, 1090), r.uniform(430, 820)
        paper_slip(c, x, y, r.uniform(56, 76), r.uniform(34, 44), angle=r.uniform(-40, 40), lines=r.choice([2, 3]))


def katalog(c):
    s = 1.15
    iso = Iso(590, 1004, s)
    room(c, iso, 540, 480, 560, wall=C(200, 178, 140), floor=C(140, 100, 66))
    wall_shelf(c, iso, 60, 440, 420, seed=7, wall="l")
    wall_shelf(c, iso, 60, 440, 290, seed=8, wall="l")
    x0, w, h, d = 40, 430, 330, 110
    iso_box(c, iso, x0, 0, 10, w, h, d, WOOD)
    P = iso.p
    rows, cols = 7, 8
    for i in range(cols):
        for j in range(rows):
            xa, xb = x0 + 8 + i * (w - 16) / cols, x0 + 8 + (i + 1) * (w - 16) / cols - 6
            ya, yb = 12 + j * (h - 24) / rows, 12 + (j + 1) * (h - 24) / rows - 6
            c.shape([P(xa, ya, 10 + d), P(xb, ya, 10 + d), P(xb, yb, 10 + d), P(xa, yb, 10 + d)], C(170, 122, 76), outline=1.8,
                    opacity=0.7)
            hx, hy = P((xa + xb) / 2, (ya + yb) / 2, 10 + d)
            c.shape(ellipse(hx, hy, 4.5, 3, n=8), C(200, 170, 100), outline=1.2)
    cwid, chei = (w - 16) / cols - 6, (h - 24) / rows - 6
    iso_box(c, iso, x0 + 8 + 3 * (w - 16) / cols, 12 + 2 * (h - 24) / rows, 10 + d, cwid, chei, 120, C(170, 122, 76))
    tx, ty = P(x0 + 8 + 3.5 * (w - 16) / cols, 12 + 3 * (h - 24) / rows, 10 + d + 70)
    for k in range(6):
        paper_slip(c, tx - 10 + k * 5, ty - 20 - k * 4, 48, 36, angle=-8, lines=2, col=C(246, 240, 224))
    # tangga + pustakawan
    lx, ly = P(480, 0, 170)
    top = ly - 470
    for dx in (-36, 36):
        c.line([(lx + dx, ly), (lx + dx + 50, top)], width=5)
    for k in range(1, 9):
        t = k / 9
        c.line([(lx - 36 + 50 * t, ly - 470 * t), (lx + 36 + 50 * t, ly - 470 * t)], width=4)
    person(c, lx + 40, ly - 260, s=1.2, shirt=C(80, 100, 90), pants=C(60, 50, 50), hair="bun", skirt=True,
           arms=((-60, -10), "down"), look=-1, shadow=False)
    # mahasiswa mengantuk membawa lentera
    px, py = P(300, 0, 440)

    def lantern(cc, x, shy, s):
        cc.line([(x + 62 * s, shy + 30 * s), (x + 62 * s, shy + 88 * s)], width=3)
        cc.shape(ellipse(x + 62 * s, shy + 108 * s, 17 * s, 21 * s, n=18), C(250, 200, 110), outline=2.4)
        cc.wash(cc.mask(ellipse(x + 62 * s, shy + 108 * s, 90 * s, 90 * s), blur=26), C(255, 220, 140), opacity=0.3, gran=0.05,
                edge=0)

    person(c, px, py, s=1.4, shirt=C(170, 70, 50), pants=C(70, 80, 100), hair="bowl", arms=("down", (60, 30)), mouth="flat",
           hold=lantern)
    c.text((px + 110, py - 400), "z", size=46, path=CARDO_I)
    c.text((px + 140, py - 450), "z", size=36, path=CARDO_I)


def kampus(c):
    c.shape(rect(0, 330, 1240, 1400), C(226, 214, 176), opacity=0.55, outline=3, shade=0.3)
    c.shape(rect(0, 1100, 1240, 1400), C(150, 120, 80), opacity=0.5, outline=2.4, hatch=dict(spacing=14, angle=90, alpha=0.25))
    c.shape(rect(830, 520, 1090, 1400), C(130, 90, 56), outline=3.2, shade=0.3)
    c.shape(rect(860, 560, 1060, 860), C(150, 108, 70), outline=2.2)
    c.shape(rect(860, 910, 1060, 1360), C(150, 108, 70), outline=2.2)
    c.shape(ellipse(1058, 1000, 10, 10, n=12), C(220, 190, 110), outline=2)
    c.shape(rect(830, 430, 1090, 500), C(240, 232, 210), outline=2.4)
    c.text((960, 466), "Ruang Dosen", size=34, path=CARDO_B)
    c.shape(rect(110, 470, 530, 820), C(180, 140, 90), outline=3)
    r = random.Random(4)
    for k in range(6):
        paper_slip(c, 180 + (k % 3) * 130, 570 + (k // 3) * 150, 104, 124, angle=r.uniform(-6, 6), lines=4)
    c.text((320, 492), "PENGUMUMAN", size=28, path=CARDO_B)
    c.shape(rect(0, 1400, 1240, 2204), C(200, 190, 170), opacity=0.6, outline=3)
    for k in range(1, 9):
        c.line([(k * 150, 1400), (k * 150 - 90, 2204)], width=1.4, alpha=0.4)
    c.line([(0, 1560), (1240, 1560)], width=1.2, alpha=0.3)
    specs = [(150, "hijab", C(200, 120, 140), C(70, 70, 100), True, C(150, 60, 80)),
             (330, "bowl", C(90, 120, 160), C(60, 60, 70), False, C(30, 24, 22)),
             (510, "bun", C(230, 200, 120), C(70, 60, 80), True, C(30, 24, 22)),
             (690, "bowl", C(238, 238, 232), C(40, 40, 50), False, C(30, 24, 22))]
    for x, hair, shirt, pants, skirt, hc in specs:
        person(c, x, 1600, s=1.35, shirt=shirt, pants=pants, hair=hair, skirt=skirt, arms=((30, 50), (-30, 50)), hair_col=hc,
               mouth="flat", hold=lambda cc, xx, shy, s: draft_stack(cc, xx, shy + 74 * s, 74 * s, 44 * s, n=6))
    c.text((700, 1150), "REVISI", size=46, path=CARDO_B, angle=14, alpha=0.85)
    c.text((520, 1200), "REVISI", size=34, path=CARDO_B, angle=-10, alpha=0.7)


def doi(c):
    gx, gy = 620, 520
    c.shape(ellipse(gx, gy, 140, 140, n=50), C(150, 190, 190), opacity=0.6, outline=3.2, shade=0.5)
    c.line(ellipse(gx, gy, 140, 50, n=40), width=1.6, alpha=0.6, closed=True)
    c.line(ellipse(gx, gy, 54, 140, n=40), width=1.6, alpha=0.6, closed=True)
    c.line([(gx - 140, gy), (gx + 140, gy)], width=1.4, alpha=0.5)
    c.shape(rect(gx - 12, gy + 140, gx + 12, gy + 190), WOOD_D, outline=2.2)
    c.shape(ellipse(gx, gy + 196, 80, 18), WOOD, outline=2.4)
    c.shape([(110, 720), (1130, 720), (1130, 1500), (110, 1500)], C(120, 70, 50), outline=3.2)
    left = [(140, 740), (600, 780), (600, 1480), (140, 1450)]
    right = [(640, 780), (1100, 740), (1100, 1450), (640, 1480)]
    c.shape(left, C(246, 238, 216), opacity=0.5, outline=3)
    c.shape(right, C(246, 238, 216), opacity=0.5, outline=3)
    r = random.Random(5)
    ends = []
    for x0 in (170, 670):
        for k in range(7):
            y = 830 + k * 88
            c.line([(x0, y), (x0 + 300, y)], width=1.8, alpha=0.6)
            c.line([(x0, y + 22), (x0 + 220, y + 22)], width=1.4, alpha=0.4)
            tx, ty = x0 + 360, y + 8
            c.line([(x0 + 300, y + 8), (tx - 30, ty)], width=1.6)
            c.shape(rot(rect(tx - 30, ty - 16, tx + 50, ty + 16), r.uniform(-10, 10), tx, ty), C(210, 170, 90), outline=2.0)
            c.text((tx + 10, ty), "DOI", size=20, path=CARDO_B)
            ends.append((tx + 10, ty - 16))
    for k in range(9):
        ex, ey = r.choice(ends)
        c.line([(gx + r.uniform(-100, 100), gy + 110), ((gx + ex) / 2 + r.uniform(-60, 60), (gy + ey) / 2), (ex, ey)], width=1.2,
               alpha=0.45, wobble=2)
    person(c, 1010, 1620, s=1.4, shirt=C(90, 120, 160), pants=C(60, 60, 70), arms=((-70, -30), "down"),
           hold=lambda cc, x, shy, s: magnifier(cc, x - 78 * s, shy - 40 * s, s * 1.2))


def ai(c):
    c.shape(rrect(330, 400, 910, 1040, 40), C(120, 130, 125), outline=3.4, hatch=dict(spacing=10, angle=-40, alpha=0.22))
    c.shape(rrect(400, 470, 840, 710, 24), C(180, 215, 205), opacity=0.6, outline=3)
    c.text((620, 570), "Chatbot", size=64, path=CARDO_B)
    c.text((620, 648), "“ini rujukannya!”", size=40, path=CARDO_I)
    for x in (430, 520, 610, 700, 790):
        c.shape(ellipse(x, 790, 22, 22, n=18), C(230, 200, 120), outline=2.4)
    for x in (380, 860):
        c.shape(rect(x - 14, 320, x + 14, 400), C(100, 110, 105), outline=2.4)
        c.shape(ellipse(x, 312, 22, 14), C(200, 120, 60), outline=2.2)
    c.shape(rect(430, 950, 810, 980), C(60, 50, 50), outline=2.6)
    pts = [(620, 970), (600, 1100), (680, 1220), (560, 1340), (640, 1460)]
    for a, b in zip(pts[:-1], pts[1:]):
        c.shape([(a[0] - 120, a[1]), (a[0] + 120, a[1]), (b[0] + 120, b[1]), (b[0] - 120, b[1])], C(246, 240, 222), opacity=0.5,
                outline=2.2)
        for k in range(3):
            t = (k + 1) / 4
            yy, xx = a[1] + (b[1] - a[1]) * t, a[0] + (b[0] - a[0]) * t
            c.line([(xx - 90, yy), (xx + 60, yy)], width=1.4, alpha=0.55)
    r = random.Random(6)
    spots = [(170, 1150), (1060, 1120), (330, 1390), (930, 1360), (820, 1540), (430, 1560), (1080, 1500), (150, 1380),
             (980, 1230)]
    for x, y in spots:
        ghost_slip(c, x, y, r.uniform(84, 110), r.uniform(52, 64), r.uniform(-25, 25))
    person(c, 230, 1630, s=1.45, shirt=C(238, 238, 232), pants=C(50, 55, 70), arms=((60, -20), "down"), mouth="o", look=1,
           hold=lambda cc, x, shy, s: magnifier(cc, x + 78 * s, shy - 30 * s, s * 1.1, ang=30))


def dosenku(c):
    s = 1.25
    iso = Iso(594, 960, s)
    room(c, iso, 520, 470, 480, wall=C(214, 222, 206), floor=C(160, 118, 80))
    P = iso.p
    # lemari "Crossref"
    iso_box(c, iso, 30, 0, 20, 170, 300, 120, WOOD)
    for j in range(5):
        y = 30 + j * 52
        c.line([P(36, y, 140), P(194, y, 140)], width=1.8, alpha=0.7)
    lx, ly = P(115, 300, 80)
    c.shape(rect(lx - 86, ly - 112, lx + 86, ly - 58), C(240, 232, 210), outline=2.4)
    c.text((lx, ly - 85), "Crossref", size=34, path=CARDO_B)
    # kuil "OpenAlex" (namanya dari Perpustakaan Aleksandria)
    tx0, tz = 300, 30
    iso_box(c, iso, tx0, 0, tz, 200, 26, 110, C(225, 214, 190))
    for k in range(4):
        iso_box(c, iso, tx0 + 14 + k * 50, 26, tz + 40, 20, 200, 20, C(236, 228, 208), outline=2.0)
    iso_box(c, iso, tx0, 226, tz, 200, 30, 110, C(225, 214, 190))
    ox, oy = P(tx0 + 100, 256, tz + 55)
    c.shape([(ox - 140, oy + 8), (ox + 140, oy + 8), (ox, oy - 74)], C(225, 214, 190), outline=2.6)
    c.shape(rect(ox - 100, oy - 172, ox + 100, oy - 118), C(240, 232, 210), outline=2.4)
    c.text((ox, oy - 145), "OpenAlex", size=34, path=CARDO_B)
    desk(c, iso, 200, 260)
    kx, ky = P(310, 141, 320)
    a = P(115, 300, 80)
    pipe(c, [(a[0], a[1] - 116), (a[0] + 30, a[1] - 230), (kx - 150, ky - 300), (kx - 60, ky - 120)], r=15, col=C(90, 150, 140))
    b = (ox, oy - 172)
    pipe(c, [b, (b[0] - 20, b[1] - 80), (kx + 150, ky - 320), (kx + 60, ky - 120)], r=15, col=C(90, 150, 140))

    def screen(cc, x, y, ss):
        cc.text((x, y - 16 * ss), "Dosenku", size=int(40 * ss), path=CARDO_B)
        for k in range(3):
            cc.line([(x - 70 * ss, y + (14 + k * 16) * ss), (x + 40 * ss, y + (14 + k * 16) * ss)], width=1.6, alpha=0.6)
            check_stamp(cc, x + 66 * ss, y + (14 + k * 16) * ss, 0.26 * ss)

    laptop_front(c, kx, ky, s=0.95, screen=screen)
    r = random.Random(8)
    for x, y in ((250, 520), (420, 470), (820, 500), (1000, 560), (600, 420), (930, 700)):
        paper_slip(c, x, y, 80, 50, angle=r.uniform(-20, 20))
        check_stamp(c, x + 30, y + 14, 0.7)
    sx, sy = P(150, 0, 450)
    person(c, sx, sy, s=1.35, shirt=C(238, 238, 232), pants=C(50, 55, 70), arms=("down", (60, -60)), look=1)
    sx, sy = P(500, 0, 300)
    person(c, sx, sy, s=1.35, shirt=C(60, 80, 130), pants=C(60, 80, 130), hair="hijab", hair_col=C(150, 60, 80),
           skirt=True, arms=((-60, -60), "down"), look=-1)


def penutup(c):
    emblem(c, 620, 760, 1.1)
    c.text((620, 1040), "Dosenku", size=150, path=CARDO_B)
    c.text((620, 1170), "Skripsi terarah. Dosen senang.", size=60, path=CARDO_I)
    for side in (-1, 1):
        c.line([(620 + side * 60, 1250), (620 + side * 200, 1238), (620 + side * 330, 1266), (620 + side * 400, 1244)], width=2.6)
        c.outline(ellipse(620 + side * 410, 1244, 10, 10, n=12), width=2.2)
    rib = [(260, 1320), (980, 1320), (940, 1365), (980, 1410), (260, 1410), (300, 1365)]
    c.shape(rib, C(150, 206, 196), opacity=0.75, outline=3)
    c.text((620, 1364), "dosenku.biz.id", size=66, path=CARDO_B, alpha=1.0)
    c.text((620, 1480), "Gratis untuk mulai", size=48, path=CARDO_I)
    q = [(900, 520), (1010, 380), (1050, 350), (1020, 420), (930, 530)]
    c.shape(q, C(240, 236, 226), opacity=0.6, outline=2.6)
    c.line([(900, 530), (870, 580)], width=3.2)


SCENES = dict(hook=hook, gulungan=gulungan, aleksandria=aleksandria, gessner=gessner, katalog=katalog, kampus=kampus,
              doi=doi, ai=ai, dosenku=dosenku, penutup=penutup)
