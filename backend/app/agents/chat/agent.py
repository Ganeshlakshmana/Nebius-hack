from __future__ import annotations

import re
from app.services.data_tools import DataTools
from app.services.component_risk import ComponentRisk, resolve_components


class ChatAgent:
    """Grounded deterministic router; answers only with rows returned by data tools."""
    def __init__(self, tools: DataTools):
        self.tools = tools

    def answer(self, message: str, shortlist: list[str] | None = None, component: str | None = None) -> dict:
        ids = list(dict.fromkeys(re.findall(r"SUPP_\d{5}", message.upper())))
        if not ids:
            ids = list(dict.fromkeys(shortlist or []))
        lower = message.lower()
        if component or resolve_components(message) or re.search(r"\b(component|part|parts)\b", lower):
            return ComponentRisk(self.tools).chat_answer(component or message, ids)
        if len(ids) > 1:
            by = "financial_health" if "financial" in lower else "total_risk"
            rows = self.tools.get_suppliers(ids)
            rows.sort(key=lambda r: float(r["Financial_Health_Score"] if by == "financial_health" else r["Total_Risk_Index"]))
            if not rows:
                return {"answer": "No matching suppliers were found in the dataset.", "components": [], "tool_calls": ["get_suppliers"], "validated": True}
            value_column = "Financial_Health_Score" if by == "financial_health" else "Total_Risk_Index"
            answer = f"Lowest {by.replace('_', ' ')} risk in this set is {rows[0]['supplierID']} ({float(rows[0][value_column]):g}); "
            answer += "; ".join(f"{r['supplierID']}: {float(r[value_column]):g}" for r in rows) + "."
            return {"answer": answer, "components": [{"type": "ranking_table", "props": {"items": rows, "metric": value_column}}],
                    "tool_calls": ["get_suppliers"], "validated": True,
                    "provenance": {"dataset_columns": ["supplierID", value_column]}}
        if len(ids) == 1 and ("why" in lower or "explain" in lower or "risk" in lower):
            explanation = self.tools.explainer.explain(ids[0])
            drivers = explanation["contributions"][:3]
            detail = "; ".join(f"{d['factor'].removesuffix('_Score').replace('_', ' ')} contributes {d['points']:+.2f} points" for d in drivers)
            return {"answer": f"{ids[0]} has Total Risk Index {explanation['total']:g} ({explanation['risk_band']}). Top peer-relative drivers: {detail}. Formula fit R²={explanation['r2']:.4f} ({explanation['mode']}).",
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
