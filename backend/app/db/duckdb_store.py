from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import duckdb


class SupplierStore:
    """Read-only analytics facade over the source CSV."""

    def __init__(self, csv_path: Path):
        if not csv_path.is_file():
            raise FileNotFoundError(f"Supplier dataset not found: {csv_path}")
        self.csv_path = csv_path.resolve()
        self.connection = duckdb.connect(database=":memory:", read_only=False)
        escaped = str(self.csv_path).replace("'", "''")
        self.connection.execute(
            f"CREATE VIEW suppliers AS SELECT * FROM read_csv_auto('{escaped}', header=true, sample_size=-1)"
        )
        self.columns = [row[0] for row in self.connection.execute("DESCRIBE suppliers").fetchall()]
        self.count = int(self.connection.execute("SELECT COUNT(*) FROM suppliers").fetchone()[0])
        self.id_column = "supplierID"
        self.score_columns = [
            name for name in self.columns
            if name.endswith("_Score") and not name.endswith("_Level")
            and name not in {"Total_Risk_Index", "Industry_Benchmark_Score"}
        ]
        self.role_map = {
            "total_risk": "Total_Risk_Index",
            "name": "Supplier Name",
            "po_volume_eur": "Purchase Order Volume (EUR)",
            "order_change_rate": "Order Change Rate",
            "delivery_rating": "Supplier Delivery Rating",
            "confirmation_rate": "Order Confirmation Rate",
            "sourcing_risk_level": "Sourcing Risk Level",
            "supply_chain_complexity": "Supply Chain Complexity",
        }
        missing = [column for column in [self.id_column, *self.role_map.values(), *self.score_columns] if column not in self.columns]
        if missing:
            raise ValueError(f"Dataset is missing required columns: {', '.join(missing)}")

    def query(self, sql: str, params: list[Any] | tuple[Any, ...] = ()) -> list[dict[str, Any]]:
        cursor = self.connection.execute(sql, params)
        names = [item[0] for item in cursor.description]
        return [dict(zip(names, row)) for row in cursor.fetchall()]

    def supplier(self, supplier_id: str) -> dict[str, Any] | None:
        rows = self.query('SELECT * FROM suppliers WHERE "supplierID" = ?', [supplier_id])
        return rows[0] if rows else None

    def profile(self) -> list[dict[str, Any]]:
        profiles: list[dict[str, Any]] = []
        for column in self.columns:
            safe = '"' + column.replace('"', '""') + '"'
            row = self.query(
                f"SELECT COUNT(*) AS n, COUNT({safe}) AS non_null, MIN(TRY_CAST({safe} AS DOUBLE)) AS min_value, "
                f"MAX(TRY_CAST({safe} AS DOUBLE)) AS max_value, COUNT(DISTINCT {safe}) AS distinct_values FROM suppliers"
            )[0]
            profiles.append({"name": column, "type": "numeric" if row["min_value"] is not None else "categorical",
                             "null_count": row["n"] - row["non_null"], "min": row["min_value"],
                             "max": row["max_value"], "distinct_values": row["distinct_values"]})
        return profiles
