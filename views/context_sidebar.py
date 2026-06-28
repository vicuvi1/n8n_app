"""Right Context sidebar — automation snapshot and contextual info."""

from __future__ import annotations

import html

import streamlit as st

from services.automation_status import fetch_automation_status


def _status_color(state: str) -> str:
    return {
        "running": "#34D399",
        "starting": "#FBBF24",
        "stopped": "#9CA3AF",
        "unknown": "#9CA3AF",
    }.get(state, "#94A3B8")


def render_automation_status_card() -> None:
    """Small card: n8n running state + active workflow count."""
    status = fetch_automation_status()
    color = _status_color(status.n8n_state)

    if status.active_workflows is not None and status.total_workflows is not None:
        workflows_line = (
            f'<strong style="color:#E8EAEF;font-size:1.1rem;">{status.active_workflows}</strong>'
            f'<span style="color:#8B93A7;"> active</span>'
            f'<span style="color:#6B7280;"> · {status.total_workflows} total</span>'
        )
    else:
        note = html.escape(status.workflows_note or "Unavailable")
        workflows_line = f'<span style="color:#8B93A7;font-size:0.8rem;">{note}</span>'

    st.markdown(
        f"""
        <div class="automation-status-card">
          <div class="context-card-title">Automation Status</div>
          <div class="automation-status-row">
            <span class="automation-status-dot" style="background:{color};"></span>
            <div>
              <div class="automation-status-label">n8n</div>
              <div class="automation-status-value" style="color:{color};">{html.escape(status.n8n_label)}</div>
            </div>
          </div>
          <div class="automation-status-url">{html.escape(status.n8n_url)}</div>
          <div class="automation-status-divider"></div>
          <div class="automation-status-label">Active workflows</div>
          <div class="automation-status-workflows">{workflows_line}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("↻ Refresh status", key="context_refresh_automation_status", use_container_width=True):
        fetch_automation_status(force_refresh=True)
        st.rerun()


def render_context_sidebar() -> None:
    """Right Context sidebar."""
    st.markdown(
        """
        <div class="context-sidebar-header">
          <span class="context-sidebar-badge">CTX</span>
          Context
        </div>
        """,
        unsafe_allow_html=True,
    )
    render_automation_status_card()

    st.markdown(
        """
        <div class="context-tips-card">
          <strong>Quick tips</strong>
          Press <kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>N</kbd> to open the Generator.<br/>
          Use the ✨ button (bottom-right) from any page.
        </div>
        """,
        unsafe_allow_html=True,
    )
