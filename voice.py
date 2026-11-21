"""Tambah voice-over (Fish Audio TTS) ke video hasil kontener.

Contoh:
  python voice.py konten/gta-vi.json --video output/GTA_VI_Dosenku.mp4
  python voice.py konten/sidang-skripsi.json --video output/Dosenku_Sidang_Skripsi_PS2.mp4
  python voice.py konten/sidang-skripsi.json --list-voices      # lihat suara Indonesia + ID-nya

API key dibaca dari environment variable FISH_AUDIO_API_KEY, atau dari file
~/.config/kontener/fish.env (isi: FISH_AUDIO_API_KEY=...). Jangan simpan key di repo.

Alur:
1. Ambil daftar kalimat dari konten: key "voiceover" (narasi), atau "lines" (dialog skit,
   pakai field "tts" kalau ada untuk ejaan/arah emosi) + "extra_voiceover".
2. Pilih suara per karakter dari "voices" (reference_id Fish Audio). Kalau kosong, dipilih
   otomatis dari library Fish Audio sesuai "voice_roles" (female/male, young/old) lalu
   disimpan di output/<nama>-voice/voices.json supaya konsisten saat dijalankan ulang.
3. Generate tiap kalimat (cache: kalimat yang tidak berubah tidak dibuat ulang).
4. Kalau ffmpeg ada: tempel ke video, kalimat yang kepanjangan dipercepat sedikit,
   musik otomatis mengecil saat ada suara (ducking) -> <video>-voice.mp4.
Hanya butuh Python standard library + ffmpeg.
"""
import argparse
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
API = "https://api.fish.audio"
UA = "kontener-voice/1.0"

FEMALE = ["female", "perempuan", "wanita", "cewek", "woman", "girl", "ibu", "mbak", "gadis", "feminine", "lady"]
MALE = ["male", "pria", "laki", "cowok", "man", "boy", "bapak", "masculine", "guy", "abang"]
OLD = ["old", "mature", "middle", "deep", "bapak", "ibu", "tua", "dewasa", "narrator", "berat", "wise"]
YOUNG = ["young", "youth", "teen", "muda", "remaja", "anak", "student", "mahasiswa", "casual", "santai"]
# Jangan pakai tiruan tokoh nyata / karakter berhak cipta untuk iklan.
AVOID = re.compile(r"prabowo|jokowi|gibran|anies|ganjar|megawati|bahlil|purbaya|dedi mulyadi|windah|raffi|ariel|"
                   r"willie|simanjuntak|deddy|corbuzier|atta|ricis|baim|soekarno|habibie|ahok|trump|obama|elon|"
                   r"ronaldo|messi|doraemon|nobita|unyil|sonic|brawl|mortal|spongebob|squidward|upin|ipin|naruto|"
                   r"mario|minecraft|roblox|cyberpunk|furina|genshin|brainrot|sahur|meme|google|ruangguru", re.I)


# ---------------------------------------------------------------- key & http
def api_key():
    k = os.environ.get("FISH_AUDIO_API_KEY", "").strip()
    if k:
        return k
    f = Path.home() / ".config" / "kontener" / "fish.env"
    if f.exists():
        for line in f.read_text(encoding="utf-8").splitlines():
            if line.strip().startswith("FISH_AUDIO_API_KEY="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    sys.exit("API key tidak ditemukan. Set environment variable FISH_AUDIO_API_KEY "
             "(lalu buka terminal baru) atau buat ~/.config/kontener/fish.env")


def http(method, path, key, body=None, params=None, headers=None, timeout=180):
    url = API + path + ("?" + urllib.parse.urlencode(params, doseq=True) if params else "")
    data = json.dumps(body).encode() if body is not None else None
    h = {"Authorization": f"Bearer {key}", "User-Agent": UA}
    if body is not None:
        h["Content-Type"] = "application/json"
    h.update(headers or {})
    req = urllib.request.Request(url, data=data, headers=h, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()


# ---------------------------------------------------------------- voices
def guess(item):
    txt = " ".join([item.get("title", ""), item.get("description", ""), " ".join(item.get("tags", []))]).lower()
    g = "female" if any(w in txt for w in FEMALE) else ("male" if any(w in txt for w in MALE) else "?")
    age = "old" if any(w in txt for w in OLD) else ("young" if any(w in txt for w in YOUNG) else "?")
    return g, age


def search_voices(key, language="id", n=60):
    st, raw = http("GET", "/model", key, params={"language": language, "page_size": min(n, 100),
                                                    "sort_by": "task_count"})
    if st != 200:
        sys.exit(f"Gagal mengambil daftar suara ({st}): {raw[:300]!r}")
    items = json.loads(raw).get("items", [])
    return [i for i in items if i.get("state", "trained") == "trained" and i.get("type", "tts") == "tts"]


def list_voices(key):
    items = search_voices(key)
    print(f"{'ID':34} {'gender':7} {'usia':6} pemakaian  judul")
    for it in items:
        g, a = guess(it)
        print(f"{it['_id']:34} {g:7} {a:6} {it.get('task_count', 0):9}  {it.get('title', '')[:60]}")
    print("\nSalin ID yang cocok ke bagian \"voices\" di file konten, mis. {\"bu\": \"<ID>\"}.")


def pick_voices(key, roles, fixed, cache_file):
    chosen = dict(fixed or {})
    if cache_file.exists():
        for k, v in json.loads(cache_file.read_text(encoding="utf-8")).items():
            chosen.setdefault(k, v)
    need = [w for w in roles if w not in chosen]
    if not need:
        return chosen
    items = search_voices(key, "id") or search_voices(key, "en")
    used = set(chosen.values())
    for who in need:
        want = roles[who] if isinstance(roles[who], dict) else {"gender": roles[who]}
        best, best_s = None, -1e9
        for it in items:
            if it["_id"] in used or AVOID.search(it.get("title", "") + " " + it.get("description", "")):
                continue
            g, a = guess(it)
            s = math.log1p(it.get("task_count", 0))
            if want.get("gender"):
                s += 6 if g == want["gender"] else (-1 if g == "?" else -20)
            if want.get("age"):
                s += 2 if a == want["age"] else (0 if a == "?" else -2)
            if s > best_s:
                best, best_s = it, s
        if best is None:
            sys.exit("Tidak menemukan suara yang cocok. Isi \"voices\" manual (lihat --list-voices).")
        chosen[who] = best["_id"]
        used.add(best["_id"])
        print(f"  suara {who:8} -> {best['_id']}  ({best.get('title', '')[:50]})")
    cache_file.parent.mkdir(parents=True, exist_ok=True)
    cache_file.write_text(json.dumps(chosen, indent=2), encoding="utf-8")
    return chosen


# ---------------------------------------------------------------- script
def voice_items(cfg):
    items = []
    if cfg.get("voiceover"):
        vo = cfg["voiceover"]
        for i, v in enumerate(vo):
            nxt = vo[i + 1]["t0"] if i + 1 < len(vo) else None
            mx = v.get("max") or ((nxt - v["t0"] - 0.1) if nxt else 4.0)
            items.append(dict(who=v.get("who", "narator"), text=v.get("tts", v["text"]), t0=float(v["t0"]), max=float(mx)))
    elif cfg.get("lines"):
        ls = cfg["lines"]
        for i, l in enumerate(ls):
            nxt = float(ls[i + 1]["t0"]) if i + 1 < len(ls) else None
            slot = float(l["t1"]) - float(l["t0"])
            mx = min(slot + 0.6, (nxt - float(l["t0"]) - 0.08)) if nxt else slot + 0.8
            items.append(dict(who=l["who"], text=l.get("tts", l["text"]), t0=float(l["t0"]), max=max(mx, slot)))
    for v in cfg.get("extra_voiceover", []):
        items.append(dict(who=v["who"], text=v.get("tts", v["text"]), t0=float(v["t0"]), max=float(v.get("max", 3.0))))
    return items


def tts(key, text, ref, model, speed, out):
    body = {"text": text, "reference_id": ref, "format": "mp3", "mp3_bitrate": 192, "normalize": True,
            "language": "id", "latency": "normal", "prosody": {"speed": speed}}
    st, raw = http("POST", "/v1/tts", key, body=body, headers={"model": model})
    if st == 402 and model != "s2.1-pro-free":
        print("  saldo/kuota model berbayar habis, coba model gratis s2.1-pro-free ...")
        return tts(key, text, ref, "s2.1-pro-free", speed, out)
    if st != 200:
        try:
            msg = json.loads(raw).get("message", raw[:200])
        except Exception:
            msg = raw[:200]
        sys.exit(f"TTS gagal ({st}): {msg}")
    out.write_bytes(raw)
    return model


def fake_tts(text, out):
    dur = max(0.8, len(text) / 15)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", f"sine=frequency=330:duration={dur}",
                    "-af", "volume=0.5", str(out)], check=True)


# ---------------------------------------------------------------- mix
def duration(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                       capture_output=True, text=True)
    return float(r.stdout.strip() or 0)


def mix(video, clips, out, loud=-14):
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-i", str(video)]
    for c in clips:
        cmd += ["-i", str(c["file"])]
    parts = []
    for i, c in enumerate(clips, start=1):
        d = duration(c["file"])
        tempo = 1.0
        if d > c["max"]:
            tempo = min(d / c["max"], 1.3)
            if d / c["max"] > 1.3:
                print(f"  ! kalimat {i} ({c['who']}) masih {d / 1.3:.1f} dtk > slot {c['max']:.1f} dtk, akan sedikit menimpa")
        ms = int(c["t0"] * 1000)
        parts.append(f"[{i}:a]aresample=44100,aformat=channel_layouts=stereo,atempo={tempo:.3f},"
                     f"adelay={ms}|{ms},volume=1.15[v{i}]")
    n = len(clips)
    vins = "".join(f"[v{i}]" for i in range(1, n + 1))
    parts.append(f"{vins}amix=inputs={n}:normalize=0:dropout_transition=0[vo]")
    parts.append("[vo]asplit=2[vo1][vo2]")
    parts.append("[0:a]aresample=44100,aformat=channel_layouts=stereo,volume=0.85[bed0]")
    parts.append("[bed0][vo1]sidechaincompress=threshold=0.02:ratio=12:attack=15:release=380[bed]")
    parts.append(f"[bed][vo2]amix=inputs=2:normalize=0:duration=first,loudnorm=I={loud}:TP=-1.5:LRA=11[aout]")
    cmd += ["-filter_complex", ";".join(parts), "-map", "0:v", "-map", "[aout]", "-c:v", "copy",
            "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-movflags", "+faststart", str(out)]
    subprocess.run(cmd, check=True)


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description="Voice-over Fish Audio untuk video kontener")
    ap.add_argument("konten")
    ap.add_argument("--video", help="video yang mau diberi suara (default output/<nama>.mp4)")
    ap.add_argument("--model", default="s2.1-pro", help="s2.1-pro (default), s2.1-pro-free, s2-pro, s1")
    ap.add_argument("--list-voices", action="store_true")
    ap.add_argument("--regen", action="store_true", help="buat ulang semua audio walau sudah ada")
    ap.add_argument("--repick", action="store_true", help="pilih ulang suara otomatis")
    ap.add_argument("--fake-tts", action="store_true", help=argparse.SUPPRESS)
    a = ap.parse_args()

    kpath = Path(a.konten)
    cfg = json.loads(kpath.read_text(encoding="utf-8"))
    slug = kpath.stem
    vdir = ROOT / "output" / f"{slug}-voice"
    vdir.mkdir(parents=True, exist_ok=True)
    key = None if a.fake_tts else api_key()
    if a.list_voices:
        list_voices(key)
        return

    items = voice_items(cfg)
    if not items:
        sys.exit("Konten ini belum punya \"voiceover\" atau \"lines\".")
    roles = cfg.get("voice_roles") or {w: {} for w in {i["who"] for i in items}}
    cache_file = vdir / "voices.json"
    if a.repick and cache_file.exists():
        cache_file.unlink()
    voices = {w: "fake" for w in roles} if a.fake_tts else pick_voices(key, roles, cfg.get("voices"), cache_file)
    speed = cfg.get("voice_speed", {})

    manifest_f = vdir / "manifest.json"
    manifest = json.loads(manifest_f.read_text(encoding="utf-8")) if manifest_f.exists() else {}
    clips = []
    print(f"Membuat {len(items)} kalimat suara ...")
    for n, it in enumerate(items, start=1):
        ref = voices[it["who"]]
        sp = float(speed.get(it["who"], 1.0)) if isinstance(speed, dict) else float(speed)
        sig = hashlib.sha1(json.dumps([it["text"], ref, a.model, sp]).encode()).hexdigest()[:12]
        f = vdir / f"{n:02d}_{it['who']}.mp3"
        if a.regen or manifest.get(f.name) != sig or not f.exists():
            print(f"  [{n:02d}] {it['who']}: {it['text']}")
            if a.fake_tts:
                fake_tts(it["text"], f)
            else:
                tts(key, it["text"], ref, a.model, sp, f)
            manifest[f.name] = sig
            manifest_f.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        clips.append(dict(it, file=f))

    video = Path(a.video) if a.video else ROOT / "output" / f"{slug}.mp4"
    if not shutil.which("ffmpeg"):
        print(f"\nAudio tersimpan di {vdir}\nffmpeg tidak ditemukan, jadi belum ditempel ke video. "
              "Install ffmpeg (winget install Gyan.FFmpeg) lalu jalankan ulang perintah yang sama.")
        return
    if not video.exists():
        sys.exit(f"Video {video} tidak ada. Render dulu: python build.py {a.konten}")
    out = video.with_name(video.stem + "-voice.mp4")
    print("Menempel suara ke video ...")
    mix(video, clips, out)
    print(f"Selesai: {out}")


if __name__ == "__main__":
    main()
