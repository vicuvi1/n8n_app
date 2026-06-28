"""AI Workflow Generator — Gemini-powered workflow creation in the Automation Hub."""

from __future__ import annotations

import json

from dataclasses import asdict
from datetime import datetime

import streamlit as st

from config.constants import (
    DEFAULT_WORKFLOW_OPTIMIZATION,
    GEMINI_MODELS,
    WORKFLOW_OPTIMIZATION_KEYS,
    WORKFLOW_OPTIMIZATION_OPTIONS,
)
from config.workflow_templates import READY_MADE_TEMPLATE_KEYS, READY_MADE_TEMPLATES
from services.llm_client import LLMError, MissingDependencyError, generate_workflow_with_gemini
from services.n8n_client import N8nClient, WorkflowPushResult
from utils.json_utils import normalize_workflow, parse_workflow_json
from utils.session import (
    get_gemini_api_key,
    get_gemini_model,
    get_n8n_api_key,
    get_n8n_base_url,
    get_n8n_instance_url,
    n8n_credentials_ready,
)
from utils.template_store import (
    TemplateStoreError,
    get_merged_template_keys,
    get_merged_templates,
    safe_workflow_filename,
    save_user_template,
)
from utils.user_feedback import feedback_for_session_message
from utils.ui import (
    empty_state,
    render_copy_json_button,
    render_flow_map,
    render_generator_steps,
    render_push_feedback,
    render_section_label,
    render_workflow_json_editor,
    reset_workflow_json_editor,
    section_header,
)
from utils.workflow_history import (
    WORKFLOW_HISTORY_MAX,
    WorkflowHistoryError,
    add_workflow_to_history,
    delete_history_entry,
    get_history_entry,
    list_workflow_history,
)
from utils.workflow_viz import build_linear_flow_text, build_mermaid_diagram, get_node_summary


def _format_history_timestamp(iso_value: str) -> str:
    if not iso_value:
        return "Unknown time"
    try:
        dt = datetime.fromisoformat(iso_value.replace("Z", "+00:00"))
        return dt.strftime("%b %d, %Y · %H:%M UTC")
    except ValueError:
        return iso_value[:16].replace("T", " ")


def _init_generator_state() -> None:
    if "workflow_prompt" not in st.session_state:
        st.session_state.workflow_prompt = ""
    if "_last_applied_template" not in st.session_state:
        st.session_state._last_applied_template = "none"
    if "workflow_editor_nonce" not in st.session_state:
        st.session_state.workflow_editor_nonce = 0
    if "show_save_template_form" not in st.session_state:
        st.session_state.show_save_template_form = False
    if "last_push_result" not in st.session_state:
        st.session_state.last_push_result = None
    if "history_view_id" not in st.session_state:
        st.session_state.history_view_id = None
    if "workflow_optimization" not in st.session_state:
        st.session_state.workflow_optimization = DEFAULT_WORKFLOW_OPTIMIZATION


def _get_workflow_optimization() -> str:
    mode = st.session_state.get("workflow_optimization", DEFAULT_WORKFLOW_OPTIMIZATION)
    return mode if mode in WORKFLOW_OPTIMIZATION_KEYS else DEFAULT_WORKFLOW_OPTIMIZATION


def _render_optimization_options() -> str:
    """Speed vs reliability toggle for workflow generation."""
    st.markdown('<div class="hub-panel">', unsafe_allow_html=True)
    st.markdown('<p class="hub-panel-title">Optimization</p>', unsafe_allow_html=True)
    mode = st.radio(
        "Workflow optimization",
        options=WORKFLOW_OPTIMIZATION_KEYS,
        format_func=lambda key: WORKFLOW_OPTIMIZATION_OPTIONS[key],
        horizontal=True,
        key="workflow_optimization",
        help=(
            "**Speed** — fewer nodes, linear flows, minimal branching. "
            "**Reliability** — validation, error branches, and failure alerts."
        ),
    )
    if mode == "speed":
        st.caption("Fewer nodes and simpler paths — best for fast prototypes and low-latency automations.")
    else:
        st.caption("Extra validation and error handling — best for production and critical automations.")
    st.markdown("</div>", unsafe_allow_html=True)
    return mode


def _workflow_from_editor(fallback: dict) -> dict:
    """Use the latest valid JSON from the editor, falling back to session workflow."""
    json_text = st.session_state.get("workflow_json_text", "")
    if not json_text.strip():
        return fallback
    try:
        return normalize_workflow(parse_workflow_json(json_text))
    except ValueError:
        return fallback


def _store_push_result(result: WorkflowPushResult) -> None:
    payload = asdict(result)
    payload["editor_url"] = result.editor_url
    st.session_state.last_push_result = payload


def _render_gemini_prompt_section() -> str:
    """Primary input — large text area for describing the desired automation."""
    model = get_gemini_model()
    model_label = GEMINI_MODELS.get(model, model)

    st.markdown(
        f"""
        <div class="generator-gemini-section">
          <div class="gen-badge">✨ Gemini AI</div>
          <h3>Generate Workflow with Gemini</h3>
          <p>Describe the automation you want — triggers, APIs, conditions, alerts, and integrations.
          <strong style="color:#C5CAD6;">{model_label}</strong> will turn your description into deployable n8n workflow JSON.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    return st.text_area(
        "Describe your automation",
        height=300,
        label_visibility="collapsed",
        placeholder=(
            "Example: When a new email arrives in Gmail with subject containing 'invoice', "
            "extract the sender and amount, look up the vendor in Airtable, and post a summary "
            "to Slack #finance. If the amount is over $5,000, also create a Jira ticket."
        ),
        key="workflow_prompt",
    )


def _apply_template_selection() -> None:
    templates = get_merged_templates()
    keys = get_merged_template_keys()
    if not keys:
        return

    with st.expander("My saved templates", expanded=False):
        template_key = st.selectbox(
            "Load a saved template",
            options=keys,
            format_func=lambda k: templates[k]["label"],
            key="user_saved_template_select",
        )
        if st.button("Load template", key="load_user_saved_template", use_container_width=True, type="secondary"):
            selected = templates[template_key]
            if selected.get("prompt"):
                st.session_state.workflow_prompt = selected["prompt"]
            if selected.get("workflow"):
                st.session_state.generated_workflow = selected["workflow"]
                reset_workflow_json_editor(selected["workflow"])
                st.session_state.last_push_result = None
            st.rerun()


def _render_ready_made_templates(show_api_error) -> str | None:
    """
    Clickable template grid. Returns template key if one was clicked and generation ran.
    """
    model_label = GEMINI_MODELS.get(get_gemini_model(), get_gemini_model())
    render_section_label("Ready-made templates", f"One-click generate with {model_label}")

    clicked_prompt: str | None = None

    for row_start in range(0, len(READY_MADE_TEMPLATE_KEYS), 4):
        row_keys = READY_MADE_TEMPLATE_KEYS[row_start : row_start + 4]
        cols = st.columns(4)
        for col, key in zip(cols, row_keys):
            template = READY_MADE_TEMPLATES[key]
            with col:
                st.markdown(
                    f"""
                    <div class="template-tile">
                      <div class="template-tile-icon">{template["icon"]}</div>
                      <div class="template-tile-title">{template["label"]}</div>
                      <div class="template-tile-desc">{template["description"]}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if st.button(
                    "Generate",
                    key=f"ready_template_{key}",
                    use_container_width=True,
                    type="secondary",
                ):
                    st.session_state.workflow_prompt = template["prompt"]
                    st.session_state._active_template_label = template["label"]
                    _run_generation(
                        template["prompt"],
                        show_api_error,
                        template_label=template["label"],
                    )
                    clicked_prompt = template["prompt"]

    return clicked_prompt


def _run_generation(
    prompt: str,
    show_api_error,
    *,
    template_label: str | None = None,
) -> None:
    api_key = get_gemini_api_key()
    model = get_gemini_model()
    model_label = GEMINI_MODELS.get(model, model)

    optimization = _get_workflow_optimization()
    optimization_label = WORKFLOW_OPTIMIZATION_OPTIONS[optimization]

    spinner_text = (
        f'Generating "{template_label}" ({optimization_label}) with {model_label}…'
        if template_label
        else f"Generating ({optimization_label}) with {model_label}…"
    )

    with st.spinner(spinner_text):
        try:
            workflow = generate_workflow_with_gemini(
                api_key,
                prompt,
                model,
                optimization_mode=optimization,
            )
            st.session_state.generated_workflow = workflow
            st.session_state.api_error = None
            reset_workflow_json_editor(workflow)
            st.session_state.last_push_result = None
            try:
                add_workflow_to_history(
                    workflow,
                    prompt=prompt,
                    model=model,
                    source=template_label or "custom",
                    optimization=optimization,
                )
            except WorkflowHistoryError as exc:
                st.warning(f"Workflow generated but history was not saved: {exc}")
            st.success(
                f'✅ Workflow **"{workflow.get("name", "Untitled")}"** generated with **{model_label}** '
                f'({optimization_label}).'
            )
        except MissingDependencyError as exc:
            st.session_state.generated_workflow = None
            st.error(str(exc))
            st.info("Then restart the app: `pip install -r requirements.txt`")
        except (LLMError, ValueError) as exc:
            st.session_state.generated_workflow = None
            show_api_error(exc)


def _push_to_n8n(workflow: dict) -> None:
    if st.session_state.get("workflow_json_error"):
        fb = feedback_for_session_message("Fix JSON errors in the editor before pushing to n8n.")
        _store_push_result(WorkflowPushResult(success=False, error=fb.message))
        return

    if not n8n_credentials_ready():
        fb = feedback_for_session_message(
            "Add your n8n Instance URL and API Key in the sidebar, then click Save n8n."
        )
        _store_push_result(WorkflowPushResult(success=False, error=fb.message))
        return

    workflow = _workflow_from_editor(workflow)
    instance_url = get_n8n_instance_url()

    with st.spinner(f"Pushing to n8n at {instance_url}…"):
        client = N8nClient(get_n8n_base_url(), get_n8n_api_key())
        result = client.push_workflow(workflow, instance_url)
        _store_push_result(result)

        if result.success:
            st.session_state.generated_workflow = workflow
            st.toast(f'Workflow "{result.workflow_name}" pushed to n8n', icon="✅")


def _render_save_template_form(workflow: dict) -> None:
    if not st.session_state.get("show_save_template_form"):
        return

    default_name = workflow.get("name", "My Workflow")
    with st.container(border=True):
        st.markdown("##### Save as Template")
        template_name = st.text_input(
            "Template name",
            value=default_name,
            key="save_template_name_input",
        )
        save_col, cancel_col = st.columns(2)
        with save_col:
            if st.button("Confirm save", type="primary", use_container_width=True, key="confirm_save_template"):
                try:
                    template_id = save_user_template(
                        template_name,
                        workflow,
                        st.session_state.get("workflow_prompt", ""),
                    )
                    st.session_state.show_save_template_form = False
                    st.session_state._last_applied_template = template_id
                    st.success(f'Template **"{template_name.strip()}"** saved.')
                    st.rerun()
                except TemplateStoreError as exc:
                    st.error(str(exc))
        with cancel_col:
            if st.button("Cancel", use_container_width=True, key="cancel_save_template"):
                st.session_state.show_save_template_form = False
                st.rerun()


def _render_workflow_action_buttons(json_str: str, workflow: dict) -> None:
    """Action bar under the JSON preview."""
    st.markdown('<div class="action-toolbar">', unsafe_allow_html=True)
    st.markdown('<div class="action-toolbar-title">Workflow actions</div>', unsafe_allow_html=True)
    col_copy, col_push, col_save, col_download = st.columns(4)

    with col_copy:
        render_copy_json_button(json_str, button_key="copy_workflow_json", compact=True)

    with col_push:
        push_disabled = bool(st.session_state.get("workflow_json_error")) or not n8n_credentials_ready()
        if st.button(
            "Push to n8n",
            use_container_width=True,
            disabled=push_disabled,
            help="POST /api/v1/workflows using saved n8n credentials from the sidebar.",
            key="push_workflow_to_n8n",
            type="primary",
        ):
            _push_to_n8n(workflow)

    with col_save:
        if st.button(
            "Save as Template",
            use_container_width=True,
            disabled=bool(st.session_state.get("workflow_json_error")),
            key="save_workflow_template",
            type="secondary",
        ):
            st.session_state.show_save_template_form = True

    with col_download:
        st.download_button(
            "Download as .json file",
            data=json_str,
            file_name=safe_workflow_filename(workflow.get("name", "workflow")),
            mime="application/json",
            use_container_width=True,
            key="download_workflow_json",
        )

    render_push_feedback(st.session_state.get("last_push_result"))
    st.markdown("</div>", unsafe_allow_html=True)
    _render_save_template_form(workflow)


def _render_workflow_output(show_api_error) -> None:
    workflow = st.session_state.get("generated_workflow")
    if not workflow:
        return

    render_section_label("Workflow JSON", "Edit, validate, and push to n8n")

    updated = render_workflow_json_editor(workflow)
    st.session_state.generated_workflow = updated

    json_str = st.session_state.get("workflow_json_text", json.dumps(updated, indent=2))
    _render_workflow_action_buttons(json_str, updated)

    render_section_label("Visual workflow map", "Node flow preview")
    mermaid = build_mermaid_diagram(updated)
    render_flow_map(
        mermaid,
        build_linear_flow_text(updated),
        get_node_summary(updated),
    )


def _reuse_history_entry(entry: dict) -> None:
    workflow = entry.get("workflow")
    if not isinstance(workflow, dict):
        st.error("This history entry has no workflow data.")
        return

    st.session_state.generated_workflow = workflow
    if entry.get("prompt"):
        st.session_state.workflow_prompt = entry["prompt"]
    reset_workflow_json_editor(workflow)
    st.session_state.last_push_result = None
    st.session_state.history_view_id = None
    st.toast(f'Loaded "{entry.get("name", "workflow")}" from history', icon="↩️")


def _render_workflow_history() -> None:
    """Workflow History — view, re-use, or delete past generations."""
    import html

    render_section_label("Workflow history", f"Last {WORKFLOW_HISTORY_MAX} generations on this device")

    try:
        entries = list_workflow_history()
    except WorkflowHistoryError as exc:
        st.error(str(exc))
        return

    if not entries:
        empty_state(
            "🕘",
            "No history yet",
            "Generate a workflow above and it will appear here for quick re-use.",
        )
        return

    for entry in entries:
        entry_id = entry.get("id", "")
        meta_parts = [
            _format_history_timestamp(entry.get("created_at", "")),
            f"{entry.get('node_count', 0)} nodes",
        ]
        if entry.get("model"):
            meta_parts.append(entry["model"])
        if entry.get("source") and entry["source"] != "custom":
            meta_parts.append(entry["source"])
        if entry.get("optimization"):
            label = WORKFLOW_OPTIMIZATION_OPTIONS.get(
                entry["optimization"], entry["optimization"]
            )
            meta_parts.append(label)

        name = html.escape(str(entry.get("name", "Untitled Workflow")))
        meta_text = html.escape(" · ".join(meta_parts))
        st.markdown(
            f"""
            <div class="history-card">
              <div class="history-item">
                <div class="history-item-title">{name}</div>
                <div class="history-item-meta">{meta_text}</div>
              </div>
            """,
            unsafe_allow_html=True,
        )

        view_col, reuse_col, delete_col, _ = st.columns([1, 1, 1, 1])
        with view_col:
            if st.button("View", key=f"history_view_{entry_id}", use_container_width=True, type="secondary"):
                st.session_state.history_view_id = entry_id
        with reuse_col:
            if st.button("Re-use", key=f"history_reuse_{entry_id}", use_container_width=True, type="secondary"):
                _reuse_history_entry(entry)
                st.rerun()
        with delete_col:
            if st.button("Delete", key=f"history_delete_{entry_id}", use_container_width=True, type="secondary"):
                try:
                    delete_history_entry(entry_id)
                    if st.session_state.get("history_view_id") == entry_id:
                        st.session_state.history_view_id = None
                    st.toast("Removed from history", icon="🗑️")
                    st.rerun()
                except WorkflowHistoryError as exc:
                    st.error(str(exc))
        st.markdown("</div>", unsafe_allow_html=True)

    view_id = st.session_state.get("history_view_id")
    if view_id:
        entry = get_history_entry(view_id)
        if entry and isinstance(entry.get("workflow"), dict):
            with st.container(border=True):
                st.markdown(f"**Preview:** {entry.get('name', 'Workflow')}")
                if entry.get("prompt"):
                    with st.expander("Original prompt"):
                        st.markdown(entry["prompt"])
                st.code(
                    json.dumps(entry["workflow"], indent=2),
                    language="json",
                )


def _render_credentials_hint() -> None:
    if get_gemini_api_key():
        return

    empty_state(
        "🔑",
        "Gemini API key required",
        "Add your **Google Gemini API Key** in the sidebar under **API Configuration**, then save.",
    )


def _can_generate() -> bool:
    return bool(get_gemini_api_key())


def render_generator_tab(show_api_error) -> None:
    """Automation Hub — Generate Workflow with Gemini."""
    section_header(
        "Workflow Generator",
        "Turn plain-English automation ideas into n8n workflows with Google Gemini.",
    )

    _init_generator_state()
    has_workflow = bool(st.session_state.get("generated_workflow"))
    render_generator_steps(has_workflow=has_workflow)

    prompt = _render_gemini_prompt_section()
    _render_optimization_options()

    if not _can_generate():
        _render_credentials_hint()
        _render_workflow_history()
        return

    _render_ready_made_templates(show_api_error)
    _apply_template_selection()

    generate_clicked = st.button(
        "Generate Workflow",
        type="primary",
        use_container_width=True,
        help=f"Calls {GEMINI_MODELS.get(get_gemini_model(), get_gemini_model())} with an n8n-optimized prompt.",
    )

    if generate_clicked:
        if not prompt.strip():
            st.warning("Describe your automation in the text area above before generating.")
        else:
            _run_generation(prompt, show_api_error)

    _render_workflow_output(show_api_error)
    _render_workflow_history()
