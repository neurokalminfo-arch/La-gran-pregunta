import sys, math
sys.path.append('/home/claude/video')
import cairo, numpy as np
from PIL import Image
from lib import *
import importlib.util as U; _s=U.spec_from_file_location('vthumb','/home/claude/video/thumb.py'); _m=U.module_from_spec(_s); _s.loader.exec_module(_m); stroke_text=_m.stroke_text
TW, TH = 1280, 720
im = Image.open('img/thumb_earth.png').convert('RGB')
r = max(TW / im.width, TH / im.height); im = im.resize((int(im.width * r), int(im.height * r)), Image.LANCZOS)
x0 = (im.width - TW); im = im.crop((x0 - 60, 0, x0 - 60 + TW, TH)) if x0 > 60 else im.crop((0, 0, TW, TH))
a = np.dstack([np.asarray(im)[:, :, ::-1], np.full((TH, TW), 255, np.uint8)]).copy()
surf = cairo.ImageSurface(cairo.FORMAT_RGB24, TW, TH); ctx = cairo.Context(surf)
ctx.set_source_surface(cairo.ImageSurface.create_for_data(memoryview(a), cairo.FORMAT_RGB24, TW, TH), 0, 0); ctx.paint()
g = cairo.LinearGradient(0, 0, 700, 0); g.add_color_stop_rgba(0, 0, 0, 0, .85); g.add_color_stop_rgba(1, 0, 0, 0, 0)
ctx.set_source(g); ctx.paint()
# flecha roja de giro al revés (frente del globo, de derecha a izquierda)
gx, gy, rx, ry = 990, 520, 430, 105
def arcpath(w, c, al):
    ctx.save(); ctx.translate(gx, gy); ctx.scale(1, ry / rx); ctx.arc(0, 0, rx, math.radians(12), math.radians(128)); ctx.restore()
    col(ctx, c, al); ctx.set_line_width(w); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.stroke()
arcpath(30, (0, 0, 0), .6); arcpath(18, hexc('#FF3B2F'), 1)
th = math.radians(128); ex, ey = gx + rx * math.cos(th), gy + ry * math.sin(th)
tx, ty = -rx * math.sin(th), ry * math.cos(th); n = math.hypot(tx, ty); tx, ty = tx / n, ty / n
ctx.save(); ctx.translate(ex, ey); ctx.rotate(math.atan2(ty, tx))
ctx.move_to(62, 0); ctx.line_to(-18, -44); ctx.line_to(-18, 44); ctx.close_path()
col(ctx, (0, 0, 0), .6); ctx.set_line_width(10); ctx.stroke_preserve(); col(ctx, hexc('#FF3B2F')); ctx.fill(); ctx.restore()
stroke_text(ctx, "SÁHARA", 50, 250, 150, hexc('#55D46E'), outline=16, maxw=560)
stroke_text(ctx, "VERDE", 50, 390, 150, hexc('#55D46E'), outline=16, maxw=560)
stroke_text(ctx, "EUROPA", 50, 530, 120, hexc('#BFE3FF'), outline=14, maxw=560)
stroke_text(ctx, "HELADA", 50, 650, 120, hexc('#BFE3FF'), outline=14, maxw=560)
surf.write_to_png('out/miniatura_tierra_al_reves.png')
Image.open('out/miniatura_tierra_al_reves.png').resize((320, 180)).save('thumb_small.png')
