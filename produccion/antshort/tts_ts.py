import json, base64, urllib.request
def tts_ts(text, out_mp3, out_json, voice='QgCtSwnXVKRyDKcdnGOE', model='eleven_v4'):
    K = open('/home/claude/video/.xi_key').read().strip()
    body = json.dumps({"text": text, "model_id": model, "language_code": "es",
                       "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}}).encode()
    r = urllib.request.Request(f'https://api.elevenlabs.io/v1/text-to-speech/{voice}/with-timestamps?output_format=mp3_44100_128',
                               data=body, headers={'xi-api-key': K, 'Content-Type': 'application/json'})
    d = json.loads(urllib.request.urlopen(r, timeout=300).read())
    open(out_mp3, 'wb').write(base64.b64decode(d['audio_base64']))
    json.dump(d['alignment'], open(out_json, 'w'))
    return d['alignment']
