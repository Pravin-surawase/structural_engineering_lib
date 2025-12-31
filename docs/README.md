# Docs Index (Start Here)

If this folder feels “too big”, you’re right — most people only need a handful of docs. This page tells you which ones matter for which audience.

> **Version info:** See [TASKS.md](TASKS.md) for current/next release status.

## Quick CLI Reference (v0.11.0+)

```bash
python -m structural_lib design input.csv -o results.json
python -m structural_lib design input.csv -o results.json --insights  # v0.13.0+
python -m structural_lib bbs results.json -o schedule.csv
python -m structural_lib detail results.json -o detailing.json
python -m structural_lib dxf results.json -o drawings.dxf
python -m structural_lib mark-diff --bbs schedule.csv --dxf drawings.dxf
python -m structural_lib job job.json -o ./output
python -m structural_lib validate job.json
python -m structural_lib critical ./output --top 10 --format=csv -o critical.csv
python -m structural_lib report ./output --format=html -o report.html
```
For VS Code AI-agent work, start with:
- [AI_CONTEXT_PACK.md](AI_CONTEXT_PACK.md)
- [AI summary](../llms.txt)
- [Handoff Quick Start](HANDOFF.md)

---

## For Most Users (recommended reading order)

1) **Quick start (Python):** [getting-started/python-quickstart.md](getting-started/python-quickstart.md)
2) **Excel usage tutorial:** [getting-started/excel-tutorial.md](getting-started/excel-tutorial.md)
3) **Full API surface:** [reference/api.md](reference/api.md)
4) **IS 456 formula cheat sheet:** [reference/is456-formulas.md](reference/is456-formulas.md)
5) **Problems & fixes:** [reference/troubleshooting.md](reference/troubleshooting.md)

---

## Visual Outputs (v0.11.0+)

Generate human-readable summaries from job outputs:

```bash
# Critical set table (CSV/HTML)
python -m structural_lib critical ./output --top 10 --format=csv -o critical.csv

# Report summary (HTML/JSON)
python -m structural_lib report ./output --format=html -o report.html
```

Input for both commands is the job output folder created by `python -m structural_lib job`.
The HTML report includes a cross-section SVG, input sanity heatmap, stability scorecard,
and units sentinel.

You can also generate reports from `design_results.json` with batch packaging:
```bash
python -m structural_lib report results.json --format=html -o report/ --batch-threshold 80
```

---

## DXF Rendering (optional)

Render DXF outputs to PNG/PDF for quick sharing:

```bash
python scripts/dxf_render.py drawings.dxf -o drawings.png
python scripts/dxf_render.py drawings.dxf -o drawings.pdf --dpi 200
```

Requires: `pip install "structural-lib-is456[render]"`

---

## For Beginners (more explanation, slower pace)

- [getting-started/beginners-guide.md](getting-started/beginners-guide.md) (covers both Python + Excel/VBA)

---

## Learning Path (beginner-first)

If you want to understand the concepts and the code step by step, start here:
- [learning/README.md](learning/README.md)
- [learning/learning-plan.md](learning/learning-plan.md)
- [learning/concepts-map.md](learning/concepts-map.md)
- [learning/glossary.md](learning/glossary.md)
- [learning/exercises.md](learning/exercises.md)

---

## For Contributors / Maintainers

- Architecture & layering: [architecture/project-overview.md](architecture/project-overview.md)
- Consolidated architecture/data flow: [architecture/deep-project-map.md](architecture/deep-project-map.md)
- Library contract (stability promises): [reference/library-contract.md](reference/library-contract.md)
- BBS + DXF contract: [reference/bbs-dxf-contract.md](reference/bbs-dxf-contract.md)
- Testing strategy & CI setup: [contributing/testing-strategy.md](contributing/testing-strategy.md)
- VBA testing guide: [contributing/vba-testing-guide.md](contributing/vba-testing-guide.md)
- Development practices: [contributing/development-guide.md](contributing/development-guide.md)
- Repo professionalism playbook: [contributing/repo-professionalism.md](contributing/repo-professionalism.md)
- Solo maintainer operating system: [contributing/solo-maintainer-operating-system.md](contributing/solo-maintainer-operating-system.md)
- VBA side specifics: [contributing/vba-guide.md](contributing/vba-guide.md)
- Packaging the add-in (`.xlam`): [contributing/excel-addin-guide.md](contributing/excel-addin-guide.md)
- Common engineering/coding traps: [reference/known-pitfalls.md](reference/known-pitfalls.md)
- Git workflow rules: [_internal/GIT_GOVERNANCE.md](_internal/GIT_GOVERNANCE.md)

---

## Planning / Research (roadmaps, “what’s next”)

- What to do next this session: [planning/next-session-brief.md](planning/next-session-brief.md)
- v0.8 implementation playbook: [v0.8_EXECUTION_CHECKLIST.md](v0.8_EXECUTION_CHECKLIST.md)
- Task board (canonical backlog): [TASKS.md](TASKS.md)
- v0.8+ research log: [planning/research-ai-enhancements.md](planning/research-ai-enhancements.md)
- High-level production checklist: [planning/production-roadmap.md](planning/production-roadmap.md)

---

## Release History

- User-facing change history: root [CHANGELOG.md](../CHANGELOG.md)
- Append-only release ledger (locked entries): [RELEASES.md](RELEASES.md)

---

## Internal (multi-agent workflow)

These are mainly for the AI-agent workflow you’re using to build the repo:
- [_internal/AGENT_WORKFLOW.md](_internal/AGENT_WORKFLOW.md)
- Role prompts: see [../agents/README.md](../agents/README.md)
