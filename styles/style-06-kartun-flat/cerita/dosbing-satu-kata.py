"""Cerita pendek (fiksi): "Dosbingku cuma balas satu kata" — Nadia & Pak Hendra.

Struktur story: hook misteri → konflik berulang (Revisi ×7) → titik terendah → berubah (berhenti menebak,
siapkan bimbingan) → twist (dosen menunggu pertanyaan) → callback ending ("Lulus.") → pancingan komentar.
Dosenku muncul sebagai alat menyiapkan bimbingan (kerangka Bab 2, rujukan ber-DOI), bukan joki.
"""
from art import AMBER, GREEN, INK, RED, WHITE

G = 1238
BROWN = (120, 96, 80)
DOSENKU = (15, 118, 110)

RAKA = ((52, 110, 170), 0, "hijab", (120, 92, 170))  # Nadia
HENDRA = ((96, 104, 120), 1, "old", None)
TEMAN = [((243, 162, 41), 0, "hijab", (226, 120, 140)), ((34, 143, 141), 3, "short", None),
         ((200, 80, 70), 1, "long", (70, 46, 36))]


def tk(p, face="smile", arm="down"):
    shirt, skin, hair, hc = p
    return ("tokoh", shirt, skin, hair, hc, None, face, arm)


def build(ctx):
    L, D = ctx["L"], ctx["D"]
    E = []

    def add(kind, t0, t1, **kw):
        E.append(dict(kind=kind, t0=t0, t1=t1, **kw))

    def spr(a, t0, t1, x, y, s=1.0, z=3, **kw):
        add("sprite", t0, t1, art=a if isinstance(a, tuple) else (a,), x=x, y=y, s=s, z=z, **kw)

    def pill(txt, t0, t1, y=300, bg=INK, fg=WHITE, size=40, x=540, **kw):
        add("pill", t0, t1, text=txt, x=x, y=y, bg=bg, fg=fg, size=size, z=6, **kw)

    def stamp(txt, t0, t1, y=470, col=RED, x=540, size=56):
        add("stamp", t0, t1, text=txt, x=x, y=y, col=col, size=size, z=9, **{"in": "stamp"})

    def bubble(txt, t0, t1, x, y, w=420, size=36, tail="left", **kw):
        add("bubble", t0, t1, text=txt, x=x, y=y, w=w, size=size, tail=tail, z=7, **kw)

    def person(p, t0, t1, x, face="smile", faces=(), arm="down", s=0.95, enter=True, tag=None, tagcol=INK, z=2):
        kw = {} if enter else {"in": "none", "sfx": False}
        spr(tk(p, face, arm), t0, t1, x, G, s=s, z=z, bob=3, art_at=[(tt, tk(p, f, arm)) for tt, f in faces], **kw)
        if tag:
            spr(("label_tag", tag, tagcol), t0 + (0.15 if enter else 0), t1, x, G - 420 * s - 6, z=3, **kw)

    def cut(i):
        return L(i) - 0.05

    # ------------------------------------------------ 0. hook (gelap)
    h1 = cut(1)
    add("hooktitle", -0.8, h1, lines=[("6 BULAN, DOSBINGKU", WHITE), ("CUMA BALAS 1 KATA", AMBER)], y=330, size=78,
        stagger=0.45)
    spr(("phone", "CHAT"), 0.7, h1, 540, 1250, s=2.6, z=2)
    bubble("Revisi.", 1.8, h1, 600, 860, w=330, size=64, tail="left")
    spr("qmark", 3.0, h1, 880, 700, s=1.0, z=5)

    # ------------------------------------------------ 1. kenalan
    t0, t1 = h1, cut(2)
    person(RAKA, t0, t1, 260, tag="NADIA", tagcol=RAKA[0])
    person(HENDRA, L(1, 0.3), t1, 800, tag="PAK HENDRA", tagcol=HENDRA[0])
    pill("DOSBING PALING IRIT BICARA", L(1, 0.62), t1, bg=INK)
    bubble("...", L(1, 0.75), t1, 860, 760, w=200, size=50, tail="left")

    # ------------------------------------------------ 2. Bab 1 → Revisi
    t0, t1 = cut(2), cut(3)
    person(RAKA, t0, t1, 220, face="smile", faces=[(L(2, 0.75), "o")], enter=False, tag="NADIA", tagcol=RAKA[0])
    spr(("laptop", "BAB 1"), t0 + 0.1, t1, 660, G - 10, s=1.15, z=3)
    stamp("REVISI", L(2, 0.72), t1, y=520, size=72)

    # ------------------------------------------------ 3. revisi lagi & lagi
    t0, t1 = cut(3), cut(5)
    person(RAKA, t0, t1, 220, face="worry", enter=False, tag="NADIA", tagcol=RAKA[0])
    spr(("contract", 20), t0, t1, 700, G - 10, s=1.0, z=3, sfx=False,
        art_at=[(L(3, 0.65), ("contract", 40))])
    pill("JUDUL BARU", L(3, 0.05), L(3, 0.45), y=300, bg=BROWN)
    pill("+20 HALAMAN", L(3, 0.5), cut(4), y=300, bg=BROWN)
    stamp("REVISI", L(3, 0.32), t1, y=470, x=420, size=60)
    stamp("REVISI", L(3, 0.92), t1, y=610, x=700, size=60)
    # 4. tujuh kali
    for k, (x, y) in enumerate([(330, 640), (760, 440), (470, 900), (820, 820), (590, 720)]):
        stamp("REVISI", L(4, 0.05) + 0.18 * k, t1, y=y, x=x, size=52)
    add("counter", L(4, 0.05), t1, n0=2, n1=7, c0=L(4, 0.05), cdur=1.0, x=540, y=300, size=48, z=10)
    pill("TANPA PENJELASAN", L(4, 0.55), t1, y=1060, bg=RED)

    # ------------------------------------------------ 5. teman-teman sidang
    t0, t1 = cut(5), cut(6)
    for k, (p, x) in enumerate(zip(TEMAN, (520, 720, 920))):
        person(p, L(5, 0.15) + 0.35 * k, t1, x, face="happy", arm="up", s=0.85, z=2)
        spr(("cert", "LULUS"), L(5, 0.2) + 0.35 * k, t1, x, 760, s=0.55, z=4)
    person(RAKA, t0, t1, 190, face="worry", enter=False, tag="NADIA", tagcol=RAKA[0], z=3)
    pill("SATU PER SATU SIDANG", L(5, 0.05), t1, bg=GREEN)

    # ------------------------------------------------ 6. titik terendah
    t0, t1 = cut(6), cut(7)
    add("dim", t0, t1, alpha=150, z=1)
    person(RAKA, t0, t1, 400, face="worry", enter=False, z=3)
    add("calendar", t0 + 0.1, t1, n0=21, n1=23, count=1.4, head="JAM", x=820, y=560, s=0.9, z=4)
    bubble("Ganti judul lagi?", L(6, 0.4), t1, 640, 860, w=400, size=36, tail="left")
    pill("JUDUL KE-4?", L(6, 0.1), t1, y=300, bg=RED)

    # ------------------------------------------------ 7. berhenti menebak (Dosenku)
    t0, t1 = cut(7), cut(8)
    person(RAKA, t0, t1, 220, face="talk", faces=[(L(7, 0.6), "smile")], tag="NADIA", tagcol=RAKA[0])
    stamp("BERHENTI MENEBAK", L(7, 0.06), t1, y=300, col=DOSENKU, size=50)
    spr(("laptop", "DOSENKU"), L(7, 0.25), t1, 680, G - 10, s=1.15, z=3)
    pill("KERANGKA BAB 2 RAPI", L(7, 0.35), t1, y=470, bg=DOSENKU, size=34)
    pill("RUJUKAN BER-DOI ✓", L(7, 0.7), t1, y=560, bg=DOSENKU, size=34)

    # ------------------------------------------------ 8. tiga pertanyaan
    t0, t1 = cut(8), cut(9)
    person(RAKA, t0, t1, 200, face="talk", enter=False, tag="NADIA", tagcol=RAKA[0])
    pill("3 PERTANYAAN SPESIFIK", t0 + 0.05, t1, bg=INK)
    for k, q in enumerate(("1. Rumusan masalah?", "2. Kerangka teori?", "3. Metode?")):
        bubble(q, L(8, 0.2) + 0.45 * k, t1, 660, 560 + k * 150, w=420, size=34, tail="left")

    # ------------------------------------------------ 9. HP bergetar
    t0, t1 = cut(9), cut(10)
    pill("5 MENIT KEMUDIAN", t0 + 0.05, t1, bg=BROWN)
    spr(("phone", "1 PESAN"), L(9, 0.12), t1, 540, 1150, s=2.6, z=3, bob=14, sfx="ding", sfx_dt=0.0)
    person(RAKA, t0, t1, 200, face="o", s=0.8, enter=False, z=4)
    pill("BALASAN PANJANG!", L(9, 0.6), t1, y=420, bg=GREEN)

    # ------------------------------------------------ 10. twist
    t0, t1 = cut(10), cut(11)
    person(HENDRA, t0, t1, 820, face="smile", faces=[(L(10, 0.55), "happy")], tag="PAK HENDRA", tagcol=HENDRA[0])
    bubble("Akhirnya kamu bertanya. Dari awal saya menunggu itu.", L(10, 0.05), t1, 430, 900, w=560, size=40,
           tail="right")

    # ------------------------------------------------ 11. makna
    t0, t1 = cut(11), cut(12)
    add("xcheck", L(11, 0.05), t1, text="PENOLAKAN", icon="cross", x=540, y=450, size=84, z=5)
    add("xcheck", L(11, 0.5), t1, text="UNDANGAN", icon="check", col=GREEN, x=540, y=610, size=84, z=5)
    pill("buat bimbingan", L(11, 0.7), t1, y=720, bg=BROWN, size=32)
    person(RAKA, t0, t1, 300, face="smile", s=0.85, z=2)
    person(HENDRA, t0, t1, 780, face="smile", s=0.85, z=2)

    # ------------------------------------------------ 12. sidang
    t0, t1 = cut(12), cut(13)
    add("calendar", t0 + 0.1, t1, n0=1, n1=3, count=1.0, head="BULAN", x=540, y=520, s=0.85, z=4)
    pill("HARI SIDANG", L(12, 0.35), t1, y=300, bg=INK)
    person(RAKA, t0, t1, 280, face="worry", tag="NADIA", tagcol=RAKA[0])
    person(HENDRA, t0, t1, 800, face="smile", tag="PAK HENDRA", tagcol=HENDRA[0])

    # ------------------------------------------------ 13. callback: "Lulus."
    t0, t1 = cut(13), cut(14)
    person(HENDRA, t0, t1, 800, face="happy", enter=False, tag="PAK HENDRA", tagcol=HENDRA[0])
    person(RAKA, t0, t1, 280, face="o", faces=[(L(13, 0.9), "happy")], enter=False, tag="NADIA", tagcol=RAKA[0])
    bubble("Lulus.", t0 + 0.05, t1, 620, 760, w=330, size=68, tail="right")
    stamp("LULUS", L(13, 0.9), t1, y=360, col=GREEN, size=86)
    spr(("cert", "LULUS"), L(13, 1.2), t1, 280, 720, s=0.7, z=4)

    # ------------------------------------------------ 14–15. komentar + Dosenku
    t0 = cut(14)
    dur = L(15) + D(15) + 2.0
    add("title", t0, dur, lines=[("PERNAH DAPAT BALASAN", INK), ("1 KATA DARI DOSBING?", RED)], x=540, y=320, size=72,
        z=6)
    pill("CERITA DI KOMENTAR", L(14, 0.4), dur, y=480, bg=INK, size=38)
    pill("Siapkan bimbinganmu • dosenku.biz.id", cut(15) + 0.1, dur, y=590, bg=DOSENKU, size=36)
    pill("Dosenku • Skripsi terarah. Dosen senang.", L(15, 0.5), dur, y=690, bg=BROWN, size=28)
    person(RAKA, t0, dur, 300, face="happy", arm="up", s=0.9, z=3)
    person(HENDRA, t0, dur, 780, face="smile", s=0.9, z=3)

    cuts = [("hook", 0.0), ("kenalan", h1)] + [(nm, cut(i)) for i, nm in (
        (2, "bab1"), (3, "revisi"), (5, "teman"), (6, "malam"), (7, "berubah"), (8, "pertanyaan"), (9, "hp"),
        (10, "twist"), (11, "makna"), (12, "sidang"), (13, "lulus"), (14, "cta"))]
    global HOOK_END
    HOOK_END = h1
    return E, cuts, dur


HOOK_END = 0.0
