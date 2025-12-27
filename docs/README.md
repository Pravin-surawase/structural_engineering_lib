# Docs Index (Start Here)

If this folder feels “too big”, you’re right — most people only need a handful of docs. This page tells you which ones matter for which audience.
**Current version:** v0.9.4

## Quick CLI Reference (v0.9.4+)

```bash
python -m structural_lib design input.csv -o results.json
python -m structural_lib bbs results.json -o schedule.csv
python -m structural_lib dxf results.json -o drawings.dxf
python -m structural_lib job job.json -o ./output
```
For VS Code AI-agent work, start with:
- [AI_CONTEXT_PACK.md](AI_CONTEXT_PACK.md)

---

## For Most Users (recommended reading order)

1) **Quick start (Python):** [getting-started/python-quickstart.md](getting-started/python-quickstart.md)
2) **Excel usage tutorial:** [getting-started/excel-tutorial.md](getting-started/excel-tutorial.md)
3) **Full API surface:** [reference/api.md](reference/api.md)
4) **IS 456 formula cheat sheet:** [reference/is456-formulas.md](reference/is456-formulas.md)
5) **Problems & fixes:** [reference/troubleshooting.md](reference/troubleshooting.md)

---

## For Beginners (more explanation, slower pace)

- [getting-started/beginners-guide.md](getting-started/beginners-guide.md) (covers both Python + Excel/VBA)

---

## For Contributors / Maintainers

- Architecture & layering: [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)
- Consolidated architecture/data flow: [DEEP_PROJECT_MAP.md](DEEP_PROJECT_MAP.md)
- Testing strategy & CI setup: [contributing/testing-strategy.md](contributing/testing-strategy.md)
- VBA testing guide: [contributing/vba-testing-guide.md](contributing/vba-testing-guide.md)
- Development practices: [contributing/development-guide.md](contributing/development-guide.md)
- VBA side specifics: [contributing/vba-guide.md](contributing/vba-guide.md)
- Packaging the add-in (`.xlam`): [contributing/excel-addin-guide.md](contributing/excel-addin-guide.md)
- Common engineering/coding traps: [reference/known-pitfalls.md](reference/known-pitfalls.md)
- Git workflow rules: [_internal/GIT_GOVERNANCE.md](_internal/GIT_GOVERNANCE.md)

---

## Planning / Research (roadmaps, “what’s next”)

- What to do next this session: [NEXT_SESSION_BRIEF.md](NEXT_SESSION_BRIEF.md)
- v0.8 implementation playbook: [v0.8_EXECUTION_CHECKLIST.md](v0.8_EXECUTION_CHECKLIST.md)
- Task board (canonical backlog): [TASKS.md](TASKS.md)
- v0.8+ research log: [RESEARCH_AI_ENHANCEMENTS.md](RESEARCH_AI_ENHANCEMENTS.md)
- High-level production checklist: [PRODUCTION_ROADMAP.md](PRODUCTION_ROADMAP.md)

---

## Release History

- User-facing change history: root [CHANGELOG.md](../CHANGELOG.md)
- Append-only release ledger (locked entries): [RELEASES.md](RELEASES.md)

---

## Internal (multi-agent workflow)

These are mainly for the AI-agent workflow you’re using to build the repo:
- [_internal/AGENT_WORKFLOW.md](_internal/AGENT_WORKFLOW.md)
- Role prompts: see [../agents/README.md](../agents/README.md)
