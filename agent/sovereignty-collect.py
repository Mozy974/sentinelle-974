#!/usr/bin/env python3
# ==============================================================================
# sovereignty-collect.py — Collecteur de flux réseau sortants (Sentinelle 974)
# Version: 0.1.0
#
# Capture les connexions TCP/UDP sortantes (hors loopback) via `ss` et les pousse
# vers l'API (POST /flows). L'API classe les destinations (local / cloud LLM /
# télémétrie / eu / us / cn / ru) et recalcule le score de conformité.
#
# Usage : sudo python3 sovereignty-collect.py [--api http://127.0.0.1:8090]
# ==============================================================================

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import urllib.request

# Plages privées / loopback (à ignorer : flux internes)
_PRIVATE_PREFIXES = ("127.", "10.", "192.168.", "172.16.", "172.17.", "172.18.",
                     "172.19.", "172.20.", "172.21.", "172.22.", "172.23.",
                     "172.24.", "172.25.", "172.26.", "172.27.", "172.28.",
                     "172.29.", "172.30.", "172.31.", "169.254.", "::1", "fe80:")


def _split_addr(addr: str) -> tuple[str, str]:
    """Sépare une adresse 'ip:port' (gère IPv6 [::1]:port et scope %iface)."""
    addr = addr.strip()
    if addr.startswith("["):  # IPv6 entre crochets
        m = re.match(r"^\[([^\]]+)\]:(\d+)$", addr)
        if m:
            return m.group(1), m.group(2)
        return addr, ""
    if addr.count(":") == 1:  # IPv4:port
        ip, port = addr.rsplit(":", 1)
        return ip, port
    # IPv6 sans crochets (rare dans ss) ou pas de port
    return addr, ""


def _is_private(ip: str) -> bool:
    return ip.startswith(_PRIVATE_PREFIXES)


def collect_tcp() -> list[dict]:
    flows = []
    try:
        out = subprocess.run(
            ["ss", "-tnp", "state", "established"],
            capture_output=True, text=True, timeout=30,
        ).stdout
    except (OSError, subprocess.TimeoutExpired):
        return flows
    for line in out.splitlines()[1:]:
        parts = line.split()
        if len(parts) < 4:
            continue
        peer = parts[3]
        proc = parts[4] if len(parts) > 4 else ""
        proc = re.sub(r'users:\(\(.*?\)\)', '', proc).strip('",')
        ip, port = _split_addr(peer)
        if not port or not port.isdigit():
            continue
        if _is_private(ip):
            continue
        flows.append({
            "dest_ip": ip, "dest_port": int(port), "proto": "tcp",
            "process": proc, "dest_host": "", "region": "unknown", "verdict": "allow",
        })
    return flows


def collect_udp() -> list[dict]:
    flows = []
    try:
        out = subprocess.run(
            ["ss", "-unp"], capture_output=True, text=True, timeout=30,
        ).stdout
    except (OSError, subprocess.TimeoutExpired):
        return flows
    for line in out.splitlines()[1:]:
        parts = line.split()
        if len(parts) < 4:
            continue
        peer = parts[3]
        proc = parts[4] if len(parts) > 4 else ""
        proc = re.sub(r'users:\(\(.*?\)\)', '', proc).strip('",')
        ip, port = _split_addr(peer)
        if not port or not port.isdigit():
            continue
        if _is_private(ip):
            continue
        flows.append({
            "dest_ip": ip, "dest_port": int(port), "proto": "udp",
            "process": proc, "dest_host": "", "region": "unknown", "verdict": "allow",
        })
    return flows


def push(flows: list[dict], api_url: str) -> None:
    if not flows:
        print("Aucun flux sortant observé.")
        return
    payload = json.dumps(flows).encode()
    req = urllib.request.Request(
        f"{api_url}/flows", data=payload,
        headers={"Content-Type": "application/json"}, method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            resp = json.loads(r.read())
        print(f"Poussé {len(resp)} flux vers {api_url}/flows")
    except Exception as e:
        print(f"Erreur push API: {e}", file=sys.stderr)


def main() -> int:
    ap = argparse.ArgumentParser(description="Collecteur souveraineté Sentinelle 974")
    ap.add_argument("--api", default="http://127.0.0.1:8090")
    args = ap.parse_args()

    flows = collect_tcp() + collect_udp()
    # Dédupliquer (ip, port, proto)
    seen = set()
    dedup = []
    for f in flows:
        key = (f["dest_ip"], f["dest_port"], f["proto"])
        if key not in seen:
            seen.add(key)
            dedup.append(f)

    print(f"Flux sortants détectés: {len(dedup)}")
    push(dedup, args.api)
    return 0


if __name__ == "__main__":
    sys.exit(main())
