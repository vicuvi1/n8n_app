"""Friendly error messages and user feedback for n8n / Docker / JSON actions."""

from __future__ import annotations

import html
import json
from dataclasses import dataclass

import streamlit as st

from config.constants import DEBUG
from services.docker_service import DockerError
from services.n8n_client import N8nAPIError
from utils.credentials_store import CredentialsStoreError


@dataclass
class UserFeedback:
    """Structured message for display in the UI."""

    title: str
    message: str
    hint: str | None = None
    level: str = "error"  # error | warning | info | success

    def as_markdown(self) -> str:
        text = f"**{self.title}** — {self.message}"
        if self.hint:
            text += f"\n\n💡 {self.hint}"
        return text

    def as_plain(self) -> str:
        parts = [f"{self.title} — {self.message}"]
        if self.hint:
            parts.append(self.hint)
        return " ".join(parts)


def explain_n8n_api_error(exc: N8nAPIError, context: str = "") -> UserFeedback:
    """Map n8n REST / connectivity errors to friendly guidance."""
    raw = str(exc).strip()
    code = exc.status_code
    ctx = f" while {context}" if context else ""

    if code in (401, 403):
        return UserFeedback(
            title="Wrong n8n API key",
            message=f"n8n rejected your API key{ctx}.",
            hint=(
                "In n8n open **Settings → API**, create a new key with workflow permissions, "
                "then update **sidebar → API Configuration → Save n8n**."
            ),
        )

    if code == 404 or "api not found" in raw.lower():
        return UserFeedback(
            title="n8n API not found",
            message="The API URL doesn't look right — n8n may be running but the path is wrong.",
            hint="Set Instance URL to your n8n root only, e.g. `http://localhost:5678` (no `/api/v1` suffix).",
        )

    if code == 400 or "rejected the workflow" in raw.lower():
        return UserFeedback(
            title="n8n rejected the workflow",
            message=f"The workflow JSON isn't valid for import{ctx}.",
            hint="Check node types, connections, and required fields in the editor — then try Push to n8n again.",
        )

    if code == 409:
        return UserFeedback(
            title="Workflow name conflict",
            message="n8n couldn't create the workflow because of a naming conflict.",
            hint="Rename the workflow in the JSON editor and push again.",
        )

    if code is not None and code >= 500:
        return UserFeedback(
            title="n8n server error",
            message=f"n8n returned an error{ctx}.",
            hint="Check n8n logs in Docker Control or restart the container, then retry.",
        )

    lower = raw.lower()
    if "cannot reach" in lower or "is the server running" in lower:
        return UserFeedback(
            title="n8n isn't reachable",
            message=f"We couldn't connect to your n8n instance{ctx}.",
            hint="Start n8n from **Docker Control**, or confirm the Instance URL in the sidebar.",
        )

    if "did not respond in time" in lower or "timeout" in lower:
        return UserFeedback(
            title="n8n timed out",
            message=f"n8n took too long to respond{ctx}.",
            hint="The server may be overloaded or still starting — wait a moment and try again.",
        )

    if "network error" in lower:
        return UserFeedback(
            title="Network problem",
            message=f"A network error occurred talking to n8n{ctx}.",
            hint="Check your connection, firewall, and that n8n is running on the configured URL.",
        )

    return UserFeedback(
        title="n8n error",
        message=raw or f"Something went wrong with n8n{ctx}.",
        hint="Verify n8n is running and your API key is saved in the sidebar.",
    )


def explain_n8n_failure(message: str | None, status_code: int | None = None) -> UserFeedback:
    """Build feedback from a stored error string (e.g. push result)."""
    exc = N8nAPIError(message or "n8n request failed.", status_code=status_code)
    return explain_n8n_api_error(exc)


def explain_docker_error(exc: DockerError) -> UserFeedback:
    raw = str(exc).strip()
    lower = raw.lower()

    if "not installed" in lower or "not on path" in lower:
        return UserFeedback(
            title="Docker not installed",
            message="Docker isn't available on this machine.",
            hint="Install [Docker Desktop](https://www.docker.com/products/docker-desktop/), then reopen this app.",
        )

    if "container" in lower and "not found" in lower:
        return UserFeedback(
            title="n8n container missing",
            message="The Docker container `n8n` doesn't exist yet.",
            hint="Create it with: `docker run -d --name n8n -p 5678:5678 n8nio/n8n`",
        )

    if "timed out" in lower:
        return UserFeedback(
            title="Docker command timed out",
            message="Docker didn't finish in time.",
            hint="Make sure Docker Desktop is running, then try again.",
        )

    return UserFeedback(
        title="Docker error",
        message=raw or "A Docker command failed.",
        hint="Open Docker Desktop, confirm the daemon is running, and retry from Docker Control.",
    )


def explain_json_error(exc: ValueError | json.JSONDecodeError) -> UserFeedback:
    text = str(exc).strip()
    lower = text.lower()

    if isinstance(exc, json.JSONDecodeError) or "invalid json" in lower:
        return UserFeedback(
            title="Invalid JSON",
            message="The workflow editor contains JSON that couldn't be parsed.",
            hint="Look for missing commas, quotes, or brackets. Use **Format JSON** after fixing syntax.",
        )

    if "missing required fields" in lower:
        return UserFeedback(
            title="Incomplete workflow JSON",
            message=text,
            hint='A valid n8n workflow needs `"name"`, `"nodes"`, and `"connections"` at the top level.',
        )

    if "must contain at least one node" in lower:
        return UserFeedback(
            title="No workflow nodes",
            message="n8n workflows need at least one node.",
            hint="Add a trigger node (webhook, schedule, etc.) or regenerate the workflow.",
        )

    if "connection" in lower and "not a node name" in lower:
        return UserFeedback(
            title="Broken workflow connections",
            message=text,
            hint='Every name in `"connections"` must exactly match a node `"name"` in the nodes array.',
        )

    if "must be a single object" in lower:
        return UserFeedback(
            title="Invalid workflow shape",
            message="Workflow JSON must be one object `{ ... }`, not a list.",
            hint="Wrap your content in a single JSON object with name, nodes, and connections.",
        )

    return UserFeedback(
        title="Workflow JSON problem",
        message=text or "The workflow JSON isn't valid.",
        hint="Fix the editor content or regenerate the workflow with Gemini.",
    )


def explain_credentials_error(exc: CredentialsStoreError) -> UserFeedback:
    return UserFeedback(
        title="Couldn't save credentials",
        message=str(exc),
        hint="Check that `.streamlit/secrets.toml` isn't open in another program and try again.",
    )


def explain_exception(exc: Exception, context: str = "") -> UserFeedback:
    """Pick the best friendly explanation for a raised exception."""
    if isinstance(exc, N8nAPIError):
        return explain_n8n_api_error(exc, context)
    if isinstance(exc, DockerError):
        return explain_docker_error(exc)
    if isinstance(exc, (ValueError, json.JSONDecodeError)):
        return explain_json_error(exc)
    if isinstance(exc, CredentialsStoreError):
        return explain_credentials_error(exc)

    return UserFeedback(
        title="Something went wrong",
        message=str(exc) or "An unexpected error occurred.",
        hint="Try again. If the problem persists, check n8n and your sidebar credentials.",
    )


def show_user_feedback(feedback: UserFeedback) -> None:
    """Render structured feedback in Streamlit."""
    text = feedback.as_markdown()
    if feedback.level == "success":
        st.success(text)
    elif feedback.level == "warning":
        st.warning(text)
    elif feedback.level == "info":
        st.info(text)
    else:
        st.error(text)

    if DEBUG and feedback.level == "error":
        st.caption("Debug mode is on — see traceback above if an exception was passed to show_user_error.")


def show_user_error(exc: Exception, context: str = "") -> None:
    """Show a friendly error for any supported exception."""
    if DEBUG:
        st.exception(exc)
    show_user_feedback(explain_exception(exc, context))


def feedback_for_session_message(message: str, level: str = "error") -> UserFeedback:
    """Convert common inline session-state messages to UserFeedback."""
    lower = message.lower()
    if "api key" in lower and "sidebar" in lower:
        return UserFeedback(
            title="n8n credentials needed",
            message=message,
            hint="Open **sidebar → API Configuration**, enter URL + key, then **Save n8n**.",
            level=level,
        )
    if "json" in lower and "editor" in lower:
        return UserFeedback(
            title="Fix workflow JSON first",
            message=message,
            hint="Correct syntax in the editor until you see the green valid JSON badge.",
            level=level,
        )
    return UserFeedback(title="Notice", message=message, level=level)


def render_feedback_banner(feedback: UserFeedback, css_class: str = "user-feedback-banner") -> None:
    """HTML banner for push/docker panels."""
    level_class = feedback.level if feedback.level in ("success", "error", "warning", "info") else "error"
    hint_html = (
        f'<div class="user-feedback-hint">💡 {html.escape(feedback.hint)}</div>'
        if feedback.hint
        else ""
    )
    st.markdown(
        f"""
        <div class="{css_class} {level_class}">
          <strong>{html.escape(feedback.title)}</strong><br/>
          <span>{html.escape(feedback.message)}</span>
          {hint_html}
        </div>
        """,
        unsafe_allow_html=True,
    )
