"""Repinta las fotos de referencia como óleo empastado (claude-drawing / OilPainting), guardando las fases."""
import sys, os, time
sys.path.insert(0, os.path.expanduser('~/.claude/skills/claude-drawing/lib'))
import numpy as np
from PIL import Image, ImageFilter
from oilpaint import OilPainting

def paint(name, src, seed=1, out_dir='plates', stage_dir='stages'):
    im = Image.open(src).convert('RGB')
    r = max(1920 / im.width, 1080 / im.height); im = im.resize((round(im.width * r), round(im.height * r)), Image.LANCZOS)
    x0 = (im.width - 1920) // 2; y0 = (im.height - 1080) // 2; im = im.crop((x0, y0, x0 + 1920, y0 + 1080))
    from PIL import ImageEnhance
    im = ImageEnhance.Color(im).enhance(1.35); im = ImageEnhance.Contrast(im).enhance(1.12)
    ref = np.asarray(im).astype(np.float32) / 255.0
    g = np.asarray(im.convert('L').filter(ImageFilter.GaussianBlur(6))).astype(np.float32)
    gy, gx = np.gradient(g)
    # tensor de estructura suavizado -> dirección de los trazos a lo largo de los contornos
    from scipy.ndimage import gaussian_filter
    def blur(a, r=14): return gaussian_filter(a.astype(np.float32), r)
    jxx, jyy, jxy = blur(gx * gx), blur(gy * gy), blur(gx * gy)
    ang = 0.5 * np.arctan2(2 * jxy, jxx - jyy) + np.pi / 2
    o = OilPainting(1920, 1080, seed=seed)
    o.layer(ref, ang, length=(80, 140), width=(30, 44), density=2.6, value_jitter=0.02); o.stage('boceto')
    o.layer(ref, ang, length=(40, 70), width=(14, 22), density=2.0, value_jitter=0.03); o.stage('base')
    o.layer(ref, ang, length=(20, 38), width=(7, 11), density=1.9, value_jitter=0.04); o.stage('trazos')
    edge = np.clip(np.hypot(gx, gy) / 12, 0, 1); edge = blur(edge.astype(np.float32), 8); edge = (edge > .08).astype(np.float32)
    o.layer(ref, ang, length=(8, 18), width=(3, 5), density=1.6, value_jitter=0.04, mask=edge); o.stage('detalle')
    sd = os.path.join(stage_dir, name); os.makedirs(sd, exist_ok=True)
    o.save(os.path.join(out_dir, name + '.png'), stages_dir=sd)

if __name__ == '__main__':
    t0 = time.time()
    for n in sys.argv[1:]:
        paint(n, f'/home/claude/antartida/img/{n}.png'); print(n, round(time.time() - t0), 's', flush=True)
