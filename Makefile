# ==============================================================================
# Sentinelle 974 — Makefile
# ==============================================================================
SHELL := /bin/bash
COMPOSE := docker compose

.PHONY: up down logs ps build health agent scan sovereignty report clean

## Démarre la stack (API + Postgres + Prometheus)
up:
	$(COMPOSE) up -d --build

## Arrête la stack
down:
	$(COMPOSE) down

## Logs (suivi)
logs:
	$(COMPOSE) logs -f api

## État des conteneurs
ps:
	$(COMPOSE) ps

## Rebuild l'image API
build:
	$(COMPOSE) build api

## Vérifie /health de l'API
health:
	@curl -s http://127.0.0.1:8090/health | jq .

## Lance l'agent d'audit (hôte) et pousse les findings vers l'API
agent:
	sudo bash agent/sentinelle-agent.sh

## Scan d'inventaire uniquement (docker/systemd/ports/ollama)
scan:
	sudo bash agent/sentinelle-agent.sh --inventory-only

## Collecte souveraineté (flux réseau sortants)
sovereignty:
	sudo python3 agent/sovereignty-collect.py

## Génère le rapport Markdown depuis l'API
report:
	@curl -s http://127.0.0.1:8090/report | tee report.md

## Nettoie volumes + conteneurs (DESTRUCTIF)
clean:
	$(COMPOSE) down -v
