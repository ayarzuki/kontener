# kontener

Kumpulan gaya (style) video konten pendek untuk marketing **Dosenku** (dan akun lain, mis. @kalpitalbiz).
Tiap style adalah template: isi teksnya ditulis di satu file JSON, lalu satu perintah
menghasilkan video MP4 vertikal (1080×1920, 30 fps) lengkap dengan musik dan watermark.

## Daftar style

| Kode | Nama | Cocok untuk | Contoh |
|---|---|---|---|
| `style-01` | [Synthwave Fakta](styles/style-01-synthwave-fakta/) | Listicle "N fakta" seputar topik yang lagi ramai (game, gadget, tren), ditutup polling A/B di komentar | [`konten/gta-vi.json`](konten/gta-vi.json) |
| `style-02` | [PS2 Cutscene Skit](styles/style-02-ps2-cutscene/) | Skit komedi 3D low-poly ala cutscene PS2 dengan subtitle, punchline soal produk, end card URL | [`konten/sidang-skripsi.json`](konten/sidang-skripsi.json) |
| `style-03` | [Parchment Explainer](styles/style-03-parchment-explainer/) | Penjelas sejarah ala buku cerita (tinta + cat air di perkamen), narasi + subtitle, produk sebagai jawaban di akhir | [`konten/sejarah-rujukan.json`](konten/sejarah-rujukan.json) |
| `style-04` | [Lo-fi Pixel Study](styles/style-04-lofi-pixel/) | Loop "study with me" pixel art: kamar kos hujan, musik lo-fi, timer pomodoro, notifikasi & CTA produk | [`konten/lofi-bab2.json`](konten/lofi-bab2.json) |
| `style-05` | [3D Animasi Sinematik](styles/style-05-animasi-3d/) | Film pendek 3D rasa film animasi bioskop (tokoh orisinal berhijab, kamar kos), bisa untuk cerita produk atau berita dengan kartu data + polling | [`konten/malam-bimbingan.json`](konten/malam-bimbingan.json), [`konten/anthropic-turun.json`](konten/anthropic-turun.json) |
| `style-06` | [Kartun Flat](styles/style-06-kartun-flat/) | Gaya gambar explainer viral "money mindset": tokoh flat, rumus diketik, angka berhitung, stempel istilah, pita subtitle. Jumlah tokoh & alur bebas | [`konten/mindset-es-teh.json`](konten/mindset-es-teh.json), [`konten/mindset-gaji.json`](konten/mindset-gaji.json), [`konten/bocor-halus.json`](konten/bocor-halus.json) |

![Preview style-01](styles/style-01-synthwave-fakta/preview.jpg)

![Preview style-02](styles/style-02-ps2-cutscene/preview.jpg)

![Preview style-03](styles/style-03-parchment-explainer/preview.jpg)

![Preview style-04](styles/style-04-lofi-pixel/preview.jpg)

![Preview style-05](styles/style-05-animasi-3d/preview.jpg)

![Preview style-06](styles/style-06-kartun-flat/preview.jpg)

## Setup (sekali saja)

1. Install **Python 3.10+** dan **ffmpeg**. Di Windows:
   ```powershell
   winget install Python.Python.3.12
   winget install Gyan.FFmpeg
   ```
   Tutup lalu buka lagi terminal setelah install.
2. Di folder repo ini:
   ```powershell
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```

## Bikin video baru

1. Salin contoh dari style yang mau dipakai, mis. `copy konten\_template.json konten\topik-baru.json`
   (style-01), `copy konten\sidang-skripsi.json konten\skit-baru.json` (style-02), atau
   `copy konten\sejarah-rujukan.json konten\sejarah-baru.json` (style-03), atau
   `copy konten\lofi-bab2.json konten\lofi-baru.json` (style-04). Style-05 dan style-06 butuh file cerita
   (`stories/<nama>.py` / `cerita/<nama>.py`) selain JSON, lihat README style-nya.
2. Edit isinya. Panduan tiap field ada di README style-nya.
3. Cek tampilan dulu (cepat, hanya gambar):
   ```powershell
   python build.py konten\topik-baru.json --preview
   ```
   Hasilnya di `output\topik-baru-preview\`. Pastikan tidak ada teks yang terlalu panjang.
4. Render videonya:
   ```powershell
   python build.py konten\topik-baru.json
   ```
   Hasilnya `output\topik-baru.mp4`, siap upload ke TikTok, Reels, atau Shorts.

## Voice-over (Fish Audio)

`voice.py` membuat suara TTS lewat API Fish Audio lalu menempelkannya ke video
(musik otomatis mengecil saat ada suara).

1. Simpan API key sebagai environment variable Windows `FISH_AUDIO_API_KEY`
   (Start → "Edit environment variables for your account" → New), lalu buka terminal baru.
   Alternatif: file `%USERPROFILE%\.config\kontener\fish.env` berisi `FISH_AUDIO_API_KEY=...`.
   **Jangan** taruh key di folder repo ini.
2. Jalankan:
   ```powershell
   python voice.py konten\gta-vi.json --video output\GTA_VI_Dosenku.mp4
   python voice.py konten\sidang-skripsi.json --video output\Dosenku_Sidang_Skripsi_PS2.mp4
   ```
   Hasil: `output\<nama video>-voice.mp4`. Tanpa `--video`, dipakai `output\<nama-konten>.mp4`.
3. Suara per karakter dipilih otomatis dari library Fish Audio (bahasa Indonesia) sesuai
   `voice_roles`, lalu dicatat di `output\<nama>-voice\voices.json`. Untuk menggantinya:
   `python voice.py konten\x.json --list-voices`, salin ID ke `"voices"` di file konten
   (mis. `"voices": {"bu": "<ID>"}`), lalu jalankan ulang. `--repick` memilih ulang otomatis.

Di file konten:
- `voiceover`: narasi bebas `{t0, text, tts?, max?}` (style-01, 03, 04, 05, 06; di style-03 dan 06 `text` juga jadi
  subtitle, di style-04 subtitle ditulis terpisah di `captions`, di style-05 subtitle aktif dengan `"captions": true`).
- `lines[].tts`: teks khusus TTS untuk dialog skit (ejaan, mis. "ber-de-o-i", atau arah emosi
  `[whispering]`, `[surprised]`), subtitle tetap memakai `text` (style-02).
- `extra_voiceover`: suara tambahan tanpa subtitle (mis. penutup iklan).
- `voice_speed`: kecepatan per karakter (0,5–2,0).

Kalimat yang sudah dibuat disimpan (cache), jadi menjalankan ulang hanya membuat kalimat yang berubah.
Kalau saldo model berbayar habis, script otomatis mencoba model gratis `s2.1-pro-free`.

## Struktur folder

```
kontener/
├─ CLAUDE.md                 # panduan untuk Claude Code (perintah, aturan konten & suara)
├─ build.py                  # perintah utama: JSON -> MP4
├─ voice.py                  # voice-over Fish Audio + mixing ke video
├─ konten/                   # satu file JSON = satu video
│  ├─ _template.json         # template style-01
│  ├─ gta-vi.json            # contoh style-01
│  ├─ sidang-skripsi.json    # contoh style-02
│  ├─ sejarah-rujukan.json   # contoh style-03
│  ├─ lofi-bab2.json         # contoh style-04
│  ├─ malam-bimbingan.json   # contoh style-05 (Dosenku)
│  ├─ anthropic-turun.json   # contoh style-05 (berita pasar, @kalpitalbiz)
│  ├─ mindset-es-teh.json    # contoh style-06 (4 anak)
│  ├─ mindset-gaji.json      # contoh style-06 (4 karyawan)
│  └─ bocor-halus.json       # contoh style-06 (1 tokoh)
├─ styles/
│  ├─ style-01-synthwave-fakta/
│  │  ├─ README.md           # panduan gaya: warna, font, layout, timing, tipe hero
│  │  ├─ style.py            # mesin visual (Renderer)
│  │  ├─ music.py            # musik latar orisinal
│  │  └─ preview.jpg
│  ├─ style-02-ps2-cutscene/
│  │  ├─ README.md           # panduan skit, pose, karakter, audio
│  │  ├─ style.py            # kamera, subtitle, end card (Renderer)
│  │  ├─ engine.py           # renderer 3D low-poly (moderngl)
│  │  ├─ character.py        # karakter ber-rig
│  │  ├─ sets.py             # ruang sidang, props, bukit
│  │  ├─ skits/sidang.py     # koreografi skit "Sidang Skripsi"
│  │  ├─ music.py            # musik lounge + SFX
│  │  └─ preview.jpg
│  ├─ style-03-parchment-explainer/
│  │  ├─ README.md           # panduan gaya, field JSON, cara menggambar adegan
│  │  ├─ style.py            # kamera Ken Burns, transisi tinta->cat, label, subtitle (Renderer)
│  │  ├─ ink.py              # toolkit tinta + cat air + perkamen + tokoh
│  │  ├─ props.py            # diorama, rak, pipa, dll.
│  │  ├─ stories/sejarah-rujukan.py  # adegan cerita "Sejarah daftar pustaka"
│  │  ├─ music.py            # folk gitar petik + efek balik halaman
│  │  └─ preview.jpg
│  ├─ style-04-lofi-pixel/
│  │  ├─ README.md           # panduan field JSON, font, audio
│  │  ├─ style.py            # adegan kamar kos + overlay jendela retro (Renderer)
│  │  ├─ pixel.py            # font bitmap 5x7, dithering Bayer, cahaya bertingkat
│  │  ├─ music.py            # lo-fi hip-hop + hujan + vinyl + guntur
│  │  └─ preview.jpg
│  ├─ style-05-animasi-3d/
│  │  ├─ README.md           # panduan field JSON, overlay data, cara menulis cerita
│  │  ├─ cg.py               # mesin 3D moderngl (SSS, bayangan, ACES, tekstur)
│  │  ├─ nara.py             # tokoh Nara ber-rig (wajah, alis, mulut, lengan)
│  │  ├─ room.py             # set kamar kos + tekstur layar/HP/poster
│  │  ├─ stories/            # malam-bimbingan.py, pasar-merah.py (shot, pose, cahaya)
│  │  ├─ style.py            # renderer 2 lapis (DOF), bloom, overlay (Renderer)
│  │  ├─ music.py            # skor orkestra kecil + SFX
│  │  └─ preview.jpg
│  └─ style-06-kartun-flat/
│     ├─ README.md           # kenapa formatnya viral, elemen, cara menulis cerita
│     ├─ art.py              # sprite vektor flat: tokoh (hijab/rambut/nomor), props, kartu, stempel
│     ├─ cerita/             # mindset-es-teh.py, mindset-gaji.py, bocor-halus.py
│     ├─ style.py            # timeline elemen, animasi, subtitle karaoke (Renderer)
│     ├─ music.py            # ukulele + marimba + SFX otomatis dari timeline
│     └─ preview.jpg
├─ assets/fonts/             # Anton, Poppins, Cardo, Crimson Text (lisensi OFL)
└─ output/                   # hasil render (tidak masuk git)
```

## Menambah style baru

1. Buat folder `styles/style-03-<nama>/` berisi `style.py` (punya class `Renderer(cfg)` dengan
   `scenes`, `starts`, `total`, `frame(g)`, `cut_times()`, dan konstanta `W`, `H`, `FPS`) serta `music.py`
   (fungsi `make_music(path, total, cuts, cfg=None)`, opsional konstanta `LOUDNESS`). Paling gampang: salin style yang paling mirip lalu ubah.
2. Di file konten, isi `"style": "style-03"`.
3. Tambahkan barisnya di tabel "Daftar style" di atas.

## Catatan

- Semua visual dan musik dibuat dari nol oleh kode. Jangan masukkan logo, karakter, atau cuplikan
  trailer milik pihak lain (mis. Rockstar) supaya aman dari klaim hak cipta.
- Font Anton dan Poppins memakai SIL Open Font License; lisensinya ada di `assets/fonts/`.
