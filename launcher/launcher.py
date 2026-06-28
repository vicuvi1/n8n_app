"""
n8n Command Center — Windows launcher.

On each run:
  1. Clone or git-pull the latest app from GitHub
  2. Create/update a virtual environment
  3. pip install -r requirements.txt (upgrade)
  4. Start Streamlit and open the browser
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


def pause(msg: str = "Press Enter to exit…") -> None:
    try:
        input(msg)
    except EOFError:
        pass


def log(msg: str) -> None:
    print(f"[n8n] {msg}", flush=True)


def run(cmd: list[str] | str, cwd: Path | None = None, check: bool = True) -> subprocess.CompletedProcess:
    log(f"> {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    return subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        check=check,
        shell=isinstance(cmd, str),
        text=True,
    )


def get_install_dir() -> Path:
    """Persistent install location (survives exe updates)."""
    base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    return base / APP_FOLDER_NAME


def find_python() -> str | None:
    """Find Python 3.10+ on Windows."""
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
                cmd + ["-c", "import sys; raise SystemExit(0 if sys.version_info >= (3,10) else 1)"],
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


def sync_repository(install_dir: Path) -> Path:
    git = find_git()
    if not git:
        raise RuntimeError(
            "Git is not installed. Install from https://git-scm.com/download/win and try again."
        )

    if not install_dir.exists():
        install_dir.parent.mkdir(parents=True, exist_ok=True)
        log(f"Cloning repository to {install_dir}…")
        run([git, "clone", "--branch", REPO_BRANCH, "--depth", "1", REPO_URL, str(install_dir)])
    else:
        log("Pulling latest changes from GitHub…")
        run([git, "-C", str(install_dir), "fetch", "origin", REPO_BRANCH])
        run([git, "-C", str(install_dir), "reset", "--hard", f"origin/{REPO_BRANCH}"])

    return install_dir


def _python_args(python_cmd: str) -> list[str]:
    """Split 'py -3.12' or 'python' into argv prefix."""
    return python_cmd.split()


def ensure_venv(app_dir: Path, python_cmd: str) -> Path:
    venv_dir = app_dir / ".venv"
    if not venv_dir.exists():
        log("Creating virtual environment…")
        run(_python_args(python_cmd) + ["-m", "venv", str(venv_dir)])

    if sys.platform == "win32":
        python = venv_dir / "Scripts" / "python.exe"
        pip = venv_dir / "Scripts" / "pip.exe"
    else:
        python = venv_dir / "bin" / "python"
        pip = venv_dir / "bin" / "pip"

    if not python.exists():
        raise RuntimeError(f"Virtual environment is broken. Delete {venv_dir} and retry.")

    log("Installing / updating dependencies…")
    run([str(pip), "install", "--upgrade", "pip"], cwd=app_dir)
    run([str(pip), "install", "--upgrade", "-r", "requirements.txt"], cwd=app_dir)

    return python


def is_streamlit_running() -> bool:
    import socket

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(1)
        return sock.connect_ex((STREAMLIT_HOST, STREAMLIT_PORT)) == 0


def start_streamlit(python: Path, app_dir: Path) -> subprocess.Popen:
    log(f"Starting dashboard at {APP_URL} …")
    env = os.environ.copy()
    env["BROWSER"] = "none"  # we open browser ourselves

    proc = subprocess.Popen(
        [
            str(python),
            "-m",
            "streamlit",
            "run",
            "app.py",
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

    # Wait for server to accept connections
    for _ in range(30):
        if is_streamlit_running():
            break
        time.sleep(0.5)

    webbrowser.open(APP_URL)
    log("Dashboard opened in your browser. Keep this window open while using the app.")
    return proc


def main() -> int:
    print()
    print("=" * 52)
    print("   n8n Command Center — Launcher")
    print("=" * 52)
    print()

    python_cmd = find_python()
    if not python_cmd:
        log("ERROR: Python 3.10+ not found.")
        log("Install from https://www.python.org/downloads/ (check 'Add to PATH').")
        pause()
        return 1

    log(f"Using Python: {python_cmd}")

    try:
        install_dir = get_install_dir()
        app_dir = sync_repository(install_dir)
        venv_python = ensure_venv(app_dir, python_cmd)
        proc = start_streamlit(venv_python, app_dir)

        log("Press Ctrl+C here to stop the server.")
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
