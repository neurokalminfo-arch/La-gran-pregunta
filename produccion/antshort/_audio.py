
# ------------------------------------------------------------------ audio
SR = 48000
def place(buf, sig, t0, g=1.0):
    i = int(t0 * SR)
    if i >= len(buf) or i < 0: return
    n = min(len(sig), len(buf) - i); buf[i:i + n] += g * sig[:n]

def audio():
    n = int(DUR * SR); mus = np.zeros(n); sfx = np.zeros(n); rng = np.random.default_rng(2)
    beat = 60 / 96; tt = np.arange(n) / SR
    def kick():
        m = int(.35 * SR); t_ = np.arange(m) / SR; f = 48 + 90 * np.exp(-t_ * 35)
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t_ * 9)
    def hat():
        m = int(.05 * SR); return rng.standard_normal(m) * np.exp(-np.arange(m) / SR * 80) * .22
    def pluck(f, dur=.5):
        m = int(dur * SR); t_ = np.arange(m) / SR
        return (np.sin(2 * np.pi * f * t_) + .4 * np.sin(2 * np.pi * 2 * f * t_)) * np.exp(-t_ * 5) * np.minimum(1, t_ / .005)
    notes = [220, 261.6, 329.6, 293.7, 220, 196, 246.9, 261.6]   # arpegio frío (La menor)
    tb = PH[1][1]; i = 0
    while tb < DUR - .8:
        place(mus, kick(), tb, .5)
        place(mus, hat(), tb + beat / 2, .5)
        place(mus, pluck(notes[i % 8]), tb, .18); place(mus, pluck(notes[(i + 2) % 8] * 2, .3), tb + beat / 2, .08)
        tb += beat; i += 1
    pad = .05 * (np.sin(2 * np.pi * 110 * tt) + np.sin(2 * np.pi * 164.8 * tt + 1) + .7 * np.sin(2 * np.pi * 220.5 * tt))
    pad *= np.minimum(1, tt / 2.5); mus += pad
    mus *= np.clip((DUR - tt) / 1.0, 0, 1)
    def thump(dur=.6, f0=55):
        m = int(dur * SR); t_ = np.arange(m) / SR; f = f0 + 80 * np.exp(-t_ * 20)
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t_ * 5)
    def whoosh(dur=.3):
        m = int(dur * SR); w = np.convolve(rng.standard_normal(m), np.ones(30) / 30, 'same'); return w * np.sin(np.pi * np.arange(m) / m) ** 2 * 1.8
    def wash(dur=1.6):   # agua subiendo
        m = int(dur * SR); w = np.convolve(rng.standard_normal(m), np.ones(60) / 60, 'same'); t_ = np.arange(m) / m
        return w * np.sin(np.pi * t_) * 2.5
    def crack():
        m = int(.5 * SR); x = np.zeros(m); idx = rng.integers(0, m, 90); x[idx] = rng.uniform(-1, 1, 90)
        return np.convolve(x, np.ones(8) / 2, 'same') * np.exp(-np.arange(m) / SR * 4) + thump(.5, 40)[:m] * .6
    def tick():
        m = int(.03 * SR); t_ = np.arange(m) / SR; return np.sin(2 * np.pi * 1800 * t_) * np.exp(-t_ * 120)
    place(sfx, crack(), wt('globe', 'derritiera'), .9)
    for ti, amp, fl in IMPACTS: place(sfx, thump(), ti, .6 * amp / 18)
    for p in PH[1:]: place(sfx, whoosh(), p[1] - .12, .35)
    for key in ('rise', 'cities', 'five', 'spain', 'world'):
        p = next(x for x in PH if x[0] == key); place(sfx, wash(), p[1] + .1, .5)
    tn = wt('nasa', 'ciento')
    for i in range(14): place(sfx, tick(), tn + i * .1, .3)
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', os.path.join(HERE, 'audio', 'voz.mp3'), '-ac', '1', '-ar', str(SR), '-f', 'f32le', '/tmp/_v.raw'], check=True)
    v = np.fromfile('/tmp/_v.raw', np.float32).astype(np.float64); voice = np.zeros(n); place(voice, v, V0)
    envv = np.convolve(np.abs(voice), np.ones(2400) / 2400, 'same'); duck = 1 - .55 * np.clip(envv / .05, 0, 1)
    m_ = voice + mus * .22 * duck + sfx * .35
    m_ /= max(1e-6, np.max(np.abs(m_))) / .95
    np.stack([m_, m_], 1).astype(np.float32).tofile('/tmp/_m.raw')
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', '/tmp/_m.raw',
                    '-af', 'loudnorm=I=-14:TP=-1.5', '-ar', str(SR), os.path.join(HERE, 'audio', 'mezcla.wav')], check=True)
    print('audio ok', round(DUR, 1))
