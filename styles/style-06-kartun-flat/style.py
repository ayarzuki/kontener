"""Style 06 — Kartun Flat (gaya gambar + animasi vektor datar ala explainer "money mindset").

Langit krem, bukit hijau, tokoh flat bernomor, persamaan diketik di layar, angka berhitung naik, stempel istilah,
pita subtitle gelap di 1/3 bawah. Alur adegan ditulis di cerita/<nama>.py; narasi + subtitle dari `voiceover` JSON.
"""
import importlib.util
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
import sys  # noqa: E402

sys.path.insert(0, str(HERE))
import art  # noqa: E402

W, H, FPS = 1080, 1920, 30
BAND_Y = 1330
GROUND_Y = 1238
BAND = (51, 35, 26)
GREEN_TXT = (126, 210, 138)


def ease_out_back(u, k=1.70158):
    u = min(1.0, max(0.0, u))
    return 1 + (k + 1) * (u - 1) ** 3 + k * (u - 1) ** 2


def smooth(u):
    u = min(1.0, max(0.0, u))
    return u * u * (3 - 2 * u)


def load_story(name):
    path = HERE / "cerita" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"cerita_{name.replace('-', '_')}", path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


# ------------------------------------------------------------------ latar
def cream_bg(seed=3):
    rng = np.random.default_rng(seed)
    y = np.linspace(0, 1, BAND_Y)[:, None]
    top, bot = np.array((251, 240, 219)), np.array((246, 228, 196))
    sky = (top * (1 - y) + bot * y)[:, None, :] * np.ones((1, W, 1))
    im = Image.fromarray(sky.astype(np.uint8)).convert("RGBA")
    full = Image.new("RGBA", (W, H), BAND + (255,))
    full.alpha_composite(im, (0, 0))
    d = ImageDraw.Draw(full)
    xs = np.arange(0, W + 9, 8)
    back = [(x, 1012 + 26 * math.sin(x / 210 + 0.6) + 12 * math.sin(x / 90)) for x in xs]
    d.polygon(back + [(W, BAND_Y), (0, BAND_Y)], fill=(186, 216, 140))
    front = [(x, 1090 + 30 * math.sin(x / 260 + 2.2) + 10 * math.sin(x / 110 + 1)) for x in xs]
    d.polygon(front + [(W, BAND_Y), (0, BAND_Y)], fill=(141, 191, 96))
    for _ in range(150):
        x = rng.uniform(10, W - 10)
        yy = rng.uniform(1120, BAND_Y - 14)
        s = rng.uniform(5, 9)
        d.line([(x - s, yy - s), (x, yy), (x + s, yy - s * 1.2)], fill=(112, 163, 72), width=3)
    d.rectangle((0, BAND_Y - 4, W, BAND_Y + 2), fill=(92, 66, 48))
    return full


def dark_bg(seed=5):
    rng = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:H, 0:W]
    r = np.sqrt(((xx - W / 2) / W) ** 2 + ((yy - H * 0.42) / H) ** 2)
    c0, c1 = np.array((58, 42, 32)), np.array((24, 17, 13))
    a = (c0 * (1 - np.clip(r * 1.7, 0, 1))[..., None] + c1 * np.clip(r * 1.7, 0, 1)[..., None])
    im = Image.fromarray(a.astype(np.uint8)).convert("RGBA")
    d = ImageDraw.Draw(im)
    for _ in range(140):
        x, y = rng.uniform(0, W), rng.uniform(0, H)
        rr = rng.uniform(0.8, 2.2)
        v = int(rng.uniform(70, 140))
        d.ellipse((x - rr, y - rr, x + rr, y + rr), fill=(v, v - 10, v - 20))
    return im


# ------------------------------------------------------------------ renderer
class Renderer:
    def __init__(self, cfg):
        self.cfg = cfg
        self.cps = float(cfg.get("caption_cps", 15.5))
        self.vo = cfg.get("voiceover", [])
        self.story = load_story(cfg["story"])
        ctx = dict(L=self.L, D=self.D, cfg=cfg)
        self.els, cuts, self.dur = self.story.build(ctx)
        self.cuts = cuts  # [(nama, t0)]
        bounds = [c[1] for c in cuts] + [self.dur]
        self.scenes, self.starts = [], []
        for (nm, a), b in zip(cuts, bounds[1:]):
            s0, s1 = int(round(a * FPS)), int(round(b * FPS))
            self.starts.append(s0)
            self.scenes.append((nm, s1 - s0))
        self.total = int(round(self.dur * FPS))
        self.hook_end = getattr(self.story, "HOOK_END", 0.0)
        self._bg = {}
        self._spr = {}
        self.caps = self.build_captions()
        cfg["_sfx"] = self.sfx_events()

    # waktu narasi
    def D(self, i):
        v = self.vo[i]
        return float(v.get("dur", len(v.get("tts", v["text"])) / self.cps))

    def L(self, i, frac=0.0):
        return float(self.vo[i]["t0"]) + frac * self.D(i)

    def cut_times(self):
        return [c[1] for c in self.cuts[1:]]

    # ---------------------------------------------------------- sfx dari timeline
    def sfx_events(self):
        ev = [("whoosh", t) for t in self.cut_times()]
        for e in self.els:
            k, t0 = e["kind"], e["t0"]
            if e.get("sfx") is False:
                continue
            if e.get("sfx"):
                ev.append((e["sfx"], t0 + e.get("sfx_dt", 0)))
            elif k == "stamp":
                ev.append(("stamp", t0))
            elif k == "eq":
                n = len(e["full"].split(" "))
                for j in range(n):
                    ev.append(("type", t0 + e.get("type", 0.9) * j / max(1, n - 1)))
                if e.get("result"):
                    ev.append(("ding", e.get("t_res", t0 + e.get("type", 0.9) + 0.25)))
            elif k == "result":
                ev.append(("cash", t0 + e.get("count", 0.8)))
            elif k == "calendar":
                tt = t0 + 0.25
                while tt < t0 + 0.25 + e.get("count", 1.5):
                    ev.append(("tick", tt))
                    tt += 0.09
            elif k == "crowd" and e.get("n1", e["n"]) > e["n"]:
                ev.append(("swell", e.get("g0", t0)))
            elif k in ("sprite", "pill", "counter", "bars", "title", "xcheck", "crate", "gauge", "bubble"):
                if e.get("in", "pop") != "none":
                    ev.append(("pop", t0))
        return sorted(ev, key=lambda x: x[1])

    # ---------------------------------------------------------- util sprite
    def spr(self, spec):
        if spec not in self._spr:
            fn = getattr(art, spec[0])
            self._spr[spec] = fn(*spec[1:])
        return self._spr[spec]

    def scaled(self, spec, s):
        key = (spec, round(s, 3))
        if key not in self._spr:
            im = self.spr(spec)
            if abs(s - 1) > 1e-3:
                im = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.LANCZOS)
            self._spr[key] = im
        return self._spr[key]

    def place(self, im, base, x, y, s, anchor, alpha=1.0, rot=0.0):
        if s <= 0.01 or alpha <= 0.01:
            return
        sp = im if abs(s - 1) < 1e-3 else im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))),
                                                     Image.BILINEAR)
        if rot:
            sp = sp.rotate(rot, resample=Image.BICUBIC, expand=True)
        if alpha < 0.999:
            sp = sp.copy()
            sp.putalpha(sp.getchannel("A").point(lambda v: int(v * alpha)))
        if anchor == "bottom":
            px, py = x - sp.width / 2, y - sp.height
        else:
            px, py = x - sp.width / 2, y - sp.height / 2
        base.alpha_composite(sp, (int(round(px)), int(round(py))))

    def anim(self, e, t):
        """skala, alpha, dx, dy, rot untuk animasi masuk/keluar."""
        t0, t1 = e["t0"], e["t1"]
        s, a, dx, dy, rot = 1.0, 1.0, 0.0, 0.0, 0.0
        mode = e.get("in", "pop")
        u = (t - t0)
        if mode == "pop":
            s = ease_out_back(u / 0.3) if u < 0.3 else 1.0
            a = smooth(u / 0.12)
        elif mode == "drop":
            if u < 0.45:
                v = u / 0.45
                dy = -(1 - v) ** 2 * 420 if v < 0.7 else -abs(math.sin((v - 0.7) / 0.3 * math.pi)) * 24
            a = smooth(u / 0.1)
        elif mode == "stamp":
            s = 1.0 + 0.9 * (1 - smooth(u / 0.16))
            a = smooth(u / 0.1)
        elif mode == "fade":
            a = smooth(u / 0.25)
        elif mode == "slide":
            dx = (1 - smooth(u / 0.35)) * e.get("from_dx", -500)
        out = e.get("out", "cut")
        if out == "pop" and t > t1 - 0.18:
            v = (t1 - t) / 0.18
            s *= max(0.0, v)
            a *= max(0.0, v)
        elif out == "fade" and t > t1 - 0.25:
            a *= max(0.0, (t1 - t) / 0.25)
        bob = e.get("bob", 0)
        if bob:
            dy += -abs(math.sin((t + e.get("phase", 0)) * 2.4)) * bob
        return s, a, dx, dy, rot

    def pos(self, e, t):
        mv = e.get("move")
        if not mv:
            return e.get("x", 0), e.get("y", 0)
        if t <= mv[0][0]:
            return mv[0][1], mv[0][2]
        for (ta, xa, ya), (tb, xb, yb) in zip(mv[:-1], mv[1:]):
            if ta <= t <= tb:
                u = smooth((t - ta) / max(1e-6, tb - ta))
                return xa + (xb - xa) * u, ya + (yb - ya) * u - math.sin(u * math.pi) * e.get("arc", 0)
        return mv[-1][1], mv[-1][2]

    # ---------------------------------------------------------- elemen
    def draw_el(self, base, e, t):
        k = e["kind"]
        s, a, dx, dy, rot = self.anim(e, t)
        x, y = self.pos(e, t)
        x, y = x + dx, y + dy
        sc = e.get("s", 1.0)
        anchor = e.get("anchor", "bottom" if k in ("sprite", "crate") else "center")
        if k == "sprite":
            spec = e["art"]
            for tt, sp in e.get("art_at", []):
                if t >= tt:
                    spec = sp
            self.place(self.scaled(spec, sc), base, x, y, s, anchor, a, e.get("rot", 0))
        elif k == "pill":
            spec = ("pill", e["text"], e.get("bg", art.INK), e.get("fg", art.WHITE), e.get("size", 40), 34,
                    e.get("icon"))
            self.place(self.scaled(spec, sc), base, x, y, s, anchor, a)
        elif k == "counter":
            u = smooth((t - e.get("c0", e["t0"])) / max(1e-6, e.get("cdur", 1.0)))
            n = int(round(e["n0"] + (e["n1"] - e["n0"]) * u))
            spec = ("pill", f"× {n}", art.INK, art.WHITE, e.get("size", 40), 30, e.get("icon"))
            self.place(self.spr(spec), base, x, y, s, anchor, a)
        elif k == "eq":
            toks = e["full"].split(" ")
            tt = e.get("type", 0.9)
            nt = len(toks) if t >= e["t0"] + tt else max(1, int((t - e["t0"]) / max(1e-6, tt) * len(toks)) + 1)
            shown = " ".join(toks[:nt])
            res = e.get("result", "")
            t_res = e.get("t_res", e["t0"] + tt + 0.25)
            show_res = res if (res and t >= t_res) else ""
            size = self.eq_size(e)
            spec = ("eqbox", e["full"], shown, show_res, size, self.eq_width(e, size))
            u = t - e["t0"]
            s = 0.94 + 0.06 * smooth(u / 0.2)
            self.place(self.spr(spec), base, x, y, s, "center", a)
        elif k == "result":
            u = smooth((t - e["t0"]) / max(1e-6, e.get("count", 0.8)))
            v = e.get("v0", 0) + (e["value"] - e.get("v0", 0)) * u
            dec = e.get("dec", 0)
            txt = f"{v:,.{dec}f}".replace(",", "X").replace(".", ",").replace("X", ".")
            spec = ("resultbox", e.get("prefix", "") + txt + e.get("suffix", ""), e.get("size", 96))
            self.place(self.spr(spec), base, x, y, s, "center", a)
        elif k == "stamp":
            spec = ("stamp", e["text"], e.get("col", (46, 140, 112)), e.get("size", 52))
            self.place(self.scaled(spec, sc), base, x, y, s, "center", a)
        elif k == "calendar":
            u = smooth((t - e["t0"] - 0.25) / max(1e-6, e.get("count", 1.5)))
            n = int(round(e["n0"] + (e["n1"] - e["n0"]) * u))
            self.place(self.scaled(("calendar", n, e.get("head", "HARI")), sc), base, x, y, s, "center", a)
        elif k == "crate":
            u = smooth((t - e.get("g0", e["t0"])) / max(1e-6, e.get("gdur", 1.5)))
            n = int(round(e["n0"] + (e["n1"] - e["n0"]) * u))
            self.place(self.scaled(("crate", n), sc), base, x, y, s, "bottom", a)
        elif k == "crowd":
            self.draw_crowd(base, e, t, a)
        elif k == "bars":
            self.draw_bars(base, e, t, s, a)
        elif k == "title":
            self.draw_title(base, e, t, s, a)
        elif k == "xcheck":
            f = art.F(e.get("size", 84))
            spec = ("icon", e["icon"], int(e.get("size", 84) * 0.42))
            ic = self.spr(spec)
            tw = f.getlength(e["text"])
            tot = tw + 24 + ic.width
            layer = Image.new("RGBA", (int(tot) + 20, int(e.get("size", 84) * 1.6)), (0, 0, 0, 0))
            d = ImageDraw.Draw(layer)
            d.text((10, layer.height / 2 + 6), e["text"], font=f, fill=e.get("col", art.INK), anchor="lm")
            layer.alpha_composite(ic, (int(10 + tw + 24), int((layer.height - ic.height) / 2)))
            self.place(layer, base, x, y, s, "center", a)
        elif k == "gauge":
            g = self.spr(("gauge",))
            self.place(self.scaled(("gauge",), sc), base, x, y, s, "center", a)
            u = smooth((t - e.get("n0t", e["t0"] + 0.3)) / 1.0)
            ang = 180 + (e.get("to", 165)) * u + 4 * math.sin(t * 13) * u
            d = ImageDraw.Draw(base)
            cx, cy = x, y - g.height * sc / 2 + 220 * sc
            r = 150 * sc
            d.line([(cx, cy), (cx + r * math.cos(math.radians(ang)), cy + r * math.sin(math.radians(ang)))],
                   fill=art.INK, width=int(10 * sc))
            d.ellipse((cx - 16 * sc, cy - 16 * sc, cx + 16 * sc, cy + 16 * sc), fill=art.INK)
        elif k == "bubble":
            spec = ("bubble", e["text"], e.get("w", 420), e.get("size", 34), e.get("tail", "left"))
            self.place(self.spr(spec), base, x, y, s, "bottom", a)
        elif k == "dim":
            u = smooth((t - e["t0"]) / 0.3)
            ov = Image.new("RGBA", (W, BAND_Y), (60, 50, 40, int(e.get("alpha", 120) * u)))
            base.alpha_composite(ov, (0, 0))
        elif k == "hooktitle":
            self.draw_hook(base, e, t)

    def eq_size(self, e):
        size = e.get("size", 70)
        txt = e["full"] + ((" = " + e["result"]) if e.get("result") else "")
        while size > 40 and art.F(size).getlength(txt) + 90 > 960:
            size -= 2
        return size

    def eq_width(self, e, size):
        f = art.F(size)
        txt = e["full"] + ((" = " + e["result"]) if e.get("result") else "")
        return int(f.getlength(txt) + 90)

    def draw_crowd(self, base, e, t, a):
        n = e["n"]
        if e.get("n1"):
            u = smooth((t - e.get("g0", e["t0"])) / max(1e-6, e.get("gdur", 1.5)))
            n = int(round(e["n"] + (e["n1"] - e["n"]) * u))
        x0, x1 = e.get("x0", 360), e.get("x1", 1060)
        yb, yf = e.get("yb", 1060), e.get("yf", GROUND_Y)
        per = e.get("per", 10)
        rows = max(1, math.ceil(e.get("n1", e["n"]) / per))
        pts = []
        for r in range(rows):
            v = r / max(1, rows - 1) if rows > 1 else 1.0
            y = yb + (yf - yb) * v
            sc = e.get("sb", 0.22) + (e.get("sf", 0.34) - e.get("sb", 0.22)) * v
            for c in range(per):
                xx = x0 + (x1 - x0) * (c + 0.5 + (0.5 if r % 2 else 0) * 0.5) / per
                pts.append((r, xx, y, sc))
        # isi dari depan ke belakang supaya yang baru muncul di belakang
        order = sorted(pts, key=lambda p_: -p_[0])[::-1]
        order = sorted(pts, key=lambda p_: (-p_[2], p_[1]))[:n]
        for r, xx, y, sc in sorted(order, key=lambda p_: p_[2]):
            self.place(self.scaled(e.get("art", ("cart",)), round(sc, 2)), base, xx, y, 1.0, "bottom", a)

    def draw_bars(self, base, e, t, s, a):
        x0, y0, x1, y1 = e["box"]
        card = Image.new("RGBA", (x1 - x0 + 20, y1 - y0 + 20), (0, 0, 0, 0))
        d = ImageDraw.Draw(card)
        d.rounded_rectangle((10, 10, x1 - x0 + 10, y1 - y0 + 10), 30, fill=(255, 255, 255), outline=art.INK, width=5)
        vals = e["values"]
        n = len(vals)
        vmax = max(vals)
        bw = (x1 - x0 - 80) / n * 0.62
        gap = (x1 - x0 - 80) / n
        hmax = (y1 - y0) - (200 if e.get("cats") else 170)
        for i, v in enumerate(vals):
            tb = e["t0"] + 0.3 + i * e.get("stagger", 0.45)
            u = smooth((t - tb) / 0.6)
            if t < tb:
                continue
            hh = max(10, hmax * (v / vmax) ** e.get("power", 1.0)) * u
            bx = 10 + 40 + gap * i + (gap - bw) / 2
            by1 = y1 - y0 + 10 - (72 if e.get("cats") else 40)
            d.rounded_rectangle((bx, by1 - hh, bx + bw, by1), 12, fill=e["colors"][i], outline=art.INK, width=4)
            lab = e["labels"][i] if u > 0.95 else e.get("fmt", "{:.0f}").format(v * u)
            d.text((bx + bw / 2, by1 - hh - 30), lab, font=art.F(e.get("lsize", 38)), fill=art.INK, anchor="mm")
            if e.get("cats"):
                d.text((bx + bw / 2, by1 + 20), e["cats"][i], font=art.F(e.get("csize", 26), "Medium"),
                       fill=(110, 96, 86), anchor="mm")
        self.place(card, base, (x0 + x1) / 2, (y0 + y1) / 2, s, "center", a)

    def draw_title(self, base, e, t, s, a):
        lines = e["lines"]
        size = e.get("size", 92)
        f = art.F(size)
        hh = int(size * 1.15 * len(lines) + 30)
        ww = int(max(f.getlength(l_[0]) for l_ in lines) + 40)
        layer = Image.new("RGBA", (ww, hh), (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        for i, (txt, col) in enumerate(lines):
            d.text((ww / 2, 15 + size * 1.15 * (i + 0.5)), txt, font=f, fill=col, anchor="mm",
                   stroke_width=2, stroke_fill=col)
        self.place(layer, base, e["x"], e["y"], s, "center", a)

    def draw_hook(self, base, e, t):
        size = e.get("size", 88)
        f = art.F(size)
        for i, (txt, col) in enumerate(e["lines"]):
            tl = e["t0"] + i * e.get("stagger", 0.35)
            if t < tl:
                continue
            s = ease_out_back((t - tl) / 0.3)
            layer = Image.new("RGBA", (W, int(size * 1.4)), (0, 0, 0, 0))
            ImageDraw.Draw(layer).text((W / 2, size * 0.7), txt, font=f, fill=col, anchor="mm", stroke_width=2,
                                       stroke_fill=col)
            self.place(layer, base, W / 2, e["y"] + i * size * 1.15, s, "center", smooth((t - tl) / 0.1))

    # ---------------------------------------------------------- subtitle
    def build_captions(self):
        caps = []
        f = art.F(66)
        for i, v in enumerate(self.vo):
            if v.get("caption") is False:
                continue
            t0, dur = float(v["t0"]), self.D(i)
            words = v["text"].split()
            wts = [len(w_) + 2 for w_ in words]
            tot = sum(wts)
            items, tt = [], t0
            for w_, wt in zip(words, wts):
                dd = dur * wt / tot
                items.append((tt, tt + dd, w_))
                tt += dd
            chunk = []
            for it in items:
                cand = chunk + [it]
                txt = " ".join(c[2] for c in cand)
                if chunk and (len(cand) > 3 or f.getlength(txt) > 860):
                    caps.append(chunk)
                    chunk = [it]
                else:
                    chunk = cand
                if it[2][-1] in ".,:?!" and len(chunk) >= 1 and f.getlength(" ".join(c[2] for c in chunk)) > 160:
                    caps.append(chunk)
                    chunk = []
            if chunk:
                if caps and len(chunk) == 1 and len(chunk[0][2]) < 5 and caps[-1][0][0] >= t0:
                    caps[-1] = caps[-1] + chunk
                else:
                    caps.append(chunk)
        return caps

    def draw_caption(self, base, t):
        f = art.F(66)
        for ch in self.caps:
            end = ch[-1][1] + 0.12
            if ch[0][0] <= t < end:
                words = [c[2] for c in ch]
                sp = f.getlength(" ")
                tot = sum(f.getlength(w_) for w_ in words) + sp * (len(words) - 1)
                x = W / 2 - tot / 2
                d = ImageDraw.Draw(base)
                for (a, b, w_) in ch:
                    if a <= t < b + 0.04:
                        col = art.AMBER
                    elif any(c.isdigit() for c in w_) or w_.startswith("Rp"):
                        col = GREEN_TXT
                    else:
                        col = (255, 250, 240)
                    d.text((x, 1428), w_, font=f, fill=col, anchor="lm")
                    x += f.getlength(w_) + sp
                return

    # ---------------------------------------------------------- frame
    def bg(self, kind):
        if kind not in self._bg:
            self._bg[kind] = cream_bg() if kind == "cream" else dark_bg()
        return self._bg[kind]

    def frame(self, g):
        t = g / FPS
        hook = t < self.hook_end
        base = self.bg("dark" if hook else "cream").copy()
        act = [e for e in self.els if e["t0"] <= t < e["t1"]]
        for e in sorted(act, key=lambda e_: e_.get("z", 0)):
            self.draw_el(base, e, t)
        # pita bawah + label seri
        if not hook:
            d = ImageDraw.Draw(base)
            d.rectangle((0, BAND_Y + 2, W, H), fill=BAND)
        c = self.cfg
        sp = ("pill", c.get("series", "MINDSET"), art.INK, (255, 246, 229), 40, 34, c.get("series_icon", "teh"))
        pil = self.spr(sp)
        self.place(pil, base, W / 2, 112, 1.0, "center", 0.65 if hook else 1.0)
        self.draw_caption(base, t)
        foot = c.get("footer")
        if foot:
            ImageDraw.Draw(base).text((W / 2, 1858), foot, font=art.F(28, "Medium"), fill=(150, 128, 110), anchor="mm")
        return np.asarray(base.convert("RGB"))
