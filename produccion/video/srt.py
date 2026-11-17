"""Build an .srt for the full video from per-block audio + sentence/pause alignment."""
import json, os, re, subprocess
import scenes
from render import silences, LEAD, block_duration

HERE = os.path.dirname(os.path.abspath(__file__))
N = json.load(open(os.path.join(HERE, 'narration.json')))

def adur(p):
    return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', p],
                                capture_output=True, text=True).stdout)

def chunks(s, maxc=84):
    """Split sentence into subtitle-sized pieces at commas/ellipses if long."""
    if len(s) <= maxc: return [s]
    parts = re.split(r'(?<=[,…:—.])\s+', s)
    out, cur = [], ''
    for p in parts:
        if len(cur) + len(p) + 1 > maxc and cur:
            out.append(cur); cur = p
        else:
            cur = (cur + ' ' + p).strip()
    out.append(cur)
    return out

def ts(x):
    h, r = divmod(x, 3600); m, s = divmod(r, 60)
    return f"{int(h):02d}:{int(m):02d}:{int(s):02d},{int(round((s % 1) * 1000)) % 1000:03d}"

def main():
    off, items = 0.0, []
    for name, phases in scenes.BLOCKS:
        ap = os.path.join(HERE, 'audio', name + '.mp3')
        A = adur(ap); sil = silences(ap)
        segs = []
        for s in re.split(r'(?<=[.?!])\s+(?=[A-ZÁÉÍÓÚ¿])', N[name]):
            segs += chunks(s.strip())
        tot = sum(len(s) for s in segs)
        cuts, acc = [0.0], 0
        for s in segs[:-1]:
            acc += len(s); g = A * acc / tot
            cand = [x for x in sil if x > cuts[-1] + 0.3]
            b = min(cand, key=lambda x: abs(x - g)) if cand else g
            cuts.append(b if abs(b - g) < 2 else max(g, cuts[-1] + 0.4))
        cuts.append(A)
        for i, s in enumerate(segs):
            items.append((off + LEAD + cuts[i], off + LEAD + cuts[i + 1] - 0.05, s))
        off += block_duration(name, phases)
    out = os.path.join(HERE, 'out', 'guerra_nuclear_subtitulos.srt')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, 'w') as f:
        for i, (a, b, s) in enumerate(items, 1):
            f.write(f"{i}\n{ts(a)} --> {ts(b)}\n{s}\n\n")
    print(len(items), 'subs')

if __name__ == '__main__':
    main()
