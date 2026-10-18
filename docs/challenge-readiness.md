# Siemens challenge readiness

## Verified locally
- Explore 10,000 suppliers, filter, rank, shortlist and compare up to 20.
- Backend-grounded chat covers the two challenge examples. Financial Health results for SUPP_00012 / SUPP_00450 / SUPP_00731: 54 / 65 / 53.
- Component screening uses illustrative, disclosed weights. It shows critical factors, missing qualification evidence, dimension-wise dominance and sensitivity across 16 weight scenarios. Scenario counts are not probabilities.
- Research UI calls the backend. Tavily searches sources, retrieves up to three pages, and performs up to two targeted follow-up searches when incident candidates are identified. Reports preserve links, dates where provided, execution outcomes, and limitations; downloadable as Markdown.
- Real-company research is separate from the anonymous CSV. An anonymous ID is never used as a real-company search identity.
- Shortlist Markdown export is implemented.

## Limits to demonstrate honestly
- Chat is a deterministic router, not unrestricted LLM conversation. Research planning and follow-up use explicit rules, not model reasoning.
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
Optional buyer-supplied official domain, conservative incident-vs-policy triage, freshness labels, citation-linked decision actions and decision-packet export now implemented. Domain matches are anchors, not legal-entity verification. No model-based semantic understanding or independent corroboration is claimed. External evidence remains unverified.

## Any-component sourcing workspace
Open Sourcing after shortlisting suppliers. Enter component, application/specification, quantity and delivery date. Edit requirements and mark which are mandatory. Record per-supplier evidence references, reviewer names, scope rationale and validity dates. User attestation is not independent document verification. No requirement can be cleared with demo evidence, missing review metadata or evidence expiring before delivery. Failed mandatory checks block readiness regardless of score. Completed checks lead only to authorized review, never automatic award. Submitted packets are recorded in the local SQLite audit log; draft entries survive workspace navigation and reloads using session storage in the same browser tab. Clear the draft to start another purchase; export before closing the tab.

Demo: shortlist the three challenge IDs, enter a custom component (for example a vibration isolator), and generate with missing evidence. Show that even the lowest-risk supplier has unresolved gates. Enter a failed requirement for one supplier and regenerate. Download the decision packet to preserve the brief, weights, risk scores, per-requirement status, evidence references and limitations. Demo evidence must be marked as such and cannot satisfy a real requirement.

Evaluation total: 81 passing backend cases, including sourcing gate regressions. Token Factory inference remains pending valid credentials. Public deployment, authenticated reviewer identity and jury login remain outstanding.
