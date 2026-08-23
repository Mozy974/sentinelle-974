"""Sentinelle 974 — schémas Pydantic."""
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class FindingIn(BaseModel):
    category: str = Field(..., max_length=64)
    severity: str = Field(..., max_length=16)
    title: str = Field(..., max_length=255)
    description: str = ""
    host: str = "localhost"
    source: str = "agent"
    data: dict[str, Any] = Field(default_factory=dict)


class FindingOut(FindingIn):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class FlowIn(BaseModel):
    dest_ip: str
    dest_port: int
    proto: str = "tcp"
    process: str = ""
    dest_host: str = ""
    region: str = "unknown"
    verdict: str = "allow"


class FlowOut(FlowIn):
    id: int
    observed_at: datetime

    model_config = {"from_attributes": True}


class ScoreOut(BaseModel):
    host: str
    score: float
    grade: str
    details: dict[str, Any]
    computed_at: datetime

    model_config = {"from_attributes": True}


class HealthOut(BaseModel):
    status: str
    host: str
    version: str
    ollama: Optional[str] = None
    db: str
