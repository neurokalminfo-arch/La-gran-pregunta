# Biología Oculta · motor de vídeo

Motor con el que se hizo el vídeo 1 («¿Por qué unos engordan y otros no, comiendo lo mismo?», https://youtu.be/AKlu6lj-ysE) y sus Shorts. Todo se dibuja con código (Python + skia): estilo pizarra sobre fondo blanco, personajes ilustrados, subtítulos palabra a palabra, música y efectos sintetizados.

## Requisitos
```bash
pip install skia-python numpy pillow      # en entornos gestionados: --break-system-packages
# además: ffmpeg y ffprobe en el PATH
```

## Estructura
```
motor/
├── fonts/            Permanent Marker, Patrick Hand, Anton y Poppins (licencias OFL/Apache)
├── make_brand.py     logo 800×800 y banner 2560×1440 del canal
├── marca/            logo, banner y ficha del canal (descripción, palabras clave)
└── v1/               vídeo 1
    ├── script.py     GUION: bloques → beats (frase, tipo de escena, parámetros, kw, src)
    ├── tts.py        voz ElevenLabs por bloques con marcas de tiempo → audio/*.mp3 + *.json
    ├── timeline.py   une la voz, mete pausas → voice.wav, timeline.json, subtitulos_es.srt
    ├── audio.py      música + whoosh/pop + ducking → mix.wav
    ├── lib.py        primitivas: colores, textos, iconos, gráficas, rotulador, papel
    ├── chars.py      personajes (médico, chico, chica) y cuerpo anatómico
    ├── scenes.py     ~60 escenas animadas; cada una reacciona a las palabras (S.wt("palabra"))
    ├── render.py     cámara, transiciones, palabra clave, subtítulos, botones sociales
    ├── shorts.py     Shorts 1080×1920 a partir de listas de beats del largo
    ├── thumb*.py     miniaturas hechas con código
    └── audio/        voz del vídeo 1 (mp3 + alineación) para poder re-renderizarlo
```

## Flujo para un vídeo nuevo (p. ej. v2)
1. `cp -r v1 v2` y vaciar `v2/audio/`.
2. Escribir el guion en `v2/script.py` (≥ 1.330 palabras ≈ 8 min con la voz de Carlos). Reutilizar escenas de `scenes.py` o añadir nuevas.
3. Voz: `ELEVENLABS_API_KEY=... python3 tts.py` (voz Carlos `QgCtSwnXVKRyDKcdnGOE`, modelo `eleven_v4`). Nunca subir la clave al repositorio.
4. `python3 timeline.py && python3 audio.py`
5. Revisar fotogramas: `python3 render.py stills` → `stills/`.
6. Render completo: `python3 render.py full`. Después se unen las escenas y se añade el audio:
   ```bash
   ls segs/seg_*.mp4 | sort | sed "s/^/file '/; s/$/'/" > concat.txt
   ffmpeg -f concat -safe 0 -i concat.txt -c copy video_only.mp4
   ffmpeg -i video_only.mp4 -i mix.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k \
          -af "loudnorm=I=-14:TP=-1.5:LRA=11" -movflags +faststart video_final.mp4
   ```
7. Shorts: editar la lista `SHORTS` de `shorts.py` (índices de beats + titular) → `python3 shorts.py stills` y luego `python3 shorts.py`.
8. Publicar: subir los mp4 a `biologia-oculta/<tanda>/` de este repositorio. En Metricool, marca **Airnaze** (blogId 7796113), cuyo YouTube es Biología Oculta: Shorts a las 08:00 y a las 20:00, tipo short, no para niños, categoría Educación. Programar solo con el OK del usuario.

## Notas
- Los archivos generados (`segs/`, `stills/`, `*.wav`, `*.mp4`) no se guardan aquí; se regeneran.
- Protocolo editorial y ficha del canal: proyecto «Youtube.» de Claude (`claude/protocolo-curiosidad-youtube.md`, `claude/biologia-oculta-canal.md`).
