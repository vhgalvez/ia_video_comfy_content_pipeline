#!/usr/bin/env python3

from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from comfy_pipeline.orchestrator import JobOrchestrator


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Procesa jobs/*/visual_manifest.json y los envía a ComfyUI")
    parser.add_argument("--jobs-root", type=Path, required=True, help="Ruta a la carpeta jobs/")
    parser.add_argument("--workflow", type=Path, required=True, help="Ruta a workflow-comfyui-basic-next-scene-v2.json")
    parser.add_argument("--comfy-url", default="http://127.0.0.1:8188", help="URL base de ComfyUI")
    parser.add_argument("--job-id", help="Procesar solo un job concreto, por ejemplo 000001")
    parser.add_argument("--dry-run", action="store_true", help="Solo genera rendered_comfy_workflow.json, no envía nada a ComfyUI")
    parser.add_argument("--wait", action="store_true", help="Espera a que ComfyUI termine y guarda comfy_history.json")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    orchestrator = JobOrchestrator(args.jobs_root, args.workflow, comfy_url=args.comfy_url)

    jobs = orchestrator.find_jobs()
    if args.job_id:
        jobs = [p for p in jobs if p.name == args.job_id]

    if not jobs:
        print("No se encontraron jobs válidos.")
        return 1

    for job_dir in jobs:
        print(f"\n=== Procesando job {job_dir.name} ===")
        result = orchestrator.process_job(job_dir, dry_run=args.dry_run, wait=args.wait)
        print(f"Workflow renderizado: {result.rendered_workflow_path}")
        if result.prompt_id:
            print(f"Prompt enviado a ComfyUI: {result.prompt_id}")
        if result.history_path:
            print(f"History guardado en: {result.history_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
