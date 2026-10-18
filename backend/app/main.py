from __future__ import annotations

import asyncio
import json
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from app.agents.chat.agent import ChatAgent
from app.agents.live_orders.agent import LiveOrdersAgent
from app.agents.memos.agent import MemoAgent
from app.agents.news.agent import NewsAgent
from app.agents.research.agent import ResearchAgent
from app.agents.scenarios.agent import ScenarioAgent
from app.config.settings import settings
from app.db.duckdb_store import SupplierStore
from app.db.sqlite_store import AppStore
from app.models.schemas import ChatRequest, CompareRequest, ResearchRequest, ScenarioRequest, WhatIfRequest
from app.services.data_tools import DataTools
from app.services.events import AgentBus, EventBus
from app.services.explainer import ScoreExplainer
from app.services.search_gateway import SearchGateway


@asynccontextmanager
async def lifespan(app: FastAPI):
    data = SupplierStore(settings.dataset_path)
    store = AppStore(settings.sqlite_path)
    events = EventBus()
    bus = AgentBus(store, events)
    search = SearchGateway(store)
    explainer = ScoreExplainer(data)
    tools = DataTools(data, store, explainer)
    app.state.data = data
    app.state.store = store
    app.state.events = events
    app.state.bus = bus
    app.state.search = search
    app.state.tools = tools
    app.state.chat = ChatAgent(tools)
    app.state.live_orders = LiveOrdersAgent(data, store)
    app.state.news = NewsAgent(store, search)
    app.state.research = ResearchAgent(store, bus, search)
    app.state.scenarios = ScenarioAgent(tools)
    app.state.memos = MemoAgent(tools)
    yield
    data.connection.close()


app = FastAPI(title="Supplier Risk Intelligence API", version="0.1.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=[
    "http://localhost:3000", "http://127.0.0.1:3000",
    "http://localhost:5173", "http://127.0.0.1:5173",
],
                   allow_credentials=False, allow_methods=["*"], allow_headers=["*"])


def _sse(event: dict[str, Any]) -> str:
    return "data: " + json.dumps(event, default=str) + "\n\n"


@app.get("/health")
def health() -> dict:
    data = app.state.data
    return {"status": "ok", "dataset_rows": data.count,
            "formula_mode": app.state.tools.explainer.mode,
            "formula_r2": app.state.tools.explainer.r2,
            "feed_status": "running" if app.state.live_orders.running else "idle",
            "agents": ["chat", "live_orders", "news", "research", "scenarios", "memos"],
            "internal_agent_auth": "hmac-sha256"}


@app.get("/meta/schema")
def schema() -> dict:
    data = app.state.data
    return {"dataset": data.csv_path.name, "row_count": data.count, "columns": data.profile(),
            "roles": data.role_map, "risk_score_columns": data.score_columns,
            "tri_formula": {"mode": app.state.tools.explainer.mode, "r2": app.state.tools.explainer.r2,
                            "weights": app.state.tools.explainer.weights},
            "risk_bands": {"low": [0, 25], "medium": [25, 50], "high": [50, 75], "critical": [75, 100]}}


@app.get("/suppliers")
def list_suppliers(min_tri: float | None = None, max_tri: float | None = None,
                   risk_band: str | None = None, sourcing_risk_level: str | None = None,
                   complexity: str | None = None, min_po: float | None = None, max_po: float | None = None,
                   sort_by: str = "total_risk", order: str = "desc",
                   limit: int = Query(50, ge=1, le=100), offset: int = Query(0, ge=0)) -> dict:
    return app.state.tools.filter_suppliers(min_tri=min_tri, max_tri=max_tri, risk_band=risk_band,
        sourcing_risk_level=sourcing_risk_level, complexity=complexity, min_po=min_po, max_po=max_po,
        sort_by=sort_by, order=order, limit=limit, offset=offset)


@app.get("/suppliers/{supplier_id}")
def supplier(supplier_id: str) -> dict:
    row = app.state.data.supplier(supplier_id)
    if not row:
        raise HTTPException(404, "Supplier not found")
    return {"profile": row, "operations": app.state.live_orders.status(supplier_id),
            "provenance": {"dataset": app.state.data.csv_path.name}}


@app.get("/suppliers/{supplier_id}/explain")
def explain(supplier_id: str) -> dict:
    try:
        return app.state.tools.explainer.explain(supplier_id)
    except KeyError:
        raise HTTPException(404, "Supplier not found") from None


@app.post("/compare")
def compare(request: CompareRequest) -> dict:
    result = app.state.tools.compare(request.ids, request.custom_weights)
    if result.get("error"):
        raise HTTPException(422, result)
    return result


@app.get("/operations/status")
def operations_status(ids: str = Query(..., description="Comma-separated supplier IDs")) -> dict:
    requested = list(dict.fromkeys(value.strip() for value in ids.split(",") if value.strip()))
    if len(requested) > 100:
        raise HTTPException(422, "At most 100 supplier IDs are allowed")
    statuses = [app.state.live_orders.status(sid) for sid in requested]
    missing = [sid for sid, status in zip(requested, statuses) if status is None]
    return {"items": [item for item in statuses if item], "unknown_ids": missing,
            "source": "simulated_feed", "provenance": {"dataset_baselines": True}}


@app.get("/operations/alerts")
def operations_alerts(ids: str | None = None, min_severity: str = "low") -> dict:
    id_list = [item.strip() for item in ids.split(",") if item.strip()] if ids else None
    levels = {"low": 0, "medium": 1, "high": 2, "critical": 3}
    if min_severity.lower() not in levels:
        raise HTTPException(422, "Invalid severity")
    alerts = app.state.store.get_alerts(id_list)
    alerts = [item for item in alerts if levels.get(item["severity"], 0) >= levels[min_severity.lower()]]
    return {"items": alerts, "source": "simulated_feed"}


@app.post("/operations/scenario")
async def operations_scenario(request: ScenarioRequest, supplier_id: str | None = None) -> dict:
    live = app.state.live_orders
    if request.action == "reset":
        live.reset()
        app.state.store.audit("live_orders", "scenario_reset", {"seed": request.seed})
        return {"status": "reset", "source": "simulated_feed"}
    if request.action == "pause":
        live.running = False
        return {"status": "paused", "source": "simulated_feed"}
    try:
        alert = live.start_demo_scenario(supplier_id)
    except KeyError:
        raise HTTPException(404, "Supplier not found") from None
    envelope = app.state.bus.send("live_orders", "news", "ops_alert", alert)
    news = app.state.news.check(alert["supplier_id"])
    app.state.bus.send("news", "research", "signals_checked", news)
    report = None
    if alert["severity"] in {"high", "critical"}:
        report = app.state.research.run(alert["supplier_id"], alert["supplier_id"], alert["alert_id"])
        app.state.bus.send("research", "scenarios", "research_completed", {"research_id": report["research_id"], "status": report["status"]})
    alternatives = app.state.scenarios.what_if(alert["supplier_id"], 5)
    app.state.store.audit("scenarios", "alternatives_ranked", {"supplier_id": alert["supplier_id"], "count": len(alternatives.get("alternatives", []))})
    await app.state.events.publish({"agent": "scenarios", "type": "alternatives_ranked", "payload": alternatives})
    return {"status": "running", "alert": alert, "news": news, "research": report,
            "alternatives": alternatives, "handoff_message_id": envelope.message_id,
            "source": "simulated_feed"}


@app.post("/chat")
def chat(request: ChatRequest) -> dict:
    result = app.state.chat.answer(request.message, request.supplier_ids)
    app.state.store.audit("chat", "chat_answer", {"tool_calls": result.get("tool_calls"), "validated": result.get("validated")})
    return result


@app.post("/research")
async def start_research(request: ResearchRequest) -> dict:
    report = app.state.research.run(request.company, request.supplier_id)
    app.state.bus.send("research", "news", "research_started", {"research_id": report["research_id"], "company": request.company})
    return {"research_id": report["research_id"], "status": report["status"]}


@app.get("/research/{research_id}")
def get_research(research_id: str) -> dict:
    report = app.state.research.get(research_id)
    if not report:
        raise HTTPException(404, "Research report not found")
    return report


@app.get("/signals/{supplier_id}")
def signals(supplier_id: str) -> dict:
    if not app.state.data.supplier(supplier_id):
        raise HTTPException(404, "Supplier not found")
    return app.state.news.check(supplier_id)


@app.post("/scenarios/what-if")
def what_if(request: WhatIfRequest) -> dict:
    result = app.state.scenarios.what_if(request.supplier_id, request.limit)
    if result.get("error"):
        raise HTTPException(404, result["error"])
    return result


@app.post("/memos/shortlist")
def memo(body: dict[str, Any]) -> StreamingResponse:
    ids = body.get("ids", [])
    if not isinstance(ids, list) or not ids or len(ids) > 20:
        raise HTTPException(422, "Provide between 1 and 20 supplier IDs")
    document = app.state.memos.build_html(ids, body.get("chosen"), str(body.get("note", "")))
    return StreamingResponse(iter([document]), media_type="text/html; charset=utf-8",
                             headers={"Content-Disposition": "attachment; filename=shortlist-memo.html"})


@app.get("/events/stream")
@app.get("/operations/stream")
def events_stream() -> StreamingResponse:
    async def event_generator():
        async for event in app.state.events.subscribe():
            yield _sse(event)
    return StreamingResponse(event_generator(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


@app.get("/research/{research_id}/events")
def research_events(research_id: str) -> StreamingResponse:
    if not app.state.research.get(research_id):
        raise HTTPException(404, "Research report not found")
    async def event_generator():
        yield _sse({"agent": "research", "type": "report_available", "payload": {"research_id": research_id}})
    return StreamingResponse(event_generator(), media_type="text/event-stream")
