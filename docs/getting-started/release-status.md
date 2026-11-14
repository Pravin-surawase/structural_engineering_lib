---
owner: Main Agent
status: active
last_updated: 2026-11-14
doc_type: guide
complexity: beginner
tags: [release, installation, external-user]
---

# Current Release

The current published package is **StructLib 0.29.1**. It includes the
two beam shear fixes from #1080. The package rejects nonpositive support
distances and reports the derived steel percentage and its source when
it exceeds the supported range.
The [publication receipt](releases.md#v0291-published-and-verified) records
same-byte TestPyPI/PyPI/GitHub delivery, public hashes and a clean external install.
Later development commits are unreleased and do not replace those public bytes.

- [PyPI package and available versions](https://pypi.org/project/structural-lib-is456/)
- [GitHub release](https://github.com/Pravin-surawase/structural_engineering_lib/releases/latest)
- [Exact publication receipt](releases.md)
- [Changelog](https://github.com/Pravin-surawase/structural_engineering_lib/blob/main/CHANGELOG.md)

## Install the exact release

StructLib 0.29.1 requires Python 3.11 or newer.

```bash
python3 -m pip install "structural-lib-is456==0.29.1"
python3 -m structural_lib install-preflight
```

The preflight should show:

- `structural_lib: 0.29.1`
- the interpreter you intended to use
- a package origin inside that environment's `site-packages`
- the installed/not-installed state of optional extras.

## What “normal release” means

`0.29.1` is a final PEP 440 version. An ordinary
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
