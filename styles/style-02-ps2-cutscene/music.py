"""Musik lounge orisinal (bossa ringan, 100 BPM) + efek suara dari daftar "audio.sfx" di konten.

Musik sengaja pelan supaya ada ruang untuk suara TTS. Bagian musik diatur lewat
"audio.music": [[mulai, selesai], ...] — jeda di antaranya jadi momen hening yang lucu.
Tipe SFX: typing (t0,t1,rate), ding (t), sting (t), scrape (t,dur), steps (t0,t1,every), jingle (t).
"""
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, lfilter

SR = 44100
BPM = 100
BEAT = 60 / BPM
LOUDNESS = -16  # target LUFS (lebih pelan dari style-01, ruang untuk voice-over)


def _filt(x, f, kind):
    b, a = butter(2, f, btype=kind, fs=SR)
    return lfilter(b, a, x)


def _mtof(m):
    return 440 * 2 ** ((m - 69) / 12)


def make_music(path, total, cuts, cfg=None, seed=7):
    rng = np.random.default_rng(seed)
    N = int(SR * total)

    def add(buf, sig, t):
        i = int(t * SR)
        if i >= len(buf):
            return
        j = min(len(buf), i + len(sig))
        buf[i:j] += sig[: j - i]

    def epiano(f, dur, vel=1.0):
        n = int(dur * SR)
        t = np.arange(n) / SR
        s = (np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t / 0.4)
             + 0.12 * np.sin(2 * np.pi * 3.01 * f * t) * np.exp(-t / 0.15) + 0.06 * np.sin(2 * np.pi * 7.1 * f * t) * np.exp(-t / 0.03))
        env = np.exp(-t / 1.1) * np.minimum(1, t / 0.004)
        env[-int(0.05 * SR):] *= np.linspace(1, 0, int(0.05 * SR))
        return s * env * vel * (1 + 0.08 * np.sin(2 * np.pi * 4.5 * t))

    def bass(f, dur):
        n = int(dur * SR)
        t = np.arange(n) / SR
        s = np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t / 0.12)
        env = np.exp(-t / 0.35) * np.minimum(1, t / 0.006)
        env[-int(0.03 * SR):] *= np.linspace(1, 0, int(0.03 * SR))
        return s * env

    def section(length):
        n = int(length * SR)
        L, R = np.zeros(n), np.zeros(n)
        chords = [(53, [64, 69, 72, 76]), (52, [62, 67, 71, 74]), (50, [60, 65, 69, 72]), (48, [59, 64, 67, 71])]
        bar = 4 * BEAT
        for b in range(int(np.ceil(length / bar))):
            root, notes = chords[b % 4]
            t0 = b * bar
            for k, cb in enumerate((0.0, 1.5, 2.5, 3.0)):
                vel = 0.55 if k else 0.7
                for j, m in enumerate(notes):
                    s = epiano(_mtof(m), 0.9 if k < 3 else 1.4, vel * 0.18)
                    add(L, s * (0.9 if j % 2 else 1.1), t0 + cb * BEAT + j * 0.008)
                    add(R, s * (1.1 if j % 2 else 0.9), t0 + cb * BEAT + j * 0.008)
            for cb, m in ((0, root), (1.5, root + 7), (2, root + 7), (3, root + 7)):
                s = bass(_mtof(m - 12), 0.7) * 0.42
                add(L, s, t0 + cb * BEAT)
                add(R, s, t0 + cb * BEAT)
            for k in range(16):
                nn = int(0.05 * SR)
                hs = _filt(rng.standard_normal(nn), 6000, "high") * np.exp(-np.arange(nn) / SR / 0.018)
                v = 0.05 if k % 2 else 0.03
                add(L, hs * v, t0 + k * BEAT / 4)
                add(R, hs * v * 0.8, t0 + k * BEAT / 4 + 0.004)
            for cb in (0.0, 1.5, 3.0, 2.5):
                nn = int(0.06 * SR)
                tt = np.arange(nn) / SR
                rim = (np.sin(2 * np.pi * 1700 * tt) * 0.5 + _filt(rng.standard_normal(nn), 2500, "high") * 0.5) * np.exp(-tt / 0.012)
                add(L, rim * 0.09, t0 + cb * BEAT)
                add(R, rim * 0.07, t0 + cb * BEAT)
        fo = int(0.25 * SR)
        for ch in (L, R):
            ch[-fo:] *= np.linspace(1, 0, fo)
        return L, R

    def click():
        nn = int(0.025 * SR)
        return _filt(rng.standard_normal(nn), [1800, 6500], "band") * np.exp(-np.arange(nn) / SR / 0.006)

    audio = (cfg or {}).get("audio", {})
    L, R = np.zeros(N), np.zeros(N)
    for a, b in audio.get("music", [[0, total - 1]]):
        ml, mr = section(b - a)
        add(L, ml, a)
        add(R, mr, a)
    fx = np.zeros(N)
    for s in audio.get("sfx", []):
        kind = s["type"]
        if kind == "typing":
            t, rate = s["t0"], s.get("rate", 11)
            while t < s["t1"]:
                add(fx, click() * rng.uniform(0.25, 0.45), t)
                t += rng.uniform(0.6, 1.4) / rate
        elif kind == "ding":
            for f, dt in ((1318.5, 0.0), (1975.5, 0.11)):
                tt = np.arange(int(1.2 * SR)) / SR
                add(fx, (np.sin(2 * np.pi * f * tt) + 0.3 * np.sin(2 * np.pi * 2.76 * f * tt) * np.exp(-tt / 0.1))
                    * np.exp(-tt / 0.45) * 0.22, s["t"] + dt)
        elif kind == "sting":
            for m, dt in ((79, 0.0), (83, 0.06), (86, 0.12)):
                add(fx, epiano(_mtof(m), 0.6, 0.22), s["t"] + dt)
        elif kind == "scrape":
            dur = s.get("dur", 0.45)
            tt = np.arange(int(dur * SR)) / SR
            sig = _filt(rng.standard_normal(len(tt)), [300, 1400], "band") * (np.sin(2 * np.pi * 38 * tt) * 0.5 + 0.6)
            add(fx, sig * np.sin(np.pi * tt / dur) ** 0.7 * s.get("amp", 0.3), s["t"])
        elif kind == "steps":
            t = s["t0"]
            while t < s["t1"]:
                tt = np.arange(int(0.12 * SR)) / SR
                sig = np.sin(2 * np.pi * (90 + 60 * np.exp(-tt / 0.01)) * tt) * np.exp(-tt / 0.03)
                sig += _filt(rng.standard_normal(len(tt)), [800, 4000], "band") * np.exp(-tt / 0.015) * 0.6
                add(fx, sig * 0.45, t)
                t += s.get("every", 0.3)
        elif kind == "jingle":
            t0 = s["t"]
            for i, m in enumerate((72, 76, 79, 84)):
                tt = np.arange(int(1.6 * SR)) / SR
                f = _mtof(m)
                sig = (np.sin(2 * np.pi * f * tt) + 0.4 * np.sin(2 * np.pi * 2 * f * tt) * np.exp(-tt / 0.3)
                       + 0.25 * np.sin(2 * np.pi * 3.98 * f * tt) * np.exp(-tt / 0.12)) * np.exp(-tt / 0.6)
                add(fx, sig * 0.2, t0 + i * 0.09)
            for m in (60, 64, 67, 72, 76):
                add(fx, epiano(_mtof(m), 3.0, 0.16), t0 + 0.42)
            tt = np.arange(int(0.5 * SR)) / SR
            add(fx, _filt(rng.standard_normal(len(tt)), [2000, 9000], "band") * (tt / 0.5) ** 2 * 0.12, max(0, t0 - 0.45))
    L += fx
    R += fx
    st = np.stack([L, R], 1)
    st /= max(1e-9, np.max(np.abs(st))) / 0.9
    fade = np.ones(N)
    f0 = int((total - 1.2) * SR)
    fade[f0:] = np.linspace(1, 0, N - f0)
    st *= fade[:, None]
    wavfile.write(str(path), SR, (st * 32767).astype(np.int16))
