# Supplier Risk Intelligence Platform  
## Multi-Agent System for Siemens – Long-Term Architecture & Implementation Plan

**Version:** 1.0  
**Date:** 18 October 2026  
**Status:** Ready for Implementation  
**Target:** Siemens Supplier Risk Intelligence Challenge (Rolling Stock Components)

---

### 1. Vision & Objectives

Build a production-grade, multi-agent Supplier Risk Intelligence system that:

- Continuously assesses and explains supplier risk using historic data + real-time signals
- Allows buyers to filter, rank, and compare up to 20 suppliers with rich visual risk profiles
- Provides a grounded chatbot that answers natural-language questions with full provenance
- Features a deep Research Agent capable of investigating any real-world company
- Delivers “wow” experiences: dynamic UI generation, scenario simulation, auto-generated memos, transparent agent workflows
- Is designed for **long-term use**: modular, observable, extensible, auditable, and maintainable beyond the hackathon

**Success Criteria**
- Answers the challenge example questions accurately and with explanations
- Research Agent produces high-quality reports with source links
- UI feels like a professional procurement tool, not a prototype
- System can be extended with new risk models, data sources, or agents without major rewrites
- Full audit trail of every score change and agent decision

---

### 2. Core Features (Prioritized)

#### Must-Have (Challenge Requirements)
- Historical Scoring Agent (reads the provided 10k-supplier dataset)
- Real-time News Agent powered by Tavily
- Live Orders / Operational Metrics Agent
- Rich comparison UI (filter, rank, multi-select ≤20, side-by-side, risk profiles, “why risky”)
- Grounded chatbot
- Research Agent (plan → search → dig deeper → structured report with sources)
- Auto-generated shortlist memos

#### High-Impact Wow Features
- **Dynamic UI Generation**: Chatbot answers can spawn interactive components (comparison cards, radar charts, evidence panels, timelines)
- **Transparent Multi-Agent Workflow**: Live activity panel showing what each agent is doing and why
- **Scenario / What-If Simulation**: “What happens if Supplier X fails?” → impact analysis + ranked alternatives
- **Risk Trajectory & Early Warning**: Trend arrows, 30/90-day outlook, volatility indicators
- **Explainability Engine**: Natural-language “Why is the score high?” with ranked factors + evidence + sources
- **Configurable Risk Weights**: Buyers can adjust importance of Financial vs ESG vs Operational etc.
- **Confidence & Data Coverage Scores**: Every risk score carries uncertainty and freshness metadata
- **One-click Artifacts**: PDF Shortlist Memo, Risk Briefing (PPTX), shareable Risk Cards

#### Long-Term Differentiators
- Multi-tier / contagion risk visualization (graph view)
- Human-in-the-loop approval for high-impact score changes
- Full observability & audit logging
- API-first design so the system can be embedded into Siemens procurement tools later
- Pluggable risk model engine (swap scoring logic without touching agents)

---

### 3. System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Presentation Layer                          │
│  Streamlit (MVP)  →  Next.js + React (Production)               │
│  • Comparison Workspace  • Chat Interface  • Research Mode      │
│  • Dynamic Component Renderer  • Agent Activity Panel           │
└────────────────────────────┬────────────────────────────────────┘
                             │ REST / WebSocket
┌────────────────────────────▼────────────────────────────────────┐
│                  Orchestration Layer (LangGraph)                │
│  Supervisor Agent + Shared State + Checkpointing                │
└──────┬──────────────┬──────────────┬──────────────┬─────────────┘
       │              │              │              │
┌──────▼─────┐  ┌─────▼─────┐  ┌─────▼─────┐  ┌─────▼──────┐
│ Historical │  │ Real-time │  │ Live      │  │ Research   │
│ Scoring    │  │ News      │  │ Orders    │  │ Agent      │
│ Agent      │  │ Agent     │  │ Agent     │  │ (Deep)     │
└──────┬─────┘  └─────┬─────┘  └─────┬─────┘  └─────┬──────┘
       │              │              │              │
       └──────────────┴──────────────┴──────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                     Data & Knowledge Layer                      │
│  • Supplier Risk Store (DuckDB / PostgreSQL)                    │
│  • Vector Store (Chroma / pgvector) for RAG                     │
│  • Event / Audit Log                                            │
│  • Tavily Cache + Research Memory                               │
└─────────────────────────────────────────────────────────────────┘
```

**Key Design Principles for Longevity**
- Agents are pure functions of shared state where possible
- All external calls (Tavily, LLM) are behind interfaces → easy to swap providers
- Risk scoring logic is isolated in a dedicated module
- Full checkpointing and time-travel debugging via LangGraph
- Every agent action is logged with provenance

---

### 4. Agent Specifications

| Agent | Inputs | Responsibilities | Outputs |
|-------|--------|------------------|---------|
| **Historical Scoring Agent** | Full dataset + risk criteria | Load, validate, compute/refresh all scores, detect anomalies, maintain data quality flags | Updated risk profile + confidence |
| **Real-time News Agent** | Supplier name / ID + keywords | Tavily search (news + finance topics), extract signals, map to risk dimensions (Media Sentiment, Compliance, ESG, Geopolitical, etc.), attach sources | Score deltas + evidence snippets + URLs |
| **Live Orders Agent** | Operational metrics stream / simulated feed | Monitor PO volume, delivery rating, order change rate, confirmation rate; update Operational Resilience & Sourcing Risk | Operational score updates + alerts |
| **Research Agent** | Any real company name | Plan research steps → execute multi-hop Tavily (search + extract + research) → dig deeper on red flags → synthesize structured report | Full Risk Report (Executive Summary, Scorecard, Timeline, Red Flags, Sources, Recommendations) |
| **Chat / Answer Agent** | User question + selected suppliers | RAG over supplier profiles + agent outputs; generate explanations, comparisons, dynamic UI instructions | Natural answer + optional UI payload |
| **Supervisor** | User intent | Route to correct agents, manage parallel execution, merge results, decide when human review is needed | Coordinated final state |

---

### 5. Technology Stack (2026 Best Practices)

| Layer | Technology | Rationale for Long-Term Use |
|-------|------------|-----------------------------|
| Orchestration | **LangGraph** (1.x) | Stateful, checkpointable, production-proven, excellent observability |
| LLM Interface | LangChain + LiteLLM / native providers | Model-agnostic (OpenAI, Anthropic, xAI, local) |
| Search & Research | **Tavily** (Search + Extract + Research APIs) | Purpose-built for agents, high-quality results, source attribution |
| Frontend (MVP) | Streamlit + Plotly | Fastest path to polished interactive UI |
| Frontend (Production) | Next.js 15 + React + Tailwind + shadcn/ui | Long-term maintainable, beautiful, SEO-ready if needed |
| Backend API | FastAPI | High performance, automatic OpenAPI, easy auth |
| Primary Store | DuckDB (local) → PostgreSQL + pgvector | Analytics-friendly, easy migration path |
| Vector Store | Chroma (dev) / pgvector (prod) | Simple → scalable |
| Caching | Redis | Tavily results, agent memory, session state |
| Observability | LangSmith + structured logging (structlog) | Full agent traces + business metrics |
| Artifact Generation | WeasyPrint / ReportLab (PDF), python-pptx | Professional memos and briefings |
| Deployment | Docker + Docker Compose → Kubernetes | Portable and scalable |
| CI/CD | GitHub Actions | Automated testing of agents and scoring logic |

**Why this stack ages well**
- All major components are open-source or have strong enterprise support
- Clear separation allows replacing any single piece (e.g., swap Tavily for another search provider)
- LangGraph + FastAPI + PostgreSQL is a proven enterprise pattern in 2026

---

### 6. Data Strategy

- **Source of Truth**: The provided `supplier_risk_dataset.csv` (10,000 suppliers)
- Enrichment: Real-time scores are stored as overlays / versioned updates (never overwrite original historic values without audit)
- Schema: Strict typing + risk level enums (Low / Medium / High / Critical)
- Features to add for production:
  - `last_updated`, `data_freshness_score`, `confidence_score`, `source_coverage`
  - Safety-critical component flags and certification status (domain extension)
  - Multi-tier relationship table (future)

---

### 7. Implementation Roadmap

**Phase 0 – Foundation (Days 1-2)**
- Project structure, dependency management, synthetic data validation
- Load and index the 10k dataset
- Basic Historical Scoring Agent
- Streamlit skeleton with table + filters

**Phase 1 – Core Agents & Comparison UI (Days 3-5)**
- Real-time News Agent (Tavily)
- Live Orders Agent (simulated stream)
- Side-by-side comparison + radar charts + “Why risky” explanations
- Grounded chatbot answering the challenge example questions

**Phase 2 – Research Agent & Wow Features (Days 6-8)**
- Full Research Agent with planning + deep-dive loop
- Dynamic UI generation from chatbot
- Scenario simulation engine
- Auto-generated Shortlist Memo (PDF)
- Agent activity visualization panel

**Phase 3 – Hardening & Long-Term Readiness (Days 9-12)**
- Confidence scores, trends, configurable weights
- Full audit logging
- API layer (FastAPI)
- Observability (LangSmith)
- Dockerization + basic tests
- Documentation & demo script

**Phase 4 – Production Path (Post-Challenge)**
- Migrate frontend to Next.js
- PostgreSQL + proper auth
- Human-in-the-loop workflows
- Multi-tier graph expansion
- Integration adapters for Siemens systems

---

### 8. Long-Term Maintainability & Governance

- **Modularity**: Agents, scoring engine, and data access are independent packages
- **Configuration over Code**: Risk weights, Tavily parameters, LLM models, and UI themes are config-driven
- **Observability First**: Every agent run produces structured traces
- **Data Versioning**: Historic scores are immutable; new scores create new versions
- **Human Oversight**: Critical score changes or research reports can require approval
- **Testing Strategy**: Unit tests for scoring logic, integration tests for agent graphs, evaluation datasets for chatbot & research quality
- **Security & Compliance**: No PII in logs, API key management via secrets, audit trail for all decisions
- **Extensibility Points**:
  - New risk dimensions → just extend the scoring module
  - New data sources → implement a simple adapter interface
  - New agents → register with the LangGraph supervisor

---

### 9. Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Tavily rate limits / cost | Aggressive caching + fallback mock mode |
| LLM hallucination in explanations | Strict RAG + citation requirements + confidence thresholds |
| Dataset drift | Versioned scoring + monitoring of score distributions |
| Complexity explosion | Strict agent boundaries + supervisor pattern |
| Demo failure | Pre-computed research examples + offline mode |

---

### 10. Immediate Next Steps

1. Confirm Tavily API key availability (or proceed with robust mock mode)
2. Choose primary LLM provider for the demo
3. Initialize the repository with the architecture above
4. Begin Phase 0: data loading + Historical Scoring Agent + basic Streamlit UI

---

**This plan delivers a solution that not only wins the challenge but becomes a solid foundation for a real Siemens internal tool.**

Ready to start implementation on your command.  
Just say **“Build Phase 0”** or **“Start full system”** and we begin.