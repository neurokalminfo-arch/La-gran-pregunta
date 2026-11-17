"""YouTube thumbnails (drawn at 1920x1080, saved at 1280x720)."""
import cairo, math, random, os
from lib import *
from PIL import Image

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out')

def stroke_text(ctx, s, x, y, size, c, fam=F_BLACK, align='l', outline=10, track=0, maxw=None):
    font(ctx, fam, size)
    tw = ctx.text_extents(s).x_advance
    if maxw and tw > maxw:
        size *= maxw / tw; font(ctx, fam, size); tw = ctx.text_extents(s).x_advance
    x0 = x - tw / 2 if align == 'c' else x - tw if align == 'r' else x
    ctx.move_to(x0, y); ctx.text_path(s)
    col(ctx, (0, 0, 0), 0.9); ctx.set_line_width(outline); ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.stroke_preserve(); col(ctx, c); ctx.fill()
    return tw

def mushroom(ctx, x, y, s, c, a):
    col(ctx, c, a)
    rrect(ctx, x - s * .09, y - s * .55, s * .18, s * .6, s * .05); ctx.fill()
    for dx, dy, r in [(-.22, -.62, .2), (.22, -.62, .2), (0, -.72, .26), (-.1, -.85, .2), (.12, -.84, .2), (0, -.55, .18)]:
        ctx.arc(x + dx * s, y + dy * s, r * s, 0, 2 * math.pi); ctx.fill()
    ctx.save(); ctx.translate(x, y); ctx.scale(1, .25); ctx.arc(0, 0, s * .45, 0, 2 * math.pi); ctx.restore(); ctx.fill()

def thumb_a(ctx):
    """Empty supermarket aisle, nuclear glow at the far window. Text: LO PEOR NO SON LAS BOMBAS."""
    vx, vy = 470, 470
    col(ctx, hexc('#0B0D11')); ctx.paint()
    # far wall window with orange sky + mushroom cloud
    wx0, wy0, wx1, wy1 = vx - 150, vy - 170, vx + 150, vy + 40
    g = cairo.LinearGradient(0, wy0, 0, wy1)
    g.add_color_stop_rgb(0, .35, .12, .06); g.add_color_stop_rgb(1, 1, .55, .2)
    ctx.set_source(g); ctx.rectangle(wx0, wy0, wx1 - wx0, wy1 - wy0); ctx.fill()
    glow(ctx, vx, wy1 - 20, 420, AMBER, .55)
    mushroom(ctx, vx + 20, wy1, 150, (.15, .06, .04), .9)
    col(ctx, (0, 0, 0)); ctx.set_line_width(8); ctx.rectangle(wx0, wy0, wx1 - wx0, wy1 - wy0); ctx.stroke()
    # floor & ceiling planes
    col(ctx, hexc('#14171D')); ctx.move_to(0, H); ctx.line_to(wx0 - 40, wy1 + 40); ctx.line_to(wx1 + 40, wy1 + 40); ctx.line_to(1120, H); ctx.close_path(); ctx.fill()
    # floor reflection of glow
    fg = cairo.RadialGradient(vx, wy1 + 60, 10, vx, wy1 + 60, 420)
    fg.add_color_stop_rgba(0, 1, .55, .2, .35); fg.add_color_stop_rgba(1, 1, .55, .2, 0)
    ctx.set_source(fg); ctx.move_to(0, H); ctx.line_to(wx0 - 40, wy1 + 40); ctx.line_to(wx1 + 40, wy1 + 40); ctx.line_to(1120, H); ctx.close_path(); ctx.fill()
    # shelving units (left & right) as perspective quads with empty shelves
    def shelf_side(xn, xf, top_n, top_f, bot_n, bot_f, side):
        col(ctx, hexc('#1C212A'))
        ctx.move_to(xn, top_n); ctx.line_to(xf, top_f); ctx.line_to(xf, bot_f); ctx.line_to(xn, bot_n); ctx.close_path(); ctx.fill()
        for k in range(1, 6):
            u = k / 6
            yn = lerp(top_n, bot_n, u); yf = lerp(top_f, bot_f, u)
            col(ctx, hexc('#7F8794')); ctx.set_line_width(10)
            ctx.move_to(xn, yn); ctx.line_to(xf, yf); ctx.stroke()
            col(ctx, hexc('#C9CED6'), .25); ctx.set_line_width(3)
            ctx.move_to(xn, yn - 6); ctx.line_to(xf, yf - 2); ctx.stroke()
        # price tags, nothing on shelves
        rnd = random.Random(side)
        for k in range(1, 6):
            u = k / 6
            for j in range(4):
                v = .1 + j * .22 + rnd.uniform(-.03, .03)
                x = lerp(xn, xf, v); yn = lerp(top_n, bot_n, u); yf = lerp(top_f, bot_f, u)
                y = lerp(yn, yf, v); s = lerp(1, .25, v)
                col(ctx, AMBER, .85); ctx.rectangle(x - 14 * s, y + 4, 28 * s, 16 * s); ctx.fill()
        # one lone can on left side
    shelf_side(-40, wx0 - 40, 60, wy0 - 10, H + 40, wy1 + 40, 1)
    shelf_side(1000, wx1 + 40, 60, wy0 - 10, H + 40, wy1 + 40, 2)
    # ceiling lights
    for k in range(4):
        u = k / 4
        y = lerp(30, wy0 - 30, u ** .7); w = lerp(380, 60, u ** .7); x = vx
        col(ctx, hexc('#DDE6F0'), .85 - .5 * u); rrect(ctx, x - w / 2, y, w, lerp(18, 5, u), 6); ctx.fill()
    # vignette right for text panel
    g = cairo.LinearGradient(760, 0, 1060, 0)
    g.add_color_stop_rgba(0, 0.03, 0.035, 0.045, 0); g.add_color_stop_rgba(1, 0.03, 0.035, 0.045, 1)
    ctx.set_source(g); ctx.rectangle(760, 0, W - 760, H); ctx.fill()
    col(ctx, (0.03, 0.035, 0.045)); ctx.rectangle(1060, 0, W - 1060, H); ctx.fill()
    # text
    stroke_text(ctx, "¿Y SI MAÑANA", 960, 300, 200, INK, outline=14, maxw=900)
    stroke_text(ctx, "EXPLOTA UNA", 960, 500, 200, INK, outline=14, maxw=900)
    stroke_text(ctx, "BOMBA", 960, 710, 210, RED, outline=14, maxw=900)
    stroke_text(ctx, "ATÓMICA?", 960, 910, 210, RED, outline=14, maxw=900)

def thumb_b(ctx):
    """Scale contrast: tiny bar 90 M (bombs) vs huge bar 5.000 M (hunger)."""
    background(ctx, grid=False)
    base = 960
    col(ctx, INK); ctx.rectangle(200, base - 26, 300, 26); ctx.fill()
    stroke_text(ctx, "90 M", 350, base - 70, 130, INK, align='c')
    mushroom(ctx, 350, base - 230, 190, MUTED, .9)
    col(ctx, RED); ctx.rectangle(640, 300, 420, base - 300); ctx.fill()
    plate(ctx, 850, 220, 170, 1, .1)
    stroke_text(ctx, "5.000 M", 850, 660, 150, INK, align='c', outline=12, maxw=400)
    stroke_text(ctx, "¿QUÉ ES", 1150, 470, 190, INK, outline=12, maxw=700)
    stroke_text(ctx, "PEOR?", 1150, 690, 230, AMBER, outline=12, maxw=700)

def thumb_c(ctx):
    """Earth half swallowed by black smoke, wheat dying."""
    col(ctx, hexc('#07080B')); ctx.paint()
    rnd = random.Random(3)
    for i in range(160):
        col(ctx, INK, rnd.uniform(.2, .7)); ctx.arc(rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(1, 2.5), 0, 2 * math.pi); ctx.fill()
    gx, gy, r = 560, 560, 430
    glow(ctx, gx, gy, r * 1.35, hexc('#5AA9FF'), .25)
    globe(ctx, gx, gy, r, 1, 0, 0)
    ctx.save(); ctx.arc(gx, gy, r + 2, 0, 2 * math.pi); ctx.clip()
    for i in range(120):
        x = rnd.uniform(gx - r, gx + r); y = gy - r + rnd.uniform(0, r * 1.15) * rnd.random() ** .5
        rr = rnd.uniform(60, 160)
        g = cairo.RadialGradient(x, y, 0, x, y, rr)
        g.add_color_stop_rgba(0, .05, .05, .06, .85); g.add_color_stop_rgba(1, .05, .05, .06, 0)
        ctx.set_source(g); ctx.arc(x, y, rr, 0, 2 * math.pi); ctx.fill()
    ctx.restore()
    stroke_text(ctx, "SIN SOL.", 1120, 450, 200, INK, outline=12, maxw=740)
    stroke_text(ctx, "SIN COMIDA.", 1120, 640, 200, AMBER, outline=12, maxw=740)
    for i in range(4):
        wheat(ctx, 1200 + i * 90, 940, 200 - i * 25, mix(AMBER, DIM, .3 + i * .2), 1)

def save(fn, name):
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H); ctx = cairo.Context(surf)
    fn(ctx)
    p = os.path.join(OUT, name + '_1920.png'); surf.write_to_png(p)
    im = Image.open(p).convert('RGB').resize((1280, 720), Image.LANCZOS)
    im.save(os.path.join(OUT, name + '.png'), optimize=True)
    os.remove(p)

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    save(thumb_a, 'miniatura_A_principal')
    save(thumb_b, 'miniatura_B_alternativa')
    save(thumb_c, 'miniatura_C_alternativa')
    # small-size readability check (as seen in the YouTube feed)
    ims = [Image.open(os.path.join(OUT, n + '.png')) for n in ('miniatura_A_principal', 'miniatura_B_alternativa', 'miniatura_C_alternativa')]
    S = Image.new('RGB', (1280 + 20, 720 + 20 + 190), 'white')
    S.paste(ims[0], (10, 10))
    for i, im in enumerate(ims):
        S.paste(im.resize((320, 180), Image.LANCZOS), (10 + i * 330, 740))
    S.save('/home/claude/video/thumb_check.png')
