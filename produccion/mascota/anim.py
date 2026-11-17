"""Prueba 20 s estilo animación 2D plana: la mascota de La Gran Pregunta descubre que el Sol sale por el oeste.
Uso: python3 anim.py stills | audio | video"""
import sys, os, math, json, re, random, subprocess, time
sys.path.append('/home/claude/video')
import cairo
import numpy as np
from PIL import Image, ImageFilter
from lib import font, hexc, clamp, lerp, ease, eout, mix, F_BLACK, F_XB
from script import TEXT

HERE = os.path.dirname(os.path.abspath(__file__))
W, H, FPS, DUR = 1920, 1080, 30, 20.0
V0 = 1.5
A = json.load(open(os.path.join(HERE, 'audio', 'align.json')))
WD = [(m.group(), V0 + A['character_start_times_seconds'][m.start()], V0 + A['character_end_times_seconds'][m.end() - 1])
      for m in re.finditer(r'\S+', TEXT)]
def wt(word, end=False, nth=0):
    hits = [w for w in WD if word.lower() in w[0].lower()]
    return hits[nth][2 if end else 1]

def col(ctx, c, a=1.0): ctx.set_source_rgba(c[0], c[1], c[2], a)
def rr(ctx, x, y, w, h, r):
    r = min(r, w / 2, h / 2)
    ctx.new_sub_path(); ctx.arc(x + w - r, y + r, r, -math.pi / 2, 0); ctx.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    ctx.arc(x + r, y + h - r, r, math.pi / 2, math.pi); ctx.arc(x + r, y + r, r, math.pi, 1.5 * math.pi); ctx.close_path()
def ell(ctx, x, y, rx, ry):
    ctx.save(); ctx.translate(x, y); ctx.scale(rx, ry); ctx.arc(0, 0, 1, 0, 2 * math.pi); ctx.restore()
def T(ctx, s, x, y, size, c, fam=F_BLACK, a=1.0, outline=0):
    font(ctx, fam, size); w = ctx.text_extents(s).x_advance
    ctx.move_to(x - w / 2, y); ctx.text_path(s)
    if outline: col(ctx, (0.05, 0.05, 0.1), a); ctx.set_line_width(outline); ctx.set_line_join(cairo.LINE_JOIN_ROUND); ctx.stroke_preserve()
    col(ctx, c, a); ctx.fill(); ctx.new_path()
def backpop(x):
    if x <= 0: return 0.0
    if x >= 1: return 1.0
    c1 = 1.8; return 1 + (c1 + 1) * (x - 1) ** 3 + c1 * (x - 1) ** 2

# ------------------------------------------------------------------ paleta (tonos pastel, luz de amanecer)
WALL = hexc('#9C93C9'); WALL2 = hexc('#8A80BB'); CAB = hexc('#E8E2D2'); WOOD = hexc('#8B5A3C'); WOOD2 = hexc('#74482F')
FLOOR = hexc('#6E5A6A'); FRIDGE = hexc('#F2F0EA'); PLANT = hexc('#5E8C61'); PLANT2 = hexc('#4A7550'); POT = hexc('#C97B4F')
SOFA = hexc('#5A6496'); HOOD = hexc('#2F4F8F'); HOOD2 = hexc('#24407A'); PANTS = hexc('#8A8C99'); SKIN = hexc('#14141C')
RIM = hexc('#FF9A4D'); AMBER = hexc('#FFB224'); INK = hexc('#F4F1EA'); RED = hexc('#FF4B3A')

# ------------------------------------------------------------------ personaje articulado
def rot(ang, v): return (v[0] * math.cos(ang) - v[1] * math.sin(ang), v[0] * math.sin(ang) + v[1] * math.cos(ang))
def add(a, b): return (a[0] + b[0], a[1] + b[1])

STAND = dict(lean=0, head=0, ls=.12, le=.15, rs=-.12, re=-.15, lh=.05, lk=0, rh=-.05, rk=0, crouch=0)
def pose(**kw):
    p = dict(STAND); p.update(kw); return p
def blend(p, q, k):
    return {key: lerp(p[key], q[key], k) for key in p}

def character(ctx, x, ground, s, P, face=1, eyes='normal', mouth='flat', blink=0.0, mug=None, t=0.0):
    """x,ground: pies. s: escala. face: 1 mira a la derecha, -1 izquierda. mug: None | 'hand'"""
    ctx.save(); ctx.translate(x, ground); ctx.scale(s * face, s)
    hip = (0, -250 + P['crouch'])
    def limb(o, a1, a2, l1, l2):
        k = add(o, rot(a1, (0, l1))); e = add(k, rot(a1 + a2, (0, l2))); return k, e
    lk, lf = limb(hip, P['lh'], P['lk'], 125, 125)
    rk_, rf = limb(hip, P['rh'], P['rk'], 125, 125)
    neck = add(hip, rot(P['lean'], (0, -175)))
    sh = add(neck, rot(P['lean'], (0, 22)))
    lel, lha = limb(sh, P['ls'] + P['lean'], P['le'], 95, 90)
    rel, rha = limb(sh, P['rs'] + P['lean'], P['re'], 95, 90)
    head = add(neck, rot(P['lean'] + P['head'], (0, -88)))
    ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    def line(pts, w, c, a=1.0):
        ctx.move_to(*pts[0])
        for q in pts[1:]: ctx.line_to(*q)
        ctx.set_line_width(w); col(ctx, c, a); ctx.stroke()
    # brazo y pierna del fondo (más oscuros)
    line([hip, rk_, rf], 36, mix(PANTS, (0, 0, 0), .25))
    col(ctx, SKIN); ell(ctx, rf[0] + 14, rf[1] + 6, 30, 14); ctx.fill()
    line([sh, rel, rha], 32, HOOD2)
    col(ctx, SKIN); ctx.arc(*rha, 17, 0, 2 * math.pi); ctx.fill()
    # luz de borde (contorno cálido) detrás del cuerpo
    line([hip, neck], 112, RIM, .9)
    line([hip, lk, lf], 42, RIM, .8)
    # pierna delantera
    line([hip, lk, lf], 36, PANTS)
    col(ctx, SKIN); ell(ctx, lf[0] + 14, lf[1] + 6, 30, 14); ctx.fill()
    # torso (sudadera) + capucha
    line([add(hip, (0, -6)), neck], 104, HOOD)
    col(ctx, HOOD2); ell(ctx, neck[0] - 18, neck[1] - 10, 62, 40); ctx.fill()
    # cordones y «?» en el pecho
    ctx.set_line_width(4); col(ctx, INK, .9)
    for dx in (-8, 12): ctx.move_to(neck[0] + dx, neck[1] + 10); ctx.line_to(neck[0] + dx + 2, neck[1] + 55); ctx.stroke()
    cx_, cy_ = lerp(hip[0], neck[0], .5) + 10, lerp(hip[1], neck[1], .5) + 10
    col(ctx, AMBER); ctx.save(); ctx.translate(cx_, cy_); ctx.scale(1 / 1, 1)
    font(ctx, F_BLACK, 54); ctx.move_to(-14, 18); ctx.text_path("?"); ctx.fill(); ctx.restore(); ctx.new_path()
    # cabeza
    hx, hy = head
    col(ctx, RIM, .9); ctx.arc(hx - 4, hy, 80, 0, 2 * math.pi); ctx.fill()
    col(ctx, SKIN); ctx.arc(hx, hy, 78, 0, 2 * math.pi); ctx.fill()
    col(ctx, (1, 1, 1), .07); ctx.arc(hx + 22, hy - 28, 30, 0, 2 * math.pi); ctx.fill()
    # ojos
    ex = hx + 34; ey = hy - 8
    sizes = {'normal': (15, 18), 'sleepy': (15, 18), 'wide': (24, 27), 'happy': (15, 18)}
    rx, ry = sizes.get(eyes, (15, 18))
    for i, ox in enumerate((-30, 6)):
        col(ctx, (1, 1, 1)); ell(ctx, ex + ox, ey, rx, ry * max(0.08, 1 - blink)); ctx.fill()
        if blink < .8:
            col(ctx, SKIN); pr = 9 if eyes != 'wide' else 7
            ctx.arc(ex + ox + (4 if eyes != 'wide' else 0), ey + (2 if eyes != 'wide' else 0), pr, 0, 2 * math.pi); ctx.fill()
        if eyes == 'sleepy':  # párpado caído
            col(ctx, SKIN); ctx.rectangle(ex + ox - rx - 2, ey - ry - 2, 2 * rx + 4, ry * 1.0); ctx.fill()
            col(ctx, (1, 1, 1), .5); ctx.set_line_width(3); ctx.move_to(ex + ox - rx, ey - ry * .02); ctx.line_to(ex + ox + rx, ey - ry * .02); ctx.stroke()
        if eyes == 'happy':
            col(ctx, SKIN); ell(ctx, ex + ox, ey + ry * .7, rx + 3, ry * .8); ctx.fill()
    # boca
    mx, my = hx + 40, hy + 36
    col(ctx, (1, 1, 1)); ctx.set_line_width(5)
    if mouth == 'o': ell(ctx, mx, my + 4, 13, 17); ctx.fill(); col(ctx, SKIN); ell(ctx, mx, my + 6, 7, 10); ctx.fill()
    elif mouth == 'smile': ctx.arc(mx, my - 8, 18, .4, math.pi - .4); ctx.stroke()
    elif mouth == 'yawn': ell(ctx, mx, my + 6, 16, 24); ctx.fill(); col(ctx, SKIN); ell(ctx, mx, my + 8, 10, 17); ctx.fill()
    else: ctx.move_to(mx - 12, my); ctx.line_to(mx + 12, my); ctx.stroke()
    # brazo delantero (encima del torso) + taza
    line([sh, lel, lha], 34, HOOD)
    if mug == 'hand':
        ctx.save(); ctx.translate(lha[0] + 8, lha[1] - 4)
        col(ctx, INK); rr(ctx, -26, -44, 52, 60, 8); ctx.fill()
        col(ctx, INK); ctx.set_line_width(8); ctx.arc(28, -16, 14, -1.2, 1.2); ctx.stroke()
        col(ctx, AMBER); ctx.rectangle(-26, -24, 52, 10); ctx.fill()
        for j in range(2):  # vapor
            col(ctx, (1, 1, 1), .45); ctx.set_line_width(5)
            ctx.move_to(-8 + j * 16, -52)
            for k in range(6): ctx.line_to(-8 + j * 16 + 8 * math.sin(t * 5 + k + j), -52 - k * 9)
            ctx.stroke()
        ctx.restore()
    col(ctx, SKIN); ctx.arc(*lha, 18, 0, 2 * math.pi); ctx.fill()
    ctx.restore()
    return {'hand': lha, 'head': head}

def walk_pose(ph, base=None):
    s = math.sin(ph); c = math.cos(ph)
    return pose(lh=.42 * s, lk=max(0, -.7 * c) * (1 if s < 0 else .3), rh=-.42 * s, rk=max(0, .7 * c) * (1 if s > 0 else .3),
                ls=-.45 * s + .1, le=.3, rs=.45 * s - .1, re=-.3, crouch=6 * abs(c), lean=.05)

# ------------------------------------------------------------------ fondos (pre-renderizados, nítidos y desenfocados)
def bg_kitchen(ctx, w):
    col(ctx, WALL); ctx.rectangle(0, 0, w, H); ctx.fill()
    col(ctx, WALL2); ctx.rectangle(0, 780, w, 60); ctx.fill()
    col(ctx, FLOOR); ctx.rectangle(0, 860, w, H - 860); ctx.fill()
    col(ctx, (0, 0, 0), .08)
    for x in range(0, w, 140): ctx.rectangle(x, 860, 3, H - 860); ctx.fill()
    # lámpara
    col(ctx, hexc('#3B3550')); ctx.rectangle(560, 0, 6, 120); ctx.fill()
    ctx.move_to(500, 170); ctx.line_to(626, 170); ctx.line_to(590, 115); ctx.line_to(536, 115); ctx.close_path(); ctx.fill()
    # armarios altos y ventana pequeña
    col(ctx, CAB); rr(ctx, 120, 90, 360, 200, 10); ctx.fill(); rr(ctx, 760, 90, 360, 200, 10); ctx.fill()
    col(ctx, (0, 0, 0), .08); ctx.rectangle(298, 100, 4, 180); ctx.fill(); ctx.rectangle(938, 100, 4, 180); ctx.fill()
    col(ctx, CAB); rr(ctx, 480, 300, 280, 230, 8); ctx.fill()
    g = cairo.LinearGradient(0, 315, 0, 515); g.add_color_stop_rgb(0, *hexc('#6F6AA8')); g.add_color_stop_rgb(1, *hexc('#F2B48A'))
    ctx.set_source(g); ctx.rectangle(495, 315, 250, 200); ctx.fill()
    # encimera
    col(ctx, CAB); rr(ctx, 60, 560, 1150, 34, 8); ctx.fill()
    col(ctx, WOOD); ctx.rectangle(80, 594, 1110, 266); ctx.fill()
    col(ctx, WOOD2)
    for x in (360, 640, 920): ctx.rectangle(x, 610, 4, 240); ctx.fill()
    for x in (260, 760):  # taburetes
        col(ctx, hexc('#6A4530')); rr(ctx, x - 70, 700, 140, 26, 13); ctx.fill(); ctx.rectangle(x - 6, 726, 12, 140); ctx.fill(); ctx.rectangle(x - 50, 860, 100, 8); ctx.fill()
    # nevera
    col(ctx, FRIDGE); rr(ctx, 1290, 190, 230, 670, 18); ctx.fill()
    col(ctx, (0, 0, 0), .1); ctx.rectangle(1290, 470, 230, 4); ctx.fill(); ctx.rectangle(1300, 300, 8, 120); ctx.fill(); ctx.rectangle(1300, 500, 8, 160); ctx.fill()
    # planta
    col(ctx, POT); ctx.move_to(1600, 860); ctx.line_to(1700, 860); ctx.line_to(1715, 770); ctx.line_to(1585, 770); ctx.close_path(); ctx.fill()
    for i in range(9):
        a = -math.pi / 2 + (i - 4) * .22; col(ctx, PLANT if i % 2 else PLANT2)
        ctx.save(); ctx.translate(1650, 775); ctx.rotate(a + math.pi / 2); ell(ctx, 0, -110, 26, 110); ctx.fill(); ctx.restore()
    # ventana grande (a la derecha) con cortinas
    wx = 1880; col(ctx, CAB); rr(ctx, wx, 140, 520, 600, 12); ctx.fill()
    g = cairo.LinearGradient(0, 160, 0, 720); g.add_color_stop_rgb(0, *hexc('#4D4A8F')); g.add_color_stop_rgb(1, *hexc('#E99A7A'))
    ctx.set_source(g); ctx.rectangle(wx + 20, 160, 480, 560); ctx.fill()
    r = random.Random(3)
    for i in range(9):
        bw = r.uniform(40, 70); bh = r.uniform(100, 260); bx = wx + 20 + i * 55
        col(ctx, hexc('#5E5490')); ctx.rectangle(bx, 720 - bh, bw, bh); ctx.fill()
    # sofá
    col(ctx, SOFA); rr(ctx, 2480, 640, 520, 160, 30); ctx.fill(); rr(ctx, 2480, 560, 520, 120, 30); ctx.fill()
    col(ctx, hexc('#4B5486')); ctx.rectangle(2500, 790, 20, 70); ctx.fill(); ctx.rectangle(2960, 790, 20, 70); ctx.fill()

_BG = {}
def bg_surface(key, w, blur=0):
    k = (key, w, blur)
    if k not in _BG:
        s = cairo.ImageSurface(cairo.FORMAT_RGB24, w, H); c = cairo.Context(s)
        {'kitchen': bg_kitchen}[key](c, w)
        if blur:
            s.write_to_png('/tmp/_bg.png'); im = Image.open('/tmp/_bg.png').filter(ImageFilter.GaussianBlur(blur)); im.save('/tmp/_bg.png')
            s = cairo.ImageSurface.create_from_png('/tmp/_bg.png')
        _BG[k] = s
    return _BG[k]

def curtains(ctx, wx, k):
    """cortinas sobre la ventana grande; k: 0 cerradas, 1 abiertas."""
    for side in (0, 1):
        w = lerp(250, 70, k)
        x = wx + 10 if side == 0 else wx + 510 - w
        col(ctx, hexc('#E8C98A')); ctx.rectangle(x, 130, w, 630); ctx.fill()
        col(ctx, (0, 0, 0), .08)
        for j in range(5): ctx.rectangle(x + (j + .5) * w / 5, 130, 3, 630); ctx.fill()
    col(ctx, hexc('#C9A86A')); ctx.rectangle(wx - 20, 120, 560, 16); ctx.fill()

# ------------------------------------------------------------------ escena exterior: el Sol sale por el oeste
def outside(ctx, t, t0, k_sun):
    q = clamp((t - t0) / 3.0)
    g = cairo.LinearGradient(0, 0, 0, H)
    g.add_color_stop_rgb(0, *mix(hexc('#3B3A7A'), hexc('#6C7BC4'), q)); g.add_color_stop_rgb(.65, *mix(hexc('#C97C8A'), hexc('#F7B98A'), q)); g.add_color_stop_rgb(1, *hexc('#FFD9A0'))
    ctx.set_source(g); ctx.paint()
    sx, sy = 430, lerp(820, 470, eout(k_sun))  # sol a la IZQUIERDA (oeste)
    rg = cairo.RadialGradient(sx, sy, 40, sx, sy, 520); rg.add_color_stop_rgba(0, 1, .85, .5, .85); rg.add_color_stop_rgba(1, 1, .6, .3, 0)
    ctx.set_source(rg); ctx.paint()
    col(ctx, hexc('#FFE08A')); ctx.arc(sx, sy, 120, 0, 2 * math.pi); ctx.fill()
    for i in range(12):  # rayos
        a = i * math.pi / 6 + t * .2; col(ctx, hexc('#FFE08A'), .35); ctx.set_line_width(10)
        ctx.move_to(sx + 150 * math.cos(a), sy + 150 * math.sin(a)); ctx.line_to(sx + 210 * math.cos(a), sy + 210 * math.sin(a)); ctx.stroke()
    r = random.Random(8)
    for layer, (c, base, hmin, hmax) in enumerate([(hexc('#8E7FB8'), 860, 120, 330), (hexc('#6A5C9A'), 930, 160, 420)]):
        x = -40
        while x < W + 40:
            bw = r.uniform(90, 180); bh = r.uniform(hmin, hmax)
            col(ctx, c); ctx.rectangle(x, base - bh, bw, bh + 300); ctx.fill()
            for wy in range(int(base - bh + 25), int(base - 20), 46):
                for wx in range(int(x + 14), int(x + bw - 22), 30):
                    if r.random() < .3: col(ctx, hexc('#FFD27A'), .7); ctx.rectangle(wx, wy, 12, 18); ctx.fill()
            x += bw + 6
    # veleta / brújula sobre un tejado señalando el oeste
    bx, by = 1080, 560
    col(ctx, hexc('#3B3550')); ctx.rectangle(bx - 5, by, 10, 160); ctx.fill()
    col(ctx, hexc('#3B3550')); ctx.set_line_width(8)
    ctx.move_to(bx - 90, by); ctx.line_to(bx + 90, by); ctx.stroke(); ctx.move_to(bx, by - 90); ctx.line_to(bx, by + 60); ctx.stroke()
    for s_, dx, dy in (("N", 0, -110), ("S", 0, 115), ("E", 115, 12), ("O", -118, 12)):
        T(ctx, s_, bx + dx, by + dy + 14, 44, AMBER if s_ == "O" else INK, F_BLACK, 1, outline=8)
    # marco de la ventana
    col(ctx, CAB); ctx.set_line_width(60); ctx.rectangle(0, 0, W, H); ctx.stroke()
    ctx.rectangle(W / 2 - 15, 0, 30, H); ctx.fill()

# ------------------------------------------------------------------ tarjeta final: empujar la Tierra
_GLOBE = None
def globe_mod():
    global _GLOBE
    if _GLOBE is None:
        import importlib.util as U
        sys.path.insert(0, '/home/claude/tierra')
        sp = U.spec_from_file_location('tsc', '/home/claude/tierra/scenes.py'); _GLOBE = U.module_from_spec(sp); sp.loader.exec_module(_GLOBE)
    return _GLOBE

# ------------------------------------------------------------------ guion de planos
T_CAFE = wt('café'); T_ABRES = wt('abres'); T_VENT_END = wt('ventana', True); T_SOL = wt('Sol'); T_OESTE = wt('oeste')
T_QUE = wt('¿Qué'); T_REVES = wt('revés', True)
S_WIN = T_VENT_END - .1        # corte a la ventana
S_FACE = T_OESTE + .55          # primer plano de sorpresa
S_END = T_QUE + 2.6             # tarjeta final

def shot_kitchen(ctx, t):
    # cámara: el ancho de la cocina es 3100 px; seguimos al personaje
    if t < T_ABRES - .1:
        px = 900; P = dict(STAND); eyes = 'sleepy'; mouth = 'flat'; mug = 'hand'
        if t < 2.6:   # bostezo y estiramiento
            k = math.sin(clamp((t - .4) / 2.0) * math.pi)
            P = blend(pose(ls=.25, le=1.6, rs=-.1, re=-.2), pose(ls=2.7, le=.3, rs=-2.7, re=-.3, lean=-.06, head=-.15), k)
            mouth = 'yawn' if k > .4 else 'flat'; mug = None
        else:         # sorbo de café
            k = math.sin(clamp((t - T_CAFE) / 1.2) * math.pi)
            P = blend(pose(ls=-.3, le=-1.4), pose(ls=-1.1, le=-1.9, head=.1), k); mouth = 'flat'
            if t > T_CAFE + .9: eyes = 'normal'; mouth = 'smile'
        cam_x = lerp(380, 460, t / (T_ABRES))
        zoom = lerp(1.0, 1.06, t / T_ABRES)
        walkph = None
    else:
        q = clamp((t - (T_ABRES - .1)) / (S_WIN - T_ABRES - .1))
        t_arrive = T_ABRES + 1.0
        if t < t_arrive:
            px = lerp(900, 1880 + 120, eout((t - T_ABRES + .1) / 1.1)); P = walk_pose(t * 11); walkph = True
        else:
            px = 2000; k = ease(clamp((t - t_arrive) / .5)); P = blend(walk_pose(t_arrive * 11), pose(ls=-2.4, le=-.3, rs=-2.0, re=-.4), k); walkph = False
        eyes = 'normal'; mouth = 'smile'; mug = 'hand' if t < t_arrive else None
        cam_x = lerp(460, px - 900, ease(clamp((t - T_ABRES) / 1.3))); zoom = 1.06
    ctx.save(); ctx.translate(W / 2, H / 2); ctx.scale(zoom, zoom); ctx.translate(-W / 2 - cam_x, -H / 2)
    ctx.set_source_surface(bg_surface('kitchen', 3100), 0, 0); ctx.paint()
    curtains(ctx, 1880, ease(clamp((t - (T_ABRES + 1.1)) / .7)))
    blink = 1.0 if (t % 3.1) < .12 else 0
    character(ctx, px, 870, 1.0, P, face=1, eyes=eyes, mouth=mouth, blink=blink, mug=mug, t=t)
    # sombra en el suelo
    ctx.restore()

def shot_window(ctx, t):
    outside(ctx, t, S_WIN, clamp((t - S_WIN) / 2.0))
    k = clamp((t - T_OESTE) / .25)
    if k > 0:
        s = backpop(k)
        ctx.save(); ctx.translate(430, 230); ctx.scale(s, s)
        col(ctx, RED); rr(ctx, -210, -70, 420, 130, 24); ctx.fill()
        T(ctx, "OESTE", 0, 32, 96, INK, F_BLACK); ctx.restore()
    # silueta del personaje de espaldas en primer plano (desenfocada por el tamaño)
    ctx.save(); ctx.translate(1540, 1280); ctx.scale(2.0, 2.0)
    col(ctx, HOOD2); rr(ctx, -110, -260, 220, 300, 80); ctx.fill()
    col(ctx, SKIN); ctx.arc(0, -330, 92, 0, 2 * math.pi); ctx.fill()
    col(ctx, RIM, .6); ctx.set_line_width(6); ctx.arc(0, -330, 92, math.pi * 1.0, math.pi * 1.6); ctx.stroke()
    ctx.restore()

def shot_face(ctx, t):
    q = t - S_FACE
    z = 1 + .04 * q
    ctx.save(); ctx.translate(W / 2, H / 2); ctx.scale(z, z); ctx.translate(-W / 2, -H / 2)
    ctx.save(); ctx.translate(-1500, -300); ctx.scale(1.4, 1.4)
    ctx.set_source_surface(bg_surface('kitchen', 3100, blur=16), 0, 0); ctx.paint(); ctx.restore()
    shake = 10 * math.exp(-q * 6) * math.sin(q * 60)
    P = pose(ls=-.4, le=-1.2, rs=.5, re=.4, head=-.05 + .03 * math.sin(q * 3))
    character(ctx, 900 + shake, 1900, 2.6, P, face=-1, eyes='wide', mouth='o', blink=0, mug=None, t=t)
    ctx.restore()
    # la taza cae
    mq = clamp((q - .25) / .7)
    if mq < 1:
        y = lerp(520, 1300, mq * mq); a = mq * 4
        ctx.save(); ctx.translate(1180, y); ctx.rotate(a); col(ctx, INK); rr(ctx, -40, -60, 80, 95, 10); ctx.fill()
        col(ctx, AMBER); ctx.rectangle(-40, -30, 80, 14); ctx.fill(); ctx.restore()
    k = clamp((q - .1) / .2)
    if k > 0:
        s = backpop(k); ctx.save(); ctx.translate(1350, 330); ctx.rotate(.12); ctx.scale(s, s)
        T(ctx, "?!", 0, 70, 230, AMBER, F_BLACK, 1, outline=18); ctx.restore()

def shot_end(ctx, t):
    q = t - S_END
    g = cairo.LinearGradient(0, 0, 0, H); g.add_color_stop_rgb(0, *hexc('#1B1E3A')); g.add_color_stop_rgb(1, *hexc('#2E2A55'))
    ctx.set_source(g); ctx.paint()
    r = random.Random(4)
    for _ in range(120): col(ctx, (1, 1, 1), r.uniform(.2, .8)); ctx.arc(r.uniform(0, W), r.uniform(0, H), r.uniform(1, 2.5), 0, 2 * math.pi); ctx.fill()
    G = globe_mod()
    push = ease(clamp((q - .6) / .8))
    spin = -(q * 25) * push + 10
    G.oglobe(ctx, 1150, 600, 330, spin, lat0=18)
    if push > 0: G.spin_arrow(ctx, 1150, 600, 330, -1, RED, 1, min(1, push * 1.4))
    # el personaje empuja la Tierra
    k = clamp(q / .5)
    P = blend(walk_pose(q * 8), pose(lean=.35, ls=-1.5, le=-.2, rs=-1.3, re=-.3, lh=.5, lk=.2, rh=-.4, rk=.1), ease(clamp((q - .4) / .4)))
    character(ctx, lerp(300, 640, eout(k)), 980, .95, P, face=1, eyes='normal' if q < 1.5 else 'happy', mouth='smile', t=t)
    kt = clamp((q - 1.0) / .4)
    if kt > 0:
        s = backpop(kt)
        ctx.save(); ctx.translate(W / 2, 140); ctx.scale(s, s)
        T(ctx, "¿Y SI LA TIERRA GIRARA AL REVÉS?", 0, 0, 84, INK, F_BLACK, 1, outline=14); ctx.restore()
    kl = clamp((q - 2.6) / .4)
    if kl > 0:
        col(ctx, AMBER, kl); ctx.arc(1330, 980, 46, 0, 2 * math.pi); ctx.fill()
        T(ctx, "?", 1330, 1004, 70, hexc('#14141C'), F_BLACK, kl)
        font(ctx, F_BLACK, 50); ctx.move_to(1395, 998); ctx.text_path("LA GRAN PREGUNTA"); col(ctx, INK, kl); ctx.fill(); ctx.new_path()

def frame(ctx, t):
    if t < S_WIN: shot_kitchen(ctx, t)
    elif t < S_FACE: shot_window(ctx, t)
    elif t < S_END: shot_face(ctx, t)
    else: shot_end(ctx, t)
    for cut in (S_WIN, S_FACE, S_END):  # pequeño destello en cada corte
        if 0 <= t - cut < .12: col(ctx, (1, 1, 1), .25 * (1 - (t - cut) / .12)); ctx.paint()
    g = cairo.RadialGradient(W / 2, H / 2, 500, W / 2, H / 2, 1250); g.add_color_stop_rgba(0, 0, 0, 0, 0); g.add_color_stop_rgba(1, 0, 0, 0, .35)
    ctx.set_source(g); ctx.paint()

# ------------------------------------------------------------------ sonido
SR = 48000
def place(buf, sig, t0, g=1.0):
    i = int(t0 * SR); m = min(len(sig), len(buf) - i)
    if 0 <= i < len(buf): buf[i:i + m] += g * sig[:m]
def audio():
    n = int(DUR * SR); tt = np.arange(n) / SR; rng = np.random.default_rng(1)
    mus = np.zeros(n); sfx = np.zeros(n)
    beat = 60 / 100
    def pluck(f, d=.5):
        m = int(d * SR); x = np.arange(m) / SR; return (np.sin(2 * np.pi * f * x) + .3 * np.sin(4 * np.pi * f * x)) * np.exp(-x * 6) * np.minimum(1, x / .004)
    notes = [523.3, 659.3, 784, 659.3, 587.3, 698.5, 880, 698.5]
    tb = 0; i = 0
    while tb < S_WIN - .2: place(mus, pluck(notes[i % 8]), tb, .12); tb += beat / 2; i += 1   # música alegre de mañana
    tb = S_END; i = 0
    while tb < DUR - .5: place(mus, pluck(notes[(i * 3) % 8] / 2, .7), tb, .14); tb += beat / 2; i += 1
    mus *= np.clip((DUR - tt) / 1.2, 0, 1)
    def whoosh(d=.35):
        m = int(d * SR); w = np.convolve(rng.standard_normal(m), np.ones(30) / 30, 'same'); return w * np.sin(np.pi * np.arange(m) / m) ** 2 * 2
    def step():
        m = int(.08 * SR); x = np.arange(m) / SR; return np.sin(2 * np.pi * 90 * x) * np.exp(-x * 40)
    def sting():  # acorde de sorpresa
        m = int(1.4 * SR); x = np.arange(m) / SR
        return sum(np.sin(2 * np.pi * f * x) for f in (311.1, 370, 466.2, 622.3)) * np.exp(-x * 2) * .25
    def crash():
        m = int(.6 * SR); x = np.zeros(m); idx = rng.integers(0, m // 3, 200); x[idx] = rng.uniform(-1, 1, 200)
        return np.convolve(x, np.ones(5) / 2, 'same') * np.exp(-np.arange(m) / SR * 5)
    def slide():
        m = int(.6 * SR); w = np.convolve(rng.standard_normal(m), np.ones(80) / 80, 'same'); return w * np.sin(np.pi * np.arange(m) / m) * 3
    def rumble():
        m = int(2.0 * SR); x = np.arange(m) / SR; return np.sin(2 * np.pi * np.cumsum(40 + 20 * x) / SR) * np.minimum(1, x / .5) * np.exp(-x * .8)
    for k_ in range(9): place(sfx, step(), T_ABRES + k_ * .14, .5)
    place(sfx, slide(), T_ABRES + 1.1, .4)
    for c in (S_WIN, S_FACE, S_END): place(sfx, whoosh(), c - .15, .5)
    place(sfx, sting(), T_OESTE, .9)
    place(sfx, crash(), S_FACE + .9, .9)
    place(sfx, rumble(), S_END + .6, .7)
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', os.path.join(HERE, 'audio', 'voz.mp3'), '-ac', '1', '-ar', str(SR), '-f', 'f32le', '/tmp/_v.raw'], check=True)
    v = np.fromfile('/tmp/_v.raw', np.float32).astype(np.float64); voice = np.zeros(n); place(voice, v, V0)
    env = np.convolve(np.abs(voice), np.ones(2400) / 2400, 'same'); duck = 1 - .5 * np.clip(env / .05, 0, 1)
    m_ = voice + mus * .5 * duck + sfx * .35; m_ /= np.abs(m_).max() / .95
    np.stack([m_, m_], 1).astype(np.float32).tofile('/tmp/_m.raw')
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', '/tmp/_m.raw', '-af', 'loudnorm=I=-14:TP=-1.5',
                    '-ar', str(SR), os.path.join(HERE, 'audio', 'mezcla.wav')], check=True)

def stills(ts):
    ims = []
    for t in ts:
        s = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H); c = cairo.Context(s); frame(c, t); s.write_to_png('/tmp/_s.png')
        ims.append(Image.open('/tmp/_s.png').resize((480, 270)))
    S = Image.new('RGB', (480 * 4, 270 * ((len(ims) + 3) // 4)))
    for i, im in enumerate(ims): S.paste(im, ((i % 4) * 480, (i // 4) * 270))
    S.save(os.path.join(HERE, 'sheet.jpg'))

def video():
    out = os.path.join(HERE, 'out', 'prueba_mascota_20s.mp4')
    enc = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgr0', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                            '-i', os.path.join(HERE, 'audio', 'mezcla.wav'), '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-preset', 'veryfast',
                            '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', out], stdin=subprocess.PIPE)
    s = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H); c = cairo.Context(s)
    for f in range(int(DUR * FPS)):
        frame(c, f / FPS); s.flush(); enc.stdin.write(bytes(s.get_data()))
    enc.stdin.close(); enc.wait(); print(out)

if __name__ == '__main__':
    m = sys.argv[1]
    if m == 'stills': stills([float(x) for x in sys.argv[2:]] or [.5, 2.0, 4.6, 5.8, 6.6, 7.6, 8.4, 9.3, 9.8, 10.6, 12.0, 13.4, 14.5, 16, 18, 19.5])
    elif m == 'audio': audio()
    elif m == 'video': video()
