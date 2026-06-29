"""Shared runtime caches — fewer Docker/API calls per Streamlit rerun."""

from __future__ import annotations

import time

import streamlit as st

from services.docker_service import N8nRuntimeStatus, get_n8n_status, invalidate_n8n_status_cache

RUNTIME_STATUS_SESSION_SEC = 8


def get_shared_runtime_status(*, force_refresh: bool = False) -> N8nRuntimeStatus:
    """One Docker status check per rerun cycle (shared by header, hub, context)."""
    if not force_refresh:
        cached = st.session_state.get("_runtime_status")
        ts = float(st.session_state.get("_runtime_status_ts", 0))
        if isinstance(cached, N8nRuntimeStatus) and time.time() - ts < RUNTIME_STATUS_SESSION_SEC:
            return cached

    status = get_n8n_status(force_refresh=force_refresh)
    st.session_state._runtime_status = status
    st.session_state._runtime_status_ts = time.time()
    return status


def invalidate_runtime_status() -> None:
    st.session_state.pop("_runtime_status", None)
    st.session_state.pop("_runtime_status_ts", None)


def invalidate_all_status_caches() -> None:
    """Clear Docker + session status after start/stop/restart or manual refresh."""
    invalidate_n8n_status_cache()
    invalidate_runtime_status()
    from services.automation_status import invalidate_automation_status_cache

    invalidate_automation_status_cache()


def invalidate_data_caches() -> None:
    """Clear n8n API list caches after credentials change or workflow mutations."""
    st.session_state.pop("workflows_cache", None)
    st.session_state.pop("executions_cache", None)
    st.session_state.pop("hub_stats_cache", None)
    from services.automation_status import invalidate_automation_status_cache

    invalidate_automation_status_cache()


def invalidate_all_caches() -> None:
    """Clear runtime status and all n8n API-backed session caches."""
    invalidate_all_status_caches()
    invalidate_data_caches()
