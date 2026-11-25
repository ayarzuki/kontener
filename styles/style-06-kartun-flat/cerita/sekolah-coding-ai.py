"""Satu tokoh (Bima, mahasiswa semester 7): koding & AI jadi mata pelajaran pilihan.

Fakta (dicek 26 Nov 2026):
  - Permendikdasmen 13/2025: koding & kecerdasan artifisial = mapel pilihan, bertahap mulai TA 2025/2026,
    kelas 5 SD s.d. kelas 12; 2 jam/minggu (SMA 11-12 sampai 5 jam) — kodingka.kemendikdasmen.go.id
  - Mendikdasmen Abdul Mu'ti, Konaspi Nusa Dua (2 Okt 2026): baru ~25% sekolah mengajarkan coding & AI — Antara
  - Hitungan ilustrasi: 2 jam x 36 minggu x 8 tahun (kelas 5 SD - kelas 12) = 576 jam
"""
from art import AMBER, GREEN, INK, RED, WHITE

G = 1238
TEAL = (15, 118, 110)
BLUE = (66, 110, 170)
JEANS = (58, 70, 96)
SKIN = 1


def bima(face="smile", arm="down"):
    """Tokoh mahasiswa (pria, rambut pendek)."""
    return ("tokoh", BLUE, SKIN, "short", (40, 36, 34), None, face, arm, False, JEANS, False)


def build(ctx):
    L, D = ctx["L"], ctx["D"]
    E = []

    def add(kind, t0, t1, **kw):
        E.append(dict(kind=kind, t0=t0, t1=t1, **kw))

    def spr(a, t0, t1, x, y, s=1.0, z=3, **kw):
        add("sprite", t0, t1, art=a if isinstance(a, tuple) else (a,), x=x, y=y, s=s, z=z, **kw)

    def tokoh(t0, t1, x=230, s=1.0, face="smile", faces=(), arm="down", enter=True, tag=True, z=2):
        kw = {} if enter else {"in": "none", "sfx": False}
        spr(bima(face, arm), t0, t1, x, G, s=s, z=z, bob=3,
            art_at=[(tt, bima(f, arm)) for tt, f in faces], **kw)
        if tag:
            spr(("label_tag", "BIMA", BLUE), t0 + (0.15 if enter else 0), t1, x, G - 420 * s - 6,
                s=1.0, z=3, **kw)

    def pill(txt, t0, t1, y=300, bg=INK, fg=WHITE, size=44, x=540, **kw):
        add("pill", t0, t1, text=txt, x=x, y=y, bg=bg, fg=fg, size=size, z=6, **kw)

    def stamp(txt, t0, t1, y=470, col=(46, 140, 112), x=540, size=48):
        add("stamp", t0, t1, text=txt, x=x, y=y, col=col, size=size, z=9, **{"in": "stamp"})

    def eq(full, res, t0, t1, y=330, typ=0.7, size=64):
        add("eq", t0, t1, full=full, result=res, x=540, y=y, size=size, type=typ,
            t_res=t0 + typ + 0.2, z=7)

    # ---------------------------------------------------------- 0. hook (layar gelap)
    h1 = L(1) - 0.05
    add("hooktitle", -0.8, h1,
        lines=[("KELAS 5 SD SUDAH", WHITE), ("BELAJAR AI", AMBER)], y=300, size=80, stagger=0.45)
    spr(("laptop", "KODING & AI"), 0.6, h1, 360, 1245, s=2.0, z=2)
    spr(("cert", "PORTOFOLIO"), 1.6, h1, 820, 1235, s=1.15, z=2, **{"in": "drop"})
    spr("qmark", 2.9, h1, 900, 790, s=1.05, z=4)
    pill("KAMU SEMESTER BERAPA?", 2.0, h1, y=530, bg=AMBER, fg=INK, size=36, x=470)

    # ---------------------------------------------------------- 1. sejak kapan
    t0, t1 = h1, L(2) - 0.05
    tokoh(t0, t1, x=230)
    pill("MAPEL PILIHAN", L(1, 0.25), t1, bg=GREEN)
    pill("MULAI TAHUN AJARAN 2025", L(1, 0.55), t1, y=410, size=32)
    spr(("laptop", "KODING & KA"), L(1, 0.7), t1, 790, G - 8, s=1.65, z=3)

    # ---------------------------------------------------------- 2. baru 25 persen
    t0, t1 = L(2) - 0.05, L(3) - 0.05
    tokoh(t0, t1, x=165, s=0.92, face="o", tag=False, enter=False)
    pill("DATA KEMENDIKDASMEN", L(2, 0.05), t1, y=290, size=32, bg=INK)
    add("bars", L(2, 0.3), t1, box=(330, 470, 985, 1120), values=[25, 75],
        labels=["25%", "75%"], cats=["sudah jalan", "belum jalan"], csize=32,
        colors=[GREEN, (172, 166, 152)], stagger=0.35, lsize=40, fmt="{:.0f}%", z=5, **{"in": "none"})

    # ---------------------------------------------------------- 3. dua jam seminggu
    t0, t1 = L(3) - 0.05, L(4) - 0.05
    tokoh(t0, t1, x=230, face="talk", enter=False)
    eq("2 jam × 36 minggu", "72 jam / tahun", t0 + 0.05, t1, y=330, typ=0.6, size=60)
    pill("SMA KELAS 11: 5 JAM", L(3, 0.55), t1, y=520, size=32, bg=AMBER, fg=INK)
    spr(("laptop", "JADWAL"), L(3, 0.15), t1, 800, G - 8, s=1.55, z=3)

    # ---------------------------------------------------------- 4. tangga jenjang
    t0, t1 = L(4) - 0.05, L(5) - 0.05
    tokoh(t0, t1, x=190, s=0.88, face="talk", tag=False)
    pill("SD: KARTU, TANPA KOMPUTER", L(4, 0.1), t1, y=290, x=650, size=30, bg=INK)
    pill("SMP: PEMROGRAMAN BLOK", L(4, 0.45), t1, y=400, x=650, size=30, bg=INK)
    pill("SMA: KODE + APLIKASI AI", L(4, 0.78), t1, y=510, x=650, size=30, bg=GREEN)

    # ---------------------------------------------------------- 5. hitung 576 jam
    t0, t1 = L(5) - 0.05, L(6) - 0.05
    tokoh(t0, t1, x=200, s=0.9, face="talk", tag=False, enter=False)
    eq("2 jam/minggu × 36", "72 jam / tahun", t0 + 0.05, t1, y=280, typ=0.5, size=58)
    eq("72 jam × 8 tahun", "576 jam", L(5, 0.4), t1, y=410, typ=0.5, size=58)
    stamp("TOTAL 8 TAHUN SEKOLAH", L(5, 0.75), t1, y=560, col=TEAL, size=40)
    spr(("calendar", 8, "TAHUN"), L(5, 0.2), t1, 830, G - 8, s=1.05, z=3)

    # ---------------------------------------------------------- 6. yang tidak didapat
    t0, t1 = L(6) - 0.05, L(7) - 0.05
    tokoh(t0, t1, x=200, face="worry", tag=False, enter=False)
    pill("KALAU SEKOLAHMU BELUM IKUT", L(6, 0.05), t1, y=290, size=30, bg=INK, x=650)
    add("xcheck", L(6, 0.3), t1, text="0 JAM", icon="cross", col=RED, x=650, y=470, size=120, z=5)
    stamp("TIDAK KEMBALI", L(6, 0.65), t1, y=590, col=RED, x=650, size=44)

    # ---------------------------------------------------------- 7. bukan kalah
    t0, t1 = L(7) - 0.05, L(8) - 0.05
    tokoh(t0, t1, x=230, face="talk", faces=[(L(7, 0.85), "happy")])
    pill("BUKAN KALAH", L(7, 0.2), t1, bg=GREEN, size=44)
    pill("KEJAR SENDIRI, LEBIH CEPAT", L(7, 0.55), t1, y=420, size=32, bg=INK)
    add("xcheck", L(7, 0.75), t1, text="BISA DIBELI", icon="check", col=GREEN, x=560, y=560, size=76)

    # ---------------------------------------------------------- 8. tiga langkah
    t0, t1 = L(8) - 0.05, L(9) - 0.05
    tokoh(t0, t1, x=175, s=0.85, face="talk", tag=False)
    pill("1 PROYEK NYATA", L(8, 0.1), t1, y=290, x=660, size=32, bg=INK)
    pill("1 ALAT", L(8, 0.38), t1, y=400, x=660, size=32, bg=INK)
    pill("1 HASIL", L(8, 0.66), t1, y=510, x=660, size=32, bg=GREEN)
    spr(("cert", "SKRIPSI"), L(8, 0.8), t1, 660, G - 8, s=1.2, z=3, **{"in": "drop"})

    # ---------------------------------------------------------- 9. CTA
    t0 = L(9) - 0.05
    dur = L(9) + D(9) + 1.7
    add("title", t0, dur, lines=[("SEKOLAHMU ADA", INK), ("MAPEL CODING?", RED)], x=540, y=300, size=76, z=6)
    pill("KOMEN: 1 ADA • 2 TIDAK • 3 BARU DENGAR", L(9, 0.15), dur, bg=RED, size=28, y=470)
    for k, lab in enumerate(("ADA", "TIDAK", "BARU")):
        x = 290 + k * 250
        t_k = L(9, 0.35) + 0.2 * k
        spr(("numcircle", k + 1, RED), t_k, dur, x, 700, s=1.15, z=5)
        pill(lab, t_k + 0.08, dur, y=762, x=x, bg=INK, size=24)
    tokoh(t0, dur, x=540, s=0.78, face="happy", arm="up", tag=False, z=3)

    cuts = [("hook", 0.0), ("sejak", h1)] + [(nm, L(i) - 0.05) for i, nm in (
        (2, "25-persen"), (3, "dua-jam"), (4, "jenjang"), (5, "hitung"), (6, "nol"),
        (7, "bukan-kalah"), (8, "langkah"), (9, "cta"))]
    global HOOK_END
    HOOK_END = h1
    return E, cuts, dur


HOOK_END = 0.0
