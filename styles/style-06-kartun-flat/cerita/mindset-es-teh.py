"""Parabel "Mindset Es Teh": modal sama Rp1 juta, 4 anak, hasil Rp15 jt → Rp495 jt (ilustrasi).

Hitungan:
  anak 1: 300 hari × Rp50rb = Rp15 jt (gerobak sendiri, jualan sendiri)
  anak 2: sewa Rp200rb/bln → Rp1 jt = 5 gerobak; 5 × 300 × Rp30rb (bersih) = Rp45 jt
  anak 3: uang muka langganan Rp36 jt ÷ Rp2,4 jt (sewa setahun) = 15 gerobak → 20 × 300 × Rp30rb = Rp180 jt
  anak 4: + pinjaman Rp120 jt = 50 gerobak → 70 × 300 × Rp30rb = Rp630 jt − cicilan & bunga Rp135 jt = Rp495 jt
"""
import art
from art import AMBER, GREEN, INK, RED, SONS, WHITE

G = 1238  # garis kaki


def build(ctx):
    L, D = ctx["L"], ctx["D"]
    E = []

    def end(i, extra=0.0):
        return L(i) + D(i) + extra

    def add(kind, t0, t1, **kw):
        E.append(dict(kind=kind, t0=t0, t1=t1, **kw))

    def son(i, x, t0, t1, s=0.92, face="smile", z=2, tag=None, faces=(), enter=True, **kw):
        if not enter:
            kw = dict(kw, sfx=False)
            kw["in"] = "none"
        add("sprite", t0, t1, art=("person", i, face, "down", True), x=x, y=G, s=s, z=z, bob=3, phase=i * 0.7,
            art_at=[(tt, ("person", i, f, "down", True)) for tt, f in faces], **kw)
        if tag:
            ex = {} if enter else {"in": "none", "sfx": False}
            add("sprite", t0 + (0.15 if enter else 0), t1, art=("label_tag", tag, SONS[i] if isinstance(i, int) else INK),
                x=x, y=G - 420 * s - 6, s=1.0, z=3, **ex)

    def pill(txt, t0, t1, y=300, bg=INK, fg=WHITE, size=44, x=540, **kw):
        add("pill", t0, t1, text=txt, x=x, y=y, bg=bg, fg=fg, size=size, z=6, **kw)

    def stamp(txt, t0, t1, y=470, col=(46, 140, 112), x=540, size=52):
        add("stamp", t0, t1, text=txt, x=x, y=y, col=col, size=size, z=9, **{"in": "stamp"})

    def eq(full, res, t0, t1, y=330, typ=0.8, t_res=None, size=70):
        add("eq", t0, t1, full=full, result=res, x=540, y=y, size=size, type=typ, t_res=t_res or t0 + typ + 0.2, z=7)

    # ------------------------------------------------ 0. hook (layar gelap)
    h1 = L(1) - 0.05
    add("hooktitle", -0.8, h1, lines=[("MODAL SAMA RP1 JUTA,", WHITE), ("KOK BEDA 33×?", AMBER)], y=330, size=76,
        stagger=0.45)
    for i in range(4):
        add("sprite", 0.8 + i * 0.12, h1, art=("person", i, "smile", "down", True), x=240 + i * 200, y=1180, s=0.75,
            z=2)
        add("sprite", 1.9 + i * 0.12, h1, art=("money", "Rp1 jt"), x=240 + i * 200, y=830, s=0.9, z=3,
            **{"in": "drop"})
    add("sprite", 3.0, h1, art=("qmark",), x=900, y=740, s=1.0, z=4)

    # ------------------------------------------------ 1. keluarga
    t0, t1 = h1, L(2) - 0.05
    add("sprite", t0, t1, art=("person", "father", "smile", "down", False), x=150, y=G, s=0.95, z=2, bob=2)
    add("sprite", t0 + 0.2, t1, art=("label_tag", "PAK DARTO", INK), x=150, y=G - 405, z=3)
    xs = [370, 545, 720, 895]
    for i, x in enumerate(xs):
        son(i, x, L(1, 0.2) + i * 0.12, t1, s=0.84)
    pill("4 ANAK", L(1, 0.12), L(1, 0.52), bg=RED)
    pill("Rp1 JUTA × 4 ANAK", L(1, 0.54), t1, bg=GREEN)
    for i, x in enumerate(xs):
        add("sprite", L(1, 0.6) + i * 0.1, t1, art=("money", "Rp1 jt"), x=x, y=G - 380, s=0.85, z=4,
            **{"in": "drop"})
    stamp("MODAL AWAL", L(1, 0.8), t1, y=470)

    # ------------------------------------------------ 2. anak 1: gerobak sendiri
    t0, t1 = L(2) - 0.05, L(3) - 0.05
    son(0, 210, t0, t1, s=0.95, tag="ANAK 1", faces=[(L(2, 0.62), "happy")])
    add("sprite", L(2, 0.1), t1, art=("cart", "ES TEH"), x=650, y=G, s=1.15, z=2)
    add("sprite", L(2, 0.2), L(2, 0.55), art=("price_tag", "Rp1 jt"), x=870, y=800, s=1.0, z=5)
    pill("1 GEROBAK", L(2, 0.14), L(2, 0.6))
    add("sprite", L(2, 0.5), t1, art=("sun",), x=930, y=560, s=0.9, z=1)
    pill("UNTUNG Rp50rb / HARI", L(2, 0.62), t1, bg=GREEN)

    # ------------------------------------------------ 3. anak 1: setahun
    t0, t1 = L(3) - 0.05, L(4) - 0.05
    cnt = 0.42 * D(3)
    add("calendar", t0, t1, n0=1, n1=300, count=cnt, x=290, y=760, s=1.0, z=3)
    add("crate", t0, t1, n0=1, n1=21, g0=t0 + 0.25, gdur=cnt, x=750, y=G - 10, s=1.15, z=3)
    eq("300 × Rp50rb", "Rp15 jt", L(3, 0.28), t1, typ=0.7)
    stamp("TUMBUH ORGANIK", L(3, 0.7), t1, y=470)

    # ------------------------------------------------ 4. anak 2: sewa
    t0, t1 = L(4) - 0.05, L(5) - 0.05
    son(1, 210, t0, t1, s=0.95, tag="ANAK 2")
    add("sprite", t0 + 0.25, L(4, 0.5), art=("qmark",), x=300, y=780, s=0.9, z=4)
    add("sprite", L(4, 0.08), L(4, 0.6), art=("sign", (("BELI Rp1 jt", INK),), False), x=700, y=G, s=1.05, z=3,
        art_at=[(L(4, 0.24), ("sign", (("BELI Rp1 jt", INK), ("SEWA Rp200rb/bln", GREEN)), True))])
    add("crowd", L(4, 0.62), t1, n=1, n1=5, g0=L(4, 0.62), gdur=0.9, per=5, x0=390, x1=1070, yb=G, yf=G,
        sb=0.4, sf=0.4, z=2, **{"in": "none"})
    add("counter", L(4, 0.62), t1, n0=1, n1=5, c0=L(4, 0.62), cdur=0.9, x=540, y=300, icon="cart", size=44, z=6)

    # ------------------------------------------------ 5. anak 2: hasil
    t0, t1 = L(5) - 0.05, L(6) - 0.05
    son(1, 210, t0, t1, s=0.95, tag="ANAK 2", faces=[(L(5, 0.6), "happy")], enter=False)
    add("crowd", t0, t1, n=5, per=5, x0=390, x1=1070, yb=G, yf=G, sb=0.4, sf=0.4, z=2, **{"in": "none"})
    eq("5 × 300 × Rp30rb", "Rp45 jt", L(5, 0.05), t1, typ=0.8)
    pill("untung bersih per gerobak per hari", L(5, 0.08), t1, y=438, bg=(120, 96, 80), size=28)
    add("bars", L(5, 0.55), t1, box=(560, 540, 1010, 960), values=[15, 45], labels=["Rp15 jt", "Rp45 jt"],
        colors=[SONS[0], SONS[1]], stagger=0.3, lsize=34, fmt="Rp{:.0f} jt", z=5)
    stamp("SEWA, BUKAN BELI", L(5, 0.78), t1, y=520, col=(30, 120, 150))

    # ------------------------------------------------ 6. anak 3: kantor
    t0, t1 = L(6) - 0.05, L(7) - 0.05
    son(2, 200, t0, t1, s=0.95, tag="ANAK 3", faces=[(L(6, 0.42), "talk")])
    for k, x in enumerate((585, 775, 965)):
        add("sprite", L(6, 0.1) + 0.12 * k, t1, art=("office", "KANTOR"), x=x, y=G, s=0.74, z=2)
    add("counter", L(6, 0.14), t1, n0=3, n1=20, c0=L(6, 0.2), cdur=1.1, x=540, y=300, icon="office", size=44, z=6)
    add("bubble", L(6, 0.42), t1, text="Langganan es teh setahun, bayar di muka!", w=460, size=34, x=480, y=800, z=7)

    # ------------------------------------------------ 7. anak 3: uang muka → gerobak
    t0, t1 = L(7) - 0.05, L(8) - 0.05
    son(2, 200, t0, t1, s=0.95, tag="ANAK 3", enter=False)
    add("sprite", L(7, 0.04), L(7, 0.6), art=("moneybag", "Rp36 jt"), x=650, y=G - 20, s=1.2, z=3)
    eq("Rp36 jt ÷ Rp2,4 jt", "15 gerobak", L(7, 0.12), t1, typ=0.8, size=64)
    pill("Rp2,4 jt = sewa 1 gerobak setahun", L(7, 0.16), t1, y=432, bg=(120, 96, 80), size=28)
    add("crowd", L(7, 0.6), t1, n=5, n1=20, g0=L(7, 0.62), gdur=1.1, per=10, x0=350, x1=1030, yb=1120, yf=G,
        sb=0.27, sf=0.33, z=2, **{"in": "none"})
    add("counter", L(7, 0.62), t1, n0=5, n1=20, c0=L(7, 0.62), cdur=1.1, x=540, y=600, icon="cart", size=44, z=6)

    # ------------------------------------------------ 8. anak 3: hasil
    t0, t1 = L(8) - 0.05, L(9) - 0.05
    son(2, 200, t0, t1, s=0.95, tag="ANAK 3", faces=[(L(8, 0.5), "happy")], enter=False)
    add("crowd", t0, t1, n=20, per=10, x0=350, x1=1030, yb=1120, yf=G, sb=0.27, sf=0.33, z=2, **{"in": "none"})
    eq("20 × 300 × Rp30rb", "Rp180 jt", L(8, 0.0), t1, typ=0.8)
    stamp("UANG MUKA PELANGGAN", L(8, 0.62), t1, y=480, col=(196, 110, 30), size=46)

    # ------------------------------------------------ 9. anak 4: ke bank
    t0, t1 = L(9) - 0.05, L(10) - 0.05
    son(3, 190, t0, t1, s=0.95, tag="ANAK 4")
    add("counter", t0 + 0.1, t1, n0=20, n1=20, x=540, y=300, icon="cart", size=44, z=6)
    add("sprite", L(9, 0.3), t1, art=("contract", 20), x=330, y=900, s=0.9, z=5,
        move=[(L(9, 0.72), 330, 900), (L(9, 0.95), 650, 980)], arc=120)
    add("sprite", L(9, 0.55), t1, art=("bank",), x=790, y=G, s=0.9, z=3)

    # ------------------------------------------------ 10. anak 4: pinjaman → 70 gerobak
    t0, t1 = L(10) - 0.05, L(11) - 0.05
    son(3, 190, t0, t1, s=0.95, tag="ANAK 4", faces=[(L(10, 0.6), "happy")], enter=False)
    add("sprite", t0, L(10, 0.46), art=("bank",), x=790, y=G, s=0.9, z=3, **{"in": "none"})
    add("sprite", t0, L(10, 0.46), art=("contract", 20), x=650, y=980, s=0.9, z=4, **{"in": "none"})
    stamp("DISETUJUI", L(10, 0.04), L(10, 0.46), y=880, x=790, col=(40, 150, 90), size=56)
    pill("PINJAMAN Rp120 jt", L(10, 0.1), L(10, 0.46), bg=AMBER, fg=INK)
    add("crowd", L(10, 0.46), t1, n=20, n1=70, g0=L(10, 0.48), gdur=1.6, per=12, x0=330, x1=1040, yb=980, yf=G,
        sb=0.17, sf=0.29, z=2, **{"in": "none"})
    add("counter", L(10, 0.46), t1, n0=20, n1=70, c0=L(10, 0.48), cdur=1.6, x=540, y=300, icon="cart", size=44, z=6)

    # ------------------------------------------------ 11. anak 4: hasil bersih
    t0, t1 = L(11) - 0.05, L(12) - 0.05
    son(3, 190, t0, t1, s=0.95, z=3, tag="ANAK 4", enter=False)
    add("crowd", t0, t1, n=70, per=12, x0=330, x1=1040, yb=980, yf=G, sb=0.17, sf=0.29, z=2, **{"in": "none"})
    add("dim", t0, t1, alpha=110, z=4)
    eq("70 × 300 × Rp30rb", "Rp630 jt", t0 + 0.05, t1, y=290, typ=0.6, size=62)
    eq("Rp630 jt − Rp135 jt", "", L(11, 0.3), t1, y=440, typ=0.6, size=62)
    pill("cicilan + bunga", L(11, 0.36), t1, y=540, bg=(120, 96, 80), size=28)
    add("result", L(11, 0.62), t1, value=495, prefix="= Rp", suffix=" jt", count=0.8, x=540, y=690, size=100, z=8)
    stamp("LEVERAGE", L(11, 0.92), t1, y=850, col=RED, size=50)

    # ------------------------------------------------ 12. risiko
    t0, t1 = L(12) - 0.05, L(13) - 0.05
    son(3, 540, t0, t1, s=1.0, face="worry", z=3)
    add("gauge", L(12, 0.08), t1, x=540, y=560, s=1.15, n0t=L(12, 0.15), to=160, z=5)
    add("bubble", L(12, 0.5), t1, text="Kalau sepi?", w=300, size=36, x=830, y=880, tail="left", z=6)
    pill("CICILAN TETAP JALAN", L(12, 0.6), t1, bg=RED, y=300)

    # ------------------------------------------------ 13. perbandingan
    t0, t1 = L(13) - 0.05, L(14) - 0.05
    pill("MODAL SAMA Rp1 JUTA", t0, t1, bg=GREEN, y=280, **{"in": "none"})
    box = (60, 370, 1020, 1090)
    add("bars", t0, t1, box=box, values=[15, 45, 180, 495], labels=["Rp15 jt", "Rp45 jt", "Rp180 jt", "Rp495 jt"],
        colors=list(SONS), stagger=0.32, lsize=36, fmt="Rp{:.0f} jt", z=5, **{"in": "none"})
    gap = (box[2] - box[0] - 80) / 4
    for i in range(4):
        add("sprite", t0 + 0.3 + 0.32 * i, t1, art=("person", i, "smile", "down", True),
            x=box[0] + 40 + gap * (i + 0.5), y=G, s=0.34, z=3, sfx=False)

    # ------------------------------------------------ 14. uang vs cara berpikir
    t0, t1 = L(14) - 0.05, L(15) - 0.05
    add("sprite", t0, t1, art=("person", "father", "smile", "down", False), x=540, y=G, s=0.95, z=2, bob=2)
    add("xcheck", L(14, 0.05), t1, text="UANG", icon="cross", x=540, y=560, size=96, z=5)
    add("xcheck", L(14, 0.5), t1, text="CARA BERPIKIR", icon="check", col=GREEN, x=540, y=740, size=96, z=5)

    # ------------------------------------------------ 15. CTA
    t0 = L(15) - 0.05
    dur = end(15, 1.6)
    add("title", t0, dur, lines=[("KAMU ANAK", INK), ("NOMOR BERAPA?", RED)], x=540, y=330, size=94, z=6)
    pill("KOMEN 1, 2, 3 ATAU 4 • FOLLOW @kalpitalbiz", L(15, 0.2), dur, bg=RED, size=34, y=520)
    for i in range(4):
        x = 210 + i * 220
        son(i, x, t0 + 0.1 * i, dur, s=0.84, faces=[(L(15, 0.6), "happy")], sfx=False)
        add("sprite", L(15, 0.4) + 0.2 * i, dur, art=("numcircle", i + 1, SONS[i]), x=x, y=760, s=1.0, z=5)

    cuts = [("hook", 0.0), ("keluarga", h1)] + [(nm, L(i) - 0.05) for i, nm in (
        (2, "anak1"), (3, "anak1-hasil"), (4, "anak2"), (5, "anak2-hasil"), (6, "anak3"), (7, "anak3-dp"),
        (8, "anak3-hasil"), (9, "anak4-bank"), (10, "anak4-pinjam"), (11, "anak4-hasil"), (12, "risiko"),
        (13, "banding"), (14, "mindset"), (15, "cta"))]
    global HOOK_END
    HOOK_END = h1
    return E, cuts, dur


HOOK_END = 0.0
