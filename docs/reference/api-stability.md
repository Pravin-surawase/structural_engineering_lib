---
owner: Main Agent
status: active
last_updated: 2026-08-17
doc_type: reference
complexity: intermediate
tags: [api, alpha, compatibility]
---

# API Stability and Classification

**Type:** Reference
**Audience:** Developers
**Status:** Alpha Preview
**Importance:** High
**Version:** 0.23.1a1
**Last Updated:** 2026-08-17

StructLib is a pre-1.0 Alpha. No exported Python symbol currently carries a
post-1.0 stable compatibility promise, and passing software tests do not imply
complete IS 456 coverage, qualified structural review, or professional
approval.

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
| `stable` | Reserved for a separately approved compatibility commitment; none exist in this Alpha. |
| `preview` | Deliberately exported and documented, but may change before 1.0. |
| `compatibility` | Retained migration facade; new callers should use the recommended facade. |
| `internal` | No public compatibility promise. |

CI regenerates the registry from the installed candidate and fails when a
declared export, public-looking callable, facade classification, or package
version changes without an intentional registry update.

## Compatibility policy

Within the Alpha channel, changes remain surgical and documented. Confirmed
unsafe behavior is corrected even if permissive callers used it: a
compatibility route may map known aliases, but it may not fill missing
structural inputs, hide import loss, or convert missing status to PASS.

Use exact Alpha pins for reproducibility:

```bash
python3 -m pip install "structural-lib-is456===0.23.1a1"
python3 -c "import structural_lib; print(structural_lib.__version__, structural_lib.__file__)"
```

See [Which API should I use?](api-levels.md), the [deprecation
policy](deprecation-policy.md), and the [release policy](../getting-started/releases.md).
