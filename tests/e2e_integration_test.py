"""
End-to-end integration test for the Automation Hub flow:

  Select model → Save Gemini key → Start n8n → Generate workflow → Edit JSON → Push to n8n

Run from project root:
  python tests/e2e_integration_test.py

Uses real credentials from .streamlit/secrets.toml when present.
Never prints API keys.
"""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config.constants import DEFAULT_GEMINI_MODEL, GEMINI_MODEL_KEYS, GEMINI_MODELS
from services.docker_service import get_n8n_status, start_n8n
from services.llm_client import generate_workflow_with_gemini
from services.n8n_client import N8nClient, build_blank_workflow
from utils.credentials_store import read_secrets, save_all_credentials
from utils.json_utils import parse_workflow_json, prepare_workflow_for_push


class StepResult:
    def __init__(self, name: str, passed: bool, detail: str = ""):
        self.name = name
        self.passed = passed
        self.detail = detail


def _mask(value: str) -> str:
    value = (value or "").strip()
    if not value:
        return "(empty)"
    if len(value) <= 8:
        return "****"
    return f"{value[:4]}…{value[-4:]}"


def step_select_model_and_save_gemini_key(secrets: dict) -> StepResult:
    """Verify model list and credentials save round-trip."""
    model = secrets.get("gemini_model") or DEFAULT_GEMINI_MODEL
    if model not in GEMINI_MODEL_KEYS:
        return StepResult(
            "1. Select model & save Gemini key",
            False,
            f"Saved model {model!r} is not in GEMINI_MODELS.",
        )

    gemini_key = (secrets.get("gemini_api_key") or "").strip()
    n8n_url = (secrets.get("n8n_url") or "http://localhost:5678").strip()
    n8n_key = (secrets.get("n8n_api_key") or "").strip()

    if not gemini_key:
        # Still verify save round-trip with a placeholder in an isolated temp file.
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "secrets.toml"
            save_all_credentials(
                n8n_url=n8n_url,
                n8n_api_key=n8n_key or "test-n8n-key-placeholder",
                llm_provider="Google Gemini",
                gemini_model=model,
                gemini_api_key="test-gemini-key-placeholder",
                openai_api_key="",
                groq_api_key="",
                path=path,
            )
            saved = read_secrets(path)
        if saved.get("gemini_model") != model:
            return StepResult("1. Select model & save Gemini key", False, "Model not persisted correctly.")
        return StepResult(
            "1. Select model & save Gemini key",
            False,
            f"Save mechanism OK for {GEMINI_MODELS.get(model, model)}, "
            "but no gemini_api_key in secrets.toml (save it in sidebar -> API Configuration).",
        )

    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "secrets.toml"
        save_all_credentials(
            n8n_url=n8n_url,
            n8n_api_key=n8n_key or "test-n8n-key-placeholder",
            llm_provider=secrets.get("llm_provider") or "Google Gemini",
            gemini_model=model,
            gemini_api_key=gemini_key,
            openai_api_key=secrets.get("openai_api_key") or "",
            groq_api_key=secrets.get("groq_api_key") or "",
            path=path,
        )
        saved = read_secrets(path)

    if saved.get("gemini_model") != model:
        return StepResult("1. Select model & save Gemini key", False, "Model not persisted correctly.")

    label = GEMINI_MODELS.get(model, model)
    return StepResult(
        "1. Select model & save Gemini key",
        True,
        f"Model: {label} · Gemini key: {_mask(gemini_key)}",
    )


def step_start_n8n() -> StepResult:
    """Ensure n8n is reachable (start Docker container if stopped)."""
    status = get_n8n_status()
    if status.state == "running" and status.port_open:
        return StepResult("2. Start n8n (Docker)", True, status.message)

    if status.state == "stopped":
        try:
            result = start_n8n()
            status = get_n8n_status()
            if status.state == "running" and status.port_open:
                return StepResult("2. Start n8n (Docker)", True, result.message)
            return StepResult(
                "2. Start n8n (Docker)",
                False,
                f"Start issued but status is {status.state}: {status.message}",
            )
        except Exception as exc:
            return StepResult("2. Start n8n (Docker)", False, str(exc))

    return StepResult(
        "2. Start n8n (Docker)",
        False,
        f"Unexpected state: {status.state} — {status.message}",
    )


def step_generate_workflow(secrets: dict) -> tuple[StepResult, dict | None, bool]:
    """Generate a minimal workflow with Gemini, or fall back to a blank workflow."""
    gemini_key = (secrets.get("gemini_api_key") or "").strip()
    model = secrets.get("gemini_model") or DEFAULT_GEMINI_MODEL

    if not gemini_key:
        workflow = build_blank_workflow("E2E Integration Test")
        return (
            StepResult(
                "3. Generate workflow (Gemini)",
                False,
                "Skipped live Gemini call (no API key). Using blank workflow fallback for later steps.",
            ),
            workflow,
            False,
        )

    prompt = (
        "Create a minimal n8n workflow named E2E Integration Test that runs on a "
        "manual trigger and sets a single Set node field message to hello."
    )
    try:
        workflow = generate_workflow_with_gemini(
            api_key=gemini_key,
            user_prompt=prompt,
            model=model,
        )
    except Exception as exc:
        workflow = build_blank_workflow("E2E Integration Test")
        return (
            StepResult("3. Generate workflow (Gemini)", False, f"{exc} (using blank workflow fallback)."),
            workflow,
            False,
        )

    name = workflow.get("name", "")
    nodes = workflow.get("nodes") or []
    if not name or not nodes:
        return StepResult("3. Generate workflow (Gemini)", False, "Empty workflow returned."), None, False

    return (
        StepResult(
            "3. Generate workflow (Gemini)",
            True,
            f'Generated "{name}" with {len(nodes)} node(s) via {model}.',
        ),
        workflow,
        True,
    )


def step_edit_json(workflow: dict) -> tuple[StepResult, dict]:
    """Simulate editor edit: rename workflow and re-validate JSON."""
    edited = dict(workflow)
    edited["name"] = "E2E Integration Test (edited)"
    raw = json.dumps(edited, indent=2)

    # Round-trip like the Ace editor
    reparsed = parse_workflow_json(raw)
    payload = prepare_workflow_for_push(reparsed)

    if payload.get("name") != edited["name"]:
        return StepResult("4. Edit JSON", False, "Edited name lost after validation."), edited

    return (
        StepResult(
            "4. Edit JSON",
            True,
            f'Validated edited workflow "{payload["name"]}" ({len(payload.get("nodes", []))} nodes).',
        ),
        payload,
    )


def step_push_to_n8n(workflow: dict, secrets: dict) -> StepResult:
    """Push workflow to n8n and delete the test artifact."""
    n8n_url = (secrets.get("n8n_url") or "http://localhost:5678").strip().rstrip("/")
    n8n_key = (secrets.get("n8n_api_key") or "").strip()

    if not n8n_key:
        return StepResult(
            "5. Push to n8n",
            False,
            "No n8n_api_key in secrets.toml - save n8n credentials in the sidebar.",
        )

    base_url = f"{n8n_url}/api/v1"
    client = N8nClient(base_url, n8n_key)
    result = client.push_workflow(workflow, n8n_url)

    if not result.success:
        code = f" (HTTP {result.status_code})" if result.status_code else ""
        return StepResult("5. Push to n8n", False, f"{result.error}{code}")

    workflow_id = result.workflow_id
    detail = (
        f'Pushed "{result.workflow_name}" · id={workflow_id} · '
        f'{result.node_count} nodes · editor: {result.editor_url}'
    )

    if workflow_id:
        try:
            client.delete_workflow(workflow_id)
            detail += " · test workflow deleted"
        except Exception as exc:
            detail += f" · cleanup failed: {exc}"

    return StepResult("5. Push to n8n", True, detail)


def step_module_imports() -> StepResult:
    """Smoke-test that core modules import cleanly (without starting Streamlit)."""
    try:
        from views import generator_tab, docker_panel, hub_home  # noqa: F401
        from utils.user_feedback import explain_n8n_api_error  # noqa: F401
        from views.generator_fab import render_generator_keyboard_shortcut  # noqa: F401
    except Exception as exc:
        return StepResult("0. Module imports", False, str(exc))
    return StepResult("0. Module imports", True, "Core views and services load OK")


def _safe_print(text: str) -> None:
    """Print without crashing on Windows cp1252 consoles."""
    encoding = getattr(sys.stdout, "encoding", None) or "utf-8"
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode(encoding, errors="replace").decode(encoding, errors="replace"))


def main() -> int:
    print("=" * 60)
    _safe_print("Automation Hub - End-to-End Integration Test (N19)")
    print("=" * 60)

    results: list[StepResult] = []

    results.append(step_module_imports())

    secrets = read_secrets()
    has_n8n = bool(secrets.get("n8n_api_key"))
    print(f"\nSecrets: gemini={'yes' if secrets.get('gemini_api_key') else 'no'}, "
          f"n8n={'yes' if has_n8n else 'no'}, "
          f"model={secrets.get('gemini_model') or DEFAULT_GEMINI_MODEL}")

    results.append(step_select_model_and_save_gemini_key(secrets))
    results.append(step_start_n8n())

    gen_result, workflow, gemini_live = step_generate_workflow(secrets)
    results.append(gen_result)

    if workflow:
        edit_result, edited = step_edit_json(workflow)
        results.append(edit_result)
        if edit_result.passed:
            results.append(step_push_to_n8n(edited, secrets))
    else:
        results.append(StepResult("4. Edit JSON", False, "Skipped - generation failed."))
        results.append(StepResult("5. Push to n8n", False, "Skipped - generation failed."))

    print()
    passed = sum(1 for r in results if r.passed)
    required = [r for r in results if r.name.startswith(("0.", "2.", "4.", "5."))]
    required_passed = sum(1 for r in required if r.passed)
    gemini_steps = [r for r in results if r.name.startswith(("1.", "3."))]
    gemini_passed = sum(1 for r in gemini_steps if r.passed)

    for r in results:
        icon = "PASS" if r.passed else "FAIL"
        print(f"[{icon}] {r.name}")
        if r.detail:
            _safe_print(f"       {r.detail}")

    print()
    print(f"Result: {passed}/{len(results)} steps passed")
    if not gemini_live:
        print("Note: Steps 1 and 3 need a saved Gemini API key for the full UI flow.")
    print(f"Infrastructure (Docker, JSON, push): {required_passed}/{len(required)} passed")
    print("=" * 60)

    # Pass if infrastructure path works; Gemini steps are required only when key is saved.
    gemini_key_present = bool((secrets.get("gemini_api_key") or "").strip())
    if gemini_key_present:
        return 0 if passed == len(results) else 1
    return 0 if required_passed == len(required) else 1


if __name__ == "__main__":
    raise SystemExit(main())
