from __future__ import annotations

import os
import secrets
from pathlib import Path

from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parents[2]
PROJECT_DIR = BACKEND_DIR.parent
load_dotenv(PROJECT_DIR / ".env")


def _dataset_path() -> Path:
    raw = os.getenv("DATASET_PATH")
    if raw:
        path = Path(raw)
        return path if path.is_absolute() else (PROJECT_DIR / path).resolve()
    candidates = [PROJECT_DIR / "data" / "supplier_risk_dataset.csv",
                  PROJECT_DIR / "supplier_risk_dataset.csv"]
    return next((path for path in candidates if path.is_file()), candidates[0])


class Settings:
    dataset_path = _dataset_path()
    sqlite_path = BACKEND_DIR / "app" / "data" / "app.sqlite3"
    offline_mode = os.getenv("OFFLINE_MODE", "true").lower() in {"1", "true", "yes"}
    feed_speed_seconds = max(1, int(os.getenv("FEED_SPEED_SECONDS", "5")))
    tavily_api_key = os.getenv("TAVILY_API_KEY", "")
    llm_api_key = os.getenv("LLM_API_KEY", "")
    llm_model = os.getenv("LLM_MODEL", "")
    # In local development, ephemeral credentials keep the in-process bus usable.
    # Set both environment values to stable secrets when multiple processes are used.
    agent_api_key = os.getenv("INTERNAL_AGENT_API_KEY") or secrets.token_urlsafe(24)
    agent_secret = os.getenv("INTERNAL_AGENT_SECRET") or secrets.token_urlsafe(48)


settings = Settings()
