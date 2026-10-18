# Scenario (alternatives) agent - Evals

_Code: `agents/scenarios/agent.py`, `services/data_tools.py::alternatives`_  
_Status: Implemented (nearest-profile alternatives). Custom-weight re-ranking lives in `/compare`._

How we measure whether the agent is right. Run existing tests with `python -m pytest backend/tests -q`.

## Existing automated checks

| Test | Verifies |
|---|---|
| `tests/test_api.py::test_simulated_ops_and_agent_handoffs` | Alternatives list is non-empty after the demo scenario |
| `tests/test_guardrails.py::test_scenarios_exclude_alerted_and_never_return_source` | Source excluded, `limit` honoured, sorted by distance, `exclude_alerted` works, unknown ID -> 404 |

## Planned evals

- Determinism: same input -> same ordered list.
- Alert flag: after starting the demo scenario, the affected supplier is flagged when it appears as a candidate.

## Targets

| Metric | Target |
|---|---|
| Determinism | 100% |
| Source in results | 0 |
| Ordering correctness | 100% |
