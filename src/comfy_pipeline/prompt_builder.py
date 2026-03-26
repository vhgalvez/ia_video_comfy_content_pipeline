from __future__ import annotations

from typing import Any


PROMPT_FIELDS = (
    "subject",
    "action",
    "environment",
    "style",
    "composition_goal",
)


def _clean_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _join_parts(parts: list[str]) -> str:
    return ", ".join(part for part in parts if part)


def build_comfy_prompt(scene: dict) -> str:
    base = scene.get("comfy_prompt_base")
    if not isinstance(base, dict):
        raise ValueError("Each scene must contain a comfy_prompt_base object")

    parts = ["same character"]
    parts.extend(_clean_text(base.get(field)) for field in PROMPT_FIELDS)

    continuity_anchor = _clean_text(base.get("continuity_anchor"))
    if continuity_anchor:
        parts.append(f"continuity anchor {continuity_anchor}")

    aspect_ratio = _clean_text(base.get("aspect_ratio"))
    if aspect_ratio:
        parts.append(f"aspect ratio {aspect_ratio}")

    prompt = _join_parts(parts)

    negative_prompt = _clean_text(base.get("negative_prompt"))
    if negative_prompt:
        prompt = f"{prompt}. Negative prompt: {negative_prompt}"

    return prompt


def build_next_scene_lines(scene_plan: list) -> str:
    lines: list[str] = []
    for scene in scene_plan:
        lines.append(f"Next Scene: {build_comfy_prompt(scene)}")
    return "\n".join(lines)
