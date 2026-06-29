# n8n AI Management Dashboard

A Python **Streamlit** application that uses **Google Gemini** to generate n8n workflows from plain-English prompts and the **official n8n REST API** to create, manage, activate, and monitor workflows — all from a polished dark-mode command center UI.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32%2B-red)
![License](https://img.shields.io/badge/License-MIT-green)

## Overview

| Tab | Description |
|-----|-------------|
| **AI Generator** | Describe an automation in English → Gemini returns production-ready n8n JSON → push to your instance |
| **Control Center** | List all workflows with summary metrics, toggle active/inactive, delete |
| **Execution Monitor** | SOC-style log of recent runs with failed executions highlighted in red |

## Screenshots

The dashboard features a dark slate theme inspired by modern dev tools (Linear/Vercel aesthetic), with:

- Branded header and sidebar with connection status pills
- Pill-style tab navigation with accent highlights
- KPI cards for workflow and execution stats
- Bordered data tables and empty states when credentials are missing

## Prerequisites

1. **Python 3.10+**
2. **n8n** running locally or remotely (e.g. `http://localhost:5678`)
3. **n8n API key** — in n8n go to **Settings → API**, create a key with scopes:
   - `workflow:read`, `workflow:create`, `workflow:update`, `workflow:delete`
   - `execution:read`
4. **Google Gemini API key** — free tier at [Google AI Studio](https://aistudio.google.com/apikey)

## Quick start

```powershell
# Clone the repo
git clone https://github.com/vicuvi1/n8n_app.git
cd n8n_app

# Create virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Launch the dashboard
streamlit run app.py
```

The app opens in your browser at **http://localhost:8501**.

## Windows desktop launcher (.exe)

Build a one-click **`n8n Command Center.exe`** with a custom icon. Each time you run it, the launcher will:

1. **Git pull** the latest code from [github.com/vicuvi1/n8n_app](https://github.com/vicuvi1/n8n_app)
2. **Install/update** all Python dependencies in a local venv
3. **Start Streamlit** and open `http://localhost:8501` in your browser

App files are stored at: `%LOCALAPPDATA%\n8n_command_center\`

### Download pre-built .exe (recommended)

Download **`n8n Command Center.exe`** from [GitHub Releases](https://github.com/vicuvi1/n8n_app/releases) — no build step required. Place it on your Desktop and double-click to launch.

> The `.exe` is not stored in git (see `.gitignore`). New builds are published automatically when a version tag like `v1.0.0` is pushed.

### Prerequisites to build & run the .exe

- **Python 3.10+** ([python.org](https://www.python.org/downloads/)) — check "Add Python to PATH"
- **Git** ([git-scm.com](https://git-scm.com/download/win))

### Build the executable

```powershell
cd c:\Users\victo\Desktop\n8n_app\launcher
.\build.ps1
```

Output: `launcher\dist\n8n Command Center.exe`

Copy that file to your Desktop or pin it to the taskbar. Double-click to launch.

**First-run tip:** To persist your API keys, copy your secrets file after the first launch:

```powershell
mkdir "$env:LOCALAPPDATA\n8n_command_center\.streamlit" -Force
copy ".streamlit\secrets.toml" "$env:LOCALAPPDATA\n8n_command_center\.streamlit\secrets.toml"
```

> **Note:** Keep the launcher window open while using the app. Press `Ctrl+C` in that window to stop the server.

### macOS / Linux

```bash
git clone https://github.com/vicuvi1/n8n_app.git
cd n8n_app
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Configuration

Enter credentials in the **sidebar**:

| Field | Example |
|-------|---------|
| Gemini API Key | `AIza...` |
| n8n Instance URL | `http://localhost:5678` |
| n8n API Key | Your n8n API key |

Credentials are stored in **Streamlit session state only** (in-memory, per browser tab). They are not saved to disk.

### Optional: persistent secrets

Create `.streamlit/secrets.toml` (gitignored) for keys that survive restarts:

```toml
gemini_api_key = "AIza..."
n8n_url = "http://localhost:5678"
n8n_api_key = "n8n_api_..."
```

See [Streamlit secrets management](https://docs.streamlit.io/develop/concepts/connections/secrets-management).

### Theme

The dark theme is configured in [`.streamlit/config.toml`](.streamlit/config.toml). Customize colors there without touching application code.

## Project structure

```
n8n_app/
├── app.py                          # Streamlit entry — 3 tabs + sidebar
├── requirements.txt
├── .streamlit/config.toml          # Dark theme (slate + n8n pink accent)
├── config/
│   └── constants.py                # Model name, timeouts, limits
├── prompts/
│   └── n8n_system_prompt.py        # Gemini system prompt (n8n expert)
├── services/
│   ├── gemini_client.py            # Gemini workflow generation
│   └── n8n_client.py               # n8n REST API wrapper
├── utils/
│   ├── session.py                  # Session state helpers
│   ├── json_utils.py               # JSON parse + workflow validation
│   ├── workflow_viz.py             # Mermaid flow diagrams
│   └── ui.py                       # Custom CSS + UI components
├── views/
│   └── generator_tab.py            # AI Generator tab UI
├── assets/
│   └── icon.ico                    # App icon for Windows .exe
└── launcher/
    ├── launcher.py                 # Auto-update + start script
    ├── build.ps1                   # Builds the .exe
    ├── generate_icon.py            # Creates assets/icon.ico
    └── n8n_command_center.spec     # PyInstaller config
```

## How it works

### AI Workflow Generator

1. Type a plain-English automation description.
2. Gemini (`gemini-2.5-flash`) returns a valid n8n workflow JSON object.
3. Preview the JSON in the UI.
4. Click **Push to n8n** to `POST /api/v1/workflows`.

The system prompt forces JSON-only output with `name`, `nodes`, `connections`, and `settings`. Read-only fields are stripped before upload.

### Workflow Control Center

- Fetches all workflows via `GET /api/v1/workflows`
- Shows total / active / inactive counts
- **Activate** / **Deactivate** via dedicated POST endpoints
- **Delete** with confirmation step

### Execution Monitor

- Fetches recent runs via `GET /api/v1/executions?limit=50`
- KPI cards for total, success, and failed runs
- Failed executions highlighted in red
- Optional auto-refresh every 10 seconds

## n8n API endpoints

| Action | Method | Path |
|--------|--------|------|
| List workflows | `GET` | `/api/v1/workflows` |
| Create workflow | `POST` | `/api/v1/workflows` |
| Delete workflow | `DELETE` | `/api/v1/workflows/{id}` |
| Activate | `POST` | `/api/v1/workflows/{id}/activate` |
| Deactivate | `POST` | `/api/v1/workflows/{id}/deactivate` |
| List executions | `GET` | `/api/v1/executions` |

Base URL: `{your_n8n_url}/api/v1`  
Auth header: `X-N8N-API-KEY: <your_key>`

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Cannot reach n8n | Verify URL and that n8n is running on port 5678 |
| 401/403 from n8n | Regenerate API key with correct scopes |
| Gemini key rejected | Check key at [AI Studio](https://aistudio.google.com/apikey) |
| Invalid JSON from AI | Rephrase prompt; raw model output is shown on error |
| Push fails | Ensure workflow JSON has `name`, `nodes`, `connections` |
| Styles not updating | Hard-refresh browser or restart `streamlit run app.py` |

## Tech stack

- **UI:** Streamlit + custom CSS (Inter font, dark theme)
- **AI:** Google Gemini API via `google-genai` SDK
- **API client:** `requests` → n8n REST API v1
- **Data:** `pandas` for workflow/execution tables

## License

MIT
