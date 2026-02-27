"""
REST API routes for the Home Server Orchestrator controller.
"""

import logging
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from .config import APPS_DIR, SLUG_PATTERN
from .docker_manager import DockerManager
from .app_service import AppService
from .models import AppMetadata, ActionResponse

logger = logging.getLogger(__name__)
router = APIRouter()


def _validate_slug(app_slug: str) -> None:
    """Raise 400 if slug is invalid, 404 if app folder doesn't exist."""
    if not SLUG_PATTERN.match(app_slug):
        raise HTTPException(status_code=400, detail="Invalid app slug")
    app_dir = Path(APPS_DIR) / app_slug
    if not app_dir.is_dir():
        raise HTTPException(status_code=404, detail=f"App '{app_slug}' not found")


# ──────────────────────────── List apps ────────────────────────────


@router.get("/apps", response_model=list[AppMetadata])
async def list_apps():
    """Return metadata + live status for every discovered app."""
    return AppService.list_apps()


# ──────────────────────────── Start app ────────────────────────────


@router.post("/apps/{app_slug}/start", response_model=ActionResponse)
async def start_app(app_slug: str):
    """Run docker compose up -d for the given app."""
    _validate_slug(app_slug)

    success, message = DockerManager.compose_up(app_slug)
    if not success:
        raise HTTPException(status_code=500, detail=message)

    return ActionResponse(status="ok", app=app_slug, message=message)


# ──────────────────────────── Stop app ─────────────────────────────


@router.post("/apps/{app_slug}/stop", response_model=ActionResponse)
async def stop_app(app_slug: str):
    """Run docker compose down for the given app."""
    _validate_slug(app_slug)

    success, message = DockerManager.compose_down(app_slug)
    if not success:
        raise HTTPException(status_code=500, detail=message)

    return ActionResponse(status="ok", app=app_slug, message=message)


# ──────────────────────────── App icon ─────────────────────────────

# Minimal 1x1 transparent PNG (fallback when app.png is missing)
_FALLBACK_PNG = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
    b"\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89"
    b"\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01"
    b"\r\n\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
)


@router.get("/apps/{app_slug}/icon")
async def get_app_icon(app_slug: str):
    """Serve the app's icon image (app.png), or a transparent fallback."""
    _validate_slug(app_slug)

    icon_path = Path(APPS_DIR) / app_slug / "app.png"
    if icon_path.is_file():
        return FileResponse(str(icon_path), media_type="image/png")

    # Return a minimal transparent PNG so the UI never gets a broken image
    from fastapi.responses import Response

    return Response(content=_FALLBACK_PNG, media_type="image/png")
