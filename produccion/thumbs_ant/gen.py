import json, base64, urllib.request, sys, concurrent.futures
K = open('.oa_key').read().strip()
P = {
 'a_espacio': "Epic cinematic view of planet Earth from space centered on Antarctica: the white ice continent is melting and cracking, huge glowing turquoise waterfalls pour off its edges into the ocean, steam and cracks, the oceans visibly swelling; dramatic rim light from the sun on the left, deep black space, ultra high contrast, saturated teal and orange, YouTube thumbnail style, no text.",
 'b_calle': "Street-level cinematic photo of a wide European city avenue with classic stone buildings and a domed building, completely flooded with seawater up to the third floor, a traffic light and street signs half underwater, a gigantic Antarctic iceberg floating at the end of the avenue towering over the buildings, dramatic storm sky with a sunbeam, ultra high contrast, saturated teal and orange, YouTube thumbnail style, no text, no people.",
 'c_ola': "Dramatic split scene: on the left a colossal Antarctic ice wall collapsing into the sea with an explosion of ice and spray, on the right a modern glass skyscraper half submerged with a bright red waterline mark on its facade, rising water between them, dark stormy sky, ultra high contrast, saturated teal and orange, YouTube thumbnail style, no text, no people.",
}
def gen(k):
    body = json.dumps({"model": "gpt-image-2", "prompt": P[k], "size": "1536x1024", "quality": "high", "n": 1}).encode()
    r = urllib.request.Request('https://api.openai.com/v1/images/generations', data=body, headers={'Authorization': 'Bearer ' + K, 'Content-Type': 'application/json'})
    d = json.loads(urllib.request.urlopen(r, timeout=600).read())
    open(k + '.png', 'wb').write(base64.b64decode(d['data'][0]['b64_json'])); return k
with concurrent.futures.ThreadPoolExecutor(3) as ex:
    for k in ex.map(gen, P): print(k, 'ok', flush=True)
