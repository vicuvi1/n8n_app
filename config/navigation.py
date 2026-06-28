"""Sidebar navigation — Automation Hub pages."""

HUB_PAGES: dict[str, dict[str, str]] = {
    "hub": {
        "label": "Hub Overview",
        "icon": "🏠",
        "description": "Dashboard summary and quick actions",
    },
    "docker": {
        "label": "Docker Control",
        "icon": "🐳",
        "description": "Start, stop & monitor n8n in Docker",
    },
    "generator": {
        "label": "Gemini Generator",
        "icon": "✨",
        "description": "Generate workflows with Gemini",
    },
    "control": {
        "label": "Control Center",
        "icon": "⚙️",
        "description": "Manage workflows on n8n",
    },
    "monitor": {
        "label": "Execution Monitor",
        "icon": "📡",
        "description": "SOC-style run history",
    },
}

HUB_PAGE_ORDER = ["hub", "docker", "generator", "control", "monitor"]
DEFAULT_HUB_PAGE = "hub"
