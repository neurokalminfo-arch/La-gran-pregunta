import json, os, sys, base64, urllib.request, urllib.error
sys.path.insert(0, os.path.dirname(__file__))
from script import BLOCKS

KEY = os.environ.get("ELEVENLABS_API_KEY") or open(os.path.expanduser("~/.secrets/eleven")).read().strip()
VOICE = "QgCtSwnXVKRyDKcdnGOE"
OUT = os.path.join(os.path.dirname(__file__), "audio")
os.makedirs(OUT, exist_ok=True)
MODELS = [m for m in sys.argv[1:]] or ["eleven_v4", "eleven_multilingual_v2"]


def call(text, model):
    body = {"text": text, "model_id": model, "language_code": "es",
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}}
    req = urllib.request.Request(
        f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE}/with-timestamps?output_format=mp3_44100_128",
        data=json.dumps(body).encode(), headers={"xi-api-key": KEY, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=300) as r:
        return json.load(r)


words = 0
for name, beats in BLOCKS:
    text = " ".join(b[0] for b in beats)
    words += len(text.split())
    dst = os.path.join(OUT, f"{name}.json")
    if os.path.exists(dst):
        continue
    last = None
    for m in MODELS:
        try:
            d = call(text, m)
            d["model"] = m
            break
        except urllib.error.HTTPError as e:
            last = e.read().decode()[:300]
            print("fallo", m, last)
    else:
        sys.exit("sin modelo válido: " + str(last))
    open(os.path.join(OUT, f"{name}.mp3"), "wb").write(base64.b64decode(d.pop("audio_base64")))
    d["text"] = text
    json.dump(d, open(dst, "w"), ensure_ascii=False)
    print(name, d["model"], round(d["alignment"]["character_end_times_seconds"][-1], 1), "s")
print("palabras", words)
