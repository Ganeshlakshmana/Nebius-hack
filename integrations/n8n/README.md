# Railwise negotiation preparation in n8n Cloud

These workflows connect the Commercial workspace to Railwise's deterministic commercial optimizer and refresh saved contract alerts. They do not contact suppliers, send negotiation messages, interpret contract language, approve awards, or use an LLM to invent prices. Negotiation plans remain buyer-reviewed.

## Request path

Dashboard → server-side `/api/commercial` → authenticated n8n webhook → authenticated Railwise `/api/internal/commercial/evaluate` → private FastAPI optimizer → result back to dashboard.

n8n Cloud cannot reach the backend's private Docker address. The two `/api/internal/commercial/*` frontend routes are narrow, authenticated proxies to the private backend. The backend's port 8000 stays private. The daily workflow calls the same authenticated proxy for `/commercial/scan`.

## Required values

Use two independent random secrets (at least 32 characters each):

- `COMMERCIAL_API_KEY`: shared by the FastAPI backend, frontend proxy and n8n HTTP Request credentials.
- `N8N_WEBHOOK_KEY`: shared by the frontend server and the n8n Webhook credential. Keep it separate from the backend key.

Keep both secrets in the server's private `.env`; never put them in browser JavaScript, workflow JSON, GitHub, or a screenshot. `N8N_COMMERCIAL_WEBHOOK` is the production webhook URL shown by n8n after publishing.

## Setup and activation

1. Create the n8n Cloud workspace and open its editor. The marketing site is not a workspace; finish signup and apply the hackathon credit code in n8n's billing flow if prompted.
2. Set `COMMERCIAL_API_KEY` and `N8N_WEBHOOK_KEY` in `/opt/railwise/.env` on the Railwise VM. Keep the existing `PUBLIC_HOST` and provider values. Do not paste either secret into chat.
3. Import `railwise-commercial-webhook.json` into n8n. In **Dashboard request**, create/select a Header Auth credential named `Railwise dashboard → n8n`, header `X-Railwise-Key`, value `N8N_WEBHOOK_KEY`.
4. In **Evaluate commercial scenario**, set the URL to `https://YOUR-RAILWISE-PUBLIC-HOST/api/internal/commercial/evaluate`. Create/select a different Header Auth credential named `Railwise n8n → API`, header `X-Railwise-Key`, value `COMMERCIAL_API_KEY`.
5. Save, test with a synthetic case, then **Publish** the webhook workflow. Copy its Production URL (not the Test URL). Set that URL as `N8N_COMMERCIAL_WEBHOOK` in `/opt/railwise/.env`.
6. Redeploy/restart Railwise so the frontend receives the three commercial variables. Then use the dashboard's Commercial workspace to run the same synthetic case and confirm a report returns. If a request fails, the UI must show an error; it must not claim success.
7. Import `railwise-contract-monitor.json`. Use the same `Railwise n8n → API` credential and set its URL to `https://YOUR-RAILWISE-PUBLIC-HOST/api/internal/commercial/scan`. Run it manually once and confirm `status: completed`.
8. Publish and activate the daily monitor only after the manual run succeeds. It is scheduled for 08:00 Europe/Berlin. Leave the error workflow inactive unless you have separately assigned it in each workflow's settings.

The exact workspace URL is needed to complete steps 3–5. No workspace has been connected to this project yet, so the templates are prepared but not imported, activated, or live.

## Safe test case

Use `mode: "simulation"`, two shortlisted supplier IDs, synthetic offers, a future delivery date, and clearly labelled `DEMO` quote references. The optimizer validates quote comparability, date/lead-time feasibility, capacity, minimum order, risk ceiling, and contract gates. It returns modeled allocations and buyer-entered contract alerts. A demo result is not a negotiated saving, verified supplier capability, legal conclusion, or award recommendation.

## Limits and data handling

- Alerts appear in the dashboard; email, Slack and supplier notifications are not configured.
- Contract records and quote fields are synthetic or buyer-entered. No contract-document extraction is implemented.
- Public search must not be used to infer private contractual relationships.
- Only one comparable quote per supplier, one currency/unit, integer demand, linear unit prices, fixed fees, MOQ and capacity are modeled.
- n8n execution history can contain quote and contract data. Restrict workspace access and retention before using non-demo commercial records.
