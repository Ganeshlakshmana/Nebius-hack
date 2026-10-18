from __future__ import annotations

import json
import re
from app.services.data_tools import DataTools
from app.services.component_risk import ComponentRisk, resolve_components


class ChatAgent:
    """Grounded deterministic router; answers only with rows returned by data tools."""
    def __init__(self, tools: DataTools):
        self.tools = tools

    def answer(self, message: str, shortlist: list[str] | None = None, component: str | None = None) -> dict:
        result = self._route(message, shortlist, component)
        unsupported = self.unsupported_ids(result)
        if unsupported:
            result["validated"] = False
            result["validation_errors"] = [f"Supplier ID not present in tool output: {i}" for i in unsupported]
        return result

    @staticmethod
    def unsupported_ids(result: dict) -> list[str]:
        """Validator: every supplier ID named in the answer must appear in this turn's tool output."""
        evidence = json.dumps({k: v for k, v in result.items() if k != "answer"}, default=str)
        return sorted({i for i in re.findall(r"SUPP_\d{5}", result.get("answer", "")) if i not in evidence})

    def _route(self, message: str, shortlist: list[str] | None = None, component: str | None = None) -> dict:
        ids = list(dict.fromkeys(re.findall(r"SUPP_\d{5}", message.upper())))
        if not ids:
            ids = list(dict.fromkeys(shortlist or []))
        lower = message.lower()
        ids = list(dict.fromkeys(i.strip().upper() for i in ids))
        if len(ids) > 20:
            return {"answer": "Select at most 20 suppliers.", "status": "clarification_required", "components": [], "tool_calls": [], "validated": True}
        if ids:
            rows = self.tools.get_suppliers(ids)
            missing = sorted(set(ids) - {r["supplierID"] for r in rows})
            if missing:
                return {"answer": "Some supplier IDs were not found. Correct the IDs before comparing; no partial ranking was produced.",
                        "status": "clarification_required", "unknown_ids": missing, "components": [], "tool_calls": ["get_suppliers"], "validated": True}
        if re.search(r"\b(certified|certification|iso|approved|price|cheapest|capacity|manufactures|guarantee|guaranteed)\b", lower):
            return {"answer": "The supplied dataset does not verify component capability, certification, approval, price or available capacity. Request supplier evidence before an award decision. I can screen supplier risk using the available scores.",
                    "status": "insufficient_evidence", "components": [], "tool_calls": ["get_suppliers"] if ids else [], "validated": True}
        if component or resolve_components(message) or re.search(r"\b(component|part|parts)\b", lower):
            return ComponentRisk(self.tools).chat_answer(component or message, ids)
        if len(ids) > 1:
            metric_columns = {"financial": "Financial_Health_Score", "credit": "Credit_Rating_Score", "quality": "Quality_Risk_Score", "cyber": "Digital_Security_Score", "digital": "Digital_Security_Score", "compliance": "Compliance_Risk_Score", "safety": "Safety_Incident_Score"}
            mentioned = list(dict.fromkeys(col for term, col in metric_columns.items() if term in lower))
            if len(mentioned) > 1:
                return {"answer": "Choose one risk metric, or select a component for a weighted comparison.", "status": "clarification_required", "components": [], "tool_calls": [], "validated": True}
            value_column = mentioned[0] if mentioned else "Total_Risk_Index"
            by = value_column.removesuffix("_Score").replace("_", " ")
            rows = self.tools.get_suppliers(ids)
            rows.sort(key=lambda r: (float(r[value_column]), r["supplierID"]))
            if not rows:
                return {"answer": "No matching suppliers were found in the dataset.", "components": [], "tool_calls": ["get_suppliers"], "validated": True}
            winners = [r["supplierID"] for r in rows if r[value_column] == rows[0][value_column]]
            answer = f"Lowest {by.replace('_', ' ')} risk in this set is {', '.join(winners)} ({float(rows[0][value_column]):g}); "
            answer += "; ".join(f"{r['supplierID']}: {float(r[value_column]):g}" for r in rows) + "."
            return {"answer": answer, "components": [{"type": "ranking_table", "props": {"items": rows, "metric": value_column}}],
                    "tool_calls": ["get_suppliers"], "validated": True,
                    "provenance": {"dataset_columns": ["supplierID", value_column]}}
        if len(ids) == 1 and ("why" in lower or "explain" in lower or "risk" in lower):
            explanation = self.tools.explainer.explain(ids[0])
            drivers = explanation["contributions"][:3]
            detail = "; ".join(f"{d['factor'].removesuffix('_Score').replace('_', ' ')} contributes {d['points']:+.2f} points" for d in drivers)
            return {"answer": f"{ids[0]} has Total Risk Index {explanation['total']:g} ({explanation['risk_band']}). Estimated peer-relative drivers (fitted model; original formula is not supplied): {detail}. Formula fit R²={explanation['r2']:.4f} ({explanation['mode']}).",
                    "components": [{"type": "contribution_bars", "props": explanation}],
                    "tool_calls": ["explain_score"], "validated": True, "provenance": explanation["provenance"]}
        if ids:
            rows = self.tools.get_suppliers(ids)
            return {"answer": "Supplier data is available in the attached dataset card(s).", "components": [{"type": "supplier_card", "props": {"items": rows}}],
                    "tool_calls": ["get_suppliers"], "validated": True,
                    "provenance": {"dataset_columns": list(rows[0]) if rows else []}}
        result = self.tools.filter_suppliers(limit=10, sort_by="total_risk", order="desc")
        return {"answer": "I can answer dataset questions when you provide supplier IDs or ask for a ranking/filter. Here are the 10 highest TRI suppliers from the dataset.",
                "components": [{"type": "ranking_table", "props": result}], "tool_calls": ["filter_suppliers"],
                "validated": True, "provenance": result["provenance"]}
