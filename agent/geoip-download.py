#!/usr/bin/env python3
# ==============================================================================
# geoip-download.py — Télécharge la base GeoLite2-City (MaxMind, gratuite)
# Version: 0.1.0
#
# Nécessite une clé de licence MaxMind gratuite (https://www.maxmind.com/en/geolite2/signup)
#   export MAXMIND_LICENSE_KEY=xxxx
#   python3 geoip-download.py --out ~/.cache/sentinelle/GeoLite2-City.mmdb
#
# La base est ensuite lue LOCALEMENT par l'API (geoip2) — aucun appel externe
# au moment du scan. C'est le point clé de la souveraineté.
# ==============================================================================

from __future__ import annotations

import argparse
import os
import sys
import tarfile
import urllib.request

BASE_URL = "https://download.maxmind.com/app/geoip_download"
EDITION = "GeoLite2-City"


def main() -> int:
    ap = argparse.ArgumentParser(description="Télécharge GeoLite2-City (MaxMind)")
    ap.add_argument("--out", default=os.path.expanduser("~/.cache/sentinelle/GeoLite2-City.mmdb"))
    ap.add_argument("--key", default=os.environ.get("MAXMIND_LICENSE_KEY", ""))
    args = ap.parse_args()

    if not args.key:
        print("ERREUR: clé MaxMind manquante. export MAXMIND_LICENSE_KEY=xxxx", file=sys.stderr)
        print("Inscription gratuite: https://www.maxmind.com/en/geolite2/signup", file=sys.stderr)
        return 1

    url = f"{BASE_URL}?edition_id={EDITION}&license_key={args.key}&suffix=tar.gz"
    print(f"Téléchargement de {EDITION}...")
    req = urllib.request.Request(url, headers={"User-Agent": "sentinelle-974/0.1"})
    with urllib.request.urlopen(req, timeout=120) as r:
        data = r.read()

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    tmp = args.out + ".tar.gz"
    with open(tmp, "wb") as f:
        f.write(data)

    # Extraire le .mmdb du tar.gz
    with tarfile.open(tmp, "r:gz") as tar:
        mmdb = next((m for m in tar.getmembers() if m.name.endswith(".mmdb")), None)
        if not mmdb:
            print("ERREUR: .mmdb introuvable dans l'archive", file=sys.stderr)
            return 1
        src = tar.extractfile(mmdb)
        if src is None:
            print("ERREUR: impossible d'extraire le .mmdb", file=sys.stderr)
            return 1
        with open(args.out, "wb") as dst:
            dst.write(src.read())

    os.remove(tmp)
    print(f"Base GeoIP installée: {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
