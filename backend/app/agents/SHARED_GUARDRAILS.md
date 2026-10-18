# Shared guardrails (all agents)

These apply to every agent in `backend/app/agents/`. Per-agent files add to them, never relax them.

## Principles
1. **Grounded by construction.** Data answers come from typed tools over the dataset; no answer from model memory.
2. **Historic data is immutable.** The CSV is opened read-only in DuckDB. Operational, news and custom-weight data are overlays stored in SQLite.
3. **Label what is simulated or unverified.** `source: simulated_feed`, `qualification_status: unverified`, `triage_status: unreviewed`.
4. **Say what is missing.** Return a status and `limitations` instead of filling a gap.
5. **Everything is auditable.** Agent actions go to the audit log; hand-offs go through the signed `AgentBus` and are streamed over SSE.

## Controls

| Area | Control | Status |
|---|---|---|
| Inter-agent trust | HMAC-SHA256 signed envelopes with key id; invalid signature or key raises `PermissionError` | Implemented (`services/events.py`) |
| Secrets | `INTERNAL_AGENT_API_KEY`, `INTERNAL_AGENT_SECRET`, `TAVILY_API_KEY`, `LLM_API_KEY` read from env only; `.env` is git-ignored; never returned by an endpoint | Implemented |
| SQL safety | Bound parameters; sort columns from an allow-list | Implemented |
| Request validation | Pydantic bounds on message, ID lists, limits | Implemented (memo body still a free-form dict) |
| External calls | `OFFLINE_MODE=true` default; 24 h cache; 10 s timeout; failures return empty results | Implemented |
| CORS | Only the local frontend origins | Implemented |
| Provenance | Responses carry `tool_calls` and `provenance` (dataset file and columns) | Implemented for chat, component and compare paths |
| Endpoint authentication | `require_agent_key` exists for cross-process agent calls but no user authentication on the public API | **Gap** - add auth before any non-local deployment |
| Rate limiting | None | **Gap** |
| Prompt injection | Not applicable until an LLM is wired; rule: external text is data, never instructions | Planned |
| PII | Dataset is anonymised; real company names only come from the user | Policy |

## Change checklist for any agent
- Does the new output include provenance and a limitation when data is missing?
- Is anything simulated/unverified labelled?
- Is there a test (or eval case) that would fail if the agent invented a value?
- Were `GUARDRAILS.md` and `EVALS.md` updated?
