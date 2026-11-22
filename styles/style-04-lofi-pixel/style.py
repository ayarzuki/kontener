"""Style 04 - Lo-fi Pixel Study: loop "study with me" pixel art (270x480, diperbesar 4x).

Kamar kos malam hujan: jendela besar (kota + hujan + petir), lampu meja, lampu tumblr, kucing tidur,
kopi beruap, mahasiswa berheadphone dari belakang, laptop menampilkan aplikasi Dosenku.
Overlay jendela retro: judul + timer pomodoro, notifikasi bertahap, panel CTA. Font bitmap 5x7 buatan sendiri.
"""
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
import pixel as px  # noqa: E402

W, H, FPS = 1080, 1920, 30
LW, LH, S = 270, 480, 4

WALL = (44, 38, 74)
WALL_D = (32, 28, 58)
WARM = (124, 84, 92)
WOOD = (122, 80, 54)
WOOD_L = (150, 102, 66)
WOOD_D = (86, 54, 38)
TEAL = (15, 118, 110)
CREAM = (246, 240, 226)
INK = (30, 24, 40)
GLASS = (46, 42, 102, 102, 224, 220)  # x0, y0, x1, y1 (pakai indeks)


def C(*c):
    return tuple(int(v) for v in c)


class Scene:
    def __init__(self, seed=5):
        self.rng = np.random.default_rng(seed)
        r = self.rng
        self.gx0, self.gy0, self.gx1, self.gy1 = 46, 42, 224, 220
        # langit + gedung (statis)
        gh, gw = self.gy1 - self.gy0, self.gx1 - self.gx0
        self.sky = px.dither_gradient(gh, gw, [(18, 20, 48), (34, 30, 76), (70, 48, 104), (118, 66, 112)], 0, self.gx0, self.gy0)
        self.bld = np.zeros((gh, gw), bool)
        self.bwin = []
        x = 0
        while x < gw:
            bw = int(r.integers(14, 30))
            bh = int(r.integers(40, 120))
            self.bld[gh - bh:, x:x + bw - 1] = True
            for wy in range(gh - bh + 5, gh - 4, 7):
                for wx in range(x + 3, x + bw - 4, 5):
                    if r.random() < 0.45:
                        self.bwin.append((wx, wy, r.random() < 0.7, r.uniform(0, 100), r.uniform(6, 20)))
            x += bw + int(r.integers(0, 4))
        self.tower = (int(gw * 0.62), gh - 132)
        self.rain = [(r.uniform(0, gw), r.uniform(0, gh), r.uniform(90, 140), int(r.integers(3, 7))) for _ in range(150)]
        self.drops = [(r.uniform(4, gw - 4), r.uniform(0, gh), r.uniform(3, 9), r.uniform(0, 10)) for _ in range(16)]
        self.back = self._back()
        self.front, self.front_a = self._front()

    # -- lapisan statis
    def _back(self):
        a = px.dither_gradient(LH, LW, [WALL_D, WALL, WALL_D], 1)
        lm = px.light_mask(LH, LW, 64, 250, 150, 4)
        warm = np.asarray(WARM, np.float32)
        a = (a * (1 - lm[..., None] * 0.55) + warm * lm[..., None] * 0.55).astype(np.uint8)
        return a

    def _front(self):
        im = Image.new("RGBA", (LW, LH), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        fr, frd = (96, 66, 54), (66, 46, 40)
        d.rectangle((40, 36, 229, 41), fill=fr)
        d.rectangle((40, 221, 229, 226), fill=frd)
        d.rectangle((40, 36, 45, 226), fill=fr)
        d.rectangle((224, 36, 229, 226), fill=frd)
        d.rectangle((133, 42, 136, 220), fill=fr)
        d.rectangle((46, 129, 223, 132), fill=fr)
        d.rectangle((34, 226, 236, 233), fill=(120, 86, 70))
        d.rectangle((34, 233, 236, 235), fill=(80, 56, 48))
        # gorden
        for x0, x1, flip in ((18, 56, False), (214, 252, True)):
            d.rectangle((x0, 26, x1, 244), fill=(132, 62, 78))
            for k in range(x0 + 4, x1, 8):
                d.line((k, 28, k + (2 if flip else -2), 244), fill=(104, 46, 62), width=2)
            d.rectangle((x0, 26, x1, 30), fill=(150, 78, 92))
        d.rectangle((10, 22, 260, 25), fill=(70, 50, 44))
        # tanaman di ambang jendela
        d.polygon([(198, 212), (218, 212), (215, 226), (201, 226)], fill=(170, 92, 60))
        d.rectangle((197, 210, 219, 213), fill=(190, 108, 72))
        for (lx, ly, rx, ry) in ((208, 210, 196, 188), (208, 210, 214, 182), (208, 210, 224, 194), (208, 210, 204, 196),
                                 (208, 210, 219, 200)):
            d.line((lx, ly, rx, ry), fill=(64, 132, 84), width=3)
            d.ellipse((rx - 3, ry - 3, rx + 3, ry + 3), fill=(80, 156, 98))
        # meja
        d.rectangle((0, 298, LW, 305), fill=WOOD_L)
        d.rectangle((0, 372, LW, LH), fill=(24, 20, 38))
        for k in range(372, LH, 2):
            d.line((0, k, LW, k), fill=(30, 24, 46) if (k // 2) % 2 else (24, 20, 38))
        d.rectangle((0, 305, LW, 372), fill=WOOD)
        d.rectangle((0, 368, LW, 372), fill=WOOD_D)
        d.rectangle((0, 305, LW, 308), fill=WOOD_D)
        for k in range(8, LW, 34):
            d.line((k, 312, k + 20, 312), fill=WOOD_D)
        # tumpukan buku
        for i, c in enumerate(((150, 50, 50), (60, 96, 120), (190, 150, 70), (90, 70, 110))):
            y = 296 - i * 5
            d.rectangle((52 + i, y - 4, 88 - i * 2, y), fill=c)
            d.line((52 + i, y - 4, 88 - i * 2, y - 4), fill=tuple(min(255, v + 40) for v in c))
        # lampu meja
        d.rectangle((18, 294, 42, 298), fill=(50, 60, 64))
        d.line((30, 294, 40, 258), fill=(60, 70, 74), width=3)
        d.line((40, 258, 58, 244), fill=(60, 70, 74), width=3)
        d.polygon([(50, 236), (70, 236), (78, 252), (46, 252)], fill=(60, 120, 100))
        d.line((46, 252, 78, 252), fill=(255, 220, 150), width=2)
        # laptop
        d.polygon([(88, 296), (182, 296), (186, 302), (84, 302)], fill=(150, 156, 172))
        d.line((84, 302, 186, 302), fill=(110, 114, 130))
        d.rectangle((96, 234, 174, 296), fill=(40, 42, 54))
        # mug
        d.rectangle((190, 282, 204, 298), fill=(232, 228, 216))
        d.rectangle((190, 282, 204, 284), fill=(96, 56, 36))
        d.arc((200, 285, 210, 295), -90, 90, fill=(232, 228, 216), width=2)
        a = np.asarray(im)
        return a[..., :3].copy(), a[..., 3] > 0

    # -- lapisan dinamis
    def glass(self, arr, t, flash):
        x0, y0, x1, y1 = self.gx0, self.gy0, self.gx1, self.gy1
        g = self.sky.copy()
        gh, gw = g.shape[:2]
        bcol = np.array((22, 22, 44), np.uint8)
        g[self.bld] = bcol
        for (wx, wy, warm, ph, per) in self.bwin:
            on = (math.sin((t + ph) * 2 * math.pi / per) > -0.6)
            if on:
                g[wy:wy + 2, wx:wx + 2] = (255, 206, 120) if warm else (170, 214, 255)
        tx, ty = self.tower
        g[ty:ty + 3, tx - 1:tx + 2] = (30, 30, 54)
        if (t % 1.6) < 0.5:
            g[ty - 2:ty, tx] = (255, 60, 60)
        img = Image.fromarray(g)
        d = ImageDraw.Draw(img)
        for (rx, ry, sp, ln) in self.rain:
            yy = (ry + t * sp * 2.2) % (gh + 10) - 10
            xx = (rx - t * sp * 0.35) % gw
            d.line((xx, yy, xx - 1, yy + ln), fill=(120, 130, 190))
        g = np.asarray(img).copy()
        for (dx, dy, sp, ph) in self.drops:
            yy = int((dy + t * sp) % gh)
            xx = int(dx)
            g[max(0, yy - 6):yy, xx] = (g[max(0, yy - 6):yy, xx] * 0.6 + np.array((160, 170, 230)) * 0.4).astype(np.uint8)
            g[yy:yy + 2, xx:xx + 2] = (190, 200, 245)
        if flash > 0:
            g = np.clip(g.astype(np.float32) + flash * np.array((150, 150, 190)), 0, 255).astype(np.uint8)
        arr[y0:y1, x0:x1] = g

    def string_lights(self, arr, t):
        cols = [(255, 120, 120), (255, 220, 120), (140, 220, 255), (190, 140, 255), (140, 255, 170)]
        for i in range(17):
            x = 26 + i * 13
            y = int(31 + 7 * math.sin(math.pi * (x - 20) / 230))
            if i:
                px.rect(arr, x - 12, y - 1, x, y, (40, 36, 40))
            on = math.sin(t * 2.2 + i * 1.7) > -0.3
            c = cols[i % 5] if on else tuple(v // 3 for v in cols[i % 5])
            px.rect(arr, x - 1, y, x + 2, y + 3, c)
            if on:
                for (ox, oy) in ((-2, 1), (3, 1), (0, 4), (1, -1)):
                    yy, xx = y + oy, x + ox
                    if 0 <= yy < LH and 0 <= xx < LW and (xx + yy) % 2 == 0:
                        arr[yy, xx] = (np.asarray(arr[yy, xx], np.float32) * 0.5 + np.array(c) * 0.5).astype(np.uint8)

    def screen(self, arr, t, cfg):
        x0, y0, x1, y1 = 100, 238, 170, 292
        px.rect(arr, x0, y0, x1, y1, (236, 248, 246))
        px.rect(arr, x0, y0, x1, y0 + 9, TEAL)
        px.draw_text(arr, x0 + 3, y0 + 1, "DOSENKU", (255, 255, 255))
        rows = cfg.get("screen_rows", ["BAB 2", "RUJUKAN", "DOI OK"])
        lt = t - 1.0
        for i in range(5):
            y = y0 + 14 + i * 7
            p = min(1.0, max(0.0, (lt - i * 1.6) / 1.2))
            if p <= 0:
                break
            ln = int((40 if i % 2 else 52) * p)
            px.rect(arr, x0 + 4, y, x0 + 4 + ln, y + 2, (120, 140, 150))
            if p >= 1 and i < len(rows) + 2:
                px.rect(arr, x1 - 9, y - 1, x1 - 4, y + 3, TEAL)
        if (t * 2) % 2 < 1:
            k = min(4, int(max(0, lt) / 1.6))
            px.rect(arr, x0 + 6 + 48, y0 + 14 + k * 7, x0 + 7 + 48, y0 + 18 + k * 7, (30, 30, 40))

    def cat(self, arr, t):
        img = Image.fromarray(arr)
        d = ImageDraw.Draw(img)
        b = 1 if (t % 2.4) < 1.2 else 0
        d.ellipse((214, 280 - b, 258, 300), fill=(224, 136, 62))
        for k in range(4):
            d.line((222 + k * 9, 283 - b, 226 + k * 9, 296), fill=(186, 100, 42), width=2)
        d.ellipse((208, 284, 228, 300), fill=(232, 146, 70))
        d.polygon([(210, 288), (212, 280), (216, 286)], fill=(232, 146, 70))
        d.polygon([(220, 286), (224, 279), (226, 287)], fill=(232, 146, 70))
        d.line((213, 293, 216, 293), fill=(60, 30, 20))
        d.line((220, 293, 223, 293), fill=(60, 30, 20))
        flick = math.sin(max(0, (t % 4.0) - 3.2) * 8) * 4
        d.line((256, 296, 264, 292 + flick, 262, 284 + flick), fill=(224, 136, 62), width=3)
        arr[:] = np.asarray(img)
        if b:
            pass

    def steam(self, arr, t):
        for k in range(3):
            for j in range(10):
                ph = (t * 0.6 + k * 0.33 + j * 0.1) % 1.0
                y = int(280 - ph * 34)
                x = int(195 + k * 4 + 3 * math.sin(ph * 9 + k * 2 + t))
                if (x + y + j) % 2 == 0 and ph < 0.85 and 0 <= y < LH:
                    a = 0.55 * (1 - ph)
                    arr[y, x] = (arr[y, x] * (1 - a) + np.array((220, 220, 236)) * a).astype(np.uint8)

    def person(self, arr, t, bpm):
        beat = 60 / bpm
        bob = 1 if (t % beat) < beat * 0.35 else 0
        img = Image.fromarray(arr)
        d = ImageDraw.Draw(img)
        hood = (40, 66, 78)
        hood_l = (64, 96, 104)
        d.polygon([(64, LH), (78, 396), (104, 374), (166, 374), (192, 396), (206, LH)], fill=hood)
        d.line((78, 396, 104, 374), fill=hood_l, width=2)
        d.line((64, LH, 78, 396), fill=(120, 96, 90), width=2)
        d.polygon([(102, 380), (135, 400), (168, 380), (160, 372), (110, 372)], fill=(52, 80, 92))
        cy = 350 + bob
        d.ellipse((108, cy - 28, 162, cy + 26), fill=(26, 22, 32))
        d.arc((108, cy - 28, 162, cy + 26), 200, 330, fill=(70, 120, 120), width=2)
        d.arc((104, cy - 34, 166, cy + 20), 190, 350, fill=(220, 84, 96), width=4)
        d.rounded_rectangle((100, cy - 8, 112, cy + 14), 3, fill=(220, 84, 96))
        d.rounded_rectangle((158, cy - 8, 170, cy + 14), 3, fill=(220, 84, 96))
        d.line((101, cy - 6, 101, cy + 12), fill=(250, 140, 150))
        arr[:] = np.asarray(img)

    def render(self, t, cfg, bpm, flash=0.0):
        arr = self.back.copy()
        self.glass(arr, t, flash)
        m = self.front_a
        arr[m] = self.front[m]
        self.string_lights(arr, t)
        # cahaya lampu di meja
        lm = px.light_mask(80, 120, 62, 300, 60, 3, 0, 260)
        sub = arr[260:340, 0:120].astype(np.float32)
        arr[260:340, 0:120] = np.clip(sub * (1 + 0.35 * lm[..., None]) + 18 * lm[..., None], 0, 255).astype(np.uint8)
        self.screen(arr, t, cfg)
        sg = px.light_mask(60, 140, 135, 300, 60, 3, 65, 290)
        sub = arr[290:350, 65:205].astype(np.float32)
        arr[290:350, 65:205] = np.clip(sub + sg[..., None] * np.array((10, 40, 38)), 0, 255).astype(np.uint8)
        self.cat(arr, t)
        self.steam(arr, t)
        self.person(arr, t, bpm)
        return arr


# ---------------------------------------------------------------- overlay jendela retro
def window_box(arr, x0, y0, x1, y1, title, body_col=CREAM):
    px.rect(arr, x0 + 2, y0 + 2, x1 + 2, y1 + 2, (10, 8, 20))
    px.rect(arr, x0, y0, x1, y1, (20, 16, 30))
    px.rect(arr, x0 + 1, y0 + 1, x1 - 1, y1 - 1, body_col)
    px.rect(arr, x0 + 1, y0 + 1, x1 - 1, y0 + 10, TEAL)
    px.draw_text(arr, x0 + 4, y0 + 2, title, (255, 255, 255))
    px.rect(arr, x1 - 9, y0 + 3, x1 - 3, y0 + 9, (236, 248, 246))
    for k in range(5):
        for xx in (x1 - 8 + k, x1 - 4 - k):
            if 0 <= xx < arr.shape[1] and 0 <= y0 + 4 + k < arr.shape[0]:
                arr[y0 + 4 + k, xx] = TEAL


def pop_scale(p):
    if p <= 0:
        return 0
    if p >= 1:
        return 1
    return min(1.0, p * 1.4)


class Renderer:
    def __init__(self, cfg):
        self.cfg = cfg
        self.dur = float(cfg.get("duration", 30))
        self.bpm = float(cfg.get("bpm", 80))
        cuts = [0.0] + [float(c) for c in cfg.get("scene_cuts", [])] + [self.dur]
        self.scenes, self.starts = [], []
        for a, b in zip(cuts[:-1], cuts[1:]):
            self.starts.append(int(round(a * FPS)))
            self.scenes.append(("loop", int(round(b * FPS)) - int(round(a * FPS))))
        self.total = int(round(self.dur * FPS))
        self.scene = Scene(cfg.get("seed", 5))

    def cut_times(self):
        return []

    def flash(self, t):
        f = 0.0
        for lt in self.cfg.get("lightning", []):
            dt = t - float(lt)
            if 0 <= dt < 0.12 or 0.25 <= dt < 0.33:
                f = max(f, 0.6 if dt < 0.12 else 0.35)
        return f

    def overlays(self, arr, t):
        c = self.cfg
        ti = c.get("title", {})
        if t >= 0.3:
            x0, y0, x1, y1 = 8, 46, 142, 96
            window_box(arr, x0, y0, x1, y1, ti.get("bar", "STUDY.EXE"))
            px.draw_text(arr, x0 + 5, y0 + 15, ti.get("line1", "STUDY WITH ME"), INK)
            px.draw_text(arr, x0 + 5, y0 + 24, ti.get("line2", ""), (90, 90, 110))
            rem = max(0, int(float(ti.get("timer", 1500)) - t))
            px.draw_text(arr, x0 + 5, y0 + 34, f"{rem // 60:02d}:{rem % 60:02d}", TEAL, scale=2)
        for n in c.get("notifs", []):
            a, b = float(n["t0"]), float(n.get("t1", float(n["t0"]) + 4.5))
            if a <= t < b:
                lines = n["lines"]
                wdt = max(px.text_width(l_) for l_ in lines) + 12
                hh = 14 + 9 * len(lines) + 2
                slide = min(1.0, (t - a) / 0.25)
                out = min(1.0, (b - t) / 0.25)
                x1 = 262
                x0 = int(x1 - wdt + (1 - slide * out) * (wdt + 12))
                y0 = int(n.get("y", 150))
                window_box(arr, x0, y0, x0 + wdt, y0 + hh, n.get("bar", "DOSENKU"))
                for i, l_ in enumerate(lines):
                    px.draw_text(arr, x0 + 6, y0 + 14 + i * 9, l_, TEAL if "✓" in l_ else INK)
        for v in c.get("captions", []):
            a, b = float(v["t0"]), float(v["t1"])
            if a <= t < b:
                lines = v["lines"]
                wdt = max(px.text_width(l_) for l_ in lines) + 10
                y0 = int(v.get("y", 404))
                x0 = LW // 2 - wdt // 2
                sub = arr[y0:y0 + 9 * len(lines) + 6, x0:x0 + wdt].astype(np.float32)
                arr[y0:y0 + 9 * len(lines) + 6, x0:x0 + wdt] = (sub * 0.35).astype(np.uint8)
                for i, l_ in enumerate(lines):
                    px.draw_text_c(arr, LW // 2, y0 + 4 + i * 9, l_, (255, 255, 255))
        cta = c.get("cta")
        if cta and t >= float(cta["t0"]):
            p = min(1.0, (t - float(cta["t0"])) / 0.35)
            h = int(150 * p)
            if h > 12:
                x0, x1 = 22, 248
                yc = 212
                y0, y1 = yc - h // 2, yc + h // 2
                window_box(arr, x0, y0, x1, y1, cta.get("bar", "DOSENKU.EXE"))
                if p >= 1:
                    px.draw_text_c(arr, (x0 + x1) // 2, y0 + 20, cta.get("big", "DOSENKU"), TEAL, scale=4, shadow=(170, 220, 210))
                    px.draw_text_c(arr, (x0 + x1) // 2, y0 + 56, cta.get("line1", ""), INK)
                    px.draw_text_c(arr, (x0 + x1) // 2, y0 + 66, cta.get("line2", ""), INK)
                    bw = px.text_width(cta.get("url", "DOSENKU.BIZ.ID"), 2) + 12
                    px.rect(arr, (x0 + x1) // 2 - bw // 2, y0 + 82, (x0 + x1) // 2 + bw // 2, y0 + 104, TEAL)
                    px.draw_text_c(arr, (x0 + x1) // 2, y0 + 86, cta.get("url", "DOSENKU.BIZ.ID"), (255, 255, 255), scale=2)
                    blink = (t * 2) % 2 < 1.4
                    if blink:
                        px.draw_text_c(arr, (x0 + x1) // 2, y0 + 114, cta.get("note", "GRATIS UNTUK MULAI ♥"), (200, 70, 90))
                    px.draw_text_c(arr, (x0 + x1) // 2, y0 + 128, cta.get("tag", "SKRIPSI TERARAH. DOSEN SENANG."), (90, 90, 110))
        wm = c.get("watermark", "DOSENKU")
        px.draw_text(arr, LW - px.text_width(wm) - 6, 6, wm, (230, 230, 240), shadow=(20, 16, 30))

    def frame(self, g):
        t = g / FPS
        arr = self.scene.render(t, self.cfg, self.bpm, self.flash(t))
        self.overlays(arr, t)
        return np.asarray(Image.fromarray(arr).resize((W, H), Image.NEAREST))
