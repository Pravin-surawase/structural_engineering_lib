#!/usr/bin/env bash
# launch_stack.sh — Full-stack development launcher for structural_engineering_lib
#
# Launches FastAPI backend + React frontend with comprehensive health checks
# Supports local (direct) and Docker modes
#
# Usage: ./scripts/launch_stack.sh [--local|--docker|--docker-dev] [options]

set -euo pipefail

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ANSI Colors & Symbols
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
DIM='\033[2m'
NC='\033[0m' # No Color

CHECK="✓"
CROSS="✗"
WARN="⚠"
ARROW="→"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Configuration
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_FILE="/tmp/structural_lib_launch.log"
FASTAPI_PID=""
REACT_PID=""
MODE="local"
VERBOSE=0
OPEN_BROWSER=0
SKIP_REACT=0
SKIP_FASTAPI=0

FASTAPI_PORT=8000
REACT_PORT=5173

HEALTH_CHECK_TIMEOUT_LOCAL=30
HEALTH_CHECK_TIMEOUT_DOCKER=90
PORT_CHECK_TIMEOUT=30

# Platform detection
OS_TYPE="$(uname -s)"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Helper Functions
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

log() {
    echo -e "$@" | tee -a "$LOG_FILE"
}

log_verbose() {
    if [[ $VERBOSE -eq 1 ]]; then
        echo -e "${DIM}$@${NC}" | tee -a "$LOG_FILE"
    else
        echo -e "$@" >> "$LOG_FILE"
    fi
}

success() {
    log "${GREEN}${CHECK}${NC} $@"
}

error() {
    log "${RED}${CROSS}${NC} $@"
}

warning() {
    log "${YELLOW}${WARN}${NC} $@"
}

info() {
    log "${CYAN}${ARROW}${NC} $@"
}

section() {
    log ""
    log "${BOLD}${BLUE}━━━ $@ ━━━${NC}"
}

show_help() {
    cat << EOF
${BOLD}structural_engineering_lib — Full Stack Launcher${NC}

${BOLD}USAGE:${NC}
  ./scripts/launch_stack.sh [options]

${BOLD}MODES:${NC}
  ${GREEN}--local${NC}        Local development mode (default) — FastAPI + React directly
  ${GREEN}--docker${NC}       Docker mode — FastAPI via docker-compose + React directly
  ${GREEN}--docker-dev${NC}   Docker dev mode — FastAPI via docker-compose.dev.yml + React

${BOLD}OPTIONS:${NC}
  ${GREEN}--kill-only${NC}    Just kill existing services, don't start anything
  ${GREEN}--check-only${NC}   Just run pre-flight checks, don't start anything
  ${GREEN}--no-react${NC}     Start FastAPI only, skip React
  ${GREEN}--no-fastapi${NC}   Start React only, skip FastAPI
  ${GREEN}--open${NC}         Open browser automatically when React is ready
  ${GREEN}--verbose${NC}      Show detailed output
  ${GREEN}--help${NC}         Show this help

${BOLD}EXAMPLES:${NC}
  ./scripts/launch_stack.sh                    # Local mode
  ./scripts/launch_stack.sh --docker --open    # Docker mode + open browser
  ./scripts/launch_stack.sh --kill-only        # Just cleanup
  ./scripts/launch_stack.sh --no-react         # FastAPI only

${BOLD}URLS:${NC}
  FastAPI: ${CYAN}http://localhost:8000/docs${NC}
  React:   ${CYAN}http://localhost:5173${NC}

${BOLD}LOGS:${NC}
  ${LOG_FILE}
EOF
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Cleanup & Signal Handling
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

cleanup() {
    log ""
    section "Shutting down services"

    if [[ -n "$FASTAPI_PID" ]] && kill -0 "$FASTAPI_PID" 2>/dev/null; then
        info "Stopping FastAPI (PID $FASTAPI_PID)..."
        kill "$FASTAPI_PID" 2>/dev/null || true
        wait "$FASTAPI_PID" 2>/dev/null || true
        success "FastAPI stopped"
    fi

    if [[ -n "$REACT_PID" ]] && kill -0 "$REACT_PID" 2>/dev/null; then
        info "Stopping React (PID $REACT_PID)..."
        kill "$REACT_PID" 2>/dev/null || true
        wait "$REACT_PID" 2>/dev/null || true
        success "React stopped"
    fi

    if [[ "$MODE" == "docker"* ]]; then
        info "Stopping Docker containers..."
        cd "$REPO_ROOT"
        docker compose down 2>/dev/null || true
        success "Docker stopped"
    fi

    log ""
    log "${BOLD}${GREEN}All services stopped${NC}"
}

trap cleanup SIGINT SIGTERM EXIT

get_process_on_port() {
    local port=$1
    if [[ "$OS_TYPE" == "Darwin" ]]; then
        lsof -ti ":$port" 2>/dev/null || true
    else
        # Linux
        ss -lptn "sport = :$port" 2>/dev/null | awk '{print $6}' | grep -oE 'pid=[0-9]+' | grep -oE '[0-9]+' || true
    fi
}

kill_port() {
    local port=$1
    local pids=$(get_process_on_port "$port")

    if [[ -z "$pids" ]]; then
        log_verbose "Port $port is free"
        return 0
    fi

    for pid in $pids; do
        local proc_name=""
        if [[ "$OS_TYPE" == "Darwin" ]]; then
            proc_name=$(ps -p "$pid" -o comm= 2>/dev/null || echo "unknown")
        else
            proc_name=$(ps -p "$pid" -o cmd= 2>/dev/null || echo "unknown")
        fi

        info "Killing process on port $port (PID $pid: $proc_name)"
        kill -9 "$pid" 2>/dev/null || true
        success "Killed PID $pid"
    done

    # Verify port is now free
    sleep 1
    pids=$(get_process_on_port "$port")
    if [[ -n "$pids" ]]; then
        warning "Port $port still in use after kill, retrying..."
        sleep 2
        for pid in $pids; do
            kill -9 "$pid" 2>/dev/null || true
        done
        sleep 1
        if [[ -n "$(get_process_on_port "$port")" ]]; then
            error "Failed to free port $port after multiple attempts"
            return 1
        fi
    fi
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Phase 0: Kill Existing Services
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

kill_existing_services() {
    section "Phase 0: Cleaning up existing services"

    # Stop Docker containers first
    cd "$REPO_ROOT"
    if docker compose ps 2>/dev/null | grep -q "Up"; then
        info "Stopping running Docker containers..."
        docker compose down 2>/dev/null || true
        success "Docker containers stopped"
    else
        log_verbose "No Docker containers running"
    fi

    # Kill processes on ports
    if [[ $SKIP_FASTAPI -eq 0 ]]; then
        kill_port "$FASTAPI_PORT"
    fi

    if [[ $SKIP_REACT -eq 0 ]]; then
        kill_port "$REACT_PORT"
    fi

    success "Cleanup complete"
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Phase 1: Pre-flight Checks
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

check_python() {
    local venv_python="$REPO_ROOT/.venv/bin/python"

    if [[ ! -x "$venv_python" ]]; then
        error "Python venv not found at .venv/bin/python"
        return 1
    fi

    local py_version=$("$venv_python" --version 2>&1 | grep -oE '[0-9]+\.[0-9]+' | head -1)
    local major=$(echo "$py_version" | cut -d. -f1)
    local minor=$(echo "$py_version" | cut -d. -f2)

    if [[ $major -lt 3 ]] || [[ $major -eq 3 && $minor -lt 11 ]]; then
        error "Python $py_version < 3.11 (required)"
        return 1
    fi

    success "Python $py_version"
    return 0
}

check_node() {
    if ! command -v node &>/dev/null; then
        error "Node.js not found"
        return 1
    fi

    local node_version=$(node --version | grep -oE '[0-9]+' | head -1)
    if [[ $node_version -lt 18 ]]; then
        error "Node.js v$node_version < v18 (required)"
        return 1
    fi

    success "Node.js v$node_version"
    return 0
}

check_npm() {
    if ! command -v npm &>/dev/null; then
        error "npm not found"
        return 1
    fi

    local npm_version=$(npm --version)
    success "npm v$npm_version"
    return 0
}

check_node_modules() {
    if [[ ! -d "$REPO_ROOT/react_app/node_modules" ]]; then
        warning "node_modules not found — will install"
        return 1
    fi
    success "node_modules exists"
    return 0
}

check_ports() {
    local all_free=0

    if [[ $SKIP_FASTAPI -eq 0 ]]; then
        local fastapi_pid=$(get_process_on_port "$FASTAPI_PORT")
        if [[ -n "$fastapi_pid" ]]; then
            error "Port $FASTAPI_PORT in use (PID $fastapi_pid)"
            all_free=1
        else
            success "Port $FASTAPI_PORT free"
        fi
    fi

    if [[ $SKIP_REACT -eq 0 ]]; then
        local react_pid=$(get_process_on_port "$REACT_PORT")
        if [[ -n "$react_pid" ]]; then
            error "Port $REACT_PORT in use (PID $react_pid)"
            all_free=1
        else
            success "Port $REACT_PORT free"
        fi
    fi

    return $all_free
}

check_key_files() {
    local missing=0

    local files=(
        "fastapi_app/main.py"
        "react_app/package.json"
        "Python/structural_lib/__init__.py"
        ".venv/bin/python"
    )

    for file in "${files[@]}"; do
        if [[ ! -f "$REPO_ROOT/$file" ]]; then
            error "Missing: $file"
            missing=1
        else
            log_verbose "Found: $file"
        fi
    done

    if [[ $missing -eq 0 ]]; then
        success "All key files present"
    fi

    return $missing
}

check_structural_lib() {
    cd "$REPO_ROOT"
    if .venv/bin/python -c "from structural_lib import api; print('OK')" &>/dev/null; then
        success "structural_lib imports OK"
        return 0
    else
        error "structural_lib import failed — run: pip install -e Python/"
        return 1
    fi
}

check_docker() {
    # Check Colima
    if ! command -v colima &>/dev/null; then
        error "Colima not found — install: brew install colima"
        return 1
    fi

    if ! colima status &>/dev/null; then
        warning "Colima not running — will start"
        return 1
    fi

    success "Colima running"

    # Check Docker
    if ! docker info &>/dev/null; then
        error "Docker not accessible"
        return 1
    fi

    success "Docker OK"
    return 0
}

check_netcat() {
    if ! command -v nc &>/dev/null; then
        error "netcat (nc) not found — install: brew install netcat (macOS) or apt install netcat (Linux)"
        return 1
    fi
    log_verbose "netcat available"
    return 0
}

check_git_status() {
    cd "$REPO_ROOT"
    if [[ -n $(git status --porcelain 2>/dev/null) ]]; then
        warning "Uncommitted changes detected"
    else
        log_verbose "Git working tree clean"
    fi
}

run_preflight_checks() {
    section "Phase 1: Pre-flight checks"

    local checks_passed=0

    # Always check Python and key files
    check_python || checks_passed=1
    check_key_files || checks_passed=1

    # Check structural_lib import
    if [[ $SKIP_FASTAPI -eq 0 ]]; then
        check_structural_lib || checks_passed=1
    fi

    # Check Node/npm for React
    if [[ $SKIP_REACT -eq 0 ]]; then
        check_node || checks_passed=1
        check_npm || checks_passed=1
        check_node_modules || true  # Non-fatal, we can fix
    fi

    # Check Docker for docker modes (non-fatal — Phase 2 can start Colima)
    if [[ "$MODE" == "docker"* ]]; then
        check_docker || true  # Non-fatal, Phase 2 will fix
    fi

    # Check netcat (required for wait_for_port)
    check_netcat || checks_passed=1

    # Check ports (after kill phase, should be free)
    check_ports || checks_passed=1

    # Check git status (warning only)
    check_git_status

    if [[ $checks_passed -ne 0 ]]; then
        error "Pre-flight checks failed"
        return 1
    fi

    success "All pre-flight checks passed"
    return 0
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Phase 2: Fix Prerequisites
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

fix_prerequisites() {
    section "Phase 2: Installing prerequisites"

    # Install node_modules if missing
    if [[ $SKIP_REACT -eq 0 ]] && [[ ! -d "$REPO_ROOT/react_app/node_modules" ]]; then
        info "Installing npm dependencies..."
        cd "$REPO_ROOT/react_app"

        if npm install; then
            success "npm install complete"
        else
            error "npm install failed — check network connection"
            sleep 2
            info "Retrying npm install..."
            if npm install; then
                success "npm install complete (retry)"
            else
                error "npm install failed after retry"
                return 1
            fi
        fi
    fi

    # Start Colima if needed
    if [[ "$MODE" == "docker"* ]]; then
        if ! colima status &>/dev/null; then
            info "Starting Colima (this may take 30-60 seconds)..."
            if colima start --cpu 4 --memory 4; then
                success "Colima started"
                sleep 5  # Give it time to fully initialize
            else
                error "Failed to start Colima"
                return 1
            fi
        fi

        # Verify Docker is accessible after Colima start
        if ! docker info &>/dev/null; then
            error "Docker still not accessible after starting Colima"
            return 1
        fi
        success "Docker accessible"
    fi

    success "Prerequisites ready"
    return 0
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Phase 3: Launch Services
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

wait_for_health() {
    local url=$1
    local max_wait=$2
    local service_name=$3

    info "Waiting for $service_name health check..."
    local elapsed=0

    while [[ $elapsed -lt $max_wait ]]; do
        if curl -sf "$url" &>/dev/null; then
            success "$service_name is healthy"
            return 0
        fi
        sleep 2
        elapsed=$((elapsed + 2))
        log_verbose "Health check attempt $((elapsed / 2))..."
    done

    error "$service_name health check timeout after ${max_wait}s"
    return 1
}

wait_for_port() {
    local port=$1
    local max_wait=$2
    local service_name=$3

    info "Waiting for $service_name on port $port..."
    local elapsed=0

    while [[ $elapsed -lt $max_wait ]]; do
        if nc -z localhost "$port" 2>/dev/null; then
            success "$service_name is listening on port $port"
            return 0
        fi
        sleep 2
        elapsed=$((elapsed + 2))
        log_verbose "Port check attempt $((elapsed / 2))..."
    done

    error "$service_name not available on port $port after ${max_wait}s"
    return 1
}

launch_fastapi_local() {
    section "Starting FastAPI (local mode)"

    cd "$REPO_ROOT"
    info "Launching uvicorn..."

    local start_time=$(date +%s)

    # Launch FastAPI in background, redirect output to log
    .venv/bin/uvicorn fastapi_app.main:app \
        --host 0.0.0.0 \
        --port "$FASTAPI_PORT" \
        --reload \
        >> "$LOG_FILE" 2>&1 &

    FASTAPI_PID=$!
    log_verbose "FastAPI PID: $FASTAPI_PID"

    # Check for early process death
    sleep 3
    if ! kill -0 "$FASTAPI_PID" 2>/dev/null; then
        error "FastAPI process died immediately after start"
        error "Last 20 lines of log:"
        tail -20 "$LOG_FILE" | while read line; do echo "${RED}  | ${NC}$line"; done
        return 1
    fi

    # Wait for health check
    if ! wait_for_health "http://127.0.0.1:$FASTAPI_PORT/health" "$HEALTH_CHECK_TIMEOUT_LOCAL" "FastAPI"; then
        error "FastAPI failed to start"
        if [[ -n "$FASTAPI_PID" ]] && kill -0 "$FASTAPI_PID" 2>/dev/null; then
            error "Last 20 lines from FastAPI log:"
            tail -20 "$LOG_FILE" | while read line; do
                echo "${RED}  | ${NC}$line"
            done
        else
            error "FastAPI process died. Check $LOG_FILE for details"
            tail -20 "$LOG_FILE" | while read line; do
                echo "${RED}  | ${NC}$line"
            done
        fi
        return 1
    fi

    local end_time=$(date +%s)
    local duration=$((end_time - start_time))

    success "FastAPI started in ${duration}s (PID $FASTAPI_PID)"
    return 0
}

launch_fastapi_docker() {
    section "Starting FastAPI (docker mode)"

    cd "$REPO_ROOT"

    local compose_file="docker-compose.yml"
    if [[ "$MODE" == "docker-dev" ]]; then
        compose_file="docker-compose.dev.yml"
    fi

    info "Building and starting Docker containers ($compose_file)..."
    local start_time=$(date +%s)

    if [[ $VERBOSE -eq 1 ]]; then
        docker compose -f "$compose_file" up --build -d
    else
        docker compose -f "$compose_file" up --build -d >> "$LOG_FILE" 2>&1
    fi

    # Wait for health check (longer timeout for Docker build)
    if ! wait_for_health "http://localhost:$FASTAPI_PORT/health" "$HEALTH_CHECK_TIMEOUT_DOCKER" "FastAPI (Docker)"; then
        error "FastAPI Docker container failed to start"
        error "Docker logs:"
        docker compose -f "$compose_file" logs --tail=30 | while read line; do
            echo "${RED}  | ${NC}$line"
        done
        return 1
    fi

    local end_time=$(date +%s)
    local duration=$((end_time - start_time))

    success "FastAPI Docker started in ${duration}s"
    return 0
}

launch_react() {
    section "Starting React"

    cd "$REPO_ROOT/react_app"
    info "Launching Vite dev server..."

    local start_time=$(date +%s)

    # Launch React in background
    npm run dev >> "$LOG_FILE" 2>&1 &
    REACT_PID=$!
    log_verbose "React PID: $REACT_PID"

    # Wait for port to be available
    if ! wait_for_port "$REACT_PORT" "$PORT_CHECK_TIMEOUT" "React"; then
        error "React failed to start"
        if [[ -n "$REACT_PID" ]] && kill -0 "$REACT_PID" 2>/dev/null; then
            error "Last 20 lines from React log:"
            tail -20 "$LOG_FILE" | grep -A 20 "npm run dev" | tail -20 | while read line; do
                echo "${RED}  | ${NC}$line"
            done
        else
            error "React process died. Check $LOG_FILE for details"
        fi
        return 1
    fi

    local end_time=$(date +%s)
    local duration=$((end_time - start_time))

    success "React started in ${duration}s (PID $REACT_PID)"
    return 0
}

launch_services() {
    section "Phase 3: Launching services"

    # Launch FastAPI
    if [[ $SKIP_FASTAPI -eq 0 ]]; then
        if [[ "$MODE" == "local" ]]; then
            launch_fastapi_local || return 1
        else
            launch_fastapi_docker || return 1
        fi
    fi

    # Launch React
    if [[ $SKIP_REACT -eq 0 ]]; then
        launch_react || return 1
    fi

    return 0
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Phase 4: Status Summary
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

show_status() {
    section "Phase 4: Status summary"

    log ""
    log "${BOLD}╔════════════════════════════════════════════════════════════════╗${NC}"
    log "${BOLD}║${NC}  ${GREEN}${BOLD}✓ Full Stack Running${NC}                                      ${BOLD}║${NC}"
    log "${BOLD}╠════════════════════════════════════════════════════════════════╣${NC}"

    if [[ $SKIP_FASTAPI -eq 0 ]]; then
        log "${BOLD}║${NC}  ${CYAN}FastAPI:${NC}  http://localhost:$FASTAPI_PORT/docs                ${BOLD}║${NC}"
        if [[ "$MODE" == "local" ]]; then
            log "${BOLD}║${NC}            ${DIM}PID: $FASTAPI_PID${NC}                                   ${BOLD}║${NC}"
        else
            log "${BOLD}║${NC}            ${DIM}Mode: Docker${NC}                                  ${BOLD}║${NC}"
        fi
    fi

    if [[ $SKIP_REACT -eq 0 ]]; then
        log "${BOLD}║${NC}  ${CYAN}React:${NC}    http://localhost:$REACT_PORT                       ${BOLD}║${NC}"
        log "${BOLD}║${NC}            ${DIM}PID: $REACT_PID${NC}                                   ${BOLD}║${NC}"
    fi

    log "${BOLD}╠════════════════════════════════════════════════════════════════╣${NC}"
    log "${BOLD}║${NC}  ${YELLOW}Mode:${NC}     $MODE                                           ${BOLD}║${NC}"
    log "${BOLD}║${NC}  ${YELLOW}Logs:${NC}     $LOG_FILE  ${BOLD}║${NC}"
    log "${BOLD}╠════════════════════════════════════════════════════════════════╣${NC}"
    log "${BOLD}║${NC}  ${DIM}Press Ctrl+C to stop all services${NC}                         ${BOLD}║${NC}"
    log "${BOLD}╚════════════════════════════════════════════════════════════════╝${NC}"
    log ""

    # Open browser if requested
    if [[ $OPEN_BROWSER -eq 1 ]] && [[ $SKIP_REACT -eq 0 ]]; then
        info "Opening browser..."
        if [[ "$OS_TYPE" == "Darwin" ]]; then
            open "http://localhost:$REACT_PORT" 2>/dev/null || true
        elif [[ "$OS_TYPE" == "Linux" ]]; then
            xdg-open "http://localhost:$REACT_PORT" 2>/dev/null || true
        fi
    fi
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Main
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

main() {
    # Initialize log
    echo "=== structural_engineering_lib Launch Log ===" > "$LOG_FILE"
    echo "Date: $(date)" >> "$LOG_FILE"
    echo "" >> "$LOG_FILE"

    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --local)
                MODE="local"
                shift
                ;;
            --docker)
                MODE="docker"
                shift
                ;;
            --docker-dev)
                MODE="docker-dev"
                shift
                ;;
            --kill-only)
                kill_existing_services
                success "Kill-only mode complete"
                exit 0
                ;;
            --check-only)
                run_preflight_checks
                exit $?
                ;;
            --no-react)
                SKIP_REACT=1
                shift
                ;;
            --no-fastapi)
                SKIP_FASTAPI=1
                shift
                ;;
            --open)
                OPEN_BROWSER=1
                shift
                ;;
            --verbose)
                VERBOSE=1
                shift
                ;;
            --help|-h)
                show_help
                exit 0
                ;;
            *)
                error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done

    # Validate combinations
    if [[ $SKIP_REACT -eq 1 ]] && [[ $SKIP_FASTAPI -eq 1 ]]; then
        error "Cannot skip both React and FastAPI"
        exit 1
    fi

    # Header
    log ""
    log "${BOLD}${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
    log "${BOLD}${BLUE}║${NC}  ${BOLD}structural_engineering_lib — Full Stack Launcher${NC}         ${BOLD}${BLUE}║${NC}"
    log "${BOLD}${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"

    # Phase 0: Kill existing services
    kill_existing_services

    # Phase 1: Pre-flight checks
    if ! run_preflight_checks; then
        error "Cannot proceed — fix errors above"
        exit 1
    fi

    # Phase 2: Fix prerequisites
    if ! fix_prerequisites; then
        error "Cannot proceed — fix errors above"
        exit 1
    fi

    # Phase 3: Launch services
    if ! launch_services; then
        error "Failed to launch services"
        exit 1
    fi

    # Phase 4: Status summary
    show_status

    # Keep script running (trap will handle cleanup)
    wait
}

# Run main
main "$@"
