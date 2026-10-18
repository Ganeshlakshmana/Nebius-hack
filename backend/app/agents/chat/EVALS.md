# Chat agent - Evals

_Code: `agents/chat/agent.py`, `services/component_risk.py`, `services/data_tools.py`_  
_Status: Implemented. Deterministic router (no LLM call yet); LLM phrasing is the planned next step._

How we measure whether the agent is right. Run existing tests with `python -m pytest backend/tests -q`.

## Existing automated checks

| Test | Verifies |
|---|---|
| `tests/test_api.py::test_core_api_and_dataset_grounding` | Comparison chat answer is `validated` and names the requested supplier; `/explain` total equals the dataset TRI |
| `tests/test_components.py::test_component_ranking_and_chat` | Component route via free text and explicit `component`; scores sorted ascending; `unverified` status |
| `tests/test_components.py::test_chat_no_selection_and_selection_limit` | No supplier selected -> clarification, no components; 21 IDs rejected |
| `tests/test_components.py::test_analysis_rejects_ambiguous_or_missing_inputs` | Unknown part, two parts, unknown supplier -> 422 |

## Planned evals

- Golden set of >= 30 questions (challenge examples + edge cases) with expected tool calls and expected numbers, run in CI.
- Numeric faithfulness: 100% of numbers in the answer appear in tool output (once an LLM phrases answers).
- Refusal set: questions needing external facts ('is X ISO certified?') must return a limitation, not an answer.
- Injection set: supplier names containing instructions must not change tool choice.

## Targets

| Metric | Target |
|---|---|
| Tool-call accuracy | >= 95% on golden set |
| Numeric faithfulness | 100% |
| Correct refusal / clarification | >= 95% |
| p95 latency (templated) | < 1 s |
