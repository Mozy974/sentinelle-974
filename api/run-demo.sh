#!/usr/bin/env bash
# Lance l'API Sentinelle 974 en mode démo (SQLite + Luciole 1.1B)
set -e
cd "$(dirname "$0")"
unset PYTHONPATH
export DATABASE_URL="sqlite:///./demo.db"
export OLLAMA_BASE_URL="http://127.0.0.1:11434"
export SENTINELLE_HOST="kali"
export SENTINELLE_LLM_MODEL="OpenLLM-France/Luciole-Instruct-1.1:1B"
exec .venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8090
