# Démo guidée — Sentinelle 974

Scénario client : **« Voici ce qui sort vraiment de votre machine »**

## Prérequis

- Docker + `docker compose`
- `python3`, `jq`, `curl`
- Ollama local optionnel (pour l'agent IA `/explain`)

## Lancer la démo

```bash
cd sentinelle-974
./demo.sh
```

La démo enchaîne 8 étapes automatiquement :

1. **Stack** — démarre API + Postgres + Prometheus (Compose)
2. **Santé** — vérifie `/health`
3. **Inventaire** — `sentinelle-agent.sh` : conteneurs, services, ports, Ollama
4. **CVE** — `cve-collect.py` : vulnérabilités Debian (423 détectées sur Kali)
5. **Souveraineté** — `sovereignty-collect.py` : flux sortants
6. **Score** — `/sovereignty-score` : note A→F
7. **Dashboard** — ouvre `http://127.0.0.1:8090/dashboard`
8. **Rapport PDF** — `rapport-sentinelle-974.pdf` pour le client

## Script de la démo (ce qu'on dit au client)

| Étape | Ce qu'on montre | Ce qu'on dit |
|---|---|---|
| 3 | La liste des services | « Tout ce qui tourne sur votre machine, en clair. » |
| 4 | Les CVE | « Les failles connues, avec leur gravité. » |
| 5 | Les flux sortants | « Ici, ce qui part réellement : vers l'UE, ou hors UE. » |
| 6 | Le score | « Votre note de conformité souveraineté. » |
| 7 | Le dashboard | « Une page, lisible par votre dirigeant. » |
| 8 | Le PDF | « Le rapport pour votre assurance / audit. » |

## Argument clé (à répéter)

> **Aucune donnée ne quitte la machine.** Le scan, l'analyse, l'IA (Ollama local) —
> tout tourne sur place. C'est la différence avec un SaaS US.

## Après la démo

- Le rapport PDF (`rapport-sentinelle-974.pdf`) est laissé au client.
- Proposer l'**audit ponctuel** (490 €) comme première vente, puis l'abonnement.

## Remarques

- Le **cold start** de l'agent IA (Ollama) peut prendre 30s-2min. Pour une démo
  fluide, pré-charger le modèle avant (voir README, section « Agent IA local »).
- La collecte souveraineté et l'audit complet nécessitent `sudo` pour voir les
  noms de processus (`ss -p`). Sans sudo, l'inventaire reste fonctionnel.
