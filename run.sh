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
#   commit    Stage, commit, and push safely
#   pr        Create/finish pull requests
#   session   Start/end agent sessions
#   find      Discover scripts and API signatures
#   release   Version bumps and release management
#   audit     Run readiness/governance audit
#   test      Run test suites
#   generate  Generate indexes, SDKs, manifests
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
set -euo pipefail

# Resolve repo root from this script's location
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="$REPO_ROOT/.venv/bin/python"
SCRIPTS="$REPO_ROOT/scripts"

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
        _error "Python venv not found at $VENV"
        echo "  Run: python3 -m venv .venv && .venv/bin/pip install -e Python/"
        exit 1
    fi
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
  --changed            Only run categories for recently changed files
  --pre-commit         Run pre-commit hooks (black, ruff, mypy, isort)
  --category <name>    Run one category: api|docs|arch|governance|fastapi|git|stale|code
  --fix                Auto-fix what's fixable (sync numbers, etc.)
  --json               Machine-readable JSON output
  --list               Show available categories and their scripts

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

# ── Command: commit ────────────────────────────────────────────────────────

_cmd_commit() {
    if [[ $# -eq 0 ]]; then
        _error "Commit message required"
        echo "  Usage: ./run.sh commit \"type: message\""
        echo "  Example: ./run.sh commit \"feat: add beam optimization\""
        exit 1
    fi
    "$SCRIPTS/ai_commit.sh" "$@"
}

_help_commit() {
    cat <<'EOF'
Usage: ./run.sh commit "type: message" [options]

Stage, commit, and push safely. Delegates to ai_commit.sh.

Options:
  --force       Skip PR requirement check
  --dry-run     Preview what would be committed
  --amend       Amend the last commit
  --push        Push-only (no new commit)

Commit types: feat|fix|docs|refactor|test|chore|ci(scope): description

Examples:
  ./run.sh commit "feat: add beam optimization"
  ./run.sh commit "fix: stirrup spacing" --force
  ./run.sh commit "docs: update API reference" --dry-run
EOF
}

# ── Command: pr ────────────────────────────────────────────────────────────

_cmd_pr() {
    local subcmd="${1:-}"
    shift 2>/dev/null || true

    case "$subcmd" in
        create)
            if [[ $# -lt 2 ]]; then
                _error "Usage: ./run.sh pr create TASK-XXX \"description\""
                exit 1
            fi
            "$SCRIPTS/create_task_pr.sh" "$@"
            ;;
        finish)
            "$SCRIPTS/finish_task_pr.sh" "$@"
            ;;
        status)
            if command -v gh &>/dev/null; then
                gh pr view --web 2>/dev/null || gh pr list
            else
                _error "GitHub CLI (gh) not installed"
                echo "  Install: brew install gh"
                exit 1
            fi
            ;;
        *)
            _help_pr
            [[ -n "$subcmd" ]] && _error "Unknown pr subcommand: $subcmd"
            exit 1
            ;;
    esac
}

_help_pr() {
    cat <<'EOF'
Usage: ./run.sh pr <subcommand> [args]

Manage pull requests.

Subcommands:
  create TASK-XXX "description"    Create a task PR branch
  finish [args]                    Push, create/merge PR
  status                           View current PR status

Examples:
  ./run.sh pr create TASK-501 "Add shear wall support"
  ./run.sh pr finish
  ./run.sh pr status
EOF
}

# ── Command: session ───────────────────────────────────────────────────────

_cmd_session() {
    local subcmd="${1:-}"
    shift 2>/dev/null || true

    case "$subcmd" in
        start)
            "$SCRIPTS/agent_start.sh" --quick "$@"
            ;;
        end)
            _require_venv
            "$VENV" "$SCRIPTS/session.py" end --fix "$@"
            ;;
        summary)
            _require_venv
            "$VENV" "$SCRIPTS/session.py" summary --write "$@"
            ;;
        sync)
            _require_venv
            "$VENV" "$SCRIPTS/session.py" sync --fix "$@"
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
  start      Begin session (verify env, read priorities)
  end        End session (log, sync, handoff)
  summary    Generate session summary from git log
  sync       Sync stale doc numbers
  check      Check session docs for issues
  context    Dump compact orientation context (tasks, brief, git status)
  brief      Fast 20-line agent brief (--agent <name> | --handoff)

Examples:
  ./run.sh session start      # First thing every session
  ./run.sh session context    # Quick orientation mid-session
  ./run.sh session end        # Last thing every session
  ./run.sh session sync       # Fix stale numbers mid-session
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
  ./run.sh find "commit code"              # Find commit-related scripts
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
  run patch|minor|major    Bump version and update all files
  verify                   Verify installed package in clean venv
  check-docs               Check docs have correct version
  checklist                Print release checklist

Examples:
  ./run.sh release run patch        # Bump patch version
  ./run.sh release verify           # Verify release
  ./run.sh release check-docs       # Check version in docs
EOF
}

# ── Command: audit ─────────────────────────────────────────────────────────

_cmd_audit() {
    _require_venv
    local subcmd="${1:-}"

    case "$subcmd" in
        --score)
            "$VENV" "$SCRIPTS/governance_health_score.py" "${@:2}"
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
  (no args)          Full readiness audit (25 checks)
  --score            Governance health score (weighted)
  --errors           Error handling coverage audit
  --inputs           Input validation coverage audit
  --diagnostics      System diagnostics bundle

Examples:
  ./run.sh audit                    # Full readiness report
  ./run.sh audit --score            # Quick governance score
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
            "$VENV" "$SCRIPTS/test_import_3d_pipeline.py" "${@:2}"
            ;;
        --vba)
            _require_venv
            "$VENV" "$SCRIPTS/run_vba_smoke_tests.py" "${@:2}"
            "$VENV" "$SCRIPTS/test_vba_adapter.py" "${@:2}"
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
        --help)
            _help_test
            exit 0
            ;;
        "")
            # Default: run pytest
            _require_venv
            cd "$REPO_ROOT/Python"
            "$VENV" -m pytest tests/ -v "$@"
            ;;
        *)
            # Pass all args to pytest
            _require_venv
            cd "$REPO_ROOT/Python"
            "$VENV" -m pytest tests/ "$@"
            ;;
    esac
}

_help_test() {
    cat <<'EOF'
Usage: ./run.sh test [options]

Run test suites.

Options:
  (no args)          Run full pytest suite (default)
  --parity           FastAPI ↔ library parity tests
  --pipeline         Import → Design → 3D integration test
  --vba              VBA adapter + smoke tests (macOS only)
  --cli              CLI cold-start smoke test
  --benchmark        API endpoint benchmarks
  --ci               Full local CI (black, ruff, mypy, pytest, coverage)
  --changed          Run tests only for changed files (smart mapping)
  --stats            Update test_stats.json with current counts

Any other args are passed directly to pytest:
  ./run.sh test -k "test_flexure" -v
  ./run.sh test --tb=short -x

Examples:
  ./run.sh test                     # Run all tests
  ./run.sh test --parity            # API parity check
  ./run.sh test -k "shear" -v      # Run shear tests, verbose
  ./run.sh test --ci                # Full CI locally
EOF
}

# ── Command: generate ──────────────────────────────────────────────────────

_cmd_generate() {
    _require_venv
    local subcmd="${1:-}"
    shift 2>/dev/null || true

    case "$subcmd" in
        indexes)
            "$SCRIPTS/generate_all_indexes.sh" "$@"
            ;;
        sdk)
            "$VENV" "$SCRIPTS/generate_client_sdks.py" "$@"
            ;;
        manifest)
            "$VENV" "$SCRIPTS/generate_api_manifest.py" "$@"
            ;;
        docs-index)
            "$VENV" "$SCRIPTS/generate_docs_index.py" "$@"
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

Generate indexes, SDKs, manifests, and scaffolds.

Subcommands:
  indexes              Regenerate all folder index.json + index.md
  sdk                  Generate TypeScript/Python client SDKs
  manifest             Generate/validate api-manifest.json
  docs-index           Generate docs-index.json from markdown
  scaffold <module>    Generate pytest test template for a module

Examples:
  ./run.sh generate indexes                     # Regenerate all indexes
  ./run.sh generate sdk                         # Generate client SDKs
  ./run.sh generate scaffold structural_lib.core  # Test template
EOF
}

# ── Command: info ──────────────────────────────────────────────────────────

_cmd_info() {
    _require_venv
    _header "Library Info"
    "$VENV" "$SCRIPTS/library_info.py" "$@"
}

_help_info() {
    cat <<'EOF'
Usage: ./run.sh info [options]

Library metadata, API surface, architecture, element support, and tooling.

Options:
  --api              Public API functions (26 functions, line numbers)
  --architecture     4-layer architecture rules
  --elements         IS 456 element support map
  --cli              CLI commands (python -m structural_lib)
  --scripts          Scripts & automation inventory
  --agents           Agents, skills & prompts inventory
  --json             Machine-readable JSON output
  --all              Show everything

Examples:
  ./run.sh info                       # Quick overview
  ./run.sh info --api                 # List public API functions
  ./run.sh info --elements            # Check element support
  ./run.sh info --json                # JSON for programmatic use
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
  --fix                Apply auto-fixes and commit
  --review weekly      Quick weekly review (numbers, links, feedback)
  --review monthly     Full monthly review (all checks + archive)
  --status             Show last evolution run + recommendations
  --report             Generate report without fixes
  --json               JSON output

Examples:
  ./run.sh evolve                       # Full dry-run scan
  ./run.sh evolve --fix                  # Apply fixes + commit
  ./run.sh evolve --review weekly --fix  # Weekly auto-maintenance
  ./run.sh evolve --status               # When was last run?
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
    echo -e "  ${GREEN}commit${NC}      Stage, commit, and push safely"
    echo -e "  ${GREEN}pr${NC}          Create/finish pull requests"
    echo -e "  ${GREEN}session${NC}     Start/end agent sessions"
    echo -e "  ${GREEN}find${NC}        Discover scripts and API signatures"
    echo -e "  ${GREEN}release${NC}     Version bumps and release management"
    echo -e "  ${GREEN}audit${NC}       Run readiness/governance audit"
    echo -e "  ${GREEN}test${NC}        Run test suites"
    echo -e "  ${GREEN}generate${NC}    Generate indexes, SDKs, manifests"
    echo -e "  ${GREEN}health${NC}      Project health scan (unified checker)"
    echo -e "  ${GREEN}feedback${NC}    Agent feedback collection & analysis"
    echo -e "  ${GREEN}evolve${NC}      Self-evolution engine (scan + fix + report)"
    echo -e "  ${GREEN}info${NC}        Library metadata, API, architecture, elements"
    echo -e "  ${GREEN}preflight${NC}   Pre-flight safety check (branch, venv, ports)"
    echo ""
    echo -e "${BOLD}Quick Start:${NC}"
    echo -e "  ${DIM}./run.sh session start${NC}              # Begin work"
    echo -e "  ${DIM}./run.sh check --quick${NC}              # Fast validation"
    echo -e "  ${DIM}./run.sh commit \"feat: description\"${NC}  # Save work"
    echo -e "  ${DIM}./run.sh session end${NC}                # Wrap up"
    echo ""
    echo -e "${DIM}Run ./run.sh <command> --help for detailed usage.${NC}"
}

# Handle --help for any command
_dispatch_help() {
    local cmd="$1"
    case "$cmd" in
        check)    _help_check ;;
        commit)   _help_commit ;;
        pr)       _help_pr ;;
        session)  _help_session ;;
        find)     _help_find ;;
        release)  _help_release ;;
        audit)    _help_audit ;;
        test)     _help_test ;;
        generate) _help_generate ;;
        health)   _help_health ;;
        feedback) _help_feedback ;;
        evolve)   _help_evolve ;;
        info)     _help_info ;;
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
        'commit:Stage, commit, and push'
        'pr:Manage pull requests'
        'session:Manage agent sessions'
        'find:Discover scripts and API'
        'release:Version bumps'
        'audit:Readiness audit'
        'test:Run test suites'
        'generate:Generate indexes and SDKs'
        'health:Project health scan'
        'feedback:Agent feedback collection'
        'evolve:Self-evolution engine'
        'info:Library metadata and API'
    )
    local -a check_opts=('--quick' '--changed' '--pre-commit' '--category' '--fix' '--json' '--list' '--serial')
    local -a categories=('api' 'docs' 'arch' 'governance' 'fastapi' 'git' 'stale' 'code')
    local -a pr_subs=('create' 'finish' 'status')
    local -a session_subs=('start' 'end' 'summary' 'sync' 'check')
    local -a generate_subs=('indexes' 'sdk' 'manifest' 'docs-index' 'scaffold')
    local -a health_opts=('--fix' '--score' '--quick' '--category' '--json')
    local -a feedback_subs=('log' 'summary' 'pending' 'resolve' 'stats')
    local -a evolve_opts=('--fix' '--review' '--status' '--report' '--json')
    local -a test_opts=('--parity' '--pipeline' '--vba' '--cli' '--benchmark' '--ci' '--stats')
    local -a audit_opts=('--score' '--errors' '--inputs' '--diagnostics')
    local -a release_subs=('run' 'verify' 'check-docs' 'checklist')

    if (( CURRENT == 2 )); then
        _describe 'command' commands
    elif (( CURRENT == 3 )); then
        case "${words[2]}" in
            check) _values 'option' $check_opts ;;
            pr) _values 'subcommand' $pr_subs ;;
            session) _values 'subcommand' $session_subs ;;
            generate) _values 'subcommand' $generate_subs ;;
            health) _values 'option' $health_opts ;;
            feedback) _values 'subcommand' $feedback_subs ;;
            evolve) _values 'option' $evolve_opts ;;
            info) _values 'option' '--api' '--architecture' '--elements' '--cli' '--scripts' '--agents' '--json' '--all' ;;
            test) _values 'option' $test_opts ;;
            audit) _values 'option' $audit_opts ;;
            release) _values 'subcommand' $release_subs ;;
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
        commit)   _cmd_commit "$@" ;;
        pr)       _cmd_pr "$@" ;;
        session)  _cmd_session "$@" ;;
        find)     _cmd_find "$@" ;;
        release)  _cmd_release "$@" ;;
        audit)    _cmd_audit "$@" ;;
        test)     _cmd_test "$@" ;;
        generate) _cmd_generate "$@" ;;
        health)   _cmd_health "$@" ;;
        feedback) _cmd_feedback "$@" ;;
        evolve)   _cmd_evolve "$@" ;;
        info)     _cmd_info "$@" ;;
        preflight) _require_venv; "$VENV" "$SCRIPTS/preflight.py" "$@" ;;
        *)
            _error "Unknown command: $cmd"
            echo ""
            _print_usage
            exit 1
            ;;
    esac
}

main "$@"
