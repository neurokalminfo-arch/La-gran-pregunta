import json, sys, urllib.request
K = open('/home/claude/video/.xi_key').read().strip()
def tts(text, out, voice, model='eleven_v4', stability=0.5, similarity=0.75):
    body = json.dumps({"text": text, "model_id": model, "language_code": "es",
                       "voice_settings": {"stability": stability, "similarity_boost": similarity}}).encode()
    r = urllib.request.Request(f'https://api.elevenlabs.io/v1/text-to-speech/{voice}?output_format=mp3_44100_128',
                               data=body, headers={'xi-api-key': K, 'Content-Type': 'application/json'})
    try:
        data = urllib.request.urlopen(r, timeout=300).read()
    except urllib.error.HTTPError as e:
        raise SystemExit(f'HTTP {e.code}: {e.read()[:400]}')
    open(out, 'wb').write(data)
if __name__ == '__main__':
    tts(sys.argv[1], sys.argv[2], sys.argv[3])
