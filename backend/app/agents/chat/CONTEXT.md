# Chat agent - Context

_Code: `agents/chat/agent.py`, `services/component_risk.py`, `services/data_tools.py`_  
_Status: Implemented. Deterministic router with a supplier-ID validator (no LLM call yet); LLM phrasing is the planned next step._

What the agent knows, reads and is wired to.

- Serves `POST /chat` (message <= 2000 chars, <= 20 `supplier_ids`, optional `component`) and the frontend proxy `app/api/chat/route.ts`.
- Reads the immutable 10,000-supplier dataset through `DataTools` (DuckDB, read-only view) and the TRI weight explainer (`ScoreExplainer`).
- Routing today: component keywords/`component` field -> `ComponentRisk.chat_answer`; >1 supplier ID -> ranking table; 1 ID with why/explain/risk -> score explanation; 1 ID otherwise -> supplier card; no ID -> top-10 highest-TRI suppliers.
- Supplier IDs come from the message (`SUPP_#####`) or, if none, from the user's shortlist.
- Returns `{answer, components[], tool_calls[], validated, provenance}`; the UI renders `components` (ranking_table, contribution_bars, supplier_card, component_risk).
