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

1) **Quick start (Python):** [GETTING_STARTED_PYTHON.md](GETTING_STARTED_PYTHON.md)
2) **Excel usage tutorial:** [EXCEL_TUTORIAL.md](EXCEL_TUTORIAL.md)
3) **Full API surface:** [API_REFERENCE.md](API_REFERENCE.md)
4) **IS 456 formula cheat sheet:** [IS456_QUICK_REFERENCE.md](IS456_QUICK_REFERENCE.md)
5) **Problems & fixes:** [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

---

## For Beginners (more explanation, slower pace)

- [BEGINNERS_GUIDE.md](BEGINNERS_GUIDE.md) (covers both Python + Excel/VBA)

---

## For Contributors / Maintainers

- Architecture & layering: [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)
- Consolidated architecture/data flow: [DEEP_PROJECT_MAP.md](DEEP_PROJECT_MAP.md)
- Testing strategy & CI setup: [TESTING_STRATEGY.md](TESTING_STRATEGY.md)
- VBA testing guide: [VBA_TESTING_GUIDE.md](VBA_TESTING_GUIDE.md)
- Development practices: [DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md)
- VBA side specifics: [VBA_GUIDE.md](VBA_GUIDE.md)
- Packaging the add-in (`.xlam`): [EXCEL_ADDIN_GUIDE.md](EXCEL_ADDIN_GUIDE.md)
- Common engineering/coding traps: [KNOWN_PITFALLS.md](KNOWN_PITFALLS.md)
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
