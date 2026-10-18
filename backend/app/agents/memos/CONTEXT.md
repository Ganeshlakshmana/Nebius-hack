# Memo agent - Context

_Code: `agents/memos/agent.py`_  
_Status: Implemented (HTML memo). Narrative text generation is not LLM-based yet._

What the agent knows, reads and is wired to.

- Serves `POST /memos/shortlist` with `ids` (1-20), optional `chosen`, optional `note`; returns a downloadable HTML file.
- Table content (name, TRI, sourcing risk, PO volume) is read from the dataset via `DataTools.get_suppliers`.
- Memo text states that operations-feed data is simulated and not part of the official TRI.
