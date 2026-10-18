# FastAPI backend

The API loads the immutable supplier CSV from `data/supplier_risk_dataset.csv` by default (or `DATASET_PATH`) and stores operational events, alerts, search cache, research reports and audit records in SQLite under `backend/app/data/`.

## Run locally

From the repository root, install with `python -m pip install -e backend`, copy `.env.example` to `.env`, and set private internal credentials. Start with `python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000`. The OpenAPI UI is at `http://127.0.0.1:8000/docs`; health is `http://127.0.0.1:8000/health`.

The Vite frontend runs at `http://127.0.0.1:5173`. Chat uses its server-side `/api/chat` proxy to this backend (`BACKEND_URL`, default `http://127.0.0.1:8000`). The explorer still reads `public/suppliers.json`; research UI and other views are not yet connected to the API. Start both servers for chat.

## Component-specific decisions

Ask: `Compare brake pads for SUPP_00012, SUPP_00450 and SUPP_00731`, or select a component in the chat panel and ask about your shortlist.

- `GET /components`: supported profiles, weights and qualification checks.
- `POST /components/analyze`: `{ "component": "brake pads", "supplier_ids": ["SUPP_00012", "SUPP_00450"] }`.
- `POST /chat`: detects supported parts in natural language; optional `component` overrides detection.
- `POST /research`: accepts optional `component` to focus real-company searches on capability, testing, recalls and lifecycle support. Search snippets remain untriaged; they are not proof of qualification.

Seven profiles cover braking, traction, wheelsets/bearings, signalling/control electronics, passenger doors, HVAC and batteries. Weights in `app/services/component_risk.py` are **illustrative application defaults, not Siemens-approved engineering rules**. The normalized weighted sum operates on supplier-level scores, preserves original Total Risk Index values and shows critical factors separately. Rankings support ties. Missing metrics produce no score; unknown IDs and ambiguous/unsupported components require clarification. No anonymous supplier is linked automatically to a real company.

Every company card includes factor scores, weights, critical concerns and required component checks. Component capability, certifications, capacity and part mappings remain unverified because the input data does not contain them.

## Credentials

`INTERNAL_AGENT_API_KEY` identifies signed inter-agent messages and `INTERNAL_AGENT_SECRET` signs/verifies them with HMAC-SHA256. Keep `.env` private and out of Git. `TAVILY_API_KEY` is optional; live searches require setting `OFFLINE_MODE=false`. No LLM provider is currently wired into chat or research triage, so those outputs remain deterministic/partial.

## Tests

From the `backend` directory, run `python -m pytest tests -q`.
