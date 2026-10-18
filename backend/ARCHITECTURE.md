# Backend Architecture
## Supplier Risk Intelligence Platform – Siemens Challenge

**Version:** 2.2
**Date:** 18 October 2026
**Scope:** Backend design for a ~48-hour build, with a defined path to production
**Dataset:** `supplier_risk_dataset.csv` (10,000 suppliers), described in `risk_criteria_description.md`

> **Reading this document.** Sections 1–11 describe the target design. Section 0 records what the code in `backend/app/` actually implements today, and Section 12 covers agent governance: context, intent, guidelines, guardrails and evals. Where they differ, Section 0 and the per-agent docs in `backend/app/agents/` describe the running system.

---

## 0. Implementation Status (as of 18 October 2026)

| Area | Target (this doc) | Implemented now |
|------|-------------------|-----------------|
| Chat agent | LLM tool loop + validator + UI component builder | Deterministic router over data tools (`agents/chat/agent.py`); no LLM call; returns `ranking_table`, `contribution_bars`, `supplier_card`, `component_risk` components with `tool_calls` and `provenance`. JSON response, not SSE |
| Component screening | — (added after v2.1) | `services/component_risk.py`: 7 component profiles (braking, traction, wheelsets, signalling, doors, HVAC, batteries) with illustrative weights; `GET /components`, `POST /components/analyze`; every result `qualification_status: unverified` |
| Live Orders agent | Continuous simulated feed, rolling windows, drift detection | One seeded demo scenario (delivery drop to 72% of baseline, `drift_z = -3.5`); overlay stored in SQLite; `source: simulated_feed` |
| Research agent | LangGraph plan→search→extract→triage→deep-dive→synthesize→cite_check | Budgeted search across 7 dimensions (≤15 searches), source-linked timeline, no triage; reports are `status: partial` |
| News signals | Classified by triage rubric | Search only when a real company name is supplied; all signals `unreviewed`, `dimension: unclassified` |
| Scenarios | Peer-group alternatives with deltas | Nearest-profile alternatives (TRI gap + 10× relative PO gap), open-alert flag |
| Memos | PDF with LLM summary | HTML download, all values escaped, data-only table |
| Inter-agent bus | Hand-offs, events | HMAC-SHA256 signed `AgentBus`, audit log, SSE `EventBus` |
| Frontend integration | — | Next.js `app/api/chat/route.ts` proxies `POST /chat` to `BACKEND_URL` (default `http://127.0.0.1:8000`); supplier table loads from static `public/suppliers.json`, not `/suppliers` |
| Tests | Golden questions, calibration, drift | 9 test functions in `tests/test_api.py` and `tests/test_components.py` (10 cases with parametrisation) |

---

## 1. Principles

1. **Grounded by construction.** The LLM never answers data questions from memory or retrieval. It calls typed tools, and its answer is checked against what the tools returned.
2. **Historic data is immutable.** The dataset is loaded read-only. Live operations, news signals and custom weights are separate overlays shown alongside it.
3. **Explanations are computed, then phrased.** Score drivers come from recovered TRI weights; the LLM only puts them into words.
4. **Simulated data is anchored and labelled.** The operations feed is generated from each supplier's real baseline and carries a `source: "simulated_feed"` marker through every API response.
5. **Visible agents.** Every agent step and hand-off emits an event that the UI streams.
6. **Minimal infrastructure.** Two containers and two embedded databases. Anything that doesn't change the demo is on the production path.

---

## 2. Architecture

```
┌──────────────────────────────────────────────────────────────────────────┐
│                        FastAPI (single service)                          │
│                                                                          │
│  Routers: /suppliers  /compare  /chat  /research  /operations  /signals  │
│           /scenarios  /memos  /events  /meta                             │
│                                                                          │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────────────────┐     │
│  │ Data tools  │◄─┤ Score        │◄─┤ Chat agent                   │     │
│  │ (DuckDB)    │  │ explainer    │  │ tool loop + validator        │     │
│  └─────────────┘  └──────────────┘  │ + UI component builder       │     │
│        ▲                            └──────────────────────────────┘     │
│        │                                                                 │
│  ┌─────┴──────────────────────┐   ┌──────────────────────────────┐       │
│  │ Live Orders agent          │   │ Research agent               │       │
│  │ feed generator → rolling   │   │ (LangGraph subgraph)         │       │
│  │ metrics → drift → alerts   │   └──────────────┬───────────────┘       │
│  └─────┬──────────────────────┘                  │                       │
│        │                      ┌──────────────┐   │                       │
│        │                      │ News signals │───┤                       │
│        │                      └──────────────┘   ▼                       │
│        │                             Search gateway (Tavily, cached)     │
│        ▼                                                                 │
│  Event bus (in-process): agent hand-offs + SSE to frontend               │
│        │                                                                 │
│        ├──► Hand-off coordinator (ops alert → news → research → scenarios)│
│        │                                                                 │
│  ┌─────┴────────┐  ┌──────────────┐                                      │
│  │ Scenario svc │  │ Memo service │                                      │
│  └──────────────┘  └──────────────┘                                      │
└──────────┬───────────────────────────────────────┬───────────────────────┘
           │                                       │
  DuckDB (dataset, read-only)         SQLite (ops events, live metrics, alerts,
                                      search cache, reports, signals, audit log)
```

**Why no LLM supervisor.** The frontend already knows the intent of most requests (chat, research, operations). Agent-to-agent hand-offs are triggered by events with deterministic rules in a small **hand-off coordinator**, which is cheaper, faster and easier to explain than an LLM routing every step. Inside the chat agent, tool selection does the routing.

---

## 3. Technology Stack

| Component | Choice | Reason |
|-----------|--------|--------|
| API | FastAPI + Pydantic v2 | Async, typed, OpenAPI for the frontend team |
| Streaming | Server-Sent Events (`sse-starlette`) | One-way agent progress and ops ticker |
| Analytics store | DuckDB (in-process) | Fast filters and ranking over 10k rows |
| App store | SQLite | Ops events, metrics, cache, reports and audit log with no extra service |
| Feed scheduling | asyncio background task | Ticks the operations feed; no job queue needed |
| Drift detection | numpy (EWMA z-score + CUSUM) | Simple, explainable, fast over 10k suppliers |
| Agent graph | LangGraph (research agent only) | Explicit loop control where it matters |
| LLM access | LiteLLM | Provider-agnostic; one model with reliable tool calling |
| Search | Tavily (search + extract) | Built for agents, returns source URLs |
| Explainability | statsmodels (OLS), scikit-learn + SHAP (fallback) | Recovers exact or approximate score drivers |
| PDF | Jinja2 HTML template + WeasyPrint | Memo layout in HTML, rendered to PDF |
| Logging | structlog (JSON) | Traces every agent step; feeds the audit log |
| Tests | pytest + golden-question set | Proves grounding before the demo |
| Packaging | uv + Docker Compose | Two services: `api`, `web` |

---

## 4. Data Layer

### 4.1 Loading and schema discovery

At startup:
1. Load the CSV into DuckDB table `suppliers`.
2. Normalise headers to snake_case aliases (for example `"Purchase Order Volume (EUR)"` → `po_volume_eur`) while keeping the original names for display.
3. Profile every column (type, null rate, range, distinct values) and expose it at `GET /meta/schema`.
4. Fail fast with a clear error if a column in `columns.yaml` is missing from the CSV.

### 4.2 `config/columns.yaml`

Column names follow `risk_criteria_description.md`. Exact header spelling, the ID column and the categorical values are confirmed against the CSV in Block 0.

```yaml
id: Supplier_ID                      # assumed; IDs look like SUPP_00012
total_risk: Total_Risk_Index

# Candidate TRI inputs. TRI is documented as a weighted average of the
# risk categories; the regression confirms which ones actually enter it.
category_scores:
  financial_health: Financial_Health_Score
  credit_rating: Credit_Rating_Score
  compliance: Compliance_Risk_Score
  governance: Governance_Risk_Score
  quality: Quality_Risk_Score
  safety: Safety_Incident_Score
  operational_resilience: Operational_Resilience_Score
  labor_stability: Labor_Stability_Score
  sub_tier_visibility: Sub_Tier_Visibility_Score
  digital_security: Digital_Security_Score
  environmental_exposure: Environmental_Exposure_Score
  geopolitical: Geopolitical_Risk_Score
  political_stability: Political_Stability_Score
  esg_performance: ESG_Performance_Score   # may also exist as E/S/G pillar columns
  media_sentiment: Media_Sentiment_Score
  market_sentiment: Market_Sentiment_Score
  external_intelligence: External_Intelligence_Score

context_scores:                      # shown, but probably not TRI inputs; regression decides
  industry_benchmark: Industry_Benchmark_Score

operational_metrics:                 # verify exact header spelling in the CSV
  po_volume_eur: "Purchase Order Volume (EUR)"
  order_change_rate: "Order Change Rate"              # %, higher = worse
  delivery_rating: "Supplier Delivery Rating"         # %, higher = better
  confirmation_rate: "Order Confirmation Rate"        # %, higher = better
  sourcing_risk_level: "Sourcing Risk Level"          # categorical, check values
  supply_chain_complexity: "Supply Chain Complexity"  # categorical or numeric, check

score_direction: higher_is_riskier   # all *_Score columns, 0 = no risk, 100 = maximum risk
risk_bands:                          # derived from TRI for display; adjust after profiling
  low: [0, 25]
  medium: [25, 50]
  high: [50, 75]
  critical: [75, 100]
peer_grouping: [sourcing_risk_level, supply_chain_complexity]  # no component/country column documented
peer_min_size: 30                    # smaller groups fall back to the whole population
```

### 4.3 TRI weight recovery (`services/explainer.py`)

Runs once at startup; results are cached in SQLite.

```python
def recover_tri_formula(df, target, features) -> FormulaFit:
    ols = sm.OLS(df[target], sm.add_constant(df[features])).fit()
    if ols.rsquared >= 0.99:
        weights = ols.params.drop("const")
        weights = weights[weights.abs() > 1e-3]           # drop columns that don't enter TRI
        return FormulaFit(mode="exact", weights=weights, r2=ols.rsquared)
    model = HistGradientBoostingRegressor().fit(df[features], df[target])
    return FormulaFit(mode="approximate", model=model,
                      explainer=shap.TreeExplainer(model), r2=model.score(df[features], df[target]))
```

The fitted weights are also shown in the UI as "How the Total Risk Index is built", which is a useful trust signal on its own.

Per-supplier explanation:

```python
def explain(supplier_id) -> ScoreExplanation:
    row = get_row(supplier_id)
    peers = get_peer_medians(row.sourcing_risk_level, row.supply_chain_complexity)
    contributions = [
        Contribution(factor=f, value=row[f], peer_median=peers[f],
                     points=w * (row[f] - peers[f]))       # SHAP values in approximate mode
        for f, w in fit.weights.items()
    ]
    return ScoreExplanation(total=row.total_risk, mode=fit.mode, r2=fit.r2,
                            peer_group=peers.label, contributions=sorted_by_abs(contributions),
                            live_alerts=get_active_alerts(supplier_id))
```

### 4.4 SQLite tables

| Table | Purpose |
|-------|---------|
| `ops_events` | Generated events: supplier, type, timestamp, PO value, on-time flag, scenario tag |
| `live_metrics` | Rolling 7- and 30-day metrics per supplier, drift statistics, live-adjusted operational score |
| `ops_alerts` | Drift alerts: supplier, metric, baseline, current, spend at risk, severity, status |
| `search_cache` | Tavily query → response, with timestamp and 24h TTL |
| `research_reports` | Report JSON, status, budget used, events, triggering alert if any |
| `signals` | Per-supplier or per-company news signals: dimension, severity, URL, date |
| `audit_log` | Append-only: every agent step, tool call, hand-off, LLM call and validator result |
| `memos` | Generated memo metadata and file path |

---

## 5. Agents and Services

### 5.1 Data tools (`services/data_tools.py`)

Pure functions over DuckDB and SQLite, shared by the API routers and the chat agent:

| Tool | Signature |
|------|-----------|
| `get_suppliers` | `(ids: list[str]) -> list[SupplierProfile]` |
| `filter_suppliers` | `(filters: FilterSpec, sort: SortSpec, limit: int ≤ 100) -> list[SupplierSummary]` |
| `rank_suppliers` | `(ids: list[str], by: str, ascending: bool) -> list[RankedSupplier]` |
| `explain_score` | `(id: str) -> ScoreExplanation` |
| `compare_suppliers` | `(ids: list[str] ≤ 20) -> ComparisonResult` |
| `find_alternatives` | `(id: str, limit: int) -> list[Alternative]` |
| `get_live_operations` | `(ids: list[str]) -> list[LiveOpsStatus]` |
| `get_alerts` | `(ids: list[str] \| None, min_severity: str) -> list[OpsAlert]` |
| `get_signals` | `(id: str) -> list[NewsSignal]` |

`FilterSpec` and `SortSpec` are whitelisted against `columns.yaml`. The LLM never writes SQL.

### 5.2 Live Orders agent (`agents/live_orders/`)

The headline wow feature. Three parts: a feed generator, a monitor and an alert step that hands off to other agents.

#### Feed generator (`feed.py`)

Generates a realistic event stream anchored to the dataset. It sits behind an `OperationsFeed` interface, so a real ERP adapter can replace it later without changing the agent.

| Aspect | How it is grounded |
|--------|--------------------|
| Event rate per supplier | Proportional to its Purchase Order Volume (EUR); high-spend suppliers produce more events |
| PO values | Drawn so that annualised volume matches the supplier's PO volume |
| On-time delivery probability | The supplier's Supplier Delivery Rating |
| Confirmation probability | The supplier's Order Confirmation Rate |
| Change probability | The supplier's Order Change Rate |
| Day-to-day variance | Scaled by Supply Chain Complexity and Operational_Resilience_Score, calibrated on the spread across all 10k rows |

Event types: `po_placed`, `po_changed`, `po_confirmed`, `po_confirmation_missed`, `delivery_on_time`, `delivery_late`.

**Time model.** The feed backfills 90 simulated days at startup so rolling metrics exist immediately. It then advances one simulated day every few seconds (configurable) so the demo moves visibly.

**Scenarios** (`scenarios/*.yaml`). A seeded script injects drift into chosen suppliers, for example:

```yaml
name: delivery_collapse
seed: 42
events:
  - supplier: SUPP_00731
    start_day: 3
    duration_days: 10
    delivery_rating_to: 0.71
    confirmation_rate_to: 0.80
    tag: "labor dispute (scenario)"
```

The scenario tag is kept in `ops_events` for audit but is never shown to the agent, so detection is genuine.

#### Monitor (`monitor.py`)

On each simulated day, per supplier:
1. Update rolling 7- and 30-day delivery rating, confirmation rate and change rate.
2. Compare with the supplier's own baseline from the dataset using an EWMA z-score and CUSUM, so the agent detects *change*, not just low values.
3. Compute **spend at risk** = PO volume × live operational risk × sourcing multiplier, where the multiplier is higher for a high Sourcing Risk Level (hard to replace).
4. Compute the **live-adjusted operational score**: the historic Operational_Resilience_Score plus a bounded delta driven by drift, with the reason recorded. The historic value is never overwritten.

#### Alerting and hand-offs (`alerts.py`, `services/handoffs.py`)

An alert fires when drift persists for at least 3 simulated days and spend at risk passes a configurable threshold. Severity combines drift size, spend at risk and Sourcing Risk Level.

Hand-off rules in the coordinator:

| Trigger | Action |
|---------|--------|
| Alert of medium severity or above | News signals check for the supplier (in a real deployment, the matched company name) |
| News finds a high-severity item, or alert is high/critical | Research agent run, linked to the alert |
| Alert is high/critical | Scenario service pre-ranks alternatives |
| Any step | Event to the activity panel and an `audit_log` row |

Because the dataset is anonymised, news and research for a `SUPP_` ID run against a company name only when a mapping exists. For the demo, the scenario file can map chosen suppliers to real companies, and this mapping is shown in the UI as "demo mapping".

Example activity stream:
> **Live Orders** · SUPP_00731 delivery rating 94% → 71% over 10 days (z = −4.1)
> **Live Orders** · Spend at risk €4.2M · Sourcing Risk Level: High · Severity: critical
> **News** · Searching recent news… 2 items about a labor dispute (high)
> **Research** · Deep dive started on the labor dispute
> **Scenarios** · 5 alternatives ranked; best: SUPP_04410 (TRI 31, delivery 96%)

### 5.3 Chat agent (`agents/chat.py`)

A tool-calling loop (max 6 tool calls per turn):

1. The system prompt states the rule: answer only from tool results; if data is missing, say so; label simulated operations data.
2. The LLM calls data tools, plus `start_research(company)` for a real company outside the dataset.
3. **Validator:** extracts every `SUPP_\d+` ID and every number from the draft answer and checks each appears in this turn's tool results (numbers matched after rounding). One retry on failure; then a table of the raw tool output.
4. **UI component builder:** maps tool results to components deterministically:

| Tool result | Component |
|-------------|-----------|
| `rank_suppliers` | `ranking_table` |
| `compare_suppliers` | `radar_overlay` + `comparison_table` |
| `explain_score` | `contribution_bars` |
| `get_suppliers` (single) | `supplier_card` |
| `find_alternatives` | `alternatives_list` |
| `get_live_operations` | `ops_sparklines` |
| `get_alerts` | `alert_list` |

**Examples:**
- "Which of SUPP_00012, SUPP_00450 and SUPP_00731 has the lowest financial risk?" → `rank_suppliers(ids, by="financial_health", ascending=True)` → answer naming the lowest, with all three Financial_Health_Score values (lower = less risk) → `ranking_table`.
- "Why is the Total Risk Index of SUPP_00018 so high?" → `explain_score("SUPP_00018")` → top contributions vs peers → `contribution_bars`, plus any live alert.
- "Which of my shortlisted suppliers is deteriorating right now?" → `get_live_operations(shortlist)` → `ops_sparklines`.

### 5.4 Research agent (`agents/research/`, LangGraph)

```
plan ──► search (parallel) ──► extract ──► triage ──┬──► synthesize ──► cite_check ──► report
                                              ▲      │
                                              └──────┘ deep_dive (red flags found, budget left, ≤2 rounds)
```

| Node | What it does |
|------|--------------|
| `plan` | Resolves the company (name, country, website), then writes 5–8 queries mapped to the dataset's risk dimensions: financial health and credit, compliance and governance, quality and safety, labor stability, ESG, digital security, geopolitical and political exposure |
| `search` | Runs queries in parallel through the search gateway |
| `extract` | Pulls full text from the top results, including the company site and filings where found |
| `triage` | The LLM labels each finding with dimension, severity and confidence, keeping its URL. High-severity or low-confidence findings become red flags |
| `deep_dive` | For each red flag, writes 1–2 targeted follow-up queries and loops back to `search` |
| `synthesize` | Builds the `ResearchReport` from collected findings only, with a scorecard using the same dimensions as the dataset |
| `cite_check` | Drops any claim whose URL wasn't retrieved during this run and lists it under "Limitations" |

**Budget, enforced in graph state:** 15 searches, 10 extracts, 2 deep-dive rounds, 180 seconds. On any cap, the agent skips to `synthesize` and marks the report partial.

If the run was triggered by an ops alert, the report includes the alert and states whether the findings explain it.

### 5.5 News signals service (`services/signals.py`)

- Runs news searches for a supplier or company on demand, when added to a comparison, or when triggered by an ops alert.
- Classifies each item with the same dimension and severity rubric as research triage.
- Stores results in `signals`. **It never changes dataset scores.**

### 5.6 Scenario service (`services/scenarios.py`)

"What if SUPP_X fails?":
1. Candidate pool: suppliers in the same peer group (Sourcing Risk Level and Supply Chain Complexity), excluding SUPP_X.
2. Rank candidates by a blend of similarity of operational profile (PO volume range, complexity) and lower TRI (or the buyer's custom weights).
3. Exclude or flag candidates with an active ops alert.
4. Show the delta for each category score and live metric against SUPP_X.

The UI states that alternatives are matched on risk and operational profile, since the dataset has no component category.

### 5.7 Custom weights

Buyers set weights per category in the UI. The backend computes a `custom_score` and returns it **next to** the official TRI, never instead of it. Weights are passed in the request; nothing is stored server-side.

### 5.8 Memo service (`services/memos.py`)

Input: selected supplier IDs, the chosen supplier, an optional buyer note and optional research report IDs.
Output: a PDF with a decision summary, comparison table, drivers per shortlisted supplier, live operational status and alerts (labelled simulated), news and research red flags with links, a methodology note (TRI weights, R², peer grouping) and the generation timestamp.
The LLM writes only the summary paragraph; all tables come directly from the data.

---

## 6. API

| Method | Path | Returns |
|--------|------|---------|
| GET | `/health` | Status, dataset row count, formula mode, feed status |
| GET | `/meta/schema` | Column profile, role mapping, recovered TRI weights |
| GET | `/suppliers` | Filtered, sorted, paginated list |
| GET | `/suppliers/{id}` | Full profile, including live-adjusted operational score |
| GET | `/suppliers/{id}/explain` | `ScoreExplanation` |
| POST | `/compare` | `ComparisonResult` for ≤20 IDs (422 above 20), optional custom weights |
| GET | `/operations/status?ids=` | `LiveOpsStatus` per supplier |
| GET | `/operations/alerts` | Active and recent alerts |
| GET | `/operations/stream` | SSE: ops ticker events and alerts |
| POST | `/operations/scenario` | Start, pause or reset a seeded demo scenario |
| POST | `/chat` | Target: SSE stream. **Now:** JSON `{answer, components, tool_calls, validated, provenance}` |
| GET | `/components` | Component profile catalogue with illustrative weights and required checks |
| POST | `/components/analyze` | Component-priority screening for 1–20 suppliers (422 on ambiguous component or unknown ID) |
| POST | `/research` | `{research_id}`; starts the run in the background |
| GET | `/research/{id}/events` | SSE stream of agent steps |
| GET | `/research/{id}` | `ResearchReport` (final or partial) |
| GET | `/events/stream` | SSE: all agent activity and hand-offs, for the activity panel |
| GET | `/signals/{id}` | News signals for a supplier |
| POST | `/scenarios/what-if` | Ranked alternatives |
| POST | `/memos/shortlist` | Target: PDF. **Now:** HTML attachment |

Every response with derived claims includes `provenance`: dataset columns used, tool calls made, feed source, or URLs.

---

## 7. Core Models (Pydantic)

```python
class Contribution(BaseModel):
    factor: str; value: float; peer_median: float; points: float

class ScoreExplanation(BaseModel):
    supplier_id: str; total: float; risk_band: str
    mode: Literal["exact", "approximate"]; r2: float; peer_group: str
    contributions: list[Contribution]
    live_alerts: list["OpsAlert"]

class LiveOpsStatus(BaseModel):
    supplier_id: str
    baseline: dict[str, float]            # from the dataset
    rolling_7d: dict[str, float]; rolling_30d: dict[str, float]
    drift_z: dict[str, float]
    spend_at_risk_eur: float
    live_operational_score: float; historic_operational_score: float
    delta_reason: str | None
    sparkline: list[dict]                 # daily points for the UI
    source: Literal["simulated_feed", "erp"] = "simulated_feed"

class OpsAlert(BaseModel):
    alert_id: str; supplier_id: str; metric: str
    baseline: float; current: float; drift_z: float; days_persisting: int
    spend_at_risk_eur: float; sourcing_risk_level: str
    severity: Literal["low", "medium", "high", "critical"]
    status: Literal["open", "investigating", "resolved"]
    linked_research_id: str | None

class NewsSignal(BaseModel):
    dimension: str                        # one of the dataset's risk dimensions
    severity: Literal["low", "medium", "high"]
    summary: str; url: HttpUrl; published: date | None

class Finding(NewsSignal):
    confidence: float; is_red_flag: bool

class ResearchReport(BaseModel):
    company: str; resolved_website: HttpUrl | None
    status: Literal["complete", "partial"]
    executive_summary: str
    scorecard: dict[str, Literal["low", "medium", "high", "unknown"]]
    red_flags: list[Finding]; timeline: list[Finding]
    recommendations: list[str]; limitations: list[str]
    sources: list[HttpUrl]; budget_used: dict[str, int]
    dataset_match: str | None; triggering_alert: str | None

class UIComponent(BaseModel):
    type: Literal["ranking_table", "comparison_table", "radar_overlay",
                  "contribution_bars", "supplier_card", "alternatives_list",
                  "ops_sparklines", "alert_list"]
    props: dict

class ChatResponse(BaseModel):
    answer: str; components: list[UIComponent]
    validated: bool; tool_calls: list[str]
```

---

## 8. Project Structure

**Current layout** (repo root = `fullstack/`):

```
backend/
├── ARCHITECTURE.md, README.md, pyproject.toml
├── app/
│   ├── main.py                  # FastAPI app, all routes, agent wiring in lifespan()
│   ├── config/                  # settings.py, columns.yaml
│   ├── agents/
│   │   ├── README.md            # index of agent docs
│   │   ├── SHARED_GUARDRAILS.md # rules for every agent
│   │   └── <agent>/             # chat, live_orders, news, research, scenarios, memos
│   │       ├── agent.py
│   │       └── CONTEXT.md, INTENT.md, GUIDELINES.md, GUARDRAILS.md, EVALS.md
│   ├── services/                # data_tools, explainer, component_risk, events, search_gateway, security
│   ├── models/schemas.py        # Pydantic request/response models
│   ├── db/                      # duckdb_store.py (read-only dataset), sqlite_store.py (overlays, audit)
│   └── data/app.sqlite3         # runtime state (git-ignored)
└── tests/                       # test_api.py, test_components.py
data/supplier_risk_dataset.csv   # immutable source dataset
```

**Target layout:**

```
supplier-risk-intelligence/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config/              # settings.py, columns.yaml, thresholds.yaml
│   │   ├── api/                 # one router per resource
│   │   ├── agents/
│   │   │   ├── chat.py
│   │   │   ├── validator.py
│   │   │   ├── live_orders/     # feed.py, monitor.py, alerts.py, scenarios/*.yaml
│   │   │   └── research/        # graph.py, nodes.py, prompts.py, budget.py
│   │   ├── services/            # data_tools, explainer, handoffs, signals, scenarios,
│   │   │                        # memos, search_gateway, events
│   │   ├── models/              # Pydantic schemas
│   │   ├── db/                  # duckdb.py, sqlite.py
│   │   └── templates/           # memo.html
│   ├── tests/
│   │   ├── golden_questions.yaml
│   │   ├── test_data_tools.py
│   │   ├── test_explainer.py
│   │   ├── test_feed_calibration.py
│   │   ├── test_drift_detection.py
│   │   └── test_chat_grounding.py
│   └── pyproject.toml
├── frontend/                    # Next.js + Tailwind + shadcn/ui + Recharts
├── data/
│   ├── raw/supplier_risk_dataset.csv
│   ├── raw/risk_criteria_description.md
│   └── demo_cache/              # pre-generated research reports
├── docker-compose.yml
├── .env.example                 # TAVILY_API_KEY, LLM_MODEL, LLM_API_KEY, OFFLINE_MODE, FEED_SPEED
└── README.md
```

---

## 9. Reliability for the Demo

- **Seeded operations scenario:** fully offline and reproducible; `POST /operations/scenario` resets it between rehearsals.
- **Offline mode** (`OFFLINE_MODE=true`): the search gateway serves only from `search_cache` and `data/demo_cache`. Cached research runs replay their stored events at normal speed with a "cached run" badge.
- **Pre-generated reports:** for the companies mapped in the demo scenario, plus 2 more, run the day before.
- **Warm start:** TRI weights, peer medians and the 90-day ops backfill are computed at startup.
- **Timeouts:** 20s per LLM call, 10s per search; the research agent continues with what it has.

---

## 10. Testing

**Implemented** (`python -m pytest backend/tests -q`, all passing on 18 Oct 2026):

| Test | What it proves |
|------|----------------|
| `test_core_api_and_dataset_grounding` | 10,000 rows loaded; list, profile, explain (total = dataset TRI), compare and chat paths work |
| `test_simulated_ops_and_agent_handoffs` | Demo scenario returns `simulated_feed`, creates an alert, triggers partial research and alternatives |
| `test_compare_rejects_more_than_twenty` | 21 IDs → 422 |
| `test_component_ranking_and_chat` | Weights sum to 1; scores reproducible and sorted; chat routes to component screening; `unverified` status |
| `test_analysis_rejects_ambiguous_or_missing_inputs` | Unknown part, two parts, unknown supplier → 422 |
| `test_chat_no_selection_and_selection_limit` | No suppliers → clarification; 21 IDs rejected; duplicates collapsed |
| `test_missing_values_and_ties` | Missing metric → no score, no rank; ties share a rank |
| `test_component_research_queries` | Component research adds component-specific queries and stays `unverified` |

Per-agent eval plans and targets are in `backend/app/agents/<agent>/EVALS.md`. Known gaps: no direct tests for news signals or memos yet.

**Target:**

| Test | What it proves |
|------|----------------|
| `test_data_tools` | Filters, ranking and the 20-supplier cap behave correctly |
| `test_explainer` | Contributions sum to TRI minus the peer baseline in exact mode; R² reported |
| `test_feed_calibration` | Over a long run without scenarios, each supplier's simulated delivery, confirmation and change rates converge to its dataset values |
| `test_drift_detection` | Scenario drift is detected within the expected number of days; the false-alert rate on unperturbed suppliers stays below a set threshold |
| `test_chat_grounding` | Every golden question returns the correct supplier and values; the validator catches injected wrong numbers |
| Research smoke test | One cached run produces a report in which every claim has a retrieved URL |

`golden_questions.yaml` contains the two challenge questions plus at least 10 more (ranking, filtering, "why" questions, comparisons, live operations, an out-of-dataset company, an unanswerable question). Expected answers are computed directly from DuckDB, not written by hand.

---

## 11. Path to Production (not built during the event)

| Event build | Production |
|-------------|------------|
| Simulated feed generator | ERP or webhook adapter behind the same `OperationsFeed` interface |
| In-process event bus | Kafka or Redis Streams |
| DuckDB + SQLite | PostgreSQL (plus pgvector if document search is added) |
| Background tasks in FastAPI | Job queue (Temporal or ARQ) for research refreshes |
| Demo company mapping | Supplier master data linking IDs to legal entities |
| No authentication | SSO, role-based access |
| Rubric-based signal severity | Calibrated against historical supplier incidents |
| structlog + SQLite audit | OpenTelemetry + LangSmith, append-only audit store |
| Live-adjusted score as overlay | Human-approved score updates with versioning |

---

## 12. Agent Governance: Context, Intent, Guidelines, Guardrails, Evals

Every agent folder in `backend/app/agents/` carries five documents next to its code, so behaviour rules change in the same pull request as the code they govern:

| File | Answers |
|------|---------|
| `CONTEXT.md` | Which endpoints call it, which data it reads, how it hands off |
| `INTENT.md` | Why it exists and what "good" looks like |
| `GUIDELINES.md` | How it must behave (and how maintainers must change it) |
| `GUARDRAILS.md` | Hard limits, each marked **Implemented** or **Planned** |
| `EVALS.md` | Existing tests, planned evals, numeric targets |

Cross-agent rules are in `backend/app/agents/SHARED_GUARDRAILS.md`; the index is `backend/app/agents/README.md`.

### 12.1 Shared guardrails (summary)

| Control | Status |
|---------|--------|
| Dataset read-only; overlays in SQLite | Implemented |
| `simulated_feed` / `unverified` / `unreviewed` labels on non-dataset output | Implemented |
| No fabrication: missing providers return a status and `limitations` | Implemented |
| HMAC-SHA256 signed, audited inter-agent envelopes | Implemented |
| Parameterised SQL, allow-listed sort columns, Pydantic request bounds | Implemented |
| Secrets only from environment; `.env` git-ignored | Implemented |
| Offline-by-default search with cache, timeout and budget | Implemented |
| Numeric answer validator for LLM-phrased chat | Planned |
| Prompt-injection isolation for external text | Planned (with LLM step) |
| User authentication and rate limiting on the public API | **Gap**: required before any non-local deployment |
| Memo rejects unknown IDs; validated memo body schema | Planned |

### 12.2 Eval strategy

1. **Unit/contract tests** (exist): grounding, bounds, labels, rejection of ambiguous input.
2. **Golden set** (planned): ≥30 chat questions with expected tool calls and numbers computed from DuckDB, run in CI; target ≥95% tool-call accuracy and 100% numeric faithfulness.
3. **Safety sets** (planned): refusal cases (facts not in data), injection cases (instructions in supplier names or snippets), XSS cases for memos.
4. **Research/news quality** (planned, once triage exists): labelled snippets and reference companies; citation validity 100%, red-flag recall ≥80%.

A change to an agent is complete only when its `GUARDRAILS.md` and `EVALS.md` reflect the change.
