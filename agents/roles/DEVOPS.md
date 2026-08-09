---
owner: Governance Agent
status: active
last_updated: 2026-08-07
doc_type: reference
complexity: intermediate
tags: [agents, roles]
---

# DEVOPS Agent — Role Document

**Role:** Manage repository structure and automation.

**Focus Areas:**
- Repo layout and file organization
- VBA module export/import workflows
- Versioning and tagging
- Build/test automation (CI when ready)

---

## When to Use This Role

Use DEVOPS agent when:
- Designing or refining folder structure
- Setting up version control workflows
- Creating automation scripts
- Preparing for releases or packaging

---

## Repository Structure

```
structural_engineering_lib/
├── VBA/
│   ├── Modules/          ← Exported .bas files (source of truth)
│   ├── Tests/            ← Test modules
│   ├── Examples/         ← Example usage
│   └── Build/            ← .xlam add-in (generated)
├── Python/
│   ├── structural_lib/   ← Python package
│   ├── tests/            ← pytest tests
│   └── examples/         ← Example scripts
├── Excel/                ← Flagship workbook (future)
│   └── BeamDesign.xlsm
├── logs/                 ← Session logs
├── docs/                 ← All documentation
├── agents/               ← Role documents for AI
├── .gitignore
├── CHANGELOG.md
├── LICENSE
└── README.md
```

---

## Version Control Workflow

### Commit Messages
```
<type>: <short description>

Types:
- feat: new feature
- fix: bug fix
- docs: documentation
- refactor: code restructuring
- test: adding tests
- chore: maintenance

Examples:
feat: add doubly reinforced beam support
fix: correct Tc interpolation for edge grades
docs: update API reference with shear functions
```

### Branching (when needed)
- `main` — stable, release-ready
- `feat/<name>` — feature development
- `fix/<name>` — bug fixes

### Tagging
```
v0.1.0 — first working version
v0.2.0 — doubly reinforced added
v1.0.0 — production ready with ductile detailing
```

---

## Automation Tasks

| Task | Tool | Status |
|------|------|--------|
| Python tests | GitHub Actions + pytest | ✅ Active |
| VBA tests | `RunAllTests` Macro | ✅ Active (Mac Compatible) |
| Python lint | black + ruff + mypy (CI) | ✅ Active |
| Build .xlam | Manual export | 🔜 Planned |
| CI pipeline | GitHub Actions | ✅ Active |

### Dependabot (Low Noise)
- Dependabot runs weekly for:
   - GitHub Actions (`/`)
   - Python dependencies (`/Python`)
- Updates are grouped (to reduce PR churn), labeled `dependencies`, and use `chore(deps)` commit prefixes.

## GitHub Security Posture (Low Maintenance)
- Protect `main` in GitHub settings (require PR + required checks; disallow force-push + deletion).
- Prefer repo settings + least-privilege workflow permissions over high-maintenance action SHA pinning.

Practical note:
- If the repo ruleset requires PR branches to be up to date, use `gh pr update-branch <PR_NUMBER>` before merging.

## Mac VBA Workflow
1. **Edit:** Edit `.bas` files in VS Code.
2. **Import:** In Excel VBA Editor, remove old module -> Import new file.
3. **Compile:** `Debug > Compile VBAProject`.
4. **Test:** Run `RunAllTests` in Immediate Window.
   - *Note:* Do not rely on `Debug.Print` during calculation steps.

---

## Output Expectations

When acting as DEVOPS agent, provide:
1. **Structure recommendations** — Where files should live
2. **Workflow steps** — Clear, numbered instructions
3. **Automation scripts** — Shell/Python scripts if needed
4. **Checklists** — Pre-release verification steps

## Environment Targets
- Excel/VBA: Office 2016+ (Win/Mac), 64-bit preferred.
- Python: 3.9–3.12.
- Avoid platform-specific paths; keep builds reproducible.

---

## Example Prompt

```
Use project-overview.md as context. Act as DEVOPS agent.
Design a pre-release checklist for v0.1.0 including
tests to run, docs to update, and git commands.
```

---

**Reference:** See `docs/architecture/project-overview.md` (context) and `docs/contributing/development-guide.md` Section 16 (release checklist).
