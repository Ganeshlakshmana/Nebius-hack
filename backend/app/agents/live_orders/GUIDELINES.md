# Live Orders agent - Guidelines

_Code: `agents/live_orders/agent.py`_  
_Status: Implemented as a deterministic simulated feed (one demo scenario). A continuous generator is planned._

Rules for how the agent (and anyone changing it) should behave.

## Agent-specific rules

- Every payload carries `source: "simulated_feed"`; the UI must display it as simulated.
- Historic fields stay unchanged; live values are shown next to them (`historic_operational_score` vs `live_operational_score`).
- Severity is rule-based: `critical` if spend at risk >= EUR 250,000, else `high`.
- Keep simulated numbers anchored to the supplier's real baseline; do not invent unrelated suppliers or orders.
- Record each alert in the audit log (`simulated_alert_created`).

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
