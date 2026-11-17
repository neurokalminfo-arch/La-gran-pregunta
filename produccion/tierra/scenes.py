"""Escenas: '¿Qué pasaría si la Tierra girara al revés?' — globo, mapas animados y fotos GPT."""
import sys, math, random, os, importlib.util
sys.path.append('/home/claude/video')
import cairo
import numpy as np
from lib import *
import narration

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location('iscenes', '/home/claude/internet/scenes.py')
I = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(I); I.HERE = HERE
photo, bottom_shade, left_shade, stamp, big, xmark, chip_card = I.photo, I.bottom_shade, I.left_shade, I.stamp, I.big, I.xmark, I.chip_card
def P(t, d): return clamp(t / d) if d else 1.0

OCEAN = hexc('#0B1621'); LAND2 = hexc('#27313D'); EDGE2 = hexc('#36414F')
SAND = hexc('#E0A040'); VERDE = hexc('#45B565'); ICE = hexc('#DCEBF5'); COLD = hexc('#5AA9FF'); WARM = hexc('#FF8A3A')
SRC = "Mikolajewicz et al. (2018), Earth System Dynamics · Instituto Max Planck de Meteorología"

# ------------------------------------------------------------------ globo ortográfico
_R = None
def _rings():
    global _R
    if _R is None:
        _R = [(iso, np.radians(np.array(poly[0], float))) for iso, polys in geo().items() for poly in polys]
    return _R

def oglobe(ctx, x, y, r, lon0, lat0=18, a=1.0, land=hexc('#3F8A5A'), ocean=hexc('#15385A'), tint=None):
    col(ctx, ocean, a); ctx.arc(x, y, r, 0, 2 * math.pi); ctx.fill()
    ctx.save(); ctx.arc(x, y, r, 0, 2 * math.pi); ctx.clip()
    l0, p0 = math.radians(lon0), math.radians(lat0)
    sp, cp = math.sin(p0), math.cos(p0)
    for iso, R in _rings():
        lon = R[:, 0] - l0; lat = R[:, 1]
        cosc = sp * np.sin(lat) + cp * np.cos(lat) * np.cos(lon)
        if (cosc < -0.05).all(): continue
        px = np.cos(lat) * np.sin(lon); py = cp * np.sin(lat) - sp * np.cos(lat) * np.cos(lon)
        back = cosc < 0
        if back.any():
            n = np.hypot(px, py) + 1e-9; px = np.where(back, px / n, px); py = np.where(back, py / n, py)
        X = x + r * px; Y = y - r * py
        ctx.move_to(X[0], Y[0])
        for i in range(1, len(X)): ctx.line_to(X[i], Y[i])
        ctx.close_path()
        c = tint(iso) if tint else land
        col(ctx, c, a); ctx.fill()
    ctx.restore()
    g = cairo.RadialGradient(x - r * .35, y - r * .35, r * .05, x, y, r)
    g.add_color_stop_rgba(0, 1, 1, 1, .10 * a); g.add_color_stop_rgba(.7, 0, 0, 0, .1 * a); g.add_color_stop_rgba(1, 0, 0, 0, .6 * a)
    ctx.set_source(g); ctx.arc(x, y, r, 0, 2 * math.pi); ctx.fill()
    glow(ctx, x, y, r * 1.08, hexc('#5AA9FF'), .10 * a)
    col(ctx, hexc('#5AA9FF'), .35 * a); ctx.set_line_width(2); ctx.arc(x, y, r, 0, 2 * math.pi); ctx.stroke()

def spin_arrow(ctx, x, y, r, sign, c, a=1.0, k=1.0):
    """Flecha elíptica delante del globo. sign=+1 izquierda→derecha (giro real), -1 al revés."""
    if k <= 0: return
    ctx.save(); ctx.translate(x, y + r * .05); ctx.scale(1, .22)
    col(ctx, c, a); ctx.set_line_width(10); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    a0, a1 = math.radians(20), math.radians(160)
    span = (a1 - a0) * k
    if sign > 0: ctx.arc_negative(0, 0, r * 1.25, a1, a1 - span); end = a1 - span; tang = -1
    else: ctx.arc(0, 0, r * 1.25, a0, a0 + span); end = a0 + span; tang = 1
    ctx.stroke(); ctx.restore()
    ex, ey = x + r * 1.25 * math.cos(end), y + r * .05 + r * 1.25 * .22 * math.sin(end)
    dx = -math.sin(end) * tang; ctx.save(); ctx.translate(ex, ey)
    s = 34; col(ctx, c, a)
    ctx.move_to(dx * s, 0); ctx.line_to(-dx * s * .3, -s * .7); ctx.line_to(-dx * s * .3, s * .7); ctx.close_path(); ctx.fill()
    ctx.restore(); ctx.set_line_cap(cairo.LINE_CAP_BUTT)

def flip_pos(t, t0, t1):
    """Integral de una velocidad que pasa de +1 a -1 entre t0 y t1."""
    if t < t0: return t
    if t < t1: return t0 + (t - t0) - (t - t0) ** 2 / (t1 - t0)
    return t0 - (t - t1)

def flip_sign(t, t0, t1):
    return 1 if t < t0 else (-1 if t > t1 else 1 - 2 * (t - t0) / (t1 - t0))

# ------------------------------------------------------------------ mapas
def mapbg(ctx, Pj, fills=None, under=None, a=1.0):
    col(ctx, OCEAN, a); ctx.paint()
    ctx.set_line_width(1); col(ctx, hexc('#13212E'), a)
    for lat in range(-60, 90, 15):
        x0, y = Pj(-180, lat); x1, _ = Pj(200, lat); ctx.move_to(x0, y); ctx.line_to(x1, y)
    ctx.stroke()
    if under: under()
    draw_map(ctx, Pj, fills, base=LAND2, edge=EDGE2, a=a)

def land_path(ctx, Pj):
    for iso, polys in geo().items():
        for poly in polys:
            for i, (lon, lat) in enumerate(poly[0]):
                x, y = Pj(lon, lat)
                (ctx.move_to if i == 0 else ctx.line_to)(x, y)
            ctx.close_path()

def blobs(ctx, Pj, items, c, a, on_land=True):
    """items: (lon, lat, radio_grados)."""
    if a <= 0: return
    ctx.save()
    if on_land: land_path(ctx, Pj); ctx.clip()
    for lon, lat, rd in items:
        x, y = Pj(lon, lat); r = rd * Pj.s * Pj.k
        g = cairo.RadialGradient(x, y, 0, x, y, r)
        g.add_color_stop_rgba(0, *c, .85 * a); g.add_color_stop_rgba(.6, *c, .6 * a); g.add_color_stop_rgba(1, *c, 0)
        ctx.set_source(g); ctx.arc(x, y, r, 0, 2 * math.pi); ctx.fill()
    ctx.restore()

def dot(ctx, Pj, lon, lat, name, k, c=INK, dx=18, align='l', size=28):
    if k <= 0: return
    x, y = Pj(lon, lat)
    col(ctx, c, k); ctx.arc(x, y, 7, 0, 2 * math.pi); ctx.fill()
    col(ctx, (0, 0, 0), .55 * k); w = twidth(ctx, name, size, F_SEMI) + 20
    rrect(ctx, x + dx - 10 if align == 'l' else x - dx - w + 10, y - size + 2, w, size + 14, 6); ctx.fill()
    text(ctx, name, x + dx if align == 'l' else x - dx, y + 6, size, c, F_SEMI, align, k)

_SEEDS = {}
def winds(ctx, Pj, box, t, sign_fn=None, c=AMBER, k=1.0, n=170, speed=9.0, seed=1, vfn=None):
    """Vientos zonales: alisios (|lat|<30) hacia el oeste, del oeste en 30-60, polares hacia el oeste."""
    if k <= 0: return
    lon0, lon1, lat0, lat1 = box
    key = (box, n, seed)
    if key not in _SEEDS:
        r = random.Random(seed); _SEEDS[key] = [(r.uniform(lon0, lon1), r.uniform(lat0, lat1), r.uniform(.6, 1.3)) for _ in range(n)]
    pos = sign_fn(t) if sign_fn else (t, 1)
    S, sgn = pos
    span = lon1 - lon0
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    for lon, lat, sp in _SEEDS[key]:
        al = abs(lat)
        u = -1 if al < 30 else (1 if al < 60 else -.6)
        v = (-.35 if lat > 0 else .35) if al < 30 else 0
        L = (lon - lon0 + u * speed * sp * S) % span
        x_lon = lon0 + L
        fade = min(1, L / 4, (span - L) / 4)
        ln = 5 * sp * sgn
        x0, y0 = Pj(x_lon, lat); x1, y1 = Pj(x_lon - u * ln, lat - v * ln)
        cc = c(lat) if callable(c) else c
        col(ctx, cc, .75 * k * fade * min(1, abs(sgn) * 3 + .15)); ctx.set_line_width(3.2)
        ctx.move_to(x1, y1); ctx.line_to(x0, y0); ctx.stroke()
        col(ctx, cc, .95 * k * fade); ctx.arc(x0, y0, 3.2, 0, 2 * math.pi); ctx.fill()
    ctx.set_line_cap(cairo.LINE_CAP_BUTT)

def polyline(ctx, Pj, pts, c, a, w=8, dash=None, prog_=1.0, flow_t=None):
    if a <= 0 or prog_ <= 0: return
    xy = [Pj(lo, la) for lo, la in pts]
    seg = [math.dist(xy[i], xy[i + 1]) for i in range(len(xy) - 1)]; tot = sum(seg); lim = tot * prog_
    col(ctx, c, a); ctx.set_line_width(w); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    if dash: ctx.set_dash(dash)
    ctx.move_to(*xy[0]); acc = 0
    for i, sg in enumerate(seg):
        if acc + sg >= lim:
            f = (lim - acc) / sg if sg else 0
            ctx.line_to(xy[i][0] + (xy[i + 1][0] - xy[i][0]) * f, xy[i][1] + (xy[i + 1][1] - xy[i][1]) * f); break
        ctx.line_to(*xy[i + 1]); acc += sg
    ctx.stroke(); ctx.set_dash([]); ctx.set_line_cap(cairo.LINE_CAP_BUTT)
    if flow_t is not None:  # puntos que viajan por la línea
        for j in range(int(tot / 70)):
            s = (j * 70 + flow_t * 120) % tot
            acc = 0
            for i, sg in enumerate(seg):
                if acc + sg >= s and s <= lim:
                    f = (s - acc) / sg; px = xy[i][0] + (xy[i + 1][0] - xy[i][0]) * f; py = xy[i][1] + (xy[i + 1][1] - xy[i][1]) * f
                    col(ctx, INK, a * .9); ctx.arc(px, py, w * .55, 0, 2 * math.pi); ctx.fill(); break
                acc += sg

def src(ctx, s=SRC, a=1.0):
    source(ctx, s, a)

def tag(ctx, s, x, y, k, c=INK, size=54, bg=(0, 0, 0), align='l'):
    if k <= 0: return
    w = twidth(ctx, s, size, F_BLACK) + 50
    x0 = x if align == 'l' else (x - w / 2 if align == 'c' else x - w)
    col(ctx, bg, .6 * k); rrect(ctx, x0, y - size - 10, w, size + 34, 12); ctx.fill()
    text(ctx, s, x0 + 25, y + 4, size, c, F_BLACK, 'l', k)

def counter_txt(ctx, s, x, y, size, c=INK, align='c', a=1):
    text(ctx, s, x, y, size, c, F_BLACK, align, a)

def fmt_es(v, dec=1):
    return f"{v:,.{dec}f}".replace(",", "X").replace(".", ",").replace("X", ".")

# ------------------------------------------------------------------ proyecciones
EU = Proj(-34, 44, 33, 73, 0, 0, W, H)
ATL = Proj(-105, 45, 18, 72, 0, 0, W, H)
AFR = Proj(-30, 70, -4, 42, 0, 0, W, H)
SAM = Proj(-92, -28, -56, 14, 120, 40, 1000, 1000)
WORLD = world_proj(40, 60, W - 80, H - 140)
IND = Proj(25, 115, -22, 32, 0, 0, W, H)

SAHARA = [(-10, 23, 12), (2, 25, 13), (16, 24, 12), (28, 23, 10), (-2, 18, 10), (14, 18, 10), (30, 18, 7)]
ARABIA = [(46, 23, 9), (53, 20, 6), (40, 29, 6), (60, 30, 6)]
ARGBR = [(-63, -34, 9), (-66, -28, 7), (-60, -30, 7), (-68, -40, 7), (-53, -28, 6), (-50, -24, 4), (-70, -46, 6)]
SUSA = [(-104, 32, 8), (-96, 33, 7), (-87, 33, 6)]
SWASIA = [(60, 32, 9), (68, 30, 7)]

ICE_NOW = [(-70, 72), (-70, 64), (-50, 65), (-34, 66), (-28, 66.5), (-22, 67.5), (-17, 68.5), (-14, 69), (-12, 69.5), (-8, 70), (-4, 71), (2, 72), (8, 72.5), (14, 73), (24, 73), (34, 72.5), (44, 73), (60, 74), (60, 80), (-70, 80)]
ICE_RET = [(-70, 72), (-55, 60), (-34, 58), (-28, 54), (-20, 50), (-12, 46.5), (-9.5, 44), (-6, 43.3), (-1.5, 43.4), (-1.2, 46), (-3, 48.6), (1.5, 50.2), (6, 53.5), (12, 54), (24, 55), (34, 60), (44, 62), (60, 66), (60, 80), (-70, 80)]

def ice(ctx, Pj, p, a=1.0):
    pts = [(lerp(a0[0], b0[0], p), lerp(a0[1], b0[1], p)) for a0, b0 in zip(ICE_NOW, ICE_RET)]
    xy = [Pj(lo, la) for lo, la in pts]
    ctx.move_to(*xy[0])
    for q in xy[1:]: ctx.line_to(*q)
    ctx.close_path()
    g = cairo.LinearGradient(0, 0, 0, H)
    g.add_color_stop_rgba(0, *ICE, .95 * a); g.add_color_stop_rgba(1, *hexc('#A9C8DE'), .85 * a)
    ctx.set_source(g); ctx.fill_preserve(); col(ctx, (1, 1, 1), .6 * a); ctx.set_line_width(2); ctx.stroke()

def thermo(ctx, x, y, h, level, c, a=1.0):
    col(ctx, LINE, a); rrect(ctx, x - 22, y - h, 44, h, 22); ctx.fill(); ctx.arc(x, y + 20, 44, 0, 2 * math.pi); ctx.fill()
    col(ctx, c, a); ctx.arc(x, y + 20, 32, 0, 2 * math.pi); ctx.fill()
    lv = h * clamp(level); rrect(ctx, x - 12, y - lv, 24, lv + 20, 12); ctx.fill()

def card(ctx, x, y, w, h, k, edge=AMBER):
    col(ctx, PANEL, .95 * k); rrect(ctx, x, y, w, h, 28); ctx.fill()
    col(ctx, edge, k); ctx.set_line_width(4); rrect(ctx, x, y, w, h, 28); ctx.stroke()

def qmark(ctx, x, y, s, k, c=AMBER):
    if k <= 0: return
    pulse = 1 + .05 * math.sin(k * 10)
    glow(ctx, x, y, s * 1.4, c, .35 * k)
    text(ctx, "?", x, y + s * .36, s * pulse, c, F_BLACK, a=k)

# ================================================================== 00 HOOK
def h1(ctx, t, d):
    p = P(t, d); x, y, r = W / 2, H / 2 + 20, 380
    t0, t1 = d * .18, d * .36
    S = flip_pos(t, t0, t1); s = flip_sign(t, t0, t1)
    oglobe(ctx, x, y, r, 10 - 28 * S, a=1 - ease(prog(p, .62, .72)))
    if p < .7:
        c = GREEN if s > 0 else RED
        spin_arrow(ctx, x, y, r, 1 if s > 0 else -1, c, 1 - ease(prog(p, .62, .7)), 1 if abs(s) > .3 else abs(s) / .3)
    if p > .62:
        k = ease(prog(p, .62, .74))
        ctx.push_group(); photo(ctx, 'sunrise_west', t - d * .62, d * .38, True, dark=.1, focus=(.5, .45))
        ctx.pop_group_to_source(); ctx.paint_with_alpha(k)
        tag(ctx, "OESTE", W / 2, 260, ease(prog(p, .78, .86)), AMBER, 70, align='c')
        tag(ctx, "← ESTE", 70, 1000, ease(prog(p, .84, .92)) * .8, INK, 34)

def h2(ctx, t, d):
    p = P(t, d)
    mapbg(ctx, EU, under=lambda: ice(ctx, EU, ease(prog(p, .05, .75))))
    dot(ctx, EU, -1.5, 43.6, "Golfo de Vizcaya", ease(prog(p, .6, .72)), AMBER, dx=-18, align='r', size=34)
    dot(ctx, EU, -3.7, 40.4, "Madrid", ease(prog(p, .3, .4)), INK, size=26)
    dot(ctx, EU, -0.1, 51.5, "Londres", ease(prog(p, .2, .3)), INK, size=26)

def h3(ctx, t, d):
    p = P(t, d); g = ease(prog(p, .2, .8))
    mapbg(ctx, AFR)
    blobs(ctx, AFR, SAHARA + ARABIA, SAND, 1 - g)
    blobs(ctx, AFR, SAHARA + ARABIA, VERDE, g)
    tag(ctx, "SÁHARA", 760, 330, 1, INK, 60)

def h4(ctx, t, d):
    p = P(t, d); g = ease(prog(p, .15, .75))
    mapbg(ctx, SAM)
    blobs(ctx, SAM, ARGBR, VERDE, 1 - g)
    blobs(ctx, SAM, ARGBR, SAND, g)
    big(ctx, "ARGENTINA", 470, 110, INK, ease(prog(p, .05, .2)), x=1500)
    big(ctx, "+ SUR DE BRASIL", 580, 56, MUTED, ease(prog(p, .2, .35)), x=1500)
    big(ctx, "EL MAYOR DESIERTO", 760, 66, SAND, ease(prog(p, .55, .7)), x=1500)
    big(ctx, "DEL PLANETA", 840, 66, SAND, ease(prog(p, .6, .75)), x=1500)

def h5(ctx, t, d):
    p = P(t, d)
    photo(ctx, 'supercomputer', t, d, True, dark=.35, focus=(.55, .5))
    bottom_shade(ctx, 520)
    stamp(ctx, "SIMULACIÓN · INSTITUTO MAX PLANCK", 90, 820, ease(prog(p, .05, .2)), AMBER, 40)
    yrs = int(6990 * eout(prog(p, .15, .6)))
    text(ctx, f"{fmt_int(yrs)} años simulados", 90, 960, 90, INK, F_BLACK, 'l', ease(prog(p, .12, .25)))

def h6(ctx, t, d):
    p = P(t, d)
    photo(ctx, 'venus_sky', t, d, True, dark=.55 - .25 * ease(prog(p, .1, .8)), focus=(.5, .6))
    qmark(ctx, 1500, 480, 300, ease(prog(p, .15, .3)))
    label(ctx, "Al final del vídeo", 1500, 720, ease(prog(p, .3, .45)), INK, 32)

# ================================================================== 01 POR QUÉ
def p1(ctx, t, d):
    p = P(t, d); x, y, r = 620, H / 2 + 20, 360
    oglobe(ctx, x, y, r, 30 - t * 6)
    spin_arrow(ctx, x, y, r, 1, GREEN, 1, 1)
    col(ctx, AMBER, .8); ctx.set_line_width(4); ctx.set_dash([10, 8]); ctx.move_to(x - r, y + r * .0); ctx.line_to(x + r, y); ctx.stroke(); ctx.set_dash([])
    v = 1670 * eout(prog(p, .08, .45))
    text(ctx, fmt_int(v), 1450, 520, 200, AMBER, F_BLACK, a=ease(prog(p, .05, .15)))
    label(ctx, "km/h en el ecuador", 1450, 600, ease(prog(p, .1, .2)), INK, 40)
    k = ease(prog(p, .6, .7))
    if k > 0:
        on = 1 if int(t * 4) % 2 == 0 else .6
        col(ctx, RED, .85 * k * on); rrect(ctx, 1110, 700, 680, 110, 16); ctx.fill()
        text(ctx, "FRENAZO = CATÁSTROFE", 1450, 775, 50, INK, F_BLACK, a=k)

def p2(ctx, t, d):
    p = P(t, d)
    for i, (sg, c, s) in enumerate([(1, GREEN, "NUESTRA TIERRA"), (-1, RED, "TIERRA AL REVÉS")]):
        k = ease(prog(p, i * .25, .15 + i * .25)); x = 540 + i * 840
        if k <= 0: continue
        oglobe(ctx, x, 520, 270, 0 - sg * t * 10, a=k)
        spin_arrow(ctx, x, 520, 270, sg, c, k, 1)
        text(ctx, s, x, 950, 52, c, F_BLACK, a=k)
    big(ctx, "¿Y si SIEMPRE hubiera sido así?", 140, 64, INK, ease(prog(p, .5, .62)))

def p3(ctx, t, d):
    p = P(t, d)
    if p < .62:
        photo(ctx, 'nebula', t, d * .62, True, dark=.15)
        stamp(ctx, "HACE 4.600 MILLONES DE AÑOS", 90, 130, ease(prog(p, .05, .15)), AMBER, 40)
        # flecha de giro sobre el disco
        k = ease(prog(p, .2, .35)); ctx.save(); ctx.translate(W / 2, H / 2); ctx.scale(1, .35)
        col(ctx, AMBER, .8 * k); ctx.set_line_width(9); ctx.arc(0, 0, 640, math.radians(200) + t * .4, math.radians(320) + t * .4); ctx.stroke(); ctx.restore()
    else:
        k = ease(prog(p, .62, .7))
        ctx.push_group(); photo(ctx, 'ballerina', t - d * .62, d * .38, True, dark=.2); ctx.pop_group_to_source(); ctx.paint_with_alpha(k)
        tag(ctx, "MISMO GIRO", 90, 1000, ease(prog(p, .72, .8)), AMBER, 56)

def p4(ctx, t, d):
    p = P(t, d)
    photo(ctx, 'supercomputer', t, d, False, dark=.55, focus=(.4, .5))
    stamp(ctx, "2018", 90, 140, ease(prog(p, 0, .1)), AMBER, 60)
    for i, s in enumerate(["Instituto Max Planck de Meteorología", "Centro Alemán de Computación Climática", "Universidad de Hamburgo", "Universidad de Reading"]):
        k = ease(prog(p, .08 + i * .1, .18 + i * .1))
        chip_card(ctx, 90, 220 + i * 140, 1000, 110, s, "", k)
    k = ease(prog(p, .6, .72))
    text(ctx, "≈ 7.000", 1500, 560, 170, AMBER, F_BLACK, a=k); label(ctx, "años simulados", 1500, 640, k, INK, 40)
    src(ctx, a=ease(prog(p, .1, .2)))

def p5(ctx, t, d):
    p = P(t, d)
    for i, (s, c) in enumerate([("Tierra real", GREEN), ("Tierra al revés", RED)]):
        k = ease(prog(p, .05 + i * .12, .2 + i * .12)); x = 560 + i * 340
        thermo(ctx, x, 760, 420, .62 * k, c, k)
        label(ctx, s, x, 900, k, INK, 30)
    big(ctx, "Temperatura media:", 330, 60, MUTED, ease(prog(p, .05, .15)), x=1380)
    big(ctx, "CASI IGUAL", 450, 110, INK, ease(prog(p, .25, .35)), x=1380)
    for i, s in enumerate(["dónde hace frío", "dónde llueve", "dónde NUNCA llueve"]):
        k = ease(prog(p, .5 + i * .12, .6 + i * .12))
        text(ctx, "≠ " + s, 1100, 600 + i * 95, 56, AMBER, F_XB, 'l', k)

def p6(ctx, t, d):
    p = P(t, d); k = eout(prog(p, 0, .2))
    card(ctx, 460, 320, 1000, 440, k)
    col(ctx, AMBER, k); ctx.arc(640, 470, 70, 0, 2 * math.pi); ctx.fill()
    text(ctx, "?", 640, 500, 90, BG, F_BLACK, a=k)
    text(ctx, "LA GRAN PREGUNTA", 750, 470, 50, INK, F_BLACK, 'l', k)
    label(ctx, "Una pregunta imposible cada semana", 750, 515, k, MUTED, 26, 'l')
    pressed = prog(p, .55, .62)
    c = mix(RED, LINE, pressed); s = "SUSCRITO ✓" if pressed > .5 else "SUSCRIBIRSE"
    sc = 1 - .06 * math.sin(pressed * math.pi)
    ctx.save(); ctx.translate(W / 2, 650); ctx.scale(sc, sc)
    col(ctx, c, k); rrect(ctx, -260, -55, 520, 110, 55); ctx.fill()
    text(ctx, s, 0, 18, 50, INK, F_BLACK, a=k); ctx.restore()

def p7(ctx, t, d):
    """Tiovivo: la pelota va recta, pero su rastro sobre el disco se curva."""
    p = P(t, d)
    half = .5; rev = p >= half
    pp = prog(p, 0, half) if not rev else prog(p, half, 1)
    w = (1 if not rev else -1) * 1.6
    cx, cy, R = 700, H / 2 + 20, 400
    ang = w * t
    # disco
    ctx.save(); ctx.translate(cx, cy); ctx.rotate(ang)
    col(ctx, hexc('#1A2230')); ctx.arc(0, 0, R, 0, 2 * math.pi); ctx.fill()
    for i in range(8):
        col(ctx, AMBER if i % 2 else hexc('#2A3445'), .35); ctx.move_to(0, 0); ctx.arc(0, 0, R, i * math.pi / 4, (i + 1) * math.pi / 4); ctx.close_path(); ctx.fill()
    col(ctx, LINE); ctx.set_line_width(4); ctx.arc(0, 0, R, 0, 2 * math.pi); ctx.stroke()
    ctx.restore()
    person(ctx, cx, cy, 40, INK)
    # lanzamiento: empieza en tl
    tl = (0 if not rev else d * half) + d * half * .15; T = d * half * .55
    tau = clamp((t - tl) / T)
    # amigo en el borde (gira con el disco)
    fa = w * tl
    fx, fy = cx + R * math.cos(ang - 0) * 1, cy + R * math.sin(ang)
    fang = ang - w * tl  # amigo empieza en ángulo 0 cuando se lanza
    fx, fy = cx + (R - 30) * math.cos(fang), cy + (R - 30) * math.sin(fang)
    person(ctx, fx, fy, 30, GREEN)
    # rastro curvado sobre el disco
    c = GREEN if not rev else RED
    if tau > 0:
        col(ctx, c, .95); ctx.set_line_width(7); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        N = 40
        for i in range(N + 1):
            s = tau * i / N; tt = tl + s * T
            rr = (R - 30) * s; th = (ang - w * tt)  # posición del rastro en el disco (gira con él)
            px, py = cx + rr * math.cos(th), cy + rr * math.sin(th)
            (ctx.move_to if i == 0 else ctx.line_to)(px, py)
        ctx.stroke()
        # pelota en línea recta (marco inercial)
        bx, by = cx + (R - 30) * tau, cy
        col(ctx, INK, .35); ctx.set_dash([8, 8]); ctx.set_line_width(3); ctx.move_to(cx, cy); ctx.line_to(cx + R - 30, cy); ctx.stroke(); ctx.set_dash([])
        col(ctx, RED if not rev else AMBER); ctx.arc(bx, by, 16, 0, 2 * math.pi); ctx.fill()
    ctx.set_line_cap(cairo.LINE_CAP_BUTT)
    k = ease(prog(pp, .05, .2))
    text(ctx, "TIERRA REAL" if not rev else "TIERRA AL REVÉS", 1470, 380, 66, c, F_BLACK, a=k)
    label(ctx, "la pelota va recta…", 1470, 470, ease(prog(pp, .3, .45)), INK, 38)
    label(ctx, "…pero su camino se tuerce", 1470, 530, ease(prog(pp, .55, .7)), AMBER, 38)
    text(ctx, "→" if not rev else "←", 1470, 700, 150, c, F_BLACK, a=ease(prog(pp, .7, .8)))
    big(ctx, "EFECTO CORIOLIS", 900, 54, MUTED, ease(prog(p, .1, .2)), x=1470)

def p8(ctx, t, d):
    p = P(t, d)
    if p < .5:
        k = ease(prog(p, 0, .12))
        # remolino de agua
        ctx.save(); ctx.translate(W / 2, 470)
        for i in range(5):
            col(ctx, COLD, .5 * k); ctx.set_line_width(8)
            ctx.arc(0, 0, 60 + i * 45, t * 3 + i, t * 3 + i + 3.5); ctx.stroke()
        ctx.restore()
        xmark(ctx, W / 2, 470, 360, RED, ease(prog(p, .15, .25)))
        stamp(ctx, "MITO", W / 2 - 90, 870, ease(prog(p, .2, .3)), RED, 80)
    else:
        mapbg(ctx, ATL)
        winds(ctx, ATL, (-105, 45, 18, 72), t, k=ease(prog(p, .5, .6)))
        big(ctx, "MILES DE KM", 160, 90, AMBER, ease(prog(p, .6, .7)))
        label(ctx, "aquí el efecto sí manda", W / 2, 230, ease(prog(p, .68, .78)), INK, 36)

def p9(ctx, t, d):
    p = P(t, d)
    mapbg(ctx, WORLD)
    t0, t1 = d * .25, d * .4
    winds(ctx, WORLD, (-170, 190, -55, 75), t, sign_fn=lambda tt: (flip_pos(tt, t0, t1), flip_sign(tt, t0, t1)),
          c=lambda la: mix(AMBER, RED, ease(prog(t, t0, t1))), n=320, speed=8)
    k = ease(prog(p, .7, .82))
    if k > 0:
        x, y = WORLD(10, 52); ctx.set_line_width(6); col(ctx, COLD, k); ctx.arc(x, y, 150 + 10 * math.sin(t * 4), 0, 2 * math.pi); ctx.stroke()
        tag(ctx, "EUROPA", x + 170, y - 120, k, COLD, 56)
    tag(ctx, "TODOS LOS VIENTOS, AL REVÉS", 60, 1040, ease(prog(p, .35, .45)), INK, 44)

# ================================================================== 02 EUROPA
GULF = [(-82, 25), (-75, 33), (-62, 40), (-45, 44), (-30, 49), (-18, 54), (-10, 59), (-2, 64), (8, 68)]
def e1(ctx, t, d):
    p = P(t, d)
    mapbg(ctx, ATL)
    winds(ctx, ATL, (-105, 45, 34, 66), t, c=WARM, k=ease(prog(p, .05, .15)), n=120, seed=4)
    polyline(ctx, ATL, GULF, RED, ease(prog(p, .35, .45)), 14, prog_=ease(prog(p, .35, .7)), flow_t=t)
    tag(ctx, "Vientos del oeste: aire templado del océano", 60, 1040, ease(prog(p, .08, .18)) * (1 - ease(prog(p, .38, .45))), WARM, 40)
    tag(ctx, "Cinta transportadora del Atlántico", 60, 1040, ease(prog(p, .45, .55)), RED, 40)

def e2(ctx, t, d):
    p = P(t, d)
    mapbg(ctx, ATL)
    lat = 51.5; x0, y = ATL(-105, lat); x1, _ = ATL(45, lat)
    k = ease(prog(p, .1, .3))
    col(ctx, AMBER, .8 * k); ctx.set_line_width(3); ctx.set_dash([12, 8]); ctx.move_to(x0, y); ctx.line_to(x0 + (x1 - x0) * k, y); ctx.stroke(); ctx.set_dash([])
    dot(ctx, ATL, -0.1, 51.5, "Londres · 51,5° N", ease(prog(p, .05, .15)), AMBER, size=34)
    dot(ctx, ATL, -8.5, 42.9, "Galicia", ease(prog(p, .12, .2)), INK)
    dot(ctx, ATL, -9.1, 38.7, "Lisboa", ease(prog(p, .16, .24)), INK)
    dot(ctx, ATL, -73.6, 45.5, "Montreal · 45,5° N", ease(prog(p, .45, .55)), COLD, size=34, dx=-18, align='r')
    dot(ctx, ATL, -71.2, 46.8, "Quebec · 46,8° N", ease(prog(p, .55, .65)), COLD, size=30)
    stamp(ctx, "MÁS AL NORTE… Y MÁS SUAVE", 60, 1040, ease(prog(p, .7, .8)), AMBER, 40)

def e3(ctx, t, d):
    p = P(t, d)
    mapbg(ctx, ATL)
    t0, t1 = d * .05, d * .2
    winds(ctx, ATL, (-105, 45, 34, 66), t, sign_fn=lambda tt: (flip_pos(tt, t0, t1), flip_sign(tt, t0, t1)),
          c=lambda la: mix(WARM, COLD, ease(prog(t, t0, t1))), n=120, seed=4)
    fade = 1 - ease(prog(p, .55, .85))
    polyline(ctx, ATL, GULF, RED, fade, 14, flow_t=t * fade)
    v = lerp(19, 0, ease(prog(p, .5, .85)))
    card(ctx, 1240, 620, 620, 330, 1)
    text(ctx, fmt_es(v, 0) if v > .5 else "≈ 0", 1550, 800, 150, RED if v > .5 else COLD, F_BLACK)
    label(ctx, "millones de m³ de agua por segundo", 1550, 880, 1, INK, 26)
    label(ctx, "Circulación del Atlántico", 1550, 680, 1, MUTED, 26)
    src(ctx)

def e4(ctx, t, d):
    p = P(t, d)
    if p < .62:
        mapbg(ctx, EU, under=lambda: ice(ctx, EU, ease(prog(p, 0, .5))))
        dot(ctx, EU, -0.1, 51.5, "Gran Bretaña", ease(prog(p, .15, .25)), INK, size=32)
        dot(ctx, EU, -2.9, 43.3, "Bilbao", ease(prog(p, .4, .48)), AMBER, size=30)
        dot(ctx, EU, -3.8, 43.46, "Santander", ease(prog(p, .45, .52)), AMBER, size=30, dx=-18, align='r')
        src(ctx)
    else:
        photo(ctx, 'frozen_coast', t - d * .62, d * .38, True, dark=.15)
        stamp(ctx, "COSTA CANTÁBRICA · INVIERNO", 80, 1000, ease(prog(p, .7, .8)), INK, 40)

def e5(ctx, t, d):
    p = P(t, d)
    x = 640
    lv = lerp(.75, .2, ease(prog(p, .15, .6)))
    thermo(ctx, x, 800, 560, lv, mix(WARM, COLD, ease(prog(p, .15, .6))))
    v = -20 * ease(prog(p, .15, .6))
    text(ctx, f"{fmt_es(v, 0)} °C" if v < -.5 else "0 °C", 1300, 560, 220, COLD, F_BLACK, a=ease(prog(p, .1, .2)))
    label(ctx, "inviernos en el noroeste de Europa", 1300, 650, ease(prog(p, .15, .25)), INK, 38)
    stamp(ctx, "MÁS DE 20 °C MÁS FRÍOS", 1010, 790, ease(prog(p, .6, .7)), COLD, 46)
    src(ctx)

def e6(ctx, t, d):
    p = P(t, d)
    def tint_under():
        pass
    mapbg(ctx, ATL)
    blobs(ctx, ATL, [(5, 52, 12), (20, 55, 12), (-2, 47, 8), (12, 46, 8), (30, 60, 10)], COLD, ease(prog(p, .05, .25)))
    blobs(ctx, ATL, [(-78, 36, 10), (-74, 41, 8), (-80, 31, 7)], WARM, ease(prog(p, .2, .4)))
    dot(ctx, ATL, -77, 38.9, "Costa este de EE. UU. · más templada", ease(prog(p, .25, .35)), WARM, size=30)
    dot(ctx, ATL, -57, 51, "Terranova y Labrador · sin hielo", ease(prog(p, .45, .55)), WARM, size=30)
    k = ease(prog(p, .7, .82))
    if k > 0:
        xa, ya = ATL(-60, 30); xb, yb = ATL(10, 30)
        ctx.set_line_width(8); col(ctx, AMBER, k); ctx.move_to(xa, ya); ctx.curve_to(xa + 200, ya + 160, xb - 200, yb + 160, xb, yb); ctx.stroke()
        ctx.move_to(xb, yb - 40); ctx.curve_to(xb - 200, yb - 200, xa + 200, ya - 200, xa, ya - 40); ctx.stroke()
        tag(ctx, "CLIMAS INTERCAMBIADOS", W / 2, 1040, k, AMBER, 50, align='c')

def e7(ctx, t, d):
    p = P(t, d)
    photo(ctx, 'sahara_dunes', t, d, True, dark=.45, focus=(.5, .5))
    qmark(ctx, W / 2, 470, 320, ease(prog(p, .2, .4)))

# ================================================================== 03 SÁHARA
def s1(ctx, t, d):
    p = P(t, d)
    if p < .45:
        photo(ctx, 'sahara_dunes', t, d * .45, False, dark=.25)
        v = 9 * eout(prog(p, .05, .35))
        text(ctx, f"≈ {fmt_es(v, 0)} millones de km²", 90, 1000, 80, INK, F_BLACK, 'l', ease(prog(p, .03, .1)))
    else:
        mapbg(ctx, AFR); blobs(ctx, AFR, SAHARA + ARABIA, SAND, 1)
        winds(ctx, AFR, (-30, 70, 4, 34), t, c=SAND, k=ease(prog(p, .45, .55)), n=130, seed=7)
        tag(ctx, "ALISIOS: SOPLAN DESDE EL ESTE · SECOS", 60, 1040, ease(prog(p, .55, .65)), SAND, 42)

def s2(ctx, t, d):
    p = P(t, d)
    mapbg(ctx, AFR)
    g = ease(prog(p, .45, .95))
    blobs(ctx, AFR, SAHARA + ARABIA, SAND, 1 - g * .6)
    t0, t1 = d * .05, d * .25
    winds(ctx, AFR, (-30, 70, 4, 34), t, sign_fn=lambda tt: (flip_pos(tt, t0, t1), flip_sign(tt, t0, t1)),
          c=lambda la: mix(SAND, COLD, ease(prog(t, t0, t1))), n=130, seed=7)
    tag(ctx, "AHORA EL VIENTO LLEGA DEL OCÉANO · HÚMEDO", 60, 1040, ease(prog(p, .3, .4)), COLD, 42)

def s3(ctx, t, d):
    p = P(t, d)
    if p < .6:
        g = ease(prog(p, 0, .45))
        mapbg(ctx, AFR); blobs(ctx, AFR, SAHARA + ARABIA, SAND, (1 - g) * .4 + .0); blobs(ctx, AFR, SAHARA + ARABIA, VERDE, g)
        dot(ctx, AFR, -15, 14, "África occidental", ease(prog(p, .1, .2)), INK)
        dot(ctx, AFR, 45, 24, "Arabia", ease(prog(p, .3, .4)), INK)
        src(ctx)
    else:
        photo(ctx, 'green_sahara', t - d * .6, d * .4, True, dark=.1)
        tag(ctx, "EL SÁHARA VERDE", 80, 1000, ease(prog(p, .68, .78)), VERDE, 60)

def s4(ctx, t, d):
    p = P(t, d)
    photo(ctx, 'rock_art', t, d, True, dark=.25, focus=(.5, .5))
    stamp(ctx, "HACE ~10.000 AÑOS", 80, 130, ease(prog(p, .05, .15)), AMBER, 50)
    for i, s in enumerate(["LAGOS", "HIPOPÓTAMOS", "COCODRILOS"]):
        tag(ctx, s, 80, 820 + i * 0 if False else 700 + i * 110, ease(prog(p, .2 + i * .1, .3 + i * .1)), INK, 50)

def s5(ctx, t, d):
    p = P(t, d)
    v = lerp(41.8, 31.2, ease(prog(p, .1, .5)))
    for i, (val, c, s) in enumerate([(41.8, SAND, "Tierra real"), (v, VERDE if p > .5 else SAND, "Tierra al revés")]):
        k = ease(prog(p, i * .08, .1 + i * .08))
        h = 560 * val / 41.8 * k
        x = 380 + i * 360
        col(ctx, c, .9); rrect(ctx, x - 110, 880 - h, 220, h, 12); ctx.fill()
        text(ctx, fmt_es(val), x, 860 - h, 64, INK, F_BLACK, a=k)
        label(ctx, s, x, 940, k, INK, 30)
    label(ctx, "millones de km² de desierto permanente", 560, 1000, 1, MUTED, 26)
    text(ctx, "−25 %", 1430, 470, 220, VERDE, F_BLACK, a=ease(prog(p, .5, .6)))
    label(ctx, "≈ 11 millones de km² que reverdecen", 1430, 560, ease(prog(p, .55, .65)), INK, 36)
    tag(ctx, "> TODO EE. UU.", 1430, 720, ease(prog(p, .72, .82)), AMBER, 64, align='c')
    src(ctx)

def s6(ctx, t, d):
    p = P(t, d)
    mapbg(ctx, SAM)
    x, y = SAM(-62, -32)
    qmark(ctx, x, y, 240, ease(prog(p, .3, .5)))

# ================================================================== 04 AMÉRICA
def a1(ctx, t, d):
    p = P(t, d)
    photo(ctx, 'pampa_fields', t, d, True, dark=.15, focus=(.5, .55))
    stamp(ctx, "LA PAMPA · ARGENTINA", 80, 130, ease(prog(p, .03, .12)), AMBER, 46)
    for i, s in enumerate(["TRIGO", "MAÍZ", "SOJA", "GANADO"]):
        tag(ctx, s, 80 + i * 330, 1000, ease(prog(p, .25 + i * .08, .33 + i * .08)), INK, 46)

def a2(ctx, t, d):
    p = P(t, d)
    g = ease(prog(p, .4, .85))
    mapbg(ctx, SAM)
    blobs(ctx, SAM, ARGBR, VERDE, 1 - g); blobs(ctx, SAM, ARGBR, SAND, g)
    t0, t1 = d * .05, d * .25
    winds(ctx, SAM, (-92, -28, -50, 10), t, sign_fn=lambda tt: (flip_pos(tt, t0, t1), flip_sign(tt, t0, t1)), c=COLD, n=90, seed=9,
          k=1 - ease(prog(p, .5, .7)) * .6)
    big(ctx, "EL MAYOR", 470, 100, SAND, ease(prog(p, .55, .65)), x=1500)
    big(ctx, "DESIERTO", 590, 100, SAND, ease(prog(p, .6, .7)), x=1500)
    big(ctx, "DE LA TIERRA", 690, 64, INK, ease(prog(p, .65, .75)), x=1500)
    src(ctx)

def a3(ctx, t, d):
    p = P(t, d)
    if p < .45:
        mapbg(ctx, SAM); blobs(ctx, SAM, ARGBR, SAND, 1)
        for i, (lo, la, n, al) in enumerate([(-58.4, -34.6, "Buenos Aires", 'l'), (-60.7, -32.9, "Rosario", 'r'), (-64.2, -31.4, "Córdoba", 'r'), (-51.2, -30.0, "Porto Alegre", 'l')]):
            dot(ctx, SAM, lo, la, n, ease(prog(p, .03 + i * .08, .1 + i * .08)), INK, size=30, dx=18 if al == 'l' else -18, align=al)
    else:
        photo(ctx, 'pampa_desert', t - d * .45, d * .55, True, dark=.15)
        tag(ctx, "EL GRANERO DE SUDAMÉRICA… ARENA", 80, 1000, ease(prog(p, .6, .7)), SAND, 50)

def a4(ctx, t, d):
    p = P(t, d)
    mapbg(ctx, WORLD)
    steps = [(ARGBR, SAND, .0), (SUSA, SAND, .15), (SAHARA + ARABIA, VERDE, .35), (SWASIA, VERDE, .5)]
    for items, c, s0 in steps: blobs(ctx, WORLD, items, c, ease(prog(p, s0, s0 + .15)))
    blobs(ctx, WORLD, [(5, 52, 10), (20, 55, 10), (-2, 47, 7), (30, 60, 9)], COLD, ease(prog(p, .62, .77)))
    k = ease(prog(p, .8, .9))
    for i, (c, s) in enumerate([(SAND, "más seco"), (VERDE, "más húmedo"), (COLD, "más frío")]):
        col(ctx, c, k); ctx.arc(110 + i * 330, 1030, 16, 0, 2 * math.pi); ctx.fill()
        text(ctx, s, 140 + i * 330, 1042, 34, INK, F_SEMI, 'l', k)
    src(ctx, a=0)

def a5(ctx, t, d):
    p = P(t, d); k = eout(prog(p, 0, .2))
    card(ctx, 360, 280, 1200, 420, k)
    col(ctx, PANEL, .95 * k); ctx.move_to(520, 700); ctx.line_to(600, 700); ctx.line_to(500, 780); ctx.close_path(); ctx.fill()
    text(ctx, "¿Tu país gana", W / 2, 440, 90, INK, F_BLACK, a=k)
    text(ctx, "o pierde?", W / 2, 560, 90, AMBER, F_BLACK, a=k)
    text(ctx, "Escríbelo en los comentarios ↓", W / 2, 650, 36, MUTED, F_SEMI, a=ease(prog(p, .3, .45)))

def a6(ctx, t, d):
    p = P(t, d)
    photo(ctx, 'deep_ocean', t, d, True, dark=.4)
    qmark(ctx, W / 2, 480, 300, ease(prog(p, .3, .5)))
    big(ctx, "EL OCÉANO", 860, 90, INK, ease(prog(p, .1, .25)))

# ================================================================== 05 OCÉANO
AMOC_UP = [(-85, 22), (-75, 32), (-55, 40), (-35, 47), (-20, 55), (-8, 62), (5, 68)]
AMOC_DN = [(-15, 64), (-32, 55), (-45, 40), (-38, 15), (-30, -10), (-25, -35), (-15, -50)]
PMOC_UP = [(125, 12), (140, 25), (155, 36), (170, 44), (185, 52)]
PMOC_DN = [(180, 56), (172, 42), (182, 20), (170, 0), (160, -25), (150, -45)]
def o1(ctx, t, d):
    p = P(t, d)
    mapbg(ctx, WORLD)
    polyline(ctx, WORLD, AMOC_UP, RED, 1, 12, prog_=ease(prog(p, .05, .4)), flow_t=t)
    polyline(ctx, WORLD, AMOC_DN, COLD, 1, 10, dash=[16, 10], prog_=ease(prog(p, .35, .75)), flow_t=t)
    k = ease(prog(p, .3, .4))
    if k > 0:
        x, y = WORLD(0, 66); glow(ctx, x, y, 60, COLD, k); text(ctx, "↓", x + 50, y + 20, 70, COLD, F_BLACK, a=k)
    tag(ctx, "superficie: agua cálida", 60, 1040, ease(prog(p, .08, .18)), RED, 38)
    tag(ctx, "fondo: agua fría", 760, 1040, ease(prog(p, .4, .5)), COLD, 38)

def o2(ctx, t, d):
    p = P(t, d)
    mapbg(ctx, WORLD)
    fa = 1 - ease(prog(p, .1, .35))
    polyline(ctx, WORLD, AMOC_UP, RED, fa, 12, flow_t=t); polyline(ctx, WORLD, AMOC_DN, COLD, fa, 10, dash=[16, 10], flow_t=t)
    polyline(ctx, WORLD, PMOC_UP, RED, 1, 14, prog_=ease(prog(p, .35, .6)), flow_t=t)
    polyline(ctx, WORLD, PMOC_DN, COLD, 1, 10, dash=[16, 10], prog_=ease(prog(p, .5, .75)), flow_t=t)
    k = ease(prog(p, .6, .7))
    card(ctx, 640, 690, 640, 300, k)
    text(ctx, fmt_es(23 * eout(prog(p, .6, .85)), 0), 960, 860, 150, RED, F_BLACK, a=k)
    label(ctx, "millones de m³/s · PACÍFICO", 960, 935, k, INK, 28)
    label(ctx, "(hoy en el Atlántico: 19)", 960, 740, k, MUTED, 26)
    tag(ctx, "EL MOTOR SE MUDA AL PACÍFICO", 60, 110, ease(prog(p, .3, .4)), INK, 44)
    src(ctx, a=k)

def o3(ctx, t, d):
    p = P(t, d)
    if p < .7:
        g = ease(prog(p, .1, .6))
        mapbg(ctx, IND, under=lambda: blobs(ctx, IND, [(65, 14, 10 * g + .1), (88, 14, 7 * g + .1), (75, 6, 9 * g + .1)], RED, .9, on_land=False))
        tag(ctx, "OCÉANO ÍNDICO", 60, 110, ease(prog(p, .02, .12)), INK, 50)
        tag(ctx, "ZONA CON MUY POCO OXÍGENO", 60, 1040, ease(prog(p, .3, .4)), RED, 46)
        src(ctx, a=0)
    else:
        photo(ctx, 'deep_ocean', t - d * .7, d * .3, True, dark=.25)
        tag(ctx, "UN DESIERTO BAJO EL MAR", 80, 1000, ease(prog(p, .75, .85)), RED, 54)

def o4(ctx, t, d):
    p = P(t, d)
    photo(ctx, 'cyano_bloom', t, d, True, dark=.15)
    tag(ctx, "CIANOBACTERIAS", 80, 160, ease(prog(p, .03, .12)), VERDE, 70)
    stamp(ctx, "+2.000 MILLONES DE AÑOS: OXIGENARON LA ATMÓSFERA", 80, 1000, ease(prog(p, .55, .65)), INK, 36)
    src(ctx, a=ease(prog(p, .2, .3)) * (1 - ease(prog(p, .5, .55))))

def o5(ctx, t, d):
    p = P(t, d); k = eout(prog(p, 0, .2))
    pop = 1 + .25 * math.sin(math.pi * prog(p, .35, .5))
    ctx.save(); ctx.translate(W / 2, 450); ctx.scale(pop, pop)
    glow(ctx, 0, 0, 260, AMBER, .5 * k * prog(p, .35, .5))
    thumb(ctx, 0, 0, 220, AMBER if p > .42 else INK, k)
    ctx.restore()
    big(ctx, "¿TE ESTÁ VOLANDO LA CABEZA?", 820, 70, INK, ease(prog(p, .1, .25)))
    label(ctx, "Dale a me gusta", W / 2, 900, ease(prog(p, .3, .45)), AMBER, 44)

def o6(ctx, t, d):
    p = P(t, d); x, y, r = W / 2, H / 2 + 30, 340
    oglobe(ctx, x, y, r, t * 18, a=1)
    spin_arrow(ctx, x, y, r, -1, RED, 1, 1)
    k = ease(prog(p, .45, .6))
    big(ctx, "¿HA PASADO DE VERDAD?", 120, 80, AMBER, k)

# ================================================================== 06 VENUS
def venus(ctx, x, y, r, t, a=1.0, sign=-1):
    g = cairo.RadialGradient(x - r * .3, y - r * .3, r * .1, x, y, r)
    g.add_color_stop_rgba(0, *hexc('#FFE3A8'), a); g.add_color_stop_rgba(1, *hexc('#B87A2A'), a)
    ctx.set_source(g); ctx.arc(x, y, r, 0, 2 * math.pi); ctx.fill()
    ctx.save(); ctx.arc(x, y, r, 0, 2 * math.pi); ctx.clip()
    for i in range(-6, 7):
        yy = y + i * r / 6.5; off = (t * 40 * sign + i * 37) % (r * 2)
        col(ctx, hexc('#FFF2D0'), .18 * a); ctx.set_line_width(r / 12)
        ctx.move_to(x - r * 1.5 + off, yy); ctx.curve_to(x - r * .5 + off, yy - 20, x + off, yy + 20, x + r + off, yy); ctx.stroke()
    ctx.restore()
    g = cairo.RadialGradient(x, y, r * .6, x, y, r)
    g.add_color_stop_rgba(0, 0, 0, 0, 0); g.add_color_stop_rgba(1, 0, 0, 0, .55 * a)
    ctx.set_source(g); ctx.arc(x, y, r, 0, 2 * math.pi); ctx.fill()

def v1(ctx, t, d):
    p = P(t, d)
    photo(ctx, 'venus_sky', t, d, True, dark=.1, focus=(.5, .62))
    tag(ctx, "VENUS", W / 2, 200, ease(prog(p, .55, .68)), AMBER, 90, align='c')

def v2(ctx, t, d):
    p = P(t, d)
    x, y, r = 560, 500, 300
    venus(ctx, x, y, r, t)
    spin_arrow(ctx, x, y, r, -1, RED, 1, 1)
    k = ease(prog(p, .05, .15))
    tag(ctx, "SALE POR EL OESTE", x, 940, k, AMBER, 50, align='c')
    for i, (val, s, c) in enumerate([(243, "días dura su DÍA", RED), (225, "días dura su AÑO", INK)]):
        kk = ease(prog(p, .4 + i * .15, .5 + i * .15))
        w = 640 * val / 243 * kk
        col(ctx, c, .9 * kk); rrect(ctx, 1080, 400 + i * 220, w, 90, 12); ctx.fill()
        text(ctx, str(int(val * eout(kk))), 1100, 470 + i * 220, 64, BG, F_BLACK, 'l', kk)
        label(ctx, s, 1080, 540 + i * 220, kk, INK, 32, 'l')

def v3(ctx, t, d):
    p = P(t, d)
    for i, (s, c) in enumerate([("CHOQUE GIGANTE", RED), ("ATMÓSFERA QUE FRENA", AMBER)]):
        k = ease(prog(p, .05 + i * .4, .15 + i * .4)); x = 520 + i * 880
        if k <= 0: continue
        venus(ctx, x, 480, 220, t, k, sign=-1 if i else 1)
        if i == 0:
            q = prog(p, .1, .3); bx = x - 600 + 450 * q; by = 480 - 300 + 230 * q
            if q < 1: col(ctx, MUTED, k); ctx.arc(bx, by, 40, 0, 2 * math.pi); ctx.fill()
            else: glow(ctx, x - 160, 320, 160 * (1 - prog(p, .3, .45)), AMBER, k)
        else:
            ctx.set_line_width(14); col(ctx, hexc('#FFE3A8'), .35 * k); ctx.arc(x, 480, 270, 0, 2 * math.pi); ctx.stroke()
        text(ctx, s, x, 850, 52, c, F_BLACK, a=k)
        label(ctx, "Hipótesis " + str(i + 1), x, 920, k, MUTED, 28)
    big(ctx, "NADIE LO SABE CON CERTEZA", 120, 60, INK, ease(prog(p, 0, .1)))

def v4(ctx, t, d):
    p = P(t, d); cx, cy = W / 2, H / 2 + 40
    glow(ctx, cx, cy, 120, AMBER, 1); col(ctx, hexc('#FFD27A')); ctx.arc(cx, cy, 50, 0, 2 * math.pi); ctx.fill()
    col(ctx, LINE); ctx.set_line_width(2); ctx.save(); ctx.translate(cx, cy); ctx.scale(1, .32); ctx.arc(0, 0, 720, 0, 2 * math.pi); ctx.restore(); ctx.stroke()
    th = t * .5 + .6
    ux, uy = cx + 720 * math.cos(th), cy + 720 * .32 * math.sin(th)
    tilt = math.radians(98)
    ctx.save(); ctx.translate(ux, uy); ctx.rotate(tilt - math.pi / 2)
    col(ctx, hexc('#7FD8E0'), .5); ctx.set_line_width(5); ctx.save(); ctx.scale(.25, 1); ctx.arc(0, 0, 150, 0, 2 * math.pi); ctx.restore(); ctx.stroke()
    col(ctx, hexc('#9FE6EE')); ctx.arc(0, 0, 80, 0, 2 * math.pi); ctx.fill()
    col(ctx, INK); ctx.set_line_width(4); ctx.move_to(-130, 0); ctx.line_to(130, 0); ctx.stroke()
    ctx.restore()
    tag(ctx, "URANO", 80, 140, ease(prog(p, .03, .12)), hexc('#9FE6EE'), 70)
    text(ctx, f"{int(98 * eout(prog(p, .2, .5)))}°", 1700, 220, 160, AMBER, F_BLACK, a=ease(prog(p, .2, .3)))
    label(ctx, "de inclinación", 1700, 290, ease(prog(p, .25, .35)), INK, 34)
    label(ctx, "rueda como una pelota", W / 2, 1020, ease(prog(p, .55, .7)), INK, 40)

def v5(ctx, t, d):
    p = P(t, d); cx, cy, R = 600, 520, 300
    col(ctx, PANEL); ctx.arc(cx, cy, R, 0, 2 * math.pi); ctx.fill()
    col(ctx, LINE); ctx.set_line_width(6); ctx.arc(cx, cy, R, 0, 2 * math.pi); ctx.stroke()
    for i in range(24):
        a = -math.pi / 2 + i * 2 * math.pi / 24
        col(ctx, MUTED); ctx.set_line_width(4 if i % 6 == 0 else 2)
        ctx.move_to(cx + (R - 30) * math.cos(a), cy + (R - 30) * math.sin(a)); ctx.line_to(cx + (R - 10) * math.cos(a), cy + (R - 10) * math.sin(a)); ctx.stroke()
    hrs = lerp(22, 24, ease(prog(p, .2, .6)))
    a1 = -math.pi / 2 + 2 * math.pi * hrs / 24 - 1e-3
    col(ctx, AMBER, .35); ctx.move_to(cx, cy); ctx.arc(cx, cy, R - 40, -math.pi / 2, a1); ctx.close_path(); ctx.fill()
    col(ctx, AMBER); ctx.set_line_width(8); ctx.move_to(cx, cy); ctx.line_to(cx + (R - 50) * math.cos(a1), cy + (R - 50) * math.sin(a1)); ctx.stroke()
    text(ctx, f"{fmt_es(hrs, 0)} h", 1400, 470, 200, AMBER, F_BLACK)
    label(ctx, "hace ~600 millones de años: 22 h" if p < .6 else "hoy: 24 h", 1400, 560, 1, INK, 36)
    k = ease(prog(p, .65, .75))
    # Luna
    mx, my = 1650, 200; col(ctx, hexc('#CFCFC8'), k); ctx.arc(mx, my, 60, 0, 2 * math.pi); ctx.fill()
    tag(ctx, "+ ~2 milésimas de segundo por siglo", 1400, 800, k, INK, 40, align='c')

def v6(ctx, t, d):
    p = P(t, d)
    tiles = [('sunrise_west', "EL SOL, POR EL OESTE", AMBER), ('frozen_coast', "EUROPA HELADA", COLD),
             ('green_sahara', "SÁHARA VERDE", VERDE), ('pampa_desert', "ARGENTINA, DESIERTO", SAND)]
    for i, (img, s, c) in enumerate(tiles):
        k = ease(prog(p, .1 + i * .19, .2 + i * .19))
        if k <= 0: continue
        x0, y0 = (i % 2) * W / 2, (i // 2) * H / 2
        ctx.save(); ctx.rectangle(x0 + 6, y0 + 6, W / 2 - 12, H / 2 - 12); ctx.clip()
        ctx.translate(x0 + W / 4, y0 + H / 4); ctx.scale(.5, .5); ctx.translate(-W / 2, -H / 2)
        ctx.push_group(); photo(ctx, img, t, d, True, dark=.15); ctx.pop_group_to_source(); ctx.paint_with_alpha(k)
        ctx.restore()
        tag(ctx, s, x0 + 40, y0 + H / 2 - 50, k, c, 44)

def v7(ctx, t, d):
    p = P(t, d)
    if p < .42:
        k = eout(prog(p, 0, .08)) * (1 - ease(prog(p, .37, .42)))
        card(ctx, 360, 300, 1200, 400, k)
        text(ctx, "¿Qué pregunta", W / 2, 460, 90, INK, F_BLACK, a=k)
        text(ctx, "respondemos ahora?", W / 2, 580, 90, AMBER, F_BLACK, a=k)
        text(ctx, "Escríbela en los comentarios ↓", W / 2, 660, 36, MUTED, F_SEMI, a=k)
    else:
        I.end_sun(ctx, t - d * .42, d * .58)

VIS = {
    '00_hook': [h1, h2, h3, h4, h5, h6],
    '01_porque': [p1, p2, p3, p4, p5, p6, p7, p8, p9],
    '02_europa': [e1, e2, e3, e4, e5, e6, e7],
    '03_sahara': [s1, s2, s3, s4, s5, s6],
    '04_america': [a1, a2, a3, a4, a5, a6],
    '05_oceano': [o1, o2, o3, o4, o5, o6],
    '06_venus': [v1, v2, v3, v4, v5, v6, v7],
}

def blocks():
    out = []
    for name, texts in narration.BLOCKS:
        fns = VIS[name]
        assert len(fns) == len(texts), (name, len(fns), len(texts))
        out.append((name, list(zip(fns, texts))))
    return out
