# Scenario (alternatives) agent - Evals

_Code: `agents/scenarios/agent.py`, `services/data_tools.py::alternatives`_  
_Status: Implemented (nearest-profile alternatives). Custom-weight re-ranking lives in `/compare`._

How we measure whether the agent is right. Run existing tests with `python -m pytest backend/tests -q`.

## Existing automated checks

| Test | Verifies |
|---|---|
| `tests/test_api.py::test_simulated_ops_and_agent_handoffs` | Alternatives list is non-empty after the demo scenario |

## Planned evals

- Determinism: same input -> same ordered list.
- Exclusion: the source ID never appears; results length == `limit` (or fewer only when data is short).
- Alert flag: after starting the demo scenario, the affected supplier is flagged when it appears as a candidate.
- Monotonic check: sorted by non-decreasing `profile_distance`.

## Targets

| Metric | Target |
|---|---|
| Determinism | 100% |
| Source in results | 0 |
| Ordering correctness | 100% |
