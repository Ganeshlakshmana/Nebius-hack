# Supplier Risk Intelligence Platform
## Smart Supplier Selection for Trains – Siemens Challenge Plan

**Version:** 2.1
**Date:** 18 October 2026
**Status:** Ready for implementation
**Timebox assumption:** ~48-hour event. If the event is shorter, cut from the bottom of the cut order in section 8; if longer, add from section 10.

---

### 1. Goal

Help a rail buyer who is sourcing a critical component go from hundreds of suppliers to a justified final choice:

1. **Narrow** – filter and rank the field.
2. **Compare** – put up to 20 suppliers side by side and see *why* each is risky.
3. **Monitor** – watch live operational signals and get alerted when a supplier starts to deteriorate.
4. **Ask** – get answers in plain language that are grounded in the data.
5. **Investigate** – hand a real company name to a research agent and get a sourced risk report.
6. **Justify** – export a shortlist memo that explains the decision.

**Design rules:**
- Every number on screen or in a chat answer comes from the dataset, the labelled operations feed, or a cited source.
- Historic dataset values are never overwritten. Live data is an overlay with its own deltas, reasons and audit trail.
- The operations feed is simulated from each supplier's real baseline and is labelled as such everywhere it appears.

---

### 2. The Dataset

`supplier_risk_dataset.csv` – 10,000 anonymised suppliers, described in `risk_criteria_description.md`.

- **18 risk scores**, all on a 0–100 scale where **0 = no risk and 100 = maximum risk**. This applies even to scores whose names sound positive (ESG_Performance, Financial_Health, Credit_Rating), so the UI labels every score as risk.
- **Total_Risk_Index** is documented as a weighted average of the risk categories, so its weights can be recovered exactly.
- **Industry_Benchmark_Score** compares a supplier with its peers and is treated as context, not as a TRI input, unless the regression shows otherwise.
- **Six operational metrics:** Purchase Order Volume (EUR), Order Change Rate, Supplier Delivery Rating, Order Confirmation Rate, Sourcing Risk Level and Supply Chain Complexity.
- **No component category or country column is documented.** Peer groups and alternatives therefore use Sourcing Risk Level, Supply Chain Complexity and similarity of risk profile. If the CSV has extra columns, we use them.

Exact header spellings, the ID column name and the values of the two categorical metrics are confirmed in Block 0.

---

### 3. Success Criteria (what the judges will test)

| # | Criterion | How we prove it |
|---|-----------|-----------------|
| 1 | Both example questions answered correctly and with explanation | Golden-question test set, run before every demo |
| 2 | "Why is the TRI high?" gives quantified, specific reasons | Score decomposition from the recovered TRI weights (section 6) |
| 3 | Comparison of up to 20 suppliers goes beyond a table | Radar overlay, contribution bars, heatmap, live sparklines, per-supplier risk cards |
| 4 | Live operations visibly drive the multi-agent workflow | Drift alert → news check → research → alternatives, shown step by step in the activity panel |
| 5 | Research agent visibly plans, digs deeper on red flags, cites sources | Live activity stream plus a report in which every claim links to a source |
| 6 | Demo never breaks | Seeded operations scenario, cached research reports, offline mode |

---

### 4. Feature Set

#### Must-have (challenge requirements)
- **Supplier explorer** – filters (any score range, risk band, sourcing risk level, supply chain complexity, PO volume), sortable ranking, multi-select capped at 20.
- **Comparison workspace** – radar overlay, side-by-side table with best/worst highlighting, risk heatmap and a "why risky" panel per supplier.
- **Grounded chatbot** – answers via tool calls against the dataset and live operations, never from memory or vector similarity.
- **Research agent** – plan → search → triage red flags → deep-dive loop → synthesize → citation check, with every step streamed to the UI.

#### Headline wow feature: Live Orders Agent
- **Operations feed** replaying purchase orders, order changes, confirmations and deliveries for every supplier. Each supplier's event rates and baselines come from its own row in the dataset; variance is calibrated across all 10k suppliers.
- **Drift detection** against each supplier's own baseline, so the agent catches deterioration rather than just low absolute values.
- **Spend at risk** – PO volume × live operational risk, weighted up for hard-to-replace suppliers. This tells the buyer where a problem costs the most.
- **Live-adjusted operational score** shown as an overlay with delta and reason, beside the untouched historic Operational_Resilience_Score.
- **Agent hand-offs** – a serious drift alert triggers the news agent; red flags trigger the research agent; the scenario service pre-ranks alternatives. The activity panel shows the whole chain.
- **Demo scenarios** – a seeded script injects realistic drift into chosen suppliers, so the story is reproducible on stage.

#### Further surprise features (in build order)
1. **Agent activity panel** – a live timeline of what each agent is doing and why.
2. **Dynamic UI in chat** – answers can render a comparison table, radar chart, contribution chart, supplier card or live operations chart inline.
3. **Shortlist memo** – a one-click PDF covering the selection, ranking rationale, main risks, live operational status and sources.
4. **What-if alternatives** – "If SUPP_X fails, who replaces it?" returns ranked alternatives with similar profiles and a risk trade-off for each.
5. **Custom priority weights** – buyers re-rank by their own priorities; the official TRI always stays visible alongside.
6. **News signals layer** – recent news per supplier or company, tagged by risk dimension and severity, shown beside the historic scores rather than merged into them.

#### Explicitly out of scope for the event
- News-driven automatic changes to dataset scores. They are uncalibrated and hard to defend.
- Postgres, Redis, pgvector, Kubernetes, authentication and multi-tenancy. These belong to the production path (section 10).

---

### 5. Architecture at a Glance

```
┌────────────────────────────── Next.js frontend ───────────────────────────────┐
│ Explorer + ops ticker │ Compare (≤20) + sparklines │ Chat + dynamic components │
│ Research mode │ Live operations view │ Agent activity panel (SSE)             │
└───────────────────────────────────┬───────────────────────────────────────────┘
                                    │ REST + Server-Sent Events
┌───────────────────────────────────▼───────────────────────────────────────────┐
│                              FastAPI backend                                  │
│  Data tools · Score explainer · Chat agent · Research graph                   │
│  Live Orders agent + feed generator · News signals · Scenarios · Memos        │
│  Event bus (agent hand-offs + UI streaming)                                   │
└──────────────┬──────────────────────────────────────┬─────────────────────────┘
               │                                      │
     DuckDB (dataset, read-only)        SQLite (ops events, live metrics, cache,
                                        reports, signals, audit log)
                                                      │
                                             Tavily + LLM provider
```

The full design is in `backend_architecture.md`.

**Frontend choice.** We use Next.js because dynamic chat components and live operations views are central to the demo. If nobody on the team is comfortable with React, switch to Streamlit with a fixed set of chat component types and a polling operations view; the backend does not change.

---

### 6. Explainability: How "Why Is It Risky?" Works

1. **Recover the TRI weights.** The criteria file documents TRI as a weighted average of the risk categories. We fit a linear regression of TRI on the candidate category scores across all 10,000 rows.
   - If R² ≥ 0.99 (expected), the fitted weights are the formula and the explanation is labelled "exact".
   - Otherwise, we fit a gradient-boosted model and use SHAP values, labelled "approximate".
2. **Decompose each supplier's score.** contribution(category) = weight × (supplier score − peer median). Peers are suppliers with the same Sourcing Risk Level and Supply Chain Complexity, falling back to the whole population if a group is too small.
3. **Explain in words second.** The LLM receives the ranked contributions and phrases them; it cannot add factors that aren't in the decomposition.
4. **Add operational context.** If the Live Orders agent has an active alert for the supplier, the explanation mentions it separately as a live signal, not as part of TRI.

Example output: *"TRI 78. Biggest driver: Financial Health risk 84 vs a peer median of 41, adding +9 points. Second: Compliance risk adding +6. Quality risk is lower than peers (−2). Live: delivery rating has dropped from 94% to 71% over 10 days."*

---

### 7. Grounding Rules (hallucination control)

- **Chat answers are tool-backed.** The chat agent calls typed tools and answers only from their results.
- **Answers are checked before display.** Every supplier ID and number in the answer must appear in that turn's tool results. On failure the answer is regenerated once, then falls back to a plain table of the tool output.
- **Research claims need a source.** Every claim in a research report carries a source URL retrieved during the run. Unsourced claims are dropped and listed under "Limitations".
- **Simulated data is always labelled.** Every live operations view, chat answer and memo section that uses the feed says "Simulated ERP feed based on dataset baselines".
- **Uncertainty is visible.** Missing data, approximate explanations and low-coverage research are labelled in the UI, not hidden.

---

### 8. Implementation Roadmap (48 hours, 3–4 people)

| Block | Hours | Deliverable | Owner |
|-------|-------|-------------|-------|
| 0 | 0–3 | Repo, Docker Compose, dataset in DuckDB, headers confirmed, column profile, TRI weights recovered | Backend |
| 1 | 3–10 | Data APIs (list, filter, rank, profile, explain, compare) plus explorer and comparison UI | Backend + Frontend |
| 2 | 10–18 | Tool-calling chat agent, answer validator, both example questions passing | AI |
| 3 | 10–22 | Research agent graph with Tavily, SSE event stream, report view | AI + Frontend |
| 4 | 18–28 | Live Orders agent: feed generator, rolling metrics, drift detection, spend at risk, ops ticker and sparklines | Backend + Frontend |
| 5 | 26–32 | Agent hand-offs (ops → news → research → alternatives), activity panel, dynamic chat components | All |
| 6 | 32–37 | Shortlist memo PDF, what-if alternatives | Backend |
| 7 | 37–40 | Custom weights, news signals layer | Backend + Frontend |
| 8 | 40–44 | Golden-question tests, seeded demo scenario, cached research reports, offline mode, bug fixing | All |
| 9 | 44–48 | Demo script, three rehearsals, "path to production" slide | All |

**Cut order if behind schedule:** news signals layer → custom weights → what-if → dynamic chat components (fall back to tables). Blocks 0–5 and the memo are never cut.

---

### 9. Demo Script (target 6 minutes)

1. **Narrow** (45s) – filter to suppliers with a high Sourcing Risk Level and large PO volume, rank by TRI, select 8.
2. **Compare** (60s) – radar overlay; click the riskiest supplier to show its contribution breakdown.
3. **Monitor** (75s) – the ops ticker raises a drift alert on a shortlisted supplier. The activity panel shows the hand-off chain: spend at risk calculated, news checked, red flag found, alternatives ranked.
4. **Ask** (60s) – run both example questions live, then "Which of my shortlisted suppliers is deteriorating right now?" with an inline chart.
5. **Investigate** (75s) – research a real company; show planning, a red flag and the deep dive; open the report and click a source.
6. **Justify** (45s) – generate the shortlist memo and open the PDF.

**Fallback:** the operations scenario is seeded and runs offline. If the network fails, the research step uses a pre-generated report for the same company, and we say so openly.

---

### 10. Path to Production (one slide, not built during the event)

- Replace the feed generator with a real ERP or webhook adapter behind the same interface.
- PostgreSQL in place of DuckDB/SQLite; a streaming backbone (Kafka or Redis Streams) for operations events.
- Single sign-on, role-based access and an append-only audit store.
- Calibrated news-to-risk scoring, validated against historical supplier incidents.
- Human approval for any change to an official risk score.
- Multi-tier supplier graph for contagion risk, using Sub_Tier_Visibility as a starting point.
- Background job queue for scheduled research refreshes.

---

### 11. Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Simulated feed seen as fake data | Anchored to each supplier's real values, calibrated on all 10k rows, labelled everywhere, same adapter interface as a real ERP |
| Drift alerts are noisy | Thresholds tuned on the generated baseline; alerts require persistence over several days and a minimum spend at risk |
| Chat gives a wrong number | Tool-only answers plus a validator; golden-question tests before the demo |
| TRI weights can't be recovered exactly | SHAP-based fallback, labelled "approximate" in the UI |
| Tavily rate limits, cost or outage | Per-run budget caps, SQLite cache, pre-generated demo reports |
| Research agent runs too long | Hard caps: 15 searches, 2 deep-dive rounds, 3 minutes; partial report on timeout |
| Header names differ from the criteria file | Confirmed in Block 0; all names live in `columns.yaml` |
| Scope creep | Out-of-scope list (section 4) and cut order (section 8) agreed up front |

---

### 12. Immediate Next Steps

1. Confirm event length and team roles; adjust section 8.
2. Obtain the Tavily API key and pick an LLM provider with reliable tool calling.
3. Read the CSV header row, confirm `columns.yaml`, and check the values of Sourcing Risk Level and Supply Chain Complexity.
4. Recover the TRI weights and write the golden-question file (the two example questions plus 10 more) before building the chat agent.
5. Choose 2–3 suppliers for the seeded demo scenario: high PO volume, high Sourcing Risk Level, currently moderate TRI.
