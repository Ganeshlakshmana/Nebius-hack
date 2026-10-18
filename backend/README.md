# FastAPI backend

The API loads the immutable supplier CSV from `data/supplier_risk_dataset.csv` by default (or `DATASET_PATH`) and stores operational events, alerts, search cache, research reports and audit records in SQLite under `backend/app/data/`.

## Run locally

From the repository root, install with `python -m pip install -e backend`, copy `.env.example` to `.env`, and set private internal credentials. Start with `python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000`. The OpenAPI UI is at `http://127.0.0.1:8000/docs`; health is `http://127.0.0.1:8000/health`.

The Vite frontend runs at `http://127.0.0.1:5173`; that origin is allowed by the API’s CORS configuration. The current frontend still reads `public/suppliers.json`; wiring each frontend view to the API is a separate integration change.

## Credentials

`INTERNAL_AGENT_API_KEY` identifies signed inter-agent messages and `INTERNAL_AGENT_SECRET` signs/verifies them with HMAC-SHA256. Keep `.env` private and out of Git. `TAVILY_API_KEY` is optional; live searches require setting `OFFLINE_MODE=false`. No LLM provider is currently wired into chat or research triage, so those outputs remain deterministic/partial.

## Tests

From the `backend` directory, run `python -m pytest tests -q`.
