from __future__ import annotations

from dataclasses import dataclass
import json
import logging
from pathlib import Path
from typing import Any

from .comfy_api import send_workflow
from .prompt_builder import build_comfy_prompt, build_next_scene_lines
from .workflow import inject_workflow_values, load_workflow_template, save_workflow


LOGGER = logging.getLogger(__name__)


@dataclass
class JobResult:
    job_path: Path
    rendered_workflow_path: Path
    prompt_id: str | None = None
    history: dict[str, Any] | None = None


def find_jobs(jobs_root: Path) -> list[Path]:
    if not jobs_root.exists():
        raise FileNotFoundError(f"Jobs root does not exist: {jobs_root}")
    return sorted(
        path
        for path in jobs_root.iterdir()
        if path.is_dir() and (path / "visual_manifest.json").exists()
    )


def process_job(
    job_path: Path,
    *,
    workflow_path: Path,
    comfy_url: str = "http://127.0.0.1:8188",
    dry_run: bool = False,
    wait: bool = False,
) -> JobResult:
    LOGGER.info("Processing job %s", job_path)
    manifest = _load_manifest(job_path / "visual_manifest.json")

    scene_plan = manifest.get("scene_plan")
    if not isinstance(scene_plan, list) or not scene_plan:
        raise ValueError(f"{job_path} does not contain a valid scene_plan list")

    base_prompt = build_comfy_prompt(scene_plan[0])
    next_scene_lines = build_next_scene_lines(scene_plan)

    workflow_template = load_workflow_template(workflow_path)
    rendered_workflow = inject_workflow_values(
        workflow_template,
        base_prompt=base_prompt,
        next_scene_lines=next_scene_lines,
    )

    rendered_workflow_path = save_workflow(
        rendered_workflow,
        job_path / "rendered_comfy_workflow.json",
    )

    images_dir = job_path / "images"
    images_dir.mkdir(exist_ok=True)

    if dry_run:
        LOGGER.info("Dry run enabled for job %s", job_path.name)
        return JobResult(
            job_path=job_path,
            rendered_workflow_path=rendered_workflow_path,
        )

    api_result = send_workflow(rendered_workflow, comfy_url, wait=wait)
    return JobResult(
        job_path=job_path,
        rendered_workflow_path=rendered_workflow_path,
        prompt_id=api_result.get("prompt_id"),
        history=api_result.get("history"),
    )


def _load_manifest(manifest_path: Path) -> dict[str, Any]:
    with manifest_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)
