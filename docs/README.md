# Docs Index (Start Here)

> **For AI Agents:** This index uses semantic metadata to help you find the right doc quickly.
> Look at the **Type** and **Complexity** columns to decide what to read.

---

## 📋 Quick Navigation (Semantic Index)

### 🚀 Start Here (by role)

| Role | Start With | Type | Complexity | Description |
|------|-----------|------|------------|-------------|
| **AI Agent (new)** | [agent-bootstrap.md](getting-started/agent-bootstrap.md) | guide | beginner | 60-second onboarding checklist |
| **AI Agent (working)** | [agent-quick-reference.md](agents/guides/agent-quick-reference.md) | reference | intermediate | Commands, scripts, workflows |
| **AI Agent (coding)** | [ai-agent-coding-guide.md](guides/ai-agent-coding-guide.md) | guide | intermediate | Coding standards, tests, reviews |
| **Python Developer** | [python-quickstart.md](getting-started/python-quickstart.md) | tutorial | beginner | Install, import, first design |
| **Excel User** | [excel-tutorial.md](getting-started/excel-tutorial.md) | tutorial | beginner | UDF usage, workbook setup |
| **Contributor** | [development-guide.md](contributing/development-guide.md) | guide | intermediate | PR process, code style, tests |
| **Researcher** | [research/README.md](research/README.md) | index | intermediate | Research catalog and findings |

### 📚 By Topic (all docs)

| Topic | Key Docs | Type | Complexity | What You'll Learn |
|-------|---------|------|------------|-------------------|
| **API** | [api.md](reference/api.md) | reference | advanced | Full function signatures, parameters |
| **IS 456 Formulas** | [is456-formulas.md](reference/is456-formulas.md) | reference | intermediate | Clause references, equations |
| **Architecture** | [project-overview.md](architecture/project-overview.md) | guide | intermediate | Layer structure, data flow |
| **Testing** | [testing-strategy.md](contributing/testing-strategy.md) | guide | intermediate | Test categories, coverage, CI |
| **Git Workflow** | [git-automation/README.md](git-automation/README.md) | hub | beginner | Git automation hub, scripts, workflow |
| **Git Workflow (legacy)** | [git-workflow-ai-agents.md](contributing/git-workflow-ai-agents.md) | guide | beginner | Commit, PR, merge rules |
| **Streamlit API Index** | [../streamlit_app/API_INDEX.md](../streamlit_app/API_INDEX.md) | reference | intermediate | Streamlit components/functions |
| **Troubleshooting** | [troubleshooting.md](reference/troubleshooting.md) | reference | beginner | Common errors, fixes |
| **Tasks** | [TASKS.md](TASKS.md) | index | beginner | What to work on next |
| **Session Log** | [SESSION_LOG.md](SESSION_LOG.md) | log | beginner | Recent work history |

---

## 🔍 Document Type Legend

| Type | Icon | Purpose | When to Use |
|------|------|---------|-------------|
| **tutorial** | 📖 | Step-by-step learning | New to a topic |
| **guide** | 📋 | Conceptual understanding | Need context |
| **reference** | 📚 | Lookup information | Know what you need |
| **index** | 🗂️ | Navigate to other docs | Finding related content |
| **log** | 📝 | Historical record | Understanding history |

---

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
- **[agent-bootstrap.md](getting-started/agent-bootstrap.md)** - New agent checklist
- **[AGENT_WORKFLOW_MASTER_GUIDE.md](agents/guides/agent-workflow-master-guide.md)** - Complete automation guide
- **[AGENT_QUICK_REFERENCE.md](agents/guides/agent-quick-reference.md)** - Essential commands
- **[ai-agent-coding-guide.md](guides/ai-agent-coding-guide.md)** - Coding standards and quality gates
- [ai-context-pack.md](getting-started/ai-context-pack.md) - Project context
- [AI summary](../llms.txt) - LLM-friendly summary
- [Handoff Quick Start](contributing/handoff.md) - Session handoff

---

## Documentation Maintenance

Keep indexes and link checks current after doc updates:

```bash
./scripts/generate_all_indexes.sh
.venv/bin/python scripts/generate_docs_index.py --write
.venv/bin/python scripts/check_docs_index.py
.venv/bin/python scripts/check_docs_index_links.py
```

## Canonical Sources Map

Single source per topic. If you see a legacy filename, use the canonical path below.

### Canonical roots (authoritative)

- `README.md`
- `SESSION_LOG.md`
- `TASKS.md`

### Legacy root redirects (docs/ -> canonical)

| Legacy file | Canonical location |
| --- | --- |
| `api-reference.md` | `reference/api.md` |
| `beginners-guide.md` | `getting-started/beginners-guide.md` |
| `current-state-and-goals.md` | `planning/current-state-and-goals.md` |
| `deep-project-map.md` | `architecture/deep-project-map.md` |
| `development-guide.md` | `contributing/development-guide.md` |
| `excel-addin-guide.md` | `contributing/excel-addin-guide.md` |
| `excel-quickstart.md` | `getting-started/excel-quickstart.md` |
| `excel-tutorial.md` | `getting-started/excel-tutorial.md` |
| `getting-started-python.md` | `getting-started/python-quickstart.md` |
| `is456-quick-reference.md` | `reference/is456-formulas.md` |
| `known-pitfalls.md` | `reference/known-pitfalls.md` |
| `mission-and-principles.md` | `architecture/mission-and-principles.md` |
| `next-session-brief.md` | `planning/next-session-brief.md` |
| `production-roadmap.md` | `planning/production-roadmap.md` |
| `project-overview.md` | `architecture/project-overview.md` |
| `research-ai-enhancements.md` | `planning/research-ai-enhancements.md` |
| `research-detailing.md` | `planning/research-detailing.md` |
| `testing-strategy.md` | `contributing/testing-strategy.md` |
| `troubleshooting.md` | `reference/troubleshooting.md` |
| `vba-guide.md` | `contributing/vba-guide.md` |
| `vba-testing-guide.md` | `contributing/vba-testing-guide.md` |
| `verification-examples.md` | `verification/examples.md` |
| `verification-pack.md` | `verification/pack.md` |

### Legacy contributing redirects (docs/contributing -> canonical)

| Legacy file | Canonical location |
| --- | --- |
| `contributing/git-workflow-for-ai-agents.md` | `git-workflow-ai-agents.md` |

### Archived legacy stubs

| Legacy file | Archived location |
| --- | --- |
| `v0.7-requirements.md` | `_archive/v0.7-requirements.md` |
| `v0.8-execution-checklist.md` | `_archive/v0.8-execution-checklist.md` |

---

## For Developers (Building on the Platform)

**Want to integrate this library into your own applications?** Start here:

1. **[Platform Guide](developers/platform-guide.md)** - Design your first beam in 15 minutes
2. **[Integration Examples](developers/integration-examples.md)** - PDF reports, REST APIs, batch processing
3. **[Extension Guide](developers/extension-guide.md)** - Add custom features without modifying core
4. **[API Stability Policy](reference/api-stability.md)** - Versioning, breaking changes, migration guides

**Full developer hub:** [developers/README.md](developers/README.md)

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
.venv/bin/python scripts/dxf_render.py drawings.dxf -o drawings.png
.venv/bin/python scripts/dxf_render.py drawings.dxf -o drawings.pdf --dpi 200
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
- Visual architecture diagrams: [architecture/visual-architecture.md](architecture/visual-architecture.md)
- Pipeline data flow diagrams: [architecture/data-flow-diagrams.md](architecture/data-flow-diagrams.md)
- Module dependency graph: [architecture/dependencies.md](architecture/dependencies.md)
- Library contract (stability promises): [reference/library-contract.md](reference/library-contract.md)
- BBS + DXF contract: [reference/bbs-dxf-contract.md](reference/bbs-dxf-contract.md)
- Testing strategy & CI setup: [contributing/testing-strategy.md](contributing/testing-strategy.md)
- VBA testing guide: [contributing/vba-testing-guide.md](contributing/vba-testing-guide.md)
- Insights verification pack: [verification/insights-verification-pack.md](verification/insights-verification-pack.md)
- Development practices: [contributing/development-guide.md](contributing/development-guide.md)
- **Git workflow for AI agents:** [git-workflow-ai-agents.md](contributing/git-workflow-ai-agents.md) ⚠️
- Background agent guide: [contributing/background-agent-guide.md](contributing/background-agent-guide.md)
- Repo professionalism playbook: [contributing/repo-professionalism.md](contributing/repo-professionalism.md)
- Contributor learning paths: [contributing/learning-paths.md](contributing/learning-paths.md)
- Solo maintainer operating system: [contributing/solo-maintainer-operating-system.md](contributing/solo-maintainer-operating-system.md)
- VBA side specifics: [contributing/vba-guide.md](contributing/vba-guide.md)
- Packaging the add-in (`.xlam`): [contributing/excel-addin-guide.md](contributing/excel-addin-guide.md)
- Common engineering/coding traps: [reference/known-pitfalls.md](reference/known-pitfalls.md)
- Git workflow rules: [_internal/git-governance.md](_internal/git-governance.md)

---

## Planning / Research (roadmaps, “what’s next”)

- What to do next this session: [planning/next-session-brief.md](planning/next-session-brief.md)
- v0.8 implementation playbook: [_archive/2026-01/v0.8-execution-checklist.md](_archive/2026-01/v0.8-execution-checklist.md)
- Task board (canonical backlog): [TASKS.md](TASKS.md)
- v0.8+ research log: [planning/research-ai-enhancements.md](planning/research-ai-enhancements.md)
- Research index: [research/README.md](research/README.md)
- High-level production checklist: [planning/production-roadmap.md](_archive/planning/production-roadmap.md)

---

## Release History

- User-facing change history: root [CHANGELOG.md](../CHANGELOG.md)
- Append-only release ledger (locked entries): [getting-started/releases.md](getting-started/releases.md)

---

## Internal (multi-agent workflow)

These are mainly for the AI-agent workflow you’re using to build the repo:
- [_internal/agent-workflow.md](_internal/agent-workflow.md)
- Role prompts: see [../agents/README.md](../agents/README.md)
