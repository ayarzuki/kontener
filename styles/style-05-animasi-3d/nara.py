"""Nara: tokoh mahasiswi berhijab (orisinal) dengan rig sederhana dan wajah ekspresif.

Dibangun menghadap +z di ruang lokal; titik asal = tengah dudukan kursi. Satuan cm.
state: spine (pitch, yaw, roll), head (pitch, yaw, roll), gaze (x, y), lid (0 buka..1 tutup), wide (0..1),
brow (sudut, tinggi), mouth (bentuk), mouth_open (0..1), blush (0..1), armL/armR (pitch, roll, yaw, tekuk), handR_open.
"""
import math

import numpy as np

from cg import Mesh, Part, R, Sc, T, chain, sd_ellipsoid, sdf_mesh, smax, smin, sphere, superellipsoid, tube

SKIN = (222, 168, 128)
HIJAB = (206, 138, 140)
TOP = (52, 138, 128)
PANTS = (58, 70, 100)
BROW = (62, 40, 30)
LIP = (150, 66, 70)
MOUTH_IN = (90, 28, 36)
TONGUE = (226, 112, 118)
EYE_W = (250, 248, 244)
IRIS = (92, 58, 36)

_M = {}


def mesh(key, fn):
    if key not in _M:
        _M[key] = fn()
    return _M[key]


# ---------------------------------------------------------------- bentuk organik (SDF)
def head_sdf(P):
    d = sd_ellipsoid(P, (0, 13, 0), (12.5, 13.5, 12))
    d = smin(d, sd_ellipsoid(P, (4.6, 7.8, 6.6), (5.4, 5.0, 5.4)), 3.5)
    d = smin(d, sd_ellipsoid(P, (-4.6, 7.8, 6.6), (5.4, 5.0, 5.4)), 3.5)
    d = smin(d, sd_ellipsoid(P, (0, 3.8, 4.6), (6.6, 4.3, 6.0)), 3.5)
    d = smin(d, sd_ellipsoid(P, (0, 10.6, 11.6), (1.8, 1.6, 1.9)), 1.6)
    return d


def head_mesh():
    return sdf_mesh(head_sdf, (0, 11, 1), 20, 140, 96)


_SZ = {}


def surf(x, y):
    """Titik di permukaan depan kepala pada (x, y) + sudut kemiringan (derajat) untuk menempelkan fitur wajah."""
    k = (round(x, 2), round(y, 2))
    if k not in _SZ:
        lo, hi = 0.0, 25.0
        for _ in range(40):
            mid = (lo + hi) / 2
            if head_sdf(np.array([[x, y, mid]]))[0] < 0:
                lo = mid
            else:
                hi = mid
        z = lo
        e = 0.05
        g = np.array([(head_sdf(np.array([[x, y + e, z]])) - head_sdf(np.array([[x, y - e, z]])))[0],
                      (head_sdf(np.array([[x + e, y, z]])) - head_sdf(np.array([[x - e, y, z]])))[0]]) / (2 * e)
        pitch = math.degrees(math.atan2(g[0], 1.0))
        yaw = math.degrees(math.atan2(g[1], 1.0))
        _SZ[k] = (z, pitch, yaw)
    return _SZ[k]


def hijab_mesh():
    def sdf(P):
        o = smin(sd_ellipsoid(P, (0, 14.2, -0.6), (14.6, 15.6, 14.0)), sd_ellipsoid(P, (0, 1.5, 0.5), (12.8, 9.5, 12.0)), 4.5)
        hole = sd_ellipsoid(P, (0, 10.8, 13.2), (9.4, 10.8, 9.2))
        return smax(o, -hole, 1.4)
    return sdf_mesh(sdf, (0, 11, -1), 24, 150, 100)


def drape_mesh():
    def sdf(P):
        d = sd_ellipsoid(P, (0, 0, 0), (17, 8.5, 13))
        d = smin(d, sd_ellipsoid(P, (0, -8, 5), (12.5, 11, 6.5)), 4)
        return d
    return sdf_mesh(sdf, (0, -3, 1), 20, 120, 80)


def torso_mesh():
    def sdf(P):
        d = sd_ellipsoid(P, (0, 12, 0), (13.5, 13, 10))
        d = smin(d, sd_ellipsoid(P, (0, 27, 0), (15, 11, 10.5)), 5)
        d = smin(d, sd_ellipsoid(P, (11.5, 33, 0), (6.5, 5.5, 6.5)), 4)
        d = smin(d, sd_ellipsoid(P, (-11.5, 33, 0), (6.5, 5.5, 6.5)), 4)
        return d
    return sdf_mesh(sdf, (0, 20, 0), 32, 120, 80)


def hand_mesh():
    def sdf(P):
        d = sd_ellipsoid(P, (0, -3.2, 0), (2.8, 3.6, 1.6))
        d = smin(d, sd_ellipsoid(P, (2.4, -1.6, 0.6), (0.9, 2.0, 0.9)), 0.8)
        return d
    return sdf_mesh(sdf, (0, -3, 0), 7, 60, 40)


# ---------------------------------------------------------------- wajah
def _arc(w, depth, n=7):
    return [(-w + 2 * w * k / (n - 1), -depth * (1 - ((2 * k / (n - 1)) - 1) ** 2), 0.0) for k in range(n)]


def face_parts(H, st):
    p = []
    gx, gy = st.get("gaze", (0.0, 0.0))
    lid = float(st.get("lid", 0.0))
    wide = float(st.get("wide", 0.0))
    for side in (-1, 1):
        ec = (side * 4.6, 13.2, 8.4)
        EM = chain(H, T(*ec))
        eye = mesh("eyeball", lambda: sphere(3.5, 36))
        p.append(Part(eye, EYE_W, chain(EM, Sc(1 + 0.06 * wide)), 1, gloss=0.85, sss=0.1))
        yaw = gx * 28 + side * 4
        pitch = -gy * 22
        IM = chain(EM, R("y", yaw), R("x", pitch))
        iris = mesh("iris", lambda: superellipsoid(2.15, 2.15, 0.7, 1, 1, 32, 18))
        p.append(Part(iris, IRIS, chain(IM, T(0, 0, 3.05)), 2, gloss=0.7))
        ring = mesh("iris_ring", lambda: superellipsoid(1.5, 1.5, 0.72, 1, 1, 28, 16))
        p.append(Part(ring, (150, 100, 60), chain(IM, T(0, 0, 3.1)), 3, gloss=0.6))
        pup = mesh("pupil", lambda: superellipsoid(1.0, 1.0, 0.7, 1, 1, 24, 14))
        ps = 1.0 + 0.25 * wide
        p.append(Part(pup, (14, 10, 10), chain(IM, T(0, 0, 3.3), Sc(ps, ps, 1)), 4, gloss=0.9))
        hl = mesh("hl", lambda: sphere(0.48, 14))
        p.append(Part(hl, (255, 255, 255), chain(IM, T(-0.9, 1.0, 3.75)), 5, emit=1.5, cast=False))
        hl2 = mesh("hl2", lambda: sphere(0.22, 10))
        p.append(Part(hl2, (255, 255, 255), chain(IM, T(0.9, -0.8, 3.7)), 6, emit=1.2, cast=False))
        # kelopak atas: kubah kulit yang berputar menutup
        dome = mesh("lid", lambda: _dome(3.78))
        ang = -85 + 85 * lid - 8 * wide
        p.append(Part(dome, SKIN, chain(EM, R("x", -ang - 5)), 7, sss=0.6))
        lash = mesh("lash", lambda: tube([(3.6 * math.cos(a), 0, 3.6 * math.sin(a)) for a in np.linspace(0.1, math.pi - 0.1, 9)], 0.32, 8))
        p.append(Part(lash, (40, 26, 22), chain(EM, R("x", -ang - 5), R("x", 90), T(0, 0, 0)), 8))
        low = mesh("lowlid", lambda: _dome(3.7, lower=True))
        p.append(Part(low, SKIN, chain(EM, R("x", 62)), 9, sss=0.6))
        # alis
        ba, bh = st.get("brow", (0.0, 0.0))
        bh = max(-0.6, min(0.5, bh))  # jangan sampai alis naik ke kain hijab
        bw = mesh("brow", lambda: tube(_arc(3.0, -0.6, 7), 0.5, 12, taper=0.5))
        bz, bp, byw = surf(side * 4.7, 17.9 + bh)
        p.append(Part(bw, BROW, chain(H, T(side * 4.7, 17.9 + bh, bz + 0.55), R("y", byw), R("x", -bp), R("z", -side * ba)), 10))
        if st.get("blush", 0) > 0.01:
            bl = mesh("blush", lambda: superellipsoid(2.2, 1.3, 0.6, 1, 1, 20, 12))
            b = float(st["blush"])
            col = tuple(int(s + (c - s) * b) for s, c in zip(SKIN, (238, 128, 128)))
            cz, cp, cyw = surf(side * 7.2, 9.4)
            p.append(Part(bl, col, chain(H, T(side * 7.2, 9.4, cz - 0.35), R("y", cyw), R("x", -cp)), 11, sss=0.8, cast=False))
    mz, mp, _ = surf(0.0, 6.4)
    p += mouth_parts(chain(H, T(0, 6.4, mz - 0.15), R("x", -mp)), st.get("mouth", "smile0"), float(st.get("mouth_open", 0)))
    return p


def _dome(r, lower=False):
    """Kubah setengah bola terbuka (untuk kelopak)."""
    nu, nv = 36, 14
    u = np.linspace(-math.pi, math.pi, nu, endpoint=False)
    v = np.linspace(0.0, math.pi / 2, nv) if not lower else np.linspace(-math.pi / 2, -0.25, nv)
    U, Vv = np.meshgrid(u, v)
    x = r * np.cos(Vv) * np.cos(U)
    y = r * np.sin(Vv)
    z = r * np.cos(Vv) * np.sin(U)
    V = np.stack([x, y, z], -1).reshape(-1, 3)
    F = []
    for j in range(nv - 1):
        for i in range(nu):
            i2 = (i + 1) % nu
            a, b, c, d = j * nu + i, j * nu + i2, (j + 1) * nu + i, (j + 1) * nu + i2
            F += [(a, b, c), (b, d, c)]
    return Mesh(V, np.array(F, np.int32))


def mouth_parts(M, shape, op):
    p = []
    if op > 0.05 or shape in ("O", "A", "grin_open"):
        o = max(op, 0.5)
        w, h = {"O": (1.4, 1.7), "A": (2.6, 1.9), "grin_open": (3.4, 1.6)}.get(shape, (2.4, 1.6))
        m = mesh(("mo", shape), lambda: superellipsoid(w, h, 0.9, 1, 1, 30, 18))
        p.append(Part(m, MOUTH_IN, chain(M, Sc(1, 0.35 + 0.65 * o, 1)), 20, gloss=0.3))
        tg = mesh("tongue", lambda: superellipsoid(1.4, 0.7, 0.6, 1, 1, 18, 10))
        p.append(Part(tg, TONGUE, chain(M, T(0, -h * 0.55 * (0.35 + 0.65 * o), 0.4)), 21, gloss=0.4))
        if shape == "grin_open":
            th = mesh("teeth", lambda: superellipsoid(2.6, 0.45, 0.6, 1, 1, 20, 10))
            p.append(Part(th, (250, 250, 246), chain(M, T(0, h * 0.62 * (0.35 + 0.65 * o), 0.45)), 22, gloss=0.5))
        return p
    if shape == "smile":
        pts = _arc(2.6, 1.1)
    elif shape == "smile0":
        pts = _arc(1.9, 0.45)
    elif shape == "frown":
        pts = [(x, -y - 1.0, z) for x, y, z in _arc(1.9, 0.7)]
    elif shape == "wavy":
        pts = [(-2.0, 0, 0), (-1.0, 0.35, 0), (0, -0.1, 0), (1.0, 0.35, 0), (2.0, 0, 0)]
    else:
        pts = [(-1.6, 0, 0), (1.6, 0, 0)]
    m = mesh(("ml", shape), lambda: tube(pts, 0.42, 10, smooth=len(pts) > 2))
    p.append(Part(m, LIP, M, 23, gloss=0.3))
    return p


# ---------------------------------------------------------------- tubuh
def arm_parts(C, side, ang, top=None, cuffc=None):
    pitch, roll, yaw, bend = ang
    top = TOP if top is None else top
    cuffc = (40, 118, 110) if cuffc is None else cuffc
    p = []
    S = chain(C, T(side * 14, 34, 0), R("y", side * yaw), R("z", side * roll), R("x", -pitch))
    up = mesh("uparm", lambda: tube([(0, 0, 0), (0, -17, 0)], 4.3, 18, smooth=False))
    p.append(Part(up, top, S, 30, bump=0.1))
    sh = mesh("shoulderball", lambda: sphere(4.6, 24))
    p.append(Part(sh, top, S, 31, bump=0.1))
    E = chain(S, T(0, -17, 0), R("x", -bend))
    el = mesh("elbow", lambda: sphere(3.9, 20))
    p.append(Part(el, top, E, 32, bump=0.1))
    fo = mesh("forearm", lambda: tube([(0, 0, 0), (0, -14, 0)], 3.7, 18, smooth=False, taper=0.0))
    p.append(Part(fo, top, E, 33, bump=0.1))
    cuff = mesh("cuff", lambda: tube([(0, -13, 0), (0, -15.2, 0)], 3.9, 18, smooth=False))
    p.append(Part(cuff, cuffc, E, 34, bump=0.1))
    hm = mesh("hand", hand_mesh)
    HM = chain(E, T(0, -15, 0), Sc(-1 if side < 0 else 1, 1, 1))
    p.append(Part(hm, SKIN, HM, 35, sss=0.7))
    return p, HM


def nara(M, st, t=0.0):
    p = []
    top = tuple(st.get("top_col", TOP))
    hij = tuple(st.get("hijab_col", HIJAB))
    pants = tuple(st.get("pants_col", PANTS))
    cuffc = tuple(int(c * 0.85) for c in top)
    sp, sy, sr = st.get("spine", (0, 0, 0))
    hp, hy, hr = st.get("head", (0, 0, 0))
    bounce = float(st.get("bounce", 0.0))
    # kaki (duduk, mengarah ke depan)
    for side in (-1, 1):
        th = mesh("thigh", lambda: tube([(0, 0, 0), (0, 0, 34)], 6.2, 18, smooth=False))
        p.append(Part(th, pants, chain(M, T(side * 7.5, 6, -4)), 40, bump=0.08))
        sh = mesh("shin", lambda: tube([(0, 0, 0), (0, -40, 0)], 5.0, 16, smooth=False))
        p.append(Part(sh, pants, chain(M, T(side * 7.5, 6, 30)), 41, bump=0.08))
    C = chain(M, T(0, 2 + bounce, -2), R("y", sy), R("z", sr), R("x", sp))
    tm = mesh("torso", torso_mesh)
    p.append(Part(tm, top, C, 42, bump=0.1))
    dr = mesh("drape", drape_mesh)
    p.append(Part(dr, hij, chain(C, T(0, 37, 0.5)), 43, bump=0.04))
    H = chain(C, T(0, 39, 1.5), R("y", hy), R("z", hr), R("x", hp))
    hm = mesh("head", head_mesh)
    p.append(Part(hm, SKIN, H, 44, sss=1.0, gloss=0.08))
    hj = mesh("hijab", hijab_mesh)
    p.append(Part(hj, hij, H, 45, bump=0.04))
    p += face_parts(H, st)
    if st.get("sweat", 0) > 0:
        ph = (t * 0.6) % 1.0
        sx, sy = 7.6, 15.6 - 4.5 * ph
        dz, dp, dyw = surf(sx, sy)
        drop = mesh("sweat2", lambda: superellipsoid(1.4, 2.1, 1.0, 1, 1, 16, 12))
        p.append(Part(drop, (150, 210, 245), chain(H, T(sx, sy, dz + 0.3)), 46, gloss=0.9, emit=0.15, cast=False))
    hands = {}
    for side, key in ((-1, "armL"), (1, "armR")):
        ap, hmx = arm_parts(C, side, st.get(key, (20, 10, 0, 30)), top, cuffc)
        p += ap
        hands[key] = hmx
    st["_hands"] = hands
    st["_head"] = H
    return p
