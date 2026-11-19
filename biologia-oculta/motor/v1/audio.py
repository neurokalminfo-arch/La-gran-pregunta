"""Música de fondo + efectos sintetizados y mezcla con la voz → mix.wav"""
import json, os, re, wave
import numpy as np

D = os.path.dirname(os.path.abspath(__file__))
SR = 44100
beats = json.load(open(f"{D}/timeline.json"))
with wave.open(f"{D}/voice.wav") as w:
    voice = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
N = len(voice); T = N / SR
rng = np.random.default_rng(5)


def env(n, a=.005, r=.4):
    t = np.arange(n) / SR
    return np.minimum(1, t / a) * np.exp(-t / r)


def note(f, dur, kind="pluck", vol=.2):
    n = int(dur * SR); t = np.arange(n) / SR
    if kind == "pluck":
        s = (np.sin(2 * np.pi * f * t) + .35 * np.sin(4 * np.pi * f * t) + .12 * np.sin(6 * np.pi * f * t)) * env(n, .004, .35)
    else:  # pad
        s = sum(np.sin(2 * np.pi * f * d * t + p) for d, p in ((1, 0), (1.004, 1), (.996, 2), (2, .5))) / 4
        s *= np.minimum(1, t / .8) * np.minimum(1, (dur - t) / .8)
    return s * vol


def midi(m):
    return 440 * 2 ** ((m - 69) / 12)


music = np.zeros(N + SR * 4, np.float32)
bpm = 96; beat = 60 / bpm; bar = beat * 4
chords = [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]]  # Am F C G
arp = [0, 1, 2, 1, 2, 0, 1, 2]
t = 0.0; bi = 0
while t < T + 2:
    ch = chords[bi % 4]
    pad = sum(note(midi(m - 12), bar + .6, "pad", .05) for m in ch)
    i0 = int(t * SR); music[i0:i0 + len(pad)] += pad[:len(music) - i0]
    for k in range(8):
        tt = t + k * beat / 2
        m = ch[arp[k]] + (12 if k in (3, 7) else 0)
        nn = note(midi(m + 12), .6, "pluck", .045 if k % 2 else .06)
        j = int(tt * SR); music[j:j + len(nn)] += nn[:len(music) - j]
    # bombo suave
    for k in range(4):
        j = int((t + k * beat) * SR); n = int(.25 * SR); tk = np.arange(n) / SR
        kick = np.sin(2 * np.pi * (55 + 60 * np.exp(-tk * 30)) * tk) * np.exp(-tk * 12) * .12
        music[j:j + n] += kick[:len(music) - j]
    t += bar; bi += 1
music = music[:N]
fade = np.ones(N); fl = int(3 * SR); fade[-fl:] = np.linspace(1, 0, fl); fade[:int(SR)] = np.linspace(0, 1, int(SR))
music *= fade

sfx = np.zeros(N + SR, np.float32)


def add(sig, at):
    j = int(at * SR)
    if 0 <= j < len(sfx):
        sfx[j:j + len(sig)] += sig[:len(sfx) - j]


def whoosh():
    n = int(.45 * SR); x = rng.normal(0, 1, n)
    # ruido filtrado con barrido (media móvil variable)
    out = np.zeros(n); acc = 0.0
    for i in range(n):
        a = .02 + .25 * (i / n)
        acc += a * (x[i] - acc); out[i] = acc
    e = np.sin(np.linspace(0, np.pi, n)) ** 2
    return out * e * .5


def pop():
    n = int(.12 * SR); tt = np.arange(n) / SR
    return np.sin(2 * np.pi * (900 - 2500 * tt) * tt) * np.exp(-tt * 40) * .25


WH, PO = whoosh(), pop()
for b in beats:
    add(WH * (.6 if b["i"] else 1.0), max(0, b["start"] - .12))
    kw = b["p"].get("kw")
    if kw:
        tok = re.sub(r"[^\wáéíóúñ]", "", kw.split()[0].lower())[:5]
        for w in b["words"]:
            if re.sub(r"[^\wáéíóúñ]", "", w[0].lower()).startswith(tok):
                add(PO, max(0, w[1] - .1)); break
        else:
            add(PO, b["start"] + 1.0)
sfx = sfx[:N]

# ducking: la música baja cuando hay voz
vol = np.convolve(np.abs(voice), np.ones(2205) / 2205, "same")
duck = np.where(vol > .01, .55, 1.0)
duck = np.convolve(duck, np.ones(4410) / 4410, "same")
mix = voice * 1.0 + music * duck * .55 + sfx * .35
mix /= max(1.0, np.abs(mix).max() / .95)
st = np.stack([mix, mix], 1)
with wave.open(f"{D}/mix.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((st * 32767).astype(np.int16).tobytes())
print("mix ok", round(T, 1), "s")
