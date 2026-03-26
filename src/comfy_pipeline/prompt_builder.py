from __future__ import annotations

from typing import Any, Dict, List


def _join_keywords(keywords: List[str] | None) -> str:
    if not keywords:
        return ""
    return ", ".join(k.strip() for k in keywords if str(k).strip())


def _clean_parts(parts: List[str]) -> str:
    return ", ".join(p.strip() for p in parts if isinstance(p, str) and p.strip())


def build_initial_prompt(manifest: Dict[str, Any]) -> str:
    """Build a strong initial image prompt from manifest-level context and first scene."""
    scenes = manifest.get("scene_plan", [])
    if not scenes:
        raise ValueError("visual_manifest.json no contiene scene_plan")

    first = scenes[0]
    base = first.get("comfy_prompt_base", {})
    character = manifest.get("character_design", {})
    visual_style = manifest.get("visual_style", {})

    parts = [
        character.get("core_identity") or base.get("subject"),
        character.get("physical_markers"),
        character.get("wardrobe_anchor"),
        base.get("action"),
        base.get("environment"),
        visual_style.get("primary_look") or base.get("style"),
        visual_style.get("lighting"),
        visual_style.get("camera_language"),
        visual_style.get("texture_mood"),
        base.get("composition_goal"),
        f"aspect ratio {manifest.get('aspect_ratio')}" if manifest.get("aspect_ratio") else "",
        _join_keywords(base.get("keywords")),
        "realistic cinematic style",
    ]
    return _clean_parts(parts)


def build_next_scene_prompts(manifest: Dict[str, Any]) -> List[str]:
    """Build one Comfy-friendly line per scene for the Text Multiline node."""
    scenes = manifest.get("scene_plan", [])
    if not scenes:
        raise ValueError("visual_manifest.json no contiene scene_plan")

    character = manifest.get("character_design", {})
    continuity_global = character.get("continuity_anchor") or character.get("core_identity") or "same subject"
    visual_style = manifest.get("visual_style", {})
    style_global = visual_style.get("primary_look") or "realistic cinematic style"

    lines: List[str] = []
    for scene in scenes:
        base = scene.get("comfy_prompt_base", {})
        line_parts = [
            "Next Scene:",
            f"same subject, same identity anchor ({base.get('continuity_anchor') or continuity_global})",
            base.get("subject"),
            base.get("action"),
            base.get("environment"),
            scene.get("camera"),
            scene.get("mood"),
            base.get("composition_goal"),
            base.get("style") or style_global,
            f"aspect ratio {base.get('aspect_ratio')}" if base.get("aspect_ratio") else "",
            f"motion cue {base.get('motion_cue')}" if base.get("motion_cue") else "",
            "realistic cinematic style",
        ]
        lines.append(_clean_parts(line_parts))
    return lines


def build_negative_prompt(manifest: Dict[str, Any]) -> str:
    scenes = manifest.get("scene_plan", [])
    if not scenes:
        return ""
    negatives = []
    for scene in scenes:
        neg = scene.get("comfy_prompt_base", {}).get("negative_prompt")
        if neg:
            negatives.append(neg)
    if not negatives:
        return ""
    return ", ".join(dict.fromkeys(negatives))
