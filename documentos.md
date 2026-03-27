base) PS C:\Users\vhgal\Documents\desarrollo\ia\ia_video_comfy_content_pipeline> python scripts\run_comfy_jobs.py --jobs-root C:\Users\vhgal\Documents\desarrollo\ia\neurocontent-engine\jobs --workflow C:\Users\vhgal\Documents\desarrollo\ia\ia_video_comfy_content_pipeline\workflows\workflow-comfyui-basic-next-scene-v2.json --dry-run
INFO comfy_pipeline.orchestrator: Processing job C:\Users\vhgal\Documents\desarrollo\ia\neurocontent-engine\jobs\000001
INFO comfy_pipeline.orchestrator: Dry run enabled for job 000001
INFO root: Rendered workflow saved to C:\Users\vhgal\Documents\desarrollo\ia\neurocontent-engine\jobs\000001\rendered_comfy_workflow.json
INFO comfy_pipeline.orchestrator: Processing job C:\Users\vhgal\Documents\desarrollo\ia\neurocontent-engine\jobs\000002
INFO comfy_pipeline.orchestrator: Dry run enabled for job 000002
INFO root: Rendered workflow saved to C:\Users\vhgal\Documents\desarrollo\ia\neurocontent-engine\jobs\000002\rendered_comfy_workflow.json
INFO comfy_pipeline.orchestrator: Processing job C:\Users\vhgal\Documents\desarrollo\ia\neurocontent-engine\jobs\000003
INFO comfy_pipeline.orchestrator: Dry run enabled for job 000003
INFO root: Rendered workflow saved to C:\Users\vhgal\Documents\desarrollo\ia\neurocontent-engine\jobs\000003\rendered_comfy_workflow.json
(base) PS C:\Users\vhgal\Documents\desarrollo\ia\ia_video_comfy_content_pipeline> python C:\Users\vhgal\Documents\desarrollo\ia\ia_video_comfy_content_pipeline\scripts\run_comfy_jobs.py --jobs-root C:\Users\vhgal\Documents\desarrollo\ia\neurocontent-engine\jobs --workflow C:\Users\vhgal\Documents\desarrollo\ia\ia_video_comfy_content_pipeline\workflows\workflow-comfyui-basic-next-scene-v2.json --dry-run
INFO comfy_pipeline.orchestrator: Processing job C:\Users\vhgal\Documents\desarrollo\ia\neurocontent-engine\jobs\000001
INFO comfy_pipeline.orchestrator: Dry run enabled for job 000001
INFO root: Rendered workflow saved to C:\Users\vhgal\Documents\desarrollo\ia\neurocontent-engine\jobs\000001\rendered_comfy_workflow.json
INFO comfy_pipeline.orchestrator: Processing job C:\Users\vhgal\Documents\desarrollo\ia\neurocontent-engine\jobs\000002
INFO comfy_pipeline.orchestrator: Dry run enabled for job 000002
INFO root: Rendered workflow saved to C:\Users\vhgal\Documents\desarrollo\ia\neurocontent-engine\jobs\000002\rendered_comfy_workflow.json
INFO comfy_pipeline.orchestrator: Processing job C:\Users\vhgal\Documents\desarrollo\ia\neurocontent-engine\jobs\000003
INFO comfy_pipeline.orchestrator: Dry run enabled for job 000003
INFO root: Rendered workflow saved to C:\Users\vhgal\Documents\desarrollo\ia\neurocontent-engine\jobs\000003\rendered_comfy_workflow.json
(base) PS C:\Users\vhgal\Documents\desarrollo\ia\ia_video_comfy_content_pipeline> ls C:\Users\vhgal\Documents\desarrollo\ia\neurocontent-engine\jobs\000001\


    Directorio: C:\Users\vhgal\Documents\desarrollo\ia\neurocontent-engine\jobs\000001


Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
d-----        26/03/2026     17:47                audio
d-----        26/03/2026     20:24                images
d-----        26/03/2026     17:56                logs
d-----        26/03/2026     17:56                subtitles
-a----        26/03/2026     16:16           1604 brief.json
-a----        26/03/2026     20:25          40158 rendered_comfy_workflow.json
-a----        26/03/2026     16:16           1067 script.json
-a----        26/03/2026     17:56            542 status.json
-a----        26/03/2026     16:16          24215 visual_manifest.json


(base) PS C:\Users\vhgal\Documents\desarrollo\ia\ia_video_comfy_content_pipeline>



Copy-Item C:\Users\vhgal\Documents\desarrollo\ia\neurocontent-engine\jobs\000001\rendered_comfy_workflow.json C:\Users\vhgal\Documents\desarrollo\ia\neurocontent-engine\jobs\000001\images\


cd C:\Users\vhgal\AppData\Local\Programs\ComfyUI\resources\ComfyU 

python main.py --listen 127.0.0.1 --port 8188







Terminal 1

Déjala así, sin cerrarla:

conda activate comfy
cd C:\Users\vhgal\AppData\Local\Programs\ComfyUI\resources\ComfyUI
python main.py --listen 127.0.0.1 --port 8188


conda activate comfy
cd C:\Users\vhgal\AppData\Local\Programs\ComfyUI\resources\ComfyUI
python -m pip install -U --pre comfyui-manager
python .\main.py --enable-manager --listen 127.0.0.1 --port 8188


conda activate comfy
cd C:\Users\vhgal\AppData\Local\Programs\ComfyUI\resources\ComfyUI
python .\main.py --enable-manager --listen 127.0.0.1 --port 8188



Terminal 2

Ejecuta esto:

conda activate comfy
cd C:\Users\vhgal\Documents\desarrollo\ia\ia_video_comfy_content_pipeline
python -m pip install -r .\requirements.txt
python scripts\run_comfy_jobs.py --jobs-root C:\Users\vhgal\Documents\desarrollo\ia\neurocontent-engine\jobs --workflow workflows\workflow-comfyui-basic-next-scene-v2.json --comfy-url http://127.0.0.1:8188 --wait


