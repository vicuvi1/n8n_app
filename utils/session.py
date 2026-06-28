"""Streamlit session state helpers."""

from datetime import datetime, timezone

import streamlit as st

from config.constants import DEFAULT_GEMINI_MODEL, GEMINI_MODEL_KEYS, LLM_PROVIDERS

# Maps sidebar label -> session-state key for the provider API key.
PROVIDER_KEY_FIELDS = {
    "Google Gemini": "gemini_api_key",
    "OpenAI": "openai_api_key",
    "Groq": "groq_api_key",
}


def _load_secrets_into_session() -> None:
    """Pre-fill session state from .streamlit/secrets.toml when available."""
    try:
        secrets = st.secrets
    except Exception:
        return

    if secrets.get("n8n_url") and not st.session_state.get("n8n_url"):
        st.session_state.n8n_url = secrets["n8n_url"]
    elif secrets.get("n8n_url"):
        if st.session_state.n8n_url == "http://localhost:5678":
            st.session_state.n8n_url = secrets["n8n_url"]

    if secrets.get("n8n_api_key") and not st.session_state.get("n8n_api_key"):
        st.session_state.n8n_api_key = secrets["n8n_api_key"]

    if secrets.get("gemini_api_key") and not st.session_state.get("gemini_api_key"):
        st.session_state.gemini_api_key = secrets["gemini_api_key"]

    if secrets.get("openai_api_key") and not st.session_state.get("openai_api_key"):
        st.session_state.openai_api_key = secrets["openai_api_key"]

    if secrets.get("groq_api_key") and not st.session_state.get("groq_api_key"):
        st.session_state.groq_api_key = secrets["groq_api_key"]

    if secrets.get("gemini_model") and st.session_state.get("gemini_model") == DEFAULT_GEMINI_MODEL:
        st.session_state.gemini_model = secrets["gemini_model"]

    if secrets.get("llm_provider") and st.session_state.get("llm_provider") == LLM_PROVIDERS[0]:
        st.session_state.llm_provider = secrets["llm_provider"]

    meta = secrets.get("credentials_meta", {})
    if meta:
        st.session_state.credentials_meta = dict(meta)


def get_credentials_meta() -> dict:
    return st.session_state.get("credentials_meta", {})


def apply_saved_credentials_meta(meta: dict) -> None:
    """Update session metadata after persisting secrets.toml."""
    if meta:
        st.session_state.credentials_meta = dict(meta)


def get_n8n_key_expiry_info() -> tuple[str | None, int | None]:
    """Return (expiry_iso, days_remaining) for the saved n8n API key."""
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
        "llm_provider": LLM_PROVIDERS[0],
        "gemini_model": DEFAULT_GEMINI_MODEL,
        "gemini_api_key": "",
        "openai_api_key": "",
        "groq_api_key": "",
        "n8n_url": "http://localhost:5678",
        "n8n_api_key": "",
        "generated_workflow": None,
        "api_error": None,
        "delete_confirm_id": None,
        "credentials_meta": {},
        "active_hub_page": "hub",
        "docker_log": [],
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    _load_secrets_into_session()


def get_gemini_model() -> str:
    model = st.session_state.get("gemini_model", DEFAULT_GEMINI_MODEL)
    return model if model in GEMINI_MODEL_KEYS else DEFAULT_GEMINI_MODEL


def get_llm_provider() -> str:
    return st.session_state.get("llm_provider", LLM_PROVIDERS[0])


def get_llm_api_key(provider: str | None = None) -> str:
    """Return the API key for the active (or specified) LLM provider."""
    provider = provider or get_llm_provider()
    field = PROVIDER_KEY_FIELDS.get(provider, "gemini_api_key")
    return st.session_state.get(field, "")


def llm_credentials_ready() -> bool:
    """Return True when the selected LLM provider has an API key."""
    return bool(get_llm_api_key())


def credentials_ready() -> bool:
    """Return True when n8n + active LLM provider credentials are set."""
    return n8n_credentials_ready() and llm_credentials_ready()


def n8n_credentials_ready() -> bool:
    """Return True when n8n URL and API key are provided."""
    return bool(st.session_state.get("n8n_url") and st.session_state.get("n8n_api_key"))


def get_n8n_base_url() -> str:
    """Normalize n8n instance URL to the /api/v1 base path."""
    url = get_n8n_instance_url()
    if url.endswith("/api/v1"):
        return url
    return f"{url}/api/v1"


def get_n8n_instance_url() -> str:
    """Return the n8n instance root URL (no /api/v1 suffix)."""
    return st.session_state.get("n8n_url", "").strip().rstrip("/")


def get_n8n_api_key() -> str:
    return st.session_state.get("n8n_api_key", "")


def get_gemini_api_key() -> str:
    return st.session_state.get("gemini_api_key", "")
