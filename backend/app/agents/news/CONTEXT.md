# News signals agent - Context

_Code: `agents/news/agent.py`, `services/search_gateway.py`_  
_Status: Partially implemented. Retrieves source-linked results; no LLM triage, so all signals are `unreviewed`._

What the agent knows, reads and is wired to.

- Serves `GET /signals/{supplier_id}` and is called by the scenario hand-off.
- Dataset suppliers are anonymised (`SUPP_#####`), so searching is only attempted when a real `company` name is supplied; otherwise the result is empty with a status.
- Search goes through `SearchGateway` (Tavily adapter, 24-hour SQLite cache, offline mode by default).
- Signals are stored in the `signals` table and audited.
