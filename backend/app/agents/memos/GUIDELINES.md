# Memo agent - Guidelines

_Code: `agents/memos/agent.py`_  
_Status: Implemented (HTML memo). Narrative text generation is not LLM-based yet._

Rules for how the agent (and anyone changing it) should behave. See also `../SHARED_GUARDRAILS.md`.

- Escape every dynamic value (`html.escape`), including the user's `note` and `chosen`.
- Include generation timestamp (UTC), selected supplier, table, and methodology/limitations.
- Do not include simulated-feed numbers in the official TRI columns; if added later, label them.
- Do not state facts not present in the data or in a cited source.
