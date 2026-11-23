"""Parabel "Mindset Gaji": 4 karyawan, gaji sama Rp5 jt/bln, tabungan 5 tahun (ilustrasi, tanpa bunga/imbal hasil).

Hitungan:
  K1: gaji habis tiap bulan                     → Rp0
  K2: 10% = Rp500rb × 60 bulan                  → Rp30 jt
  K3: 20% (Rp1 jt) + sampingan Rp500rb × 60     → Rp90 jt
  K4: tahun 1: 20% × 12 = Rp12 jt untuk kursus; tahun 2–5 gaji Rp8 jt, 30% = Rp2,4 jt × 48 → Rp115,2 jt
"""
from art import AMBER, GREEN, INK, RED, SONS, WHITE

G = 1238
BROWN = (120, 96, 80)


def build(ctx):
    L, D = ctx["L"], ctx["D"]
    E = []

    def add(kind, t0, t1, **kw):
        E.append(dict(kind=kind, t0=t0, t1=t1, **kw))

    def son(i, x, t0, t1, s=0.92, face="smile", z=2, tag=None, faces=(), enter=True, arm="down", **kw):
        if not enter:
            kw = dict(kw, sfx=False)
            kw["in"] = "none"
        add("sprite", t0, t1, art=("person", i, face, arm, True), x=x, y=G, s=s, z=z, bob=3, phase=i * 0.7,
            art_at=[(tt, ("person", i, f, arm, True)) for tt, f in faces], **kw)
        if tag:
            ex = {} if enter else {"in": "none", "sfx": False}
            add("sprite", t0 + (0.15 if enter else 0), t1, art=("label_tag", tag, SONS[i]), x=x, y=G - 420 * s - 6,
                s=1.0, z=3, **ex)

    def pill(txt, t0, t1, y=300, bg=INK, fg=WHITE, size=44, x=540, **kw):
        add("pill", t0, t1, text=txt, x=x, y=y, bg=bg, fg=fg, size=size, z=6, **kw)

    def stamp(txt, t0, t1, y=470, col=(46, 140, 112), x=540, size=52):
        add("stamp", t0, t1, text=txt, x=x, y=y, col=col, size=size, z=9, **{"in": "stamp"})

    def eq(full, res, t0, t1, y=330, typ=0.8, size=70):
        add("eq", t0, t1, full=full, result=res, x=540, y=y, size=size, type=typ, t_res=t0 + typ + 0.2, z=7)

    def spr(name, t0, t1, x, y, s=1.0, z=3, **kw):
        a = name if isinstance(name, tuple) else (name,)
        add("sprite", t0, t1, art=a, x=x, y=y, s=s, z=z, **kw)

    # ------------------------------------------------ 0. hook
    h1 = L(1) - 0.05
    add("hooktitle", -0.8, h1, lines=[("GAJI SAMA RP5 JUTA,", WHITE), ("TABUNGAN BEDA RP115 JT?", AMBER)], y=330,
        size=68, stagger=0.45)
    for i in range(4):
        spr(("person", i, "smile", "down", True), 0.8 + i * 0.12, h1, 240 + i * 200, 1180, s=0.75, z=2)
        spr(("envelope", "Rp5 jt", "GAJI"), 1.9 + i * 0.12, h1, 240 + i * 200, 830, s=0.75, **{"in": "drop"})
    spr("qmark", 3.2, h1, 900, 740, s=1.0, z=4)

    # ------------------------------------------------ 1. kantor
    t0, t1 = h1, L(2) - 0.05
    spr(("office", "KANTOR"), t0, t1, 540, 1020, s=1.0, z=1, **{"in": "none"})
    xs = [190, 380, 700, 890]
    for i, x in enumerate(xs):
        son(i, x, L(1, 0.12) + i * 0.12, t1, s=0.84)
    pill("4 KARYAWAN BARU", L(1, 0.05), L(1, 0.5), bg=RED)
    pill("GAJI Rp5 JT / BULAN", L(1, 0.52), t1, bg=GREEN)
    for i, x in enumerate(xs):
        spr(("envelope", "Rp5 jt", "GAJI"), L(1, 0.6) + i * 0.1, t1, x, G - 380, s=0.7, z=4, **{"in": "drop"})
    stamp("START SAMA", L(1, 0.82), t1, y=470)

    # ------------------------------------------------ 2. K1 jajan
    t0, t1 = L(2) - 0.05, L(3) - 0.05
    son(0, 200, t0, t1, s=0.95, tag="KARYAWAN 1", faces=[(L(2, 0.3), "happy")])
    spr(("envelope", "Rp5 jt", "GAJI"), L(2, 0.1), L(2, 0.42), 560, 760, s=1.0)
    pill("GAJIAN, LANGSUNG JAJAN", L(2, 0.14), t1, bg=RED)
    items = [(("cup",), "Nongkrong", "Rp1,2 jt", 470, 2.2), (("bags",), "Belanja", "Rp1,8 jt", 700, 0.9),
             (("phone", "CICILAN"), "Cicilan HP", "Rp2 jt", 930, 0.85)]
    for k, (a, nm, price, x, sc) in enumerate(items):
        tk = L(2, 0.45) + k * 0.35 * D(2) * 0.42
        spr(a, tk, t1, x, G - 10, s=sc, z=3)
        spr(("price_tag", price), tk + 0.15, t1, x, 960, s=0.95, z=5)

    # ------------------------------------------------ 3. K1 hasil
    t0, t1 = L(3) - 0.05, L(4) - 0.05
    son(0, 200, t0, t1, s=0.95, tag="KARYAWAN 1", faces=[(L(3, 0.5), "worry")], enter=False)
    eq("Rp5 jt − Rp5 jt", "Rp0", L(3, 0.0), t1, typ=0.6)
    add("calendar", L(3, 0.1), t1, n0=1, n1=5, count=0.45 * D(3), head="TAHUN", x=560, y=720, s=0.9, z=3)
    spr(("jar", "Rp0"), L(3, 0.55), t1, 860, G - 10, s=1.0, z=3)
    stamp("HIDUP GAJIAN KE GAJIAN", L(3, 0.62), t1, y=480, col=RED, size=46)

    # ------------------------------------------------ 4. K2 sisihkan 10%
    t0, t1 = L(4) - 0.05, L(5) - 0.05
    son(1, 200, t0, t1, s=0.95, tag="KARYAWAN 2")
    spr(("envelope", "Rp5 jt", "GAJI"), L(4, 0.08), t1, 470, 720, s=0.95)
    pill("10% DI AWAL BULAN", L(4, 0.15), t1, bg=GREEN)
    spr(("arrow", GREEN, 140), L(4, 0.4), t1, 690, 760, s=1.0, anchor="center")
    spr(("jar", "Rp500rb"), L(4, 0.45), t1, 880, 900, s=1.0, z=3)
    spr(("bags",), L(4, 0.7), t1, 640, G - 10, s=0.6, z=2)
    spr(("price_tag", "sisanya Rp4,5 jt"), L(4, 0.72), t1, 700, 1070, s=0.8, z=5)

    # ------------------------------------------------ 5. K2 hasil
    t0, t1 = L(5) - 0.05, L(6) - 0.05
    son(1, 200, t0, t1, s=0.95, tag="KARYAWAN 2", faces=[(L(5, 0.6), "happy")], enter=False)
    eq("Rp500rb × 60", "Rp30 jt", L(5, 0.05), t1, typ=0.6)
    add("calendar", L(5, 0.05), t1, n0=1, n1=60, count=0.4 * D(5), head="BULAN", x=560, y=720, s=0.9, z=3)
    spr(("jar", "Rp500rb"), t0, t1, 880, G - 10, s=1.05, z=3,
        art_at=[(L(5, 0.3), ("jar", "Rp10 jt")), (L(5, 0.45), ("jar", "Rp20 jt")), (L(5, 0.6), ("jar", "Rp30 jt"))])
    stamp("BAYAR DIRI SENDIRI DULU", L(5, 0.7), t1, y=480, size=44)

    # ------------------------------------------------ 6. K3 20% + sampingan
    t0, t1 = L(6) - 0.05, L(7) - 0.05
    son(2, 200, t0, t1, s=0.95, tag="KARYAWAN 3")
    pill("20% + SAMPINGAN", L(6, 0.08), t1, bg=GREEN)
    spr(("jar", "Rp1 jt"), L(6, 0.15), t1, 500, G - 10, s=0.95, z=3)
    spr(("laptop", "TOKO ONLINE"), L(6, 0.42), t1, 800, 900, s=1.0, z=3)
    pill("akhir pekan", L(6, 0.5), t1, y=640, x=800, bg=BROWN, size=28)
    spr(("price_tag", "+Rp500rb"), L(6, 0.85), t1, 820, 1060, s=1.0, z=5)

    # ------------------------------------------------ 7. K3 hasil
    t0, t1 = L(7) - 0.05, L(8) - 0.05
    son(2, 200, t0, t1, s=0.95, tag="KARYAWAN 3", faces=[(L(7, 0.6), "happy")], enter=False)
    eq("Rp1,5 jt × 60", "Rp90 jt", L(7, 0.05), t1, typ=0.6)
    add("bars", L(7, 0.45), t1, box=(470, 520, 1020, 960), values=[30, 90], labels=["Rp30 jt", "Rp90 jt"],
        colors=[SONS[1], SONS[2]], stagger=0.3, lsize=34, fmt="Rp{:.0f} jt", z=5)
    stamp("PENGHASILAN TAMBAHAN", L(7, 0.7), t1, y=470, col=(196, 110, 30), size=46)

    # ------------------------------------------------ 8. K4 kursus
    t0, t1 = L(8) - 0.05, L(9) - 0.05
    son(3, 190, t0, t1, s=0.95, tag="KARYAWAN 4")
    pill("TAHUN 1: 20% UNTUK SKILL", L(8, 0.05), L(8, 0.65), bg=AMBER, fg=INK)
    spr(("jar", "Rp12 jt"), L(8, 0.3), L(8, 0.62), 480, G - 10, s=0.95, z=3,
        move=[(L(8, 0.48), 480, G - 10), (L(8, 0.6), 760, G - 120)], out="pop")
    spr(("cert", "SERTIFIKAT"), L(8, 0.58), t1, 760, 1000, s=1.1, z=3)
    eq("Rp1 jt × 12", "Rp12 jt", L(8, 0.66), t1, typ=0.5, y=330)
    stamp("INVESTASI KE DIRI SENDIRI", L(8, 0.86), t1, y=470, col=(30, 120, 150), size=44)

    # ------------------------------------------------ 9. K4 pindah kerja
    t0, t1 = L(9) - 0.05, L(10) - 0.05
    son(3, 190, t0, t1, s=0.95, tag="KARYAWAN 4", faces=[(L(9, 0.5), "happy")], enter=False)
    spr(("office", "KANTOR BARU"), L(9, 0.05), t1, 760, G, s=0.95, z=2)
    pill("TAHUN 2", L(9, 0.03), t1, bg=INK)
    add("result", L(9, 0.55), t1, value=8, v0=5, prefix="GAJI Rp", suffix=" jt", count=0.6, x=540, y=520, size=84, z=8)
    spr(("price_tag", "dulu Rp5 jt"), L(9, 0.6), t1, 540, 690, s=0.85, z=5)

    # ------------------------------------------------ 10. K4 hasil
    t0, t1 = L(10) - 0.05, L(11) - 0.05
    son(3, 190, t0, t1, s=0.95, z=3, tag="KARYAWAN 4", enter=False)
    add("crowd", L(10, 0.4), t1, n=1, n1=48, g0=L(10, 0.42), gdur=1.6, per=8, x0=370, x1=1030, yb=960, yf=G,
        sb=0.55, sf=0.75, art=("money", "Rp2,4 jt"), z=2, **{"in": "none"})
    add("counter", L(10, 0.4), t1, n0=1, n1=48, c0=L(10, 0.42), cdur=1.6, x=540, y=890, icon="uang", size=40, z=6)
    add("dim", L(10, 0.62), t1, alpha=100, z=4)
    eq("Rp8 jt × 30%", "Rp2,4 jt", t0 + 0.05, t1, y=290, typ=0.6, size=64)
    eq("Rp2,4 jt × 48", "", L(10, 0.35), t1, y=440, typ=0.5, size=64)
    add("result", L(10, 0.7), t1, value=115.2, dec=1, prefix="= Rp", suffix=" jt", count=0.8, x=540, y=610, size=96,
        z=8)

    # ------------------------------------------------ 11. gaji sekarang
    t0, t1 = L(11) - 0.05, L(12) - 0.05
    pill("GAJI SEKARANG", t0 + 0.05, t1, bg=INK)
    for i, x in enumerate([200, 420, 640, 880]):
        son(i, x, t0 + 0.05 * i, t1, s=0.84, faces=[(L(11, 0.3), "happy")] if i == 3 else [], sfx=False)
        tag = "Rp8 jt" if i == 3 else "Rp5 jt"
        spr(("price_tag", tag), L(11, 0.15) + (0.0 if i == 3 else 0.5 + 0.12 * i), t1, x + 18, 780,
            s=1.15 if i == 3 else 0.85, z=5)

    # ------------------------------------------------ 12. perbandingan
    t0, t1 = L(12) - 0.05, L(13) - 0.05
    pill("GAJI AWAL SAMA Rp5 JT", t0, t1, bg=GREEN, y=280, **{"in": "none"})
    box = (60, 370, 1020, 1090)
    add("bars", t0, t1, box=box, values=[0, 30, 90, 115.2], labels=["Rp0", "Rp30 jt", "Rp90 jt", "Rp115 jt"],
        colors=list(SONS), stagger=0.32, lsize=36, fmt="Rp{:.0f} jt", z=5, **{"in": "none"})
    gap = (box[2] - box[0] - 80) / 4
    for i in range(4):
        add("sprite", t0 + 0.3 + 0.32 * i, t1, art=("person", i, "smile", "down", True),
            x=box[0] + 40 + gap * (i + 0.5), y=G, s=0.34, z=3, sfx=False)

    # ------------------------------------------------ 13. gaji vs kebiasaan
    t0, t1 = L(13) - 0.05, L(14) - 0.05
    spr(("office", "KANTOR"), t0, t1, 540, G, s=0.9, z=2, sfx=False, **{"in": "none"})
    add("xcheck", L(13, 0.05), t1, text="GAJI", icon="cross", x=540, y=500, size=96, z=5)
    add("xcheck", L(13, 0.5), t1, text="KEBIASAAN", icon="check", col=GREEN, x=540, y=680, size=96, z=5)

    # ------------------------------------------------ 14. CTA
    t0 = L(14) - 0.05
    dur = L(14) + D(14) + 1.6
    add("title", t0, dur, lines=[("KAMU KARYAWAN", INK), ("NOMOR BERAPA?", RED)], x=540, y=330, size=88, z=6)
    pill("KOMEN 1, 2, 3 ATAU 4 • FOLLOW @kalpitalbiz", L(14, 0.2), dur, bg=RED, size=34, y=520)
    for i in range(4):
        x = 210 + i * 220
        son(i, x, t0 + 0.1 * i, dur, s=0.84, faces=[(L(14, 0.6), "happy")], sfx=False)
        add("sprite", L(14, 0.4) + 0.2 * i, dur, art=("numcircle", i + 1, SONS[i]), x=x, y=760, s=1.0, z=5)

    cuts = [("hook", 0.0), ("kantor", h1)] + [(nm, L(i) - 0.05) for i, nm in (
        (2, "k1-jajan"), (3, "k1-hasil"), (4, "k2-sisih"), (5, "k2-hasil"), (6, "k3-sampingan"), (7, "k3-hasil"),
        (8, "k4-kursus"), (9, "k4-pindah"), (10, "k4-hasil"), (11, "gaji-kini"), (12, "banding"), (13, "kebiasaan"),
        (14, "cta"))]
    global HOOK_END
    HOOK_END = h1
    return E, cuts, dur


HOOK_END = 0.0
