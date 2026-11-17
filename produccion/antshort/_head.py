"""Short '¿Qué pasaría si se derritiera toda la Antártida?' — 9:16, animación con código, karaoke por palabra,
cámara (punch-in, sacudidas, destellos), partículas y diseño de sonido sintetizado.
Uso: python3 render.py stills | audio | video"""
import sys, os, math, random, re, json, subprocess, time
sys.path.append('/home/claude/video')
import cairo
import numpy as np
from lib import (col, hexc, rrect, glow, ease, eout, prog, lerp, mix, clamp, fmt_int, Proj, draw_map, skyline, font,
                 BG, INK, MUTED, RED, AMBER, GREEN, LINE, PANEL, F_BLACK, F_XB, F_SEMI)
from script import PHASES, TEXT

HERE = os.path.dirname(os.path.abspath(__file__))
SW, SH, FPS = 1080, 1920, 30
V0 = 0.15                      # la voz empieza aquí
BLUE = hexc('#5AA9FF'); DARK = hexc('#06080B'); OFF = hexc('#151A22')

# ------------------------------------------------------------------ tiempos (alineación de ElevenLabs)
A = json.load(open(os.path.join(HERE, 'audio', 'align.json')))
CST, CEN = A['character_start_times_seconds'], A['character_end_times_seconds']
WORDS = [(m.group(), V0 + CST[m.start()], V0 + CEN[m.end() - 1], m.start()) for m in re.finditer(r'\S+', TEXT)]
PH = []; pos = 0
for k, s in PHASES:
    i = TEXT.index(s, pos); PH.append([k, V0 + CST[i] - (0 if not PH else .05), s, i, i + len(s)]); pos = i + len(s)
PH[0][1] = 0.0
DUR = V0 + CEN[-1] + 1.3
for j in range(len(PH)): PH[j].append((PH[j + 1][1] if j + 1 < len(PH) else DUR) - PH[j][1])

def wt(phase, needle, end=False):
    """tiempo (absoluto) de la palabra que contiene `needle` dentro de la fase."""
    p = next(x for x in PH if x[0] == phase)
    for w, a, b, ci in WORDS:
        if p[3] <= ci < p[4] and needle.lower() in w.lower():
            return b if end else a
    raise KeyError(needle)

# caption chunks: hasta ~3 palabras, corte en puntuación
CHUNKS = []; cur = []
for w in WORDS:
    cur.append(w)
    if len(' '.join(x[0] for x in cur)) > 14 or re.search(r'[.?!:,]$', w[0]) or len(cur) >= 3:
        CHUNKS.append(cur); cur = []
if cur: CHUNKS.append(cur)
HL = re.compile(r'(xx|pasó|oscuras|chile|semáforos|ciento|dieciséis|diez|tarjeta|rápido|cincuenta|corazón|igualado|golpe|otra|setenta|dos|horas|agua|radio|linterna|efectivo|medicinas|batería|tres|kit|internet|gran|pregunta)', re.I)

# impactos: (tiempo, fuerza de sacudida, destello)
IMPACTS = []  # se rellena tras definir las fases (ver abajo)

# ------------------------------------------------------------------ utilidades de dibujo
def T(ctx, s, x, y, size, c=INK, fam=F_BLACK, align='c', a=1.0, maxw=980, outline=0, track=0):
    if a <= 0 or not s: return
    font(ctx, fam, size); tw = ctx.text_extents(s).x_advance
    if maxw and tw > maxw:
        size *= maxw / tw; font(ctx, fam, size); tw = ctx.text_extents(s).x_advance
    x0 = x - tw / 2 if align == 'c' else x - tw if align == 'r' else x
    ctx.move_to(x0, y); ctx.text_path(s)
    if outline:
        col(ctx, (0, 0, 0), a); ctx.set_line_width(outline); ctx.set_line_join(cairo.LINE_JOIN_ROUND); ctx.stroke_preserve()
    col(ctx, c, a); ctx.fill(); ctx.new_path()

def back_pop(x):
    """easeOutBack: entrada con rebote."""
    if x <= 0: return 0.0
    if x >= 1: return 1.0
    c1 = 1.9; c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2

def popk(t, t0, dur=.35): return back_pop((t - t0) / dur)

def scaled(ctx, x, y, s, fn):
    if s <= 0: return
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s); fn(); ctx.restore()

def tag(ctx, s, x, y, k, c=AMBER, size=46, bg=(0, 0, 0)):
    if k <= 0: return
    font(ctx, F_XB, size); w = ctx.text_extents(s).x_advance + 50
    col(ctx, bg, .7 * k); rrect(ctx, x - w / 2, y - size - 12, w, size + 36, 14); ctx.fill()
    T(ctx, s, x, y + 2, size, c, F_XB, a=k)

def stamp(ctx, s, x, y, t, t0, c=RED, size=150, rot=-.08):
    if t < t0: return
    q = clamp((t - t0) / .22); sc = lerp(2.4, 1.0, eout(q)); a = min(1, q * 2)
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(sc, sc)
    font(ctx, F_BLACK, size); w = ctx.text_extents(s).x_advance + 60
    col(ctx, c, a); ctx.set_line_width(12); rrect(ctx, -w / 2, -size * .95, w, size * 1.3, 18); ctx.stroke()
    T(ctx, s, 0, size * .32, size, c, F_BLACK, a=a)
    ctx.restore()

def counter(ctx, v, x, y, size, c, a=1, suffix=''):
    T(ctx, fmt_int(int(v)) + suffix, x, y, size, c, F_BLACK, a=a, outline=16)

# fondo: degradado + rejilla + partículas + viñeta + grano
RND = random.Random(7)
DUST = [(RND.uniform(0, SW), RND.uniform(0, SH), RND.uniform(1.5, 4), RND.uniform(8, 30), RND.uniform(0, 6.28)) for _ in range(70)]
def background(ctx, t, tint=(0.04, 0.05, 0.07), dust=True):
    g = cairo.LinearGradient(0, 0, 0, SH)
    g.add_color_stop_rgb(0, *mix(tint, (0, 0, 0), .2)); g.add_color_stop_rgb(.5, *tint); g.add_color_stop_rgb(1, *mix(tint, (0, 0, 0), .5))
    ctx.set_source(g); ctx.paint()
    ctx.set_line_width(1); col(ctx, (1, 1, 1), .025)
    for x in range(0, SW + 1, 90): ctx.move_to(x + .5, 0); ctx.line_to(x + .5, SH)
    for y in range(0, SH + 1, 90): ctx.move_to(0, y + .5); ctx.line_to(SW, y + .5)
    ctx.stroke()
    if dust:
        for x, y, r, sp, ph in DUST:
            yy = (y - t * sp) % SH; xx = x + 14 * math.sin(t * .7 + ph)
            col(ctx, AMBER, .10 + .08 * math.sin(t * 2 + ph)); ctx.arc(xx, yy, r, 0, 2 * math.pi); ctx.fill()

_GRAIN = []
def grain_surfaces():
    if not _GRAIN:
        r = np.random.default_rng(3)
        for _ in range(4):
            n = (r.random((SH // 2, SW // 2)) * 255).astype(np.uint8)
            a = np.dstack([n, n, n, np.full_like(n, 255)]).copy()
            _GRAIN.append((cairo.ImageSurface.create_for_data(memoryview(a), cairo.FORMAT_RGB24, SW // 2, SH // 2), a))
    return _GRAIN

def overlay(ctx, t):
    g = cairo.RadialGradient(SW / 2, SH * .45, SH * .25, SW / 2, SH * .45, SH * .75)
    g.add_color_stop_rgba(0, 0, 0, 0, 0); g.add_color_stop_rgba(1, 0, 0, 0, .65)
    ctx.set_source(g); ctx.paint()
    gs = grain_surfaces()[int(t * 24) % 4][0]
    ctx.save(); ctx.scale(2, 2); ctx.set_source_surface(gs, 0, 0); ctx.paint_with_alpha(.045); ctx.restore()
