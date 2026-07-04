#!/bin/bash
# J.A.R.V.I.S. OS - Shutdown Script
# Gracefully stops all JARVIS OS services

set -euo pipefail

JARVIS_ROOT="/opt/data/JARVIS_OS"
LOGS_DIR="$JARVIS_ROOT/logs"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')] ✓${NC} $1"
}

warning() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] ⚠${NC} $1"
}

error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ✗${NC} $1"
}

stop_service() {
    local name="$1"
    local pid_file="$LOGS_DIR/$name.pid"

    if [[ -f "$pid_file" ]]; then
        local pid=$(cat "$pid_file")
        if kill -0 $pid 2>/dev/null; then
            log "Stopping $name (PID: $pid)..."
            kill $pid
            local count=0
            while kill -0 $pid 2>/dev/null && [[ $count -lt 10 ]]; do
                sleep 1
                ((count++))
            done
            if kill -0 $pid 2>/dev/null; then
                kill -9 $pid
                warning "$name force killed after timeout"
            else
                success "$name stopped gracefully"
            fi
        fi
        rm -f "$pid_file"
    fi
}

main() {
    log "═══════════════════════════════════════"
    log "  J.A.R.V.I.S. OS SHUTDOWN SEQUENCE"
    log "═══════════════════════════════════════"

    # Save state before shutdown
    log "Saving system state..."
    python3 -c "
import json
from datetime import datetime
from pathlib import Path
state = {
    'shutdown_time': datetime.now().isoformat(),
    'services_stopped': []
}
Path('/opt/data/JARVIS_OS/logs/shutdown_state.json').write_text(json.dumps(state, indent=2))
" 2>/dev/null || true

    # Stop in reverse order (backup first, core last)
    services=(
        "backup_service"
        "cron_service"
        "agent_orchestrator"
        "voice_pipeline"
        "mission_control"
        "brain_sync"
        "jarvis_daemon"
    )

    for service in "${services[@]}"; do
        stop_service "$service"
    done

    log "═══════════════════════════════════════"
    success "J.A.R.V.I.S. OS SHUTDOWN COMPLETE"
    log "═══════════════════════════════════════"
}

main