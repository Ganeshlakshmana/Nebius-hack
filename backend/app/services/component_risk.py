"""Transparent component-priority screening, not engineering qualification."""
from __future__ import annotations

import math
import re
from app.services.decision_brief import decision_brief


# Illustrative procurement priorities, not Siemens-approved engineering weights.
PROFILES = {
    "braking": ("Braking systems", ["brake", "brakes", "braking", "brake pad", "brake pads", "brake disc"],
                {"Quality_Risk_Score": .35, "Safety_Incident_Score": .25, "Compliance_Risk_Score": .2, "Operational_Resilience_Score": .2},
                ["Component-specific braking performance and test evidence", "Traceability and defect containment", "Applicable approvals and production capacity"]),
    "traction": ("Traction motors & drives", ["traction", "traction motor", "motor", "motors", "inverter", "inverters"],
                 {"Quality_Risk_Score": .3, "Operational_Resilience_Score": .3, "Sub_Tier_Visibility_Score": .2, "Financial_Health_Score": .2},
                 ["Required power, thermal and duty-cycle performance", "Critical material and sub-tier availability", "Repair, spares and lifecycle support"]),
    "wheelsets": ("Wheelsets & bearings", ["wheelset", "wheelsets", "wheel", "wheels", "axle", "axles", "bearing", "bearings", "bogie", "bogies"],
                  {"Quality_Risk_Score": .4, "Safety_Incident_Score": .3, "Compliance_Risk_Score": .15, "Operational_Resilience_Score": .15},
                  ["Fatigue and material inspection evidence", "Batch traceability and inspection records", "Fit with vehicle loads and operating conditions"]),
    "signalling": ("Signalling & control electronics", ["signalling", "signaling", "signal", "control system", "control systems", "electronics", "tcms"],
                   {"Digital_Security_Score": .3, "Quality_Risk_Score": .25, "Compliance_Risk_Score": .25, "Operational_Resilience_Score": .2},
                   ["Required safety assurance and system compatibility", "Secure update and vulnerability response process", "Software lifecycle and obsolescence support"]),
    "doors": ("Passenger doors", ["door", "doors", "door system", "door systems"],
              {"Quality_Risk_Score": .35, "Safety_Incident_Score": .3, "Operational_Resilience_Score": .2, "Compliance_Risk_Score": .15},
              ["Entrapment protection and emergency release testing", "Cycle reliability and vehicle integration", "Spares availability and maintenance requirements"]),
    "hvac": ("HVAC systems", ["hvac", "air conditioning", "ventilation", "heating"],
             {"Quality_Risk_Score": .3, "Operational_Resilience_Score": .3, "Environmental_Exposure_Score": .2, "ESG_Performance_Score": .2},
             ["Climate envelope and required cooling/heating capacity", "Energy use and maintainability evidence", "Refrigerant and applicable compliance requirements"]),
    "batteries": ("Batteries & energy storage", ["battery", "batteries", "energy storage"],
                  {"Safety_Incident_Score": .3, "Quality_Risk_Score": .25, "Sub_Tier_Visibility_Score": .25, "Compliance_Risk_Score": .2},
                  ["Thermal safety and protection testing", "Cell traceability and material sourcing", "Lifecycle, warranty and recycling arrangements"]),
}


def resolve_components(text: str) -> list[str]:
    normalized = re.sub(r"[-_]", " ", text.lower())
    normalized = re.sub(r"\bsets?\s+of\s+breaks?\b", "brakes", normalized)
    # Speech-to-text commonly turns "brake" into "break". Correct it only
    # when the following noun makes the intended rail component unambiguous.
    normalized = re.sub(r"\bbreak(s)?\s+(?=(?:wheel|pad|disc|shoe|system)s?\b)", r"brake\1 ", normalized)
    # Brake wheels are part of the braking request; do not also classify them
    # as generic wheelsets and create an avoidable ambiguity.
    if re.search(r"\bbrake(s)?\s+wheel(s)?\b", normalized):
        return ["braking"]
    return [key for key, (_, aliases, _, _) in PROFILES.items()
            if any(re.search(r"\b" + re.escape(alias) + r"\b", normalized) for alias in [key, *aliases])]


def catalog() -> list[dict]:
    return [{"id": key, "name": p[0], "weights": p[2], "qualification_checks": p[3]}
            for key, p in PROFILES.items()]


class ComponentRisk:
    def __init__(self, tools):
        self.tools = tools

    def analyze(self, component: str, ids: list[str]) -> dict:
        matched = resolve_components(component)
        if len(matched) != 1:
            return {"status": "clarification_required", "message": "Choose one supported component for this analysis.", "supported_components": catalog()}
        key = matched[0]
        label, _, weights, checks = PROFILES[key]
        ids = list(dict.fromkeys(s.upper().strip() for s in ids))
        auto_screen = not ids
        if len(ids) > 20:
            return {"status": "clarification_required", "message": "Select at most 20 supplier IDs."}
        rows = self.tools.get_all_suppliers() if auto_screen else self.tools.get_suppliers(ids)
        missing = sorted(set(ids) - {r["supplierID"] for r in rows})
        if missing:
            return {"status": "clarification_required", "message": "Some supplier IDs were not found; no partial ranking was produced.", "unknown_ids": missing}
        items = []
        for row in rows:
            factors, unavailable = [], []
            for col, weight in weights.items():
                raw = row.get(col)
                try:
                    score = float(raw)
                    valid = math.isfinite(score) and 0 <= score <= 100
                except (TypeError, ValueError):
                    valid = False
                if not valid:
                    unavailable.append(col)
                    continue
                factors.append({"column": col, "score": score, "weight": weight,
                                "contribution": round(score * weight, 4)})
            score = None if unavailable else round(sum(f["score"] * f["weight"] for f in factors), 2)
            concerns = [f for f in factors if f["score"] >= 75]
            items.append({"supplier_id": row["supplierID"], "company": row["Supplier Name"],
                          "component_score": score, "original_total_risk": row["Total_Risk_Index"],
                          "qualification_status": "unverified", "factors": sorted(factors, key=lambda f: -f["contribution"]),
                          "critical_factors": concerns, "missing_metrics": unavailable,
                          "decision": "Insufficient data" if unavailable else "Review critical factors" if concerns else "Continue component due diligence",
                          "required_checks": checks})
        items.sort(key=lambda x: (x["component_score"] is None, x["component_score"] if x["component_score"] is not None else math.inf, x["supplier_id"]))
        first_rank = {}
        for index, item in enumerate(items, start=1):
            if item["component_score"] is None:
                item["rank"] = None
            else:
                item["rank"] = first_rank.setdefault(item["component_score"], index)
        candidate_count = len(items)
        if auto_screen:
            items = items[:20]
        brief = decision_brief(items, weights)
        return {"decision_brief": brief, "status": "complete", "component": label, "component_id": key, "items": items,
                "candidate_count": candidate_count,
                "weights": weights, "model_version": "component-screening-v1",
                "methodology": "Weighted sum of supplier-level risk scores. Lower is better. Illustrative application-defined weights, not Siemens-approved or component test results.",
                "limitations": ["Component capability, certifications, price, capacity and supplier-to-part mappings are absent from the dataset.",
                                "This screens supplier risk for a component priority; it does not establish component suitability or safety.",
                                "Original Total Risk Index is preserved. Critical factors remain visible regardless of the weighted average."],
                "provenance": {"dataset": self.tools.data.csv_path.name, "columns": list(weights)}}

    def chat_answer(self, component: str, ids: list[str]) -> dict:
        result = self.analyze(component, ids)
        if result["status"] != "complete":
            return {"answer": result["message"], "components": [], "validated": True, "status": result["status"],
                    "tool_calls": ["component_risk"], "component_analysis": result}
        lines = [f"{result['component']} — risk-ranked {len(result['items'])} of {result['candidate_count']} supplier records (lower is better)."]
        for item in result["items"]:
            factors = ", ".join(f"{f['column'].removesuffix('_Score').replace('_', ' ')} {f['score']:g}" for f in item["factors"][:2])
            lines.append(f"{item['company']} ({item['supplier_id']}): {item['component_score'] if item['component_score'] is not None else 'unavailable'}/100. {item['decision']}. Main weighted factors: {factors}.")
        lines.append("Qualification and component supply capability are unverified. The dataset has no part-to-supplier mapping, capacity, quote, or certification evidence; this is a risk-priority shortlist, not proof these companies supply the part. Review the required checks in each card.")
        return {"answer": "\n\n".join(lines), "components": [{"type": "component_risk", "props": result}],
                "component_analysis": result, "supplier_ids": [item["supplier_id"] for item in result["items"]],
                "validated": True, "tool_calls": ["get_suppliers", "component_risk"], "provenance": result["provenance"]}
