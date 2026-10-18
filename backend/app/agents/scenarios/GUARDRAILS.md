# Scenario (alternatives) agent - Guardrails

_Code: `agents/scenarios/agent.py`, `services/data_tools.py::alternatives`_  
_Status: Implemented (nearest-profile alternatives). Custom-weight re-ranking lives in `/compare`._

Hard limits and safety controls. 'Planned' items are not enforced yet.

| Guardrail | Control | Status |
|---|---|---|
| Bounded input | `limit` 1-20 (Pydantic). | Implemented |
| Unknown supplier | 404 with message; no partial result. | Implemented |
| Transparent method | Distance formula and dataset columns returned in `provenance`. | Implemented |
| Capability honesty | `matching_note` states component category is not in the data. | Implemented |
| Exclude alerted suppliers option | Allow filtering out suppliers with open alerts. | Planned |
| Component filter | Use component screening scores when a component is selected. | Planned |
