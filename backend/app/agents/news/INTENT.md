# News signals agent - Intent

_Code: `agents/news/agent.py`, `services/search_gateway.py`_  
_Status: Partially implemented. Retrieves source-linked results; no LLM triage, so all signals are `unreviewed`._

Why the agent exists and what 'good' looks like.

- Surface external events that may change a supplier's risk picture, with links a buyer can verify.
- Keep external signals strictly separate from the dataset's scores.
