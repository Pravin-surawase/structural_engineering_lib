---
owner: Main Agent
status: active
last_updated: 2026-10-29
doc_type: guide
complexity: intermediate
tags: [architecture, reuse, adapters]
---

# Code Reuse and Library Structure

**Type:** Guide
**Audience:** Developers
**Status:** Active
**Importance:** High
**Last Updated:** 2026-10-29

This guide explains reuse at the current owners. [AGENTS.md](../../AGENTS.md)
and [Agent Coding Standards](../contributing/agent-coding-standards.md) govern
execution and implementation. The former Streamlit-to-React migration plan and
three-layer module inventory are historical; do not use them for new work.

## Core principle

Keep one implementation of each engineering outcome. Search the maintained
code and its real callers before adding a wrapper or model. Reuse a typed
producer's loader/builder and result semantics instead of reconstructing a
partial dictionary or filling missing engineering facts with defaults.

## Current layers

| Owner | Reusable responsibility |
| --- | --- |
| `Python/structural_lib/core/` | Types, contracts and explicit evidence/result state |
| `Python/structural_lib/codes/is456/` | Pure, unit-explicit IS 456 calculations |
| `Python/structural_lib/services/` | Orchestration, strict admission, adapters, exports and serialization |
| `fastapi_app/`, `react_app/` | HTTP, files and user interaction using the maintained services |

Dependencies point inward. A rendering or HTTP dependency cannot be imported
into Core/code calculations. Root compatibility modules re-export their owners;
they are not places for a second implementation. Use [API levels](../reference/api-levels.md)
and the [classification registry](../reference/api-classification.json) to
select a consumer API, rather than exposing every helper through `api.py`.

## Reuse by outcome

Use the existing CSV adapter and strict CLI input contract for CSV intake;
`useCSVFileImport` connects the React caller. Use the existing beam geometry
service and `useBeamGeometry` for 3D data. Use the maintained effective-depth
binding for strength-to-detailing composition. Use domain-owned transport to
retain failed/unavailable ratios through JSON, reports and HTTP.

Services may perform I/O at their declared boundary; calculations must stay
independent of the host. Keep physical reinforcement, source/case identity,
units and exclusions when composing operations. Requested steel area does not
replace a physical layout or bar schedule. An optional renderer is an explicit
extra, and missing renderer support does not grant permission to fabricate an
output or a passing status.

## Verification and change scope

Trace a confirmed failure to its maintained owner and repair that cause.
Exercise the actual producer/consumer path, preserve compatibility exceptions,
and inspect affected rendered files. Freeze the complete intended batch before
its routine verification and required hosted PR checks. Follow the canonical
coding guide for source-bound commands and [the native Git workflow](../git-automation/git-workflow-single-source.md)
for delivery. Avoid unrelated migrations, public signature changes or broad
suite repetitions merely because a shared folder changed.
