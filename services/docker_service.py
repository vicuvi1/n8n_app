"""Docker control for local n8n container."""

from __future__ import annotations

import shutil
import socket
import subprocess
import time
from dataclasses import dataclass

from config.constants import DOCKER_CONTAINER_NAME, N8N_DEFAULT_PORT, N8N_DEFAULT_URL

N8N_STATUS_CACHE_SEC = 8
_status_cache: dict = {"ts": 0.0, "data": None}
_container_name_cache: str | None = None


class DockerError(Exception):
    """Raised when a Docker command fails."""


@dataclass
class DockerCommandResult:
    command: str
    message: str
    output: str = ""


@dataclass
class N8nRuntimeStatus:
    state: str  # running | stopped | starting | unknown
    message: str
    container_running: bool
    port_open: bool
    container_name: str
    url: str


def _run_docker(args: list[str], timeout: int = 60) -> subprocess.CompletedProcess:
    if not shutil.which("docker"):
        raise DockerError(
            "Docker is not installed or not on PATH. Install Docker Desktop: https://www.docker.com/products/docker-desktop/"
        )
    try:
        return subprocess.run(
            ["docker", *args],
            capture_output=True,
            text=True,
            timeout=timeout,
            check=True,
        )
    except subprocess.CalledProcessError as exc:
        err = (exc.stderr or exc.stdout or "").strip()
        raise DockerError(err or f"Docker command failed: docker {' '.join(args)}") from exc
    except subprocess.TimeoutExpired as exc:
        raise DockerError("Docker command timed out.") from exc


def container_exists(name: str = DOCKER_CONTAINER_NAME) -> bool:
    try:
        result = subprocess.run(
            ["docker", "inspect", name],
            capture_output=True,
            text=True,
            timeout=10,
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def is_container_running(name: str = DOCKER_CONTAINER_NAME) -> bool:
    if not container_exists(name):
        return False
    try:
        result = _run_docker(["inspect", "-f", "{{.State.Running}}", name], timeout=10)
        return result.stdout.strip().lower() == "true"
    except DockerError:
        return False


def is_port_open(host: str = "127.0.0.1", port: int = N8N_DEFAULT_PORT) -> bool:
    try:
        with socket.create_connection((host, port), timeout=1.5):
            return True
    except OSError:
        return False


def invalidate_n8n_status_cache() -> None:
    """Clear cached Docker/port status (call after start/stop/restart)."""
    global _container_name_cache
    _status_cache["ts"] = 0.0
    _status_cache["data"] = None
    _container_name_cache = None


def _discover_n8n_container() -> str | None:
    """Find an n8n Docker container when the default name `n8n` is not used."""
    if not shutil.which("docker"):
        return None
    try:
        queries = [
            ["ps", "-a", "--filter", "ancestor=n8nio/n8n", "--format", "{{.Names}}"],
            ["ps", "-a", "--filter", "name=n8n", "--format", "{{.Names}}"],
        ]
        for args in queries:
            result = subprocess.run(
                ["docker", *args],
                capture_output=True,
                text=True,
                timeout=10,
            )
            names = [n.strip() for n in result.stdout.splitlines() if n.strip()]
            if names:
                return names[0]
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return None
    return None


def resolve_n8n_container_name(*, force: bool = False) -> str:
    """Return the Docker container name for the local n8n instance."""
    global _container_name_cache
    if (
        not force
        and _container_name_cache
        and container_exists(_container_name_cache)
    ):
        return _container_name_cache

    if container_exists(DOCKER_CONTAINER_NAME):
        _container_name_cache = DOCKER_CONTAINER_NAME
        return DOCKER_CONTAINER_NAME

    discovered = _discover_n8n_container()
    if discovered and container_exists(discovered):
        _container_name_cache = discovered
        return discovered

    return DOCKER_CONTAINER_NAME

def _build_n8n_status(
    container_name: str | None = None,
    url: str = N8N_DEFAULT_URL,
) -> N8nRuntimeStatus:
    """Compute n8n runtime status (uncached)."""
    container_name = container_name or resolve_n8n_container_name()
    if not shutil.which("docker"):
        return N8nRuntimeStatus(
            state="unknown",
            message="Docker not found — install Docker Desktop to use this panel.",
            container_running=False,
            port_open=False,
            container_name=container_name,
            url=url,
        )

    running = is_container_running(container_name)
    port = is_port_open()

    if running and port:
        return N8nRuntimeStatus(
            state="running",
            message=f"n8n is running on {url}",
            container_running=True,
            port_open=True,
            container_name=container_name,
            url=url,
        )

    if running and not port:
        return N8nRuntimeStatus(
            state="starting",
            message=f"Container `{container_name}` is up — waiting for {url} …",
            container_running=True,
            port_open=False,
            container_name=container_name,
            url=url,
        )

    if port:
        return N8nRuntimeStatus(
            state="running",
            message=f"n8n is running on {url}",
            container_running=running,
            port_open=True,
            container_name=container_name,
            url=url,
        )

    return N8nRuntimeStatus(
        state="stopped",
        message="n8n is stopped",
        container_running=False,
        port_open=False,
        container_name=container_name,
        url=url,
    )


def get_n8n_status(
    container_name: str | None = None,
    url: str = N8N_DEFAULT_URL,
    *,
    force_refresh: bool = False,
) -> N8nRuntimeStatus:
    """Return combined Docker + port status for n8n (cached briefly)."""
    now = time.time()
    cached = _status_cache.get("data")
    if (
        not force_refresh
        and cached is not None
        and now - float(_status_cache.get("ts", 0)) < N8N_STATUS_CACHE_SEC
    ):
        return cached

    resolved = container_name or resolve_n8n_container_name(force=force_refresh)
    status = _build_n8n_status(resolved, url)
    _status_cache["ts"] = now
    _status_cache["data"] = status
    return status


def start_n8n(container_name: str | None = None) -> DockerCommandResult:
    container_name = container_name or resolve_n8n_container_name()
    if not container_exists(container_name):
        raise DockerError(
            f"Container `{container_name}` not found. Create it first:\n"
            f"docker run -d --name {container_name} -p 5678:5678 n8nio/n8n"
        )
    proc = _run_docker(["start", container_name])
    output = (proc.stdout or proc.stderr or "").strip()
    return DockerCommandResult(
        command=f"docker start {container_name}",
        message=f"Started container `{container_name}`.",
        output=output,
    )


def stop_n8n(container_name: str | None = None) -> DockerCommandResult:
    container_name = container_name or resolve_n8n_container_name()
    if not container_exists(container_name):
        raise DockerError(f"Container `{container_name}` does not exist.")
    proc = _run_docker(["stop", container_name])
    output = (proc.stdout or proc.stderr or "").strip()
    return DockerCommandResult(
        command=f"docker stop {container_name}",
        message=f"Stopped container `{container_name}`.",
        output=output,
    )


def restart_n8n(container_name: str | None = None) -> DockerCommandResult:
    container_name = container_name or resolve_n8n_container_name()
    if not container_exists(container_name):
        raise DockerError(f"Container `{container_name}` does not exist.")
    proc = _run_docker(["restart", container_name])
    output = (proc.stdout or proc.stderr or "").strip()
    return DockerCommandResult(
        command=f"docker restart {container_name}",
        message=f"Restarted container `{container_name}`.",
        output=output,
    )
