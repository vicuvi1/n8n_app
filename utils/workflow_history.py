"""Persist the last N generated workflows for view, re-use, and delete."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

WORKFLOW_HISTORY_MAX = 10
HISTORY_PATH = Path(__file__).resolve().parent.parent / "data" / "workflow_history.json"


class WorkflowHistoryError(Exception):
    """Raised when workflow history cannot be read or written."""


def _load_entries() -> list[dict[str, Any]]:
    if not HISTORY_PATH.is_file():
        return []
    try:
        with HISTORY_PATH.open(encoding="utf-8") as handle:
            data = json.load(handle)
    except (json.JSONDecodeError, OSError) as exc:
        raise WorkflowHistoryError(f"Could not read workflow history: {HISTORY_PATH}") from exc

    entries = data.get("entries", [])
    if not isinstance(entries, list):
        return []
    return entries


def _write_entries(entries: list[dict[str, Any]]) -> None:
    HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {"entries": entries[:WORKFLOW_HISTORY_MAX]}
    tmp_path = HISTORY_PATH.with_suffix(".json.tmp")
    try:
        tmp_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        tmp_path.replace(HISTORY_PATH)
    except OSError as exc:
        raise WorkflowHistoryError(f"Could not write workflow history: {HISTORY_PATH}") from exc


def list_workflow_history() -> list[dict[str, Any]]:
    """Return history entries newest first."""
    entries = _load_entries()
    return sorted(entries, key=lambda e: e.get("created_at", ""), reverse=True)


def get_history_entry(entry_id: str) -> dict[str, Any] | None:
    for entry in _load_entries():
        if entry.get("id") == entry_id:
            return entry
    return None


def add_workflow_to_history(
    workflow: dict[str, Any],
    *,
    prompt: str = "",
    model: str = "",
    source: str = "",
    optimization: str = "",
) -> str:
    """Append a generated workflow to history (keeps last WORKFLOW_HISTORY_MAX)."""
    entry_id = uuid.uuid4().hex[:12]
    nodes = workflow.get("nodes") or []
    entry = {
        "id": entry_id,
        "name": workflow.get("name") or "Untitled Workflow",
        "workflow": workflow,
        "prompt": prompt.strip(),
        "model": model,
        "source": source,
        "optimization": optimization,
        "node_count": len(nodes) if isinstance(nodes, list) else 0,
        "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }

    entries = _load_entries()
    entries.insert(0, entry)
    _write_entries(entries[:WORKFLOW_HISTORY_MAX])
    return entry_id


def delete_history_entry(entry_id: str) -> bool:
    """Remove one history entry. Returns True if deleted."""
    entries = _load_entries()
    new_entries = [e for e in entries if e.get("id") != entry_id]
    if len(new_entries) == len(entries):
        return False
    _write_entries(new_entries)
    return True


def clear_workflow_history() -> None:
    """Remove all history entries."""
    _write_entries([])
