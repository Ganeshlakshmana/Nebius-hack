from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any


class AppStore:
    def __init__(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.path = path
        with self.connect() as db:
            db.executescript("""
                PRAGMA journal_mode=WAL;
                CREATE TABLE IF NOT EXISTS audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    actor TEXT NOT NULL, event_type TEXT NOT NULL, payload TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS agent_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    sender TEXT NOT NULL, recipient TEXT NOT NULL, event_type TEXT NOT NULL,
                    payload TEXT NOT NULL, signature TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS ops_alerts (
                    alert_id TEXT PRIMARY KEY, supplier_id TEXT NOT NULL, metric TEXT NOT NULL,
                    baseline REAL NOT NULL, current REAL NOT NULL, drift_z REAL NOT NULL,
                    days_persisting INTEGER NOT NULL, spend_at_risk_eur REAL NOT NULL,
                    sourcing_risk_level TEXT NOT NULL, severity TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'open', source TEXT NOT NULL DEFAULT 'simulated_feed',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS live_metrics (
                    supplier_id TEXT PRIMARY KEY, payload TEXT NOT NULL,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS research_reports (
                    research_id TEXT PRIMARY KEY, status TEXT NOT NULL, payload TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS signals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, supplier_id TEXT NOT NULL,
                    payload TEXT NOT NULL, created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS search_cache (
                    cache_key TEXT PRIMARY KEY, query TEXT NOT NULL, payload TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );
            """)

    def connect(self) -> sqlite3.Connection:
        db = sqlite3.connect(self.path, timeout=10)
        db.row_factory = sqlite3.Row
        return db

    def audit(self, actor: str, event_type: str, payload: dict[str, Any]) -> None:
        with self.connect() as db:
            db.execute("INSERT INTO audit_log(actor,event_type,payload) VALUES(?,?,?)",
                       (actor, event_type, json.dumps(payload, default=str)))

    def save_message(self, sender: str, recipient: str, event_type: str,
                     payload: dict[str, Any], signature: str) -> None:
        with self.connect() as db:
            db.execute("INSERT INTO agent_messages(sender,recipient,event_type,payload,signature) VALUES(?,?,?,?,?)",
                       (sender, recipient, event_type, json.dumps(payload, default=str), signature))

    def get_alerts(self, supplier_ids: list[str] | None = None) -> list[dict[str, Any]]:
        with self.connect() as db:
            if supplier_ids:
                marks = ",".join("?" for _ in supplier_ids)
                rows = db.execute(f"SELECT * FROM ops_alerts WHERE supplier_id IN ({marks}) ORDER BY created_at DESC", supplier_ids).fetchall()
            else:
                rows = db.execute("SELECT * FROM ops_alerts ORDER BY created_at DESC LIMIT 500").fetchall()
        return [dict(row) for row in rows]
