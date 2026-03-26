from __future__ import annotations

import logging
import time
from typing import Any

import requests


LOGGER = logging.getLogger(__name__)


def send_workflow(
    workflow: dict[str, Any],
    comfy_url: str,
    *,
    wait: bool = False,
    poll_interval: float = 2.0,
    timeout_seconds: float = 300.0,
) -> dict[str, Any]:
    base_url = comfy_url.rstrip("/")
    payload = {"prompt": workflow}

    LOGGER.info("Sending workflow to ComfyUI at %s/prompt", base_url)
    response = requests.post(f"{base_url}/prompt", json=payload, timeout=30)
    response.raise_for_status()
    result = response.json()

    if wait:
        prompt_id = result.get("prompt_id")
        if not prompt_id:
            raise ValueError("ComfyUI response did not include prompt_id")
        history = wait_for_workflow(
            prompt_id,
            comfy_url=base_url,
            poll_interval=poll_interval,
            timeout_seconds=timeout_seconds,
        )
        result["history"] = history

    return result


def wait_for_workflow(
    prompt_id: str,
    *,
    comfy_url: str,
    poll_interval: float = 2.0,
    timeout_seconds: float = 300.0,
) -> dict[str, Any]:
    base_url = comfy_url.rstrip("/")
    deadline = time.monotonic() + timeout_seconds

    while time.monotonic() < deadline:
        history = get_history(prompt_id, comfy_url=base_url)
        if history:
            LOGGER.info("ComfyUI completed prompt %s", prompt_id)
            return history
        time.sleep(poll_interval)

    raise TimeoutError(f"Timed out waiting for ComfyUI prompt {prompt_id}")


def get_history(prompt_id: str, *, comfy_url: str) -> dict[str, Any]:
    base_url = comfy_url.rstrip("/")
    response = requests.get(f"{base_url}/history/{prompt_id}", timeout=30)
    response.raise_for_status()
    return response.json()
