from __future__ import annotations

from fastapi import Header, HTTPException
from app.config.settings import settings


def require_agent_key(x_agent_api_key: str | None = Header(default=None)) -> None:
    """Dependency for any future cross-process agent-to-agent HTTP endpoint."""
    if not x_agent_api_key or x_agent_api_key != settings.agent_api_key:
        raise HTTPException(status_code=401, detail="Invalid internal agent API key")
