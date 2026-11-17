"""All scenes of '¿Y si mañana estallara una guerra nuclear?'.

Each block = list of (phase_fn, narration_text). Phase length inside a block is proportional
to the narration weight of its text; a block's total length comes from its audio file.
Phase fn signature: fn(ctx, t, d) -> draws content (background is drawn by the renderer).
"""
import math, random, cairo
from lib import *

def P(t, d):
    return t / d if d else 1.0

# ======================================================================= HOOK
def h_clock(ctx, t, d):
    p = P(t, d)
    g = cairo.LinearGradient(0, 0, 0, H)
    g.add_color_stop_rgba(0, 0.10, 0.13, 0.19, 1); g.add_color_stop_rgba(1, 0.04, 0.05, 0.06, 0)
    ctx.set_source(g); ctx.rectangle(0, 0, W, H); ctx.fill()
    skyline(ctx, 930, a=1, seed=7, lit=0.35)
    label(ctx, "Mañana", W / 2, 300, a=ease(prog(p, 0, .2)), size=34, c=INK)
    s = 7 + int(t)
    tx = "09:14"
    a = ease(prog(p, .05, .3))
    text(ctx, tx, W / 2, 520, 230, INK, F_BLACK, a=a)
    text(ctx, f":{s:02d}", W / 2 + 330, 520, 70, AMBER, F_MONO, 'l', a)

def _europe():
    return Proj(-12, 44, 34, 66, 0, 0, W, H)

_LIGHTS = None
def city_lights(ctx, Pj, a):
    global _LIGHTS
    if _LIGHTS is None:
        r = random.Random(11)
        pts = [(2.35, 48.86), (13.4, 52.5), (-3.7, 40.4), (12.5, 41.9), (-0.12, 51.5), (21, 52.2), (16.4, 48.2),
               (4.9, 52.4), (14.4, 50.1), (19, 47.5), (30.5, 50.45), (37.6, 55.75), (9.2, 45.5), (2.17, 41.4),
               (23.7, 37.98), (26.1, 44.4), (18.07, 59.33), (10.75, 59.9), (12.57, 55.68), (24.9, 60.2),
               (4.35, 50.85), (8.68, 50.11), (11.58, 48.14), (-9.14, 38.72), (27.5, 53.9), (30.3, 59.9)]
        _LIGHTS = []
        for lon, lat in pts:
            _LIGHTS.append((lon, lat, 1.0))
            for _ in range(14):
                _LIGHTS.append((lon + r.gauss(0, 1.6), lat + r.gauss(0, 1.0), r.uniform(0.2, 0.6)))
    for lon, lat, w in _LIGHTS:
        x, y = Pj(lon, lat)
        glow(ctx, x, y, 10 + 18 * w, AMBER, 0.22 * w * a)

def h_flash(ctx, t, d):
    p = P(t, d)
    Pj = _europe()
    draw_map(ctx, Pj, base=hexc('#151B24'), edge=hexc('#232B37'))
    city_lights(ctx, Pj, 1)
    fx, fy = Pj(15.5, 50.6)
    tf = prog(p, .22, 1)
    if tf > 0:
        k = eout(prog(tf, 0, .12))
        glow(ctx, fx, fy, 30 + 260 * k, (1, 1, 1), 1.0 * (1 - prog(tf, .1, .6)) + 0.15)
        glow(ctx, fx, fy, 60 + 120 * k, AMBER, 0.8 * (1 - prog(tf, .3, 1)) + .2)
        for i in range(3):
            rp = prog(tf, .05 + i * .15, .6 + i * .15)
            if 0 < rp < 1:
                col(ctx, AMBER, (1 - rp) * 0.7); ctx.set_line_width(3)
                ctx.arc(fx, fy, 20 + 380 * eout(rp), 0, 2 * math.pi); ctx.stroke()
    la = ease(prog(p, .45, .6))
    label(ctx, "1 bomba nuclear", 120, 930, la, INK, 34, 'l')
    label(ctx, "de baja potencia", 120, 975, la, MUTED, 26, 'l')

def h_counter(ctx, t, d):
    p = P(t, d)
    Pj = world_proj()
    draw_map(ctx, Pj, a=0.45)
    k = eout(prog(p, .05, .55))
    r = random.Random(4)
    zones = [(-100, 40, 14, 7), (15, 50, 10, 5), (45, 55, 18, 6)]
    n = int(160 * k)
    for i in range(160):
        zx, zy, sx, sy = zones[i % 3]
        lon, lat = zx + r.gauss(0, sx / 2), zy + r.gauss(0, sy / 2)
        if i < n:
            x, y = Pj(lon, lat); glow(ctx, x, y, 22, RED, 0.5)
    col(ctx, BG, 0.55); ctx.rectangle(0, 330, W, 380); ctx.fill()
    text(ctx, fmt_int(91_500_000 * k), W / 2, 560, 190, INK, F_BLACK)
    label(ctx, "muertos y heridos · en unas pocas horas", W / 2, 640, 1, MUTED, 30)
    sa = ease(prog(p, .6, .75))
    text(ctx, "Simulación «Plan A» · Universidad de Princeton", W / 2, 780, 34, AMBER, F_SEMI, a=sa)
    source(ctx, "Princeton SGS, «Plan A»", sa)

def h_notworst(ctx, t, d):
    p = P(t, d)
    text(ctx, "…y eso no sería", W / 2, 500, 120, INK, F_BLACK, a=ease(prog(p, 0, .25)))
    a2 = ease(prog(p, .35, .6))
    text(ctx, "lo peor.", W / 2, 650, 150, RED, F_BLACK, a=a2)

def h_plate(ctx, t, d):
    p = P(t, d)
    g = cairo.LinearGradient(0, 600, 0, H)
    g.add_color_stop_rgba(0, .07, .08, .1, 1); g.add_color_stop_rgba(1, .03, .03, .04, 1)
    ctx.set_source(g); ctx.rectangle(0, 600, W, H - 600); ctx.fill()
    # cold light cone
    cg = cairo.RadialGradient(W / 2, 640, 20, W / 2, 640, 700)
    cg.add_color_stop_rgba(0, .7, .75, .82, .22); cg.add_color_stop_rgba(1, .7, .75, .82, 0)
    ctx.set_source(cg); ctx.paint()
    plate(ctx, W / 2, 680, 330, 1, 0.1)
    text(ctx, "semanas después · lejos de las bombas", W / 2, 230, 40, MUTED, F_SEMI, a=ease(prog(p, .05, .3)))
    text(ctx, "tu plato", W / 2, 400, 150, INK, F_BLACK, a=ease(prog(p, .78, .92)))

HOOK = [
    (h_clock, "Mañana. Nueve y catorce de la mañana."),
    (h_flash, "En algún lugar de Europa explota una sola bomba nuclear. Pequeña. De las menos potentes que existen."),
    (h_counter, "Unas pocas horas después... más de noventa millones de personas han muerto o están heridas. Eso es lo que calculó una simulación de la Universidad de Princeton."),
    (h_notworst, "Y aun así... eso no sería lo peor."),
    (h_plate, "Lo peor empezaría semanas más tarde. Lejos de las bombas. En un sitio en el que casi nadie piensa cuando imagina una guerra nuclear... tu plato."),
]

# ======================================================================= BLOCK 1
def b1_q(ctx, t, d):
    p = P(t, d)
    text(ctx, "1 bomba", 560, 580, 130, INK, F_BLACK, a=ease(prog(p, 0, .2)))
    a = ease(prog(p, .25, .45))
    col(ctx, MUTED, a); ctx.set_line_width(6)
    ctx.move_to(850, 540); ctx.line_to(1010, 540); ctx.stroke()
    ctx.move_to(1010, 515); ctx.line_to(1045, 540); ctx.line_to(1010, 565); ctx.close_path(); ctx.fill()
    text(ctx, "90 millones", 1420, 580, 110, RED, F_BLACK, a=ease(prog(p, .45, .65)))
    text(ctx, "?", W / 2, 360, 200, AMBER, F_BLACK, a=ease(prog(p, .7, .9)))

def chess_clock(ctx, x, y, left_active, tl, tr, a=1):
    col(ctx, PANEL, a); rrect(ctx, x - 420, y - 150, 840, 300, 30); ctx.fill()
    col(ctx, LINE, a); ctx.set_line_width(3); rrect(ctx, x - 420, y - 150, 840, 300, 30); ctx.stroke()
    for i, (tm, act) in enumerate(((tl, left_active), (tr, not left_active))):
        cx = x - 210 + i * 420
        col(ctx, RED if act else DIM, a)
        rrect(ctx, cx - 90, y - 200 + (14 if act else 0), 180, 40, 10); ctx.fill()
        col(ctx, (0, 0, 0), a); rrect(ctx, cx - 170, y - 90, 340, 180, 18); ctx.fill()
        text(ctx, tm, cx, y + 38, 96, RED if act else MUTED, F_MONO, a=a)

def b1_chess(ctx, t, d):
    p = P(t, d)
    left = int(t * 1.6) % 2 == 0
    sec = 10 - (t * 1.7) % 10
    chess_clock(ctx, W / 2, 470, left, f"0:{sec:04.1f}" if left else "0:08.0", "0:07.4" if left else f"0:{sec:04.1f}")
    text(ctx, "Nadie quiere ser el segundo", W / 2, 860, 76, INK, F_BLACK, a=ease(prog(p, .25, .5)))

def b1_alert(ctx, t, d):
    p = P(t, d)
    n = 2100 * eout(prog(p, 0, .4))
    text(ctx, fmt_int(n) + ("+" if p > .4 else ""), W / 2, 470, 230, AMBER, F_BLACK)
    label(ctx, "cabezas nucleares en alerta máxima", W / 2, 560, 1, INK, 36)
    a = ease(prog(p, .5, .7))
    bx, by, bw = 560, 680, 800
    col(ctx, DIM, a); rrect(ctx, bx, by, bw, 46, 10); ctx.fill()
    col(ctx, RED, a); rrect(ctx, bx, by, bw * 0.97 * ease(prog(p, .55, .8)), 46, 10); ctx.fill()
    text(ctx, "casi todas: EE. UU. y Rusia", W / 2, 800, 40, INK, F_SEMI, a=a)
    source(ctx, "SIPRI Yearbook 2026 (2.100–2.200 en alerta)", a)

def b1_missile(ctx, t, d):
    p = P(t, d)
    Pj = world_proj(60, 120, W - 120, H - 220)
    draw_map(ctx, Pj, fills={'RUS': (RED, .55), 'USA': (RED, .55)})
    x0, y0 = Pj(55, 56); x1, y1 = Pj(-97, 39)
    cx, cy = (x0 + x1) / 2, 60
    k = ease(prog(p, .05, .5))
    col(ctx, AMBER, 1); ctx.set_line_width(5); ctx.set_dash([18, 12])
    N = 60
    pts = []
    for i in range(int(N * k) + 1):
        u = i / N
        bx = (1 - u) ** 2 * x0 + 2 * (1 - u) * u * cx + u * u * x1
        by = (1 - u) ** 2 * y0 + 2 * (1 - u) * u * cy + u * u * y1
        pts.append((bx, by))
    for i, (bx, by) in enumerate(pts):
        (ctx.move_to if i == 0 else ctx.line_to)(bx, by)
    ctx.stroke(); ctx.set_dash([])
    if pts:
        glow(ctx, pts[-1][0], pts[-1][1], 30, AMBER, 1)
    mins = 30 * (1 - ease(prog(p, .1, .55)))
    col(ctx, BG, .8); rrect(ctx, W / 2 - 240, 760, 480, 150, 20); ctx.fill()
    text(ctx, f"{int(mins):02d}:{int((mins % 1) * 60):02d}", W / 2, 875, 110, INK, F_MONO)
    label(ctx, "≈ 30 minutos", W / 2, 740, 1, AMBER, 32)
    a = ease(prog(p, .6, .8))
    text(ctx, "minutos, no días, para decidir", W / 2, 1010, 54, INK, F_BLACK, a=a)

def silo(ctx, x, y, s, a):
    col(ctx, INK, a)
    ctx.move_to(x, y - s); ctx.line_to(x + s * .18, y - s * .7); ctx.line_to(x + s * .18, y)
    ctx.line_to(x - s * .18, y); ctx.line_to(x - s * .18, y - s * .7); ctx.close_path(); ctx.fill()

def b1_logic(ctx, t, d):
    p = P(t, d)
    text(ctx, "¿Espero a confirmarlo?", W / 2, 330, 96, INK, F_BLACK, a=ease(prog(p, 0, .2)))
    for i in range(8):
        x = 420 + i * 155
        gone = prog(p, .35 + i * .05, .45 + i * .05)
        silo(ctx, x, 720, 220, (1 - gone) * 0.9 + 0.08)
        if gone > 0.3:
            strike(ctx, x, 630, 120, gone)
    text(ctx, "…puede que mis misiles ya no existan", W / 2, 900, 58, RED, F_BLACK, a=ease(prog(p, .65, .85)))

def b1_domino(ctx, t, d):
    p = P(t, d)
    labels = ["Objetivos militares", "Armas del enemigo", "Ciudades"]
    label(ctx, "Simulación «Plan A» · Princeton", W / 2, 180, 1, MUTED, 28)
    # first: the trigger
    tx = 260
    glow(ctx, tx, 640, 70, AMBER, 1 if p < .9 else .6)
    label(ctx, "1ª bomba", tx, 820, 1, AMBER, 26)
    for i, lb in enumerate(labels):
        x = 640 + i * 440
        fall = ease(prog(p, .12 + i * .25, .3 + i * .25))
        ctx.save(); ctx.translate(x + 60, 820); ctx.rotate(fall * 1.05)
        c = RED if i == 2 else mix(INK, RED, .5 * i)
        col(ctx, c, .25 + .75 * ease(prog(p, .05 + i * .25, .15 + i * .25)))
        rrect(ctx, -120, -360, 120, 360, 12); ctx.fill()
        ctx.restore()
        text(ctx, lb, x, 900, 40, INK, F_XB, a=ease(prog(p, .15 + i * .25, .3 + i * .25)))
        label(ctx, f"fase {i + 1}", x, 950, ease(prog(p, .15 + i * .25, .3 + i * .25)), MUTED, 22)

def b1_chain(ctx, t, d):
    p = P(t, d)
    text(ctx, "Nadie decide destruir el mundo.", W / 2, 360, 80, INK, F_BLACK, a=ease(prog(p, 0, .25)))
    for i in range(5):
        a = ease(prog(p, .3 + i * .08, .4 + i * .08))
        x = 440 + i * 260
        col(ctx, RED if i == 4 else AMBER, a); ctx.arc(x, 580, 34, 0, 2 * math.pi); ctx.fill()
        if i < 4:
            col(ctx, MUTED, a); ctx.set_line_width(4); ctx.move_to(x + 50, 580); ctx.line_to(x + 200, 580); ctx.stroke()
            ctx.move_to(x + 200, 565); ctx.line_to(x + 222, 580); ctx.line_to(x + 200, 595); ctx.close_path(); ctx.fill()
    text(ctx, "Cada uno solo responde al anterior.", W / 2, 800, 64, MUTED, F_XB, a=ease(prog(p, .6, .85)))

B1 = [
    (b1_q, "Vamos por partes. Primero: ¿cómo puede una sola bomba pequeña acabar en noventa millones de víctimas?"),
    (b1_chess, "Por una razón muy simple: nadie quiere ser el segundo."),
    (b1_alert, "Hoy hay más de dos mil cabezas nucleares montadas en misiles y en alerta máxima. Casi todas son de Estados Unidos o de Rusia."),
    (b1_missile, "Un misil intercontinental tarda alrededor de media hora en cruzar el planeta. Así que, si un país cree que le están atacando, tiene minutos —no días— para decidir."),
    (b1_logic, "Y la lógica es brutal: si espero a confirmarlo, puede que mis misiles ya no existan cuando quiera usarlos."),
    (b1_domino, "Por eso, en la simulación de Princeton, esa primera bomba provoca una respuesta. Esa respuesta provoca otra. Primero contra objetivos militares... después contra las armas del enemigo... y al final, contra las ciudades."),
    (b1_chain, "Nadie decide destruir el mundo. Cada uno solo responde al anterior."),
]

# ======================================================================= CTA SUBSCRIBE
def logo(ctx, x, y, r, a=1):
    col(ctx, AMBER, a); ctx.arc(x, y, r, 0, 2 * math.pi); ctx.fill()
    text(ctx, "?", x, y + r * 0.42, r * 1.25, BG, F_BLACK, a=a)

def cta_sub(ctx, t, d):
    p = P(t, d)
    logo(ctx, W / 2 - 430, 450, 70)
    text(ctx, "LA GRAN PREGUNTA", W / 2 - 330, 478, 76, INK, F_BLACK, 'l')
    clicked = p > .45
    bx, by = W / 2 - 250, 600
    col(ctx, DIM if clicked else RED); rrect(ctx, bx, by, 500, 110, 55); ctx.fill()
    text(ctx, "SUSCRITO" if clicked else "SUSCRÍBETE", bx + 250 - (30 if clicked else 0), by + 72, 50,
         INK, F_BLACK)
    if clicked:
        # bell
        sw = math.sin(t * 14) * 0.35 * (1 - prog(p, .5, .8))
        ctx.save(); ctx.translate(bx + 445, by + 50); ctx.rotate(sw)
        col(ctx, INK); ctx.move_to(-22, 22); ctx.curve_to(-22, -30, 22, -30, 22, 22); ctx.close_path(); ctx.fill()
        ctx.arc(0, 30, 8, 0, 2 * math.pi); ctx.fill(); ctx.restore()
    # cursor
    cp = ease(prog(p, .1, .42))
    cx, cy = lerp(W / 2 + 500, bx + 250, cp), lerp(950, by + 70, cp)
    if p > .42 and p < .5:
        glow(ctx, cx, cy, 60, INK, .4)
    col(ctx, INK); ctx.move_to(cx, cy); ctx.line_to(cx, cy + 46); ctx.line_to(cx + 13, cy + 34)
    ctx.line_to(cx + 32, cy + 34); ctx.close_path(); ctx.fill()
    text(ctx, "Cada vídeo empieza con una pregunta… y termina con una respuesta.", W / 2, 880, 40, MUTED,
         F_SEMI, a=ease(prog(p, .5, .7)))

CTA_SUB = [(cta_sub, "Si te gusta entender lo que casi nadie explica, suscríbete a La Gran Pregunta. Aquí cada vídeo empieza con una pregunta... y termina con una respuesta.")]

# ======================================================================= BLOCK 2
def b2_title(ctx, t, d):
    p = P(t, d)
    label(ctx, "Segunda pregunta", W / 2, 420, ease(prog(p, 0, .3)), AMBER, 34)
    text(ctx, "¿Cuántas bombas hay?", W / 2, 590, 130, INK, F_BLACK, a=ease(prog(p, .15, .45)))

_DOTS = None
def b2_dots(ctx, t, d):
    global _DOTS
    p = P(t, d)
    N, cols = 12187, 150
    sp, x0, y0 = 8.2, (W - 150 * 8.2) / 2, 250
    if _DOTS is None:
        _DOTS = [(x0 + (i % cols) * sp, y0 + (i // cols) * sp) for i in range(N)]
    shown = int(N * eout(prog(p, 0, .35)))
    hl = int(4012 * eout(prog(p, .55, .75)))
    col(ctx, MUTED, .8)
    for i in range(hl, shown):
        x, y = _DOTS[i]; ctx.rectangle(x, y, 5, 5)
    ctx.fill()
    col(ctx, AMBER)
    for i in range(hl):
        x, y = _DOTS[i]; ctx.rectangle(x, y, 5, 5)
    ctx.fill()
    col(ctx, BG, .85); rrect(ctx, 0, 0, W, 210, 0); ctx.fill()
    text(ctx, fmt_int(shown), 120, 165, 120, INK, F_BLACK, 'l')
    label(ctx, "cabezas nucleares en el mundo · 2026", 125, 205, 1, MUTED, 24, 'l')
    a = ease(prog(p, .55, .7))
    text(ctx, fmt_int(hl), W - 120, 165, 120, AMBER, F_BLACK, 'r', a)
    label(ctx, "desplegadas en misiles y aviones", W - 120, 205, a, AMBER, 24, 'r')
    source(ctx, "SIPRI Yearbook 2026")

def b2_hiro(ctx, t, d):
    p = P(t, d)
    s = 34
    a1 = ease(prog(p, .0, .2))
    sm = math.sqrt(15) * s; big = math.sqrt(300) * s
    gy = 820
    col(ctx, INK, a1); ctx.rectangle(420, gy - sm, sm, sm); ctx.fill()
    text(ctx, "Hiroshima, 1945", 420 + sm / 2, gy + 60, 38, INK, F_XB, a=a1)
    label(ctx, "≈ 15 kilotones", 420 + sm / 2, gy + 100, a1, MUTED, 24)
    k = ease(prog(p, .5, .8))
    side = big * k
    col(ctx, RED, .85 * k); ctx.rectangle(980, gy - side, side, side); ctx.fill()
    a2 = ease(prog(p, .7, .9))
    text(ctx, "Una ojiva moderna", 980 + big / 2, gy + 60, 38, INK, F_XB, a=a2)
    label(ctx, "p. ej. 300 kt · 20 veces más", 980 + big / 2, gy + 100, a2, MUTED, 24)
    label(ctx, "Superficie = potencia", W / 2, 170, 1, MUTED, 24)

def donut(ctx, x, y, r, frac, a=1):
    ctx.set_line_width(r * 0.32)
    col(ctx, DIM, a); ctx.arc(x, y, r, 0, 2 * math.pi); ctx.stroke()
    col(ctx, RED, a); ctx.arc(x, y, r, -math.pi / 2, -math.pi / 2 + 2 * math.pi * frac); ctx.stroke()

def b2_donut(ctx, t, d):
    p = P(t, d)
    f = 0.83 * eout(prog(p, .05, .5))
    donut(ctx, 700, 540, 230, f)
    text(ctx, f"{int(round(f * 100))} %", 700, 580, 110, INK, F_BLACK)
    a = ease(prog(p, .35, .6))
    col(ctx, RED, a); ctx.rectangle(1080, 420, 40, 40); ctx.fill()
    text(ctx, "EE. UU. + Rusia", 1145, 455, 54, INK, F_XB, 'l', a)
    col(ctx, DIM, a); ctx.rectangle(1080, 540, 40, 40); ctx.fill()
    text(ctx, "Resto del mundo", 1145, 575, 54, MUTED, F_XB, 'l', a)
    label(ctx, "de las armas disponibles", 1080, 680, a, MUTED, 24, 'l')
    source(ctx, "SIPRI Yearbook 2026", a)

def bars2(ctx, p, a=1.0):
    rows = [("Muertos", 34.1, INK), ("Heridos", 57.4, RED)]
    for i, (lb, v, c) in enumerate(rows):
        y = 430 + i * 220
        k = eout(prog(p, .1 + i * .25, .45 + i * .25))
        text(ctx, lb, 260, y + 70, 48, INK, F_XB, 'l', a)
        col(ctx, c, a * .9); rrect(ctx, 560, y, 1100 * (v / 60) * k, 100, 12); ctx.fill()
        text(ctx, f"{v * k:.1f} M".replace(".", ","), 580 + 1100 * (v / 60) * k, y + 72, 56, c, F_BLACK, 'l', a * (k > .02))

def b2_bars(ctx, t, d):
    p = P(t, d)
    label(ctx, "Primeras horas · simulación «Plan A»", W / 2, 300, ease(prog(p, 0, .15)), MUTED, 28)
    bars2(ctx, p)
    source(ctx, "Princeton SGS / ICAN")

def b2_stamp(ctx, t, d):
    p = P(t, d)
    label(ctx, "Primeras horas · simulación «Plan A»", W / 2, 300, 1, MUTED, 28)
    bars2(ctx, 1.0, .35)
    k = eout(prog(p, .05, .25))
    ctx.save(); ctx.translate(W / 2, 560); ctx.rotate(-0.12); ctx.scale(1.6 - .6 * k, 1.6 - .6 * k)
    col(ctx, AMBER, k); ctx.set_line_width(8); rrect(ctx, -520, -90, 1040, 160, 14); ctx.stroke()
    text(ctx, "SOLO EXPLOSIONES", 0, 32, 100, AMBER, F_BLACK, a=k)
    ctx.restore()
    text(ctx, "No cuentan lo que viene después.", W / 2, 900, 64, INK, F_BLACK, a=ease(prog(p, .5, .75)))

B2 = [
    (b2_title, "Segunda pregunta: ¿cuántas bombas hay en el mundo?"),
    (b2_dots, "A principios de 2026, el instituto SIPRI de Estocolmo contó unas doce mil cabezas nucleares. Unas cuatro mil ya están desplegadas en misiles y aviones."),
    (b2_hiro, "Para que te hagas una idea: la bomba de Hiroshima tenía la fuerza de unas quince mil toneladas de dinamita. Muchas de las cabezas actuales son decenas de veces más potentes."),
    (b2_donut, "Y solo dos países, Estados Unidos y Rusia, tienen más del ochenta por ciento de todas."),
    (b2_bars, "Volvamos a la simulación. En unas pocas horas, Princeton calcula más de treinta y cuatro millones de muertos... y más de cincuenta y siete millones de heridos."),
    (b2_stamp, "Pero fíjate en un detalle: esas cifras solo cuentan las explosiones. No cuentan lo que viene después."),
]

# ======================================================================= BLOCK 3
def house(ctx, x, y, s, a=1, lit=1.0):
    col(ctx, hexc('#1C222C'), a); ctx.rectangle(x - s * .5, y - s * .55, s, s * .55); ctx.fill()
    ctx.move_to(x - s * .62, y - s * .5); ctx.line_to(x, y - s * .95); ctx.line_to(x + s * .62, y - s * .5)
    ctx.close_path(); ctx.fill()
    col(ctx, AMBER, a * lit); ctx.rectangle(x - s * .3, y - s * .4, s * .18, s * .16); ctx.fill()
    ctx.rectangle(x + s * .12, y - s * .4, s * .18, s * .16); ctx.fill()
    glow(ctx, x, y - s * .3, s * .7, AMBER, .15 * lit * a)

def b3_house(ctx, t, d):
    p = P(t, d)
    col(ctx, hexc('#0E1218')); ctx.rectangle(0, 760, W, H - 760); ctx.fill()
    col(ctx, LINE); ctx.set_line_width(2); ctx.move_to(0, 760); ctx.line_to(W, 760); ctx.stroke()
    for i, fx in enumerate((150, 1790)):
        f = (math.sin(t * 2 + i * 2) + 1) / 2
        glow(ctx, fx, 760, 90, AMBER, .25 + .2 * f)
    house(ctx, W / 2, 760, 260)
    text(ctx, "Sobrevives al primer día.", W / 2, 300, 84, INK, F_BLACK, a=ease(prog(p, .3, .5)))
    text(ctx, "¿Estás a salvo?", W / 2, 420, 84, AMBER, F_BLACK, a=ease(prog(p, .75, .9)))

_PART = None
def b3_wind(ctx, t, d):
    global _PART
    p = P(t, d)
    if _PART is None:
        r = random.Random(5)
        _PART = [(r.uniform(-400, W), r.uniform(150, 900), r.uniform(60, 160), r.uniform(2, 6)) for _ in range(700)]
    col(ctx, hexc('#0E1218')); ctx.rectangle(0, 900, W, H - 900); ctx.fill()
    house(ctx, 1500, 900, 160, lit=0.6)
    for x, y, v, s in _PART:
        xx = (x + v * t) % (W + 400) - 200
        yy = y + math.sin(t + x) * 10
        col(ctx, hexc('#B8C98A'), .35); ctx.arc(xx, yy, s, 0, 2 * math.pi); ctx.fill()
    for i in range(4):
        y = 250 + i * 160
        col(ctx, MUTED, .5); ctx.set_line_width(3)
        ox = (t * 120 + i * 300) % (W + 400) - 400
        ctx.move_to(ox, y); ctx.line_to(ox + 260, y); ctx.stroke()
    a = ease(prog(p, .1, .3))
    col(ctx, BG, .7 * a); rrect(ctx, 100, 90, 900, 150, 16); ctx.fill()
    text(ctx, "Polvo radiactivo", 140, 165, 60, INK, F_BLACK, 'l', a)
    label(ctx, "arrastrado a cientos de kilómetros", 140, 212, a, MUTED, 26, 'l')

def b3_icons(ctx, t, d):
    p = P(t, d)
    items = [("Hospitales", cross), ("Electricidad", None), ("Agua", tap), ("Internet", wifi)]
    for i, (lb, fn) in enumerate(items):
        x = 360 + i * 400
        off = prog(p, .2 + i * .17, .3 + i * .17)
        c = mix(INK, DIM, off)
        if fn is None:
            bulb(ctx, x, 540, 170, c, 1, on=1 - off)
        elif fn is tap:
            tap(ctx, x, 540, 200, c, drop=1 - off)
        elif fn is cross:
            cross(ctx, x, 540, 170, mix(RED, DIM, off))
        else:
            fn(ctx, x, 540, 190, c)
        if off > 0:
            strike(ctx, x, 540, 220, .9, ease(off))
        text(ctx, lb, x, 760, 44, mix(INK, MUTED, off), F_XB)

def b3_local(ctx, t, d):
    p = P(t, d)
    Pj = world_proj()
    k = ease(prog(p, .1, .4))
    fills = {iso: (RED, .6 * k) for iso in ['USA', 'RUS'] + EUROPE}
    draw_map(ctx, Pj, fills=fills)
    text(ctx, "Afectaría sobre todo a los países en guerra", W / 2, 1010, 54, INK, F_BLACK, a=k)

def b3_notrad(ctx, t, d):
    p = P(t, d)
    radiation(ctx, W / 2, 470, 220, AMBER, ease(prog(p, 0, .3)))
    sp = ease(prog(p, .55, .75))
    if sp > 0:
        col(ctx, RED); ctx.set_line_width(26); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.move_to(W / 2 - 260, 210); ctx.line_to(W / 2 - 260 + 520 * sp, 210 + 520 * sp); ctx.stroke()
        ctx.set_line_cap(cairo.LINE_CAP_BUTT)
    text(ctx, "Y no es la radiación.", W / 2, 920, 84, INK, F_BLACK, a=ease(prog(p, .6, .85)))

B3 = [
    (b3_house, "Supongamos que tú no vives cerca de ningún objetivo. Las bombas caen lejos. Sobrevives al primer día. ¿Estás a salvo?"),
    (b3_wind, "Durante las primeras semanas, el viento arrastra polvo radiactivo a cientos de kilómetros."),
    (b3_icons, "Los hospitales que siguen en pie no pueden atender a millones de heridos. Sin electricidad no hay bombeo de agua, ni frigoríficos, ni internet."),
    (b3_local, "Pero todo esto, por terrible que sea, afecta sobre todo a los países en guerra."),
    (b3_notrad, "Lo que convierte una guerra nuclear en un problema de todo el planeta es otra cosa. Y no es la radiación."),
]

# ======================================================================= BLOCK 4
_SMOKE = None
def smoke_field(ctx, t, x0, x1, ybase, rise, a=1.0, n=160, seed=9, top=0):
    rnd = random.Random(seed)
    for i in range(n):
        sx = rnd.uniform(x0, x1); sp = rnd.uniform(.6, 1.4); ph = rnd.uniform(0, 10); sz = rnd.uniform(40, 120)
        life = ((t * .12 * sp + ph / 10) % 1)
        y = ybase - life * rise
        if y < top: continue
        x = sx + math.sin(ph + t * .5) * 40 + life * 60
        r = sz * (0.6 + life * 1.6)
        g = cairo.RadialGradient(x, y, 0, x, y, r)
        gl = .30 + .1 * rnd.random()
        g.add_color_stop_rgba(0, gl, gl, gl + .02, .32 * a * (1 - life * .6))
        g.add_color_stop_rgba(1, gl, gl, gl, 0)
        ctx.set_source(g); ctx.arc(x, y, r, 0, 2 * math.pi); ctx.fill()

def b4_smoke(ctx, t, d):
    p = P(t, d)
    smoke_field(ctx, t + 5, 0, W, 1150, 1100, 1, 140)
    text(ctx, "ES EL HUMO.", W / 2, 600, 190, INK, F_BLACK, a=ease(prog(p, .1, .5)))

def b4_fire(ctx, t, d):
    p = P(t, d)
    g = cairo.LinearGradient(0, 600, 0, 940)
    g.add_color_stop_rgba(0, 1, .35, .1, 0); g.add_color_stop_rgba(1, 1, .35, .1, .55 * ease(prog(p, 0, .3)))
    ctx.set_source(g); ctx.rectangle(0, 600, W, 340); ctx.fill()
    smoke_field(ctx, t, 100, W - 100, 900, 900, ease(prog(p, .1, .4)), 150, seed=3)
    skyline(ctx, 960, 1, seed=21, lit=0.0, c=hexc('#07080A'))
    a = ease(prog(p, .55, .75))
    col(ctx, BG, .75 * a); rrect(ctx, 100, 90, 1000, 150, 16); ctx.fill()
    text(ctx, "Hollín negro", 140, 165, 60, INK, F_BLACK, 'l', a)
    label(ctx, "millones de toneladas subiendo al cielo", 140, 212, a, MUTED, 26, 'l')

def b4_strato(ctx, t, d):
    p = P(t, d)
    gy, cy = 980, 560     # ground, cloud ceiling
    g = cairo.LinearGradient(0, 0, 0, gy)
    g.add_color_stop_rgba(0, .03, .03, .07, 1); g.add_color_stop_rgba(1, .07, .11, .17, 1)
    ctx.set_source(g); ctx.rectangle(0, 0, W, gy); ctx.fill()
    col(ctx, hexc('#0E1218')); ctx.rectangle(0, gy, W, H - gy); ctx.fill()
    # clouds + rain below ceiling
    rnd = random.Random(2)
    for i in range(14):
        x = (i * 160 + t * 20) % (W + 200) - 100
        for k in range(3):
            col(ctx, hexc('#3A4452'), .7); ctx.arc(x + k * 45, cy + 40 + rnd.uniform(-8, 8), 45, 0, 2 * math.pi); ctx.fill()
    col(ctx, hexc('#5AA9FF'), .35); ctx.set_line_width(2)
    for i in range(120):
        x = (i * 37.3) % W; y0 = cy + 100 + ((i * 53 + t * 400) % (gy - cy - 120))
        ctx.move_to(x, y0); ctx.line_to(x - 6, y0 + 22)
    ctx.stroke()
    col(ctx, AMBER, .8); ctx.set_line_width(2); ctx.set_dash([12, 10])
    ctx.move_to(0, cy); ctx.line_to(W, cy); ctx.stroke(); ctx.set_dash([])
    label(ctx, "Aquí se forman nubes y lluvia", 60, cy + 150, 1, INK, 24, 'l')
    label(ctx, "Estratosfera · aquí no llueve", 60, 170, ease(prog(p, .35, .5)), AMBER, 30, 'l')
    # plume
    k = ease(prog(p, .05, .5))
    top = lerp(gy, 260, k)
    rnd = random.Random(8)
    for i in range(70):
        u = i / 70
        y = lerp(gy, top, u)
        spread = 60 + 200 * u + (900 * ease(prog(p, .5, .9)) if y < cy - 120 else 0) * u
        x = W / 2 + 120 + rnd.uniform(-1, 1) * spread
        r = 50 + 60 * u
        gg = cairo.RadialGradient(x, y, 0, x, y, r)
        gg.add_color_stop_rgba(0, .42, .42, .44, .5); gg.add_color_stop_rgba(1, .42, .42, .44, 0)
        ctx.set_source(gg); ctx.arc(x, y, r, 0, 2 * math.pi); ctx.fill()
    if p > .5:
        sp = ease(prog(p, .5, .9))
        col(ctx, (.33, .33, .35), .7 * sp); rrect(ctx, W / 2 + 120 - 1000 * sp, 220, 2000 * sp, 150, 70); ctx.fill()
    text(ctx, "Nada lo limpia.", W - 80, 460, 64, INK, F_BLACK, 'r', ease(prog(p, .8, .95)))

def b4_globe(ctx, t, d):
    p = P(t, d)
    sx, sy = 260, 300
    glow(ctx, sx, sy, 260, AMBER, .9)
    col(ctx, hexc('#FFD27A')); ctx.arc(sx, sy, 90, 0, 2 * math.pi); ctx.fill()
    dark = ease(prog(p, .1, .7))
    col(ctx, AMBER, .25 * (1 - dark)); ctx.set_line_width(3)
    for i in range(7):
        ctx.move_to(sx + 120, sy + (i - 3) * 30); ctx.line_to(1000, 540 + (i - 3) * 90)
    ctx.stroke()
    globe(ctx, 1240, 560, 360, 1, 0, t)
    # dark band from north
    ctx.save(); ctx.arc(1240, 560, 362, 0, 2 * math.pi); ctx.clip()
    col(ctx, (.02, .02, .025), .72 * dark); ctx.rectangle(860, 190, 760, 740 * (0.35 + .65 * dark)); ctx.fill()
    ctx.restore()
    col(ctx, hexc('#5AA9FF'), .35); ctx.set_line_width(3); ctx.arc(1240, 560, 362, 0, 2 * math.pi); ctx.stroke()
    a = ease(prog(p, .55, .75))
    text(ctx, "Una sombrilla negra", 1240, 1010, 58, INK, F_BLACK, a=a)
    label(ctx, "durante años", 260, 520, ease(prog(p, .2, .4)), AMBER, 30)

def thermo(ctx, x, y, h, lvl, c, a=1):
    col(ctx, LINE, a); rrect(ctx, x - 26, y - h, 52, h, 26); ctx.fill(); ctx.arc(x, y + 20, 50, 0, 2 * math.pi); ctx.fill()
    col(ctx, c, a); rrect(ctx, x - 14, y - h * lvl, 28, h * lvl + 10, 14); ctx.fill(); ctx.arc(x, y + 20, 36, 0, 2 * math.pi); ctx.fill()

def b4_cold(ctx, t, d):
    p = P(t, d)
    k = ease(prog(p, .1, .6))
    thermo(ctx, 420, 760, 480, lerp(.8, .25, k), mix(RED, hexc('#5AA9FF'), k))
    label(ctx, "Menos luz → menos calor", 420, 920, 1, INK, 28)
    g = ease(prog(p, .45, .95))
    for i in range(7):
        x = 980 + i * 120
        h = lerp(420, 120, g) * (0.85 + 0.15 * math.sin(i * 1.7))
        wheat(ctx, x, 800, h, mix(AMBER, DIM, g), 1)
    col(ctx, hexc('#2A2218')); ctx.rectangle(900, 800, 900, 18); ctx.fill()
    label(ctx, "→ los cultivos no crecen", 1340, 920, ease(prog(p, .45, .65)), INK, 28)

def b4_title(ctx, t, d):
    p = P(t, d)
    rnd = random.Random(1)
    for i in range(260):
        x = (rnd.uniform(0, W) + math.sin(t + i) * 30) % W
        y = (rnd.uniform(0, H) + t * rnd.uniform(30, 70)) % H
        col(ctx, (.7, .7, .72), .35); ctx.arc(x, y, rnd.uniform(1.5, 4), 0, 2 * math.pi); ctx.fill()
    label(ctx, "Los científicos lo llaman", W / 2, 440, ease(prog(p, 0, .3)), MUTED, 34)
    text(ctx, "INVIERNO NUCLEAR", W / 2, 620, 170, INK, F_BLACK, a=ease(prog(p, .25, .6)))

B4 = [
    (b4_smoke, "Es el humo."),
    (b4_fire, "Cuando una bomba nuclear cae sobre una ciudad, no solo destruye edificios. Provoca incendios gigantescos. Millones de toneladas de hollín negro suben hacia el cielo."),
    (b4_strato, "Y aquí está la clave: ese humo sube tan alto que supera la altura donde se forman las nubes. Llega a la estratosfera. Allí arriba no llueve. Nada lo limpia."),
    (b4_globe, "Así que el humo se queda... durante años. Rodea el planeta entero y funciona como una sombrilla negra que tapa parte de la luz del Sol."),
    (b4_cold, "Menos luz significa menos calor. Y menos calor significa que los cultivos no crecen."),
    (b4_title, "Los científicos lo llaman invierno nuclear."),
]

# ======================================================================= CTA COMMENT
def cta_comment(ctx, t, d):
    p = P(t, d)
    draw_map(ctx, world_proj(), a=.5)
    k = eout(prog(p, 0, .25))
    col(ctx, PANEL, .95 * k); rrect(ctx, 360, 300, 1200, 380, 30); ctx.fill()
    col(ctx, PANEL, .95 * k); ctx.move_to(520, 680); ctx.line_to(600, 680); ctx.line_to(500, 760); ctx.close_path(); ctx.fill()
    col(ctx, AMBER, k); ctx.set_line_width(4); rrect(ctx, 360, 300, 1200, 380, 30); ctx.stroke()
    text(ctx, "¿Qué país tendría", W / 2, 450, 84, INK, F_BLACK, a=k)
    text(ctx, "más comida?", W / 2, 560, 84, AMBER, F_BLACK, a=k)
    text(ctx, "Escríbelo en los comentarios ↓", W / 2, 640, 36, MUTED, F_SEMI, a=ease(prog(p, .3, .5)))
    label(ctx, "Al final te digo si acertaste", W / 2, 900, ease(prog(p, .6, .8)), INK, 30)

CTA_COM = [(cta_comment, "Antes de seguir, una pregunta para ti. En ese mundo sin cosechas... ¿qué país crees que tendría más comida? Escríbelo en los comentarios. Al final te digo si acertaste.")]

# ======================================================================= BLOCK 5
def b5_study(ctx, t, d):
    p = P(t, d)
    k = eout(prog(p, 0, .2))
    col(ctx, PANEL, k); rrect(ctx, 460, 260, 1000, 520, 24); ctx.fill()
    col(ctx, LINE, k); ctx.set_line_width(2); rrect(ctx, 460, 260, 1000, 520, 24); ctx.stroke()
    label(ctx, "Estudio científico · 2022", 520, 340, k, AMBER, 26, 'l')
    text(ctx, "Nature Food", 520, 450, 96, INK, F_BLACK, 'l', k)
    text(ctx, "Xia y colaboradores", 520, 520, 40, MUTED, F_SEMI, 'l', k)
    text(ctx, "¿Qué pasa con las cosechas", 520, 640, 46, INK, F_XB, 'l', ease(prog(p, .3, .5)))
    text(ctx, "tras una guerra nuclear?", 520, 700, 46, INK, F_XB, 'l', ease(prog(p, .3, .5)))
    for i in range(5):
        wheat(ctx, 1560 + (i % 2) * 70, 900 - i * 10, 260, AMBER, .3 + .1 * i)
    source(ctx, "Xia et al., Nature Food (2022)")

def food_bar(ctx, p, drop, c, title, sub):
    label(ctx, "Producción mundial de alimentos", 260, 330, 1, MUTED, 26, 'l')
    k = eout(prog(p, .2, .55))
    bw = 1400
    col(ctx, DIM); rrect(ctx, 260, 380, bw, 130, 14); ctx.fill()
    col(ctx, c); rrect(ctx, 260, 380, bw * (1 - drop * k), 130, 14); ctx.fill()
    text(ctx, f"−{int(round(drop * 100 * k))} %", 260 + bw * (1 - drop * k) + (20 if drop < .5 else -20), 475, 80,
         INK, F_BLACK, 'l' if drop < .5 else 'r')
    text(ctx, title, 260, 650, 60, INK, F_BLACK, 'l', ease(prog(p, 0, .2)))
    label(ctx, sub, 260, 700, ease(prog(p, .1, .3)), MUTED, 26, 'l')

def b5_7(ctx, t, d):
    p = P(t, d)
    food_bar(ctx, p, .07, AMBER, "Guerra India – Pakistán", "efecto en 5 años")
    a = ease(prog(p, .65, .85))
    for i in range(40):
        person(ctx, 280 + i * 35, 900, 46, INK, a * .7)
    text(ctx, "…para 8.000 millones de personas", 260, 1000, 44, INK, F_XB, 'l', a)
    source(ctx, "Xia et al., Nature Food (2022)")

def b5_90(ctx, t, d):
    p = P(t, d)
    food_bar(ctx, p, .90, RED, "Guerra total EE. UU. – Rusia", "calorías producidas · 3–4 años después")
    source(ctx, "Xia et al., Nature Food (2022)")

def b5_people(ctx, t, d):
    p = P(t, d)
    for i in range(4):
        hungry = i < 3
        k = ease(prog(p, .3 + i * .1, .45 + i * .1))
        c = mix(INK, RED, k) if hungry else INK
        person(ctx, 480 + i * 320, 640, 330, c, 1 if not hungry else 1 - .35 * k)
    text(ctx, "3 de cada 4", W / 2, 900, 96, RED, F_BLACK, a=ease(prog(p, .6, .8)))
    label(ctx, "pasando hambre en 2 años", W / 2, 960, ease(prog(p, .65, .85)), INK, 30)
    source(ctx, "Xia et al., Nature Food (2022)")

def b5_compare(ctx, t, d):
    p = P(t, d)
    base, maxh = 900, 560
    a1 = ease(prog(p, 0, .15))
    h1 = maxh * 90 / 5000
    col(ctx, INK, a1); ctx.rectangle(560, base - h1, 260, h1); ctx.fill()
    text(ctx, "90 M", 690, base - h1 - 30, 64, INK, F_BLACK, a=a1)
    label(ctx, "víctimas de las bombas", 690, base + 60, a1, MUTED, 24)
    k = eout(prog(p, .12, .45))
    h2 = maxh * k
    col(ctx, RED); ctx.rectangle(1100, base - h2, 260, h2); ctx.fill()
    text(ctx, fmt_int(5000 * k) + " M", 1230, base - h2 - 30, 72, RED, F_BLACK, a=k > .02)
    label(ctx, "muertes por hambre", 1230, base + 60, ease(prog(p, .12, .3)), MUTED, 24)
    text(ctx, "Las bombas no serían lo peor.", W / 2, 150, 64, INK, F_BLACK, a=ease(prog(p, .75, .9)))
    source(ctx, "Princeton SGS · Xia et al., Nature Food (2022)")

def hunger_map(ctx, p, green=0.0, hemi=0.0):
    Pj = world_proj()
    k = ease(prog(p, .3, .55))
    fills = {iso: (RED, .75 * k) for iso in ['CAN'] + EUROPE}
    if green > 0:
        fills.update({'ARG': (GREEN, .85 * green), 'AUS': (GREEN, .85 * green)})
    draw_map(ctx, Pj, fills=fills)
    if hemi > 0:
        x0, ye = Pj(-170, 0)
        col(ctx, GREEN, .07 * hemi); ctx.rectangle(0, ye, W, H - ye); ctx.fill()
        col(ctx, INK, .6 * hemi); ctx.set_line_width(2); ctx.set_dash([14, 10])
        ctx.move_to(0, ye); ctx.line_to(W, ye); ctx.stroke(); ctx.set_dash([])
        label(ctx, "Ecuador", 80, ye - 14, hemi, INK, 22, 'l')
    return Pj

def b5_map(ctx, t, d):
    p = P(t, d)
    Pj = hunger_map(ctx, p)
    a = ease(prog(p, .5, .7))
    x, y = Pj(-100, 60); label(ctx, "Canadá", x, y, a, INK, 30)
    x, y = Pj(15, 57); label(ctx, "Europa", x, y - 60, a, INK, 30)
    text(ctx, "Entre las zonas con más hambre", W / 2, 1015, 54, INK, F_BLACK, a=ease(prog(p, .55, .75)))
    label(ctx, "Ni siquiera estarían en guerra", W / 2, 120, ease(prog(p, .1, .3)), AMBER, 30)
    source(ctx, "mapas de Xia et al. (2022)", a)

B5 = [
    (b5_study, "En 2022, un equipo de científicos publicó en la revista Nature Food el estudio más completo sobre esto. Calcularon qué pasaría con las cosechas del mundo tras distintos tipos de guerra nuclear."),
    (b5_7, "Empezaron por una guerra pequeña, entre India y Pakistán. Solo con eso, la producción mundial de alimentos caería un siete por ciento en cinco años. Un siete por ciento menos de comida... para ocho mil millones de personas."),
    (b5_90, "Después calcularon el peor escenario: una guerra total entre Estados Unidos y Rusia. Tres o cuatro años después, las calorías que produce el planeta caerían alrededor de un noventa por ciento."),
    (b5_people, "En solo dos años, más de tres de cada cuatro personas en la Tierra estarían pasando hambre."),
    (b5_compare, "Y el resultado final: más de cinco mil millones de muertos por hambre. Cinco mil millones. Frente a noventa millones de víctimas de las bombas. Por eso decía al principio que las bombas no serían lo peor."),
    (b5_map, "Y hay algo todavía más inquietante: muchos de los países que más sufrirían ni siquiera estarían en guerra. En los mapas del estudio, Canadá y gran parte de Europa aparecen entre las zonas con más hambre."),
]

# ======================================================================= CTA LIKE
def cta_like(ctx, t, d):
    p = P(t, d)
    k = eout(prog(p, .05, .3))
    pop = 1 + .15 * math.sin(prog(p, .3, .45) * math.pi)
    ctx.save(); ctx.translate(W / 2, 470); ctx.scale(max(k * pop, 1e-3), max(k * pop, 1e-3))
    glow(ctx, 0, 0, 260, AMBER, .35)
    thumb(ctx, 0, 0, 260, INK)
    ctx.restore()
    for i in range(10):
        bp = prog(p, .3, .6)
        if 0 < bp < 1:
            ang = i * math.pi / 5
            col(ctx, AMBER, 1 - bp); ctx.arc(W / 2 + math.cos(ang) * 260 * eout(bp), 470 + math.sin(ang) * 260 * eout(bp), 10, 0, 2 * math.pi); ctx.fill()
    text(ctx, "¿Te ha cambiado la idea?", W / 2, 820, 76, INK, F_BLACK, a=ease(prog(p, .2, .45)))
    label(ctx, "Dale a like", W / 2, 900, ease(prog(p, .4, .6)), AMBER, 34)

CTA_LIKE = [(cta_like, "Si este dato te ha cambiado la idea que tenías de una guerra nuclear, dale a like. Así YouTube sabe que este vídeo merece llegar a más gente.")]

# ======================================================================= BLOCK 6
def b6_map(ctx, t, d):
    p = P(t, d)
    g = ease(prog(p, .55, .75))
    Pj = hunger_map(ctx, 1.0, green=g)
    label(ctx, "La respuesta", W / 2, 120, ease(prog(p, 0, .2)), AMBER, 30)
    x, y = Pj(-65, -38); text(ctx, "Argentina", x + 40, y + 10, 40, GREEN, F_BLACK, 'l', g)
    x, y = Pj(134, -25); text(ctx, "Australia", x, y + 150, 40, GREEN, F_BLACK, a=g)
    source(ctx, "mapas de Xia et al. (2022)", g)

def b6_hemi(ctx, t, d):
    p = P(t, d)
    hunger_map(ctx, 1.0, green=1.0, hemi=ease(prog(p, .1, .3)))
    a = ease(prog(p, .3, .5))
    col(ctx, BG, .85 * a); rrect(ctx, 1060, 760, 800, 270, 18); ctx.fill()
    label(ctx, "Una razón probable", 1100, 820, a, AMBER, 24, 'l')
    for i, s in enumerate(["Hemisferio sur", "Lejos de los objetivos", "Producen más comida de la que consumen"]):
        text(ctx, "· " + s, 1100, 880 + i * 52, 36, INK, F_SEMI, 'l', ease(prog(p, .35 + i * .15, .5 + i * .15)))

def b6_paradox(ctx, t, d):
    p = P(t, d)
    label(ctx, "La paradoja", W / 2, 360, ease(prog(p, 0, .15)), AMBER, 34)
    text(ctx, "Quienes mejor resistirían", W / 2, 520, 92, INK, F_BLACK, a=ease(prog(p, .1, .3)))
    text(ctx, "no tendrían nada que ver", W / 2, 640, 92, INK, F_BLACK, a=ease(prog(p, .25, .45)))
    text(ctx, "con la guerra.", W / 2, 760, 92, GREEN, F_BLACK, a=ease(prog(p, .35, .55)))

B6 = [
    (b6_map, "Ahora sí, la respuesta a la pregunta de antes. ¿Qué países saldrían mejor parados? En los mapas del estudio destacan dos: Argentina y Australia."),
    (b6_hemi, "¿Por qué? Una razón probable: están en el hemisferio sur, lejos de los principales objetivos, y producen mucha más comida de la que consumen."),
    (b6_paradox, "Y fíjate en la paradoja: en una guerra entre las mayores potencias del mundo, quienes mejor podrían resistir serían dos países que no tendrían nada que ver con ella. Si lo acertaste en los comentarios... enhorabuena."),
]

# ======================================================================= BLOCK 7
def b7_q(ctx, t, d):
    p = P(t, d)
    label(ctx, "Última pregunta", W / 2, 380, ease(prog(p, 0, .2)), AMBER, 34)
    text(ctx, "¿Por qué no ha pasado nunca?", W / 2, 560, 110, INK, F_BLACK, a=ease(prog(p, .5, .75)))

def b7_close(ctx, t, d):
    p = P(t, d)
    text(ctx, "Nadie ganaría.", W / 2, 470, 120, INK, F_BLACK, a=ease(prog(p, 0, .2)) * (1 - .6 * prog(p, .5, .6)))
    text(ctx, "Pero ha estado cerca.", W / 2, 680, 120, RED, F_BLACK, a=ease(prog(p, .6, .8)))

def crt(ctx, t, p, alert=1.0, a=1.0):
    cx, cy, r = 700, 560, 330
    col(ctx, hexc('#06120B'), a); ctx.arc(cx, cy, r, 0, 2 * math.pi); ctx.fill()
    col(ctx, CRT, .35 * a); ctx.set_line_width(2)
    for k in (1, 2, 3):
        ctx.arc(cx, cy, r * k / 3, 0, 2 * math.pi); ctx.stroke()
    ctx.move_to(cx - r, cy); ctx.line_to(cx + r, cy); ctx.move_to(cx, cy - r); ctx.line_to(cx, cy + r); ctx.stroke()
    ang = t * 2
    g = cairo.LinearGradient(cx, cy, cx + math.cos(ang) * r, cy + math.sin(ang) * r)
    col(ctx, CRT, .8 * a); ctx.set_line_width(4)
    ctx.move_to(cx, cy); ctx.line_to(cx + math.cos(ang) * r, cy + math.sin(ang) * r); ctx.stroke()
    for i in range(5):
        bx = cx - 120 + i * 40 + math.sin(i) * 30; by = cy - 200 + i * 25 + t * 6
        on = (math.sin(t * 6 + i) > 0) * alert
        col(ctx, RED if on else CRT, a * (.5 + .5 * on)); ctx.arc(bx, by, 9, 0, 2 * math.pi); ctx.fill()
    ctx.set_line_width(14); col(ctx, hexc('#1B2027'), a); ctx.arc(cx, cy, r + 8, 0, 2 * math.pi); ctx.stroke()

def b7_bunker(ctx, t, d):
    p = P(t, d)
    text(ctx, "26 · 09 · 1983", 1150, 330, 90, INK, F_MONO, 'l', ease(prog(p, 0, .15)))
    label(ctx, "Búnker de alerta · cerca de Moscú", 1150, 390, ease(prog(p, .15, .3)), MUTED, 26, 'l')
    label(ctx, "Oficial de guardia: Stanislav Petrov", 1150, 440, ease(prog(p, .3, .45)), INK, 26, 'l')
    crt(ctx, t, p, alert=1.0 if p > .6 else 0.0)
    if p > .6:
        bl = 1.0 if int(t * 3) % 2 == 0 else .35
        col(ctx, RED, bl); rrect(ctx, 1150, 560, 650, 170, 14); ctx.fill()
        text(ctx, "ALERTA", 1475, 640, 64, INK, F_BLACK, a=1)
        label(ctx, "lanzamiento de misiles · EE. UU.", 1475, 695, 1, INK, 22)

def b7_duty(ctx, t, d):
    p = P(t, d)
    crt(ctx, t, p, 1.0, .35)
    col(ctx, hexc('#2A0E0B')); ctx.arc(1400, 560, 170, 0, 2 * math.pi); ctx.fill()
    col(ctx, RED); ctx.arc(1400, 545, 140, 0, 2 * math.pi); ctx.fill()
    text(ctx, "INFORMAR", 1400, 560, 46, INK, F_BLACK)
    a = ease(prog(p, .45, .7))
    text(ctx, "→ podría desencadenar una respuesta", 1400, 820, 40, INK, F_XB, a=a)

def b7_decide(ctx, t, d):
    p = P(t, d)
    col(ctx, hexc('#2A0E0B')); ctx.arc(W / 2, 520, 170, 0, 2 * math.pi); ctx.fill()
    col(ctx, RED); ctx.arc(W / 2, 505, 140, 0, 2 * math.pi); ctx.fill()
    text(ctx, "INFORMAR", W / 2, 520, 46, INK, F_BLACK)
    app = ease(prog(p, 0, .35)); ret = ease(prog(p, .55, .8))
    fy = lerp(1100, 700, app) + 400 * ret
    col(ctx, INK, .9); rrect(ctx, W / 2 - 45, fy, 90, 400, 45); ctx.fill()
    text(ctx, "«Un ataque real no sería con un puñado de misiles»", W / 2, 180, 44, MUTED, F_SEMI,
         a=ease(prog(p, .2, .4)))
    text(ctx, "Error del sistema.", W / 2, 920, 84, AMBER, F_BLACK, a=ease(prog(p, .7, .9)))

def b7_false(ctx, t, d):
    p = P(t, d)
    k = eout(prog(p, .02, .2))
    ctx.save(); ctx.translate(W / 2, 360); ctx.rotate(-.06); ctx.scale(1.5 - .5 * k, 1.5 - .5 * k)
    col(ctx, GREEN, k); ctx.set_line_width(8); rrect(ctx, -480, -90, 960, 160, 14); ctx.stroke()
    text(ctx, "FALSA ALARMA", 0, 32, 100, GREEN, F_BLACK, a=k)
    ctx.restore()
    a = ease(prog(p, .4, .6))
    for i in range(25):
        x = 360 + i * 50
        person(ctx, x, 760, 70, AMBER if i == 12 else DIM, a * (1 if i == 12 else .8))
    if a > 0: glow(ctx, 360 + 12 * 50, 740, 90, AMBER, .4 * a)
    text(ctx, "La decisión de una sola persona.", W / 2, 950, 64, INK, F_BLACK, a=ease(prog(p, .6, .8)))

B7 = [
    (b7_q, "Última pregunta. Con más de doce mil bombas y decisiones que se toman en minutos... ¿por qué no ha pasado nunca?"),
    (b7_close, "Parte de la respuesta es justo lo que acabas de ver: todos saben que no habría ganador. Pero la otra parte es más inquietante. Porque ha estado cerca."),
    (b7_bunker, "Veintiséis de septiembre de 1983. Un búnker cerca de Moscú. El oficial soviético Stanislav Petrov está de guardia cuando el sistema de alerta marca que Estados Unidos ha lanzado misiles contra la Unión Soviética."),
    (b7_duty, "Su deber es informar a sus superiores. Y eso podría desencadenar una respuesta."),
    (b7_decide, "Petrov piensa que, si Estados Unidos atacara de verdad, no lo haría con un puñado de misiles. Decide que es un error del sistema. Y no lo comunica como un ataque."),
    (b7_false, "Tenía razón. Era una falsa alarma. Ese día, la diferencia entre el mundo de este vídeo y el nuestro... fue la decisión de una sola persona."),
]

# ======================================================================= BLOCK 8 (close)
def clockface(ctx, x, y, r, sec_before, a=1):
    col(ctx, PANEL, a); ctx.arc(x, y, r, 0, 2 * math.pi); ctx.fill()
    col(ctx, LINE, a); ctx.set_line_width(4); ctx.arc(x, y, r, 0, 2 * math.pi); ctx.stroke()
    for i in range(60):
        ang = i / 60 * 2 * math.pi - math.pi / 2
        l = .12 if i % 5 == 0 else .05
        col(ctx, INK if i % 5 == 0 else MUTED, a); ctx.set_line_width(5 if i % 5 == 0 else 2)
        ctx.move_to(x + math.cos(ang) * r * (1 - l), y + math.sin(ang) * r * (1 - l))
        ctx.line_to(x + math.cos(ang) * r * .96, y + math.sin(ang) * r * .96); ctx.stroke()
    m = -sec_before / 60  # minutes relative to 12
    ang = m / 60 * 2 * math.pi - math.pi / 2
    col(ctx, RED, a); ctx.set_line_width(10); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.move_to(x, y); ctx.line_to(x + math.cos(ang) * r * .85, y + math.sin(ang) * r * .85); ctx.stroke()
    hang = (m / 60) / 12 * 2 * math.pi - math.pi / 2
    col(ctx, INK, a); ctx.set_line_width(14)
    ctx.move_to(x, y); ctx.line_to(x + math.cos(hang) * r * .55, y + math.sin(hang) * r * .55); ctx.stroke()
    ctx.set_line_cap(cairo.LINE_CAP_BUTT)
    col(ctx, INK, a); ctx.arc(x, y, 14, 0, 2 * math.pi); ctx.fill()

def b8_clock(ctx, t, d):
    p = P(t, d)
    sb = lerp(600, 85, eout(prog(p, 0, .45)))
    clockface(ctx, 640, 540, 330, sb)
    text(ctx, f"{int(sb)} s", 1150, 520, 170, RED, F_BLACK, 'l')
    label(ctx, "para la medianoche", 1160, 590, 1, INK, 30, 'l')
    a = ease(prog(p, .5, .7))
    label(ctx, "Reloj del Juicio Final · 2026", 1160, 680, a, MUTED, 24, 'l')
    text(ctx, "Nunca había estado tan cerca.", 1160, 760, 44, AMBER, F_XB, 'l', ease(prog(p, .7, .9)))
    source(ctx, "Bulletin of the Atomic Scientists, 2026", a)

def b8_back(ctx, t, d):
    p = P(t, d)
    sb = lerp(85, 300, ease(prog(p, .35, .85)))
    clockface(ctx, 640, 540, 330, sb)
    text(ctx, "Un reloj", 1150, 420, 80, INK, F_BLACK, 'l', ease(prog(p, 0, .15)))
    text(ctx, "no es una profecía.", 1150, 510, 80, INK, F_BLACK, 'l', ease(prog(p, .05, .2)))
    text(ctx, "Se puede atrasar.", 1150, 680, 80, GREEN, F_BLACK, 'l', ease(prog(p, .6, .8)))

def b8_final(ctx, t, d):
    p = P(t, d)
    plate(ctx, W / 2, 700, 300, ease(prog(p, 0, .2)), 0.1)
    text(ctx, "Lo peor no serían las bombas.", W / 2, 260, 76, INK, F_BLACK, a=ease(prog(p, .45, .6)))
    g = ease(prog(p, .7, .9))
    text(ctx, "Sería todo lo que dejaríamos de cultivar.", W / 2, 370, 60, AMBER, F_XB, a=g)

B8 = [
    (b8_clock, "Hoy el Reloj del Juicio Final, el que usan los científicos atómicos para medir lo cerca que estamos de la catástrofe, marca ochenta y cinco segundos para la medianoche. Nunca había estado tan cerca."),
    (b8_back, "Pero un reloj no es una profecía. Lo mueven las decisiones de las personas... y se puede volver a atrasar."),
    (b8_final, "Así que, si alguien te pregunta qué pasaría si mañana estallara una guerra nuclear, ya sabes la respuesta. Lo peor no serían las bombas. Sería todo lo que dejaríamos de cultivar."),
]

# ======================================================================= END
def end_sun(ctx, t, d):
    p = P(t, d)
    k = 1 - ease(prog(p, .2, .85))
    x, y = 520, 470
    if k > 0:
        glow(ctx, x, y, 380 * k + 40, AMBER, .9 * k)
        col(ctx, hexc('#FFD27A'), k); ctx.arc(x, y, 160 * k + 4, 0, 2 * math.pi); ctx.fill()
    col(ctx, LINE); ctx.set_line_width(2); ctx.arc(x, y, 168, 0, 2 * math.pi); ctx.stroke()
    text(ctx, "¿Y si el Sol", x, 820, 84, INK, F_BLACK, a=ease(prog(p, .1, .3)))
    text(ctx, "desapareciera?", x, 920, 84, AMBER, F_BLACK, a=ease(prog(p, .2, .4)))
    # end-screen placeholder area (YouTube elements go on the right)
    a = ease(prog(p, .35, .55))
    col(ctx, LINE, a); ctx.set_line_width(3); ctx.set_dash([14, 10])
    rrect(ctx, 1060, 260, 720, 405, 16); ctx.stroke(); ctx.set_dash([])
    label(ctx, "Siguiente vídeo", 1420, 470, a * .6, MUTED, 26)
    logo(ctx, 1260, 850, 60, a)
    text(ctx, "LA GRAN PREGUNTA", 1340, 875, 46, INK, F_BLACK, 'l', a)

END = [(end_sun, "Y si te has quedado pensando en un cielo sin Sol... tengo otra pregunta para ti. ¿Qué pasaría si el Sol desapareciera de golpe? Te espero en ese vídeo.")]

BLOCKS = [
    ("00_hook", HOOK), ("01_una_bomba", B1), ("02_cta_sub", CTA_SUB), ("03_arsenal", B2),
    ("04_dia_despues", B3), ("05_humo", B4), ("06_cta_comentario", CTA_COM), ("07_hambre", B5),
    ("08_cta_like", CTA_LIKE), ("09_quien_comeria", B6), ("10_petrov", B7), ("11_cierre", B8),
    ("12_siguiente", END),
]
