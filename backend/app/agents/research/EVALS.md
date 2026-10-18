# Research agent - Evals

_Code: `agents/research/agent.py`, `services/search_gateway.py`, `services/events.py`_  
_Status: Partially implemented. Budgeted multi-dimension search with source links; triage, scorecard and recommendations are not generated yet (`status: partial`)._

How we measure whether the agent is right. Run existing tests with `python -m pytest backend/tests -q`.

## Existing automated checks

| Test | Verifies |
|---|---|
| `tests/test_components.py::test_component_research_queries` | Component research adds component-specific queries, `component_qualification: unverified`, and an empty scorecard |
| `tests/test_api.py::test_simulated_ops_and_agent_handoffs` | Alert-triggered research returns `status: partial` |
| `tests/test_guardrails.py::test_research_rejects_company_name_empty_after_cleaning` | Name cleaned, empty name -> 422, <= 15 searches, every timeline item has a URL |

## Planned evals

- Budget test with a stubbed gateway that always returns results: never more than 15 searches.
- Citation test: every timeline URL was returned by the gateway in this run.
- Offline test: no network call; `limitations` explains how to enable live research.
- Quality set (once triage exists): 10 known companies with human-written reference findings; score recall of red flags and citation validity.

## Targets

| Metric | Target |
|---|---|
| Items without URL | 0 |
| Searches per report | <= 15 |
| Citation validity | 100% |
| Red-flag recall (when built) | >= 80% |

## Executable trust regressions
`tests/test_trust_evals.py` covers metric faithfulness, unsupported claims, incomplete comparisons, weight normalization, research follow-up and unresolved anonymous identity. CI: `.github/workflows/trust-evals.yml`.
