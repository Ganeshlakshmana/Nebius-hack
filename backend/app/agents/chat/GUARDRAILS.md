# Chat agent - Guardrails

_Code: `agents/chat/agent.py`, `services/component_risk.py`, `services/data_tools.py`_  
_Status: Implemented. Deterministic router with a supplier-ID validator (no LLM call yet); LLM phrasing is the planned next step._

Hard limits and safety controls. 'Planned' and 'Gap' items are not enforced yet.

## Agent-specific guardrails

| Guardrail | Control | Status |
|---|---|---|
| Grounding | Every figure comes from a tool call; response carries `tool_calls` and `provenance`. | Implemented (by construction: no free text generation) |
| Input bounds | `message` 1-2000 chars, <= 20 supplier IDs, component 2-100 chars (Pydantic). | Implemented |
| Parameterised SQL | IDs/filters are bound parameters; sort columns come from an allow-list. | Implemented |
| Unknown IDs | Component analysis refuses partial rankings when any ID is unknown (HTTP 422). | Implemented |
| No qualification claims | `qualification_status` is always `unverified`; weights labelled illustrative, not Siemens-approved. | Implemented |
| Answer validator (supplier IDs) | `ChatAgent.unsupported_ids`: every `SUPP_#####` in the answer must appear in this turn's tool output, otherwise `validated: false` plus `validation_errors`. | Implemented |
| Answer validator (numbers) | Re-check every number in an LLM-phrased answer against tool output; fall back to the template answer on mismatch. | Planned (with the LLM step) |
| Prompt-injection hygiene | Supplier names / search snippets are data; never concatenated into instructions. | Planned with the LLM step |
| Audit | Each answer is written to the audit log (`chat_answer`, tool_calls, validated). | Implemented |

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

## Trust update
Unknown IDs never produce partial chat rankings. Research/news severity is `unassessed`; uncalibrated numeric research confidence is omitted (`null`). Research uses bounded keyword-triggered follow-up and up to three page extractions; potential concerns are not verified findings. See `docs/challenge-readiness.md` for limits.
