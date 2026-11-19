"""Renderiza el vídeo: python3 render.py stills | full [desde hasta]"""
import json, os, sys, math, subprocess, re, unicodedata, random
import numpy as np
import skia
from multiprocessing import Pool
from lib import *
import scenes

D = os.path.dirname(os.path.abspath(__file__))
BEATS = json.load(open(f"{D}/timeline.json"))
PAPER_IMG = None


def norm(s):
    return re.sub(r"[^\wáéíóúñü]", "", s.lower())


class Ctx:
    def __init__(self, b, i):
        self.b, self.i, self.p, self.text = b, i, b["p"], b["text"]
        self.dur = b["dur"]
        self.words = [[w[0], w[1] - b["start"], w[2] - b["start"]] for w in b["words"]]
        self.t = 0.0
        self.chunks, cur = [], []
        for i, w in enumerate(self.words):
            cur.append(w)
            if len(cur) >= 4 or w[0][-1] in ".,?!:;" or i == len(self.words) - 1:
                self.chunks.append(cur); cur = []

    def wt(self, prefix, default=1.0, after=-1.0):
        pf = norm(prefix)
        for w in self.words:
            if w[1] > after and norm(w[0]).startswith(pf):
                return w[1]
        return default

    def kw_time(self):
        kw = self.p.get("kw")
        if not kw:
            return None
        for tok in kw.split():
            tk = norm(tok)
            if len(tk) >= 3:
                for w in self.words:
                    if norm(w[0]).startswith(tk[:5]):
                        return max(.3, w[1] - .1)
        return 1.0


def punch_times(S):
    ts = []
    kt = S.kw_time()
    if kt is not None:
        ts.append(kt)
    return ts


def draw_frame(c, S, t, short=False):
    S.t = t
    c.drawImage(PAPER_IMG, 0, 0)
    # cámara: deriva lenta + golpe de zoom en la palabra clave + transición de entrada
    u = t / max(S.dur, .1)
    z = 1.0 + .045 * eio(u)
    for pt in punch_times(S):
        if pt <= t < pt + .45:
            z += .05 * math.sin((t - pt) / .45 * math.pi)
    dx = (18 if S.i % 2 else -18) * eio(u)
    tr = S.i % 4
    k = eo(pr(t, 0, .38))
    c.save()
    c.translate(W / 2, H / 2)
    if tr == 0:
        c.translate((1 - k) * 260, 0)
    elif tr == 1:
        z *= lerp(.82, 1, k)
    elif tr == 2:
        c.translate(0, (1 - k) * 180)
    else:
        c.rotate((1 - k) * -4); z *= lerp(.9, 1, k)
    c.scale(z, z)
    step = int(t * FPS) // 4
    rj = random.Random(step * 7 + S.i)
    c.rotate(rj.uniform(-.12, .12)); c.translate(rj.uniform(-1.5, 1.5), rj.uniform(-1.5, 1.5))
    c.translate(-W / 2 + dx, -H / 2)
    alpha = int(255 * k)
    if alpha < 255:
        c.saveLayerAlpha(None, alpha)
    scenes.SCENES[S.b["kind"]](c, S)
    if alpha < 255:
        c.restore()
    c.restore()
    # capa fija: palabra clave y fuente
    kt = S.kw_time()
    if kt is not None and t >= kt and not short:
        c.save(); c.translate(0, 0)
        marker_text(c, S.p["kw"], W / 2, 175, 96, INK, YEL, (t - kt) / .6)
        c.restore()
    if short:
        return
    if S.p.get("src") and t > .6:
        source_tag(c, S.p["src"], 255 * pr(t, .6, .4))
    captions(c, S, t)
    social(c, S, t)


CAP = None


def captions(c, S, t):
    ch = None
    for k, chunk in enumerate(S.chunks):
        nxt = S.chunks[k + 1][0][1] if k + 1 < len(S.chunks) else S.dur
        if chunk[0][1] - .05 <= t < min(nxt, chunk[-1][2] + .6):
            ch = chunk; break
    if not ch:
        return
    f = font("cap", 82)
    words = [w[0].strip("…").replace("...", "") for w in ch]
    widths = [f.measureText(w) for w in words]
    gap = 28
    total = sum(widths) + gap * (len(words) - 1)
    x = W / 2 - total / 2; y = 1040
    for w, wd, wo in zip(words, widths, ch):
        on = wo[1] - .03 <= t
        cur = wo[1] - .03 <= t < wo[2] + .08
        c.save(); c.translate(x + wd / 2, y)
        sc = 1.0 + (.14 * (1 - pr(t, wo[1], .18)) + .06 if cur else 0)
        c.scale(sc, sc)
        sp = skia.Paint(AntiAlias=True, Color=C(INK), Style=skia.Paint.kStroke_Style, StrokeWidth=13, StrokeJoin=skia.Paint.kRound_Join)
        c.drawString(w, -wd / 2, 0, f, sp)
        c.drawString(w, -wd / 2, 0, f, fill((255, 232, 40) if cur else WHITE, 255 if on else 150))
        c.restore()
        x += wd + gap


def social(c, S, t):
    ta = S.b["start"] + t
    cta = S.b["kind"] in ("like", "comment_ask", "subscribe")
    win = ((ta - 25) % 75) < 6 and ta > 20
    if not (cta or win):
        return
    k0 = S.b["start"] if cta else ta - ((ta - 25) % 75)
    k = eo(pr(ta, k0 + .2, .5)) * (1 - (eo(pr(ta, k0 + 5.4, .5)) if not cta else 0))
    for i, (lb, ic) in enumerate((("ME GUSTA", "like"), ("COMENTA", "comment"), ("COMPARTE", "share"))):
        kk = eo(pr(k, i * .15, .7))
        x = W + 10 - (300) * kk; y = 700 + i * 82
        rrect(c, x, y, 290, 64, 32, INK, 0, RED, 255, False)
        c.drawCircle(x + 34, y + 32, 20, fill(WHITE))
        if ic == "like":
            icon(c, "like", x + 34, y + 30, .2)
        elif ic == "comment":
            icon(c, "comment", x + 34, y + 30, .11)
        else:
            arrow(c, x + 22, y + 40, x + 46, y + 26, RED, 5, 1, 10)
        text(c, lb, x + 64, y + 44, 34, WHITE, "bold", "l")


def surface():
    arr = np.zeros((H, W, 4), np.uint8)
    return arr, skia.Surface(arr, colorType=skia.kRGBA_8888_ColorType)


def init():
    global PAPER_IMG
    PAPER_IMG = make_paper()


def render_beat(i):
    init()
    b = BEATS[i]
    f0, f1 = round(b["start"] * FPS), round((b["start"] + b["dur"]) * FPS)
    out = f"{D}/segs/seg_{i:03d}.mp4"
    if os.path.exists(out):
        return i
    tmp = out.replace(".mp4", ".tmp.mp4")
    arr, surf = surface()
    S = Ctx(b, i)
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(FPS),
                           "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", tmp],
                          stdin=subprocess.PIPE)
    with surf as c:
        for f in range(f0, f1):
            draw_frame(c, S, f / FPS - b["start"])
            ff.stdin.write(arr.tobytes())
    ff.stdin.close()
    if ff.wait() == 0:
        os.rename(tmp, out)
    return i


def stills():
    init()
    os.makedirs(f"{D}/stills", exist_ok=True)
    arr, surf = surface()
    for i, b in enumerate(BEATS):
        S = Ctx(b, i)
        for tag, frac in (("a", .5), ("b", .9)):
            with surf as c:
                draw_frame(c, S, b["dur"] * frac)
            skia.Image.fromarray(arr.copy(), colorType=skia.kRGBA_8888_ColorType).save(f"{D}/stills/{i:03d}{tag}.jpg", skia.kJPEG, 80)


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "stills":
        stills()
    else:
        os.makedirs(f"{D}/segs", exist_ok=True)
        rng = range(int(sys.argv[2]), int(sys.argv[3])) if len(sys.argv) > 3 else range(len(BEATS))
        with Pool(2) as pool:
            for i in pool.imap_unordered(render_beat, list(rng)):
                print("ok", i, flush=True)
