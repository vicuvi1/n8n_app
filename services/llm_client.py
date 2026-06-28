"""Multi-provider LLM client for n8n workflow generation."""

from __future__ import annotations

from typing import Any

from config.constants import (
    DEFAULT_GEMINI_MODEL,
    DEFAULT_WORKFLOW_OPTIMIZATION,
    GEMINI_MODELS,
    GROQ_MODEL,
    LLM_PROVIDERS,
    OPENAI_MODEL,
    WORKFLOW_OPTIMIZATION_RELIABILITY,
)
from prompts.n8n_system_prompt import SYSTEM_PROMPT, build_gemini_user_prompt
from utils.json_utils import normalize_workflow, parse_workflow_json


class LLMError(Exception):
    """Raised when an LLM API call fails."""


class MissingDependencyError(LLMError):
    """Raised when a provider SDK is not installed."""


def _validate_prompt(user_prompt: str) -> str:
    text = user_prompt.strip()
    if not text:
        raise ValueError("Please enter a workflow description before generating.")
    return text


def _parse_response(raw_text: str, provider: str) -> dict[str, Any]:
    if not raw_text:
        raise LLMError(f"{provider} returned an empty response. Try rephrasing your prompt.")
    try:
        return normalize_workflow(parse_workflow_json(raw_text))
    except ValueError as exc:
        raise LLMError(f"{exc}\n\nRaw model output:\n{raw_text[:500]}") from exc


def _auth_error(provider: str, exc: Exception) -> LLMError:
    raise LLMError(f"{provider} API key rejected. Check your key and try again.") from exc


def _generate_gemini(
    api_key: str,
    user_prompt: str,
    model: str = DEFAULT_GEMINI_MODEL,
    optimization_mode: str = DEFAULT_WORKFLOW_OPTIMIZATION,
) -> dict[str, Any]:
    try:
        from google import genai
        from google.genai import types
    except ImportError as exc:
        raise MissingDependencyError(
            "Google GenAI library not installed. Run: pip install google-genai"
        ) from exc

    try:
        client = genai.Client(api_key=api_key)
        temperature = 0.15 if optimization_mode == WORKFLOW_OPTIMIZATION_RELIABILITY else 0.1
        response = client.models.generate_content(
            model=model,
            contents=build_gemini_user_prompt(user_prompt, optimization_mode),
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=temperature,
                response_mime_type="application/json",
                thinking_config=types.ThinkingConfig(thinking_budget=0),
            ),
        )
        raw_text = response.text
    except Exception as exc:
        error_msg = str(exc).lower()
        if any(x in error_msg for x in ("api key", "401", "403", "invalid")):
            raise _auth_error("Google Gemini", exc)
        if "404" in error_msg or "not found" in error_msg:
            others = [m for m in GEMINI_MODELS if m != model]
            raise LLMError(
                f"Model `{model}` is not available on your API key. "
                f"Try another from the sidebar — e.g. `{others[0] if others else DEFAULT_GEMINI_MODEL}`."
            ) from exc
        if "503" in error_msg or "capacity" in error_msg or "overloaded" in error_msg:
            raise LLMError(
                "Google Gemini is at capacity (503). Try Gemini 2.5 Flash Lite, OpenAI, or Groq."
            ) from exc
        raise LLMError(f"Google Gemini error ({model}): {exc}") from exc

    return _parse_response(raw_text, f"Google Gemini ({model})")


def _generate_openai(api_key: str, user_prompt: str) -> dict[str, Any]:
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise MissingDependencyError(
            "OpenAI library not installed. Run: pip install openai"
        ) from exc

    try:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.2,
        )
        raw_text = response.choices[0].message.content or ""
    except Exception as exc:
        error_msg = str(exc).lower()
        if any(x in error_msg for x in ("api key", "401", "403", "invalid", "authentication")):
            raise _auth_error("OpenAI", exc)
        raise LLMError(f"OpenAI error: {exc}") from exc

    return _parse_response(raw_text, "OpenAI")


def _generate_groq(api_key: str, user_prompt: str) -> dict[str, Any]:
    try:
        from groq import Groq
    except ImportError as exc:
        raise MissingDependencyError(
            "Groq library not installed. Run: pip install groq"
        ) from exc

    try:
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.2,
        )
        raw_text = response.choices[0].message.content or ""
    except Exception as exc:
        error_msg = str(exc).lower()
        if any(x in error_msg for x in ("api key", "401", "403", "invalid", "authentication")):
            raise _auth_error("Groq", exc)
        raise LLMError(f"Groq error: {exc}") from exc

    return _parse_response(raw_text, "Groq")


def generate_workflow(
    provider: str,
    api_key: str,
    user_prompt: str,
    *,
    gemini_model: str = DEFAULT_GEMINI_MODEL,
) -> dict[str, Any]:
    """
    Generate an n8n workflow JSON using the selected LLM provider.

    Args:
        provider: One of LLM_PROVIDERS (e.g. "Google Gemini", "OpenAI", "Groq").
        api_key: API key for the selected provider.
        user_prompt: Plain-English workflow description.
        gemini_model: Gemini model id when provider is Google Gemini.

    Returns:
        Validated workflow dict ready for preview or push to n8n.
    """
    prompt = _validate_prompt(user_prompt)

    if not api_key:
        raise ValueError(f"Please enter your {provider} API key in the sidebar.")

    if provider == "Google Gemini":
        return _generate_gemini(api_key, prompt, gemini_model)
    if provider == "OpenAI":
        return _generate_openai(api_key, prompt)
    if provider == "Groq":
        return _generate_groq(api_key, prompt)

    raise ValueError(f"Unknown provider: {provider}. Choose from: {', '.join(LLM_PROVIDERS)}")


def generate_workflow_with_gemini(
    api_key: str,
    user_prompt: str,
    model: str | None = None,
    optimization_mode: str = DEFAULT_WORKFLOW_OPTIMIZATION,
) -> dict[str, Any]:
    """
    Generate n8n workflow JSON using the selected Gemini model.

    Uses an optimized system + user prompt for clean, importable n8n JSON.
    """
    if not api_key:
        raise ValueError("Please enter your Google Gemini API key in the sidebar.")

    return _generate_gemini(
        api_key,
        _validate_prompt(user_prompt),
        model or DEFAULT_GEMINI_MODEL,
        optimization_mode=optimization_mode,
    )
