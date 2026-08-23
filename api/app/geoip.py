"""Sentinelle 974 — géolocalisation locale (MaxMind GeoLite2).

Lit la base GeoLite2-City LOCALEMENT (aucun appel externe au scan).
Fallback gracieux si la base ou geoip2 est absent : 'other'.
"""
from __future__ import annotations

import os

_reader = None
_geoip2_available = True

try:
    import geoip2.database  # type: ignore
except ImportError:
    _geoip2_available = False

# Pays de l'UE (ISO 3166-1 alpha-2) — pour classer 'eu'
EU_COUNTRIES = {
    "AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR", "DE", "GR",
    "HU", "IE", "IT", "LV", "LT", "LU", "MT", "NL", "PL", "PT", "RO", "SK",
    "SI", "ES", "SE",
}

# Pays hors UE à signaler explicitement
NON_EU_WATCH = {"US", "CN", "RU", "GB", "IN", "SG", "HK", "TW", "IL", "AE"}


def _load_reader():
    global _reader
    if _reader is not None:
        return _reader
    if not _geoip2_available:
        return None
    path = os.environ.get(
        "GEOIP_DB",
        os.path.expanduser("~/.cache/sentinelle/GeoLite2-City.mmdb"),
    )
    if not os.path.exists(path):
        return None
    try:
        _reader = geoip2.database.Reader(path)
    except Exception:
        _reader = None
    return _reader


def country_for_ip(ip: str) -> str | None:
    """Retourne le code pays ISO (ex: 'FR') ou None si inconnu/indisponible."""
    reader = _load_reader()
    if reader is None:
        return None
    try:
        return reader.city(ip).country.iso_code
    except Exception:
        return None


def region_for_country(country: str | None) -> str:
    """Mappe un code pays vers une région Sentinelle : eu/us/cn/ru/other."""
    if not country:
        return "other"
    c = country.upper()
    if c in EU_COUNTRIES:
        return "eu"
    if c == "US":
        return "us"
    if c == "CN":
        return "cn"
    if c == "RU":
        return "ru"
    if c in NON_EU_WATCH:
        return "other"  # hors UE, signalé mais pas de catégorie dédiée
    return "other"
