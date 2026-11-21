"""Properti siap pakai untuk diorama perkamen: ruang potongan isometrik, jendela, rak, pipa, dll."""
import math
import random

import numpy as np

from ink import (C, CARDO_B, capsule, ellipse, iso_box, move, paper_slip, rect, rot, rrect)

WOOD = C(150, 104, 62)
WOOD_D = C(110, 74, 46)
WALL = C(222, 200, 160)
FLOOR = C(170, 122, 78)
TEAL = C(15, 118, 110)
INK_DARK = C(40, 28, 21)


def room(c, iso, X, Z, Hh, wall=WALL, floor=FLOOR, t=22, slab=60, planks=True, brick=False):
    P = iso.p
    # back walls
    wl = [P(0, 0, 0), P(0, 0, Z), P(0, Hh, Z), P(0, Hh, 0)]
    wr = [P(0, 0, 0), P(X, 0, 0), P(X, Hh, 0), P(0, Hh, 0)]
    c.shape(wl, np.asarray(wall) * 0.9, opacity=0.75, outline=2.8, shade=0.3)
    c.shape(wr, wall, opacity=0.75, outline=2.8, shade=0.3)
    if brick:
        for k in range(1, int(Hh / 34)):
            y = k * 34
            c.line([P(0, y, 0), P(X, y, 0)], width=1.2, alpha=0.35)
            c.line([P(0, y, 0), P(0, y, Z)], width=1.2, alpha=0.35)
    # floor
    fl = [P(0, 0, 0), P(X, 0, 0), P(X, 0, Z), P(0, 0, Z)]
    c.shape(fl, floor, opacity=0.8, outline=2.8, shade=0.2)
    if planks:
        for k in range(1, int(Z / 46)):
            z = k * 46
            c.line([P(0, 0, z), P(X, 0, z)], width=1.4, alpha=0.5)
    # wall cut tops (thickness)
    c.shape([P(-t, Hh, -t), P(X, Hh, -t), P(X, Hh, 0), P(0, Hh, 0), P(0, Hh, Z), P(-t, Hh, Z)], C(90, 70, 55), opacity=0.9,
            outline=2.6, hatch=dict(spacing=5, angle=30, alpha=0.6))
    c.shape([P(X, 0, -t), P(X, 0, 0), P(X, Hh, 0), P(X, Hh, -t)], C(175, 140, 105), opacity=0.8, outline=2.6,
            hatch=dict(spacing=6, angle=-30, alpha=0.35))
    c.shape([P(-t, 0, Z), P(0, 0, Z), P(0, Hh, Z), P(-t, Hh, Z)], C(175, 140, 105), opacity=0.8, outline=2.6,
            hatch=dict(spacing=6, angle=30, alpha=0.35))
    # floor slab section
    c.shape([P(0, 0, Z), P(X, 0, Z), P(X, -slab, Z), P(0, -slab, Z)], C(120, 92, 66), opacity=0.85, outline=2.6,
            hatch=dict(spacing=6, angle=20, alpha=0.45))
    c.shape([P(X, 0, Z), P(X, 0, 0), P(X, -slab, 0), P(X, -slab, Z)], C(100, 76, 54), opacity=0.85, outline=2.6,
            hatch=dict(spacing=6, angle=-20, alpha=0.45))


def window(c, iso, x0, x1, y0, y1, wall="r", sky=C(170, 200, 210)):
    P = iso.p
    if wall == "r":
        poly = [P(x0, y0, 0), P(x1, y0, 0), P(x1, y1, 0), P(x0, y1, 0)]
        mid = [P((x0 + x1) / 2, y0, 0), P((x0 + x1) / 2, y1, 0)]
        mid2 = [P(x0, (y0 + y1) / 2, 0), P(x1, (y0 + y1) / 2, 0)]
    else:
        poly = [P(0, y0, x0), P(0, y0, x1), P(0, y1, x1), P(0, y1, x0)]
        mid = [P(0, y0, (x0 + x1) / 2), P(0, y1, (x0 + x1) / 2)]
        mid2 = [P(0, (y0 + y1) / 2, x0), P(0, (y0 + y1) / 2, x1)]
    c.shape(poly, sky, opacity=0.6, outline=3.2)
    c.line(mid, width=2.6)
    c.line(mid2, width=2.6)


def wall_shelf(c, iso, x0, x1, y, depth=60, seed=0, wall="r"):
    P = iso.p
    if wall == "r":
        iso_box(c, iso, x0, y - 10, 0, x1 - x0, 10, depth, WOOD)
        # books standing on the shelf, drawn as small iso boxes
        r = random.Random(seed)
        x = x0 + 6
        pal = [C(150, 50, 40), C(60, 90, 70), C(170, 120, 50), C(70, 70, 110), C(120, 80, 50)]
        while x < x1 - 20:
            bw = r.uniform(12, 22)
            bh = r.uniform(50, 85)
            iso_box(c, iso, x, y, 6, bw, bh, depth - 14, r.choice(pal), outline=1.8)
            x += bw + 2
    else:
        iso_box(c, iso, 0, y - 10, x0, depth, 10, x1 - x0, WOOD)
        r = random.Random(seed)
        z = x0 + 6
        pal = [C(150, 50, 40), C(60, 90, 70), C(170, 120, 50), C(70, 70, 110), C(120, 80, 50)]
        while z < x1 - 20:
            bw = r.uniform(12, 22)
            bh = r.uniform(50, 85)
            iso_box(c, iso, 6, y, z, depth - 14, bh, bw, r.choice(pal), outline=1.8)
            z += bw + 2


# ================================================================ props
def magnifier(c, x, y, s=1.0, ang=-35):
    hx, hy = x + 60 * s * math.cos(math.radians(ang + 90)), y + 60 * s * math.sin(math.radians(ang + 90))
    c.shape(capsule((x, y), (hx, hy), 6 * s), C(110, 74, 46), outline=2.2 * s)
    c.shape(ellipse(x, y, 30 * s, 30 * s, n=30), C(200, 225, 230), opacity=0.45, outline=4 * s)


def draft_stack(c, x, y, w=90, h=60, n=6, ang=0):
    """Tumpukan naskah (balok kertas) dengan garis halaman di sisi depan; (x, y) = tengah bawah."""
    d = h * 0.35
    top = [(x - w / 2, y - h), (x + w / 2, y - h), (x + w / 2 + d * 0.6, y - h - d), (x - w / 2 + d * 0.6, y - h - d)]
    front = [(x - w / 2, y - h), (x + w / 2, y - h), (x + w / 2, y), (x - w / 2, y)]
    c.shape(front, C(240, 232, 206), opacity=0.6, outline=2.0, shade=0.2)
    c.shape(top, C(250, 246, 232), opacity=0.45, outline=2.0)
    for k in range(1, n):
        yy = y - h + h * k / n
        c.line([(x - w / 2 + 3, yy), (x + w / 2 - 3, yy)], width=1.1, alpha=0.45, wobble=0.4)
    for k in range(3):
        yy = y - h - d * 0.5 + (k - 1) * d * 0.22
        c.line([(x - w / 2 + d * 0.3 + 10, yy), (x + w / 2 - 6, yy)], width=1.2, alpha=0.5, wobble=0.3)


def pipe(c, pts, r=22, col=C(170, 120, 70)):
    for a, b in zip(pts[:-1], pts[1:]):
        c.shape(capsule(a, b, r), col, outline=2.6, shade=0.2)
    for a, b in zip(pts[:-1], pts[1:]):
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        n = int(L / 70)
        ang = math.atan2(b[1] - a[1], b[0] - a[0])
        for k in range(1, n + 1):
            t = k / (n + 1)
            px, py = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
            nx, ny = -math.sin(ang) * r, math.cos(ang) * r
            c.shape(capsule((px - nx * 1.1, py - ny * 1.1), (px + nx * 1.1, py + ny * 1.1), 6), C(200, 170, 110), outline=2.0)


def check_stamp(c, x, y, s=1.0, col=TEAL):
    c.shape(ellipse(x, y, 26 * s, 26 * s, n=24), col, opacity=0.8, outline=2.6 * s)
    c.line([(x - 12 * s, y + 1 * s), (x - 3 * s, y + 10 * s), (x + 13 * s, y - 10 * s)], width=5 * s, taper=False, wobble=0.3)


def ghost_slip(c, cx, cy, w=80, h=50, ang=0):
    poly = rot(rect(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), ang, cx, cy)
    c.wash(c.mask(poly, blur=3), C(235, 235, 245), opacity=0.25, gran=0.4)
    n = len(poly)
    for i in range(n):
        a, b = poly[i], poly[(i + 1) % n]
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        k = 0
        while k < L:
            t0, t1 = k / L, min(1, (k + 9) / L)
            c.line([(a[0] + (b[0] - a[0]) * t0, a[1] + (b[1] - a[1]) * t0), (a[0] + (b[0] - a[0]) * t1, a[1] + (b[1] - a[1]) * t1)],
                   width=1.6, alpha=0.6, wobble=0.2, taper=False)
            k += 16
    c.text((cx, cy), "?", size=34, path=CARDO_B, alpha=0.6, angle=-ang)


def laptop_front(c, x, y, s=1.0, screen=None):
    c.shape(rrect(x - 110 * s, y - 150 * s, x + 110 * s, y - 6 * s, 10 * s), C(80, 80, 90), outline=2.6 * s)
    c.shape(rect(x - 98 * s, y - 138 * s, x + 98 * s, y - 18 * s), C(236, 248, 246), opacity=0.7, outline=2.0 * s)
    c.shape([(x - 140 * s, y + 18 * s), (x + 140 * s, y + 18 * s), (x + 116 * s, y - 6 * s), (x - 116 * s, y - 6 * s)],
            C(150, 150, 160), outline=2.6 * s)
    if screen:
        screen(c, x, y - 78 * s, s)


def column(c, x, ytop, ybot, w=60):
    c.shape(rect(x - w / 2, ytop + 30, x + w / 2, ybot - 24), C(232, 220, 196), opacity=0.7, outline=2.6, shade=0.4)
    for k in range(1, 4):
        xx = x - w / 2 + w * k / 4
        c.line([(xx, ytop + 34), (xx, ybot - 28)], width=1.5, alpha=0.6)
    c.shape(rect(x - w / 2 - 14, ytop, x + w / 2 + 14, ytop + 30), C(225, 212, 186), outline=2.6)
    c.shape(rect(x - w / 2 - 12, ybot - 24, x + w / 2 + 12, ybot), C(225, 212, 186), outline=2.6)



def scissors(c, x, y, s):
    for a in (-18, 18):
        c.line(rot([(x, y), (x - 34 * s, y - 10 * s)], a, x, y), width=3 * s)
    c.outline(ellipse(x + 8 * s, y + 6 * s, 7 * s, 5 * s), width=2.4 * s)
    c.outline(ellipse(x + 8 * s, y - 6 * s, 7 * s, 5 * s), width=2.4 * s)


