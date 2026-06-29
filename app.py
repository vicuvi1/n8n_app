"""
n8n AI Management Dashboard — Streamlit entry point.

Automation Hub (sidebar):
  - Hub Overview
  - Docker n8n Control Panel
  - Generate Workflow with Gemini
  - Workflow Control Center
  - Live Execution Monitor
"""

import time

import pandas as pd
import streamlit as st

import config.constants as app_constants
from config.navigation import HUB_PAGES
from services.n8n_client import N8nAPIError, N8nClient
from utils.runtime_cache import get_shared_runtime_status, invalidate_data_caches
from utils.session import (
    credentials_ready,
    get_llm_provider,
    get_n8n_api_key,
    get_n8n_base_url,
    init_session_state,
    llm_credentials_ready,
    n8n_credentials_ready,
)
from utils.sidebar import render_sidebar
from utils.user_feedback import show_user_error
from utils.ui import (
    empty_state,
    inject_styles,
    kpi_cards,
    render_header,
    render_page_chip,
    section_header,
)
from views.context_sidebar import render_context_sidebar
from views.docker_panel import render_docker_panel
from views.generator_fab import render_generator_keyboard_shortcut, render_workflow_generator_fab
from views.generator_tab import render_generator_tab
from views.hub_home import render_hub_home

AUTO_REFRESH_INTERVAL = app_constants.AUTO_REFRESH_INTERVAL
EXECUTIONS_CACHE_SEC = getattr(app_constants, "EXECUTIONS_CACHE_SEC", 30)

# ─── Page config ─────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="n8n AI Management Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_session_state()
inject_styles()


def get_n8n_client() -> N8nClient:
    return N8nClient(get_n8n_base_url(), get_n8n_api_key())


def show_api_error(exc: Exception, context: str = "") -> None:
    """Show a friendly, actionable error message."""
    show_user_error(exc, context)


def _invalidate_workflow_caches() -> None:
    invalidate_data_caches()


def _get_workflows(*, force: bool = False) -> list:
    if not force and isinstance(st.session_state.get("workflows_cache"), list):
        return st.session_state.workflows_cache
    workflows = get_n8n_client().list_workflows()
    st.session_state.workflows_cache = workflows
    st.session_state.pop("hub_stats_cache", None)
    return workflows


def _get_executions(*, force: bool = False) -> list:
    cache = st.session_state.get("executions_cache")
    now = time.time()
    if (
        not force
        and isinstance(cache, dict)
        and now - cache.get("ts", 0) < EXECUTIONS_CACHE_SEC
        and isinstance(cache.get("data"), list)
    ):
        return cache["data"]
    executions = get_n8n_client().list_executions()
    st.session_state.executions_cache = {"ts": now, "data": executions}
    st.session_state.pop("hub_stats_cache", None)
    return executions


def _render_quick_setup_banner() -> None:
    missing = []
    if not n8n_credentials_ready():
        missing.append("**n8n URL & API key**")
    if not llm_credentials_ready():
        missing.append(f"**{get_llm_provider()} API key**")
    if missing:
        st.info(
            "Quick setup — Add "
            + " and ".join(missing)
            + " in the sidebar under **API Configuration**, then click **Save all keys**."
        )


def _go_to_page(page_id: str) -> None:
    st.session_state.active_hub_page = page_id
    st.rerun()


def _render_page_title() -> None:
    page_id = st.session_state.get("active_hub_page", "hub")
    page = HUB_PAGES.get(page_id, HUB_PAGES["hub"])
    render_page_chip(page["icon"], page["label"], page["description"])


# ─── Workflow Control Center ───────────────────────────────────────────────────

def tab_manager() -> None:
    section_header(
        "Workflow Control Center",
        "View, activate, deactivate, and delete workflows on your n8n server.",
    )

    if not n8n_credentials_ready():
        empty_state("🔗", "n8n connection required", "Enter n8n URL and API key in sidebar → API Configuration.")
        return

    _, btn_col = st.columns([4, 1])
    with btn_col:
        refresh = st.button("↻ Refresh", use_container_width=True)

    try:
        workflows = _get_workflows(force=refresh)

        if not workflows:
            empty_state("📋", "No workflows yet", "Create one in the AI Generator or in n8n directly.")
            return

        active_count = sum(1 for wf in workflows if wf.get("active"))
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Workflows", len(workflows))
        m2.metric("Active", active_count)
        m3.metric("Inactive", len(workflows) - active_count)

        rows = [
            {
                "Name": wf.get("name", "Unnamed"),
                "ID": wf.get("id", ""),
                "Status": "🟢 Active" if wf.get("active") else "⚪ Inactive",
            }
            for wf in workflows
        ]
        with st.container(border=True):
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

        st.markdown("##### Workflow Actions")
        search = st.text_input("Search workflows", placeholder="Filter by name…", key="control_center_search")
        filtered = workflows
        if search.strip():
            needle = search.strip().lower()
            filtered = [wf for wf in workflows if needle in str(wf.get("name", "")).lower()]

        if not filtered:
            st.info("No workflows match your search.")
            return

        labels = [
            f"{wf.get('name', 'Unnamed')}  ·  {'Active' if wf.get('active') else 'Inactive'}  ·  {wf.get('id', '')}"
            for wf in filtered
        ]
        selected_idx = st.selectbox("Select workflow", range(len(filtered)), format_func=lambda i: labels[i])
        wf = filtered[selected_idx]
        wf_id = wf.get("id", "")
        wf_name = wf.get("name", "Unnamed")
        is_active = wf.get("active", False)

        wf_key = wf_id or f"idx_{selected_idx}"

        with st.container(border=True):
            st.markdown(f"**{wf_name}** · `{'Active' if is_active else 'Inactive'}` · `{wf_id}`")
            action_col1, action_col2, _ = st.columns([1, 1, 2])
            with action_col1:
                toggle_label = "⏸ Deactivate" if is_active else "▶ Activate"
                if st.button(toggle_label, key=f"toggle_{wf_key}", use_container_width=True):
                    try:
                        get_n8n_client().toggle_workflow(wf_id, is_active)
                        _invalidate_workflow_caches()
                        st.rerun()
                    except N8nAPIError as exc:
                        show_api_error(exc, "updating the workflow")
            with action_col2:
                if st.session_state.delete_confirm_id == wf_id:
                    if st.button("🗑 Confirm delete", key=f"confirm_del_{wf_key}", type="primary"):
                        try:
                            get_n8n_client().delete_workflow(wf_id)
                            st.session_state.delete_confirm_id = None
                            _invalidate_workflow_caches()
                            st.rerun()
                        except N8nAPIError as exc:
                            show_api_error(exc, "deleting the workflow")
                    if st.button("Cancel", key=f"cancel_del_{wf_key}"):
                        st.session_state.delete_confirm_id = None
                        st.rerun()
                else:
                    if st.button("🗑 Delete", key=f"delete_{wf_key}", use_container_width=True):
                        st.session_state.delete_confirm_id = wf_id
                        st.rerun()
    except N8nAPIError as exc:
        show_api_error(exc, "loading workflows")


# ─── Live Execution Monitor ──────────────────────────────────────────────────

def _highlight_failed(row: pd.Series) -> list[str]:
    status = str(row.get("Status", "")).lower()
    if status in ("error", "failed"):
        return ["background-color: #3b1212; color: #fca5a5"] * len(row)
    return [""] * len(row)


def _format_executions_df(executions: list) -> pd.DataFrame:
    rows = []
    for ex in executions:
        rows.append(
            {
                "Execution ID": ex.get("id", ""),
                "Status": ex.get("status", "unknown"),
                "Started At": ex.get("startedAt", ""),
                "Finished At": ex.get("stoppedAt") or ex.get("finishedAt", ""),
                "Workflow ID": ex.get("workflowId", ""),
            }
        )
    df = pd.DataFrame(rows)
    if not df.empty:
        for col in ("Started At", "Finished At"):
            df[col] = pd.to_datetime(df[col], errors="coerce").dt.strftime("%Y-%m-%d %H:%M:%S")
    return df


def tab_executions() -> None:
    section_header(
        "Live Execution Monitor",
        "SOC-style log of recent workflow runs — failed executions highlighted in red.",
    )

    if not n8n_credentials_ready():
        empty_state("📡", "n8n connection required", "Enter n8n URL and API key in sidebar → API Configuration.")
        return

    ctrl_col, refresh_col = st.columns([3, 1])
    with ctrl_col:
        auto_refresh = st.checkbox(f"Auto-refresh every {AUTO_REFRESH_INTERVAL}s", value=False)
    with refresh_col:
        force_refresh = st.button("↻ Refresh now", use_container_width=True)

    try:
        executions = _get_executions(force=force_refresh or auto_refresh)
        if not executions:
            empty_state("📭", "No executions yet", "Run a workflow in n8n to see history here.")
        else:
            failed = sum(1 for ex in executions if str(ex.get("status", "")).lower() in ("error", "failed"))
            success = sum(1 for ex in executions if str(ex.get("status", "")).lower() == "success")
            kpi_cards(len(executions), success, failed)
            df = _format_executions_df(executions)
            styled = df.style.apply(_highlight_failed, axis=1)
            with st.container(border=True):
                st.dataframe(styled, use_container_width=True, hide_index=True)
    except N8nAPIError as exc:
        show_api_error(exc, "loading executions")

    if auto_refresh:
        time.sleep(AUTO_REFRESH_INTERVAL)
        st.rerun()


# ─── Main ────────────────────────────────────────────────────────────────────

def main() -> None:
    render_sidebar()
    status = get_shared_runtime_status()
    page = st.session_state.get("active_hub_page", "hub")

    if page == "generator":
        render_header(status)
        _render_page_title()
        if not credentials_ready():
            _render_quick_setup_banner()
        render_generator_tab(show_api_error)
    else:
        main_col, context_col = st.columns([3.4, 1], gap="large")

        with context_col:
            render_context_sidebar()

        with main_col:
            render_header(status)
            _render_page_title()
            if page == "hub" and not credentials_ready():
                _render_quick_setup_banner()

            if page == "hub":
                render_hub_home(_go_to_page)
            elif page == "docker":
                render_docker_panel()
            elif page == "control":
                tab_manager()
            elif page == "monitor":
                tab_executions()

    render_generator_keyboard_shortcut(_go_to_page)
    render_workflow_generator_fab(_go_to_page)


if __name__ == "__main__":
    main()
