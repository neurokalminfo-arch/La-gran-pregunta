"""Vídeo largo v2 '¿Qué pasaría si se derritiera toda la Antártida?'
Estilo: óleo empastado pintado con código (claude-drawing) que se pinta delante del espectador,
infografía viva (cámara, transiciones de zoom, sacudidas, partículas), gráficos Manim y sonido sintetizado.
Uso: python3 render2.py stills [bloques] | all [bloques] | audio | assemble"""
import sys, os, re, json, time, math, random, subprocess
sys.path.insert(0, '/home/claude/antartida')
sys.path.append('/home/claude/video')
import cairo
import numpy as np
from lib import W, H, FPS, background, col, hexc, clamp, lerp, ease, eout, glow, AMBER, INK, RED
import importlib.util as U

HERE = os.path.dirname(os.path.abspath(__file__))
A_DIR = '/home/claude/antartida'
_s = U.spec_from_file_location('ascenes', os.path.join(A_DIR, 'scenes.py'))
AS = U.module_from_spec(_s); _s.loader.exec_module(AS)
LEAD, TAIL = 0.3, 0.7
TR = 0.32           # duración de la transición de zoom entre fases

# ------------------------------------------------------------------ cuadros pintados (óleo con fases)
_PL = {}
STAGES = ['00_boceto', '01_base', '02_trazos', '03_detalle', '04_final']
def plate(name):
    if name not in _PL:
        sd = os.path.join(HERE, 'stages', name)
        _PL[name] = [cairo.ImageSurface.create_from_png(os.path.join(sd, s + '.png')) for s in STAGES]
    return _PL[name]

ICY = {'ice_cliff', 'ice_aerial', 'low_sea_cliff', 'thwaites', 'drill_ship'}
def particles(ctx, t, kind, a=1.0):
    r = random.Random(11)
    if kind == 'snow':
        for _ in range(140):
            x0, y0, sp, sz = r.uniform(0, W), r.uniform(0, H), r.uniform(25, 90), r.uniform(1.5, 4.5)
            x = (x0 + 30 * math.sin(t * .6 + x0)) % W; y = (y0 + t * sp) % H
            col(ctx, (1, 1, 1), .55 * a); ctx.arc(x, y, sz, 0, 2 * math.pi); ctx.fill()
    elif kind == 'dust':
        for _ in range(70):
            x0, y0, sp, sz = r.uniform(0, W), r.uniform(0, H), r.uniform(6, 22), r.uniform(1.5, 3.5)
            x = (x0 + t * sp) % W; y = (y0 - t * sp * .4 + 20 * math.sin(t + x0)) % H
            col(ctx, AMBER, (.25 + .2 * math.sin(t * 2 + x0)) * a); ctx.arc(x, y, sz, 0, 2 * math.pi); ctx.fill()
    elif kind == 'glow':
        for _ in range(50):
            x0, y0, sp, sz = r.uniform(0, W), r.uniform(0, H), r.uniform(8, 30), r.uniform(2, 5)
            y = (y0 - t * sp) % H
            col(ctx, (0.4, 0.8, 1.0), (.3 + .3 * math.sin(t * 3 + x0)) * a); ctx.arc(x0, y, sz, 0, 2 * math.pi); ctx.fill()

def painted_photo(ctx, name, t, d, zin=True, pan=(0, 0), dark=0.35, focus=(0.5, 0.5)):
    st = plate(name)
    p = clamp(t / max(d, .01))
    s0, s1 = (1.0, 1.12) if zin else (1.12, 1.0)
    s = lerp(s0, s1, ease(p) * .5 + p * .5)
    fx, fy = focus
    rv = t / 1.5   # 0..1: el cuadro se pinta durante 1,5 s
    def draw_surf(surf, a):
        if a <= 0: return
        ctx.save(); ctx.translate(W * fx + pan[0] * p, H * fy + pan[1] * p); ctx.scale(s, s)
        ctx.translate(-W * fx, -H * fy); ctx.set_source_surface(surf, 0, 0); ctx.paint_with_alpha(a); ctx.restore()
    if rv >= 1:
        draw_surf(st[-1], 1)
    else:
        col(ctx, hexc('#E9E1D0')); ctx.paint()            # lienzo
        k = rv * (len(st) - 1)
        for i in range(len(st)):
            a = clamp(k - i + 1)
            if i > k + 1: break
            draw_surf(st[i], a if i > 0 else clamp(k * 1.5 + .2))
    if dark > 0: col(ctx, (0, 0, 0), dark * .85); ctx.paint()
    kind = 'snow' if name in ICY else ('glow' if name == 'deep_current' else 'dust')
    particles(ctx, t, kind, clamp((t - .8) / .6))
    g = cairo.RadialGradient(W / 2, H / 2, 300, W / 2, H / 2, 1200)
    g.add_color_stop_rgba(0, 0, 0, 0, 0); g.add_color_stop_rgba(1, 0, 0, 0, .65)
    ctx.set_source(g); ctx.paint()

AS.photo = painted_photo

# ------------------------------------------------------------------ clips de Manim
class Clip:
    def __init__(self, path):
        self.path = path; self.proc = None; self.idx = -1; self.buf = None; self.surf = None
        self.n = int(round(float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', path],
                                                capture_output=True, text=True).stdout) * FPS)) - 1
    def _open(self, start):
        if self.proc: self.proc.kill()
        self.proc = subprocess.Popen(['ffmpeg', '-v', 'error', '-ss', f'{start / FPS:.3f}', '-i', self.path, '-f', 'rawvideo', '-pix_fmt', 'bgra',
                                      '-s', f'{W}x{H}', '-'], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        self.idx = start - 1
    def frame(self, t):
        i = min(int(t * FPS), self.n - 1)
        if self.proc is None or i < self.idx or i > self.idx + 60: self._open(i)
        while self.idx < i:
            raw = self.proc.stdout.read(W * H * 4)
            if len(raw) < W * H * 4: break
            self.buf = np.frombuffer(raw, np.uint8).reshape(H, W, 4).copy(); self.idx += 1
            self.surf = cairo.ImageSurface.create_for_data(memoryview(self.buf), cairo.FORMAT_RGB24, W, H)
        return self.surf

CLIPS = {}
def manim_scene(key, file):
    def f(ctx, t, d):
        if key not in CLIPS: CLIPS[key] = Clip(os.path.join(HERE, 'manim/media/videos/escenas/1080p30', file))
        s = CLIPS[key].frame(t)
        if s is not None: ctx.set_source_surface(s, 0, 0); ctx.paint()
        particles(ctx, t, 'dust', .4)
    f.__name__ = 'manim_' + key
    return f

AS.VIS['03_gravedad'][3] = manim_scene('huella', 'Huella.mp4')
AS.VIS['06_futuro'][3] = manim_scene('grados', 'Grados.mp4')

# ------------------------------------------------------------------ tiempos (mismo audio que v1)
def adur(n):
    return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0',
                                 os.path.join(A_DIR, 'audio', n + '.mp3')], capture_output=True, text=True).stdout)
def silences(n):
    o = subprocess.run(['ffmpeg', '-i', os.path.join(A_DIR, 'audio', n + '.mp3'), '-af', 'silencedetect=noise=-35dB:d=0.25',
                        '-f', 'null', '-'], capture_output=True, text=True).stderr
    st = [float(x) for x in re.findall(r'silence_start: ([\d.]+)', o)]; en = [float(x) for x in re.findall(r'silence_end: ([\d.]+)', o)]
    return [(a + b) / 2 for a, b in zip(st, en)]
def layout(name, phases):
    A = adur(name); D = A + LEAD + TAIL
    ws = [len(s) for _, s in phases]; tot = sum(ws); sil = silences(name)
    cuts, acc = [0.0], 0
    for w in ws[:-1]:
        acc += w; g = A * acc / tot
        cand = [x for x in sil if x > cuts[-1] + .6]
        b = min(cand, key=lambda x: abs(x - g)) if cand else g
        cuts.append(b if abs(b - g) < 2.5 else max(g, cuts[-1] + .6))
    edges = [0.0] + [LEAD + c for c in cuts[1:]] + [D]
    return [(fn, edges[i], edges[i + 1] - edges[i]) for i, (fn, _) in enumerate(phases)], D

# impactos: fase -> lista de (fracción, sacudida, destello)
IMP = {'k1': [(.38, 22, .7)], 'k2': [(.1, 14, 0), (.5, 16, 0)], 'k3': [(.35, 14, 0)], 't2': [(.4, 10, 0)], 't3': [(.3, 12, .2)],
       't5': [(.6, 10, 0)], 'u1': [(.6, 10, 0)], 'u3': [(.15, 14, 0)], 'u4': [(.6, 14, 0)], 'u5': [(.75, 10, 0)], 'g1': [(.3, 14, .2)],
       'g3': [(.45, 12, 0)], 'g5': [(.35, 12, 0)], 'c2': [(.25, 12, 0)], 'c4': [(.3, 10, 0)], 'f2': [(.5, 14, .25)], 'f5': [(.6, 12, 0)],
       'f6': [(.5, 10, 0)], 'n1': [(.45, 10, 0)], 'n2': [(.65, 16, .2)], 'n3': [(.45, 12, 0)], 'n5': [(.6, 14, 0)], 'n6': [(.8, 18, .3)],
       'n7': [(.7, 16, .25)]}

def cam(fn, t, d):
    sx = sy = 0.0; fl = 0.0
    for fr, amp, f_ in IMP.get(fn.__name__, []):
        ti = fr * d
        if t >= ti:
            e = math.exp(-(t - ti) * 8); sx += amp * e * math.sin((t - ti) * 67); sy += amp * e * math.cos((t - ti) * 51)
            if f_: fl = max(fl, f_ * math.exp(-(t - ti) * 9))
    return sx, sy, fl

_GR = []
def grain():
    if not _GR:
        r = np.random.default_rng(5)
        for _ in range(4):
            n = (r.random((H // 2, W // 2)) * 255).astype(np.uint8); a = np.dstack([n, n, n, np.full_like(n, 255)]).copy()
            _GR.append((cairo.ImageSurface.create_for_data(memoryview(a), cairo.FORMAT_RGB24, W // 2, H // 2), a))
    return _GR

_CV = []
def canvas_tex():
    """textura de lienzo (trama + fibras) para unificar infografía y óleo."""
    if not _CV:
        from scipy.ndimage import gaussian_filter
        r = np.random.default_rng(9)
        n = r.random((H, W)).astype(np.float32)
        weave = (np.sin(np.arange(W)[None, :] * 1.9) * np.sin(np.arange(H)[:, None] * 1.9)) * .5 + .5
        fib = gaussian_filter(n, (0.6, 6)) * .6 + gaussian_filter(n, (6, 0.6)) * .4
        v = np.clip(.5 + (fib - fib.mean()) * 4 + (weave - .5) * .25, 0, 1)
        g = (v * 255).astype(np.uint8); a = np.dstack([g, g, g, np.full_like(g, 255)]).copy()
        _CV.append((cairo.ImageSurface.create_for_data(memoryview(a), cairo.FORMAT_RGB24, W, H), a))
    return _CV[0][0]

def scene_at(ctx, fn, t, d, zoom=1.0, sx=0.0, sy=0.0, rot=0.0):
    ctx.save(); ctx.translate(W / 2 + sx, H / 2 + sy); ctx.rotate(rot); ctx.scale(zoom, zoom); ctx.translate(-W / 2, -H / 2)
    background(ctx); fn(ctx, t, d); ctx.restore()

def draw(ctx, lay, tb, gt):
    """gt = tiempo global (para deriva de cámara y grano)."""
    i = max(j for j, (_, s, _) in enumerate(lay) if s <= tb or j == 0)
    fn, s, d = lay[i]; t = tb - s
    sx, sy, fl = cam(fn, t, d)
    drift_x = 6 * math.sin(gt * .37); drift_y = 5 * math.sin(gt * .29 + 1); rot = .0025 * math.sin(gt * .21)
    punch = 1 + .045 * math.exp(-t * 7) if i else 1
    if i and t < TR:   # transición: el plano anterior se aleja con zoom y se desvanece
        q = ease(t / TR); pfn, ps, pd = lay[i - 1]
        ctx.push_group(); scene_at(ctx, pfn, pd - .001, pd, 1 + .12 * q, drift_x, drift_y, rot); ctx.pop_group_to_source(); ctx.paint()
        ctx.push_group(); scene_at(ctx, fn, t, d, 1.10 - .10 * q, drift_x, drift_y, rot); ctx.pop_group_to_source(); ctx.paint_with_alpha(q)
        sw = cairo.LinearGradient(-500 + 2900 * q, 0, -100 + 2900 * q, 0)   # barrido de luz
        sw.add_color_stop_rgba(0, 1, 1, 1, 0); sw.add_color_stop_rgba(.5, 1, 1, 1, .14 * (1 - q)); sw.add_color_stop_rgba(1, 1, 1, 1, 0)
        ctx.set_source(sw); ctx.paint()
    else:
        scene_at(ctx, fn, t, d, punch, sx + drift_x, sy + drift_y, rot)
    # luz cálida que se desplaza + grano
    lx = W * (.5 + .45 * math.sin(gt * .11)); g = cairo.RadialGradient(lx, -100, 0, lx, -100, 900)
    g.add_color_stop_rgba(0, 1, .72, .35, .07); g.add_color_stop_rgba(1, 1, .72, .35, 0); ctx.set_source(g); ctx.paint()
    ctx.save(); ctx.scale(2, 2); ctx.set_source_surface(grain()[int(gt * 24) % 4][0], 0, 0); ctx.paint_with_alpha(.035); ctx.restore()
    ctx.save(); ctx.set_operator(cairo.OPERATOR_SOFT_LIGHT); ctx.set_source_surface(canvas_tex(), 0, 0); ctx.paint_with_alpha(.35); ctx.restore()
    if fl > 0: col(ctx, (1, 1, 1), fl); ctx.paint()

def blocks(): return AS.blocks()

def offsets():
    B = blocks(); o = 0.0; out = {}
    for n, p in B:
        lay, D = layout(n, p); out[n] = (o, D, lay); o += D
    return out

def stills(which=None):
    os.makedirs(os.path.join(HERE, 'stills'), exist_ok=True)
    for name, (off, D, lay) in offsets().items():
        if which and name not in which: continue
        for i, (fn, s, d) in enumerate(lay):
            for fr in (.08, .7):
                surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H); ctx = cairo.Context(surf)
                draw(ctx, lay, s + d * fr, off + s + d * fr)
                surf.write_to_png(os.path.join(HERE, 'stills', f'{name}_{i:02d}_{fn.__name__}_{int(fr*100)}.png'))
        print(name, round(D, 1), flush=True)

def render(name):
    off, D, lay = offsets()[name]
    out = os.path.join(HERE, 'parts', name + '.mp4'); tmp = out[:-4] + '.part.mp4'
    n = int(round(D * FPS))
    pr = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgr0', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                           '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '19', '-pix_fmt', 'yuv420p', '-r', str(FPS), tmp], stdin=subprocess.PIPE)
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H); ctx = cairo.Context(surf); t0 = time.time()
    for f in range(n):
        tb = f / FPS; draw(ctx, lay, tb, off + tb); surf.flush(); pr.stdin.write(bytes(surf.get_data()))
    pr.stdin.close()
    if pr.wait() == 0: os.replace(tmp, out)
    print(name, round(D, 1), 's', round(time.time() - t0), 's render', flush=True)

# ------------------------------------------------------------------ sonido
SR = 48000
def place(buf, sig, t0, g=1.0):
    i = int(t0 * SR)
    if i < 0 or i >= len(buf): return
    m = min(len(sig), len(buf) - i); buf[i:i + m] += g * sig[:m]

def audio():
    OFF = offsets(); TOT = sum(v[1] for v in OFF.values())
    n = int(TOT * SR); voice = np.zeros(n); mus = np.zeros(n); sfx = np.zeros(n); rng = np.random.default_rng(4)
    for name, (off, D, lay) in OFF.items():
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', os.path.join(A_DIR, 'audio', name + '.mp3'), '-ac', '1', '-ar', str(SR), '-f', 'f32le', '/tmp/_b.raw'], check=True)
        place(voice, np.fromfile('/tmp/_b.raw', np.float32).astype(np.float64), off + LEAD)
    tt = np.arange(n) / SR
    # música: pad grave + arpegio frío (La menor), cambia de acorde cada 4 compases
    chords = [(110, 130.8, 164.8), (87.3, 130.8, 174.6), (98, 146.8, 196), (82.4, 123.5, 164.8)]
    beat = 60 / 84; bar = beat * 4
    def pluck(f, dur=.9):
        m = int(dur * SR); t_ = np.arange(m) / SR
        return (np.sin(2 * np.pi * f * t_) + .35 * np.sin(2 * np.pi * 2 * f * t_) + .15 * np.sin(2 * np.pi * 3 * f * t_)) * np.exp(-t_ * 3.5) * np.minimum(1, t_ / .004)
    tb = 0.0; k = 0
    while tb < TOT - 2:
        ch = chords[(k // 16) % 4]
        place(mus, pluck(ch[k % 3] * 2 * (2 if k % 8 == 7 else 1)), tb, .10)
        tb += beat / 2; k += 1
    ci = ((tt // (bar * 8)) % 4).astype(int)
    for j in range(3):
        f = np.array([c[j] for c in chords])[ci]
        mus += .035 * np.sin(2 * np.pi * np.cumsum(f) / SR + j)
    m_ = int(.4 * SR)   # bombo suave cada compás desde el bloque 1
    kick = np.sin(2 * np.pi * np.cumsum(45 + 70 * np.exp(-np.arange(m_) / SR * 30)) / SR) * np.exp(-np.arange(m_) / SR * 8)
    tb = OFF['01_tamano'][0]
    while tb < TOT - 3: place(mus, kick, tb, .22); tb += bar / 2
    mus *= np.clip(tt / 3, 0, 1) * np.clip((TOT - tt) / 3, 0, 1)
    def whoosh(dur=.4):
        m = int(dur * SR); w = np.convolve(rng.standard_normal(m), np.ones(40) / 40, 'same'); return w * np.sin(np.pi * np.arange(m) / m) ** 2 * 2
    def thump(dur=.7, f0=48):
        m = int(dur * SR); t_ = np.arange(m) / SR; return np.sin(2 * np.pi * np.cumsum(f0 + 80 * np.exp(-t_ * 22)) / SR) * np.exp(-t_ * 5)
    def brush(dur=1.4):  # pinceladas: ráfagas de ruido filtrado
        m = int(dur * SR); x = np.zeros(m)
        for _ in range(9):
            a = rng.integers(0, m - 6000); L = rng.integers(3000, 6000)
            x[a:a + L] += np.convolve(rng.standard_normal(L), np.ones(12) / 12, 'same') * np.sin(np.pi * np.arange(L) / L)
        return x * .9
    def crack():
        m = int(.6 * SR); x = np.zeros(m); idx = rng.integers(0, m, 120); x[idx] = rng.uniform(-1, 1, 120)
        return np.convolve(x, np.ones(6) / 2, 'same') * np.exp(-np.arange(m) / SR * 4) + .6 * thump(.6, 38)
    wind = np.convolve(rng.standard_normal(n), np.ones(300) / 300, 'same') * 6
    wmask = np.zeros(n)
    for name, (off, D, lay) in OFF.items():
        for fn, s, d in lay:
            t0 = off + s
            if fn.__name__ != 'k1' or name != '00_hook': place(sfx, whoosh(), t0 - .18, .45)
            for fr, amp, f_ in IMP.get(fn.__name__, []): place(sfx, thump(), t0 + fr * d, .5 * amp / 16)
            src = __import__('inspect').getsource(fn) if not fn.__name__.startswith('manim') else ''
            m = re.findall(r"photo\(ctx, '([a-z_]+)'", src)
            if m:
                place(sfx, brush(), t0 + .05, .35)
                if any(x in ICY for x in m):
                    a, b = int(t0 * SR), int((t0 + d) * SR); wmask[a:b] = 1
    k1 = OFF['00_hook'][2][0]; place(sfx, crack(), k1[1] + .45, .9); place(sfx, crack(), k1[1] + 1.6, .7)
    wmask = np.convolve(wmask, np.ones(SR) / SR, 'same'); sfx += wind * wmask * .25
    env = np.convolve(np.abs(voice), np.ones(2400) / 2400, 'same'); duck = 1 - .5 * np.clip(env / .05, 0, 1)
    mix = voice + mus * .55 * duck + sfx * .30
    mix /= max(1e-6, np.abs(mix).max()) / .95
    np.stack([mix, mix], 1).astype(np.float32).tofile('/tmp/_mix.raw')
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', '/tmp/_mix.raw', '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11',
                    '-ar', str(SR), os.path.join(HERE, 'audio', 'mezcla.wav')], check=True)
    print('audio', round(TOT, 1))

def assemble():
    names = list(offsets())
    open(os.path.join(HERE, 'concat.txt'), 'w').write(''.join(f"file 'parts/{n}.mp4'\n" for n in names))
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', 'concat.txt', '-c', 'copy', 'video_only.mp4'], check=True, cwd=HERE)
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', 'video_only.mp4', '-i', 'audio/mezcla.wav', '-map', '0:v', '-map', '1:a', '-c:v', 'copy',
                    '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', 'out/antartida_v2.mp4'], check=True, cwd=HERE)
    print('ok')

if __name__ == '__main__':
    m = sys.argv[1]
    if m == 'stills': stills(sys.argv[2:] or None)
    elif m == 'all':
        for n in (sys.argv[2:] or list(offsets())): render(n)
    elif m == 'audio': audio()
    elif m == 'assemble': assemble()
