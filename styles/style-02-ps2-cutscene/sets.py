"""Set ruang sidang, props, tekstur, dan set penutup (bukit)."""
import math
import random
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from engine import (P_FABRIC, P_GRASS, P_PLAIN, P_TEX, P_UNLIT, P_UNLIT_TEX, P_WALL, P_WOOD, M4, Mesh, Obj, box,
                    cyl, ellipsoid_pts, hull, quad, tbox)

FD = Path(__file__).resolve().parents[2] / "assets" / "fonts"
POP_B = str(FD / "Poppins-Bold.ttf")
POP_M = str(FD / "Poppins-Medium.ttf")
POP_R = str(FD / "Poppins-Regular.ttf")
PROPS = {
    "slide": ["Pengaruh Durasi Media Sosial", "terhadap Pola Tidur Mahasiswa"],
    "student": "Raka Pratama",
    "prodi": "Program Studi Psikologi",
    "year": "2026",
}


def set_props(p):
    PROPS.update(p or {})
TEAL = (15, 118, 110)


def font(p, s):
    return ImageFont.truetype(p, s)


# ---------------------------------------------------------------- textures
def logo_img(size=512, word=False):
    s = size
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, s - 1, s - 1), int(s * 14 / 64), fill=TEAL + (255,))
    k = s / 64
    # book shape from favicon
    d.rounded_rectangle((16 * k, 16 * k, 48 * k, 42 * k), int(4.5 * k), fill=(240, 253, 250, 255))
    d.rectangle((16 * k, 38 * k, 48 * k, 42 * k), fill=(240, 253, 250, 255))
    d.ellipse((16 * k, 38 * k, 25 * k, 47 * k), fill=(240, 253, 250, 255))
    d.rectangle((20.5 * k, 42 * k, 48 * k, 46.5 * k), fill=TEAL + (255,))
    d.ellipse((16 * k + 4.5 * k - 4.5 * k, 42 * k, 25 * k, 51 * k), fill=TEAL + (255,))
    for y in (25, 32):
        d.line((24 * k, y * k, 40 * k, y * k), fill=TEAL + (255,), width=int(3.2 * k))
        d.ellipse((24 * k - 1.6 * k, (y - 1.6) * k, 24 * k + 1.6 * k, (y + 1.6) * k), fill=TEAL + (255,))
        d.ellipse((40 * k - 1.6 * k, (y - 1.6) * k, 40 * k + 1.6 * k, (y + 1.6) * k), fill=TEAL + (255,))
    return im


def lid_img():
    im = Image.new("RGBA", (680, 440), (58, 62, 70, 255))
    d = ImageDraw.Draw(im)
    for i in range(0, 440, 4):
        d.line((0, i, 680, i), fill=(62, 66, 74, 255))
    lg = logo_img(190)
    im.alpha_composite(lg, ((680 - 190) // 2, (440 - 190) // 2 - 10))
    return im


def screen_student():
    W, H = 680, 440
    im = Image.new("RGBA", (W, H), (247, 249, 251, 255))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, W, 46), fill=(255, 255, 255, 255))
    d.line((0, 46, W, 46), fill=(219, 227, 234, 255), width=2)
    im.alpha_composite(logo_img(30), (14, 8))
    d.text((54, 23), "dosenku · bimbingan", font=font(POP_B, 20), fill=(10, 16, 23), anchor="lm")
    d.rounded_rectangle((300, 66, 660, 128), 14, fill=TEAL + (255,))
    d.text((318, 97), "Cek rujukan Bab 2 dong", font=font(POP_M, 21), fill=(255, 255, 255), anchor="lm")
    d.rounded_rectangle((20, 146, 560, 336), 14, fill=(238, 242, 246, 255), outline=(219, 227, 234, 255), width=2)
    d.text((40, 176), "50 rujukan dicek:", font=font(POP_B, 21), fill=(10, 16, 23), anchor="lm")
    for i, t in enumerate(["50 punya DOI valid", "Sumber: Crossref & OpenAlex", "0 rujukan fiktif"]):
        y = 216 + i * 38
        d.ellipse((40, y - 11, 62, y + 11), fill=(52, 211, 153, 255))
        d.line((45, y, 50, y + 5, 58, y - 5), fill=(255, 255, 255), width=3)
        d.text((74, y), t, font=font(POP_M, 20), fill=(60, 72, 86), anchor="lm")
    d.rounded_rectangle((20, 372, 660, 420), 12, fill=(255, 255, 255, 255), outline=(219, 227, 234, 255), width=2)
    d.text((40, 396), "Tulis pertanyaan…", font=font(POP_R, 19), fill=(140, 150, 165), anchor="lm")
    return im


def screen_logo():
    W, H = 680, 440
    im = Image.new("RGBA", (W, H), (240, 253, 250, 255))
    lg = logo_img(190)
    im.alpha_composite(lg, ((W - 190) // 2, 28))
    d = ImageDraw.Draw(im)
    d.text((W / 2, 268), "dosenku", font=font(POP_B, 62), fill=TEAL, anchor="mm")
    return im


def screen_bu():
    W, H = 680, 440
    im = Image.new("RGBA", (W, H), (255, 255, 255, 255))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, W, 48), fill=(232, 236, 240, 255))
    d.rounded_rectangle((16, 10, 664, 38), 12, fill=(255, 255, 255, 255))
    d.text((32, 24), "doi.org/10.1016/j.sleep.2024.03.011", font=font(POP_R, 17), fill=(60, 64, 72), anchor="lm")
    d.ellipse((60, 90, 170, 200), fill=(34, 170, 110, 255))
    d.line((88, 146, 108, 166, 144, 124), fill=(255, 255, 255), width=12)
    d.text((196, 120), "DOI ditemukan", font=font(POP_B, 38), fill=(20, 26, 34), anchor="lm")
    d.text((196, 168), "Artikel jurnal · terbit 2024", font=font(POP_M, 22), fill=(90, 100, 110), anchor="lm")
    for i in range(5):
        y = 240 + i * 34
        d.rounded_rectangle((60, y, 60 + [560, 520, 590, 480, 400][i], y + 14), 7, fill=(225, 230, 236, 255))
    return im


def keyboard_img():
    im = Image.new("RGBA", (340, 140), (40, 42, 48, 255))
    d = ImageDraw.Draw(im)
    for r in range(5):
        for c in range(14):
            x = 8 + c * 23.4 + (r % 2) * 6
            y = 8 + r * 25
            if x + 19 < 334:
                d.rounded_rectangle((x, y, x + 19, y + 19), 3, fill=(24, 25, 30, 255))
    return im


def thesis_img():
    im = Image.new("RGBA", (420, 600), (18, 92, 62, 255))
    d = ImageDraw.Draw(im)
    gold = (226, 190, 110)
    d.text((210, 120), "SKRIPSI", font=font(POP_B, 64), fill=gold, anchor="mm")
    words = " ".join(PROPS["slide"]).upper().split()
    rows, cur = [], ""
    f24 = font(POP_M, 24)
    for w in words:
        if f24.getlength((cur + " " + w).strip()) <= 360:
            cur = (cur + " " + w).strip()
        else:
            rows.append(cur)
            cur = w
    rows.append(cur)
    for i, r in enumerate(rows[:4]):
        d.text((210, 230 + i * 32), r, font=f24, fill=gold, anchor="mm")
    d.ellipse((160, 370, 260, 470), outline=gold, width=5)
    d.text((210, 515), PROPS["student"].upper(), font=font(POP_B, 26), fill=gold, anchor="mm")
    d.text((210, 552), PROPS["year"], font=font(POP_M, 24), fill=gold, anchor="mm")
    return im


def slide_img():
    W, H = 960, 540
    im = Image.new("RGBA", (W, H), (250, 250, 248, 255))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, W, 96), fill=TEAL + (255,))
    d.text((W / 2, 50), "SIDANG SKRIPSI", font=font(POP_B, 54), fill=(255, 255, 255), anchor="mm")
    for i, line in enumerate(PROPS["slide"][:2]):
        d.text((W / 2, 190 + i * 56), line, font=font(POP_B, 44), fill=(20, 30, 40), anchor="mm")
    d.text((W / 2, 350), PROPS["student"], font=font(POP_M, 34), fill=(70, 80, 90), anchor="mm")
    d.text((W / 2, 398), PROPS["prodi"], font=font(POP_R, 28), fill=(110, 120, 130), anchor="mm")
    return im


def plate_img(text):
    im = Image.new("RGBA", (400, 120), (248, 248, 244, 255))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, 400, 12), fill=TEAL + (255,))
    d.text((200, 66), text, font=font(POP_B, 46), fill=(25, 30, 40), anchor="mm")
    return im


def clock_img():
    im = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse((0, 0, 255, 255), fill=(30, 30, 36, 255))
    d.ellipse((12, 12, 243, 243), fill=(250, 250, 246, 255))
    for k in range(12):
        a = 2 * math.pi * k / 12
        d.line((128 + 98 * math.sin(a), 128 - 98 * math.cos(a), 128 + 112 * math.sin(a), 128 - 112 * math.cos(a)),
               fill=(30, 30, 36), width=6)
    d.line((128, 128, 128 + 55 * math.sin(2.1), 128 - 55 * math.cos(2.1)), fill=(30, 30, 36), width=9)
    d.line((128, 128, 128 + 85 * math.sin(5.2), 128 - 85 * math.cos(5.2)), fill=(30, 30, 36), width=6)
    return im


def sky_img():
    W, H = 1024, 1024
    a = np.zeros((H, W, 3), np.float32)
    ys = np.linspace(0, 1, H)[:, None]
    top = np.array([22, 78, 210], np.float32)
    bot = np.array([120, 180, 245], np.float32)
    a[:] = (top * (1 - ys) + bot * ys)[:, None, :][:, 0, :][:, None, :]
    im = Image.fromarray(a.astype(np.uint8)).convert("RGBA")
    cl = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(cl)
    rnd = random.Random(4)
    for cx, cy, sc in [(180, 300, 1.0), (760, 220, 1.3), (520, 520, 0.8), (90, 640, 0.9), (900, 600, 1.0),
                       (400, 760, 0.7)]:
        for _ in range(14):
            rx_ = rnd.uniform(40, 95) * sc
            ox = rnd.uniform(-130, 130) * sc
            oy = rnd.uniform(-30, 25) * sc - abs(ox) * 0.15
            d.ellipse((cx + ox - rx_, cy + oy - rx_ * 0.7, cx + ox + rx_, cy + oy + rx_ * 0.7), fill=255)
        d.rectangle((cx - 140 * sc, cy + 20 * sc, cx + 140 * sc, cy + 60 * sc), fill=0)
    cl = cl.filter(ImageFilter.GaussianBlur(6))
    white = Image.new("RGBA", (W, H), (255, 255, 255, 255))
    sh = Image.new("RGBA", (W, H), (205, 220, 240, 255))
    im.paste(sh, (0, 14), cl.point(lambda v: int(v * 0.9)))
    im.paste(white, (0, 0), cl)
    return im


class Textures:
    def __init__(self, gl):
        self.logo = gl.texture(logo_img(512))
        self.lid = gl.texture(lid_img())
        self.scr_student = gl.texture(screen_student())
        self.scr_bu = gl.texture(screen_bu())
        self.scr_logo = gl.texture(screen_logo())
        self.keys = gl.texture(keyboard_img())
        self.thesis = gl.texture(thesis_img())
        self.slide = gl.texture(slide_img())
        self.plate1 = gl.texture(plate_img("Penguji I"))
        self.plate2 = gl.texture(plate_img("Penguji II"))
        self.clock = gl.texture(clock_img())
        self.sky = gl.texture(sky_img())


# ---------------------------------------------------------------- props (local meshes)
def chair_mesh(col=(214, 58, 44)):
    m = Mesh()
    m.add(box((0, 0.36, 0.02), (0.54, 0.17, 0.52), col, P_FABRIC))
    m.add(tbox(0.42, 1.0, 0.54, 0.16, 0.5, 0.13, col, P_FABRIC, z0=-0.25, z1=-0.29))
    for s in (-1, 1):
        m.add(box((s * 0.28, 0.52, 0.0), (0.09, 0.3, 0.48), col, P_FABRIC))
    m.add(box((0, 0.14, 0.0), (0.46, 0.28, 0.44), [c * 0.6 for c in col], P_FABRIC))
    return m


def laptop_obj(tex_screen, tex_lid, tex_keys, open_deg=108):
    o = Obj()
    base = Mesh()
    base.add(box((0, 0.009, 0), (0.34, 0.018, 0.235), (70, 74, 82)))
    o.add(base)
    o.add(quad((-0.155, 0.0185, 0.01), (0.155, 0.0185, 0.01), (0.155, 0.0185, -0.105), (-0.155, 0.0185, -0.105),
               (255, 255, 255), P_TEX), tex_keys)
    lid = Mesh()
    lid.add(box((0, 0.11, -0.006), (0.34, 0.22, 0.012), (64, 68, 76)))
    lidM = M4((0, 0.018, -0.115), (-(open_deg - 90), 0, 0))
    o.add(lid.transformed(lidM))
    scr = quad((-0.155, 0.012, 0.0005), (0.155, 0.012, 0.0005), (0.155, 0.208, 0.0005), (-0.155, 0.208, 0.0005),
               (255, 255, 255), P_UNLIT_TEX)
    o.add(scr.transformed(lidM), tex_screen)
    back = quad((0.165, 0.005, -0.0125), (-0.165, 0.005, -0.0125), (-0.165, 0.215, -0.0125), (0.165, 0.215, -0.0125),
                (255, 255, 255), P_TEX)
    o.add(back.transformed(lidM), tex_lid)
    return o


def cup_mesh():
    m = Mesh()
    m.add(cyl((0, 0, 0), 0.075, 0.012, (245, 245, 240), segs=12))
    m.add(cyl((0, 0.012, 0), 0.034, 0.075, (248, 248, 244), segs=10, r2=0.044))
    m.add(cyl((0, 0.084, 0), 0.041, 0.002, (70, 40, 20), segs=10))
    m.add(box((0.05, 0.05, 0), (0.025, 0.035, 0.008), (245, 245, 240)))
    return m


def thesis_obj(tex):
    o = Obj()
    o.add(box((0, 0.022, 0), (0.21, 0.044, 0.3), (18, 92, 62)))
    o.add(box((0, 0.022, 0), (0.2, 0.036, 0.296), (242, 238, 226)))
    o.add(quad((-0.105, 0.0445, 0.15), (0.105, 0.0445, 0.15), (0.105, 0.0445, -0.15), (-0.105, 0.0445, -0.15),
               (255, 255, 255), P_TEX), tex)
    return o


def plate_obj(tex):
    o = Obj()
    h, w, t = 0.075, 0.2, 0.022
    o.add(quad((-w / 2, 0, t), (w / 2, 0, t), (w / 2, h, 0), (-w / 2, h, 0), (255, 255, 255), P_TEX), tex)
    o.add(quad((w / 2, 0, -t), (-w / 2, 0, -t), (-w / 2, h, 0), (w / 2, h, 0), (240, 240, 236)))
    return o


# ---------------------------------------------------------------- room
class Room:
    BACK, LEFT, RIGHT, FRONT, CEIL = -2.3, -2.6, 2.6, 3.2, 2.7

    def __init__(self, gl, tx):
        self.items = []  # (Obj, model)
        st = Obj()
        B, L, R, F, Cc = self.BACK, self.LEFT, self.RIGHT, self.FRONT, self.CEIL
        floor = (198, 200, 204)
        st.add(quad((L, 0, F), (R, 0, F), (R, 0, B), (L, 0, B), floor, P_WALL))
        for i in range(-5, 6):
            st.add(box((i * 0.5, 0.0008, 0.45), (0.006, 0.001, F - B), (178, 180, 186)))
        for k in range(12):
            z = B + k * 0.5
            st.add(box((0, 0.0008, z), (R - L, 0.001, 0.006), (178, 180, 186)))
        wall = (38, 152, 142)
        st.add(quad((L, 0, B), (R, 0, B), (R, Cc, B), (L, Cc, B), wall, P_WALL))
        st.add(quad((L, 0, F), (L, 0, B), (L, Cc, B), (L, Cc, F), wall, P_WALL))
        st.add(quad((R, 0, B), (R, 0, F), (R, Cc, F), (R, Cc, B), wall, P_WALL))
        st.add(quad((R, 0, F), (L, 0, F), (L, Cc, F), (R, Cc, F), wall, P_WALL))
        dark = (28, 118, 110)
        for x in np.arange(L + 0.6, R, 0.6):
            st.add(box((x, Cc / 2, B + 0.004), (0.012, Cc, 0.008), dark))
            st.add(box((x, Cc / 2, F - 0.004), (0.012, Cc, 0.008), dark))
        for z in np.arange(B + 0.6, F, 0.6):
            st.add(box((L + 0.004, Cc / 2, z), (0.008, Cc, 0.012), dark))
            st.add(box((R - 0.004, Cc / 2, z), (0.008, Cc, 0.012), dark))
        base = (230, 232, 230)
        st.add(box((0, 0.05, B + 0.01), (R - L, 0.1, 0.02), base))
        st.add(box((0, 0.05, F - 0.01), (R - L, 0.1, 0.02), base))
        st.add(box((L + 0.01, 0.05, 0.45), (0.02, 0.1, F - B), base))
        st.add(box((R - 0.01, 0.05, 0.45), (0.02, 0.1, F - B), base))
        st.add(quad((L, Cc, B), (R, Cc, B), (R, Cc, F), (L, Cc, F), (226, 226, 222), P_WALL))
        for x in (-1.3, 0.0, 1.3):
            for z in (-1.6, 0.0, 1.6):
                st.add(quad((x - 0.45, Cc - 0.002, z + 0.25), (x + 0.45, Cc - 0.002, z + 0.25),
                            (x + 0.45, Cc - 0.002, z - 0.25), (x - 0.45, Cc - 0.002, z - 0.25), (255, 255, 250), P_UNLIT))
        # door (back wall, left)
        st.add(box((-1.6, 1.05, B + 0.03), (0.98, 2.14, 0.05), (236, 236, 232)))
        st.add(box((-1.6, 1.02, B + 0.05), (0.84, 2.04, 0.05), (28, 40, 104), P_WALL))
        st.add(box((-1.26, 1.0, B + 0.09), (0.05, 0.14, 0.04), (220, 220, 216)))
        # projector screen + slide (back wall, right)
        st.add(box((0.75, 1.55, B + 0.02), (1.72, 1.02, 0.03), (240, 240, 238)))
        st.add(quad((-0.04, 1.1, B + 0.04), (1.54, 1.1, B + 0.04), (1.54, 1.99, B + 0.04), (-0.04, 1.99, B + 0.04),
                    (255, 255, 255), P_UNLIT_TEX), tx.slide)
        # clock
        st.add(quad((-0.62, 2.03, B + 0.03), (-0.38, 2.03, B + 0.03), (-0.38, 2.27, B + 0.03), (-0.62, 2.27, B + 0.03),
                    (255, 255, 255), P_TEX), tx.clock)
        # table (navy cloth)
        nav = (30, 40, 98)
        st.add(box((0, 0.748, 0), (2.4, 0.035, 1.2), nav, P_FABRIC))
        st.add(tbox(0.0, 0.735, 2.34, 1.14, 2.4, 1.2, nav, P_FABRIC))
        st.upload(gl)
        self.items.append((st, np.eye(4)))
        self.chair = Obj().add(chair_mesh()).upload(gl)
        self.chairs = [(-0.55, -1.02, 0), (0.55, -1.02, 0), (0.05, 1.02, 180), (-0.75, 1.02, 180)]
        self.lap_student = laptop_obj(tx.scr_student, tx.lid, tx.keys).upload(gl)
        self.lap_bu = laptop_obj(tx.scr_bu, tx.lid, tx.keys).upload(gl)
        self.cup = Obj().add(cup_mesh()).upload(gl)
        self.thesis = thesis_obj(tx.thesis).upload(gl)
        self.plate1 = plate_obj(tx.plate1).upload(gl)
        self.plate2 = plate_obj(tx.plate2).upload(gl)
        self.student_lap_pos = [0.05, 0.766, 0.36]

    def draw(self, gl, chairs=None, lap=None):
        for o, M in self.items:
            o.draw(gl, M)
        for (x, z, yaw) in (chairs or self.chairs):
            self.chair.draw(gl, M4((x, 0, z), (0, yaw, 0)))
        lx, lz, lyaw = lap or (0.12, 0.38, 0)
        self.lap_student.draw(gl, M4((lx, 0.766, lz), (0, lyaw, 0)))
        self.lap_bu.draw(gl, M4((0.6, 0.766, -0.33), (0, 180, 0)))
        self.cup.draw(gl, M4((-0.18, 0.766, -0.36)))
        self.thesis.draw(gl, M4((0.22, 0.766, -0.3), (0, 8, 0)))
        self.thesis.draw(gl, M4((0.24, 0.81, -0.31), (0, -4, 0)))
        self.plate1.draw(gl, M4((-0.55, 0.766, -0.08)))
        self.plate2.draw(gl, M4((0.55, 0.766, -0.08)))


class Hill:
    def __init__(self, gl, tx):
        o = Obj()
        o.add(quad((-40, -14, -30), (40, -14, -30), (40, 40, -30), (-40, 40, -30), (255, 255, 255), P_UNLIT_TEX), tx.sky)
        pts = ellipsoid_pts((0, -30, -2), (38, 30.6, 34), lats=(50, 62, 70, 76, 81, 85, 88), lons=18)
        o.add(hull(pts, (70, 170, 40), P_GRASS))
        o.add(hull(ellipsoid_pts((-16, -26, -22), (30, 27.5, 12), lats=(55, 70, 80, 87), lons=14), (60, 150, 40), P_GRASS))
        self.obj = o.upload(gl)

    def draw(self, gl):
        self.obj.draw(gl, np.eye(4))
