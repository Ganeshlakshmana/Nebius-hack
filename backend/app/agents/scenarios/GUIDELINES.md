# Scenario (alternatives) agent - Guidelines

_Code: `agents/scenarios/agent.py`, `services/data_tools.py::alternatives`_  
_Status: Implemented (nearest-profile alternatives). Custom-weight re-ranking lives in `/compare`._

Rules for how the agent (and anyone changing it) should behave.

## Agent-specific rules

- Return `profile_distance` and `active_ops_alert` for every alternative.
- Do not claim an alternative can make the same part; always include the `matching_note`.
- Exclude the source supplier; respect `limit`.
- Treat open ops alerts as a penalty signal to the user, not as dataset facts.

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
