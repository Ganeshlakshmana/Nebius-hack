# Railwise: demo script (about 8 minutes)

**Audience:** hackathon judges · **DO** = click or type · **SAY** = speak

## Prepare before recording
- Pull the latest `main`. Start the backend (port 8000) and frontend, then open the app (http://127.0.0.1:5173 with `npm run dev`).
- For live research, set `OFFLINE_MODE=false`, a Tavily key, and the Nebius Token Factory key with `LLM_MODEL=nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B`.
- Shortlist **SUPP_00012, SUPP_00450, SUPP_00731**.
- Run Research for `Knorr-Bremse` with domain `knorr-bremse.com` and component `brake pads`. Let it finish (up to 2 minutes) and show the saved result. Don't describe it as running live.
- Prepare a Sourcing brief (`Brake pads`, quantity 500, a future delivery date) and pre-fill verified evidence for SUPP_00731.
- Download the packets in advance as a backup. If you use them, say they were generated earlier.
- Use demo-only data. Don't show credentials.

---

## 1. The buyer's problem (0:00 – 0:30)
**SAY:** "Siemens buys train components from thousands of suppliers. A low risk score doesn't prove a company can make your part, and a low price doesn't mean a good deal. Railwise takes a buyer from risk, to sourcing, to contracts and negotiation, to research. Every number traces back to its source."

## 2. Overview: four risk lenses (0:30 – 1:00)
**DO:** Open **Overview**. Click the train's **Quality**, **Operations**, **Financial** and **Cybersecurity** areas.

**SAY:** "These are the four risks a rail buyer cares about most, mapped onto the train. Each one opens all 10,000 suppliers ranked on that risk. At the top are the portfolio totals, including 384 critical suppliers."

## 3. Suppliers: every supplier, every risk (1:00 – 1:45)
**DO:** Open **Suppliers**. Search, filter by risk level and minimum delivery rating, then sort. Open **SUPP_00018**.

**SAY:** "Each supplier has 20 risk factors, plus its delivery and order history. SUPP_00018 has a Total Risk Index of 80, which is critical."

**DO:** Ask in chat: `Why is the Total Risk Index of SUPP_00018 so high?`

**SAY:** "The original formula wasn't supplied, so we fitted one to the historic data. It reproduces the index with an R² of 0.998. These driver contributions are estimates from that fit: compliance, operational resilience and governance."

## 4. Compare (1:45 – 2:15)
**DO:** Open **Compare** with the three suppliers. Ask: `Which of SUPP_00012, SUPP_00450 and SUPP_00731 has the lowest financial risk?`

**SAY:** "Up to 20 suppliers side by side on every risk. The answer comes straight from the data: SUPP_00731 at 53, SUPP_00012 at 54, SUPP_00450 at 65. Lower means lower risk."

## 5. Sourcing: any component, your requirements (2:15 – 3:30)
**DO:** Open **Sourcing** with the prepared brief: component, specification, quantity 500, delivery date, the four mandatory requirements, and quality / operations / compliance weights. Generate the decision packet.

**SAY:** "We can source any component against our own specification, quantity and delivery date. Suppliers are scored on their quality, operations and compliance history. SUPP_00731 leads at 55.1, but missing qualification evidence stops a recommendation becoming an approval."

**DO:** Show SUPP_00731 with verified evidence: **Ready for authorized review**. Then mark one requirement failed for SUPP_00012: **Blocked**.

**SAY:** "With reviewed evidence, SUPP_00731 is ready for authorized review. A failed mandatory check blocks a supplier whatever its score. Demo or expired evidence never counts."

## 6. Commercial: quotes, contracts and negotiation (3:30 – 5:30)
**DO:** Open **Commercial**. Click **Load synthetic quotes for 3 supplier(s)**. Point to the **SYNTHETIC SCENARIO** label.

**SAY:** "Next comes the commercial side. These are the quotes we got back from our request for quotation. Here they're synthetic, and clearly labelled. Each quote has a unit price, fixed cost, capacity, minimum order, lead time, payment terms and validity date."

**DO:** For each supplier, set the **Contract record** (**Existing agreement**, **No agreement confirmed** or **Unknown**), **Contract end**, **Notice deadline** and **Obligations / restrictions**. Set **Maximum share per supplier (%)** and **Maximum supplier risk**. Click **Compare sets and prepare negotiation**.

**SAY:** "Before negotiating, we check the contracts we already have with these suppliers: is there an agreement, when does it end, when is the notice deadline, and is there a restriction on switching? We also set our own limits, such as no more than 60% from one supplier and a maximum risk level."

**DO:** Show **Top purchasing options**, **Candidate checks**, and **Contract and opportunity alerts**.

**SAY:** "Railwise tests every combination of up to three suppliers against price, capacity, minimum order, delivery date, concentration and risk. It returns the five cheapest feasible options. In our run, that was a 60/40 split for EUR 10,920. Every quote that's excluded shows why: expired, too slow for our delivery date, too risky, or not comparable. Contract alerts flag notice deadlines within 60 days, agreements ending within 90 days, and agreements that end before our delivery."

**DO:** Open **Negotiation preparation**, then click **Export assumptions and negotiation brief**.

**SAY:** "For each supplier, we get a negotiation brief: whether a realistic fallback exists and what it would cost, plus the questions to raise: volume tiers, payment timing, delivery slots, warranty, and switching costs. It prepares the buyer for the conversation. It never sends messages or commits to anything on its own."

**DO:** Show **Saved contract monitor** → **Refresh monitored alerts**.

**SAY:** "For ongoing monitoring, we've built n8n workflows. One connects this screen to the backend through an authenticated webhook. A daily scan rechecks saved cases every morning and raises contract alerts. A third workflow makes any failure visible. The workflow templates are ready, and go live once the app is deployed on a public HTTPS address."

## 7. Research: any real company (5:30 – 6:45)
**DO:** Open the prepared Knorr-Bremse report. Show search coverage, a source card with **Inspect source ↗**, the Nemotron findings and **Next actions before choosing this supplier**.

**SAY:** "Research investigates any real company on the web. Tavily searches public sources and extracts the pages. Each source is labelled: does it match the official domain, is it an incident or just policy text, and how recent is it? Incidents trigger follow-up searches.
Then NVIDIA's Nemotron model, running on Nebius Token Factory, reviews the top excerpts. Every finding has to quote the exact source text and cite a real source, or it's rejected and we fall back to the rule-based review. Nemotron's findings are advisory: they never change a score or approve a supplier."

## 8. Live operations (6:45 – 7:15)
**DO:** In the API docs (http://127.0.0.1:8000/docs), run `POST /operations/scenario` with `SUPP_00001` and `{"action": "start"}`.

**SAY:** "On top of the historic data runs a simulated live feed. SUPP_00001's deliveries drop from 84% to 61%, putting €141,238 at risk. The news, research and scenario agents react, and replacement suppliers are ranked. Every hand-off is signed and logged."

## 9. Defensible hand-off (7:15 – 8:00)
**DO:** Download the sourcing **decision packet** and the shortlist **memo**.

**SAY:** "The buyer leaves with the brief, the screening, open requirements, quote comparison, contract alerts, negotiation brief and evidence references. Six agents, each with documented guardrails, and a test suite that runs on every push. Railwise supports an authorized review. It never awards a contract automatically. Thank you."

---

## Present limitations honestly
- **Chat** answers through fixed, data-grounded routes. **Nemotron** reviews research excerpts only; a validated quote doesn't prove its interpretation is right.
- **Quotes and contracts** in the Commercial screen are synthetic and buyer-entered. There's no legal interpretation or document verification. A modeled option isn't a negotiated price or a guaranteed saving.
- **No request for quotation or negotiation message is sent automatically.** The app prepares the buyer; people contact suppliers.
- **n8n templates** are not yet imported or tested in n8n Cloud; they need a public HTTPS deployment.
- **Operations data** is simulated. **Company identity** and **reviewer statements** are not independently verified.
- Public deployment, jury login and the screen recording are still submission tasks.

## Say this, not that
| Avoid | Say |
|---|---|
| "It's trained on historic data" | "The formula is fitted to historic data" |
| "Research or Nemotron updates the risk score" | "Research gives linked evidence and actions; scores don't change" |
| "n8n negotiates with suppliers" | "n8n monitors contracts; Railwise prepares the negotiation" |
| "It saves EUR X" | "The lowest modeled cost is EUR X under these assumptions" |
| "It awards the contract" | "It shows who's ready for authorized review" |
