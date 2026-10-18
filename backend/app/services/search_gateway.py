from __future__ import annotations

import hashlib
import json
import re
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from urllib.parse import urlparse

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
        self.last_status = "not_started"

    def search(self, query: str, max_results: int = 5) -> list[dict]:
        self.last_status = "started"
        max_results = max(1, min(max_results, 10))
        cache_key = hashlib.sha256(f"{max_results}:{query.strip().lower()}".encode()).hexdigest()
        with self.store.connect() as db:
            cached = db.execute("SELECT payload, created_at FROM search_cache WHERE cache_key=?", (cache_key,)).fetchone()
        if cached:
            # SQLite CURRENT_TIMESTAMP format is UTC; age is calculated by SQLite.
            with self.store.connect() as db:
                fresh = db.execute("SELECT created_at >= datetime('now','-24 hours') FROM search_cache WHERE cache_key=?", (cache_key,)).fetchone()[0]
            if fresh or settings.offline_mode:
                self.last_status = "cached" if fresh else "stale_offline_cache"
                return json.loads(cached["payload"])[:max_results]
        if settings.offline_mode or not settings.tavily_api_key:
            self.last_status = "offline" if settings.offline_mode else "provider_not_configured"
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
            self.last_status = "provider_error"
            return []
        # Snippets are untrusted external text: keep them as plain data, never as markup or instructions.
        results = [{"title": strip_html(item.get("title", "")), "url": item.get("url", ""),
                    "content": strip_html(item.get("content", "")), "published": item.get("published_date")}
                   for item in result.get("results", []) if isinstance(item, dict) and urlparse(item.get("url", "")).scheme in {"http", "https"} and urlparse(item.get("url", "")).hostname][:max_results]
        self.last_status = "live_results" if results else "no_results"
        with self.store.connect() as db:
            db.execute("INSERT OR REPLACE INTO search_cache(cache_key,query,payload) VALUES(?,?,?)",
                       (cache_key, query, json.dumps(results)))
        return results

    def extract(self, urls: list[str]) -> dict:
        """Retrieve only selected search result URLs via Tavily; expose partial failure."""
        urls = list(dict.fromkeys(u for u in urls if urlparse(u).scheme in {'http', 'https'}))[:3]
        if not urls or settings.offline_mode or not settings.tavily_api_key:
            return {'results': [], 'failed_results': [], 'status': 'not_run'}
        request = Request('https://api.tavily.com/extract',
            data=json.dumps({'urls': urls, 'extract_depth': 'basic', 'format': 'text'}).encode(),
            headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {settings.tavily_api_key}'}, method='POST')
        try:
            with urlopen(request, timeout=20) as response:
                data = json.loads(response.read().decode())
            if not isinstance(data, dict):
                raise ValueError('Invalid provider response')
            results = [{'url': item['url'], 'content': strip_html(item.get('raw_content', ''))[:6000]}
                       for item in data.get('results', []) if isinstance(item, dict) and item.get('url') in urls]
            found = {item['url'] for item in results}
            return {'results': results, 'failed_results': [{'url': u} for u in urls if u not in found],
                    'status': 'complete' if len(found) == len(urls) else 'partial'}
        except (HTTPError, URLError, TimeoutError, ValueError, TypeError):
            return {'results': [], 'failed_results': [{'url': u} for u in urls], 'status': 'provider_error'}
