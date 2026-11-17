import sys, os, concurrent.futures
sys.path.insert(0, '/home/claude/video')
from tts import tts
import narration
V = 'QgCtSwnXVKRyDKcdnGOE'
def go(b):
    name, ph = b; out = f'audio/{name}.mp3'
    if os.path.exists(out) and len(sys.argv) < 2: return name, 'exists'
    tts(' '.join(ph), out, V); return name, 'ok'
sel = [b for b in narration.BLOCKS if len(sys.argv) < 2 or b[0] in sys.argv[1:]]
with concurrent.futures.ThreadPoolExecutor(3) as ex:
    for r in ex.map(go, sel): print(*r, flush=True)
