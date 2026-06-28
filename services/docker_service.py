"""Docker control for local n8n container."""

from __future__ import annotations

import shutil
import socket
import subprocess
from dataclasses import dataclass

from config.constants import DOCKER_CONTAINER_NAME, N8N_DEFAULT_PORT, N8N_DEFAULT_URL


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


def get_n8n_status(
    container_name: str = DOCKER_CONTAINER_NAME,
    url: str = N8N_DEFAULT_URL,
) -> N8nRuntimeStatus:
    """Return combined Docker + port status for n8n."""
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


def start_n8n(container_name: str = DOCKER_CONTAINER_NAME) -> DockerCommandResult:
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


def stop_n8n(container_name: str = DOCKER_CONTAINER_NAME) -> DockerCommandResult:
    if not container_exists(container_name):
        raise DockerError(f"Container `{container_name}` does not exist.")
    proc = _run_docker(["stop", container_name])
    output = (proc.stdout or proc.stderr or "").strip()
    return DockerCommandResult(
        command=f"docker stop {container_name}",
        message=f"Stopped container `{container_name}`.",
        output=output,
    )


def restart_n8n(container_name: str = DOCKER_CONTAINER_NAME) -> DockerCommandResult:
    if not container_exists(container_name):
        raise DockerError(f"Container `{container_name}` does not exist.")
    proc = _run_docker(["restart", container_name])
    output = (proc.stdout or proc.stderr or "").strip()
    return DockerCommandResult(
        command=f"docker restart {container_name}",
        message=f"Restarted container `{container_name}`.",
        output=output,
    )
