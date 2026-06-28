"""Backward-compatible shim — use services.llm_client instead."""

from services.llm_client import LLMError as GeminiAPIError
from services.llm_client import generate_workflow, generate_workflow_with_gemini

__all__ = ["GeminiAPIError", "generate_workflow", "generate_workflow_with_gemini"]
