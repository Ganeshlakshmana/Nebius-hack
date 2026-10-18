# Memo agent - Evals

_Code: `agents/memos/agent.py`_  
_Status: Implemented (HTML memo). Narrative text generation is not LLM-based yet._

How we measure whether the agent is right. Run existing tests with `python -m pytest backend/tests -q`.

## Existing automated checks

| Test | Verifies |
|---|---|
| None yet | `/memos/shortlist` has no automated test |

## Planned evals

- XSS test: `<script>` in `note`/`chosen` appears escaped.
- Fidelity test: every number in the memo table equals the dataset value.
- Boundary tests: 0 and 21 IDs -> 422; unknown ID -> 422 (after fix).
- Snapshot test of the memo structure (sections present, simulated-data disclaimer present).

## Targets

| Metric | Target |
|---|---|
| Unescaped dynamic values | 0 |
| Table/dataset mismatches | 0 |
