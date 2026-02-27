from pydantic import BaseModel
from typing import Optional


class AppMetadata(BaseModel):
    """Represents a managed application and its current state."""

    name: str
    slug: str
    description: str = ""
    github_url: Optional[str] = None
    port: int
    url: str = ""
    status: str = "stopped"  # running | stopped | partial


class ActionResponse(BaseModel):
    """Standard response for start/stop actions."""

    status: str  # ok | error
    app: str
    message: str
