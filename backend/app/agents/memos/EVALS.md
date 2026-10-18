# Memo agent - Evals

_Code: `agents/memos/agent.py`_  
_Status: Implemented (HTML memo with input validation). Narrative text generation is not LLM-based yet._

How we measure whether the agent is right. Run existing tests with `python -m pytest backend/tests -q`.

## Existing automated checks

| Test | Verifies |
|---|---|
| `tests/test_guardrails.py::test_memo_escapes_input_and_rejects_bad_ids` | `<script>` escaped; simulated-data note present; unknown ID, wrong `chosen`, 0/21 IDs, long note -> 422 |

## Planned evals

- Fidelity test: every number in the memo table equals the dataset value.
- Snapshot test of the memo structure (sections present, simulated-data disclaimer present).

## Targets

| Metric | Target |
|---|---|
| Unescaped dynamic values | 0 |
| Table/dataset mismatches | 0 |
