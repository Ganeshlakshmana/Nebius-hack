# Live Orders agent - Evals

_Code: `agents/live_orders/agent.py`_  
_Status: Implemented as a deterministic simulated feed (one demo scenario). A continuous generator is planned._

How we measure whether the agent is right. Run existing tests with `python -m pytest backend/tests -q`.

## Existing automated checks

| Test | Verifies |
|---|---|
| `tests/test_api.py::test_simulated_ops_and_agent_handoffs` | Scenario returns `simulated_feed`, creates an alert for the requested supplier, and status rows are labelled |

## Planned evals

- Property test: after `reset`, no `simulated_feed` rows remain and dataset values are byte-identical.
- Severity boundary tests around EUR 250,000 and each sourcing multiplier.
- Drift test: z-score sign and magnitude for several suppliers.
- Dedupe test once alert dedupe exists.

## Targets

| Metric | Target |
|---|---|
| Source label present | 100% of responses |
| Dataset mutation | 0 bytes changed |
| Severity rule correctness | 100% on boundary cases |
