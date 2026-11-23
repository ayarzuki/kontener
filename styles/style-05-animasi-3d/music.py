"""Skor orkestra kecil orisinal untuk film pendek: piano, string, pizzicato, glockenspiel, perkusi ringan.

Suasana mengikuti "music_moods" di JSON: malam (piano sedih), tegang (akor tahan + detak jam), ajaib (arpeggio naik),
montase (pizzicato riang), pagi (tenang + burung), sorak (penuh, string membesar), akhir (akor hangat + lonceng).
SFX dari "sfx": typing, whoosh, buzz (HP bergetar), ding, sparkle, pop.
"""
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, fftconvolve, lfilter

SR = 44100
LOUDNESS = -17
MOODS = {
    "malam": dict(bpm=70, prog=[(45, [57, 60, 64]), (41, [57, 60, 65]), (48, [55, 60, 64]), (43, [55, 59, 62])], style="sad"),
    "tegang": dict(bpm=70, prog=[(41, [57, 60, 65])], style="hold"),
    "ajaib": dict(bpm=84, prog=[(41, [65, 69, 72, 77]), (43, [67, 71, 74, 79]), (48, [67, 72, 76, 79])], style="arp"),
    "montase": dict(bpm=116, prog=[(48, [64, 67, 72]), (43, [62, 67, 71]), (45, [64, 69, 72]), (41, [65, 69, 72])], style="pizz"),
    "pagi": dict(bpm=80, prog=[(48, [64, 67, 72]), (41, [65, 69, 72])], style="calm"),
    "sorak": dict(bpm=120, prog=[(41, [65, 69, 72]), (43, [67, 71, 74]), (48, [67, 72, 76]), (45, [69, 72, 76])], style="full"),
    "akhir": dict(bpm=80, prog=[(41, [65, 69, 72, 77])], style="end"),
    "krisis": dict(bpm=96, prog=[(40, [52, 55, 59]), (41, [53, 57, 60]), (38, [50, 53, 57]), (40, [52, 56, 59])], style="pulse"),
}


def mtof(m):
    return 440 * 2 ** ((m - 69) / 12)


def filt(x, f, kind, order=2):
    b, a = butter(order, f, btype=kind, fs=SR)
    return lfilter(b, a, x)


_PC = {}


def piano(m, dur=2.5, vel=1.0):
    k = (m, round(dur, 2))
    if k not in _PC:
        n = int(dur * SR)
        t = np.arange(n) / SR
        f = mtof(m)
        s = np.zeros(n)
        dec = 1.8 * (60 / max(30, m)) ** 1.3
        for h in range(1, 10):
            fh = f * h * (1 + 0.0003 * h * h)
            if fh > 12000:
                break
            s += np.sin(2 * np.pi * fh * t) * np.exp(-t * h * 0.9 / dec) / h ** 1.2
        s += filt(np.random.default_rng(m).standard_normal(n), 2500, "low") * np.exp(-t / 0.01) * 0.15
        s *= np.minimum(1, t / 0.003)
        s[-int(0.05 * SR):] *= np.linspace(1, 0, int(0.05 * SR))
        _PC[k] = s
    return _PC[k] * vel


def strings(notes, dur, att=0.8):
    n = int(dur * SR)
    t = np.arange(n) / SR
    s = np.zeros(n)
    for m in notes:
        for d in (-0.004, 0.0, 0.005):
            f = mtof(m) * (1 + d) * (1 + 0.003 * np.sin(2 * np.pi * 5.2 * t))
            ph = np.cumsum(f) / SR
            s += 2 * (ph % 1) - 1
    s = filt(s, 2200, "low")
    a = int(min(att, dur / 2) * SR)
    env = np.ones(n)
    env[:a] = np.linspace(0, 1, a)
    r = int(min(0.6, dur / 3) * SR)
    env[-r:] *= np.linspace(1, 0, r)
    return s * env / max(1, len(notes) * 3)


def pizz(m, dur=0.45):
    t = np.arange(int(dur * SR)) / SR
    f = mtof(m)
    return sum(np.sin(2 * np.pi * f * h * t) * np.exp(-t * (8 + 4 * h)) / h for h in range(1, 6))


def glock(m, dur=1.2):
    t = np.arange(int(dur * SR)) / SR
    f = mtof(m)
    return (np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * 2.76 * f * t) * np.exp(-t / 0.1)) * np.exp(-t / 0.5)


def noise(rng, dur, lo, hi):
    return filt(filt(rng.standard_normal(int(dur * SR)), lo, "high"), hi, "low")


def make_music(path, total, cuts, cfg=None, seed=31):
    cfg = cfg or {}
    rng = np.random.default_rng(seed)
    n = int((total + 3) * SR)
    L, R = np.zeros(n), np.zeros(n)

    def add(sig, t, g=1.0, pan=0.0):
        i = int(t * SR)
        if i < 0 or i >= n:
            return
        j = min(n, i + len(sig))
        L[i:j] += sig[:j - i] * g * (1 - pan)
        R[i:j] += sig[:j - i] * g * (1 + pan)

    moods = cfg.get("music_moods", [[0, "malam"]])
    bounds = [float(a) for a, _ in moods] + [total]
    for k, (a, name) in enumerate(moods):
        md = MOODS[name]
        t0, t1 = float(a), bounds[k + 1]
        beat = 60 / md["bpm"]
        bar = 4 * beat
        sty = md["style"]
        if sty == "hold":
            root, ch = md["prog"][0]
            add(strings(ch, t1 - t0 + 0.4, 0.5), t0, 0.35)
            add(piano(root, 3.0), t0, 0.3)
            tt = t0
            while tt < t1:
                add(noise(rng, 0.03, 2500, 8000) * np.exp(-np.arange(int(0.03 * SR)) / SR / 0.006), tt, 0.25, pan=0.3)
                tt += 0.5
            continue
        if sty == "end":
            root, ch = md["prog"][0]
            for i, m in enumerate([root, root + 12] + ch):
                add(piano(m, 4.0), t0 + i * 0.05, 0.22, pan=-0.3 + i * 0.1)
            add(strings(ch, t1 - t0 + 0.5, 0.6), t0, 0.4)
            for i, m in enumerate((84, 88, 91, 96)):
                add(glock(m), t0 + 0.6 + i * 0.12, 0.1, pan=0.3)
            continue
        b = 0
        while t0 + b * bar < t1 - 0.05:
            tb = t0 + b * bar
            root, ch = md["prog"][b % len(md["prog"])]
            if sty == "sad":
                add(piano(root, bar + 0.5), tb, 0.3)
                for i, m in enumerate([ch[0], ch[1], ch[2], ch[1]]):
                    if tb + i * beat < t1:
                        add(piano(m, 2.0, 0.8), tb + i * beat, 0.16, pan=-0.2 + 0.1 * i)
                add(strings([c - 12 for c in ch], min(bar, t1 - tb) + 0.3, 1.2), tb, 0.16)
            elif sty == "arp":
                add(strings(ch[:3], min(bar, t1 - tb) + 0.3, 0.4), tb, 0.3)
                for i in range(8):
                    m = ch[i % len(ch)] + 12 * (i // len(ch))
                    if tb + i * beat / 2 < t1:
                        add(piano(m, 1.5, 0.8), tb + i * beat / 2, 0.15, pan=-0.4 + i * 0.1)
                        add(glock(m + 12, 0.8), tb + i * beat / 2, 0.05, pan=0.3)
                add(piano(root, bar), tb, 0.25)
            elif sty in ("pizz", "full"):
                pat = [0, 2, 1, 2, 0, 2, 1, 2]
                for i, idx in enumerate(pat):
                    tt = tb + i * beat / 2
                    if tt < t1:
                        add(pizz(ch[idx] if idx < len(ch) else ch[-1]), tt, 0.22, pan=-0.3 + 0.2 * idx)
                add(pizz(root + 12, 0.6), tb, 0.35)
                add(pizz(root + 19, 0.6), tb + 2 * beat, 0.25)
                for i in range(8):
                    if tb + i * beat / 2 < t1:
                        sh = noise(rng, 0.06, 5000, 11000) * np.sin(np.pi * np.linspace(0, 1, int(0.06 * SR)))
                        add(sh, tb + i * beat / 2, 0.06 if i % 2 else 0.1, pan=0.3)
                if sty == "full":
                    add(strings(ch, min(bar, t1 - tb) + 0.3, 0.3), tb, 0.45)
                    for i in range(4):
                        if tb + i * beat < t1:
                            add(piano(ch[i % 3] + 12, 1.2), tb + i * beat, 0.12)
                    for cb in (1, 3):
                        if tb + cb * beat < t1:
                            cl = noise(rng, 0.12, 900, 5000) * np.exp(-np.arange(int(0.12 * SR)) / SR / 0.03)
                            add(cl, tb + cb * beat, 0.3)
                    if b % 2 == 0:
                        for i, m in enumerate((84, 88, 91)):
                            add(glock(m), tb + i * beat * 0.5, 0.07, pan=0.35)
            elif sty == "pulse":
                add(strings(ch, min(bar, t1 - tb) + 0.3, 0.6), tb, 0.28)
                for i in range(8):
                    tt = tb + i * beat / 2
                    if tt < t1:
                        add(pizz(root + 12 + (7 if i % 4 == 3 else 0), 0.35), tt, 0.3 if i % 2 == 0 else 0.18)
                        hh = noise(rng, 0.04, 6000, 12000) * np.exp(-np.arange(int(0.04 * SR)) / SR / 0.01)
                        add(hh, tt + 0.01, 0.08, pan=0.3)
                tl = np.arange(int(0.6 * SR)) / SR
                timp = np.sin(2 * np.pi * np.cumsum(55 + 30 * np.exp(-tl / 0.05)) / SR) * np.exp(-tl / 0.3)
                add(timp, tb, 0.35)
                if b % 2 == 1:
                    add(piano(ch[2] + 12, 1.5, 0.7), tb + 2.5 * beat, 0.1)
            elif sty == "calm":
                add(strings(ch, min(bar, t1 - tb) + 0.3, 1.0), tb, 0.22)
                add(piano(ch[2] + 12, 2.0, 0.7), tb + beat, 0.1)
            b += 1
    # SFX
    for e in cfg.get("sfx", []):
        t, kind = float(e["t"]), e["kind"]
        if kind == "typing":
            tt, end = t, t + float(e.get("dur", 1.5))
            gap = 0.06 if e.get("fast") else 0.11
            while tt < end:
                cl = noise(rng, 0.025, 2000, 9000) * np.exp(-np.arange(int(0.025 * SR)) / SR / 0.005)
                add(cl, tt + rng.uniform(0, 0.02), 0.2, pan=rng.uniform(-0.2, 0.2))
                tt += gap + rng.uniform(0, gap * 0.5)
        elif kind == "whoosh":
            w = noise(rng, 1.2, 300, 5000) * np.sin(np.pi * np.linspace(0, 1, int(1.2 * SR))) ** 2
            add(w, t, 0.4)
            tt = t
            while tt < t + 3:
                add(noise(rng, 0.02, 3000, 9000) * np.exp(-np.arange(int(0.02 * SR)) / SR / 0.004), tt, 0.15, pan=0.3)
                tt += 0.08
        elif kind == "buzz":
            d = float(e.get("dur", 0.9))
            tt = np.arange(int(d * SR)) / SR
            bz = np.sign(np.sin(2 * np.pi * 150 * tt)) * (np.sin(2 * np.pi * 6 * tt) > 0) * 0.3
            add(filt(bz, 800, "low"), t, 0.5)
        elif kind == "ding":
            for i, m in enumerate((88, 95)):
                add(glock(m, 0.8), t + i * 0.1, 0.3)
        elif kind == "sparkle":
            for i in range(10):
                add(glock(96 + int(rng.integers(0, 8)), 0.6), t + i * 0.06, 0.06, pan=rng.uniform(-0.5, 0.5))
        elif kind == "pop":
            tt = np.arange(int(0.2 * SR)) / SR
            add(np.sin(2 * np.pi * np.cumsum(200 + 600 * np.exp(-tt / 0.02)) / SR) * np.exp(-tt / 0.05), t, 0.5)
            add(noise(rng, 0.5, 2000, 9000) * np.exp(-np.arange(int(0.5 * SR)) / SR / 0.12), t, 0.25)
        elif kind == "thud":
            tt = np.arange(int(0.5 * SR)) / SR
            boom = np.sin(2 * np.pi * np.cumsum(45 + 140 * np.exp(-tt / 0.03)) / SR) * np.exp(-tt / 0.18)
            add(np.tanh(1.6 * boom), t, 0.7)
            add(noise(rng, 0.3, 300, 3000) * np.exp(-np.arange(int(0.3 * SR)) / SR / 0.05), t, 0.25)
            boing = np.sin(2 * np.pi * np.cumsum(180 + 60 * np.sin(2 * np.pi * 14 * tt) * np.exp(-tt / 0.2)) / SR) * np.exp(-tt / 0.25)
            add(boing, t + 0.02, 0.2)
        elif kind == "fall":
            d = 0.4
            tt = np.arange(int(d * SR)) / SR
            add(np.sin(2 * np.pi * np.cumsum(1400 * np.exp(-tt / 0.25) + 200) / SR) * 0.25 * (tt / d), t, 0.35)
        elif kind == "drop":
            tt = np.arange(int(0.25 * SR)) / SR
            add(noise(rng, 0.25, 800, 5000) * (tt / tt[-1]) ** 1.5 * 0.4, t - 0.2, 0.35)
            add(np.sin(2 * np.pi * np.cumsum(140 + 300 * np.exp(-tt / 0.03)) / SR) * np.exp(-tt / 0.07), t + 0.05, 0.4)
        elif kind == "birds":
            for i in range(8):
                tt = np.arange(int(0.12 * SR)) / SR
                f = 3000 + 1200 * np.sin(2 * np.pi * 14 * tt)
                add(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * tt / tt[-1]) * 0.15, t + i * rng.uniform(0.25, 0.5), 0.4,
                    pan=0.6)
    ir_n = int(1.6 * SR)
    ti = np.arange(ir_n) / SR
    for i, buf in enumerate((L, R)):
        ir = filt(np.random.default_rng(60 + i).standard_normal(ir_n) * np.exp(-ti / 0.45), 5000, "low")
        wet = fftconvolve(buf, ir)[:n]
        buf += wet * 0.3 * np.abs(buf).max() / (np.abs(wet).max() + 1e-9)
    N = int(total * SR)
    st = np.stack([L[:N], R[:N]], 1)
    fi, fo = int(0.3 * SR), int(1.2 * SR)
    st[:fi] *= np.linspace(0, 1, fi)[:, None]
    st[-fo:] *= np.linspace(1, 0, fo)[:, None]
    st /= np.abs(st).max() + 1e-9
    wavfile.write(str(path), SR, (st * 0.89 * 32767).astype(np.int16))
