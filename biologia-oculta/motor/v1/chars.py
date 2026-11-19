"""Personajes nuevos (estilo ilustración de pizarra con volumen) y cuerpo anatómico."""
import math
import skia
from lib import (C, stroke, fill, smooth, poly, text, INK, WHITE, TEAL, AMBER, RED, GREEN, BLUE, GREY, YEL, PINK)

SKIN = (255, 255, 255)
SHIRT_BLUE = (150, 200, 235)
PANTS = (38, 44, 56)
JEANS = (70, 105, 165)


def limb(c, pts, w, col, a=255, o=5):
    p = poly(pts)
    c.drawPath(p, stroke(INK, w + 2 * o, a))
    c.drawPath(p, stroke(col, w, a))


def blob(c, path, col, a=255, w=6):
    c.drawPath(path, fill(col, a)); c.drawPath(path, stroke(INK, w, a))


def person(c, x, y, s=1.0, mood="happy", pose="stand", t=0.0, doctor=False, col=INK, talk=False,
           arm=None, legs=None, a=255, lean=0, hair=None, sweat=False, glasses=False, shadow=True):
    layer = a < 255
    if layer:
        c.saveLayerAlpha(None, int(max(0, a)))
    c.save(); c.translate(x, y); c.rotate(lean)
    woman = hair == "f"
    if col != INK:
        shirt = col
    else:
        shirt = WHITE if doctor else (AMBER if woman else BLUE)
    pants = PANTS if doctor else ((90, 80, 110) if woman else JEANS)
    if shadow:
        c.drawOval(skia.Rect.MakeXYWH(-75 * s, -12 * s, 150 * s, 24 * s), fill(INK, 28))
    ph = t * 2 * math.pi * (1.6 if pose == "walk" else 2.6 if pose == "run" else 0)
    sw = {"walk": .42, "run": .8}.get(pose, 0)
    la, lb = (math.sin(ph) * sw, -math.sin(ph) * sw) if legs is None else legs
    # piernas
    for sx, ang in ((-1, lb), (1, la)):
        hip = (sx * 17 * s, -125 * s)
        kn = (hip[0] + math.sin(ang) * 58 * s, hip[1] + math.cos(ang) * 58 * s)
        bend = ang * .5 - (.35 if pose == "run" and ang < 0 else 0)
        ft = (kn[0] + math.sin(bend) * 56 * s, kn[1] + math.cos(bend) * 56 * s)
        limb(c, [hip, kn, ft], 30 * s, pants, a, 4 * s)
        c.drawOval(skia.Rect.MakeXYWH(ft[0] - 16 * s, ft[1] - 12 * s, 46 * s, 24 * s), fill(INK, a))
    # pelo largo por detrás
    hy = -308 * s; hr = 54 * s
    if woman:
        back = smooth([(-hr * 1.05, hy), (-hr * 1.15, hy + hr * 1.3), (-hr * .3, hy + hr * 1.5), (hr * .3, hy + hr * 1.5), (hr * 1.15, hy + hr * 1.3), (hr * 1.05, hy)], True)
        blob(c, back, (90, 60, 40), a, 5 * s)
    # torso
    if doctor:
        coat = smooth([(-50 * s, -250 * s), (-58 * s, -170 * s), (-64 * s, -92 * s), (64 * s, -92 * s), (58 * s, -170 * s), (50 * s, -250 * s)], True)
        blob(c, coat, WHITE, a, 6 * s)
        c.drawPath(poly([(-21 * s, -251 * s), (21 * s, -251 * s), (0, -196 * s)], True), fill(SHIRT_BLUE, a))
        c.drawPath(poly([(-6 * s, -246 * s), (6 * s, -246 * s), (9 * s, -205 * s), (0, -188 * s), (-9 * s, -205 * s)], True), fill(INK, a))
        for sx in (-1, 1):
            c.drawPath(poly([(sx * 23 * s, -252 * s), (sx * 3 * s, -190 * s), (sx * 3 * s, -95 * s)]), stroke(INK, 4.5 * s, a))
            c.drawPath(poly([(sx * 23 * s, -252 * s), (sx * 30 * s, -225 * s), (sx * 18 * s, -218 * s)]), stroke(INK, 4 * s, a))
            pk = skia.Path(); pk.moveTo(sx * 22 * s, -135 * s); pk.lineTo(sx * 22 * s, -112 * s)
            pk.quadTo(sx * 36 * s, -102 * s, sx * 50 * s, -112 * s); pk.lineTo(sx * 50 * s, -135 * s)
            c.drawPath(pk, stroke(INK, 4 * s, a))
        for by in (-175, -150, -125):
            c.drawCircle(9 * s, by * s, 4 * s, fill(INK, a))
        st = skia.Path(); st.moveTo(-30 * s, -248 * s); st.cubicTo(-46 * s, -170 * s, 10 * s, -160 * s, 34 * s, -205 * s)
        c.drawPath(st, stroke(INK, 9 * s, a)); c.drawPath(st, stroke((120, 128, 140), 5 * s, a))
        c.drawCircle(36 * s, -200 * s, 11 * s, fill((200, 205, 212), a)); c.drawCircle(36 * s, -200 * s, 11 * s, stroke(INK, 4 * s, a))
    else:
        tor = smooth([(-48 * s, -250 * s), (-52 * s, -190 * s), (-46 * s, -118 * s), (46 * s, -118 * s), (52 * s, -190 * s), (48 * s, -250 * s)], True)
        blob(c, tor, shirt, a, 6 * s)
        c.drawArc(skia.Rect.MakeXYWH(-16 * s, -262 * s, 32 * s, 26 * s), 0, 180, False, stroke(INK, 4 * s, a))
    # brazos
    if arm is None:
        if pose in ("walk", "run"):
            k = 1.15 if pose == "run" else 1
            arm = (math.pi - .25 - math.sin(ph) * sw * k, -math.pi + .25 - math.sin(ph) * sw * k)
        elif pose == "point":
            arm = (.75 + .1 * math.sin(t * 4), -math.pi * .9)
        elif pose == "pointl":
            arm = (math.pi * .9, -.75 - .1 * math.sin(t * 4))
        elif pose == "cheer":
            arm = (.35 + .12 * math.sin(t * 6), -.35 - .12 * math.sin(t * 6))
        elif pose == "shrug":
            arm = (math.pi * .6, -math.pi * .6)
        else:
            arm = (math.pi * .9, -math.pi * .9)
    sleeve = WHITE if doctor else shirt
    for sx, ang in ((1, arm[0]), (-1, arm[1])):
        sh = (sx * 44 * s, -238 * s)
        el = (sh[0] + math.sin(ang) * 58 * s, sh[1] - math.cos(ang) * 58 * s)
        a2 = ang + (.25 if pose in ("walk", "run") else 0) * (1 if sx > 0 else -1)
        hd = (el[0] + math.sin(a2) * 52 * s, el[1] - math.cos(a2) * 52 * s)
        limb(c, [sh, el], 25 * s, sleeve, a, 4 * s)
        limb(c, [el, hd], 23 * s, sleeve if doctor else SKIN, a, 4 * s)
        c.drawCircle(hd[0], hd[1], 15 * s, fill(SKIN, a)); c.drawCircle(hd[0], hd[1], 15 * s, stroke(INK, 5 * s, a))
        th = (hd[0] + math.cos(ang) * 12 * s * sx, hd[1] + math.sin(ang) * 12 * s * sx)
        c.drawCircle(th[0], th[1], 6 * s, fill(SKIN, a)); c.drawCircle(th[0], th[1], 6 * s, stroke(INK, 4 * s, a))
    # cuello + cabeza
    c.drawCircle(0, hy, hr, fill(SKIN, a)); c.drawCircle(0, hy, hr, stroke(INK, 7 * s, a))
    if woman:
        bang = smooth([(-hr * 1.02, hy - 2 * s), (-hr * .7, hy - hr * .95), (0, hy - hr * 1.12), (hr * .7, hy - hr * .95), (hr * 1.02, hy - 2 * s), (hr * .4, hy - hr * .55), (-hr * .5, hy - hr * .45)], True)
        blob(c, bang, (90, 60, 40), a, 5 * s)
    elif doctor:
        c.drawArc(skia.Rect.MakeXYWH(-hr, hy - hr, hr * 2, hr * 2), 200, 140, False, stroke(INK, 5 * s, a))
        c.drawCircle(-6 * s, hy - hr * .82, 15 * s, fill((215, 222, 230), a)); c.drawCircle(-6 * s, hy - hr * .82, 15 * s, stroke(INK, 5 * s, a))
        c.drawCircle(-6 * s, hy - hr * .82, 6 * s, stroke(INK, 3 * s, a))
    else:
        tuft = poly([(-hr * .85, hy - hr * .45), (-hr * .7, hy - hr * 1.15), (-hr * .3, hy - hr * .9), (0, hy - hr * 1.3), (hr * .3, hy - hr * .95),
                     (hr * .75, hy - hr * 1.2), (hr * .9, hy - hr * .45), (0, hy - hr * .7)], True)
        c.drawPath(tuft, fill(INK, a))
    # cara
    blink = ((t + (x * 0.0137) % 3.7) % 3.7) < .12
    ex, ey = 18 * s, hy - 4 * s
    if mood == "sleep" or blink:
        for sx in (-1, 1):
            c.drawArc(skia.Rect.MakeXYWH(sx * ex - 9 * s, ey - 4 * s, 18 * s, 10 * s), 0, 180, False, stroke(INK, 4 * s, a))
    else:
        for sx in (-1, 1):
            c.drawOval(skia.Rect.MakeXYWH(sx * ex - 6 * s, ey - 11 * s, 12 * s, 20 * s), fill(INK, a))
            c.drawCircle(sx * ex + 2 * s, ey - 6 * s, 2.5 * s, fill(WHITE, a))
    if glasses:
        for sx in (-1, 1):
            c.drawCircle(sx * ex, ey, 15 * s, stroke(INK, 3.5 * s, a))
    if mood in ("happy", "calm") and not talk:
        for sx in (-1, 1):
            c.drawCircle(sx * 33 * s, hy + 14 * s, 8 * s, fill(PINK, 90 * a / 255))
    my = hy + 22 * s
    if talk:
        o = 7 * s + 9 * s * abs(math.sin(t * 15))
        c.drawOval(skia.Rect.MakeXYWH(-13 * s, my - o / 2, 26 * s, o), fill(INK, a))
    elif mood == "happy":
        sm = skia.Path(); sm.moveTo(-20 * s, my - 6 * s); sm.quadTo(0, my + 16 * s, 20 * s, my - 6 * s); sm.close()
        c.drawPath(sm, fill(INK, a))
    elif mood == "calm":
        c.drawArc(skia.Rect.MakeXYWH(-14 * s, my - 12 * s, 28 * s, 18 * s), 20, 140, False, stroke(INK, 5 * s, a))
    elif mood in ("tired", "sad"):
        c.drawArc(skia.Rect.MakeXYWH(-14 * s, my, 28 * s, 16 * s), 200, 140, False, stroke(INK, 5 * s, a))
        if mood == "tired":
            for sx in (-1, 1):
                c.drawArc(skia.Rect.MakeXYWH(sx * ex - 10 * s, ey + 9 * s, 20 * s, 9 * s), 0, 180, False, stroke(GREY, 3 * s, a))
    elif mood == "wow":
        c.drawOval(skia.Rect.MakeXYWH(-9 * s, my - 8 * s, 18 * s, 22 * s), fill(INK, a))
    elif mood == "skeptic":
        c.drawLine(-14 * s, my + 4 * s, 14 * s, my - 3 * s, stroke(INK, 5 * s, a))
        c.drawLine(6 * s, ey - 24 * s, 28 * s, ey - 30 * s, stroke(INK, 5 * s, a))
    else:
        c.drawLine(-12 * s, my, 12 * s, my, stroke(INK, 5 * s, a))
    if sweat:
        for i in range(2):
            yy = hy - 10 * s + ((t * 60 + i * 25) % 50) * s
            c.drawCircle(hr + 12 * s + i * 14 * s, yy, 7 * s, fill(BLUE, a * .85))
    c.restore()
    if layer:
        c.restore()


def anatomy(c, x, y, s=1.0, glow=None, t=0.0, a=255):
    """Cuerpo de frente con órganos. (x, y) = centro del pecho. Altura ≈ 900*s."""
    c.save(); c.translate(x, y); c.scale(s, s)
    skin = (246, 196, 176)
    body = smooth([(26, -290), (40, -250), (150, -225), (185, -150), (200, 60), (225, 230), (190, 240),
                   (160, 70), (150, -60), (130, 120), (120, 250), (95, 520), (40, 525), (20, 260), (0, 230),
                   (-20, 260), (-40, 525), (-95, 520), (-120, 250), (-130, 120), (-150, -60), (-160, 70), (-190, 240),
                   (-225, 230), (-200, 60), (-185, -150), (-150, -225), (-40, -250), (-26, -290)], True)
    c.drawPath(body, fill(skin, a)); c.drawPath(body, stroke((150, 80, 70), 6, a))
    c.drawCircle(0, -350, 66, fill(skin, a)); c.drawCircle(0, -350, 66, stroke((150, 80, 70), 6, a))
    # vasos
    for sx in (-1, 1):
        v = smooth([(sx * 20, -220), (sx * 120, -170), (sx * 170, 40), (sx * 200, 200)])
        c.drawPath(v, stroke((90, 150, 210), 5, a * .8))
        v2 = smooth([(sx * 25, 150), (sx * 70, 300), (sx * 70, 500)])
        c.drawPath(v2, stroke((210, 70, 70), 5, a * .8))
    def g(name):
        return glow == name
    # pulmones
    for sx in (-1, 1):
        lung = smooth([(sx * 20, -200), (sx * 95, -195), (sx * 115, -80), (sx * 95, -20), (sx * 25, -40)], True)
        blob(c, lung, (240, 160, 170) if sx < 0 else (160, 200, 235), a, 4)
    heart = smooth([(-5, -120), (30, -140), (45, -95), (10, -50), (-25, -85)], True)
    blob(c, heart, (215, 60, 60), a, 4)
    # hígado (lado derecho del cuerpo = izquierda de la imagen)
    liver = smooth([(-120, 0), (-60, -25), (30, -15), (40, 20), (-40, 60), (-110, 55)], True)
    if g("liver"):
        c.drawCircle(-50, 20, 110 + 8 * math.sin(t * 6), fill(YEL, 120 * a / 255))
    blob(c, liver, (170, 70, 60), a, 4)
    stom = smooth([(40, -5), (100, -10), (105, 50), (55, 75), (30, 45)], True)
    blob(c, stom, (240, 170, 120), a, 4)
    gut = smooth([(-85, 80), (85, 80), (95, 190), (0, 215), (-95, 190)], True)
    blob(c, gut, (235, 150, 140), a, 4)
    for i in range(3):
        c.drawPath(smooth([(-70, 110 + i * 30), (-20, 95 + i * 30), (20, 125 + i * 30), (70, 105 + i * 30)]), stroke((180, 90, 90), 3, a))
    if g("muscle"):
        for sx in (-1, 1):
            c.drawOval(skia.Rect.MakeXYWH(sx * 70 - 45, 290, 90, 180), fill(TEAL, (110 + 60 * math.sin(t * 6)) * a / 255))
    if g("brain"):
        c.drawCircle(0, -350, 70 + 6 * math.sin(t * 6), fill(YEL, 140 * a / 255))
    c.restore()
