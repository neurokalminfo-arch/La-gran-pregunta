import sys, math
sys.path.append('/home/claude/video')
import cairo, numpy as np
from PIL import Image
from lib import hexc, col
import importlib.util as U
_s = U.spec_from_file_location('vthumb', '/home/claude/video/thumb.py'); _m = U.module_from_spec(_s); _s.loader.exec_module(_m); stroke_text = _m.stroke_text
TW, TH = 1280, 720
def base(src, yfrac=.5):
    im = Image.open(src).convert('RGB'); r = TW / im.width; im = im.resize((TW, round(im.height * r)), Image.LANCZOS)
    y0 = int((im.height - TH) * yfrac); im = im.crop((0, y0, TW, y0 + TH))
    a = np.dstack([np.asarray(im)[:, :, ::-1], np.full((TH, TW), 255, np.uint8)]).copy()
    s = cairo.ImageSurface(cairo.FORMAT_RGB24, TW, TH); c = cairo.Context(s)
    c.set_source_surface(cairo.ImageSurface.create_for_data(memoryview(a), cairo.FORMAT_RGB24, TW, TH), 0, 0); c.paint()
    return s, c, a
def shade(c, x0, y0, x1, y1, a=.75):
    g = cairo.LinearGradient(x0, y0, x1, y1); g.add_color_stop_rgba(0, 0, 0, 0, a); g.add_color_stop_rgba(1, 0, 0, 0, 0); c.set_source(g); c.paint()
def tag(c, s, x, y, size, bg, fg=(1, 1, 1)):
    c.select_font_face('Inter Display', cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD); c.set_font_size(size)
    w = c.text_extents(s).x_advance
    c.save(); c.translate(x, y); c.rotate(-.05)
    col(c, bg); c.rectangle(-18, -size * .95, w + 36, size * 1.25); c.fill()
    col(c, fg); c.move_to(0, 0); c.show_text(s); c.new_path(); c.restore()

ICE = hexc('#BFE8FF'); SAND = hexc('#FFB224'); WHITE = hexc('#FFFFFF')
# 1: split ciudad
s, c, _ = base('v1_split.png', .45)
shade(c, 0, 0, 0, 260, .6); shade(c, 0, TH, 0, TH - 300, .7)
stroke_text(c, "EUROPA", 30, 110, 110, WHITE, outline=16, maxw=520)
stroke_text(c, "CONGELADA", 30, 220, 100, ICE, outline=16, maxw=560)
stroke_text(c, "ARGENTINA", 660, 590, 100, WHITE, outline=16, maxw=600)
stroke_text(c, "DESIERTO", 660, 695, 104, SAND, outline=16, maxw=600)
s.write_to_png('mini_1_europa_argentina.png')
# 2: planeta
s, c, _ = base('v2_planeta.png', .5)
shade(c, 0, 0, 520, 0, .85)
stroke_text(c, "¿Y SI GIRA", 30, 130, 96, WHITE, outline=16, maxw=480)
stroke_text(c, "AL REVÉS?", 30, 240, 104, hexc('#FF4B3A'), outline=16, maxw=480)
tag(c, "EUROPA: 20 °C MÁS FRÍO", 60, 650, 46, hexc('#2E8BFF'))
s.write_to_png('mini_2_planeta.png')
# 3: frontera
s, c, _ = base('v3_hombre.png', .45)
shade(c, 0, 0, 0, 260, .6)
stroke_text(c, "EUROPA", 40, 130, 112, ICE, outline=16, maxw=540)
stroke_text(c, "ARGENTINA", 680, 130, 104, SAND, outline=16, maxw=570)
tag(c, "20 °C MÁS FRÍO", 60, 640, 54, hexc('#2E8BFF'))
tag(c, "DESIERTO", 800, 640, 62, hexc('#E2561B'))
s.write_to_png('mini_3_frontera.png')
from PIL import Image
ims = [Image.open(f) for f in ('mini_1_europa_argentina.png', 'mini_2_planeta.png', 'mini_3_frontera.png')]
S = Image.new('RGB', (1280, 720 + 160), 'black')
for i, im in enumerate(ims): S.paste(im.resize((640, 360)), ((i % 2) * 640, (i // 2) * 360))
for i, im in enumerate(ims): S.paste(im.resize((240, 135)), (40 + i * 300, 735))
S.save('preview.jpg')
