"""Docker n8n Control Panel — start, stop, restart, live status."""

from __future__ import annotations

import html
import time
from datetime import datetime
from typing import Callable

import streamlit as st

from config.constants import DOCKER_STATUS_REFRESH_SEC, N8N_DEFAULT_URL
from services.docker_service import (
    DockerCommandResult,
    DockerError,
    get_n8n_status,
    invalidate_n8n_status_cache,
    restart_n8n,
    start_n8n,
    stop_n8n,
)
from utils.ui import section_header, render_section_label
from utils.user_feedback import explain_docker_error
from views.n8n_quick_actions import render_n8n_quick_actions

DOCKER_LOG_MAX = 50


def _init_docker_log() -> None:
    if "docker_log" not in st.session_state:
        st.session_state.docker_log = []


def _append_docker_log(
    level: str,
    command: str,
    message: str,
    detail: str = "",
) -> None:
    _init_docker_log()
    st.session_state.docker_log.insert(
        0,
        {
            "time": datetime.now().strftime("%H:%M:%S"),
            "level": level,
            "command": command,
            "message": message,
            "detail": detail,
        },
    )
    st.session_state.docker_log = st.session_state.docker_log[:DOCKER_LOG_MAX]


def _run_docker_action(command_label: str, action: Callable[[], DockerCommandResult]) -> None:
    try:
        result = action()
        invalidate_n8n_status_cache()
        _append_docker_log("success", result.command, result.message, result.output)
    except DockerError as exc:
        fb = explain_docker_error(exc)
        _append_docker_log("error", command_label, fb.as_plain(), detail=str(exc))


def _render_docker_log() -> None:
    entries = st.session_state.get("docker_log", [])
    log_col, clear_col = st.columns([4, 1])
    with log_col:
        st.markdown("##### Command output")
    with clear_col:
        if st.button("Clear log", key="docker_clear_log", use_container_width=True):
            st.session_state.docker_log = []
            st.rerun()

    if not entries:
        st.markdown(
            '<div class="docker-log-panel"><span class="docker-log-empty">No commands run yet. '
            "Output from Start, Stop, and Restart will appear here.</span></div>",
            unsafe_allow_html=True,
        )
        return

    rows: list[str] = []
    for entry in entries:
        level = entry["level"]
        msg_class = f"docker-log-msg-{level}"
        detail_html = ""
        if entry.get("detail"):
            detail_html = (
                f'<pre class="docker-log-detail">{html.escape(entry["detail"])}</pre>'
            )
        rows.append(
            f"""
            <div class="docker-log-entry docker-log-{level}">
              <div class="docker-log-meta">
                <span class="docker-log-time">{html.escape(entry["time"])}</span>
                <span class="docker-log-cmd">{html.escape(entry["command"])}</span>
              </div>
              <div class="{msg_class}">{html.escape(entry["message"])}</div>
              {detail_html}
            </div>
            """
        )

    st.markdown(
        f'<div class="docker-log-panel">{"".join(rows)}</div>',
        unsafe_allow_html=True,
    )


def _status_color(state: str) -> str:
    return {
        "running": "#34D399",
        "starting": "#FBBF24",
        "stopped": "#9CA3AF",
        "unknown": "#9CA3AF",
    }.get(state, "#94A3B8")


def _status_dot(state: str) -> str:
    color = _status_color(state)
    pulse = "animation: docker-pulse 1.5s ease-in-out infinite;" if state == "starting" else ""
    return f'<span class="docker-status-dot" style="background:{color}; {pulse}"></span>'


def render_docker_status_banner(status=None) -> None:
    """Compact status strip — reusable on Hub Overview and Docker page."""
    if status is None:
        status = get_n8n_status()
    color = _status_color(status.state)
    st.markdown(
        f"""
        <div class="docker-status-banner" style="border-color:{color}33;">
          {_status_dot(status.state)}
          <span class="docker-status-text" style="color:{color};">{status.message}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_docker_panel() -> None:
    """Full Docker n8n Control Panel with action buttons."""
    _init_docker_log()

    section_header(
        "Docker n8n Control Panel",
        "Start, stop, or restart your local n8n Docker container.",
    )

    status = get_n8n_status()
    render_docker_status_banner(status)
    render_n8n_quick_actions(status)

    render_section_label("Container actions", "Docker commands for the n8n container")
    col_start, col_stop, col_restart = st.columns(3)

    with col_start:
        if st.button("▶️ Start n8n (Docker)", use_container_width=True, type="primary"):
            _run_docker_action("docker start n8n", start_n8n)
            st.rerun()

    with col_stop:
        if st.button("⏹️ Stop n8n", use_container_width=True, type="secondary"):
            _run_docker_action("docker stop n8n", stop_n8n)
            st.rerun()

    with col_restart:
        if st.button("🔄 Restart n8n", use_container_width=True, type="secondary"):
            _run_docker_action("docker restart n8n", restart_n8n)
            st.rerun()

    _render_docker_log()

    st.markdown("---")
    refresh_col, auto_col = st.columns([1, 2])
    with refresh_col:
        if st.button("↻ Refresh status", use_container_width=True):
            invalidate_n8n_status_cache()
            status = get_n8n_status(force_refresh=True)
            _append_docker_log("info", "status check", status.message)
            st.rerun()
    with auto_col:
        auto_refresh = st.checkbox(
            "Live status (auto-refresh every 10s)",
            value=False,
            key="docker_auto_refresh",
        )

    with st.expander("Docker details"):
        st.markdown(
            f"""
            - **Container name:** `{status.container_name}`
            - **Default URL:** [{N8N_DEFAULT_URL}]({N8N_DEFAULT_URL})
            - **Container running:** {"Yes" if status.container_running else "No"}
            - **Port 5678 open:** {"Yes" if status.port_open else "No"}
            """
        )
        st.code(
            f"docker start {status.container_name}\n"
            f"docker stop {status.container_name}\n"
            f"docker restart {status.container_name}",
            language="bash",
        )

    if auto_refresh:
        time.sleep(DOCKER_STATUS_REFRESH_SEC)
        st.rerun()
