#!/usr/bin/env python3
"""Génère le one-pager client Sentinelle 974 (flyer A4, reportlab)."""
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle, HRFlowable,
)

OUT = "/home/mozy/Bureau/Créer une application formidable cybersécurité et souveraineté des données./sentinelle-974/one-pager-sentinelle-974.pdf"

# Palette (dark theme, cohérente avec le dashboard)
BG = colors.HexColor("#0d1117")
PANEL = colors.HexColor("#161b22")
ACCENT = colors.HexColor("#2f81f7")
GREEN = colors.HexColor("#3fb950")
AMBER = colors.HexColor("#d29922")
RED = colors.HexColor("#f85149")
TEXT = colors.HexColor("#e6edf3")
MUTED = colors.HexColor("#8b949e")
BORDER = colors.HexColor("#30363d")

W, H = A4
MARGIN = 16 * mm
CONTENT_W = W - 2 * MARGIN

doc = SimpleDocTemplate(
    OUT, pagesize=A4,
    leftMargin=MARGIN, rightMargin=MARGIN,
    topMargin=14 * mm, bottomMargin=12 * mm,
    title="Sentinelle 974 — Souveraineté des données",
)

# Styles
hero = ParagraphStyle("hero", fontName="Helvetica-Bold", fontSize=23, leading=27, textColor=TEXT)
sub = ParagraphStyle("sub", fontName="Helvetica", fontSize=10.5, leading=15, textColor=MUTED)
h2 = ParagraphStyle("h2", fontName="Helvetica-Bold", fontSize=13, leading=16, textColor=TEXT, spaceBefore=8)
body = ParagraphStyle("body", fontName="Helvetica", fontSize=9.5, leading=14, textColor=TEXT)
small = ParagraphStyle("small", fontName="Helvetica", fontSize=8, leading=11, textColor=MUTED)
cta = ParagraphStyle("cta", fontName="Helvetica-Bold", fontSize=12, leading=16, textColor=colors.white)

story = []

# --- Bandeau titre ---
story.append(Paragraph("Sentinelle 974", hero))
story.append(Spacer(1, 2 * mm))
story.append(Paragraph(
    "La souveraineté de vos données, <b>sans quitter La Réunion</b>.", sub))
story.append(Spacer(1, 3 * mm))
story.append(HRFlowable(width="100%", thickness=1.2, color=ACCENT))
story.append(Spacer(1, 5 * mm))

# --- Accroche problème ---
story.append(Paragraph("Le constat", h2))
story.append(Paragraph(
    "Vos logiciels métier envoient des données vers des serveurs <b>hors de l'Union "
    "européenne</b> — souvent aux États-Unis — sans que vous le sachiez. Pour un "
    "cabinet médical, un expert-comptable ou une mairie, c'est un risque RGPD réel : "
    "<b>jusqu'à 4% du chiffre d'affaires</b> d'amende, et une dépendance totale au "
    "câble sous-marin en cas de cyclone.", body))
story.append(Spacer(1, 4 * mm))

# --- La solution ---
story.append(Paragraph("La solution, 100% locale", h2))
story.append(Paragraph(
    "Sentinelle 974 s'installe <b>chez vous</b>, sur un petit boîtier. Elle observe, "
    "analyse et vous explique — <b>rien ne repart</b>.", body))
story.append(Spacer(1, 3 * mm))

# --- Les 4 piliers (table) ---
pillars = [
    ["Inventaire", "Tout ce qui tourne sur vos machines, en clair."],
    ["Audit CVE", "Les vulnérabilités connues, avec leur gravité."],
    ["Flux sortants", "Ce qui part réellement : vers l'UE, ou hors UE."],
    ["Score A-F", "Votre note de conformité, en une page."],
]
pt = Table(pillars, colWidths=[38 * mm, CONTENT_W - 38 * mm])
pt.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, -1), PANEL),
    ("BOX", (0, 0), (-1, -1), 0.6, BORDER),
    ("INNERGRID", (0, 0), (-1, -1), 0.4, BORDER),
    ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
    ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
    ("FONTSIZE", (0, 0), (-1, -1), 9),
    ("TEXTCOLOR", (0, 0), (0, -1), GREEN),
    ("TEXTCOLOR", (1, 0), (1, -1), TEXT),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("TOPPADDING", (0, 0), (-1, -1), 7),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ("LEFTPADDING", (0, 0), (-1, -1), 10),
]))
story.append(pt)
story.append(Spacer(1, 5 * mm))

# --- Argument clé (encadré) ---
arg = Paragraph(
    "<b>Pourquoi ça change tout :</b> conformité RGPD démontrable, indépendance "
    "vis-à-vis des infrastructures cloud étrangères, et continuité d'activité même "
    "si le câble est coupé. Vos données restent à La Réunion — point.", body)
at = Table([[arg]], colWidths=[CONTENT_W])
at.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#0d2a1e")),
    ("BOX", (0, 0), (-1, -1), 0.8, GREEN),
    ("LEFTPADDING", (0, 0), (-1, -1), 10),
    ("RIGHTPADDING", (0, 0), (-1, -1), 10),
    ("TOPPADDING", (0, 0), (-1, -1), 8),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
]))
story.append(at)
story.append(Spacer(1, 5 * mm))

# --- Offre pilote (CTA) ---
story.append(Paragraph("Offre pilote — 3 places", h2))
story.append(Paragraph(
    "<b>Audit de souveraineté offert</b> (valeur 490 €) : 30 minutes, sur place ou à "
    "distance, et vous repartez avec un rapport clair et lisible. Ensuite, l'abonnement "
    "démarre à <b>149 €/mois</b>.", body))
story.append(Spacer(1, 4 * mm))

cta_text = "Contact : [Prénom] — [téléphone] — ismael.pelicot@gmail.com · Saint-Pierre, La Réunion"
cta_table = Table([[Paragraph(cta_text, cta)]], colWidths=[CONTENT_W])
cta_table.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, -1), ACCENT),
    ("LEFTPADDING", (0, 0), (-1, -1), 10),
    ("RIGHTPADDING", (0, 0), (-1, -1), 10),
    ("TOPPADDING", (0, 0), (-1, -1), 9),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
]))
story.append(cta_table)

# --- Pied ---
story.append(Spacer(1, 4 * mm))
story.append(Paragraph(
    "Sentinelle 974 — plateforme self-hosted de souveraineté des données et de posture "
    "cybersécurité. Aucune donnée métier ne quitte l'île. · "
    "https://github.com/Mozy974/sentinelle-974", small))

doc.build(story)
print(f"One-pager généré : {OUT}")
