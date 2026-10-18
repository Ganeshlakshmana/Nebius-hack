from __future__ import annotations

import json
import uuid
import re
from app.config.settings import settings
from app.services.model_review import review_evidence
from app.services.research_evidence import assess, decision, official_domain, canonical_url
from app.db.sqlite_store import AppStore
from app.services.events import AgentBus
from app.services.search_gateway import SearchGateway, clean_search_term


class ResearchAgent:
    """Research job boundary; never invents sourced findings when providers are absent."""
    def __init__(self, store: AppStore, bus: AgentBus, search: SearchGateway):
        self.store, self.bus, self.search = store, bus, search

    def run(self, company: str, supplier_id: str | None = None, triggering_alert: str | None = None, component: str | None = None, domain: str | None = None) -> dict:
        company = clean_search_term(company)
        component = clean_search_term(component, 100) if component else None
        if len(company) < 2:
            raise ValueError("Company name must contain at least 2 characters after cleaning")
        domain = official_domain(domain)
        research_id = str(uuid.uuid4())
        dimensions = ["financial health and credit", "compliance and governance", "quality and safety",
                      "labor stability", "ESG", "digital security", "geopolitical and political exposure"]
        if component:
            dimensions = [f"{component} manufacturing capability product specifications", f"{component} quality recalls safety issues",
                          f"{component} certification testing approvals", f"{component} capacity delivery lifecycle support", *dimensions[:2]]
        if domain:
            dimensions = [f"site:{domain} company identity rail products", *dimensions]
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
                result["url"] = canonical_url(result["url"])
                if result["url"] in sources:
                    continue
                sources.append(result["url"])
                timeline.append({"dimension": dimension, "severity": "unassessed",
                    "summary": (result["title"] + ": " + result["content"][:500]).strip(),
                    "url": result["url"], "published": result["published"],
                    "confidence": None, "is_red_flag": False})
        # Inspect retrieved pages before deciding whether a risk word describes an event.
        initial_extraction = self.search.extract(sources[:3])
        initial_pages = {item['url']: item['content'] for item in initial_extraction['results']}
        for item in timeline:
            item['extracted_excerpt'] = initial_pages.get(item['url'], '')[:6000]
            item.update(assess(item, company, domain))
        model_review = review_evidence(company, component, timeline)
        model_candidates = {f['evidence_id'] for f in model_review['findings'] if f['classification'] == 'reported_incident'}
        candidates = [item for item in timeline if item['classification'] == 'reported_incident' or item['evidence_id'] in model_candidates][:2]
        for candidate in candidates:
            # Company-scoped follow-up; untrusted page content never becomes query instructions.
            results = self.search.search(f'"{company}" rail incident investigation official statement resolution remediation', max_results=3)
            searches += 1
            search_outcomes.append({'dimension': 'Incident follow-up', 'status': self.search.last_status, 'results': len(results)})
            for result in results:
                result['url'] = canonical_url(result['url'])
                if result['url'] not in sources:
                    sources.append(result['url'])
                    timeline.append({'dimension': 'Incident follow-up', 'severity': 'unassessed',
                        'summary': result['title']+': '+result['content'][:500], 'url': result['url'],
                        'published': result['published'], 'confidence': None, 'is_red_flag': False})
        selected_urls = list(dict.fromkeys([i['url'] for i in timeline if i['dimension'] == 'Incident follow-up'] + [i['url'] for i in candidates] + sources))[:3]
        remaining_urls = [u for u in selected_urls if u not in initial_pages]
        extraction = self.search.extract(remaining_urls) if candidates and remaining_urls else {'results': [], 'failed_results': [], 'status': 'not_run'}
        extracted = {**initial_pages, **{item['url']: item['content'] for item in extraction['results']}}
        for item in timeline:
            item['extracted_excerpt'] = extracted.get(item['url'], '')[:6000]
            item.update(assess(item, company, domain))
        configured = bool(settings.tavily_api_key) and not settings.offline_mode
        limitations = (["Evidence uses conservative rule-based triage; reported-incident candidates and severity are not independently verified."]
                       if configured else ["Configure TAVILY_API_KEY and set OFFLINE_MODE=false for live sourced research."])
        limitations.append("No results is not evidence of low risk. Company identity, publication dates and claims require verification.")
        if anonymous:
            limitations.append("Anonymized supplier IDs cannot be researched as real companies; provide a verified company identity.")
        limitations.append("Rule-based classification can miss incidents or misread context, including historic or unrelated claims. Follow-up sources do not automatically corroborate a claim.")
        failed_urls = {i["url"] for batch in (initial_extraction, extraction) for i in batch["failed_results"]} - set(extracted)
        if failed_urls:
            limitations.append(f"Could not retrieve {len(failed_urls)} selected source pages.")
        report = {"extraction_status": extraction["status"] if extraction["status"] != "not_run" else initial_extraction["status"],"search_outcomes": search_outcomes, "official_domain": domain, "identity_status": "buyer_supplied_domain" if domain else "unresolved","research_id": research_id, "company": company, "resolved_website": None,
                  "status": "partial", "executive_summary": f"Retrieved {len(timeline)} source-linked search results for {company}; rule-based evidence triage requires human verification.",
                  "scorecard": {}, "red_flags": [], "timeline": timeline, "recommendations": [],
                  "limitations": limitations, "sources": sources,
                  "budget_used": {"searches": searches, "extracts": int(initial_extraction["status"] != "not_run") + int(extraction["status"] != "not_run"), "deep_dive_rounds": int(bool(candidates))},
                  "component": component, "component_qualification": "unverified" if component else None,
                  "dataset_match": None, "requested_supplier_id": supplier_id, "triggering_alert": triggering_alert}
        report["model_review"] = model_review
        report["limitations"].append("Model findings are advisory, not verified facts. Citation and quote validation does not establish semantic accuracy. Follow-up pages are not re-reviewed by the model.")
        report["decision"] = decision(report)
        for finding in model_review["findings"]:
            report["decision"]["actions"].append({"priority": "review", "action": finding["buyer_question"], "evidence_ids": [finding["evidence_id"]]})
        report["recommendations"] = report["decision"]["actions"]
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
