"""Application-wide constants."""

APP_TITLE = "n8n AI Management Dashboard"
APP_ICON = "⚡"

# Gemini model for workflow generation (free tier compatible).
GEMINI_MODEL = "gemini-2.5-flash"

# HTTP timeout for n8n API calls (seconds).
N8N_REQUEST_TIMEOUT = 15

# Default number of executions to fetch in the SOC monitor.
EXECUTIONS_LIMIT = 50

# Auto-refresh interval for execution monitor (seconds).
AUTO_REFRESH_INTERVAL = 10

# Set True to show full tracebacks in the UI (development only).
DEBUG = False
