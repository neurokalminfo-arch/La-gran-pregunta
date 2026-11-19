import os
"""Miniatura provisional con el nuevo estilo: dos personas idénticas, una con la barriga en llamas (×2)."""
import numpy as np, skia, math
from lib import *
from chars import person

TW, TH = 1280, 720
arr = np.zeros((TH, TW, 4), np.uint8)
surf = skia.Surface(arr, colorType=skia.kRGBA_8888_ColorType)


def flame(c, x, y, s):
    c.save(); c.translate(x, y); c.scale(s, s)
    outer = smooth([(0, 60), (-55, 20), (-50, -40), (-20, -70), (-25, -120), (10, -80), (30, -150), (45, -60), (60, -30), (50, 25)], True)
    c.drawPath(outer, fill((255, 110, 30))); c.drawPath(outer, stroke(INK, 6))
    inner = smooth([(0, 45), (-28, 15), (-20, -25), (5, -45), (8, -80), (25, -35), (30, 10)], True)
    c.drawPath(inner, fill((255, 220, 60)))
    c.restore()


with surf as c:
    c.clear(C((255, 255, 255)))
    # mitad izquierda cálida, derecha fría
    c.drawRect(skia.Rect.MakeXYWH(0, 0, 640, 720), fill((255, 236, 205)))
    c.drawRect(skia.Rect.MakeXYWH(640, 0, 640, 720), fill((222, 230, 240)))
    c.drawLine(640, 0, 640, 720, stroke(INK, 8))
    # sol
    c.drawCircle(110, 140, 70, fill(YEL)); c.drawCircle(110, 140, 70, stroke(AMBER, 8))
    person(c, 330, 690, 1.55, "happy", "walk", .15)
    for i, (dx, dy, sc) in enumerate(((0, 0, 1.4), (-60, 30, .9), (60, 25, 1.0))):
        flame(c, 330 + dx, 480 + dy, sc * .9)
    person(c, 960, 690, 1.55, "tired", "stand", 0.0, col=(150, 156, 170))
    icon(c, "phone", 1060, 380, .55)
    # ×2 grande
    t = font("bold", 230)
    for sx, col in ((8, INK), (0, AMBER)):
        c.drawString("×2", 470 + sx, 300 + sx, t, fill(col))
    # titular
    f = font("marker", 70); s = "ANTES DE DESAYUNAR"
    w = f.measureText(s)
    c.save(); c.translate(640, 660); c.rotate(-2)
    c.drawRoundRect(skia.Rect.MakeXYWH(-w / 2 - 26, -70, w + 52, 96), 14, 14, fill(RED))
    c.drawRoundRect(skia.Rect.MakeXYWH(-w / 2 - 26, -70, w + 52, 96), 14, 14, stroke(INK, 6))
    c.drawString(s, -w / 2, 4, f, fill(WHITE)); c.restore()
skia.Image.fromarray(arr, colorType=skia.kRGBA_8888_ColorType).save(os.path.dirname(os.path.abspath(__file__)) + "/miniatura_provisional.jpg", skia.kJPEG, 92)
print("ok")
