---
owner: Main Agent
status: active
last_updated: 2026-10-29
doc_type: guide
complexity: intermediate
tags: [python, architecture, coding, verification]
---

# Agent Coding Standards

**Type:** Guide
**Audience:** Developers and AI agents
**Status:** Active
**Importance:** Critical
**Last Updated:** 2026-10-29

## Purpose

Use this guide for implementation conventions. [AGENTS.md](../../AGENTS.md)
owns execution, permissions, Git, sessions and architecture. Path-scoped rules
apply alongside it. This guide does not create another approval or release
process. The earlier three-layer/Streamlit migration examples are retired.

## Quick Checklist

Identify the actual checkout, task scope, maintained caller and outcome owner
before editing. Search for the existing implementation. Preserve unrelated
work, explicit engineering inputs, failed results and named later gates.
Complete the agreed implementation and documentation batch, then verify its
outcomes and inspect its essential diff. Use one reviewed PR and its required
hosted checks for the milestone.

## 1. Architecture Rules

| Layer | Owner | Responsibility |
| --- | --- | --- |
| Core types | `Python/structural_lib/core/` | Shared types, contracts and result state; no IS 456 math |
| IS 456 code | `Python/structural_lib/codes/is456/` | Deterministic engineering calculations with explicit units; no I/O |
| Services | `Python/structural_lib/services/` | Orchestration, adapters, producer/consumer composition and serialization |
| UI/IO | `fastapi_app/`, `react_app/` | HTTP/file/user interaction; delegate engineering calculations |

Imports point inward: Core ← IS 456 ← Services ← UI/IO. Never import a service
or UI module into Core or the code calculation layer. React/FastAPI are the
active applications; historical Streamlit paths are not implementation targets.

`Python/structural_lib/api.py` is a compatibility stub. Service implementation
belongs in `services/`; adding code to the stub creates the wrong owner. Use
[API levels](../reference/api-levels.md) to choose a consumer entrypoint and the
[API classification](../reference/api-classification.json) to verify its
support class. Typed `design.is456` family facades are the promoted task routes;
root/service facades and retained compatibility routes have their declared roles.

## 2. File Structure and Reuse

Keep new code at the maintained outcome owner. Reuse adapters, input admission,
detailing bindings, serializers and result envelopes instead of creating a
parallel calculation or silently translating missing facts into defaults.
Search exact symbols and maintained callers with `rg`; discover function
signatures before calling a service API:

```bash
./run.sh find --api design_beam_is456
./scripts/python_runtime.sh scripts/discover_api_signatures.py design_beam_is456
```

Run these commands from the repository root. For topic routing use
`./run.sh context show <area>` with a real area when a concrete question needs
more context. Registries own inventories; do not copy them into new guides.

## 3. Naming Conventions

Use the maintained function's exact parameter names. New promoted parameters
follow the [API design guidelines](../guidelines/api-design-guidelines.md),
including explicit units and declared defaults. Existing compatibility
exceptions require their own disposition; do not rename positional parameters
or remove aliases during an unrelated correction.

Geometry/actions must state their units: mm, N/mm², kN and kNm at the selected
boundary. Preserve sign, load-combination and physical-reinforcement basis.
Conversions belong at an explicit adapter, not inside an unexplained default.

## 4. Type Hints

Annotate maintained inputs, outputs and meaningful unavailable states. A value
that can legitimately be unavailable must not be advertised as always numeric.
Use existing typed models and dataclasses; avoid a second dictionary schema
when an owner already supplies a loader or builder.

## 5. Docstrings

Document required/optional inputs, units, return state, assumptions, exclusions,
source/case provenance and outcome-changing errors. Follow the existing Google
style. Keep illustrative pseudocode clearly labelled; runnable recipes need
all preceding cells, files and optional dependencies declared.

## 6. Error Handling

Separate invalid intake, calculation failure and admitted engineering results.
Canonical invalid intake uses `InputContractError`. A valid result can be
`PASS`, `FAIL` or `HOLD`; inspect its result envelope, completeness, freshness
and approval state. `is_ok` alone cannot establish all of those meanings.

Use maintained error types and issue codes. A failed check with no evaluated
ratio is not zero utilization. Known unavailable ratios serialize as JSON
`null` with `UTILIZATION_NOT_EVALUATED` and the owner-specific reason; unexpected
non-finite values still fail at the transport owner. Preserve failed checks
and reasons through every affected consumer. Do not catch and suppress a root
cause, clamp to PASS or weaken physical effective-depth validation.

## 7. Testing

Choose evidence that can distinguish the corrected main-process outcome from
the original failure. For input/detailing changes, verify strength depth agrees
with the actual bar centroid and retain rejection of mismatches/unverified
layouts. For a transport change, exercise the maintained producer and consumer,
including admitted FAIL/HOLD and invalid intake where affected. For an output
change, inspect the actual generated file and its dimensions/units/status.

All repository commands use the bound runtime from the repository root. For
example, this existing example module has a focused executable test:

```bash
./scripts/python_runtime.sh -m pytest Python/tests/test_public_examples.py -q
```

Replace that selection with the real affected tests for your task. After the
content freezes, run the affected formatter/linter, focused behavior checks and
`./run.sh check`. Broad Python/full checks need a named risk or release reason;
do not duplicate unchanged suites after every edit. Validation is read-only;
formatters are intentional implementation writes completed before final review.
The [terminal rules](../../.github/instructions/terminal-rules.instructions.md)
cover command working directories and fallbacks.

## 8. Import Order and Dependencies

Follow the configured formatter/linter and inward import direction. Keep optional
I/O/rendering dependencies at their boundary and declare the appropriate extra.
Do not import UI packages to make a core calculation work. Do not change runtime
or test-tool dependency ranges as an incidental cleanup.

## 9. Calculation and Output Changes

A changed engineering branch needs its exact code edition/amendment, source/case,
units, assumptions, independent expected result and justified tolerance. Apply
[IS 456 verification](../../.github/skills/is456-verification/SKILL.md) and the
[function quality pipeline](../../.github/skills/function-quality-pipeline/SKILL.md)
when their scope applies. Source/table provenance stays with runtime results and
tests. The existing normalized IS-data source-use permission is already passed;
release authorization remains separate.

## 10. Delivery

Follow the [native Git workflow](../git-automation/git-workflow-single-source.md)
and [token-efficiency policy](../guidelines/ai-token-efficiency.md). One writer
owns shared/generated paths. Reviewers inspect the essential main process;
the named roles do not require additional agents or repeated full suites.
A green software check or merged PR proves only its selected scope. Qualified
engineering acceptance, installed-host evidence and publication retain their
separate gates. Record the root cause, correction and relevant verification in
the PR; keep a handoff only when unfinished work or a real transition needs it.
