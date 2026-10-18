from __future__ import annotations
from app.services.data_tools import DataTools


class ScenarioAgent:
    def __init__(self, tools: DataTools):
        self.tools = tools

    def what_if(self, supplier_id: str, limit: int = 5, exclude_alerted: bool = False) -> dict:
        if not exclude_alerted:
            return self.tools.alternatives(supplier_id, limit)
        # Over-fetch, then drop suppliers with an open operations alert.
        result = self.tools.alternatives(supplier_id, limit + 20)
        if "alternatives" in result:
            result["alternatives"] = [a for a in result["alternatives"] if not a["active_ops_alert"]][:limit]
            result["excluded_alerted"] = True
        return result
