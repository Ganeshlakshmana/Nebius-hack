# Live Orders agent - Intent

_Code: `agents/live_orders/agent.py`_  
_Status: Implemented as a deterministic simulated feed (one demo scenario). A continuous generator is planned._

Why the agent exists and what 'good' looks like.

- Show how the platform reacts to a deteriorating live signal without touching official history.
- Quantify exposure: spend at risk = PO volume x TRI/100 x sourcing multiplier (1.0 / 1.25 / 1.6).
- Trigger the downstream agents so the demo shows detection -> investigation -> alternatives in one flow.
