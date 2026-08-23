"""Sentinelle 974 — logique de souveraineté.

Classement des destinations réseau par région, sans appel externe :
- plages privées (RFC1918 / loopback / link-local) -> "local"
- plages publiques -> "other" (GeoIP local optionnel via geoip2, sinon inconnu)
Le verdict est dérivé de la politique (aucun LLM cloud, aucune télémétrie).
"""
from __future__ import annotations

import ipaddress

# Plages privées / locales (RFC1918, loopback, link-local, CGNAT, multicast)
_PRIVATE_NETS = [
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("169.254.0.0/16"),
    ipaddress.ip_network("100.64.0.0/10"),
    ipaddress.ip_network("224.0.0.0/4"),
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("fc00::/7"),
    ipaddress.ip_network("fe80::/10"),
]

# Domaines / hôtes connus de télémétrie ou de LLM cloud (liste défensive, non exhaustive)
_TELEMETRY_HOSTS = {
    "telemetry.mozilla.org", "incoming.telemetry.mozilla.org",
    "telemetry.ubuntu.com", "metrics.ubuntu.com",
    "dc.services.visualstudio.com", "vortex.data.microsoft.com",
    "settings-win.data.microsoft.com", "telemetry.microsoft.com",
    "www.google-analytics.com", "ssl.google-analytics.com",
    "analytics.google.com", "stats.g.doubleclick.net",
    "sentry.io", "o*.ingest.sentry.io",
}

_CLOUD_LLM_HOSTS = {
    "api.openai.com", "chatgpt.com", "api.anthropic.com", "claude.ai",
    "generativelanguage.googleapis.com", "api.mistral.ai",
    "api.deepseek.com", "api.groq.com", "api.together.xyz",
    "api.perplexity.ai", "api.cohere.ai", "api.replicate.com",
    "openrouter.ai", "api.openrouter.ai",
}


def classify_ip(ip: str) -> str:
    """Retourne 'local' si l'IP est privée, sinon région GeoIP (eu/us/cn/ru/other)."""
    try:
        addr = ipaddress.ip_address(ip)
    except ValueError:
        return "unknown"
    for net in _PRIVATE_NETS:
        if addr in net:
            return "local"
    # IP publique : géolocalisation locale (MaxMind) si dispo
    from . import geoip

    country = geoip.country_for_ip(ip)
    return geoip.region_for_country(country)


def classify_host(host: str) -> str:
    """Classe un nom d'hôte : local / cloud_llm / telemetry / other."""
    h = host.lower().rstrip(".")
    if h in ("localhost",) or h.endswith(".local") or h.endswith(".lan"):
        return "local"
    if h in _CLOUD_LLM_HOSTS or any(h.endswith("." + d) for d in _CLOUD_LLM_HOSTS):
        return "cloud_llm"
    if h in _TELEMETRY_HOSTS or any(h.endswith("." + d) for d in _TELEMETRY_HOSTS):
        return "telemetry"
    return "other"


def verdict_for(region: str, host: str) -> str:
    """Déduit le verdict (allow/warn/block) de la politique souveraineté."""
    if region == "local":
        return "allow"
    if region == "eu":
        return "allow"  # dans l'UE : conforme RGPD
    if region == "cloud_llm":
        return "block"
    if region == "telemetry":
        return "block"
    # IP publique hors UE (us/cn/ru/other) : avertissement
    return "warn"


def compute_score(flows: list[dict]) -> dict:
    """Calcule un score de conformité 0..100 + grade A..F.

    Pénalités :
    - flux vers LLM cloud : -30 chacun
    - flux télémétrie : -20 chacun
    - flux hors UE (us/cn/ru/other) : -10 chacun
    - flux UE (eu) : conforme, pas de pénalité
    """
    score = 100.0
    penalties = {"cloud_llm": 0, "telemetry": 0, "non_eu": 0, "eu": 0, "local": 0}
    for f in flows:
        region = f.get("region", "unknown")
        if region == "cloud_llm":
            score -= 30
            penalties["cloud_llm"] += 1
        elif region == "telemetry":
            score -= 20
            penalties["telemetry"] += 1
        elif region in ("us", "cn", "ru", "other"):
            score -= 10
            penalties["non_eu"] += 1
        elif region == "eu":
            penalties["eu"] += 1
        elif region == "local":
            penalties["local"] += 1
    score = max(0.0, min(100.0, score))
    grade = _grade(score)
    return {
        "score": round(score, 1),
        "grade": grade,
        "penalties": penalties,
        "total_flows": len(flows),
    }


def _grade(score: float) -> str:
    if score >= 90:
        return "A"
    if score >= 80:
        return "B"
    if score >= 70:
        return "C"
    if score >= 60:
        return "D"
    if score >= 50:
        return "E"
    return "F"
