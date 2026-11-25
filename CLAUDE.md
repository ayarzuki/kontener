# CLAUDE.md — kontener

Repo ini berisi template video konten pendek (vertikal 1080×1920) untuk marketing **Dosenku**.
Pemilik: Zuki. Bahasa kerja: Indonesia santai. Mesin: Windows (PowerShell), repo di
`C:\Users\PAB-ACDM-NB3299\Documents\kontener`, remote `github.com/ayarzuki/kontener` (private).

## Tentang produk (jangan mengarang fitur lain)

- **Dosenku** = pendamping skripsi berbasis AI untuk mahasiswa Indonesia.
- Fitur: brainstorm judul, kerangka Bab 1–5, rujukan jurnal ber-DOI (Crossref & OpenAlex, bisa dicek sendiri),
  latihan sidang. Gratis untuk mulai.
- URL resmi di video: **dosenku.biz.id** (bukan pages.dev). Tagline: "Skripsi terarah. Dosen senang."
- Warna brand: teal `#0f766e`. Watermark teks "Dosenku".
- Posisikan sebagai alat bimbingan, **bukan joki skripsi**.

## Perintah

```powershell
pip install -r requirements.txt                      # sekali (numpy, pillow, scipy, moderngl)
python build.py konten\<nama>.json --preview         # 1 PNG per scene -> output\<nama>-preview\  (cek dulu!)
python build.py konten\<nama>.json                   # render penuh -> output\<nama>.mp4
python voice.py konten\<nama>.json                   # voice-over Fish Audio -> output\<nama>-voice.mp4
python voice.py konten\<nama>.json --video output\X.mp4   # beri suara ke video tertentu
python voice.py konten\<nama>.json --list-voices     # daftar suara Indonesia + ID
```

- Butuh `ffmpeg` di PATH (sudah terpasang via winget).
- Set `PYTHONUTF8=1` kalau output di-redirect ke file (konsol Windows cp1252 bikin UnicodeEncodeError).
- API key Fish Audio ada di env `FISH_AUDIO_API_KEY` (atau `~/.config/kontener/fish.env`).
  **Jangan pernah** mencetak, menyalin, atau meng-commit key.

## Struktur

- `build.py` — JSON konten → MP4. Memilih style dari key `"style"` (`style-01`, `style-02`, …).
- `voice.py` — TTS Fish Audio per kalimat (ada cache), lalu ditempel ke video dengan ducking musik.
- `konten/*.json` — satu file = satu video. `_template.json` = template style-01.
- `styles/style-01-synthwave-fakta/` — listicle "N fakta" synthwave + polling A/B. Panduan: README di folder itu.
- `styles/style-02-ps2-cutscene/` — skit komedi 3D low-poly ala cutscene PS2 + subtitle. Koreografi per skit
  ada di `skits/<nama>.py`; teks dialog di JSON. Panduan: README di folder itu.
- `styles/style-03-parchment-explainer/` — penjelas sejarah ala buku cerita (tinta + cat air di perkamen, diorama
  isometrik, Ken Burns, subtitle sobekan kertas). Adegan digambar di `stories/<cerita>.py`; narasi = `voiceover`.
- `styles/style-04-lofi-pixel/` — loop "study with me" pixel art 270×480 (×4): kamar kos hujan, lo-fi, timer pomodoro,
  notifikasi & CTA jendela retro. Font bitmap 5×7 sendiri (kapital saja). Narasi = `voiceover`, subtitle = `captions`.
- `styles/style-05-animasi-3d/` — film pendek 3D sinematik (moderngl): tokoh Nara berhijab di kamar kos, DOF, bloom.
  Shot/pose/cahaya per cerita di `stories/<nama>.py`; overlay data (headline, cards, poll, disclaimer, cta, captions)
  di JSON. Render berat (±15–25 mnt per menit video): render per scene, cek frame per frame.
- `styles/style-06-kartun-flat/` — gaya gambar explainer "money mindset" vektor flat: rumus diketik, angka berhitung,
  stempel istilah, pita subtitle karaoke. Gaya visual saja: jumlah tokoh & alur bebas, ditulis di `cerita/<nama>.py`
  (`build(ctx)` → elemen, potongan, durasi). Render cepat (±30 dtk).
- `output/` — hasil render, tidak masuk git.

## Alur membuat video baru

1. **Riset dulu** kalau topiknya berita/tren: cari fakta terbaru, catat sumber + tanggal. Setiap fakta di layar
   wajib punya baris `source`. Angle yang kena untuk penonton Indonesia: kebanggaan lokal, harga dalam rupiah,
   akses/platform di Indonesia, rekor/angka, kebutuhan praktis.
2. Salin JSON contoh dari style yang dipakai (`gta-vi.json` / `_template.json` untuk style-01,
   `sidang-skripsi.json` untuk style-02, `sejarah-rujukan.json` untuk style-03, `lofi-bab2.json` untuk style-04,
   `malam-bimbingan.json` / `anthropic-turun.json` untuk style-05, `mindset-es-teh.json` / `bocor-halus.json` untuk
   style-06), isi kontennya. Style-05/06 juga butuh file cerita baru.
3. `--preview`, **lihat PNG-nya** (teks tidak boleh tabrakan/terpotong), baru render penuh.
4. Kalau perlu suara: isi `voiceover` (style-01/03/04/05/06) atau pakai `lines` (+ `tts`, `extra_voiceover`) untuk style-02,
   lalu `voice.py`. Pastikan tidak ada peringatan "kalimat … > slot"; kalau ada, padatkan teks atau naikkan
   `voice_speed`.
5. Commit + push (lihat bagian Git).

## Aturan konten

- Semua visual & musik dibuat oleh kode. **Jangan** pakai logo, karakter, key art, footage, atau lagu pihak lain.
  Nama produk/game boleh disebut sebagai teks.
- Batas teks style-01: headline 2 baris, body ±110 karakter, sumber 1 baris.
- Style-02: kalau timing dialog digeser > ±0,3 dtk atau cerita baru, sesuaikan/buat `skits/<nama>.py`
  (SHOTS, pose per waktu). Durasi scene kelipatan 0,5 dtk supaya pas ketukan musik.
- **Brand default semua video = Dosenku** (watermark/footer "Dosenku", CTA dosenku.biz.id, warna teal). Akun lain
  (mis. @kalpitalbiz) hanya kalau Zuki minta eksplisit untuk video itu. Topik umum (berita, ekonomi) tetap ditutup
  dengan jembatan ke skripsi, mis. "cari rujukan jurnal ber-DOI di Dosenku".
- Konten keuangan: selalu tampilkan "bukan nasihat investasi/keuangan"; angka karangan diberi label
  "ilustrasi" dan hitungannya harus konsisten; angka pasar wajib dicek ke sumber + tanggal.
- Hook boleh memancing komentar, tapi jangan pakai stereotip SARA.

## Aturan suara (Fish Audio)

- **Jangan pakai suara tiruan tokoh nyata** (politisi, artis, kreator: Prabowo, Jokowi, Windah, dll.) atau
  karakter berhak cipta. `voice.py` punya filter `AVOID`, tapi tetap cek judul suara yang dipilih.
- Suara yang sudah dipakai & aman: narator `248cf6d6ff744c2ba09d379de5c118ae` (Toren),
  wanita `d36af9647ef647118c64b23b97087838` (Narator Indonesia),
  pria paruh baya `6d7909c639cc40499a4e9f8ed219136d` (Agus Iki),
  pria muda `d2a7c0f595dc4004858fe1e7b3898069` (Pria Muda Penjelas).
- Simpan pilihan suara di `"voices"` pada JSON agar konsisten. Model default `s2.1-pro`; emosi pakai tanda
  kurung siku di `tts`, mis. `[whispering]`, `[surprised]`. Angka/singkatan sulit ditulis sebagai ejaan
  (mis. "ber-de-o-i") di field `tts`, subtitle tetap pakai `text`.

## Git

- Commit langsung ke `main` lalu `git push origin main`; pesan commit bahasa Indonesia, singkat.
- Jangan commit `output/`, file `.env`, key, atau file `.bat` lokal (`jalankan-voice.bat`, `daftar-suara.bat`).

## Cara kerja dengan Zuki

- Jalankan perintah lewat CLI, jangan minta/menyuruh pakai kontrol layar.
- Kirim hasil akhir sebagai path file di `output\` + ringkasan singkat; sebutkan sumber fakta yang dipakai.
