# Live Orders agent - Guidelines

_Code: `agents/live_orders/agent.py`_  
_Status: Implemented as a deterministic simulated feed (one demo scenario). A continuous generator is planned._

Rules for how the agent (and anyone changing it) should behave. See also `../SHARED_GUARDRAILS.md`.

- Every payload carries `source: "simulated_feed"`; the UI must display it as simulated.
- Historic fields stay unchanged; live values are shown next to them (`historic_operational_score` vs `live_operational_score`).
- Severity is rule-based: `critical` if spend at risk >= EUR 250,000, else `high`.
- Keep simulated numbers anchored to the supplier's real baseline; do not invent unrelated suppliers or orders.
- Record each alert in the audit log (`simulated_alert_created`).
