from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, Optional
import json
import copy


@dataclass(frozen=True)
class WorkflowNodeMap:
    initial_prompt_node_id: int = 45
    multiline_node_id: int = 81
    base_save_node_id: int = 9
    next_scene_save_node_id: int = 58


class WorkflowTemplate:
    def __init__(self, workflow: Dict[str, Any], node_map: WorkflowNodeMap | None = None):
        self.workflow = workflow
        self.node_map = node_map or WorkflowNodeMap()

    @classmethod
    def from_file(cls, path: str | Path, node_map: WorkflowNodeMap | None = None) -> "WorkflowTemplate":
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls(data, node_map=node_map)

    def render(
        self,
        *,
        initial_prompt: str,
        next_scene_lines: Iterable[str],
        job_id: str,
        initial_prefix: Optional[str] = None,
        nextscene_prefix: Optional[str] = None,
    ) -> Dict[str, Any]:
        wf = copy.deepcopy(self.workflow)
        self._set_node_text(wf, self.node_map.initial_prompt_node_id, initial_prompt)
        self._set_node_text(wf, self.node_map.multiline_node_id, "\n".join(next_scene_lines))

        self._set_save_prefix(
            wf,
            self.node_map.base_save_node_id,
            initial_prefix or f"{job_id}/flux",
        )
        self._set_save_prefix(
            wf,
            self.node_map.next_scene_save_node_id,
            nextscene_prefix or f"{job_id}/nextscene",
        )
        return wf

    @staticmethod
    def _find_node(workflow: Dict[str, Any], node_id: int) -> Dict[str, Any]:
        for node in workflow.get("nodes", []):
            if node.get("id") == node_id:
                return node
        raise KeyError(f"No se encontró el nodo {node_id} en el workflow")

    def _set_node_text(self, workflow: Dict[str, Any], node_id: int, value: str) -> None:
        node = self._find_node(workflow, node_id)
        widgets = node.setdefault("widgets_values", [])
        if not widgets:
            widgets.append(value)
        else:
            widgets[0] = value

    def _set_save_prefix(self, workflow: Dict[str, Any], node_id: int, value: str) -> None:
        node = self._find_node(workflow, node_id)
        widgets = node.setdefault("widgets_values", [])
        if not widgets:
            widgets.append(value)
        else:
            widgets[0] = value
