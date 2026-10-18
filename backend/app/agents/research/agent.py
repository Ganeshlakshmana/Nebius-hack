from __future__ import annotations

import json
import uuid
from app.config.settings import settings
from app.db.sqlite_store import AppStore
from app.services.events import AgentBus
from app.services.search_gateway import SearchGateway


class ResearchAgent:
    """Research job boundary; never invents sourced findings when providers are absent."""
    def __init__(self, store: AppStore, bus: AgentBus, search: SearchGateway):
        self.store, self.bus, self.search = store, bus, search

    def run(self, company: str, supplier_id: str | None = None, triggering_alert: str | None = None, component: str | None = None) -> dict:
        research_id = str(uuid.uuid4())
        dimensions = ["financial health and credit", "compliance and governance", "quality and safety",
                      "labor stability", "ESG", "digital security", "geopolitical and political exposure"]
        if component:
            dimensions = [f"{component} manufacturing capability product specifications", f"{component} quality recalls safety issues",
                          f"{component} certification testing approvals", f"{component} capacity delivery lifecycle support", *dimensions[:2]]
        timeline, sources = [], []
        searches = 0
        for dimension in dimensions:
            if searches >= 15:
                break
            self.bus.send("research", "news", "research_search_started",
                          {"research_id": research_id, "dimension": dimension})
            results = self.search.search(f'"{company}" supplier {dimension}', max_results=3)
            searches += 1
            for result in results:
                if result["url"] in sources:
                    continue
                sources.append(result["url"])
                timeline.append({"dimension": dimension, "severity": "low",
                    "summary": (result["title"] + ": " + result["content"][:500]).strip(),
                    "url": result["url"], "published": result["published"],
                    "confidence": 0.35, "is_red_flag": False})
        configured = bool(settings.tavily_api_key) and not settings.offline_mode
        limitations = (["Retrieved search snippets are source-linked but not yet triaged by an LLM; severity is not a validated risk judgement."]
                       if configured else ["Configure TAVILY_API_KEY and set OFFLINE_MODE=false for live sourced research."])
        report = {"research_id": research_id, "company": company, "resolved_website": None,
                  "status": "partial", "executive_summary": f"Retrieved {len(timeline)} source-linked search results for {company}; automated risk triage is not enabled.",
                  "scorecard": {}, "red_flags": [], "timeline": timeline, "recommendations": [],
                  "limitations": limitations, "sources": sources,
                  "budget_used": {"searches": searches, "extracts": 0, "deep_dive_rounds": 0},
                  "component": component, "component_qualification": "unverified" if component else None,
                  "dataset_match": supplier_id, "triggering_alert": triggering_alert}
        if component:
            report["limitations"].append("Search results do not establish component qualification or link this real company to an anonymized supplier.")
        self.store.audit("research", "research_started", {"research_id": research_id, "company": company})
        self.store.audit("research", "research_completed", {"research_id": research_id, "status": report["status"]})
        with self.store.connect() as db:
            db.execute("INSERT INTO research_reports(research_id,status,payload) VALUES(?,?,?)",
                       (research_id, report["status"], json.dumps(report)))
        return report

    def get(self, research_id: str) -> dict | None:
        with self.store.connect() as db:
            row = db.execute("SELECT payload FROM research_reports WHERE research_id=?", (research_id,)).fetchone()
        return json.loads(row["payload"]) if row else None
