"""Automation status snapshot — n8n runtime + workflow counts."""

from __future__ import annotations

import time
from dataclasses import dataclass

import streamlit as st

from services.docker_service import get_n8n_status
from services.n8n_client import N8nAPIError, N8nClient
from utils.session import get_n8n_api_key, get_n8n_base_url, n8n_credentials_ready
from utils.user_feedback import explain_n8n_api_error

AUTOMATION_STATUS_CACHE_SEC = 45


@dataclass
class AutomationStatus:
    n8n_state: str
    n8n_label: str
    n8n_url: str
    port_open: bool
    active_workflows: int | None = None
    total_workflows: int | None = None
    workflows_note: str | None = None


def _runtime_label(state: str) -> str:
    return {
        "running": "Running",
        "starting": "Starting",
        "stopped": "Stopped",
        "unknown": "Unknown",
    }.get(state, state.title())


def fetch_automation_status(*, force_refresh: bool = False) -> AutomationStatus:
    """Build current automation status (cached briefly in session state)."""
    cache = st.session_state.get("automation_status_cache")
    now = time.time()
    if (
        not force_refresh
        and isinstance(cache, dict)
        and now - cache.get("ts", 0) < AUTOMATION_STATUS_CACHE_SEC
        and isinstance(cache.get("data"), AutomationStatus)
    ):
        return cache["data"]

    runtime = get_n8n_status()
    status = AutomationStatus(
        n8n_state=runtime.state,
        n8n_label=_runtime_label(runtime.state),
        n8n_url=runtime.url,
        port_open=runtime.port_open,
    )

    if runtime.state != "running" or not runtime.port_open:
        status.workflows_note = "Start n8n to load workflow counts."
    elif not n8n_credentials_ready():
        status.workflows_note = "Add n8n API credentials to load counts."
    else:
        try:
            client = N8nClient(get_n8n_base_url(), get_n8n_api_key())
            workflows = client.list_workflows()
            status.total_workflows = len(workflows)
            status.active_workflows = sum(1 for wf in workflows if wf.get("active"))
        except N8nAPIError as exc:
            fb = explain_n8n_api_error(exc, "loading workflow counts")
            status.workflows_note = fb.title

    st.session_state.automation_status_cache = {"ts": now, "data": status}
    return status


def invalidate_automation_status_cache() -> None:
    st.session_state.pop("automation_status_cache", None)
