import json
import logging
import os
import re
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)

# Base directory where managed apps are stored (mounted volume)
APPS_DIR: str = os.getenv("APPS_DIR", "/apps")


def _detect_host_apps_dir() -> str:
    """
    Auto-detect the host-side absolute path of the /apps mount.

    Docker resolves bind mounts on the HOST filesystem, so managed apps
    that use volumes need the host path, not the container path.

    Detection order:
    1. HOST_APPS_DIR env var (explicit override — always wins)
    2. Inspect own container's mount info via Docker CLI
    3. Fallback to container-internal path (non-mount apps still work)
    """
    # 1. Explicit override
    explicit = os.getenv("HOST_APPS_DIR", "").strip()
    if explicit:
        logger.info("HOST_APPS_DIR from env: %s", explicit)
        return explicit

    # 2. Auto-detect from container mount info
    try:
        hostname = os.environ.get("HOSTNAME", "")
        if hostname:
            result = subprocess.run(
                ["docker", "inspect", hostname, "--format", "{{json .Mounts}}"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                mounts = json.loads(result.stdout.strip())
                for mount in mounts:
                    if mount.get("Destination") == APPS_DIR:
                        host_path = mount.get("Source", "")
                        if host_path:
                            logger.info("HOST_APPS_DIR auto-detected: %s", host_path)
                            return host_path
    except Exception as exc:
        logger.warning("Failed to auto-detect HOST_APPS_DIR: %s", exc)

    # 3. Fallback
    fallback = str(Path(APPS_DIR).resolve())
    logger.warning(
        "Could not detect host apps path. Using fallback: %s. "
        "Bind mounts in managed apps may not work. "
        "Set HOST_APPS_DIR in .env to fix this.",
        fallback,
    )
    return fallback


HOST_APPS_DIR: str = _detect_host_apps_dir()

# Regex to validate app slugs — prevents path traversal
SLUG_PATTERN: re.Pattern = re.compile(r"^[a-zA-Z0-9_-]+$")
