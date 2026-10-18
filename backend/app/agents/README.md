# Agents - documentation index

Each agent folder contains five files:

| File | Purpose |
|---|---|
| `CONTEXT.md` | What the agent reads, serves and is wired to |
| `INTENT.md` | Why it exists and what success means |
| `GUIDELINES.md` | Behaviour rules for the agent and its maintainers |
| `GUARDRAILS.md` | Hard limits, with Implemented / Planned status |
| `EVALS.md` | Existing tests, planned evals and targets |

Each folder is self-contained. The platform-wide rules are repeated inside every agent: core principles and the change checklist in `GUIDELINES.md`, and the platform guardrails that apply to that agent in `GUARDRAILS.md`.

| Agent | Status |
|---|---|
| [Chat agent](./chat/CONTEXT.md) | Implemented. Deterministic dataset worker behind the Nemotron conversational supervisor. |
| [Live Orders agent](./live_orders/CONTEXT.md) | Implemented as a deterministic simulated feed (one demo scenario). A continuous generator is planned. |
| [News signals agent](./news/CONTEXT.md) | Partially implemented. Retrieves source-linked results; no LLM triage, so all signals are `unreviewed`. |
| [Research agent](./research/CONTEXT.md) | Budgeted search/extraction, rule-based and Nemotron evidence review, targeted follow-up and cited buyer actions. Reports remain partial and unverified; no numeric scorecard. |
| [Scenario (alternatives) agent](./scenarios/CONTEXT.md) | Implemented (nearest-profile alternatives). Custom-weight re-ranking lives in `/compare`. |
| [Memo agent](./memos/CONTEXT.md) | Implemented (HTML memo with input validation). Narrative text generation is not LLM-based yet. |

The supervisor in supervisor/agent.py selects up to three allowlisted actions using conversation history. It is an additional orchestration module, not an unrestricted autonomous agent.
