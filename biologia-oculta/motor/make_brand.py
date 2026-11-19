"""Logo y banner de Biología Oculta, dibujados con código (PIL, supersampling)."""
import math, random, os
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops

BG = (8, 14, 24)
TEAL = (38, 214, 196)
AMBER = (255, 176, 64)
WHITE = (236, 244, 246)
FONT_B = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts", "Poppins-Bold.ttf")
FONT_L = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts", "Poppins-Light.ttf")


def radial_bg(w, h, cx, cy, r, inner, outer):
    img = Image.new("RGB", (w, h), outer)
    px = img.load()
    for y in range(0, h, 2):
        for x in range(0, w, 2):
            d = min(1, math.hypot(x - cx, y - cy) / r)
            t = d ** 1.6
            c = tuple(int(inner[i] * (1 - t) + outer[i] * t) for i in range(3))
            px[x, y] = c
            if x + 1 < w: px[x + 1, y] = c
            if y + 1 < h:
                px[x, y + 1] = c
                if x + 1 < w: px[x + 1, y + 1] = c
    return img


def glow_layer(size, draw_fn, blur):
    layer = Image.new("RGB", size, (0, 0, 0))
    draw_fn(ImageDraw.Draw(layer))
    return layer.filter(ImageFilter.GaussianBlur(blur))


def eye_points(cx, cy, w, h, n=200):
    """Contorno de almendra (ojo)."""
    top, bot = [], []
    for i in range(n + 1):
        t = i / n
        x = cx - w / 2 + w * t
        y = h / 2 * math.sin(math.pi * t) ** 0.9
        top.append((x, cy - y))
        bot.append((x, cy + y))
    return top + bot[::-1]


def draw_emblem(img, cx, cy, s, seed=7):
    """Ojo cuyo iris es una célula: membrana turquesa, núcleo ámbar, orgánulos."""
    rnd = random.Random(seed)
    W, H = img.size
    eye = eye_points(cx, cy, s * 1.9, s * 1.05)
    ir = s * 0.46  # radio iris/célula

    def lines(d, width_mul=1.0):
        d.line(eye + [eye[0]], fill=TEAL, width=int(s * 0.045 * width_mul), joint="curve")
        d.ellipse([cx - ir, cy - ir, cx + ir, cy + ir], outline=TEAL, width=int(s * 0.035 * width_mul))

    # halo
    img.paste(ImageChops.add(img, glow_layer((W, H), lambda d: lines(d, 2.4), s * 0.09)))

    d = ImageDraw.Draw(img)
    # relleno de la célula (citoplasma)
    cell = Image.new("L", (W, H), 0)
    ImageDraw.Draw(cell).ellipse([cx - ir, cy - ir, cx + ir, cy + ir], fill=255)
    cyto = radial_bg(W, H, cx, cy, ir, (20, 70, 78), (10, 26, 36))
    img.paste(cyto, (0, 0), cell)

    d = ImageDraw.Draw(img)
    # orgánulos (pequeños óvalos turquesa tenues)
    for _ in range(14):
        a = rnd.uniform(0, 2 * math.pi)
        rr = rnd.uniform(ir * 0.55, ir * 0.85)
        ox, oy = cx + rr * math.cos(a), cy + rr * math.sin(a)
        ow = s * rnd.uniform(0.03, 0.06)
        d.ellipse([ox - ow, oy - ow * 0.6, ox + ow, oy + ow * 0.6], fill=(46, 150, 140))

    # núcleo ámbar con brillo
    nr = ir * 0.42
    img.paste(ImageChops.add(img, glow_layer((W, H), lambda dd: dd.ellipse(
        [cx - nr * 1.3, cy - nr * 1.3, cx + nr * 1.3, cy + nr * 1.3], fill=(180, 100, 20)), s * 0.08)))
    nuc = radial_bg(W, H, cx - nr * 0.3, cy - nr * 0.3, nr * 1.4, (255, 214, 140), (214, 120, 30))
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).ellipse([cx - nr, cy - nr, cx + nr, cy + nr], fill=255)
    img.paste(nuc, (0, 0), m)
    d = ImageDraw.Draw(img)
    # nucléolo + reflejo
    d.ellipse([cx + nr * 0.05, cy + nr * 0.05, cx + nr * 0.45, cy + nr * 0.45], fill=(150, 70, 10))
    d.ellipse([cx - nr * 0.62, cy - nr * 0.62, cx - nr * 0.30, cy - nr * 0.30], fill=(255, 245, 225))

    # trazos nítidos encima
    lines(d)


def logo(path, size=800):
    S = size * 3
    img = radial_bg(S, S, S / 2, S / 2, S * 0.7, (16, 34, 48), BG)
    draw_emblem(img, S / 2, S / 2, S * 0.42)
    img.resize((size, size), Image.LANCZOS).save(path)


def banner(path):
    W, H = 2560, 1440
    S = 2
    img = radial_bg(W * S, H * S, W * S / 2, H * S / 2, W * S * 0.55, (16, 34, 48), BG)
    d = ImageDraw.Draw(img)
    rnd = random.Random(3)
    # partículas / células de fondo
    for _ in range(260):
        x, y = rnd.uniform(0, W * S), rnd.uniform(0, H * S)
        r = rnd.uniform(2, 9) * S
        c = TEAL if rnd.random() < 0.8 else AMBER
        a = rnd.uniform(0.12, 0.45)
        col = tuple(int(BG[i] * (1 - a) + c[i] * a) for i in range(3))
        d.ellipse([x - r, y - r, x + r, y + r], fill=col)
    # hebra de ADN tenue de lado a lado
    for i in range(0, W * S, 6 * S):
        t = i / (W * S) * 10 * math.pi
        y1 = H * S / 2 + math.sin(t) * 120 * S
        y2 = H * S / 2 - math.sin(t) * 120 * S
        for y, c in ((y1, TEAL), (y2, AMBER)):
            a = 0.18
            col = tuple(int(BG[k] * (1 - a) + c[k] * a) for k in range(3))
            d.ellipse([i - 3 * S, y - 3 * S, i + 3 * S, y + 3 * S], fill=col)
    # oscurecer el centro (zona segura 1546x423) para legibilidad
    shade = Image.new("L", (W * S, H * S), 0)
    ImageDraw.Draw(shade).rounded_rectangle(
        [(W - 1700) / 2 * S, (H - 520) / 2 * S, (W + 1700) / 2 * S, (H + 520) / 2 * S], radius=200 * S, fill=200)
    shade = shade.filter(ImageFilter.GaussianBlur(90 * S))
    img = Image.composite(Image.new("RGB", img.size, BG), img, shade)

    # emblema a la izquierda de la zona segura
    ecx, ecy = (W / 2 - 560) * S, H / 2 * S
    draw_emblem(img, ecx, ecy, 190 * S)

    d = ImageDraw.Draw(img)
    fb = ImageFont.truetype(FONT_B, 150 * S)
    fl = ImageFont.truetype(FONT_L, 50 * S)
    tx = (W / 2 - 330) * S
    d.text((tx, H / 2 * S - 25 * S), "BIOLOGÍA", font=fb, fill=WHITE, anchor="ls")
    wb = d.textlength("BIOLOGÍA ", font=fb)
    d.text((tx, H / 2 * S + 115 * S), "OCULTA", font=fb, fill=AMBER, anchor="ls")
    d.text((tx + 6 * S, H / 2 * S + 190 * S), "Lo que pasa dentro de ti mientras no miras",
           font=fl, fill=(150, 200, 205), anchor="ls")
    img.resize((W, H), Image.LANCZOS).save(path, quality=92)


if __name__ == "__main__":
    logo("logo_biologia_oculta.png")
    banner("banner_biologia_oculta.png")
    print("ok")
