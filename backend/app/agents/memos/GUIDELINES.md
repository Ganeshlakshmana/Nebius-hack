# Memo agent - Guidelines

_Code: `agents/memos/agent.py`_  
_Status: Implemented (HTML memo with input validation). Narrative text generation is not LLM-based yet._

Rules for how the agent (and anyone changing it) should behave.

## Agent-specific rules

- Escape every dynamic value (`html.escape`), including the user's `note` and `chosen`.
- Include generation timestamp (UTC), selected supplier, table, and methodology/limitations.
- Do not include simulated-feed numbers in the official TRI columns; if added later, label them.
- Do not state facts not present in the data or in a cited source.

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
