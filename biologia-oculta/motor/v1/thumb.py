import os
"""Miniatura 1280x720: reloj 7:00 + célula con puerta trasera abierta + figura caminando."""
import numpy as np, skia, math
from lib import *

TW, TH = 1280, 720
arr = np.zeros((TH, TW, 4), np.uint8)
surf = skia.Surface(arr, colorType=skia.kRGBA_8888_ColorType)
with surf as c:
    c.clear(C((247, 241, 228)))
    # mancha de color de fondo
    c.drawCircle(860, 380, 380, fill(YEL, 255))
    # célula muscular
    c.save(); c.translate(860, 470); c.rotate(-4)
    rrect(c, -330, -150, 660, 300, 90, (170, 60, 60), 12, (247, 205, 195), shadow=True)
    for i in range(3):
        y = -80 + i * 60
        c.drawPath(smooth([(-250, y), (0, y + 14), (250, y)]), stroke((215, 140, 130), 7))
    # puerta trasera abierta con luz
    c.drawRect(skia.Rect.MakeXYWH(150, -150, 120, 26), fill((150, 255, 190)))
    c.save(); c.translate(150, -137); c.rotate(-75); rrect(c, 0, -14, 120, 28, 8, INK, 6, GREEN, shadow=False); c.restore()
    for j, (dx, dy) in enumerate(((210, -230), (190, -320), (240, -400))):
        pts=[(dx+34*math.cos(j+math.pi/3*k), dy+34*math.sin(j+math.pi/3*k)) for k in range(6)]
        p=poly(pts,True); c.drawPath(p, fill(AMBER)); c.drawPath(p, stroke(INK,6))
    arrow(c, 210, -200, 210, -100, GREEN, 12, 1, 30)
    text(c, "MÚSCULO", -60, 40, 64, (150, 50, 50), "marker")
    c.restore()
    # reloj 7:00
    clock(c, 190, 330, 120, 7.0)
    # figura caminando
    stick(c, 330, 700, .95, "happy", "walk", .18)
    # texto
    for dx, dy in ((5, 6),):
        text(c, "10 MIN", 330 + dx, 600 + dy - 470, 1, INK)
    f = font("marker", 92)
    for s, x, y, col in (("SIN INSULINA", 640, 120, INK),):
        w = f.measureText(s)
        c.drawRoundRect(skia.Rect.MakeXYWH(x - w / 2 - 24, y - 82, w + 48, 108), 16, 16, fill(WHITE))
        c.drawRoundRect(skia.Rect.MakeXYWH(x - w / 2 - 24, y - 82, w + 48, 108), 16, 16, stroke(INK, 6))
        c.drawString(s, x - w / 2, y, f, fill(RED))
skia.Image.fromarray(arr, colorType=skia.kRGBA_8888_ColorType).save(os.path.dirname(os.path.abspath(__file__)) + "/miniatura.jpg", skia.kJPEG, 92)
print("ok")
