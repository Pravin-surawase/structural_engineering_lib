---
owner: Main Agent
status: active
last_updated: 2026-11-18
doc_type: guide
complexity: beginner
tags: [release, installation, external-user]
---

# Current Release

The current published package is **StructLib 0.31.0**. It was published on
18 November 2026. It corrects edited beam cage clearance, torsion receiver
peak moments and one-way slab creep checks, and tightens Generic and ETABS CSV
import. The
[public install receipt](https://github.com/Pravin-surawase/structural_engineering_lib/releases/download/v0.31.0/public-install-verification.json)
records the artifact hashes and a clean install from PyPI.

- [PyPI package for 0.31.0](https://pypi.org/project/structural-lib-is456/0.31.0/)
- [GitHub release for 0.31.0](https://github.com/Pravin-surawase/structural_engineering_lib/releases/tag/v0.31.0)
- [Release ledger](releases.md)
- [Changelog](https://github.com/Pravin-surawase/structural_engineering_lib/blob/v0.31.0/CHANGELOG.md)

## Install the exact release

StructLib 0.31.0 requires Python 3.11 or newer.

```bash
python3 -m pip install "structural-lib-is456==0.31.0"
python3 -m structural_lib install-preflight
```

The preflight should show:

- `structural_lib: 0.31.0`
- the interpreter you intended to use
- a package origin inside that environment's `site-packages`
- the installed/not-installed state of optional extras.

## Upgrade existing Generic CSV files

Strict Generic CSV import now requires a finite, positive span for each beam.
Use one of these column headers in the combined CSV or, for a paired import,
in the geometry CSV.

| Units | Accepted headers | Example for a 4.2 m span |
| --- | --- | --- |
| Millimetres | `span_mm`, `Span (mm)` | `4200` |
| Metres | `Span_m`, `Span (m)` | `4.2` |

The import ledger records metre inputs in millimetres. Existing files without
a span column need the actual span for every beam. A missing, blank or invalid
span blocks import. Earlier versions could assume 5 m when the column was absent.

## What “normal release” means

`0.31.0` is a final PEP 440 version. An ordinary
`pip install structural-lib-is456` can select it on a supported Python version.
The package retains Beta maturity: APIs may change before v1.0 and the supported
engineering scope is case-qualified.

The release includes 15 CLI entry points and 13 canonical family-facade
journeys. Use the [capability contract](../reference/api-levels.md), the
[family facade cookbook](../cookbook/python/family-facades.md), and the
[evidence crosswalk](../verification/is456-library-first-evidence.md) to confirm
the boundary of a proposed workflow.

## Verification and claim boundary

The release process binds the public wheel and source distribution to the
GitHub release and append-only publication receipt. The exact-wheel acceptance
matrix must cover advertised positive and negative software journeys; consult
the ledger for the selected version's completed evidence.

Publication is not:

- complete IS 456 coverage;
- a stable API guarantee;
- qualified structural-engineering review;
- professional, engineering-use, or construction-use approval;
- Windows Excel or ETABS application acceptance.

Review every project's inputs, assumptions, limitations, status, and outputs
independently with a qualified structural engineer.
