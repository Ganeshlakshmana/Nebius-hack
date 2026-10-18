from __future__ import annotations

import numpy as np

from app.db.duckdb_store import SupplierStore


class ScoreExplainer:
    def __init__(self, data: SupplierStore):
        self.data = data
        self.features = data.score_columns
        fields = [f'"{column}"' for column in ["Total_Risk_Index", *self.features]]
        rows = data.query("SELECT " + ",".join(fields) + " FROM suppliers")
        matrix = np.asarray([[float(row[column]) for column in ["Total_Risk_Index", *self.features]] for row in rows], dtype=float)
        y, x = matrix[:, 0], matrix[:, 1:]
        design = np.column_stack((np.ones(len(x)), x))
        coefficients, *_ = np.linalg.lstsq(design, y, rcond=None)
        predicted = design @ coefficients
        residual = float(np.sum((y - predicted) ** 2))
        total = float(np.sum((y - y.mean()) ** 2))
        self.r2 = 1.0 - residual / total if total else 1.0
        self.mode = "fitted_surrogate"
        self.weights = {name: float(weight) for name, weight in zip(self.features, coefficients[1:])
                        if abs(float(weight)) > 1e-3}

    def explain(self, supplier_id: str) -> dict:
        row = self.data.supplier(supplier_id)
        if not row:
            raise KeyError(supplier_id)
        groups = self.data.query(
            'SELECT "Sourcing Risk Level" AS sourcing, "Supply Chain Complexity" AS complexity, COUNT(*) AS n '
            'FROM suppliers WHERE "Sourcing Risk Level" = ? AND "Supply Chain Complexity" = ? GROUP BY 1,2',
            [row["Sourcing Risk Level"], row["Supply Chain Complexity"]])
        peer_fallback = not groups or groups[0]["n"] < 30
        if peer_fallback:
            median_rows = self.data.query("SELECT " + ",".join(
                f'median("{column}") AS "{column}"' for column in self.weights) + " FROM suppliers")
            peer_group = "all suppliers (peer group < 30)"
        else:
            medians = ",".join(f'median("{column}") AS "{column}"' for column in self.weights)
            median_rows = self.data.query(
                f'SELECT {medians} FROM suppliers WHERE "Sourcing Risk Level" = ? AND "Supply Chain Complexity" = ?',
                [row["Sourcing Risk Level"], row["Supply Chain Complexity"]])
            peer_group = f'{row["Sourcing Risk Level"]} / {row["Supply Chain Complexity"]}'
        medians = median_rows[0]
        contributions = [{"factor": factor, "value": float(row[factor]), "peer_median": float(medians[factor]),
                          "points": self.weights[factor] * (float(row[factor]) - float(medians[factor]))}
                         for factor in self.weights]
        contributions.sort(key=lambda item: abs(item["points"]), reverse=True)
        total_risk = float(row["Total_Risk_Index"])
        return {"supplier_id": supplier_id, "total": total_risk, "risk_band": row["Total_Risk_Index_Level"].lower(),
                "mode": self.mode, "r2": self.r2, "weights": self.weights, "peer_group": peer_group,
                "contributions": contributions, "provenance": {"dataset_columns": ["Total_Risk_Index", *self.weights]}}
