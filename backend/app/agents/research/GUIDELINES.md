# Research agent - Guidelines

_Code: `agents/research/agent.py`, `services/search_gateway.py`, `services/events.py`_  
_Status: Partially implemented. Budgeted multi-dimension search with source links; triage, scorecard and recommendations are not generated yet (`status: partial`)._

Rules for how the agent (and anyone changing it) should behave.

## Agent-specific rules

- Return `status: partial` and a plain `limitations` list until triage is implemented.
- Every timeline item needs a URL; confidence for untriaged snippets stays low (0.35) and `is_red_flag` false.
- With a component, add the limitation that results do not prove component qualification or the link to an anonymised supplier.
- Respect the search budget; stop early rather than exceed it.
- Emit agent events (`research_search_started`) so the UI can show progress.

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
