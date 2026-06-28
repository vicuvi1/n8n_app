"""Application-wide constants."""

APP_TITLE = "n8n AI Management Dashboard"
APP_ICON = "⚡"

# LLM providers (sidebar dropdown labels).
LLM_PROVIDERS = ["Google Gemini", "OpenAI", "Groq"]

# Google Gemini models — id -> display label (sidebar selectbox).
GEMINI_MODELS: dict[str, str] = {
    "gemini-2.5-flash": "Gemini 2.5 Flash (recommended)",
    "gemini-2.5-flash-lite": "Gemini 2.5 Flash Lite (fast / free tier)",
    "gemini-2.5-pro": "Gemini 2.5 Pro (highest quality)",
    "gemini-2.0-flash": "Gemini 2.0 Flash (stable)",
    "gemini-2.0-flash-lite": "Gemini 2.0 Flash Lite",
    "gemini-1.5-flash-8b": "Gemini 1.5 Flash 8B (legacy, lightweight)",
}

DEFAULT_GEMINI_MODEL = "gemini-2.5-flash"
GEMINI_MODEL_KEYS = list(GEMINI_MODELS.keys())

# Other provider defaults.
OPENAI_MODEL = "gpt-4o-mini"
GROQ_MODEL = "llama-3.3-70b-versatile"

# Backward-compatible alias.
GEMINI_MODEL = DEFAULT_GEMINI_MODEL

# Docker n8n instance (control panel).
DOCKER_CONTAINER_NAME = "n8n"
N8N_DEFAULT_URL = "http://localhost:5678"
N8N_DEFAULT_PORT = 5678
DOCKER_STATUS_REFRESH_SEC = 3

# HTTP timeout for n8n API calls (seconds).
N8N_REQUEST_TIMEOUT = 15

# Default number of executions to fetch in the SOC monitor.
EXECUTIONS_LIMIT = 50

# Auto-refresh interval for execution monitor (seconds).
AUTO_REFRESH_INTERVAL = 10

# Set True to show full tracebacks in the UI (development only).
DEBUG = False

# Workflow generator optimization modes.
WORKFLOW_OPTIMIZATION_SPEED = "speed"
WORKFLOW_OPTIMIZATION_RELIABILITY = "reliability"
WORKFLOW_OPTIMIZATION_OPTIONS: dict[str, str] = {
    WORKFLOW_OPTIMIZATION_SPEED: "Optimize for Speed",
    WORKFLOW_OPTIMIZATION_RELIABILITY: "Optimize for Reliability",
}
DEFAULT_WORKFLOW_OPTIMIZATION = WORKFLOW_OPTIMIZATION_SPEED
WORKFLOW_OPTIMIZATION_KEYS = list(WORKFLOW_OPTIMIZATION_OPTIONS.keys())
