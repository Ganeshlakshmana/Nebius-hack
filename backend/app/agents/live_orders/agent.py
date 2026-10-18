from __future__ import annotations

import json
import uuid
from typing import Any
from app.db.duckdb_store import SupplierStore
from app.db.sqlite_store import AppStore


class LiveOrdersAgent:
    def __init__(self, data: SupplierStore, store: AppStore):
        self.data, self.store = data, store
        self.running = False

    def status(self, supplier_id: str) -> dict[str, Any] | None:
        row = self.data.supplier(supplier_id)
        if not row:
            return None
        baseline = {"delivery_rating": float(row["Supplier Delivery Rating"]),
                    "confirmation_rate": float(row["Order Confirmation Rate"]),
                    "order_change_rate": float(row["Order Change Rate"])}
        with self.store.connect() as db:
            saved = db.execute("SELECT payload FROM live_metrics WHERE supplier_id=?", (supplier_id,)).fetchone()
        if saved:
            payload = json.loads(saved["payload"])
            current = payload.get("current", baseline)
            drift_z = payload.get("drift_z", {key: 0.0 for key in baseline})
            sparkline = payload.get("sparkline", [])
        else:
            current, drift_z, sparkline = baseline, {key: 0.0 for key in baseline}, []
        multiplier = {"low": 1.0, "medium": 1.25, "high": 1.6}.get(str(row["Sourcing Risk Level"]).lower(), 1.0)
        spend = float(row["Purchase Order Volume (EUR)"]) * float(row["Total_Risk_Index"]) / 100 * multiplier
        delivery_delta = current["delivery_rating"] - baseline["delivery_rating"]
        return {"supplier_id": supplier_id, "baseline": baseline, "rolling_7d": current, "rolling_30d": current,
                "drift_z": drift_z, "spend_at_risk_eur": round(spend, 2),
                "live_operational_score": round(max(0, min(100, float(row["Operational_Resilience_Score"]) - delivery_delta)), 2),
                "historic_operational_score": float(row["Operational_Resilience_Score"]),
                "delta_reason": "Simulated delivery drift overlay" if delivery_delta else None,
                "sparkline": sparkline, "source": "simulated_feed"}

    def start_demo_scenario(self, supplier_id: str | None = None) -> dict:
        if supplier_id:
            row = self.data.supplier(supplier_id)
        else:
            row = self.data.query(
                'SELECT * FROM suppliers WHERE "Sourcing Risk Level" = \'High\' '
                'ORDER BY "Purchase Order Volume (EUR)" DESC LIMIT 1')[0]
            supplier_id = row["supplierID"]
        if not row:
            raise KeyError(supplier_id)
        # Dedupe: one open simulated alert per supplier and metric.
        with self.store.connect() as db:
            existing = db.execute("SELECT * FROM ops_alerts WHERE supplier_id=? AND metric='delivery_rating' "
                                  "AND status='open' AND source='simulated_feed'", (supplier_id,)).fetchone()
        if existing:
            self.running = True
            return {**dict(existing), "deduplicated": True}
        baseline = float(row["Supplier Delivery Rating"])
        current = round(max(5.0, baseline * 0.72), 2)
        multiplier = 1.6 if row["Sourcing Risk Level"] == "High" else 1.25
        spend = float(row["Purchase Order Volume (EUR)"]) * float(row["Total_Risk_Index"]) / 100 * multiplier
        alert = {"alert_id": str(uuid.uuid4()), "supplier_id": supplier_id, "metric": "delivery_rating",
                 "baseline": baseline, "current": current, "drift_z": -3.5, "days_persisting": 3,
                 "spend_at_risk_eur": round(spend, 2), "sourcing_risk_level": row["Sourcing Risk Level"],
                 "severity": "critical" if spend >= 250000 else "high", "status": "open",
                 "source": "simulated_feed"}
        payload = {"current": {"delivery_rating": current,
                   "confirmation_rate": float(row["Order Confirmation Rate"]),
                   "order_change_rate": float(row["Order Change Rate"])},
                   "drift_z": {"delivery_rating": -3.5, "confirmation_rate": 0.0, "order_change_rate": 0.0},
                   "sparkline": [{"day": i, "delivery_rating": round(baseline - (baseline-current)*i/3, 2)} for i in range(4)]}
        with self.store.connect() as db:
            db.execute("INSERT OR REPLACE INTO live_metrics(supplier_id,payload,updated_at) VALUES(?,?,CURRENT_TIMESTAMP)",
                       (supplier_id, json.dumps(payload)))
            db.execute("INSERT OR REPLACE INTO ops_alerts(alert_id,supplier_id,metric,baseline,current,drift_z,days_persisting,spend_at_risk_eur,sourcing_risk_level,severity,status,source) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
                       (alert["alert_id"], supplier_id, alert["metric"], baseline, current, -3.5, 3, spend,
                        row["Sourcing Risk Level"], alert["severity"], "open", "simulated_feed"))
        self.running = True
        self.store.audit("live_orders", "simulated_alert_created", alert)
        return alert

    def reset(self) -> None:
        with self.store.connect() as db:
            db.execute("DELETE FROM live_metrics")
            db.execute("DELETE FROM ops_alerts WHERE source='simulated_feed'")
        self.running = False
