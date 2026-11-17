"""Escenas: '¿Qué pasaría si se derritiera toda la Antártida?'"""
import sys, math, random, os, json, importlib.util
sys.path.append('/home/claude/video')
import cairo
import numpy as np
from lib import *
import narration

HERE = os.path.dirname(os.path.abspath(__file__))
_s = importlib.util.spec_from_file_location('tscenes', '/home/claude/tierra/scenes.py')
T = importlib.util.module_from_spec(_s); _s.loader.exec_module(T)
I = T.I; I.HERE = HERE
photo, bottom_shade, stamp, big, xmark, chip_card = I.photo, I.bottom_shade, I.stamp, I.big, I.xmark, I.chip_card
oglobe, mapbg, blobs, dot, polyline, tag, card, qmark, thermo, fmt_es = T.oglobe, T.mapbg, T.blobs, T.dot, T.polyline, T.tag, T.card, T.qmark, T.thermo, T.fmt_es
P = T.P
OCEAN, LAND2, VERDE, SAND, ICE, COLD, WARM = T.OCEAN, T.LAND2, T.VERDE, T.SAND, T.ICE, T.COLD, T.WARM
WATER = hexc('#2E8BFF'); ROCK = hexc('#7A5A40'); SNOW = hexc('#EEF4F8')
def src(ctx, s, a=1.0): source(ctx, s, a)

# ------------------------------------------------------------------ Antártida
_ATA = None
def ata():
    global _ATA
    if _ATA is None:
        d = json.load(open('/home/claude/video/world.geojson'))
        f = [f for f in d['features'] if f['properties']['name'] == 'Antarctica'][0]
        _ATA = []
        for p in f['geometry']['coordinates']:
            a = np.array(p[0], float); a[a[:, 1] < -84, 1] = -90; _ATA.append(a)
    return _ATA

# añadir la Antártida al globo ortográfico
T._rings()
T._R += [('ATA', np.radians(a)) for a in ata()]

def ice_tint(k_rock):
    def f(iso):
        if iso == 'ATA': return mix(SNOW, ROCK, k_rock)
        return hexc('#3F8A5A')
    return f

class Polar:
    """Proyección azimutal equidistante centrada en el Polo Sur."""
    def __init__(self, cx, cy, px_per_deg):
        self.cx, self.cy, self.d = cx, cy, px_per_deg
    def __call__(self, lon, lat):
        r = (90 + lat) * self.d; a = math.radians(lon)
        return self.cx + r * math.sin(a), self.cy - r * math.cos(a)

def draw_ata(ctx, Pp, c, a=1.0):
    for R in ata():
        for i, (lo, la) in enumerate(R):
            x, y = Pp(lo, la); (ctx.move_to if i == 0 else ctx.line_to)(x, y)
        ctx.close_path()
    col(ctx, c, a); ctx.fill()

def polar_bg(ctx, Pp, rmax_deg=60, others=True):
    col(ctx, OCEAN); ctx.paint()
    col(ctx, hexc('#13212E')); ctx.set_line_width(1)
    for lat in (-80, -70, -60, -50, -40):
        ctx.arc(Pp.cx, Pp.cy, (90 + lat) * Pp.d, 0, 2 * math.pi); ctx.stroke()
    if others:
        for iso, polys in geo().items():
            for poly in polys:
                pts = poly[0]
                if max(p[1] for p in pts) > -20: continue
                for i, (lo, la) in enumerate(pts):
                    x, y = Pp(lo, la); (ctx.move_to if i == 0 else ctx.line_to)(x, y)
                ctx.close_path()
        col(ctx, LAND2); ctx.fill()

def wave(ctx, x0, x1, y, t, c=WATER, a=.85, ybot=H, amp=6):
    ctx.move_to(x0, ybot); ctx.line_to(x0, y)
    for x in range(int(x0), int(x1) + 20, 20):
        ctx.line_to(x, y + amp * math.sin(x / 60 + t * 2.5))
    ctx.line_to(x1, ybot); ctx.close_path()
    g = cairo.LinearGradient(0, y, 0, ybot); g.add_color_stop_rgba(0, *c, a); g.add_color_stop_rgba(1, *hexc('#0A2A55'), a)
    ctx.set_source(g); ctx.fill()
    col(ctx, (1, 1, 1), .5 * a); ctx.set_line_width(3)
    for x in range(int(x0), int(x1), 20):
        yy = y + amp * math.sin(x / 60 + t * 2.5)
        (ctx.move_to if x == int(x0) else ctx.line_to)(x, yy)
    ctx.stroke()

def building(ctx, x, base, w, floors, fh, c=hexc('#2A3442'), a=1.0):
    col(ctx, c, a); ctx.rectangle(x, base - floors * fh, w, floors * fh); ctx.fill()
    for f in range(floors):
        for j in range(4):
            col(ctx, AMBER if (f * 7 + j * 3) % 5 else hexc('#3A4658'), .55 * a)
            ctx.rectangle(x + 14 + j * (w - 28) / 4, base - (f + 1) * fh + fh * .25, (w - 28) / 4 - 10, fh * .5); ctx.fill()

def meter(ctx, s, x, y, k, c=WATER):
    tag(ctx, s, x, y, k, c, 64)

# siluetas de ciudad
def sil_towers(ctx, x0, x1, base, seed, c, a):
    r = random.Random(seed); x = x0
    while x < x1:
        w = r.uniform(30, 70); h = r.uniform(180, 460)
        col(ctx, c, a); ctx.rectangle(x, base - h, w, h); ctx.fill(); x += w + r.uniform(2, 8)

def sil_venice(ctx, x0, x1, base, c, a):
    col(ctx, c, a)
    ctx.rectangle(x0, base - 170, x1 - x0, 170); ctx.fill()
    cx = x0 + (x1 - x0) * .3; ctx.rectangle(cx - 18, base - 430, 36, 360); ctx.fill()
    ctx.move_to(cx - 22, base - 430); ctx.line_to(cx, base - 490); ctx.line_to(cx + 22, base - 430); ctx.fill()
    for dx, r in ((.6, 55), (.75, 40), (.85, 30)):
        ctx.arc(x0 + (x1 - x0) * dx, base - 170, r, math.pi, 2 * math.pi); ctx.fill()

def sil_gables(ctx, x0, x1, base, c, a):
    x = x0; i = 0
    while x < x1:
        w = 46; h = 200 + (i % 3) * 30
        col(ctx, c, a); ctx.rectangle(x, base - h, w, h); ctx.fill()
        ctx.move_to(x, base - h); ctx.line_to(x + w / 2, base - h - 34); ctx.line_to(x + w, base - h); ctx.fill()
        x += w + 4; i += 1

def statue(ctx, x, base, pxm, c=hexc('#5FB8A0'), a=1.0):
    """Pedestal (≈47 m) y estatua (≈46 m hasta la antorcha)."""
    col(ctx, hexc('#8C8478'), a)
    ctx.move_to(x - 30 * pxm, base); ctx.line_to(x + 30 * pxm, base); ctx.line_to(x + 12 * pxm, base - 47 * pxm); ctx.line_to(x - 12 * pxm, base - 47 * pxm); ctx.close_path(); ctx.fill()
    y0 = base - 47 * pxm; col(ctx, c, a)
    ctx.move_to(x - 8 * pxm, y0); ctx.line_to(x + 8 * pxm, y0); ctx.line_to(x + 5 * pxm, y0 - 28 * pxm); ctx.line_to(x - 5 * pxm, y0 - 28 * pxm); ctx.close_path(); ctx.fill()
    ctx.arc(x, y0 - 32 * pxm, 4 * pxm, 0, 2 * math.pi); ctx.fill()
    for i in range(7):
        ang = math.pi + i * math.pi / 6; ctx.move_to(x, y0 - 34 * pxm); ctx.line_to(x + 7 * pxm * math.cos(ang), y0 - 34 * pxm + 7 * pxm * math.sin(ang))
    ctx.set_line_width(1.5 * pxm); ctx.stroke()
    ctx.set_line_width(3 * pxm); ctx.move_to(x + 4 * pxm, y0 - 26 * pxm); ctx.line_to(x + 7 * pxm, y0 - 42 * pxm); ctx.stroke()
    glow(ctx, x + 7 * pxm, y0 - 45 * pxm, 6 * pxm, AMBER, a); col(ctx, AMBER, a); ctx.arc(x + 7 * pxm, y0 - 45 * pxm, 2.2 * pxm, 0, 2 * math.pi); ctx.fill()

# ================================================================== 00 HOOK
def k1(ctx, t, d):
    p = P(t, d)
    if p < .38:
        photo(ctx, 'ice_cliff', t, d * .38, True, dark=.1)
        k = ease(prog(p, .1, .3))
        col(ctx, (1, 1, 1), .8 * k); ctx.set_line_width(4)
        r = random.Random(3)
        for _ in range(6):
            x = r.uniform(500, 1400); y = r.uniform(250, 500); ctx.move_to(x, y)
            for j in range(int(6 * k) + 1): x += r.uniform(-30, 30); y += r.uniform(20, 50); ctx.line_to(x, y)
            ctx.stroke()
        return
    col(ctx, BG); ctx.paint()
    base, pxm = 1000, 13.0
    building(ctx, 820, base, 280, 19, 58 * pxm / 19)
    lvl = 58 * ease(prog(p, .45, .9))
    wave(ctx, 0, W, base - lvl * pxm, t)
    y58 = base - 58 * pxm
    col(ctx, AMBER); ctx.set_line_width(4); ctx.set_dash([14, 10]); ctx.move_to(200, y58); ctx.line_to(1720, y58); ctx.stroke(); ctx.set_dash([])
    text(ctx, f"+{int(lvl)} m", 1500, y58 - 30, 96, INK, F_BLACK, a=ease(prog(p, .4, .5)))
    label(ctx, "≈ 20 pisos", 520, y58 - 30, ease(prog(p, .5, .6)), AMBER, 44)

def k2(ctx, t, d):
    p = P(t, d)
    for i, (img, s, c, ok) in enumerate([('madrid_gate', "MADRID · ≈650 m", VERDE, True), ('obelisk_flood', "BUENOS AIRES", RED, False)]):
        k = ease(prog(p, i * .4, .1 + i * .4))
        if k <= 0: continue
        x0 = i * W / 2
        ctx.save(); ctx.rectangle(x0 + 4, 0, W / 2 - 8, H); ctx.clip()
        ctx.translate(x0 + W / 4, H / 2); ctx.scale(.75, .75); ctx.translate(-W / 2, -H / 2)
        ctx.push_group(); photo(ctx, img, t, d, True, dark=.15); ctx.pop_group_to_source(); ctx.paint_with_alpha(k)
        ctx.restore()
        tag(ctx, s, x0 + W / 4, 980, k, c, 50, align='c')
        text(ctx, "✓" if ok else "✗", x0 + W / 4, 260, 180, c, F_BLACK, a=ease(prog(p, .1 + i * .4, .2 + i * .4)))

def k3(ctx, t, d):
    p = P(t, d)
    photo(ctx, 'low_sea_cliff', t, d, True, dark=.15)
    k = ease(prog(p, .3, .45))
    if k > 0:
        x, y = 1600, 380 + 60 * ease(prog(p, .45, .8))
        col(ctx, AMBER, k); ctx.set_line_width(26); ctx.move_to(x, 220); ctx.line_to(x, y); ctx.stroke()
        ctx.move_to(x - 60, y); ctx.line_to(x + 60, y); ctx.line_to(x, y + 80); ctx.close_path(); ctx.fill()
    tag(ctx, "AQUÍ, EL MAR BAJA", 80, 1000, ease(prog(p, .45, .55)), AMBER, 60)

def k4(ctx, t, d):
    p = P(t, d); x, y, r = 640, H / 2, 380
    oglobe(ctx, x, y, r, t * 8, lat0=-62, tint=ice_tint(0))
    for i, s in enumerate(["NASA · satélites GRACE", "Nature · 2020 y 2023", "Science Advances · 2015", "Universidad de Harvard"]):
        chip_card(ctx, 1150, 260 + i * 150, 680, 110, s, "", ease(prog(p, .3 + i * .1, .4 + i * .1)))

def k5(ctx, t, d):
    p = P(t, d)
    photo(ctx, 'bare_antarctica', t, d, True, dark=.35)
    k = ease(prog(p, .1, .2))
    thermo(ctx, 260, 820, 520, lerp(.8, .4, ease(prog(p, .1, .6))), mix(RED, COLD, ease(prog(p, .1, .6))), k)
    qmark(ctx, 1100, 480, 300, ease(prog(p, .55, .7)))
    tag(ctx, "¿POR QUÉ NO VUELVE?", 1100, 980, ease(prog(p, .65, .75)), INK, 56, align='c')

# ================================================================== 01 TAMAÑO
PP = Polar(560, 560, 14.0)
def europe_overlay(ctx, cx, cy, kmpx, c, a):
    for iso in EUROPE:
        for poly in geo().get(iso, []):
            for i, (lo, la) in enumerate(poly[0]):
                x = cx + (lo - 15) * math.cos(math.radians(52)) * 111 * kmpx; y = cy - (la - 52) * 111 * kmpx
                (ctx.move_to if i == 0 else ctx.line_to)(x, y)
            ctx.close_path()
    col(ctx, c, a); ctx.fill()

def t1(ctx, t, d):
    p = P(t, d)
    polar_bg(ctx, PP, others=False)
    draw_ata(ctx, PP, SNOW)
    kmpx = PP.d / 111
    k = ease(prog(p, .3, .5))
    ox = lerp(1400, 560, ease(prog(p, .3, .6)))
    europe_overlay(ctx, ox, 560, kmpx, AMBER, .75 * k)
    text(ctx, "14 millones de km²", 1420, 220, 70, INK, F_BLACK, a=ease(prog(p, .05, .15)))
    text(ctx, "≈ 1,4 × EUROPA", 1420, 330, 90, AMBER, F_BLACK, a=ease(prog(p, .6, .7)))

def t2(ctx, t, d):
    p = P(t, d); base = 960; pxkm = 130
    col(ctx, BG); ctx.paint()
    k = ease(prog(p, 0, .25))
    col(ctx, ROCK); ctx.rectangle(0, base, W, H - base); ctx.fill()
    pts = [(0, 2.0), (300, 2.6), (600, 3.4), (900, 4.9), (1100, 4.2), (1400, 3.0), (1700, 2.2), (1920, 1.6)]
    ctx.move_to(0, base)
    for x, h in pts: ctx.line_to(x, base - h * pxkm * k)
    ctx.line_to(W, base); ctx.close_path()
    g = cairo.LinearGradient(0, base - 640, 0, base); g.add_color_stop_rgb(0, *SNOW); g.add_color_stop_rgb(1, *hexc('#8FB8D8')); ctx.set_source(g); ctx.fill()
    ka = ease(prog(p, .2, .35))
    yav = base - 1.94 * pxkm
    col(ctx, WATER, ka); ctx.set_line_width(3); ctx.set_dash([12, 8]); ctx.move_to(0, yav); ctx.line_to(W, yav); ctx.stroke(); ctx.set_dash([])
    tag(ctx, "media ≈ 2 km", 80, yav - 20, ka, BG, 40, bg=SNOW)
    km = ease(prog(p, .35, .5))
    x = 900; col(ctx, RED, km); ctx.set_line_width(5); ctx.move_to(x, base); ctx.line_to(x, base - 4.9 * pxkm * k); ctx.stroke()
    tag(ctx, "≈ 4,9 km", x + 30, base - 4.9 * pxkm - 10, km, RED, 54)
    kt = ease(prog(p, .55, .7))
    if kt > 0:  # Teide
        tx = 1500; th = 3.715 * pxkm
        col(ctx, hexc('#5A4636'), kt); ctx.move_to(tx - 260, base); ctx.line_to(tx - 30, base - th); ctx.line_to(tx + 30, base - th); ctx.line_to(tx + 260, base); ctx.close_path(); ctx.fill()
        tag(ctx, "Teide · 3.715 m", tx - 150, base - th - 40, kt, INK, 40)

def t3(ctx, t, d):
    p = P(t, d)
    photo(ctx, 'ice_aerial', t, d, True, dark=.25)
    v = -89.2 * eout(prog(p, .1, .55))
    thermo(ctx, 320, 850, 560, lerp(.6, .05, eout(prog(p, .1, .55))), COLD)
    text(ctx, f"{fmt_es(v)} °C", 1200, 560, 200, INK, F_BLACK, a=ease(prog(p, .05, .15)))
    tag(ctx, "BASE VOSTOK", 1200, 700, ease(prog(p, .3, .4)), COLD, 50, align='c')

def t4(ctx, t, d):
    p = P(t, d)
    IB = Proj(-10, 4.5, 35.5, 44.2, 80, 140, 900, 860)
    col(ctx, BG); ctx.paint()
    draw_map(ctx, IB, {'ESP': (hexc('#3A4A5C'), 1)}, base=LAND2, edge=T.EDGE2)
    k = ease(prog(p, .1, .5))
    hb = 820 * k
    col(ctx, SNOW, .9); ctx.rectangle(1080, 960 - hb, 160, hb); ctx.fill()
    text(ctx, f"{int(53 * k)} km", 1160, 940 - hb, 70, INK, F_BLACK, a=ease(prog(p, .1, .2)))
    ke = ease(prog(p, .5, .8))
    for i in range(6):
        if ke * 6 > i:
            y0 = 960 - i * 820 / 6.0
            col(ctx, ROCK, .9); ctx.move_to(1340, y0); ctx.line_to(1430, y0 - 820 / 6.0); ctx.line_to(1520, y0); ctx.close_path(); ctx.fill()
    tag(ctx, "= 6 EVEREST", 1560, 520, ease(prog(p, .78, .88)), AMBER, 56)
    label(ctx, "Hielo de la Antártida extendido sobre España", 540, 1040, ease(prog(p, .05, .15)), MUTED, 30)

def t5(ctx, t, d):
    p = P(t, d)
    polar_bg(ctx, PP, others=False); draw_ata(ctx, PP, SNOW)
    for i in range(10):
        x0, y0 = 1250 + (i % 5) * 120, 300 + (i // 5) * 130
        if i < 9:
            q = ease(prog(p, .2 + i * .04, .45 + i * .04)); ang = i * .7
            x = lerp(x0, 560 + 150 * math.cos(ang), q); y = lerp(y0, 560 + 150 * math.sin(ang), q)
        else:
            x, y = x0, y0
        col(ctx, ICE); rrect(ctx, x - 40, y - 40, 80, 80, 12); ctx.fill()
        col(ctx, hexc('#8FB8D8')); ctx.set_line_width(3); rrect(ctx, x - 40, y - 40, 80, 80, 12); ctx.stroke()
    text(ctx, "90 %", 1500, 820, 200, AMBER, F_BLACK, a=ease(prog(p, .6, .7)))
    label(ctx, "del hielo del planeta", 1500, 900, ease(prog(p, .62, .72)), INK, 40)

def t6(ctx, t, d): T.p6(ctx, t, d)

def t7(ctx, t, d):
    p = P(t, d)
    photo(ctx, 'ice_cliff', t, d, True, dark=.2, focus=(.5, .4))
    lvl = ease(prog(p, .2, .9))
    ctx.push_group(); wave(ctx, 0, W, lerp(H + 20, 640, lvl), t, a=.7); ctx.pop_group_to_source(); ctx.paint()
    qmark(ctx, W / 2, 400, 260, ease(prog(p, .5, .65)))

# ================================================================== 02 SUBIDA
def u1(ctx, t, d):
    p = P(t, d); col(ctx, BG); ctx.paint()
    base = 860; pxm = 22
    cities = [("MIAMI", lambda x0, x1: sil_towers(ctx, x0, x1, base, 2, hexc('#3A4658'), 1)),
              ("VENECIA", lambda x0, x1: sil_venice(ctx, x0, x1, base, hexc('#3A4658'), 1)),
              ("GUAYAQUIL", lambda x0, x1: sil_towers(ctx, x0, x1, base, 7, hexc('#3A4658'), 1)),
              ("ÁMSTERDAM", lambda x0, x1: sil_gables(ctx, x0, x1, base, hexc('#3A4658'), 1))]
    for i, (n, f) in enumerate(cities):
        x0 = 40 + i * 470; f(x0, x0 + 420)
        text(ctx, n, x0 + 210, 960, 46, INK, F_BLACK, a=ease(prog(p, i * .08, .1 + i * .08)))
    lvl = 5 * ease(prog(p, .2, .6))
    wave(ctx, 0, W, base - lvl * pxm * 1.0 - 10, t, a=.8, ybot=920)
    meter(ctx, f"+{fmt_es(lvl, 0)} m", 80, 180, 1)
    k = ease(prog(p, .7, .8))
    if k > 0:
        col(ctx, hexc('#8C8478'), k); ctx.rectangle(1450, base - 160, 420, 30); ctx.fill()
        tag(ctx, "DIQUES", 1660, 650, k, AMBER, 46, align='c')

FLOOD_ES = [(-6.0, 37.4, .5), (-6.25, 37.1, .55), (-6.35, 36.85, .45), (-6.1, 37.7, .3), (-0.38, 39.47, .3), (-0.33, 39.25, .3),
            (2.17, 41.38, .12), (2.05, 41.32, .12), (0.75, 40.7, .25), (-0.8, 37.7, .18), (-0.7, 38.0, .15)]
def u2(ctx, t, d):
    p = P(t, d)
    IB = Proj(-10, 4.5, 35.5, 44.2, 0, 0, W, H)
    mapbg(ctx, IB)
    g = ease(prog(p, .05, .55))
    items = [(lo, la, 1.9 * r * g + .01) for lo, la, r in FLOOD_ES]
    blobs(ctx, IB, items, WATER, 1)
    for i, (lo, la, n, al) in enumerate([(-5.98, 37.39, "Sevilla", 'r'), (-0.38, 39.47, "Valencia", 'l'), (2.17, 41.39, "Barcelona", 'l'),
                                          (0.75, 40.7, "Delta del Ebro", 'l'), (-6.4, 36.95, "Doñana", 'r'), (-0.8, 37.7, "Mar Menor", 'l')]):
        dot(ctx, IB, lo, la, n, ease(prog(p, .1 + i * .1, .18 + i * .1)), INK, size=30, dx=18 if al == 'l' else -18, align=al)
    meter(ctx, f"+{int(25 * eout(prog(p, .05, .5)))} m", 80, 160, 1)
    dot(ctx, IB, -3.7, 40.4, "Madrid · a salvo", ease(prog(p, .85, .95)), VERDE, size=30)

FLOOD_W = [(-58.4, -34.6, 2.2), (-56.2, -34.9, 1.2), (-74.8, 11.0, 1.2), (5.0, 52.3, 1.8), (-81.5, 27.5, 3.2), (-80.4, 25.8, 1.6), (90, 23.5, 2.5), (121.4, 31.2, 1.6), (-90.0, 29.9, 1.4)]
def u3(ctx, t, d):
    p = P(t, d)
    mapbg(ctx, T.WORLD)
    g = ease(prog(p, .05, .5))
    blobs(ctx, T.WORLD, [(lo, la, 2.2 * r * g + .01) for lo, la, r in FLOOD_W], WATER, 1, on_land=False)
    for lo, la, r in FLOOD_W:
        x, y = T.WORLD(lo, la); col(ctx, WATER, .8 * g); ctx.set_line_width(3); ctx.arc(x, y, 24 + 14 * ((t * .8) % 1), 0, 2 * math.pi); ctx.stroke()
    for i, (lo, la, n, al) in enumerate([(-58.4, -34.6, "Buenos Aires · Montevideo", 'l'), (-74.8, 11.0, "Barranquilla", 'r'), (5.0, 52.3, "Países Bajos", 'r'), (-81.5, 27.5, "Florida", 'r')]):
        dot(ctx, T.WORLD, lo, la, n, ease(prog(p, .2 + i * .12, .3 + i * .12)), INK, size=30, dx=18 if al == 'l' else -18, align=al)
    meter(ctx, f"+{int(58 * eout(prog(p, .05, .5)))} m", 80, 160, 1)

def u4(ctx, t, d):
    p = P(t, d); col(ctx, BG); ctx.paint()
    base, pxm = 1000, 9.0
    statue(ctx, 960, base, pxm)
    lvl = 58 * ease(prog(p, .1, .7))
    wave(ctx, 0, W, base - lvl * pxm, t, a=.75)
    for m, s in ((47, "pedestal · 47 m"), (58, "+58 m")):
        y = base - m * pxm; col(ctx, AMBER if m == 58 else MUTED, .9); ctx.set_line_width(3); ctx.set_dash([10, 8]); ctx.move_to(1150, y); ctx.line_to(1500, y); ctx.stroke(); ctx.set_dash([])
        text(ctx, s, 1520, y + 14, 40, AMBER if m == 58 else MUTED, F_XB, 'l', ease(prog(p, .3 if m == 47 else .6, .45 if m == 47 else .7)))
    tag(ctx, "NUEVA YORK", 80, 140, ease(prog(p, 0, .1)), INK, 56)

def u5(ctx, t, d):
    p = P(t, d); col(ctx, BG); ctx.paint()
    base = 960; pxm = 760 / 3700
    cities = [("Madrid", 650), ("Ciudad de México", 2240), ("Bogotá", 2640), ("Quito", 2850), ("La Paz", 3640)]
    for i, (n, h) in enumerate(cities):
        k = ease(prog(p, .05 + i * .12, .2 + i * .12)); x = 260 + i * 330
        hh = h * pxm * k
        col(ctx, VERDE, .85); rrect(ctx, x - 90, base - hh, 180, hh, 10); ctx.fill()
        text(ctx, f"{fmt_int(int(h * k))} m", x, base - hh - 20, 46, INK, F_BLACK, a=k)
        label(ctx, n, x, base + 50, k, INK, 32)
    wave(ctx, 0, W, base - 58 * pxm, t, a=.9, ybot=base + 4, amp=3)
    tag(ctx, "el mar: +58 m", 1500, base - 40, ease(prog(p, .7, .8)), WATER, 36)

def u6(ctx, t, d):
    p = P(t, d)
    photo(ctx, 'ice_aerial', t, d, True, dark=.4)
    qmark(ctx, W / 2, 480, 300, ease(prog(p, .35, .5)))
    big(ctx, "DEBAJO DEL HIELO…", 860, 80, INK, ease(prog(p, .1, .25)))

# ================================================================== 03 GRAVEDAD
def g1(ctx, t, d):
    p = P(t, d)
    if p < .55:
        x, y, r = W / 2, H / 2, 420
        oglobe(ctx, x, y, r, t * 6, lat0=-70, tint=ice_tint(ease(prog(p, .1, .45))))
        tag(ctx, "TIERRA", W / 2, 1040, ease(prog(p, .3, .4)), ROCK, 60, align='c')
    else:
        photo(ctx, 'bare_antarctica', t - d * .55, d * .45, True, dark=.1)
        tag(ctx, "ANTÁRTIDA OCCIDENTAL: ROCA BAJO EL MAR", 80, 1000, ease(prog(p, .65, .75)), INK, 44)

def g2(ctx, t, d):
    p = P(t, d)
    if p < .55:
        col(ctx, BG); ctx.paint()
        q = ease(prog(p, .15, .35)); rise = ease(prog(p, .3, .52))
        depth = 160 * (1 - rise)
        sea = 520
        ctx.move_to(0, H)
        for x in range(0, W + 20, 20):
            dd = depth * math.exp(-((x - W / 2) / 420) ** 2)
            ctx.line_to(x, 640 + dd)
        ctx.line_to(W, H); ctx.close_path(); col(ctx, ROCK); ctx.fill()
        col(ctx, WATER, .5); ctx.rectangle(0, sea, 300, 640 - sea); ctx.fill(); ctx.rectangle(W - 300, sea, 300, 640 - sea); ctx.fill()
        if q < 1:
            col(ctx, SNOW, 1 - q); ctx.move_to(360, 640 + 10)
            for x in range(360, W - 340, 20):
                ctx.line_to(x, 640 + depth * math.exp(-((x - W / 2) / 420) ** 2) - 420 * math.exp(-((x - W / 2) / 520) ** 2) * (1 - q) - 10)
            ctx.line_to(W - 360, 650); ctx.close_path(); ctx.fill()
        if rise > 0:
            col(ctx, AMBER, rise); ctx.set_line_width(10)
            for x in (760, 960, 1160): ctx.move_to(x, 900); ctx.line_to(x, 820); ctx.stroke(); ctx.move_to(x - 25, 830); ctx.line_to(x, 790); ctx.line_to(x + 25, 830); ctx.fill()
        tag(ctx, "LA ROCA SUBE · CIENTOS DE METROS", 80, 1040, ease(prog(p, .35, .45)), AMBER, 42)
    else:
        PQ = Polar(W / 2, H / 2 + 20, 15.0)
        polar_bg(ctx, PQ, others=False); draw_ata(ctx, PQ, ROCK)
        k = ease(prog(p, .6, .85))
        seas = [(-120, -80, 4.5), (-100, -78, 3.5), (-140, -82, 3), (-85, -80, 3), (-110, -83.5, 2.5), (-150, -79, 2.5), (-70, -77, 2)]
        for lo, la, r in seas:
            x, y = PQ(lo, la); col(ctx, OCEAN, k); ctx.arc(x, y, r * PQ.d * k, 0, 2 * math.pi); ctx.fill()
        tag(ctx, "UN ARCHIPIÉLAGO", 80, 140, k, AMBER, 60)

def earth_section(ctx, t, bulge_s, bulge_n, ice_k):
    cx, cy, r = W / 2, H / 2 + 30, 330
    pts = []
    for i in range(181):
        th = i * 2 * math.pi / 180
        dS = (th - math.pi / 2 + math.pi) % (2 * math.pi) - math.pi
        dN = (th + math.pi / 2 + math.pi) % (2 * math.pi) - math.pi
        rr = r + 40 + bulge_s * math.exp(-(dS / .45) ** 2) + bulge_n * (math.cos(dN) * .5 + .5) * .6
        pts.append((cx + rr * math.cos(th), cy + rr * math.sin(th)))
    ctx.move_to(*pts[0])
    for q in pts[1:]: ctx.line_to(*q)
    ctx.close_path(); col(ctx, WATER, .85); ctx.fill()
    col(ctx, hexc('#4A3A2C')); ctx.arc(cx, cy, r, 0, 2 * math.pi); ctx.fill()
    if ice_k > 0:
        col(ctx, SNOW, ice_k); ctx.save(); ctx.translate(cx, cy + r - 10); ctx.scale(1, .45); ctx.arc(0, 0, 200, 0, math.pi * 2); ctx.restore(); ctx.fill()
    return cx, cy, r

def g3(ctx, t, d):
    p = P(t, d); col(ctx, BG); ctx.paint()
    cx, cy, r = earth_section(ctx, t, 70 * ease(prog(p, .2, .5)), 0, 1)
    k = ease(prog(p, .35, .5))
    col(ctx, WARM, k); ctx.set_line_width(8)
    for a in (-.5, .5, -1.0, 1.0):
        th = math.pi / 2 + a * .55; x0, y0 = cx + (r + 230) * math.cos(th), cy + (r + 230) * math.sin(th)
        x1, y1 = cx + (r + 90) * math.cos(th * .85 + math.pi / 2 * .15), cy + (r + 90) * math.sin(th * .85 + math.pi / 2 * .15)
        ctx.move_to(x0, y0); ctx.line_to(x1, y1); ctx.stroke(); ctx.arc(x1, y1, 12, 0, 2 * math.pi); ctx.fill()
    tag(ctx, "LA GRAVEDAD DEL HIELO ATRAE EL MAR", 80, 140, ease(prog(p, .5, .6)), WARM, 44)
    label(ctx, "Antártida", cx, cy + r + 150, ease(prog(p, .05, .15)), INK, 34)

def g4(ctx, t, d):
    p = P(t, d); col(ctx, BG); ctx.paint()
    q = ease(prog(p, .1, .5))
    cx, cy, r = earth_section(ctx, t, 70 * (1 - q) - 25 * q, 40 * q, 1 - q)
    k = ease(prog(p, .35, .5))
    col(ctx, AMBER, k); ctx.set_line_width(9)
    for x in (cx - 260, cx + 260):
        ctx.move_to(x, cy + 120); ctx.line_to(x, cy - 160); ctx.stroke(); ctx.move_to(x - 25, cy - 150); ctx.line_to(x, cy - 200); ctx.line_to(x + 25, cy - 150); ctx.fill()
    tag(ctx, "EL AGUA SE VA AL NORTE", 80, 140, k, AMBER, 50)
    tag(ctx, "JUNTO A LA ANTÁRTIDA: EL MAR BAJA", W / 2, 1050, ease(prog(p, .55, .65)), INK, 42, align='c')
    dot(ctx, lambda lo, la: (cx + 360, cy + 300), 0, 0, "Tierra del Fuego", ease(prog(p, .75, .85)), AMBER, size=30)

def g5(ctx, t, d):
    p = P(t, d)
    mapbg(ctx, T.ATL)
    blobs(ctx, T.ATL, [(-75, 38, 6), (-71, 42, 5), (-80, 32, 5)], WATER, ease(prog(p, .1, .3)), on_land=False)
    text(ctx, "+30 %", 1250, 520, 220, WATER, F_BLACK, a=ease(prog(p, .3, .4)))
    label(ctx, "más que la media mundial", 1250, 600, ease(prog(p, .35, .45)), INK, 40)
    dot(ctx, T.ATL, -77, 38.9, "Washington", ease(prog(p, .15, .25)), INK, size=28, dx=-18, align='r')
    dot(ctx, T.ATL, -71.1, 42.4, "Boston", ease(prog(p, .2, .3)), INK, size=28, dx=-18, align='r')
    src(ctx, "Mitrovica et al. (2009), Science · Universidad de Harvard · escenario: solo Antártida Occidental")

def g6(ctx, t, d):
    p = P(t, d)
    photo(ctx, 'deep_current', t, d, True, dark=.35)
    qmark(ctx, W / 2, 480, 280, ease(prog(p, .3, .5)))

# ================================================================== 04 OCÉANO
PS = Polar(W / 2, H / 2 + 20, 9.5)
def currents(ctx, t, k, slow=0.0):
    for lon in range(-150, 210, 60):
        pts = [(lon + 10 * math.sin(la / 8), la) for la in range(-70, -24, 3)]
        polyline(ctx, PS, pts, COLD, k, 10, prog_=1, flow_t=t * (1 - slow * .7))

def c1(ctx, t, d):
    p = P(t, d)
    polar_bg(ctx, PS); draw_ata(ctx, PS, SNOW)
    currents(ctx, t, ease(prog(p, .1, .3)))
    tag(ctx, "OXÍGENO", 80, 180, ease(prog(p, .4, .5)), COLD, 56)
    tag(ctx, "NUTRIENTES", 80, 300, ease(prog(p, .48, .58)), VERDE, 56)
    text(ctx, "≈ 40 %", 1600, 820, 150, AMBER, F_BLACK, a=ease(prog(p, .7, .8)))
    label(ctx, "de las profundidades", 1600, 890, ease(prog(p, .72, .82)), INK, 34)

def c2(ctx, t, d):
    p = P(t, d)
    polar_bg(ctx, PS); draw_ata(ctx, PS, SNOW)
    s = ease(prog(p, .2, .6))
    currents(ctx, t, 1 - .5 * s, slow=s)
    col(ctx, hexc('#BFE3FF'), .35 * s); ctx.arc(PS.cx, PS.cy, (90 - 62) * PS.d, 0, 2 * math.pi); ctx.fill()
    text(ctx, f"−{int(40 * s)} %", 1560, 520, 170, RED, F_BLACK, a=ease(prog(p, .2, .3)))
    label(ctx, "hacia 2050", 1560, 600, ease(prog(p, .3, .4)), INK, 34)
    label(ctx, "solo con el deshielo actual", 1560, 650, ease(prog(p, .3, .4)), MUTED, 28)
    src(ctx, "Li et al. (2023), Nature")

def c3(ctx, t, d):
    p = P(t, d); col(ctx, BG); ctx.paint()
    for i, (c, s, refl) in enumerate([(SNOW, "HIELO: REFLEJA", True), (hexc('#1E2A38'), "ROCA Y MAR: ABSORBEN", False)]):
        k = ease(prog(p, i * .35, .15 + i * .35)); x0 = i * W / 2
        if k <= 0: continue
        col(ctx, c, k); ctx.rectangle(x0 + 60, 760, W / 2 - 120, 140); ctx.fill()
        for j in range(5):
            x = x0 + 200 + j * 130; q = (t * .8 + j * .2) % 1
            col(ctx, AMBER, k); ctx.set_line_width(5); ctx.set_dash([14, 10])
            ctx.move_to(x - 120, 200); ctx.line_to(x, 760); ctx.stroke()
            if refl: ctx.move_to(x, 760); ctx.line_to(x + 120, 200); ctx.stroke()
            ctx.set_dash([])
            if not refl: glow(ctx, x, 800, 60, RED, k * .8)
        text(ctx, s, x0 + W / 4, 1000, 48, INK, F_BLACK, a=k)

def c4(ctx, t, d):
    p = P(t, d); col(ctx, BG); ctx.paint(); cx, cy, R = W / 2, H / 2, 300
    k = ease(prog(p, 0, .2))
    rot = t * 1.2
    for i, (s, c) in enumerate([("MENOS HIELO", COLD), ("MÁS CALOR", RED)]):
        a0 = rot + i * math.pi
        col(ctx, c, k); ctx.set_line_width(14); ctx.arc(cx, cy, R, a0 + .25, a0 + math.pi - .25); ctx.stroke()
        ex, ey = cx + R * math.cos(a0 + math.pi - .25), cy + R * math.sin(a0 + math.pi - .25)
        ctx.arc(ex, ey, 20, 0, 2 * math.pi); ctx.fill()
        text(ctx, s, cx + (R + 230) * (1 if i == 0 else -1), cy + 20, 60, c, F_BLACK, a=ease(prog(p, .1 + i * .2, .2 + i * .2)))

def c5(ctx, t, d):
    p = P(t, d); k = eout(prog(p, 0, .2))
    card(ctx, 360, 280, 1200, 420, k)
    text(ctx, "¿A qué altura está", W / 2, 440, 84, INK, F_BLACK, a=k)
    text(ctx, "tu ciudad?", W / 2, 560, 90, AMBER, F_BLACK, a=k)
    text(ctx, "Escríbelo en los comentarios ↓", W / 2, 650, 36, MUTED, F_SEMI, a=ease(prog(p, .3, .45)))

def c6(ctx, t, d):
    p = P(t, d)
    photo(ctx, 'polar_forest', t, d, True, dark=.65 - .3 * ease(prog(p, .2, .9)))
    qmark(ctx, W / 2, 480, 280, ease(prog(p, .3, .5)) * (1 - ease(prog(p, .8, .95))))

# ================================================================== 05 PASADO
def f1(ctx, t, d):
    p = P(t, d)
    photo(ctx, 'drill_ship', t, d, True, dark=.15)
    stamp(ctx, "2017 · ANTÁRTIDA OCCIDENTAL", 80, 140, ease(prog(p, .05, .15)), AMBER, 46)
    tag(ctx, "A MENOS DE 900 KM DEL POLO SUR", 80, 1000, ease(prog(p, .4, .5)), INK, 46)

def f2(ctx, t, d):
    p = P(t, d); col(ctx, BG); ctx.paint()
    col(ctx, hexc('#0E2A44')); ctx.rectangle(0, 200, W, 300); ctx.fill()
    for i, c in enumerate(['#4A3A2C', '#5A4636', '#3E3226', '#6B5440']):
        col(ctx, hexc(c)); ctx.rectangle(0, 500 + i * 140, W, 140); ctx.fill()
    q = ease(prog(p, .05, .45)); x = 600
    col(ctx, LINE); ctx.rectangle(x - 22, 120, 44, 380 + 560 * q); ctx.fill()
    k = ease(prog(p, .45, .6))
    if k > 0:
        cx = lerp(x, 1250, k)
        col(ctx, hexc('#6B5440')); rrect(ctx, cx - 70, 260, 140, 680, 20); ctx.fill()
        r = random.Random(5); col(ctx, hexc('#E8D2A8'), k); ctx.set_line_width(3)
        for _ in range(26):
            yy = r.uniform(300, 900); xx = cx + r.uniform(-50, 50); ctx.move_to(xx, yy)
            for j in range(5): xx += r.uniform(-14, 14); yy += r.uniform(5, 20); ctx.line_to(xx, yy)
            ctx.stroke()
    tag(ctx, "RAÍCES · POLEN · ESPORAS", 1330, 400, ease(prog(p, .6, .7)), AMBER, 44)
    text(ctx, "90 millones de años", 1580, 640, 64, INK, F_BLACK, a=ease(prog(p, .7, .8)))

def f3(ctx, t, d):
    p = P(t, d)
    photo(ctx, 'polar_forest', t, d, True, dark=.1)
    thermo(ctx, 200, 840, 480, .55 * ease(prog(p, .05, .3)), WARM, ease(prog(p, .02, .1)))
    text(ctx, "≈ 12 °C", 300, 500, 120, INK, F_BLACK, 'l', ease(prog(p, .1, .2)))
    label(ctx, "temperatura media", 300, 560, ease(prog(p, .15, .25)), INK, 34, 'l')
    tag(ctx, "4 MESES DE NOCHE POLAR", 80, 1000 if False else 1010, ease(prog(p, .6, .7)), COLD, 46)

def f4(ctx, t, d):
    p = P(t, d)
    photo(ctx, 'seymour_fossils', t, d, True, dark=.2)
    stamp(ctx, "ISLA SEYMOUR", 80, 140, ease(prog(p, .05, .15)), AMBER, 50)
    for i, s in enumerate(["DINOSAURIOS", "PINGÜINOS DE ≈2 M", "MARSUPIALES"]):
        tag(ctx, s, 80, 720 + i * 110, ease(prog(p, .3 + i * .15, .4 + i * .15)), INK, 50)

def f5(ctx, t, d):
    p = P(t, d); col(ctx, BG); ctx.paint(); base = 920; pxp = 640 / 1700
    for i, (lo, hi, s, c) in enumerate([(420, 420, "HOY", COLD), (1120, 1680, "LA SELVA", WARM)]):
        k = ease(prog(p, .05 + i * .25, .25 + i * .25)); x = 560 + i * 520
        col(ctx, LINE); rrect(ctx, x - 90, base - 680, 180, 680, 30); ctx.fill()
        col(ctx, c, .9); rrect(ctx, x - 80, base - hi * pxp * k, 160, hi * pxp * k, 24); ctx.fill()
        if hi != lo:
            col(ctx, (0, 0, 0), .3); ctx.rectangle(x - 80, base - hi * pxp * k, 160, (hi - lo) * pxp * k); ctx.fill()
        text(ctx, s, x, base + 70, 48, INK, F_BLACK, a=k)
        text(ctx, f"{fmt_int(lo)}" + (f"–{fmt_int(hi)}" if hi != lo else ""), x, base - hi * pxp * k - 30, 50, INK, F_BLACK, a=k)
    label(ctx, "partes por millón de CO₂", 820, 1060, 1, MUTED, 30)
    text(ctx, "× 3–4", 1600, 560, 180, AMBER, F_BLACK, a=ease(prog(p, .6, .7)))
    src(ctx, "Klages et al. (2020), Nature")

def f6(ctx, t, d):
    p = P(t, d); x, y, r = 700, H / 2, 380
    q = ease(prog(p, .15, .7))
    oglobe(ctx, x, y, r, t * 6, lat0=-70, tint=ice_tint(1 - q))
    v = 34 * eout(prog(p, .1, .6))
    text(ctx, f"hace {int(v)} millones de años", 1500, 520, 60, INK, F_BLACK, a=ease(prog(p, .05, .15)))
    tag(ctx, "CO₂ BAJA → NACE EL HIELO", 1500, 680, ease(prog(p, .4, .5)), COLD, 46, align='c')

def f7(ctx, t, d):
    p = P(t, d)
    photo(ctx, 'ice_aerial', t, d, True, dark=.35)
    big(ctx, "¿PUEDE VOLVER", 440, 110, INK, ease(prog(p, .1, .25)))
    big(ctx, "A DESAPARECER?", 580, 110, AMBER, ease(prog(p, .2, .35)))

# ================================================================== 06 FUTURO
def n1(ctx, t, d):
    p = P(t, d); x, y, r = 640, H / 2, 360
    oglobe(ctx, x, y, r, t * 6, lat0=-62, tint=ice_tint(0))
    for j in range(2):
        a = t * .9 - j * .25
        sx, sy = x + (r + 70) * math.cos(a), y + (r + 70) * .35 * math.sin(a)
        col(ctx, INK); ctx.rectangle(sx - 14, sy - 8, 28, 16); ctx.fill()
        col(ctx, COLD); ctx.rectangle(sx - 44, sy - 4, 26, 8); ctx.fill(); ctx.rectangle(sx + 18, sy - 4, 26, 8); ctx.fill()
    tag(ctx, "GRACE · NASA", 1450, 220, ease(prog(p, .05, .15)), COLD, 50, align='c')
    v = 135 * eout(prog(p, .45, .85))
    text(ctx, f"{int(v)}.000", 1450, 560, 170, AMBER, F_BLACK, a=ease(prog(p, .42, .5)))
    label(ctx, "millones de toneladas de hielo al año", 1450, 640, ease(prog(p, .45, .55)), INK, 34)
    src(ctx, "NASA · media desde 2002", ease(prog(p, .5, .6)))

def n2(ctx, t, d):
    p = P(t, d); col(ctx, BG); ctx.paint()
    v = 180000 * eout(prog(p, .05, .45))
    text(ctx, fmt_int(int(v)), W / 2, 520, 240, INK, F_BLACK, a=ease(prog(p, .02, .1)))
    label(ctx, "años a ese ritmo", W / 2, 610, ease(prog(p, .1, .2)), INK, 44)
    k = ease(prog(p, .6, .7))
    if k > 0:
        col(ctx, RED, .85 * k); rrect(ctx, W / 2 - 420, 720, 840, 120, 18); ctx.fill()
        text(ctx, "EL RITMO NO ES FIJO", W / 2, 800, 56, INK, F_BLACK, a=k)

def n3(ctx, t, d):
    p = P(t, d)
    if p < .62:
        PQ = Polar(W / 2, H / 2 + 20, 15.0)
        polar_bg(ctx, PQ, others=False)
        draw_ata(ctx, PQ, SNOW)
        k = ease(prog(p, .25, .4))
        ctx.save()
        for R in ata():
            for i, (lo, la) in enumerate(R):
                x, y = PQ(lo, la); (ctx.move_to if i == 0 else ctx.line_to)(x, y)
            ctx.close_path()
        ctx.clip()
        ctx.move_to(PQ.cx, PQ.cy)
        ctx.arc(PQ.cx, PQ.cy, 600, math.radians(-90 - 180), math.radians(-90 - 30)); ctx.close_path()
        col(ctx, RED, .55 * k); ctx.fill(); ctx.restore()
        tag(ctx, "ORIENTAL · ESTABLE", 1250, 620, ease(prog(p, .05, .15)), INK, 44)
        tag(ctx, "OCCIDENTAL · BAJO EL MAR", 120, 300, k, RED, 44)
        dot(ctx, PQ, -106, -75.5, "Thwaites", ease(prog(p, .45, .55)), AMBER, size=34, dx=-18, align='r')
    else:
        photo(ctx, 'thwaites', t - d * .62, d * .38, True, dark=.15)
        tag(ctx, "GLACIAR THWAITES", 80, 140, ease(prog(p, .64, .72)), AMBER, 56)
        text(ctx, "+65 cm", 1600, 1000, 130, INK, F_BLACK, a=ease(prog(p, .8, .88)))

def n4(ctx, t, d):
    p = P(t, d); col(ctx, BG); ctx.paint()
    rates = [1.3, 1.3, 2.4, 2.4, 2.4, 2.4, 10, 10, 10]
    cum = np.cumsum(rates); base = 920; pxm = 640 / cum[-1]
    for i, c in enumerate(cum):
        k = ease(prog(p, .1 + i * .07, .18 + i * .07)); x = 260 + i * 170
        col(ctx, WATER if rates[i] < 2 else (AMBER if rates[i] < 5 else RED), .9)
        rrect(ctx, x - 60, base - c * pxm * k, 120, c * pxm * k, 8); ctx.fill()
        label(ctx, f"+{i + 1} °C", x, base + 50, k, INK, 32)
        if i in (0, 2, 6):
            text(ctx, f"{fmt_es(rates[i])} m/°C", x, base - c * pxm - 30, 40, INK, F_BLACK, a=k)
    src(ctx, "Garbe et al. (2020), Nature · subida del mar a largo plazo")

def n5(ctx, t, d):
    p = P(t, d); col(ctx, hexc('#2A1408')); ctx.paint()
    g = cairo.LinearGradient(0, 0, 0, H); g.add_color_stop_rgb(0, *hexc('#E0702A')); g.add_color_stop_rgb(1, *hexc('#3A1408')); ctx.set_source(g); ctx.paint()
    k = ease(prog(p, .05, .2)); base = 900
    col(ctx, (0, 0, 0), k)
    ctx.set_line_width(10)
    ctx.move_to(300, base); ctx.line_to(420, 380); ctx.line_to(540, base); ctx.stroke()
    for y in range(450, base, 90): ctx.move_to(420 - (y - 380) * .23, y); ctx.line_to(420 + (y - 380) * .23, y); ctx.stroke()
    ctx.move_to(780, base); ctx.curve_to(860, 620, 1060, 600, 1140, base); ctx.fill()
    glow(ctx, 960, 760, 120, RED, k * (.6 + .3 * math.sin(t * 6)))
    col(ctx, (0, 0, 0), k); fx = 1500; s = 1 + .08 * math.sin(t * 9)
    ctx.save(); ctx.translate(fx, base); ctx.scale(s, s)
    ctx.move_to(0, 0); ctx.curve_to(-140, -120, -40, -300, 0, -420); ctx.curve_to(40, -300, 140, -120, 0, 0); ctx.fill(); ctx.restore()
    col(ctx, (0, 0, 0), k); ctx.rectangle(0, base, W, H - base); ctx.fill()
    tag(ctx, "≈ 10.000 GtC", 80, 160, ease(prog(p, .25, .35)), INK, 50)
    tag(ctx, "+3 M POR SIGLO", W / 2, 1040, ease(prog(p, .6, .7)), AMBER, 54, align='c')
    src(ctx, "Winkelmann et al. (2015), Science Advances", ease(prog(p, .3, .4)) * 0)

def n6(ctx, t, d):
    p = P(t, d)
    PQ = Polar(1250, H / 2 + 20, 13.0)
    polar_bg(ctx, PQ, others=False)
    up = ease(prog(p, .05, .35)); down = ease(prog(p, .45, .75))
    draw_ata(ctx, PQ, mix(SNOW, ROCK, up))
    lv = .3 + .55 * up - .55 * down
    thermo(ctx, 300, 860, 600, lv, mix(COLD, RED, up * (1 - down)))
    text(ctx, f"+{fmt_es(9 * up * (1 - down), 0)} °C", 480, 400, 110, INK, F_BLACK, 'l', 1)
    k = ease(prog(p, .78, .88))
    if k > 0:
        col(ctx, RED, .9 * k); rrect(ctx, 880, 880, 740, 130, 18); ctx.fill()
        text(ctx, "EL HIELO NO VUELVE", 1250, 965, 60, INK, F_BLACK, a=k)
    src(ctx, "Garbe et al. (2020), Nature", ease(prog(p, .8, .9)))

def n7(ctx, t, d):
    p = P(t, d)
    tiles = [('ice_cliff', "+58 METROS", WATER), ('madrid_gate', "MADRID, A SALVO", VERDE),
             ('obelisk_flood', "BUENOS AIRES, BAJO EL MAR", RED), ('low_sea_cliff', "JUNTO AL HIELO, EL MAR BAJA", AMBER)]
    for i, (img, s, c) in enumerate(tiles):
        k = ease(prog(p, .1 + i * .12, .2 + i * .12))
        if k <= 0: continue
        x0, y0 = (i % 2) * W / 2, (i // 2) * H / 2
        ctx.save(); ctx.rectangle(x0 + 6, y0 + 6, W / 2 - 12, H / 2 - 12); ctx.clip()
        ctx.translate(x0 + W / 4, y0 + H / 4); ctx.scale(.5, .5); ctx.translate(-W / 2, -H / 2)
        ctx.push_group(); photo(ctx, img, t, d, True, dark=.15); ctx.pop_group_to_source(); ctx.paint_with_alpha(k)
        ctx.restore()
        tag(ctx, s, x0 + 40, y0 + H / 2 - 50, k, c, 40)
    k = ease(prog(p, .7, .8))
    if k > 0:
        col(ctx, (0, 0, 0), .75 * k); ctx.paint()
        text(ctx, "ESTE SIGLO", W / 2, 560, 160, AMBER, F_BLACK, a=k)

_TH = None
def n8(ctx, t, d):
    global _TH
    p = P(t, d)
    if p < .38:
        k = eout(prog(p, 0, .08)) * (1 - ease(prog(p, .33, .38)))
        card(ctx, 360, 300, 1200, 400, k)
        text(ctx, "¿Qué hacemos", W / 2, 460, 90, INK, F_BLACK, a=k)
        text(ctx, "desaparecer ahora?", W / 2, 580, 90, AMBER, F_BLACK, a=k)
        text(ctx, "Escríbelo en los comentarios ↓", W / 2, 660, 36, MUTED, F_SEMI, a=k)
        return
    q = prog(p, .38, 1)
    if _TH is None:
        _TH = cairo.ImageSurface.create_from_png('/home/claude/tierra/out/miniatura_tierra_al_reves.png')
    a = ease(prog(q, 0, .15))
    ctx.save(); ctx.translate(1060, 260); ctx.scale(720 / 1280, 405 / 720); ctx.set_source_surface(_TH, 0, 0); ctx.paint_with_alpha(a); ctx.restore()
    col(ctx, LINE, a); ctx.set_line_width(3); rrect(ctx, 1060, 260, 720, 405, 16); ctx.stroke()
    label(ctx, "Siguiente vídeo", 1420, 230, a, MUTED, 26)
    text(ctx, "¿Y si la Tierra", 520, 420, 80, INK, F_BLACK, a=ease(prog(q, .05, .2)))
    text(ctx, "girara al revés?", 520, 520, 80, AMBER, F_BLACK, a=ease(prog(q, .1, .25)))
    b = ease(prog(q, .3, .45))
    col(ctx, AMBER, b); ctx.arc(1260, 850, 60, 0, 2 * math.pi); ctx.fill()
    text(ctx, "?", 1260, 875, 75, BG, F_BLACK, a=b)
    text(ctx, "LA GRAN PREGUNTA", 1340, 875, 46, INK, F_BLACK, 'l', b)
    pressed = prog(q, .55, .62)
    col(ctx, mix(RED, LINE, pressed), b); rrect(ctx, 260, 800, 520, 110, 55); ctx.fill()
    text(ctx, "SUSCRITO ✓" if pressed > .5 else "SUSCRIBIRSE", 520, 873, 50, INK, F_BLACK, a=b)

VIS = {
    '00_hook': [k1, k2, k3, k4, k5],
    '01_tamano': [t1, t2, t3, t4, t5, t6, t7],
    '02_subida': [u1, u2, u3, u4, u5, u6],
    '03_gravedad': [g1, g2, g3, g4, g5, g6],
    '04_oceano': [c1, c2, c3, c4, c5, c6],
    '05_pasado': [f1, f2, f3, f4, f5, f6, f7],
    '06_futuro': [n1, n2, n3, n4, n5, n6, n7, n8],
}

def blocks():
    out = []
    for name, texts in narration.BLOCKS:
        fns = VIS[name]
        assert len(fns) == len(texts), (name, len(fns), len(texts))
        out.append((name, list(zip(fns, texts))))
    return out
