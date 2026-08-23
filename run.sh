#!/usr/bin/env bash
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# run.sh — Unified CLI for structural_engineering_lib
#
# Single entry point for AI agents and developers. Dispatches to the right
# script so you never need to remember 78 individual script names.
#
# Usage:
#   ./run.sh <command> [subcommand] [options]
#   ./run.sh --help
#
# Commands:
#   check     Run validation checks (all, or by category)
#   session   Start/end agent sessions
#   find      Discover scripts and API signatures
#   release   Version bumps and release management
#   audit     Run readiness/governance audit
#   test      Run test suites
#   frontend  Run React commands with the Node version pinned by .nvmrc
#   generate  Generate SDKs, manifests, and scaffolds
#   context   Validate and query live repository context
#   route     Route tasks to the right agent
#   tools     Tool & script discovery
#   control   Canonical control-plane registry
#   pipeline  Pipeline state tracking
#   parity    Cross-layer implementation/test parity dashboard
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
set -euo pipefail

# Resolve repo root from this script's location
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPTS="$REPO_ROOT/scripts"
VENV="$SCRIPTS/python_runtime.sh"

# ── Colors ─────────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
DIM='\033[2m'
NC='\033[0m'

# ── Helpers ────────────────────────────────────────────────────────────────

_header() {
    echo -e "${BOLD}${CYAN}━━━ $1 ━━━${NC}"
}

_error() {
    echo -e "${RED}ERROR: $1${NC}" >&2
}

_hint() {
    echo -e "${DIM}$1${NC}"
}

_require_venv() {
    if [[ ! -x "$VENV" ]]; then
        _error "Python runtime launcher not found at $VENV"
        echo "  Run: python3 -m venv .venv && .venv/bin/pip install -e Python/"
        exit 1
    fi
}

_run_with_usage_event() {
    local label="$1"
    shift
    local started_epoch finished_epoch duration_sec status
    started_epoch=$(date +%s)
    set +e
    "$@"
    status=$?
    set -e
    finished_epoch=$(date +%s)
    duration_sec=$((finished_epoch - started_epoch))
    "$VENV" "$SCRIPTS/session.py" usage \
        --event "$label" --duration-sec "$duration_sec" --result-code "$status" \
        >/dev/null 2>&1 || true
    return "$status"
}

# ── Command: check ─────────────────────────────────────────────────────────

_cmd_check() {
    _require_venv
    "$VENV" "$SCRIPTS/check_all.py" "$@"
}

_help_check() {
    cat <<'EOF'
Usage: ./run.sh check [options]

Run validation checks across the codebase.

Options:
  (no args)            Run ALL checks (parallel by category)
  --quick              Fast subset: links, imports, hygiene (<30s)
  --changed            Run categories for whole-candidate impact domains
  --pre-commit         Run pre-commit hooks (black, ruff, mypy, bandit)
  --category <name>    Run one category: api|docs|arch|governance|fastapi|git|stale|code
  --fix                Auto-fix what's fixable (sync numbers, etc.)
  --json               Machine-readable JSON output
  --list               Show available categories and their scripts
  --no-reuse           Force fresh checks instead of exact PASS reuse

Categories:
  api          API contracts, manifest, endpoint validation
  docs         Links, doc versions, metadata, tasks format
  arch         Architecture boundaries, circular imports, import validation
  governance   Governance rules, repo hygiene, Python version, schemas
  fastapi      FastAPI issues, Docker config, OpenAPI snapshot
  git          Git state, unfinished merges, version consistency
  stale        Stale script refs, instruction drift, bootstrap freshness
  code         Type annotations

Examples:
  ./run.sh check                      # Run everything
  ./run.sh check --quick              # Fast validation
  ./run.sh check --category api       # API checks only
  ./run.sh check --category docs --fix  # Fix doc issues
  ./run.sh check --json               # CI-friendly output
EOF
}

# ── Command: session ───────────────────────────────────────────────────────

_cmd_session_begin() {
    _require_venv
    local agent="" task_id="" task="" model="unknown" reasoning="unknown"
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --agent) agent="${2:-}"; shift 2 ;;
            --task-id) task_id="${2:-}"; shift 2 ;;
            --task) task="${2:-}"; shift 2 ;;
            --model) model="${2:-}"; shift 2 ;;
            --reasoning) reasoning="${2:-}"; shift 2 ;;
            --help|-h)
                echo "Usage: ./run.sh session begin --task-id TASK --agent ROLE [--task TEXT] [--model NAME] [--reasoning LEVEL]"
                return 0
                ;;
            *) _error "Unknown session begin option: $1"; return 1 ;;
        esac
    done
    if [[ -z "$task_id" ]]; then
        _error "session begin requires --task-id"
        return 1
    fi

    local -a usage_args=(usage --checkpoint start --task-id "$task_id")
    [[ -n "$task" ]] && usage_args+=(--task "$task")
    usage_args+=(--model "$model" --reasoning "$reasoning")
    "$VENV" "$SCRIPTS/session.py" "${usage_args[@]}"

    local -a brief_args=()
    [[ -n "$agent" ]] && brief_args+=(--agent "$agent")
    local started_epoch finished_epoch duration_sec status
    started_epoch=$(date +%s)
    set +e
    bash "$SCRIPTS/agent_brief.sh" "${brief_args[@]}"
    status=$?
    if [[ "$status" -eq 0 ]]; then
        "$SCRIPTS/agent_start.sh" --quick --preflight-only
        status=$?
    fi
    set -e
    finished_epoch=$(date +%s)
    duration_sec=$((finished_epoch - started_epoch))
    "$VENV" "$SCRIPTS/session.py" usage \
        --event "orientation/session start" \
        --duration-sec "$duration_sec" --result-code "$status" >/dev/null
    return "$status"
}

_cmd_session() {
    local subcmd="${1:-}"
    shift 2>/dev/null || true

    case "$subcmd" in
        begin)
            _cmd_session_begin "$@"
            ;;
        start)
            "$SCRIPTS/agent_start.sh" --quick "$@"
            ;;
        end)
            _require_venv
            _run_with_usage_event "session end" "$VENV" "$SCRIPTS/session.py" end "$@"
            ;;
        handoff)
            _require_venv
            "$VENV" "$SCRIPTS/session.py" handoff "$@"
            ;;
        summary)
            _require_venv
            "$VENV" "$SCRIPTS/session.py" summary "$@"
            ;;
        sync)
            _require_venv
            "$VENV" "$SCRIPTS/session.py" sync "$@"
            ;;
        check)
            _require_venv
            "$VENV" "$SCRIPTS/session.py" check "$@"
            ;;
        context)
            _require_venv
            "$VENV" "$SCRIPTS/session.py" context "$@"
            ;;
        brief)
            bash "$SCRIPTS/agent_brief.sh" "$@"
            ;;
        costs|usage|compact|trust)
            _require_venv
            "$VENV" "$SCRIPTS/session.py" "$subcmd" "$@"
            ;;
        *)
            _help_session
            [[ -n "$subcmd" ]] && _error "Unknown session subcommand: $subcmd"
            exit 1
            ;;
    esac
}

_help_session() {
    cat <<'EOF'
Usage: ./run.sh session <subcommand>

Manage agent work sessions.

Subcommands:
  begin      Timed compact brief + environment start for one exact task
  start      Begin session (verify env, read priorities)
  end        Validate closeout; --fix updates handoff, --log-cost records a proxy
  handoff    Write a receipt-bound durable task handoff
  summary    Preview summary from git log; pass --write to update docs
  sync       Check stale doc numbers; pass --fix to update them
  check      Check session docs for issues
  context    Dump compact orientation context (tasks, brief, git status)
  brief      Fast 20-line agent brief (--agent <name> | --handoff)
  usage      Record/show model, reasoning, agent, and usage checkpoints
  costs      Show legacy Git-activity proxies (not billing or tokens)
  compact    Archive old SESSION_LOG entries
  trust      Show or reset session trust state

Examples:
  ./run.sh session begin --task-id TASK-XXX --agent governance
  ./run.sh session start      # Compatibility entry without automatic timing
  ./run.sh session context    # Quick orientation mid-session
  ./run.sh session usage --help
  ./run.sh session end        # Validate closeout without hidden writes
  ./run.sh session sync --fix # Explicitly fix stale numbers when required
EOF
}

# ── Command: find ──────────────────────────────────────────────────────────

_cmd_find() {
    _require_venv
    if [[ "${1:-}" == "--api" ]]; then
        shift
        if [[ $# -eq 0 ]]; then
            _error "Function name required"
            echo "  Usage: ./run.sh find --api <function_name>"
            exit 1
        fi
        "$VENV" "$SCRIPTS/discover_api_signatures.py" "$@"
    elif [[ "${1:-}" == "--list" ]]; then
        "$VENV" "$SCRIPTS/find_automation.py" --list
    elif [[ $# -eq 0 ]]; then
        _help_find
        exit 1
    else
        "$VENV" "$SCRIPTS/find_automation.py" "$@"
    fi
}

_help_find() {
    cat <<'EOF'
Usage: ./run.sh find <query> [options]

Discover scripts and API signatures.

Options:
  <query>          Fuzzy search for a script by task description
  --api <func>     Get exact parameter names for an API function
  --list           List all mapped automation tasks

Examples:
  ./run.sh find "check api"                # Find API validation scripts
  ./run.sh find --api design_beam_is456    # Get exact API signatures
  ./run.sh find --list                     # Show all mapped tasks
EOF
}

# ── Command: release ───────────────────────────────────────────────────────

_cmd_release() {
    _require_venv
    if [[ $# -eq 0 ]]; then
        _help_release
        exit 1
    fi
    "$VENV" "$SCRIPTS/release.py" "$@"
}

_help_release() {
    cat <<'EOF'
Usage: ./run.sh release <subcommand>

Version bumps and release management.

Subcommands:
  preflight [version]      Run pre-release validation checks
  run <version>            Bump version and update all files
  verify                   Verify installed package in clean venv
  check-docs               Check docs have correct version
  checklist                Print release checklist
  permission-check         Verify public-distribution permission record
  footing-inclusion-check  Verify complete footing D1 integration

Examples:
  ./run.sh release preflight 0.24.0a1  # Validate an Alpha publication candidate
  ./run.sh release run 0.24.0a1        # Bump to an Alpha publication candidate
  ./run.sh release verify --version 0.24.0a1  # Verify exact release artifact
  ./run.sh release check-docs        # Check version in docs
  ./run.sh release permission-check  # Check standing distribution permission
  ./run.sh release footing-inclusion-check  # Check footing release inclusion
EOF
}

# ── Command: audit ─────────────────────────────────────────────────────────

_cmd_audit() {
    _require_venv
    local subcmd="${1:-}"

    case "$subcmd" in
        --score)
            "$VENV" "$SCRIPTS/project_health.py" --score "${@:2}"
            ;;
        --errors)
            "$VENV" "$SCRIPTS/audit_error_handling.py" "${@:2}"
            ;;
        --inputs)
            "$VENV" "$SCRIPTS/audit_input_validation.py" "${@:2}"
            ;;
        --diagnostics)
            "$VENV" "$SCRIPTS/collect_diagnostics.py" "${@:2}"
            ;;
        ""|--help)
            if [[ "$subcmd" == "--help" ]]; then
                _help_audit
                exit 0
            fi
            "$VENV" "$SCRIPTS/audit_readiness_report.py" "${@:1}"
            ;;
        *)
            # Pass everything to audit_readiness_report.py
            "$VENV" "$SCRIPTS/audit_readiness_report.py" "$@"
            ;;
    esac
}

_help_audit() {
    cat <<'EOF'
Usage: ./run.sh audit [options]

Run readiness and governance audits.

Options:
  (no args)          Full readiness audit (current evidence set)
  --score            Project health score (alias for health --score)
  --errors           Error handling coverage audit
  --inputs           Input validation coverage audit
  --diagnostics      System diagnostics bundle

Examples:
  ./run.sh audit                    # Full readiness report
  ./run.sh audit --score            # Quick project health score
  ./run.sh audit --diagnostics      # System info bundle
EOF
}

# ── Command: test ──────────────────────────────────────────────────────────

_cmd_test() {
    local subcmd="${1:-}"

    case "$subcmd" in
        --parity)
            _require_venv
            "$VENV" "$SCRIPTS/test_api_parity.py" "${@:2}"
            ;;
        --pipeline)
            _require_venv
            "$VENV" "$SCRIPTS/test_import_pipeline.py" "${@:2}"
            ;;
        --cli)
            _require_venv
            "$VENV" "$SCRIPTS/external_cli_test.py" "${@:2}"
            ;;
        --benchmark)
            _require_venv
            "$VENV" "$SCRIPTS/benchmark_api.py" "${@:2}"
            ;;
        --ci)
            "$SCRIPTS/ci_local.sh"
            ;;
        --changed)
            _require_venv
            "$VENV" "$SCRIPTS/test_changed.py" "${@:2}"
            ;;
        --stats)
            _require_venv
            "$VENV" "$SCRIPTS/update_test_stats.py" "${@:2}"
            ;;
        --python)
            _require_venv
            (
                cd "$REPO_ROOT/Python"
                "$VENV" -m pytest tests/ "${@:2}"
            )
            ;;
        --fastapi)
            _require_venv
            "$VENV" -m pytest "$REPO_ROOT/fastapi_app/tests" "${@:2}"
            ;;
        --react)
            _cmd_frontend test "${@:2}"
            ;;
        --all)
            _require_venv
            (
                cd "$REPO_ROOT/Python"
                "$VENV" -m pytest tests/
            )
            "$VENV" -m pytest "$REPO_ROOT/fastapi_app/tests"
            _cmd_frontend test
            ;;
        --help)
            _help_test
            exit 0
            ;;
        "")
            # Backward-compatible default: run the Python package suite.
            _require_venv
            (
                cd "$REPO_ROOT/Python"
                "$VENV" -m pytest tests/ -v "$@"
            )
            ;;
        *)
            # Pass all args to pytest
            _require_venv
            (
                cd "$REPO_ROOT/Python"
                "$VENV" -m pytest tests/ "$@"
            )
            ;;
    esac
}

_help_test() {
    cat <<'EOF'
Usage: ./run.sh test [options]

Run test suites.

Options:
  (no args)          Run the Python package suite (backward-compatible default)
  --python           Run the Python package suite explicitly
  --fastapi          Run the complete FastAPI suite
  --react            Run the complete React/Vitest suite with pinned Node
  --all              Run Python, FastAPI, and React test suites
  --parity           FastAPI ↔ library parity tests
  --pipeline         Import → Design → 3D integration test
  --cli              CLI cold-start smoke test
  --benchmark        API endpoint benchmarks
  --ci               Full local CI (black, ruff, mypy, pytest, coverage)
  --changed          Run tests only for changed files (smart mapping)
  --stats            Update test_stats.json with current counts

Any other args are passed directly to pytest:
  ./run.sh test -k "test_flexure" -v
  ./run.sh test --tb=short -x

Examples:
  ./run.sh test                     # Run Python package tests
  ./run.sh test --fastapi           # Run FastAPI tests
  ./run.sh test --react             # Run React tests with pinned Node
  ./run.sh test --all               # Run all three product test suites
  ./run.sh test --parity            # API parity check
  ./run.sh test -k "shear" -v      # Run shear tests, verbose
  ./run.sh test --ci                # Full CI locally
EOF
}

# ── Command: frontend ──────────────────────────────────────────────────────

_frontend_node() {
    _require_venv
    "$VENV" "$SCRIPTS/node_runtime.py" -- "$@"
}

_frontend_require_dependencies() {
    local tool
    for tool in eslint tsc vite vitest; do
        if [[ ! -e "$REPO_ROOT/react_app/node_modules/.bin/$tool" ]]; then
            _error "React dependencies are not ready in this worktree (missing $tool)."
            echo "  Run: ./scripts/python_runtime.sh scripts/node_runtime.py -- npm --prefix react_app ci"
            return 1
        fi
    done
}

_cmd_frontend() {
    local subcmd="${1:-check}"
    shift 2>/dev/null || true

    case "$subcmd" in
        runtime)
            _require_venv
            "$VENV" "$SCRIPTS/node_runtime.py" --print
            ;;
        lint)
            _frontend_require_dependencies
            _frontend_node npm --prefix react_app run lint "$@"
            ;;
        test)
            _frontend_require_dependencies
            if [[ "$#" -gt 0 ]]; then
                _frontend_node npm --prefix react_app test -- "$@"
            else
                _frontend_node npm --prefix react_app test
            fi
            ;;
        build)
            _frontend_require_dependencies
            _frontend_node npm --prefix react_app run build "$@"
            ;;
        check)
            _frontend_require_dependencies
            _frontend_node npm --prefix react_app run lint
            _frontend_node npm --prefix react_app test
            _frontend_node npm --prefix react_app run build
            ;;
        dev)
            _frontend_require_dependencies
            _frontend_node npm --prefix react_app run dev "$@"
            ;;
        --help|-h|help)
            _help_frontend
            ;;
        *)
            _error "Unknown frontend command: $subcmd"
            _help_frontend
            return 1
            ;;
    esac
}

_help_frontend() {
    cat <<'EOF'
Usage: ./run.sh frontend [runtime|lint|test|build|check|dev] [options]

Run React commands with the healthy Node.js major pinned by .nvmrc. The
selector supports Homebrew, an already-selected runtime, and nvm installs; it
does not assume that nvm itself is installed.

Each linked worktree needs its own lockfile-pinned dependencies. If readiness
fails, run:
  ./scripts/python_runtime.sh scripts/node_runtime.py -- npm --prefix react_app ci

Commands:
  runtime            Print the selected Node/npm versions and binary directory
  lint               Run ESLint
  test               Run Vitest; remaining arguments are passed to Vitest
  build              Run TypeScript and the production Vite build
  check              Run lint, tests, and build in order (default)
  dev                Start the Vite development server

Examples:
  ./run.sh frontend runtime
  ./run.sh frontend test useBatchDesign
  ./run.sh frontend check
EOF
}

# ── Command: generate ──────────────────────────────────────────────────────

_cmd_generate() {
    _require_venv
    local subcmd="${1:-}"
    shift 2>/dev/null || true

    case "$subcmd" in
        sdk)
            "$VENV" "$SCRIPTS/generate_client_sdks.py" "$@"
            ;;
        manifest)
            "$VENV" "$SCRIPTS/generate_api_manifest.py" "$@"
            ;;
        scaffold)
            if [[ $# -eq 0 ]]; then
                _error "Module name required"
                echo "  Usage: ./run.sh generate scaffold <module>"
                exit 1
            fi
            "$VENV" "$SCRIPTS/create_test_scaffold.py" "$@"
            ;;
        *)
            _help_generate
            [[ -n "$subcmd" ]] && _error "Unknown generate subcommand: $subcmd"
            exit 1
            ;;
    esac
}

_help_generate() {
    cat <<'EOF'
Usage: ./run.sh generate <subcommand> [args]

Generate SDKs, manifests, and scaffolds.

Subcommands:
  sdk                  Generate TypeScript/Python client SDKs
  manifest             Generate/validate api-manifest.json
  scaffold <module>    Generate pytest test template for a module

Examples:
  ./run.sh generate sdk                         # Generate client SDKs
  ./run.sh generate scaffold structural_lib.core  # Test template
EOF
}

# ── Self-Evolving System ───────────────────────────────────────────────────

_cmd_health() {
    _require_venv
    _header "Project Health"
    "$VENV" "$SCRIPTS/project_health.py" "$@"
}

_help_health() {
    cat <<'EOF'
Usage: ./run.sh health [options]

Unified project health scanner (docs, code, agents, infra, feedback).

Options:
  --fix              Auto-fix fixable issues
  --score            Print health score only (0-100)
  --quick            Quick scan (docs numbers + links only)
  --category <name>  Scan specific category (docs|code|agents|infra|feedback)
  --json             Machine-readable JSON output

Examples:
  ./run.sh health                     # Full scan
  ./run.sh health --fix               # Auto-fix everything fixable
  ./run.sh health --score             # Just the score
  ./run.sh health --category agents   # Scan agent instructions only
EOF
}

_cmd_feedback() {
    _require_venv
    "$VENV" "$SCRIPTS/agent_feedback.py" "$@"
}

_help_feedback() {
    cat <<'EOF'
Usage: ./run.sh feedback <subcommand> [options]

Agent feedback collection and analysis.

Subcommands:
  log                Log feedback from current session
  summary            Show feedback trends and recurring issues
  pending            List unresolved items
  resolve <id>       Mark a feedback item as resolved
  stats              Aggregate statistics

Examples:
  ./run.sh feedback log --agent backend --stale-doc "api.md wrong params"
  ./run.sh feedback log --agent frontend --missing "No hook docs"
  ./run.sh feedback summary
  ./run.sh feedback pending --brief
  ./run.sh feedback resolve abc123
EOF
}

_cmd_evolve() {
    _require_venv
    _header "Self-Evolution"
    "$VENV" "$SCRIPTS/evolve.py" "$@"
}

_help_evolve() {
    cat <<'EOF'
Usage: ./run.sh evolve [options]

Self-evolution engine — scans, fixes, and evolves the project.

Options:
  --fix                Apply auto-fixes for Codex review
  --review weekly      Quick weekly review (numbers, links, feedback)
  --review monthly     Full monthly review (all checks + archive)
  --status             Show last evolution run + recommendations
  --report             Generate report without fixes
  --json               JSON output

Examples:
  ./run.sh evolve                       # Full dry-run scan
  ./run.sh evolve --fix                  # Apply fixes for Codex review
  ./run.sh evolve --review weekly        # Weekly report-only review
  ./run.sh evolve --status               # When was last run?
EOF
}

# ── Command: dev ───────────────────────────────────────────────────────────

_cmd_dev() {
    _header "Development Stack"
    bash "$SCRIPTS/launch_stack.sh" "$@"
}

_help_dev() {
    cat <<'EOF'
Usage: ./run.sh dev [options]

Launch the full development stack (FastAPI + React). Kills existing services,
runs pre-flight checks, fixes prerequisites, and launches everything.

Modes:
  --local          Local mode: uvicorn + npm run dev (default)
  --docker         Docker mode: docker compose up
  --docker-dev     Docker dev mode: docker compose -f docker-compose.dev.yml up

Options:
  --kill-only      Kill existing services and exit
  --check-only     Run pre-flight checks only
  --no-react       Skip React frontend
  --no-fastapi     Skip FastAPI backend
  --open           Open browser after launch
  --verbose        Show detailed output

Examples:
  ./run.sh dev                        # Launch full stack (local mode)
  ./run.sh dev --docker               # Launch with Docker
  ./run.sh dev --kill-only            # Stop all services
EOF
}

# ── Command: route ─────────────────────────────────────────────────────────

_cmd_route() {
    _require_venv
    local query="${*:-}"
    if [[ -z "$query" ]]; then
        _error "Usage: ./run.sh route \"your task description\""
        echo "  Routes natural language to the right agent + skills"
        echo ""
        echo "  Examples:"
        echo "    ./run.sh route \"design beam 300x500\""
        echo "    ./run.sh route \"fix csv import bug\""
        echo "    ./run.sh route \"security audit\""
        exit 1
    fi
    "$VENV" "$SCRIPTS/prompt_router.py" "$query"
}

# ── Command: tools ─────────────────────────────────────────────────────────

_cmd_task() {
    _require_venv
    case "${1:-}" in
        brief)
            shift
            if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
                _help_task
                return
            fi
            if [[ $# -eq 0 ]]; then
                _error "Task description required"
                _help_task
                exit 1
            fi
            "$VENV" "$SCRIPTS/prompt_router.py" --brief "$@"
            ;;
        *)
            _help_task
            [[ -n "${1:-}" ]] && _error "Unknown task subcommand: $1"
            exit 1
            ;;
    esac
}

_help_task() {
    cat <<'EOF'
Usage: ./run.sh task brief <description> [--json]

Build a read-only task intake brief from live worktree state, role routing, and
the automation registry. Git lifecycle actions remain Codex-native.
EOF
}

_cmd_tools() {
    _require_venv
    case "${1:-}" in
        --list|list)    "$VENV" "$SCRIPTS/tool_registry.py" --list ;;
        --find|find)    shift; "$VENV" "$SCRIPTS/tool_registry.py" --find "$*" ;;
        --agent|agent)  shift; "$VENV" "$SCRIPTS/tool_registry.py" --agent "$1" ;;
        --stats|stats)  "$VENV" "$SCRIPTS/tool_registry.py" --stats ;;
        --permission)   shift; "$VENV" "$SCRIPTS/tool_registry.py" --permission "$1" ;;
        *)
            echo -e "${BOLD}./run.sh tools${NC} — Tool & script discovery"
            echo ""
            echo "  Subcommands:"
            echo "    --list                List all tools/scripts"
            echo "    --find \"query\"        Search tools by keyword"
            echo "    --agent <name>        Show tools for specific agent"
            echo "    --stats               Tool registry statistics"
            echo "    --permission <level>  Filter by permission level"
            echo ""
            echo "  Examples:"
            echo "    ./run.sh tools --agent backend"
            echo "    ./run.sh tools --find \"beam design\""
            echo "    ./run.sh tools --permission ReadOnly"
            ;;
    esac
}

# ── Command: control ───────────────────────────────────────────────────────

_cmd_control() {
    _require_venv
    "$VENV" "$SCRIPTS/control_plane/cli.py" "$@"
}

# ── Command: context ───────────────────────────────────────────────────────

_cmd_context() {
    _require_venv
    "$VENV" "$SCRIPTS/repo_context.py" "$@"
}

# ── Command: verification ─────────────────────────────────────────────────

_cmd_verification() {
    _require_venv
    "$VENV" "$SCRIPTS/verification.py" "$@"
}

# ── Command: pipeline ──────────────────────────────────────────────────────

_cmd_pipeline() {
    _require_venv
    case "${1:-}" in
        new)     shift; "$VENV" "$SCRIPTS/pipeline_state.py" new "$@" ;;
        advance) shift; "$VENV" "$SCRIPTS/pipeline_state.py" advance "$@" ;;
        fail)    shift; "$VENV" "$SCRIPTS/pipeline_state.py" fail "$@" ;;
        show)    shift; "$VENV" "$SCRIPTS/pipeline_state.py" show "$@" ;;
        list)    shift; "$VENV" "$SCRIPTS/pipeline_state.py" list "$@" ;;
        resume)  shift; "$VENV" "$SCRIPTS/pipeline_state.py" resume "$@" ;;
        *)
            echo -e "${BOLD}./run.sh pipeline${NC} — Pipeline state tracking"
            echo ""
            echo "  Subcommands:"
            echo "    new      Create a new pipeline"
            echo "    advance  Complete current step"
            echo "    fail     Mark step as failed"
            echo "    show     Show pipeline details"
            echo "    list     List all pipelines"
            echo "    resume   Generate resume context"
            echo ""
            echo "  Examples:"
            echo "    ./run.sh pipeline new --task TASK-857 --agent backend"
            echo "    ./run.sh pipeline advance TASK-857-pipeline --notes \"done\""
            echo "    ./run.sh pipeline list --status running"
            ;;
    esac
}

# ── Command: coverage ──────────────────────────────────────────────────────

_cmd_coverage() {
    _require_venv
    "$VENV" "$SCRIPTS/check_clause_coverage.py" "$@"
}

_cmd_parity() {
    _require_venv
    "$VENV" "$SCRIPTS/parity_dashboard.py" "$@"
}

_help_parity() {
    cat <<'EOF'
Usage: ./run.sh parity [--json] [--missing] [--section <name>]

Show declared supported/held Indian-code capability families, public API
exposure, FastAPI endpoint tests, and frontend API hooks. Capability percentages
are planning indicators, not clause completeness or engineering approval.
EOF
}

# ── Command: efficiency ───────────────────────────────────────────────────

_cmd_efficiency() {
    _require_venv
    local subcmd="${1:-check}"
    case "$subcmd" in
        check)
            shift || true
            "$VENV" "$SCRIPTS/check_token_efficiency.py" "$@"
            ;;
        prompt)
            "$VENV" "$SCRIPTS/check_token_efficiency.py" --prompt
            ;;
        *)
            _error "Unknown efficiency subcommand: $subcmd"
            _help_efficiency
            return 1
            ;;
    esac
}

_help_efficiency() {
    cat <<'EOF'
Usage: ./run.sh efficiency [check|prompt] [--json]

Validate project-side low-token controls or print the reusable task preamble.
Provider usage is available through Codex /status and Settings > Usage.
EOF
}

# ── Command: model ────────────────────────────────────────────────────────

_cmd_model() {
    _require_venv
    "$VENV" "$SCRIPTS/model_picker.py" "$@"
}

_help_model() {
    cat <<'EOF'
Usage: ./run.sh model <task description> [options]
       ./run.sh model --table

Recommend a GPT-5.6 model and reasoning profile from the checked-in policy.
The command advises only; apply the result with /model in Codex desktop.

Options:
  --risk auto|low|normal|high|critical
  --repeatable
  --ambiguous
  --important
  --orchestrator
  --json
EOF
}

# ── Main Dispatch ──────────────────────────────────────────────────────────

_print_usage() {
    echo -e "${BOLD}${CYAN}━━━ run.sh — Unified CLI for structural_engineering_lib ━━━${NC}"
    echo ""
    echo -e "${BOLD}Usage:${NC} ./run.sh <command> [subcommand] [options]"
    echo ""
    echo -e "${BOLD}Commands:${NC}"
    echo -e "  ${GREEN}check${NC}       Run validation checks (all, or by category)"
    echo -e "  ${GREEN}session${NC}     Start/end agent sessions"
    echo -e "  ${GREEN}find${NC}        Discover scripts and API signatures"
    echo -e "  ${GREEN}release${NC}     Version bumps and release management"
    echo -e "  ${GREEN}audit${NC}       Run readiness/governance audit"
    echo -e "  ${GREEN}test${NC}        Run test suites"
    echo -e "  ${GREEN}frontend${NC}    Run React checks with the pinned Node runtime"
    echo -e "  ${GREEN}generate${NC}    Generate SDKs, manifests, and scaffolds"
    echo -e "  ${GREEN}context${NC}     Validate/query live context without generated indexes"
    echo -e "  ${GREEN}verification${NC} Plan change domains and inspect exact PASS evidence"
    echo -e "  ${GREEN}health${NC}      Project health scan (unified checker)"
    echo -e "  ${GREEN}feedback${NC}    Agent feedback collection & analysis"
    echo -e "  ${GREEN}dev${NC}         Launch full development stack (FastAPI + React)"
    echo -e "  ${GREEN}evolve${NC}      Self-evolution engine (scan + fix + report)"
    echo -e "  ${GREEN}preflight${NC}   Pre-flight safety check (branch, venv, ports)"
    echo -e "  ${GREEN}route${NC}       Route natural language to the right agent"
    echo -e "  ${GREEN}task${NC}        Build a lane-safe task intake brief"
    echo -e "  ${GREEN}tools${NC}       Tool & script discovery (list, find,stats)"
    echo -e "  ${GREEN}control${NC}     Validate and query the canonical operation registry"
    echo -e "  ${GREEN}pipeline${NC}    Pipeline state tracking (new, advance, show)"
    echo -e "  ${GREEN}coverage${NC}    Namespaced decorator registration report"
    echo -e "  ${GREEN}parity${NC}      Declared capability and cross-layer parity dashboard"
    echo -e "  ${GREEN}efficiency${NC}  Validate low-token agent and context controls"
    echo -e "  ${GREEN}model${NC}       Recommend a model and reasoning level for a task"
    echo -e "  ${GREEN}diagnose${NC}    Diagnose CI failures (--pr N, --local, --fix)"
    echo ""
    echo -e "${BOLD}Quick Start:${NC}"
    echo -e "  ${DIM}./run.sh session start${NC}              # Begin work"
    echo -e "  ${DIM}./run.sh check --quick${NC}              # Fast validation"
    echo -e "  ${DIM}Codex Git/GitHub${NC}                         # Commit, push, and open PR"
    echo -e "  ${DIM}./run.sh session end${NC}                # Wrap up"
    echo ""
    echo -e "${DIM}Run ./run.sh <command> --help for detailed usage.${NC}"
}

# Handle --help for any command
_dispatch_help() {
    local cmd="$1"
    case "$cmd" in
        check)    _help_check ;;
        session)  _help_session ;;
        find)     _help_find ;;
        release)  _help_release ;;
        audit)    _help_audit ;;
        test)     _help_test ;;
        frontend) _help_frontend ;;
        generate) _help_generate ;;
        context)  _cmd_context --help ;;
        verification) _cmd_verification --help ;;
        health)   _help_health ;;
        feedback) _help_feedback ;;
        evolve)   _help_evolve ;;
        dev)      _help_dev ;;
        route)    _cmd_route ;;
        task)     _help_task ;;
        tools)    _cmd_tools ;;
        control)  _cmd_control --help ;;
        pipeline) _cmd_pipeline ;;
        coverage) _cmd_coverage ;;
        parity)   _help_parity ;;
        efficiency) _help_efficiency ;;
        model)      _help_model ;;
        *)        _print_usage ;;
    esac
}

# ── Shell completion ────────────────────────────────────────────────────────

# Source this to enable tab completion: eval "$(./run.sh --completions)"
_run_sh_completions() {
    if [[ "${1:-}" == "--completions" ]]; then
        cat <<'COMP'
# Zsh completion for ./run.sh
_run_sh() {
    local -a commands=(
        'check:Run validation checks'
        'session:Manage agent sessions'
        'find:Discover scripts and API'
        'release:Version bumps'
        'audit:Readiness audit'
        'test:Run test suites'
        'frontend:Run React commands with pinned Node'
        'generate:Generate SDKs and manifests'
        'context:Query live repository context'
        'verification:Plan change domains and exact PASS evidence'
        'health:Project health scan'
        'feedback:Agent feedback collection'
        'evolve:Self-evolution engine'
        'route:Route tasks to the right agent'
        'task:Build a lane-safe task intake brief'
        'tools:Tool and script discovery'
        'control:Canonical operation registry'
        'pipeline:Pipeline state tracking'
        'parity:Cross-layer parity dashboard'
        'efficiency:Validate low-token controls'
        'model:Recommend model and reasoning profile'
    )
    local -a check_opts=('--quick' '--changed' '--pre-commit' '--category' '--fix' '--json' '--list' '--serial' '--no-reuse')
    local -a categories=('api' 'docs' 'arch' 'governance' 'fastapi' 'git' 'stale' 'code')
    local -a session_subs=('start' 'end' 'handoff' 'summary' 'sync' 'check' 'context' 'brief' 'usage' 'costs' 'compact' 'trust')
    local -a task_subs=('brief')
    local -a generate_subs=('indexes' 'sdk' 'manifest' 'docs-index' 'scaffold')
    local -a health_opts=('--fix' '--score' '--quick' '--category' '--json')
    local -a feedback_subs=('log' 'summary' 'pending' 'resolve' 'stats')
    local -a evolve_opts=('--fix' '--review' '--status' '--report' '--json')
    local -a test_opts=('--python' '--fastapi' '--react' '--all' '--parity' '--pipeline' '--cli' '--benchmark' '--ci' '--stats')
    local -a frontend_subs=('runtime' 'lint' 'test' 'build' 'check' 'dev')
    local -a audit_opts=('--score' '--errors' '--inputs' '--diagnostics')
    local -a release_subs=('preflight' 'run' 'verify' 'check-docs' 'checklist' 'permission-check' 'footing-inclusion-check')
    local -a efficiency_subs=('check' 'prompt')
    local -a control_subs=('validate' 'find' 'list' 'stats' 'export-legacy')
    local -a context_subs=('validate' 'list' 'show' 'summary')
    local -a verification_subs=('validate' 'plan' 'fingerprint' 'probe' 'record')

    if (( CURRENT == 2 )); then
        _describe 'command' commands
    elif (( CURRENT == 3 )); then
        case "${words[2]}" in
            check) _values 'option' $check_opts ;;
            session) _values 'subcommand' $session_subs ;;
            task) _values 'subcommand' $task_subs ;;
            generate) _values 'subcommand' $generate_subs ;;
            health) _values 'option' $health_opts ;;
            feedback) _values 'subcommand' $feedback_subs ;;
            evolve) _values 'option' $evolve_opts ;;
            test) _values 'option' $test_opts ;;
            frontend) _values 'subcommand' $frontend_subs ;;
            audit) _values 'option' $audit_opts ;;
            release) _values 'subcommand' $release_subs ;;
            efficiency) _values 'subcommand' $efficiency_subs ;;
            control) _values 'subcommand' $control_subs ;;
            context) _values 'subcommand' $context_subs ;;
            verification) _values 'subcommand' $verification_subs ;;
        esac
    elif (( CURRENT == 4 )); then
        case "${words[2]}" in
            check)
                if [[ "${words[3]}" == "--category" ]]; then
                    _values 'category' $categories
                fi
                ;;
        esac
    fi
}
compdef _run_sh ./run.sh
compdef _run_sh run.sh
COMP
        exit 0
    fi
}

# Main entry point
main() {
    # Handle --completions before anything else
    if [[ "${1:-}" == "--completions" ]]; then
        _run_sh_completions "$@"
    fi

    local cmd="${1:-}"

    # No command → show usage
    if [[ -z "$cmd" ]]; then
        _print_usage
        exit 0
    fi

    # Global --help
    if [[ "$cmd" == "--help" || "$cmd" == "-h" || "$cmd" == "help" ]]; then
        _print_usage
        exit 0
    fi

    shift

    # Check for --help as second arg
    if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
        _dispatch_help "$cmd"
        exit 0
    fi

    # Dispatch
    case "$cmd" in
        check)    _cmd_check "$@" ;;
        session)  _cmd_session "$@" ;;
        find)     _cmd_find "$@" ;;
        release)  _cmd_release "$@" ;;
        audit)    _cmd_audit "$@" ;;
        test)     _cmd_test "$@" ;;
        frontend) _cmd_frontend "$@" ;;
        generate) _cmd_generate "$@" ;;
        context)  _cmd_context "$@" ;;
        verification) _cmd_verification "$@" ;;
        health)   _cmd_health "$@" ;;
        feedback) _cmd_feedback "$@" ;;
        evolve)   _cmd_evolve "$@" ;;
        dev)      _cmd_dev "$@" ;;
        preflight) _require_venv; "$VENV" "$SCRIPTS/preflight.py" "$@" ;;
        route)    _cmd_route "$@" ;;
        task)     _cmd_task "$@" ;;
        tools)    _cmd_tools "$@" ;;
        control)  _cmd_control "$@" ;;
        coverage) _cmd_coverage "$@" ;;
        parity)    _cmd_parity "$@" ;;
        diagnose) _require_venv; "$VENV" "$SCRIPTS/diagnose_ci.py" "$@" ;;
        pipeline) _cmd_pipeline "$@" ;;
        efficiency) _cmd_efficiency "$@" ;;
        model)      _cmd_model "$@" ;;
        *)
            _error "Unknown command: $cmd"
            echo ""
            _print_usage
            exit 1
            ;;
    esac
}

main "$@"
