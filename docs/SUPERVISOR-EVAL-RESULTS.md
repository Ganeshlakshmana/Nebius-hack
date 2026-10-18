# Supervisor evaluation results — 18 October 2026

Model: configured Nemotron through Token Factory. Dataset: repository challenge CSV.

| Stage | Passed | Total |
|---|---:|---:|
| Initial live routing baseline | 22 | 29 |
| LangGraph main corpus, two repetitions | 58 | 58 |
| LangGraph additional phrasing corpus, two repetitions | 20 | 20 |
| Complete offline backend suite | 186 | 186 |

TypeScript checking and frontend production build passed. The running frontend `/api/chat` was also checked for supplier lookup and comparison plus memo; both returned `orchestrator: langgraph` and the expected specialist node paths.

Failures discovered and addressed: repeated supplier clarification, lowercase IDs, financial values repeated as quality values on follow-up, malformed component plans, generic words accepted as company identity, reversed filter ranges marked completed, incorrect highest/lowest risk direction, and vague responses to unsupported sending requests. Regression tests also inject provider timeouts and tool failures and check graph isolation and validation-before-dispatch.

Machine-readable results, including initial failed answers and final node paths: `backend/evals/results/2026-10-18-langgraph.json`. Instructions and assertion scope: `backend/evals/README.md`.

These are finite regression results, not a general reliability percentage. Deterministic lookups and routing repairs are included. Research retrieval was a labelled fixture in live supervisor evaluations; Tavily factual accuracy, UI visual correctness and durable workflow recovery were not established by this run. Additional phrasing cases were used for fixes, so they are no longer an independent holdout. No claim of production readiness is made.
