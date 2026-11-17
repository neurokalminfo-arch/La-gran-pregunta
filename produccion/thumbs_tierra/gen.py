import json, base64, urllib.request, sys, concurrent.futures
K = open('.oa_key').read().strip()
P = {
 'v1_split': "Dramatic split-screen image divided by a jagged diagonal crack from top-right to bottom-left. LEFT HALF: a classic European coastal city with stone buildings and a cathedral completely frozen solid, thick ice and huge icicles hanging from balconies, the harbor sea frozen into white ice with trapped boats, blizzard, glowing icy blue light. RIGHT HALF: a wide South American city avenue with a tall white obelisk half buried under enormous orange sand dunes, scorching sun, heat haze, cracked dry earth, buildings swallowed by sand. Extreme contrast between freezing blue and burning orange, ultra cinematic, hyper detailed, YouTube thumbnail style, no text, no people.",
 'v2_planeta': "Planet Earth seen from space, close and huge, filling the frame, with a giant glowing red curved arrow around it showing it spinning the wrong way. Europe is completely covered in thick white ice and snow with frozen seas, while Argentina and southern Brazil are bright orange sand desert, the Sahara is lush green. Dramatic sunlight, deep black space, extreme saturation and contrast, ultra cinematic, YouTube thumbnail style, no text.",
 'v3_hombre': "A lone small human silhouette standing exactly on a sharp border line between two worlds: on the left an endless frozen European landscape with a frozen sea, icebergs and a snowstorm in icy blue light; on the right an endless burning orange desert of huge dunes with a half-buried windmill and fence posts under a blazing sun. The border line runs vertically through the center. Epic scale, extreme contrast blue versus orange, ultra cinematic, YouTube thumbnail style, no text.",
}
def gen(k):
    body = json.dumps({"model": "gpt-image-2", "prompt": P[k], "size": "1536x1024", "quality": "high", "n": 1}).encode()
    r = urllib.request.Request('https://api.openai.com/v1/images/generations', data=body, headers={'Authorization': 'Bearer ' + K, 'Content-Type': 'application/json'})
    d = json.loads(urllib.request.urlopen(r, timeout=600).read())
    open(k + '.png', 'wb').write(base64.b64decode(d['data'][0]['b64_json'])); return k
with concurrent.futures.ThreadPoolExecutor(3) as ex:
    for k in ex.map(gen, P): print(k, 'ok', flush=True)
