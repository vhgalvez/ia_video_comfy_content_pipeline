from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional
import json

from .prompt_builder import build_initial_prompt, build_next_scene_prompts, build_negative_prompt
from .workflow import WorkflowTemplate
from .comfy_api import ComfyAPI


@dataclass
class JobResult:
    job_id: str
    rendered_workflow_path: Path
    prompt_id: Optional[str]
    history_path: Optional[Path]


class JobOrchestrator:
    def __init__(self, jobs_root: Path, workflow_path: Path, comfy_url: str = "http://127.0.0.1:8188"):
        self.jobs_root = jobs_root
        self.workflow_path = workflow_path
        self.template = WorkflowTemplate.from_file(workflow_path)
        self.api = ComfyAPI(comfy_url)

    def find_jobs(self) -> List[Path]:
        return sorted([p for p in self.jobs_root.iterdir() if p.is_dir() and (p / "visual_manifest.json").exists()])

    def process_job(self, job_dir: Path, *, dry_run: bool = False, wait: bool = False) -> JobResult:
        manifest_path = job_dir / "visual_manifest.json"
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest: Dict[str, Any] = json.load(f)

        initial_prompt = build_initial_prompt(manifest)
        next_scene_lines = build_next_scene_prompts(manifest)
        _ = build_negative_prompt(manifest)  # reserved for future workflow extension

        rendered = self.template.render(
            initial_prompt=initial_prompt,
            next_scene_lines=next_scene_lines,
            job_id=job_dir.name,
        )

        rendered_workflow_path = job_dir / "rendered_comfy_workflow.json"
        with open(rendered_workflow_path, "w", encoding="utf-8") as f:
            json.dump(rendered, f, ensure_ascii=False, indent=2)

        if dry_run:
            return JobResult(job_id=job_dir.name, rendered_workflow_path=rendered_workflow_path, prompt_id=None, history_path=None)

        queue_response = self.api.queue_prompt(rendered, client_id=f"job-{job_dir.name}")
        prompt_id = queue_response.get("prompt_id")

        history_path: Optional[Path] = None
        if wait and prompt_id:
            history = self.api.wait_for_prompt(prompt_id)
            history_path = job_dir / "comfy_history.json"
            with open(history_path, "w", encoding="utf-8") as f:
                json.dump(history, f, ensure_ascii=False, indent=2)

        return JobResult(
            job_id=job_dir.name,
            rendered_workflow_path=rendered_workflow_path,
            prompt_id=prompt_id,
            history_path=history_path,
        )
