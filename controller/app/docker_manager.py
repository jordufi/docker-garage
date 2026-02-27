"""
Docker Compose manager — thin wrapper around the Docker CLI.

Uses Docker-out-of-Docker (DOOD): the controller container mounts
the host's /var/run/docker.sock and shells out to `docker compose`.
This keeps dependencies minimal (no Docker SDK) and behaviour
identical to manual CLI usage.
"""

import json
import logging
import os
import subprocess
from pathlib import Path

from .config import APPS_DIR, HOST_APPS_DIR

logger = logging.getLogger(__name__)


class DockerManager:
    """Static helpers for docker compose lifecycle operations."""

    @staticmethod
    def _build_env(app_slug: str) -> dict[str, str]:
        """
        Build environment dict for subprocess calls.

        Injects HOST_APPS_DIR so managed compose files can use
        ${HOST_APPS_DIR} for bind mounts that resolve on the host.
        """
        env = dict(os.environ)
        # Provide both the base HOST_APPS_DIR and the specific app path
        host_app_dir = str(Path(HOST_APPS_DIR) / app_slug)
        env["HOST_APPS_DIR"] = HOST_APPS_DIR
        env["HOST_APP_DIR"] = host_app_dir
        return env

    @staticmethod
    def _run(
        args: list[str], cwd: str, env: dict[str, str] | None = None
    ) -> subprocess.CompletedProcess:
        """Run a subprocess and return the result (never raises)."""
        logger.info("Running: %s  cwd=%s", " ".join(args), cwd)
        return subprocess.run(
            args,
            cwd=cwd,
            env=env,
            capture_output=True,
            text=True,
            timeout=120,
        )

    @staticmethod
    def compose_up(app_slug: str) -> tuple[bool, str]:
        """Start an app stack. Returns (success, message)."""
        app_dir = str(Path(APPS_DIR) / app_slug)
        env = DockerManager._build_env(app_slug)
        result = DockerManager._run(
            ["docker", "compose", "up", "-d", "--remove-orphans"],
            cwd=app_dir,
            env=env,
        )
        if result.returncode != 0:
            logger.error("compose up failed: %s", result.stderr)
            return False, result.stderr.strip()
        return True, "started"

    @staticmethod
    def compose_down(app_slug: str) -> tuple[bool, str]:
        """Stop an app stack. Returns (success, message)."""
        app_dir = str(Path(APPS_DIR) / app_slug)
        env = DockerManager._build_env(app_slug)
        result = DockerManager._run(
            ["docker", "compose", "down"],
            cwd=app_dir,
            env=env,
        )
        if result.returncode != 0:
            logger.error("compose down failed: %s", result.stderr)
            return False, result.stderr.strip()
        return True, "stopped"

    @staticmethod
    def get_status(app_slug: str) -> str:
        """
        Query container status for an app stack.

        Returns:
            "running"  — all containers running
            "stopped"  — no containers or all exited
            "partial"  — mixed state
        """
        app_dir = str(Path(APPS_DIR) / app_slug)
        result = DockerManager._run(
            ["docker", "compose", "ps", "--format", "json"],
            cwd=app_dir,
        )

        if result.returncode != 0 or not result.stdout.strip():
            return "stopped"

        # docker compose ps --format json outputs one JSON object per line (NDJSON)
        containers = []
        for line in result.stdout.strip().splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                containers.append(json.loads(line))
            except json.JSONDecodeError:
                continue

        if not containers:
            return "stopped"

        states = {c.get("State", "").lower() for c in containers}

        if states == {"running"}:
            return "running"
        if "running" in states:
            return "partial"
        return "stopped"
