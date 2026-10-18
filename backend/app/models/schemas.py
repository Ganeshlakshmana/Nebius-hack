from __future__ import annotations

from typing import Any, Literal
from pydantic import BaseModel, Field


class CompareRequest(BaseModel):
    ids: list[str] = Field(min_length=1, max_length=20)
    custom_weights: dict[str, float] | None = None


class WhatIfRequest(BaseModel):
    supplier_id: str
    limit: int = Field(default=5, ge=1, le=20)


class ResearchRequest(BaseModel):
    company: str = Field(min_length=2, max_length=200)
    supplier_id: str | None = None
    component: str | None = Field(default=None, min_length=2, max_length=100)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    supplier_ids: list[str] = Field(default_factory=list, max_length=20)
    component: str | None = Field(default=None, min_length=2, max_length=100)


class ComponentAnalysisRequest(BaseModel):
    component: str = Field(min_length=2, max_length=100)
    supplier_ids: list[str] = Field(min_length=1, max_length=20)


class ScenarioRequest(BaseModel):
    action: Literal["start", "pause", "reset"] = "start"
    seed: int = 42


class UIComponent(BaseModel):
    type: str
    props: dict[str, Any]


class ChatResponse(BaseModel):
    answer: str
    components: list[UIComponent] = []
    validated: bool
    tool_calls: list[str] = []
    provenance: dict[str, Any] = {}
