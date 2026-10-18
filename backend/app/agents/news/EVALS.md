# News signals agent - Evals

_Code: `agents/news/agent.py`, `services/search_gateway.py`_  
_Status: Partially implemented. Retrieves source-linked results; no LLM triage, so all signals are `unreviewed`._

How we measure whether the agent is right. Run existing tests with `python -m pytest backend/tests -q`.

## Existing automated checks

| Test | Verifies |
|---|---|
| None yet | The news agent runs inside `test_simulated_ops_and_agent_handoffs`, but its output is not asserted |

## Planned evals

- Offline contract test: `GET /signals/{id}` returns `provider_not_configured`, empty `signals`, and a limitation.
- Gateway test with a stubbed Tavily response: results without URLs are dropped; cache hit avoids a second call.
- Triage set (once built): 50 labelled snippets, target >= 85% dimension accuracy and no red flag from a single weak source.
- Injection set: snippet text containing instructions must not alter output fields.

## Targets

| Metric | Target |
|---|---|
| Fabricated findings | 0 |
| Signals with URL | 100% |
| Triage dimension accuracy | >= 85% (when built) |
