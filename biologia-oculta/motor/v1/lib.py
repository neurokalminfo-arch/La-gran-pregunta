"""Primitivas de dibujo estilo pizarra (skia): figuras de palo, iconos, gráficas, textos con rotulador."""
import math, random
import numpy as np
import skia

W, H, FPS = 1920, 1080, 30
import os
FD = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "fonts") + os.sep
TF = {
    "marker": skia.Typeface.MakeFromFile(FD + "PermanentMarker-Regular.ttf"),
    "hand": skia.Typeface.MakeFromFile(FD + "PatrickHand-Regular.ttf"),
    "bold": skia.Typeface.MakeFromFile(FD + "Poppins-Bold.ttf"),
    "reg": skia.Typeface.MakeFromFile(FD + "Poppins-Regular.ttf"),
    "cap": skia.Typeface.MakeFromFile(FD + "Anton-Regular.ttf"),
}
INK = (22, 24, 30); PAPER = (255, 255, 255); TEAL = (20, 160, 146); AMBER = (240, 158, 10)
RED = (226, 76, 52); GREEN = (52, 170, 102); YEL = (255, 222, 89); BLUE = (52, 120, 210)
GREY = (150, 156, 165); SKIN = (250, 247, 240); WHITE = (255, 255, 255); PINK = (240, 140, 150)
COL = {"red": RED, "teal": TEAL, "amber": AMBER, "green": GREEN, "blue": BLUE, "ink": INK}


def C(c, a=255):
    return skia.Color(c[0], c[1], c[2], int(max(0, min(255, a))))


def stroke(c=INK, w=6, a=255, trim=None):
    p = skia.Paint(AntiAlias=True, Color=C(c, a), Style=skia.Paint.kStroke_Style, StrokeWidth=w,
                   StrokeCap=skia.Paint.kRound_Cap, StrokeJoin=skia.Paint.kRound_Join)
    if trim is not None and trim < 1:
        pe = skia.TrimPathEffect.Make(0, min(1.0, max(0.001, float(trim))))
        if pe is not None:
            p.setPathEffect(pe)
    return p


def fill(c=INK, a=255):
    return skia.Paint(AntiAlias=True, Color=C(c, a), Style=skia.Paint.kFill_Style)


# ── easing ──
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def pr(t, a, d=0.4):
    return clamp((t - a) / d) if d > 0 else (1.0 if t >= a else 0.0)


def eo(x):  # ease out cubic
    x = clamp(x); return 1 - (1 - x) ** 3


def eio(x):
    x = clamp(x); return 4 * x ** 3 if x < .5 else 1 - (-2 * x + 2) ** 3 / 2


def back(x):  # ease out back
    x = clamp(x); c1 = 1.70158; c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2


def lerp(a, b, x):
    return a + (b - a) * x


# ── caminos ──
def poly(pts, closed=False, jitter=0, seed=1):
    rnd = random.Random(seed)
    p = skia.Path()
    for i, (x, y) in enumerate(pts):
        if jitter:
            x += rnd.uniform(-jitter, jitter); y += rnd.uniform(-jitter, jitter)
        (p.moveTo if i == 0 else p.lineTo)(x, y)
    if closed:
        p.close()
    return p


def smooth(pts, closed=False):
    """Catmull-Rom → Bézier."""
    p = skia.Path()
    n = len(pts)
    if n < 2:
        return p
    P = pts + ([pts[0], pts[1]] if closed else [])
    p.moveTo(*P[0])
    rng = range(len(P) - 1) if not closed else range(n)
    for i in rng:
        p0 = P[i - 1] if i > 0 else (P[-2] if closed else P[0])
        p1, p2 = P[i], P[(i + 1) % len(P)]
        p3 = P[(i + 2) % len(P)] if (i + 2 < len(P) or closed) else p2
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        p.cubicTo(*c1, *c2, *p2)
    if closed:
        p.close()
    return p


def line(c, x0, y0, x1, y1, col=INK, w=6, prog=1.0, a=255):
    if prog <= 0:
        return
    c.drawLine(x0, y0, lerp(x0, x1, prog), lerp(y0, y1, prog), stroke(col, w, a))


def arrow(c, x0, y0, x1, y1, col=INK, w=7, prog=1.0, head=26, a=255):
    if prog <= 0:
        return
    xe, ye = lerp(x0, x1, prog), lerp(y0, y1, prog)
    c.drawLine(x0, y0, xe, ye, stroke(col, w, a))
    ang = math.atan2(y1 - y0, x1 - x0)
    for s in (-1, 1):
        c.drawLine(xe, ye, xe - head * math.cos(ang + s * .5), ye - head * math.sin(ang + s * .5), stroke(col, w, a))


def circle(c, x, y, r, col=INK, w=6, fillc=None, prog=1.0, a=255):
    if fillc is not None:
        c.drawCircle(x, y, r, fill(fillc, a * (1 if prog >= 1 else prog)))
    if prog >= 1:
        c.drawCircle(x, y, r, stroke(col, w, a))
    elif prog > 0:
        p = skia.Path(); p.addCircle(x, y, r)
        c.drawPath(p, stroke(col, w, a, trim=prog))


def rrect(c, x, y, w, h, r=24, col=INK, sw=6, fillc=None, a=255, shadow=True):
    rect = skia.Rect.MakeXYWH(x, y, w, h)
    if shadow and fillc is not None:
        c.drawRoundRect(skia.Rect.MakeXYWH(x + 8, y + 10, w, h), r, r, fill(INK, a * .12))
    if fillc is not None:
        c.drawRoundRect(rect, r, r, fill(fillc, a))
    if sw:
        c.drawRoundRect(rect, r, r, stroke(col, sw, a))


# ── texto ──
def font(kind, size):
    f = skia.Font(TF[kind], size)
    f.setEdging(skia.Font.Edging.kAntiAlias)
    return f


def tw(s, kind, size):
    return font(kind, size).measureText(s)


def text(c, s, x, y, size=60, col=INK, kind="hand", align="c", a=255):
    f = font(kind, size)
    w = f.measureText(s)
    dx = {"c": -w / 2, "l": 0, "r": -w}[align]
    c.drawString(s, x + dx, y, f, fill(col, a))
    return w


def fit_size(s, kind, size, maxw):
    w = tw(s, kind, size)
    return size if w <= maxw else size * maxw / w


def marker_text(c, s, x, y, size=84, col=INK, hl=YEL, prog=1.0, kind="marker", a=255):
    """Texto con subrayado de rotulador amarillo que barre de izquierda a derecha."""
    size = fit_size(s, kind, size, 1700)
    w = tw(s, kind, size)
    if hl is not None and prog > 0:
        hp = eo(pr(prog, 0, .6))
        rect = skia.Rect.MakeXYWH(x - w / 2 - 18, y - size * .62, (w + 36) * hp, size * .78)
        c.drawRoundRect(rect, 10, 10, fill(hl, a * .85))
    tp = eo(pr(prog, .15, .5))
    if tp > 0:
        c.save(); c.translate(x, y); s_ = lerp(.85, 1, back(tp)); c.scale(s_, s_)
        text(c, s, 0, 0, size, col, kind, "c", a * tp)
        c.restore()


# ── figuras de palo ──
def stick(c, x, y, s=1.0, mood="happy", pose="stand", t=0.0, doctor=False, col=INK, talk=False,
          arm=None, legs=None, a=255, lean=0, hair=None, sweat=False, glasses=False):
    """(x, y) = pies. Altura ≈ 330*s."""
    w = 7 * s
    P = lambda cc=col, ww=w: stroke(cc, ww, a)
    c.save(); c.translate(x, y); c.rotate(lean)
    hip = (0, -150 * s); neck = (0, -255 * s); head = (0, -295 * s); hr = 40 * s
    ph = t * 2 * math.pi * (1.6 if pose == "walk" else 2.6 if pose == "run" else 0)
    sw = {"walk": .45, "run": .85}.get(pose, 0)
    # piernas
    if legs is None:
        la, lb = math.sin(ph) * sw, -math.sin(ph) * sw
    else:
        la, lb = legs
    for ang in (la, lb):
        kx, ky = hip[0] + math.sin(ang) * 80 * s, hip[1] + math.cos(ang) * 80 * s
        fx, fy = kx + math.sin(ang * .6 - .15 * (pose == "run")) * 75 * s, ky + math.cos(ang * .6) * 75 * s
        c.drawPath(poly([hip, (kx, ky), (fx, fy)]), P())
    # cuerpo / bata
    if doctor:
        coat = poly([(-30 * s, -245 * s), (-48 * s, -110 * s), (48 * s, -110 * s), (30 * s, -245 * s)], True)
        c.drawPath(coat, fill(WHITE, a)); c.drawPath(coat, P(INK, 5 * s))
        c.drawLine(0, -245 * s, 0, -110 * s, P(INK, 4 * s))
        st = skia.Path(); st.moveTo(-18 * s, -245 * s); st.cubicTo(-30 * s, -180 * s, 25 * s, -170 * s, 18 * s, -245 * s)
        c.drawPath(st, P(TEAL, 5 * s)); c.drawCircle(4 * s, -186 * s, 8 * s, fill(TEAL, a))
    else:
        c.drawLine(*neck, *hip, P())
    # brazos
    if arm is None:
        if pose in ("walk", "run"):
            arm = (math.pi - math.sin(ph) * sw * 1.1, math.pi + math.sin(ph) * sw * 1.1)
        elif pose == "point":
            arm = (.75 + .1 * math.sin(t * 4), -math.pi * .9)
        elif pose == "pointl":
            arm = (math.pi * .9, -.75 - .1 * math.sin(t * 4))
        elif pose == "cheer":
            arm = (.35 + .12 * math.sin(t * 6), -.35 - .12 * math.sin(t * 6))
        elif pose == "shrug":
            arm = (math.pi * .6, -math.pi * .6)
        else:
            arm = (math.pi * .92, -math.pi * .92)
    sh = (0, -235 * s)
    for i, ang in enumerate(arm):
        ex, ey = sh[0] + math.sin(ang) * 65 * s, sh[1] - math.cos(ang) * 65 * s
        hx, hy = ex + math.sin(ang) * 60 * s, ey - math.cos(ang) * 60 * s
        c.drawPath(poly([sh, (ex, ey), (hx, hy)]), P())
    # cabeza
    c.drawCircle(*head, hr, fill(SKIN, a)); c.drawCircle(*head, hr, P())
    if hair == "f":
        hp = skia.Path(); hp.moveTo(-hr, head[1]); hp.cubicTo(-hr, head[1] - hr * 1.5, hr, head[1] - hr * 1.5, hr, head[1])
        hp.lineTo(hr * 1.1, head[1] + hr * .9); c.drawPath(hp, P(INK, 6 * s))
    ex = 14 * s; ey = head[1] - 6 * s
    if mood == "sleep":
        for sx in (-1, 1):
            c.drawLine(sx * ex - 7 * s, ey, sx * ex + 7 * s, ey, P(INK, 4 * s))
    else:
        for sx in (-1, 1):
            c.drawCircle(sx * ex, ey, 4.5 * s, fill(INK, a))
    if glasses or doctor:
        for sx in (-1, 1):
            c.drawCircle(sx * ex, ey, 11 * s, P(INK, 3 * s))
        c.drawLine(-ex + 11 * s, ey, ex - 11 * s, ey, P(INK, 3 * s))
    if mood == "tired":
        for sx in (-1, 1):
            c.drawArc(skia.Rect.MakeXYWH(sx * ex - 9 * s, ey + 3 * s, 18 * s, 10 * s), 0, 180, False, P(GREY, 3 * s))
    my = head[1] + 18 * s
    if talk:
        o = 6 * s * (0.5 + 0.5 * abs(math.sin(t * 17)))
        c.drawOval(skia.Rect.MakeXYWH(-9 * s, my - o / 2, 18 * s, o), fill(INK, a))
    elif mood in ("happy", "calm"):
        c.drawArc(skia.Rect.MakeXYWH(-14 * s, my - 12 * s, 28 * s, 18 * s), 20, 140, False, P(INK, 4 * s))
    elif mood in ("tired", "sad"):
        c.drawArc(skia.Rect.MakeXYWH(-13 * s, my, 26 * s, 16 * s), 200, 140, False, P(INK, 4 * s))
    elif mood == "wow":
        c.drawCircle(0, my + 2 * s, 7 * s, P(INK, 4 * s))
    elif mood == "skeptic":
        c.drawLine(-12 * s, my + 4 * s, 12 * s, my - 2 * s, P(INK, 4 * s))
        c.drawLine(4 * s, ey - 20 * s, 22 * s, ey - 26 * s, P(INK, 4 * s))
    else:
        c.drawLine(-10 * s, my, 10 * s, my, P(INK, 4 * s))
    if sweat:
        for i in range(2):
            yy = head[1] - 10 * s + ((t * 60 + i * 25) % 50) * s
            c.drawCircle(hr + 10 * s + i * 12 * s, yy, 6 * s, fill(BLUE, a * .8))
    c.restore()


def speaking(words, t):
    return any(w[1] - .05 <= t <= w[2] for w in words)


# ── iconos ──
def hexagon(c, x, y, r=16, col=AMBER, a=255, rot=0):
    pts = [(x + r * math.cos(rot + math.pi / 3 * i), y + r * math.sin(rot + math.pi / 3 * i)) for i in range(6)]
    p = poly(pts, True)
    c.drawPath(p, fill(YEL, a)); c.drawPath(p, stroke(col, max(2, r * .22), a))


def clock(c, x, y, r, hour, col=INK, a=255, ring=False):
    circle(c, x, y, r, col, r * .06, fillc=WHITE, a=a)
    for i in range(12):
        ang = i * math.pi / 6
        c.drawLine(x + math.sin(ang) * r * .82, y - math.cos(ang) * r * .82, x + math.sin(ang) * r * .92,
                   y - math.cos(ang) * r * .92, stroke(col, r * .035, a))
    hh = (hour % 12) / 12 * 2 * math.pi; mm = (hour % 1) * 2 * math.pi
    c.drawLine(x, y, x + math.sin(hh) * r * .5, y - math.cos(hh) * r * .5, stroke(col, r * .07, a))
    c.drawLine(x, y, x + math.sin(mm) * r * .75, y - math.cos(mm) * r * .75, stroke(RED, r * .045, a))
    c.drawCircle(x, y, r * .06, fill(col, a))


def icon(c, name, x, y, s=1.0, a=255, t=0.0):
    c.save(); c.translate(x, y); c.scale(s, s)
    K = lambda w=6, col=INK: stroke(col, w, a)
    if name == "plate":
        c.drawCircle(0, 0, 70, fill(WHITE, a)); c.drawCircle(0, 0, 70, K()); c.drawCircle(0, 0, 45, K(4, GREY))
        c.drawLine(-100, -50, -100, 60, K(5)); [c.drawLine(-110 + i * 10, -50, -110 + i * 10, -20, K(3)) for i in range(3)]
        c.drawLine(100, -50, 100, 60, K(5)); c.drawOval(skia.Rect.MakeXYWH(92, -55, 16, 40), K(4))
        c.drawCircle(-12, -8, 16, fill(GREEN, a)); c.drawCircle(15, 10, 14, fill(AMBER, a))
    elif name == "pills":
        rrect(c, -45, -50, 90, 110, 14, INK, 6, WHITE, a, False); rrect(c, -52, -78, 104, 30, 8, INK, 6, RED, a, False)
        c.drawLine(-30, 0, 30, 0, K(4, GREY)); c.drawLine(-30, 20, 20, 20, K(4, GREY))
    elif name == "ice":
        rrect(c, -80, -10, 160, 70, 12, INK, 6, (200, 230, 245), a, False)
        for i, (xx, yy) in enumerate([(-40, -30), (5, -40), (45, -25)]):
            c.save(); c.translate(xx, yy); c.rotate(15 * (i - 1))
            rrect(c, -22, -22, 44, 44, 6, BLUE, 4, (225, 242, 252), a, False); c.restore()
    elif name == "dumbbell":
        c.drawLine(-70, 0, 70, 0, K(10))
        for sx in (-1, 1):
            rrect(c, sx * 70 - 18, -45, 36, 90, 8, INK, 6, GREY, a, False)
            rrect(c, sx * 98 - 10, -30, 20, 60, 6, INK, 5, GREY, a, False)
    elif name == "sun":
        c.drawCircle(0, 0, 50, fill(YEL, a)); c.drawCircle(0, 0, 50, K(6, AMBER))
        for i in range(10):
            ang = i * math.pi / 5 + t * .4
            c.drawLine(math.cos(ang) * 68, math.sin(ang) * 68, math.cos(ang) * 92, math.sin(ang) * 92, K(6, AMBER))
    elif name == "walk":
        stick(c, 0, 110, .62, "happy", "walk", t, a=a)
    elif name == "cookie":
        c.drawCircle(0, 0, 60, fill((214, 160, 90), a)); c.drawCircle(0, 0, 60, K(6, (150, 95, 40)))
        for xx, yy in [(-25, -20), (15, -30), (20, 15), (-15, 25), (0, 0)]:
            c.drawCircle(xx, yy, 7, fill((90, 55, 30), a))
    elif name == "coffee":
        rrect(c, -50, -50, 100, 110, 16, INK, 6, WHITE, a, False)
        c.drawArc(skia.Rect.MakeXYWH(35, -25, 50, 50), -90, 180, False, K(8))
        c.drawRect(skia.Rect.MakeXYWH(-42, -42, 84, 18), fill((110, 70, 40), a))
        for i in (-20, 10):
            st = skia.Path(); st.moveTo(i, -65); st.cubicTo(i - 15, -85, i + 15, -95, i, -115); c.drawPath(st, K(4, GREY))
    elif name == "phone":
        rrect(c, -40, -75, 80, 150, 14, INK, 6, (40, 50, 64), a, False)
        rrect(c, -30, -60, 60, 115, 6, INK, 0, (120, 200, 240), a, False)
    elif name == "scale":
        rrect(c, -90, -25, 180, 60, 14, INK, 6, WHITE, a, False)
        rrect(c, -40, -15, 80, 34, 6, INK, 4, (210, 235, 225), a, False)
        text(c, "?", 0, 14, 34, INK, "bold")
    elif name == "car":
        body = poly([(-130, 30), (-130, -10), (-80, -20), (-50, -60), (50, -60), (85, -20), (130, -10), (130, 30)], True)
        c.drawPath(body, fill((235, 120, 100), a)); c.drawPath(body, K())
        c.drawPath(poly([(-40, -50), (-62, -20), (0, -20), (0, -50)], True), fill((200, 230, 245), a))
        c.drawPath(poly([(10, -50), (10, -20), (70, -20), (45, -50)], True), fill((200, 230, 245), a))
        for sx in (-1, 1):
            c.drawCircle(sx * 75, 32, 26, fill(INK, a)); c.drawCircle(sx * 75, 32, 10, fill(GREY, a))
    elif name == "alarm":
        sh = math.sin(t * 50) * 6 if (t % 1.2) < .7 else 0
        c.translate(sh, 0)
        c.drawCircle(0, 0, 75, fill(WHITE, a)); c.drawCircle(0, 0, 75, K(8, RED))
        for sx in (-1, 1):
            c.drawCircle(sx * 55, -70, 22, fill(RED, a))
            c.drawLine(sx * 45, 60, sx * 60, 90, K(8, RED))
        c.drawLine(0, 0, 0, -45, K(7)); c.drawLine(0, 0, 30, 10, K(7))
    elif name == "calendar":
        rrect(c, -90, -80, 180, 170, 12, INK, 6, WHITE, a, False); c.drawRect(skia.Rect.MakeXYWH(-90, -80, 180, 40), fill(RED, a))
    elif name == "like":
        p = skia.Path(); p.moveTo(-50, -5); p.lineTo(-10, -5); p.lineTo(5, -60); p.cubicTo(25, -65, 30, -40, 22, -5)
        p.lineTo(60, -5); p.cubicTo(75, -5, 75, 15, 62, 18); p.cubicTo(75, 22, 72, 40, 58, 40)
        p.cubicTo(68, 48, 62, 64, 48, 62); p.lineTo(-10, 62); p.close()
        c.drawPath(p, fill(WHITE, a)); c.drawPath(p, K(7)); rrect(c, -75, -8, 30, 74, 6, INK, 6, BLUE, a, False)
    elif name == "brain":
        p = smooth([(-70, 10), (-75, -30), (-40, -65), (0, -70), (40, -62), (72, -30), (70, 15), (35, 40), (-20, 42)], True)
        c.drawPath(p, fill(PINK, a)); c.drawPath(p, K())
        for sx in (-30, 10):
            q = skia.Path(); q.moveTo(sx, -55); q.cubicTo(sx + 25, -30, sx - 10, -10, sx + 15, 20); c.drawPath(q, K(4))
    elif name == "liver":
        p = smooth([(-140, -10), (-110, -60), (-20, -75), (90, -60), (150, -30), (110, 10), (20, 40), (-90, 45)], True)
        c.drawPath(p, fill((176, 72, 64), a)); c.drawPath(p, K())
        q = skia.Path(); q.moveTo(-10, -70); q.cubicTo(0, -20, -20, 10, -5, 40); c.drawPath(q, K(4, (110, 40, 36)))
    elif name == "bell":
        p = skia.Path(); p.moveTo(-45, 30); p.cubicTo(-45, -60, 45, -60, 45, 30); p.lineTo(55, 40); p.lineTo(-55, 40); p.close()
        c.drawPath(p, fill(YEL, a)); c.drawPath(p, K()); c.drawCircle(0, 50, 10, fill(INK, a))
    elif name == "bed":
        rrect(c, -170, -20, 340, 50, 10, INK, 6, (180, 200, 230), a, False)
        c.drawLine(-170, -60, -170, 70, K(10)); c.drawLine(170, -20, 170, 70, K(10))
        rrect(c, -160, -48, 70, 30, 12, INK, 5, WHITE, a, False)
    elif name == "comment":
        rrect(c, -110, -70, 220, 120, 30, INK, 7, WHITE, a, False)
        c.drawPath(poly([(-50, 48), (-75, 90), (-10, 48)]), fill(WHITE, a)); c.drawPath(poly([(-50, 50), (-75, 90), (-10, 50)]), K(7))
        for i in range(3):
            c.drawCircle(-45 + i * 45, -10, 11, fill(TEAL, a))
    elif name == "warning":
        p = poly([(0, -80), (85, 70), (-85, 70)], True)
        c.drawPath(p, fill(YEL, a)); c.drawPath(p, K(8)); text(c, "!", 0, 55, 100, INK, "bold", a=a)
    c.restore()


def xmark(c, x, y, r=70, prog=1.0, w=16, a=255):
    p1, p2 = eo(pr(prog, 0, .5)), eo(pr(prog, .5, .5))
    line(c, x - r, y - r, x + r, y + r, RED, w, p1, a)
    line(c, x + r, y - r, x - r, y + r, RED, w, p2, a)


def check(c, x, y, r=40, prog=1.0, w=14, col=GREEN, a=255):
    p = poly([(x - r, y), (x - r * .3, y + r * .7), (x + r, y - r * .8)])
    c.drawPath(p, stroke(col, w, a, trim=prog))


def axes(c, x, y, w, h, prog=1.0, xl="", yl="", a=255):
    arrow(c, x, y + h, x, y - 10, INK, 6, eo(prog), 20, a)
    arrow(c, x, y + h, x + w + 10, y + h, INK, 6, eo(prog), 20, a)
    if xl:
        text(c, xl, x + w, y + h + 50, 38, INK, "hand", "r", a * prog)
    if yl:
        text(c, yl, x + 20, y - 20, 38, INK, "hand", "l", a * prog)


def curve(c, x, y, w, h, fn, prog=1.0, col=TEAL, sw=9, n=120, a=255):
    if prog <= 0:
        return
    pts = [(x + w * i / n, y + h - h * fn(i / n)) for i in range(int(n * prog) + 1)]
    if len(pts) > 1:
        c.drawPath(poly(pts), stroke(col, sw, a))


def flag(c, x, y, w, h, kind, a=255):
    if kind == "es":
        c.drawRect(skia.Rect.MakeXYWH(x, y, w, h), fill((198, 11, 30), a))
        c.drawRect(skia.Rect.MakeXYWH(x, y + h / 4, w, h / 2), fill((255, 196, 0), a))
    else:
        for i, col in enumerate([(0, 104, 71), (255, 255, 255), (206, 17, 38)]):
            c.drawRect(skia.Rect.MakeXYWH(x + i * w / 3, y, w / 3, h), fill(col, a))
    c.drawRect(skia.Rect.MakeXYWH(x, y, w, h), stroke(INK, 5, a))


def source_tag(c, s, a=255):
    f = font("reg", 24); w = f.measureText("Fuente: " + s)
    rrect(c, 36, 30, w + 36, 46, 12, INK, 0, (242, 242, 242), a * .95, False)
    c.drawString("Fuente: " + s, 54, 61, f, fill(INK, a * .85))


def make_paper():
    rng = np.random.default_rng(3)
    arr = np.zeros((H, W, 4), np.uint8)
    base = np.array(PAPER, np.float32)
    noise = rng.normal(0, 2.2, (H, W, 1)).astype(np.float32)
    yy, xx = np.mgrid[0:H, 0:W]
    vign = 1 - .035 * (((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
    img = base * vign[..., None] + noise * .5
    arr[..., :3] = np.clip(img, 0, 255); arr[..., 3] = 255
    return skia.Image.fromarray(arr, colorType=skia.kRGBA_8888_ColorType)
