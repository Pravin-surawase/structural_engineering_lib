---
name: development-rules
description: "Hard-learned development rules by domain — Python, FastAPI, React, Testing. Prevents the specific mistakes that caused 70+ audit findings across v0.21.0-v0.21.3."
---

# Development Rules Skill

These rules were learned the hard way across v0.21.0-v0.21.3, where 70+ issues were discovered post-release. Each rule maps to a specific incident.

## When to Use

- **Every agent should read their domain section** before writing code
- **Reviewer must verify** these rules during code review
- **New agents** must read this as part of onboarding

## Universal Rules (ALL Agents)

| # | Rule | Incident | Severity |
|---|------|----------|----------|
| U-1 | Never swallow exceptions silently — log or re-raise with context | v0.21.2: clauses.json missing → silent `{}` | CRITICAL |
| U-2 | Never use `except Exception:` without specific handling | v0.21.2: traceability.py hid failures | CRITICAL |
| U-3 | All public functions must be in `__all__` AND importable | v0.21.2: README claimed non-existent API | HIGH |
| U-4 | Data files must be declared in pyproject.toml package-data | v0.21.2: clauses.json not in wheel | HIGH |
| U-5 | README code examples must be tested in CI | v0.21.2: examples didn't work | HIGH |
| U-6 | Version numbers must be consistent across all files | v0.21.x: version drift across docs | MEDIUM |
| U-7 | Import-time side effects are forbidden (no warnings, no I/O) | v0.21.3 EA-2: import warnings | HIGH |

## Python Core Rules (`Python/structural_lib/`)

| # | Rule | Incident | Agent |
|---|------|----------|-------|
| PY-1 | All parameters use explicit units: `b_mm`, `d_mm`, `fck_nmm2`, `Mu_knm` | Historical confusion | @backend, @structural-math |
| PY-2 | Division by zero must be guarded: `x / y if y != 0 else 0` | Edge case failures | @structural-math |
| PY-3 | IS 456 clause reference required in docstring for every formula | Audit finding | @structural-math |
| PY-4 | Every new function needs: unit test + edge test + SP:16 benchmark | v0.21.0: insufficient testing | @tester |
| PY-5 | Return types must be dataclasses, not dicts (with `.to_dict()` method) | v0.21.3 EA-4: inconsistent returns | @backend |
| PY-6 | Lazy imports for non-core modules (use `__getattr__` pattern) | v0.21.3 EA-10: 382ms startup | @backend |
| PY-7 | Never modify `core/` from `codes/` or `services/` | Architecture rule | @backend |
| PY-8 | Deprecation warnings gated behind actual function call, not module load | v0.21.3 EA-2 | @backend |

## FastAPI Rules (`fastapi_app/`)

| # | Rule | Incident | Agent |
|---|------|----------|-------|
| FA-1 | NEVER use `str(e)` in error responses — use generic messages, log original | v0.21.3 EA-18: 32 CWE-209 instances | @api-developer |
| FA-2 | All endpoints must have rate limiting (global middleware) | v0.21.3 EA-17: only 2/59 had limits | @api-developer |
| FA-3 | WebSocket inputs validated via Pydantic models | v0.21.3 EA-19: raw dict access | @api-developer |
| FA-4 | CORS origins from config/env, never hardcoded | v0.21.3 EA-20 | @api-developer |
| FA-5 | Auth warning when disabled in production | v0.21.3 EA-16 | @ops |
| FA-6 | Routers import from `structural_lib` — never reimplement math | Architecture rule | @api-developer |
| FA-7 | Error responses must not expose internal paths or stack traces | OWASP CWE-209 | @api-developer, @security |

## React Rules (`react_app/`)

| # | Rule | Incident | Agent |
|---|------|----------|-------|
| RE-1 | Forms must have cross-field validation (not just HTML5) | v0.21.3 EA-15: depth > cover unchecked | @frontend |
| RE-2 | All computations go through FastAPI — no local JS math | Architecture rule | @frontend |
| RE-3 | Check `react_app/src/hooks/` before creating a new hook | Historical duplication | @frontend |
| RE-4 | Check `react_app/src/components/` before creating a component | Historical duplication | @frontend |
| RE-5 | Tailwind only — no custom CSS files | Project convention | @frontend |
| RE-6 | Workflow guidance (WorkflowHint) on key pages | v0.21.3 EA-11: users lost | @frontend |

## Testing Rules (`Python/tests/`)

| # | Rule | Incident | Agent |
|---|------|----------|-------|
| TE-1 | NEVER use MagicMock for structural Result types (FlexureResult, ShearResult, etc.) | v0.21.0: ShearResult field bug masked by mock | @tester |
| TE-2 | Use `repo_only` marker for tests needing full repo (not just package) | v0.21.3 EA-8: sdist tests broke | @tester |
| TE-3 | E2E pipeline test required for each structural element | v0.21.3 EA-7: no chain testing | @tester |
| TE-4 | API stability test: all `__all__` members must be importable | v0.21.3 EA-9: phantom exports | @tester |
| TE-5 | Import silence test: `import structural_lib` emits zero warnings | v0.21.3 EA-6 | @tester |
| TE-6 | SP:16 benchmark values must match within ±0.1% | IS 456 compliance requirement | @tester |
| TE-7 | Packaging test: wheel must not contain tests/, scripts/, examples/ | v0.21.2: leaked files | @tester |

## Documentation Rules

| # | Rule | Incident | Agent |
|---|------|----------|-------|
| DO-1 | WORKLOG.md: one line per code change, every time, no exceptions | Historical gaps | @doc-master |
| DO-2 | next-session-brief.md: MUST be updated at session end | 10+ hours rework from missing brief | @doc-master |
| DO-3 | TASKS.md: mark done items, add discovered items | Tasks repeated when not tracked | @doc-master |
| DO-4 | README code examples must match actual API exactly | v0.21.2: phantom function claims | @doc-master |
| DO-5 | CHANGELOG: append-only, immutable past entries | Data integrity | @doc-master |
| DO-6 | New docs need metadata header (Type, Audience, Status, etc.) | Governance requirement | @doc-master |

## Security Rules

| # | Rule | Incident | Agent |
|---|------|----------|-------|
| SE-1 | No internal error details in HTTP responses | v0.21.3: CWE-209 | @security, @api-developer |
| SE-2 | Rate limiting on all public endpoints | v0.21.3: DoS risk | @api-developer |
| SE-3 | Input validation at system boundaries (Pydantic) | v0.21.3: WebSocket raw | @api-developer |
| SE-4 | Dependencies audited before release | pip-audit recommended | @security |
| SE-5 | Auth must warn in production when disabled | v0.21.3 EA-16 | @ops |

## How to Enforce

1. **Code review**: Reviewer checks rules for changed domains
2. **Quality gate**: Level 1-3 automated checks (see `/quality-gate` skill)
3. **Pre-release**: Full checklist (see `/release-preflight` skill)
4. **Agent evolution**: Violations tracked by agent-evolver scoring