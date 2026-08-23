# Sentinelle 974

Plateforme **self-hosted** de souveraineté des données + posture cyber, pensée pour
les PME et collectivités de La Réunion. **Aucune donnée métier ne quitte la machine
(ou le LAN).**

## Modules

| Module | Endpoint | Description |
|---|---|---|
| Découverte | `GET /inventory` | Conteneurs Docker, services systemd, ports, Ollama |
| Audit CVE | `GET /cves` | Findings CVE (Debian tracker + NVD + APT) |
| Souveraineté | `GET /sovereignty-score` + `GET /flows` | Carte des flux sortants + score de conformité |
| GeoIP local | — | Classement eu/us/cn/ru via base MaxMind locale |
| Politique | — | Règles : aucun LLM cloud, aucune télémétrie |
| Dashboard | `GET /dashboard` | Page unique : score + findings + flux (100% local) |
| Rapport | `GET /report` + `GET /report.pdf` | Markdown + PDF prêt pour un salon, un garage, une mairie |
| Agent IA | `GET /explain/{id}` | Explication d'un finding en FR/créole (Ollama local) |

## Architecture

```
[hôte Debian]
  ├── sentinelle-api (FastAPI)      :8090
  ├── sentinelle-agent (Bash + AppArmor)
  ├── postgres (sentinelle-db)      :5433
  ├── prometheus (sentinelle-prom)  :9091
  └── ollama + open-webui (déjà en place :3000)
```

## Démarrage rapide

```bash
cd sentinelle-974
cp .env.example .env
make up          # build + démarre API, Postgres, Prometheus
make health      # vérifie /health
```

## Agent (sur l'hôte)

```bash
# Installer les scripts
sudo cp agent/sentinelle-agent.sh /usr/local/bin/sentinelle-agent
sudo cp agent/sovereignty-collect.py /usr/local/bin/sovereignty-collect
sudo cp agent/cve-collect.py /usr/local/bin/cve-collect
sudo chmod +x /usr/local/bin/sentinelle-agent /usr/local/bin/sovereignty-collect /usr/local/bin/cve-collect

# Lancer un audit complet (inventaire + risques)
sudo sentinelle-agent --api http://127.0.0.1:8090

# Collecter les flux souveraineté
sudo sovereignty-collect --api http://127.0.0.1:8090

# Scan CVE (Debian tracker + NVD + APT)
python3 cve-collect.py --api http://127.0.0.1:8090          # push vers l'API
python3 cve-collect.py --quiet --out /var/log/sentinelle    # cron silencieux
python3 cve-collect.py --nvd --nvd-limit 20                 # enrichissement CVSS
```

## GeoIP local (MaxMind)

```bash
# 1. Clé gratuite : https://www.maxmind.com/en/geolite2/signup
export MAXMIND_LICENSE_KEY=xxxx
python3 agent/geoip-download.py --out ~/.cache/sentinelle/GeoLite2-City.mmdb

# 2. L'API lit la base LOCALEMENT (aucun appel externe au scan)
#    Les IP publiques sont classées eu/us/cn/ru/other.
```

## AppArmor (durcissement)

```bash
sudo cp agent/usr.bin.sentinelle-agent /etc/apparmor.d/
sudo apparmor_parser -r /etc/apparmor.d/usr.bin.sentinelle-agent
sudo aa-complain /usr/local/bin/sentinelle-agent   # observer
sudo aa-enforce /usr/local/bin/sentinelle-agent    # durcir
```

## Cron

```bash
sudo cp agent/sentinelle-cron /etc/cron.d/sentinelle
```

## Endpoints

- `GET /health` — état API + DB + Ollama
- `GET /inventory` — inventaire
- `GET /cves?severity=HIGH` — findings CVE
- `GET /sovereignty-score` — score de conformité (A..F)
- `GET /flows` — flux réseau observés
- `GET /dashboard` — dashboard HTML (score + findings + flux)
- `GET /report.pdf` — rapport PDF (reportlab)
- `GET /explain/{id}?lang=fr|creole` — explication IA locale d'un finding
- `GET /explain/{id}/stream?format=sse|plain` — explication en streaming (token par token)
- `POST /ingest` — ingestion findings (agent)
- `POST /flows` — ingestion flux (agent)
- `GET /report` — rapport Markdown

## Souveraineté — comment ça marche

1. `sovereignty-collect.py` capture les connexions sortantes (`ss -tnp`).
2. L'API classe chaque destination : `local` (RFC1918) / `eu` / `cloud_llm` / `telemetry` / `us` / `cn` / `ru` / `other`.
3. Le score part de 100 et pénalise : LLM cloud −30, télémétrie −20, hors UE −10.
4. Grade A..F affiché dans le rapport.

> GeoIP local optionnel : brancher `geoip2` + base MaxMind locale pour classer
> `other` en `eu` / `us` / `cn` / `ru` sans appel externe.

## Agent IA local — prérequis & choix du modèle

L'endpoint `GET /explain/{id}?lang=fr|creole` fait de l'inférence **100% locale** via Ollama.
Deux variantes :

- `GET /explain/{id}` — réponse complète (JSON, attend la fin de l'inférence).
- `GET /explain/{id}/stream?format=plain|sse` — streaming token par token
  (plus réactif pour une démo ; `format=plain` pour `curl`, `sse` pour le front).

Points à connaître :

- **Modèle par défaut** : `OpenLLM-France/Luciole-Instruct-1.1:1B` (léger, français, chat classique).
- **Éviter les modèles "reasoning"** (ex : `qwen3.5`) : ils génèrent dans le champ
  `thinking` et laissent `content` vide → réponse nulle côté API.
- **Cold start** : le chargement du modèle en RAM prend 30s à 2 min selon le modèle
  et la charge machine. Pré-charger avec `keep_alive` avant une démo.
- **Machine requise** : l'inférence CPU est ~2 s/token sur une machine saturée.
  Pour une démo fluide, fermer les apps lourdes (navigateur/desktop) ou utiliser
  une machine dédiée (le mini-PC cible), pas le poste de dev.

Surcharge : `SENTINELLE_LLM_MODEL=mistral:latest` (ou tout modèle chat local).

## Différenciation 974

- Données restent à La Réunion (RGPD + résilience cyclone / coupure câble).
- Contrat de filière numérique 2026-2028 : cybersécurité + souveraineté financés.
- Cible : TPE (salon, garage), collectivités, flottes Debian auditées.

## Limites (MVP)

- Pas d'exploits, pas de PoC d'attaque, pas de payloads — détection + hardening uniquement.
- GeoIP précis nécessite une base locale (optionnel).
- Front : API JSON + rapport Markdown (dashboard HTMX en semaine 5-6).
