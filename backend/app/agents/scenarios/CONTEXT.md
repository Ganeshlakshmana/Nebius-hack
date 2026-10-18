# Scenario (alternatives) agent - Context

_Code: `agents/scenarios/agent.py`, `services/data_tools.py::alternatives`_  
_Status: Implemented (nearest-profile alternatives). Custom-weight re-ranking lives in `/compare`._

What the agent knows, reads and is wired to.

- Serves `POST /scenarios/what-if` (`supplier_id`, `limit` 1-20) and runs at the end of the live-orders hand-off.
- Candidates share the source supplier's sourcing-risk level and supply-chain complexity (falls back to all suppliers if fewer than 30).
- Distance = |TRI gap| + 10 x relative PO-volume gap. Result flags suppliers that have an open ops alert.
- The dataset has no component category, so matching is by risk and operational profile only (stated in `matching_note`).
