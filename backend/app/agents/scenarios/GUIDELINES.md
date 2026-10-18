# Scenario (alternatives) agent - Guidelines

_Code: `agents/scenarios/agent.py`, `services/data_tools.py::alternatives`_  
_Status: Implemented (nearest-profile alternatives). Custom-weight re-ranking lives in `/compare`._

Rules for how the agent (and anyone changing it) should behave. See also `../SHARED_GUARDRAILS.md`.

- Return `profile_distance` and `active_ops_alert` for every alternative.
- Do not claim an alternative can make the same part; always include the `matching_note`.
- Exclude the source supplier; respect `limit`.
- Treat open ops alerts as a penalty signal to the user, not as dataset facts.
