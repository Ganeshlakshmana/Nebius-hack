# News signals agent - Guardrails

_Code: `agents/news/agent.py`, `services/search_gateway.py`_  
_Status: Partially implemented. Retrieves source-linked results; no LLM triage, so all signals are `unreviewed`._

Hard limits and safety controls. 'Planned' and 'Gap' items are not enforced yet.

## Agent-specific guardrails

| Guardrail | Control | Status |
|---|---|---|
| No fabrication | Without provider or in offline mode the agent returns empty signals and a status. | Implemented |
| Score separation | Signals never modify `Total_Risk_Index` or any dataset field. | Implemented |
| Source linking | Only results with a URL are kept (gateway filter). | Implemented |
| Cost control | 24-hour cache; `basic` search depth; 10 s timeout; failures return empty list. | Implemented |
| Query safety | `clean_search_term` strips quotes, backticks and control characters, collapses whitespace and caps the company name at 200 characters before it is put in a query. | Implemented |
| Triage | LLM or rules classify dimension/severity with confidence and a red-flag rule requiring >= 2 sources or a high-reliability source. | Planned |
| Untrusted content | `strip_html` removes markup from titles and snippets in the gateway; snippets are stored as data only. | Implemented |
| Instruction isolation | When triage uses a model, snippets go in a data field with a fixed output schema, never in the instructions. | Planned with triage |

## Platform guardrails that apply to this agent

| Guardrail | Control | Status |
|---|---|---|
| Immutable dataset | The CSV is opened read-only in DuckDB; overlays live in SQLite. | Implemented |
| Secrets from environment only | `INTERNAL_AGENT_API_KEY`, `INTERNAL_AGENT_SECRET`, `TAVILY_API_KEY`, `LLM_API_KEY` come from env; `.env` is git-ignored; never returned by an endpoint. | Implemented |
| Signed hand-offs | Messages on the `AgentBus` are HMAC-SHA256 signed with a key id; a bad signature or key raises `PermissionError`; each hand-off is audited. | Implemented |
| Audit log | Agent actions are written to the SQLite audit table. | Implemented |
| Offline-by-default external calls | `OFFLINE_MODE=true` by default; 24 h cache; 10 s timeout; failures return empty results. | Implemented |
| CORS | Only the local frontend origins (ports 3000 and 5173) may call the API from a browser. | Implemented |
| User authentication | No user login on the public API (`require_agent_key` is only for future cross-process agent calls). | Gap: required before any non-local deployment |
| Rate limiting | No request rate limits. | Gap |
