#!/usr/bin/env python3
# scripts\render_jobs_and_prepare.py
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Renderiza workflows de ComfyUI para jobs y opcionalmente copia el JSON renderizado a images/ (modo legacy)."
    )
    parser.add_argument(
        "--jobs-root",
        type=Path,
        required=True,
        help="Ruta a la carpeta jobs del proyecto neurocontent-engine",
    )
    parser.add_argument(
        "--workflow",
        type=Path,
        required=True,
        help="Ruta al workflow base de ComfyUI",
    )
    parser.add_argument(
        "--python-bin",
        default=sys.executable,
        help="Python a usar para ejecutar scripts/run_comfy_jobs.py",
    )
    parser.add_argument(
        "--pipeline-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Raíz del repo ia_video_comfy_content_pipeline",
    )
    parser.add_argument(
        "--comfy-url",
        default="http://127.0.0.1:8188",
        help="URL base de ComfyUI",
    )
    parser.add_argument(
        "--wait",
        action="store_true",
        help="Esperar a que ComfyUI termine y guardar history",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Ejecutar en ComfyUI; si no se pasa, usa dry-run",
    )
    parser.add_argument(
        "--copy-to-images",
        action="store_true",
        help="Modo legacy: copia rendered_comfy_workflow.json a images/. No recomendado.",
    )
    parser.add_argument(
        "--only-job",
        help="Procesar solo un job, por ejemplo 000001",
    )
    return parser.parse_args()


def build_run_comfy_jobs_command(args: argparse.Namespace) -> list[str]:
    script_path = args.pipeline_root / "scripts" / "run_comfy_jobs.py"

    cmd = [
        args.python_bin,
        str(script_path),
        "--jobs-root",
        str(args.jobs_root),
        "--workflow",
        str(args.workflow),
        "--comfy-url",
        args.comfy_url,
    ]

    if args.execute:
        if args.wait:
            cmd.append("--wait")
    else:
        cmd.append("--dry-run")

    return cmd


def get_target_jobs(jobs_root: Path, only_job: str | None) -> list[Path]:
    if only_job:
        job_path = jobs_root / only_job
        if not job_path.exists():
            raise FileNotFoundError(f"No existe el job solicitado: {job_path}")
        return [job_path]

    jobs = []
    for path in sorted(jobs_root.iterdir()):
        if path.is_dir() and (path / "visual_manifest.json").exists():
            jobs.append(path)
    return jobs


def copy_rendered_to_images(job_path: Path) -> None:
    rendered = job_path / "rendered_comfy_workflow.json"
    if not rendered.exists():
        raise FileNotFoundError(
            f"No existe workflow renderizado en: {rendered}")

    images_dir = job_path / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    target = images_dir / "rendered_comfy_workflow.json"
    shutil.copy2(rendered, target)
    print(f"[LEGACY COPY] {rendered} -> {target}")


def main() -> int:
    args = parse_args()

    if not args.jobs_root.exists():
        raise FileNotFoundError(f"No existe jobs-root: {args.jobs_root}")

    if not args.workflow.exists():
        raise FileNotFoundError(f"No existe workflow base: {args.workflow}")

    target_jobs = get_target_jobs(args.jobs_root, args.only_job)
    if not target_jobs:
        print("No se encontraron jobs válidos.")
        return 1

    cmd = build_run_comfy_jobs_command(args)
    print("Ejecutando:")
    print(" ".join(cmd))
    print()

    result = subprocess.run(cmd, check=False)
    if result.returncode != 0:
        print(f"run_comfy_jobs.py terminó con código {result.returncode}")
        return result.returncode

    print("\nValidando resultados renderizados...\n")

    for job_path in target_jobs:
        rendered = job_path / "rendered_comfy_workflow.json"
        if rendered.exists():
            print(f"[OK] {rendered}")
        else:
            print(f"[ERROR] Falta: {rendered}")
            return 2

        if args.copy_to_images:
            copy_rendered_to_images(job_path)
        else:
            print(f"[INFO] No se copia a images/ (modo recomendado).")

    print("\nProceso completado correctamente.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
