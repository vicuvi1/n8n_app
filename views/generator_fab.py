"""Floating quick-access button and keyboard shortcut for the Workflow Generator."""

from __future__ import annotations

from collections.abc import Callable

import streamlit as st
import streamlit.components.v1 as components

from config.navigation import HUB_PAGES

GENERATOR_PAGE_ID = "generator"
GENERATOR_SHORTCUT_LABEL = "Ctrl+Shift+N"
GENERATOR_SHORTCUT_HINT = "Ctrl+Shift+N (Windows/Linux) · Cmd+Shift+N (Mac)"
SHORTCUT_BUTTON_KEY = "generator_shortcut_nav"


def _open_generator(navigate: Callable[[str], None]) -> None:
    if st.session_state.get("active_hub_page") == GENERATOR_PAGE_ID:
        return
    navigate(GENERATOR_PAGE_ID)


def render_generator_keyboard_shortcut(navigate: Callable[[str], None]) -> None:
    """Bind Ctrl/Cmd+Shift+N to open the Gemini Workflow Generator."""
    st.markdown(
        f"""
        <style>
        .st-key-{SHORTCUT_BUTTON_KEY} {{
            position: absolute !important;
            width: 1px !important;
            height: 1px !important;
            overflow: hidden !important;
            clip: rect(0, 0, 0, 0) !important;
            white-space: nowrap !important;
            border: 0 !important;
            padding: 0 !important;
            margin: -1px !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

    if st.button(
        "Open Workflow Generator",
        key=SHORTCUT_BUTTON_KEY,
        help=f"Keyboard shortcut: {GENERATOR_SHORTCUT_HINT}",
    ):
        _open_generator(navigate)

    components.html(
        f"""
        <script>
        (function () {{
          const win = window.parent;
          if (win.__n8nGeneratorShortcutInstalled) return;
          win.__n8nGeneratorShortcutInstalled = true;

          win.document.addEventListener(
            "keydown",
            function (event) {{
              if (!(event.ctrlKey || event.metaKey) || !event.shiftKey) return;
              if (event.key !== "N" && event.key !== "n") return;

              event.preventDefault();
              event.stopPropagation();

              const btn = win.document.querySelector(".st-key-{SHORTCUT_BUTTON_KEY} button");
              if (btn) btn.click();
            }},
            true
          );
        }})();
        </script>
        """,
        height=0,
    )


def render_workflow_generator_fab(navigate: Callable[[str], None]) -> None:
    """
    Fixed bottom-right FAB to open the Gemini Workflow Generator.

    Hidden while already on the generator page.
    """
    if st.session_state.get("active_hub_page") == GENERATOR_PAGE_ID:
        return

    page = HUB_PAGES[GENERATOR_PAGE_ID]
    tooltip = (
        f"{page['icon']} {page['label']} — build n8n workflows with Gemini "
        f"({GENERATOR_SHORTCUT_HINT})"
    )

    if st.button(
        "✨",
        key="fab_open_workflow_generator",
        help=tooltip,
        type="primary",
    ):
        _open_generator(navigate)
