# Research agent - Context

_Code: `agents/research/agent.py`, `services/search_gateway.py`, `services/events.py`_  
_Status: Partially implemented. Budgeted multi-dimension search with source links; triage, scorecard and recommendations are not generated yet (`status: partial`)._

What the agent knows, reads and is wired to.

- Serves `POST /research` (`company` 2-200 chars, optional `supplier_id`, optional `component`), `GET /research/{id}`, `GET /research/{id}/events`.
- Searches 7 default dimensions (financial, compliance/governance, quality/safety, labor, ESG, digital security, geopolitical); with a `component` it searches capability, recalls/safety, certification and capacity first.
- Budget: at most 15 searches per report, 0 extracts, 0 deep-dive rounds (recorded in `budget_used`).
- Reports are stored in `research_reports`; progress is announced on the signed `AgentBus`.
- Can be triggered by a high/critical live-orders alert (`triggering_alert`).
