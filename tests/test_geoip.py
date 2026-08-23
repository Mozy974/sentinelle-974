"""Tests du module geoip (mapping pays -> région) — logique pure."""
from app import geoip


def test_region_for_country_eu():
    for c in ("FR", "DE", "ES", "IT"):
        assert geoip.region_for_country(c) == "eu"


def test_region_for_country_watch():
    assert geoip.region_for_country("US") == "us"
    assert geoip.region_for_country("CN") == "cn"
    assert geoip.region_for_country("RU") == "ru"


def test_region_for_country_none():
    assert geoip.region_for_country(None) == "other"


def test_region_for_country_other():
    # Hors UE mais pas une catégorie dédiée (GB est hors UE depuis le Brexit)
    assert geoip.region_for_country("GB") == "other"
    assert geoip.region_for_country("") == "other"


def test_country_for_ip_no_db():
    # Sans base GeoIP installée -> None (fallback gracieux)
    r = geoip.country_for_ip("8.8.8.8")
    assert r is None or isinstance(r, str)
