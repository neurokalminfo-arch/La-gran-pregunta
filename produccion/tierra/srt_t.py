import sys, re, os, json
sys.path.append('/home/claude/video')
import narration
from render_t import adur, silences, LEAD
def chunks(s, maxc=84):
    if len(s) <= maxc: return [s]
    parts = re.split(r'(?<=[,…:.])\s+', s); out, cur = [], ''
    for p in parts:
        if len(cur) + len(p) + 1 > maxc and cur: out.append(cur); cur = p
        else: cur = (cur + ' ' + p).strip()
    out.append(cur); return out
def ts(x):
    h, r = divmod(x, 3600); m, s = divmod(r, 60)
    return f"{int(h):02d}:{int(m):02d}:{int(s):02d},{int(round((s % 1) * 1000)) % 1000:03d}"
offs = json.load(open('offsets.json')); items = []
for name, texts in narration.BLOCKS:
    A = adur(name); sil = silences(name); off = offs[name][0]
    segs = []
    for s in re.split(r'(?<=[.?!])\s+(?=[A-ZÁÉÍÓÚ¿])', ' '.join(texts)): segs += chunks(s.strip())
    tot = sum(len(s) for s in segs); cuts, acc = [0.0], 0
    for s in segs[:-1]:
        acc += len(s); g = A * acc / tot
        cand = [x for x in sil if x > cuts[-1] + .3]
        b = min(cand, key=lambda x: abs(x - g)) if cand else g
        cuts.append(b if abs(b - g) < 2 else max(g, cuts[-1] + .4))
    cuts.append(A)
    for i, s in enumerate(segs): items.append((off + LEAD + cuts[i], off + LEAD + cuts[i + 1] - .05, s))
with open('out/tierra_al_reves_subtitulos.srt', 'w') as f:
    for i, (a, b, s) in enumerate(items, 1): f.write(f"{i}\n{ts(a)} --> {ts(b)}\n{s}\n\n")
print(len(items))
