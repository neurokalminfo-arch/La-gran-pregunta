"""Short 9:16: ¿Y si mañana estallara la Tercera Guerra Mundial?
Usage: python3 short2.py stills | render"""
import cairo, json, math, os, random, re, subprocess, sys, time
import lib
from lib import (col, hexc, text, label, rrect, glow, font, ease, eout, prog, lerp, mix, clamp, fmt_int,
                 Proj, draw_map, person, skyline, BG, INK, MUTED, DIM, RED, AMBER, GREEN, LINE, PANEL, GRIDC,
                 F_BLACK, F_XB, F_SEMI, F_MED, F_MONO)

SW, SH, FPS = 1080, 1920, 30
HERE = os.path.dirname(os.path.abspath(__file__))
AUD = os.path.join(HERE, 'audio', 'short2.mp3')
OUTD = os.path.join(HERE, 'out')
LEAD, TAIL = 0.15, 0.6
CY = 830          # vertical centre of the graphic band
CAP_Y = 1500      # captions baseline

def bg(ctx, t):
    col(ctx, BG); ctx.paint()
    ctx.set_line_width(1); col(ctx, GRIDC)
    for x in range(0, SW + 1, 90):
        ctx.move_to(x + .5, 0); ctx.line_to(x + .5, SH)
    for y in range(0, SH + 1, 90):
        ctx.move_to(0, y + .5); ctx.line_to(SW, y + .5)
    ctx.stroke()
    g = cairo.RadialGradient(SW / 2, CY, 200, SW / 2, CY, 1300)
    g.add_color_stop_rgba(0, 0, 0, 0, 0); g.add_color_stop_rgba(1, 0, 0, 0, .8)
    ctx.set_source(g); ctx.paint()

def T(ctx, s, x, y, size, c=INK, fam=F_BLACK, align='c', a=1.0, maxw=None, outline=0):
    if a <= 0: return
    font(ctx, fam, size)
    tw = ctx.text_extents(s).x_advance
    if maxw and tw > maxw:
        size *= maxw / tw; font(ctx, fam, size); tw = ctx.text_extents(s).x_advance
    x0 = x - tw / 2 if align == 'c' else x - tw if align == 'r' else x
    ctx.move_to(x0, y); ctx.text_path(s)
    if outline:
        col(ctx, (0, 0, 0), a); ctx.set_line_width(outline); ctx.set_line_join(cairo.LINE_JOIN_ROUND); ctx.stroke_preserve()
    col(ctx, c, a); ctx.fill()

def shake(t, amp, freq=40):
    return amp * math.sin(t * freq) , amp * math.cos(t * freq * 1.3)

# ------------------------------------------------------------------ icons
def phone(ctx, x, y, w, h, a=1.0, screen=None):
    col(ctx, hexc('#2A2F38'), a); rrect(ctx, x - w / 2, y - h / 2, w, h, w * .14); ctx.fill()
    col(ctx, screen or hexc('#0E1116'), a); rrect(ctx, x - w / 2 + 14, y - h / 2 + 14, w - 28, h - 28, w * .11); ctx.fill()
    col(ctx, (0, 0, 0), a); rrect(ctx, x - w * .14, y - h / 2 + 26, w * .28, 22, 11); ctx.fill()

def pump(ctx, x, y, s, a=1.0, c=RED):
    col(ctx, c, a); rrect(ctx, x - s * .32, y - s * .5, s * .5, s, s * .06); ctx.fill()
    col(ctx, BG, a); rrect(ctx, x - s * .25, y - s * .4, s * .36, s * .26, s * .03); ctx.fill()
    col(ctx, c, a); ctx.set_line_width(s * .05)
    ctx.move_to(x + s * .18, y - s * .25); ctx.line_to(x + s * .34, y - s * .25); ctx.line_to(x + s * .34, y + s * .2)
    ctx.line_to(x + s * .26, y + s * .2); ctx.stroke()
    rrect(ctx, x - s * .4, y + s * .48, s * .66, s * .08, 6); ctx.fill()

def chip(ctx, x, y, s, a=1.0, c=AMBER):
    col(ctx, c, a); ctx.set_line_width(s * .05)
    for i in range(5):
        o = -s * .32 + i * s * .16
        for (x1, y1, x2, y2) in ((x + o, y - s * .5, x + o, y - s * .35), (x + o, y + s * .35, x + o, y + s * .5),
                                 (x - s * .5, y + o, x - s * .35, y + o), (x + s * .35, y + o, x + s * .5, y + o)):
            ctx.move_to(x1, y1); ctx.line_to(x2, y2)
    ctx.stroke()
    rrect(ctx, x - s * .36, y - s * .36, s * .72, s * .72, s * .08); ctx.fill()
    col(ctx, BG, a); rrect(ctx, x - s * .2, y - s * .2, s * .4, s * .4, s * .04); ctx.fill()

def tanker(ctx, x, y, s, a=1.0):
    col(ctx, INK, a)
    ctx.move_to(x - s, y); ctx.line_to(x + s * .8, y); ctx.line_to(x + s, y - s * .25); ctx.line_to(x - s, y - s * .25)
    ctx.close_path(); ctx.fill()
    rrect(ctx, x - s * .9, y - s * .5, s * .3, s * .26, 3); ctx.fill()

# ------------------------------------------------------------------ scenes
def s_alarm(ctx, t, d):
    p = t / d
    fl = (math.sin(t * 14) + 1) / 2
    col(ctx, RED, .10 + .18 * fl); ctx.paint()
    T(ctx, "06:00", SW / 2, 420, 200, INK, F_BLACK, a=ease(prog(t, 0, .25)))
    dx, dy = shake(t, 9 * (1 - prog(p, .7, 1)))
    phone(ctx, SW / 2 + dx, CY + 160 + dy, 430, 760)
    # emergency banner
    k = eout(prog(t, .35, .7))
    bx, by = SW / 2 - 185 + dx, CY - 120 + dy - 60 * (1 - k)
    col(ctx, hexc('#F3F1EC'), k); rrect(ctx, bx, by, 370, 300, 26); ctx.fill()
    col(ctx, RED, k); ctx.arc(bx + 50, by + 50, 22, 0, 2 * math.pi); ctx.fill()
    T(ctx, "!", bx + 50, by + 63, 36, INK, F_BLACK, a=k)
    T(ctx, "ALERTA", bx + 88, by + 64, 34, RED, F_BLACK, 'l', k)
    for i, ln in enumerate(["Ha comenzado la", "TERCERA GUERRA", "MUNDIAL"]):
        T(ctx, ln, bx + 30, by + 140 + i * 52, 40 if i else 32, hexc('#111317'), F_BLACK if i else F_SEMI, 'l', k, maxw=310)
    for r in range(3):
        rp = ((t * 1.6 + r / 3) % 1)
        col(ctx, RED, (1 - rp) * .6); ctx.set_line_width(5)
        ctx.arc(SW / 2 + dx, CY + 160 + dy, 260 + 300 * rp, 0, 2 * math.pi); ctx.stroke()

def s_twist(ctx, t, d):
    p = t / d
    T(ctx, "LO PRIMERO", SW / 2, 420, 120, INK, a=ease(prog(p, 0, .15)))
    T(ctx, "NO ES UNA BOMBA", SW / 2, 540, 96, INK, a=ease(prog(p, .05, .2)), maxw=980)
    k = eout(prog(p, .7, .82))
    if k > 0:
        sc = 1 + .25 * (1 - k)
        ctx.save(); ctx.translate(SW / 2, CY + 120); ctx.scale(sc * .8, sc * .8)
        glow(ctx, 0, 0, 360, RED, .35 * k)
        pump(ctx, 0, 0, 440, k)
        ctx.restore()
        T(ctx, "ES LA GASOLINERA", SW / 2, CY + 440, 84, RED, a=k, maxw=980)

def s_hormuz(ctx, t, d):
    p = t / d
    P = Proj(46, 62, 21, 31, 40, 330, SW - 80, 760)
    ctx.save(); ctx.rectangle(0, 260, SW, 1060); ctx.clip()
    draw_map(ctx, P, base=hexc('#1E2530'), edge=hexc('#3A4452'), edge_w=1.5)
    ctx.restore()
    sx, sy = P(56.4, 26.5)
    k = ease(prog(p, .05, .3))
    col(ctx, AMBER, k); ctx.set_line_width(4); ctx.arc(sx, sy, 70, 0, 2 * math.pi); ctx.stroke()
    T(ctx, "ORMUZ", sx + 90, sy - 30, 52, AMBER, F_BLACK, 'l', k)
    label(ctx, "≈ 30 km", sx + 92, sy + 16, k, INK, 26, 'l')
    closed = prog(p, .62, .72)
    for i in range(10):
        u = ((t * .18 + i / 10) % 1)
        x = lerp(P(51, 27.2)[0], P(60, 24.5)[0], u); y = lerp(P(51, 27.2)[1], P(60, 24.5)[1], u)
        if closed > 0 and x > sx - 30: continue
        tanker(ctx, x, y, 22, .9)
    if closed > 0:
        col(ctx, RED, closed); ctx.set_line_width(16); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.move_to(sx - 55, sy - 55); ctx.line_to(sx + 55, sy + 55); ctx.move_to(sx + 55, sy - 55); ctx.line_to(sx - 55, sy + 55)
        ctx.stroke(); ctx.set_line_cap(cairo.LINE_CAP_BUTT)
    T(ctx, "1/5", 140, 300, 170, INK, F_BLACK, 'l', ease(prog(p, .2, .35)))
    label(ctx, "del petróleo que consume el mundo", 145, 345, ease(prog(p, .25, .4)), MUTED, 26, 'l')
    # price gauge
    g = ease(prog(p, .7, .95))
    if g > 0:
        x0, y0 = 140, 1180
        col(ctx, PANEL); rrect(ctx, x0, y0, 800, 90, 45); ctx.fill()
        col(ctx, mix(AMBER, RED, g)); rrect(ctx, x0, y0, 800 * (.25 + .75 * g), 90, 45); ctx.fill()
        T(ctx, "PRECIO", x0 + 30, y0 + 62, 44, BG, F_BLACK, 'l')
        T(ctx, "↑", x0 + 800 * (.25 + .75 * g) - 50, y0 + 70, 70, INK, F_BLACK)
    lib.text(ctx, "Fuente: EIA", SW - 40, 1300, 20, MUTED, F_MED, 'r', ease(prog(p, .2, .4)))

def s_chips(ctx, t, d):
    p = t / d
    k = ease(prog(p, 0, .2))
    T(ctx, "SEGUNDO GOLPE", SW / 2, 360, 54, AMBER, F_BLACK, a=k)
    T(ctx, "tu móvil", SW / 2, 470, 110, INK, a=k)
    dark = ease(prog(p, .55, .8))
    scr = mix(hexc('#2B6CB0'), hexc('#0E1116'), dark)
    phone(ctx, 330, CY + 170, 330, 600, 1, scr)
    if dark > .5:
        T(ctx, "SIN", 330, CY + 150, 64, RED, a=dark); T(ctx, "STOCK", 330, CY + 220, 64, RED, a=dark)
    else:
        for i in range(3):
            for j in range(4):
                col(ctx, INK, .55 * (1 - dark)); rrect(ctx, 220 + i * 80, CY - 40 + j * 90, 56, 56, 14); ctx.fill()
    ck = eout(prog(p, .2, .4))
    ctx.save(); ctx.translate(780, CY + 30); ctx.scale(max(ck, 1e-3), max(ck, 1e-3)); chip(ctx, 0, 0, 260); ctx.restore()
    T(ctx, "≈80 %", 780, CY + 300, 110, AMBER, a=ck)
    label(ctx, "de los chips más avanzados", 780, CY + 350, ck, INK, 24)
    label(ctx, "se fabrican en Taiwán", 780, CY + 390, ck, INK, 24)
    lib.text(ctx, "Fuente: TrendForce", SW - 40, 1300, 20, MUTED, F_MED, 'r', ck)

def s_bill(ctx, t, d):
    p = t / d
    T(ctx, "¿Y LA FACTURA?", SW / 2, 380, 96, INK, a=ease(prog(p, 0, .15)), maxw=980)
    k = eout(prog(p, .12, .35))
    h = 720 * k
    col(ctx, hexc('#F3F1EC')); ctx.move_to(240, 470); ctx.line_to(840, 470); ctx.line_to(840, 470 + h)
    for i in range(12):
        ctx.line_to(840 - (i + .5) * 50, 470 + h + (18 if i % 2 == 0 else 0))
    ctx.line_to(240, 470 + h); ctx.close_path(); ctx.fill()
    if k > .3:
        a = ease(prog(k, .3, 1))
        label(ctx, "Guerra EE. UU. – China", SW / 2, 560, a, hexc('#555B66'), 24)
        label(ctx, "por Taiwán · primer año", SW / 2, 600, a, hexc('#555B66'), 24)
        v = 10.6 * eout(prog(p, .3, .6))
        T(ctx, f"{v:.1f}".replace('.', ','), SW / 2, 790, 190, hexc('#111317'), a=a)
        T(ctx, "BILLONES $", SW / 2, 880, 64, RED, a=a)
    for i, s in enumerate(["> PANDEMIA", "> CRISIS 2008"]):
        sk = eout(prog(p, .62 + i * .12, .72 + i * .12))
        if sk > 0:
            ctx.save(); ctx.translate(SW / 2, 990 + i * 110); ctx.rotate(-.06); ctx.scale(1.4 - .4 * sk, 1.4 - .4 * sk)
            col(ctx, RED, sk); ctx.set_line_width(6); rrect(ctx, -270, -60, 540, 92, 10); ctx.stroke()
            T(ctx, s, 0, 6, 58, RED, a=sk); ctx.restore()
    lib.text(ctx, "Fuente: Bloomberg Economics", SW - 40, 1300, 20, MUTED, F_MED, 'r', k)

def s_city(ctx, t, d):
    p = t / d
    g = cairo.LinearGradient(0, 300, 0, 1250)
    g.add_color_stop_rgba(0, .1, .13, .2, 0); g.add_color_stop_rgba(1, .1, .13, .2, 1)
    ctx.set_source(g); ctx.rectangle(0, 300, SW, 950); ctx.fill()
    ctx.save(); ctx.rectangle(0, 0, SW, 1260); ctx.clip()
    lib.W = SW
    skyline(ctx, 1250, 1, seed=4, lit=.7, x0=0, x1=SW)
    lib.W = 1920
    ctx.restore()
    T(ctx, "SIN UN SOLO", SW / 2, 470, 96, INK, a=ease(prog(p, 0, .2)))
    T(ctx, "DISPARO", SW / 2, 580, 120, INK, a=ease(prog(p, .05, .25)))
    T(ctx, "…ya la estarías pagando", SW / 2, 760, 64, AMBER, F_XB, a=ease(prog(p, .5, .7)), maxw=980)

def s_cta(ctx, t, d):
    p = t / d
    T(ctx, "¿Qué se agotaría", SW / 2, 400, 92, INK, a=ease(prog(p, 0, .15)), maxw=1000)
    T(ctx, "primero?", SW / 2, 510, 110, AMBER, a=ease(prog(p, .05, .2)))
    opts = [("Gasolina", pump), ("Móviles", None), ("Comida", None)]
    for i, (lb, _) in enumerate(opts):
        k = eout(prog(p, .15 + i * .08, .3 + i * .08))
        y = 650 + i * 170
        col(ctx, PANEL, k); rrect(ctx, 190, y, 700, 130, 30); ctx.fill()
        col(ctx, LINE, k); ctx.set_line_width(3); rrect(ctx, 190, y, 700, 130, 30); ctx.stroke()
        T(ctx, ["A", "B", "C"][i], 260, y + 88, 60, AMBER, a=k)
        T(ctx, lb, 330, y + 88, 64, INK, F_XB, 'l', k)
    k = ease(prog(p, .55, .7))
    col(ctx, RED, k); rrect(ctx, SW / 2 - 260, 1170, 520, 110, 55); ctx.fill()
    T(ctx, "SÍGUENOS", SW / 2, 1245, 56, INK, a=k)

SCENES = [
    (s_alarm, "Seis de la mañana. Todos los móviles suenan a la vez: ha empezado la Tercera Guerra Mundial."),
    (s_twist, "Y lo primero que te va a destrozar no es una bomba... es la gasolinera."),
    (s_hormuz, "Por un estrecho de apenas treinta kilómetros, Ormuz, pasa una quinta parte del petróleo que consume el planeta. Si se cierra, el precio se dispara en horas."),
    (s_chips, "Segundo golpe: tu móvil. Alrededor del ochenta por ciento de los chips más avanzados se fabrican en Taiwán. Sin ellos, no hay móviles, ni coches, ni ordenadores nuevos."),
    (s_bill, "¿Y la factura? Una guerra entre Estados Unidos y China por Taiwán costaría más de diez billones de dólares el primer año. Más que la pandemia. Más que la crisis de 2008."),
    (s_city, "Así que, sin un solo disparo en tu ciudad... ya la estarías pagando."),
    (s_cta, "¿Qué crees que se agotaría primero? Te leo en comentarios. Y síguenos para más grandes preguntas."),
]
NARRATION = ' '.join(s for _, s in SCENES)

# ------------------------------------------------------------------ timing
def adur():
    return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', AUD],
                                capture_output=True, text=True).stdout)

def silences():
    o = subprocess.run(['ffmpeg', '-i', AUD, '-af', 'silencedetect=noise=-35dB:d=0.2', '-f', 'null', '-'],
                       capture_output=True, text=True).stderr
    st = [float(x) for x in re.findall(r'silence_start: ([\d.]+)', o)]
    en = [float(x) for x in re.findall(r'silence_end: ([\d.]+)', o)]
    return [(a + b) / 2 for a, b in zip(st, en)]

def align(pieces, A, sil):
    tot = sum(len(s) for s in pieces)
    cuts, acc = [0.0], 0
    for s in pieces[:-1]:
        acc += len(s); g = A * acc / tot
        cand = [x for x in sil if x > cuts[-1] + .3]
        b = min(cand, key=lambda x: abs(x - g)) if cand else g
        cuts.append(b if abs(b - g) < 1.5 else max(g, cuts[-1] + .3))
    cuts.append(A)
    return cuts

def timeline():
    if os.path.exists(AUD):
        A, sil = adur(), silences()
    else:
        A, sil = len(NARRATION) / 16.0, []
    sc = align([s for _, s in SCENES], A, sil)
    lay = [(fn, (LEAD + sc[i]) if i else 0.0, (LEAD + sc[i + 1]) if i < len(SCENES) - 1 else A + LEAD + TAIL)
           for i, (fn, _) in enumerate(SCENES)]
    lay = [(fn, s, e - s) for fn, s, e in lay]
    # captions: chunks of ~3-5 words, timed by chars inside each scene
    caps = []
    for i, (_, s) in enumerate(SCENES):
        words = s.split(); chunks, cur = [], []
        for w in words:
            cur.append(w)
            if len(' '.join(cur)) > 16 or re.search(r'[.?!:,]$|\.\.\.$', w):
                chunks.append(' '.join(cur)); cur = []
        if cur: chunks.append(' '.join(cur))
        a0, a1 = LEAD + sc[i], LEAD + sc[i + 1]
        sub = align(chunks, a1 - a0, [x - (a0 - LEAD) for x in sil if a0 - LEAD < x < a1 - LEAD])
        for j, c in enumerate(chunks):
            caps.append((a0 + sub[j], a0 + sub[j + 1], c))
    return lay, caps, A + LEAD + TAIL

HL = re.compile(r'(guerra|bomba|gasolinera|petróleo|móvil|chips|taiwán|billones|factura|pagando|ormuz|cierra|dispara|comentarios|síguenos)', re.I)

def draw(ctx, lay, caps, tb, D):
    bg(ctx, tb)
    for i, (fn, s, d) in enumerate(lay):
        if s <= tb < s + d or (i == len(lay) - 1 and tb >= s):
            t = tb - s
            a = 1.0 if i == 0 else min(1.0, t / .18)
            ctx.push_group(); fn(ctx, t, d); ctx.pop_group_to_source(); ctx.paint_with_alpha(a)
            break
    # brand
    label(ctx, "La Gran Pregunta", SW / 2, 160, 1, AMBER, 28)
    # caption
    for a, b, c in caps:
        if a <= tb < b:
            k = eout(prog(tb, a, a + .12)); sc = .85 + .15 * k
            hl = bool(HL.search(c))
            ctx.save(); ctx.translate(SW / 2, CAP_Y); ctx.scale(sc, sc)
            T(ctx, c.upper(), 0, 0, 84, AMBER if hl else INK, F_BLACK, a=k, maxw=980, outline=14)
            ctx.restore()
            break
    col(ctx, AMBER); ctx.rectangle(0, SH - 10, SW * tb / D, 10); ctx.fill()

def stills():
    lay, caps, D = timeline()
    os.makedirs(os.path.join(HERE, 'stills2'), exist_ok=True)
    for i, (fn, s, d) in enumerate(lay):
        surf = cairo.ImageSurface(cairo.FORMAT_RGB24, SW, SH); ctx = cairo.Context(surf)
        draw(ctx, lay, caps, s + d * .85, D)
        surf.write_to_png(os.path.join(HERE, 'stills2', f'{i}_{fn.__name__}.png'))
    print('D', D, 'caps', len(caps))

def sfx(D):
    """Alarm beeps at the start + low impact at the twist. Returns wav path."""
    lay, _, _ = timeline()
    twist = lay[1][1] + lay[1][2] * .58
    out = os.path.join(HERE, 'sfx2.wav')
    beeps = '+'.join(f"between(t,{i*0.22:.2f},{i*0.22+0.12:.2f})" for i in range(8))
    expr = (f"0.22*sin(2*PI*1180*t)*({beeps})"
            f"+0.55*sin(2*PI*(55-25*(t-{twist:.2f}))*(t-{twist:.2f}))*exp(-3*(t-{twist:.2f}))*gte(t,{twist:.2f})")
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'lavfi', '-i',
                    f"aevalsrc='{expr}':s=48000:d={D:.2f}", '-ac', '2', out], check=True)
    return out

def render():
    lay, caps, D = timeline()
    n = int(round(D * FPS))
    fx = sfx(D)
    os.makedirs(OUTD, exist_ok=True)
    out = os.path.join(OUTD, 'short_tercera_guerra_mundial_9x16.mp4'); tmp = out[:-4] + '.part.mp4'
    enc = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgr0', '-s', f'{SW}x{SH}',
                            '-r', str(FPS), '-i', '-', '-i', AUD, '-i', fx, '-filter_complex',
                            f"[1:a]aresample=48000,adelay={int(LEAD*1000)}|{int(LEAD*1000)},apad[v];[2:a]volume=0.8[f];"
                            f"[v][f]amix=inputs=2:normalize=0,loudnorm=I=-14:TP=-1.5[a]",
                            '-map', '0:v', '-map', '[a]', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18',
                            '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-t', f'{D:.3f}', '-movflags', '+faststart', tmp],
                           stdin=subprocess.PIPE)
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, SW, SH); ctx = cairo.Context(surf)
    t0 = time.time()
    for f in range(n):
        draw(ctx, lay, caps, f / FPS, D); surf.flush(); enc.stdin.write(bytes(surf.get_data()))
    enc.stdin.close()
    if enc.wait() == 0: os.replace(tmp, out)
    print('render', round(D, 1), 's in', round(time.time() - t0), 's')

if __name__ == '__main__':
    {'stills': stills, 'render': render}[sys.argv[1]]()
