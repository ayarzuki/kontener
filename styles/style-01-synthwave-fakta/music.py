"""Musik latar synthwave orisinal (dibuat dari nol, bebas royalti).

120 BPM, akor Am-F-C-G, impact di awal, whoosh + hit di tiap pergantian scene,
fade out di 1,5 detik terakhir. Panjang durasi scene sebaiknya kelipatan 0,5 detik
agar pergantian scene jatuh tepat di ketukan.
"""
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, lfilter

SR = 44100
BPM = 120
BEAT = 60 / BPM


def _mtof(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def _filt(x, fc, kind):
    b, a = butter(2, fc, btype=kind, fs=SR)
    return lfilter(b, a, x)


def _saw(f, n, ph=0.0):
    t = np.arange(n) / SR
    return 2 * ((t * f + ph) % 1.0) - 1


def make_music(path, total, cuts, seed=3):
    N = int(SR * total)
    rng = np.random.default_rng(seed)

    def add(buf, sig, start):
        i = int(start * SR)
        if i >= len(buf):
            return
        j = min(len(buf), i + len(sig))
        buf[i:j] += sig[: j - i]

    CH = [(45, [57, 60, 64]), (41, [53, 57, 60]), (48, [55, 60, 64]), (43, [55, 59, 62])]
    BAR = 4 * BEAT
    nbars = int(np.ceil(total / BAR))
    t_all = np.arange(N) / SR
    duck = 1 - 0.55 * np.exp(-((t_all % BEAT) / 0.11))
    end_beats = total - 1.4

    pad = np.zeros(N)
    for b in range(nbars):
        _, notes = CH[b % 4]
        n = int(BAR * SR) + int(0.5 * SR)
        sig = np.zeros(n)
        for m in notes:
            f = _mtof(m)
            sig += _saw(f * 2 ** (0.07 / 12), n) + _saw(f * 2 ** (-0.07 / 12), n, 0.3)
        env = np.ones(n)
        a, r = int(0.25 * SR), int(0.5 * SR)
        env[:a] = np.linspace(0, 1, a)
        env[-r:] = np.linspace(1, 0, r)
        add(pad, sig * env, b * BAR)
    pad = _filt(pad, 1800, "low") * 0.045 * duck

    bass = np.zeros(N)
    step = BEAT / 2
    for k in range(int(total / step)):
        root, _ = CH[int(k * step / BAR) % 4]
        f = _mtof(root)
        n = int(step * SR)
        tt = np.arange(n) / SR
        sig = 0.6 * _saw(f, n) + 0.5 * np.sin(2 * np.pi * f / 2 * tt)
        add(bass, sig * np.exp(-tt / 0.16) * np.minimum(1, tt / 0.004), k * step)
    bass = _filt(bass, 650, "low") * 0.32 * duck

    arp = np.zeros(N)
    step = BEAT / 4
    pat = [0, 1, 2, 1, 0, 2, 1, 2]
    for k in range(int(total / step)):
        tpos = k * step
        _, notes = CH[int(tpos / BAR) % 4]
        m = notes[pat[k % 8]] + 12 + (12 if (k % 16) in (6, 14) else 0)
        f = _mtof(m)
        n = int(0.2 * SR)
        tt = np.arange(n) / SR
        sig = 0.6 * np.sign(np.sin(2 * np.pi * f * tt)) + 0.4 * _saw(f, n)
        add(arp, sig * np.exp(-tt / 0.07) * np.minimum(1, tt / 0.003), tpos)
    arp = _filt(arp, 3200, "low") * 0.05
    d = int(0.375 * SR)
    arpL, arpR = arp.copy(), arp.copy()
    for i in range(1, 4):
        g = 0.38 ** i
        (arpR if i % 2 else arpL)[d * i:] += arp[:-d * i] * g

    drums = np.zeros(N)
    nk = int(0.45 * SR)
    tt = np.arange(nk) / SR
    kick = np.sin(2 * np.pi * np.cumsum(46 + 120 * np.exp(-tt / 0.035)) / SR) * np.exp(-tt / 0.22)
    kick += 0.3 * rng.standard_normal(nk) * np.exp(-tt / 0.004)
    ns = int(0.35 * SR)
    ts = np.arange(ns) / SR
    b, a = butter(2, [1000, 5200], btype="band", fs=SR)
    clap = lfilter(b, a, rng.standard_normal(ns)) * np.exp(-ts / 0.11) * 1.4
    clap += 0.4 * np.sin(2 * np.pi * 190 * ts) * np.exp(-ts / 0.05)
    nh = int(0.08 * SR)
    hat = _filt(rng.standard_normal(nh), 7500, "high") * np.exp(-(np.arange(nh) / SR) / 0.022)
    for k in range(int(total / BEAT)):
        tb = k * BEAT
        if tb > end_beats:
            break
        add(drums, kick * 0.85, tb)
        if k % 2 == 1:
            add(drums, clap * 0.32, tb)
        add(drums, hat * 0.16, tb + BEAT / 2)
        add(drums, hat * 0.06, tb + BEAT / 4)
        add(drums, hat * 0.06, tb + 3 * BEAT / 4)

    fx = np.zeros(N)
    ni = int(2.2 * SR)
    ti = np.arange(ni) / SR
    boom = np.sin(2 * np.pi * (38 + 60 * np.exp(-ti / 0.08)) * ti) * np.exp(-ti / 0.55)
    crash = _filt(rng.standard_normal(ni), 3000, "high") * np.exp(-ti / 0.6) * 0.35
    add(fx, (boom * 0.9 + crash) * 0.8, 0.03)
    for c in cuts:
        nw = int(0.55 * SR)
        tw = np.arange(nw) / SR
        noise = rng.standard_normal(nw)
        b1, a1 = butter(2, [300, 1500], btype="band", fs=SR)
        b2, a2 = butter(2, [1500, 7000], btype="band", fs=SR)
        mix = np.linspace(0, 1, nw)
        sig = lfilter(b1, a1, noise) * (1 - mix) + lfilter(b2, a2, noise) * mix
        env = np.where(tw < 0.42, (tw / 0.42) ** 2, np.exp(-(tw - 0.42) / 0.05))
        add(fx, sig * env * 0.28, c - 0.42)
        nd = int(0.5 * SR)
        td = np.arange(nd) / SR
        add(fx, np.sin(2 * np.pi * (55 + 40 * np.exp(-td / 0.05)) * td) * np.exp(-td / 0.2) * 0.35, c)
    nf = int(1.6 * SR)
    tf = np.arange(nf) / SR
    add(fx, np.sin(2 * np.pi * (40 + 50 * np.exp(-tf / 0.08)) * tf) * np.exp(-tf / 0.6) * 0.7
        + _filt(rng.standard_normal(nf), 3000, "high") * np.exp(-tf / 0.7) * 0.25, end_beats - 0.1)

    mono = pad + bass + drums + fx
    st = np.stack([mono + arpL + pad * 0.15, mono + arpR - pad * 0.15], 1)
    fade = np.ones(N)
    f0 = int((total - 1.5) * SR)
    fade[f0:] = np.linspace(1, 0, N - f0) ** 1.5
    st *= fade[:, None]
    st = np.tanh(st * 1.4) / np.tanh(1.4)
    st /= np.max(np.abs(st)) / 0.89
    wavfile.write(str(path), SR, (st * 32767).astype(np.int16))
