# AI Context Pack (VS Code “Vibe Coding”)

Use this file as the single entrypoint for AI agents working in VS Code.

## 0) Golden rule
- Prefer small, deterministic changes.
- Keep Python + VBA parity (same formulas, same units, same edge-case behavior).
- Update docs *in the same change* when behavior/API changes.

---

## 1) What this repo is
- IS 456 RC beam design library.
- Implementations: Python package under `Python/` + VBA modules under `VBA/`.
- Strength design + detailing + DXF export are done (v0.7.0).
- Serviceability (deflection/crack width) is the next big milestone (v0.8).

Start here for architecture and boundaries:
- [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)

---

## 2) “Load these docs first” (minimal context)
Use these as the default context set for most tasks:
- [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md) (layering + intent)
- [API_REFERENCE.md](API_REFERENCE.md) (public API contracts)
- [KNOWN_PITFALLS.md](KNOWN_PITFALLS.md) (units/table rules/edge cases)
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) (VBA/Mac quirks, fixes)
- [TASKS.md](TASKS.md) (canonical backlog + acceptance mindset)
- [NEXT_SESSION_BRIEF.md](NEXT_SESSION_BRIEF.md) (where to resume quickly)

---

## 3) When you’re implementing code
### Python
- Package root: `Python/structural_lib/`
- Tests: `Python/tests/`

Recommended workflow:
1) Add/modify function in Python.
2) Add/modify the matching VBA module function.
3) Add/extend Python unit tests.
4) (If feasible) add/update VBA test harness cases.

### VBA
- Library modules: `VBA/Modules/`
- VBA tests: `VBA/Tests/`

Import order matters; see:
- [VBA_GUIDE.md](VBA_GUIDE.md)

---

## 4) Planning & research (what to read)
- Active v0.8+ research log: [RESEARCH_AI_ENHANCEMENTS.md](RESEARCH_AI_ENHANCEMENTS.md)
- Production checklist summary: [PRODUCTION_ROADMAP.md](PRODUCTION_ROADMAP.md)
- Release ledger (append-only): [RELEASES.md](RELEASES.md)

Historical reference material lives here:
- [docs/_archive/RESEARCH_AND_FINDINGS.md](_archive/RESEARCH_AND_FINDINGS.md)

---

## 5) Agent roles (prompt building blocks)
Role prompt templates live here:
- [../agents/README.md](../agents/README.md)

Internal governance docs (rarely needed during normal coding):
- [docs/_internal/AGENT_WORKFLOW.md](_internal/AGENT_WORKFLOW.md)
- [docs/_internal/GIT_GOVERNANCE.md](_internal/GIT_GOVERNANCE.md)

---

## 6) Copy-paste prompt recipes
### Implement a feature (Python + VBA parity)
"Use PROJECT_OVERVIEW and API_REFERENCE as context. Act as DEV + TESTER. Implement TASK-XXX in Python and VBA with identical behavior and units. Add Python tests. Where VBA tests are practical, add at least one regression case. Output should be deterministic and auditable."

### Debug a mismatch (Python vs VBA)
"Use KNOWN_PITFALLS + TROUBLESHOOTING. Act as TESTER. Create a minimal repro input set, identify the first divergence point, then propose the smallest parity fix with tests."

### Update docs after code change
"Act as DOCS. Update API_REFERENCE examples and any impacted guides. Keep wording precise; no claims about tooling you didn’t run."
