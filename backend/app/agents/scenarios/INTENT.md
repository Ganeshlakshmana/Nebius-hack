# Scenario (alternatives) agent - Intent

_Code: `agents/scenarios/agent.py`, `services/data_tools.py::alternatives`_  
_Status: Implemented (nearest-profile alternatives). Custom-weight re-ranking lives in `/compare`._

Why the agent exists and what 'good' looks like.

- Answer 'if I have to replace this supplier, who is the closest low-disruption alternative?' with a transparent rule.
- Keep the rule inspectable: no hidden model, distances are returned.
