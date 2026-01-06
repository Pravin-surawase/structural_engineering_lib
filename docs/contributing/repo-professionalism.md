# Repo Professionalism Playbook

Purpose: keep the repo reliable, predictable, and safe to publish even when work is fast or done by multiple agents.

This doc does not replace existing rules. It links to the canonical sources and adds a practical "what to do next" map.

---

## 0) First-time setup

```bash
cd Python && python -m venv ../.venv && source ../.venv/bin/activate
pip install -e ".[dev]"
pre-commit install
```

After this, always use `.venv/bin/python` (not bare `python`).

---

## 1) Non-negotiables (read first)

- Beam-only scope until v1.0. Do not expand scope in the core without PM approval.
- Determinism and units are mandatory (see `docs/reference/known-pitfalls.md`).
- No direct commits to `main`. All changes go through PRs.
- Every change links to a TASK or Issue and updates docs with code.

Canonical sources:
- Git rules: `docs/_internal/GIT_GOVERNANCE.md`
- Dev standards: `docs/contributing/development-guide.md`
- Test strategy: `docs/contributing/testing-strategy.md`
- Agent workflow: `docs/_internal/AGENT_WORKFLOW.md`

---

## 2) GitHub hygiene and governance

### Branching and PRs
- Use short-lived branches: `feat/task-XXX-...`, `fix/task-XXX-...`.
- Squash merge after CI passes: `gh pr merge <PR> --squash --delete-branch`.
- Delete branches after merge (the command above does this automatically).
- Local guardrail: pre-commit blocks commits on `main` (see `.pre-commit-config.yaml`).
- CI guardrail: pushes to `main` must be associated with a PR (see `.github/workflows/main-branch-guard.yml`).

### Task hygiene
- TASKS format is enforced locally: `scripts/check_tasks_format.py`.
- Keep WIP=1 and move tasks between sections (no duplicates).
- For phased initiatives, use a single umbrella task and list included TASK IDs in its description; track the included tasks in Recently Done.

### Docs hygiene
- Docs index structure is enforced locally and in CI: `scripts/check_docs_index.py`.
- Release docs consistency is enforced locally and in CI: `scripts/check_release_docs.py`.
- Session docs consistency is enforced locally and in CI: `scripts/check_session_docs.py`.
- Handoff brief is derived from SESSION_LOG: `scripts/update_handoff.py` (or `scripts/end_session.py --fix`).
- API docs sync is enforced locally and in CI: `scripts/check_api_docs_sync.py`.
- Pre-release checklist structure is enforced locally and in CI: `scripts/check_pre_release_checklist.py`.
- API doc signatures are enforced locally and in CI: `scripts/check_api_doc_signatures.py`.
- Next-session brief length is enforced locally and in CI: `scripts/check_next_session_brief_length.py`.
- CLI reference completeness is enforced locally and in CI: `scripts/check_cli_reference.py`.
- Docs index links are enforced locally and in CI: `scripts/check_docs_index_links.py`.

### PR discipline
- Use the PR template in `.github/pull_request_template.md`.
- Link a TASK ID in the PR body.
- Wait for CI: `gh pr checks <PR> --watch`.

### Issues and labels (keep small)
Recommended minimal labels:
- `type/bug`, `type/feature`, `type/docs`
- `prio/P0`, `prio/P1`, `prio/P2`
- `area/core`, `area/dxf`, `area/bbs`, `area/vba`, `area/docs`
- `agent/DEV`, `agent/TESTER`, `agent/DOCS`

### Releases
- Append to `docs/RELEASES.md` and `CHANGELOG.md`.
- Tag after merge: `git tag -a vX.Y.Z -m "vX.Y.Z"`.
- Publish via Actions (Trusted Publishing).

---

## 3) Quality gates and checks

| Stage | Command | Why it matters |
| --- | --- | --- |
| Docs-only | `.venv/bin/python scripts/check_doc_versions.py` | Prevent version drift |
| Links touched | `.venv/bin/python scripts/check_links.py` | Avoid broken docs |
| Fast code check | `./scripts/quick_check.sh` | Catch basic issues early |
| Full local CI | `./scripts/ci_local.sh` | CI parity before PR |
| External CLI test | `.venv/bin/python scripts/external_cli_test.py` | S-007 cold-start validation |
| Release verify | `.venv/bin/python scripts/verify_release.py --version X.Y.Z --source pypi` | Confirm PyPI artifact |

If any check modifies files, re-stage and re-commit.

---

## 4) Automation map (what is automated vs manual)

### Automated now
- Python CI tests + lint + typecheck + CodeQL
- Doc version drift check in CI
- Pre-commit formatting and whitespace fixes
- Release tagging and PyPI publishing workflow

### Manual now
- VBA test runs and parity checks
- External CLI cold-start test (S-007)

### Next automation candidates
- VBA build automation (.xlam)
- Python <-> VBA parity harness
- Release notes draft from PR labels

---

## 5) Learn from professional libraries

### What they do right
- Stable API contracts and explicit deprecation policy
- Strict versioning and release notes
- Deterministic outputs and golden tests
- Clear docs with examples that run

### Common mistakes to avoid
- Silent breaking changes in schemas
- Unit ambiguity or mixed conventions
- Tests that are brittle or too strict
- Docs that drift from code

### How we apply it here
- Schema versioning and library contract docs
- Golden examples in `Python/examples/`
- CI gates + pre-release checklist
- API stability labels in `docs/reference/api-stability.md`

---

## 6) Repo structure rules

- Keep the 3-layer architecture intact (core/app/io).
- Do not refactor the core structure pre-v1.0.
- Put public contracts in `docs/reference/`.
- Put plans and research in `docs/planning/`.
- Put maintainer workflows in `docs/contributing/`.

---

## 7) AI agents usage (do this, avoid that)

### Do
- **Read `.github/copilot-instructions.md` first** — it's the single source of truth for agent rules.
- Pick a role (DEV/TESTER/DOCS/DEVOPS) before acting.
- Read only the docs you need, then summarize.
- Use the handoff template in `docs/_internal/AGENT_WORKFLOW.md`.

### Avoid
- Editing without reading current file content.
- Large context dumps that obscure the task.
- Making assumptions about schema or units.

### Scope boundary (do NOT add until post-v1.0)
- Frame/slab/foundation checks
- 3D analysis or FEA
- PDF report generation
- ETABS API (COM/OAPI) — CSV-only until v1.0

---

## 8) Confidence loop (minimal but effective)

**Per-session checklist**
1) Run `scripts/start_session.py`.
2) Pick one TASK and finish it.
3) Run the relevant checks (docs or code).
4) Update `docs/SESSION_LOG.md` and `docs/TASKS.md`.
5) Run `scripts/update_handoff.py` (or `scripts/end_session.py --fix`).
6) Stop.

**Release checklist (high level)**
- CI green
- Doc drift clean
- Verification pack still passes
- External CLI test done (S-007)
- `docs/RELEASES.md` and `CHANGELOG.md` updated

Full checklist: `docs/planning/pre-release-checklist.md`.

---

## 9) Quick links

- Git governance: `docs/_internal/GIT_GOVERNANCE.md`
- Development guide: `docs/contributing/development-guide.md`
- Testing strategy: `docs/contributing/testing-strategy.md`
- Pre-release checklist: `docs/planning/pre-release-checklist.md`
- Agent workflow: `docs/_internal/AGENT_WORKFLOW.md`
