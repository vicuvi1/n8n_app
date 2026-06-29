"""Quick actions when n8n is running — open, list workflows, create blank."""

from __future__ import annotations

from collections.abc import Callable

import streamlit as st

from services.docker_service import N8nRuntimeStatus
from services.n8n_client import N8nAPIError, N8nClient
from utils.runtime_cache import get_shared_runtime_status, invalidate_data_caches
from utils.session import (
    get_n8n_api_key,
    get_n8n_base_url,
    get_n8n_instance_url,
    n8n_credentials_ready,
)
from utils.user_feedback import explain_n8n_api_error, feedback_for_session_message, show_user_feedback


def _navigate_to(page_id: str, set_active_page: Callable[[str], None] | None) -> None:
    invalidate_data_caches()
    st.session_state.pop("n8n_quick_action_feedback", None)
    if set_active_page is not None:
        set_active_page(page_id)
    else:
        st.session_state.active_hub_page = page_id
        st.rerun()


def _create_blank_workflow(instance_url: str) -> None:
    if not n8n_credentials_ready():
        st.session_state.n8n_quick_action_feedback = {
            "level": "error",
            "feedback": feedback_for_session_message(
                "Add your n8n Instance URL and API Key in the sidebar to create workflows."
            ).__dict__,
        }
        return

    try:
        client = N8nClient(get_n8n_base_url(), get_n8n_api_key())
        created = client.create_blank_workflow()
        workflow_id = created.get("id", "")
        workflow_name = created.get("name", "New Workflow")
        editor_url = f"{instance_url.rstrip('/')}/workflow/{workflow_id}" if workflow_id else None
        st.session_state.n8n_quick_action_feedback = {
            "level": "success",
            "message": f'Blank workflow **"{workflow_name}"** created on n8n.',
            "editor_url": editor_url,
            "workflow_id": workflow_id,
        }
        invalidate_data_caches()
        st.toast(f'Created "{workflow_name}"', icon="✅")
    except N8nAPIError as exc:
        st.session_state.n8n_quick_action_feedback = {
            "level": "error",
            "feedback": explain_n8n_api_error(exc, "creating a blank workflow").__dict__,
        }


def _render_quick_action_feedback() -> None:
    from utils.user_feedback import UserFeedback

    feedback = st.session_state.get("n8n_quick_action_feedback")
    if not feedback:
        return

    if feedback.get("feedback"):
        show_user_feedback(UserFeedback(**feedback["feedback"]))
        editor_url = feedback.get("editor_url")
        if feedback.get("level") == "success" and editor_url:
            st.link_button("Open new workflow in n8n ↗", editor_url)
        if st.button("Dismiss", key="n8n_quick_action_dismiss", use_container_width=True):
            st.session_state.pop("n8n_quick_action_feedback", None)
            st.rerun()
        return

    level = feedback.get("level", "info")
    message = feedback.get("message", "")
    if level == "success":
        st.success(message)
        editor_url = feedback.get("editor_url")
        if editor_url:
            st.link_button("Open new workflow in n8n ↗", editor_url)
    elif level == "error":
        st.error(message)
    else:
        st.info(message)

    if st.button("Dismiss", key="n8n_quick_action_dismiss", use_container_width=True):
        st.session_state.pop("n8n_quick_action_feedback", None)
        st.rerun()


def render_n8n_quick_actions(
    status: N8nRuntimeStatus | None = None,
    *,
    set_active_page: Callable[[str], None] | None = None,
    section_title: str = "Quick actions",
) -> None:
    """Show open / list / create actions when n8n is running."""
    if status is None:
        status = get_shared_runtime_status()

    if status.state != "running" or not status.port_open:
        return

    instance_url = get_n8n_instance_url() or status.url
    browser_url = instance_url.rstrip("/")

    st.markdown(f"##### {section_title}")
    open_col, list_col, create_col = st.columns(3)

    with open_col:
        st.link_button(
            "Open n8n in browser",
            browser_url,
            use_container_width=True,
            help="Open your n8n instance in a new tab.",
        )

    with list_col:
        list_disabled = not n8n_credentials_ready()
        if st.button(
            "List my workflows",
            use_container_width=True,
            disabled=list_disabled,
            help="Open Workflow Control Center with your n8n workflows.",
            key="n8n_quick_list_workflows",
        ):
            st.session_state.n8n_quick_action_feedback = None
            _navigate_to("control", set_active_page)

    with create_col:
        create_disabled = not n8n_credentials_ready()
        if st.button(
            "Create blank workflow",
            use_container_width=True,
            disabled=create_disabled,
            help="Create a new workflow with a manual trigger via the n8n API.",
            key="n8n_quick_create_blank",
        ):
            _create_blank_workflow(browser_url)

    if list_disabled or create_disabled:
        st.caption("Save **n8n credentials** in the sidebar to list or create workflows via API.")

    _render_quick_action_feedback()
