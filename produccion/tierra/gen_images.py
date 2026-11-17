import json, base64, urllib.request, concurrent.futures, sys, os
K = open('/home/claude/tierra/.oa_key').read().strip()
STYLE = (" Cinematic documentary photograph, photorealistic, moody low-key lighting, teal and amber color grade, "
         "shallow depth of field, 35mm film look. Absolutely no text, no letters, no logos, no brand names, no watermarks.")
P = {
 'sunrise_west': "Wide landscape at dawn: the Sun rising over a calm sea horizon and rocky coastal cliffs, long golden rays, low mist, a lone lighthouse silhouette.",
 'frozen_coast': "Rugged green Atlantic coastline with steep cliffs and a small fishing harbor, but the sea is covered by thick white sea ice and ice floes all the way to the horizon, snow on the cliffs, overcast winter light, eerie and beautiful.",
 'green_sahara': "Vast Sahara landscape transformed: lush green grassland and acacia woodland, a shallow lake with hippos in the water, red sandstone rock formations in the background, warm late afternoon light.",
 'sahara_dunes': "Endless golden Sahara sand dunes under a harsh midday sun, wind blowing sand off the dune crests, a tiny camel caravan far away for scale.",
 'pampa_fields': "Argentine Pampas: endless flat golden wheat field and green soybean rows under a huge sky with cumulus clouds, a lone windmill water pump and a few cattle.",
 'pampa_desert': "The same flat Argentine Pampas turned into a desert: cracked dry earth and low sand dunes burying a wooden fence, an old rusty windmill water pump standing alone, dust haze, harsh light.",
 'supercomputer': "Inside a modern climate research supercomputer hall: long rows of black server cabinets with blue status lights, cool air haze, one scientist seen from behind looking at a screen with a colorful global weather map.",
 'nebula': "Space art: a young star surrounded by a huge swirling flat disk of gas and dust, the protoplanetary disk spiraling, tiny clumps forming planets, deep space background.",
 'ballerina': "A ballet dancer spinning in a pirouette on a dark stage, arms pulled close to the body, motion blur of the skirt, single warm spotlight.",
 'carousel': "Old children's playground merry-go-round carousel seen from above at a slight angle, spinning with motion blur, a red ball in the air above it, late afternoon park.",
 'rock_art': "Ancient prehistoric rock paintings on a sandstone cliff wall in the Sahara desert: ochre paintings of giraffes, hippos, cattle and human figures, warm side light showing rock texture.",
 'cyano_bloom': "Aerial view of the open ocean with huge swirling blooms of bright turquoise and green cyanobacteria at the surface, patterns like marble, small research ship for scale.",
 'deep_ocean': "Dim deep ocean water, murky green-grey, almost no life, a few small fish struggling near the surface light far above, particles floating, ominous.",
 'venus_sky': "View from a high mountain at night: the planet Venus shining as a very bright point of light low in the twilight sky above the horizon, the crescent Moon nearby, deep blue and amber gradient sky.",
 'thumb_earth': "Planet Earth seen from space, photorealistic, showing Africa and South America: the Sahara region is lush bright green with forests, while Argentina and southern Brazil are bright orange sand desert, dramatic sunlight from the left, black space background; the planet placed on the right half of the frame, empty black space on the left half.",
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
