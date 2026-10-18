# Scenario (alternatives) agent - Guardrails

_Code: `agents/scenarios/agent.py`, `services/data_tools.py::alternatives`_  
_Status: Implemented (nearest-profile alternatives). Custom-weight re-ranking lives in `/compare`._

Hard limits and safety controls. 'Planned' and 'Gap' items are not enforced yet.

## Agent-specific guardrails

| Guardrail | Control | Status |
|---|---|---|
| Bounded input | `limit` 1-20 (Pydantic). | Implemented |
| Unknown supplier | 404 with message; no partial result. | Implemented |
| Transparent method | Distance formula and dataset columns returned in `provenance`. | Implemented |
| Capability honesty | `matching_note` states component category is not in the data. | Implemented |
| Exclude alerted suppliers | `exclude_alerted: true` on `/scenarios/what-if` drops suppliers with an open operations alert. | Implemented |
| Component filter | Use component screening scores when a component is selected. | Planned |

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
