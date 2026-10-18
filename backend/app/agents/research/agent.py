from __future__ import annotations

import json
import uuid
import re
from app.config.settings import settings
from app.db.sqlite_store import AppStore
from app.services.events import AgentBus
from app.services.search_gateway import SearchGateway, clean_search_term


class ResearchAgent:
    """Research job boundary; never invents sourced findings when providers are absent."""
    def __init__(self, store: AppStore, bus: AgentBus, search: SearchGateway):
        self.store, self.bus, self.search = store, bus, search

    def run(self, company: str, supplier_id: str | None = None, triggering_alert: str | None = None, component: str | None = None) -> dict:
        company = clean_search_term(company)
        component = clean_search_term(component, 100) if component else None
        if len(company) < 2:
            raise ValueError("Company name must contain at least 2 characters after cleaning")
        research_id = str(uuid.uuid4())
        dimensions = ["financial health and credit", "compliance and governance", "quality and safety",
                      "labor stability", "ESG", "digital security", "geopolitical and political exposure"]
        if component:
            dimensions = [f"{component} manufacturing capability product specifications", f"{component} quality recalls safety issues",
                          f"{component} certification testing approvals", f"{component} capacity delivery lifecycle support", *dimensions[:2]]
        timeline, sources, search_outcomes = [], [], []
        anonymous = bool(re.fullmatch(r"SUPP_\d{5}", company, re.IGNORECASE))
        searches = 0
        for dimension in dimensions:
            if searches >= 15:
                break
            self.bus.send("research", "news", "research_search_started",
                          {"research_id": research_id, "dimension": dimension})
            results = [] if anonymous else self.search.search(f'"{company}" rail railway {dimension}', max_results=3)
            search_outcomes.append({"dimension": dimension, "status": "anonymous_identity_unresolved" if anonymous else self.search.last_status, "results": len(results)})
            searches += 1
            for result in results:
                if result["url"] in sources:
                    continue
                sources.append(result["url"])
                timeline.append({"dimension": dimension, "severity": "unassessed",
                    "summary": (result["title"] + ": " + result["content"][:500]).strip(),
                    "url": result["url"], "published": result["published"],
                    "confidence": None, "is_red_flag": False})
        # Deterministic investigation policy: a term triggers follow-up, never a factual risk verdict.
        concern_terms = ('recall', 'bankruptcy', 'insolvency', 'lawsuit', 'breach', 'sanction')
        for item in timeline:
            item['potential_concern'] = any(re.search(r'\b'+term+r'\b', item['summary'], re.I) for term in concern_terms)
        candidates = [item for item in timeline if item['potential_concern']][:2]
        for candidate in candidates:
            term = next(term for term in concern_terms if re.search(r'\b'+term+r'\b', candidate['summary'], re.I))
            results = self.search.search(f'"{company}" {term} official statement investigation resolution', max_results=3)
            searches += 1
            search_outcomes.append({'dimension': f'Follow-up: {term}', 'status': self.search.last_status, 'results': len(results)})
            for result in results:
                if result['url'] not in sources:
                    sources.append(result['url'])
                    timeline.append({'dimension': f'Follow-up: {term}', 'severity': 'unassessed',
                        'summary': result['title']+': '+result['content'][:500], 'url': result['url'],
                        'published': result['published'], 'confidence': None, 'is_red_flag': False, 'potential_concern': False})
        selected_urls = list(dict.fromkeys([i['url'] for i in candidates] + sources))[:3]
        extraction = self.search.extract(selected_urls)
        extracted = {item['url']: item['content'] for item in extraction['results']}
        for item in timeline:
            item['extracted_excerpt'] = extracted.get(item['url'], '')[:1200]
        configured = bool(settings.tavily_api_key) and not settings.offline_mode
        limitations = (["Retrieved search snippets are source-linked but not yet triaged by an LLM; severity is not a validated risk judgement."]
                       if configured else ["Configure TAVILY_API_KEY and set OFFLINE_MODE=false for live sourced research."])
        limitations.append("No results is not evidence of low risk. Company identity, publication dates and claims require verification.")
        if anonymous:
            limitations.append("Anonymized supplier IDs cannot be researched as real companies; provide a verified company identity.")
        limitations.append("Investigation triggers use keyword matching, which may include negated, historic or unrelated claims. Follow-up sources do not automatically corroborate a claim.")
        if extraction["failed_results"]:
            limitations.append(f"Could not retrieve {len(extraction['failed_results'])} selected source pages.")
        report = {"extraction_status": extraction["status"],"search_outcomes": search_outcomes, "identity_status": "unresolved","research_id": research_id, "company": company, "resolved_website": None,
                  "status": "partial", "executive_summary": f"Retrieved {len(timeline)} source-linked search results for {company}; automated risk triage is not enabled.",
                  "scorecard": {}, "red_flags": [], "timeline": timeline, "recommendations": [],
                  "limitations": limitations, "sources": sources,
                  "budget_used": {"searches": searches, "extracts": int(extraction["status"] != "not_run"), "deep_dive_rounds": int(bool(candidates))},
                  "component": component, "component_qualification": "unverified" if component else None,
                  "dataset_match": None, "requested_supplier_id": supplier_id, "triggering_alert": triggering_alert}
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
