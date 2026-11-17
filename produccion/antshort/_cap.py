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
