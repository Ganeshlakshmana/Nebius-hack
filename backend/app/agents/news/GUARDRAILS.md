# News signals agent - Guardrails

_Code: `agents/news/agent.py`, `services/search_gateway.py`_  
_Status: Partially implemented. Retrieves source-linked results; no LLM triage, so all signals are `unreviewed`._

Hard limits and safety controls. 'Planned' items are not enforced yet.

| Guardrail | Control | Status |
|---|---|---|
| No fabrication | Without provider or in offline mode the agent returns empty signals and a status. | Implemented |
| Score separation | Signals never modify `Total_Risk_Index` or any dataset field. | Implemented |
| Source linking | Only results with a URL are kept (gateway filter). | Implemented |
| Cost control | 24-hour cache; `basic` search depth; 10 s timeout; failures return empty list. | Implemented |
| Query safety | Company string is quoted into the query; strip quotes/newlines and cap length before use. | Planned (length capped only at the research endpoint) |
| Triage | LLM or rules classify dimension/severity with confidence and a red-flag rule requiring >= 2 sources or a high-reliability source. | Planned |
| Untrusted content | Snippets are treated as data; strip HTML; never pass to a model as instructions. | Planned with triage |
