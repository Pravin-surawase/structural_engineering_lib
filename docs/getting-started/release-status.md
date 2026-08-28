---
owner: Main Agent
status: active
last_updated: 2026-08-28
doc_type: guide
complexity: beginner
tags: [release, installation, external-user]
---

# Current Release

The current public release is **StructLib 0.24.0**, published on 2026-08-28.

- [PyPI package](https://pypi.org/project/structural-lib-is456/0.24.0/)
- [GitHub release](https://github.com/Pravin-surawase/structural_engineering_lib/releases/tag/v0.24.0)
- [Exact publication receipt](releases.md#v0240-public-normal-software-release-receipt)
- [Changelog](https://github.com/Pravin-surawase/structural_engineering_lib/blob/main/CHANGELOG.md#0240--2026-08-28)

## Install the exact release

StructLib 0.24.0 requires Python 3.11 or newer.

```bash
python3 -m pip install "structural-lib-is456==0.24.0"
python3 -m structural_lib install-preflight
```

The preflight should show:

- `structural_lib: 0.24.0`;
- the interpreter you intended to use;
- a package origin inside that environment's `site-packages`;
- the installed/not-installed state of optional extras.

## What “normal release” means

`0.24.0` is a normal/final PEP 440 version rather than a prerelease-tagged
version, so an ordinary
`pip install structural-lib-is456` selects it on a supported Python version.
The package retains Beta maturity: APIs may change before v1.0 and the supported
engineering scope is case-qualified.

The release includes 15 CLI entry points and 13 canonical family-facade
journeys. Use the [capability contract](../reference/api-levels.md), the
[family facade cookbook](../cookbook/python/family-facades.md), and the
[evidence crosswalk](../verification/is456-library-first-evidence.md) to confirm
the boundary of a proposed workflow.

## Verification and claim boundary

The public wheel and source distribution are bound to the GitHub release and
the append-only publication receipt. Exact-wheel acceptance covered advertised
positive and negative software journeys.

Publication is not:

- complete IS 456 coverage;
- a stable API guarantee;
- qualified structural-engineering review;
- professional, engineering-use, or construction-use approval;
- Windows Excel or ETABS application acceptance.

Review every project's inputs, assumptions, limitations, status, and outputs
independently with a qualified structural engineer.
