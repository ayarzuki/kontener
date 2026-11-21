"""Skit 'Sidang Skripsi' — koreografi, kamera, dan pose per waktu.

Teks dialog + timing-nya dibaca dari file konten (key "lines"). Kalau timing dialog
digeser jauh, sesuaikan juga waktu-waktu adegan di file ini (shot, gestur, jalan).
Cast: "bu" (Bu Dosen, berhijab), "pak" (Pak Dosen, batik), "mhs" (mahasiswa).
"""
import math

import numpy as np

from engine import M4

LINES = []  # (who, text, t0, t1) — diisi configure()
END_T = 28.85
TOTAL = 32.5
CAST = {"pak": "pak", "bu": "bu", "mhs": "student"}

# t0, t1, eye0, tgt0, eye1, tgt1, fov, set
SHOTS = [
    (0.0, 2.65, (-0.42, 1.66, 1.98), (0.02, 1.0, -0.9), (-0.36, 1.62, 1.82), (0.02, 1.0, -0.9), 46, "room"),
    (2.65, 4.7, (0.42, 1.25, 0.1), (0.55, 1.03, -0.95), (0.43, 1.25, 0.0), (0.55, 1.03, -0.95), 36, "room"),
    (4.7, 6.7, (-0.36, 1.27, 0.2), (-0.55, 1.0, -0.95), (-0.37, 1.27, 0.1), (-0.55, 1.0, -0.95), 40, "room"),
    (6.7, 9.1, (-0.03, 1.25, -0.08), (0.12, 1.03, 0.97), (-0.02, 1.25, 0.0), (0.12, 1.03, 0.97), 36, "room"),
    (9.1, 11.25, (0.92, 1.42, -1.62), (0.6, 0.86, -0.3), (0.88, 1.38, -1.52), (0.6, 0.86, -0.3), 40, "room"),
    (11.25, 12.9, (-0.4, 1.25, 0.05), (-0.55, 1.04, -0.95), (-0.41, 1.25, -0.1), (-0.55, 1.04, -0.95), 36, "room"),
    (12.9, 15.1, (-0.4, 1.36, 0.42), (-0.52, 1.04, -0.95), (-0.41, 1.34, 0.28), (-0.52, 1.04, -0.95), 42, "room"),
    (15.1, 16.6, (-0.03, 1.25, -0.06), (0.12, 1.03, 0.97), (-0.02, 1.25, 0.04), (0.12, 1.03, 0.97), 34, "room"),
    (16.6, 18.0, (0.12, 1.31, 0.75), (0.12, 0.89, 0.29), (0.12, 1.27, 0.69), (0.12, 0.89, 0.29), 52, "room"),
    (18.0, 21.0, (1.85, 2.45, 2.65), (-0.45, 0.65, 0.1), (1.75, 2.4, 2.55), (-0.45, 0.65, 0.1), 58, "room"),
    (21.0, 22.1, (0.32, 1.5, -0.42), (-0.05, 1.28, 1.25), (0.32, 1.48, -0.36), (-0.05, 1.28, 1.25), 52, "room"),
    (22.1, 23.9, (0.26, 1.22, -0.08), (0.4, 1.05, 0.97), (0.27, 1.22, 0.0), (0.4, 1.05, 0.97), 36, "room"),
    (23.9, 26.6, (0.1, 1.33, -0.74), (0.1, 1.07, 0.97), (0.1, 1.31, -0.62), (0.1, 1.07, 0.97), 50, "room"),
    (26.6, END_T, (0.3, 1.28, 0.15), (0.47, 1.03, -0.97), (0.31, 1.28, 0.05), (0.47, 1.03, -0.97), 42, "room"),
    (END_T, TOTAL, (0.0, 1.32, 2.15), (0.0, 1.55, -1.6), (0.0, 1.36, 1.85), (0.0, 1.58, -1.6), 44, "hill"),
]

POS = {"pak": np.array([-0.55, 0, -0.97]), "bu": np.array([0.55, 0, -0.97]), "mhs": np.array([0.12, 0, 0.97])}
PAK_SEAT2 = np.array([-0.2, 0, 0.97])
WALK = [(-0.55, -0.97), (-1.55, -0.97), (-1.55, 1.52), (-0.3, 1.52)]
T_STAND, T_WALK0, T_WALK1 = 18.05, 18.45, 20.85
T_SHIFT0, T_SHIFT1 = 22.3, 22.9
T_PAKSIT = 23.0
SEEDS = {"bu": 1, "pak": 2, "mhs": 3}
HEADS = {"pak": (-0.55, 1.21, -0.92), "bu": (0.55, 1.21, -0.92), "mhs": (0.12, 1.21, 0.92)}
SEAT_ARMS = dict(armL=(-58, 8, 18, -32), armR=(-58, 8, 18, -32))


def configure(cfg):
    LINES[:] = [(l["who"], l["text"], float(l["t0"]), float(l["t1"])) for l in cfg["lines"]]


def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def smooth(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


def lerp(a, b, p):
    return a + (b - a) * p


def talk(t, seed):
    v = 0.55 + 0.45 * math.sin(t * 2 * math.pi * 4.7 + seed) * math.sin(t * 2 * math.pi * 2.3 + seed * 1.7)
    v = abs(math.sin(t * 2 * math.pi * 3.4 + seed)) * 0.75 + 0.25 * v
    return clamp(v)


def speaking(who, t):
    for sp, txt, t0, t1 in LINES:
        if sp == who and t0 <= t <= t1:
            e = min(t - t0, t1 - t) / 0.08
            return clamp(e) * talk(t, SEEDS.get(who, 0))
    return 0.0


def blink(t, seed):
    period = 3.1 + (seed % 5) * 0.37
    return 1.0 if (t + seed * 0.71) % period < 0.11 else 0.0


def walk_state(t):
    pts = [np.array(p, float) for p in WALK]
    seg = [np.linalg.norm(pts[i + 1] - pts[i]) for i in range(len(pts) - 1)]
    total = sum(seg)
    u = clamp((t - T_WALK0) / (T_WALK1 - T_WALK0))
    u = u * u * (3 - 2 * u) * 0.25 + u * 0.75
    d = u * total
    acc = 0
    for i, L in enumerate(seg):
        if d <= acc + L or i == len(seg) - 1:
            f = (d - acc) / L
            p = pts[i] + (pts[i + 1] - pts[i]) * clamp(f)
            dirv = pts[i + 1] - pts[i]
            yaw = math.degrees(math.atan2(dirv[0], dirv[1]))
            if i + 1 < len(seg) and f > 0.8:
                dn = pts[i + 2] - pts[i + 1]
                yn = math.degrees(math.atan2(dn[0], dn[1]))
                yaw += ((yn - yaw + 180) % 360 - 180) * smooth((f - 0.8) / 0.2) * 0.5
            if i > 0 and f < 0.2:
                dp = pts[i] - pts[i - 1]
                yp = math.degrees(math.atan2(dp[0], dp[1]))
                yaw += ((yp - yaw + 180) % 360 - 180) * (1 - smooth(f / 0.2)) * 0.5
            return p, yaw, d
        acc += L


def head_aim(pos, yaw, sitting, target, lean=6):
    head = np.array([pos[0], 1.21 if sitting else 1.62, pos[2]])
    v = np.array(target, float) - head
    a = math.radians(-yaw)
    lx = v[0] * math.cos(a) + v[2] * math.sin(a)
    lz = -v[0] * math.sin(a) + v[2] * math.cos(a)
    hyaw = math.degrees(math.atan2(lx, lz))
    hp = -math.degrees(math.atan2(v[1], math.hypot(lx, lz)))
    gx = clamp((hyaw - clamp(hyaw, -45, 45)) / 25, -1, 1)
    return (clamp(hp - lean * 0.5, -25, 30), clamp(hyaw, -50, 50), 0), (gx, clamp(-hp / 30, -0.8, 0.8))


def mhs_x(t):
    return lerp(0.12, 0.4, smooth((t - T_SHIFT0) / (T_SHIFT1 - T_SHIFT0)))


def states(t):
    out = {}
    mpos = np.array([mhs_x(t), 0, 0.97])
    look = HEADS["pak"]
    if t < 4.7:
        look = HEADS["bu"]
    if 9.1 <= t < 12.9:
        look = (0.3, 1.1, -0.6)
    if t >= 18.0:
        pk = states_pak(t)[0]
        look = (pk[0], 1.62 if t < T_PAKSIT else 1.2, pk[2])
    hd, gz = head_aim(mpos, 180, True, look)
    p = dict(sit=1, head=hd, gaze=gz, blink=blink(t, 3), mouth=speaking("mhs", t), **SEAT_ARMS)
    if 6.7 <= t < 9.1:
        p.update(smile=0.45, brow=0.1)
        k = smooth((t - 6.9) / 0.4) * (1 - smooth((t - 8.6) / 0.4))
        p["armR"] = (lerp(-58, -64, k), 8, 14, lerp(-32, -70, k))
    if 15.1 <= t < 16.6:
        k = smooth((t - 15.25) / 0.3) * (1 - smooth((t - 16.3) / 0.3))
        p.update(smile=0.25, brow=0.25 * k)
        p["head"] = (hd[0], hd[1], 7 * k)
        p["armL"] = (-58, 8, lerp(18, 10, k), lerp(-32, -62, k))
        p["armR"] = (-58, 8, lerp(18, 10, k), lerp(-32, -62, k))
    if 22.1 <= t < 23.9:
        p.update(eyes_wide=0.35, brow=0.7, brow_ang=-5)
    if t >= 23.9:
        p.update(smile=0.15)
    out["mhs"] = (mpos, 180.0, p)

    bpos = POS["bu"]
    blook = HEADS["mhs"]
    if 2.65 <= t < 4.7:
        blook = (-0.1, 1.15, 0.2)
    if 9.1 <= t < 12.9:
        blook = (0.6, 0.9, -0.38)
    if 18.0 <= t < 23.9:
        pk = states_pak(t)[0]
        blook = (pk[0], 1.5, pk[2])
    if t >= 26.6:
        blook = (0.46, 1.25, -0.25)
    hd, gz = head_aim(bpos, 0, True, blook)
    p = dict(sit=1, head=hd, gaze=gz, blink=blink(t, 1), mouth=speaking("bu", t), **SEAT_ARMS)
    if t < 2.65:
        p.update(brow_ang=7, brow=0.0, brow_r_extra=0.5)
    if 2.65 <= t < 4.7:
        p.update(smile=0.3, brow_r_extra=0.8, brow_ang=4)
    if 9.1 <= t < 12.9:
        ty = math.sin(t * 2 * math.pi * 6) * 4
        p["armL"] = (-60, 8, 24, -30 + ty)
        p["armR"] = (-60, 8, 24, -30 - ty)
        if t > 9.9:
            p.update(eyes_wide=0.5, brow=0.8)
    if t >= 26.6:
        p.update(blink=max(p["blink"], 0.38), brow=-0.25, brow_ang=3)
    out["bu"] = (bpos, 0.0, p)
    out["pak"] = states_pak(t)
    return out


def states_pak(t):
    pos = POS["pak"].copy()
    if t < T_STAND:
        look = HEADS["mhs"]
        if 2.65 <= t < 4.7:
            look = HEADS["bu"]
        if 9.1 <= t < 12.9:
            look = (0.55, 0.95, -0.4)
        hd, gz = head_aim(pos, 0, True, look)
        p = dict(sit=1, head=hd, gaze=gz, blink=blink(t, 2), mouth=speaking("pak", t), **SEAT_ARMS)
        if 4.7 <= t < 6.7:
            k = smooth((t - 4.85) / 0.3) * (1 - smooth((t - 6.3) / 0.3))
            p.update(brow=-0.15, brow_ang=8 * k)
            p["armR"] = (lerp(-58, -30, k), lerp(8, 30, k), lerp(18, 0, k), lerp(-32, -105, k))
        if 11.25 <= t < 12.9:
            p.update(eyes_wide=0.9, brow=1.0, lean=lerp(6, -2, smooth((t - 11.3) / 0.3)))
        if 12.9 <= t < 15.1:
            ln = lerp(6, 16, smooth((t - 12.95) / 0.5))
            p.update(lean=ln, brow=0.5, brow_ang=-4)
            p["head"] = (hd[0] - (ln - 6) * 1.1, hd[1], hd[2])
        if 15.1 <= t < 18.0:
            p.update(eyes_wide=0.4, brow=0.6, lean=10)
        return pos, 0.0, p
    if t < T_WALK0:
        k = smooth((t - T_STAND) / (T_WALK0 - T_STAND))
        p = dict(sit=1 - k, head=(5, 0, 0), blink=0, mouth=0, brow=-0.2, brow_ang=8,
                 armL=(lerp(-58, -10, k), 8, 10, lerp(-32, -10, k)), armR=(lerp(-58, -10, k), 8, 10, lerp(-32, -10, k)))
        return pos, lerp(0, -40, k), p
    if t < T_PAKSIT:
        wp, wyaw, dist = walk_state(t)
        pos = np.array([wp[0], 0, wp[1]])
        moving = T_WALK0 <= t < T_WALK1
        ph = dist / 1.15 * 2 * math.pi
        sw = 30 * math.sin(ph) if moving else 0
        bob = -0.025 * abs(math.sin(ph)) if moving else 0
        p = dict(sit=0, hip_dy=bob, lean=8 if moving else 2, blink=blink(t, 2), brow=-0.25, brow_ang=8,
                 legL=(-sw, 35 * max(0, math.sin(ph)) + 5), legR=(sw, 35 * max(0, -math.sin(ph)) + 5),
                 armL=(sw * 0.7, 8, 0, -15), armR=(-sw * 0.7, 8, 0, -15))
        yaw = wyaw
        if not moving:
            d = np.array([mhs_x(t), 0, 0.97]) - pos
            ty = math.degrees(math.atan2(d[0], d[2]))
            yaw = yaw + ((ty - yaw + 180) % 360 - 180) * smooth((t - T_WALK1) / 0.3)
            p["mouth"] = speaking("pak", t)
            p["head"], p["gaze"] = head_aim(pos, yaw, False, (mhs_x(t), 1.2, 0.97))
            if 21.0 <= t < 22.1:
                k2 = smooth((t - 21.05) / 0.25) * (1 - smooth((t - 21.8) / 0.3))
                p["armR"] = (lerp(0, -45, k2), 8, lerp(0, 30, k2), lerp(-15, -40, k2))
                p.update(smile=0.3)
        else:
            p["head"] = (6, 0, 0)
            p["mouth"] = 0
        return pos, yaw, p
    pos = PAK_SEAT2.copy()
    hd, gz = head_aim(pos, 180, True, (-0.15, 0.85, 0.45))
    ty = math.sin(t * 2 * math.pi * 5.5) * 4
    p = dict(sit=1, head=hd, gaze=gz, blink=blink(t, 2), mouth=speaking("pak", t), lean=12,
             armL=(-60, 8, 30, -30 + ty), armR=(-60, 8, 30, -30 - ty), smile=0.45, brow=0.2, brow_ang=-7)
    if 24.0 <= t < 26.6:
        hd2, gz2 = head_aim(pos, 180, True, (0.42, 1.2, 0.97))
        k = smooth((t - 24.0) / 0.3)
        p["head"] = tuple(lerp(a, b, k) for a, b in zip(hd, hd2))
        p["gaze"] = gz2
    return pos, 180.0, p


def chairs_at(t):
    return [(-0.55, -0.97, 0), (0.55, -0.97, 0), (mhs_x(t), 0.97, 180), (-0.78 if t < T_PAKSIT else -0.2, 0.97, 180)]


def lap_at(t):
    return (mhs_x(t), 0.4, 0) if t < 23.5 else (0.1, 0.4, -14)


def draw(world, t, set_name):
    """Gambar semua objek untuk waktu t (kamera sudah di-set oleh style)."""
    gl = world.gl
    if set_name == "room":
        world.room.draw(gl, chairs_at(t), lap_at(t))
        for name, (pos, yaw, p) in states(t).items():
            ch = world.cast[name]
            ch.pos[:] = pos
            ch.yaw = yaw
            ch.pose(p)
            ch.draw(gl)
    else:
        world.hill.draw(gl)
        ch = world.hero
        ch.pos[:] = (0, 0.58, -1.6)
        ch.yaw = 0
        sway = math.sin(t * 1.7) * 1.5
        ch.pose(dict(sit=0, head=(4, 0, sway), smile=0.55, blink=blink(t, 3), lean=-2, gaze=(0, -0.2),
                     armL=(-28, 6, 16, -62), armR=(-28, 6, 16, -62), legL=(0, 2), legR=(0, 2)))
        ch.draw(gl)
        world.lap_end.draw(gl, M4((0, 0.58 + 1.13, -1.6 + 0.36), (-6, 0, 0)))
