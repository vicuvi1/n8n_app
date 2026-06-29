"""Automation Hub overview — landing page."""

import time

import streamlit as st

from config.navigation import HUB_PAGES, HUB_PAGE_ORDER
from services.n8n_client import N8nAPIError, N8nClient
from utils.session import credentials_ready, get_llm_provider, get_n8n_api_key, get_n8n_base_url, n8n_credentials_ready
from utils.ui import empty_state, kpi_cards, render_section_label, render_stat_grid, section_header
from utils.user_feedback import explain_n8n_api_error, show_user_feedback
from views.docker_panel import render_docker_status_banner
from views.n8n_quick_actions import render_n8n_quick_actions
from services.docker_service import get_n8n_status


def _fetch_hub_stats() -> tuple[dict, object | None]:
    cache = st.session_state.get("hub_stats_cache")
    now = time.time()
    if isinstance(cache, dict) and now - cache.get("ts", 0) < 45:
        return cache["stats"], cache.get("warning")

    stats = {
        "workflows": 0,
        "active": 0,
        "executions": 0,
        "failed": 0,
        "success": 0,
    }
    warning = None
    if not n8n_credentials_ready():
        return stats, warning

    try:
        client = N8nClient(get_n8n_base_url(), get_n8n_api_key())
        workflows = client.list_workflows()
        executions = client.list_executions(limit=50)
        stats["workflows"] = len(workflows)
        stats["active"] = sum(1 for w in workflows if w.get("active"))
        stats["executions"] = len(executions)
        stats["failed"] = sum(
            1 for e in executions if str(e.get("status", "")).lower() in ("error", "failed")
        )
        stats["success"] = sum(1 for e in executions if str(e.get("status", "")).lower() == "success")
    except N8nAPIError as exc:
        warning = explain_n8n_api_error(exc, "loading hub statistics")
        warning.level = "warning"

    st.session_state.hub_stats_cache = {"ts": time.time(), "stats": stats, "warning": warning}
    return stats, warning


def render_hub_home(set_active_page) -> None:
    """Render Automation Hub overview."""
    section_header(
        "Automation Hub",
        "Your command center for AI workflow generation, deployment, and monitoring.",
    )

    render_section_label("n8n runtime", "Docker container & quick actions")
    n8n_status = get_n8n_status()
    render_docker_status_banner(n8n_status)
    render_n8n_quick_actions(n8n_status, set_active_page=set_active_page)
    if st.button(
        "Open Docker Control Panel",
        key="hub_runtime_go_docker",
        use_container_width=False,
        type="secondary",
    ):
        set_active_page("docker")
        st.rerun()

    render_section_label("Hub metrics", "Live from your n8n instance")

    if not n8n_credentials_ready():
        empty_state(
            "🔗",
            "Connect n8n to unlock the hub",
            "Add your n8n URL and API key in the sidebar under **API Configuration**.",
        )
    else:
        stats, hub_warning = _fetch_hub_stats()
        if hub_warning:
            show_user_feedback(hub_warning)
        render_stat_grid(stats["workflows"], stats["active"], stats["executions"], stats["failed"])

        if stats["executions"] > 0:
            kpi_cards(stats["executions"], stats["success"], stats["failed"])

    render_section_label("Explore the Hub", "Jump to any section")
    cols = st.columns(len(HUB_PAGE_ORDER))
    for col, page_id in zip(cols, HUB_PAGE_ORDER):
        if page_id == "hub":
            continue
        page = HUB_PAGES[page_id]
        with col:
            st.markdown(
                f"""
                <div class="hub-card">
                  <div class="hub-card-icon">{page["icon"]}</div>
                  <div class="hub-card-title">{page["label"]}</div>
                  <div class="hub-card-desc">{page["description"]}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button(
                f"Open {page['label']}",
                key=f"hub_card_go_{page_id}",
                use_container_width=True,
                type="secondary",
            ):
                set_active_page(page_id)
                st.rerun()

    render_section_label("System snapshot")
    provider = get_llm_provider()
    snap1, snap2 = st.columns(2)
    with snap1:
        st.markdown(
            f"""
            <div class="section-card">
              <h3>LLM Provider</h3>
              <p><strong>{provider}</strong> — selected in sidebar</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with snap2:
        ready = "Ready" if credentials_ready() else "Incomplete"
        color = "#34D399" if credentials_ready() else "#FBBF24"
        st.markdown(
            f"""
            <div class="section-card">
              <h3>Credentials</h3>
              <p style="color:{color}; font-weight:600;">{ready}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
