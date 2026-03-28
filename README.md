# Comfy Content Pipeline

Pipeline para convertir cada `jobs/<id>/visual_manifest.json` en un workflow renderizado de ComfyUI para la fase de imagen con **Qwen Image Edit + Lightning + Next Scene**, dejando separada la fase posterior de video con **WAN 2.2**.

## Rol de cada archivo

- Workflow base editable: `workflows/workflow-comfyui-basic-next-scene-v2.json`
- Workflow renderizado por job: `jobs/<id>/rendered_comfy_workflow.json`
- Entrada editorial por job: `jobs/<id>/visual_manifest.json`

Regla operativa:

- La plantilla que se corrige es el workflow base.
- El archivo que se ejecuta por job es el workflow renderizado.
- No uses como referencia copias viejas de `rendered_comfy_workflow.json` dentro de `images/`.

## Qué hace este proyecto

- Lee `jobs/*/visual_manifest.json`
- Construye el prompt base desde `scene_plan[0].comfy_prompt_base`
- Construye la lista de escenas desde `scene_plan[].comfy_prompt_base`
- Inyecta esos valores en `workflow-comfyui-basic-next-scene-v2.json`
- Guarda `rendered_comfy_workflow.json` dentro de cada job
- Opcionalmente envía el workflow a la API de ComfyUI

## Arquitectura final

### Fase 1: imagen

```text
visual_manifest.json
  -> comfy_prompt_base
  -> Qwen Image Edit + Lightning + Next Scene
  -> images/
```

### Fase 2: video

```text
visual_manifest.json
  -> wan_prompt_base
  -> WAN 2.2
  -> clips/
```

WAN 2.2 no forma parte del workflow base actual de imagen. Debe vivir en otro workflow separado para video.

## Modelos esperados por el workflow base actual

El workflow base actual esta alineado con esta familia:

- `vae/Qwen_Image-VAE.safetensors`
- `text_encoders/qwen_2.5_vl_7b_fp8_scaled.safetensors`
- `diffusion_models/qwen_image_edit_2509_fp8_e4m3fn.safetensors`
- `loras/Qwen-Image-Edit-2509-Lightning-4steps-V1.0-bf16.safetensors`
- `loras/next-scene_lora-v2-3000.safetensors`

No cambies este workflow base a WAN 2.2 ni a GGUF salvo que tambien rediseñes el workflow completo.

## Nodos que modifica el renderer

El renderer actual modifica estos nodos del workflow base:

- Nodo `68`: prompt base de imagen (`TextEncodeQwenImageEditPlus`)
- Nodo `81`: bloque multilinea de escenas (`Text Multiline`)
- Nodo `74`: selector de linea (`Text Load Line From File`)

Implementacion en:

- `src/comfy_pipeline/workflow.py`

Compatibilidad heredada:

- `workflow.py` acepta tambien el nodo legado `45` si reaparece en una variante anterior del workflow.

## Validacion manual en ComfyUI

- El nodo `Text Load Line From File` debe quedarse en indice `0` durante validacion manual.
- El nodo `LoadImage` usa `example.png` desde `ComfyUI/input`.
- La nota del workflow base ya recuerda esta regla.

## Flujo recomendado

### 1. Renderizar jobs sin ejecutar ComfyUI

```bash
python scripts/run_comfy_jobs.py \
  --jobs-root /ruta/a/jobs \
  --workflow /ruta/a/workflow-comfyui-basic-next-scene-v2.json \
  --dry-run
```

### 2. Revisar el workflow renderizado correcto

```text
jobs/<id>/rendered_comfy_workflow.json
```

### 3. Ejecutar ese workflow por job

Si usas el script:

```bash
python scripts/run_comfy_jobs.py \
  --jobs-root /ruta/a/jobs \
  --workflow /ruta/a/workflow-comfyui-basic-next-scene-v2.json \
  --comfy-url http://127.0.0.1:8188 \
  --wait
```

Si haces pruebas manuales en la UI, carga el `rendered_comfy_workflow.json` de la raiz del job, no una copia antigua en `images/`.

## Estructura esperada

```text
jobs/
├── 000001/
│   ├── audio/
│   ├── images/
│   ├── subtitles/
│   ├── brief.json
│   ├── script.json
│   ├── status.json
│   ├── visual_manifest.json
│   └── rendered_comfy_workflow.json
└── 000002/
```

## Estado actual del codigo

- `src/comfy_pipeline/workflow.py` es requerido por `src/comfy_pipeline/orchestrator.py`
- El `dry-run` debe regenerar `rendered_comfy_workflow.json` por job
- La fase `visual_manifest -> rendered workflow` queda separada de la fase WAN 2.2

## Nota sobre API

Este repositorio puede renderizar workflows aunque ComfyUI no este levantado. Si `http://127.0.0.1:8188` no responde, el modo `--dry-run` sigue siendo la forma correcta de validar la plantilla y regenerar los jobs.

# 🖥️ Especificaciones del Sistema

| Componente       | Detalle                                  |
| ---------------- | ---------------------------------------- |
| GPU              | NVIDIA GeForce RTX 4070 (12 GB VRAM)     |
| CPU              | AMD Ryzen 7 5700X (8 núcleos / 16 hilos) |
| RAM              | 32 GB                                    |
| Almacenamiento 1 | SSD 1 TB (Sistema Operativo)             |
| Almacenamiento 2 | SSD / HDD 1 TB (Archivos y proyectos)    |

---

# ⚙️ Capacidades del Equipo

| Área                   | Capacidad                                              |
| ---------------------- | ------------------------------------------------------ |
| IA / LLM local         | Modelos hasta ~7B–13B (optimizados, quantizados)       |
| Generación de imágenes | Excelente (Stable Diffusion, ComfyUI, Qwen Image Edit) |
| Generación de video    | Media–Alta (Wan, AnimateDiff, workflows optimizados)   |
| Procesamiento de audio | Alto rendimiento (WhisperX, TTS)                       |
| Multitarea             | Alta (32 GB RAM permite pipelines complejos)           |
| Render / edición       | Muy bueno (FFmpeg, pipelines automatizados)            |

---

# 🚀 Uso Recomendado del Hardware

## 🔹 GPU (RTX 4070)

- Ideal para:
  - ComfyUI (imágenes + workflows)
  - Modelos diffusion
  - Inferencia LLM ligera (con optimización)
- Evitar:
  - Cargar demasiados modelos simultáneamente (OOM)

## 🔹 CPU (Ryzen 7 5700X)

- Ideal para:
  - Orquestación (Python, scripts)
  - FFmpeg
  - WhisperX en fallback CPU

## 🔹 RAM (32 GB)

- Permite:
  - Pipeline completo (audio + imagen + video)
  - Batch processing
- Límite:
  - Video pesado + múltiples modelos → cuidado

## 🔹 Almacenamiento

- SSD Sistema:
  - OS + entornos (WSL, Python, ComfyUI)
- SSD/HDD Datos:
  - Outputs (videos, imágenes, audio)
  - Modelos IA

---

# 🧠 Arquitectura Recomendada (TU CASO)

````bash
[WSL2 - CPU + RAM]
Guion → TTS → Subtítulos → Orquestación

        ↓

[Windows - GPU RTX 4070]
ComfyUI → Imágenes → Animación

        ↓

[WSL2]
FFmpeg → Render final




##  Modelos esperados por el workflow base actual

El workflow base actual está alineado con esta familia:

- `vae/Qwen_Image-VAE.safetensors`
- `text_encoders/qwen_2.5_vl_7b_fp8_scaled.safetensors`
- `unet/Qwen-Image-Edit-2509-Q3_K_M.gguf`
- `loras/Qwen-Image-Edit-2509-Lightning-4steps-V1.0-bf16.safetensors`
- `loras/next-scene_lora-v2-3000.safetensors`

Notas:
- El workflow ya no usa el diffusion model pesado `qwen_image_edit_2509_fp8_e4m3fn.safetensors`.
- El workflow actual requiere `ComfyUI-GGUF`.
- El modelo GGUF debe ubicarse en `ComfyUI/models/unet/`.

- El workflow base actual fue adaptado para usar GGUF en lugar del modelo pesado safetensors.
- El entorno de ejecución validado usa PyTorch 2.8.0 + CUDA 12.8 en Windows.
- ComfyUI se ejecuta en modo `--lowvram` sobre RTX 4070 12 GB.
- WAS Node Suite y FFmpeg están configurados y operativos.



```text
jobs/000001/visual_manifest.json
   ↓
Python / orquestador
   ↓
rendered_comfy_workflow.json
   ↓
ComfyUI
   ├── Qwen Image Edit
   ├── Lightning
   └── Next Scene
   ↓
images/
   ↓
workflow WAN 2.2
   ↓
clips/
   ↓
FFmpeg
   ↓
video final
```

------------------

## Solo renderizar todos los jobs

```bash
  python scripts\render_jobs_and_prepare.py ^
  --jobs-root C:\Users\vhgal\Documents\desarrollo\ia\neurocontent-engine\jobs ^
  --workflow C:\Users\vhgal\Documents\desarrollo\ia\ia_video_comfy_content_pipeline\workflows\workflow-comfyui-basic-next-scene-v2.json
````

## Solo un job

```bash
  python scripts\render_jobs_and_prepare.py ^
  --jobs-root C:\Users\vhgal\Documents\desarrollo\ia\neurocontent-engine\jobs ^
  --workflow C:\Users\vhgal\Documents\desarrollo\ia\ia_video_comfy_content_pipeline\workflows\workflow-comfyui-basic-next-scene-v2.json ^
  --only-job 000001
```

## Ejecutar en ComfyUI

```bash
  python scripts\render_jobs_and_prepare.py ^
  --jobs-root C:\Users\vhgal\Documents\desarrollo\ia\neurocontent-engine\jobs ^
  --workflow C:\Users\vhgal\Documents\desarrollo\ia\ia_video_comfy_content_pipeline\workflows\workflow-comfyui-basic-next-scene-v2.json ^
  --execute ^
  --wait
```


## video-dataset


```text

C:\Users\vhgal\Documents\desarrollo\ia\AI-video-automation\video-dataset

video-dataset/
├── jobs/
│   └── 000001/
│       ├── job.json
│       ├── status.json
│       ├── source/
│       │   ├── 000001_brief.json
│       │   ├── 000001_script.json
│       │   ├── 000001_visual_manifest.json
│       │   └── 000001_rendered_comfy_workflow.json
│       ├── audio/
│       │   └── 000001_narration.wav
│       ├── subtitles/
│       │   └── 000001_narration.srt
│       ├── images/
│       │   ├── scene_001.png
│       │   ├── scene_003.png
│       │   └── previews/
│       ├── videos/
│       │   ├── scene_002.mp4
│       │   └── previews/
│       ├── logs/
│       │   ├── 000001_phase_editorial.log
│       │   ├── 000001_phase_audio.log
│       │   └── 000001_phase_subtitles.log
│       ├── timeline/
│       │   └── vertical/
│       └── output/
│           └── vertical/
└── voices/
    ├── voice_global_0001/
    │   ├── voice.json
    │   ├── reference.wav
    │   ├── reference.txt
    │   └── voice_clone_prompt.json
    └── voices_index.json

```