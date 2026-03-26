# Comfy Content Pipeline

Pipeline para convertir cada `jobs/<id>/visual_manifest.json` en un workflow ejecutable de ComfyUI, generar imágenes consistentes con **Qwen Image Edit + Lightning + Next Scene**, y dejar preparado el paso posterior a WAN 2.2.

## Qué hace

- Lee `jobs/*/visual_manifest.json`
- Construye prompts a partir de `scene_plan[].comfy_prompt_base`
- Inyecta esos prompts dentro de `workflow-comfyui-basic-next-scene-v2.json`
- Envía el workflow modificado a la API de ComfyUI
- Guarda una copia del workflow renderizado dentro del job
- Opcionalmente espera a que termine la ejecución y guarda metadatos

## Estructura esperada

```text
jobs/
├── 000001/
│   ├── audio/narration.wav
│   ├── subtitles/narration.srt
│   ├── brief.json
│   ├── script.json
│   ├── status.json
│   └── visual_manifest.json
└── 000002/
```

## Instalación

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/WSL
pip install -r requirements.txt
```

## Ejemplo de uso

```bash
python scripts/run_comfy_jobs.py \
  --jobs-root /ruta/a/jobs \
  --workflow /ruta/a/workflow-comfyui-basic-next-scene-v2.json \
  --comfy-url http://127.0.0.1:8188 \
  --wait
```

## Modo prueba sin enviar a ComfyUI

```bash
python scripts/run_comfy_jobs.py \
  --jobs-root /ruta/a/jobs \
  --workflow /ruta/a/workflow-comfyui-basic-next-scene-v2.json \
  --dry-run
```

## Nodos que modifica este proyecto

El script actual está preparado para tu workflow concreto:

- Nodo `45` → prompt inicial (`CLIPTextEncode`)
- Nodo `81` → bloque multilinea de escenas (`Text Multiline`)
- Nodo `9` → prefijo de guardado de imagen base (`SaveImage`)
- Nodo `58` → prefijo de guardado de escenas (`SaveImage`)

Si cambias el workflow, ajusta `WorkflowNodeMap` en `src/comfy_pipeline/workflow.py`.



jobs/
   ↓
visual_manifest.json
   ↓
run_pipeline.sh / .bat
   ↓
Python
   ↓
ComfyUI API
   ↓
Qwen + Lightning + Next Scene
   ↓
images/


____________________

visual_manifest.json
   ↓
Qwen Image Edit + Lightning + Next Scene
   ↓
images/
   ↓
WAN 2.2
   ↓
clips/

```bash
python scripts/run_comfy_jobs.py --jobs-root jobs --workflow workflows/workflow-comfyui-basic-next-scene-v2.json --dry-run
```
