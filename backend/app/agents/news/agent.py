from __future__ import annotations

import json

from app.config.settings import settings
from app.db.sqlite_store import AppStore
from app.services.search_gateway import SearchGateway, clean_search_term


class NewsAgent:
    def __init__(self, store: AppStore, search: SearchGateway):
        self.store, self.search = store, search

    def check(self, supplier_id: str, company: str | None = None) -> dict:
        # An anonymised ID is not treated as a real company name.
        company = clean_search_term(company) if company else None
        query_target = company or supplier_id
        items = self.search.search(f'"{query_target}" recent supplier risk news', max_results=5) if company else []
        signals = [{"dimension": "unclassified", "severity": "unassessed", "summary": item["title"],
                    "url": item["url"], "published": item["published"], "triage_status": "unreviewed"}
                   for item in items]
        result = {"supplier_id": supplier_id, "company": company, "signals": signals,
                  "status": "unreviewed_results" if signals else ("provider_not_configured" if not settings.tavily_api_key or settings.offline_mode else "no_results"),
                  "source": "external_search", "limitations": ["Search results are unreviewed and do not change dataset scores."]}
        for signal in signals:
            with self.store.connect() as db:
                db.execute("INSERT INTO signals(supplier_id,payload) VALUES(?,?)", (supplier_id, json.dumps(signal)))
        self.store.audit("news", "news_check", result)
        return result
