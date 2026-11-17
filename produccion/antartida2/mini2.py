import sys, math
sys.path.append('/home/claude/video')
import cairo, numpy as np
from PIL import Image
from lib import *
import importlib.util as U
_s = U.spec_from_file_location('vthumb', '/home/claude/video/thumb.py'); _m = U.module_from_spec(_s); _s.loader.exec_module(_m); stroke_text = _m.stroke_text
TW, TH = 1280, 720
im = Image.open('/home/claude/antartida2/plates/thumb_flood.png').convert('RGB')
r = TW / im.width; im = im.resize((TW, int(im.height * r)), Image.LANCZOS)
y0 = int((im.height - TH) * .45); im = im.crop((0, y0, TW, y0 + TH))
a = np.dstack([np.asarray(im)[:, :, ::-1], np.full((TH, TW), 255, np.uint8)]).copy()
surf = cairo.ImageSurface(cairo.FORMAT_RGB24, TW, TH); ctx = cairo.Context(surf)
ctx.set_source_surface(cairo.ImageSurface.create_for_data(memoryview(a), cairo.FORMAT_RGB24, TW, TH), 0, 0); ctx.paint()
g = cairo.LinearGradient(0, 0, 0, 420); g.add_color_stop_rgba(0, 0, 0, 0, .7); g.add_color_stop_rgba(1, 0, 0, 0, 0); ctx.set_source(g); ctx.paint()
stroke_text(ctx, "+58 METROS", 40, 175, 170, hexc('#FFFFFF'), outline=18, maxw=1000)
stroke_text(ctx, "¿TU CIUDAD?", 44, 300, 110, hexc('#FFB224'), outline=14, maxw=760)
surf.write_to_png('/home/claude/antartida2/out/miniatura_antartida_v2.png')
Image.open('/home/claude/antartida2/out/miniatura_antartida_v2.png').resize((640, 360)).save('/home/claude/antartida2/thumb_check.png')
