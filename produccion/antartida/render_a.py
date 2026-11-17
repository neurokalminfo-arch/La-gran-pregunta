"""Render: python3 render_i.py stills | all [names...] | assemble"""
import sys, os, re, json, time, subprocess
sys.path.append('/home/claude/video')
import cairo
from lib import W, H, FPS, background
import scenes

HERE = os.path.dirname(os.path.abspath(__file__))
LEAD, TAIL, FADE = 0.3, 0.7, 0.25

def adur(n):
    return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0',
                                 os.path.join(HERE, 'audio', n + '.mp3')], capture_output=True, text=True).stdout)

def silences(n):
    o = subprocess.run(['ffmpeg', '-i', os.path.join(HERE, 'audio', n + '.mp3'), '-af', 'silencedetect=noise=-35dB:d=0.25',
                        '-f', 'null', '-'], capture_output=True, text=True).stderr
    st = [float(x) for x in re.findall(r'silence_start: ([\d.]+)', o)]
    en = [float(x) for x in re.findall(r'silence_end: ([\d.]+)', o)]
    return [(a + b) / 2 for a, b in zip(st, en)]

def layout(name, phases):
    A = adur(name); D = A + LEAD + TAIL
    ws = [len(s) for _, s in phases]; tot = sum(ws)
    sil = silences(name)
    cuts, acc = [0.0], 0
    for w in ws[:-1]:
        acc += w; g = A * acc / tot
        cand = [x for x in sil if x > cuts[-1] + .6]
        b = min(cand, key=lambda x: abs(x - g)) if cand else g
        cuts.append(b if abs(b - g) < 2.5 else max(g, cuts[-1] + .6))
    edges = [0.0] + [LEAD + c for c in cuts[1:]] + [D]
    return [(fn, edges[i], edges[i + 1] - edges[i]) for i, (fn, _) in enumerate(phases)], D

def draw(ctx, lay, tb, first=False, last=False):
    background(ctx)
    for i, (fn, s, d) in enumerate(lay):
        if s <= tb < s + d or (i == len(lay) - 1 and tb >= s):
            t = tb - s; a = 1.0
            if not (i == 0 and first): a = min(a, t / FADE)
            if not (i == len(lay) - 1 and last): a = min(a, (d - t) / FADE)
            ctx.push_group(); fn(ctx, t, d); ctx.pop_group_to_source(); ctx.paint_with_alpha(max(0, min(1, a)))
            return

def stills(which=None):
    os.makedirs(os.path.join(HERE, 'stills'), exist_ok=True)
    for name, phases in scenes.blocks():
        if which and name not in which: continue
        lay, D = layout(name, phases)
        for i, (fn, s, d) in enumerate(lay):
            surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H); ctx = cairo.Context(surf)
            draw(ctx, lay, s + d * .8); surf.write_to_png(os.path.join(HERE, 'stills', f'{name}_{i}_{fn.__name__}.png'))
        print(name, round(D, 1), [(f.__name__, round(s, 1)) for f, s, _ in lay], flush=True)

def render(name, phases, first, last):
    lay, D = layout(name, phases)
    out = os.path.join(HERE, 'parts', name + '.mp4'); tmp = out[:-4] + '.part.mp4'
    n = int(round(D * FPS))
    pr = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgr0', '-s', f'{W}x{H}',
                           '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18',
                           '-pix_fmt', 'yuv420p', '-r', str(FPS), tmp], stdin=subprocess.PIPE)
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H); ctx = cairo.Context(surf); t0 = time.time()
    for f in range(n):
        draw(ctx, lay, f / FPS, first, last); surf.flush(); pr.stdin.write(bytes(surf.get_data()))
    pr.stdin.close()
    if pr.wait() == 0: os.replace(tmp, out)
    print(name, round(D, 1), 's', round(time.time() - t0), 's render', flush=True)

def assemble():
    B = scenes.blocks(); names = [n for n, _ in B]
    durs = {n: layout(n, p)[1] for n, p in B}
    open(os.path.join(HERE, 'concat.txt'), 'w').write(''.join(f"file 'parts/{n}.mp4'\n" for n in names))
    ins, filt, offs, o = [], [], [], 0.0
    for i, n in enumerate(names):
        ins += ['-i', f'audio/{n}.mp3']
        filt.append(f"[{i}:a]aresample=48000,adelay={int(LEAD*1000)}|{int(LEAD*1000)},apad,atrim=0:{durs[n]:.3f}[a{i}]")
        offs.append(o); o += durs[n]
    filt.append(''.join(f'[a{i}]' for i in range(len(names))) + f"concat=n={len(names)}:v=0:a=1[v]")
    # whoosh at each block start (pattern interrupt) + soft low drone bed
    wh = '+'.join(f"0.35*exp(-6*abs(t-{x+0.15:.2f}))*sin(2*PI*(180+900*exp(-8*abs(t-{x+0.15:.2f})))*t)*gte(t,{max(x-0.2,0):.2f})*lte(t,{x+0.8:.2f})" for x in offs[1:])
    filt.append(f"aevalsrc='{wh}+0.012*sin(2*PI*55*t)*(1+0.3*sin(2*PI*0.07*t))':s=48000:d={o:.2f},aformat=channel_layouts=stereo[fx]")
    filt.append("[v]aformat=channel_layouts=stereo[vs];[vs][fx]amix=inputs=2:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11[out]")
    subprocess.run(['ffmpeg', '-y', '-v', 'error', *ins, '-filter_complex', ';'.join(filt), '-map', '[out]', '-ar', '48000',
                    '-c:a', 'pcm_s16le', 'voice.wav'], check=True, cwd=HERE)
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', 'concat.txt', '-c', 'copy', 'video_only.mp4'], check=True, cwd=HERE)
    os.makedirs(os.path.join(HERE, 'out'), exist_ok=True)
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', 'video_only.mp4', '-i', 'voice.wav', '-map', '0:v', '-map', '1:a', '-c:v', 'copy',
                    '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', 'out/antartida.part.mp4'], check=True, cwd=HERE)
    os.replace(os.path.join(HERE, 'out/antartida.part.mp4'), os.path.join(HERE, 'out/antartida.mp4'))
    json.dump({n: [offs[i], durs[n]] for i, n in enumerate(names)}, open(os.path.join(HERE, 'offsets.json'), 'w'), indent=1)
    print('total', round(o, 1))

if __name__ == '__main__':
    m = sys.argv[1]
    if m == 'stills': stills(sys.argv[2:] or None)
    elif m == 'all':
        os.makedirs(os.path.join(HERE, 'parts'), exist_ok=True)
        B = scenes.blocks()
        for i, (n, p) in enumerate(B):
            if len(sys.argv) > 2 and n not in sys.argv[2:]: continue
            render(n, p, i == 0, i == len(B) - 1)
    elif m == 'assemble': assemble()
