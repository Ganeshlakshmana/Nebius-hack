# Live Orders agent - Guardrails

_Code: `agents/live_orders/agent.py`_  
_Status: Implemented as a deterministic simulated feed (one demo scenario). A continuous generator is planned._

Hard limits and safety controls. 'Planned' and 'Gap' items are not enforced yet.

## Agent-specific guardrails

| Guardrail | Control | Status |
|---|---|---|
| Immutable history | Overlay lives in SQLite; DuckDB view is read-only. | Implemented |
| Simulation labelling | `source: simulated_feed` on status, alert and scenario responses. | Implemented |
| Bounded values | Simulated delivery rating floored at 5.0; live operational score clamped to 0-100. | Implemented |
| Reset | `reset` deletes only `source='simulated_feed'` alerts and all overlay metrics. | Implemented |
| Unknown supplier | Unknown ID -> HTTP 404, no alert written. | Implemented |
| Alert dedupe | One open simulated alert per supplier and metric; a repeat start returns the existing alert with `deduplicated: true`. | Implemented |
| Alert rate cap | Cap new alerts per minute once a continuous feed exists. | Planned |
| Real-data boundary | A real ERP feed must use a different `source` value and never reuse `simulated_feed`. | Planned (production path) |

## Platform guardrails that apply to this agent

| Guardrail | Control | Status |
|---|---|---|
| Immutable dataset | The CSV is opened read-only in DuckDB; overlays live in SQLite. | Implemented |
| Secrets from environment only | `INTERNAL_AGENT_API_KEY`, `INTERNAL_AGENT_SECRET`, `TAVILY_API_KEY`, `LLM_API_KEY` come from env; `.env` is git-ignored; never returned by an endpoint. | Implemented |
| Signed hand-offs | Messages on the `AgentBus` are HMAC-SHA256 signed with a key id; a bad signature or key raises `PermissionError`; each hand-off is audited. | Implemented |
| Audit log | Agent actions are written to the SQLite audit table. | Implemented |
| Parameterised SQL | Bound parameters; sort columns from an allow-list. | Implemented |
| CORS | Only the local frontend origins (ports 3000 and 5173) may call the API from a browser. | Implemented |
| User authentication | No user login on the public API (`require_agent_key` is only for future cross-process agent calls). | Gap: required before any non-local deployment |
| Rate limiting | No request rate limits. | Gap |
