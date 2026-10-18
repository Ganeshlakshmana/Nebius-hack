# Chat agent - Guardrails

_Code: `agents/chat/agent.py`, `services/component_risk.py`, `services/data_tools.py`_  
_Status: Implemented. Deterministic router (no LLM call yet); LLM phrasing is the planned next step._

Hard limits and safety controls. 'Planned' items are not enforced yet.

| Guardrail | Control | Status |
|---|---|---|
| Grounding | Every figure comes from a tool call; response carries `tool_calls` and `provenance`. | Implemented (by construction: no free text generation) |
| Input bounds | `message` 1-2000 chars, <= 20 supplier IDs, component 2-100 chars (Pydantic). | Implemented |
| Parameterised SQL | IDs/filters are bound parameters; sort columns come from an allow-list. | Implemented |
| Unknown IDs | Component analysis refuses partial rankings when any ID is unknown (HTTP 422). | Implemented |
| No qualification claims | `qualification_status` is always `unverified`; weights labelled illustrative, not Siemens-approved. | Implemented |
| Answer validator | Re-check every number in an LLM-phrased answer against tool output; fall back to the template answer on mismatch. | Planned (`validated` is currently always true because answers are templated) |
| Prompt-injection hygiene | Supplier names / search snippets are data; never concatenated into instructions. | Planned with the LLM step |
| Audit | Each answer is written to the audit log (`chat_answer`, tool_calls, validated). | Implemented |
