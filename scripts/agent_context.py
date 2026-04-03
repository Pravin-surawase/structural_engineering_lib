#!/usr/bin/env python3
"""Agent Context Loader — gives each agent its tailored startup context.

Usage:
    .venv/bin/python scripts/agent_context.py <agent_name>
    .venv/bin/python scripts/agent_context.py --list
"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# ── Agent registry ──────────────────────────────────────────────────────

AGENTS: dict[str, dict] = {}


def agent(name: str, description: str):
    """Decorator to register an agent context function."""

    def decorator(func):
        AGENTS[name] = {"description": description, "func": func}
        return func

    return decorator


# ── Helpers ─────────────────────────────────────────────────────────────


def run(cmd: str, cwd: str | None = None, timeout: int = 15) -> str:
    """Run a shell command and return stdout (stripped). Returns '' on error."""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=cwd or str(ROOT),
        )
        return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return ""


def head(filepath: str, n: int = 15) -> str:
    """Read first n lines of a file relative to ROOT."""
    p = ROOT / filepath
    if not p.exists():
        return f"  (file not found: {filepath})"
    lines = p.read_text().splitlines()[:n]
    return "\n".join(f"  {l}" for l in lines)


def section(title: str):
    """Print a section header."""
    print(f"\n{'─' * 60}")
    print(f"  {title}")
    print(f"{'─' * 60}")


def bullet(text: str):
    print(f"  • {text}")


# ── Common status (shared by all agents) ────────────────────────────────


def print_status():
    """Print common project status: git, tasks, session brief."""
    section("PROJECT STATUS")

    # Git
    branch = run("git branch --show-current")
    uncommitted = run("git status --porcelain | wc -l").strip()
    recent = run("git --no-pager log --oneline -5")
    print(f"\n  Branch: {branch}")
    print(f"  Uncommitted files: {uncommitted}")
    print("  Recent commits:")
    for line in recent.splitlines()[:5]:
        print(f"    {line}")

    # Session brief
    section("SESSION BRIEF (docs/planning/next-session-brief.md)")
    print(head("docs/planning/next-session-brief.md", 20))

    # Active tasks
    section("ACTIVE TASKS (docs/TASKS.md — first 25 lines)")
    print(head("docs/TASKS.md", 25))


# ── Agent context functions ─────────────────────────────────────────────


@agent("orchestrator", "Plan, triage, and delegate tasks")
def ctx_orchestrator():
    print_status()

    section("DECISION TREE — Which Agent?")
    print("""  Python/structural_lib changes → @backend
  React/Tailwind/R3F changes    → @frontend
  FastAPI routes/endpoints      → @api-developer
  IS 456 formula/compliance     → @structural-engineer
  Code review needed            → @reviewer
  Tests needed                  → @tester
  Docs/session/archive          → @doc-master
  Git/Docker/CI                 → @ops
  Project health/maintenance    → @governance
  UI/UX design (read-only)      → @ui-designer""")

    section("SKILL ROUTING")
    print("""  /session-management   → session start/end
  /safe-file-ops        → move/delete files
  /api-discovery        → API param lookup
  /is456-verification   → IS 456 test runner
  /react-validation     → React build/lint
  /architecture-check   → 4-layer validation""")

    section("MANDATORY PIPELINE")
    print("""  1. PLAN    → Read priorities, scope work
  2. GATHER  → Search before coding (hooks, routes, API)
  3. EXECUTE → Delegate to specialist agent
  4. VERIFY  → @reviewer checks changes
  5. DOCUMENT → @doc-master updates docs
  6. COMMIT  → @ops commits via ai_commit.sh""")


@agent("backend", "Python structural_lib core — IS 456 math, services, adapters")
def ctx_backend():
    print_status()

    section("4-LAYER ARCHITECTURE")
    print("""  Core types  → Python/structural_lib/core/         (no IS 456 math)
  IS 456 Code → Python/structural_lib/codes/is456/  (pure math, NO I/O)
  Services    → Python/structural_lib/services/      (orchestration)
  UI/IO       → react_app/, fastapi_app/             (interfaces)

  ⚠ Import rule: Core ← IS 456 ← Services ← UI. Never upward.
  ⚠ Units: always explicit — mm, N/mm², kN, kNm""")

    section("PUBLIC API FUNCTIONS (services/api.py)")
    api_funcs = run('grep "^def " Python/structural_lib/services/api.py | head -25')
    if api_funcs:
        for line in api_funcs.splitlines():
            print(f"    {line}")
    else:
        print("  (could not read api.py)")

    section("FOLDER STRUCTURE")
    bullet("core/ — base classes, types, materials, constants")
    bullet("codes/is456/ — IS 456:2000 pure math (flexure, shear, detailing, etc.)")
    bullet("services/ — api.py (23 public funcs), adapters.py (71KB), beam_pipeline.py")
    bullet("insights/ — design insights & analysis helpers")
    bullet("reports/ — report generation")
    bullet("visualization/ — geometry_3d.py (beam_to_3d_geometry)")

    section("KEY COMMANDS")
    bullet("API signatures: .venv/bin/python scripts/discover_api_signatures.py <func>")
    bullet("Tests: cd Python && .venv/bin/python -m pytest tests/ -v")
    bullet(
        "Import check: .venv/bin/python scripts/validate_imports.py --scope structural_lib"
    )
    bullet("Architecture: .venv/bin/python scripts/check_architecture_boundaries.py")
    bullet("Skill: /api-discovery, /is456-verification, /architecture-check")

    section("WARNINGS")
    bullet("api.py at root is a STUB — real code is services/api.py")
    bullet("adapters.py → services/adapters.py (71KB, read selectively)")
    bullet("geometry_3d.py → visualization/geometry_3d.py")
    bullet("Never guess param names (b_mm not width, fck not concrete_grade)")


@agent("frontend", "React 19, R3F, Tailwind, hooks, components, Zustand")
def ctx_frontend():
    print_status()

    section("EXISTING HOOKS (DO NOT RECREATE)")
    hooks = run("ls react_app/src/hooks/ 2>/dev/null")
    if hooks:
        for h in hooks.splitlines():
            print(f"    {h}")
    else:
        print("  (could not list hooks)")

    section("KEY HOOK PURPOSES")
    bullet("useCSVFileImport, useDualCSVImport, useBatchDesign → CSV import")
    bullet("useBeamGeometry → 3D rebar/stirrup positions from API")
    bullet("useLiveDesign, useAutoDesign → live design updates")
    bullet("useBuildingGeometry, useCrossSectionGeometry → building/section viz")
    bullet("useExport → BBS/DXF/report export")
    bullet("useDesignWebSocket → WebSocket live updates")

    section("COMPONENT STRUCTURE")
    components = run("ls react_app/src/components/ 2>/dev/null")
    if components:
        for c in components.splitlines():
            print(f"    {c}/")
    else:
        print("  (could not list components)")

    section("KEY RULES")
    bullet("Tailwind ONLY — no .css files for components")
    bullet("All data flows through FastAPI — no CSV parsing or geometry in JS")
    bullet("Build check before commit: cd react_app && npm run build")
    bullet("Dev server: cd react_app && npm run dev (port 5173)")
    bullet("Skill: /react-validation")

    section("STATE STORES (Zustand)")
    bullet("useDesignStore — single beam design inputs/results")
    bullet("useImportedBeamsStore — imported CSV beams + selection")

    section("ENVIRONMENT")
    nm_exists = (ROOT / "react_app" / "node_modules").exists()
    print(
        f"  node_modules: {'✓ installed' if nm_exists else '✗ run: cd react_app && npm install'}"
    )
    node = run("node --version 2>/dev/null")
    print(f"  Node: {node if node else '✗ not found'}")


@agent("api-developer", "FastAPI routers, REST endpoints, WebSocket, Pydantic")
def ctx_api_developer():
    print_status()

    section("ROUTER FILES (13 routers, 58 endpoints)")
    routers = run("ls fastapi_app/routers/*.py 2>/dev/null")
    if routers:
        for r in routers.splitlines():
            print(f"    {Path(r).name}")
    else:
        print("  (could not list routers)")

    section("EXISTING ROUTES (live)")
    routes = run('grep -rn "@router\\." fastapi_app/routers/ | head -25')
    if routes:
        for r in routes.splitlines()[:25]:
            print(f"    {r}")
    else:
        print("  (could not grep routes)")

    section("KEY ROUTES")
    bullet("POST /api/v1/import/csv — CSV import with GenericCSVAdapter")
    bullet("POST /api/v1/geometry/beam/full — 3D rebar/stirrup positions")
    bullet("POST /api/v1/design/beam — beam design (design_beam_is456)")
    bullet("/ws/design/{session} — WebSocket live updates")
    bullet("API docs at /docs (auto-generated OpenAPI)")

    section("KEY RULES")
    bullet("FastAPI calls structural_lib directly — no duplicated logic")
    bullet("Check existing routes BEFORE adding new ones")
    bullet("Use Pydantic models in fastapi_app/models/")
    bullet("Skill: /api-discovery — get exact param names")

    section("DOCKER")
    bullet("colima start --cpu 4 --memory 4 (prerequisite on Mac)")
    bullet("docker compose up --build (production)")
    bullet("docker compose -f docker-compose.dev.yml up (dev + hot reload)")


@agent("structural-engineer", "IS 456:2000 compliance, formula validation, benchmarks")
def ctx_structural_engineer():
    print_status()

    section("IS 456 MODULES")
    is456 = run("ls Python/structural_lib/codes/is456/*.py 2>/dev/null")
    if is456:
        for f in is456.splitlines():
            print(f"    {Path(f).name}")
    else:
        print("  (could not list IS 456 modules)")

    section("KEY RULES")
    bullet("Pure math, NO I/O in codes/is456/")
    bullet("Units always explicit: mm, N/mm², kN, kNm")
    bullet("Every formula must cite its IS 456 clause number")
    bullet("Core types in core/ — no IS 456 math there")
    bullet("Skill: /is456-verification — run compliance tests")

    section("KEY FUNCTIONS")
    bullet("design_beam_is456() — main beam design entry point")
    bullet("detail_beam_is456() — detailing (bar placement, stirrups)")
    bullet("beam_to_3d_geometry() — 3D visualization positions")

    section("VERIFICATION COMMANDS")
    bullet("cd Python && .venv/bin/python -m pytest tests/ -v -k 'is456'")
    bullet(".venv/bin/python scripts/discover_api_signatures.py <func>")
    bullet("Param names: b_mm (not width), fck (not concrete_grade), d_mm (not depth)")

    section("CLAUSE COVERAGE")
    clauses = run(
        'grep -r "Clause\\|clause\\|cl\\." Python/structural_lib/codes/is456/ | wc -l'
    )
    test_is456 = run(
        'grep -r "def test_" Python/tests/ | grep -i "is456\\|flexure\\|shear\\|detailing" | wc -l'
    )
    print(f"  IS 456 clause references: {clauses}")
    print(f"  IS 456-related tests: {test_is456}")


@agent("reviewer", "Code review, architecture validation, security checks")
def ctx_reviewer():
    print_status()

    section("REVIEW CHECKLIST")
    print("""  □ Architecture: correct layer, import direction okay
  □ Units: explicit mm/N/kN/kNm, no hidden conversions
  □ Duplication: no reinvented hooks/adapters/routes
  □ IS 456: formulas cite clause numbers, correct math
  □ Git: ./scripts/ai_commit.sh used, conventional commits
  □ Tests: 85% branch coverage, edge cases covered
  □ Security: no hardcoded secrets, input validated""")

    section("VERDICT FORMAT")
    print("""  ## Verdict: APPROVED / NEEDS CHANGES / BLOCKED
  ### Findings
  - [PASS/FAIL] Category: Detail
  ### Required Actions (if not approved)
  - [ ] Action item""")

    section("SKILLS")
    bullet("/architecture-check — 4-layer boundary validation")
    bullet("/react-validation — React build/lint/type-check")
    bullet("/is456-verification — IS 456 compliance tests")

    section("COMMANDS")
    bullet(".venv/bin/python scripts/check_architecture_boundaries.py")
    bullet(".venv/bin/python scripts/validate_imports.py --scope structural_lib")
    bullet("cd react_app && npm run build")
    bullet("cd Python && .venv/bin/python -m pytest tests/ -v")


@agent("tester", "Test creation, coverage, regression testing, benchmarks")
def ctx_tester():
    print_status()

    section("TEST STRUCTURE")
    test_dirs = run("find Python/tests -type d -maxdepth 2 2>/dev/null")
    if test_dirs:
        for d in test_dirs.splitlines():
            print(f"    {d}")
    else:
        print("  (could not list test dirs)")

    section("TEST COUNTS")
    test_count = run('grep -r "def test_" Python/tests/ | wc -l')
    print(f"  Total test functions: {test_count}")

    section("KEY RULES")
    bullet("85% branch coverage required")
    bullet("Structural tests must cite IS 456 clauses")
    bullet("Use parametrize for edge cases")
    bullet("Never mock structural_lib internals — test real math")

    section("COMMANDS")
    bullet("cd Python && .venv/bin/python -m pytest tests/ -v")
    bullet(".venv/bin/python -m pytest tests/ --cov=structural_lib --cov-report=term")
    bullet("Skill: /is456-verification — run IS 456 tests by category")

    section("REACT TESTS")
    bullet("cd react_app && npx vitest run")
    bullet("Skill: /react-validation — full React validation")


@agent("doc-master", "Documentation maintenance — session logs, archives, indexes")
def ctx_doc_master():
    print_status()

    section("DOC STRUCTURE")
    bullet("docs/TASKS.md — active task board")
    bullet("docs/WORKLOG.md — one-line-per-change log")
    bullet("docs/SESSION_LOG.md — detailed session history (400KB+, read selectively)")
    bullet("docs/planning/next-session-brief.md — handoff to next agent")
    bullet("docs/docs-canonical.json — canonical doc registry")

    section("SESSION END WORKFLOW (MANDATORY)")
    print("""  1. ./run.sh commit "type: message"     # Commit work
  2. ./run.sh session summary              # Auto-log to SESSION_LOG
  3. ./run.sh session sync                 # Fix stale numbers
  4. Update docs/planning/next-session-brief.md
  5. Update docs/TASKS.md
  6. Append to docs/WORKLOG.md
  7. ./run.sh commit "docs: session end"   # Commit doc updates""")

    section("COMMANDS")
    bullet("Safe move: .venv/bin/python scripts/safe_file_move.py a b --dry-run")
    bullet("Safe delete: .venv/bin/python scripts/safe_file_delete.py f")
    bullet("Create doc: .venv/bin/python scripts/create_doc.py path")
    bullet(
        "Generate indexes: .venv/bin/python scripts/generate_enhanced_index.py --all"
    )
    bullet("Skill: /safe-file-ops, /session-management")

    section("DOC COUNTS")
    md_count = run("find docs -name '*.md' | wc -l")
    print(f"  Markdown files in docs/: {md_count}")


@agent("ops", "Git workflow, CI/CD, Docker, environment management")
def ctx_ops():
    print_status()

    section("GIT WORKFLOW — THE ONE RULE")
    print("""  ./scripts/ai_commit.sh "type: message"    # ALL commits
  NEVER manual git add/commit/push/pull
  Format: feat|fix|docs|refactor|test|chore|ci(scope): description""")

    section("PR WORKFLOW")
    bullet("./run.sh pr status — check if PR required")
    bullet("./run.sh pr create TASK-XXX 'desc' — create PR")
    bullet("./run.sh pr finish — ship the PR")
    bullet("NEVER use --force to bypass PR check")

    section("DOCKER (Colima on Mac)")
    colima = run("colima status 2>&1 | head -3")
    docker_running = run("docker info 2>/dev/null | head -1")
    if colima and "running" in colima.lower():
        print("  Colima: ✓ running")
    else:
        print("  Colima: ✗ not running → colima start --cpu 4 --memory 4")
    if docker_running:
        print("  Docker: ✓ available")
    else:
        print("  Docker: ✗ not available")
    bullet("docker compose up --build (production)")
    bullet("docker compose -f docker-compose.dev.yml up (dev)")

    section("ENVIRONMENT")
    venv = run("which python 2>/dev/null")
    print(f"  Python: {venv}")
    node = run("node --version 2>/dev/null")
    print(f"  Node: {node if node else 'not found'}")

    section("GIT STATUS")
    worktrees = run("git worktree list 2>/dev/null")
    if worktrees:
        for w in worktrees.splitlines():
            print(f"    {w}")
    stash_count = run("git stash list | wc -l")
    print(f"  Stashes: {stash_count}")

    section("ERROR RECOVERY")
    bullet("Pre-commit hook fails → check .pre-commit-config.yaml")
    bullet("Docker permission denied → colima start")
    bullet("Merge conflicts → resolve, then ai_commit.sh")
    bullet("Terminal stuck in pager → q to exit, or agent_start.sh fixes it")


@agent("governance", "Project health, maintenance, metrics tracking")
def ctx_governance():
    print_status()

    section("HEALTH METRICS (live)")
    md_count = run("find docs -name '*.md' | wc -l")
    script_count = run("ls scripts/*.py scripts/*.sh 2>/dev/null | wc -l")
    test_count = run('grep -r "def test_" Python/tests/ | wc -l')
    agent_count = run("ls .github/agents/*.agent.md 2>/dev/null | wc -l")
    skill_count = run("ls .github/skills/*/SKILL.md 2>/dev/null | wc -l")
    prompt_count = run("ls .github/prompts/*.prompt.md 2>/dev/null | wc -l")
    print(f"  Doc files: {md_count}")
    print(f"  Scripts: {script_count}")
    print(f"  Test functions: {test_count}")
    print(f"  Agents: {agent_count} | Skills: {skill_count} | Prompts: {prompt_count}")

    commits_30d = run("git --no-pager log --oneline --since='30 days ago' | wc -l")
    commits_7d = run("git --no-pager log --oneline --since='7 days ago' | wc -l")
    print(f"  Commits (7d): {commits_7d} | Commits (30d): {commits_30d}")

    section("MAINTENANCE TASKS")
    bullet("Check governance: .venv/bin/python scripts/check_governance.py --structure")
    bullet("Sync numbers: .venv/bin/python scripts/sync_numbers.py --fix")
    bullet("Link health: .venv/bin/python scripts/check_links.py")
    bullet(
        "Generate indexes: .venv/bin/python scripts/generate_enhanced_index.py --all"
    )
    bullet("Archive old docs: .venv/bin/python scripts/archive_old_files.sh")

    section("SUSTAINABILITY CHECKS")
    bullet("Version consistency: .venv/bin/python scripts/check_doc_versions.py")
    bullet("Bootstrap freshness: .venv/bin/python scripts/check_bootstrap_freshness.py")
    bullet("Instruction drift: .venv/bin/python scripts/check_instruction_drift.py")
    bullet("Architecture: .venv/bin/python scripts/check_architecture_boundaries.py")
    bullet("Skill: /safe-file-ops, /session-management")


@agent("ui-designer", "Visual design, UX flow, component layout, accessibility")
def ctx_ui_designer():
    print_status()

    section("COMPONENT INVENTORY")
    components = run("ls react_app/src/components/ 2>/dev/null")
    if components:
        for c in components.splitlines():
            print(f"    {c}/")
    else:
        print("  (could not list components)")

    section("DESIGN RULES")
    bullet("Tailwind ONLY — no custom CSS files")
    bullet("Read-only agent — design specs only, no code")
    bullet("Engineers are the primary users — clarity > aesthetics")

    section("DESIGN SPEC FORMAT (MANDATORY)")
    print("""  ## Design Spec: [Feature Name]
  ### Layout — component hierarchy, grid, responsive
  ### Visual Design — colors, typography, spacing (Tailwind)
  ### State Variations — loading, empty, error, success
  ### Interactions — hover, click, transitions
  ### Accessibility — ARIA, keyboard, contrast""")

    section("COLOR PALETTE")
    bullet("Primary: Tailwind blue-600")
    bullet("Success: green-500, Warning: amber-500, Error: red-500")
    bullet("Background: slate-50 (light), slate-900 (dark)")


# ── Main ────────────────────────────────────────────────────────────────


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("--help", "-h"):
        print("Usage: .venv/bin/python scripts/agent_context.py <agent_name>")
        print("       .venv/bin/python scripts/agent_context.py --list")
        print(f"\nAvailable agents: {', '.join(sorted(AGENTS.keys()))}")
        sys.exit(0)

    if sys.argv[1] == "--list":
        print("Available agents:\n")
        for name in sorted(AGENTS.keys()):
            desc = AGENTS[name]["description"]
            print(f"  {name:25s} {desc}")
        sys.exit(0)

    agent_name = sys.argv[1].lower().strip()
    if agent_name not in AGENTS:
        print(f"Unknown agent: {agent_name}")
        print(f"Available: {', '.join(sorted(AGENTS.keys()))}")
        sys.exit(1)

    print(f"╔{'═' * 58}╗")
    print(f"║  Agent: {agent_name:48s} ║")
    print(f"║  {AGENTS[agent_name]['description']:56s} ║")
    print(f"╚{'═' * 58}╝")

    AGENTS[agent_name]["func"]()

    # Self-evolving system context
    section("PROJECT HEALTH")
    health_score = run(
        f"{ROOT / '.venv/bin/python'} {ROOT / 'scripts/project_health.py'} --score 2>/dev/null"
    )
    if health_score:
        bullet(health_score.strip())
    else:
        bullet("Run: ./run.sh health --score")

    pending_fb = run(
        f"{ROOT / '.venv/bin/python'} {ROOT / 'scripts/agent_feedback.py'} pending --brief 2>/dev/null"
    )
    if pending_fb:
        bullet(pending_fb.strip())

    section("SESSION END CHECKLIST")
    bullet(
        "Log feedback: ./run.sh feedback log --agent "
        + agent_name
        + " --stale-doc '...' --missing '...'"
    )
    bullet("Commit: ./scripts/ai_commit.sh 'type: message'")
    bullet("Never manual git add/commit/push/pull")
    bullet("Search before coding — don't duplicate existing code")
    print()


if __name__ == "__main__":
    main()
