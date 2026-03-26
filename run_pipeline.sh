@echo off

echo 🚀 Ejecutando pipeline ComfyUI...

set PROJECT_ROOT=C:\Users\vhgal\Documents\desarrollo\ia\ia_video_comfy_content_pipeline
set JOBS_ROOT=C:\Users\vhgal\Documents\desarrollo\ia\jobs
set WORKFLOW_PATH=C:\Users\vhgal\Documents\desarrollo\ia\workflows\workflow-comfyui-basic-next-scene-v2.json
set COMFY_URL=http://127.0.0.1:8188

python %PROJECT_ROOT%\scripts\run_comfy_jobs.py ^
  --jobs-root %JOBS_ROOT% ^
  --workflow %WORKFLOW_PATH% ^
  --comfy-url %COMFY_URL% ^
  --wait

echo ✅ Pipeline terminado
pause