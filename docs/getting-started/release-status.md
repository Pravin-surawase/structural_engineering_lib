---
owner: Main Agent
status: active
last_updated: 2026-11-22
doc_type: guide
complexity: beginner
tags: [release, installation, external-user]
---

# Current Release

The current published package is **StructLib 0.31.1**. It was published on
22 November 2026. It corrects how continuous one-way slab checks account for
strip width in per-metre moment, required steel and shear results. The
[public install receipt](https://github.com/Pravin-surawase/structural_engineering_lib/releases/download/v0.31.1/public-install-verification.json)
records the artifact hashes and a clean install from PyPI.

- [PyPI package for 0.31.1](https://pypi.org/project/structural-lib-is456/0.31.1/)
- [GitHub release for 0.31.1](https://github.com/Pravin-surawase/structural_engineering_lib/releases/tag/v0.31.1)
- [Release ledger](releases.md)
- [Changelog](https://github.com/Pravin-surawase/structural_engineering_lib/blob/v0.31.1/CHANGELOG.md)

## Install the exact release

StructLib 0.31.1 requires Python 3.11 or newer.

```bash
python3 -m pip install "structural-lib-is456==0.31.1"
python3 -m structural_lib install-preflight
```

The preflight should show:

- `structural_lib: 0.31.1`
- the interpreter you intended to use
- a package origin inside that environment's `site-packages`
- the installed/not-installed state of optional extras.

## Rerun affected continuous slab checks

Rerun 0.31.0 continuous one-way slab checks that used a strip width other than
1,000 mm or whose width you cannot confirm. This applies to built-in and
supplied coefficients. Prioritize results marked `PASS` for narrower strips.
Review the corrected results and refresh any affected reports or exports.
[Slab rerun guide and example](../cookbook/python/slab-continuous-one-way.md#rerun-affected-0310-results)

## Upgrade existing Generic CSV files

Since 0.31.0, strict Generic CSV import requires a finite, positive span for each beam.
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

`0.31.1` is a final PEP 440 version. An ordinary
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
