"""n8n REST API client."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Any

import requests

from config.constants import EXECUTIONS_LIMIT, N8N_REQUEST_TIMEOUT
from utils.json_utils import prepare_workflow_for_push


class N8nAPIError(Exception):
    """Raised when the n8n API returns an error or is unreachable."""

    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


@dataclass
class WorkflowPushResult:
    """Outcome of pushing a workflow to n8n."""

    success: bool
    workflow_id: str | None = None
    workflow_name: str | None = None
    instance_url: str | None = None
    active: bool | None = None
    node_count: int | None = None
    message: str = ""
    error: str | None = None
    status_code: int | None = None

    @property
    def editor_url(self) -> str | None:
        if self.workflow_id and self.instance_url:
            return f"{self.instance_url.rstrip('/')}/workflow/{self.workflow_id}"
        return None


def build_blank_workflow(name: str = "New Workflow") -> dict[str, Any]:
    """Minimal importable workflow with a manual trigger node."""
    return {
        "name": name.strip() or "New Workflow",
        "nodes": [
            {
                "id": str(uuid.uuid4()),
                "name": "When clicking 'Execute workflow'",
                "type": "n8n-nodes-base.manualTrigger",
                "typeVersion": 1,
                "position": [250, 300],
                "parameters": {},
            }
        ],
        "connections": {},
        "settings": {},
    }


class N8nClient:
    """Thin wrapper around the official n8n REST API (/api/v1)."""

    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update(
            {
                "X-N8N-API-KEY": api_key,
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
        )

    def _request(self, method: str, path: str, **kwargs) -> Any:
        url = f"{self.base_url}{path}"
        kwargs.setdefault("timeout", N8N_REQUEST_TIMEOUT)

        try:
            response = self.session.request(method, url, **kwargs)
        except requests.exceptions.ConnectionError as exc:
            raise N8nAPIError(
                "Cannot reach n8n. Is the server running? Try Docker Control → Start n8n.",
                status_code=None,
            ) from exc
        except requests.exceptions.Timeout as exc:
            raise N8nAPIError("n8n did not respond in time. It may still be starting.") from exc
        except requests.exceptions.RequestException as exc:
            raise N8nAPIError(f"Network error: {exc}") from exc

        if response.status_code in (401, 403):
            raise N8nAPIError(
                "n8n API key invalid or missing permissions. Check sidebar → API Configuration.",
                status_code=response.status_code,
            )

        if not response.ok:
            message = self._extract_error_message(response)
            raise N8nAPIError(
                self._friendly_error_message(response.status_code, message, url),
                status_code=response.status_code,
            )

        if response.status_code == 204 or not response.content:
            return {}

        return response.json()

    @staticmethod
    def _extract_error_message(response: requests.Response) -> str:
        try:
            body = response.json()
            if isinstance(body, dict):
                if isinstance(body.get("message"), str):
                    return body["message"]
                if isinstance(body.get("error"), str):
                    return body["error"]
                if isinstance(body.get("error"), dict) and body["error"].get("message"):
                    return str(body["error"]["message"])
            return response.text
        except ValueError:
            return response.text or f"HTTP {response.status_code}"

    @staticmethod
    def _friendly_error_message(status_code: int, detail: str, url: str) -> str:
        detail = (detail or "").strip()
        if status_code == 400:
            return f"n8n rejected the workflow (400). {detail or 'Check node types, connections, and required fields.'}"
        if status_code == 404:
            return (
                f"n8n API not found at {url}. "
                "Verify the Instance URL in the sidebar (e.g. http://localhost:5678)."
            )
        if status_code == 409:
            return f"Workflow conflict (409). {detail or 'A workflow with this name may already exist.'}"
        if status_code >= 500:
            return f"n8n server error ({status_code}). {detail or 'Try again or check n8n logs.'}"
        return detail or f"HTTP {status_code}"

    @staticmethod
    def _unwrap_entity(data: Any) -> dict[str, Any]:
        if isinstance(data, dict) and isinstance(data.get("data"), dict):
            return data["data"]
        if isinstance(data, dict):
            return data
        return {}

    def list_workflows(self) -> list[dict[str, Any]]:
        """GET /workflows — returns all workflows."""
        data = self._request("GET", "/workflows")
        if isinstance(data, dict) and "data" in data:
            return data["data"]
        if isinstance(data, list):
            return data
        return []

    def create_workflow(self, workflow: dict[str, Any]) -> dict[str, Any]:
        """POST /workflows — create a new workflow from JSON."""
        payload = prepare_workflow_for_push(workflow)
        data = self._request("POST", "/workflows", json=payload)
        return self._unwrap_entity(data)

    def create_blank_workflow(self, name: str = "New Workflow") -> dict[str, Any]:
        """POST /workflows — create a starter workflow with one manual trigger node."""
        return self.create_workflow(build_blank_workflow(name))

    def push_workflow(self, workflow: dict[str, Any], instance_url: str) -> WorkflowPushResult:
        """Create a workflow on n8n and return a structured push result."""
        try:
            payload = prepare_workflow_for_push(workflow)
            created = self.create_workflow(payload)
            workflow_id = created.get("id")
            if not workflow_id:
                return WorkflowPushResult(
                    success=False,
                    instance_url=instance_url,
                    error="n8n did not return a workflow ID. The workflow may not have been created.",
                )

            return WorkflowPushResult(
                success=True,
                workflow_id=str(workflow_id),
                workflow_name=created.get("name") or payload.get("name"),
                instance_url=instance_url.rstrip("/"),
                active=created.get("active"),
                node_count=len(created.get("nodes") or payload.get("nodes") or []),
                message="Workflow created successfully on n8n.",
            )
        except N8nAPIError as exc:
            return WorkflowPushResult(
                success=False,
                instance_url=instance_url.rstrip("/"),
                workflow_name=workflow.get("name"),
                error=str(exc),
                status_code=exc.status_code,
            )
        except ValueError as exc:
            return WorkflowPushResult(
                success=False,
                instance_url=instance_url.rstrip("/"),
                workflow_name=workflow.get("name"),
                error=str(exc),
            )

    def delete_workflow(self, workflow_id: str) -> None:
        """DELETE /workflows/{id}."""
        self._request("DELETE", f"/workflows/{workflow_id}")

    def activate_workflow(self, workflow_id: str) -> dict[str, Any]:
        """POST /workflows/{id}/activate."""
        return self._request("POST", f"/workflows/{workflow_id}/activate")

    def deactivate_workflow(self, workflow_id: str) -> dict[str, Any]:
        """POST /workflows/{id}/deactivate."""
        return self._request("POST", f"/workflows/{workflow_id}/deactivate")

    def toggle_workflow(self, workflow_id: str, is_active: bool) -> dict[str, Any]:
        """Activate or deactivate based on current state."""
        if is_active:
            return self.deactivate_workflow(workflow_id)
        return self.activate_workflow(workflow_id)

    def list_executions(self, limit: int = EXECUTIONS_LIMIT) -> list[dict[str, Any]]:
        """GET /executions — fetch recent execution history."""
        data = self._request("GET", "/executions", params={"limit": limit})
        if isinstance(data, dict) and "data" in data:
            return data["data"]
        if isinstance(data, list):
            return data
        return []
