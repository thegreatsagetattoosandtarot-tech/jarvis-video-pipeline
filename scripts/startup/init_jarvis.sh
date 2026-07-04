#!/bin/bash
# J.A.R.V.I.S. OS - Master Startup Script
# Starts all JARVIS OS services in the correct order

set -euo pipefail

JARVIS_ROOT="/opt/data/JARVIS_OS"
CONFIG_DIR="$JARVIS_ROOT/config"
LOGS_DIR="$JARVIS_ROOT/logs"
SCRIPTS_DIR="$JARVIS_ROOT/scripts/startup"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."

    # Check Python
    if ! command -v python3 &> /dev/null; then
        error "python3 not found"
        exit 1
    fi

    # Check critical directories
    for dir in "$JARVIS_ROOT" "$CONFIG_DIR" "$LOGS_DIR"; do
        if [[ ! -d "$dir" ]]; then
            error "Missing directory: $dir"
            exit 1
        fi
    done

    # Check config files
    for config in "soul.md" "identity.md" "user.md" "agent.md" "tools.md" "integrations.yaml"; do
        if [[ ! -f "$CONFIG_DIR/$config" ]]; then
            warning "Missing config: $config"
        fi
    done

    # Check Ollama
    if ! curl -s http://localhost:11434/api/tags &> /dev/null; then
        warning "Ollama not running - starting..."
        ollama serve &
        sleep 3
    fi

    success "Prerequisites check complete"
}

# Start a service with logging
start_service() {
    local name="$1"
    local cmd="$2"
    local cwd="${3:-$JARVIS_ROOT}"
    local log_file="$LOGS_DIR/$name.log"

    log "Starting $name..."
    cd "$cwd"
    nohup bash -c "$cmd" >> "$log_file" 2>&1 &
    local pid=$!
    echo $pid > "$LOGS_DIR/$name.pid"
    sleep 1

    if kill -0 $pid 2>/dev/null; then
        success "$name started (PID: $pid)"
        return 0
    else
        error "$name failed to start (check $log_file)"
        return 1
    fi
}

# Stop a service
stop_service() {
    local name="$1"
    local pid_file="$LOGS_DIR/$name.pid"

    if [[ -f "$pid_file" ]]; then
        local pid=$(cat "$pid_file")
        if kill -0 $pid 2>/dev/null; then
            log "Stopping $name (PID: $pid)..."
            kill $pid
            sleep 2
            if kill -0 $pid 2>/dev/null; then
                kill -9 $pid
                warning "$name force killed"
            else
                success "$name stopped"
            fi
        fi
        rm -f "$pid_file"
    fi
}

# Main startup sequence
main() {
    log "═══════════════════════════════════════"
    log "  J.A.R.V.I.S. OS STARTUP SEQUENCE"
    log "═══════════════════════════════════════"

    check_prerequisites

    # Phase 1: Core Services
    log "Phase 1: Core Services"
    start_service "jarvis_daemon" "python3 -m core.jarvis_core"

    # Phase 2: Brain Services
    log "Phase 2: Brain Services"
    start_service "brain_sync" "python3 -m services.brain_sync.brain_sync_service"

    # Phase 3: Dashboard
    log "Phase 3: Mission Control Dashboard"
    start_service "mission_control" "python3 -m services.mission_control.main"

    # Phase 4: Voice Pipeline
    log "Phase 4: Voice Pipeline"
    start_service "voice_pipeline" "python3 -m services.voice_service.main"

    # Phase 5: Agent Orchestrator
    log "Phase 5: Agent Orchestrator"
    start_service "agent_orchestrator" "python3 -m core.agent_orchestrator"

    # Phase 6: Cron Service
    log "Phase 6: Cron Automation"
    start_service "cron_service" "python3 -m services.cron_service.scheduler"

    # Phase 7: Backup Service
    log "Phase 7: Backup Service"
    start_service "backup_service" "python3 -m services.backup_service.backup_scheduler"

    log "═══════════════════════════════════════"
    success "J.A.R.V.I.S. OS STARTUP COMPLETE"
    log "═══════════════════════════════════════"
    log "Dashboard: http://localhost:8080"
    log "Logs: $LOGS_DIR"
    log "PIDs: $LOGS_DIR/*.pid"
}

# Handle arguments
case "${1:-start}" in
    start)
        main
        ;;
    stop)
        log "Stopping J.A.R.V.I.S. OS..."
        for pid_file in "$LOGS_DIR"/*.pid; do
            [[ -f "$pid_file" ]] || continue
            name=$(basename "$pid_file" .pid)
            stop_service "$name"
        done
        success "All services stopped"
        ;;
    restart)
        $0 stop
        sleep 3
        $0 start
        ;;
    status)
        echo "Service Status:"
        echo "==============="
        for pid_file in "$LOGS_DIR"/*.pid; do
            [[ -f "$pid_file" ]] || continue
            name=$(basename "$pid_file" .pid)
            pid=$(cat "$pid_file")
            if kill -0 $pid 2>/dev/null; then
                echo -e "  ${GREEN}●${NC} $name (PID: $pid)"
            else
                echo -e "  ${RED}○${NC} $name (DEAD)"
            fi
        done
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status}"
        exit 1
        ;;
esac