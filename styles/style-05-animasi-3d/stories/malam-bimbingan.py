"""Film pendek tanpa dialog: "Malam Sebelum Bimbingan" (±32 dtk).

Shot, pose Nara, dan keadaan dunia (siang/malam, layar, HP, jam) per waktu.
Keyframe: [(t, nilai), ...], interpolasi halus (smoothstep). Nilai boleh tuple.
"""
import math

NARA_POS = (0, 48, -14)
END_T = 27.5

SHOTS = [
    dict(name="lebar-malam", t0=0.0, t1=4.0, eye0=(80, 165, -215), eye1=(66, 156, -196), tgt=(-6, 92, -24), fov=36, blur=2.0, hide_front=True),
    dict(name="wajah-lelah", t0=4.0, t1=8.2, eye0=(14, 108, -112), eye1=(10, 107, -106), tgt=(0, 99, -24), fov=30, blur=5),
    dict(name="bahu-layar", t0=8.2, t1=11.2, eye0=(52, 140, 30), eye1=(46, 134, 22), tgt=(-2, 88, -70), fov=30, blur=4),
    dict(name="wajah-terang", t0=11.2, t1=15.0, eye0=(10, 108, -112), eye1=(6, 107, -102), tgt=(0, 100, -24), fov=29, blur=5),
    dict(name="timelapse", t0=15.0, t1=19.2, eye0=(70, 160, -205), eye1=(70, 160, -205), tgt=(-6, 92, -24), fov=36, blur=2.0, hide_front=True),
    dict(name="hp", t0=19.2, t1=22.0, eye0=(35, 113, -34), eye1=(33, 107, -38), tgt=(28, 75.3, -54), fov=24, blur=6),
    dict(name="sorak", t0=22.0, t1=27.5, eye0=(0, 122, -124), eye1=(0, 120, -116), tgt=(0, 102, -16), fov=40, blur=4, hide_front=True),
    dict(name="penutup", t0=27.5, t1=32.5, eye0=(0, 120, -116), eye1=(0, 128, -168), tgt=(0, 102, -16), fov=40, blur=4, hide_front=True),
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
            if isinstance(va, str):
                return va if u < 0.5 else vb
            return va + (vb - va) * u
    return keys[-1][1]


def step(keys, t):
    v = keys[0][1]
    for a, val in keys:
        if t >= a:
            v = val
    return v


# pose lengan (pitch, roll, yaw, tekuk)
FOLD = (48, 10, -58, 22)
TYPE = (42, 14, -22, 52)
REST = (36, 16, -14, 46)
CHEEK = (70, 4, -30, 128)
CHEER = (168, -22, 0, 22)
DAY_T0, DAY_T1 = 15.6, 18.6
BLINKS = [5.3, 7.4, 9.9, 13.9, 16.4, 20.6, 24.9, 29.1, 31.0]


def nara_state(t):
    st = {}
    st["spine"] = K([(0, (34, 0, 0)), (3.5, (34, 0, 0)), (5.0, (12, 0, 3)), (11.0, (12, 0, 0)), (12.4, (6, 0, 0)), (15.0, (14, 0, 0)),
                     (19.2, (20, -6, 0)), (22.3, (20, -6, 0)), (22.8, (2, 0, 0)), (24.0, (-6, 0, 0))], t)
    st["head"] = K([(0, (42, 0, -4)), (3.5, (42, 0, -4)), (5.2, (8, 0, 6)), (11.0, (10, 0, 4)), (12.2, (2, 0, 0)), (15.0, (12, 0, 0)),
                    (19.2, (34, -10, 0)), (22.3, (34, -10, 0)), (22.8, (2, 0, 0)), (24.0, (-6, 0, 5)), (25.0, (-6, 0, -5)),
                    (26.0, (-6, 0, 5)), (27.0, (-4, 0, 0))], t)
    st["gaze"] = K([(0, (0, -0.2)), (6.4, (0.0, -0.25)), (12.2, (0.0, -0.18)), (19.2, (0.35, -0.7)), (22.6, (0.0, 0.05))], t)
    lid = K([(0, 1.0), (3.8, 1.0), (4.8, 0.45), (11.4, 0.4), (11.9, 0.0), (15.0, 0.12), (19.2, 0.2), (22.3, 0.0), (23.8, 0.0), (24.3, 0.35)], t)
    for b in BLINKS:
        if 0 <= t - b < 0.14:
            lid = max(lid, 1.0 - abs(t - b - 0.07) / 0.07 * 0.4)
    st["lid"] = lid
    st["wide"] = K([(0, 0.0), (11.6, 0.0), (12.0, 1.0), (13.6, 0.4), (22.2, 0.0), (22.5, 1.0), (23.8, 0.6), (24.3, 0.0)], t)
    st["brow"] = K([(0, (6, -0.2)), (5.0, (14, 0.3)), (8.0, (16, 0.4)), (11.6, (-6, 1.2)), (13.4, (4, 0.6)), (15.0, (2, 0.2)),
                    (19.2, (6, 0.0)), (22.3, (-8, 1.3)), (23.8, (3, 0.8))], t)
    st["mouth"] = step([(0, "flat"), (5.6, "wavy"), (7.0, "frown"), (11.7, "O"), (13.2, "smile"), (15.0, "smile0"), (19.2, "flat"),
                        (22.3, "O"), (23.6, "grin_open")], t)
    st["mouth_open"] = K([(0, 0.0), (11.6, 0.0), (11.8, 0.6), (13.0, 0.5), (13.2, 0.0), (22.2, 0.0), (22.4, 0.9), (23.5, 0.7),
                          (23.7, 0.9)], t)
    st["blush"] = K([(0, 0.0), (12.6, 0.0), (13.6, 0.7), (15.0, 0.4), (23.6, 0.4), (24.2, 1.0)], t)
    armL = K([(0, FOLD), (3.5, FOLD), (5.2, REST), (9.0, REST), (9.4, TYPE), (11.2, TYPE), (12.0, REST), (14.0, REST), (15.0, TYPE),
              (19.2, TYPE), (22.3, TYPE), (22.6, REST), (23.5, REST), (23.9, CHEER)], t)
    armR = K([(0, FOLD), (3.5, FOLD), (5.2, REST), (9.0, REST), (9.4, TYPE), (11.2, TYPE), (12.0, REST), (14.0, REST), (15.0, TYPE),
              (19.2, TYPE), (22.3, TYPE), (22.6, REST), (23.5, REST), (23.9, CHEER)], t)
    typing = (9.4 <= t < 11.2) or (15.0 <= t < 19.0)
    if typing:
        sp = 11 if t >= 15 else 7
        armL = (armL[0], armL[1], armL[2], armL[3] + 7 * math.sin(t * sp * 6.28 / 6))
        armR = (armR[0], armR[1], armR[2], armR[3] + 7 * math.sin(t * sp * 6.28 / 6 + 2.1))
    if t >= 23.9:
        wave = 10 * math.sin((t - 23.9) * 7)
        armL = (armL[0], armL[1] + wave, armL[2], armL[3])
        armR = (armR[0], armR[1] - wave, armR[2], armR[3])
        st["bounce"] = abs(math.sin((t - 23.9) * 5.5)) * 4
    if 15.0 <= t < 19.0:
        st["head"] = (st["head"][0] + 3 * math.sin(t * 8), st["head"][1], st["head"][2])
    st["armL"], st["armR"] = armL, armR
    return st


def world_state(t):
    day = ease((t - DAY_T0) / (DAY_T1 - DAY_T0))
    if t < 9.9:
        screen, app_p = "doc", 0.0
    else:
        screen, app_p = "app", min(1.0, (t - 9.9) / 1.6)
    hours = 2.0 + (t / 15.0) * 0.25 if t < DAY_T0 else 2.25 + (7.2 - 2.25) * ease((t - DAY_T0) / (DAY_T1 - DAY_T0))
    return dict(day=day, lamp=1.0 - ease((t - 16.8) / 1.2), screen=screen, app_p=app_p, phone=1 if t >= 19.8 else 0,
                clock_h=hours, crumpled=1.0 - ease((t - 16.0) / 2.0))


def light(t):
    d = ease((t - DAY_T0) / (DAY_T1 - DAY_T0))
    scr = 0.0 if t < 4.5 else (0.3 if t < 9.9 else 0.3 + 0.25 * ease((t - 9.9) / 1.0))
    scr *= (1 - 0.6 * d)
    scr_col = (0.25, 0.27, 0.3) if t < 9.9 else (0.12, 0.62, 0.55)

    def mix(a, b):
        return tuple(x + (y - x) * d for x, y in zip(a, b))
    return dict(
        key=mix((0.6, -0.35, 0.72), (0.25, -0.55, 0.8)),
        keycol=mix((1.25, 0.82, 0.48), (1.22, 1.04, 0.82)),
        fill=mix((0.0, -0.3, 1.0), (-0.5, -0.2, 0.8)),
        fillcol=mix((0.16, 0.2, 0.4), (0.3, 0.38, 0.5)),
        rim=mix((0.2, -0.3, -1.0), (0.1, -0.2, -1.0)),
        rimcol=mix((0.55, 0.38, 0.3), (0.7, 0.65, 0.6)),
        scr=(0.0, 0.05, 1.0), scrcol=tuple(c * scr for c in scr_col),
        amb_top=mix((0.05, 0.06, 0.12), (0.26, 0.28, 0.34)),
        amb_bot=mix((0.04, 0.03, 0.03), (0.18, 0.14, 0.11)),
        center=(0, 90, -40), extent=170, dist=420, far=900,
        bg_key=0.18 + 0.82 * d, bg_fill=0.35 + 0.65 * d, expo=0.88 + 0.12 * d,
    )
