"""Persist API credentials to gitignored `.streamlit/secrets.toml`."""

from __future__ import annotations

import base64
import json
import tomllib
from datetime import datetime, timedelta, timezone
from pathlib import Path

SECRETS_DIR_NAME = ".streamlit"
SECRETS_FILE_NAME = "secrets.toml"

SCALAR_KEYS = (
    "n8n_url",
    "n8n_api_key",
    "llm_provider",
    "gemini_model",
    "gemini_api_key",
    "openai_api_key",
    "groq_api_key",
)


class CredentialsStoreError(Exception):
    """Raised when credentials cannot be read or written."""


def get_secrets_path() -> Path:
    """Return path to Streamlit secrets file for this app install."""
    app_root = Path(__file__).resolve().parent.parent
    return app_root / SECRETS_DIR_NAME / SECRETS_FILE_NAME


def _toml_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def _jwt_times(api_key: str) -> tuple[str | None, str | None]:
    """Extract (created_iso, expires_iso) from a JWT without verifying signature."""
    try:
        parts = api_key.strip().split(".")
        if len(parts) != 3:
            return None, None
        payload = parts[1]
        payload += "=" * (-len(payload) % 4)
        data = json.loads(base64.urlsafe_b64decode(payload))
    except (ValueError, json.JSONDecodeError, IndexError):
        return None, None

    created = None
    expires = None
    if iat := data.get("iat"):
        created = datetime.fromtimestamp(int(iat), tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    if exp := data.get("exp"):
        expires = datetime.fromtimestamp(int(exp), tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return created, expires


def read_secrets(path: Path | None = None) -> dict:
    """Load secrets.toml as a plain dict (empty dict if missing)."""
    path = path or get_secrets_path()
    if not path.is_file():
        return {}
    try:
        with path.open("rb") as handle:
            return tomllib.load(handle)
    except tomllib.TOMLDecodeError as exc:
        raise CredentialsStoreError(f"Invalid secrets file: {path}") from exc


def _format_secrets_toml(data: dict) -> str:
    lines = [
        "# n8n Command Center credentials — DO NOT COMMIT (gitignored)",
        "# Saved from Automation Hub → API Configuration",
        "",
    ]

    for key in SCALAR_KEYS:
        value = data.get(key)
        if value:
            lines.append(f"{key} = {_toml_string(str(value))}")

    meta = data.get("credentials_meta")
    if isinstance(meta, dict) and meta:
        lines.extend(["", "[credentials_meta]"])
        for key, value in meta.items():
            if value is not None and str(value).strip():
                lines.append(f"{key} = {_toml_string(str(value))}")

    return "\n".join(lines).rstrip() + "\n"


def write_secrets(data: dict, path: Path | None = None) -> Path:
    """Atomically write secrets.toml."""
    path = path or get_secrets_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    content = _format_secrets_toml(data)
    tmp_path = path.with_suffix(".toml.tmp")

    try:
        tmp_path.write_text(content, encoding="utf-8")
        tmp_path.replace(path)
    except OSError as exc:
        raise CredentialsStoreError(f"Could not write secrets file: {path}") from exc
    finally:
        if tmp_path.exists() and not path.exists():
            tmp_path.unlink(missing_ok=True)

    return path


def _build_n8n_meta(api_key: str, existing_meta: dict | None = None) -> dict:
    meta = dict(existing_meta or {})
    now = datetime.now(timezone.utc)
    created, expires = _jwt_times(api_key)

    meta["n8n_api_key_created"] = created or now.strftime("%Y-%m-%dT%H:%M:%SZ")
    if expires:
        meta["n8n_api_key_expires"] = expires
    elif not meta.get("n8n_api_key_expires"):
        meta["n8n_api_key_expires"] = (now + timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%SZ")

    meta["n8n_api_key_note"] = "n8n JWT keys expire after 30 days — renew in n8n Settings → API"
    return meta


def save_n8n_credentials(n8n_url: str, n8n_api_key: str, path: Path | None = None) -> Path:
    """Merge and persist n8n URL + API key to secrets.toml."""
    url = n8n_url.strip().rstrip("/")
    api_key = n8n_api_key.strip()

    if not url:
        raise CredentialsStoreError("n8n Instance URL is required.")
    if not url.startswith(("http://", "https://")):
        raise CredentialsStoreError("n8n Instance URL must start with http:// or https://.")
    if not api_key:
        raise CredentialsStoreError("n8n API Key is required.")

    secrets_path = path or get_secrets_path()
    data = read_secrets(secrets_path)
    data["n8n_url"] = url
    data["n8n_api_key"] = api_key

    existing_meta = data.get("credentials_meta")
    if not isinstance(existing_meta, dict):
        existing_meta = {}
    data["credentials_meta"] = _build_n8n_meta(api_key, existing_meta)

    return write_secrets(data, secrets_path)


def save_all_credentials(
    *,
    n8n_url: str,
    n8n_api_key: str,
    llm_provider: str,
    gemini_model: str,
    gemini_api_key: str,
    openai_api_key: str,
    groq_api_key: str,
    path: Path | None = None,
) -> Path:
    """Persist n8n + LLM credentials using the same secrets.toml pattern."""
    secrets_path = path or get_secrets_path()
    data = read_secrets(secrets_path)

    url = n8n_url.strip().rstrip("/")
    api_key = n8n_api_key.strip()
    if not url or not api_key:
        raise CredentialsStoreError("n8n Instance URL and API Key are required to save.")

    data["n8n_url"] = url
    data["n8n_api_key"] = api_key
    data["llm_provider"] = llm_provider.strip()

    if gemini_model.strip():
        data["gemini_model"] = gemini_model.strip()
    if gemini_api_key.strip():
        data["gemini_api_key"] = gemini_api_key.strip()
    if openai_api_key.strip():
        data["openai_api_key"] = openai_api_key.strip()
    if groq_api_key.strip():
        data["groq_api_key"] = groq_api_key.strip()

    existing_meta = data.get("credentials_meta")
    if not isinstance(existing_meta, dict):
        existing_meta = {}
    data["credentials_meta"] = _build_n8n_meta(api_key, existing_meta)

    return write_secrets(data, secrets_path)
