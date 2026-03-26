from __future__ import annotations

import time
from typing import Any, Dict, Optional
from urllib.parse import urljoin
import requests


class ComfyAPI:
    def __init__(self, base_url: str = "http://127.0.0.1:8188", timeout: int = 30):
        self.base_url = base_url.rstrip("/") + "/"
        self.timeout = timeout
        self.session = requests.Session()

    def queue_prompt(self, workflow: Dict[str, Any], client_id: str = "comfy-content-pipeline") -> Dict[str, Any]:
        payload = {
            "prompt": self._to_prompt_payload(workflow),
            "client_id": client_id,
        }
        response = self.session.post(
            urljoin(self.base_url, "prompt"),
            json=payload,
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()

    def get_history(self, prompt_id: Optional[str] = None) -> Dict[str, Any]:
        url = urljoin(self.base_url, "history")
        if prompt_id:
            url = urljoin(self.base_url, f"history/{prompt_id}")
        response = self.session.get(url, timeout=self.timeout)
        response.raise_for_status()
        return response.json()

    def wait_for_prompt(self, prompt_id: str, poll_interval: float = 2.0, max_wait_seconds: int = 3600) -> Dict[str, Any]:
        started = time.time()
        while True:
            history = self.get_history(prompt_id)
            if history:
                return history
            if time.time() - started > max_wait_seconds:
                raise TimeoutError(f"ComfyUI no terminó el prompt {prompt_id} dentro de {max_wait_seconds}s")
            time.sleep(poll_interval)

    @staticmethod
    def _to_prompt_payload(workflow: Dict[str, Any]) -> Dict[str, Any]:
        """Convert exported workflow format to API prompt format.

        ComfyUI API expects a dict keyed by node id string with class_type and inputs.
        """
        prompt: Dict[str, Any] = {}
        link_index = {link[0]: link for link in workflow.get("links", [])}

        for node in workflow.get("nodes", []):
            node_id = str(node["id"])
            inputs: Dict[str, Any] = {}

            # linked inputs
            for inp in node.get("inputs", []):
                name = inp.get("name")
                link_id = inp.get("link")
                if name is None or link_id is None:
                    continue
                link = link_index.get(link_id)
                if not link:
                    continue
                from_node_id = str(link[1])
                from_slot = int(link[2])
                inputs[name] = [from_node_id, from_slot]

            # widget inputs
            widgets = node.get("widgets_values", [])
            widget_names = []
            for inp in node.get("inputs", []):
                widget = inp.get("widget")
                if widget and widget.get("name"):
                    widget_names.append(widget["name"])
            if widget_names and widgets:
                for idx, wname in enumerate(widget_names):
                    if idx < len(widgets):
                        inputs[wname] = widgets[idx]
            elif widgets:
                # heuristic fallback for common nodes used in this project
                if node.get("type") in {"CLIPTextEncode", "Text Multiline", "SaveImage"}:
                    inputs["text" if node.get("type") != "SaveImage" else "filename_prefix"] = widgets[0]
                elif node.get("type") == "Text Load Line From File":
                    if len(widgets) >= 5:
                        inputs.update({
                            "root_directory": widgets[0],
                            "filename": widgets[1],
                            "directory": widgets[2],
                            "index_name": widgets[3],
                            "index": widgets[4],
                        })
                else:
                    # preserve raw widgets for nodes that read positional widget args internally
                    inputs["_widget_values"] = widgets

            prompt[node_id] = {
                "class_type": node.get("type"),
                "inputs": inputs,
            }
        return prompt
