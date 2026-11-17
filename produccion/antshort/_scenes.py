
# ------------------------------------------------------------------ ESCENAS Antártida
import importlib.util as _U
_sp = _U.spec_from_file_location('ascenes', '/home/claude/antartida/scenes.py')
AS = _U.module_from_spec(_sp); _sp.loader.exec_module(AS)
oglobe, ice_tint, Polar, draw_ata, europe_overlay = AS.oglobe, AS.ice_tint, AS.Polar, AS.draw_ata, AS.europe_overlay
building, sil_towers, sil_venice = AS.building, AS.sil_towers, AS.sil_venice
WATER = hexc('#2E8BFF'); ROCK = hexc('#7A5A40'); SNOW = hexc('#EEF4F8'); ICEB = hexc('#9CC8E8')
OCEAN = hexc('#0B1621'); LAND2 = hexc('#27313D')

IMPACTS[:] = [(wt('rise', 'cincuenta'), 18, .25), (wt('cities', 'no.'), 16, 0), (wt('twist', 'bajaría'), 18, .2),
              (wt('size', 'Europa'), 10, 0), (wt('thick', 'cinco'), 12, 0), (wt('ninety', 'noventa'), 12, 0),
              (wt('five', 'inundan'), 12, 0), (wt('spain', 'Sevilla'), 10, 0), (wt('world', 'Buenos'), 12, 0),
              (wt('gravity', 'imán'), 14, .15), (wt('forest', 'selva'), 14, .25), (wt('nasa', 'toneladas'), 12, 0)]

def water(ctx, y, t, x0=0, x1=SW, ybot=SH, a=.88, amp=8):
    ctx.move_to(x0, ybot); ctx.line_to(x0, y)
    for x in range(int(x0), int(x1) + 20, 20): ctx.line_to(x, y + amp * math.sin(x / 70 + t * 3))
    ctx.line_to(x1, ybot); ctx.close_path()
    g = cairo.LinearGradient(0, y, 0, ybot); g.add_color_stop_rgba(0, *WATER, a); g.add_color_stop_rgba(1, *hexc('#06213F'), a)
    ctx.set_source(g); ctx.fill()
    col(ctx, (1, 1, 1), .55 * a); ctx.set_line_width(4)
    for x in range(int(x0), int(x1), 20):
        yy = y + amp * math.sin(x / 70 + t * 3); (ctx.move_to if x == int(x0) else ctx.line_to)(x, yy)
    ctx.stroke()
    r = random.Random(3)
    for _ in range(18):  # burbujas
        bx = r.uniform(x0, x1); by = ybot - ((t * r.uniform(60, 160) + r.uniform(0, 900)) % max(1, ybot - y))
        if by > y + 20: col(ctx, (1, 1, 1), .25); ctx.arc(bx, by, r.uniform(3, 8), 0, 2 * math.pi); ctx.stroke()

def meter(ctx, s, x, y, k, c=WATER):
    if k <= 0: return
    font(ctx, F_BLACK, 96); w = ctx.text_extents(s).x_advance + 60
    col(ctx, (0, 0, 0), .65 * k); rrect(ctx, x - w / 2, y - 100, w, 130, 22); ctx.fill()
    col(ctx, c, k); ctx.set_line_width(5); rrect(ctx, x - w / 2, y - 100, w, 130, 22); ctx.stroke()
    T(ctx, s, x, y, 96, c, F_BLACK, a=k)

def sc_globe(ctx, t, s0, d):
    background(ctx, t, tint=(0.02, 0.03, 0.06))
    q = eout(clamp((t - s0) / d)); lat0 = lerp(15, -68, q)
    r = 430 * lerp(.85, 1.05, q)
    oglobe(ctx, SW / 2, 920, r, 20 + t * 14, lat0=lat0, tint=ice_tint(0))
    glow(ctx, SW / 2, 920 + r * .7, 260, SNOW, .25 * q)
    k1 = popk(t, s0 + .05, .4); k2 = popk(t, wt('globe', 'toda'), .35)
    scaled(ctx, SW / 2, 330, k1, lambda: T(ctx, "¿Y SI SE DERRITE", 0, 0, 96, INK, outline=16))
    scaled(ctx, SW / 2, 460, k2, lambda: T(ctx, "TODA LA ANTÁRTIDA?", 0, 0, 104, ICEB, outline=16))

def sc_rise(ctx, t, s0, d):
    background(ctx, t, tint=(0.03, 0.05, 0.09))
    base, pxm = 1420, 15.5
    building(ctx, SW / 2 - 170, base, 340, 19, 58 * pxm / 19)
    t58 = wt('rise', 'cincuenta')
    lvl = 58 * eout(clamp((t - s0 - .2) / (t58 + .9 - s0)))
    water(ctx, base - lvl * pxm, t)
    y58 = base - 58 * pxm
    col(ctx, AMBER); ctx.set_line_width(5); ctx.set_dash([18, 12]); ctx.move_to(60, y58); ctx.line_to(SW - 60, y58); ctx.stroke(); ctx.set_dash([])
    meter(ctx, f"+{int(lvl)} m", SW / 2, y58 - 60, clamp((t - s0) / .3))
    k = popk(t, wt('rise', 'pisos'), .35)
    scaled(ctx, SW - 210, 1300, k, lambda: T(ctx, "20 PISOS", 0, 0, 70, AMBER, outline=12))

def sc_cities(ctx, t, s0, d):
    background(ctx, t, dust=False)
    # Madrid arriba: en alto y a salvo
    col(ctx, hexc('#5A4636')); ctx.move_to(0, 760); ctx.curve_to(300, 560, 700, 540, SW, 700); ctx.line_to(SW, 820); ctx.line_to(0, 820); ctx.close_path(); ctx.fill()
    ctx.save(); ctx.translate(0, 0); sil_towers(ctx, 250, 830, 640, 5, hexc('#3A4658'), 1); ctx.restore()
    water(ctx, 800, t, ybot=830, a=.9, amp=4)
    km = popk(t, s0 + .1, .35)
    scaled(ctx, 250, 330, km, lambda: T(ctx, "MADRID", 0, 0, 80, INK, outline=12))
    scaled(ctx, 250, 420, km, lambda: T(ctx, "≈ 650 m", 0, 0, 56, GREEN, F_XB, outline=10))
    scaled(ctx, 860, 400, popk(t, wt('cities', 'salvaría'), .3), lambda: T(ctx, "✓", 0, 0, 200, GREEN, outline=14))
    col(ctx, LINE); ctx.rectangle(0, 860, SW, 6); ctx.fill()
    # Buenos Aires abajo: bajo el agua
    sil_towers(ctx, 0, SW, 1440, 8, hexc('#3A4658'), 1)
    tb = wt('cities', 'Buenos')
    lvl = eout(clamp((t - tb) / 1.0))
    water(ctx, lerp(1450, 1060, lvl), t, ybot=1450)
    kb = popk(t, tb, .35)
    scaled(ctx, 300, 1000, kb, lambda: T(ctx, "BUENOS AIRES", 0, 0, 72, INK, outline=12))
    scaled(ctx, 860, 1010, popk(t, wt('cities', 'no.'), .3), lambda: T(ctx, "✗", 0, 0, 200, RED, outline=14))

def ice_wall(ctx, top, bottom, t, wet=0):
    r = random.Random(4); ctx.move_to(0, bottom); ctx.line_to(0, top)
    x = 0
    while x < SW:
        x += r.uniform(40, 110); ctx.line_to(x, top + r.uniform(-60, 40))
    ctx.line_to(SW, bottom); ctx.close_path()
    g = cairo.LinearGradient(0, top, 0, bottom); g.add_color_stop_rgb(0, *SNOW); g.add_color_stop_rgb(1, *hexc('#4E8DBA'))
    ctx.set_source(g); ctx.fill()
    r = random.Random(9)
    for _ in range(26):
        x = r.uniform(0, SW); col(ctx, hexc('#6FA9D2'), .6); ctx.set_line_width(r.uniform(2, 6))
        ctx.move_to(x, top + 40); ctx.line_to(x + r.uniform(-40, 40), bottom); ctx.stroke()

def sc_twist(ctx, t, s0, d):
    sky = cairo.LinearGradient(0, 0, 0, 800); sky.add_color_stop_rgb(0, *hexc('#1B2A4A')); sky.add_color_stop_rgb(1, *hexc('#D98E6A'))
    ctx.set_source(sky); ctx.paint()
    ice_wall(ctx, 420, 1500, t)
    tb = wt('twist', 'bajaría')
    q = eout(clamp((t - tb + .4) / 1.2)); y = lerp(1020, 1260, q)
    col(ctx, hexc('#3A5A70'), .9 * q); ctx.rectangle(0, 1020, SW, y - 1020); ctx.fill()   # franja mojada
    water(ctx, y, t, ybot=SH)
    k = popk(t, tb - .1, .35)
    def arrow():
        col(ctx, AMBER); ctx.rectangle(-30, -200, 60, 220); ctx.fill(); ctx.move_to(-90, 20); ctx.line_to(90, 20); ctx.line_to(0, 140); ctx.close_path(); ctx.fill()
    scaled(ctx, SW - 190, 820 + 60 * q, k, arrow)
    scaled(ctx, SW / 2, 330, popk(t, s0 + .1, .35), lambda: T(ctx, "JUNTO AL HIELO", 0, 0, 92, INK, outline=14))
    scaled(ctx, SW / 2, 450, k, lambda: T(ctx, "EL MAR BAJA", 0, 0, 110, AMBER, outline=16))

PPO = Polar(SW / 2, 860, 15.0)
def sc_size(ctx, t, s0, d):
    background(ctx, t, tint=(0.02, 0.04, 0.08), dust=False)
    draw_ata(ctx, PPO, SNOW)
    glow(ctx, SW / 2, 860, 450, ICEB, .18)
    te = wt('size', 'Europa'); q = eout(clamp((t - te + .3) / .7))
    europe_overlay(ctx, lerp(SW + 500, SW / 2, q), 860, PPO.d / 111, AMBER, .78 * clamp((t - te + .3) / .3))
    scaled(ctx, SW / 2, 1360, popk(t, te + .2, .35), lambda: T(ctx, "≈ 1,4 × EUROPA", 0, 0, 100, AMBER, outline=14))
    T(ctx, "14 MILLONES DE KM²", SW / 2, 380, 66, INK, F_XB, a=clamp((t - s0) / .3), outline=10)

def sc_thick(ctx, t, s0, d):
    background(ctx, t, dust=False)
    base, pxkm = 1420, 175
    q = eout(clamp((t - s0) / 1.2))
    col(ctx, ROCK); ctx.rectangle(0, base, SW, SH - base); ctx.fill()
    pts = [(0, 1.8), (180, 2.4), (380, 3.4), (560, 4.9), (720, 4.3), (900, 3.0), (1080, 2.2)]
    ctx.move_to(0, base)
    for x, h in pts: ctx.line_to(x, base - h * pxkm * q)
    ctx.line_to(SW, base); ctx.close_path()
    g = cairo.LinearGradient(0, base - 860, 0, base); g.add_color_stop_rgb(0, *SNOW); g.add_color_stop_rgb(1, *hexc('#7FB0D6')); ctx.set_source(g); ctx.fill()
    tc = wt('thick', 'cinco')
    v = 4.9 * eout(clamp((t - tc + .3) / .8))
    col(ctx, RED); ctx.set_line_width(6); ctx.move_to(560, base); ctx.line_to(560, base - v * pxkm); ctx.stroke()
    if t > tc - .3: T(ctx, f"{v:.1f} KM".replace('.', ','), SW / 2, 400, 150, RED, a=1, outline=16)
    kt = clamp((t - (tc + .6)) / .3)
    if kt > 0:
        tx, th = 880, 3.715 * pxkm
        col(ctx, hexc('#4A3626'), kt); ctx.move_to(tx - 200, base); ctx.line_to(tx - 25, base - th); ctx.line_to(tx + 25, base - th); ctx.line_to(tx + 200, base); ctx.close_path(); ctx.fill()
        T(ctx, "TEIDE", tx, base - th - 30, 50, INK, F_XB, a=kt, outline=10)

def sc_ninety(ctx, t, s0, d):
    background(ctx, t, tint=(0.02, 0.04, 0.08))
    P2 = Polar(SW / 2, 1000, 11.0); draw_ata(ctx, P2, SNOW)
    tn = wt('ninety', 'noventa')
    for i in range(10):
        x0, y0 = 150 + (i % 5) * 195, 420 + (i // 5) * 170
        if i < 9:
            q = eout(clamp((t - (tn - .3 + .06 * i)) / .5)); a = i * .7
            x = lerp(x0, SW / 2 + 160 * math.cos(a), q); y = lerp(y0, 1000 + 120 * math.sin(a), q); s = lerp(1, .6, q)
        else: x, y, s = x0, y0, 1
        def cube():
            col(ctx, ICEB); rrect(ctx, -60, -60, 120, 120, 16); ctx.fill(); col(ctx, (1, 1, 1), .5); rrect(ctx, -45, -45, 40, 40, 10); ctx.fill()
        scaled(ctx, x, y, s * popk(t, s0 + .04 * i, .3), cube)
    scaled(ctx, SW / 2, 1420, popk(t, tn, .35), lambda: T(ctx, "90 %", 0, 0, 200, AMBER, outline=16))

def sc_five(ctx, t, s0, d):
    background(ctx, t, dust=False)
    base = 1300
    sil_venice(ctx, 30, 520, base, hexc('#3A4658'), 1)
    sil_towers(ctx, 560, 1050, base, 2, hexc('#3A4658'), 1)
    T(ctx, "VENECIA", 275, base + 90, 56, INK, F_XB, a=1, outline=10)
    T(ctx, "MIAMI", 805, base + 90, 56, INK, F_XB, a=1, outline=10)
    lvl = 5 * eout(clamp((t - s0) / 1.4))
    water(ctx, base - lvl * 26, t, ybot=base + 20)
    meter(ctx, f"+{int(round(lvl))} m", SW / 2, 420, clamp((t - s0) / .3))

FLOOD_ES = [(-6.0, 37.4, .5), (-6.25, 37.1, .55), (-6.35, 36.85, .45), (-6.1, 37.7, .3), (-0.38, 39.47, .3), (-0.33, 39.25, .3), (0.75, 40.7, .25), (-0.8, 37.7, .18)]
IBS = Proj(-10, 4.5, 35.5, 44.2, 40, 420, 1000, 900)
def sc_spain(ctx, t, s0, d):
    background(ctx, t, dust=False)
    draw_map(ctx, IBS, None, base=LAND2, edge=hexc('#36414F'))
    g = eout(clamp((t - s0) / 1.5))
    AS.blobs(ctx, IBS, [(lo, la, 1.9 * r * g + .01) for lo, la, r in FLOOD_ES], WATER, 1)
    for lo, la, n, al in [(-5.98, 37.39, "Sevilla", 'r'), (-0.38, 39.47, "Valencia", 'l')]:
        x, y = IBS(lo, la); k = popk(t, wt('spain', n), .3)
        scaled(ctx, x, y, k, lambda: (col(ctx, INK), ctx.arc(0, 0, 10, 0, 2 * math.pi), ctx.fill()))
        T(ctx, n.upper(), x + (24 if al == 'l' else -24), y + 14, 52, INK, F_XB, 'l' if al == 'l' else 'r', clamp((t - wt('spain', n)) / .2), outline=10)
    meter(ctx, f"+{int(25 * g)} m", SW / 2, 380, clamp((t - s0) / .3))

RPL = Proj(-64, -50, -39, -29, 40, 360, 1000, 1050)
def sc_world(ctx, t, s0, d):
    background(ctx, t, dust=False)
    col(ctx, OCEAN); ctx.rectangle(0, 300, SW, 1180); ctx.fill()
    draw_map(ctx, RPL, None, base=LAND2, edge=hexc('#36414F'))
    g = eout(clamp((t - s0) / 1.6))
    AS.blobs(ctx, RPL, [(-58.4, -34.6, 1.6 * g + .01), (-57.5, -33.8, 1.3 * g + .01), (-56.2, -34.85, 1.1 * g + .01), (-59.3, -34.0, 1.0 * g + .01)], WATER, 1)
    for lo, la, n, key in [(-58.38, -34.6, "BUENOS AIRES", 'Buenos'), (-56.16, -34.9, "MONTEVIDEO", 'Montevideo')]:
        x, y = RPL(lo, la); k = clamp((t - wt('world', key)) / .2)
        col(ctx, INK, k); ctx.arc(x, y, 12, 0, 2 * math.pi); ctx.fill()
        T(ctx, n, x, y - 34, 50, INK, F_XB, a=k, outline=10)
    meter(ctx, f"+{int(58 * g)} m", SW / 2, 380, clamp((t - s0) / .3))

def section(ctx, t, bulge_s, bulge_n, ice_k):
    cx, cy, r = SW / 2, 860, 330
    pts = []
    for i in range(181):
        th = i * 2 * math.pi / 180
        dS = (th - math.pi / 2 + math.pi) % (2 * math.pi) - math.pi
        dN = (th + math.pi / 2 + math.pi) % (2 * math.pi) - math.pi
        rr = r + 40 + bulge_s * math.exp(-(dS / .45) ** 2) + bulge_n * (math.cos(dN) * .5 + .5) * .6 + 3 * math.sin(th * 12 + t * 3)
        pts.append((cx + rr * math.cos(th), cy + rr * math.sin(th)))
    ctx.move_to(*pts[0])
    for q in pts[1:]: ctx.line_to(*q)
    ctx.close_path(); col(ctx, WATER, .9); ctx.fill()
    col(ctx, hexc('#4A3A2C')); ctx.arc(cx, cy, r, 0, 2 * math.pi); ctx.fill()
    if ice_k > 0:
        col(ctx, SNOW, ice_k); ctx.save(); ctx.translate(cx, cy + r - 10); ctx.scale(1, .45); ctx.arc(0, 0, 200, 0, 2 * math.pi); ctx.restore(); ctx.fill()
    return cx, cy, r

def sc_gravity(ctx, t, s0, d):
    background(ctx, t, tint=(0.03, 0.04, 0.08))
    tg = wt('gravity', 'atrae')
    b = 90 * eout(clamp((t - tg + .3) / .8))
    cx, cy, r = section(ctx, t, b, 0, 1)
    k = clamp((t - tg) / .3)
    for a in (-1.0, -.5, .5, 1.0):  # flechas hacia el hielo
        th = math.pi / 2 + a * .6; ph = (t * 1.5) % 1
        x0, y0 = cx + (r + 260 - 80 * ph) * math.cos(th), cy + (r + 260 - 80 * ph) * math.sin(th)
        col(ctx, AMBER, k); ctx.arc(x0, y0, 16, 0, 2 * math.pi); ctx.fill()
    def magnet():
        col(ctx, RED); ctx.set_line_width(46); ctx.arc(0, 0, 70, math.pi, 2 * math.pi); ctx.stroke()
        col(ctx, INK); ctx.rectangle(-93, -4, 46, 40); ctx.fill(); ctx.rectangle(47, -4, 46, 40); ctx.fill()
    scaled(ctx, cx + 360, cy + 380, popk(t, wt('gravity', 'imán'), .35), magnet)
    T(ctx, "ANTÁRTIDA", cx, cy + r + 170, 54, INK, F_XB, a=clamp((t - s0) / .3), outline=10)
    scaled(ctx, SW / 2, 380, popk(t, tg, .35), lambda: T(ctx, "SU GRAVEDAD", 0, 0, 96, AMBER, outline=14))

def sc_escape(ctx, t, s0, d):
    background(ctx, t, tint=(0.03, 0.04, 0.08))
    q = eout(clamp((t - s0) / 1.2))
    cx, cy, r = section(ctx, t, 90 * (1 - q) - 40 * q, 70 * q, 1 - q)
    k = clamp((t - s0 - .3) / .3)
    for x in (cx - 300, cx + 300):
        ph = (t * 1.2) % 1
        col(ctx, AMBER, k); ctx.set_line_width(14); ctx.move_to(x, cy + 200 - 120 * ph); ctx.line_to(x, cy - 120 - 120 * ph); ctx.stroke()
        ctx.move_to(x - 36, cy - 110 - 120 * ph); ctx.line_to(x, cy - 170 - 120 * ph); ctx.line_to(x + 36, cy - 110 - 120 * ph); ctx.fill()
    scaled(ctx, SW / 2, 380, popk(t, wt('escape', 'norte'), .35), lambda: T(ctx, "↑ AL NORTE", 0, 0, 110, AMBER, outline=14))

def tree(ctx, x, base, h, c):
    col(ctx, c); ctx.rectangle(x - h * .03, base - h * .2, h * .06, h * .2); ctx.fill()
    for i in range(4):
        w = h * (.32 - i * .06); y = base - h * (.18 + i * .2)
        ctx.move_to(x - w, y); ctx.line_to(x, y - h * .32); ctx.line_to(x + w, y); ctx.close_path(); ctx.fill()

def sc_forest(ctx, t, s0, d):
    sky = cairo.LinearGradient(0, 0, 0, 1500)
    sky.add_color_stop_rgb(0, *hexc('#24314F')); sky.add_color_stop_rgb(.7, *hexc('#E08A4A')); sky.add_color_stop_rgb(1, *hexc('#F3C77A'))
    ctx.set_source(sky); ctx.paint()
    glow(ctx, SW / 2, 1150, 260, AMBER, .9); col(ctx, hexc('#FFE3A0')); ctx.arc(SW / 2, 1150, 70, 0, 2 * math.pi); ctx.fill()
    ts = wt('forest', 'selva'); grow = eout(clamp((t - ts + .6) / 1.0))
    for layer, (c, n, hmin, hmax, base, par) in enumerate([(hexc('#3E6B4A'), 9, 260, 420, 1300, .3), (hexc('#25452F'), 7, 380, 620, 1420, .6), (hexc('#13251A'), 5, 560, 860, 1560, 1.0)]):
        r = random.Random(layer + 3)
        for i in range(n):
            x = (i + .5) * SW / n + r.uniform(-40, 40) - (t - s0) * 20 * par
            tree(ctx, x, base, r.uniform(hmin, hmax) * grow, c)
        col(ctx, c); ctx.rectangle(0, base - 2, SW, SH - base + 2); ctx.fill()
    T(ctx, "HACE 90 MILLONES", SW / 2, 330, 84, INK, a=clamp((t - wt('forest', 'noventa')) / .2), outline=14)
    T(ctx, "DE AÑOS", SW / 2, 430, 84, INK, a=clamp((t - wt('forest', 'noventa')) / .2), outline=14)
    scaled(ctx, SW / 2, 560, popk(t, wt('forest', 'Polo'), .35), lambda: T(ctx, "POLO SUR", 0, 0, 96, AMBER, outline=14))

def sc_nasa(ctx, t, s0, d):
    background(ctx, t, tint=(0.02, 0.03, 0.06))
    x, y, r = SW / 2, 1020, 400
    oglobe(ctx, x, y, r, t * 10, lat0=-68, tint=ice_tint(0))
    for j in range(2):
        a = t * 1.1 - j * .3; sx, sy = x + (r + 80) * math.cos(a), y + (r + 80) * .35 * math.sin(a)
        col(ctx, INK); ctx.rectangle(sx - 16, sy - 9, 32, 18); ctx.fill(); col(ctx, BLUE); ctx.rectangle(sx - 50, sy - 5, 30, 10); ctx.fill(); ctx.rectangle(sx + 20, sy - 5, 30, 10); ctx.fill()
    tt = wt('nasa', 'ciento')
    v = 135 * eout(clamp((t - tt) / 1.4))
    if t > tt - .1:
        T(ctx, f"{int(v)}.000", SW / 2, 470, 190, AMBER, a=1, outline=16)
        T(ctx, "MILLONES DE TONELADAS / AÑO", SW / 2, 560, 50, INK, F_XB, a=clamp((t - wt('nasa', 'toneladas')) / .2), outline=10)
    T(ctx, "Fuente: NASA (satélites GRACE)", SW / 2, 1480, 28, MUTED, F_SEMI, a=.8)

_TH = []
def sc_cta(ctx, t, s0, d):
    background(ctx, t, tint=(0.03, 0.04, 0.08))
    k = popk(t, s0, .4)
    def bubble():
        col(ctx, PANEL); rrect(ctx, -440, -170, 880, 340, 46); ctx.fill()
        col(ctx, AMBER); ctx.set_line_width(6); rrect(ctx, -440, -170, 880, 340, 46); ctx.stroke()
        T(ctx, "¿TU CIUDAD", 0, -20, 110, INK); T(ctx, "SE SALVARÍA?", 0, 110, 110, AMBER)
    scaled(ctx, SW / 2, 520, k, bubble)
    tv = wt('cta', 'completo')
    k2 = eout(clamp((t - tv + .2) / .4))
    if k2 > 0:
        if not _TH: _TH.append(cairo.ImageSurface.create_from_png('/home/claude/antartida/out/miniatura_antartida.png'))
        th = _TH[0]; w = 900; s = w / th.get_width(); h = th.get_height() * s
        ctx.save(); ctx.translate((SW - w) / 2, 820 + 40 * (1 - k2)); ctx.scale(s, s); ctx.set_source_surface(th, 0, 0); ctx.paint_with_alpha(k2); ctx.restore()
        col(ctx, AMBER, k2); ctx.set_line_width(6); rrect(ctx, (SW - w) / 2, 820 + 40 * (1 - k2), w, h, 20); ctx.stroke()
        T(ctx, "VÍDEO COMPLETO", SW / 2, 790, 56, INK, F_XB, a=k2, outline=10)
    k3 = clamp((t - wt('cta', 'Gran')) / .3)
    if k3 > 0:
        col(ctx, AMBER, k3); ctx.arc(230, 1430, 60, 0, 2 * math.pi); ctx.fill(); T(ctx, "?", 230, 1460, 88, BG, F_BLACK, a=k3)
        T(ctx, "LA GRAN PREGUNTA", 315, 1455, 62, INK, F_BLACK, 'l', k3, maxw=680, outline=8)

SCENES = {'globe': sc_globe, 'rise': sc_rise, 'cities': sc_cities, 'twist': sc_twist, 'size': sc_size, 'thick': sc_thick,
          'ninety': sc_ninety, 'five': sc_five, 'spain': sc_spain, 'world': sc_world, 'gravity': sc_gravity, 'escape': sc_escape,
          'forest': sc_forest, 'nasa': sc_nasa, 'cta': sc_cta}
