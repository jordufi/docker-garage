"""
Application discovery and metadata service.

Reads the /apps directory, parses each app's app.json, and enriches it
with live container status from the Docker CLI.
"""

import json
import logging
from pathlib import Path

from .config import APPS_DIR, SLUG_PATTERN
from .docker_manager import DockerManager
from .models import AppMetadata

logger = logging.getLogger(__name__)


class AppService:
    """Handles app discovery and metadata resolution."""

    @staticmethod
    def _parse_app_json(app_dir: Path) -> dict | None:
        """Read and parse app.json, returning None on failure."""
        app_json = app_dir / "app.json"
        if not app_json.is_file():
            return None
        try:
            with open(app_json, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning("Failed to parse %s: %s", app_json, exc)
            return None

    @staticmethod
    def list_apps() -> list[AppMetadata]:
        """Discover all apps under APPS_DIR and return their metadata."""
        apps_path = Path(APPS_DIR)
        if not apps_path.is_dir():
            logger.warning("Apps directory does not exist: %s", APPS_DIR)
            return []

        result: list[AppMetadata] = []

        for entry in sorted(apps_path.iterdir()):
            if not entry.is_dir():
                continue

            slug = entry.name
            if not SLUG_PATTERN.match(slug):
                logger.warning("Skipping invalid app folder name: %s", slug)
                continue

            data = AppService._parse_app_json(entry)
            if data is None:
                continue

            # Ensure the slug in app.json matches the folder name
            data_slug = data.get("slug", slug)
            if data_slug != slug:
                logger.warning(
                    "Slug mismatch: folder=%s, app.json=%s — using folder name",
                    slug,
                    data_slug,
                )

            port = data.get("port", 0)
            status = DockerManager.get_status(slug)

            app = AppMetadata(
                name=data.get("name", slug),
                slug=slug,
                description=data.get("description", ""),
                github_url=data.get("github_url"),
                port=port,
                url=f"http://localhost:{port}" if port else "",
                status=status,
            )
            result.append(app)

        return result

    @staticmethod
    def get_app(slug: str) -> AppMetadata | None:
        """Fetch metadata for a single app. Returns None if not found."""
        app_dir = Path(APPS_DIR) / slug
        if not app_dir.is_dir():
            return None

        data = AppService._parse_app_json(app_dir)
        if data is None:
            return None

        port = data.get("port", 0)
        status = DockerManager.get_status(slug)

        return AppMetadata(
            name=data.get("name", slug),
            slug=slug,
            description=data.get("description", ""),
            github_url=data.get("github_url"),
            port=port,
            url=f"http://localhost:{port}" if port else "",
            status=status,
        )
