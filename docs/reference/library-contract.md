---
owner: Main Agent
status: active
last_updated: 2026-10-29
doc_type: reference
complexity: intermediate
tags: [api, compatibility, support]
---

# Library Contract

**Type:** Reference
**Audience:** Users and integrators
**Status:** Active
**Importance:** High
**Last Updated:** 2026-10-29

The maintained compatibility policy is [API Stability and Classification](api-stability.md).
Use [Which API should I use?](api-levels.md) to choose an entrypoint and the
[machine-readable classification](api-classification.json) and
[compatibility ledger](api-compatibility-ledger.json) to inspect the exact public
surface. This page routes to those owners rather than defining a second policy.

## Scope and support

The library includes multiple declared IS 456 family workflows. The
[family cookbook](../cookbook/python/family-facades.md) records their consumer
journeys and supported, advanced or held scope. It is not beam-only, and a
callable operation is not evidence of whole-standard or complete-building support.
The wheel contains the Python library and CLI; FastAPI and React are separate
source/application surfaces. Follow the support class of the chosen operation.

## Versioning and compatibility

A normal final package version and Beta development maturity can coexist.
The project remains pre-1.0: no exported Python symbol currently has a
post-1.0 stable-API commitment. Exact release pins provide reproducibility,
not professional approval. Current source may include unreleased corrections;
source identity and a published wheel are different artifacts. Publication
needs the [current release process](../getting-started/releases.md#current-release-process-29-october-2026)
and its exact candidate evidence and per-release owner authorization.

`structural_lib.api` and root-module stubs retain their documented compatibility
role. Do not treat an old v1 aspiration or re-export as a frozen public contract,
remove a retained alias without its disposition, or place new implementation in
a compatibility stub. New callers use the promoted typed facade for their task.

## Result contract

Invalid input is rejected before design. An admitted engineering result may be
`PASS`, `FAIL` or `HOLD`; read its reasons, provenance, completeness, freshness
and approval fields. A known unavailable utilization is `null` plus an explicit
reason in transport, not a zero or passing check. Preserve that meaning when
saving, composing or displaying results. A passing software test, supported-case
recipe or normal package release does not grant qualified engineering,
professional, construction-use or native-host acceptance.

See the [API reference](api.md) for concrete parameters, units, result schemas,
limitations and existing error identities. Review compatibility at those
maintained owners before changing a caller.
