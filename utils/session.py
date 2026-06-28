"""Streamlit session state helpers."""

import streamlit as st


def init_session_state() -> None:
    """Initialize all session state keys with safe defaults."""
    defaults = {
        "gemini_api_key": "",
        "n8n_url": "http://localhost:5678",
        "n8n_api_key": "",
        "generated_workflow": None,
        "api_error": None,
        "delete_confirm_id": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def credentials_ready() -> bool:
    """Return True when all three API credentials are provided."""
    return bool(
        st.session_state.get("gemini_api_key")
        and st.session_state.get("n8n_url")
        and st.session_state.get("n8n_api_key")
    )


def n8n_credentials_ready() -> bool:
    """Return True when n8n URL and API key are provided."""
    return bool(st.session_state.get("n8n_url") and st.session_state.get("n8n_api_key"))


def get_n8n_base_url() -> str:
    """Normalize n8n instance URL to the /api/v1 base path."""
    url = st.session_state.get("n8n_url", "").strip().rstrip("/")
    if url.endswith("/api/v1"):
        return url
    return f"{url}/api/v1"


def get_n8n_api_key() -> str:
    return st.session_state.get("n8n_api_key", "")


def get_gemini_api_key() -> str:
    return st.session_state.get("gemini_api_key", "")
