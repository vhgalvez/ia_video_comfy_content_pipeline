from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any


PROMPT_NODE_ID = 45
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

    _set_widget_value(rendered_workflow, PROMPT_NODE_ID, 0, base_prompt)
    _set_widget_value(rendered_workflow, NEXT_SCENES_NODE_ID, 0, next_scene_lines)
    _set_widget_value(rendered_workflow, LINE_INDEX_NODE_ID, -1, 0)

    return rendered_workflow


def save_workflow(workflow: dict[str, Any], output_path: Path | str) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(workflow, handle, ensure_ascii=False, indent=2)
    return path


def _set_widget_value(workflow: dict[str, Any], node_id: int, widget_index: int, value: Any) -> None:
    node = _find_node(workflow, node_id)
    widgets = node.get("widgets_values")
    if not isinstance(widgets, list) or not widgets:
        raise ValueError(f"Node {node_id} does not contain writable widgets_values")
    widgets[widget_index] = value


def _find_node(workflow: dict[str, Any], node_id: int) -> dict[str, Any]:
    for node in workflow.get("nodes", []):
        if node.get("id") == node_id:
            return node
    raise KeyError(f"Workflow node {node_id} was not found")
