"""Musik folk orisinal: gitar petik (sintesis aditif), bass, pad lembut, glockenspiel tipis,
plus efek "balik halaman" di setiap pergantian scene. 84 BPM, D - A - Bm - G.

Sengaja pelan dan jarang supaya narasi Fish Audio (voice.py) tetap jelas.
"""
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, fftconvolve, lfilter

SR = 44100
BPM = 84
BEAT = 60 / BPM
LOUDNESS = -17  # target LUFS (ruang untuk voice-over)

CHORDS = [  # (bass, [nada petik])
    (38, [50, 57, 62, 66]),   # D
    (45, [52, 57, 61, 64]),   # A
    (47, [54, 59, 62, 66]),   # Bm
    (43, [50, 55, 59, 62]),   # G
]
MELODY = [  # (bar, ketukan, midi, panjang)  motif glockenspiel tiap 4 bar
    (0, 0, 78, 1.0), (0, 1.5, 76, 0.5), (0, 2, 74, 1.5), (1, 0, 73, 1), (1, 1, 76, 2),
    (2, 0, 74, 1), (2, 1, 71, 1), (2, 2, 74, 1.5), (3, 0, 71, 1.5), (3, 2, 69, 2),
]


def _mtof(m):
    return 440 * 2 ** ((m - 69) / 12)


def _filt(x, f, kind, order=2):
    b, a = butter(order, f, btype=kind, fs=SR)
    return lfilter(b, a, x)


_PL = {}


def pluck(m, vel=1.0, dur=2.6, p=0.18):
    key = (m, dur)
    if key not in _PL:
        f = _mtof(m)
        n = int(dur * SR)
        t = np.arange(n) / SR
        s = np.zeros(n)
        for h in range(1, 14):
            fh = f * h * (1 + 0.0004 * h * h)
            if fh > 9000:
                break
            amp = abs(np.sin(np.pi * h * p)) / h ** 1.1
            s += amp * np.sin(2 * np.pi * fh * t) * np.exp(-t * (1.6 + 0.55 * h * h * f / 400))
        nz = _filt(np.random.default_rng(m).standard_normal(int(0.012 * SR)), 3000, "low") * 0.25
        s[:len(nz)] += nz * np.linspace(1, 0, len(nz))
        s *= np.minimum(1, t / 0.002)
        s[-int(0.05 * SR):] *= np.linspace(1, 0, int(0.05 * SR))
        _PL[key] = s / (np.abs(s).max() + 1e-9)
    return _PL[key] * vel


def bass(m, dur):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = _mtof(m)
    s = np.sin(2 * np.pi * f * t) + 0.25 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t / 0.2)
    env = np.exp(-t / 0.9) * np.minimum(1, t / 0.01)
    env[-int(0.04 * SR):] *= np.linspace(1, 0, int(0.04 * SR))
    return s * env


def glock(m, dur):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = _mtof(m)
    s = np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * 2.76 * f * t) * np.exp(-t / 0.15) \
        + 0.12 * np.sin(2 * np.pi * 5.4 * f * t) * np.exp(-t / 0.05)
    return s * np.exp(-t / 0.7) * np.minimum(1, t / 0.002)


def pad(notes, dur, rng):
    n = int(dur * SR)
    t = np.arange(n) / SR
    s = np.zeros(n)
    for m in notes:
        for det in (-0.12, 0.0, 0.11):
            f = _mtof(m) * 2 ** (det / 12)
            ph = rng.uniform(0, 6.28)
            s += np.sin(2 * np.pi * f * t + ph) + 0.18 * np.sin(4 * np.pi * f * t + ph)
    a = int(min(1.2, dur / 3) * SR)
    env = np.ones(n)
    env[:a] = np.linspace(0, 1, a)
    env[-a:] = np.minimum(env[-a:], np.linspace(1, 0, a))
    return _filt(s * env, 1400, "low")


def page_turn(rng, dur=0.42):
    n = int(dur * SR)
    t = np.arange(n) / SR
    nz = rng.standard_normal(n)
    sw = _filt(_filt(nz, 700, "high"), 5500, "low")
    env = np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 1.5
    crk = np.zeros(n)
    for _ in range(18):
        i = int(rng.uniform(0.05, 0.85) * n)
        L = int(rng.uniform(0.002, 0.006) * SR)
        crk[i:i + L] += rng.standard_normal(min(L, n - i)) * rng.uniform(0.3, 1.0)
    crk = _filt(crk, 1800, "high")
    return sw * env * 0.5 + crk * 0.35


def make_music(path, total, cuts, cfg=None, seed=4):
    rng = np.random.default_rng(seed)
    n = int(total * SR) + SR
    L, R = np.zeros(n), np.zeros(n)

    def add(buf, sig, t, g=1.0):
        i = int(t * SR)
        if i >= len(buf) or i < 0:
            return
        j = min(len(buf), i + len(sig))
        buf[i:j] += sig[:j - i] * g

    bar = 4 * BEAT
    end_t = cuts[-1] if cuts else total - 6
    nbars = int(np.ceil(end_t / bar))
    order = [0, 2, 1, 3, 0, 2, 1, 3]
    for b in range(nbars):
        t0 = b * bar
        root, notes = CHORDS[b % 4]
        for k, idx in enumerate(order):
            tt = t0 + k * BEAT / 2 + rng.uniform(-0.008, 0.008)
            vel = (0.95 if k in (0, 4) else 0.62) * rng.uniform(0.85, 1.05)
            m = root + 12 if k in (0, 4) else notes[idx]
            if k == 4 and b % 2:
                m = root + 19  # nada kelima di ketukan 3
            sig = pluck(m, vel)
            pan = 0.35 + 0.3 * (idx / 3)
            add(L, sig, tt, 0.55 * (1 - pan) + 0.2)
            add(R, sig, tt, 0.55 * pan + 0.2)
        if b >= 2:
            bs = bass(root, bar * 0.95)
            add(L, bs, t0, 0.32)
            add(R, bs, t0, 0.32)
            ps = pad(notes, bar + 0.6, rng)
            add(L, ps, t0, 0.028)
            add(R, ps, t0 + 0.012, 0.028)
        if b >= 4 and (b // 4) % 2 == 1:
            for mb, beat, m, ln in MELODY:
                if mb == b % 4:
                    g = glock(m, ln * BEAT + 0.8)
                    add(L, g, t0 + beat * BEAT, 0.07)
                    add(R, g, t0 + beat * BEAT + 0.01, 0.09)
    # akor penutup (D) yang dibiarkan berdering di scene terakhir
    for k, m in enumerate([38, 50, 57, 62, 66, 69, 74]):
        sig = pluck(m, 0.8, dur=5.5)
        add(L, sig, end_t + k * 0.045, 0.45)
        add(R, sig, end_t + k * 0.045 + 0.006, 0.45)
    g = glock(74, 3.0)
    add(L, g, end_t + 0.5, 0.08)
    add(R, g, end_t + 0.5, 0.1)
    ps = pad([50, 57, 62, 66], total - end_t + 0.5, rng)
    add(L, ps, end_t, 0.03)
    add(R, ps, end_t, 0.03)
    # efek balik halaman
    for c in cuts:
        pt = page_turn(rng)
        add(L, pt, c - 0.22, 0.5)
        add(R, pt, c - 0.2, 0.42)
    # reverb ruang kecil
    ir_n = int(1.8 * SR)
    ti = np.arange(ir_n) / SR
    for buf_i, buf in enumerate((L, R)):
        ir = np.random.default_rng(90 + buf_i).standard_normal(ir_n) * np.exp(-ti / 0.45)
        ir = _filt(ir, 4000, "low")
        wet = fftconvolve(buf, ir)[:n]
        wet *= np.abs(buf).max() / (np.abs(wet).max() + 1e-9)
        buf[:] = buf * 0.82 + wet * 0.3
    # fade in/out
    fi = int(0.4 * SR)
    fo = int(1.5 * SR)
    N = int(total * SR)
    st = np.stack([L[:N], R[:N]], axis=1)
    st[:fi] *= np.linspace(0, 1, fi)[:, None]
    st[-fo:] *= np.linspace(1, 0, fo)[:, None]
    st /= np.abs(st).max() + 1e-9
    wavfile.write(str(path), SR, (st * 0.89 * 32767).astype(np.int16))
