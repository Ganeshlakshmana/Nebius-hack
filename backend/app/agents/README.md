# Agents - documentation index

Each agent folder contains five files:

| File | Purpose |
|---|---|
| `CONTEXT.md` | What the agent reads, serves and is wired to |
| `INTENT.md` | Why it exists and what success means |
| `GUIDELINES.md` | Behaviour rules for the agent and its maintainers |
| `GUARDRAILS.md` | Hard limits, with Implemented / Planned status |
| `EVALS.md` | Existing tests, planned evals and targets |

Cross-agent rules live in [SHARED_GUARDRAILS.md](./SHARED_GUARDRAILS.md).

| Agent | Status |
|---|---|
| [Chat agent](./chat/CONTEXT.md) | Implemented. Deterministic router (no LLM call yet); LLM phrasing is the planned next step. |
| [Live Orders agent](./live_orders/CONTEXT.md) | Implemented as a deterministic simulated feed (one demo scenario). A continuous generator is planned. |
| [News signals agent](./news/CONTEXT.md) | Partially implemented. Retrieves source-linked results; no LLM triage, so all signals are `unreviewed`. |
| [Research agent](./research/CONTEXT.md) | Partially implemented. Budgeted multi-dimension search with source links; triage, scorecard and recommendations are not generated yet (`status: partial`). |
| [Scenario (alternatives) agent](./scenarios/CONTEXT.md) | Implemented (nearest-profile alternatives). Custom-weight re-ranking lives in `/compare`. |
| [Memo agent](./memos/CONTEXT.md) | Implemented (HTML memo). Narrative text generation is not LLM-based yet. |
