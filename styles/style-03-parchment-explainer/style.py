"""Style 03 - Parchment Explainer: ilustrasi tinta + cat air di perkamen, kamera Ken Burns,
transisi "tinta lalu cat", label judul & subtitle di sobekan kertas.

Konten JSON:
  "style": "style-03", "story": "<nama file di stories/>",
  "scenes": [{"draw": "<fungsi di stories/...>", "dur": 7.5, "label": "1545", "sub": "...",
              "shots": [[cx, cy, zoom_awal, zoom_akhir], ...], "cuts": [0.55], "captions": true}],
  "voiceover": [{"t0": 0.5, "text": "...", "tts": "..."}]   (teks subtitle = "text")
"""
import importlib.util
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import ink  # noqa: E402

W, H, FPS = 1080, 1920, 30
LW, LH = 1240, 2204          # kanvas logis tempat adegan digambar
K = 1.4                      # resolusi gambar = K x logis (biar close-up tetap tajam)
INK = (40, 28, 21)
GRADE = (1.0, 0.965, 0.9)
CAP_Y = 1540                 # tengah strip subtitle
LABEL_Y = 190                # tengah label judul
REVEAL = 1.05                # detik transisi tinta -> cat di awal scene


def _smooth(x):
    x = np.clip(x, 0, 1)
    return x * x * (3 - 2 * x)


def _ease(t):
    return 0.5 * t + 0.5 * (0.5 - 0.5 * math.cos(math.pi * t))


def load_story(name):
    path = HERE / "stories" / f"{name}.py"
    if not path.exists():
        raise SystemExit(f"Cerita '{name}' tidak ada di {path.parent}")
    spec = importlib.util.spec_from_file_location(f"story_{name.replace('-', '_')}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------- kertas sobek (label & subtitle)
def torn_paper(w, h, seed, tone=(243, 232, 204)):
    r = np.random.default_rng(seed)
    m = 26
    im = Image.new("L", (w + 2 * m, h + 2 * m), 0)
    pts = []
    step = 12
    for x in range(0, w + 1, step):
        pts.append((m + x, m + r.uniform(-3, 5) + (r.uniform(4, 9) if r.random() < 0.08 else 0)))
    for y in range(step, h, step * 2):
        pts.append((m + w + r.uniform(-4, 3), m + y))
    for x in range(w, -1, -step):
        pts.append((m + x, m + h + r.uniform(-5, 3) - (r.uniform(4, 9) if r.random() < 0.08 else 0)))
    for y in range(h - step, 0, -step * 2):
        pts.append((m + r.uniform(-3, 4), m + y))
    ImageDraw.Draw(im).polygon(pts, fill=255)
    alpha = np.asarray(im.filter(ImageFilter.GaussianBlur(0.8)), np.float32) / 255
    shadow = np.asarray(im.filter(ImageFilter.GaussianBlur(9)), np.float32) / 255
    shadow = np.roll(shadow, 6, axis=0) * 0.42
    hh, ww = alpha.shape
    n = ink.smooth_noise(ww, hh, 40, r) * 0.6 + ink.smooth_noise(ww, hh, 6, r) * 0.4
    col = np.asarray(tone, np.float32)[None, None, :] / 255 * (0.95 + 0.09 * n[..., None])
    # pinggir sobekan sedikit lebih gelap
    edge = np.clip(alpha - np.asarray(im.filter(ImageFilter.GaussianBlur(5)), np.float32) / 255, 0, 1)
    col = col * (1 - 0.35 * edge[..., None])
    sh_col = np.array([60, 40, 25], np.float32)[None, None, :] / 255
    a = alpha + shadow * (1 - alpha)
    rgb = (col * alpha[..., None] + sh_col * (shadow * (1 - alpha))[..., None]) / np.maximum(a, 1e-4)[..., None]
    return rgb, a, m


def text_layer(rgb, a, m, lines, ox=0):
    """lines: [(teks, font, y_tengah)] digambar di atas kertas."""
    hh, ww = a.shape
    im = Image.new("L", (ww, hh), 0)
    d = ImageDraw.Draw(im)
    for s, f, y in lines:
        d.text((ww / 2 + ox, m + y), s, font=f, fill=255, anchor="mm")
    t = np.asarray(im.filter(ImageFilter.GaussianBlur(0.45)), np.float32)[..., None] / 255 * 0.95
    inkc = np.asarray(INK, np.float32)[None, None, :] / 255
    return rgb * (1 - t) + inkc * t, a


class Sprite:
    def __init__(self, rgb, a, cx, cy):
        self.rgb, self.a = rgb.astype(np.float32), a.astype(np.float32)
        hh, ww = a.shape
        self.x0, self.y0 = int(cx - ww / 2), int(cy - hh / 2)

    def draw(self, frame, alpha=1.0, dy=0):
        if alpha <= 0.003:
            return
        hh, ww = self.a.shape
        x0, y0 = self.x0, self.y0 + int(dy)
        fx0, fy0, fx1, fy1 = max(0, x0), max(0, y0), min(W, x0 + ww), min(H, y0 + hh)
        if fx1 <= fx0 or fy1 <= fy0:
            return
        sa = self.a[fy0 - y0:fy1 - y0, fx0 - x0:fx1 - x0, None] * alpha
        src = self.rgb[fy0 - y0:fy1 - y0, fx0 - x0:fx1 - x0] * 255
        reg = frame[fy0:fy1, fx0:fx1].astype(np.float32)
        frame[fy0:fy1, fx0:fx1] = (reg * (1 - sa) + src * sa).astype(np.uint8)


def wrap(text, f, maxw):
    words, lines, cur = text.split(), [], ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if f.getlength(t) <= maxw or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- renderer
class Renderer:
    def __init__(self, cfg):
        self.cfg = cfg
        self.story = load_story(cfg.get("story", "sejarah-rujukan"))
        self.sc = cfg["scenes"]
        for s in self.sc:
            if s["draw"] not in self.story.SCENES:
                raise SystemExit(f"Adegan '{s['draw']}' tidak ada. Pilihan: {', '.join(self.story.SCENES)}")
        self.scenes, self.starts, g = [], [], 0
        for s in self.sc:
            n = int(round(float(s["dur"]) * FPS))
            self.scenes.append((s["draw"], n))
            self.starts.append(g)
            g += n
        self.total = g
        self._cache = {}
        self._paper = None
        self._prev = {}
        r = np.random.default_rng(5)
        self.n1 = (ink.smooth_noise(W, H, 220, r) * 0.8 + ink.smooth_noise(W, H, 30, r) * 0.2)
        self.n2 = (ink.smooth_noise(W, H, 150, r) * 0.75 + ink.smooth_noise(W, H, 20, r) * 0.25)
        self._build_overlays()

    # -- layers
    def paper(self):
        if self._paper is None:
            self._paper = ink.make_paper(int(round(LW * K)), int(round(LH * K)), seed=self.cfg.get("paper_seed", 3))
        return self._paper

    def layers(self, i):
        if i not in self._cache:
            if len(self._cache) >= 3:
                self._cache.pop(next(iter(self._cache)))
            s = self.sc[i]
            c = ink.Canvas(LW, LH, seed=int(s.get("seed", 11 + i * 7)), k=K)
            self.story.SCENES[s["draw"]](c)
            full, lines = c.render(self.paper(), grade=GRADE)
            self._cache[i] = (Image.fromarray(full), Image.fromarray(lines))
        return self._cache[i]

    def blank(self):
        if "blank" not in self._prev:
            p = (np.clip(self.paper() * np.asarray(GRADE, np.float32), 0, 1) * 255).astype(np.uint8)
            self._prev["blank"] = Image.fromarray(p)
        return self._prev["blank"]

    # -- camera
    def cam(self, i, t):
        s = self.sc[i]
        dur = float(s["dur"])
        shots = s.get("shots") or [[620, 1150, 1.04, 1.1]]
        cuts = s.get("cuts") or [k / len(shots) for k in range(1, len(shots))]
        bounds = [0.0] + [c_ * dur for c_ in cuts] + [dur]
        j = max(k for k in range(len(shots)) if bounds[k] <= t + 1e-6) if t > 0 else 0
        j = min(j, len(shots) - 1)
        a, b = bounds[j], bounds[j + 1]
        u = _ease(min(1, max(0, (t - a) / max(0.01, b - a))))
        sh = shots[j]
        if len(sh) == 4:
            cx, cy, z = sh[0], sh[1], sh[2] + (sh[3] - sh[2]) * u
        else:
            cx = sh[0] + (sh[3] - sh[0]) * u
            cy = sh[1] + (sh[4] - sh[1]) * u
            z = sh[2] + (sh[5] - sh[2]) * u
        return cx, cy, max(1.0, z)

    def view(self, img, cx, cy, z):
        bw, bh = LW * K / z, LH * K / z
        x0 = min(max(cx * K - bw / 2, 0), LW * K - bw)
        y0 = min(max(cy * K - bh / 2, 0), LH * K - bh)
        return np.asarray(img.resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + bw, y0 + bh)))

    # -- overlays
    def _build_overlays(self):
        ft = ink.font(ink.CARDO_B, 62)
        fs = ink.font(ink.CARDO_I, 38)
        self.labels = {}
        for i, s in enumerate(self.sc):
            if not s.get("label"):
                continue
            lines = [(s["label"], ft)] + ([(s["sub"], fs)] if s.get("sub") else [])
            w = int(max(f.getlength(t) for t, f in lines) + 90)
            h = 92 if len(lines) == 1 else 140
            rgb, a, m = torn_paper(w, h, 40 + i)
            ys = [h / 2] if len(lines) == 1 else [48, 102]
            rgb, a = text_layer(rgb, a, m, [(t, f, y) for (t, f), y in zip(lines, ys)])
            self.labels[i] = Sprite(rgb, a, W / 2, LABEL_Y)
        fw = ink.font(ink.CARDO_B, 42)
        wm = self.cfg.get("watermark", "Dosenku")
        im = Image.new("L", (int(fw.getlength(wm)) + 60, 100), 0)
        ImageDraw.Draw(im).text((30, 48), wm, font=fw, fill=255, anchor="lm")
        ImageDraw.Draw(im).line((32, 74, 32 + fw.getlength(wm) * 0.45, 72), fill=210, width=3)
        a = np.asarray(im.filter(ImageFilter.GaussianBlur(0.5)), np.float32) / 255 * 0.85
        halo = np.asarray(im.filter(ImageFilter.MaxFilter(13)).filter(ImageFilter.GaussianBlur(8)), np.float32) / 255
        halo = np.clip(halo * 1.6, 0, 1) * 0.8
        tone = np.asarray((240, 226, 192), np.float32) / 255
        rgb = np.zeros(a.shape + (3,), np.float32) + np.asarray(INK, np.float32) / 255
        rgb[68:, :, :] = np.asarray((15, 118, 110), np.float32) / 255
        al = a + halo * (1 - a)
        rgb = (rgb * a[..., None] + tone * (halo * (1 - a))[..., None]) / np.maximum(al, 1e-4)[..., None]
        self.wm = Sprite(rgb, al, W - 30 - a.shape[1] / 2, 74)
        # subtitle
        fc = ink.font(ink.CRIMSON, 50)
        self.caps = []
        vo = self.cfg.get("voiceover", [])
        ends = [s_ / FPS for s_ in self.starts[1:]] + [self.total / FPS]
        cps = float(self.cfg.get("caption_cps", 14.5))
        for k, v in enumerate(vo):
            t0 = float(v["t0"])
            si = max(i for i in range(len(self.starts)) if self.starts[i] / FPS <= t0 + 1e-6)
            if not self.sc[si].get("captions", True) or not self.cfg.get("captions", True):
                continue
            nxt = float(vo[k + 1]["t0"]) if k + 1 < len(vo) else ends[-1]
            slot_end = min(nxt - 0.12, ends[si] - 0.1)
            speak = len(v.get("tts", v["text"])) / cps
            end = min(slot_end, t0 + speak + 0.5)
            lines = wrap(v["text"], fc, 880)
            chunks = [lines[j:j + 2] for j in range(0, len(lines), 2)]
            tot = sum(len(" ".join(ch)) for ch in chunks)
            ta = t0
            group = len(self.caps)
            for ch in chunks:
                span = (end - t0) * len(" ".join(ch)) / tot
                w = int(max(fc.getlength(l_) for l_ in ch) + 80)
                h = 66 * len(ch) + 34
                rgb, a, m = torn_paper(w, h, 300 + len(self.caps), tone=(246, 238, 214))
                ys = [h / 2] if len(ch) == 1 else [h / 2 - 33, h / 2 + 33]
                rgb, a = text_layer(rgb, a, m, [(l_, fc, y) for l_, y in zip(ch, ys)])
                self.caps.append([ta, ta + span, Sprite(rgb, a, W / 2, CAP_Y), True, True])
                ta += span
            for j in range(group, len(self.caps) - 1):
                self.caps[j][4] = False      # tanpa fade-out ke potongan berikutnya
                self.caps[j + 1][3] = False  # tanpa fade-in dari potongan sebelumnya

    def cut_times(self):
        return [s / FPS for s in self.starts[1:]]

    # -- frame
    def scene_frame(self, i, t, overlays=True):
        full, lines = self.layers(i)
        cx, cy, z = self.cam(i, t)
        img = self.view(full, cx, cy, z)
        if t < REVEAL:
            prev = self.prev_frame(i)
            ln = self.view(lines, cx, cy, z).astype(np.float32)
            p1 = _smooth((t / (REVEAL * 0.45) * 1.4 - self.n1) / 0.4)[..., None]
            p2 = _smooth(((t - REVEAL * 0.3) / (REVEAL * 0.7) * 1.45 - self.n2) / 0.45)[..., None]
            cur = ln * (1 - p2) + img.astype(np.float32) * p2
            img = (prev.astype(np.float32) * (1 - p1) + cur * p1).astype(np.uint8)
        else:
            img = img.copy()
        if overlays:
            self.draw_overlays(img, i, t)
        return img

    def prev_frame(self, i):
        if i == 0:
            return self.view(self.blank(), *self.cam(0, 0))
        if i not in self._prev:
            n = self.scenes[i - 1][1]
            self._prev = {k: v for k, v in self._prev.items() if k == "blank"}
            self._prev[i] = self.scene_frame(i - 1, (n - 1) / FPS)
        return self._prev[i]

    def draw_overlays(self, img, i, t):
        s = self.sc[i]
        if s.get("watermark", True):
            self.wm.draw(img)
        if i in self.labels:
            u = _smooth((t - 0.55) / 0.4)
            self.labels[i].draw(img, alpha=float(u), dy=(1 - float(u)) * -14)
        g = self.starts[i] / FPS + t
        for a, b, sp, fin, fout in self.caps:
            lo, hi = (a - 0.12 if fin else a), (b + 0.12 if fout else b)
            if lo <= g < hi:
                al = min(1.0, (g - lo) / 0.12 if fin else 1.0, (hi - g) / 0.12 if fout else 1.0)
                sp.draw(img, alpha=max(0.0, al))

    def frame(self, g):
        i = max(k for k in range(len(self.starts)) if self.starts[k] <= g)
        return self.scene_frame(i, (g - self.starts[i]) / FPS)
