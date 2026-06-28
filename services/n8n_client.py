"""n8n REST API client."""

from typing import Any

import requests

from config.constants import EXECUTIONS_LIMIT, N8N_REQUEST_TIMEOUT
from utils.json_utils import sanitize_workflow_for_create


class N8nAPIError(Exception):
    """Raised when the n8n API returns an error or is unreachable."""

    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


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
                f"Cannot reach n8n at {self.base_url}. Is the server running?"
            ) from exc
        except requests.exceptions.Timeout as exc:
            raise N8nAPIError("n8n server did not respond in time.") from exc
        except requests.exceptions.RequestException as exc:
            raise N8nAPIError(f"Network error: {exc}") from exc

        if response.status_code in (401, 403):
            raise N8nAPIError(
                "n8n API key invalid or lacks required permissions "
                "(workflow:read, workflow:create, workflow:update, workflow:delete, execution:read).",
                status_code=response.status_code,
            )

        if not response.ok:
            message = self._extract_error_message(response)
            raise N8nAPIError(message, status_code=response.status_code)

        if response.status_code == 204 or not response.content:
            return {}

        return response.json()

    @staticmethod
    def _extract_error_message(response: requests.Response) -> str:
        try:
            body = response.json()
            return body.get("message") or body.get("error") or response.text
        except ValueError:
            return response.text or f"HTTP {response.status_code}"

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
        payload = sanitize_workflow_for_create(workflow)
        return self._request("POST", "/workflows", json=payload)

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
