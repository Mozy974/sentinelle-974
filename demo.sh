#!/usr/bin/env bash
# ==============================================================================
# demo.sh — Démo guidée Sentinelle 974 (scénario client)
# Version: 0.1.0
#
# Scénario : « Voici ce qui sort vraiment de votre machine »
#  1. Démarre la stack (API + Postgres + Prometheus)
#  2. Lance l'audit d'inventaire + les CVE + la collecte souveraineté
#  3. Ouvre le dashboard dans le navigateur
#  4. Génère le rapport PDF pour le client
#
# Usage : ./demo.sh [--port 8090]
# ==============================================================================

set -euo pipefail

RED='\033[0;31m'; GREEN='\033[0;32m'; CYAN='\033[0;36m'; BOLD='\033[1m'; NC='\033[0m'
API_URL="${API_URL:-http://127.0.0.1:8090}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

step() { echo -e "\n${BOLD}${CYAN}━━━ $1 ━━━${NC}"; }
ok()   { echo -e "  ${GREEN}✓${NC} $1"; }

step "1. Démarrage de la stack"
(cd "$SCRIPT_DIR" && docker compose up -d --build)
ok "Stack démarrée (API + Postgres + Prometheus)"

step "2. Attente de l'API"
for i in $(seq 1 30); do
    if curl -s --max-time 2 "$API_URL/health" >/dev/null 2>&1; then break; fi
    sleep 2
done
curl -s "$API_URL/health" | jq . && ok "API répond"

step "3. Audit d'inventaire (que tourne sur la machine ?)"
bash "$SCRIPT_DIR/agent/sentinelle-agent.sh" --inventory-only --api "$API_URL" 2>&1 | tail -3

step "4. Scan CVE (quelles vulnérabilités ?)"
python3 "$SCRIPT_DIR/agent/cve-collect.py" --quiet --api "$API_URL" 2>&1 | tail -3 || \
    echo "  (scan CVE sauté — nécessite le téléchargement initial du tracker)"

step "5. Collecte souveraineté (qu'est-ce qui sort ?)"
python3 "$SCRIPT_DIR/agent/sovereignty-collect.py" --api "$API_URL" 2>&1 | tail -3

step "6. Score de conformité"
curl -s "$API_URL/sovereignty-score" | jq '{score, grade}' 2>/dev/null || \
    echo "  (aucun flux observé — score non calculé)"

step "7. Ouverture du dashboard"
DASHBOARD="$API_URL/dashboard"
echo "  Dashboard : $DASHBOARD"
command -v xdg-open >/dev/null 2>&1 && xdg-open "$DASHBOARD" || true

step "8. Rapport PDF client"
curl -s -o "$SCRIPT_DIR/rapport-sentinelle-974.pdf" "$API_URL/report.pdf"
ok "Rapport généré : $SCRIPT_DIR/rapport-sentinelle-974.pdf"

echo ""
echo -e "${GREEN}${BOLD}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}${BOLD}  Démo terminée. Pitch 30s :${NC}"
echo -e "  « Vos données partent hors de l'île sans que vous le sachiez."
echo -e "    Sentinelle 974 vous montre quoi, et vous aide à tout garder"
echo -e "    à La Réunion — RGPD + résilience cyclone. »"
echo -e "${GREEN}${BOLD}═══════════════════════════════════════════════════════════════${NC}"
