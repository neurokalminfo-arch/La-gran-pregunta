"""Render blocks to video. Usage:
  python3 render.py stills                 -> PNG stills at key moments of every phase
  python3 render.py block <name> [out.mp4] -> render one block
  python3 render.py all                    -> render every block
Durations come from durations.json (seconds per block, from the narration audio) when present.
"""
import cairo, json, os, re, subprocess, sys, time
from lib import W, H, FPS, background
import scenes

FADE = 0.3
HERE = os.path.dirname(os.path.abspath(__file__))

def weight(s):
    words = len(s.split())
    ell = s.count('...') + s.count('…')
    ends = len(re.findall(r'[.?!:]', s.replace('...', '')))
    return words + 1.6 * ell + 0.7 * ends

def block_duration(name, phases):
    dpath = os.path.join(HERE, 'durations.json')
    if os.path.exists(dpath):
        d = json.load(open(dpath))
        if name in d:
            return d[name]
    return sum(weight(s) for _, s in phases) / 2.6 + 0.6

LEAD, TAIL = 0.25, 0.55

def silences(path):
    import subprocess
    o = subprocess.run(['ffmpeg', '-i', path, '-af', 'silencedetect=noise=-35dB:d=0.25', '-f', 'null', '-'],
                       capture_output=True, text=True).stderr
    st = [float(x) for x in re.findall(r'silence_start: ([\d.]+)', o)]
    en = [float(x) for x in re.findall(r'silence_end: ([\d.]+)', o)]
    return [(a + b) / 2 for a, b in zip(st, en)]

def layout(phases, D, name=None):
    ws = [weight(s) for _, s in phases]
    tot = sum(ws)
    apath = os.path.join(HERE, 'audio', f'{name}.mp3') if name else None
    if apath and os.path.exists(apath) and len(phases) > 1:
        A = D - LEAD - TAIL
        sil = silences(apath)
        cuts, acc = [], 0.0
        for w in ws[:-1]:
            acc += w
            guess = A * acc / tot
            best = min(sil, key=lambda s: abs(s - guess)) if sil else guess
            if abs(best - guess) > 2.5: best = guess
            cuts.append(LEAD + best)
        edges = [0.0] + cuts + [D]
        for i in range(1, len(edges)):
            if edges[i] <= edges[i - 1] + 0.8: edges[i] = edges[i - 1] + 0.8
        return [(fn, edges[i], edges[i + 1] - edges[i]) for i, (fn, _) in enumerate(phases)]
    out, acc = [], 0.0
    for (fn, _), w in zip(phases, ws):
        d = D * w / tot
        out.append((fn, acc, d)); acc += d
    return out

def draw(ctx, lay, tb, first_block=False, last_block=False):
    background(ctx)
    for i, (fn, s, d) in enumerate(lay):
        if s <= tb < s + d or (i == len(lay) - 1 and tb >= s):
            t = tb - s
            a = 1.0
            if not (i == 0 and first_block):
                a = min(a, t / FADE)
            if not (i == len(lay) - 1 and last_block):
                a = min(a, (d - t) / FADE)
            a = max(0.0, min(1.0, a))
            ctx.push_group()
            fn(ctx, t, d)
            ctx.pop_group_to_source()
            ctx.paint_with_alpha(a)
            return

def new_surface():
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
    return surf, cairo.Context(surf)

def stills(outdir, which=None):
    os.makedirs(outdir, exist_ok=True)
    for name, phases in scenes.BLOCKS:
        if which and name not in which: continue
        D = block_duration(name, phases)
        lay = layout(phases, D, name)
        for i, (fn, s, d) in enumerate(lay):
            surf, ctx = new_surface()
            draw(ctx, lay, s + d * 0.82)
            surf.write_to_png(os.path.join(outdir, f"{name}_{i}_{fn.__name__}.png"))

def render_block(name, phases, out, first=False, last=False):
    D = block_duration(name, phases)
    lay = layout(phases, D, name)
    n = int(round(D * FPS))
    tmp = out[:-4] + '.part.mp4'
    cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgr0', '-s', f'{W}x{H}',
           '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18',
           '-pix_fmt', 'yuv420p', '-r', str(FPS), tmp]
    pr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    surf, ctx = new_surface()
    t0 = time.time()
    for f in range(n):
        draw(ctx, lay, f / FPS, first, last)
        surf.flush()
        pr.stdin.write(bytes(surf.get_data()))
    pr.stdin.close()
    if pr.wait() == 0:
        os.replace(tmp, out)
    print(f"{name}: {n} frames, {D:.1f}s, {time.time() - t0:.0f}s render", flush=True)

if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'stills':
        stills(os.path.join(HERE, 'stills'), sys.argv[2:] or None)
    elif mode == 'block':
        name = sys.argv[2]
        phases = dict(scenes.BLOCKS)[name]
        out = sys.argv[3] if len(sys.argv) > 3 else os.path.join(HERE, 'parts', name + '.mp4')
        os.makedirs(os.path.dirname(out), exist_ok=True)
        render_block(name, phases, out)
    elif mode == 'all':
        os.makedirs(os.path.join(HERE, 'parts'), exist_ok=True)
        names = [n for n, _ in scenes.BLOCKS]
        for i, (name, phases) in enumerate(scenes.BLOCKS):
            if len(sys.argv) > 2 and name not in sys.argv[2:]: continue
            render_block(name, phases, os.path.join(HERE, 'parts', name + '.mp4'),
                         first=(i == 0), last=(i == len(names) - 1))
