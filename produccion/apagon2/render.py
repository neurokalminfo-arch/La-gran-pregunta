"""Short v2 '¿Y si mañana hubiera otro apagón?' — 9:16, animación con código, karaoke por palabra,
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
HL = re.compile(r'(luz|pasó|oscuras|chile|semáforos|ciento|dieciséis|diez|tarjeta|rápido|cincuenta|corazón|igualado|golpe|otra|setenta|dos|horas|agua|radio|linterna|efectivo|medicinas|batería|tres|kit|internet|gran|pregunta)', re.I)

# impactos: (tiempo, fuerza de sacudida, destello)
BLACKOUT = wt('city', 'país', True)
IMPACTS = [(BLACKOUT, 26, .85), (wt('yapaso', 'pasó'), 22, .35), (wt('iberia', 'oscuras'), 10, 0), (wt('chile', 'oscuras'), 10, 0),
           (wt('train', 'parados'), 14, 0), (wt('shops', 'diez'), 10, 0), (wt('why', 'rápido'), 12, .15),
           (wt('chain', 'golpe'), 16, .2), (wt('eu', 'horas'), 12, 0), (wt('days', 'tres'), 20, .25)]

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

# ------------------------------------------------------------------ ESCENAS  (t = tiempo absoluto, s0/d = fase)
def city_layer(ctx, base, seed, lit, c, hmin, hmax, wmin, wmax, win=AMBER):
    r = random.Random(seed); x = -40
    while x < SW + 40:
        w = r.randint(wmin, wmax); h = r.randint(hmin, hmax)
        col(ctx, c); ctx.rectangle(x, base - h, w - 8, h + 400); ctx.fill()
        if r.random() < .3: ctx.rectangle(x + w * .4, base - h - 60, 8, 60); ctx.fill()
        for wy in range(int(base - h + 30), int(base - 20), 44):
            for wx in range(int(x + 16), int(x + w - 30), 34):
                v = r.random()
                if v < .45 and lit > 0:
                    col(ctx, win, lit * (.45 + .5 * r.random())); ctx.rectangle(wx, wy, 14, 22); ctx.fill()
        x += w

def sky_city(ctx, t, lit, dark):
    sky = cairo.LinearGradient(0, 0, 0, 1500)
    sky.add_color_stop_rgb(0, *mix(hexc('#22355A'), DARK, dark)); sky.add_color_stop_rgb(1, *mix(hexc('#6A4228'), DARK, dark))
    ctx.set_source(sky); ctx.paint()
    if dark < 1: glow(ctx, SW / 2, 1300, 800, AMBER, .3 * (1 - dark))
    col(ctx, (1, 1, 1), .5 * (1 - dark) + .15)
    r = random.Random(5)
    for _ in range(40): ctx.arc(r.uniform(0, SW), r.uniform(200, 700), r.uniform(1, 2.5), 0, 2 * math.pi); ctx.fill()
    city_layer(ctx, 1380, 4, lit * .7, hexc('#1B2433'), 350, 760, 110, 200)
    city_layer(ctx, 1500, 9, lit, hexc('#0B0F15'), 200, 520, 140, 260)

def sc_city(ctx, t, s0, d):
    off = t >= BLACKOUT
    flick = 1.0 if t < BLACKOUT - .5 else (0.3 + .7 * (int(t * 22) % 3 != 0) if not off else 0)
    sky_city(ctx, t, flick, 1.0 if off else 0.0)
    k1 = popk(t, s0 + .05, .4); k2 = popk(t, wt('city', 'luz'), .35)
    scaled(ctx, SW / 2, 360, k1, lambda: T(ctx, "¿Y SI MAÑANA", 0, 0, 108, INK, outline=16))
    scaled(ctx, SW / 2, 500, k2, lambda: T(ctx, "SE VA LA LUZ?", 0, 0, 124, AMBER if not off else RED, outline=16))
    if off:  # chispas cayendo tras el apagón
        q = t - BLACKOUT
        r = random.Random(2)
        for _ in range(40):
            x0, vy, vx = r.uniform(100, 980), r.uniform(200, 700), r.uniform(-200, 200)
            y = 900 + vy * q - 0 + 900 * q * q * .6; x = x0 + vx * q
            if y < SH: col(ctx, AMBER, max(0, 1 - q * 1.5)); ctx.arc(x, y, 4, 0, 2 * math.pi); ctx.fill()

def sc_yapaso(ctx, t, s0, d):
    sky_city(ctx, t, 0, 1)
    k = clamp((t - s0) / .3)
    T(ctx, "NO ES UNA HIPÓTESIS", SW / 2, 420, 64, MUTED, F_XB, a=k, outline=10)
    stamp(ctx, "YA PASÓ", SW / 2, 760, t, wt('yapaso', 'pasó'), RED, 125)

IB = Proj(-10, 3.6, 35.7, 44.0, 40, 330, 1000, 1000)
CITIES_IB = [(-3.7, 40.4, "Madrid"), (2.17, 41.39, "Barcelona"), (-9.14, 38.72, "Lisboa"), (-5.98, 37.39, "Sevilla"),
             (-0.38, 39.47, "Valencia"), (-2.93, 43.26, "Bilbao"), (-8.61, 41.15, "Oporto"), (-1.13, 37.99, "Murcia"), (-4.42, 36.72, "Málaga")]
def lit_map(ctx, Pj, isos, t, t_off, origin, speed, cities, others=OFF):
    """Mapa iluminado que se apaga con una onda desde `origin` (lon, lat)."""
    draw_map(ctx, Pj, {i: (OFF, 1) for i in isos}, base=hexc('#10141A'), edge=hexc('#1E2530'))
    ox, oy = Pj(*origin); R = max(0, (t - t_off) * speed)
    ctx.save()
    for iso in isos:
        for poly in geo_polys(iso):
            for i, (lo, la) in enumerate(poly[0]):
                x, y = Pj(lo, la); (ctx.move_to if i == 0 else ctx.line_to)(x, y)
            ctx.close_path()
    ctx.clip()
    col(ctx, AMBER); ctx.paint()
    g = cairo.RadialGradient(ox, oy, max(R - 160, 0), ox, oy, R + 1)
    g.add_color_stop_rgba(0, *OFF, 1); g.add_color_stop_rgba(.85, *OFF, 1); g.add_color_stop_rgba(1, *OFF, 0)
    if R > 0: ctx.set_source(g); ctx.arc(ox, oy, R + 1, 0, 2 * math.pi); ctx.fill()
    ctx.restore()
    for lo, la, n in cities:
        x, y = Pj(lo, la); on = math.hypot(x - ox, y - oy) > R
        if on: glow(ctx, x, y, 40, (1, 1, .85), .9); col(ctx, (1, 1, .9)); ctx.arc(x, y, 7, 0, 2 * math.pi); ctx.fill()
        else: col(ctx, hexc('#2C343F')); ctx.arc(x, y, 6, 0, 2 * math.pi); ctx.fill()

from lib import geo
def geo_polys(iso): return geo().get(iso, [])

def sc_iberia(ctx, t, s0, d):
    background(ctx, t)
    z = lerp(1.0, 1.08, clamp((t - s0) / d))
    ctx.save(); ctx.translate(SW / 2, 830); ctx.scale(z, z); ctx.translate(-SW / 2, -830)
    lit_map(ctx, IB, ['ESP', 'PRT'], t, wt('iberia', 'oscuras') - .1, (-5.5, 36.5), 900, CITIES_IB)
    ctx.restore()
    tag(ctx, "28 DE ABRIL DE 2025", SW / 2, 330, clamp((t - s0) / .3), AMBER, 52)
    k = clamp((t - wt('iberia', 'segundos')) / .25)
    if k > 0:
        T(ctx, "EN SEGUNDOS", SW / 2, 1320, 96, RED, a=k, outline=14)

CH = Proj(-80, -60, -56, -17, 140, 300, 800, 1100)
CITIES_CL = [(-70.4, -23.65, "Antofagasta"), (-70.65, -33.45, "Santiago"), (-71.62, -33.05, "Valparaíso"), (-73.05, -36.82, "Concepción"),
             (-72.6, -38.74, "Temuco"), (-70.3, -18.48, "Arica"), (-73.25, -39.81, "Valdivia"), (-73.13, -40.57, "Osorno")]
def sc_chile(ctx, t, s0, d):
    background(ctx, t)
    lit_map(ctx, CH, ['CHL'], t, wt('chile', 'oscuras') - .3, (-70, -15), 750, CITIES_CL)
    tag(ctx, "FEBRERO 2025", 300, 330, clamp((t - s0) / .3), AMBER, 52)
    k = clamp((t - wt('chile', 'país')) / .3)
    if k > 0:
        v = 98 * eout(clamp((t - wt('chile', 'país')) / .8))
        T(ctx, f"{int(v)} %", 790, 860, 170, RED, a=k, outline=16)
        T(ctx, "DEL PAÍS", 790, 950, 56, INK, F_XB, a=k, outline=10)
        T(ctx, "SIN LUZ", 790, 1020, 56, INK, F_XB, a=k, outline=10)

def sc_traffic(ctx, t, s0, d):
    background(ctx, t, dust=False)
    off = t > wt('traffic', 'apagados') - .1
    # coches en atasco
    for i in range(7):
        x = (-200 + i * 190 + 150 * clamp((t - s0) / 1.2)) % (SW + 300) - 150; y = 1290
        col(ctx, hexc('#232B36')); rrect(ctx, x, y, 160, 70, 20); ctx.fill()
        glow(ctx, x + 150, y + 40, 40, AMBER, .5); col(ctx, (1, .9, .6)); ctx.arc(x + 152, y + 40, 7, 0, 2 * math.pi); ctx.fill()
    col(ctx, LINE); ctx.rectangle(SW / 2 - 14, 950, 28, 360); ctx.fill()
    s = popk(t, s0, .35)
    def body():
        col(ctx, hexc('#1E2530')); rrect(ctx, -150, -380, 300, 760, 60); ctx.fill()
        for i, c in enumerate((RED, AMBER, GREEN)):
            on = (not off) and (int(t * 3) % 3 == i)
            if on: glow(ctx, 0, -240 + i * 240, 160, c, .8)
            col(ctx, c if on else hexc('#2C343F')); ctx.arc(0, -240 + i * 240, 95, 0, 2 * math.pi); ctx.fill()
    scaled(ctx, SW / 2, 620, s * .85, body)
    if off:
        T(ctx, "OFF", SW / 2 + 260, 420, 90, RED, a=clamp((t - wt('traffic', 'apagados')) / .2), outline=12)

def sc_train(ctx, t, s0, d):
    background(ctx, t, dust=False)
    q = clamp((t - s0) / 1.4); x = lerp(SW + 100, 60, 1 - (1 - q) ** 3)
    col(ctx, MUTED); ctx.set_line_width(8); ctx.move_to(0, 1205); ctx.line_to(SW, 1205); ctx.stroke()
    for xx in range(-20, SW, 60): ctx.set_line_width(10); col(ctx, hexc('#2A2018')); ctx.move_to(xx, 1215); ctx.line_to(xx + 30, 1215); ctx.stroke()
    def wagon(x0):
        col(ctx, hexc('#C9D2DC')); rrect(ctx, x0, 960, 900, 230, 50); ctx.fill()
        col(ctx, RED); ctx.rectangle(x0, 1120, 900, 22); ctx.fill()
        for i in range(6): col(ctx, hexc('#0E1218')); rrect(ctx, x0 + 60 + i * 135, 1000, 100, 80, 12); ctx.fill()
    wagon(x); wagon(x + 920)
    if 0 < q < 1:  # chispas de frenada
        r = random.Random(int(t * 30))
        for _ in range(25):
            sx = x + r.uniform(40, 300); sy = 1200 - r.uniform(0, 30)
            col(ctx, AMBER, r.uniform(.5, 1)); ctx.set_line_width(3); ctx.move_to(sx, sy); ctx.line_to(sx + r.uniform(30, 90), sy - r.uniform(10, 60)); ctx.stroke()
    t0 = wt('train', 'Ciento')
    v = 116 * eout(clamp((t - t0) / 1.0))
    if t > t0: counter(ctx, v, SW / 2, 640, 300, AMBER)
    k = clamp((t - wt('train', 'parados')) / .3)
    if k > 0: T(ctx, "TRENES PARADOS", SW / 2, 780, 76, INK, F_XB, a=k, outline=12)

def terminal(ctx, ok, k):
    col(ctx, hexc('#2A3442')); rrect(ctx, -70, -110, 140, 220, 22); ctx.fill()
    col(ctx, hexc('#0E1218')); rrect(ctx, -52, -90, 104, 66, 8); ctx.fill()
    for r_ in range(3):
        for c_ in range(3): col(ctx, hexc('#3A4658')); rrect(ctx, -48 + c_ * 34, 0 + r_ * 32, 26, 22, 5); ctx.fill()
    if k > 0:
        c = GREEN if ok else RED
        col(ctx, c, k); ctx.set_line_width(12); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        if ok: ctx.move_to(-40, -10); ctx.line_to(-8, 25); ctx.line_to(50, -50)
        else: ctx.move_to(-45, -45); ctx.line_to(45, 45); ctx.move_to(45, -45); ctx.line_to(-45, 45)
        ctx.stroke(); ctx.set_line_cap(cairo.LINE_CAP_BUTT)

def sc_shops(ctx, t, s0, d):
    background(ctx, t)
    t1 = wt('shops', 'diez')
    for i in range(10):
        r, c = divmod(i, 5); x = 140 + c * 200; y = 520 + r * 300
        ok = i == 6
        tk = clamp((t - (t1 + .08 * i)) / .2)
        scaled(ctx, x, y, popk(t, s0 + .05 * i, .3) * (1.12 if ok and tk > 0 else 1), lambda: terminal(ctx, ok, tk))
    k = clamp((t - wt('shops', 'tarjeta')) / .3)
    if k > 0:
        T(ctx, "1 DE 10", SW / 2, 1230, 150, GREEN, a=k, outline=16)
        T(ctx, "PODÍA COBRAR CON TARJETA", SW / 2, 1310, 50, INK, F_XB, a=k, outline=10)
    T(ctx, "Fuente: CaixaBank Research", SW / 2, 1400, 26, MUTED, F_SEMI, a=.8)

def sc_why(ctx, t, s0, d):
    background(ctx, t)
    q = clamp((t - s0) / d)
    for i in range(36):  # rayos que convergen
        a = i * math.pi / 18 + t * .6; r0 = lerp(900, 300, q)
        col(ctx, AMBER, .12); ctx.set_line_width(6)
        ctx.move_to(SW / 2 + r0 * math.cos(a), 800 + r0 * math.sin(a)); ctx.line_to(SW / 2 + (r0 + 240) * math.cos(a), 800 + (r0 + 240) * math.sin(a)); ctx.stroke()
    s = lerp(.3, 1.15, eout(q)); ctx.save(); ctx.translate(SW / 2, 800); ctx.rotate(lerp(-.4, 0, eout(q))); ctx.scale(s, s)
    glow(ctx, 0, 0, 380, AMBER, .5); T(ctx, "?", 0, 220, 640, AMBER, outline=20); ctx.restore()

def ecg_y(x, t, chaos=0.0):
    """onda: latido regular (50 Hz estilizado) que con `chaos` se vuelve errática."""
    ph = (x / 260 - t * 1.6) % 1.0
    beat = 0
    if .40 < ph < .44: beat = -(ph - .40) / .04
    elif .44 < ph < .50: beat = -1 + 2.4 * (ph - .44) / .06
    elif .50 < ph < .55: beat = 1.4 - 1.4 * (ph - .50) / .05
    y = beat * 160 + 10 * math.sin(x / 30 + t * 4)
    if chaos: y += chaos * (130 * math.sin(x / 17 + t * 23) * math.sin(x / 41 - t * 7))
    return y

def draw_ecg(ctx, t, y0, c, chaos=0.0, flat=0.0, a=1):
    glow(ctx, SW * .85, y0, 160, c, .3 * a)
    ctx.set_line_width(9); ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    for x in range(0, SW + 10, 6):
        y = y0 + ecg_y(x, t, chaos) * (1 - flat)
        (ctx.move_to if x == 0 else ctx.line_to)(x, y)
    col(ctx, c, a); ctx.stroke()

def sc_heart(ctx, t, s0, d):
    background(ctx, t, dust=False)
    draw_ecg(ctx, t, 1060, GREEN)
    beat = (t * 1.6) % 1.0; pulse = 1 + .12 * math.exp(-((beat - .45) * 14) ** 2)
    k = popk(t, wt('heart', 'cincuenta'), .35)
    scaled(ctx, SW / 2, 640, k * pulse, lambda: (T(ctx, "50", 0, 0, 330, GREEN, outline=18)))
    scaled(ctx, SW / 2, 760, k, lambda: T(ctx, "VECES POR SEGUNDO", 0, 0, 58, INK, F_XB, outline=10))
    def heart():
        col(ctx, RED); ctx.move_to(0, 40)
        ctx.curve_to(-120, -40, -60, -130, 0, -60); ctx.curve_to(60, -130, 120, -40, 0, 40); ctx.fill()
    scaled(ctx, SW / 2, 400, popk(t, wt('heart', 'corazón'), .3) * pulse * 1.4, heart)

def balance(ctx, t, tilt, k=1):
    cx, cy = SW / 2, 700
    col(ctx, LINE, k); ctx.move_to(cx - 90, 1300); ctx.line_to(cx + 90, 1300); ctx.line_to(cx, cy); ctx.close_path(); ctx.fill()
    ctx.save(); ctx.translate(cx, cy); ctx.rotate(tilt)
    col(ctx, INK, k); ctx.set_line_width(18); ctx.move_to(-360, 0); ctx.line_to(360, 0); ctx.stroke()
    for sx, lab, c, ic in ((-1, "PRODUCCIÓN", AMBER, 'f'), (1, "CONSUMO", BLUE, 'h')):
        ctx.save(); ctx.translate(sx * 340, 0); ctx.rotate(-tilt)
        col(ctx, MUTED, k); ctx.set_line_width(5); ctx.move_to(0, 0); ctx.line_to(-130, 260); ctx.move_to(0, 0); ctx.line_to(130, 260); ctx.stroke()
        col(ctx, c, k); ctx.save(); ctx.translate(0, 268); ctx.scale(1, .22); ctx.arc(0, 0, 170, 0, math.pi); ctx.restore(); ctx.fill()
        if ic == 'f':  # fábrica/central
            col(ctx, c, k); ctx.rectangle(-70, 170, 140, 90); ctx.fill(); ctx.rectangle(-50, 100, 34, 80); ctx.fill(); ctx.rectangle(16, 120, 34, 60); ctx.fill()
        else:  # casa
            col(ctx, c, k); ctx.rectangle(-60, 180, 120, 80); ctx.fill(); ctx.move_to(-80, 182); ctx.line_to(0, 110); ctx.line_to(80, 182); ctx.close_path(); ctx.fill()
        T(ctx, lab, 0, 380, 44, c, F_XB, a=k, outline=8)
        ctx.restore()
    ctx.restore()

def sc_balance(ctx, t, s0, d):
    background(ctx, t)
    balance(ctx, t, .035 * math.sin(t * 2.6), popk(t, s0, .3))
    k = clamp((t - wt('balance', 'igualado')) / .3)
    if k > 0: T(ctx, "=", SW / 2, 560, 200, GREEN, a=k, outline=14)

PLANTS = [(170 + (i % 4) * 250, 520 + (i // 4) * 270) for i in range(12)]
def plant_icon(ctx, on, k):
    c = AMBER if on else hexc('#2C343F')
    col(ctx, c); ctx.move_to(-45, 70); ctx.line_to(-32, -70); ctx.line_to(32, -70); ctx.line_to(45, 70); ctx.close_path(); ctx.fill()
    col(ctx, hexc('#0E1218')); ctx.rectangle(-60, 60, 120, 20); ctx.fill()
    if on:
        for j in range(3): col(ctx, (1, 1, 1), .25); ctx.arc(-10 + j * 14, -90 - j * 22 - (k * 20 % 20), 16 + j * 5, 0, 2 * math.pi); ctx.fill()

def sc_chain(ctx, t, s0, d):
    background(ctx, t, tint=(0.07, 0.03, 0.03))
    tg = wt('chain', 'golpe')
    if t < tg + .6:  # la balanza se desploma: cae la producción (sube su platillo)
        q = eout(clamp((t - tg + .25) / .6))
        ctx.save(); ctx.push_group()
        balance(ctx, t, lerp(0, .38, q) + .06 * math.sin(t * 30) * q)
        ctx.pop_group_to_source(); ctx.paint_with_alpha(1 - clamp((t - tg - .2) / .4)); ctx.restore()
    else:
        t1 = wt('chain', 'desconectan')
        for i, (x, y) in enumerate(PLANTS):
            toff = t1 + .25 * i; on = t < toff
            scaled(ctx, x, y, popk(t, tg + .4 + .03 * i, .3), lambda: plant_icon(ctx, on, t))
            if not on and t - toff < .25: glow(ctx, x, y, 140, RED, 1 - (t - toff) / .25)
        draw_ecg(ctx, t, 1330, RED, chaos=clamp((t - t1) / 1.5), flat=clamp((t - (t1 + 2.6)) / .5), a=.9)

def star(ctx, x, y, r):
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5; rr = r if i % 2 == 0 else r * .42
        (ctx.move_to if i == 0 else ctx.line_to)(x + rr * math.cos(a), y + rr * math.sin(a))
    ctx.close_path(); ctx.fill()

def sc_eu(ctx, t, s0, d):
    background(ctx, t, tint=(0.02, 0.04, 0.10))
    cx, cy = SW / 2, 800
    for i in range(12):
        a = -math.pi / 2 + i * math.pi / 6 + .3 * (1 - eout(clamp((t - s0) / 1.0)))
        k = popk(t, s0 + .05 * i, .3); col(ctx, AMBER)
        if k > 0: ctx.save(); ctx.translate(cx + 400 * math.cos(a), cy + 400 * math.sin(a)); ctx.scale(k, k); star(ctx, 0, 0, 36); ctx.restore()
    th = wt('eu', 'setenta')
    q = clamp((t - th) / 1.4)
    col(ctx, AMBER, .25); ctx.move_to(cx, cy); ctx.arc(cx, cy, 320, -math.pi / 2, -math.pi / 2 + 2 * math.pi * q * 3 % (2 * math.pi) + 1e-3); ctx.close_path(); ctx.fill()
    if t > th - .2: counter(ctx, 72 * eout(q), cx, cy + 90, 300, INK)
    T(ctx, "HORAS", cx, cy + 200, 80, AMBER, F_XB, a=clamp((t - wt('eu', 'horas')) / .2), outline=10)
    T(ctx, "UNIÓN EUROPEA", cx, 300, 60, INK, F_XB, a=clamp((t - s0) / .3), outline=10)

# ---- kit
def ic_water(ctx):
    col(ctx, BLUE); rrect(ctx, -60, -120, 120, 240, 30); ctx.fill(); ctx.rectangle(-26, -165, 52, 50); ctx.fill()
    col(ctx, (1, 1, 1), .35); rrect(ctx, -40, -80, 22, 150, 10); ctx.fill()
def ic_can(ctx):
    col(ctx, AMBER); rrect(ctx, -95, -100, 190, 200, 24); ctx.fill(); col(ctx, BG); ctx.rectangle(-95, -25, 190, 50); ctx.fill()
def ic_radio(ctx):
    col(ctx, hexc('#C9D2DC')); rrect(ctx, -130, -80, 260, 170, 24); ctx.fill(); col(ctx, BG); ctx.arc(-50, 5, 50, 0, 2 * math.pi); ctx.fill()
    col(ctx, AMBER); rrect(ctx, 20, -40, 80, 30, 6); ctx.fill(); col(ctx, INK); ctx.set_line_width(7); ctx.move_to(70, -80); ctx.line_to(120, -190); ctx.stroke()
def ic_torch(ctx):
    col(ctx, AMBER, .35); ctx.move_to(60, -45); ctx.line_to(240, -130); ctx.line_to(240, 130); ctx.line_to(60, 45); ctx.close_path(); ctx.fill()
    col(ctx, INK); rrect(ctx, -170, -40, 240, 80, 18); ctx.fill(); rrect(ctx, 40, -60, 50, 120, 12); ctx.fill()
def ic_cash(ctx):
    for i in range(3):
        col(ctx, mix(GREEN, BG, .25 * i)); rrect(ctx, -130 + i * 14, -70 - i * 18, 260, 140, 14); ctx.fill()
    T(ctx, "€", 28, 30, 110, BG, F_BLACK)
def ic_meds(ctx):
    col(ctx, INK); rrect(ctx, -110, -90, 220, 180, 26); ctx.fill()
    col(ctx, RED); ctx.rectangle(-22, -60, 44, 120); ctx.fill(); ctx.rectangle(-60, -22, 120, 44); ctx.fill()
def ic_batt(ctx):
    col(ctx, INK); ctx.set_line_width(12); rrect(ctx, -130, -65, 240, 130, 18); ctx.stroke(); ctx.rectangle(112, -26, 24, 52); ctx.fill()
    col(ctx, GREEN); ctx.rectangle(-112, -47, 205, 94); ctx.fill()
KIT = [('agua', ic_water, "AGUA"), ('comida', ic_can, "COMIDA"), ('radio', ic_radio, "RADIO A PILAS"), ('linterna', ic_torch, "LINTERNA"),
       ('efectivo', ic_cash, "EFECTIVO"), ('medicinas', ic_meds, "MEDICINAS"), ('batería', ic_batt, "BATERÍA")]

def backpack(ctx, k=1):
    col(ctx, hexc('#3A2A1E'), k); rrect(ctx, -230, -260, 460, 520, 90); ctx.fill()
    col(ctx, hexc('#4A3626'), k); rrect(ctx, -170, -40, 340, 200, 40); ctx.fill()
    col(ctx, hexc('#2A1E14'), k); ctx.set_line_width(26); ctx.arc(0, -260, 110, math.pi, 2 * math.pi); ctx.stroke()

def sc_kit(ctx, t, s0, d):
    background(ctx, t)
    scaled(ctx, SW / 2, 1150, popk(t, s0, .35) * .8, lambda: backpack(ctx))
    times = [wt('kit', key) for key, _, _ in KIT]
    n_in = 0; hero = None
    for i, (key, fn, lab) in enumerate(KIT):
        t0 = times[i]; t1 = times[i + 1] if i + 1 < len(KIT) else t0 + 1.2
        if t < t0: continue
        if t < t1 - .15: hero = (t0, fn, lab); continue
        q = clamp((t - (t1 - .15)) / .3)
        if q < 1:  # vuela a la mochila (detrás del protagonista)
            x = SW / 2 + 60 * math.sin(i); y = lerp(620, 1100, q * q); s = lerp(1.0, .25, q)
            ctx.push_group(); scaled(ctx, x, y, s, lambda: fn(ctx)); ctx.pop_group_to_source(); ctx.paint_with_alpha(1 - q * .6)
        n_in += 1
    if hero:
        t0, fn, lab = hero
        scaled(ctx, SW / 2, 620, popk(t, t0, .3) * 1.25, lambda: fn(ctx))
        T(ctx, lab, SW / 2, 900, 84, AMBER, a=clamp((t - t0) / .15), outline=14)
    if n_in:
        T(ctx, f"{n_in}/7", SW / 2 + 260, 1320, 70, GREEN, a=1, outline=10)
    T(ctx, "TU KIT · 72 H", SW / 2, 330, 70, INK, F_XB, a=clamp((t - s0) / .3), outline=10)

def calendar(ctx, n, c):
    col(ctx, PANEL); rrect(ctx, -280, -320, 560, 640, 40); ctx.fill()
    col(ctx, c); rrect(ctx, -280, -320, 560, 150, 40); ctx.fill(); ctx.rectangle(-280, -230, 560, 60); ctx.fill()
    for x in (-140, 140): col(ctx, INK); rrect(ctx, x - 16, -360, 32, 90, 14); ctx.fill()
    T(ctx, str(n), 0, 220, 380, c if n == 3 else INK, F_BLACK)

def sc_days(ctx, t, s0, d):
    background(ctx, t, tint=(0.06, 0.03, 0.03) if t > wt('days', 'tres') else (0.04, 0.05, 0.07))
    tf = wt('days', 'tres') - .15
    if t < tf:
        scaled(ctx, SW / 2, 820, popk(t, s0, .35), lambda: calendar(ctx, 1, GREEN))
        T(ctx, "1 DÍA", SW / 2, 1290, 100, GREEN, a=clamp((t - s0) / .3), outline=12)
    else:
        q = clamp((t - tf) / .25)
        ctx.save(); ctx.translate(SW / 2, 820); ctx.scale(1, max(.02, abs(math.cos(q * math.pi)))); ctx.translate(-SW / 2, -820)
        calendar_n = 1 if q < .5 else 3
        ctx.translate(SW / 2, 820); calendar(ctx, calendar_n, GREEN if calendar_n == 1 else RED); ctx.restore()
        if q >= .5: T(ctx, "¿3 DÍAS?", SW / 2, 1290, 110, RED, a=1, outline=14)

def sc_comment(ctx, t, s0, d):
    background(ctx, t)
    k = popk(t, s0, .4)
    def bubble():
        col(ctx, PANEL); rrect(ctx, -440, -200, 880, 400, 50); ctx.fill()
        col(ctx, AMBER); ctx.set_line_width(6); rrect(ctx, -440, -200, 880, 400, 50); ctx.stroke()
        col(ctx, PANEL); ctx.move_to(-300, 195); ctx.line_to(-180, 195); ctx.line_to(-330, 320); ctx.close_path(); ctx.fill()
        T(ctx, "¿TIENES", 0, -30, 130, INK)
        T(ctx, "TU KIT?", 0, 120, 140, AMBER)
    scaled(ctx, SW / 2, 700, k, bubble)
    tc = wt('comment', 'comentarios')
    if t > tc - .3:  # escribiendo…
        for i in range(3):
            a = .4 + .6 * abs(math.sin(t * 6 - i * .7))
            col(ctx, INK, a); ctx.arc(SW / 2 - 60 + i * 60, 1120, 18, 0, 2 * math.pi); ctx.fill()
        col(ctx, PANEL); rrect(ctx, SW / 2 - 130, 1070, 260, 100, 50); ctx.set_line_width(4); col(ctx, MUTED); ctx.stroke()
        def heart():
            col(ctx, RED); ctx.move_to(0, 40); ctx.curve_to(-120, -40, -60, -130, 0, -60); ctx.curve_to(60, -130, 120, -40, 0, 40); ctx.fill()
        scaled(ctx, SW / 2 + 330, 1050, popk(t, tc, .3) * .9, heart)

def sc_cta(ctx, t, s0, d):
    background(ctx, t, tint=(0.03, 0.04, 0.08))
    k = popk(t, s0, .4)
    def card():
        col(ctx, PANEL); rrect(ctx, -460, -330, 920, 660, 40); ctx.fill()
        col(ctx, AMBER); ctx.set_line_width(6); rrect(ctx, -460, -330, 920, 660, 40); ctx.stroke()
        # wifi tachado
        for i, r in enumerate((60, 120, 180)):
            col(ctx, INK); ctx.set_line_width(26); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
            ctx.arc(0, 30, r, math.radians(225), math.radians(315)); ctx.stroke()
        col(ctx, INK); ctx.arc(0, 30, 22, 0, 2 * math.pi); ctx.fill()
        col(ctx, RED); ctx.set_line_width(30); ctx.move_to(-170, -170); ctx.line_to(170, 120); ctx.stroke(); ctx.set_line_cap(cairo.LINE_CAP_BUTT)
        T(ctx, "30 DÍAS SIN INTERNET", 0, 230, 70, AMBER, F_BLACK, maxw=820)
    scaled(ctx, SW / 2, 700, k, card)
    k2 = clamp((t - wt('cta', 'canal')) / .3)
    if k2 > 0:
        col(ctx, AMBER, k2); ctx.arc(250, 1230, 64, 0, 2 * math.pi); ctx.fill()
        T(ctx, "?", 250, 1262, 92, BG, F_BLACK, a=k2)
        T(ctx, "LA GRAN PREGUNTA", 340, 1258, 64, INK, F_BLACK, 'l', k2, maxw=660, outline=8)
        pulse = 1 + .05 * math.sin(t * 8)
        scaled(ctx, SW / 2, 1390, pulse * k2, lambda: (col(ctx, RED), rrect(ctx, -250, -55, 500, 110, 55), ctx.fill(), T(ctx, "SUSCRÍBETE", 0, 20, 54, INK, F_BLACK)))

SCENES = {'city': sc_city, 'yapaso': sc_yapaso, 'iberia': sc_iberia, 'chile': sc_chile, 'traffic': sc_traffic, 'train': sc_train,
          'shops': sc_shops, 'why': sc_why, 'heart': sc_heart, 'balance': sc_balance, 'chain': sc_chain, 'eu': sc_eu,
          'kit': sc_kit, 'days': sc_days, 'comment': sc_comment, 'cta': sc_cta}

# ------------------------------------------------------------------ captions karaoke
def captions(ctx, t):
    if t < PH[1][1]: return       # en el gancho manda el texto grande
    for ch in CHUNKS:
        a, b = ch[0][1], ch[-1][2] + .25
        if a - .05 <= t < b:
            font(ctx, F_BLACK, 84); sp = 32
            ws = [w[0].upper() for w in ch]; widths = [ctx.text_extents(w).x_advance for w in ws]
            tot = sum(widths) + sp * (len(ws) - 1); scale = min(1, 980 / tot)
            k = eout(clamp((t - a + .05) / .12))
            ctx.save(); ctx.translate(SW / 2, 1600); ctx.scale(scale * (.9 + .1 * k), scale * (.9 + .1 * k))
            x = -tot / 2
            for (w, wa, wb, _), s, wd in zip(ch, ws, widths):
                cur = wa <= t < wb + .08
                c = AMBER if cur else INK
                if cur:
                    ctx.save(); ctx.translate(x + wd / 2, -30); ctx.scale(1.06, 1.06); T(ctx, s, 0, 30, 84, c, F_BLACK, 'c', k, maxw=0, outline=16); ctx.restore()
                else:
                    T(ctx, s, x, 0, 84, c if wa <= t else mix(c, (0.6, 0.6, 0.6), .3), F_BLACK, 'l', k, maxw=0, outline=16)
                x += wd + sp
            ctx.restore()
            return

# ------------------------------------------------------------------ cuadro completo
def cam(t):
    sx = sy = 0.0; flash = 0.0
    for ti, amp, fl in IMPACTS:
        if t >= ti:
            e = math.exp(-(t - ti) * 9)
            sx += amp * e * math.sin((t - ti) * 71); sy += amp * e * math.cos((t - ti) * 53)
            if fl: flash = max(flash, fl * math.exp(-(t - ti) * 10))
    return sx, sy, flash

def frame(ctx, t):
    j = max(i for i, p in enumerate(PH) if p[1] <= t)
    k, s0, _, _, _, d = PH[j]
    sx, sy, flash = cam(t)
    zp = 1 + .07 * math.exp(-(t - s0) * 9) if j else 1   # punch-in en cada corte
    ctx.save(); ctx.translate(SW / 2 + sx, SH / 2 + sy); ctx.scale(zp, zp); ctx.translate(-SW / 2, -SH / 2)
    SCENES[k](ctx, t, s0, d)
    ctx.restore()
    if j and t - s0 < .12:  # barrido de luz en el corte
        q = (t - s0) / .12; x = lerp(-300, SW + 300, q)
        g = cairo.LinearGradient(x - 200, 0, x + 200, 0)
        g.add_color_stop_rgba(0, 1, 1, 1, 0); g.add_color_stop_rgba(.5, 1, 1, 1, .18); g.add_color_stop_rgba(1, 1, 1, 1, 0)
        ctx.set_source(g); ctx.paint()
    overlay(ctx, t)
    if flash > 0: col(ctx, (1, 1, 1), flash); ctx.paint()
    captions(ctx, t)
    T(ctx, "LA GRAN PREGUNTA", SW / 2, 150, 30, AMBER, F_XB, a=.9)
    col(ctx, AMBER); ctx.rectangle(0, SH - 12, SW * t / DUR, 12); ctx.fill()

# ------------------------------------------------------------------ audio: música + efectos sintetizados
SR = 48000
def env(n, a=.005, r=.2):
    t = np.arange(n) / SR
    return np.minimum(1, t / a) * np.exp(-t / r)

def place(buf, sig, t0, g=1.0):
    i = int(t0 * SR)
    if i >= len(buf): return
    n = min(len(sig), len(buf) - i); buf[i:i + n] += g * sig[:n]

def audio():
    n = int(DUR * SR); mus = np.zeros(n); sfx = np.zeros(n); rng = np.random.default_rng(1)
    bpm = 100; beat = 60 / bpm
    # zumbido eléctrico hasta el apagón
    tt = np.arange(int(BLACKOUT * SR)) / SR
    hum = (np.sin(2 * np.pi * 50 * tt) + .5 * np.sin(2 * np.pi * 100 * tt) + .25 * np.sin(2 * np.pi * 150 * tt)) * .12
    hum *= np.minimum(1, tt / .3); sfx[:len(hum)] += hum
    # música: bombo + bajo + hi-hat; se corta en el apagón y vuelve más oscura en 'iberia'
    def kick():
        m = int(.35 * SR); t_ = np.arange(m) / SR; f = 50 + 90 * np.exp(-t_ * 35)
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t_ * 9)
    def hat():
        m = int(.06 * SR); return rng.standard_normal(m) * np.exp(-np.arange(m) / SR * 70) * .25
    def bass(freq, dur):
        m = int(dur * SR); t_ = np.arange(m) / SR
        return (np.sin(2 * np.pi * freq * t_) + .3 * np.sin(2 * np.pi * 2 * freq * t_)) * np.minimum(1, t_ / .02) * np.exp(-t_ * 2.2)
    seg = [(0.0, BLACKOUT, [55, 55, 65.4, 49]), (PH[2][1], DUR - .3, [43.65, 43.65, 49, 41.2])]
    for a, b, notes in seg:
        tb = a; i = 0
        while tb < b:
            place(mus, kick(), tb, .55)
            place(mus, hat(), tb + beat / 2, .5)
            if i % 2 == 0: place(mus, bass(notes[(i // 2) % 4], beat * 2), tb, .35)
            tb += beat; i += 1
    # 'pad' grave continuo desde iberia
    tt = np.arange(n) / SR; pad = .06 * (np.sin(2 * np.pi * 87.3 * tt) + np.sin(2 * np.pi * 130.8 * tt + 1) + .6 * np.sin(2 * np.pi * 174.6 * tt))
    pad *= (tt > PH[2][1]) * np.minimum(1, np.maximum(0, tt - PH[2][1]) / 2)
    mus += pad
    # fundido final
    fo = np.clip((DUR - tt) / 1.0, 0, 1); mus *= fo
    # efectos
    def thump(dur=.6, f0=60):
        m = int(dur * SR); t_ = np.arange(m) / SR; f = f0 + 80 * np.exp(-t_ * 20)
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t_ * 5)
    def click():
        m = int(.03 * SR); return rng.standard_normal(m) * np.exp(-np.arange(m) / SR * 200)
    def whoosh(dur=.3):
        m = int(dur * SR); w = rng.standard_normal(m); w = np.convolve(w, np.ones(30) / 30, 'same')
        t_ = np.arange(m) / m; return w * np.sin(np.pi * t_) ** 2 * 1.8
    def beep(f=1000, dur=.08):
        m = int(dur * SR); t_ = np.arange(m) / SR; return np.sin(2 * np.pi * f * t_) * np.minimum(1, t_ / .003) * np.exp(-t_ * 20)
    def crackle(dur=.25):
        m = int(dur * SR); x = np.zeros(m); idx = rng.integers(0, m, 60); x[idx] = rng.uniform(-1, 1, 60); return x
    place(sfx, click(), BLACKOUT, 1.0); place(sfx, thump(.9, 45), BLACKOUT, 1.3)
    for ti, amp, fl in IMPACTS[1:]: place(sfx, thump(.5, 55), ti, .7 * amp / 20)
    for p in PH[2:]: place(sfx, whoosh(), p[1] - .12, .35)
    s_h = next(p for p in PH if p[0] == 'heart'); tb = s_h[1] + .2
    while tb < s_h[1] + s_h[5]:
        place(sfx, beep(980), tb, .25); tb += 1 / 1.6
    t1 = wt('chain', 'desconectan')
    for i in range(12): place(sfx, click(), t1 + .25 * i, .6); place(sfx, crackle(), t1 + .25 * i, .35)
    tf = t1 + 2.6; place(sfx, beep(980, 1.2) * np.exp(-np.arange(int(1.2 * SR)) / SR * .5), tf, .25)   # 'línea plana'
    for key, _, _ in KIT: place(sfx, beep(660, .06), wt('kit', key), .25)
    # voz + ducking de la música
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', os.path.join(HERE, 'audio', 'voz.mp3'), '-ac', '1', '-ar', str(SR), '-f', 'f32le', '/tmp/_v.raw'], check=True)
    v = np.fromfile('/tmp/_v.raw', np.float32).astype(np.float64); voice = np.zeros(n); place(voice, v, V0)
    envv = np.convolve(np.abs(voice), np.ones(2400) / 2400, 'same'); duck = 1 - .55 * np.clip(envv / .05, 0, 1)
    mix_ = voice * 1.0 + mus * .22 * duck + sfx * .35
    mix_ /= max(1e-6, np.max(np.abs(mix_))) / .95
    st = np.stack([mix_, mix_], 1).astype(np.float32); st.tofile('/tmp/_m.raw')
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', '/tmp/_m.raw',
                    '-af', 'loudnorm=I=-14:TP=-1.5', '-ar', str(SR), os.path.join(HERE, 'audio', 'mezcla.wav')], check=True)
    print('audio ok', round(DUR, 1))

def stills(ts):
    from PIL import Image
    ims = []
    for t in ts:
        surf = cairo.ImageSurface(cairo.FORMAT_RGB24, SW, SH); ctx = cairo.Context(surf); frame(ctx, t)
        surf.write_to_png('/tmp/_s.png'); ims.append(Image.open('/tmp/_s.png').resize((216, 384)))
    cols = 8; S = Image.new('RGB', (216 * cols, 404 * ((len(ims) + cols - 1) // cols)), 'white')
    from PIL import ImageDraw; d = ImageDraw.Draw(S)
    for i, (im, t) in enumerate(zip(ims, ts)):
        x, y = (i % cols) * 216, (i // cols) * 404; S.paste(im, (x, y)); d.text((x + 4, y + 386), f'{t:.1f}s', fill='black')
    S.save(os.path.join(HERE, 'sheet.png'))

def video():
    out = os.path.join(HERE, 'out', 'short_apagon_v2_9x16.mp4'); nfr = int(DUR * FPS)
    enc = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgr0', '-s', f'{SW}x{SH}', '-r', str(FPS), '-i', '-',
                            '-i', os.path.join(HERE, 'audio', 'mezcla.wav'), '-map', '0:v', '-map', '1:a',
                            '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k',
                            '-shortest', '-movflags', '+faststart', out], stdin=subprocess.PIPE)
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, SW, SH); ctx = cairo.Context(surf); t0 = time.time()
    for f in range(nfr):
        frame(ctx, f / FPS); surf.flush(); enc.stdin.write(bytes(surf.get_data()))
    enc.stdin.close(); enc.wait(); print('video', out, round(time.time() - t0), 's')

if __name__ == '__main__':
    m = sys.argv[1]
    if m == 'stills':
        ts = [float(x) for x in sys.argv[2:]] or [p[1] + p[5] * .7 for p in PH]
        stills(ts)
    elif m == 'audio': audio()
    elif m == 'video': video()
    elif m == 'info':
        for p in PH: print(f'{p[0]:8s} {p[1]:6.2f} {p[5]:5.2f}')
        print('DUR', DUR, 'blackout', BLACKOUT)
