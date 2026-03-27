from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

LEGACY_PROMPT_NODE_IDS = (68, 45)
NEXT_SCENES_NODE_ID = 81
LINE_INDEX_NODE_ID = 74


def load_workflow_template(workflow_path: Path | str) -> dict[str, Any]:
    path = Path(workflow_path)
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def inject_workflow_values(
    workflow: dict[str, Any],
    *,
    base_prompt: str,
    next_scene_lines: str,
) -> dict[str, Any]:
    rendered_workflow = copy.deepcopy(workflow)

    prompt_node = _find_first_existing_node(rendered_workflow, LEGACY_PROMPT_NODE_IDS)
    if prompt_node is not None:
        _set_widget_value(prompt_node, 0, base_prompt)

    _set_widget_value(_find_node(rendered_workflow, NEXT_SCENES_NODE_ID), 0, next_scene_lines)
    _set_widget_value(_find_node(rendered_workflow, LINE_INDEX_NODE_ID), -1, 0)

    return rendered_workflow


def save_workflow(workflow: dict[str, Any], output_path: Path | str) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(workflow, handle, ensure_ascii=False, indent=2)
    return path


def _set_widget_value(node: dict[str, Any], widget_index: int, value: Any) -> None:
    widgets = node.get("widgets_values")
    if not isinstance(widgets, list) or not widgets:
        raise ValueError(f"Node {node.get('id')} does not contain writable widgets_values")
    widgets[widget_index] = value


def _find_node(workflow: dict[str, Any], node_id: int) -> dict[str, Any]:
    for node in workflow.get("nodes", []):
        if node.get("id") == node_id:
            return node
    raise KeyError(f"Workflow node {node_id} was not found")


def _find_first_existing_node(
    workflow: dict[str, Any],
    node_ids: tuple[int, ...],
) -> dict[str, Any] | None:
    for node_id in node_ids:
        for node in workflow.get("nodes", []):
            if node.get("id") == node_id:
                return node
    return None
