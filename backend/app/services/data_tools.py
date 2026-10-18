from __future__ import annotations

import math
from typing import Any
from app.db.duckdb_store import SupplierStore
from app.db.sqlite_store import AppStore
from app.services.explainer import ScoreExplainer


SORT_COLUMNS = {
    "total_risk": '"Total_Risk_Index"', "financial_health": '"Financial_Health_Score"',
    "financial": '"Financial_Health_Score"', "credit": '"Credit_Rating_Score"',
    "quality": '"Quality_Risk_Score"', "cyber": '"Digital_Security_Score"',
    "compliance": '"Compliance_Risk_Score"', "safety": '"Safety_Incident_Score"',
    "po_volume_eur": '"Purchase Order Volume (EUR)"', "delivery_rating": '"Supplier Delivery Rating"',
    "supplier_name": '"Supplier Name"',
}


class DataTools:
    def __init__(self, data: SupplierStore, app_store: AppStore, explainer: ScoreExplainer):
        self.data, self.app_store, self.explainer = data, app_store, explainer

    def get_suppliers(self, ids: list[str]) -> list[dict[str, Any]]:
        if not ids:
            return []
        marks = ",".join("?" for _ in ids)
        return self.data.query(f'SELECT * FROM suppliers WHERE "supplierID" IN ({marks})', ids)

    def get_all_suppliers(self) -> list[dict[str, Any]]:
        """Read the supplied snapshot for bounded, in-memory screening (10k rows)."""
        return self.data.query('SELECT * FROM suppliers')

    def filter_suppliers(self, *, min_tri: float | None = None, max_tri: float | None = None,
                         risk_band: str | None = None, sourcing_risk_level: str | None = None,
                         complexity: str | None = None, min_po: float | None = None,
                         max_po: float | None = None, sort_by: str = "total_risk",
                         order: str = "desc", limit: int = 50, offset: int = 0) -> dict:
        clauses, params = [], []
        if min_tri is not None: clauses.append('"Total_Risk_Index" >= ?'); params.append(min_tri)
        if max_tri is not None: clauses.append('"Total_Risk_Index" <= ?'); params.append(max_tri)
        if risk_band:
            clauses.append('lower("Total_Risk_Index_Level") = ?'); params.append(risk_band.lower())
        if sourcing_risk_level:
            clauses.append('lower("Sourcing Risk Level") = ?'); params.append(sourcing_risk_level.lower())
        if complexity:
            clauses.append('lower("Supply Chain Complexity") = ?'); params.append(complexity.lower())
        if min_po is not None: clauses.append('"Purchase Order Volume (EUR)" >= ?'); params.append(min_po)
        if max_po is not None: clauses.append('"Purchase Order Volume (EUR)" <= ?'); params.append(max_po)
        where = " WHERE " + " AND ".join(clauses) if clauses else ""
        sort_column = SORT_COLUMNS.get(sort_by, SORT_COLUMNS["total_risk"])
        direction = "ASC" if order.lower() == "asc" else "DESC"
        total = int(self.data.query(f"SELECT COUNT(*) AS n FROM suppliers{where}", params)[0]["n"])
        rows = self.data.query(f'SELECT * FROM suppliers{where} ORDER BY {sort_column} {direction}, "supplierID" ASC LIMIT ? OFFSET ?',
                               [*params, max(1, min(limit, 100)), max(0, offset)])
        return {"items": rows, "total": total, "limit": max(1, min(limit, 100)), "offset": max(0, offset),
                "provenance": {"dataset": self.data.csv_path.name}}

    def compare(self, ids: list[str], custom_weights: dict[str, float] | None = None) -> dict:
        profiles = self.get_suppliers(ids)
        if len(profiles) != len(set(ids)):
            found = {item["supplierID"] for item in profiles}
            return {"error": "Unknown supplier IDs", "unknown_ids": sorted(set(ids) - found)}
        if custom_weights and set(custom_weights) - set(self.data.score_columns):
            return {"error": "custom_weights contains unsupported score columns"}
        if custom_weights is not None:
            if not custom_weights or any(not math.isfinite(v) or v < 0 for v in custom_weights.values()) or sum(custom_weights.values()) <= 0:
                return {"error": "Weights must be finite, non-negative and have a positive total"}
            total = sum(custom_weights.values())
            custom_weights = {key: value / total for key, value in custom_weights.items()}
        for row in profiles:
            row["custom_score"] = (sum(float(row[k]) * float(v) for k, v in custom_weights.items())
                                   if custom_weights else None)
        return {"suppliers": profiles, "custom_weights": custom_weights,
                "provenance": {"dataset_columns": list(profiles[0]) if profiles else []}}

    def alternatives(self, supplier_id: str, limit: int = 5) -> dict:
        source = self.data.supplier(supplier_id)
        if not source:
            return {"error": "Supplier not found"}
        candidates = self.data.query(
            'SELECT * FROM suppliers WHERE "supplierID" <> ? AND "Sourcing Risk Level" = ? AND "Supply Chain Complexity" = ?',
            [supplier_id, source["Sourcing Risk Level"], source["Supply Chain Complexity"]])
        if len(candidates) < 30:
            candidates = self.data.query('SELECT * FROM suppliers WHERE "supplierID" <> ?', [supplier_id])
        def distance(candidate: dict) -> float:
            risk_gap = abs(float(candidate["Total_Risk_Index"]) - float(source["Total_Risk_Index"]))
            volume_column = "Purchase Order Volume (EUR)"
            volume_gap = abs(float(candidate[volume_column]) - float(source[volume_column])) / max(float(source[volume_column]), 1.0)
            return risk_gap + volume_gap * 10
        active = {a["supplier_id"] for a in self.app_store.get_alerts() if a["status"] == "open"}
        candidates.sort(key=distance)
        result = []
        for item in candidates:
            item["profile_distance"] = round(distance(item), 3)
            item["active_ops_alert"] = item["supplierID"] in active
            result.append(item)
            if len(result) == limit: break
        return {"source_supplier": source, "alternatives": result,
                "matching_note": "Risk and operational profile; the dataset has no component category.",
                "provenance": {"dataset_columns": ["Total_Risk_Index", "Purchase Order Volume (EUR)", "Sourcing Risk Level", "Supply Chain Complexity"]}}
