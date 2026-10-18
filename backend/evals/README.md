# Supervisor evaluations

## Automated regression tests

From the repository root:

```sh
OFFLINE_MODE=true backend/.venv/bin/python -m pytest backend/tests -q
```

The existing GitHub Actions workflow runs this suite on pushes and PRs. Tests cover the actual LangGraph node sequence, validation before dispatch, request isolation, partial failures, invalid plans, model outages, exact CSV scores/order, follow-up grounding, synthetic commercial inputs, sourcing evidence gates and research evidence handling.

## Live model evaluations (paid API calls)

Configure the existing `.env` locally with `OFFLINE_MODE=false`, `LLM_API_KEY`, `LLM_BASE_URL` and `LLM_MODEL`. Do not commit credentials.

```sh
PYTHONPATH=backend backend/.venv/bin/python backend/evals/run_supervisor.py --repeat 2 --output /tmp/supervisor-main.json
PYTHONPATH=backend backend/.venv/bin/python backend/evals/run_supervisor.py --cases backend/evals/supervisor_holdout.json --repeat 2 --output /tmp/supervisor-additional.json
```

The main corpus has 26 conversations / 29 turns. The additional corpus has 10 alternate-phrasing cases. Follow-up turns consume the previous actual response, not a hand-authored successful history. The latter corpus was initially held out, but became regression data after its failures were used for fixes; it is no longer an unbiased holdout.

The runner invokes the actual FastAPI `/chat` route, compiled LangGraph, live Nemotron planner and real dataset tools. Research retrieval is explicitly stubbed to test routing without unpredictable external search; it records the company passed to research. **This is not an end-to-end Tavily/research factuality benchmark.** No purchasing, messaging or cloud deployment occurs.

Pass/fail checks include allowed tools, supplier identity, exact selected IDs, requested metric, CSV-derived numerical values and order, filter limits, required clarification status and artifact presence. A provider-unavailable fallback does not count as a live-model pass. Text-based caveat checks are basic regression assertions, not a semantic proof of safety or correctness. The runner exits nonzero on any failed assertion and writes each result as it goes. Repetitions are limited to 1–5; planning is limited to two provider attempts per turn.

## Release interpretation

Do not interpret a passing finite corpus as reliability for every phrasing. Inspect failures and raw answers, add regressions, and rerun after model/schema changes. General advice, adversarial prompt injection and external research require further human evaluation. Latencies include local tools and provider time; retrieval fixture latency is not representative of live research.
