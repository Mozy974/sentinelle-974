"""Tests du module souveraineté (classification + score) — logique pure, sans DB."""
from app import sovereignty


def test_classify_ip_private():
    assert sovereignty.classify_ip("10.0.0.5") == "local"
    assert sovereignty.classify_ip("192.168.1.1") == "local"
    assert sovereignty.classify_ip("127.0.0.1") == "local"
    assert sovereignty.classify_ip("172.16.0.1") == "local"


def test_classify_ip_public():
    # Sans base GeoIP, une IP publique -> "other" ; avec base -> eu/us/cn/ru
    r = sovereignty.classify_ip("8.8.8.8")
    assert r in ("other", "us", "eu", "cn", "ru")


def test_classify_ip_invalid():
    assert sovereignty.classify_ip("not-an-ip") == "unknown"


def test_classify_host():
    assert sovereignty.classify_host("api.openai.com") == "cloud_llm"
    assert sovereignty.classify_host("chatgpt.com") == "cloud_llm"
    assert sovereignty.classify_host("telemetry.mozilla.org") == "telemetry"
    assert sovereignty.classify_host("localhost") == "local"
    assert sovereignty.classify_host("example.com") == "other"


def test_verdict_for():
    assert sovereignty.verdict_for("local", "") == "allow"
    assert sovereignty.verdict_for("eu", "") == "allow"
    assert sovereignty.verdict_for("cloud_llm", "") == "block"
    assert sovereignty.verdict_for("telemetry", "") == "block"
    assert sovereignty.verdict_for("us", "") == "warn"
    assert sovereignty.verdict_for("cn", "") == "warn"


def test_compute_score_clean():
    res = sovereignty.compute_score([{"region": "local"}, {"region": "eu"}])
    assert res["score"] == 100.0
    assert res["grade"] == "A"
    assert res["total_flows"] == 2


def test_compute_score_penalties():
    res = sovereignty.compute_score([
        {"region": "cloud_llm"},   # -30
        {"region": "telemetry"},   # -20
        {"region": "us"},          # -10
        {"region": "local"},       # 0
    ])
    assert res["score"] == 40.0
    assert res["grade"] == "F"
    assert res["penalties"]["cloud_llm"] == 1
    assert res["penalties"]["telemetry"] == 1
    assert res["penalties"]["non_eu"] == 1
    assert res["penalties"]["local"] == 1


def test_compute_score_floor():
    res = sovereignty.compute_score([{"region": "cloud_llm"}] * 10)
    assert res["score"] == 0.0  # plancher à 0
    assert res["grade"] == "F"
