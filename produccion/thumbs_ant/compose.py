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

# A: espacio
s, c, _ = base('a_espacio.png', .35)
shade(c, TW, 0, TW * .45, 0, .8)
stroke_text(c, "¿Y SI MAÑANA", 610, 140, 104, hexc('#FFFFFF'), outline=16, maxw=640)
stroke_text(c, "SE DERRITE?", 610, 270, 132, hexc('#5FE3FF'), outline=18, maxw=650)
tag(c, "+58 METROS", 820, 400, 64, hexc('#FF3B2F'))
s.write_to_png('mini_A_se_derrite.png')
# B: calle
s, c, _ = base('b_calle.png', .55)
shade(c, 0, TH, 0, TH * .35, .85)
stroke_text(c, "¿TU CIUDAD", 40, 545, 118, hexc('#FFFFFF'), outline=16, maxw=760)
stroke_text(c, "BAJO EL AGUA?", 40, 680, 128, hexc('#FFB224'), outline=18, maxw=820)
tag(c, "+58 M", 1010, 140, 80, hexc('#FF3B2F'))
s.write_to_png('mini_B_tu_ciudad.png')
# C: ola
s, c, _ = base('c_ola.png', .45)
shade(c, 0, 0, 0, TH * .5, .7)
stroke_text(c, "¿Y SI MAÑANA", 40, 120, 92, hexc('#FFFFFF'), outline=14, maxw=640)
stroke_text(c, "SE INUNDA", 40, 240, 120, hexc('#5FE3FF'), outline=16, maxw=640)
stroke_text(c, "TU CIUDAD?", 40, 360, 120, hexc('#FFB224'), outline=16, maxw=640)
tag(c, "+58 M", 1010, 330, 70, hexc('#FF3B2F'))
s.write_to_png('mini_C_inunda.png')
ims = [Image.open(f) for f in ('mini_A_se_derrite.png', 'mini_B_tu_ciudad.png', 'mini_C_inunda.png')]
S = Image.new('RGB', (1280, 720 * 3 // 2 + 380)); 
for i, im in enumerate(ims): S.paste(im.resize((640, 360)), ((i % 2) * 640, (i // 2) * 360))
for i, im in enumerate(ims): S.paste(im.resize((240, 135)), (40 + i * 300, 760))
S.save('preview.jpg')
