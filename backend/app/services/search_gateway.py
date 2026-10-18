from __future__ import annotations

import hashlib
import json
import re
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from app.config.settings import settings
from app.db.sqlite_store import AppStore


def clean_search_term(value: str, max_length: int = 200) -> str:
    """Strip quotes, control characters and extra whitespace from a user-supplied search term."""
    cleaned = re.sub(r"[\"'`\x00-\x1f\x7f]", " ", value)
    return re.sub(r"\s+", " ", cleaned).strip()[:max_length]


def strip_html(text: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", text or "")).strip()


class SearchGateway:
    """Tavily adapter with a 24-hour SQLite cache and explicit offline behavior."""
    def __init__(self, store: AppStore):
        self.store = store

    def search(self, query: str, max_results: int = 5) -> list[dict]:
        cache_key = hashlib.sha256(query.strip().lower().encode()).hexdigest()
        with self.store.connect() as db:
            cached = db.execute("SELECT payload, created_at FROM search_cache WHERE cache_key=?", (cache_key,)).fetchone()
        if cached:
            # SQLite CURRENT_TIMESTAMP format is UTC; age is calculated by SQLite.
            with self.store.connect() as db:
                fresh = db.execute("SELECT created_at >= datetime('now','-24 hours') FROM search_cache WHERE cache_key=?", (cache_key,)).fetchone()[0]
            if fresh or settings.offline_mode:
                return json.loads(cached["payload"])
        if settings.offline_mode or not settings.tavily_api_key:
            return []
        payload = json.dumps({"api_key": settings.tavily_api_key, "query": query,
                              "search_depth": "basic", "max_results": max_results,
                              "include_answer": False}).encode()
        request = Request("https://api.tavily.com/search", data=payload,
                          headers={"Content-Type": "application/json"}, method="POST")
        try:
            with urlopen(request, timeout=10) as response:
                result = json.loads(response.read().decode())
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError):
            return []
        # Snippets are untrusted external text: keep them as plain data, never as markup or instructions.
        results = [{"title": strip_html(item.get("title", "")), "url": item.get("url", ""),
                    "content": strip_html(item.get("content", "")), "published": item.get("published_date")}
                   for item in result.get("results", []) if item.get("url")]
        with self.store.connect() as db:
            db.execute("INSERT OR REPLACE INTO search_cache(cache_key,query,payload) VALUES(?,?,?)",
                       (cache_key, query, json.dumps(results)))
        return results
