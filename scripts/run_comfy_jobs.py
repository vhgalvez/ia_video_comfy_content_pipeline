#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from comfy_pipeline.orchestrator import find_jobs, process_job


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render ComfyUI workflows from jobs/*/visual_manifest.json",
    )
    parser.add_argument("--jobs-root", type=Path, required=True, help="Path to the jobs root directory")
    parser.add_argument("--workflow", type=Path, required=True, help="Path to the ComfyUI workflow JSON template")
    parser.add_argument("--comfy-url", default="http://127.0.0.1:8188", help="ComfyUI base URL")
    parser.add_argument("--dry-run", action="store_true", help="Only generate rendered_comfy_workflow.json")
    parser.add_argument("--wait", action="store_true", help="Wait for ComfyUI completion and save comfy_history.json")
    parser.add_argument("--log-level", default="INFO", help="Logging level, for example INFO or DEBUG")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    logging.basicConfig(
        level=getattr(logging, args.log_level.upper(), logging.INFO),
        format="%(levelname)s %(name)s: %(message)s",
    )

    jobs = find_jobs(args.jobs_root)
    if not jobs:
        logging.error("No valid jobs found under %s", args.jobs_root)
        return 1

    for job_path in jobs:
        result = process_job(
            job_path,
            workflow_path=args.workflow,
            comfy_url=args.comfy_url,
            dry_run=args.dry_run,
            wait=args.wait,
        )
        logging.info("Rendered workflow saved to %s", result.rendered_workflow_path)

        if result.prompt_id:
            logging.info("Queued ComfyUI prompt %s for job %s", result.prompt_id, job_path.name)

        if result.history is not None:
            history_path = job_path / "comfy_history.json"
            history_path.write_text(
                json.dumps(result.history, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            logging.info("ComfyUI history saved to %s", history_path)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
