"""Karakter low-poly ber-rig sederhana (FK)."""
import math

import numpy as np

from engine import (P_BATIK, P_FABRIC, P_HAIR, P_PLAIN, P_SKIN, M4, Mesh, Obj, box, circle2d, cyl,
                    ellipsoid_pts, hull, poly, quad, tbox)

ZF = 0.098  # face plane (head-local z)


class Bone:
    def __init__(self, name, parent, offset):
        self.name, self.parent = name, parent
        self.offset = np.array(offset, float)
        self.dt = np.zeros(3)
        self.rot = np.zeros(3)
        self.scale = np.ones(3)
        self.obj = Obj()


SPECS = {
    "student": dict(skin=(214, 160, 118), hair=(26, 21, 20), top=(238, 238, 234), top_pat=P_FABRIC,
                    pants=(30, 31, 40), shoes=(18, 16, 16), style="spiky", glasses=False, outfit="shirt_tie",
                    brow=(30, 24, 22), iris=(62, 40, 26)),
    "pak": dict(skin=(190, 134, 94), hair=(208, 208, 212), top=(104, 56, 26), top_pat=P_BATIK,
                pants=(44, 40, 38), shoes=(36, 24, 18), style="swept", glasses=True, outfit="batik",
                brow=(170, 168, 170), iris=(58, 38, 24), mustache=True, belly=True, frame=(32, 30, 40)),
    "bu": dict(skin=(222, 172, 132), hair=(40, 30, 28), top=(38, 50, 104), top_pat=P_FABRIC,
               pants=(38, 50, 104), shoes=(28, 22, 24), style="hijab", glasses=True, outfit="hijab",
               hijab=(156, 62, 86), brow=(55, 38, 32), iris=(52, 34, 22), frame=(110, 40, 60)),
}


def head_mesh(sp):
    skin = sp["skin"]
    pts = []
    for sx in (-1, 1):
        for (x, y) in [(0.063, 0.265), (0.071, 0.225), (0.07, 0.185), (0.063, 0.145), (0.046, 0.105), (0.02, 0.083)]:
            pts.append((sx * x, y, ZF))
        pts += [(sx * 0.08, 0.15, 0.03), (sx * 0.07, 0.11, 0.0), (sx * 0.045, 0.085, -0.01), (sx * 0.05, 0.12, -0.07)]
    pts.append((0, 0.078, ZF - 0.008))
    pts += ellipsoid_pts((0, 0.225, 0.0), (0.09, 0.105, 0.1), keep=lambda x, y, z: z < 0.055)
    m = hull(pts, skin, P_SKIN)
    m.add(hull([(0, 0.205, ZF), (-0.012, 0.15, ZF), (0.012, 0.15, ZF), (0, 0.148, ZF + 0.026),
                (0, 0.165, ZF + 0.03), (-0.006, 0.18, ZF + 0.012), (0.006, 0.18, ZF + 0.012)], skin, P_SKIN))
    for s in (-1, 1):
        m.add(hull([(s * 0.083, 0.17, 0.0), (s * 0.083, 0.215, 0.0), (s * 0.083, 0.17, 0.035), (s * 0.083, 0.215, 0.03),
                    (s * 0.1, 0.18, 0.01), (s * 0.1, 0.21, 0.015)], [c * 0.92 for c in skin], P_SKIN))
    m.add(cyl((0, -0.02, -0.005), 0.046, 0.12, skin, P_SKIN, segs=7))
    return m


def hair_mesh(sp):
    hc = sp["hair"]
    style = sp["style"]
    m = Mesh()
    if style == "hijab":
        hj = sp["hijab"]
        pts = ellipsoid_pts((0, 0.228, -0.01), (0.114, 0.13, 0.124), keep=lambda x, y, z: z < 0.075)
        for s in (-1, 1):
            pts += [(s * 0.085, 0.285, 0.088), (s * 0.094, 0.2, 0.086), (s * 0.086, 0.13, 0.082), (s * 0.06, 0.074, 0.08),
                    (s * 0.075, 0.03, 0.02), (s * 0.085, 0.05, -0.07)]
        pts += [(0, 0.312, 0.09), (0, 0.052, 0.086), (0, 0.02, 0.05)]
        m.add(hull(pts, hj, P_FABRIC))
        return m
    cap = ellipsoid_pts((0, 0.236, -0.006), (0.1, 0.112, 0.11), keep=lambda x, y, z: y > 0.205 and z < 0.08)
    for s in (-1, 1):
        cap += [(s * 0.066, 0.268, ZF + 0.004), (s * 0.08, 0.235, 0.06), (s * 0.085, 0.2, 0.02), (s * 0.07, 0.14, -0.06),
                (s * 0.09, 0.19, -0.03)]
    cap += [(0, 0.285, ZF + 0.012), (0, 0.13, -0.088)]
    if style == "swept":
        for s in (-1, 1):
            cap += [(s * 0.05, 0.33, 0.07), (s * 0.08, 0.3, 0.04)]
        cap += [(0, 0.345, 0.06), (0.02, 0.29, ZF + 0.02)]
    m.add(hull(cap, hc, P_HAIR))
    if style == "spiky":
        spikes = [
            ((0.0, 0.29, 0.08), (0.05, -0.45, 1.0), 0.07), ((-0.045, 0.285, 0.075), (-0.35, -0.5, 1.0), 0.065),
            ((0.045, 0.285, 0.075), (0.4, -0.45, 1.0), 0.065), ((-0.03, 0.33, 0.03), (-0.25, 1.0, 0.6), 0.055),
            ((0.03, 0.33, 0.03), (0.3, 1.0, 0.55), 0.055), ((0.0, 0.34, -0.03), (0.05, 1.0, -0.35), 0.05),
            ((-0.065, 0.31, -0.01), (-1.0, 0.55, -0.15), 0.055), ((0.065, 0.31, -0.01), (1.0, 0.55, -0.15), 0.055),
            ((-0.04, 0.29, -0.075), (-0.5, 0.35, -1.0), 0.055), ((0.04, 0.29, -0.075), (0.5, 0.35, -1.0), 0.055),
            ((0.0, 0.25, -0.1), (0.0, 0.0, -1.0), 0.05), ((-0.08, 0.27, 0.04), (-1.0, -0.35, 0.4), 0.045),
            ((0.08, 0.27, 0.04), (1.0, -0.35, 0.4), 0.045),
        ]
        for (b, d, ln) in spikes:
            b = np.array(b)
            d = np.array(d, float)
            d /= np.linalg.norm(d)
            a = np.cross(d, [0.3, 1, 0.2])
            a /= np.linalg.norm(a)
            c = np.cross(d, a)
            w = 0.034
            pts = [b + a * w, b - a * w * 0.6 + c * w, b - a * w * 0.6 - c * w, b - d * 0.02, b + d * ln]
            m.add(hull(pts, hc, P_HAIR))
    if sp.get("mustache"):
        pts = []
        for s in (-1, 1):
            pts += [(s * 0.03, 0.134, ZF + 0.006), (s * 0.012, 0.148, ZF + 0.012), (s * 0.026, 0.142, ZF + 0.01),
                    (s * 0.032, 0.128, ZF + 0.004)]
        pts += [(0, 0.14, ZF + 0.014), (0, 0.15, ZF + 0.01)]
        m.add(hull(pts, (150, 146, 148), P_HAIR))
    return m


def glasses_mesh(sp):
    col = sp.get("frame", (30, 30, 40))
    m = Mesh()
    z = ZF + 0.016
    t = 0.0042
    for s in (-1, 1):
        cx, cy, w, h = s * 0.037, 0.198, 0.044, 0.027
        m.add(box((cx, cy + h / 2, z), (w, t, t), col))
        m.add(box((cx, cy - h / 2, z), (w, t, t), col))
        m.add(box((cx - w / 2, cy, z), (t, h, t), col))
        m.add(box((cx + w / 2, cy, z), (t, h, t), col))
        m.add(hull([(s * 0.059, cy + 0.008, z), (s * 0.059, cy + 0.004, z), (s * 0.088, cy + 0.01, 0.0),
                    (s * 0.088, cy + 0.006, 0.0)] + [(s * 0.061, cy + 0.008, z - 0.003)], col))
    m.add(box((0, 0.203, z), (0.03, t, t), col))
    return m


def eye_mesh(sp):
    m = Mesh()
    sc = [(-0.016, 0.0), (-0.008, 0.0078), (0.009, 0.0082), (0.0165, 0.001), (0.009, -0.0062), (-0.008, -0.0066)]
    m.add(poly(sc, 0.0, (242, 240, 234)))
    m.add(quad((-0.0175, 0.0045, 0.0013), (0.0175, 0.0062, 0.0013), (0.0165, 0.0098, 0.0013), (-0.0165, 0.0085, 0.0013),
               (28, 20, 22)))
    return m


def iris_mesh(sp):
    m = Mesh()
    m.add(poly(circle2d(0, -0.0003, 0.0066, n=10), 0.0007, sp["iris"]))
    m.add(poly(circle2d(0, -0.0003, 0.0033, n=8), 0.0011, (10, 8, 10)))
    m.add(poly(circle2d(0.0024, 0.0022, 0.0014, n=6), 0.0014, (255, 255, 255)))
    return m


def brow_mesh(sp, side):
    return quad((-0.019, -0.003, 0), (0.019, -0.0015, 0), (0.019, 0.0035, 0), (-0.019, 0.003, 0), sp["brow"])


def mouth_mesh(sp):
    m = Mesh()
    pts = [(-0.02, 0.0), (-0.012, 0.006), (0.012, 0.006), (0.02, 0.0), (0.012, -0.010), (-0.012, -0.010)]
    m.add(poly(pts, 0.0, (92, 30, 36)))
    m.add(quad((-0.011, 0.0022, 0.0006), (0.011, 0.0022, 0.0006), (0.0105, 0.0058, 0.0006), (-0.0105, 0.0058, 0.0006),
               (236, 232, 222)))
    return m


def torso_mesh(sp):
    col, pat = sp["top"], sp["top_pat"]
    m = Mesh()
    bel = sp.get("belly")
    pts = []
    for s in (-1, 1):
        for c in (-1, 1):
            pts += [(s * 0.15, 0.0, c * 0.095), (s * 0.185, 0.38, c * 0.115), (s * 0.205, 0.47, c * 0.085),
                    (s * 0.13, 0.52, c * 0.075), (s * 0.06, 0.545, c * 0.05)]
            pts.append((s * (0.175 if bel else 0.16), 0.17, c * (0.13 if bel else 0.105)))
    if bel:
        pts.append((0, 0.16, 0.165))
    m.add(hull(pts, col, pat))
    if sp["outfit"] == "shirt_tie":
        for s in (-1, 1):
            m.add(hull([(s * 0.062, 0.55, 0.048), (s * 0.004, 0.5, 0.098), (s * 0.07, 0.49, 0.09), (s * 0.045, 0.565, 0.03),
                        (s * 0.02, 0.53, 0.085)], (250, 250, 248), P_FABRIC))
        tie = (24, 24, 30)
        m.add(box((0, 0.505, 0.098), (0.03, 0.03, 0.02), tie, P_FABRIC))
        m.add(hull([(-0.012, 0.495, 0.1), (0.012, 0.495, 0.1), (-0.02, 0.38, 0.126), (0.02, 0.38, 0.126),
                    (0, 0.495, 0.106), (0, 0.38, 0.131)], tie, P_FABRIC))
        m.add(hull([(-0.02, 0.38, 0.126), (0.02, 0.38, 0.126), (-0.024, 0.21, 0.118), (0.024, 0.21, 0.118),
                    (0, 0.18, 0.118), (0, 0.38, 0.131), (0, 0.21, 0.123)], tie, P_FABRIC))
        m.add(tbox(-0.015, 0.035, 0.31, 0.2, 0.31, 0.2, (22, 20, 22)))
    elif sp["outfit"] == "batik":
        for s in (-1, 1):
            m.add(hull([(s * 0.062, 0.55, 0.05), (s * 0.006, 0.505, 0.1), (s * 0.075, 0.49, 0.092), (s * 0.045, 0.568, 0.03)],
                       (70, 36, 16), P_FABRIC))
        for y in (0.44, 0.34, 0.24):
            m.add(box((0, y, 0.122 + (0.03 if (bel and y < 0.3) else 0)), (0.012, 0.012, 0.006), (226, 200, 150)))
    elif sp["outfit"] == "hijab":
        hj = sp["hijab"]
        pts = []
        for s in (-1, 1):
            for c in (-1, 1):
                pts += [(s * 0.215, 0.475, c * 0.1), (s * 0.12, 0.6, c * 0.09)]
            pts += [(s * 0.16, 0.34, 0.135), (s * 0.16, 0.36, -0.13)]
        pts += [(0, 0.27, 0.15), (0, 0.29, -0.14)]
        m.add(hull(pts, hj, P_FABRIC))
    return m


def arm_meshes(sp):
    col, pat, skin = sp["top"], sp["top_pat"], sp["skin"]
    up = tbox(-0.29, 0.0, 0.085, 0.09, 0.105, 0.1, col, pat)
    up.add(hull(ellipsoid_pts((0, -0.01, 0), (0.06, 0.05, 0.058), lats=(-30, 20, 60), lons=7), col, pat))
    fo = tbox(-0.25, 0.0, 0.07, 0.074, 0.082, 0.086, col, pat)
    if sp["outfit"] == "shirt_tie":
        fo.add(tbox(-0.25, -0.215, 0.076, 0.08, 0.076, 0.08, (250, 250, 248), P_FABRIC))
    hand = hull([(sx * 0.034, -0.245, sz * 0.017) for sx in (-1, 1) for sz in (-1, 1)] +
                [(sx * 0.032, -0.32, sz * 0.012) for sx in (-1, 1) for sz in (-1, 1)] +
                [(sx * 0.018, -0.345, sz * 0.008) for sx in (-1, 1) for sz in (-1, 1)], skin, P_SKIN)
    hand.add(hull([(0.0, -0.255, 0.012), (0.0, -0.285, 0.014), (0.0, -0.3, 0.04), (0.012, -0.27, 0.03), (-0.012, -0.27, 0.03)],
                  skin, P_SKIN))
    fo.add(hand)
    return up, fo


def leg_meshes(sp):
    th = tbox(-0.46, 0.0, 0.11, 0.12, 0.15, 0.16, sp["pants"], P_FABRIC)
    sh = tbox(-0.44, 0.0, 0.092, 0.1, 0.11, 0.12, sp["pants"], P_FABRIC)
    sh.add(hull([(sx * 0.05, -0.43, -0.06) for sx in (-1, 1)] + [(sx * 0.05, -0.49, sz) for sx in (-1, 1) for sz in (-0.07, 0.16)] +
                [(sx * 0.04, -0.45, 0.15) for sx in (-1, 1)], sp["shoes"]))
    return th, sh


class Character:
    def __init__(self, gl, kind, extra=None):
        self.kind = kind
        sp = dict(SPECS[kind])
        self.sp = sp
        self.bones = {}
        self.order = []
        B = self._bone
        B("root", None, (0, 0, 0))
        B("hips", "root", (0, 0.92, 0))
        B("spine", "hips", (0, 0, 0))
        B("head", "spine", (0, 0.515, 0.0))
        B("eyeL", "head", (-0.04, 0.198, ZF + 0.001))
        B("eyeR", "head", (0.04, 0.198, ZF + 0.001))
        B("irisL", "eyeL", (0, 0, 0.0))
        B("irisR", "eyeR", (0, 0, 0.0))
        B("browL", "head", (-0.041, 0.227, ZF + 0.002))
        B("browR", "head", (0.041, 0.227, ZF + 0.002))
        B("mouth", "head", (0, 0.118, ZF + 0.0015))
        B("uarmL", "spine", (-0.21, 0.455, 0))
        B("uarmR", "spine", (0.21, 0.455, 0))
        B("farmL", "uarmL", (0, -0.29, 0))
        B("farmR", "uarmR", (0, -0.29, 0))
        B("thighL", "hips", (-0.095, 0, 0))
        B("thighR", "hips", (0.095, 0, 0))
        B("shinL", "thighL", (0, -0.46, 0))
        B("shinR", "thighR", (0, -0.46, 0))
        b = self.bones
        hm = head_mesh(sp).add(hair_mesh(sp))
        if sp.get("glasses"):
            hm.add(glasses_mesh(sp))
        b["head"].obj.add(hm.transformed(M4(s=(1.1, 1.0, 1.0))))
        for s in "LR":
            b["eye" + s].obj.add(eye_mesh(sp))
            b["iris" + s].obj.add(iris_mesh(sp))
            b["brow" + s].obj.add(brow_mesh(sp, s))
        b["mouth"].obj.add(mouth_mesh(sp))
        b["spine"].obj.add(torso_mesh(sp))
        up, fo = arm_meshes(sp)
        for s in "LR":
            b["uarm" + s].obj.add(up)
            b["farm" + s].obj.add(fo)
        th, sh = leg_meshes(sp)
        for s in "LR":
            b["thigh" + s].obj.add(th)
            b["shin" + s].obj.add(sh)
        if extra:
            for bone, mesh, tex in extra:
                b[bone].obj.add(mesh, tex)
        for bn in self.order:
            self.bones[bn].obj.upload(gl)
        self.pos = np.zeros(3)
        self.yaw = 0.0
        self.pose({})

    def _bone(self, name, parent, offset):
        self.bones[name] = Bone(name, parent, offset)
        self.order.append(name)

    def attach(self, gl, bone, mesh, tex=None):
        self.bones[bone].obj.add(mesh, tex)
        self.bones[bone].obj.upload(gl)

    # ---- pose
    def pose(self, p):
        b = self.bones
        for bn in self.order:
            b[bn].rot[:] = 0
            b[bn].scale[:] = 1
            b[bn].dt[:] = 0
        sit = p.get("sit", 0.0)
        b["hips"].dt[1] = -0.42 * sit + p.get("hip_dy", 0.0)
        b["hips"].dt[2] = p.get("hip_dz", 0.0)
        b["spine"].rot[0] = p.get("lean", 6 * sit)
        b["spine"].rot[1] = p.get("twist", 0.0)
        hp, hy, hr = p.get("head", (0, 0, 0))
        b["head"].rot[:] = (hp, hy, hr)
        gx, gy = p.get("gaze", (0, 0))
        for s in "LR":
            b["iris" + s].dt[:] = (gx * 0.0055, gy * 0.0035, 0)
        bl = p.get("blink", 0.0)
        wide = p.get("eyes_wide", 0.0)
        for s in "LR":
            b["eye" + s].scale[1] = max(0.08, (1 - bl) * (1 + 0.35 * wide))
        br = p.get("brow", 0.0)
        ang = p.get("brow_ang", 0.0)
        b["browL"].dt[1] = br * 0.008
        b["browR"].dt[1] = (br + p.get("brow_r_extra", 0.0)) * 0.008
        b["browL"].rot[2] = -ang
        b["browR"].rot[2] = ang
        mo = p.get("mouth", 0.0)
        b["mouth"].scale[1] = 0.16 + 1.15 * mo
        b["mouth"].scale[0] = 1.0 + 0.25 * p.get("smile", 0.0) - 0.15 * mo
        # arms: (pitch, roll, yaw, elbow)
        for s, sg in (("L", -1), ("R", 1)):
            up, roll, yaw, el = p.get("arm" + s, (0, 6, 0, -5))
            b["uarm" + s].rot[:] = (up, -sg * yaw, sg * roll)
            b["farm" + s].rot[:] = (el, 0, 0)
        for s in "LR":
            th, sh = p.get("leg" + s, (-90 * sit, 90 * sit))
            b["thigh" + s].rot[0] = th
            b["shin" + s].rot[0] = sh

    def world(self):
        W = {}
        root = M4(self.pos, (0, self.yaw, 0))
        for bn in self.order:
            bone = self.bones[bn]
            L = M4(bone.offset + bone.dt, bone.rot, bone.scale)
            W[bn] = (root if bone.parent is None else W[bone.parent]) @ L
        return W

    def draw(self, gl):
        W = self.world()
        for bn in self.order:
            self.bones[bn].obj.draw(gl, W[bn])
        return W
