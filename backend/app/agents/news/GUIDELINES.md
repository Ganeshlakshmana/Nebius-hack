# News signals agent - Guidelines

_Code: `agents/news/agent.py`, `services/search_gateway.py`_  
_Status: Partially implemented. Retrieves source-linked results; no LLM triage, so all signals are `unreviewed`._

Rules for how the agent (and anyone changing it) should behave.

## Agent-specific rules

- Status values: `provider_not_configured`, `no_results`, `unreviewed_results`. Never fabricate a finding to fill a gap.
- Every signal needs a URL and (when available) a publication date.
- Do not link a real company to an anonymised supplier ID unless the user supplies the mapping.
- Severity stays `low` and dimension `unclassified` until triage is implemented; do not present it as a risk judgement.
- State in `limitations` that results do not change dataset scores.

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
