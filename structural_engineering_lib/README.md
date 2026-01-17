# IS 456 RC Beam Design Library

<div align="center">

> ⚠️ **Work in Progress**: This project is under active development.
> See [TASKS.md](docs/TASKS.md) for roadmap and [next-session-brief.md](docs/planning/next-session-brief.md) for current status.

[![PyPI version](https://img.shields.io/pypi/v/structural-lib-is456.svg)](https://pypi.org/project/structural-lib-is456/)
[![Python tests](https://github.com/Pravin-surawase/structural_engineering_lib/actions/workflows/python-tests.yml/badge.svg)](https://github.com/Pravin-surawase/structural_engineering_lib/actions/workflows/python-tests.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**Professional-grade IS 456 beam design library with contract-tested APIs, comprehensive validation, and production-ready reliability. Run ETABS beam exports through IS 456 checks/design and get compliant rebar + DXF + schedules in minutes.**

## Quick Links

📚 [Documentation](docs/README.md) • 🚀 [Quick Start](#quick-start) • 💡 [Examples](Python/examples/) • 🔧 [API Reference](docs/reference/api.md) • 📊 [Insights Guide](docs/getting-started/insights-guide.md) • 🤖 [AI Summary](llms.txt)

> **🤖 For GitHub Copilot Users:** See [copilot quick start](docs/getting-started/copilot-quick-start.md) to prevent terminal lockup issues

</div>

---

## At a glance

- **Scope:** Professional-grade IS 456 RC beam design library (Python + VBA) with multi-code foundation
- **Quality:** Contract-tested APIs, 2430 tests, 86% coverage, comprehensive validation utilities, 103 automation scripts
- **Outputs:** Deterministic, auditable `results.json`, `schedule.csv`, `drawings.dxf`, HTML reports
- **Automation:** Batch-ready CLI + public API wrappers + unified agent onboarding (90% faster workflow)
- **Smart Insights:** Cost optimization, design suggestions, comparison tools, sensitivity analysis, constructability scoring
- **Documentation:** 870 validated internal links, zero orphan files, semantic folder structure with CI enforcement

---

## ⚠️ Engineering Disclaimer

> **CRITICAL: This library is a DESIGN AID, not a substitute for professional engineering judgment.**

This software is intended to assist qualified structural engineers with IS 456:2000 RC beam design calculations. By using this library, you acknowledge:

1. **Professional Responsibility:** All designs MUST be reviewed and certified by a licensed Professional Engineer (PE/SE) or equivalent authority in your jurisdiction before construction.

2. **No Liability:** The authors accept NO responsibility for structural failures, property damage, injuries, or deaths resulting from the use of this software. See [LICENSE_ENGINEERING.md](LICENSE_ENGINEERING.md) for full terms.

3. **Verification Required:** Independent hand calculations or verified commercial software should confirm critical designs. See [verification checklist](docs/legal/verification-checklist.md).

4. **Regional Compliance:** Users are responsible for ensuring compliance with local building codes, amendments to IS 456, and site-specific requirements.

**For guidance on professional certification:** [Certification Template](docs/legal/certification-template.md)

---

## Features

### Core Capabilities
- **Design & Compliance:** Flexure, shear, serviceability (deflection Level A+B, crack width) per IS 456:2000
- **Detailing:** Bar layouts, stirrup configuration, development/lap lengths per IS 13920
- **Bar Bending Schedule:** IS 2502-compliant CSV/JSON with weights, cut lengths, bar marks
- **DXF Export:** CAD-ready reinforcement drawings with title blocks and annotations
- **Batch Processing:** CSV/JSON job runner for 100+ beams, critical set reports, HTML summaries

### Advisory Tools (v0.13.0+) & Smart Library (v0.15.0)
- **Quick Precheck:** Heuristic validation (deflection risk, width adequacy, steel estimates) in <1ms
- **Sensitivity Analysis:** Identify critical parameters (depth, width, fck) with normalized coefficients
- **Constructability Scoring:** 0-100 scale based on bar spacing, stirrup spacing, layer count, standard sizes
- **Cost Optimization:** Material + labor cost calculation with design alternative comparison (v0.13.0+)
- **Design Suggestions:** 17 expert rules across 6 categories with confidence scoring (v0.13.0+)
- **Smart Dashboard:** Unified analysis combining cost, suggestions, sensitivity, and constructability (v0.15.0)
- **Comparison Tools:** Multi-design comparison with Pareto frontier and cost-aware sensitivity (v0.15.0)

### Quality & Trust
- **Professional-Grade Foundation:** Contract tests prevent API breaking changes, validation utilities reduce code duplication 30%
- **Comprehensive Testing:** 2430 tests, 86% coverage, 13 performance benchmarks
- **API Stability:** Contract-tested public APIs with deprecation policy for safe evolution
- **Error Handling:** 5-layer architecture with structured errors, zero silent failures
- **Type Safety:** Modern PEP 585/604 syntax (`list[X]`, `X | None`), stricter mypy checks
- **Deterministic:** Same input → same output (JSON/CSV/DXF) across runs
- **Traceable:** IS 456 clause references in design formulas
- **Dual Implementation:** Python + VBA with matching I/O

---

## Status

🚀 **Production-Ready Professional Tool (v0.17.5)** — Published on PyPI with enterprise-grade quality standards.

**What's new in v0.17.5 (Multi-Objective Optimization + API Validation - 2026-01-14):**
- **NSGA-II Pareto Optimization:** Multi-objective beam optimization with cost/weight/utilization tradeoffs
- **Cost Optimizer UI Enhancements:** Pareto scatter plot + best-by-objective summaries
- **API Signature Validation:** AST-based checks in pre-commit + CI to prevent contract drift
- **Test Coverage:** 13 new tests for multi-objective optimizer and Pareto front sorting

**Previous: v0.17.0 (Professional API + Debug Infrastructure - 2026-01-13):**
- **Professional API Features:** BeamInput dataclasses, report generation, audit trail, testing strategies
- **Debug Infrastructure:** 1-command diagnostics bundle (`collect_diagnostics.py`), API manifest tracking (38 symbols)
- **Documentation System:** Metadata headers on 50+ docs, standardized doc creation workflow
- **Git Workflow:** Enforcement hooks blocking manual git, improved error clarity and recovery
- **Pre-commit Validation:** API manifest check, scripts index check, doc metadata check

**Previous: v0.16.6 (Python 3.11 Baseline - 2026-01-12):**
- **Python 3.11 Baseline:** Minimum Python version raised from 3.9 to 3.11 for faster runtime
- **CI Optimization:** Test matrix reduced from 4 versions to 2 (50% faster CI)
- **Type Hint Modernization:** PEP 604 syntax (`X | None` instead of `Optional[X]`) across all modules

**Previous: v0.16.5 (Developer Experience & Automation - 2026-01-11):**
- **Unified Agent Onboarding:** Single `./scripts/agent_start.sh` command replaces 4-command workflow (90% faster)
- **Folder Structure Governance:** 115 validation errors → 0, CI-enforced folder limits, comprehensive spec
- **Git Workflow Automation:** 90-95% faster commits (45-60s → 5s), 103 automation scripts

**Previous: v0.15.0 (Code Quality Excellence - 2026-01-07):**
- **SPDX License Headers:** All 73 source files with standardized copyright
- **PEP 585/604 Type Modernization:** 398 type hints updated to modern syntax
- **Performance Benchmarks:** 13 comprehensive benchmarks with regression tracking
- **Test Organization:** 2270 tests, 86% coverage, structured into 5 categories

See [CHANGELOG.md](CHANGELOG.md) for full release history.

**Stability note:** While in active development, prefer pinning to a release version (example: `structural-lib-is456==0.17.5`).

## Quick Start

### 1) Install

```bash
# Base install
pip install structural-lib-is456

# With DXF export support (recommended)
pip install "structural-lib-is456[dxf]"

# Optional extras
pip install "structural-lib-is456[report]"     # Jinja2 templates for report rendering
pip install "structural-lib-is456[validation]" # JSON schema validation helpers
pip install "structural-lib-is456[render]"     # DXF render to PNG/PDF (matplotlib)
```

Colab:
```python
%pip install -q "structural-lib-is456[dxf]"
```

> **Naming:** Install `structural-lib-is456` · Import `structural_lib` · CLI `python3 -m structural_lib`

### 2) API in 30 seconds

```bash
python3 - <<'PY'
from structural_lib import flexure
res = flexure.design_singly_reinforced(
    b=300, d=450, d_total=500, mu_knm=150, fck=25, fy=500
)
print(f"Ast required: {res.ast_required:.0f} mm^2 | Status: {'OK' if res.is_safe else res.error_message}")
PY
```

Example output:
```
Ast required: 942 mm^2 | Status: OK
```
Exact Ast (mm²) may vary slightly by version due to rounding/table refinements.

### 3) CLI pipeline (CSV -> detailing -> BBS -> DXF)

Required for design (case-insensitive): `BeamID, Story, b, D, Span, Cover, fck, fy, Mu, Vu`
Optional overrides (used by `detail` / forced detailing): `Ast_req, Asc_req, Stirrup_Dia, Stirrup_Spacing`

PyPI (no clone):
```bash
pip install "structural-lib-is456[dxf]"
python3 -m structural_lib design input.csv -o results.json
python3 -m structural_lib detail results.json -o detailing.json
python3 -m structural_lib bbs results.json -o schedule.csv
python3 -m structural_lib dxf results.json -o drawings.dxf
```

Repo dev (editable install):
```bash
cd Python
python3 -m pip install -e ".[dxf]"

python3 -m structural_lib design examples/sample_beam_design.csv -o results.json
python3 -m structural_lib detail results.json -o detailing.json
python3 -m structural_lib bbs results.json -o schedule.csv
python3 -m structural_lib dxf results.json -o drawings.dxf
```

Optional review outputs:
```bash
python3 -m structural_lib report results.json --format=html -o report/ --batch-threshold 80
```

Optional schema validation:
```bash
python3 -m structural_lib validate results.json
```

Optional insights analysis:
```bash
python3 -m structural_lib design input.csv -o results.json --insights
# Creates: results.json + <output_stem>_insights.json
# Example: -o results.json         -> results_insights.json
# Example: -o results_insights.json -> results_insights_insights.json
# Note: CLI insights currently export precheck + sensitivity + robustness;
# constructability may be null until CLI integration is completed.
```

Design writes per-beam status in `results.json`; failed beams are flagged with `is_safe=false` (plus an error message).

ETABS exports can be normalized into this schema. See `docs/specs/ETABS_integration.md` for the mapping rules.

---

## How it works

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         IS 456 DESIGN PIPELINE                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   CSV/JSON ──► Design ──► Compliance ──► Detailing ──► DXF/Schedule    │
│      │           │            │             │              │            │
│   ETABS      Flexure      Strength      Bar Layout     Drawings        │
│   Import      Shear     Serviceability   Stirrups       BBS            │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**Highlights**
- End-to-end pipeline from input -> design -> detailing -> DXF/BBS
- Governing-case traceability with utilization summaries
- Dual implementation (VBA + Python) with matching inputs/outputs
- Unified CLI for batch automation

## Outputs

| Output | Format | Description |
|--------|--------|-------------|
| Design results | JSON | Strength + serviceability checks per beam/case |
| Detailing output | JSON | Bars/stirrups + Ld/lap from design results |
| Bar bending schedule | CSV | IS 2502 columns with weights and cut lengths |
| DXF drawings | DXF | CAD-ready reinforcement drawings |
| Critical set | CSV/HTML | Sorted utilization table from job outputs |
| Visual reports | HTML/JSON | Report with SVG, sanity heatmap, scorecard |

## Public API surface (stable wrappers)

See `docs/reference/api-stability.md` for stability labels and guarantees.

| Function | Purpose |
|----------|---------|
| `api.validate_job_spec(path)` | Validate job JSON against schema |
| `api.optimize_beam_cost(...)` | Cost optimization with material/labor breakdown (v0.13.0+) |
| `api.smart_analyze_design(...)` | Unified smart dashboard with cost, suggestions, sensitivity, constructability (v0.15.0) |
| `api.validate_design_results(path)` | Validate results JSON against schema |
| `api.compute_detailing(results)` | Detailing from design results (bars, stirrups, Ld/lap) |
| `api.compute_bbs(detailing)` | BBS rows from detailing data |
| `api.export_bbs(bbs, path)` | Write BBS to CSV |
| `api.compute_dxf(results)` | DXF drawing data from results |
| `api.compute_report(results_or_job)` | Report data from results/job output |
| `api.compute_critical(job_output)` | Critical set table from job output |

## Trust & Verification

| Aspect | Status |
|--------|--------|
| **Test Coverage** | 2270 tests, 86% overall coverage, 6 modules >90% coverage |
| **Determinism** | Same inputs → identical outputs (JSON/CSV/DXF) across runs |
| **Units** | Explicit: mm, N/mm², kN, kN·m — converted at layer boundaries |
| **Code Quality** | 0 ruff errors, contract-tested APIs, modern type hints (PEP 585/604) |
| **Clause Traceability** | Core design formulas reference IS 456 clause/table |
| **Verification Pack** | Benchmark examples in `Python/examples/` + insights verification pack (10 cases) |
| **Performance** | Quick precheck: <1ms, Full design: ~200-500ms/beam, Batch 100 beams: <1 min |

## Who it helps

- Consultants running 100+ beams from ETABS exports
- Detailers generating DXF + schedules quickly
- Students verifying hand calculations and code limits

## Scope / Non-goals

- ✅ Beam design and detailing per IS 456
- ✅ Batch automation (CSV/JSON -> outputs)
- ❌ Not a full building design tool (columns, slabs, foundations out of scope)
- ❌ Not a replacement for engineer judgment

## VBA usage (Excel)

Import `.bas` files from `VBA/Modules/` or use the add-in in `Excel/StructEngLib.xlam`.

```vba
Sub DesignBeam()
    Dim result As Variant
    result = IS456_Design_Rectangular(300, 450, 50, 500, 150, 25, 415)
    If result(0) = "OK" Then
        Debug.Print "Ast required: " & result(1) & " mm^2"
    End If
End Sub
```

More in `VBA/Examples/Example_Usage.bas`.

## Batch job runner (JSON)

For automated pipelines, use the JSON job schema:

```bash
cat > job.json <<'JSON'
{
  "schema_version": 1,
  "code": "IS456",
  "units": "IS456",
  "job_id": "demo-001",
  "beam": {
    "b_mm": 230,
    "D_mm": 500,
    "d_mm": 450,
    "fck_nmm2": 25,
    "fy_nmm2": 500
  },
  "cases": [
    {"case_id": "ULS-1", "mu_knm": 120, "vu_kn": 90}
  ]
}
JSON

python3 -m structural_lib job job.json -o ./out_demo
python3 -m structural_lib critical ./out_demo --top 10 --format=csv -o critical.csv
python3 -m structural_lib report ./out_demo --format=html -o report.html
```

## Troubleshooting (quick fixes)

- CLI not found: use `python3 -m structural_lib --help` to avoid PATH issues
- Wrong Python env: prefer `.venv/bin/python` or `python3 -m pip`
- DXF export fails: install optional dependency with `pip install "structural-lib-is456[dxf]"`
- Schema errors: run `python3 -m structural_lib validate results.json`

## Documentation

**Getting Started:**
- [Beginner's Guide](docs/getting-started/beginners-guide.md) - Start here for first-time users
- [Python Quickstart](docs/getting-started/python-quickstart.md) - API usage examples
- [Insights Guide](docs/getting-started/insights-guide.md) - Advisory insights (precheck, sensitivity, constructability)

**For Developers (Building on the Platform):**
- [Platform Guide](docs/developers/platform-guide.md) - Design your first beam in 15 minutes, integration patterns, best practices
- [Integration Examples](docs/developers/integration-examples.md) - PDF reports, REST APIs, ETABS batch processing
- [Extension Guide](docs/developers/extension-guide.md) - Add custom features without modifying core
- [API Stability Policy](docs/developers/api-stability.md) - Versioning, breaking changes, migration guides

**Reference:**
- [CLI Reference](docs/cookbook/cli-reference.md) - All CLI commands
- [API Reference](docs/reference/api.md) - Function signatures and examples
- [Insights API Reference](docs/reference/insights-api.md) - Insights module technical reference
- [API Stability](docs/reference/api-stability.md) - Stability labels and versioning
- [Known Pitfalls](docs/reference/known-pitfalls.md) - Common issues and solutions

**Excel/VBA:**
- [Excel Quickstart](docs/getting-started/excel-quickstart.md)
- [Excel Tutorial](docs/getting-started/excel-tutorial.md)

**Verification:**
- [Validation Pack](docs/verification/validation-pack.md) - IS 456/SP:16 benchmark cases
- [Insights Verification Pack](docs/verification/insights-verification-pack.md) - Insights module regression tests

**Index:** [docs/README.md](docs/README.md) - Complete documentation index

## Community

- Contributing: `CONTRIBUTING.md`
- Support: `.github/SUPPORT.md`
- Security: `.github/SECURITY.md`

## 📊 Usage Statistics & Feedback

### PyPI Downloads
[![PyPI Downloads](https://img.shields.io/pypi/dm/structural-lib-is456)](https://pypistats.org/packages/structural-lib-is456)
[![PyPI Total](https://img.shields.io/pypi/pyversions/structural-lib-is456)](https://pypi.org/project/structural-lib-is456/)

View detailed download statistics: [pypistats.org/packages/structural-lib-is456](https://pypistats.org/packages/structural-lib-is456)

### Report Issues & Request Features
- [🐛 Report a Bug](https://github.com/Pravin-surawase/structural_engineering_lib/issues/new?template=bug_report.yml)
- [✨ Request a Feature](https://github.com/Pravin-surawase/structural_engineering_lib/issues/new?template=feature_request.yml)
- [❓ Ask a Question](https://github.com/Pravin-surawase/structural_engineering_lib/issues/new?template=support.yml)
- [💬 Discussions](https://github.com/Pravin-surawase/structural_engineering_lib/discussions)

## Developer setup

### For AI Agents (Automated Workflow)

**⚡ Tier-0 Entrypoints — Start Here (3 commands only):**

| Command | When to Use | Time |
|---------|-------------|------|
| `./scripts/agent_start.sh --quick` | **Session start** | 6s |
| `./scripts/ai_commit.sh "message"` | **Every commit** | 5s |
| `./scripts/git_ops.sh --status` | **When unsure** | 1s |

> **THE ONE RULE:** Never use manual git commands. Always use `ai_commit.sh`.

**Session Workflow:**
```bash
./scripts/agent_start.sh --quick   # Start session
# ... make changes ...
./scripts/ai_commit.sh "feat: add feature"  # Commit
./scripts/git_ops.sh --status      # If unsure, get guidance
```

**Benefits:** 90-95% faster commits, 97.5% fewer errors, automated recovery

**Documentation Hub:**
- [Master Guide](docs/agents/guides/agent-workflow-master-guide.md) - Complete agent workflow
- [Quick Reference](docs/agents/guides/agent-quick-reference.md) - Essential commands
- [Git Automation](docs/git-automation/README.md) - Scripts & troubleshooting

**Git Hook Enforcement:**
- Hooks block manual `git commit/push` - use `./scripts/ai_commit.sh` instead
- Auto-installed by `./scripts/agent_start.sh`
- Check health: `./scripts/git_automation_health.sh`

### Manual Development

| Task | Command | Where |
| --- | --- | --- |
| Install dev deps | `cd Python && python3 -m pip install -e ".[dev]"` (includes Hypothesis) | repo root |
| Install hooks | `pre-commit install` | repo root |
| Install git hooks | `./scripts/install_git_hooks.sh` | repo root |
| Run tests | `cd Python && python3 -m pytest` | repo root |
| Run benchmarks | `cd Python && python3 -m pytest --benchmark-only` | repo root |
| Format check | `cd Python && python3 -m black --check .` | repo root |
| Lint check | `cd Python && python3 -m ruff check .` | repo root |
| Type check | `cd Python && python3 -m mypy` | repo root |
| Coverage report | `cd Python && python3 -m pytest --cov --cov-report=html` | repo root |
| Local CI check | `./scripts/ci_local.sh` | repo root |

## Directory structure

```
structural_engineering_lib/
├── VBA/           # VBA modules + tests
├── Python/        # Python package + tests + examples
├── Excel/         # Excel add-in and workbooks
├── scripts/       # Release and CI tooling
├── docs/          # Documentation
└── README.md
```

## License

MIT License — Free to use, modify, and distribute.

## References

- IS 456:2000 — Plain and Reinforced Concrete — Code of Practice
- SP:16-1980 — Design Aids for Reinforced Concrete to IS 456
- IS 13920:2016 — Ductile Design and Detailing of RC Structures

## Author

Pravin Surawase (GitHub: https://github.com/Pravin-surawase)
