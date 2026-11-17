import json, base64, urllib.request, concurrent.futures, sys, os
K = open('/home/claude/antartida/.oa_key').read().strip()
STYLE = (" Cinematic documentary photograph, photorealistic, moody low-key lighting, teal and amber color grade, "
         "shallow depth of field, 35mm film look. Absolutely no text, no letters, no logos, no brand names, no watermarks.")
P = {
 'ice_cliff': "Huge Antarctic glacier ice cliff rising from a dark calm sea, blue cracks and crevasses, chunks of ice falling into the water, small icebergs, cold low sun, dramatic scale.",
 'ice_aerial': "Aerial view over the endless flat white Antarctic ice sheet, mountain peaks barely poking through the ice, sastrugi wind patterns, pale blue sky, sense of immense emptiness.",
 'low_sea_cliff': "Antarctic ice wall seen from a low boat: a wide band of wet dark exposed ice and rock along the base of the cliff, as if the sea level had dropped several meters, tide-like marks, overcast light.",
 'bare_antarctica': "Antarctica without ice: vast rugged brown and grey rocky mountains and valleys, meltwater lakes, a few remaining patches of snow on peaks, a new sea channel cutting through, low polar sun.",
 'madrid_gate': "A grand neoclassical granite triumphal arch with five openings in the middle of a sunny city roundabout with gardens and blurred traffic, dry streets, summer afternoon, Madrid-like architecture.",
 'obelisk_flood': "A tall white obelisk in a wide city avenue that is completely flooded by calm sea water up to the first floors of the surrounding buildings, overcast sky, eerie silence, no people.",
 'polar_forest': "Cretaceous temperate rainforest near the South Pole: tall conifers and tree ferns, mossy ground, a misty river, very low golden sun on the horizon, prehistoric atmosphere.",
 'drill_ship': "A red-hulled polar research icebreaker ship in icy Antarctic waters with a drilling rig on deck, scientists in orange suits seen from far away, grey sky, floating sea ice.",
 'deep_current': "Deep ocean abyss in dark blue, glowing streams of cold water flowing along the sea floor like rivers of light, tiny particles, a few deep-sea creatures.",
 'seymour_fossils': "Fossil bones of a giant prehistoric penguin and ammonite shells lying on cold brown rocky ground on an Antarctic island, snow patches, scientist's brush and field notebook nearby.",
 'thwaites': "Aerial view of a massive Antarctic glacier front breaking apart: a fractured ice shelf with long rifts and a huge iceberg drifting away into dark water, dramatic.",
 'thumb_flood': "A modern coastal city skyline sunk in the sea up to the 20th floor, calm water reflecting towers, a huge Antarctic iceberg floating in the foreground on the left, dramatic cold teal light; empty space on the left upper third.",
}
def gen(name):
    out = f'img/{name}.png'
    if os.path.exists(out): return name, 'exists'
    body = {"model": "gpt-image-2", "prompt": P[name] + STYLE, "size": "1536x1024",
            "quality": "high" if name.startswith('thumb') else "medium", "n": 1}
    r = urllib.request.Request('https://api.openai.com/v1/images/generations', data=json.dumps(body).encode(),
        headers={'Authorization': f'Bearer {K}', 'Content-Type': 'application/json'})
    try:
        d = json.load(urllib.request.urlopen(r, timeout=300))
    except urllib.error.HTTPError as e:
        return name, f'HTTP {e.code} {e.read()[:300]}'
    open(out, 'wb').write(base64.b64decode(d['data'][0]['b64_json']))
    return name, 'ok'
names = sys.argv[1:] or list(P)
with concurrent.futures.ThreadPoolExecutor(5) as ex:
    for n, s in ex.map(gen, names): print(n, s, flush=True)
