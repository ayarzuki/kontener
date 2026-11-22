"""Lo-fi hip-hop orisinal: 80 BPM swing, drum berdebu, Rhodes (FM) Fmaj9-Em7-Dm9-Cmaj7, bass, melodi tipis,
kresek vinyl, suara hujan, guntur saat petir, bunyi notifikasi retro, arpeggio di panel CTA.
"""
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, fftconvolve, lfilter

SR = 44100
LOUDNESS = -17
CHORDS = [(41, [53, 57, 60, 64, 67]), (40, [52, 55, 59, 62]), (38, [50, 53, 57, 60, 64]), (36, [48, 52, 55, 59])]
MEL = [(0, 1.5, 76), (0, 2.5, 74), (1, 0.5, 71), (1, 2, 72), (2, 1, 69), (2, 2.5, 72), (3, 0.5, 71), (3, 2, 67)]


def mtof(m):
    return 440 * 2 ** ((m - 69) / 12)


def filt(x, f, kind, order=2):
    b, a = butter(order, f, btype=kind, fs=SR)
    return lfilter(b, a, x)


def rhodes(m, dur=2.8, vel=1.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = mtof(m) * (1 + 0.002 * np.sin(2 * np.pi * 0.7 * t))
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.sin(ph + 0.9 * np.exp(-t / 0.4) * np.sin(ph)) + 0.15 * np.sin(2 * ph) * np.exp(-t / 0.3)
    s *= (1 + 0.25 * np.sin(2 * np.pi * 4.5 * t))  # tremolo
    env = np.exp(-t / 1.6) * np.minimum(1, t / 0.008)
    env[-int(0.08 * SR):] *= np.linspace(1, 0, int(0.08 * SR))
    return s * env * vel


def bass(m, dur):
    n = int(dur * SR)
    t = np.arange(n) / SR
    s = np.sin(2 * np.pi * mtof(m) * t) + 0.2 * np.sin(4 * np.pi * mtof(m) * t)
    env = np.minimum(1, t / 0.01) * np.exp(-t / 1.2)
    env[-int(0.05 * SR):] *= np.linspace(1, 0, int(0.05 * SR))
    return filt(s * env, 300, "low")


def kick():
    t = np.arange(int(0.35 * SR)) / SR
    return np.sin(2 * np.pi * np.cumsum(48 + 70 * np.exp(-t / 0.035)) / SR) * np.exp(-t / 0.16)


def snare(rng):
    n = int(0.3 * SR)
    t = np.arange(n) / SR
    nz = filt(filt(rng.standard_normal(n), 1200, "high"), 5000, "low") * np.exp(-t / 0.07)
    body = np.sin(2 * np.pi * 190 * t) * np.exp(-t / 0.05)
    return nz * 0.7 + body * 0.4


def hat(rng):
    n = int(0.06 * SR)
    return filt(rng.standard_normal(n), 6000, "high") * np.exp(-np.arange(n) / SR / 0.018)


def blip(m1, m2):
    out = np.zeros(int(0.5 * SR))
    for k, m in enumerate((m1, m2)):
        t = np.arange(int(0.25 * SR)) / SR
        s = np.sign(np.sin(2 * np.pi * mtof(m) * t)) * 0.4 * np.exp(-t / 0.08)
        i = int(k * 0.1 * SR)
        out[i:i + len(s)] += filt(s, 3000, "low")
    return out


def thunder(rng, dur=4.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = filt(rng.standard_normal(n), 180, "low") * 6
    env = (np.minimum(1, t / 0.15) * np.exp(-t / 1.3)) * (1 + 0.5 * np.sin(2 * np.pi * 3 * t) * np.exp(-t))
    return x * env


def make_music(path, total, cuts, cfg=None, seed=9):
    cfg = cfg or {}
    rng = np.random.default_rng(seed)
    bpm = float(cfg.get("bpm", 80))
    beat = 60 / bpm
    bar = 4 * beat
    n = int((total + 2) * SR)
    L, R = np.zeros(n), np.zeros(n)

    def add(sig, t, g=1.0, pan=0.0):
        i = int(t * SR)
        if i < 0 or i >= n:
            return
        j = min(n, i + len(sig))
        L[i:j] += sig[:j - i] * g * (1 - pan)
        R[i:j] += sig[:j - i] * g * (1 + pan)

    K, SN = kick(), snare(rng)
    swing = beat * 0.16
    nb = int(np.ceil(total / bar))
    for b in range(nb):
        tb = b * bar
        root, ch = CHORDS[b % 4]
        for k, m in enumerate(ch):
            add(rhodes(m, bar * 0.98, 0.9 if k else 1.0), tb + k * 0.012 + (beat * 2.5 if b % 2 and k > 2 else 0), 0.07,
                pan=-0.3 + k * 0.15)
        add(bass(root, beat * 1.5), tb, 0.35)
        add(bass(root, beat * 1.2), tb + 2.5 * beat, 0.3)
        if b >= 1:
            add(K, tb, 0.5)
            add(K, tb + 2.5 * beat, 0.4)
            add(SN, tb + beat, 0.28)
            add(SN, tb + 3 * beat, 0.28)
            for k in range(8):
                add(hat(rng), tb + k * beat / 2 + (swing if k % 2 else 0), 0.09 if k % 2 else 0.12, pan=0.3)
        if b >= 2 and b % 2 == 0:
            for (mb, bt, m) in MEL:
                if mb % 2 == (b // 2) % 2 or mb >= 2:
                    add(rhodes(m, 1.4, 0.8), tb + (mb % 2) * bar / 2 + bt * beat / 2, 0.05, pan=0.25)
    # rain + vinyl
    rain = filt(filt(rng.standard_normal(n), 400, "high"), 3500, "low") * 0.05
    rain *= 1 + 0.2 * np.sin(2 * np.pi * 0.07 * np.arange(n) / SR)
    L += rain
    R += np.roll(rain, 911)
    hiss = filt(rng.standard_normal(n), 5000, "high") * 0.006
    L += hiss
    R += hiss
    for _ in range(int(total * 9)):
        i = int(rng.uniform(0, n - 300))
        c = rng.standard_normal(120) * np.exp(-np.arange(120) / 20) * rng.uniform(0.02, 0.08)
        L[i:i + 120] += c
        R[i:i + 120] += c * 0.8
    for lt in cfg.get("lightning", []):
        add(thunder(rng), float(lt) + 0.9, 0.35)
    for nf in cfg.get("notifs", []):
        add(blip(81, 88), float(nf["t0"]), 0.18)
    cta = cfg.get("cta")
    if cta:
        for k, m in enumerate((65, 69, 72, 76, 79)):
            add(rhodes(m, 2.0), float(cta["t0"]) + k * 0.08, 0.12)
    # tape: low-pass + saturasi + ruang
    for buf in (L, R):
        buf[:] = np.tanh(filt(buf, 6500, "low") * 1.3)
    ir_n = int(1.2 * SR)
    ti = np.arange(ir_n) / SR
    for i, buf in enumerate((L, R)):
        ir = filt(np.random.default_rng(70 + i).standard_normal(ir_n) * np.exp(-ti / 0.3), 3000, "low")
        wet = fftconvolve(buf, ir)[:n]
        buf += wet * 0.25 * np.abs(buf).max() / (np.abs(wet).max() + 1e-9)
    N = int(total * SR)
    st = np.stack([L[:N], R[:N]], 1)
    fi, fo = int(0.5 * SR), int(1.5 * SR)
    st[:fi] *= np.linspace(0, 1, fi)[:, None]
    st[-fo:] *= np.linspace(1, 0, fo)[:, None]
    st /= np.abs(st).max() + 1e-9
    wavfile.write(str(path), SR, (st * 0.89 * 32767).astype(np.int16))
