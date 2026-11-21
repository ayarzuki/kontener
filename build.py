"""Bikin video dari file konten JSON.

Contoh:
  python build.py konten/gta-vi.json            # render video penuh -> output/gta-vi.mp4
  python build.py konten/gta-vi.json --preview  # cuma 1 gambar contoh per scene -> output/gta-vi-preview/
  python build.py konten/gta-vi.json --jobs 4   # pakai 4 proses paralel

Butuh: Python 3.10+, ffmpeg di PATH, dan `pip install -r requirements.txt`.
"""
import argparse
import importlib.util
import json
import os
import shutil
import subprocess
import sys
from multiprocessing import Pool
from pathlib import Path

ROOT = Path(__file__).resolve().parent
STYLES = {p.name.split("-")[0] + "-" + p.name.split("-")[1]: p for p in (ROOT / "styles").iterdir() if p.is_dir()}


def load_module(style_dir, name):
    spec = importlib.util.spec_from_file_location(f"{style_dir.name}.{name}", style_dir / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def resolve_style(cfg):
    key = cfg.get("style", "style-01")
    if key not in STYLES:
        sys.exit(f"Style '{key}' tidak ada. Pilihan: {', '.join(sorted(STYLES))}")
    return STYLES[key]


_R = None
_STYLE = None


def _init(cfg, style_dir):
    global _R, _STYLE
    _STYLE = load_module(Path(style_dir), "style")
    _R = _STYLE.Renderer(cfg)


def _render_scene(args):
    si, outdir = args
    name, T = _R.scenes[si]
    tmp = Path(outdir) / f"s{si:02d}.tmp.mp4"
    out = Path(outdir) / f"s{si:02d}.mp4"
    W, H, FPS = _STYLE.W, _STYLE.H, _STYLE.FPS
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
           "-pix_fmt", "yuv420p", "-r", str(FPS), str(tmp)]
    pr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for t in range(T):
        pr.stdin.write(_R.frame(_R.starts[si] + t).tobytes())
    pr.stdin.close()
    rc = pr.wait()
    if rc == 0:
        os.replace(tmp, out)
    print(f"  scene {si + 1}/{len(_R.scenes)} ({name}) {'ok' if rc == 0 else 'GAGAL'}", flush=True)
    return rc


def main():
    ap = argparse.ArgumentParser(description="Render video dari file konten JSON")
    ap.add_argument("konten", help="path file JSON, mis. konten/gta-vi.json")
    ap.add_argument("--preview", action="store_true", help="hanya simpan 1 PNG per scene")
    ap.add_argument("--jobs", type=int, default=max(1, min(4, (os.cpu_count() or 2) - 1)))
    ap.add_argument("--out", default=None, help="nama file output (default: output/<nama-konten>.mp4)")
    a = ap.parse_args()

    kpath = Path(a.konten)
    cfg = json.loads(kpath.read_text(encoding="utf-8"))
    style_dir = resolve_style(cfg)
    slug = kpath.stem
    outdir = ROOT / "output"
    outdir.mkdir(exist_ok=True)

    if a.preview:
        _init(cfg, str(style_dir))
        from PIL import Image
        pdir = outdir / f"{slug}-preview"
        pdir.mkdir(exist_ok=True)
        for si, (name, T) in enumerate(_R.scenes):
            g = _R.starts[si] + int(T * 0.62)
            Image.fromarray(_R.frame(g)).save(pdir / f"{si + 1:02d}-{name}.png")
        print(f"Preview tersimpan di {pdir}")
        return

    if not shutil.which("ffmpeg"):
        sys.exit("ffmpeg tidak ditemukan. Install dulu (Windows: winget install Gyan.FFmpeg) lalu buka terminal baru.")

    work = outdir / f".{slug}-scenes"
    work.mkdir(exist_ok=True)
    _init(cfg, str(style_dir))
    n = len(_R.scenes)
    total = _R.total / _STYLE.FPS
    cuts = _R.cut_times()
    print(f"Render {slug}: {n} scene, {total:.1f} detik, style {style_dir.name}")

    with Pool(a.jobs, initializer=_init, initargs=(cfg, str(style_dir))) as pool:
        rcs = pool.map(_render_scene, [(i, str(work)) for i in range(n)], chunksize=1)
    if any(rcs):
        sys.exit("Ada scene yang gagal dirender.")

    music = load_module(style_dir, "music")
    wav = work / "music.wav"
    music.make_music(wav, total, cuts)

    lst = work / "list.txt"
    lst.write_text("".join(f"file 's{i:02d}.mp4'\n" for i in range(n)), encoding="utf-8")
    silent = work / "video.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst),
                    "-c", "copy", str(silent)], check=True)
    final = Path(a.out) if a.out else outdir / f"{slug}.mp4"
    tmp = final.with_name(final.stem + ".tmp.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(silent), "-i", str(wav),
                    "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                    "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", "44100", "-c:a", "aac", "-b:a", "192k",
                    "-shortest", "-movflags", "+faststart", str(tmp)], check=True)
    os.replace(tmp, final)
    print(f"Selesai: {final}")


if __name__ == "__main__":
    main()
