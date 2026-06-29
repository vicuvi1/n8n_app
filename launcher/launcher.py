"""
n8n Command Center — Windows one-click launcher.

Each run:
  1. Sync latest app from GitHub (or use local dev folder)
  2. Create / refresh virtual environment
  3. pip install -r requirements.txt (upgrade)
  4. Verify key packages, then start Streamlit + open browser
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import time
import webbrowser
from pathlib import Path

REPO_URL = "https://github.com/vicuvi1/n8n_app.git"
REPO_BRANCH = "main"
APP_FOLDER_NAME = "n8n_command_center"
STREAMLIT_PORT = 8501
STREAMLIT_HOST = "localhost"
APP_URL = f"http://{STREAMLIT_HOST}:{STREAMLIT_PORT}"

REQUIRED_PACKAGES = (
    "streamlit",
    "streamlit_ace",
    "requests",
    "google.genai",
    "pandas",
)


def pause(msg: str = "Press Enter to exit…") -> None:
    try:
        input(msg)
    except EOFError:
        pass


def log(msg: str) -> None:
    print(f"[n8n] {msg}", flush=True)


def step(n: int, total: int, msg: str) -> None:
    log(f"[{n}/{total}] {msg}")


def run(cmd: list[str] | str, cwd: Path | None = None, check: bool = True) -> subprocess.CompletedProcess:
    display = " ".join(cmd) if isinstance(cmd, list) else cmd
    log(f"> {display}")
    return subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        check=check,
        shell=isinstance(cmd, str),
        text=True,
    )


def get_install_dir() -> Path:
    base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    return base / APP_FOLDER_NAME


def get_dev_app_dir() -> Path | None:
    """When launcher.py lives inside the repo, use that copy for development."""
    candidate = Path(__file__).resolve().parent.parent
    if (candidate / "app.py").is_file() and (candidate / "requirements.txt").is_file():
        return candidate
    return None


def find_python() -> str | None:
    candidates = [
        ["py", "-3.12"],
        ["py", "-3.11"],
        ["py", "-3.10"],
        ["py", "-3"],
        ["python"],
        ["python3"],
    ]
    for cmd in candidates:
        exe = cmd[0]
        if shutil.which(exe) is None:
            continue
        try:
            result = subprocess.run(
                cmd + ["-c", "import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)"],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                return exe if len(cmd) == 1 else f"{cmd[0]} {cmd[1]}"
        except OSError:
            continue
    return None


def find_git() -> str | None:
    return shutil.which("git")


def _python_args(python_cmd: str) -> list[str]:
    return python_cmd.split()


def git_head(app_dir: Path) -> str:
    git = find_git()
    if not git or not (app_dir / ".git").exists():
        return "unknown"
    result = subprocess.run(
        [git, "-C", str(app_dir), "rev-parse", "--short", "HEAD"],
        capture_output=True,
        text=True,
    )
    return result.stdout.strip() if result.returncode == 0 else "unknown"


def sync_repository(install_dir: Path) -> Path:
    git = find_git()
    if not git:
        raise RuntimeError(
            "Git is not installed. Install from https://git-scm.com/download/win and try again."
        )

    before = git_head(install_dir) if install_dir.exists() else None

    if not install_dir.exists():
        install_dir.parent.mkdir(parents=True, exist_ok=True)
        log(f"First run — cloning repository to {install_dir}")
        run([git, "clone", "--branch", REPO_BRANCH, REPO_URL, str(install_dir)])
    else:
        log("Checking for updates on GitHub…")
        run([git, "-C", str(install_dir), "fetch", "origin", REPO_BRANCH])
        run([git, "-C", str(install_dir), "reset", "--hard", f"origin/{REPO_BRANCH}"])

    after = git_head(install_dir)
    if before and before != after:
        log(f"Updated: {before} → {after}")
    elif before == after:
        log(f"Already on latest version ({after})")
    else:
        log(f"Installed version {after}")

    return install_dir


def resolve_app_dir() -> Path:
    """Use local repo when developing; otherwise sync to %LOCALAPPDATA%."""
    force_github = os.environ.get("N8N_LAUNCHER_USE_GITHUB", "").lower() in ("1", "true", "yes")
    dev_dir = get_dev_app_dir()

    if dev_dir and not force_github:
        log(f"Local app folder detected: {dev_dir}")
        if find_git() and (dev_dir / ".git").exists():
            try:
                before = git_head(dev_dir)
                run(["git", "-C", str(dev_dir), "pull", "--ff-only", "origin", REPO_BRANCH], check=False)
                after = git_head(dev_dir)
                if before != after:
                    log(f"Local repo updated: {before} → {after}")
                else:
                    log(f"Local repo is up to date ({after})")
            except Exception:
                log("Could not git pull local folder — continuing with current files.")
        return dev_dir

    return sync_repository(get_install_dir())


def ensure_venv(app_dir: Path, python_cmd: str) -> Path:
    venv_dir = app_dir / ".venv"
    if not venv_dir.exists():
        log("Creating virtual environment…")
        run(_python_args(python_cmd) + ["-m", "venv", str(venv_dir)])

    if sys.platform == "win32":
        python = venv_dir / "Scripts" / "python.exe"
    else:
        python = venv_dir / "bin" / "python"

    if not python.exists():
        raise RuntimeError(f"Virtual environment is broken. Delete {venv_dir} and retry.")

    req_file = app_dir / "requirements.txt"
    if not req_file.is_file():
        raise RuntimeError(f"Missing requirements.txt in {app_dir}")

    log("Upgrading pip and installing requirements…")
    # Windows requires `python -m pip` to upgrade pip itself (not pip.exe directly).
    run([str(python), "-m", "pip", "install", "--upgrade", "pip"], cwd=app_dir)
    run([str(python), "-m", "pip", "install", "--upgrade", "-r", "requirements.txt"], cwd=app_dir)

    return python


def verify_packages(python: Path) -> None:
    """Import-check critical dependencies after pip install."""
    checks = "; ".join(f"import {pkg}" for pkg in REQUIRED_PACKAGES)
    run([str(python), "-c", checks])

    version_script = (
        "import streamlit as st; "
        "print('streamlit', st.__version__)"
    )
    run([str(python), "-c", version_script])


def ensure_streamlit_config(app_dir: Path) -> None:
    streamlit_dir = app_dir / ".streamlit"
    streamlit_dir.mkdir(parents=True, exist_ok=True)
    secrets = streamlit_dir / "secrets.toml"
    if not secrets.exists():
        example = streamlit_dir / "secrets.example.toml"
        if example.exists():
            log("Tip: copy secrets.example.toml → secrets.toml to save API keys between runs.")


def is_streamlit_running() -> bool:
    import socket

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(1)
        return sock.connect_ex((STREAMLIT_HOST, STREAMLIT_PORT)) == 0


def start_streamlit(python: Path, app_dir: Path) -> subprocess.Popen:
    app_py = app_dir / "app.py"
    if not app_py.is_file():
        raise RuntimeError(f"app.py not found in {app_dir}")

    log(f"Starting dashboard at {APP_URL}")
    env = os.environ.copy()
    env["BROWSER"] = "none"

    proc = subprocess.Popen(
        [
            str(python),
            "-m",
            "streamlit",
            "run",
            str(app_py),
            "--server.port",
            str(STREAMLIT_PORT),
            "--server.headless",
            "true",
            "--browser.gatherUsageStats",
            "false",
        ],
        cwd=str(app_dir),
        env=env,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0,
    )

    for _ in range(40):
        if is_streamlit_running():
            break
        time.sleep(0.5)
    else:
        log("WARNING: Server is slow to start — opening browser anyway.")

    webbrowser.open(APP_URL)
    log("Dashboard opened in your browser.")
    log("Keep this window open while using the app. Press Ctrl+C to stop.")
    return proc


def main() -> int:
    total_steps = 4
    print()
    print("=" * 54)
    print("   n8n Command Center")
    print("   Auto-update · install deps · launch dashboard")
    print("=" * 54)
    print()

    python_cmd = find_python()
    if not python_cmd:
        log("ERROR: Python 3.10+ not found.")
        log("Install from https://www.python.org/downloads/ (check 'Add Python to PATH').")
        pause()
        return 1

    log(f"Python: {python_cmd}")

    try:
        step(1, total_steps, "Sync application files")
        app_dir = resolve_app_dir()

        step(2, total_steps, "Set up virtual environment & dependencies")
        venv_python = ensure_venv(app_dir, python_cmd)

        step(3, total_steps, "Verify installed packages")
        verify_packages(venv_python)
        ensure_streamlit_config(app_dir)

        step(4, total_steps, "Start Streamlit server")
        proc = start_streamlit(venv_python, app_dir)
        proc.wait()
        return proc.returncode or 0

    except subprocess.CalledProcessError as exc:
        log(f"ERROR: Command failed (exit {exc.returncode}).")
        pause()
        return exc.returncode or 1
    except KeyboardInterrupt:
        log("Shutting down…")
        return 0
    except Exception as exc:
        log(f"ERROR: {exc}")
        pause()
        return 1


if __name__ == "__main__":
    sys.exit(main())
