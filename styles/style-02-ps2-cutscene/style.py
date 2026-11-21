"""Style 02 — PS2 Cutscene Skit.

Skit komedi pendek bergaya cutscene game PS2: karakter 3D low-poly dirender dengan OpenGL
(moderngl), subtitle per 2–3 kata di bawah, caption POV di awal, dan end card produk.
Koreografi & kamera ada di skits/<nama>.py; semua teks diambil dari file JSON konten.
"""
import importlib
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

W, H, FPS = 1080, 1920, 30
RW, RH = 720, 1280  # resolusi render 3D (di-upscale ke W x H, memberi kesan PS2)
FONT_DIR = HERE.parents[1] / "assets" / "fonts"
POP_B = str(FONT_DIR / "Poppins-Bold.ttf")
POP_M = str(FONT_DIR / "Poppins-Medium.ttf")
SUB_Y = 1560


def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def smooth(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


# ---------------------------------------------------------------- subtitle
def chunks(text, maxw=3, maxc=18):
    words = text.split()
    out, cur = [], []
    for w in words:
        cand = cur + [w]
        if cur and (len(cand) > maxw or len(" ".join(cand)) > maxc):
            out.append(" ".join(cur))
            cur = [w]
        else:
            cur = cand
        if w.endswith((".", "?", "!", ",")) and cur and w != words[-1]:
            out.append(" ".join(cur))
            cur = []
    if cur:
        out.append(" ".join(cur))
    return out


def sub_schedule(lines):
    sched = []
    for l in lines:
        t0, t1 = float(l["t0"]), float(l["t1"])
        cs = chunks(l["text"])
        lens = [len(c) + 4 for c in cs]
        tot = sum(lens)
        acc = t0
        for c, L in zip(cs, lens):
            d = (t1 - t0 + 0.15) * L / tot
            sched.append((c, acc, acc + d))
            acc += d
    return sched


class Overlay:
    def __init__(self, cfg, end_t):
        self.cfg = cfg
        self.end_t = end_t
        self.subs = sub_schedule(cfg["lines"])
        self._c = {}

    def text(self, txt, size=70, stroke=6):
        k = ("t", txt, size)
        if k not in self._c:
            f = ImageFont.truetype(POP_B, size)
            bb = f.getbbox(txt, stroke_width=stroke)
            w, h = bb[2] - bb[0] + 40, bb[3] - bb[1] + 40
            im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            sh = Image.new("L", (w, h), 0)
            ImageDraw.Draw(sh).text((20 - bb[0], 26 - bb[1]), txt, font=f, fill=200, stroke_width=stroke, stroke_fill=200)
            im.paste(Image.new("RGBA", (w, h), (0, 0, 0, 255)), (0, 0), sh.filter(ImageFilter.GaussianBlur(5)))
            ImageDraw.Draw(im).text((20 - bb[0], 20 - bb[1]), txt, font=f, fill=(255, 255, 255, 255),
                                    stroke_width=stroke, stroke_fill=(16, 14, 22, 255))
            self._c[k] = im
        return self._c[k]

    def pov(self, txt):
        k = ("pov", txt)
        if k not in self._c:
            f = ImageFont.truetype(POP_M, 40)
            w, h = int(f.getlength(txt) + 48), 74
            im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            d = ImageDraw.Draw(im)
            d.rounded_rectangle((0, 0, w - 1, h - 1), 14, fill=(255, 255, 255, 250))
            d.text((w / 2, h / 2 + 2), txt, font=f, fill=(10, 10, 12), anchor="mm")
            self._c[k] = im
        return self._c[k]

    def tagline(self, lines):
        k = ("tag",) + tuple(lines)
        if k not in self._c:
            f = ImageFont.truetype(POP_B, 56)
            im = Image.new("RGBA", (980, 60 + 84 * len(lines)), (0, 0, 0, 0))
            d = ImageDraw.Draw(im)
            for i, l in enumerate(lines):
                d.text((490, 52 + i * 84), l, font=f, fill=(255, 255, 255), anchor="mm", stroke_width=5,
                       stroke_fill=(12, 40, 90))
            self._c[k] = im
        return self._c[k]

    def watermark(self, txt):
        k = ("wm", txt)
        if k not in self._c:
            f = ImageFont.truetype(POP_B, 46)
            padx, h = 30, 76
            w = int(f.getlength(txt) + 2 * padx)
            im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            d = ImageDraw.Draw(im)
            d.rounded_rectangle((0, 0, w - 1, h - 1), h // 2, fill=(10, 4, 26, 135), outline=(255, 255, 255, 110), width=2)
            d.text((w / 2, h / 2 + 2), txt, font=f, fill=(255, 255, 255, 240), anchor="mm")
            self._c[k] = im
        return self._c[k]

    @staticmethod
    def faded(lay, k):
        if k >= 0.999:
            return lay
        lay = lay.copy()
        lay.putalpha(lay.getchannel("A").point(lambda v: int(v * k)))
        return lay

    def apply(self, img, t):
        cfg = self.cfg
        pov = cfg.get("pov")
        if pov and float(pov.get("t0", 0)) <= t < float(pov.get("t1", 3.4)):
            lay = self.pov(pov["text"])
            img.alpha_composite(lay, ((W - lay.width) // 2, 1300))
        for c, t0, t1 in self.subs:
            if t0 <= t < t1:
                lay = self.text(c)
                img.alpha_composite(lay, ((W - lay.width) // 2, SUB_Y - lay.height // 2))
        end = cfg.get("endcard", {})
        if end.get("url") and t >= self.end_t + 0.3:
            k = smooth((t - self.end_t - 0.3) / 0.35)
            lay = self.faded(self.text(end["url"], 84, 7), k)
            img.alpha_composite(lay, ((W - lay.width) // 2, int(SUB_Y - lay.height // 2 + (1 - k) * 40)))
        if end.get("tagline") and t >= self.end_t + 0.9:
            k = smooth((t - self.end_t - 0.9) / 0.35)
            lay = self.faded(self.tagline(end["tagline"]), k)
            img.alpha_composite(lay, ((W - lay.width) // 2, 150))
        wm = cfg.get("brand", {}).get("watermark")
        if wm:
            lay = self.faded(self.watermark(wm), 0.92)
            img.alpha_composite(lay, (int(W - 50 - lay.width), int(150 - lay.height / 2)))
        return img


# ---------------------------------------------------------------- world (dibuat per proses)
class World:
    def __init__(self, cfg, skit):
        from character import Character
        from engine import GL
        import sets
        sets.set_props(cfg.get("props"))
        self.gl = GL(RW, RH)
        self.tx = sets.Textures(self.gl)
        self.room = sets.Room(self.gl, self.tx)
        self.hill = sets.Hill(self.gl, self.tx)
        self.cast = {name: Character(self.gl, kind) for name, kind in skit.CAST.items()}
        self.hero = Character(self.gl, getattr(skit, "HERO", "student"))
        self.lap_end = sets.laptop_obj(self.tx.scr_logo, self.tx.lid, self.tx.keys, open_deg=100).upload(self.gl)


class Renderer:
    def __init__(self, cfg):
        self.cfg = cfg
        self.skit = importlib.import_module("skits." + cfg.get("skit", "sidang"))
        self.skit.configure(cfg)
        shots = self.skit.SHOTS
        self.shots = shots
        f = [int(round(s[0] * FPS)) for s in shots] + [int(round(shots[-1][1] * FPS))]
        self.starts = f[:-1]
        self.scenes = [(f"shot{i:02d}", f[i + 1] - f[i]) for i in range(len(shots))]
        self.total = f[-1]
        self.overlay = Overlay(cfg, self.skit.END_T)
        self._world = None

    def cut_times(self):
        return [s[0] for s in self.shots[1:]]

    def frame(self, g):
        from engine import look_at, perspective
        if self._world is None:
            self._world = World(self.cfg, self.skit)
        w = self._world
        t = g / FPS
        si = max(i for i, s in enumerate(self.starts) if s <= g)
        t0, t1, e0, g0, e1, g1, fov, set_name = self.shots[si]
        k = smooth((t - t0) / max(0.01, t1 - t0)) * 0.6 + clamp((t - t0) / max(0.01, t1 - t0)) * 0.4
        eye = np.array(e0) + (np.array(e1) - np.array(e0)) * k
        tgt = np.array(g0) + (np.array(g1) - np.array(g0)) * k
        clear = (0.4, 0.6, 0.9) if set_name == "hill" else (0.1, 0.1, 0.12)
        w.gl.begin(look_at(eye, tgt), perspective(fov, RW / RH, 0.04, 120), eye, clear=clear)
        self.skit.draw(w, t, set_name)
        img = Image.fromarray(w.gl.read()).resize((W, H), Image.BILINEAR).convert("RGBA")
        img = self.overlay.apply(img, t)
        return np.asarray(img.convert("RGB"))
