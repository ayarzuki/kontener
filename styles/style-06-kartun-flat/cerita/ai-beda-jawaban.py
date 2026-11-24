"""Satu tokoh (Rafi, mahasiswa semester 7): 3 AI ditanya hal sama, jawabannya beda.

Fakta (Kompas 19 Nov 2026, detikINET 20 Nov 2026):
  pertanyaan sama -> "kalau GTA 6 berlatar Indonesia, kota mana yang cocok jadi Vice City?"
  Kompas   : ChatGPT = Batam, Gemini = Bali, Claude = Bali
  detikINET: ChatGPT = Jakarta, Claude = Jakarta, Gemini = Bali
  -> 2 dari 3 model berubah pilihan dalam sehari (jawaban generatif tidak deterministik)
Pelajaran: jangan kutip AI sebagai sumber skripsi; minta tautan jurnal, buka sendiri.
"""
from art import AMBER, GREEN, INK, RED, TEAL, WHITE

G = 1238
NAVY = (52, 96, 150)
JEANS = (58, 70, 96)
SKIN = 1


def rafi(face="smile", arm="down"):
    """Tokoh mahasiswa (pria, rambut pendek)."""
    return ("tokoh", NAVY, SKIN, "short", (40, 36, 34), None, face, arm, False, JEANS, False)


def build(ctx):
    L, D = ctx["L"], ctx["D"]
    E = []

    def add(kind, t0, t1, **kw):
        E.append(dict(kind=kind, t0=t0, t1=t1, **kw))

    def spr(a, t0, t1, x, y, s=1.0, z=3, **kw):
        add("sprite", t0, t1, art=a if isinstance(a, tuple) else (a,), x=x, y=y, s=s, z=z, **kw)

    def tokoh(t0, t1, x=230, s=1.0, face="smile", faces=(), arm="down", enter=True, tag=True, z=2):
        kw = {} if enter else {"in": "none", "sfx": False}
        spr(rafi(face, arm), t0, t1, x, G, s=s, z=z, bob=3,
            art_at=[(tt, rafi(f, arm)) for tt, f in faces], **kw)
        if tag:
            spr(("label_tag", "RAFI", NAVY), t0 + (0.15 if enter else 0), t1, x, G - 420 * s - 6,
                s=1.0, z=3, **kw)

    def pill(txt, t0, t1, y=300, bg=INK, fg=WHITE, size=40, x=540, **kw):
        add("pill", t0, t1, text=txt, x=x, y=y, bg=bg, fg=fg, size=size, z=6, **kw)

    def stamp(txt, t0, t1, y=470, col=(46, 140, 112), x=540, size=48):
        add("stamp", t0, t1, text=txt, x=x, y=y, col=col, size=size, z=9, **{"in": "stamp"})

    def eq(full, res, t0, t1, y=330, typ=0.8, size=70):
        add("eq", t0, t1, full=full, result=res, x=540, y=y, size=size, type=typ,
            t_res=t0 + typ + 0.2, z=7)

    def kolom(items, t0, t1, y_bub=1080, y_lap=1230):
        """Tiga kolom: balon jawaban di atas ikon laptop berlabel nama model."""
        for x, nama, jawab, tk in items:
            add("bubble", t0 + tk, t1, text=jawab, w=300, size=38, x=x, y=y_bub, s=0.95, z=6)
            spr(("laptop", nama), t0 + tk, t1, x, y_lap, s=0.62, z=3, **{"in": "none", "sfx": False})

    # ---------------------------------------------------------- 0. hook (layar gelap)
    h1 = L(1) - 0.05
    add("hooktitle", -0.8, h1,
        lines=[("3 AI, 1 PERTANYAAN", WHITE), ("JAWABANNYA BEDA", AMBER)], y=300, size=76, stagger=0.45)
    add("bubble", 0.5, h1, text="BATAM", w=320, size=38, x=540, y=900, s=1.0, z=4)
    add("bubble", 1.05, h1, text="BALI", w=260, size=38, x=540, y=1030, s=1.0, z=4)
    add("bubble", 1.6, h1, text="JAKARTA", w=360, size=38, x=540, y=1160, s=1.0, z=4)
    spr("qmark", 2.5, h1, 900, 760, s=1.0, z=4)

    # ---------------------------------------------------------- 1. kenalan
    t0, t1 = h1, L(2) - 0.05
    tokoh(t0, t1, x=230, faces=[(L(1, 0.7), "talk")])
    pill("SEMESTER 7", L(1, 0.15), t1, bg=TEAL)
    spr(("laptop", "BAB 2"), L(1, 0.5), t1, 760, G - 8, s=1.5, z=3)
    pill("BARU BAB 2", L(1, 0.62), t1, y=1010, x=760, bg=INK, size=28)

    # ---------------------------------------------------------- 2. pertanyaan sama
    t0, t1 = L(2) - 0.05, L(3) - 0.05
    pill("KOTA MANA COCOK JADI LATAR GTA 6?", t0 + 0.05, t1, y=290, bg=INK, size=34)
    for k, (x, nama) in enumerate([(190, "CHATGPT"), (540, "GEMINI"), (890, "CLAUDE")]):
        spr(("laptop", nama), t0 + 0.25 + 0.18 * k, t1, x, 1150, s=0.95, z=3)
    spr("qmark", L(2, 0.7), t1, 540, 830, s=1.3, z=4)

    # ---------------------------------------------------------- 3. hasil Kompas
    t0, t1 = L(3) - 0.05, L(4) - 0.05
    pill("KOMPAS • 19 NOVEMBER", t0 + 0.05, t1, y=290, bg=INK, size=32)
    kolom([(190, "CHATGPT", "BATAM", 0.15), (540, "GEMINI", "BALI", 0.35), (890, "CLAUDE", "BALI", 0.55)],
          t0, t1)

    # ---------------------------------------------------------- 4. sehari kemudian
    t0, t1 = L(4) - 0.05, L(5) - 0.05
    pill("DETIKINET • SEHARI KEMUDIAN", t0 + 0.05, t1, y=290, bg=TEAL, size=30)
    add("calendar", t0 + 0.1, t1, n0=1, n1=1, count=0.1, head="HARI", x=190, y=620, s=0.85, z=3,
        **{"in": "none"})
    stamp("2 DARI 3 BERUBAH", L(4, 0.5), t1, y=520, col=RED, size=44)
    kolom([(190, "CHATGPT", "JAKARTA", 0.2), (540, "GEMINI", "BALI", 0.4), (890, "CLAUDE", "JAKARTA", 0.6)],
          t0, t1)

    # ---------------------------------------------------------- 5. kenapa bisa beda
    t0, t1 = L(5) - 0.05, L(6) - 0.05
    tokoh(t0, t1, x=230, face="o", enter=False)
    eq("1 pertanyaan × 3 model", "3 jawaban", t0 + 0.1, t1, y=330, typ=0.7, size=62)
    stamp("NON-DETERMINISTIK", L(5, 0.62), t1, y=520, col=(196, 110, 30), size=40)

    # ---------------------------------------------------------- 6. bahaya buat skripsi
    t0, t1 = L(6) - 0.05, L(7) - 0.05
    tokoh(t0, t1, x=230, face="worry", enter=False)
    pill("KALAU LANGSUNG DIKUTIP", t0 + 0.05, t1, y=300, bg=RED, size=32)
    add("xcheck", t0 + 0.3, t1, text="TAUTAN BISA KARANGAN", icon="cross", x=540, y=470, size=54, z=6)
    add("xcheck", t0 + 0.7, t1, text="SUMBER TIDAK BISA DIBUKA", icon="cross", x=540, y=610, size=54, z=6)
    stamp("RISIKO", L(6, 0.8), t1, y=760, col=RED, size=52)

    # ---------------------------------------------------------- 7. tiga langkah
    t0, t1 = L(7) - 0.05, L(8) - 0.05
    tokoh(t0, t1, x=170, s=0.78, face="talk", enter=False)
    pill("3 LANGKAH AMAN", t0 + 0.05, t1, y=300, bg=GREEN)
    for k, (x, lab) in enumerate([(340, "TANYA 3 AI"), (610, "MINTA TAUTAN"), (880, "BUKA SENDIRI")]):
        tk = L(7, 0.2) + 0.2 * k
        spr(("numcircle", k + 1, GREEN), tk, t1, x, 720, s=1.05, z=6)
        pill(lab, tk + 0.08, t1, y=772, x=x, bg=INK, size=24)
        spr(("icon", "check", 30), tk + 0.2, t1, x, 880, s=1.0, z=6, anchor="center")

    # ---------------------------------------------------------- 8. rujukan yang bisa dicek
    t0, t1 = L(8) - 0.05, L(9) - 0.05
    tokoh(t0, t1, x=230, face="happy", enter=False)
    pill("SEMUA BISA DIBUKA", t0 + 0.05, t1, y=300, bg=GREEN)
    spr(("cert", "JURNAL"), t0 + 0.2, t1, 760, G - 8, s=1.25, z=3, **{"in": "drop"})
    spr(("price_tag", "DOI ASLI"), t0 + 0.5, t1, 760, 1010, s=0.85, z=5)
    stamp("RUJUKAN NYATA", L(8, 0.7), t1, y=520, col=GREEN, size=48)

    # ---------------------------------------------------------- 9. CTA
    t0 = L(9) - 0.05
    dur = L(9) + D(9) + 1.6
    add("title", t0, dur, lines=[("TANYA 1 AI,", INK), ("CEK 3 SUMBER", RED)], x=540, y=300, size=72, z=6)
    pill("COBA DI dosenku.biz.id • FOLLOW @dosenkubiz", L(9, 0.15), dur, bg=RED, size=28, y=480)
    for k, (x, lab) in enumerate([(300, "TANYA"), (540, "TAUTAN"), (780, "CEK")]):
        tk = L(9, 0.35) + 0.2 * k
        spr(("numcircle", k + 1, RED), tk, dur, x, 740, s=1.1, z=5)
        pill(lab, tk + 0.08, dur, y=792, x=x, bg=INK, size=24)
    tokoh(t0, dur, x=540, s=0.8, face="happy", arm="up", tag=False, z=3)

    cuts = [("hook", 0.0), ("kenalan", h1)] + [(nm, L(i) - 0.05) for i, nm in (
        (2, "pertanyaan"), (3, "hasil-kompas"), (4, "detik"), (5, "acak"), (6, "bahaya"),
        (7, "langkah"), (8, "hasil"), (9, "cta"))]
    global HOOK_END
    HOOK_END = h1
    return E, cuts, dur


HOOK_END = 0.0
