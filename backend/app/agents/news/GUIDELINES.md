# News signals agent - Guidelines

_Code: `agents/news/agent.py`, `services/search_gateway.py`_  
_Status: Partially implemented. Retrieves source-linked results; no LLM triage, so all signals are `unreviewed`._

Rules for how the agent (and anyone changing it) should behave. See also `../SHARED_GUARDRAILS.md`.

- Status values: `provider_not_configured`, `no_results`, `unreviewed_results`. Never fabricate a finding to fill a gap.
- Every signal needs a URL and (when available) a publication date.
- Do not link a real company to an anonymised supplier ID unless the user supplies the mapping.
- Severity stays `low` and dimension `unclassified` until triage is implemented; do not present it as a risk judgement.
- State in `limitations` that results do not change dataset scores.
