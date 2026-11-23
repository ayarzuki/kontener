"""Satu tokoh (Rina): "bocor halus" — kopi Rp25rb/hari & pengeluaran kecil lain (ilustrasi).

Hitungan:
  kopi: Rp25rb × 22 hari kerja = Rp550rb/bln; × 12 = Rp6,6 jt
  bocor lain: ongkir Rp180rb + langganan Rp150rb + checkout Rp300rb
  total: Rp1,18 jt/bln × 12 = Rp14,16 jt (≈ 2,36 × gaji Rp6 jt)
  kopi tetap, sisanya dipotong: Rp630rb/bln × 12 = Rp7,56 jt
"""
from art import AMBER, GREEN, INK, RED, WHITE

G = 1238
PURPLE = (120, 92, 170)
BROWN = (120, 96, 80)


def rina(face="smile", arm="down"):
    return ("tokoh", PURPLE, 0, "hijab", (232, 120, 140), None, face, arm, False, (70, 64, 110), True)


def build(ctx):
    L, D = ctx["L"], ctx["D"]
    E = []

    def add(kind, t0, t1, **kw):
        E.append(dict(kind=kind, t0=t0, t1=t1, **kw))

    def spr(a, t0, t1, x, y, s=1.0, z=3, **kw):
        add("sprite", t0, t1, art=a if isinstance(a, tuple) else (a,), x=x, y=y, s=s, z=z, **kw)

    def tokoh(t0, t1, x=230, s=1.0, face="smile", faces=(), arm="down", enter=True, tag=True, z=2):
        kw = {} if enter else {"in": "none", "sfx": False}
        spr(rina(face, arm), t0, t1, x, G, s=s, z=z, bob=3, art_at=[(tt, rina(f, arm)) for tt, f in faces], **kw)
        if tag:
            spr(("label_tag", "RINA", PURPLE), t0 + (0.15 if enter else 0), t1, x, G - 420 * s - 6, s=1.0, z=3, **kw)

    def pill(txt, t0, t1, y=300, bg=INK, fg=WHITE, size=44, x=540, **kw):
        add("pill", t0, t1, text=txt, x=x, y=y, bg=bg, fg=fg, size=size, z=6, **kw)

    def stamp(txt, t0, t1, y=470, col=(46, 140, 112), x=540, size=52):
        add("stamp", t0, t1, text=txt, x=x, y=y, col=col, size=size, z=9, **{"in": "stamp"})

    def eq(full, res, t0, t1, y=330, typ=0.8, size=70):
        add("eq", t0, t1, full=full, result=res, x=540, y=y, size=size, type=typ, t_res=t0 + typ + 0.2, z=7)

    ITEMS = [(("cup",), 440, 1.6, "Rp550rb"), (("parcel", "ONGKIR"), 615, 0.72, "Rp180rb"),
             (("phone", "LANGGANAN"), 790, 0.72, "Rp150rb"), (("bags",), 960, 0.66, "Rp300rb")]

    def items(t0, t1, enter_times=None, tags=True):
        for k, (a, x, sc, price) in enumerate(ITEMS):
            te = enter_times[k] if enter_times else t0
            kw = {} if enter_times else {"in": "none", "sfx": False}
            spr(a, te, t1, x, G - 8, s=sc, **kw)
            if tags:
                spr(("price_tag", price), te + (0.12 if enter_times else 0), t1, x + 6, 1000 if k % 2 == 0 else 950,
                    s=0.78, z=5, **kw)

    # ------------------------------------------------ 0. hook
    h1 = L(1) - 0.05
    add("hooktitle", -0.8, h1, lines=[("KOPI RP25 RIBU,", WHITE), ("SETAHUN RP6,6 JUTA?", AMBER)], y=330, size=78,
        stagger=0.45)
    spr("cup", 0.5, h1, 540, 1230, s=3.6, z=2)
    spr(("price_tag", "Rp25rb"), 1.2, h1, 760, 860, s=1.2, z=4)
    spr(("moneybag", "Rp6,6 jt"), 2.4, h1, 270, 1230, s=1.1, z=3, **{"in": "drop"})
    spr("qmark", 3.4, h1, 880, 700, s=1.0, z=4)

    # ------------------------------------------------ 1. kenalan
    t0, t1 = h1, L(2) - 0.05
    tokoh(t0, t1, x=230, faces=[(L(1, 0.6), "happy")])
    pill("GAJI Rp6 JT / BULAN", L(1, 0.25), t1, bg=GREEN)
    spr("cup", L(1, 0.62), t1, 700, G - 10, s=3.0, z=3)
    spr(("price_tag", "Rp25rb / hari"), L(1, 0.75), t1, 720, 900, s=1.0, z=5)

    # ------------------------------------------------ 2. sebulan
    t0, t1 = L(2) - 0.05, L(3) - 0.05
    tokoh(t0, t1, x=230, enter=False)
    add("calendar", L(2, 0.15), t1, n0=1, n1=22, count=0.4 * D(2), head="HARI KERJA", x=650, y=650, s=0.95, z=3)
    add("crowd", L(2, 0.15), t1, n=1, n1=22, g0=L(2, 0.25), gdur=0.4 * D(2), per=11, x0=400, x1=1050, yb=1120,
        yf=G, sb=1.0, sf=1.15, art=("cup",), z=2, **{"in": "none"})
    eq("Rp25rb × 22", "Rp550rb", L(2, 0.55), t1, typ=0.6)

    # ------------------------------------------------ 3. setahun
    t0, t1 = L(3) - 0.05, L(4) - 0.05
    tokoh(t0, t1, x=230, face="o", enter=False)
    add("crowd", t0, t1, n=22, per=11, x0=400, x1=1050, yb=1120, yf=G, sb=1.0, sf=1.15, art=("cup",), z=2,
        **{"in": "none"})
    add("calendar", t0, t1, n0=1, n1=12, count=0.35 * D(3), head="BULAN", x=650, y=650, s=0.95, z=3)
    eq("Rp550rb × 12", "Rp6,6 jt", t0 + 0.05, t1, typ=0.6)
    stamp("LATTE FACTOR", L(3, 0.62), t1, y=470, col=(196, 110, 30))

    # ------------------------------------------------ 4. bocor lain
    t0, t1 = L(4) - 0.05, L(5) - 0.05
    tokoh(t0, t1, x=200, face="worry", enter=False)
    pill("BOCOR HALUS LAIN", L(4, 0.05), t1, bg=RED)
    items(t0, t1, enter_times=[t0 + 0.1, L(4, 0.12), L(4, 0.42), L(4, 0.72)])

    # ------------------------------------------------ 5. total
    t0, t1 = L(5) - 0.05, L(6) - 0.05
    tokoh(t0, t1, x=200, face="worry", enter=False)
    items(t0, t1)
    add("dim", t0 + 0.1, t1, alpha=105, z=4)
    eq("550 + 180 + 150 + 300", "Rp1,18 jt", t0 + 0.05, t1, y=290, typ=0.9, size=64)
    pill("angka dalam ribu rupiah, per bulan", t0 + 0.2, t1, y=380, bg=BROWN, size=26)
    eq("Rp1,18 jt × 12", "", L(5, 0.42), t1, y=480, typ=0.5, size=64)
    add("result", L(5, 0.66), t1, value=14.16, dec=2, prefix="= Rp", suffix=" jt", count=0.8, x=540, y=650, size=96,
        z=8)

    # ------------------------------------------------ 6. dibanding gaji
    t0, t1 = L(6) - 0.05, L(7) - 0.05
    add("bars", t0, t1, box=(150, 400, 930, 1120), values=[6, 14.16], labels=["Rp6 jt", "Rp14,16 jt"],
        cats=["gaji 1 bulan", "bocor 1 tahun"], csize=36, colors=[(34, 143, 141), RED], stagger=0.3, lsize=40,
        fmt="Rp{:.0f} jt", z=5, **{"in": "none"})
    stamp("≈ 2,4 BULAN GAJI", L(6, 0.55), t1, y=300, col=RED, size=50)

    # ------------------------------------------------ 7. solusi
    t0, t1 = L(7) - 0.05, L(8) - 0.05
    tokoh(t0, t1, x=200, face="talk", faces=[(L(7, 0.9), "smile")])
    items(t0, t1, tags=False)
    pill("PILIH YANG PALING PENTING", L(7, 0.45), t1, bg=GREEN)
    spr(("icon", "check", 34), L(7, 0.55), t1, 440, 980, s=1.0, z=6, anchor="center")
    for k, (_, x, _, _) in enumerate(ITEMS[1:]):
        spr(("icon", "cross", 34), L(7, 0.68) + 0.15 * k, t1, x, 980, s=1.0, z=6, anchor="center")

    # ------------------------------------------------ 8. hemat
    t0, t1 = L(8) - 0.05, L(9) - 0.05
    tokoh(t0, t1, x=200, face="happy", enter=False)
    spr("cup", t0, t1, 440, G - 8, s=1.6, z=3, sfx=False, **{"in": "none"})
    spr(("icon", "check", 34), t0, t1, 440, 980, s=1.0, z=6, anchor="center", sfx=False, **{"in": "none"})
    eq("Rp1,18 jt − Rp550rb", "Rp630rb", L(8, 0.05), t1, y=300, typ=0.6, size=64)
    eq("Rp630rb × 12", "Rp7,56 jt", L(8, 0.45), t1, y=450, typ=0.5, size=64)
    spr(("jar", "Rp630rb"), L(8, 0.2), t1, 820, G - 8, s=1.1, z=3,
        art_at=[(L(8, 0.62), ("jar", "Rp7,56 jt"))])
    stamp("PRIORITAS", L(8, 0.82), t1, y=580, col=GREEN)

    # ------------------------------------------------ 9. sadar
    t0, t1 = L(9) - 0.05, L(10) - 0.05
    tokoh(t0, t1, x=540, face="happy", tag=False)
    add("xcheck", L(9, 0.05), t1, text="PELIT", icon="cross", x=540, y=480, size=96, z=5)
    add("xcheck", L(9, 0.5), t1, text="SADAR", icon="check", col=GREEN, x=540, y=650, size=96, z=5)

    # ------------------------------------------------ 10. CTA
    t0 = L(10) - 0.05
    dur = L(10) + D(10) + 1.6
    add("title", t0, dur, lines=[("BOCOR HALUS KAMU", INK), ("PALING BESAR DI MANA?", RED)], x=540, y=320, size=74, z=6)
    pill("KOMEN DI BAWAH • FOLLOW @kalpitalbiz", L(10, 0.15), dur, bg=RED, size=34, y=500)
    cta = [(("cup",), 1.25, "KOPI"), (("parcel", "ONGKIR"), 0.55, "ONGKIR"), (("phone", "LANGGANAN"), 0.55, "LANGGANAN"),
           (("bags",), 0.5, "CHECKOUT")]
    for k, (a, sc, lab) in enumerate(cta):
        x = 160 + k * 253
        tk = L(10, 0.35) + 0.25 * k
        spr(a, tk, dur, x, 800, s=sc, z=4)
        pill(lab, tk + 0.1, dur, y=842, x=x, bg=BROWN, size=24)
    tokoh(t0, dur, x=540, s=0.82, face="happy", arm="up", tag=False, z=3)

    cuts = [("hook", 0.0), ("kenalan", h1)] + [(nm, L(i) - 0.05) for i, nm in (
        (2, "sebulan"), (3, "setahun"), (4, "bocor-lain"), (5, "total"), (6, "banding"), (7, "solusi"), (8, "hemat"),
        (9, "sadar"), (10, "cta"))]
    global HOOK_END
    HOOK_END = h1
    return E, cuts, dur


HOOK_END = 0.0
