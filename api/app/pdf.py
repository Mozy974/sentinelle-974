"""Sentinelle 974 — génération de rapport PDF (reportlab).

Aucune dépendance externe au moment de la génération : tout est local.
"""
from __future__ import annotations

import io
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

SEV_COLORS = {
    "CRIT": colors.HexColor("#f85149"),
    "HIGH": colors.HexColor("#ffa657"),
    "MED": colors.HexColor("#d29922"),
    "LOW": colors.HexColor("#3fb950"),
    "INFO": colors.HexColor("#58a6ff"),
}

VERDICT_COLORS = {
    "allow": colors.HexColor("#3fb950"),
    "warn": colors.HexColor("#d29922"),
    "block": colors.HexColor("#f85149"),
}


def build_pdf(host: str, findings: list, score, flows: list) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=18 * mm, rightMargin=18 * mm,
        topMargin=18 * mm, bottomMargin=18 * mm,
        title="Rapport Sentinelle 974",
    )
    styles = getSampleStyleSheet()
    title = styles["Title"]
    h2 = styles["Heading2"]
    body = styles["BodyText"]
    small = styles["BodyText"]
    small.fontSize = 8

    story = []

    # En-tête
    story.append(Paragraph("Sentinelle 974", title))
    story.append(Paragraph(
        f"Rapport de souveraineté & posture cyber — {host} — "
        f"{datetime.now().strftime('%d/%m/%Y %H:%M')}",
        styles["Italic"],
    ))
    story.append(Spacer(1, 6 * mm))

    # Score
    if score:
        story.append(Paragraph("Score de conformité", h2))
        story.append(Paragraph(
            f"<b>{score.grade}</b> — {score.score}/100",
            styles["Heading1"],
        ))
        story.append(Spacer(1, 4 * mm))

    # Findings
    story.append(Paragraph(f"Findings ({len(findings)})", h2))
    if findings:
        rows = [["Sévérité", "Catégorie", "Titre", "Description"]]
        for f in findings:
            rows.append([
                f.severity, f.category, f.title,
                (f.description or "")[:120],
            ])
        t = Table(rows, colWidths=[18 * mm, 22 * mm, 55 * mm, 75 * mm])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#161b22")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#30363d")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f6f8fa")]),
        ]))
        # Colorer la colonne sévérité
        for i, f in enumerate(findings, start=1):
            t.setStyle(TableStyle([
                ("TEXTCOLOR", (0, i), (0, i), SEV_COLORS.get(f.severity, colors.black)),
            ]))
        story.append(t)
    else:
        story.append(Paragraph("Aucun finding.", body))
    story.append(Spacer(1, 6 * mm))

    # Flux
    story.append(Paragraph(f"Flux réseau sortants ({len(flows)})", h2))
    if flows:
        rows = [["Destination", "Port", "Proto", "Région", "Verdict", "Processus"]]
        for fl in flows:
            rows.append([
                fl.dest_ip, str(fl.dest_port), fl.proto,
                fl.region, fl.verdict, fl.process or "?",
            ])
        t = Table(rows, colWidths=[35 * mm, 15 * mm, 15 * mm, 25 * mm, 20 * mm, 60 * mm])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#161b22")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#30363d")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f6f8fa")]),
        ]))
        for i, fl in enumerate(flows, start=1):
            t.setStyle(TableStyle([
                ("TEXTCOLOR", (4, i), (4, i), VERDICT_COLORS.get(fl.verdict, colors.black)),
            ]))
        story.append(t)
    else:
        story.append(Paragraph("Aucun flux observé.", body))

    story.append(Spacer(1, 8 * mm))
    story.append(Paragraph(
        "Généré par Sentinelle 974 — 100% local, aucune donnée ne quitte la machine.",
        small,
    ))

    doc.build(story)
    return buf.getvalue()
