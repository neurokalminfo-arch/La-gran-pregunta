"""Shorts verticales 1080x1920 a partir de las escenas del vídeo largo. python3 shorts.py [stills]"""
import json, os, sys, math, re, subprocess, wave, random
import numpy as np
import skia
from multiprocessing import Pool
import render
from render import Ctx, draw_frame, BEATS, norm
from lib import *
import scenes

D = os.path.dirname(os.path.abspath(__file__))
OUT = f"{D}/shorts"
VW, VH = 1080, 1920
SC = 0.7
SY = 500
AREA_H = 1080 * 0.7
WIDE = {'cortisol_chart', 'sunrise_cities', 'club', 'doctor_warning', 'evidence_card', 'same_mechanism', 'two_groups', 'scale_equal', 'then_now', 'mistake_coffee'}
TAIL = 2.6
SR = 44100

SHORTS = [
    {"id": "s1-mismo-desayuno", "beats": [0, 1, 2, 3, 4, 5, 9, 10, 14],
     "head": ["Comen lo mismo...", "¿por qué uno engorda?"]},
    {"id": "s2-puerta-trasera", "beats": [31, 32, 33, 34, 35, 36, 38, 39],
     "head": ["Tus músculos tienen", "una PUERTA SECRETA"]},
    {"id": "s3-doble-grasa", "beats": [46, 47, 48, 49, 50, 51, 52, 53],
     "head": ["El doble de grasa...", "y el MISMO peso"]},
    {"id": "s4-despertador", "beats": [16, 17, 18, 19, 20, 21, 23, 37, 38],
     "head": ["Lo que hace tu cuerpo", "al sonar el despertador"]},
    {"id": "s5-tres-errores", "beats": [58, 59, 60, 61, 62, 63],
     "head": ["3 errores que arruinan", "tu paseo de la mañana"]},
    {"id": "s6-como-hacerlo", "beats": [10, 65, 66, 67, 68, 69],
     "head": ["El paseo de 10 minutos", "BIEN HECHO"]},
    {"id": "s7-siesta", "beats": [17, 18, 19, 74],
     "head": ["Tu cuerpo sabe si es", "una siesta o una mañana"]},
]


def plan(sh):
    segs, t = [], 0.0
    for bi in sh["beats"]:
        b = BEATS[bi]
        segs.append((bi, t, b["dur"]))
        t += b["dur"]
    return segs, t + TAIL


def words_abs(segs):
    ws = []
    for bi, t0, dur in segs:
        b = BEATS[bi]
        for w in b["words"]:
            ws.append([w[0], w[1] - b["start"] + t0, w[2] - b["start"] + t0])
    chunks, cur = [], []
    for i, w in enumerate(ws):
        cur.append(w)
        nxt_gap = ws[i + 1][1] - w[2] if i + 1 < len(ws) else 9
        if len(cur) >= 3 or w[0][-1] in ".,?!:;" or nxt_gap > .35 or i == len(ws) - 1:
            chunks.append(cur); cur = []
    return chunks


def captions_v(c, chunks, T):
    ch = None
    for k, chunk in enumerate(chunks):
        nxt = chunks[k + 1][0][1] if k + 1 < len(chunks) else 1e9
        if chunk[0][1] - .05 <= T < min(nxt, chunk[-1][2] + .5):
            ch = chunk; break
    if not ch:
        return
    words = [w[0].replace("...", "").strip("…") for w in ch]
    size = 104
    f = font("cap", size)
    gap = 26
    total = sum(f.measureText(w) for w in words) + gap * (len(words) - 1)
    if total > 1000:
        size *= 1000 / total; f = font("cap", size); gap *= 1000 / total
        total = 1000
    x = VW / 2 - total / 2; y = 1450
    for w, wo in zip(words, ch):
        wd = f.measureText(w)
        cur = wo[1] - .03 <= T < wo[2] + .08
        c.save(); c.translate(x + wd / 2, y)
        sc = 1.0 + ((.16 * (1 - pr(T, wo[1], .18)) + .06) if cur else 0)
        c.scale(sc, sc)
        sp = skia.Paint(AntiAlias=True, Color=C(INK), Style=skia.Paint.kStroke_Style, StrokeWidth=15, StrokeJoin=skia.Paint.kRound_Join)
        c.drawString(w, -wd / 2, 0, f, sp)
        c.drawString(w, -wd / 2, 0, f, fill((255, 232, 40) if cur else WHITE, 255 if wo[1] - .03 <= T else 140))
        c.restore()
        x += wd + gap


def headline(c, head, T):
    k = pr(T, .05, .45)
    text(c, "BIOLOGÍA OCULTA", VW / 2, 92, 30, GREY, "bold", a=255 * k)
    for i, line_s in enumerate(head):
        kk = pr(T, .1 + i * .25, .45)
        if kk <= 0:
            continue
        size = fit_size(line_s, "marker", 86, 960)
        y = 190 + i * 112
        c.save(); c.translate(VW / 2, y); s = lerp(.7, 1, back(kk)); c.scale(s, s)
        if i == 1:
            w = tw(line_s, "marker", size)
            c.drawRoundRect(skia.Rect.MakeXYWH(-w / 2 - 22, -size * .78, w + 44, size * 1.02), 14, 14, fill(YEL))
        text(c, line_s, 0, 0, size, INK, "marker")
        c.restore()


def end_card(c, T, Ttot):
    k = pr(T, Ttot - TAIL, .4)
    if k <= 0:
        return
    c.drawRect(skia.Rect.MakeXYWH(0, 0, VW, VH), fill(WHITE, 235 * k))
    c.save(); c.translate(VW / 2, 760); s = back(k); c.scale(s, s)
    scenes.emblem(c, 0, 0, 1.0)
    c.restore()
    text(c, "VÍDEO COMPLETO", VW / 2, 1150, 100, INK, "marker", a=255 * k)
    text(c, "en el canal", VW / 2, 1260, 70, TEAL, "marker", a=255 * k)
    p = poly([(VW / 2 - 40, 1330), (VW / 2 - 40, 1430), (VW / 2 + 50, 1380)], True)
    c.drawPath(p, fill(RED, 255 * k))


def render_short(si):
    sh = SHORTS[si]
    render.init()
    segs, Ttot = plan(sh)
    chunks = words_abs(segs)
    n = int(round(Ttot * FPS))
    os.makedirs(OUT, exist_ok=True)
    out = f"{OUT}/{sh['id']}_video.mp4"; tmp = out + ".tmp.mp4"
    arr, surf = render.surface()
    varr = np.zeros((VH, VW, 4), np.uint8)
    vsurf = skia.Surface(varr, colorType=skia.kRGBA_8888_ColorType)
    ctxs = {bi: Ctx(BEATS[bi], k) for k, (bi, _, _) in enumerate(segs)}
    ff = None
    if not STILLS:
        ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{VW}x{VH}", "-r", str(FPS),
                               "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
    frames = range(n) if not STILLS else [int(n * f) for f in (.04, .3, .6, .97)]
    for f in frames:
        T = f / FPS
        seg = segs[-1]
        for sg in segs:
            if sg[1] <= T < sg[1] + sg[2]:
                seg = sg; break
        bi, t0, dur = seg
        lt = min(T - t0, dur - 1 / FPS)
        with surf as c:
            draw_frame(c, ctxs[bi], lt, short=True)
        img = skia.Image.fromarray(arr, colorType=skia.kRGBA_8888_ColorType, copy=False) if False else skia.Image.fromarray(arr.copy(), colorType=skia.kRGBA_8888_ColorType)
        with vsurf as c:
            c.clear(C(WHITE))
            sc = VW / 1920 if BEATS[bi]["kind"] in WIDE else SC
            c.save(); c.clipRect(skia.Rect.MakeXYWH(0, SY, VW, AREA_H))
            c.translate((VW - 1920 * sc) / 2, SY + (AREA_H - 1080 * sc) / 2); c.scale(sc, sc)
            c.drawImage(img, 0, 0); c.restore()
            src = BEATS[bi]["p"].get("src")
            if src and lt > .6:
                fz = font("reg", 22); w = fz.measureText("Fuente: " + src)
                rrect(c, VW / 2 - w / 2 - 16, SY + AREA_H + 14, w + 32, 40, 10, INK, 0, (242, 242, 242), 255, False)
                c.drawString("Fuente: " + src, VW / 2 - w / 2, SY + AREA_H + 42, fz, fill(INK, 220))
            headline(c, sh["head"], T)
            S = ctxs[bi]; kt = S.kw_time()
            if kt is not None and lt >= kt:
                kw = S.p["kw"]
                marker_text(c, kw, VW / 2, 425, fit_size(kw, "marker", 64, 900), INK, YEL, (lt - kt) / .6)
            captions_v(c, chunks, T)
            c.drawRect(skia.Rect.MakeXYWH(0, VH - 14, VW * T / Ttot, 14), fill(TEAL))
            end_card(c, T, Ttot)
        if STILLS:
            skia.Image.fromarray(varr.copy(), colorType=skia.kRGBA_8888_ColorType).save(f"{OUT}/still_{sh['id']}_{f}.jpg", skia.kJPEG, 80)
        else:
            ff.stdin.write(varr.tobytes())
    if ff:
        ff.stdin.close()
        if ff.wait() == 0:
            os.rename(tmp, out)
        make_audio(sh, segs, Ttot)
        final = f"{OUT}/{sh['id']}.mp4"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", out, "-i", f"{OUT}/{sh['id']}.wav", "-map", "0:v", "-map", "1:a",
                        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-shortest",
                        "-movflags", "+faststart", final], check=True)
    return si


def make_audio(sh, segs, Ttot):
    with wave.open(f"{D}/voice.wav") as w:
        voice = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    N = int(Ttot * SR)
    v = np.zeros(N, np.float32)
    for bi, t0, dur in segs:
        b = BEATS[bi]
        a0 = int(b["start"] * SR); seg = voice[a0:a0 + int(dur * SR)]
        j = int(t0 * SR); v[j:j + len(seg)] += seg[:N - j]
    rng = np.random.default_rng(len(sh["id"]))
    t = np.arange(N) / SR
    music = np.zeros(N, np.float32)
    bpm = 100; beat = 60 / bpm
    chords = [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]]
    k = 0; tt = 0.0
    while tt < Ttot:
        ch = chords[(k // 8) % 4]; m = ch[[0, 1, 2, 1, 2, 0, 1, 2][k % 8]] + 12
        n = int(.5 * SR); j = int(tt * SR); ts = np.arange(n) / SR
        f = 440 * 2 ** ((m - 69) / 12)
        note = (np.sin(2 * np.pi * f * ts) + .3 * np.sin(4 * np.pi * f * ts)) * np.exp(-ts / .3) * .05
        music[j:j + n] += note[:N - j]
        if k % 2 == 0:
            n2 = int(.22 * SR); ts2 = np.arange(n2) / SR
            kick = np.sin(2 * np.pi * (55 + 60 * np.exp(-ts2 * 30)) * ts2) * np.exp(-ts2 * 12) * .1
            music[j:j + n2] += kick[:N - j]
        tt += beat / 2; k += 1
    sfx = np.zeros(N, np.float32)
    wn = int(.4 * SR); x = rng.normal(0, 1, wn)
    acc = 0.0; wh = np.zeros(wn)
    for i in range(wn):
        acc += (.02 + .25 * i / wn) * (x[i] - acc); wh[i] = acc
    wh *= np.sin(np.linspace(0, np.pi, wn)) ** 2 * .5
    for bi, t0, dur in segs:
        j = max(0, int((t0 - .1) * SR)); sfx[j:j + wn] += wh[:N - j]
    vol = np.convolve(np.abs(v), np.ones(2205) / 2205, "same")
    duck = np.convolve(np.where(vol > .01, .55, 1.0), np.ones(4410) / 4410, "same")
    fade = np.ones(N); fl = int(1.5 * SR); fade[-fl:] = np.linspace(1, 0, fl)
    mix = v + music * duck * .6 * fade + sfx * .35
    mix /= max(1.0, np.abs(mix).max() / .95)
    st = np.stack([mix, mix], 1)
    with wave.open(f"{OUT}/{sh['id']}.wav", "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((st * 32767).astype(np.int16).tobytes())


STILLS = len(sys.argv) > 1 and sys.argv[1] == "stills"
if __name__ == "__main__":
    for sh in SHORTS:
        print(sh["id"], round(plan(sh)[1], 1), "s")
    if STILLS:
        for i in range(len(SHORTS)):
            render_short(i)
    else:
        with Pool(2) as pool:
            for i in pool.imap_unordered(render_short, range(len(SHORTS))):
                print("ok", SHORTS[i]["id"], flush=True)
