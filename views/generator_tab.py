"""AI Workflow Generator tab — portfolio-grade UI and generation flow."""

from __future__ import annotations

import json

import streamlit as st

from config.workflow_templates import TEMPLATE_KEYS, WORKFLOW_TEMPLATES
from services.gemini_client import GeminiAPIError, generate_workflow
from services.n8n_client import N8nAPIError, N8nClient
from utils.session import credentials_ready, get_gemini_api_key, get_n8n_api_key, get_n8n_base_url
from utils.ui import empty_state, render_copy_json_button, render_flow_map, section_header
from utils.workflow_viz import build_linear_flow_text, build_mermaid_diagram, get_node_summary


def _init_generator_state() -> None:
    if "workflow_prompt" not in st.session_state:
        st.session_state.workflow_prompt = ""
    if "_last_applied_template" not in st.session_state:
        st.session_state._last_applied_template = "none"


def _apply_template_selection() -> None:
    template_key = st.selectbox(
        "Choose a Workflow Template",
        options=TEMPLATE_KEYS,
        format_func=lambda k: WORKFLOW_TEMPLATES[k]["label"],
    )

    if template_key != st.session_state._last_applied_template:
        st.session_state._last_applied_template = template_key
        if template_key != "none":
            st.session_state.workflow_prompt = WORKFLOW_TEMPLATES[template_key]["prompt"]


def _render_input_panel() -> tuple[str, bool, bool]:
    """Return (prompt, generate_clicked, push_clicked)."""
    _apply_template_selection()

    st.markdown("##### Describe Your Automation")
    prompt = st.text_area(
        "Workflow prompt",
        height=180,
        label_visibility="collapsed",
        placeholder=(
            "Describe the workflow you want in plain English — include triggers, APIs, "
            "conditions, and where alerts should be sent."
        ),
        key="workflow_prompt",
    )

    btn_generate, btn_push, _ = st.columns([1, 1, 2])
    with btn_generate:
        generate_clicked = st.button("✨ Generate Workflow", type="primary", use_container_width=True)
    with btn_push:
        push_clicked = st.button(
            "🚀 Push to n8n",
            use_container_width=True,
            disabled=st.session_state.get("generated_workflow") is None,
        )

    return prompt, generate_clicked, push_clicked


def _run_generation(prompt: str, show_api_error) -> None:
    with st.spinner("Gemini is designing your workflow…"):
        try:
            workflow = generate_workflow(get_gemini_api_key(), prompt)
            st.session_state.generated_workflow = workflow
            st.session_state.api_error = None
            st.success(
                f'✅ Workflow **"{workflow.get("name", "Untitled")}"** generated successfully.'
            )
        except (GeminiAPIError, ValueError) as exc:
            st.session_state.generated_workflow = None
            show_api_error(exc)


def _render_workflow_output() -> None:
    workflow = st.session_state.get("generated_workflow")
    if not workflow:
        return

    json_str = json.dumps(workflow, indent=2)
    mermaid = build_mermaid_diagram(workflow)

    st.markdown("---")
    st.markdown("##### Visual Workflow Map")
    render_flow_map(
        mermaid,
        build_linear_flow_text(workflow),
        get_node_summary(workflow),
    )

    st.markdown("##### Generated Workflow Preview")
    render_copy_json_button(json_str, button_key="copy_workflow_json")

    with st.container(border=True):
        st.code(json_str, language="json")


def _push_to_n8n(show_api_error) -> None:
    workflow = st.session_state.get("generated_workflow")
    if not workflow:
        return

    with st.spinner("Installing workflow on your n8n instance…"):
        try:
            client = N8nClient(get_n8n_base_url(), get_n8n_api_key())
            result = client.create_workflow(workflow)
            st.success(f"🎉 Workflow installed — ID: `{result.get('id', 'unknown')}`")
        except N8nAPIError as exc:
            show_api_error(exc)


def render_generator_tab(show_api_error) -> None:
    """Main entry for the AI Generator tab."""
    section_header(
        "AI Workflow Generator",
        "Choose a blueprint or write a custom prompt — Gemini produces deployable n8n JSON.",
    )

    if not credentials_ready():
        empty_state(
            "🔑",
            "API keys required",
            "Enter your Gemini and n8n credentials in the sidebar to start generating workflows.",
        )
        return

    _init_generator_state()

    left, right = st.columns([1, 1], gap="large")
    with left:
        st.markdown(
            '<div class="section-card"><h3>① Blueprint</h3>'
            "<p>Start from a professional SOC or email triage template.</p></div>",
            unsafe_allow_html=True,
        )
    with right:
        st.markdown(
            '<div class="section-card"><h3>② Generate & Deploy</h3>'
            "<p>Preview the pipeline visually, copy JSON, then push to n8n.</p></div>",
            unsafe_allow_html=True,
        )

    prompt, generate_clicked, push_clicked = _render_input_panel()

    if generate_clicked:
        _run_generation(prompt, show_api_error)

    _render_workflow_output()

    if push_clicked:
        _push_to_n8n(show_api_error)
