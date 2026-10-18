# Siemens challenge readiness

## Verified locally
- Explore 10,000 suppliers, filter, rank, shortlist and compare up to 20.
- Backend-grounded chat covers the two challenge examples. Financial Health results for SUPP_00012 / SUPP_00450 / SUPP_00731: 54 / 65 / 53.
- Component screening uses illustrative, disclosed weights. It shows critical factors, missing qualification evidence, dimension-wise dominance and sensitivity across 16 weight scenarios. Scenario counts are not probabilities.
- Research UI calls the backend. Tavily searches sources, retrieves up to three pages, and performs up to two targeted follow-up searches when incident candidates are identified. Reports preserve links, dates where provided, execution outcomes, and limitations; downloadable as Markdown.
- Real-company research is separate from the anonymous CSV. An anonymous ID is never used as a real-company search identity.
- Shortlist Markdown export is implemented.

## Limits to demonstrate honestly
- Chat uses a Nemotron supervisor for conversation and bounded tool routing; data computations remain deterministic. Research uses fixed search dimensions with rule-based and Nemotron incident candidates triggering follow-up.
- Potential-concern keywords are investigation triggers, not verified allegations. Company identity, contradictory evidence, legal applicability and component certification require buyer review.
- Original total-risk formula is unknown. Explanations use a fitted statistical surrogate, never an exact original formula.
- Synthetic component assignments and simulated operations are demo overlays, not supplier capability or live events.
- Public deployment with jury login and a two-minute recording remain outstanding. Public API authentication and abuse controls must be added before exposure; local CORS is not authentication.

## Evaluation
Run from the repository root:

```sh
OFFLINE_MODE=true backend/.venv/bin/python -m pytest backend/tests -q
```

81 regression cases passed locally. Includes challenge answers, six metric routes, unknown IDs, unsupported certification/price/capacity claims, missing scores, tied ranks, normalization, component sensitivity, follow-up research, anonymous identities, limits, escaping and simulated-feed behavior. CI runs offline; tests do not establish real-world supplier suitability or open-ended language coverage.

Prior live research smoke check: Knorr-Bremse / braking systems returned linked sources. This is an execution check, not a verified risk assessment.

Latest local frontend-to-backend smoke: homepage, both challenge chat examples and arbitrary-component sourcing returned HTTP 200. Missing mandatory evidence prevented review readiness. TypeScript and production build passed. Browser visual verification is pending because browser control is disabled.

## Two-minute demo
1. Explore the portfolio and shortlist the three challenge IDs.
2. Ask the exact financial-risk question; show 53 / 54 / 65.
3. Ask why SUPP_00018 has high TRI; disclose the fitted explanation.
4. Ask for braking risk; show critical factors and decision-readiness checks.
5. Research a real company, open a source and inspect the follow-up trail.
6. Export the evidence report and shortlist memo.

## Research evidence update
Optional buyer-supplied official domain, conservative incident-vs-policy triage, freshness labels, citation-linked decision actions and decision-packet export now implemented. Domain matches are anchors, not legal-entity verification. Nemotron adds source-linked semantic interpretation; independent corroboration is not established. External evidence remains unverified.

## Any-component sourcing workspace
Open Sourcing after shortlisting suppliers. Enter component, application/specification, quantity and delivery date. Edit requirements and mark which are mandatory. Record per-supplier evidence references, reviewer names, scope rationale and validity dates. User attestation is not independent document verification. No requirement can be cleared with demo evidence, missing review metadata or evidence expiring before delivery. Failed mandatory checks block readiness regardless of score. Completed checks lead only to authorized review, never automatic award. Submitted packets are recorded in the local SQLite audit log; draft entries survive workspace navigation and reloads using session storage in the same browser tab. Clear the draft to start another purchase; export before closing the tab.

Demo: shortlist the three challenge IDs, enter a custom component (for example a vibration isolator), and generate with missing evidence. Show that even the lowest-risk supplier has unresolved gates. Enter a failed requirement for one supplier and regenerate. Download the decision packet to preserve the brief, weights, risk scores, per-requirement status, evidence references and limitations. Demo evidence must be marked as such and cannot satisfy a real requirement.

Evaluation total: 81 passing backend cases, including sourcing gate regressions. Token Factory Nemotron evidence review is integrated; scores and qualification gates remain deterministic. Public deployment, authenticated reviewer identity and jury login remain outstanding.

## Nemotron evidence review
One bounded Token Factory call reviews up to eight initial source excerpts. Nemotron thinking is disabled to keep the output within the demo token budget. Findings must match the schema, cite existing evidence IDs and quote exact source text. Unresolved identity cannot be promoted to a company incident. Invalid or unavailable model output falls back to rule-based research. Model findings remain advisory and cannot change scores or award readiness. UI and Markdown export expose model status, source-linked interpretations and buyer questions. Follow-up pages are not re-reviewed by the model.

90 offline backend tests passed, including citation fabrication, quote fabrication, duplicate citations, identity upgrading and provider failure. TypeScript and production build passed. Live synthetic policy-versus-incident smoke passed; these tests do not prove general semantic accuracy.

End-to-end live smoke through `/api/research`: Knorr-Bremse / braking systems returned HTTP 200, 17 sources, model status completed and one quote-validated finding from eight supplied excerpts. Decision remained review_required. Report ID: f44c1838-1731-4d7d-97ae-bb90f39d15e8 (local database only).

## Commercial scenario and contract monitoring
The Commercial workspace generates editable, explicitly synthetic quotes and contract metadata for the shortlist. It compares up to three-supplier sets under price, fixed cost, MOQ, capacity, delivery, concentration and risk constraints. It reports quote exclusions, contract notice/expiry/coverage alerts, and whether a hypothetical fallback set exists for each candidate. No savings or real contractual relationship is inferred from the original CSV.

Real-review API mode rejects synthetic quotes and unresolved qualification/contract checks. The dashboard currently exposes synthetic mode only. Reports can be exported as JSON with assumptions. Saved case snapshots support an authenticated monitoring scan and dashboard alert retrieval.

Three n8n workflow templates and setup instructions are in integrations/n8n/. Cloud import, credentials, publication and schedule activation are pending. Templates have not been execution-tested in n8n. Browser visual QA remains pending.

Commercial validation: 109 full-suite tests passed; the final commercial-only rerun passed 19 tests. TypeScript and production build passed. Frontend proxy smoke returned HTTP 200 with four feasible synthetic sets, a EUR 10,920 lowest-cost 60/40 allocation and contract deadline alerts; monitor retrieval returned HTTP 200. n8n JSON and graph references validated locally, not executed in Cloud.

## Conversational supervisor
Chat now handles greetings without triggering comparisons, carries the last 12 bounded messages, and uses Nemotron to select up to three allowlisted actions. Routes include compare, explain, portfolio filter, component screening, research, alternatives and draft memo. Sourcing/commercial routes ask for missing inputs and open the corresponding workspace; they do not silently create assumptions or run negotiations. Chat displays completed/failed agent traces, result tables, sources and memo downloads. Plans are validated before execution; unrequested IDs, anonymous company research, arbitrary tool names and excessive actions are rejected. General conversational responses are not evidence-validated. Provider failures use a labelled limited dataset fallback. No unrestricted code execution, supplier messaging, contract changes or purchasing.

Supervisor verification: 125 backend tests, TypeScript and production build passed. Live frontend proxy checks passed for greeting with selected suppliers, financial comparison, a quality follow-up, memo generation and real-company research (14 source links). Model planning also produced a two-action comparison-plus-memo plan. These checks establish the tested routes, not unrestricted ChatGPT equivalence or universal intent accuracy. Browser visual QA remains pending.
