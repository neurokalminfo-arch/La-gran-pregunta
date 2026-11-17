"""Shared drawing toolkit for the 'guerra nuclear' video (dark infographic style)."""
import cairo, math, json, random, os

W, H = 1920, 1080
FPS = 30

def hexc(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))

BG    = hexc('#0A0C10')
PANEL = hexc('#12161D')
LINE  = hexc('#222833')
GRIDC = hexc('#151A22')
INK   = hexc('#ECEAE4')
MUTED = hexc('#7D8490')
DIM   = hexc('#3A414D')
RED   = hexc('#FF4B3A')
AMBER = hexc('#FFB224')
GREEN = hexc('#38D996')
CRT   = hexc('#5CFF9D')
LAND  = hexc('#1E2530')
LANDE = hexc('#2C3542')

F_BLACK = "Inter Display Black"
F_XB    = "Inter Display ExtraBold"
F_SEMI  = "Inter Display SemiBold"
F_MED   = "Inter Display Medium"
F_MONO  = "DejaVu Sans Mono"

# ---------------------------------------------------------------- easing
def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x

def prog(t, a, b):
    if b <= a:
        return 1.0 if t >= b else 0.0
    return clamp((t - a) / (b - a))

def ease(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)

def eout(x):
    x = clamp(x)
    return 1 - (1 - x) ** 3

def lerp(a, b, x):
    return a + (b - a) * x

def mix(c1, c2, x):
    return tuple(lerp(a, b, x) for a, b in zip(c1, c2))

# ---------------------------------------------------------------- basics
def col(ctx, c, a=1.0):
    ctx.set_source_rgba(c[0], c[1], c[2], a)

def background(ctx, grid=True):
    col(ctx, BG)
    ctx.paint()
    if grid:
        ctx.set_line_width(1)
        col(ctx, GRIDC)
        for x in range(0, W + 1, 80):
            ctx.move_to(x + .5, 0); ctx.line_to(x + .5, H)
        for y in range(0, H + 1, 80):
            ctx.move_to(0, y + .5); ctx.line_to(W, y + .5)
        ctx.stroke()
    g = cairo.RadialGradient(W / 2, H / 2, 200, W / 2, H / 2, 1150)
    g.add_color_stop_rgba(0, 0, 0, 0, 0)
    g.add_color_stop_rgba(1, 0, 0, 0, 0.75)
    ctx.set_source(g)
    ctx.paint()

def font(ctx, fam, size):
    ctx.select_font_face(fam, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(size)

def text(ctx, s, x, y, size, c=INK, fam=F_XB, align='c', a=1.0, track=0):
    """Draw text with baseline at y. align: l / c / r. track = letter spacing px."""
    if a <= 0 or not s:
        return 0
    font(ctx, fam, size)
    if track:
        widths = [ctx.text_extents(ch).x_advance for ch in s]
        tw = sum(widths) + track * (len(s) - 1)
    else:
        tw = ctx.text_extents(s).x_advance
    x0 = x - tw / 2 if align == 'c' else x - tw if align == 'r' else x
    col(ctx, c, a)
    if track:
        cx = x0
        for ch, w in zip(s, widths):
            ctx.move_to(cx, y); ctx.show_text(ch); cx += w + track
        ctx.new_path()
    else:
        ctx.move_to(x0, y); ctx.show_text(s)
    ctx.new_path()
    return tw

def twidth(ctx, s, size, fam=F_XB):
    font(ctx, fam, size)
    return ctx.text_extents(s).x_advance

def label(ctx, s, x, y, a=1.0, c=MUTED, size=26, align='c'):
    """Small uppercase tracked label."""
    text(ctx, s.upper(), x, y, size, c, F_SEMI, align, a, track=3)

def source(ctx, s, a=1.0):
    text(ctx, "Fuente: " + s, W - 60, H - 44, 22, MUTED, F_MED, 'r', a)

def rrect(ctx, x, y, w, h, r):
    r = min(r, w / 2, h / 2)
    ctx.new_sub_path()
    ctx.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    ctx.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    ctx.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    ctx.arc(x + r, y + r, r, math.pi, 1.5 * math.pi)
    ctx.close_path()

def glow(ctx, x, y, r, c, a=1.0):
    g = cairo.RadialGradient(x, y, 0, x, y, r)
    g.add_color_stop_rgba(0, c[0], c[1], c[2], a)
    g.add_color_stop_rgba(0.35, c[0], c[1], c[2], a * 0.45)
    g.add_color_stop_rgba(1, c[0], c[1], c[2], 0)
    ctx.set_source(g)
    ctx.arc(x, y, r, 0, 2 * math.pi)
    ctx.fill()

def fmt_int(n):
    return f"{int(round(n)):,}".replace(",", ".")

# ---------------------------------------------------------------- map
_GEO = None
def geo():
    global _GEO
    if _GEO is None:
        d = json.load(open(os.path.join(os.path.dirname(__file__), 'world.geojson')))
        out = {}
        for f in d['features']:
            if f['id'] in ('ATA', '-99') and f['properties']['name'] == 'Antarctica':
                continue
            g = f['geometry']
            polys = g['coordinates'] if g['type'] == 'MultiPolygon' else [g['coordinates']]
            out.setdefault(f['id'], []).extend(polys)
        out.pop('ATA', None)
        _GEO = out
    return _GEO

EUROPE = ['ALB', 'AUT', 'BEL', 'BGR', 'BIH', 'BLR', 'CHE', 'CZE', 'DEU', 'DNK', 'ESP', 'EST', 'FIN', 'FRA',
          'GBR', 'GRC', 'HRV', 'HUN', 'IRL', 'ITA', 'LTU', 'LUX', 'LVA', 'MDA', 'MKD', 'MNE', 'NLD', 'NOR',
          'POL', 'PRT', 'ROU', 'SRB', 'SVK', 'SVN', 'SWE', 'UKR', 'CS-KM', 'KOS']

class Proj:
    """Equirectangular projection fitted into a screen rectangle, with cos(lat) correction."""
    def __init__(self, lon0, lon1, lat0, lat1, x, y, w, h):
        self.lon0, self.lat1 = lon0, lat1
        k = math.cos(math.radians((lat0 + lat1) / 2))
        sx = w / ((lon1 - lon0) * k)
        sy = h / (lat1 - lat0)
        s = min(sx, sy)
        self.k, self.s = k, s
        mw, mh = (lon1 - lon0) * k * s, (lat1 - lat0) * s
        self.ox, self.oy = x + (w - mw) / 2, y + (h - mh) / 2

    def __call__(self, lon, lat):
        return self.ox + (lon - self.lon0) * self.k * self.s, self.oy + (self.lat1 - lat) * self.s

def draw_map(ctx, P, fills=None, base=LAND, edge=LANDE, a=1.0, edge_w=1.0):
    """fills: dict iso3 -> (color, alpha)."""
    fills = fills or {}
    G = geo()
    for iso, polys in G.items():
        c, ca = fills.get(iso, (base, 1.0))
        for poly in polys:
            for ring in poly[:1]:
                for i, (lon, lat) in enumerate(ring):
                    x, y = P(lon, lat)
                    if i == 0: ctx.move_to(x, y)
                    else: ctx.line_to(x, y)
                ctx.close_path()
        col(ctx, c, a * ca)
        ctx.fill_preserve()
        col(ctx, edge, a * 0.9)
        ctx.set_line_width(edge_w)
        ctx.stroke()

def world_proj(x=60, y=150, w=W - 120, h=H - 260):
    return Proj(-170, 190, -57, 82, x, y, w, h)

# ---------------------------------------------------------------- icons
def person(ctx, x, y, s, c, a=1.0):
    col(ctx, c, a)
    ctx.arc(x, y - s * 0.62, s * 0.22, 0, 2 * math.pi); ctx.fill()
    rrect(ctx, x - s * 0.3, y - s * 0.34, s * 0.6, s * 0.72, s * 0.24); ctx.fill()

def wheat(ctx, x, y, h, c, a=1.0, grains=7):
    col(ctx, c, a)
    ctx.set_line_width(max(2, h * 0.025))
    ctx.move_to(x, y); ctx.line_to(x, y - h); ctx.stroke()
    gl = h * 0.11
    for i in range(grains):
        gy = y - h + gl * 0.6 + i * gl * 0.62
        for side in (-1, 1):
            ctx.save(); ctx.translate(x + side * gl * 0.28, gy); ctx.rotate(side * 0.5)
            ctx.scale(gl * 0.22, gl * 0.5); ctx.arc(0, 0, 1, 0, 2 * math.pi); ctx.restore(); ctx.fill()
    ctx.save(); ctx.translate(x, y - h - gl * 0.1); ctx.scale(gl * 0.2, gl * 0.45)
    ctx.arc(0, 0, 1, 0, 2 * math.pi); ctx.restore(); ctx.fill()

def plate(ctx, x, y, r, a=1.0, light=0.0):
    ctx.save(); ctx.translate(x, y); ctx.scale(1, 0.42)
    col(ctx, (0, 0, 0), 0.5 * a); ctx.arc(0, r * 0.22, r * 1.05, 0, 2 * math.pi); ctx.fill()
    col(ctx, mix(hexc('#B9BEC6'), INK, light), a); ctx.arc(0, 0, r, 0, 2 * math.pi); ctx.fill()
    col(ctx, mix(hexc('#8E949D'), hexc('#C9CDD3'), light), a); ctx.arc(0, 0, r * 0.68, 0, 2 * math.pi); ctx.fill()
    col(ctx, mix(hexc('#A3A8B0'), hexc('#DADDE2'), light), a); ctx.arc(0, -r * 0.03, r * 0.62, 0, 2 * math.pi); ctx.fill()
    ctx.restore()

def radiation(ctx, x, y, r, c, a=1.0):
    col(ctx, c, a)
    ctx.arc(x, y, r * 0.18, 0, 2 * math.pi); ctx.fill()
    for k in range(3):
        a0 = -math.pi / 2 + k * 2 * math.pi / 3 - math.pi / 6 + math.pi / 3
        a0 = math.radians(-90 + 120 * k) - math.radians(30)
        ctx.new_path()
        ctx.arc(x, y, r, a0, a0 + math.radians(60))
        ctx.arc_negative(x, y, r * 0.3, a0 + math.radians(60), a0)
        ctx.close_path(); ctx.fill()

def bulb(ctx, x, y, s, c, a=1.0, on=1.0):
    if on > 0:
        glow(ctx, x, y - s * 0.15, s * 1.3, AMBER, 0.45 * on * a)
    col(ctx, mix(DIM, AMBER, on), a)
    ctx.arc(x, y - s * 0.15, s * 0.38, 0, 2 * math.pi); ctx.fill()
    col(ctx, c, a); rrect(ctx, x - s * 0.18, y + s * 0.18, s * 0.36, s * 0.26, 4); ctx.fill()

def wifi(ctx, x, y, s, c, a=1.0):
    col(ctx, c, a); ctx.set_line_width(s * 0.09); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    for i, rr in enumerate((0.28, 0.52, 0.76)):
        ctx.arc(x, y + s * 0.3, s * rr, math.radians(-135), math.radians(-45)); ctx.stroke()
    ctx.arc(x, y + s * 0.3, s * 0.07, 0, 2 * math.pi); ctx.fill()
    ctx.set_line_cap(cairo.LINE_CAP_BUTT)

def tap(ctx, x, y, s, c, a=1.0, drop=1.0):
    col(ctx, c, a)
    rrect(ctx, x - s * 0.45, y - s * 0.35, s * 0.6, s * 0.18, 5); ctx.fill()
    rrect(ctx, x + s * 0.05, y - s * 0.35, s * 0.18, s * 0.38, 5); ctx.fill()
    rrect(ctx, x - s * 0.28, y - s * 0.5, s * 0.08, s * 0.17, 3); ctx.fill()
    if drop > 0:
        col(ctx, hexc('#5AA9FF'), a * drop)
        ctx.arc(x + s * 0.14, y + s * 0.2, s * 0.06, 0, 2 * math.pi); ctx.fill()

def cross(ctx, x, y, s, c, a=1.0):
    col(ctx, c, a)
    rrect(ctx, x - s * 0.13, y - s * 0.4, s * 0.26, s * 0.8, 4); ctx.fill()
    rrect(ctx, x - s * 0.4, y - s * 0.13, s * 0.8, s * 0.26, 4); ctx.fill()

def strike(ctx, x, y, s, a=1.0, p=1.0):
    if p <= 0: return
    col(ctx, RED, a); ctx.set_line_width(s * 0.08); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.move_to(x - s * 0.5, y - s * 0.5)
    ctx.line_to(x - s * 0.5 + s * p, y - s * 0.5 + s * p); ctx.stroke()
    ctx.set_line_cap(cairo.LINE_CAP_BUTT)

def skyline(ctx, base_y, a=1.0, seed=3, lit=1.0, x0=0, x1=W, c=hexc('#161B23'), win=AMBER):
    rnd = random.Random(seed)
    x = x0
    while x < x1:
        w = rnd.randint(60, 150); h = rnd.randint(140, 420)
        col(ctx, c, a); ctx.rectangle(x, base_y - h, w - 6, h); ctx.fill()
        if lit > 0:
            for wy in range(int(base_y - h + 20), int(base_y - 20), 28):
                for wx in range(int(x + 12), int(x + w - 20), 22):
                    if rnd.random() < 0.38:
                        col(ctx, win, a * lit * rnd.uniform(0.35, 0.9)); ctx.rectangle(wx, wy, 8, 12); ctx.fill()
        x += w
    col(ctx, c, a); ctx.rectangle(x0, base_y, x1 - x0, H - base_y); ctx.fill()

def thumb(ctx, x, y, s, c, a=1.0):
    col(ctx, c, a)
    rrect(ctx, x - s * 0.5, y - s * 0.05, s * 0.2, s * 0.55, 6); ctx.fill()
    rrect(ctx, x - s * 0.25, y - s * 0.1, s * 0.72, s * 0.6, s * 0.12); ctx.fill()
    ctx.save(); ctx.translate(x, y - s * 0.22); ctx.rotate(-0.35)
    rrect(ctx, -s * 0.12, -s * 0.38, s * 0.26, s * 0.52, s * 0.13); ctx.restore(); ctx.fill()

def globe(ctx, x, y, r, a=1.0, dark=0.0, t=0.0):
    col(ctx, hexc('#1B3A5A'), a); ctx.arc(x, y, r, 0, 2 * math.pi); ctx.fill()
    ctx.save(); ctx.arc(x, y, r, 0, 2 * math.pi); ctx.clip()
    # continents via map projection in a square, scrolled
    P = Proj(-180, 180, -80, 80, x - r * 1.6 - (t * 30) % (r * 3.2), y - r, r * 3.2 * 2, r * 2)
    P2 = Proj(-180, 180, -80, 80, x - r * 1.6 - (t * 30) % (r * 3.2) - r * 3.2, y - r, r * 3.2 * 2, r * 2)
    for PP in (P, P2):
        draw_map(ctx, PP, base=hexc('#3F7A55'), edge=hexc('#3F7A55'), a=a * 0.9, edge_w=0.5)
    ctx.set_line_width(1); col(ctx, INK, 0.07 * a)
    for k in range(-2, 3):
        ctx.save(); ctx.translate(x, y); ctx.scale(abs(k) / 3 + 0.01, 1)
        ctx.arc(0, 0, r, 0, 2 * math.pi); ctx.restore(); ctx.stroke()
    if dark > 0:
        col(ctx, (0.02, 0.02, 0.025), dark * a * 0.85)
        ctx.rectangle(x - r, y - r, 2 * r, 2 * r * clamp(dark * 1.2)); ctx.fill()
    ctx.restore()
    g = cairo.RadialGradient(x - r * 0.4, y - r * 0.4, r * 0.1, x, y, r)
    g.add_color_stop_rgba(0, 1, 1, 1, 0.08 * a); g.add_color_stop_rgba(1, 0, 0, 0, 0.55 * a)
    ctx.set_source(g); ctx.arc(x, y, r, 0, 2 * math.pi); ctx.fill()
