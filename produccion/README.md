# Producción de La Gran Pregunta

Código con el que se hacen los vídeos del canal: animación por código (pycairo + ffmpeg), voz de ElevenLabs con tiempos por palabra, música y efectos sintetizados con numpy, y escenas de Manim.

## Carpetas

| Carpeta | Qué es |
| --- | --- |
| `video/` | Librería base: `lib.py` (fuentes, colores, easing), `scenes.py`, `thumb.py` (miniaturas), `tts.py`, `srt.py` |
| `tierra/` | Vídeo largo «¿Qué pasaría si la Tierra girara al revés?» (globo ortográfico `oglobe`, `spin_arrow`, mapas) |
| `antartida/` | Vídeo largo de la Antártida, versión 1 |
| `antartida2/` | Antártida v2 (la publicada): fondos pintados al óleo (`paint.py`), Manim (`manim/escenas.py`), render con transiciones y grano (`render2.py`) |
| `apagon2/` | Short 9:16 del apagón: subtítulos karaoke palabra a palabra, impactos y cámara (`render.py`, `tts_ts.py`) |
| `antshort/` | Short de la Antártida, montado con piezas de `apagon2` |
| `thumbs_ant/`, `thumbs_tierra/` | Miniaturas con GPT Image 2 + texto (`gen.py`, `compose.py`) |
| `mascota/` | Prueba del estilo 2D plano con la mascota del canal (`anim.py`: `stills`, `audio`, `video`) |

## Instalación

```bash
sudo apt install ffmpeg libcairo2-dev pkg-config        # macOS: brew install ffmpeg cairo pkg-config
pip install pycairo numpy scipy pillow manim
```

Fuente: Inter Display (Black, ExtraBold, SemiBold, Medium) instalada en el sistema.

**Rutas:** los scripts usan rutas absolutas `/home/claude/...` (donde se crearon). Al pasarlo a Claude Code, pídele: «cambia las rutas `/home/claude/` por la carpeta de este repo».

## Claves (nunca en el repo)

- ElevenLabs: archivo `video/.xi_key` (una línea con la clave). Voz «Carlos» `QgCtSwnXVKRyDKcdnGOE`, modelo `eleven_v4`, stability 0.5, similarity 0.75, idioma `es`.
- OpenAI (miniaturas): archivo `.oa_key` junto a `gen.py`.

`.gitignore` ya excluye `.xi_key` y `.oa_key`.

## Flujo de un Short (ej. `apagon2/`)

1. `script.py`: texto (≤170 palabras, plantilla del protocolo).
2. `tts_ts.py`: voz + `audio/align.json` (tiempos por carácter).
3. `python3 render.py stills` → revisar hoja de fotogramas.
4. `python3 render.py audio && python3 render.py video` → MP4 9:16.
5. Comprimir a < 100 MB, subir a este repo y programar en Metricool (YouTube, Instagram, Facebook) **solo tras el OK del dueño del canal**.
