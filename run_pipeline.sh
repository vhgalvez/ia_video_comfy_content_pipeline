@echo off

setlocal

set PROJECT_ROOT=C:\Users\vhgal\Documents\desarrollo\ia\ia_video_comfy_content_pipeline
set JOBS_ROOT=C:\Users\vhgal\Documents\desarrollo\ia\neurocontent-engine\jobs
set WORKFLOW_PATH=%PROJECT_ROOT%\workflows\workflow-comfyui-basic-next-scene-v2.json
set COMFY_URL=http://127.0.0.1:8188

echo Ejecutando pipeline ComfyUI...
python %PROJECT_ROOT%\scripts\run_comfy_jobs.py ^
  --jobs-root %JOBS_ROOT% ^
  --workflow %WORKFLOW_PATH% ^
  --comfy-url %COMFY_URL% ^
  --wait

echo Pipeline terminado.
pause