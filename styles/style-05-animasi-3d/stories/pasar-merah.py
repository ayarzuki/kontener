"""Berita pasar ala film animasi: "Anthropic turun, semua ikut turun" (Jumat 20 Nov 2026).

Dini hari (WIB) setelah bursa AS tutup. Panah merah raksasa jatuh menancap di meja, layar laptop menampilkan grafik
ANT lalu papan pasar yang semuanya merah, HP penuh notifikasi. Data utama tampil sebagai kartu overlay (lihat JSON).
"""
import math

import numpy as np
from PIL import Image, ImageDraw

import room
from cg import Mesh, Part, R, T, chain, rbox

NARA_POS = (0, 48, -14)
PALETTE = dict(top_col=(44, 58, 104), hijab_col=(128, 158, 140), pants_col=(40, 44, 56))

W_ = dict(hide_front=True)
SHOTS = [
    dict(name="lebar", t0=0.0, t1=2.8, eye0=(70, 160, -205), eye1=(62, 154, -194), tgt=(-8, 92, -30), fov=36, blur=2.0, **W_),
    dict(name="grafik", t0=2.8, t1=7.4, eye0=(52, 140, 30), eye1=(42, 130, 16), tgt=(-2, 88, -70), fov=30, blur=4),
    dict(name="kaget", t0=7.4, t1=13.2, eye0=(10, 122, -122), eye1=(6, 119, -112), tgt=(0, 99, -24), fov=36, blur=5),
    dict(name="after-hours", t0=13.2, t1=20.2, eye0=(40, 128, 12), eye1=(34, 124, 4), tgt=(-2, 93, -70), fov=28, blur=4),
    dict(name="domino", t0=20.2, t1=26.0, eye0=(46, 150, 36), eye1=(38, 140, 20), tgt=(0, 88, -72), fov=28, blur=4),
    dict(name="hp", t0=26.0, t1=33.3, eye0=(35, 113, -34), eye1=(33, 107, -38), tgt=(28, 75.3, -54), fov=24, blur=6),
    dict(name="merah", t0=33.3, t1=40.3, eye0=(-8, 122, -122), eye1=(-4, 119, -112), tgt=(0, 99, -24), fov=36, blur=5),
    dict(name="ihsg", t0=40.3, t1=47.1, eye0=(56, 160, 34), eye1=(50, 152, 20), tgt=(0, 86, -72), fov=28, blur=4),
    dict(name="sebab", t0=47.1, t1=54.2, eye0=(66, 156, -196), eye1=(56, 150, -184), tgt=(-6, 94, -26), fov=38, blur=2.0, **W_),
    dict(name="polling", t0=54.2, t1=61.6, eye0=(0, 120, -118), eye1=(0, 121, -126), tgt=(0, 101, -16), fov=40, blur=4, **W_),
    dict(name="follow", t0=61.6, t1=66.0, eye0=(0, 121, -126), eye1=(0, 142, -166), tgt=(0, 101, -16), fov=40, blur=4, **W_),
]


def ease(u):
    u = min(1.0, max(0.0, u))
    return u * u * (3 - 2 * u)


def K(keys, t):
    if t <= keys[0][0]:
        return keys[0][1]
    for (a, va), (b, vb) in zip(keys[:-1], keys[1:]):
        if a <= t <= b:
            u = ease((t - a) / max(1e-6, b - a))
            if isinstance(va, (tuple, list)):
                return tuple(x + (y - x) * u for x, y in zip(va, vb))
            return va + (vb - va) * u
    return keys[-1][1]


def step(keys, t):
    v = keys[0][1]
    for a, val in keys:
        if t >= a:
            v = val
    return v


TYPE = (42, 14, -22, 52)
REST = (36, 16, -14, 46)
SHRUG = (28, 48, 12, 96)
WAVE = (166, -24, 0, 38)
BLINKS = [3.9, 6.6, 11.9, 15.8, 18.9, 23.2, 29.0, 36.1, 42.6, 45.9, 50.4, 53.1, 58.9, 64.6]


def nara_state(t):
    st = dict(PALETTE)
    st["spine"] = K([(0, (12, 0, 0)), (0.95, (12, 0, 0)), (1.15, (-8, 0, 0)), (2.4, (10, 0, 0)), (7.6, (12, 0, 0)),
                     (7.8, (-6, 0, 0)), (10.2, (2, 0, 0)), (13.2, (12, 0, 0)), (20.2, (12, 0, 0)), (21.0, (-8, 0, 0)),
                     (26.0, (-6, 0, 0)), (26.35, (20, -6, 0)), (33.2, (20, -6, 0)), (33.5, (8, 0, 0)), (40.3, (12, 0, 0)),
                     (47.1, (14, 0, 0)), (54.2, (14, 0, 0)), (54.7, (2, 0, 0))], t)
    head = K([(0, (10, 0, 0)), (0.95, (10, 0, 0)), (1.15, (-6, 0, 0)), (2.4, (8, 0, 0)), (7.6, (10, 0, 0)), (7.8, (-2, 0, 0)),
              (10.2, (4, 0, 2)), (13.2, (12, 0, 0)), (20.2, (10, 0, 0)), (21.0, (-10, 0, 6)), (26.0, (-8, 0, 4)),
              (26.35, (34, -10, 0)), (33.2, (34, -10, 0)), (33.5, (8, 6, -4)), (40.3, (10, 0, 0)), (47.1, (12, 0, 0)),
              (54.2, (12, 0, 0)), (54.7, (0, 0, 8)), (57.4, (-2, 0, -4)), (61.6, (-2, 0, 0))], t)
    if 37.6 <= t < 39.4:  # geleng kepala
        head = (head[0], head[1] + 14 * math.sin((t - 37.6) * 9) * (1 - (t - 37.6) / 1.8), head[2])
    if 13.2 <= t < 20.2:
        head = (head[0], head[1] + 2 * math.sin(t * 3), head[2])
    st["head"] = head
    st["gaze"] = K([(0, (0, -0.2)), (1.1, (0.1, 0.25)), (2.4, (0, -0.25)), (7.6, (0, -0.2)), (7.8, (0, 0.05)), (10.4, (0.15, 0.0)),
                    (13.2, (0, -0.2)), (21.0, (0.2, 0.3)), (26.0, (0.2, 0.2)), (26.35, (0.35, -0.7)), (33.2, (0.35, -0.7)),
                    (33.6, (0.25, -0.1)), (36.0, (-0.15, 0.0)), (40.3, (0, -0.2)), (54.4, (0, 0.08))], t)
    lid = K([(0, 0.1), (7.6, 0.1), (7.8, 0.0), (10.0, 0.0), (10.6, 0.25), (20.2, 0.2), (21.0, 0.45), (26.0, 0.4), (26.35, 0.15),
             (33.5, 0.35), (40.3, 0.3), (47.1, 0.15), (57.4, 0.15), (58.0, 0.35), (61.6, 0.3)], t)
    for b in BLINKS:
        if 0 <= t - b < 0.14:
            lid = max(lid, 1.0 - abs(t - b - 0.07) / 0.07 * 0.4)
    st["lid"] = lid
    st["wide"] = K([(0, 0.0), (1.0, 0.0), (1.15, 1.0), (2.4, 0.0), (7.65, 0.0), (7.85, 1.0), (9.8, 0.6), (10.4, 0.0),
                    (26.3, 0.0), (26.7, 0.7), (28.0, 0.0)], t)
    st["brow"] = K([(0, (6, 0.0)), (1.1, (-6, 0.35)), (2.4, (8, 0.2)), (7.65, (8, 0.2)), (7.8, (-6, 0.35)), (10.2, (14, 0.3)), (20.2, (12, 0.2)),
                    (33.5, (18, 0.3)), (40.3, (14, 0.2)), (47.1, (6, 0.1)), (54.4, (4, 0.15)), (57.6, (2, 0.1))], t)
    st["mouth"] = step([(0, "flat"), (1.1, "O"), (2.4, "flat"), (7.8, "O"), (10.2, "wavy"), (13.2, "frown"), (21.0, "wavy"),
                        (26.0, "flat"), (33.5, "frown"), (40.3, "flat"), (54.4, "smile0"), (57.6, "smile"), (61.8, "grin_open")], t)
    st["mouth_open"] = K([(0, 0.0), (1.05, 0.0), (1.15, 0.8), (2.2, 0.0), (7.75, 0.0), (7.9, 0.7), (9.9, 0.6), (10.2, 0.0),
                          (61.7, 0.0), (61.9, 0.8)], t)
    st["blush"] = K([(0, 0.0), (57.4, 0.0), (58.0, 0.5)], t)
    st["sweat"] = 1 if 33.5 <= t < 40.3 else 0
    arm = K([(0, TYPE), (0.95, TYPE), (1.15, REST), (2.6, TYPE), (7.6, TYPE), (7.9, REST), (12.6, REST), (13.2, TYPE),
             (20.2, TYPE), (21.0, REST), (26.0, REST), (26.35, TYPE), (47.1, TYPE), (54.2, TYPE), (54.7, SHRUG), (56.9, SHRUG),
             (57.5, REST)], t)
    armL, armR = arm, arm
    if t >= 61.6:
        u = ease((t - 61.6) / 0.4)
        armR = tuple(a + (b - a) * u for a, b in zip(REST, WAVE))
        armR = (armR[0], armR[1] + 14 * math.sin((t - 61.6) * 8) * u, armR[2], armR[3])
    typing = (2.8 <= t < 7.5) or (13.4 <= t < 20.1) or (47.3 <= t < 54.1)
    if typing:
        armL = (armL[0], armL[1], armL[2], armL[3] + 6 * math.sin(t * 9))
        armR = (armR[0], armR[1], armR[2], armR[3] + 6 * math.sin(t * 9 + 2.1))
    st["armL"], st["armR"] = armL, armR
    return st


# ---------------------------------------------------------------- tekstur layar
RED, GRN, AMB = (239, 68, 68), (34, 197, 94), (245, 158, 11)


def _path(n=160):
    rng = np.random.default_rng(20)
    keys = [(0.0, 89.86), (0.12, 92.56), (0.3, 88.4), (0.55, 83.05), (0.75, 87.2), (1.0, 88.91)]
    xs = np.linspace(0, 1, n)
    ys = np.interp(xs, [k[0] for k in keys], [k[1] for k in keys]) + rng.normal(0, 0.35, n) * np.sin(np.pi * xs) ** 0.5
    ys[0], ys[-1] = 89.86, 88.91
    ys[int(0.55 * (n - 1))] = 83.05
    return xs, ys


def chart_img(p, after=False):
    W, H = 640, 400
    im = Image.new("RGB", (W, H), (11, 15, 25))
    d = ImageDraw.Draw(im)
    d.text((22, 26), "ANT  Anthropic, PBC", font=room.F("Bold", 24), fill=(230, 232, 240), anchor="lm")
    price = "$87,80" if after else "$88,91"
    chg = "−1,25% after-hours" if after else "−8,26 (−8,50%)"
    d.text((22, 70), price, font=room.F("Bold", 44), fill=RED, anchor="lm")
    d.text((200, 74), chg, font=room.F("Medium", 22), fill=RED, anchor="lm")
    x0, x1, y0, y1 = 40, 600, 120, 370
    lo, hi = 82.0, 98.0

    def Y(v):
        return y1 - (v - lo) / (hi - lo) * (y1 - y0)
    for v in (85, 90, 95):
        d.line((x0, Y(v), x1, Y(v)), fill=(30, 38, 54), width=1)
        d.text((x1 + 4, Y(v)), str(v), font=room.F("Regular", 14), fill=(120, 130, 150), anchor="lm")
    for x in range(x0, x1, 18):
        d.line((x, Y(83), x + 9, Y(83)), fill=AMB, width=2)
    d.text((x0 + 4, Y(83) + 14), "IPO $83", font=room.F("Bold", 16), fill=AMB, anchor="lm")
    for x in range(x0, x1, 14):
        d.line((x, Y(97.17), x + 6, Y(97.17)), fill=(100, 110, 130), width=1)
    d.text((x0 + 4, Y(97.17) - 12), "tutup Kamis $97,17", font=room.F("Regular", 15), fill=(140, 150, 170), anchor="lm")
    xs, ys = _path()
    m = max(2, int(len(xs) * min(1.0, p)))
    pts = [(x0 + x * (x1 - x0), Y(y)) for x, y in zip(xs[:m], ys[:m])]
    poly = pts + [(pts[-1][0], y1), (pts[0][0], y1)]
    d.polygon(poly, fill=(60, 18, 24))
    d.line(pts, fill=RED, width=3)
    if p > 0.56:
        lx, ly = x0 + 0.55 * (x1 - x0), Y(83.05)
        d.ellipse((lx - 6, ly - 6, lx + 6, ly + 6), fill=AMB)
        d.text((lx, ly - 22), "$83,05", font=room.F("Bold", 18), fill=AMB, anchor="mm")
    d.text((x1, y1 + 18), "ilustrasi pergerakan 20 Nov", font=room.F("Regular", 13), fill=(110, 118, 136), anchor="rm")
    return im


ROWS = [("ANT", "−8,50%"), ("NEBIUS", "−16,1%"), ("COREWEAVE", "−12,1%"), ("BITCOIN", "< $60.000"), ("EMAS", "−2,4%"),
        ("NASDAQ", "−5,28%"), ("S&P 500", "−3,70%"), ("IHSG", "−0,92%")]


def board_img(n):
    W, H = 640, 400
    im = Image.new("RGB", (W, H), (11, 15, 25))
    d = ImageDraw.Draw(im)
    d.text((22, 26), "PASAR • JUMAT 20 NOV 2026", font=room.F("Bold", 22), fill=(230, 232, 240), anchor="lm")
    for i, (nm, v) in enumerate(ROWS[:n]):
        y = 66 + i * 41
        d.rounded_rectangle((18, y, 622, y + 34), 8, fill=(40, 14, 20))
        d.text((32, y + 17), nm, font=room.F("Bold", 20), fill=(235, 236, 242), anchor="lm")
        d.text((606, y + 17), v, font=room.F("Bold", 22), fill=RED, anchor="rm")
    return im


ALERTS = [("Bitcoin", "Turun di bawah $60.000"), ("Emas", "−2,4% • safe haven ikut merah"), ("IHSG", "−0,92% ke 5.146")]


def alerts_img(n):
    W, H = 360, 720
    y = np.linspace(0, 1, H)[:, None, None]
    a = (np.array((24, 20, 48)) * (1 - y) + np.array((80, 30, 50)) * y) * np.ones((1, W, 1))
    im = Image.fromarray(a.astype(np.uint8))
    d = ImageDraw.Draw(im)
    d.text((180, 120), "04.12", font=room.F("Medium", 76), fill=(255, 255, 255), anchor="mm")
    d.text((180, 178), "Sabtu, 21 November", font=room.F("Regular", 22), fill=(220, 220, 235), anchor="mm")
    for i, (tt, msg) in enumerate(ALERTS[:n]):
        yy = 250 + i * 128
        d.rounded_rectangle((16, yy, 344, yy + 112), 22, fill=(250, 250, 252))
        d.ellipse((30, yy + 18, 74, yy + 62), fill=RED)
        d.polygon([(42, yy + 32), (62, yy + 32), (52, yy + 50)], fill=(255, 255, 255))
        d.text((86, yy + 32), tt, font=room.F("Bold", 22), fill=(20, 24, 32), anchor="lm")
        d.text((30, yy + 84), msg, font=room.F("Medium", 21), fill=(40, 44, 56), anchor="lm")
    return im


def board_n(t):
    if t < 26.0:
        return int(min(3, max(1, 1 + (t - 20.4) // 1.3)))
    if t < 33.3:
        return 5
    if t < 40.6:
        return 7
    return 8


def world_state(t):
    if t < 20.2:
        after = t >= 14.0
        p = 1.0 if after else min(1.0, max(0.05, (t - 2.9) / 4.3))
        q = round(p * 30)
        scr = room.tex(("chart", q, after), lambda: chart_img(q / 30, after))
    else:
        n = board_n(t)
        scr = room.tex(("board", n), lambda: board_img(n))
    na = 0 if t < 26.3 else (1 if t < 29.3 else (2 if t < 40.3 else 3))
    ph = room.tex(("alerts", na), lambda: alerts_img(na))
    return dict(day=0.0, lamp=1.0, screen=scr, app_p=0.0, phone=1, phone_tex=ph, clock_h=4.2, crumpled=0.0,
                posters=("SABAR", "DISIPLIN"))


def light(t):
    red = 0.22 + 0.26 * ease((t - 20.2) / 4) + 0.12 * (1 if 33.3 <= t < 40.3 else 0)
    if t < 2.8:
        red = 0.25
    scol = (0.8, 0.16, 0.16)
    return dict(
        key=(0.6, -0.35, 0.72), keycol=(1.15, 0.78, 0.48),
        fill=(0.0, -0.3, 1.0), fillcol=(0.14, 0.17, 0.34),
        rim=(0.2, -0.3, -1.0), rimcol=(0.5, 0.34, 0.28),
        scr=(0.0, 0.05, 1.0), scrcol=tuple(c * red for c in scol),
        amb_top=(0.06, 0.06, 0.12), amb_bot=(0.04, 0.03, 0.03),
        center=(0, 90, -40), extent=170, dist=420, far=900, bg_key=0.2, bg_fill=0.4, expo=0.92,
    )


# ---------------------------------------------------------------- panah merah 3D
_AR = {}


def _cone(r, h, n=32):
    V = [(r * math.cos(a), 0, r * math.sin(a)) for a in np.linspace(0, 2 * math.pi, n, endpoint=False)]
    V += [(0, -h, 0), (0, 0, 0)]
    F = []
    for i in range(n):
        j = (i + 1) % n
        F += [(i, n, j), (i, j, n + 1)]
    return Mesh(np.array(V, np.float32), np.array(F, np.int32))


def extras(t):
    if "arrow" not in _AR:
        _AR["shaft"] = rbox(6, 18, 4, 0.25, 16)
        _AR["head"] = _cone(9, 11)
    t_hit, t0 = 0.95, 0.55
    tip_y = 74.0
    if t < t0 or t >= 2.8:  # hanya di shot pembuka
        return []
    if t < t_hit:
        u = (t - t0) / (t_hit - t0)
        y = tip_y + 190 * (1 - u * u)
        wob = 0.0
        sq = 1.0
    else:
        y = tip_y
        dt = t - t_hit
        wob = 14 * math.exp(-dt * 3.2) * math.sin(dt * 18)
        sq = 1 - 0.18 * math.exp(-dt * 9) * math.cos(dt * 25)
    base = chain(T(6, y, -99), R("y", 25), R("z", wob), np.diag([1.25 / sq ** 0.5, 1.25 * sq, 1.25 / sq ** 0.5, 1]).astype(np.float32))
    red = (226, 42, 42)
    return [Part(_AR["head"], red, chain(base, T(0, 11, 0)), 90, gloss=0.45),
            Part(_AR["shaft"], red, chain(base, T(0, 11 + 9, 0)), 91, gloss=0.45)]
