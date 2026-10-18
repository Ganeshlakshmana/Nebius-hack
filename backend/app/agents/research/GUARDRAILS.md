# Research agent - Guardrails

_Code: `agents/research/agent.py`, `services/search_gateway.py`, `services/events.py`_  
_Status: Partially implemented. Budgeted multi-dimension search with source links; triage, scorecard and recommendations are not generated yet (`status: partial`)._

Hard limits and safety controls. 'Planned' and 'Gap' items are not enforced yet.

## Agent-specific guardrails

| Guardrail | Control | Status |
|---|---|---|
| Search budget | Hard cap of 15 searches; URL de-duplication. | Implemented |
| No invented findings | Timeline is built only from returned results; empty when offline. | Implemented |
| Offline default | `OFFLINE_MODE=true` blocks live calls; cached results only. | Implemented |
| Qualification honesty | Component reports are labelled `component_qualification: unverified`. | Implemented |
| Signed hand-offs | Inter-agent messages are HMAC-SHA256 signed and audited. | Implemented |
| Company name validation | `clean_search_term` cleans `company` (and `component`); a name shorter than 2 characters after cleaning -> HTTP 422. | Implemented |
| Triage safety | Red flag requires corroboration; severity from a model must cite the supporting URL. | Planned |
| Untrusted content | Snippet HTML stripped by the gateway before it reaches the timeline. | Implemented |
| Prompt-injection defence | Page/snippet text processed in an isolated extraction step with a fixed schema output. | Planned (with triage) |
| Per-user rate limit | Limit concurrent and daily research jobs. | Planned |

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
