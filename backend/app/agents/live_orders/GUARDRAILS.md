# Live Orders agent - Guardrails

_Code: `agents/live_orders/agent.py`_  
_Status: Implemented as a deterministic simulated feed (one demo scenario). A continuous generator is planned._

Hard limits and safety controls. 'Planned' items are not enforced yet.

| Guardrail | Control | Status |
|---|---|---|
| Immutable history | Overlay lives in SQLite; DuckDB view is read-only. | Implemented |
| Simulation labelling | `source: simulated_feed` on status, alert and scenario responses. | Implemented |
| Bounded values | Simulated delivery rating floored at 5.0; live operational score clamped to 0-100. | Implemented |
| Reset | `reset` deletes only `source='simulated_feed'` alerts and all overlay metrics. | Implemented |
| Unknown supplier | Unknown ID -> HTTP 404, no alert written. | Implemented |
| Rate / alert dedupe | Avoid duplicate open alerts for same supplier+metric; cap alerts per minute. | Planned (currently each start creates a new alert) |
| Real-data boundary | A real ERP feed must use a different `source` value and never reuse `simulated_feed`. | Planned (production path) |
