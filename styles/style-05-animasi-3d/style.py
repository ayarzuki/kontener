"""Style 05 - 3D Animasi Sinematik: film pendek ala animasi 3D bioskop (tokoh & dunia orisinal).

Mesin cg.py (moderngl), tokoh nara.py, set room.py, cerita stories/<nama>.py (shot, pose, dunia, cahaya).
Pasca-proses: latar diblur (DOF), bloom, vignette, grain halus. Overlay: hook POV, end card, watermark.
"""
import importlib.util
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
import nara  # noqa: E402
import room  # noqa: E402
from cg import GL, R, T, chain  # noqa: E402

W, H, FPS = 1080, 1920, 30
RW, RH = 720, 1280
FD = HERE.parents[1] / "assets" / "fonts"
TEAL = (15, 118, 110)
_fc = {}


def F(name, size):
    k = (name, int(size))
    if k not in _fc:
        _fc[k] = ImageFont.truetype(str(FD / f"Poppins-{name}.ttf"), max(1, int(size)))
    return _fc[k]


def smooth(p):
    p = min(1.0, max(0.0, p))
    return p * p * (3 - 2 * p)


def ease_out_back(p, k=1.7):
    p = min(1.0, max(0.0, p)) - 1
    return 1 + (k + 1) * p ** 3 + k * p ** 2


def load_story(name):
    path = HERE / "stories" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"story_{name.replace('-', '_')}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def hook_box(text):
    f = F("Bold", 60)
    words, lines, cur = text.split(), [], ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if f.getlength(t) <= 860 or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w_
    lines.append(cur)
    lh = 88
    im = Image.new("RGBA", (W, len(lines) * lh + 30), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for i, l_ in enumerate(lines):
        tw = f.getlength(l_)
        d.rounded_rectangle((W / 2 - tw / 2 - 26, 10 + i * lh, W / 2 + tw / 2 + 26, 10 + i * lh + lh + 4), 22, fill=(255, 255, 255, 255))
    for i, l_ in enumerate(lines):
        d.text((W / 2, 10 + i * lh + lh / 2 + 2), l_, font=f, fill=(0, 0, 0), anchor="mm")
    return im


def soft_text(im, xy, text, f, fill, shadow=0.55, anchor="mm"):
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).text((xy[0], xy[1] + 4), text, font=f, fill=(0, 0, 0, int(255 * shadow)), anchor=anchor)
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(6)))
    ImageDraw.Draw(im).text(xy, text, font=f, fill=fill, anchor=anchor)


class Renderer:
    def __init__(self, cfg):
        self.cfg = cfg
        self.story = load_story(cfg.get("story", "malam-bimbingan"))
        self.shots = self.story.SHOTS
        self.scenes, self.starts = [], []
        for s in self.shots:
            a, b = int(round(s["t0"] * FPS)), int(round(s["t1"] * FPS))
            self.scenes.append((s["name"], b - a))
            self.starts.append(a)
        self.total = int(round(self.shots[-1]["t1"] * FPS))
        self._gl = None
        rng = np.random.default_rng(1)
        self.grain = [rng.normal(0, 1, (H // 2, W // 2)).astype(np.float32) for _ in range(8)]
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        self.vig = (1 - 0.3 * (((xx - W / 2) / (W * 0.8)) ** 2 + ((yy - H / 2) / (H * 0.72)) ** 2))[..., None]
        self._spr = {}

    def gl(self):
        if self._gl is None:
            self._gl = GL(RW, RH, samples=4, shadow_res=2048)
        return self._gl

    def cut_times(self):
        return [s["t0"] for s in self.shots[1:]]

    def render3d(self, t, si):
        s = self.shots[si]
        u = smooth((t - s["t0"]) / max(0.01, s["t1"] - s["t0"]))
        eye = tuple(a + (b - a) * u for a, b in zip(s["eye0"], s["eye1"]))
        tgt = s["tgt"]
        ws = self.story.world_state(t)
        ws["hide_front"] = s.get("hide_front", False)
        lt = self.story.light(t)
        far, near = room.room(ws, t)
        st = self.story.nara_state(t)
        x, y, z = self.story.NARA_POS
        pup = nara.nara(chain(T(x, y, z), R("y", 180)), st, t)
        if hasattr(self.story, "extras"):
            near = near + self.story.extras(t)
        g = self.gl()
        allp = far + near + pup
        lbg = dict(lt)
        k = lt.get("bg_key", 1.0)
        lbg["keycol"] = tuple(c * k for c in lt["keycol"])
        lbg["scrcol"] = tuple(c * k for c in lt.get("scrcol", (0, 0, 0)))
        lbg["fillcol"] = tuple(c * lt.get("bg_fill", 1.0) for c in lt["fillcol"])
        ex = lt.get("expo", 1.0)
        bg = g.render(far, eye, tgt, s["fov"], lbg, bg=(0.02, 0.02, 0.04, 1), shadow_parts=allp, expo=ex)
        fg = g.render(near + pup, eye, tgt, s["fov"], lt, bg=(0, 0, 0, 0), shadow_parts=allp, expo=ex)
        bgi = Image.fromarray(bg[..., :3])
        if s.get("blur", 0) > 0:
            bgi = bgi.filter(ImageFilter.GaussianBlur(s["blur"]))
        bgi = bgi.convert("RGBA")
        bgi.alpha_composite(Image.fromarray(fg, "RGBA"))
        img = bgi.convert("RGB")
        # bloom
        a = np.asarray(img, np.float32)
        lum = a.mean(2, keepdims=True)
        bright = np.clip(a * ((lum - 205) / 50).clip(0, 1), 0, 255).astype(np.uint8)
        bl = np.asarray(Image.fromarray(bright).resize((RW // 4, RH // 4), Image.BILINEAR).filter(ImageFilter.GaussianBlur(6))
                        .resize((RW, RH), Image.BILINEAR), np.float32)
        a = a + bl * 0.35
        img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).resize((W, H), Image.LANCZOS)
        a = np.asarray(img, np.float32) * self.vig
        gr = np.kron(self.grain[int(t * FPS) % len(self.grain)], np.ones((2, 2), np.float32))[:H, :W, None]
        a = a + gr * 2.2
        return np.clip(a, 0, 255).astype(np.uint8)

    def sprite(self, key, fn):
        if key not in self._spr:
            self._spr[key] = fn()
        return self._spr[key]

    def overlays(self, arr, t):
        im = Image.fromarray(arr).convert("RGBA")
        c = self.cfg
        hk = c.get("hook")
        if hk and t < float(hk.get("t1", 3)):
            hb = self.sprite("hook", lambda: hook_box(hk["text"]))
            p = ease_out_back(t / 0.35)
            q = smooth((float(hk.get("t1", 3)) - t) / 0.25)
            sp = hb.resize((max(1, int(hb.width * max(0.05, p))), max(1, int(hb.height * max(0.05, p)))), Image.BILINEAR)
            if q < 1:
                sp.putalpha(sp.getchannel("A").point(lambda v: int(v * q)))
            im.alpha_composite(sp, (int(W / 2 - sp.width / 2), int(float(hk.get("y", 300)) - sp.height / 2)))
        end = c.get("endcard")
        if end and t >= float(end["t0"]):
            lt = t - float(end["t0"])
            dim = Image.new("RGBA", im.size, (8, 30, 34, int(120 * smooth(lt / 0.6))))
            im.alpha_composite(dim)
            a = smooth(lt / 0.5)
            s = 0.85 + 0.15 * ease_out_back(lt / 0.6)
            soft_text(im, (W / 2, 640), end.get("name", "Dosenku"), F("Bold", int(150 * s)), (255, 255, 255, int(255 * a)))
            if lt > 0.4:
                b = smooth((lt - 0.4) / 0.4)
                soft_text(im, (W / 2, 780), end.get("tagline", "Skripsi terarah. Dosen senang."), F("Medium", 52), (255, 255, 255, int(255 * b)))
            if lt > 0.9:
                p = ease_out_back((lt - 0.9) / 0.4)
                f = F("Bold", int(66 * max(0.05, p)))
                url = end.get("url", "dosenku.biz.id")
                uw = f.getlength(url)
                d = ImageDraw.Draw(im)
                d.rounded_rectangle((W / 2 - uw / 2 - 48, 930 - 54 * p, W / 2 + uw / 2 + 48, 930 + 54 * p), int(54 * p) or 1, fill=(255, 255, 255, 255))
                d.text((W / 2, 930), url, font=f, fill=TEAL, anchor="mm")
            if lt > 1.3:
                b = smooth((lt - 1.3) / 0.4)
                soft_text(im, (W / 2, 1050), end.get("note", "Gratis untuk mulai"), F("Regular", 42), (255, 255, 255, int(255 * b)))
        self.data_overlays(im, t)
        wm = c.get("watermark", "Dosenku")
        soft_text(im, (W - 36, 56), wm, F("Bold", 38), (255, 255, 255, 235), shadow=0.5, anchor="rm")
        return np.asarray(im.convert("RGB"))

    # ---------------------------------------------------------- overlay data (berita/pasar)
    COLS = {"red": ((220, 38, 38), (255, 255, 255)), "green": ((22, 163, 74), (255, 255, 255)),
            "dark": ((17, 24, 39), (255, 255, 255)), "light": ((255, 255, 255), (17, 24, 39)),
            "amber": ((245, 158, 11), (17, 24, 39))}

    def card_sprite(self, cd):
        bg, fg = self.COLS.get(cd.get("color", "dark"), self.COLS["dark"])
        fl, fv, fs = F("Bold", int(cd.get("label_size", 36))), F("Bold", int(cd.get("size", 84))), F("Medium", int(cd.get("sub_size", 34)))
        lines = [(cd.get("label", ""), fl)] + [(v, fv) for v in str(cd.get("value", "")).split("\n")] + [(cd.get("sub", ""), fs)]
        lines = [(tx, f) for tx, f in lines if tx]
        w = int(max(f.getlength(tx) for tx, f in lines) + 80)
        hs = [int(f.size * 1.25) for _, f in lines]
        h = sum(hs) + 50
        pad = 30
        im = Image.new("RGBA", (w + 2 * pad, h + 2 * pad), (0, 0, 0, 0))
        sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
        ImageDraw.Draw(sh).rounded_rectangle((pad, pad + 8, pad + w, pad + h + 8), 34, fill=(0, 0, 0, 120))
        im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)))
        d = ImageDraw.Draw(im)
        d.rounded_rectangle((pad, pad, pad + w, pad + h), 34, fill=bg + (240,))
        y = pad + 25
        for (tx, f), hh in zip(lines, hs):
            col = fg if f is fv else tuple(int(c * 0.85 + (255 if fg[0] > 128 else 0) * 0.15) for c in fg)
            d.text((pad + w / 2, y + hh / 2), tx, font=f, fill=col, anchor="mm")
            y += hh
        return im

    def pop(self, im, spr, cx, cy, a, b, t, drop=False):
        if not (a <= t < b):
            return
        p = ease_out_back((t - a) / 0.35)
        q = smooth((b - t) / 0.25)
        s = max(0.05, p)
        sp = spr.resize((max(1, int(spr.width * s)), max(1, int(spr.height * s))), Image.BILINEAR)
        if q < 1:
            sp.putalpha(sp.getchannel("A").point(lambda v: int(v * q)))
        dy = (-120 * (1 - smooth((t - a) / 0.3))) if drop else 0
        im.alpha_composite(sp, (int(cx - sp.width / 2), int(cy - sp.height / 2 + dy)))

    def data_overlays(self, im, t):
        c = self.cfg
        hl = c.get("headline")
        if hl:
            spr = self.sprite("headline", lambda: self.card_sprite(dict(value=hl["text"], color="red", size=hl.get("size", 64))))
            self.pop(im, spr, W / 2, hl.get("y", 300), float(hl.get("t0", 0)), float(hl["t1"]), t)
        for i, cd in enumerate(c.get("cards", [])):
            spr = self.sprite(("card", i), lambda cd=cd: self.card_sprite(cd))
            self.pop(im, spr, cd.get("x", W / 2), cd.get("y", 360), float(cd["t0"]), float(cd["t1"]), t, drop=cd.get("drop", False))
        pl = c.get("poll")
        if pl and float(pl["t0"]) <= t < float(pl["t1"]):
            q = self.sprite("pollq", lambda: self.card_sprite(dict(value=pl.get("question", "Menurut kamu?"), color="light", size=70)))
            self.pop(im, q, W / 2, pl.get("y", 330), float(pl["t0"]), float(pl["t1"]), t)
            for k, (key, txt) in enumerate(pl["options"]):
                spr = self.sprite(("poll", k), lambda key=key, txt=txt, k=k: self.card_sprite(
                    dict(label=f"{key}", value=txt, color="green" if k == 0 else "amber", size=50, label_size=40)))
                a = float(pl["t0"]) + 0.5 + k * 0.6
                self.pop(im, spr, W / 2 + (-262 if k == 0 else 262), pl.get("y", 330) + 230, a, float(pl["t1"]), t)
            if t > float(pl["t0"]) + 2.0:
                b = smooth((t - float(pl["t0"]) - 2.0) / 0.4)
                soft_text(im, (W / 2, pl.get("y", 330) + 420), pl.get("note", "Tulis A atau B di komentar!"), F("Bold", 50),
                          (255, 255, 255, int(255 * b)))
        dc = c.get("disclaimer")
        if dc and float(dc["t0"]) <= t < float(dc["t1"]):
            spr = self.sprite("disc", lambda: self.card_sprite(dict(value=dc["text"], color="amber", size=40)))
            self.pop(im, spr, W / 2, dc.get("y", 1330), float(dc["t0"]), float(dc["t1"]), t)
        ct = c.get("cta")
        if ct and t >= float(ct["t0"]):
            lt = t - float(ct["t0"])
            dim = Image.new("RGBA", im.size, (10, 14, 24, int(150 * smooth(lt / 0.5))))
            im.alpha_composite(dim)
            s = 0.85 + 0.15 * ease_out_back(lt / 0.6)
            soft_text(im, (W / 2, 640), ct.get("text", "Follow"), F("Bold", int(64 * s)), (255, 255, 255, int(255 * smooth(lt / 0.4))))
            spr = self.sprite("cta_handle", lambda: self.card_sprite(dict(value=ct["handle"], color="red", size=88)))
            self.pop(im, spr, W / 2, 780, float(ct["t0"]) + 0.3, 1e9, t)
            if lt > 0.9:
                soft_text(im, (W / 2, 920), ct.get("sub", ""), F("Medium", 44), (255, 255, 255, int(255 * smooth((lt - 0.9) / 0.4))))
        cn = c.get("corner_note")
        if cn:
            soft_text(im, (36, 56), cn, F("Medium", 30), (255, 255, 255, 215), shadow=0.5, anchor="lm")
        so = c.get("sources")
        if so and float(so["t0"]) <= t < float(so["t1"]):
            soft_text(im, (W / 2, so.get("y", 1080)), so["text"], F("Regular", 30), (230, 230, 235, 235))
        if c.get("captions"):
            self.captions(im, t)

    def captions(self, im, t):
        if not hasattr(self, "_caps"):
            self._caps = []
            cps = float(self.cfg.get("caption_cps", 15.5))
            vo = self.cfg.get("voiceover", [])
            for k, v in enumerate(vo):
                if v.get("caption") is False:
                    continue
                t0 = float(v["t0"])
                nxt = float(vo[k + 1]["t0"]) if k + 1 < len(vo) else self.total / FPS
                dur = min(len(v.get("tts", v["text"])) / cps, nxt - t0 - 0.15, float(v.get("max", 99)))
                words = v["text"].split()
                wts = [len(w_) + 2 for w_ in words]
                tot = sum(wts)
                fc = F("Bold", 60)

                def wid(ch):
                    return fc.getlength(" ".join(w_ for *_, w_ in ch))
                tt, items = t0, []
                for w_, wt in zip(words, wts):
                    dd = dur * wt / tot
                    items.append((tt, tt + dd, w_))
                    tt += dd
                # 1) potong per frasa (tanda baca), 2) frasa pendek digabung ke frasa berikutnya,
                # 3) frasa yang terlalu lebar dibagi rata (bukan rakus) supaya tidak ada kata yatim
                phr, cur = [], []
                for it in items:
                    cur.append(it)
                    if it[2][-1] in ".,:;!?":
                        phr.append(cur)
                        cur = []
                if cur:
                    phr.append(cur)
                k = 0
                while k < len(phr):
                    if wid(phr[k]) < 260 and len(phr) > 1:
                        j = k + 1 if k + 1 < len(phr) else k - 1
                        lo, hi = min(k, j), max(k, j)
                        phr[lo:hi + 1] = [phr[lo] + phr[hi]]
                        k = 0
                        continue
                    k += 1
                line = []
                for ph in phr:
                    n = max(1, math.ceil(wid(ph) / 940))
                    if n == 1 or len(ph) < 2:
                        line.append(ph)
                        continue
                    best = None
                    import itertools
                    for cuts in itertools.combinations(range(1, len(ph)), n - 1):
                        parts = [ph[i:j] for i, j in zip((0,) + cuts, cuts + (len(ph),))]
                        sc = max(wid(p_) for p_ in parts)
                        if best is None or sc < best[0]:
                            best = (sc, parts)
                    line += best[1]
                self._caps += line
        for ch in self._caps:
            if ch[0][0] <= t < ch[-1][1] + 0.12:
                f = F("Bold", 60)
                words = [w_ for _, _, w_ in ch]
                sp = f.getlength(" ")
                tot = sum(f.getlength(w_) for w_ in words) + sp * (len(words) - 1)
                x = W / 2 - tot / 2
                d = ImageDraw.Draw(im)
                y = float(self.cfg.get("caption_y", 1500))
                for (a, b, _), w_ in zip(ch, words):
                    col = (255, 214, 64) if a <= t < b + 0.05 else (255, 255, 255)
                    d.text((x, y), w_, font=f, fill=col, anchor="lm", stroke_width=8, stroke_fill=(0, 0, 0))
                    x += f.getlength(w_) + sp
                break

    def frame(self, g):
        t = g / FPS
        si = max(k for k in range(len(self.starts)) if self.starts[k] <= g)
        return self.overlays(self.render3d(t, si), t)
