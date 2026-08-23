"""Sentinelle 974 — modèles de données."""
from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Finding(Base):
    """Un finding d'audit (risque, CVE, flux souveraineté, etc.)."""

    __tablename__ = "findings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    category: Mapped[str] = mapped_column(String(64), index=True)  # risk|cve|sovereignty|inventory
    severity: Mapped[str] = mapped_column(String(16), index=True)  # CRIT|HIGH|MED|LOW|INFO
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text, default="")
    host: Mapped[str] = mapped_column(String(128), default="localhost")
    source: Mapped[str] = mapped_column(String(64), default="agent")
    data: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class SovereigntyFlow(Base):
    """Un flux réseau sortant observé (destination, géolocalisation, verdict)."""

    __tablename__ = "sovereignty_flows"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    dest_ip: Mapped[str] = mapped_column(String(64), index=True)
    dest_port: Mapped[int] = mapped_column(Integer)
    proto: Mapped[str] = mapped_column(String(8), default="tcp")
    process: Mapped[str] = mapped_column(String(128), default="")
    dest_host: Mapped[str] = mapped_column(String(255), default="")
    region: Mapped[str] = mapped_column(String(32), default="unknown")  # local|eu|us|cn|ru|other|unknown
    verdict: Mapped[str] = mapped_column(String(16), default="allow")  # allow|warn|block
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class Score(Base):
    """Score de conformité souveraineté (dernier calcul)."""

    __tablename__ = "scores"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    host: Mapped[str] = mapped_column(String(128), default="localhost")
    score: Mapped[float] = mapped_column(Float)  # 0..100
    grade: Mapped[str] = mapped_column(String(8))  # A..F
    details: Mapped[dict] = mapped_column(JSON, default=dict)
    computed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
