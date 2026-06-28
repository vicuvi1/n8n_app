"""Google Gemini client for n8n workflow generation."""

from typing import Any

from google import genai
from google.genai import types

from config.constants import GEMINI_MODEL
from prompts.n8n_system_prompt import SYSTEM_PROMPT
from utils.json_utils import parse_workflow_json


class GeminiAPIError(Exception):
    """Raised when Gemini API call fails."""


def generate_workflow(api_key: str, user_prompt: str) -> dict[str, Any]:
    """
    Call Gemini to generate an n8n workflow JSON from a plain-English prompt.

    Returns a validated workflow dict ready for preview or push to n8n.
    """
    if not user_prompt.strip():
        raise ValueError("Please enter a workflow description before generating.")

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=user_prompt.strip(),
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.2,
                response_mime_type="application/json",
                thinking_config=types.ThinkingConfig(thinking_budget=0),
            ),
        )
    except Exception as exc:
        error_msg = str(exc).lower()
        if "api key" in error_msg or "401" in error_msg or "403" in error_msg:
            raise GeminiAPIError("Gemini API key rejected. Check your key and try again.") from exc
        raise GeminiAPIError(f"Gemini API error: {exc}") from exc

    raw_text = response.text
    if not raw_text:
        raise GeminiAPIError("Gemini returned an empty response. Try rephrasing your prompt.")

    try:
        return parse_workflow_json(raw_text)
    except ValueError as exc:
        raise GeminiAPIError(
            f"{exc}\n\nRaw model output:\n{raw_text[:500]}"
        ) from exc
