"""Sentinelle 974 — API FastAPI.

Endpoints :
- GET  /health            -> état API + DB + Ollama
- GET  /inventory         -> inventaire (findings category=inventory)
- GET  /cves              -> findings CVE (filtre severity)
- GET  /sovereignty-score -> dernier score de conformité
- GET  /flows             -> flux réseau observés
- POST /ingest            -> ingestion de findings (agent)
- POST /flows             -> ingestion de flux souveraineté
- GET  /report            -> rapport Markdown
"""
from __future__ import annotations

import json
import os

import httpx
from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, Response, StreamingResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session

from . import models, schemas
from .agent import explain_finding, stream_finding
from .config import settings
from .db import Base, engine, get_db
from .pdf import build_pdf
from .sovereignty import classify_host, classify_ip, compute_score, verdict_for

VERSION = "0.1.0"

_TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "templates")
templates = Jinja2Templates(directory=_TEMPLATE_DIR)

app = FastAPI(
    title="Sentinelle 974",
    description="Plateforme self-hosted de souveraineté des données + posture cyber (PME 974).",
    version=VERSION,
)


@app.on_event("startup")
def _startup() -> None:
    Base.metadata.create_all(bind=engine)


# --------------------------------------------------------------------------- #
# Santé
# --------------------------------------------------------------------------- #
@app.get("/health", response_model=schemas.HealthOut)
def health(db: Session = Depends(get_db)) -> schemas.HealthOut:
    db_ok = "ok"
    try:
        db.execute(select(1))
    except Exception:
        db_ok = "error"

    ollama = None
    try:
        r = httpx.get(f"{settings.ollama_base_url}/api/tags", timeout=2.0)
        if r.status_code == 200:
            models_list = r.json().get("models", [])
            ollama = f"{len(models_list)} modèles"
    except Exception:
        ollama = "injoignable"

    return schemas.HealthOut(
        status="ok" if db_ok == "ok" else "degraded",
        host=settings.sentinelle_host,
        version=VERSION,
        ollama=ollama,
        db=db_ok,
    )


# --------------------------------------------------------------------------- #
# Inventaire
# --------------------------------------------------------------------------- #
@app.get("/inventory", response_model=list[schemas.FindingOut])
def inventory(db: Session = Depends(get_db)) -> list[models.Finding]:
    return list(
        db.scalars(
            select(models.Finding)
            .where(models.Finding.category == "inventory")
            .order_by(models.Finding.created_at.desc())
            .limit(200)
        )
    )


# --------------------------------------------------------------------------- #
# CVE
# --------------------------------------------------------------------------- #
@app.get("/cves", response_model=list[schemas.FindingOut])
def cves(
    severity: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[models.Finding]:
    q = select(models.Finding).where(models.Finding.category == "cve")
    if severity:
        q = q.where(models.Finding.severity == severity.upper())
    return list(db.scalars(q.order_by(models.Finding.created_at.desc()).limit(200)))


# --------------------------------------------------------------------------- #
# Souveraineté
# --------------------------------------------------------------------------- #
@app.get("/sovereignty-score", response_model=schemas.ScoreOut)
def sovereignty_score(db: Session = Depends(get_db)) -> models.Score:
    score = db.scalars(
        select(models.Score).order_by(models.Score.computed_at.desc()).limit(1)
    ).first()
    if not score:
        raise HTTPException(status_code=404, detail="Aucun score calculé — lancer l'agent souveraineté")
    return score


@app.get("/flows", response_model=list[schemas.FlowOut])
def flows(db: Session = Depends(get_db)) -> list[models.SovereigntyFlow]:
    return list(
        db.scalars(
            select(models.SovereigntyFlow)
            .order_by(models.SovereigntyFlow.observed_at.desc())
            .limit(500)
        )
    )


# --------------------------------------------------------------------------- #
# Ingestion (agent)
# --------------------------------------------------------------------------- #
@app.post("/ingest", response_model=list[schemas.FindingOut], status_code=201)
def ingest(
    findings: list[schemas.FindingIn],
    db: Session = Depends(get_db),
) -> list[models.Finding]:
    rows = [models.Finding(**f.model_dump()) for f in findings]
    db.add_all(rows)
    db.commit()
    for r in rows:
        db.refresh(r)
    return rows


@app.post("/flows", response_model=list[schemas.FlowOut], status_code=201)
def ingest_flows(
    flows_in: list[schemas.FlowIn],
    db: Session = Depends(get_db),
) -> list[models.SovereigntyFlow]:
    rows = []
    for f in flows_in:
        region = f.region
        if region == "unknown":
            region = classify_ip(f.dest_ip)
            if region == "other" and f.dest_host:
                region = classify_host(f.dest_host)
        verdict = f.verdict if f.verdict != "allow" else verdict_for(region, f.dest_host)
        rows.append(
            models.SovereigntyFlow(
                dest_ip=f.dest_ip,
                dest_port=f.dest_port,
                proto=f.proto,
                process=f.process,
                dest_host=f.dest_host,
                region=region,
                verdict=verdict,
            )
        )
    db.add_all(rows)
    db.commit()
    for r in rows:
        db.refresh(r)

    # Recalcule le score après ingestion
    all_flows = db.scalars(select(models.SovereigntyFlow)).all()
    result = compute_score(
        [{"region": fl.region, "dest_host": fl.dest_host} for fl in all_flows]
    )
    db.add(
        models.Score(
            host=settings.sentinelle_host,
            score=result["score"],
            grade=result["grade"],
            details=result,
        )
    )
    db.commit()
    return rows


# --------------------------------------------------------------------------- #
# Dashboard HTMX
# --------------------------------------------------------------------------- #
@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)) -> HTMLResponse:
    findings = db.scalars(
        select(models.Finding).order_by(models.Finding.created_at.desc()).limit(100)
    ).all()
    score = db.scalars(
        select(models.Score).order_by(models.Score.computed_at.desc()).limit(1)
    ).first()
    flows = db.scalars(
        select(models.SovereigntyFlow)
        .order_by(models.SovereigntyFlow.observed_at.desc())
        .limit(100)
    ).all()

    # Agrégats
    sev_counts = {"CRIT": 0, "HIGH": 0, "MED": 0, "LOW": 0, "INFO": 0}
    for f in findings:
        sev_counts[f.severity] = sev_counts.get(f.severity, 0) + 1

    region_counts: dict[str, int] = {}
    for fl in flows:
        region_counts[fl.region] = region_counts.get(fl.region, 0) + 1

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "host": settings.sentinelle_host,
            "version": VERSION,
            "findings": findings,
            "score": score,
            "flows": flows,
            "sev_counts": sev_counts,
            "region_counts": region_counts,
        },
    )


# --------------------------------------------------------------------------- #
# Rapport PDF
# --------------------------------------------------------------------------- #
@app.get("/report.pdf")
def report_pdf(db: Session = Depends(get_db)) -> Response:
    findings = db.scalars(select(models.Finding).order_by(models.Finding.created_at.desc())).all()
    score = db.scalars(select(models.Score).order_by(models.Score.computed_at.desc()).limit(1)).first()
    flows = db.scalars(select(models.SovereigntyFlow).order_by(models.SovereigntyFlow.observed_at.desc())).all()
    pdf_bytes = build_pdf(settings.sentinelle_host, findings, score, flows)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=sentinelle-974-rapport.pdf"},
    )


# --------------------------------------------------------------------------- #
# Agent IA local (explication d'un finding)
# --------------------------------------------------------------------------- #
@app.get("/explain/{finding_id}")
def explain(finding_id: int, lang: str = Query(default="fr"), db: Session = Depends(get_db)) -> dict:
    finding = db.get(models.Finding, finding_id)
    if not finding:
        raise HTTPException(status_code=404, detail="Finding introuvable")
    text = explain_finding(
        {
            "title": finding.title,
            "severity": finding.severity,
            "category": finding.category,
            "description": finding.description,
        },
        lang=lang,
    )
    return {"id": finding_id, "lang": lang, "model": settings.llm_model, "explanation": text}


@app.get("/explain/{finding_id}/stream")
def explain_stream(
    finding_id: int,
    lang: str = Query(default="fr"),
    format: str = Query(default="sse"),
    db: Session = Depends(get_db),
):
    """Explication d'un finding en streaming (SSE par défaut, ou plain).

    - format=sse  : Server-Sent Events (`data: {...}\n\n`)
    - format=plain: texte brut token par token (simple `curl`)
    """
    finding = db.get(models.Finding, finding_id)
    if not finding:
        raise HTTPException(status_code=404, detail="Finding introuvable")

    payload = {
        "title": finding.title,
        "severity": finding.severity,
        "category": finding.category,
        "description": finding.description,
    }

    if format == "plain":
        def plain_gen():
            yield f"modèle: {settings.llm_model}\n\n"
            for chunk in stream_finding(payload, lang=lang):
                yield chunk
        return StreamingResponse(plain_gen(), media_type="text/plain")

    def sse_gen():
        for chunk in stream_finding(payload, lang=lang):
            yield f"data: {json.dumps({'token': chunk})}\n\n"
        yield "data: [DONE]\n\n"
    return StreamingResponse(sse_gen(), media_type="text/event-stream")


# --------------------------------------------------------------------------- #
# Rapport
# --------------------------------------------------------------------------- #
@app.get("/report")
def report(db: Session = Depends(get_db)) -> str:
    findings = db.scalars(select(models.Finding).order_by(models.Finding.created_at.desc())).all()
    score = db.scalars(select(models.Score).order_by(models.Score.computed_at.desc()).limit(1)).first()
    flows = db.scalars(select(models.SovereigntyFlow).order_by(models.SovereigntyFlow.observed_at.desc())).all()

    lines = [
        "# Rapport Sentinelle 974",
        "",
        f"- Hôte : `{settings.sentinelle_host}`",
        f"- Findings : {len(findings)}",
        f"- Flux souveraineté : {len(flows)}",
    ]
    if score:
        lines += ["", f"## Score de conformité : **{score.grade}** ({score.score}/100)"]
    lines += ["", "## Findings"]
    if not findings:
        lines += ["_Aucun finding._"]
    for f in findings:
        lines.append(f"- **[{f.severity}]** {f.title} — `{f.category}`")
        if f.description:
            lines.append(f"  {f.description}")
    lines += ["", "## Flux réseau sortants"]
    if not flows:
        lines += ["_Aucun flux observé._"]
    for fl in flows:
        lines.append(
            f"- `{fl.dest_ip}:{fl.dest_port}` ({fl.proto}) — {fl.region} — verdict `{fl.verdict}` — {fl.process or '?'}"
        )
    return "\n".join(lines) + "\n"
