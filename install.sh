#!/usr/bin/env bash
# ==============================================================================
# install.sh — Installation one-shot de Sentinelle 974
# Version: 0.1.0
#
# Installe : la stack Docker Compose (API + Postgres + Prometheus), les agents
# (audit, CVE, souveraineté), le profile AppArmor et le cron.
#
# Usage : sudo ./install.sh
# ==============================================================================

set -euo pipefail

# --- Couleurs -----------------------------------------------------------------
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; NC='\033[0m'
info()  { echo -e "${CYAN}ℹ${NC} $1"; }
ok()    { echo -e "${GREEN}✓${NC} $1"; }
warn()  { echo -e "${YELLOW}⚠${NC} $1"; }
err()   { echo -e "${RED}✗${NC} $1"; }

# --- Prérequis ----------------------------------------------------------------
if [[ "$(id -u)" -ne 0 ]]; then
    err "Ce script doit être lancé en root (sudo ./install.sh)"
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
API_URL="${API_URL:-http://127.0.0.1:8090}"

info "Sentinelle 974 — installation"
info "Répertoire projet : $SCRIPT_DIR"

# --- 1. Vérification des dépendances -----------------------------------------
info "Vérification des dépendances..."
for cmd in docker jq curl python3; do
    if ! command -v "$cmd" &>/dev/null; then
        err "Dépendance manquante : $cmd"
        exit 1
    fi
done
if ! docker compose version &>/dev/null; then
    err "docker compose (plugin) requis"
    exit 1
fi
ok "Dépendances OK"

# --- 2. Stack Docker Compose --------------------------------------------------
info "Démarrage de la stack (API + Postgres + Prometheus)..."
if [[ ! -f "$SCRIPT_DIR/.env" ]]; then
    cp "$SCRIPT_DIR/.env.example" "$SCRIPT_DIR/.env"
    ok ".env créé depuis .env.example"
fi
(cd "$SCRIPT_DIR" && docker compose up -d --build)
ok "Stack démarrée"

# --- 3. Installation des agents ----------------------------------------------
info "Installation des agents..."
install -m 0755 "$SCRIPT_DIR/agent/sentinelle-agent.sh" /usr/local/bin/sentinelle-agent
install -m 0755 "$SCRIPT_DIR/agent/sovereignty-collect.py" /usr/local/bin/sovereignty-collect
install -m 0755 "$SCRIPT_DIR/agent/cve-collect.py" /usr/local/bin/cve-collect
ok "Agents installés dans /usr/local/bin"

# --- 4. Profile AppArmor ------------------------------------------------------
info "Installation du profile AppArmor..."
if command -v aa-status &>/dev/null; then
    install -m 0644 "$SCRIPT_DIR/agent/usr.bin.sentinelle-agent" /etc/apparmor.d/
    apparmor_parser -r /etc/apparmor.d/usr.bin.sentinelle-agent 2>/dev/null || \
        warn "AppArmor : parser échoué (vérifier le profile)"
    aa-complain /usr/local/bin/sentinelle-agent 2>/dev/null || \
        warn "AppArmor : aa-complain échoué (mode complain non activé)"
    ok "Profile AppArmor installé (mode complain — passer à enforce après validation)"
else
    warn "AppArmor non disponible — profile ignoré"
fi

# --- 5. Cron ------------------------------------------------------------------
info "Installation du cron..."
install -m 0644 "$SCRIPT_DIR/agent/sentinelle-cron" /etc/cron.d/sentinelle
ok "Cron installé (/etc/cron.d/sentinelle)"

# --- 6. Vérification finale ---------------------------------------------------
info "Vérification de l'API..."
sleep 3
if curl -s --max-time 5 "$API_URL/health" | jq -e '.status' &>/dev/null; then
    ok "API répond sur $API_URL"
    curl -s "$API_URL/health" | jq .
else
    warn "API pas encore joignable sur $API_URL — vérifier 'docker compose logs api'"
fi

echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  Sentinelle 974 installée !${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
echo "  Dashboard : http://127.0.0.1:8090/dashboard"
echo "  Rapport   : http://127.0.0.1:8090/report.pdf"
echo "  API       : http://127.0.0.1:8090/health"
echo ""
echo "  Lancer un premier audit :"
echo "    sudo sentinelle-agent --api $API_URL"
echo "    sudo sovereignty-collect --api $API_URL"
echo "    python3 /usr/local/bin/cve-collect --api $API_URL"
echo ""
echo "  Durcir AppArmor (après validation) :"
echo "    sudo aa-enforce /usr/local/bin/sentinelle-agent"
