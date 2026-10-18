# Memo agent - Guardrails

_Code: `agents/memos/agent.py`_  
_Status: Implemented (HTML memo with input validation). Narrative text generation is not LLM-based yet._

Hard limits and safety controls. 'Planned' and 'Gap' items are not enforced yet.

## Agent-specific guardrails

| Guardrail | Control | Status |
|---|---|---|
| HTML escaping | All interpolated values are escaped (XSS protection). | Implemented |
| Input bounds | Between 1 and 20 IDs, otherwise 422. | Implemented |
| Download only | Served as an attachment (`Content-Disposition`). | Implemented |
| Unknown IDs | Any ID not in the dataset -> HTTP 422; no partial memo. | Implemented |
| Chosen supplier | `chosen` must be one of `ids`, otherwise 422. | Implemented |
| Body schema | `MemoRequest` (Pydantic): 1-20 IDs, `chosen` <= 20 chars, `note` <= 2000 chars. | Implemented |
| Audit | Each memo is audited (`memo_generated`). | Implemented |

## Platform guardrails that apply to this agent

| Guardrail | Control | Status |
|---|---|---|
| Immutable dataset | The CSV is opened read-only in DuckDB; overlays live in SQLite. | Implemented |
| Secrets from environment only | `INTERNAL_AGENT_API_KEY`, `INTERNAL_AGENT_SECRET`, `TAVILY_API_KEY`, `LLM_API_KEY` come from env; `.env` is git-ignored; never returned by an endpoint. | Implemented |
| Audit log | Agent actions are written to the SQLite audit table. | Implemented |
| Parameterised SQL | Bound parameters; sort columns from an allow-list. | Implemented |
| CORS | Only the local frontend origins (ports 3000 and 5173) may call the API from a browser. | Implemented |
| User authentication | No user login on the public API (`require_agent_key` is only for future cross-process agent calls). | Gap: required before any non-local deployment |
| Rate limiting | No request rate limits. | Gap |
