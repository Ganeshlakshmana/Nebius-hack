# Contract-aware negotiation workflows

Status: importable templates prepared; NOT imported, activated or tested in n8n Cloud.
The frontend Commercial screen and FastAPI calculation run locally without n8n.

## What runs where

Dashboard → server-side /api/commercial → authenticated n8n webhook → authenticated FastAPI /commercial/evaluate → result back to dashboard.

n8n hosts orchestration, not the React frontend or Python optimizer. Keep the tested optimizer in FastAPI. It uses no model tokens.
The daily schedule calls /commercial/scan; saved cases are recalculated and alerts stored for the dashboard's “Refresh monitored alerts” button.

## Configure after Cloud signup

1. Deploy Railwise/FastAPI on a reachable HTTPS host. localhost on the Mac is not reachable from n8n Cloud.
2. Set a random COMMERCIAL_API_KEY on both the backend and frontend server. Once configured, evaluation, alert reading and scan endpoints require X-Railwise-Key. Scan is disabled without it. Other app endpoints still need the planned deployment-wide jury authentication.
3. Import railwise-commercial-webhook.json. Replace the placeholder backend URL in its HTTP Request node.
4. Create two n8n Header Auth credentials, both with header name X-Railwise-Key, but different secret values:
   - Backend credential: matches COMMERCIAL_API_KEY.
   - Webhook credential: a separate random secret for dashboard-to-n8n calls.
   Replace the placeholder credential references by selecting the corresponding saved credentials in each node.
5. Test the webhook with synthetic data. It returns the backend HTTP status and JSON. Invalid input must remain an error, not a successful “workflow started” response.
6. Publish the webhook workflow. Set N8N_COMMERCIAL_WEBHOOK to its production HTTPS URL and N8N_WEBHOOK_KEY to the webhook secret on the frontend server only. Restart the frontend.
7. Import railwise-contract-monitor.json. Configure its backend URL and credential. It runs at 08:00 Europe/Berlin when activated; leave inactive until a successful manual execution.
8. Import railwise-error-handler.json, then select it as the Error Workflow in both main workflow settings. It deliberately records a visible failed execution. It does not send email or Slack messages.
9. Manually execute the monitor and confirm /commercial/alerts shows a fresh scanned_at. Break the backend credential in a test copy to verify visible failure and retries, then restore it. Only then activate the daily schedule.

## Behavior and limitations

- Alerts currently appear in the dashboard; no email, Slack or supplier contact is configured.
- No contract document extraction. Contract terms and deadlines are manually entered.
- The Commercial UI is explicitly synthetic simulation. The API additionally supports mode: review, which requires actual qualification evidence, non-demo offers and reviewed contract scope/constraints.
- A single comparable quote per supplier; one currency and unit, integer demand, linear unit price, fixed fees, MOQ and capacity.
- Up to three suppliers per set. Exhaustive subsets with cheapest feasible allocation under these assumptions; five cheapest options returned.
- Quote validity is checked for an order placed today, not guaranteed through delivery.
- “No agreement confirmed” differs from “unknown”. Existing agreements do not establish engineering qualification.
- Notice dates are user-entered; the system does not infer legal deadlines from prose.
- A case key groups component + application + supplier IDs + mode. Re-evaluation replaces that case's current snapshot.
- Scans cover the 100 most recently updated cases. Repeated scans replace snapshots rather than generating duplicate notification rows. Last scan time remains visible; failed scans return 503.
- Synthetic qualification is assumed only for scenario arithmetic. The actual gate status stays visible.
- A modeled alternative is not an agreed price, guaranteed saving, verified capacity or procurement authorization.
- Do not use public web search to infer private contractual relationships.
- n8n execution records may contain commercial data. Configure access, execution retention and redaction before using real contracts.

## Negotiation preparation

Prepare objectives, non-negotiables, evidence, permitted concessions and a realistic fallback before approaching a supplier.
Discuss total cost, delivery slots, payment timing, warranty, acceptance tests, changes and lifecycle support.
A new supplier's lower price is not leverage unless its scope, capacity, qualification and transition obligations have been checked.

References:
- https://1prd-dxp.cips.org/intelligence-hub/negotiation
- https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.webhook/
- https://docs.n8n.io/flow-logic/error-handling/
