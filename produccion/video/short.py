"""Vertical 9:16 Short from the hook block: title on top, the 16:9 hook in the middle,
burnt-in captions synced to the narration, end card. Usage: python3 short.py"""
import cairo, json, os, re, subprocess
import numpy as np
from lib import *
from render import silences, LEAD

HERE = os.path.dirname(os.path.abspath(__file__))
SW, SH = 1080, 1920
SRC = os.path.join(HERE, 'parts', '00_hook.mp4')
AUD = os.path.join(HERE, 'audio', '00_hook.mp3')
OUT = os.path.join(HERE, 'out', 'short_guerra_nuclear_9x16.mp4')
END = 3.0

text_all = json.load(open(os.path.join(HERE, 'narration.json')))['00_hook']
sents = [s.strip() for s in re.split(r'(?<=[.?!])\s+(?=[A-ZÁÉÍÓÚ¿])', text_all) if s.strip()]
adur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', AUD],
                            capture_output=True, text=True).stdout)
sil = silences(AUD)
tot = sum(len(s) for s in sents)
cuts, acc = [0.0], 0
for s in sents[:-1]:
    acc += len(s)
    g = adur * acc / tot
    cand = [x for x in sil if x > cuts[-1] + 0.3]
    b = min(cand, key=lambda x: abs(x - g)) if cand else g
    cuts.append(b if abs(b - g) < 2 else max(g, cuts[-1] + 0.4))
cuts.append(adur)
CAP = [(LEAD + cuts[i], LEAD + cuts[i + 1], s) for i, s in enumerate(sents)]

def wrap(ctx, s, size, maxw):
    font(ctx, F_BLACK, size)
    words, lines, cur = s.split(), [], ''
    for w in words:
        t = (cur + ' ' + w).strip()
        if ctx.text_extents(t).x_advance > maxw and cur:
            lines.append(cur); cur = w
        else:
            cur = t
    lines.append(cur)
    return lines

def frame(ctx, img, t, D):
    col(ctx, BG); ctx.paint()
    # top title
    label(ctx, "La Gran Pregunta", SW / 2, 230, 1, AMBER, 30)
    text(ctx, "¿Y si mañana estallara", SW / 2, 330, 72, INK, F_BLACK)
    text(ctx, "una guerra nuclear?", SW / 2, 415, 72, INK, F_BLACK)
    # middle video
    vy = 520
    if img is not None:
        ctx.save(); ctx.translate(0, vy); ctx.scale(SW / W, SW / W)
        ctx.set_source_surface(img, 0, 0); ctx.paint(); ctx.restore()
    col(ctx, LINE); ctx.set_line_width(2); ctx.rectangle(0, vy, SW, SW * H / W); ctx.stroke()
    # captions
    for a, b, s in CAP:
        if a <= t < b:
            lines = wrap(ctx, s, 66, SW - 140)
            k = ease(prog(t, a, a + .15))
            y0 = 1330
            for i, ln in enumerate(lines[:4]):
                hl = 'plato' in ln or 'peor' in ln
                text(ctx, ln, SW / 2, y0 + i * 84, 66, AMBER if hl else INK, F_BLACK, a=k)
    # end card
    if t > D - END:
        k = ease(prog(t, D - END, D - END + .4))
        col(ctx, BG, .92 * k); ctx.paint()
        text(ctx, "¿Qué sería peor", SW / 2, 820, 84, INK, F_BLACK, a=k)
        text(ctx, "que las bombas?", SW / 2, 920, 84, INK, F_BLACK, a=k)
        text(ctx, "La respuesta, en el", SW / 2, 1120, 52, MUTED, F_XB, a=k)
        text(ctx, "vídeo completo del canal", SW / 2, 1190, 52, AMBER, F_XB, a=k)
    # progress bar
    col(ctx, AMBER); ctx.rectangle(0, SH - 12, SW * t / D, 12); ctx.fill()

def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    vdur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', SRC],
                                capture_output=True, text=True).stdout)
    D = vdur + END
    n = int(round(D * FPS))
    dec = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', SRC, '-f', 'rawvideo', '-pix_fmt', 'bgra', '-'],
                           stdout=subprocess.PIPE)
    tmp = OUT[:-4] + '.part.mp4'
    enc = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgr0', '-s', f'{SW}x{SH}',
                            '-r', str(FPS), '-i', '-', '-i', AUD, '-filter_complex',
                            f'[1:a]adelay={int(LEAD * 1000)}|{int(LEAD * 1000)},apad[a]', '-map', '0:v', '-map', '[a]',
                            '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p',
                            '-c:a', 'aac', '-b:a', '192k', '-t', f'{D:.3f}', tmp], stdin=subprocess.PIPE)
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, SW, SH); ctx = cairo.Context(surf)
    fs = W * H * 4
    last = None; keep = None
    for f in range(n):
        t = f / FPS
        buf = dec.stdout.read(fs)
        if buf and len(buf) == fs:
            arr = np.frombuffer(buf, np.uint8).copy()
            keep = arr
            last = cairo.ImageSurface.create_for_data(memoryview(keep), cairo.FORMAT_RGB24, W, H)
        frame(ctx, last, t, D)
        surf.flush(); enc.stdin.write(bytes(surf.get_data()))
    enc.stdin.close()
    if enc.wait() == 0:
        os.replace(tmp, OUT)
    print('short done', D)

if __name__ == '__main__':
    main()
