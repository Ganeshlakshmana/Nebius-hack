# Live Orders agent - Context

_Code: `agents/live_orders/agent.py`_  
_Status: Implemented as a deterministic simulated feed (one demo scenario). A continuous generator is planned._

What the agent knows, reads and is wired to.

- Serves `GET /operations/status`, `GET /operations/alerts`, `POST /operations/scenario` (`start|pause|reset`).
- Baselines come from the dataset: `Supplier Delivery Rating`, `Order Confirmation Rate`, `Order Change Rate`, plus `Purchase Order Volume (EUR)`, `Total_Risk_Index`, `Sourcing Risk Level`.
- Overlay state is stored in SQLite (`live_metrics`, `ops_alerts`); the dataset is never mutated.
- The demo scenario picks the highest-PO 'High' sourcing-risk supplier (or a given one), drops delivery rating to 72% of baseline, and raises an alert with `drift_z = -3.5`.
- On scenario start, `main.py` hands off: live_orders -> news -> research (if severity high/critical) -> scenarios, and publishes SSE events.
