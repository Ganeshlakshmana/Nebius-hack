# Memo agent - Guardrails

_Code: `agents/memos/agent.py`_  
_Status: Implemented (HTML memo). Narrative text generation is not LLM-based yet._

Hard limits and safety controls. 'Planned' items are not enforced yet.

| Guardrail | Control | Status |
|---|---|---|
| HTML escaping | All interpolated values are escaped (XSS protection). | Implemented |
| Input bounds | Between 1 and 20 IDs, otherwise 422. | Implemented |
| Download only | Served as an attachment (`Content-Disposition`). | Implemented |
| Unknown IDs | Reject (422) when any ID is not found instead of producing a partial table. | Planned (currently unknown IDs are silently omitted) |
| Note length | Cap `note` length and validate `chosen` is in `ids`. | Planned |
| Body schema | Replace the free-form dict with a Pydantic model. | Planned |
