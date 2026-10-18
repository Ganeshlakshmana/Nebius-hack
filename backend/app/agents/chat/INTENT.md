# Chat agent - Intent

_Code: `agents/chat/agent.py`, `services/component_risk.py`, `services/data_tools.py`_  
_Status: Implemented. Deterministic router (no LLM call yet); LLM phrasing is the planned next step._

Why the agent exists and what 'good' looks like.

- Let a procurement buyer ask natural-language questions about suppliers and get answers that are traceable to dataset rows.
- Make every number in an answer reproducible from a named tool call and dataset columns (`provenance`).
- Never be the source of facts: if the data cannot answer, say so and ask for the missing input.
- Success looks like: the challenge's example questions answered correctly, with an explanation and a UI card, and zero ungrounded figures.
