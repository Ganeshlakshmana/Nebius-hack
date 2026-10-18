# Chat agent - Guidelines

_Code: `agents/chat/agent.py`, `services/component_risk.py`, `services/data_tools.py`_  
_Status: Implemented. Deterministic router with a supplier-ID validator (no LLM call yet); LLM phrasing is the planned next step._

Rules for how the agent (and anyone changing it) should behave.

## Agent-specific rules

- Answer only from tool results (`get_suppliers`, `filter_suppliers`, `explain_score`, `component_risk`). Do not add facts from memory.
- State the metric and direction (higher TRI = higher risk; component score: lower is better).
- Quote the formula fit (R2, mode) when explaining a score; call drivers 'peer-relative'.
- Always say component qualification is unverified; point to `required_checks`.
- If the request is ambiguous (no supplier, no/multiple components) return a clarification, not a guess.
- Return structured UI components alongside text; the text must stand alone.
- When an LLM is added: it may only phrase tool output, must receive tool results as data (not instructions), and its numbers are re-checked by the validator.

## Core principles

1. **Grounded by construction.** Data answers come from typed tools over the dataset, never from model memory.
2. **Historic data is immutable.** Never write to the dataset; store overlays separately.
3. **Label what is simulated or unverified** (`simulated_feed`, `unverified`, `unreviewed`).
4. **Say what is missing.** Return a status and `limitations` instead of filling a gap.
5. **Everything is auditable.** Log actions; send hand-offs through the signed `AgentBus`.

## Change checklist

- [ ] Does new output include provenance, and a limitation when data is missing?
- [ ] Is anything simulated or unverified labelled as such?
- [ ] Is there a test or eval case that would fail if this agent invented a value?
- [ ] Were this agent's `GUARDRAILS.md` and `EVALS.md` updated in the same change?
