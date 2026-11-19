"""Une la locución por bloques, mete pausas entre frases y escribe timeline.json + voice.wav + subtítulos .srt."""
import json, os, subprocess, sys, re
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from script import BLOCKS

D = os.path.dirname(os.path.abspath(__file__))
SR = 44100
GAP_BEAT, GAP_BLOCK, LEAD, TAIL = 0.30, 0.55, 0.35, 3.0


def load(mp3):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", mp3, "-f", "s16le", "-ac", "1", "-ar", str(SR), "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.int16).astype(np.float32) / 32768


out = [np.zeros(int(LEAD * SR), np.float32)]
t = LEAD
beats = []
for bi, (name, bl) in enumerate(BLOCKS):
    a = json.load(open(f"{D}/audio/{name}.json"))
    al = a["alignment"]; text = a["text"]; cs, ce = al["character_start_times_seconds"], al["character_end_times_seconds"]
    chars = "".join(al["characters"])
    assert chars == text, (name, len(chars), len(text))
    audio = load(f"{D}/audio/{name}.mp3")
    offs, o = [], 0
    for b in bl:
        o = text.index(b[0], o); offs.append(o); o += len(b[0])
    cuts = [0.0]
    for k in range(1, len(bl)):
        prev_end = ce[offs[k] - 2] if offs[k] >= 2 else 0
        cuts.append((prev_end + cs[offs[k]]) / 2)
    cuts.append(len(audio) / SR)
    for k, b in enumerate(bl):
        s0, s1 = cuts[k], cuts[k + 1]
        seg = audio[int(s0 * SR):int(s1 * SR)]
        # palabras con tiempo absoluto
        words = []
        for m in re.finditer(r"\S+", b[0]):
            ci = offs[k] + m.start()
            words.append([m.group(), round(t + cs[ci] - s0, 3), round(t + ce[offs[k] + m.end() - 1] - s0, 3)])
        gap = GAP_BLOCK if k == len(bl) - 1 else GAP_BEAT
        dur = len(seg) / SR + gap
        if bi == len(BLOCKS) - 1 and k == len(bl) - 1:
            gap += TAIL; dur += TAIL
        beats.append({"block": name, "i": k, "text": b[0], "kind": b[1], "p": b[2],
                      "start": round(t, 3), "dur": round(dur, 3), "words": words})
        out += [seg, np.zeros(int(gap * SR), np.float32)]
        t += dur

voice = np.concatenate(out)
import wave
with wave.open(f"{D}/voice.wav", "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(voice, -1, 1) * 32767).astype(np.int16).tobytes())
json.dump(beats, open(f"{D}/timeline.json", "w"), ensure_ascii=False, indent=0)


# subtítulos .srt: trozos de ≤ 7 palabras sin cruzar frases
def ts(x):
    h, r = divmod(x, 3600); m, s = divmod(r, 60)
    return f"{int(h):02d}:{int(m):02d}:{int(s):02d},{int(round((s % 1) * 1000)) % 1000:03d}"


lines, n = [], 1
for b in beats:
    ws = b["words"]
    chunk = []
    for i, w in enumerate(ws):
        chunk.append(w)
        if len(chunk) >= 7 or w[0][-1] in ".?!:" or i == len(ws) - 1:
            lines.append(f"{n}\n{ts(chunk[0][1])} --> {ts(chunk[-1][2] + 0.15)}\n{' '.join(c[0] for c in chunk)}\n")
            n += 1; chunk = []
open(f"{D}/subtitulos_es.srt", "w").write("\n".join(lines))
print("beats", len(beats), "duración", round(t, 1), "s =", f"{int(t // 60)}:{int(t % 60):02d}")
print("más largo", max(beats, key=lambda b: b["dur"])["dur"])
