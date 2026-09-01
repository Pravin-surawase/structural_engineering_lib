---
owner: Main Agent
status: active
last_updated: 2026-08-17
doc_type: reference
complexity: intermediate
tags: [api, result, status, identity, transport]
---

# Canonical Result and Transport Contract

The reference beam journey uses three small, versioned contracts. They prevent
Python, CLI, workflow, REST, and React transports from changing the engineering
meaning.

## 1. Effective depth

Supply exactly one of:

- explicit `d_mm`; or
- `EffectiveDepthBasisV1(clear_cover_mm, stirrup_diameter_mm,
  tension_bar_diameter_mm)`.

The shared service resolves and returns `effective-depth-basis/v1`. Adapters may
rename fields, but they do not calculate a private depth. The maintained formula
is:

```text
d = D - clear cover - stirrup diameter - tension bar diameter / 2
```

## 2. Structural result

`structural-result-envelope/v2` keeps independent facts separate:

| Axis | Values | Meaning |
|---|---|---|
| Intake | `VALID`, `PARTIAL`, `BLOCKED` | Whether calculation-bearing input was accounted and accepted |
| Calculation | `NOT_EVALUATED`, `COMPLETED`, `ERROR` | Whether the declared calculation ran successfully |
| Engineering | `NOT_EVALUATED`, `PASS`, `FAIL`, `HOLD` | Bounded software disposition |
| Freshness | `CURRENT`, `STALE` | Whether identity still matches the accepted input/result |
| Review | `QUALIFIED_REVIEW_REQUIRED`, reviewed states | Qualified-review boundary, separate from software status |

The fail-closed `overall_status` preserves `BLOCKED`, `ERROR`, `NOT_EVALUATED`,
`STALE`, `PASS`, `FAIL`, or `HOLD`. A blocked constituent cannot aggregate to
PASS. Qualified review is always explicit and a software PASS is not professional
approval.

Each envelope may carry stable issues and `ResultIdentityV1` with contract,
library, normalized-input, calculation, and artifact identities.

## 3. HTTP transport problem

HTTP acceptance is not an engineering result:

- outer `success: true` means the operation returned `data`;
- `data.result_envelope.engineering_status` contains engineering truth;
- outer `success: false` uses `structural-problem/v1` and means the requested
  operation was rejected or failed.

Thus HTTP 200 with outer success and nested engineering `FAIL` is correct and
unambiguous.

The supplied-beam WebSocket path validates the exact shared V2 request and emits
one terminal `check_result` or `beam-supplied-check-error/v2`. Its
[machine-readable exchange schema](beam-supplied-check-websocket-v2.schema.json)
is regenerated with the OpenAPI snapshot. A payload without
`structural-result-envelope/v2` remains fail-closed and is presented by the
React client as `HOLD`.

## Artifact boundary

The wheel ships the Python API and CLI. FastAPI and React are exact-head
application surfaces, not wheel contents; checked-in development clients are
repository artifacts. Wheel evidence therefore runs source-free Python/CLI,
while application evidence proves that the exact-head app imports that installed
wheel.
