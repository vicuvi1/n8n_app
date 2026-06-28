"""Sidebar — Automation Hub navigation and API settings."""

import streamlit as st

from config.constants import GEMINI_MODELS, LLM_PROVIDERS
from config.navigation import DEFAULT_HUB_PAGE, HUB_PAGE_ORDER, HUB_PAGES
from views.generator_fab import GENERATOR_PAGE_ID, GENERATOR_SHORTCUT_HINT
from utils.session import (
    apply_saved_credentials_meta,
    credentials_ready,
    get_n8n_key_expiry_info,
    n8n_credentials_ready,
)
from utils.credentials_store import (
    CredentialsStoreError,
    read_secrets,
    save_all_credentials,
    save_n8n_credentials,
)
from utils.user_feedback import show_user_error
from utils.ui import render_sidebar_brand


def _set_active_page(page_id: str) -> None:
    st.session_state.active_hub_page = page_id


def render_automation_hub_nav() -> None:
    """Primary sidebar navigation for the Automation Hub."""
    if "active_hub_page" not in st.session_state:
        st.session_state.active_hub_page = DEFAULT_HUB_PAGE

    st.sidebar.markdown(
        """
        <div class="hub-sidebar-title">
          <span class="hub-sidebar-badge">HUB</span>
          Automation Hub
        </div>
        <p class="hub-sidebar-sub">Navigate workflows, AI tools & monitoring</p>
        """,
        unsafe_allow_html=True,
    )

    for page_id in HUB_PAGE_ORDER:
        page = HUB_PAGES[page_id]
        is_active = st.session_state.active_hub_page == page_id
        label = f"{page['icon']}  {page['label']}"

        nav_help = (
            f"Shortcut: {GENERATOR_SHORTCUT_HINT}"
            if page_id == GENERATOR_PAGE_ID
            else page["description"]
        )
        if st.sidebar.button(
            label,
            key=f"hub_nav_{page_id}",
            use_container_width=True,
            type="primary" if is_active else "secondary",
            help=nav_help,
        ):
            _set_active_page(page_id)
            st.rerun()

    st.sidebar.markdown(
        f"""
        <div class="hub-nav-hint">
          <strong>{HUB_PAGES[st.session_state.active_hub_page]["label"]}</strong><br/>
          <span>{HUB_PAGES[st.session_state.active_hub_page]["description"]}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_api_configuration() -> str:
    """API keys section inside a sidebar expander. Returns active LLM provider."""
    provider = st.session_state.get("llm_provider", LLM_PROVIDERS[0])

    with st.sidebar.expander("⚙️ API Configuration", expanded=not credentials_ready()):
        st.caption("Keys load from `.streamlit/secrets.toml` when present. Use **Save** to persist.")

        st.session_state.llm_provider = st.selectbox(
            "Select LLM Provider",
            options=LLM_PROVIDERS,
            index=LLM_PROVIDERS.index(st.session_state.get("llm_provider", LLM_PROVIDERS[0]))
            if st.session_state.get("llm_provider") in LLM_PROVIDERS
            else 0,
        )
        provider = st.session_state.llm_provider

        if provider == "Google Gemini":
            st.markdown(
                '<p class="hub-panel-title" style="margin-bottom:0.5rem;">Gemini model</p>',
                unsafe_allow_html=True,
            )
            model_keys = list(GEMINI_MODELS.keys())
            current = st.session_state.get("gemini_model", model_keys[0])
            if current not in model_keys:
                current = model_keys[0]
            st.session_state.gemini_model = st.selectbox(
                "Select Gemini Model",
                options=model_keys,
                index=model_keys.index(current),
                format_func=lambda m: GEMINI_MODELS[m],
            )
            st.session_state.gemini_api_key = st.text_input(
                "Google Gemini API Key",
                value=st.session_state.gemini_api_key,
                type="password",
                placeholder="AIza…",
            )
        elif provider == "OpenAI":
            st.session_state.openai_api_key = st.text_input(
                "OpenAI API Key",
                value=st.session_state.openai_api_key,
                type="password",
                placeholder="sk-…",
            )
        elif provider == "Groq":
            st.session_state.groq_api_key = st.text_input(
                "Groq API Key",
                value=st.session_state.groq_api_key,
                type="password",
                placeholder="gsk_…",
            )

        st.markdown("##### n8n connection")
        st.session_state.n8n_url = st.text_input(
            "n8n Instance URL",
            value=st.session_state.n8n_url,
            placeholder="http://localhost:5678",
            help="Base URL of your n8n instance (no /api/v1 suffix).",
        )
        st.session_state.n8n_api_key = st.text_input(
            "n8n API Key",
            value=st.session_state.n8n_api_key,
            type="password",
            placeholder="JWT from n8n → Settings → API",
            help="Stored locally in gitignored `.streamlit/secrets.toml`.",
        )

        save_n8n_col, save_all_col = st.columns(2)
        with save_n8n_col:
            if st.button("💾 Save n8n", use_container_width=True, key="save_n8n_credentials", type="secondary"):
                try:
                    path = save_n8n_credentials(
                        st.session_state.n8n_url,
                        st.session_state.n8n_api_key,
                    )
                    meta = read_secrets(path).get("credentials_meta", {})
                    apply_saved_credentials_meta(meta)
                    st.success(f"n8n credentials saved to `{path.name}`")
                except CredentialsStoreError as exc:
                    show_user_error(exc)
        with save_all_col:
            if st.button("💾 Save all keys", use_container_width=True, key="save_all_credentials", type="primary"):
                try:
                    path = save_all_credentials(
                        n8n_url=st.session_state.n8n_url,
                        n8n_api_key=st.session_state.n8n_api_key,
                        llm_provider=st.session_state.llm_provider,
                        gemini_model=st.session_state.get("gemini_model", ""),
                        gemini_api_key=st.session_state.gemini_api_key,
                        openai_api_key=st.session_state.openai_api_key,
                        groq_api_key=st.session_state.groq_api_key,
                    )
                    meta = read_secrets(path).get("credentials_meta", {})
                    apply_saved_credentials_meta(meta)
                    st.success(f"All keys saved to `{path.parent.name}/{path.name}`")
                except CredentialsStoreError as exc:
                    show_user_error(exc)

    return provider


def render_connection_status(provider: str) -> None:
    """Status footer at bottom of sidebar."""
    st.sidebar.markdown("---")
    st.sidebar.markdown(
        '<p class="hub-panel-title" style="margin-bottom:0.5rem;">Connection status</p>',
        unsafe_allow_html=True,
    )

    expires_at, days_left = get_n8n_key_expiry_info()
    if expires_at and days_left is not None:
        if days_left < 0:
            st.sidebar.error(f"n8n key **expired** {expires_at[:10]}")
        elif days_left <= 7:
            st.sidebar.warning(f"n8n key expires **{expires_at[:10]}** ({days_left}d)")
        else:
            st.sidebar.info(f"n8n key valid until **{expires_at[:10]}**")

    if credentials_ready():
        st.sidebar.markdown(
            f'<div class="status-pill ok"><span class="status-dot"></span>All systems ready</div>',
            unsafe_allow_html=True,
        )
    elif n8n_credentials_ready():
        st.sidebar.markdown(
            f'<div class="status-pill warn"><span class="status-dot"></span>{provider} key required</div>',
            unsafe_allow_html=True,
        )
    else:
        st.sidebar.markdown(
            '<div class="status-pill err"><span class="status-dot"></span>Credentials needed</div>',
            unsafe_allow_html=True,
        )


def render_sidebar() -> None:
    """Full sidebar: brand, hub nav, API config, status."""
    render_sidebar_brand()
    st.sidebar.markdown("---")
    render_automation_hub_nav()
    st.sidebar.markdown("---")
    provider = render_api_configuration()
    render_connection_status(provider)
