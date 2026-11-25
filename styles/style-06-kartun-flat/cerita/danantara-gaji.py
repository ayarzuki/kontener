"""Cek angka: biaya pegawai DIM (lengan investasi Danantara) vs labanya. Data per 25 Nov 2026.

  BPI Danantara: laba bersih konsolidasi Rp203,4 T (9 bulan 2025), opini WTP BPK — gabungan 1.000+ BUMN.
  DIM 2025: biaya pegawai Rp250,7 M vs laba bersih Rp116,3 M (≈ 2,15×).
  DIM Jan–Apr 2026: biaya pegawai Rp146,46 M, 118 pegawai → ±Rp310 jt/orang/bulan (rata-rata total biaya).
  UMP DKI 2026 Rp5.729.876 → ≈ 54×.  Laba DIM Jan–Apr 2026 Rp705,7 M (termasuk untung kurs Rp306 M).
  Proyeksi laba DIM 2026 Rp800 M vs target RKAP Rp3,4 T (Rosan, Komisi XI DPR, 24 Nov 2026).
Tokoh di video generik (pegawai), bukan orang sungguhan.
"""
from art import AMBER, GREEN, INK, RED, TEAL, WHITE

G = 1238
BROWN = (120, 96, 80)
DOSENKU = (15, 118, 110)  # teal brand #0f766e
PEG = [((76, 107, 152), 0, "short", None), ((34, 143, 141), 3, "hijab", (90, 110, 150)),
       ((120, 92, 170), 1, "long", (70, 46, 36)), ((200, 80, 70), 2, "short", None)]


def peg(k, face="smile", arm="down"):
    shirt, skin, hair, hc = PEG[k % 4]
    return ("tokoh", shirt, skin, hair, hc, None, face, arm)


def build(ctx):
    L, D = ctx["L"], ctx["D"]
    E = []

    def add(kind, t0, t1, **kw):
        E.append(dict(kind=kind, t0=t0, t1=t1, **kw))

    def spr(a, t0, t1, x, y, s=1.0, z=3, **kw):
        add("sprite", t0, t1, art=a if isinstance(a, tuple) else (a,), x=x, y=y, s=s, z=z, **kw)

    def pill(txt, t0, t1, y=300, bg=INK, fg=WHITE, size=44, x=540, **kw):
        add("pill", t0, t1, text=txt, x=x, y=y, bg=bg, fg=fg, size=size, z=6, **kw)

    def note(txt, t0, t1, y=400, size=28, **kw):
        pill(txt, t0, t1, y=y, bg=BROWN, size=size, **kw)

    def stamp(txt, t0, t1, y=470, col=(46, 140, 112), x=540, size=52):
        add("stamp", t0, t1, text=txt, x=x, y=y, col=col, size=size, z=9, **{"in": "stamp"})

    def eq(full, res, t0, t1, y=330, typ=0.8, size=70):
        add("eq", t0, t1, full=full, result=res, x=540, y=y, size=size, type=typ, t_res=t0 + typ + 0.2, z=7)

    def result(v, t0, t1, y=440, prefix="Rp", suffix=" M", dec=1, size=96):
        add("result", t0, t1, value=v, dec=dec, prefix=prefix, suffix=suffix, count=0.8, x=540, y=y, size=size, z=8)

    def cut(i):
        return L(i) - 0.05

    # ------------------------------------------------ 0. hook
    h1 = cut(1)
    add("hooktitle", -0.8, h1, lines=[("BIAYA PEGAWAI > LABA?", WHITE), ("CEK ANGKA DANANTARA", AMBER)], y=330,
        size=72, stagger=0.45)
    spr(("office", "DIM"), 0.6, h1, 540, 1230, s=1.0, z=2)
    spr(("moneybag", "Rp250,7 M"), 1.5, h1, 230, 1230, s=1.25, z=3, **{"in": "drop"})
    spr(("price_tag", "biaya pegawai"), 1.8, h1, 240, 900, s=0.95, z=4)
    spr(("moneybag", "Rp116,3 M"), 2.3, h1, 860, 1230, s=0.95, z=3, **{"in": "drop"})
    spr(("price_tag", "laba"), 2.6, h1, 870, 980, s=0.95, z=4)
    spr("qmark", 3.3, h1, 880, 760, s=1.0, z=5)

    # ------------------------------------------------ 1. laporan keuangan Danantara
    t0, t1 = h1, cut(2)
    spr(("office", "DANANTARA"), t0, t1, 540, G, s=1.2, z=2)
    pill("LAPORAN KEUANGAN 2025", L(1, 0.05), t1)
    stamp("OPINI WTP • BPK", L(1, 0.62), t1, y=470)

    # ------------------------------------------------ 2. laba konsolidasi = gabungan BUMN
    t0, t1 = cut(2), cut(3)
    result(203.4, L(2, 0.05), t1, y=320, suffix=" T")
    note("laba bersih konsolidasi • 9 bulan 2025", L(2, 0.12), t1, y=440)
    add("crowd", L(2, 0.5), t1, n=1, n1=48, g0=L(2, 0.52), gdur=1.6, per=12, x0=120, x1=1000, yb=1000, yf=G,
        sb=0.2, sf=0.3, art=("office", "BUMN"), z=2, **{"in": "none"})
    pill("1.000+ BUMN", L(2, 0.55), t1, y=600, bg=INK, icon="office")

    # ------------------------------------------------ 3. DIM
    t0, t1 = cut(3), cut(4)
    spr(("office", "DIM"), t0, t1, 780, G, s=1.05, z=2)
    pill("PT DANANTARA INVESTMENT MANAGEMENT", L(3, 0.05), t1, size=30)
    note("lengan investasi Danantara", L(3, 0.2), t1, y=390)
    for k, x in enumerate((170, 400)):
        spr(peg(k), L(3, 0.3) + 0.15 * k, t1, x, G, s=0.85, z=3, bob=3)

    # ------------------------------------------------ 4–5. 2025: biaya pegawai vs laba
    t0, t1 = cut(4), cut(6)
    pill("DIM • TAHUN 2025", t0 + 0.05, cut(5), y=290)
    add("bars", L(4, 0.12), t1, box=(130, 390, 950, 1150), values=[250.7, 116.3], labels=["Rp250,7 M", "Rp116,3 M"],
        cats=["biaya pegawai", "laba bersih"], csize=36, colors=[RED, GREEN], stagger=0.55, lsize=42,
        fmt="Rp{:.0f} M", z=5)
    eq("Rp250,7 M ÷ Rp116,3 M", "2,15×", cut(5) + 0.05, t1, y=290, typ=0.6, size=64)
    stamp("LEBIH DARI 2× LABA", L(5, 0.45), t1, y=560, x=740, col=RED, size=44)

    # ------------------------------------------------ 6. Jan–Apr 2026: 118 pegawai
    t0, t1 = cut(6), cut(7)
    note("biaya pegawai DIM • Jan–Apr 2026", t0 + 0.1, t1, y=300, size=30)
    result(146.5, L(6, 0.15), t1, y=430)
    add("calendar", L(6, 0.3), t1, n0=1, n1=4, count=1.2, head="BULAN", x=200, y=700, s=0.8, z=3)
    add("crowd", L(6, 0.45), t1, n=1, n1=118, g0=L(6, 0.47), gdur=2.0, per=20, x0=340, x1=1060, yb=960, yf=G,
        sb=0.16, sf=0.26, art=peg(0), z=2, **{"in": "none"})
    add("counter", L(6, 0.45), t1, n0=1, n1=118, c0=L(6, 0.47), cdur=2.0, x=700, y=620, size=40, z=6)

    # ------------------------------------------------ 7. rata-rata per orang
    t0, t1 = cut(7), cut(8)
    eq("Rp146,46 M ÷ 118 ÷ 4", "Rp310 jt", t0 + 0.05, t1, y=300, typ=0.8, size=64)
    note("rata-rata per orang per bulan", L(7, 0.12), t1, y=410)
    spr(peg(2, "o"), L(7, 0.1), t1, 300, G, s=1.0, z=3, bob=3, art_at=[(L(7, 0.55), peg(2, "smile"))])
    spr(("price_tag", "Rp310 jt / bulan"), L(7, 0.3), t1, 640, 900, s=1.15, z=5)
    stamp("BUKAN TAKE-HOME PAY", L(7, 0.62), t1, y=560, col=(150, 100, 40), size=46)

    # ------------------------------------------------ 8. vs UMP Jakarta
    t0, t1 = cut(8), cut(9)
    add("bars", t0 + 0.1, t1, box=(130, 390, 950, 1150), values=[5.73, 310], labels=["Rp5,73 jt", "Rp310 jt"],
        cats=["UMP Jakarta 2026", "biaya per pegawai"], csize=32, colors=[TEAL, RED], stagger=0.6, lsize=42,
        fmt="Rp{:.0f} jt", z=5, **{"in": "none"})
    stamp("≈ 54×", L(8, 0.7), t1, y=300, col=RED, size=72)

    # ------------------------------------------------ 9. laba Jan–Apr 2026
    t0, t1 = cut(9), cut(10)
    pill("LABA DIM • JAN–APR 2026", t0 + 0.05, t1, bg=GREEN)
    result(705.7, L(9, 0.12), t1, y=440)
    note("termasuk untung selisih kurs Rp306 M", L(9, 0.6), t1, y=570)
    spr(("office", "DIM"), t0, t1, 540, G, s=0.95, z=2, sfx=False, **{"in": "none"})

    # ------------------------------------------------ 10. proyeksi vs target
    t0, t1 = cut(10), cut(11)
    add("bars", t0 + 0.1, t1, box=(130, 390, 950, 1150), values=[3.4, 0.8], labels=["Rp3,4 T", "Rp0,8 T"],
        cats=["target laba 2026", "proyeksi laba 2026"], csize=32, colors=[AMBER, RED], stagger=0.5, lsize=42,
        fmt="Rp{:.1f} T", z=5, **{"in": "none"})
    stamp("CUMA 23,5% TARGET", L(10, 0.62), t1, y=300, col=RED, size=50)

    # ------------------------------------------------ 11. penjelasan Danantara
    t0, t1 = cut(11), cut(12)
    pill("PENJELASAN DANANTARA", t0 + 0.05, t1)
    note("Komisi XI DPR, 24 Nov 2026", L(11, 0.1), t1, y=380)
    spr(("office", "DANANTARA"), t0, t1, 260, G, s=1.0, z=2)
    add("bubble", L(11, 0.2), t1, text="Tekanan pasar modal. Total biaya sesuai rencana.", w=520, size=36, x=700,
        y=880, tail="left", z=7)

    # ------------------------------------------------ 12–13. polling + CTA
    t0 = cut(12)
    dur = L(13) + D(13) + 1.6
    add("title", t0, dur, lines=[("MENURUT KAMU?", INK)], x=540, y=290, size=96, z=6)
    pill("A • WAJAR, STANDAR GLOBAL", L(12, 0.25), dur, y=440, bg=GREEN, size=40)
    pill("B • KEMAHALAN", L(12, 0.75), dur, y=540, bg=RED, size=40)
    pill("TULIS A / B DI KOMENTAR", cut(13) + 0.1, dur, y=650, bg=INK, size=34)
    pill("Rujukan jurnal ber-DOI • dosenku.biz.id", L(13, 0.45), dur, y=760, bg=DOSENKU, size=34)
    note("Dosenku • Skripsi terarah. Dosen senang.", L(13, 0.7), dur, y=850, size=28)
    for k, (x, lab, col) in enumerate(((330, "A", GREEN), (750, "B", RED))):
        spr(peg(k + 1, "happy" if k == 0 else "worry"), t0 + 0.1 * k, dur, x, G, s=0.85, z=3, bob=3)
        spr(("numcircle", lab, col), L(12, 0.25 + 0.5 * k), dur, x + 120, 1010, s=1.0, z=5)
    note("Sumber: lap. keuangan DIM (SGX), Danantara, Katadata, IDX Channel", cut(13) + 0.3, dur, y=1290, size=22)

    cuts = [("hook", 0.0), ("lapkeu", h1)] + [(nm, cut(i)) for i, nm in (
        (2, "konsolidasi"), (3, "dim"), (4, "dim-2025"), (5, "dua-kali"), (6, "pegawai-2026"), (7, "per-orang"),
        (8, "ump"), (9, "laba-2026"), (10, "target"), (11, "penjelasan"), (12, "polling"))]
    global HOOK_END
    HOOK_END = h1
    return E, cuts, dur


HOOK_END = 0.0
