from __future__ import annotations
from app.services.data_tools import DataTools


class ScenarioAgent:
    def __init__(self, tools: DataTools):
        self.tools = tools

    def what_if(self, supplier_id: str, limit: int = 5) -> dict:
        return self.tools.alternatives(supplier_id, limit)
