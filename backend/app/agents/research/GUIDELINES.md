# Research agent - Guidelines

_Code: `agents/research/agent.py`, `services/search_gateway.py`, `services/events.py`_  
_Status: Partially implemented. Budgeted multi-dimension search with source links; triage, scorecard and recommendations are not generated yet (`status: partial`)._

Rules for how the agent (and anyone changing it) should behave. See also `../SHARED_GUARDRAILS.md`.

- Return `status: partial` and a plain `limitations` list until triage is implemented.
- Every timeline item needs a URL; confidence for untriaged snippets stays low (0.35) and `is_red_flag` false.
- With a component, add the limitation that results do not prove component qualification or the link to an anonymised supplier.
- Respect the search budget; stop early rather than exceed it.
- Emit agent events (`research_search_started`) so the UI can show progress.
