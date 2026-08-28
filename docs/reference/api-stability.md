---
owner: Main Agent
status: active
last_updated: 2026-08-24
doc_type: reference
complexity: intermediate
tags: [api, beta, compatibility]
---

# API Stability and Classification

**Type:** Reference
**Audience:** Developers
**Status:** Beta Maturity / Normal Software Release
**Importance:** High
**Version:** 0.24.0
**Last Updated:** 2026-08-24

StructLib is a pre-1.0 Beta-maturity project distributed under a normal final
package version. No exported Python symbol currently carries a post-1.0 stable
compatibility promise, and passing software tests do not imply complete IS 456
coverage, qualified structural review, or professional approval.

## Machine-readable classification

The maintained [API classification registry](api-classification.json) records
every symbol on these surfaces:

- `structural_lib`: recommended root facade; declared exports are `preview`;
- `structural_lib.services.api`: recommended service facade for explicit
  workflows; declared exports are `preview`;
- `structural_lib.api`: retained delegating facade; declared exports are
  `compatibility`;
- any public-looking callable present on those modules but absent from
  `__all__`: `internal` and unsupported as a dependency.

The four classifications mean:

| Class | Current promise |
|---|---|
| `stable` | Reserved for a separately approved compatibility commitment; none exist in this pre-1.0 release. |
| `preview` | Deliberately exported and documented, but may change before 1.0. |
| `compatibility` | Retained migration facade; new callers should use the recommended facade. |
| `internal` | No public compatibility promise. |

Each tracked symbol also has one claim disposition:

| Disposition | Meaning |
|---|---|
| `canonical` | Small capability-bound task API; currently the reference beam journey |
| `advanced` | Maintained specialist/capability tool outside the small task API |
| `compatibility` | Retained public migration surface without a canonical-task claim |
| `hold` | Callable preview whose broader advertised use is blocked by a named gate |
| `internal` | Undeclared implementation detail |

Artifact claims are separate. The wheel ships the `structural_lib` Python API and
CLI. `fastapi_app` and `react_app` are exact-head application surfaces and are not
inside the wheel. The checked-in development clients under `clients/` are also
repository artifacts, not wheel contents.

CI regenerates the registry from the installed candidate and fails when a
declared export, public-looking callable, facade classification, or package
version changes without an intentional registry update.

The maintained [compatibility ledger](api-compatibility-ledger.json) separately
records canonical object ownership, identity/signature proof, retained root
stubs, `api_hub`, maintained callers, P5 held compatibility, and deletion
authorization. Its projection total must reconcile exactly with this registry;
an ambiguous maintained caller fails the generator check. The checked-in ledger
uses a lossless column-dictionary JSON encoding to retain every record within
the repository's small-file boundary.

## Compatibility policy

Within the pre-1.0 release series, changes remain surgical and documented. Confirmed
unsafe behavior is corrected even if permissive callers used it: a
compatibility route may map known aliases, but it may not fill missing
structural inputs, hide import loss, or convert missing status to PASS.
An identity-only public facade is not deprecated just because it re-exports an
object. Deprecation requires a real replacement and an owner-approved removal
schedule; held compatibility may instead carry explicit limitation metadata
with no warning or removal version.

Use exact release pins for reproducibility:

```bash
python3 -m pip install "structural-lib-is456==0.24.0"
python3 -c "import structural_lib; print(structural_lib.__version__, structural_lib.__file__)"
```

See [Which API should I use?](api-levels.md), the [P7 migration
guide](../migration/lib-pro-007-p7-compatibility-convergence.md), the
[deprecation policy](deprecation-policy.md), and the [release
policy](../getting-started/releases.md).
