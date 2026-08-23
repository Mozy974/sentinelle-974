"""Sentinelle 974 — agent IA local (Ollama).

Explique un finding en français (et créole) via un modèle local. Aucun appel
à une API cloud : l'inférence se fait sur la machine (Ollama).
"""
from __future__ import annotations

import json

import httpx

from .config import settings

# Modèle local par défaut (léger, CPU-only, français). Surchargeable via SENTINELLE_LLM_MODEL.
# Éviter les modèles "reasoning" (ex: qwen3.5) qui ne produisent pas de content.
DEFAULT_MODEL = "OpenLLM-France/Luciole-Instruct-1.1:1B"

SYSTEM_PROMPT = (
    "Tu es l'agent de Sentinelle 974 (cybersécurité, La Réunion). "
    "Explique ce finding en français, de façon claire et pédagogique, "
    "puis donne UNE action de remédiation défensive. Jamais d'exploit. "
    "Sois concis."
)


def explain_finding(finding: dict, lang: str = "fr") -> str:
    """Explique un finding via Ollama local. Retourne le texte ou un message d'erreur."""
    model = settings.llm_model
    title = finding.get("title", "")
    severity = finding.get("severity", "")
    category = finding.get("category", "")
    description = finding.get("description", "")

    user_prompt = (
        f"Finding : [{severity}] {title} (catégorie {category}).\n"
        f"Description : {description or 'aucune'}.\n"
        f"Explique ce que ça signifie pour une PME, et donne une action de remédiation défensive."
    )
    if lang == "creole":
        user_prompt += "\nRéponds en créole réunionnais."

    try:
        r = httpx.post(
            f"{settings.ollama_base_url}/api/generate",
            json={
                "model": model,
                "prompt": user_prompt,
                "system": SYSTEM_PROMPT,
                "stream": False,
                "options": {"temperature": 0.3, "num_predict": 40},
            },
            timeout=300.0,
        )
        r.raise_for_status()
        return r.json().get("response", "").strip()
    except httpx.HTTPError as e:
        return f"[Erreur Ollama] {e}"
    except Exception as e:
        return f"[Erreur] {e}"


def stream_finding(finding: dict, lang: str = "fr"):
    """Génère l'explication en streaming (token par token) via Ollama local.

    Rend les tokens un par un (générateur). Utilisé par /explain/{id}/stream
    pour une réponse progressive, plus réactive pendant une démo.
    """
    model = settings.llm_model
    title = finding.get("title", "")
    severity = finding.get("severity", "")
    category = finding.get("category", "")
    description = finding.get("description", "")

    user_prompt = (
        f"Finding : [{severity}] {title} (catégorie {category}).\n"
        f"Description : {description or 'aucune'}.\n"
        f"Explique ce que ça signifie pour une PME, et donne une action de remédiation défensive."
    )
    if lang == "creole":
        user_prompt += "\nRéponds en créole réunionnais."

    try:
        with httpx.stream(
            "POST",
            f"{settings.ollama_base_url}/api/generate",
            json={
                "model": model,
                "prompt": user_prompt,
                "system": SYSTEM_PROMPT,
                "stream": True,
                "options": {"temperature": 0.3, "num_predict": 40},
            },
            timeout=httpx.Timeout(300.0, connect=10.0),
        ) as r:
            r.raise_for_status()
            for line in r.iter_lines():
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue
                chunk = obj.get("response", "")
                if chunk:
                    yield chunk
    except httpx.HTTPError as e:
        yield f"\n[Erreur Ollama] {e}"
    except Exception as e:
        yield f"\n[Erreur] {e}"
