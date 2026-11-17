def stills(ts):
    from PIL import Image
    ims = []
    for t in ts:
        surf = cairo.ImageSurface(cairo.FORMAT_RGB24, SW, SH); ctx = cairo.Context(surf); frame(ctx, t)
        surf.write_to_png('/tmp/_s.png'); ims.append(Image.open('/tmp/_s.png').resize((216, 384)))
    cols = 8; S = Image.new('RGB', (216 * cols, 404 * ((len(ims) + cols - 1) // cols)), 'white')
    from PIL import ImageDraw; d = ImageDraw.Draw(S)
    for i, (im, t) in enumerate(zip(ims, ts)):
        x, y = (i % cols) * 216, (i // cols) * 404; S.paste(im, (x, y)); d.text((x + 4, y + 386), f'{t:.1f}s', fill='black')
    S.save(os.path.join(HERE, 'sheet.png'))

def video():
    out = os.path.join(HERE, 'out', 'short_antartida_9x16.mp4'); nfr = int(DUR * FPS)
    enc = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgr0', '-s', f'{SW}x{SH}', '-r', str(FPS), '-i', '-',
                            '-i', os.path.join(HERE, 'audio', 'mezcla.wav'), '-map', '0:v', '-map', '1:a',
                            '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k',
                            '-shortest', '-movflags', '+faststart', out], stdin=subprocess.PIPE)
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, SW, SH); ctx = cairo.Context(surf); t0 = time.time()
    for f in range(nfr):
        frame(ctx, f / FPS); surf.flush(); enc.stdin.write(bytes(surf.get_data()))
    enc.stdin.close(); enc.wait(); print('video', out, round(time.time() - t0), 's')

if __name__ == '__main__':
    m = sys.argv[1]
    if m == 'stills':
        ts = [float(x) for x in sys.argv[2:]] or [p[1] + p[5] * .7 for p in PH]
        stills(ts)
    elif m == 'audio': audio()
    elif m == 'video': video()
    elif m == 'info':
        for p in PH: print(f'{p[0]:8s} {p[1]:6.2f} {p[5]:5.2f}')
        print('DUR', DUR, 'blackout', BLACKOUT)
