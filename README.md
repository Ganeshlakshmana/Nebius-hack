# Railwise — Siemens Supplier Risk Intelligence

Frontend for the Nebius hackathon Siemens challenge. Built with React, TypeScript, shadcn/ui and a Vinext/Vite starter supporting Next.js-style routes.

## Run locally

Requires Node.js 22.13+ and npm.

```sh
npm run install:ci
npm run dev
```

Open http://127.0.0.1:5173/.

```sh
npx tsc --noEmit
npm run build
```

## Run the backend API

The FastAPI service is in `backend/`. From the repository root, install it with `python -m pip install -e backend`, copy `.env.example` to `.env` and set private credentials, then start `python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000`. API docs are at `http://127.0.0.1:8000/docs`; health is at `http://127.0.0.1:8000/health`.

The API loads `data/supplier_risk_dataset.csv` and permits the Vite frontend origin `http://127.0.0.1:5173`. **The current frontend still loads `public/suppliers.json`; frontend-to-API calls have not yet been wired.** See [backend/README.md](backend/README.md) for the backend setup and environment settings. Do not commit `.env` or provider credentials.

## Implemented

- Siemens-inspired midnight-blue and cyan interface.
- CSS 3D conceptual train with drag-to-orbit, reset and exploded assembly controls.
- Four risk lenses calculated from the supplied 10,000-supplier dataset.
- Search, risk and delivery filters, numeric sorting and pagination.
- Persistent local shortlist and comparison of up to 20 suppliers.
- Supplier risk profiles and custom preference-weight scenarios.
- Backend-connected chat with component-specific supplier risk cards and Markdown shortlist memo export.
- Research brief and agent integration-status interfaces.

## Current limitations

The FastAPI backend supports component-specific screening and optional Tavily searches. Frontend chat is connected; research UI and live-operations UI are not yet wired. General LLM chat is not implemented. The train is a conceptual illustration, not a Siemens CAD model or a supplier-to-component mapping. The supplied dataset has no component mapping, historical series or Total Risk Index weights. The original Total Risk Index is preserved.

TypeScript validation passed for the redesign. Visual QA and deployment of the 3D redesign were not completed before this handoff.

## Source and data

- `plan.md`: original user-provided implementation plan, preserved.
- `data/supplier_risk_dataset.csv`: original 10,000-row challenge dataset.
- `data/risk_criteria_description.md`: original criteria descriptions.
- `public/suppliers.json`: compact column-and-row representation used by the frontend.
- `app/page.tsx`: workspace and data interactions.
- `components/rail-scene.tsx`: interactive CSS 3D train and risk lenses.
- `app/siemens.css`: Siemens-inspired visual theme.

All risk scores use 0 = no risk and 100 = maximum risk. Delivery and confirmation rates retain their operational meaning.

## Hosting

The starter includes Sites/Cloudflare integration. `.openai/hosting.json` identifies the registered development Site, but this repository has not been deployed. Local execution uses the portable profile automatically. Keep credentials in ignored environment files. Component chat requires FastAPI on port 8000; it does not require an LLM API key. See backend/README.md for both-server setup and component analysis examples.

UI components retain their upstream source and license notices.
