"""Musik latar ringan (ukulele + marimba + shaker, 104 BPM) dan SFX yang diambil dari timeline (cfg["_sfx"])."""
import wave

import numpy as np
from scipy.signal import butter, lfilter

SR = 44100
LOUDNESS = -16
BPM = 104
PROG = [(60, [60, 64, 67]), (55, [59, 62, 67]), (57, [57, 60, 64]), (53, [57, 60, 65])]  # C G Am F


def mtof(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def filt(x, f, kind, order=2):
    b, a = butter(order, np.asarray(f, float) / (SR / 2), btype=kind)
    return lfilter(b, a, x)


def pluck(m, dur=1.2, bright=0.5, rng=None):
    """Karplus-Strong ala ukulele."""
    rng = rng or np.random.default_rng(int(m * 7))
    f = mtof(m)
    n = int(dur * SR)
    p = max(2, int(SR / f))
    buf = rng.uniform(-1, 1, p)
    out = np.zeros(n)
    for i in range(n):
        v = buf[i % p]
        out[i] = v
        buf[i % p] = 0.5 * (v + buf[(i + 1) % p]) * (0.994 + 0.004 * bright)
    return filt(out, 4500, "low") * np.exp(-np.arange(n) / SR / (dur * 0.6))


def marimba(m, dur=0.6):
    t = np.arange(int(dur * SR)) / SR
    f = mtof(m)
    return (np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * f * 4 * t) * np.exp(-t / 0.03)) * np.exp(-t / 0.18)


def noise(rng, dur, lo, hi):
    return filt(rng.uniform(-1, 1, int(dur * SR)), [lo, hi], "band")


def make_music(path, total, cuts, cfg=None, seed=11):
    cfg = cfg or {}
    rng = np.random.default_rng(seed)
    n = int((total + 2) * SR)
    L, R = np.zeros(n), np.zeros(n)

    def add(sig, t, g=1.0, pan=0.0):
        i = int(t * SR)
        if i < 0 or i >= n:
            return
        j = min(n, i + len(sig))
        L[i:j] += sig[:j - i] * g * (1 - pan)
        R[i:j] += sig[:j - i] * g * (1 + pan)

    beat = 60 / BPM
    bar = 4 * beat
    cache = {}

    def P(m, d=1.0):
        k = (m, d)
        if k not in cache:
            cache[k] = pluck(m, d)
        return cache[k]

    hook_end = cuts[0] if cuts else 0
    end_t = total - 0.3
    tb, b = 0.0, 0
    mel = [76, 74, 72, 74, 76, 79, 76, 72]
    while tb < end_t:
        root, ch = PROG[b % len(PROG)]
        intro = tb < hook_end
        # strum: D . D U . U D U
        for k, (pos, up) in enumerate([(0, 0), (1, 0), (1.5, 1), (2.5, 1), (3, 0), (3.5, 1)]):
            tt = tb + pos * beat
            if tt >= end_t:
                break
            notes = ch if not up else ch[::-1]
            for j, m in enumerate(notes):
                add(P(m + 12, 0.9), tt + j * 0.012, 0.11 * (0.6 if up else 1.0) * (0.6 if intro else 1), pan=-0.25)
        add(P(root - 12, 1.6), tb, 0.16 * (0.4 if intro else 1))
        if not intro:
            for i in range(8):  # shaker
                tt = tb + i * beat / 2
                if tt < end_t:
                    sh = noise(rng, 0.05, 5000, 11000) * np.sin(np.pi * np.linspace(0, 1, int(0.05 * SR)))
                    add(sh, tt, 0.05 if i % 2 else 0.08, pan=0.35)
            for i in (0, 2):  # kick lembut
                tt = tb + i * beat
                tk = np.arange(int(0.25 * SR)) / SR
                add(np.sin(2 * np.pi * np.cumsum(50 + 90 * np.exp(-tk / 0.02)) / SR) * np.exp(-tk / 0.12), tt, 0.3)
            if b % 2 == 1:
                for i, m in enumerate(mel[(b // 2) % 2 * 4:(b // 2) % 2 * 4 + 4]):
                    tt = tb + i * beat
                    if tt < end_t:
                        add(marimba(m + (ch[0] - 60) * 0), tt, 0.07, pan=0.25)
        tb += bar
        b += 1
    # akord penutup
    add(sum(P(m + 12, 3.0) for m in (60, 64, 67, 72)), end_t - 0.1, 0.12)

    # ---------------------------------------------------------- SFX
    tl = lambda d: np.arange(int(d * SR)) / SR  # noqa: E731
    last = {}
    for kind, t in cfg.get("_sfx", []):
        gap = {"tick": 0.07, "type": 0.06, "pop": 0.08}.get(kind, 0.05)
        if t - last.get(kind, -9) < gap:
            continue
        last[kind] = t
        if kind == "pop":
            x = tl(0.12)
            add(np.sin(2 * np.pi * np.cumsum(500 + 900 * x / 0.12) / SR) * np.exp(-x / 0.035), t, 0.22, pan=0.1)
        elif kind == "type":
            add(noise(rng, 0.03, 2000, 7000) * np.exp(-tl(0.03) / 0.006), t, 0.3, pan=-0.1)
        elif kind == "tick":
            add(noise(rng, 0.02, 3000, 9000) * np.exp(-tl(0.02) / 0.004), t, 0.18)
        elif kind == "ding":
            x = tl(0.9)
            add((np.sin(2 * np.pi * 1568 * x) + 0.5 * np.sin(2 * np.pi * 2349 * x)) * np.exp(-x / 0.25), t, 0.14)
        elif kind == "cash":
            x = tl(1.0)
            add((np.sin(2 * np.pi * 2093 * x) + 0.6 * np.sin(2 * np.pi * 2637 * x)) * np.exp(-x / 0.3), t, 0.16)
            for k in range(6):
                add(noise(rng, 0.05, 5000, 12000) * np.exp(-tl(0.05) / 0.01), t - 0.25 + k * 0.04, 0.12, pan=0.3)
        elif kind == "stamp":
            x = tl(0.3)
            add(np.tanh(2 * np.sin(2 * np.pi * np.cumsum(60 + 120 * np.exp(-x / 0.02)) / SR) * np.exp(-x / 0.08)), t,
                0.45)
            add(noise(rng, 0.15, 300, 4000) * np.exp(-tl(0.15) / 0.03), t, 0.3)
        elif kind == "swell":
            for k in range(10):
                xx = tl(0.1)
                add(np.sin(2 * np.pi * np.cumsum(400 + 60 * k + 700 * xx / 0.1) / SR) * np.exp(-xx / 0.03),
                    t + k * 0.13, 0.12, pan=-0.4 + 0.08 * k)
        elif kind == "whoosh":
            d = 0.35
            x = tl(d)
            env = np.sin(np.pi * x / d) ** 2
            add(noise(rng, d, 600, 6000) * env, t - d * 0.6, 0.12)

    mix = np.stack([L, R], 1)
    mix /= max(1e-6, np.abs(mix).max()) / 0.9
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((mix * 32767).astype(np.int16).tobytes())
