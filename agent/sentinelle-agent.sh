#!/usr/bin/env bash
# ==============================================================================
# sentinelle-agent.sh — Agent d'audit Sentinelle 974
# Version: 0.1.0
#
# Réutilise kali-pentest-audit.sh (audit OPSEC complet) puis pousse les findings
# vers l'API Sentinelle (POST /ingest). Aucune donnée ne quitte la machine.
#
# Usage:
#   sudo ./sentinelle-agent.sh [--inventory-only] [--api http://127.0.0.1:8090]
#   sudo ./sentinelle-agent.sh --inventory-only   # scan rapide (docker/systemd/ports/ollama)
# ==============================================================================

set -uo pipefail

API_URL="${API_URL:-http://127.0.0.1:8090}"
AUDIT_SCRIPT="${AUDIT_SCRIPT:-/home/mozy/Bureau/Scripts/kali-pentest-audit.sh}"
INVENTORY_ONLY=false
HOST="$(hostname)"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --inventory-only) INVENTORY_ONLY=true; shift;;
        --api) API_URL="$2"; shift 2;;
        --help|-h)
            echo "Usage: sudo $0 [--inventory-only] [--api URL]"
            exit 0;;
        *) echo "Argument inconnu: $1"; exit 1;;
    esac
done

# --- Inventaire rapide (toujours exécuté) ------------------------------------
collect_inventory() {
    local findings=()

    # Docker
    if command -v docker &>/dev/null && docker info &>/dev/null 2>&1; then
        while IFS= read -r line; do
            [[ -z "$line" ]] && continue
            name="$(echo "$line" | awk '{print $1}')"
            image="$(echo "$line" | awk '{print $2}')"
            ports="$(echo "$line" | awk '{for(i=3;i<=NF;i++) printf "%s ", $i}')"
            findings+=("{\"category\":\"inventory\",\"severity\":\"INFO\",\"title\":\"Conteneur: $name\",\"description\":\"image=$image ports=$ports\",\"host\":\"$HOST\",\"source\":\"agent\",\"data\":{\"type\":\"docker\",\"name\":\"$name\",\"image\":\"$image\"}}")
        done < <(docker ps --format '{{.Names}}\t{{.Image}}\t{{.Ports}}' 2>/dev/null)
    fi

    # Services systemd actifs (liste ciblée)
    for svc in ollama docker postgresql redis-server nginx apache2 ssh tailscaled openvpn wireguard tor fail2ban ufw; do
        state="$(systemctl is-active "$svc" 2>/dev/null || echo absent)"
        if [[ "$state" == "active" ]]; then
            findings+=("{\"category\":\"inventory\",\"severity\":\"INFO\",\"title\":\"Service: $svc\",\"description\":\"actif\",\"host\":\"$HOST\",\"source\":\"agent\",\"data\":{\"type\":\"systemd\",\"name\":\"$svc\",\"state\":\"$state\"}}")
        fi
    done

    # Ports en écoute (TCP)
    while IFS= read -r line; do
        [[ -z "$line" ]] && continue
        addr="$(echo "$line" | awk '{print $4}')"
        proc="$(echo "$line" | awk '{print $6}' | tr -d '",')"
        findings+=("{\"category\":\"inventory\",\"severity\":\"INFO\",\"title\":\"Port: $addr\",\"description\":\"process=$proc\",\"host\":\"$HOST\",\"source\":\"agent\",\"data\":{\"type\":\"port\",\"addr\":\"$addr\",\"process\":\"$proc\"}}")
    done < <(ss -tlnpH 2>/dev/null | tail -n +2)

    # Ollama (modèles)
    if curl -s --max-time 2 http://127.0.0.1:11434/api/tags >/dev/null 2>&1; then
        models="$(curl -s http://127.0.0.1:11434/api/tags | jq -r '.models[].name' 2>/dev/null | tr '\n' ' ')"
        findings+=("{\"category\":\"inventory\",\"severity\":\"INFO\",\"title\":\"Ollama actif\",\"description\":\"modèles: $models\",\"host\":\"$HOST\",\"source\":\"agent\",\"data\":{\"type\":\"ollama\",\"models\":\"$models\"}}")
    fi

    printf '%s\n' "${findings[@]}" | jq -s '.'
}

# --- Audit complet (réutilise kali-pentest-audit.sh) -------------------------
collect_audit() {
    local json_file
    if [[ -x "$AUDIT_SCRIPT" ]]; then
        # Exécute l'audit existant, récupère le JSON généré
        "$AUDIT_SCRIPT" --no-color >/dev/null 2>&1 || true
        json_file="$(ls -t /tmp/debian-security-audit/reports/audit_*.json 2>/dev/null | head -1)"
        if [[ -n "$json_file" ]]; then
            jq -c '[.risks.details[] | {category:"risk",severity:(.severity|ascii_upcase),title:.description,description:"",host:"'"$HOST"'",source:"agent",data:{}}]' "$json_file"
            return
        fi
    fi
    echo "[]"
}

# --- Push vers l'API ---------------------------------------------------------
push_findings() {
    local payload="$1"
    local count
    count="$(echo "$payload" | jq 'length' 2>/dev/null || echo 0)"
    if [[ "$count" == "0" ]]; then
        echo "Aucun finding à pousser."
        return
    fi
    echo "Pousse $count findings vers $API_URL/ingest ..."
    curl -s -X POST "$API_URL/ingest" \
        -H 'Content-Type: application/json' \
        -d "$payload" | jq -r '.[].id' | sed 's/^/  finding id=/'
}

# --- Main --------------------------------------------------------------------
echo "=== Sentinelle 974 — Agent ($HOST) ==="

INV="$(collect_inventory)"
push_findings "$INV"

if ! $INVENTORY_ONLY; then
    AUD="$(collect_audit)"
    push_findings "$AUD"
fi

echo "Terminé."
