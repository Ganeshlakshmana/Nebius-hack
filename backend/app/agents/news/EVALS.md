# News signals agent - Evals

_Code: `agents/news/agent.py`, `services/search_gateway.py`_  
_Status: Partially implemented. Retrieves source-linked results; no LLM triage, so all signals are `unreviewed`._

How we measure whether the agent is right. Run existing tests with `python -m pytest backend/tests -q`.

## Existing automated checks

| Test | Verifies |
|---|---|
| `tests/test_guardrails.py::test_news_offline_returns_status_not_findings` | Offline: empty signals, a status and limitations; unknown supplier -> 404 |
| `tests/test_guardrails.py::test_search_terms_and_snippets_are_sanitised` | Quotes/control characters removed, 200-char cap, HTML stripped |

## Planned evals

- Gateway test with a stubbed Tavily response: results without URLs are dropped; cache hit avoids a second call.
- Triage set (once built): 50 labelled snippets, target >= 85% dimension accuracy and no red flag from a single weak source.
- Injection set: snippet text containing instructions must not alter output fields.

## Targets

| Metric | Target |
|---|---|
| Fabricated findings | 0 |
| Signals with URL | 100% |
| Triage dimension accuracy | >= 85% (when built) |
