"""Persist user-saved workflow templates (local JSON, gitignored)."""

from __future__ import annotations

import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

USER_TEMPLATES_PATH = Path(__file__).resolve().parent.parent / "data" / "user_workflow_templates.json"


class TemplateStoreError(Exception):
    """Raised when a template cannot be saved or loaded."""


def _slugify(text: str) -> str:
    slug = re.sub(r"[^\w\s-]", "", text.strip().lower())
    slug = re.sub(r"[-\s]+", "_", slug)
    return slug[:48] or "template"


def safe_workflow_filename(name: str) -> str:
    """Build a safe .json download filename from a workflow name."""
    return f"{_slugify(name)}.json"


def _load_user_templates() -> dict[str, dict[str, Any]]:
    if not USER_TEMPLATES_PATH.is_file():
        return {}
    try:
        with USER_TEMPLATES_PATH.open(encoding="utf-8") as handle:
            data = json.load(handle)
    except (json.JSONDecodeError, OSError) as exc:
        raise TemplateStoreError(f"Could not read saved templates: {USER_TEMPLATES_PATH}") from exc

    templates = data.get("templates", {})
    return templates if isinstance(templates, dict) else {}


def _write_user_templates(templates: dict[str, dict[str, Any]]) -> None:
    USER_TEMPLATES_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {"templates": templates}
    tmp_path = USER_TEMPLATES_PATH.with_suffix(".json.tmp")
    try:
        tmp_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        tmp_path.replace(USER_TEMPLATES_PATH)
    except OSError as exc:
        raise TemplateStoreError(f"Could not write saved templates: {USER_TEMPLATES_PATH}") from exc


def get_merged_templates() -> dict[str, dict[str, Any]]:
    """User-saved templates only (ready-made templates are separate)."""
    return dict(_load_user_templates())


def get_merged_template_keys() -> list[str]:
    """Saved template ids for the optional user-template loader."""
    return sorted(_load_user_templates().keys())


def save_user_template(label: str, workflow: dict[str, Any], prompt: str = "") -> str:
    """Save workflow JSON as a reusable user template. Returns new template id."""
    name = label.strip()
    if not name:
        raise TemplateStoreError("Template name is required.")

    templates = _load_user_templates()
    template_id = f"user_{_slugify(name)}_{uuid.uuid4().hex[:8]}"
    templates[template_id] = {
        "label": name,
        "prompt": prompt.strip(),
        "workflow": workflow,
        "saved_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    _write_user_templates(templates)
    return template_id
