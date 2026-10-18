# Research agent - Guardrails

_Code: `agents/research/agent.py`, `services/search_gateway.py`, `services/events.py`_  
_Status: Partially implemented. Budgeted multi-dimension search with source links; triage, scorecard and recommendations are not generated yet (`status: partial`)._

Hard limits and safety controls. 'Planned' items are not enforced yet.

| Guardrail | Control | Status |
|---|---|---|
| Search budget | Hard cap of 15 searches; URL de-duplication. | Implemented |
| No invented findings | Timeline is built only from returned results; empty when offline. | Implemented |
| Offline default | `OFFLINE_MODE=true` blocks live calls; cached results only. | Implemented |
| Qualification honesty | Component reports are labelled `component_qualification: unverified`. | Implemented |
| Signed hand-offs | Inter-agent messages are HMAC-SHA256 signed and audited. | Implemented |
| Company name validation | Reject control characters/quotes, normalise whitespace before building queries. | Planned |
| Triage safety | Red flag requires corroboration; severity from a model must cite the supporting URL. | Planned |
| Prompt-injection defence | Page/snippet text processed in an isolated extraction step with a fixed schema output. | Planned |
| Per-user rate limit | Limit concurrent and daily research jobs. | Planned |
