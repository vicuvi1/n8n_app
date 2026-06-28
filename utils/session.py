"""Streamlit session state helpers."""

from datetime import datetime, timezone

import streamlit as st


def _load_secrets_into_session() -> None:
    """Pre-fill session state from .streamlit/secrets.toml when available."""
    try:
        secrets = st.secrets
    except Exception:
        return

    if secrets.get("n8n_url") and not st.session_state.get("n8n_url"):
        st.session_state.n8n_url = secrets["n8n_url"]
    elif secrets.get("n8n_url"):
        # Always sync URL from secrets if user hasn't typed in sidebar this session
        if st.session_state.n8n_url == "http://localhost:5678":
            st.session_state.n8n_url = secrets["n8n_url"]

    if secrets.get("n8n_api_key") and not st.session_state.get("n8n_api_key"):
        st.session_state.n8n_api_key = secrets["n8n_api_key"]

    if secrets.get("gemini_api_key") and not st.session_state.get("gemini_api_key"):
        st.session_state.gemini_api_key = secrets["gemini_api_key"]

    meta = secrets.get("credentials_meta", {})
    if meta:
        st.session_state.credentials_meta = dict(meta)


def get_credentials_meta() -> dict:
    return st.session_state.get("credentials_meta", {})


def get_n8n_key_expiry_info() -> tuple[str | None, int | None]:
    """
    Return (expiry_iso, days_remaining) for the saved n8n API key.
    days_remaining is negative if already expired.
    """
    meta = get_credentials_meta()
    expires_raw = meta.get("n8n_api_key_expires")
    if not expires_raw:
        return None, None

    try:
        expires_at = datetime.fromisoformat(str(expires_raw).replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        days_left = (expires_at - now).days
        return expires_raw, days_left
    except ValueError:
        return expires_raw, None


def init_session_state() -> None:
    """Initialize all session state keys with safe defaults."""
    defaults = {
        "gemini_api_key": "",
        "n8n_url": "http://localhost:5678",
        "n8n_api_key": "",
        "generated_workflow": None,
        "api_error": None,
        "delete_confirm_id": None,
        "credentials_meta": {},
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    _load_secrets_into_session()


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
