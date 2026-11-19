"""Escenas del vídeo 1. Cada función dibuja un beat: f(c, S) con S.t (s locales), S.dur, S.p, S.words."""
import math, random
from lib import *
import lib
from chars import person, anatomy
lib.stick = person
stick = person

CX, CY = 960, 600


def doc(c, S, x, y=1000, s=1.0, pose="point", a=255):
    stick(c, x, y, s, "happy", pose, S.t, doctor=True, talk=speaking(S.words, S.t), a=a)


def popin(c, S, at, x, y, fn, d=.45):
    k = pr(S.t, at, d)
    if k <= 0:
        return
    c.save(); c.translate(x, y); s = back(k); c.scale(s, s); fn(); c.restore()


def bob(S, amp=8, sp=2.0, ph=0):
    return math.sin(S.t * sp + ph) * amp


def floaty(c, S, x, y, s, f):
    c.save(); c.translate(x, y + bob(S, 6, 1.7, x)); c.scale(s, s); f(); c.restore()


def label(c, s, x, y, size=54, col=INK, a=255):
    text(c, s, x, y, size, col, "hand", "c", a)


def hexes_outside(c, S, n, x0, x1, y, seed=1, rmin=16, a=255):
    rnd = random.Random(seed)
    for i in range(n):
        x = lerp(x0, x1, (i + .5) / n) + rnd.uniform(-20, 20)
        yy = y + math.sin(S.t * 3 + i * 1.3) * 14
        hexagon(c, x, yy, rmin + rnd.uniform(0, 6), a=a, rot=S.t * .5 + i)


# ═════════════════ HOOK ═════════════════
def two_breakfast(c, S):
    line(c, 260, 820, 1660, 820, INK, 9, eo(pr(S.t, 0, .6)))
    for i, x in enumerate((620, 1300)):
        popin(c, S, .2 + i * .35, x, 820, lambda x=x, i=i: (
            stick(c, -90, 0, 1.0, "happy", "stand", S.t, hair="f" if i else None),
            icon(c, "plate", 60, -40, .8), icon(c, "coffee", 170, -50, .55)))
    popin(c, S, 1.4, 960, 560, lambda: text(c, "=", 0, 40, 200, TEAL, "marker"))


def equal_cards(c, S):
    keys = ["calor", "hora", "vida"]
    for i, it in enumerate(S.p["items"]):
        at = S.wt(keys[i], .3 + i * .6)
        x = 330 + i * 630
        def f(it=it):
            rrect(c, -270, -130, 540, 260, 30, INK, 7, WHITE)
            text(c, it, 0, 20, fit_size(it, "marker", 58, 480), INK, "marker")
            check(c, 0, 85, 26, pr(S.t, at + .3, .4), 10)
        popin(c, S, at, x, 600, f)


def person_graph(c, S):
    mood = S.p["mood"]
    stick(c, 470, 960, 1.35, mood, "stand", S.t, sweat=(mood == "tired"), lean=(6 if mood == "tired" else 0))
    clock(c, 1650, 300, 85, 11.0 + S.t / 600)
    axes(c, 900, 420, 650, 400, eo(pr(S.t, .1, .6)), "hora", "energía")
    if S.p["graph"] == "roller":
        fn = lambda u: .5 + .38 * math.sin(u * 12) * (1 - u * .3) - .2 * u
        curve(c, 900, 420, 650, 400, fn, eo(pr(S.t, .4, 1.6)), RED, 10)
        k = pr(S.t, S.wt("dulce", 2.5), .5)
        if k > 0:
            c.save(); c.translate(640, 470); c.scale(back(k), back(k))
            for r, (dx, dy) in ((14, (-150, 150)), (22, (-110, 100))):
                c.drawCircle(dx, dy, r, fill(WHITE)); c.drawCircle(dx, dy, r, stroke(INK, 5))
            rrect(c, -130, -110, 220, 170, 60, INK, 6, WHITE, shadow=False)
            icon(c, "cookie", -20, -25, .9); c.restore()
    else:
        curve(c, 900, 420, 650, 400, lambda u: .62 + .03 * math.sin(u * 9), eo(pr(S.t, .3, 1.2)), GREEN, 10)
        check(c, 1640, 520, 50, eo(pr(S.t, 1.2, .5)))


def cross_list(c, S):
    keys = ["desayuno", "genética", "voluntad"]
    for i, it in enumerate(S.p["items"]):
        y = 380 + i * 200
        at = S.wt(keys[i], .4 + i * .9)
        a = 255 * eo(pr(S.t, at - .5, .4))
        text(c, it, CX, y, 96, INK, "marker", a=a)
        w = tw(it, "marker", 96)
        line(c, CX - w / 2 - 30, y - 30, CX + w / 2 + 30, y - 40, RED, 14, eo(pr(S.t, at + .25, .35)))


def clock_window(c, S):
    h0, h1 = S.p["from"], S.p["to"]
    k = eio(pr(S.t, .3, S.dur * .7))
    x, y, r = 640, 620, 290
    # sector resaltado
    a0 = (h0 % 12) / 12 * 360 - 90; sweep = ((lerp(h0, h1, k) - h0) % 12) / 12 * 360
    if h1 - h0 <= .5:
        a0 = (h0 % 1) * 360 - 90; sweep = (lerp(h0, h1, k) - h0) % 1 * 360
    clock(c, x, y, r, lerp(h0, h1, k))
    if sweep > 0:
        c.drawArc(skia.Rect.MakeXYWH(x - r * .9, y - r * .9, r * 1.8, r * 1.8), a0, sweep, True, fill(AMBER, 90))
    clock_h = lerp(h0, h1, k)
    hh, mm = int(clock_h), int(round((clock_h % 1) * 60)) % 60
    text(c, f"{hh}:{mm:02d}", x, y + r + 110, 90, INK, "bold")
    popin(c, S, S.wt("diez", .9) if "diez" in S.text.lower() else 1.0, 1350, 860,
          lambda: stick(c, 0, 0, 1.25, "happy", "walk", S.t))
    if "desayun" in S.text.lower():
        popin(c, S, S.wt("desayunar", 2.5), 1620, 520, lambda: (icon(c, "plate", 0, 0, 1.0), xmark(c, 0, 0, 90, pr(S.t, S.wt("desayunar", 2.5) + .3, .5))))


def paradox_tease(c, S):
    at1, at2 = S.wt("doble", 3.0), S.wt("adelgaz", 5.0)
    k0 = 1 - pr(S.t, at1 - .4, .4)
    if k0 > 0:
        c.save(); c.translate(0, 0)
        popin(c, S, .1, 960, 300, lambda: text(c, "UN EXPERIMENTO", 0, 0, 90, TEAL, "marker", a=255 * k0))
        for i in range(8):
            popin(c, S, .3 + i * .12, 420 + i * 155, 900, lambda: stick(c, 0, 0, .8, "neutral", "stand", S.t, a=255 * k0))
        c.restore()
    popin(c, S, at1, 560, 560, lambda: (
        rrect(c, -300, -230, 600, 460, 40, INK, 8, WHITE),
        text(c, "×2", 0, 40, 220, AMBER, "bold"),
        text(c, "GRASA QUEMADA", 0, 160, 54, INK, "marker")))
    popin(c, S, at2, 1360, 560, lambda: (
        rrect(c, -300, -230, 600, 460, 40, INK, 8, WHITE),
        icon(c, "scale", 0, -30, 1.6),
        text(c, "MISMO PESO", 0, 160, 54, INK, "marker")))
    for i in range(3):
        k = pr(S.t, at2 + .4 + i * .15, .4)
        if k > 0:
            c.save(); c.translate(960 + (i - 1) * 90, 300 + bob(S, 10, 3, i)); c.rotate(-12 + i * 12)
            text(c, "?", 0, 0, 120 * back(k), RED, "marker"); c.restore()


def big_question(c, S):
    s = S.p["text"]
    k = pr(S.t, .1, .5)
    c.save(); c.translate(CX, 590); sc = lerp(.6, 1, back(k)) * (1 + .02 * math.sin(S.t * 3)); c.scale(sc, sc)
    marker_text(c, s, 0, 0, 120, INK, YEL, k * 1.5)
    c.restore()
    rnd = random.Random(len(s))
    for i in range(6):
        x = 260 + (i % 3) * 700 + math.sin(S.t * .8 + i) * 60
        y = (300 if i < 3 else 900) + math.cos(S.t * 1.1 + i) * 25
        a = 255 * pr(S.t, .4 + i * .12, .3)
        c.save(); c.translate(x, y); c.rotate(math.sin(S.t * 2 + i) * 15)
        text(c, "?", 0, 0, 90 + rnd.uniform(0, 50), [TEAL, AMBER, RED][i % 3], "marker", a=a); c.restore()


# ═════════════════ SEÑAL ═════════════════
def doctor_intro(c, S):
    s = S.p.get("text", "LO QUE NO ES")
    popin(c, S, 0, 620, 1000, lambda: doc(c, S, 0, 0, 1.55, "point"))
    def board():
        rrect(c, -420, -200, 840, 400, 20, INK, 9, WHITE)
        marker_text(c, s, 0, 25, fit_size(s, "marker", 92, 700), RED if "NO" in s else TEAL, YEL, pr(S.t, .6, 1))
    popin(c, S, .3, 1270, 470, board)


def icon_cross(c, S):
    keys = ["dieta", "suplemento", "helada", "gimnasio"]
    for i, nm in enumerate(S.p["icons"]):
        at = S.wt(keys[i], .3 + i * 1.2)
        x = 330 + i * 420
        popin(c, S, at - .35, x, 600, lambda nm=nm: icon(c, nm, 0, 0, 1.5, t=S.t))
        xmark(c, x, 600, 110, pr(S.t, at + .1, .5))


def hills(c, S, sun_k=1.0):
    sy = lerp(760, 360, eo(sun_k))
    icon(c, "sun", 1450, sy, 1.4, t=S.t)
    p = smooth([(0, 760), (400, 690), (900, 740), (1400, 680), (1920, 740), (1920, 1080), (0, 1080)], True)
    c.drawPath(p, fill((205, 232, 196))); c.drawPath(p, stroke(INK, 7))


def walk_sunrise(c, S):
    hills(c, S, pr(S.t, 0, 2.5))
    x = lerp(300, 1100, S.t / max(S.dur, 1))
    stick(c, x, 820, 1.15, "happy", "walk", S.t)
    clock(c, 260, 330, 90, 7.0 + S.t / 300)


def skeptic(c, S):
    stick(c, 600, 980, 1.6, "skeptic", "shrug", S.t)
    def bubble():
        for r, (dx, dy) in ((16, (-260, 170)), (26, (-210, 110))):
            c.drawCircle(dx, dy, r, fill(WHITE)); c.drawCircle(dx, dy, r, stroke(INK, 6))
        rrect(c, -200, -170, 660, 270, 120, INK, 7, WHITE, shadow=False)
        text(c, "¿Caminar despacio?", 130, -60, 64, INK, "hand")
        text(c, "Eso no sirve...", 130, 30, 64, RED, "hand")
    popin(c, S, .35, 1000, 420, bubble)
    if S.t > S.wt("nada", 2.5):
        stick(c, 1500, 980, .9, "calm", "walk", S.t, a=200)


def kcal_cookie(c, S):
    at = S.wt("treinta", 2.5)
    v = int(round(S.p["value"] * eo(pr(S.t, at, 1.2))))
    if S.t > at - .2:
        text(c, f"{v}", 650, 640, 300, AMBER, "bold")
        text(c, "kcal", 650, 760, 80, INK, "marker")
    else:
        popin(c, S, .1, 650, 600, lambda: text(c, "CALORÍAS", 0, 0, 110, INK, "marker"))
    ag = S.wt("galleta", S.dur - 1.5)
    popin(c, S, ag - .1, 1150, 600, lambda: text(c, "≈", 0, 40, 160, INK, "bold"))
    popin(c, S, ag, 1450, 600, lambda: icon(c, "cookie", 0, 0, 2.6))


def signal_body(c, S):
    stick(c, 420, 950, 1.3, "happy", "walk", S.t)
    # ondas
    for i in range(4):
        r = ((S.t * 260 + i * 110) % 440) + 40
        a = 255 * (1 - r / 480) * pr(S.t, .3, .5)
        c.drawArc(skia.Rect.MakeXYWH(420 - r, 600 - r, 2 * r, 2 * r), -40, 80, False, stroke(TEAL, 8, a))
    # sobre viajando
    k = (S.t * .45) % 1
    ex, ey = lerp(560, 1250, eio(k)), 560 - math.sin(k * math.pi) * 140
    c.save(); c.translate(ex, ey); c.rotate(-10 + 20 * k)
    rrect(c, -70, -45, 140, 90, 10, INK, 6, WHITE, shadow=False)
    c.drawPath(poly([(-70, -45), (0, 10), (70, -45)]), stroke(INK, 6)); c.restore()
    # cuerpo receptor
    gl = ["brain", "liver", "muscle"][min(2, int(max(0, S.t - 1.0) / 1.2))] if S.t > 1.0 else None
    anatomy(c, 1480, 560, .78, glow=gl, t=S.t)


def eye_open(c, S):
    k = eio(pr(S.t, .4, 1.4)); z = 1 + 2.2 * eio(pr(S.t, S.dur - 1.6, 1.4))
    c.save(); c.translate(CX, 560); c.scale(z, z)
    w, h = 520, 260 * k + 8
    eye = skia.Path(); eye.moveTo(-w, 0); eye.quadTo(0, -h * 1.6, w, 0); eye.quadTo(0, h * 1.6, -w, 0); eye.close()
    c.drawPath(eye, fill(WHITE)); c.save(); c.clipPath(eye, doAntiAlias=True)
    c.drawCircle(0, 0, 190, fill(TEAL)); c.drawCircle(0, 0, 95, fill(INK)); c.drawCircle(-40, -45, 30, fill(WHITE))
    c.restore(); c.drawPath(eye, stroke(INK, 10))
    for i in range(7):
        ang = math.pi * (1.15 + i * .7 / 6)
        c.drawLine(math.cos(ang) * w * .7, -h * .95 + 10 + abs(math.sin(ang)) * 0, math.cos(ang) * w * .8, -h * 1.1 - 30, stroke(INK, 7, 255 * k))
    c.restore()


# ═════════════════ DESPERTAR ═════════════════
def alarm(c, S):
    icon(c, "bed", 700, 820, 1.6)
    k = pr(S.t, 1.2, .6)
    c.save(); c.translate(560, 760); c.rotate(-90 + 70 * eo(k)); stick(c, 0, 0, .9, "sleep" if k < .5 else "wow", "stand", S.t); c.restore()
    icon(c, "alarm", 1350, 470, 1.6, t=S.t)
    text(c, "7:00", 1350, 700, 90, RED, "bold")
    if k < .5:
        for i in range(3):
            yy = 560 - ((S.t * 40 + i * 40) % 120)
            text(c, "z", 650 + i * 30, yy, 50 + i * 12, BLUE, "marker", a=180)


def adrenal(c, x, y, s=1.0, a=255):
    c.save(); c.translate(x, y); c.scale(s, s)
    for sx in (-1, 1):
        k = smooth([(sx * 120, -60), (sx * 190, -40), (sx * 205, 60), (sx * 160, 140), (sx * 100, 110), (sx * 110, 30)], True)
        c.drawPath(k, fill((196, 90, 80), a)); c.drawPath(k, stroke(INK, 6, a))
        hat = poly([(sx * 110, -55), (sx * 150, -110), (sx * 195, -45)], True)
        c.drawPath(hat, fill(AMBER, a)); c.drawPath(hat, stroke(INK, 6, a))
    c.restore()


def hormone_tag(c, S):
    popin(c, S, .1, 620, 620, lambda: adrenal(c, 0, 0, 1.6))
    def tag():
        rrect(c, -300, -90, 600, 180, 30, INK, 8, WHITE)
        text(c, S.p["name"], 0, 30, 100, COL[S.p["color"]], "marker")
    popin(c, S, .5, 1350, 470, tag)
    if S.t > S.wt("estrés", 2.5):
        popin(c, S, S.wt("estrés", 2.5), 1350, 740, lambda: text(c, "«la hormona del estrés»", 0, 0, 60, GREY, "hand"))
    for i in range(5):
        k = ((S.t * .5 + i * .2) % 1)
        hexagon(c, 620 + lerp(0, 600, k), 520 - math.sin(k * math.pi) * 200, 14, RED, 255 * (1 - k))


def cortisol_chart(c, S):
    x, y, w, h = 300, 330, 1000, 520
    axes(c, x, y, w, h, eo(pr(S.t, 0, .6)), "", "cortisol")
    text(c, "minutos desde que despiertas", x + w / 2, y + h + 105, 42, INK, "hand", a=255 * pr(S.t, .3, .4))
    for i, m in enumerate((0, 15, 30, 45, 60)):
        text(c, str(m), x + w * m / 60, y + h + 45, 40, GREY, "hand", a=255 * pr(S.t, .4, .4))
    fn = lambda u: .35 + .5 * (math.sin(min(u / .5, 1) * math.pi / 2) if u < .5 else 1 - .35 * (u - .5) / .5) * 1.0
    k = eo(pr(S.t, .8, max(1.0, S.wt("cincuenta", 3.5) - .8)))
    curve(c, x, y, w, h, fn, k, RED, 11)
    line(c, x, y + h - h * .35, x + w, y + h - h * .35, GREY, 4, k, 160)
    at = S.wt("cincuenta", 3.5)
    popin(c, S, at, 1560, 420, lambda: text(c, "+50%", 0, 40, 170, RED, "bold"))
    popin(c, S, at + .2, 1560, 540, lambda: text(c, "en 30 min", 0, 0, 60, INK, "hand"))
    aq = S.wt("quinientos", S.dur - 2)
    def people():
        rrect(c, -200, -80, 400, 160, 24, INK, 6, WHITE)
        for i in range(7):
            stick(c, -150 + i * 50, 50, .2, "happy")
        text(c, "509 adultos", 0, -30, 48, INK, "marker")
    popin(c, S, aq, 1560, 760, people)


def inner_alarm(c, S):
    anatomy(c, 960, 520, .85, glow="brain", t=S.t)
    icon(c, "alarm", 960, 470, .8, t=S.t)
    for i in range(3):
        r = 140 + ((S.t * 200 + i * 80) % 240)
        c.drawCircle(960, 470, r, stroke(AMBER, 6, 255 * (1 - (r - 140) / 240)))
    popin(c, S, S.wt("moverse", 2.5), 1520, 420, lambda: (
        rrect(c, -230, -90, 460, 180, 80, INK, 7, WHITE), text(c, "¡A MOVERSE!", 0, 22, 66, TEAL, "marker")))
    popin(c, S, S.wt("estrés", .8), 420, 420, lambda: (text(c, "NO ES ESTRÉS", 0, 0, 60, RED, "marker"),))


def vessel(c, y0=780, y1=960, a=255):
    top = [(x, y0 + 14 * math.sin(x / 140)) for x in range(-20, 1960, 40)]
    bot = [(x, y1 + 14 * math.sin(x / 140)) for x in range(-20, 1960, 40)]
    shape = smooth(top + bot[::-1], True)
    c.drawPath(shape, fill((250, 214, 214), a))
    c.drawPath(smooth(top), stroke(RED, 8, a)); c.drawPath(smooth(bot), stroke(RED, 8, a))


def liver_release(c, S):
    vessel(c)
    icon(c, "liver", 520, 470, 1.6)
    label(c, "hígado", 520, 640)
    for i in range(14):
        k = ((S.t * .32 + i / 14) % 1)
        if S.t < i * .12:
            continue
        if k < .35:
            x, y = lerp(560, 640, k / .35), lerp(500, 870, eio(k / .35))
        else:
            x, y = lerp(640, 2000, (k - .35) / .65), 870 + 30 * math.sin(k * 20 + i)
        hexagon(c, x, y, 18, rot=k * 6)
    popin(c, S, S.wt("cerebro", 4.0), 1450, 360, lambda: icon(c, "brain", 0, 0, 1.2))
    popin(c, S, S.wt("músculos", 4.6), 1700, 560, lambda: icon(c, "dumbbell", 0, 0, .9))


def gauge(c, x, y, r, level, label_s, col_hi=RED):
    for i in range(30):
        u = i / 29
        ang = math.pi * (1 + u)
        col = (int(lerp(GREEN[0], col_hi[0], u)), int(lerp(GREEN[1], col_hi[1], u)), int(lerp(GREEN[2], col_hi[2], u)))
        c.drawLine(x + math.cos(ang) * r * .78, y + math.sin(ang) * r * .78, x + math.cos(ang) * r, y + math.sin(ang) * r, stroke(col, 18))
    c.drawArc(skia.Rect.MakeXYWH(x - r * 1.05, y - r * 1.05, r * 2.1, r * 2.1), 180, 180, False, stroke(INK, 6))
    ang = math.pi * (1 + level)
    c.drawLine(x, y, x + math.cos(ang) * r * .7, y + math.sin(ang) * r * .7, stroke(INK, 12))
    c.drawCircle(x, y, 22, fill(INK))
    text(c, label_s, x, y + 110, 72, INK, "marker")


def insulin_gauge(c, S):
    lv = lerp(.85, S.p["level"], eo(pr(S.t, .3, 1.4))) + .02 * math.sin(S.t * 5)
    gauge(c, 960, 700, 330, lv, "INSULINA", AMBER)
    popin(c, S, S.wt("baja", 1.6), 1500, 420, lambda: text(c, "BAJA", 0, 0, 110, GREEN, "marker"))
    popin(c, S, S.wt("guarda", 1.0), 420, 420, lambda: (text(c, "= guardar", 0, 0, 60, GREY, "hand"),))


def three_stack(c, S):
    keys = ["combustible", "insulina", "señal"]
    cols = [AMBER, GREEN, TEAL]
    for i, it in enumerate(S.p["items"]):
        at = S.wt(keys[i], .3 + i * 1.0)
        y = 330 + i * 230
        def f(it=it, i=i):
            rrect(c, -620, -90, 1240, 180, 30, INK, 7, WHITE)
            c.drawCircle(-520, 0, 55, fill(cols[i])); text(c, str(i + 1), -520, 25, 70, WHITE, "bold")
            text(c, it, 60, 25, fit_size(it, "marker", 72, 980), INK, "marker")
        popin(c, S, at, 960, y, f)


def car_parked(c, S):
    line(c, 200, 840, 1720, 840, INK, 7)
    c.save(); c.translate(820, 760 + math.sin(S.t * 30) * 2); icon(c, "car", 0, 0, 2.3); c.restore()
    for i in range(4):
        k = (S.t * .8 + i * .25) % 1
        c.drawCircle(470 - k * 200, 820 - k * 80, 20 + k * 40, fill(GREY, 150 * (1 - k)))
    popin(c, S, S.wt("depósito", 1.2), 1450, 380, lambda: gauge(c, 0, 0, 150, .95, "GASOLINA", GREEN))
    def ps():
        rrect(c, -80, -80, 160, 160, 20, INK, 7, BLUE); text(c, "P", 0, 45, 130, WHITE, "bold")
        c.drawLine(0, 80, 0, 260, stroke(INK, 12))
    popin(c, S, S.wt("aparcado", S.dur - 1.2), 1500, 640, ps)


def emblem(c, x, y, s):
    c.save(); c.translate(x, y); c.scale(s, s)
    eye = skia.Path(); eye.moveTo(-180, 0); eye.quadTo(0, -170, 180, 0); eye.quadTo(0, 170, -180, 0); eye.close()
    c.drawCircle(0, 0, 210, fill((12, 22, 34)))
    c.drawPath(eye, stroke(TEAL, 18)); c.drawCircle(0, 0, 82, fill((20, 70, 78))); c.drawCircle(0, 0, 82, stroke(TEAL, 14))
    c.drawCircle(0, 0, 36, fill(AMBER)); c.drawCircle(-12, -12, 9, fill(WHITE))
    c.restore()


def subscribe(c, S):
    popin(c, S, 0, 600, 560, lambda: emblem(c, 0, 0, 1.3))
    popin(c, S, .3, 600, 920, lambda: text(c, "BIOLOGÍA OCULTA", 0, 0, 70, INK, "marker"))
    clicked = S.t > S.wt("suscríbete", 3.0) + .5
    def btn():
        rrect(c, -330, -90, 660, 180, 90, INK, 0, GREY if clicked else RED)
        text(c, "SUSCRITO" if clicked else "SUSCRÍBETE", 0, 28, 80, WHITE, "bold")
    popin(c, S, .5, 1330, 560, btn)
    popin(c, S, S.wt("suscríbete", 3.0) + .6, 1720, 560, lambda: icon(c, "bell", 0, 0, 1.4))
    k = eio(pr(S.t, S.wt("suscríbete", 3.0) - .4, .8))
    cx, cy = lerp(1700, 1360, k), lerp(950, 600, k)
    cur = poly([(cx, cy), (cx, cy + 70), (cx + 18, cy + 55), (cx + 32, cy + 85), (cx + 45, cy + 78), (cx + 30, cy + 50), (cx + 52, cy + 48)], True)
    c.drawPath(cur, fill(WHITE)); c.drawPath(cur, stroke(INK, 5))


# ═════════════════ RELOJ ═════════════════
def caveman_dawn(c, S):
    hills(c, S, pr(S.t, 0, 3))
    x = lerp(250, 1200, S.t / max(S.dur, 1))
    stick(c, x, 830, 1.2, "happy", "walk", S.t, hair="f")
    c.drawLine(x + 60, 640, x + 100, 560, stroke((120, 80, 40), 14))
    for i, tx in enumerate((300, 520)):
        tree_x = tx + 1300 * (i == 1)
        c.drawLine(tree_x, 760, tree_x, 640, stroke((120, 80, 40), 14)); c.drawCircle(tree_x, 600, 70, fill(GREEN)); c.drawCircle(tree_x, 600, 70, stroke(INK, 6))


def then_now(c, S):
    line(c, 960, 260, 960, 1000, INK, 6)
    text(c, "ANTES", 480, 300, 70, TEAL, "marker"); text(c, "AHORA", 1440, 300, 70, RED, "marker", a=255 * pr(S.t, S.wt("nadie", 2.5) - .3, .4))
    c.drawPath(smooth([(80, 900), (300, 870), (600, 920), (880, 880)]), stroke(BLUE, 30, 160))
    stick(c, lerp(150, 700, (S.t / max(S.dur, 1))), 860, 1.1, "happy", "walk", S.t, hair="f")
    if S.t > S.wt("nadie", 2.5) - .3:
        icon(c, "bed", 1440, 880, 1.1)
        stick(c, 1300, 900, 1.0, "neutral", "stand", S.t, arm=(math.pi * .75, -math.pi * .9))
        c.save(); c.translate(1440, 700); c.rotate(10); icon(c, "phone", 0, 0, .6); c.restore()
        c.drawCircle(1440, 700, 120, fill(BLUE, 40 + 20 * math.sin(S.t * 6)))


def circadian_clock(c, S):
    k = eo(pr(S.t, 0, .6))
    c.drawCircle(CX, 600, 230 * k, fill(WHITE)); c.drawCircle(CX, 600, 230 * k, stroke(INK, 9))
    ang = S.t * .9
    c.drawLine(CX, 600, CX + math.sin(ang) * 170, 600 - math.cos(ang) * 170, stroke(RED, 9))
    icon(c, "sun", CX, 460, .45, t=S.t); c.drawCircle(CX, 760, 34, fill(BLUE)); c.drawCircle(CX + 16, 750, 30, fill(WHITE))
    items = [("brain", 420, 380, "cerebro"), ("liver", 1500, 400, "hígado"), ("dumbbell", 1460, 860, "músculos")]
    for i, (nm, x, y, lb) in enumerate(items):
        at = S.wt(lb.split()[0], 1.5 + i * .7)
        on = pr(S.t, at, .4)
        if on <= 0:
            continue
        p = poly([(CX, 600), (x, y)]); pe = skia.Paint(stroke(TEAL, 6))
        pe.setPathEffect(skia.DashPathEffect.Make([20, 16], -S.t * 60)); c.drawPath(p, pe)
        c.drawCircle(x, y, 120, fill(WHITE)); c.drawCircle(x, y, 120, stroke(TEAL, 6))
        icon(c, nm, x, y - 10, .75 * back(on) if nm != "liver" else .55 * back(on), t=S.t)
        label(c, lb, x, y + 175, 52)


def three_icons(c, S):
    keys = ["luz", "comida", "movimiento"]
    for i, (nm, lb) in enumerate(zip(S.p["icons"], S.p["labels"])):
        at = S.wt(keys[i], .4 + i * .8)
        x = 420 + i * 540
        popin(c, S, at, x, 560, lambda nm=nm: (c.drawCircle(0, 0, 190, fill(WHITE)), c.drawCircle(0, 0, 190, stroke(INK, 7)), icon(c, nm, 0, -10 if nm != "walk" else -60, 1.5, t=S.t)))
        popin(c, S, at + .2, x, 870, lambda lb=lb: text(c, lb, 0, 0, 70, INK, "marker"))


def zoom_muscle(c, S):
    z = 1 + 1.5 * eio(pr(S.t, S.dur * .55, S.dur * .4))
    c.save(); c.translate(1100, 600); c.scale(z, z); c.translate(-1100, -600)
    arm = smooth([(500, 760), (700, 700), (900, 520), (1050, 470), (1200, 520), (1330, 640), (1450, 700), (1450, 800), (1200, 800), (900, 820), (700, 860)], True)
    c.drawPath(arm, fill((240, 200, 180))); c.drawPath(arm, stroke(INK, 9))
    for i in range(6):
        y = 560 + i * 40
        c.drawPath(smooth([(880, y + 40), (1100, y - 10), (1320, y + 50)]), stroke((200, 110, 100), 5))
    c.restore()
    c.drawCircle(1100, 600, 260, stroke(TEAL, 10, 255 * pr(S.t, .8, .4)))
    c.drawLine(1290, 790, 1450, 950, stroke(TEAL, 24, 255 * pr(S.t, .8, .4)))


# ═════════════════ GLUT-4 ═════════════════
def cell(c, S, doors=3, open_k=0.0, squeeze=0.0, x=960, y=700, w=1300, h=440, inflow=0.0, key_door=None):
    sx = 1 - .05 * squeeze
    c.save(); c.translate(x, y); c.scale(sx, 1 + .03 * squeeze)
    rrect(c, -w / 2, -h / 2, w, h, 110, (190, 80, 80), 12, (247, 214, 204), shadow=False)
    for i in range(5):
        yy = -h / 2 + 80 + i * 70
        c.drawPath(smooth([(-w / 2 + 120, yy), (0, yy + 18 * math.sin(S.t + i)), (w / 2 - 120, yy)]), stroke((220, 150, 140), 6))
    label(c, "célula muscular", 0, h / 2 - 30, 52, (150, 60, 60))
    xs = [(-w / 2 + w * (i + .5) / doors) for i in range(doors)]
    for i, dx in enumerate(xs):
        k = open_k if key_door is None or key_door == i else 0
        dy = -h / 2
        c.drawRect(skia.Rect.MakeXYWH(dx - 50, dy - 16, 100, 32), fill((247, 214, 204)))
        c.drawLine(dx - 50, dy - 18, dx - 50, dy + 18, stroke(INK, 7)); c.drawLine(dx + 50, dy - 18, dx + 50, dy + 18, stroke(INK, 7))
        c.save(); c.translate(dx - 50, dy); c.rotate(-80 * eo(k))
        rrect(c, 0, -14, 100, 28, 8, INK, 5, TEAL if k > .5 else (140, 200, 190), shadow=False); c.restore()
        if inflow > 0 and k > .6:
            for j in range(3):
                u = (S.t * .9 + j / 3 + i * .17) % 1
                hexagon(c, dx + math.sin(u * 7) * 10, lerp(dy - 160, dy + 150, u), 18, a=255 * min(1, (1 - u) * 3))
    c.restore()
    return [x + dx * sx for dx in xs]


def cell_doors(c, S):
    st = S.p["state"]
    if st == "closed":
        cell(c, S, 3, 0)
        hexes_outside(c, S, 9, 300, 1620, 360)
        popin(c, S, 1.2, 960, 300, lambda: text(c, "GLUT-4", 0, 0, 0.0001, INK))
        for i, dx in enumerate((743, 960, 1177)):
            k = pr(S.t, S.wt("puertas", 1.0) + i * .2, .4)
            if k > 0:
                arrow(c, dx + 120, 330, dx + 30, 455, TEAL, 6, eo(k), 18)
    elif st == "key":
        at = S.wt("llave", 1.4)
        k = eio(pr(S.t, at, 1.0))
        cell(c, S, 3, eo(pr(S.t, at + 1.0, .5)), key_door=1, inflow=1)
        hexes_outside(c, S, 7, 300, 1620, 330)
        kx, ky = lerp(300, 960, k), lerp(260, 440, k)
        c.save(); c.translate(kx, ky); c.rotate(-30 + 30 * k)
        c.drawCircle(0, 0, 40, stroke(AMBER, 14)); c.drawLine(40, 0, 160, 0, stroke(AMBER, 14))
        c.drawLine(130, 0, 130, 30, stroke(AMBER, 12)); c.drawLine(155, 0, 155, 25, stroke(AMBER, 12)); c.restore()
        popin(c, S, S.wt("insulina", 2.5), 1560, 270, lambda: text(c, "llave = INSULINA", 0, 0, 62, AMBER, "marker"))
    elif st == "contract":
        at = S.wt("contrae", 2.5)
        sq = (math.sin((S.t - at) * 7) * .5 + .5) if S.t > at else 0
        cell(c, S, 3, eo(pr(S.t, at + .5, .5)), squeeze=sq, inflow=1)
        hexes_outside(c, S, 7, 300, 1620, 330)
        if S.t > at:
            for sx in (-1, 1):
                bolt = poly([(960 + sx * 760, 560), (960 + sx * 720, 650), (960 + sx * 770, 650), (960 + sx * 720, 760)])
                c.drawPath(bolt, stroke(AMBER, 12))
            text(c, "¡contracción!", 960, 1010, 64, AMBER, "marker", a=255 * pr(S.t, at, .3))
    else:  # many
        cell(c, S, 6, eo(pr(S.t, .5, .8)), inflow=1)
        hexes_outside(c, S, 10, 260, 1660, 330)


def club(c, S):
    rrect(c, 300, 330, 1100, 600, 10, INK, 9, (60, 50, 90))
    text(c, "CÉLULA CLUB", 850, 420, 80, YEL, "marker")
    for i in range(4):
        c.drawCircle(450 + i * 270, 360, 14, fill([RED, YEL, TEAL, PINK][i], 150 + 100 * math.sin(S.t * 8 + i)))
    rrect(c, 760, 560, 180, 370, 8, INK, 8, (120, 90, 60), shadow=False)
    stick(c, 1050, 960, 1.15, "skeptic", "stand", S.t, arm=(math.pi * .55, -math.pi * .55))
    c.drawCircle(1050, 600, 0, fill(INK))
    popin(c, S, S.wt("portero", 1.0), 1240, 560, lambda: text(c, "PORTERO", 0, 0, 44, WHITE, "marker"))
    for i in range(5):
        hexagon(c, 560 - i * 95 + bob(S, 4, 4, i), 900, 30, rot=S.t * .4)
    popin(c, S, S.wt("invitación", 2.5), 1650, 560, lambda: (
        rrect(c, -210, -130, 420, 260, 20, INK, 7, WHITE),
        text(c, "SOLO CON", 0, -40, 50, INK, "marker"), text(c, "INVITACIÓN", 0, 20, 50, INK, "marker"), text(c, "(insulina)", 0, 85, 46, AMBER, "hand")))
    popin(c, S, S.wt("calle", 3.0), 300, 760, lambda: text(c, "😕", 0, 0, 1, INK))


def backdoor(c, S):
    rrect(c, 300, 330, 1100, 600, 10, INK, 9, (60, 50, 90))
    rrect(c, 760, 560, 180, 370, 8, INK, 8, (120, 90, 60), shadow=False)
    k = eo(pr(S.t, .4, .6))
    c.drawRect(skia.Rect.MakeXYWH(1300, 600, 160, 330), fill((150, 255, 190), 200 * k))
    c.save(); c.translate(1300, 600); c.rotate(-0); rrect(c, 0, 0, 160 * (1 - .8 * k), 330, 6, INK, 7, GREEN, shadow=False); c.restore()
    for i in range(6):
        u = (S.t * .5 + i / 6) % 1
        hexagon(c, lerp(1850, 1380, u), 880 - math.sin(u * math.pi) * 40, 26, a=255 * min(1, u * 4))
    popin(c, S, S.wt("llave", .3), 520, 470, lambda: (text(c, "SIN LLAVE", 0, 0, 56, WHITE, "marker"), ))
    popin(c, S, S.wt("portero", 1.0), 520, 560, lambda: (text(c, "SIN PORTERO", 0, 0, 56, WHITE, "marker"), ))


def evidence_card(c, S):
    def card():
        rrect(c, -680, -220, 1360, 440, 30, INK, 8, WHITE)
        for i in range(3):
            c.drawLine(-600, -110 + i * 50, -250, -110 + i * 50, stroke(GREY, 6))
        text(c, S.p["text"], 120, 20, fit_size(S.p["text"], "marker", 64, 900), INK, "marker")
        check(c, 520, 120, 50, pr(S.t, S.wt("funciona", 2.5) + .3, .5))
    popin(c, S, .2, 960, 600, card)
    popin(c, S, S.wt("internet", 1.0), 960, 300, lambda: (text(c, "NO ES UN MITO", 0, 0, 72, RED, "marker"),))


def vessel_idle(c, S):
    vessel(c, 330, 560)
    for i in range(12):
        u = (S.t * .12 + i / 12) % 1
        hexagon(c, lerp(-40, 1960, u), 445 + 50 * math.sin(u * 30 + i), 22, rot=S.t)
    icon(c, "bed", 820, 930, 1.1)
    stick(c, 520, 980, 1.0, "neutral", "stand", S.t, arm=(math.pi * .75, -math.pi * .9))
    c.save(); c.translate(600, 800); c.rotate(-15); icon(c, "phone", 0, 0, .45); c.restore()
    dots = "." * (1 + int(S.t * 2) % 3)
    text(c, "esperando" + dots, 1300, 860, 80, GREY, "hand", "l")


def vessel_walk(c, S):
    vessel(c, 300, 500)
    rrect(c, 900, 640, 900, 300, 60, (190, 80, 80), 10, (247, 214, 204))
    label(c, "MÚSCULO", 1350, 820, 70, (150, 60, 60))
    for i in range(10):
        u = (S.t * .45 + i / 10) % 1
        if u < .5:
            x, y = lerp(-40, 1200, u / .5), 400
        else:
            x, y = 1200 + (i % 3 - 1) * 180, lerp(400, 780, (u - .5) / .5)
        hexagon(c, x, y, 22, rot=u * 8)
    stick(c, 450, 990, 1.1, "happy", "walk", S.t)


def scale_compare(c, S):
    tilt = 12 * eio(pr(S.t, S.wt("abrir", 2.5) - .5, .8))
    c.drawPath(poly([(960, 960), (880, 1010), (1040, 1010)], True), fill(INK))
    c.drawLine(960, 960, 960, 430, stroke(INK, 12))
    c.save(); c.translate(960, 430); c.rotate(-tilt)
    c.drawLine(-520, 0, 520, 0, stroke(INK, 12))
    for sx, lb, nm in ((-1, S.p["left"], "dumbbell"), (1, S.p["right"], "walk")):
        c.save(); c.translate(sx * 520, 0); c.rotate(tilt)
        c.drawLine(-120, 200, 0, 0, stroke(INK, 5)); c.drawLine(120, 200, 0, 0, stroke(INK, 5))
        c.drawArc(skia.Rect.MakeXYWH(-160, 140, 320, 120), 0, 180, True, fill(WHITE)); c.drawArc(skia.Rect.MakeXYWH(-160, 140, 320, 120), 0, 180, True, stroke(INK, 7))
        icon(c, nm, 0, 140 if nm == "dumbbell" else 110, .8 if nm == "dumbbell" else 1.0, t=S.t)
        text(c, lb, 0, 340, 60, TEAL if sx > 0 else RED, "marker")
        c.restore()
    c.restore()
    xmark(c, 440, 520, 60, pr(S.t, S.wt("cansarte", 1.5), .5))
    check(c, 1480, 520, 50, pr(S.t, S.wt("abrir", 2.5), .5))


def doc_icon(c, x, y, s=1.0, a=255):
    c.save(); c.translate(x, y); c.scale(s, s)
    p = poly([(-60, -80), (30, -80), (60, -50), (60, 80), (-60, 80)], True)
    c.drawPath(p, fill(WHITE, a)); c.drawPath(p, stroke(INK, 6, a))
    for i in range(4):
        c.drawLine(-40, -40 + i * 30, 40, -40 + i * 30, stroke(GREY, 5, a))
    c.restore()


def study_intro(c, S):
    n = S.p["n"]
    for i in range(n):
        at = .3 + i * min(.35, (S.dur - 2) / n)
        x = 380 + i * 195
        popin(c, S, at, x, 560 + (i % 2) * 30, lambda: doc_icon(c, 0, 0, 1.3))
    popin(c, S, S.wt("siete", .3 + n * .3), 960, 360, lambda: text(c, f"{n} ESTUDIOS", 0, 0, 100, TEAL, "marker"))
    popin(c, S, S.wt("limerick", 2.0), 960, 860, lambda: text(c, "Universidad de Limerick · Irlanda", 0, 0, 62, INK, "hand"))


def glucose_curves(c, S):
    x, y, w, h = 280, 330, 1150, 540
    axes(c, x, y, w, h, eo(pr(S.t, 0, .5)), "tiempo después de comer", "azúcar en sangre")
    spike = lambda u: .2 + .7 * math.exp(-((u - .3) / .14) ** 2)
    calm = lambda u: .2 + .38 * math.exp(-((u - .3) / .17) ** 2)
    curve(c, x, y, w, h, spike, eo(pr(S.t, .4, 1.4)), RED, 10)
    text(c, "sentado", x + w * .42, y + h - h * .92, 54, RED, "marker", a=255 * pr(S.t, 1.5, .4))
    at = S.wt("bajaba", 2.4)
    curve(c, x, y, w, h, calm, eo(pr(S.t, at - .6, 1.4)), TEAL, 10)
    text(c, "paseo de 2–5 min", x + w * .62, y + h - h * .5, 54, TEAL, "marker", a=255 * pr(S.t, at, .4))
    arrow(c, x + w * .3, y + h - h * .86, x + w * .3, y + h - h * .62, GREEN, 8, eo(pr(S.t, at + .3, .5)))


def bars_17(c, S):
    base_y, x0 = 900, 420
    data = [("sentado", 1.0, RED, "", 0), ("de pie", .905, AMBER, "−9,5%", S.wt("durante", 1.5)), ("paseos", .83, TEAL, "−17%", S.wt("diecisiete", 3.0))]
    line(c, 300, base_y, 1620, base_y, INK, 7)
    for i, (lb, v, col, pct, at) in enumerate(data):
        k = eo(pr(S.t, .3 + i * .5, .7))
        x = x0 + i * 420; hh = 520 * v * k
        rrect(c, x, base_y - hh, 260, hh, 14, INK, 6, col, shadow=False)
        text(c, lb, x + 130, base_y + 70, 60, INK, "marker")
        if pct:
            popin(c, S, at, x + 130, base_y - 520 * v - 60, lambda pct=pct, col=col: text(c, pct, 0, 0, 90 if "17" in pct else 64, col, "bold"))
    text(c, "glucosa en sangre", 960, 300, 58, GREY, "hand")


def same_mechanism(c, S):
    for i, (nm, lb, at) in enumerate((("plate", "después de comer", .2), ("sun", "al despertar", S.wt("mañana", 2.5)))):
        x = 520 + i * 880
        popin(c, S, at, x, 560, lambda nm=nm, lb=lb: (
            c.drawCircle(0, 0, 200, fill(WHITE)), c.drawCircle(0, 0, 200, stroke(INK, 7)),
            icon(c, nm, -50, -30, 1.0, t=S.t), icon(c, "walk", 80, -30, 1.0, t=S.t),
            text(c, lb, 0, 280, 62, INK, "marker")))
    popin(c, S, S.wt("mismo", 3.0), 960, 560, lambda: text(c, "=", 0, 50, 200, TEAL, "marker"))


def comment_ask(c, S):
    if S.p.get("short"):
        popin(c, S, .1, 760, 560, lambda: icon(c, "comment", 0, 0, 2.6))
        popin(c, S, .6, 1350, 600, lambda: (rrect(c, -170, -120, 340, 240, 30, INK, 8, YEL), text(c, "DÍA 7", 0, 30, 100, INK, "marker")))
        return
    stick(c, 450, 990, 1.4, "calm", "stand", S.t, arm=(.3, -math.pi * .9))
    popin(c, S, S.wt("móvil", 2.4), 860, 480, lambda: icon(c, "phone", 0, 0, 1.4))
    popin(c, S, S.wt("café", 3.1), 1130, 500, lambda: icon(c, "coffee", 0, 0, 1.4))
    popin(c, S, S.wt("comentarios", S.dur - 1.6), 1420, 560, lambda: icon(c, "comment", 0, 0, 1.6))
    popin(c, S, .4, 960, 300, lambda: text(c, "¿Qué haces tú al despertar?", 0, 0, 70, INK, "marker"))


# ═════════════════ PARADOJA ═════════════════
def thirty_men(c, S):
    for i in range(30):
        r, col = divmod(i, 10)
        at = .2 + i * min(.08, (S.dur * .5) / 30)
        popin(c, S, at, 330 + col * 140, 520 + r * 190, lambda: stick(c, 0, 0, .5, "neutral", "stand", S.t))
    popin(c, S, S.wt("seis", 2.0), 1600, 330, lambda: (icon(c, "calendar", 0, 0, 1.2), text(c, "6", 0, 50, 90, INK, "bold")))
    popin(c, S, S.wt("bath", 1.0), 760, 330, lambda: text(c, "Bath + Birmingham · Reino Unido", 0, 0, 58, INK, "marker"))


def bike(c, x, y, s=1.0, t=0.0):
    c.save(); c.translate(x, y); c.scale(s, s)
    for sx in (-1, 1):
        c.drawCircle(sx * 90, 0, 60, stroke(INK, 7))
    c.drawPath(poly([(-90, 0), (-20, -90), (60, -90), (90, 0), (0, 0), (-20, -90)]), stroke(TEAL, 8))
    a = t * 6
    c.drawLine(0, 0, math.cos(a) * 30, math.sin(a) * 30, stroke(INK, 6))
    c.restore()


def two_groups(c, S):
    for i, (lab, order, at) in enumerate((("DESPUÉS de desayunar", ("plate", "bike"), .2), ("ANTES de desayunar", ("bike", "plate"), S.wt("otros", 2.0)))):
        y = 430 + i * 330
        def row(lab=lab, order=order):
            rrect(c, -760, -130, 1520, 260, 30, INK, 7, WHITE)
            text(c, lab, -380, 20, 58, [GREY, TEAL][i], "marker")
            for j, nm in enumerate(order):
                xx = 160 + j * 360
                if nm == "plate":
                    icon(c, "plate", xx, 0, .9)
                else:
                    bike(c, xx, 30, .9, S.t)
            arrow(c, 280, 0, 400, 0, INK, 7)
        popin(c, S, at, 960, y, row)


def counter_big(c, S):
    k = pr(S.t, .2, .6)
    c.save(); c.translate(CX, 600); s = back(k) * (1 + .03 * math.sin(S.t * 4)); c.scale(s, s)
    text(c, S.p["text"], 0, 90, 380, COL[S.p["color"]], "bold"); c.restore()
    popin(c, S, .7, CX, 880, lambda: text(c, S.p["label"], 0, 0, 90, INK, "marker"))
    for i in range(8):
        u = (S.t * .7 + i / 8) % 1
        x = 560 + i * 115
        c.drawPath(smooth([(x, 300 - u * 80), (x + 20, 260 - u * 120), (x, 220 - u * 150)]), stroke(AMBER, 6, 255 * (1 - u) * pr(S.t, .8, .3)))


def scale_equal(c, S):
    for i, (lb, col) in enumerate((("antes", TEAL), ("después", GREY))):
        x = 560 + i * 800
        popin(c, S, .2 + i * .3, x, 640, lambda lb=lb, col=col: (
            rrect(c, -230, -70, 460, 160, 30, INK, 8, WHITE),
            rrect(c, -110, -40, 220, 80, 12, INK, 5, (210, 235, 225), shadow=False),
            text(c, "= kg", 0, 20, 52, INK, "bold"), text(c, ("ejercicio " + lb), 0, 180, 54, col, "marker")))
    popin(c, S, 1.0, 960, 650, lambda: text(c, "=", 0, 40, 180, INK, "marker"))
    popin(c, S, S.wt("adelgazaron", 1.4), 960, 330, lambda: text(c, "MISMO PESO PERDIDO", 0, 0, 80, RED, "marker"))


def scale_vs_graph(c, S):
    popin(c, S, .1, 520, 600, lambda: (icon(c, "scale", 0, 0, 2.2), ))
    xmark(c, 520, 600, 150, pr(S.t, S.wt("báscula", 1.6), .5))
    def g():
        rrect(c, -330, -230, 660, 460, 30, INK, 7, WHITE)
        axes(c, -270, -170, 540, 330, 1)
        curve(c, -270, -170, 540, 330, lambda u: .45 + .05 * math.sin(u * 8), eo(pr(S.t, S.wt("energía", 3.0), 1.0)), GREEN, 9)
    popin(c, S, S.wt("maneja", 2.6), 1360, 600, g)
    popin(c, S, S.wt("maneja", 2.6) + .5, 1360, 920, lambda: text(c, "cómo usas la energía", 0, 0, 58, GREEN, "marker"))


def honest_note(c, S):
    doc(c, S, 360, 1000, 1.3, "point")
    def note():
        rrect(c, -480, -300, 960, 600, 20, INK, 8, YEL)
        text(c, "OJO", 0, -190, 90, RED, "marker")
        bike(c, -230, 0, 1.1, S.t); xmark(c, -230, -20, 120, pr(S.t, S.wt("paseaban", 2.5) - 2, .5) * 0)
        text(c, "pedaleaban", -230, 170, 54, INK, "hand")
        arrow(c, -40, 0, 80, 0, INK, 8, eo(pr(S.t, S.wt("suave", 4.0), .5)))
        popin(c, S, S.wt("suave", 4.0), 260, 20, lambda: icon(c, "walk", 0, 0, 1.6, t=S.t))
        text(c, "versión suave", 260, 170, 54, TEAL, "hand", a=255 * pr(S.t, S.wt("suave", 4.0), .4))
    popin(c, S, .2, 1150, 580, note)


def country_stat(c, S):
    if S.p["country"] == "es":
        popin(c, S, .1, 380, 420, lambda: (flag(c, -150, -100, 300, 200, "es"), text(c, "ESPAÑA", 0, 170, 64, INK, "marker")))
        at = S.wt("siete", 2.0)
        for i in range(7):
            col = RED if i == 3 else GREY
            popin(c, S, at - .6 + i * .08, 700 + i * 150, 760, lambda col=col: stick(c, 0, 0, .75, "neutral", "stand", S.t, col=col))
        popin(c, S, at + .2, 1160, 380, lambda: text(c, "1 de cada 7 adultos", 0, 0, 80, RED, "marker"))
    else:
        popin(c, S, .1, 380, 420, lambda: (flag(c, -150, -100, 300, 200, "mx"), text(c, "MÉXICO", 0, 170, 64, INK, "marker")))
        x, y, w, h = 700, 560, 1000, 120
        rrect(c, x, y, w, h, 20, INK, 7, WHITE, shadow=False)
        a1 = S.wt("dieciocho", 3.0); a2 = S.wt("veintidós", 5.0, after=a1)
        k1, k2 = eo(pr(S.t, a1, .7)), eo(pr(S.t, a2, .7))
        if k1 > 0:
            c.drawRect(skia.Rect.MakeXYWH(x + 4, y + 4, (w - 8) * .183 * k1, h - 8), fill(RED))
            text(c, "18% diabetes", x + 90, y + h + 80, 60, RED, "marker", "l", a=255 * k1)
        if k2 > 0:
            c.drawRect(skia.Rect.MakeXYWH(x + 4 + (w - 8) * .183, y + 4, (w - 8) * .221 * k2, h - 8), fill(AMBER))
            text(c, "+22% prediabetes", x + 90, y + h + 160, 60, AMBER, "marker", "l", a=255 * k2)
        text(c, "adultos", x + w / 2, y - 40, 52, GREY, "hand")


def four_in_ten(c, S):
    for i in range(10):
        col = RED if i < 4 else GREY
        popin(c, S, .1 + i * .07, 330 + i * 140, 820, lambda col=col: stick(c, 0, 0, .9, "neutral", "stand", S.t, col=col))
    popin(c, S, .5, 960, 380, lambda: text(c, "4 de cada 10", 0, 0, 130, RED, "marker"))
    at = S.wt("sin", 1.8)
    for i in range(4):
        k = pr(S.t, at + i * .1, .4)
        if k > 0:
            text(c, "?", 330 + i * 140, 450 + bob(S, 10, 4, i) + 60, 90 * back(k), AMBER, "marker")


def like(c, S):
    k = pr(S.t, S.wt("gusta", 1.8) + .3, .3)
    c.save(); c.translate(CX, 560); s = back(pr(S.t, .1, .5)) * (1 + .15 * math.sin(min(k, 1) * math.pi)); c.scale(s * 2.4, s * 2.4)
    icon(c, "like", 0, 0, 1.0)
    if k > 0:
        c.drawCircle(-60, 30, 0, fill(BLUE))
    c.restore()
    if k > 0:
        for i in range(8):
            ang = i / 8 * 2 * math.pi; r = 260 + 120 * eo(k)
            c.drawCircle(CX + math.cos(ang) * r, 560 + math.sin(ang) * r, 14 * (1 - k * .5), fill([RED, AMBER, TEAL][i % 3]))
    popin(c, S, .4, CX, 960, lambda: text(c, "ME GUSTA", 0, 0, 80, BLUE, "marker"))


# ═════════════════ ERRORES ═════════════════
def three_signs(c, S):
    for i in range(3):
        popin(c, S, .2 + i * .35, 480 + i * 480, 600, lambda i=i: (icon(c, "warning", 0, 0, 2.2), text(c, str(i + 1), 0, 250, 110, RED, "marker")))


def treadmill(c, x, y, t):
    c.drawPath(poly([(x - 260, y), (x + 240, y), (x + 280, y - 40)]), stroke(INK, 10))
    for i in range(8):
        xx = x - 250 + ((i * 64 - t * 300) % 512)
        c.drawLine(xx, y - 6, xx + 20, y - 6, stroke(GREY, 5))
    c.drawLine(x + 200, y, x + 200, y - 330, stroke(INK, 10)); c.drawLine(x + 200, y - 330, x + 90, y - 330, stroke(INK, 10))


def mistake_run(c, S):
    treadmill(c, 760, 920, S.t)
    stick(c, 740, 905, 1.3, "tired", "run", S.t, sweat=True, lean=8)
    popin(c, S, S.wt("cuestas", 2.5), 1450, 450, lambda: text(c, "¡PRISA!", 0, 0, 90, RED, "marker"))
    xmark(c, 1450, 720, 130, pr(S.t, S.wt("prisa", 3.4) + .2, .5))
    text(c, "ERROR 1", 960, 300, 80, RED, "marker", a=255 * pr(S.t, 0, .3))


def cortisol_gauge(c, S):
    at = S.wt("intenso", 1.2)
    lv = lerp(.2, .92, eo(pr(S.t, at, 1.2))) + .02 * math.sin(S.t * 9)
    gauge(c, 960, 720, 330, lv, "CORTISOL", RED)
    text(c, "suave", 560, 760, 54, GREEN, "marker"); text(c, "intenso", 1360, 760, 54, RED, "marker")
    popin(c, S, S.wt("calma", 3.5), 520, 360, lambda: text(c, "calma ✓", 0, 0, 1, GREEN))
    popin(c, S, S.wt("calma", 3.5), 520, 360, lambda: (rrect(c, -170, -70, 340, 140, 40, INK, 6, WHITE), text(c, "CALMA", 0, 25, 70, GREEN, "marker")))
    popin(c, S, S.wt("alarma", 4.5), 1400, 360, lambda: (rrect(c, -170, -70, 340, 140, 40, INK, 6, WHITE), text(c, "ALARMA", 0, 25, 70, RED, "marker")))
    xmark(c, 1400, 360, 90, pr(S.t, S.wt("alarma", 4.5) + .4, .4))


def mistake_coffee(c, S):
    text(c, "ERROR 2", 960, 300, 80, RED, "marker", a=255 * pr(S.t, 0, .3))
    k = back(pr(S.t, S.wt("gigante", .8), .7))
    c.save(); c.translate(1150, 640); c.scale(3.2 * k, 3.2 * k); icon(c, "coffee", 0, 0, 1.0); c.restore()
    stick(c, 560, 980, 1.2, "wow", "stand", S.t, sweat=S.t > S.wt("cortisol", 3) )
    at = S.wt("leña", S.dur - 2)
    if S.t > S.wt("cortisol", 3.0):
        cl = smooth([(400, 560), (430, 490), (520, 470), (600, 480), (680, 500), (700, 560), (620, 590), (480, 590)], True)
        c.save(); c.translate(bob(S, 6, 3), 0); c.drawPath(cl, fill((90, 98, 110))); c.drawPath(cl, stroke(INK, 6)); c.restore()
        if (S.t * 3) % 1 < .4:
            c.drawPath(poly([(560, 590), (530, 650), (565, 650), (535, 710)]), stroke(AMBER, 9))
    popin(c, S, at, 1500, 380, lambda: (text(c, "🔥", 0, 0, 1), text(c, "LEÑA AL FUEGO", 0, 0, 64, RED, "marker")))


def mistake_scale(c, S):
    text(c, "ERROR 3", 960, 300, 80, RED, "marker", a=255 * pr(S.t, 0, .3))
    icon(c, "scale", 760, 900, 1.8)
    stick(c, 760, 880, 1.2, "wow", "stand", S.t)
    popin(c, S, S.wt("milagro", 3.0), 1350, 520, lambda: (rrect(c, -260, -90, 520, 180, 60, INK, 7, WHITE), text(c, "¿MILAGRO?", 0, 28, 80, AMBER, "marker")))
    xmark(c, 1350, 520, 120, pr(S.t, S.wt("milagro", 3.0) + .5, .5))
    popin(c, S, S.wt("energía", S.dur - 1.5), 1350, 800, lambda: text(c, "≠ peso · = energía", 0, 0, 62, GREEN, "marker"))


def doctor_warning(c, S):
    doc(c, S, 430, 1000, 1.6, "point")
    popin(c, S, .3, 960, 380, lambda: icon(c, "warning", 0, 0, 1.6))
    def card():
        rrect(c, -560, -150, 1120, 300, 30, INK, 8, WHITE)
        text(c, "¿Tomas insulina u otros fármacos", 0, -40, 54, INK, "marker")
        text(c, "para el azúcar? Consulta a tu médico.", 0, 40, 54, RED, "marker")
    popin(c, S, S.wt("médico", 3.0) - .6, 1180, 760, card)


# ═════════════════ CÓMO ═════════════════
def talk_test(c, S):
    x = 520 + 40 * math.sin(S.t * .5)
    stick(c, x, 960, 1.15, "happy", "walk", S.t); stick(c, x + 200, 960, 1.15, "happy", "walk", S.t + .3, hair="f")
    popin(c, S, .4, x + 100, 430, lambda: (rrect(c, -240, -80, 480, 160, 60, INK, 6, WHITE), text(c, "…y entonces…", 0, 20, 58, INK, "hand")))
    check(c, x + 100, 300, 50, pr(S.t, S.wt("jadear", 2.0), .5))
    at = S.wt("podrías", 4.0)
    if S.t > at - .3:
        stick(c, 1450, 960, 1.2, "tired", "run", S.t, sweat=True, lean=10)
        popin(c, S, at, 1450, 480, lambda: text(c, "¡uf, uf!", 0, 0, 80, RED, "marker"))
        xmark(c, 1450, 650, 110, pr(S.t, S.wt("rápido", at + 2) + .1, .5))


def light_walk(c, S):
    hills(c, S, pr(S.t, 0, 2))
    stick(c, lerp(400, 900, S.t / max(1, S.dur)), 820, 1.1, "happy", "walk", S.t)
    popin(c, S, S.wt("reloj", 3.0), 400, 380, lambda: clock(c, 0, 0, 110, 7 + S.t / 100))


def sunrise_cities(c, S):
    for i, (city, tm, h, at) in enumerate((("Madrid", "8:35", .3, .2), ("Ciudad de México", "7:05", .7, S.wt("ciudad", 2.5)))):
        x = 520 + i * 880
        def panel(city=city, tm=tm, h=h):
            rrect(c, -380, -260, 760, 420, 30, INK, 7, (220, 236, 250))
            c.save(); c.clipRect(skia.Rect.MakeXYWH(-380, -260, 760, 420))
            icon(c, "sun", 0, 120 - 200 * h, .9, t=S.t)
            c.drawPath(smooth([(-400, 120), (-150, 80), (100, 110), (400, 70), (400, 200), (-400, 200)], True), fill((205, 232, 196)))
            c.restore()
            text(c, city, 0, -190, 56, INK, "marker"); text(c, tm, 0, 250, 90, AMBER, "bold")
        popin(c, S, at, x, 470, panel)
    at = S.wt("casa", S.dur - 2.5)
    if S.t > at - .3:
        def house():
            rrect(c, -330, -40, 660, 260, 10, INK, 7, WHITE)
            c.drawPath(poly([(-370, -40), (0, -220), (370, -40)], True), fill(RED)); c.drawPath(poly([(-370, -40), (0, -220), (370, -40)], True), stroke(INK, 7))
            stick(c, -150 + 300 * ((S.t * .3) % 1), 210, .7, "happy", "walk", S.t)
        popin(c, S, at, 960, 760, house)


def calendar7(c, S):
    days = ["L", "M", "X", "J", "V", "S", "D"]
    text(c, "7 DÍAS · 10 MINUTOS", 960, 300, 80, TEAL, "marker", a=255 * pr(S.t, 0, .4))
    step = max(.25, (S.dur - 1.5) / 8)
    for i, d in enumerate(days):
        x = 300 + i * 220
        rrect(c, x - 90, 430, 180, 220, 20, INK, 7, WHITE)
        c.drawRect(skia.Rect.MakeXYWH(x - 90, 430, 180, 50), fill(RED)); text(c, d, x, 470, 40, WHITE, "bold")
        check(c, x, 560, 45, pr(S.t, .6 + i * step, .35))
    if S.p.get("streak"):
        popin(c, S, .6 + 7 * step, 960, 830, lambda: text(c, "repetición > heroicidad", 0, 0, 72, AMBER, "marker"))
    else:
        popin(c, S, S.wt("once", S.dur - 1.5), 960, 830, lambda: (clock(c, -260, -20, 80, 11), text(c, "¿cómo te sientes?", 120, 0, 66, INK, "marker")))


def recap(c, S):
    n = S.p["n"]
    items = ["Combustible en la sangre + insulina baja", "Una puerta trasera: moverte", "No son calorías: es cómo usas la energía"]
    if n == 0:
        popin(c, S, .1, 960, 560, lambda: text(c, "3 COSAS", 0, 0, 200, TEAL, "marker"))
        return
    for i in range(n):
        y = 330 + i * 220
        cur = i == n - 1
        def card(i=i, cur=cur):
            rrect(c, -760, -85, 1520, 170, 30, INK, 7, YEL if cur else WHITE)
            c.drawCircle(-670, 0, 52, fill(TEAL)); text(c, str(i + 1), -670, 24, 66, WHITE, "bold")
            text(c, items[i], 60, 22, fit_size(items[i], "marker", 64, 1300), INK, "marker")
        if cur:
            popin(c, S, .1, 960, y, card)
        else:
            c.save(); c.translate(960, y); card(); c.restore()


def nap_fact(c, S):
    at = S.wt("siesta", 2.5)
    icon(c, "bed", 600, 820, 1.4)
    c.save(); c.translate(470, 770); c.rotate(-90); stick(c, 0, 0, .8, "sleep" if S.t < S.wt("despertar", 4.0) else "happy", "stand", S.t, hair="f"); c.restore()
    clock(c, 600, 420, 110, 19.0)
    text(c, "siesta por la tarde", 600, 620, 54, INK, "marker", a=255 * pr(S.t, at, .4))
    a2 = S.wt("subió", 5.0)
    def chart():
        rrect(c, -380, -260, 760, 520, 30, INK, 7, WHITE)
        text(c, "cortisol", 0, -190, 56, INK, "marker")
        arrow(c, -150, 150, -150, -120, GREEN, 14, eo(pr(S.t, a2 - .5, .6)))
        text(c, "mañana", -150, 220, 46, GREEN, "hand")
        arrow(c, 150, -120, 150, 150, RED, 14, eo(pr(S.t, a2 + .5, .6)))
        text(c, "siesta", 150, 220, 46, RED, "hand")
    popin(c, S, a2 - .8, 1350, 560, chart)


def next_video(c, S):
    popin(c, S, .1, 520, 560, lambda: (
        stick(c, 0, 380, 1.3, "wow", "stand", S.t),
        c.drawCircle(0, 170, 95, fill(AMBER, 200)), c.drawCircle(0, 170, 95, stroke(INK, 7))))
    popin(c, S, .5, 520, 290, lambda: text(c, "?", 0, 0, 200, RED, "marker"))
    popin(c, S, .8, 1300, 380, lambda: text(c, "PRÓXIMO VÍDEO", 0, 0, 90, TEAL, "marker"))
    popin(c, S, 1.2, 1300, 520, lambda: text(c, "¿Por qué la barriga es lo último?", 0, 0, 60, INK, "hand"))
    at = S.wt("suscríbete", S.dur - 3.5)
    clicked = S.t > at + .6
    popin(c, S, at, 1300, 760, lambda: (rrect(c, -300, -80, 600, 160, 80, INK, 0, GREY if clicked else RED), text(c, "SUSCRITO" if clicked else "SUSCRÍBETE", 0, 26, 72, WHITE, "bold")))
    popin(c, S, S.dur - 2.6, 1300, 960, lambda: (emblem(c, -260, -10, .3), text(c, "BIOLOGÍA OCULTA", 40, 10, 54, INK, "marker")))


SCENES = {k: v for k, v in globals().items() if callable(v) and not k.startswith("_")}
