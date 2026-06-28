"""JSON parsing and n8n workflow validation helpers."""

import json
import re
from typing import Any

# Fields n8n rejects or overwrites on workflow creation.
READ_ONLY_WORKFLOW_FIELDS = {
    "id",
    "createdAt",
    "updatedAt",
    "versionId",
    "active",
    "tags",
    "meta",
    "pinData",
    "shared",
    "triggerCount",
    "isArchived",
}


def strip_markdown_fences(text: str) -> str:
    """Remove ```json ... ``` wrappers if the model disobeys instructions."""
    cleaned = text.strip()
    fence_match = re.match(r"^```(?:json)?\s*\n?(.*?)\n?```\s*$", cleaned, re.DOTALL | re.IGNORECASE)
    if fence_match:
        return fence_match.group(1).strip()
    return cleaned


def parse_workflow_json(raw_text: str) -> dict[str, Any]:
    """Parse and validate workflow JSON from Gemini output."""
    cleaned = strip_markdown_fences(raw_text)
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON from AI model: {exc}") from exc

    if not isinstance(data, dict):
        raise ValueError("Workflow JSON must be a single object.")

    validate_workflow_shape(data)
    return data


def validate_workflow_shape(data: dict[str, Any]) -> None:
    """Ensure minimum required fields exist before pushing to n8n."""
    required = ("name", "nodes", "connections")
    missing = [field for field in required if field not in data]
    if missing:
        raise ValueError(f"Workflow JSON missing required fields: {', '.join(missing)}")

    if not isinstance(data["nodes"], list) or len(data["nodes"]) == 0:
        raise ValueError("Workflow must contain at least one node.")

    if not isinstance(data["connections"], dict):
        raise ValueError("Workflow 'connections' must be an object.")


def sanitize_workflow_for_create(data: dict[str, Any]) -> dict[str, Any]:
    """Strip read-only fields before POSTing to n8n."""
    return {key: value for key, value in data.items() if key not in READ_ONLY_WORKFLOW_FIELDS}
