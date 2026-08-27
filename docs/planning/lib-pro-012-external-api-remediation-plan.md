---
owner: Main Agent
status: active
last_updated: 2026-08-27
doc_type: spec
complexity: advanced
tags: [external-user, public-api, validation, usability, migration, examples]
---

# LIB-PRO-012 External API Remediation Programme

## 1. Decision and outcome

This is the implementation specification and scope authority for correcting the
external-user findings recorded in
[LIB-PRO-011](../verification/lib-pro-011-external-api-readiness-audit.md).
The audit remains the evidence and reproduction authority; this document owns
the target solution, dependency order, migration policy, acceptance evidence,
and release boundary. The
[LIB-PRO-013 owner sequencing decision](../verification/lib-pro-013-owner-sequencing-decision.json)
starts B0 and pre-authorizes F0 and R0 after their dependency gates pass.

The required work is not one patch. It has four linked outcomes:

1. **Immediate fail-closed safety:** invalid public inputs must stop before any
   calculation, detailing, BBS, report, or optimization result is created.
2. **One external Python contract:** supported member families need a small,
   consistent, explicit-unit request/result journey while legacy functions
   delegate safely through compatibility adapters.
3. **Outsider success:** strict but usable inputs, discoverable enums, grouped
   evidence fields, executable examples, predictable errors, and natural
   design-to-detailing-to-BBS composition.
4. **A gate that follows advertising:** every Python workflow promoted in a
   README, quickstart, cookbook, API guide, or CLI chain must be registered,
   negatively tested, and replayed from the exact wheel.

The current library remains `PARTIAL / ALPHA ONLY`. B0/F0/R0 internal runtime,
contract, compatibility, generated-owner, test, and documentation work is now
authorized. Professional review is deferred to one final integrated-library
step and is not an intermediate gate. No professional or engineering-use claim
exists before that final review.

## 2. Live basis and reconciliation with completed work

| Item | Current planning basis |
|---|---|
| Finding authority | `docs/verification/lib-pro-011-external-api-readiness-audit.md` |
| Audited public artifact | `structural-lib-is456==0.24.0a1` |
| Wheel SHA-256 | `b5e0df7b561e8c715f37c602200eaae2c369ec5dc992eec87110a77c1026201a` |
| Audit source base | `6a4683eb8b21bff77f2991230b4458463e61f419` |
| Plan lane | `codex/lib-pro-012-external-api-remediation-plan` |
| Root public surface | 222 exports, including 100 functions |
| Static validation state | 148 `PROVEN`, 122 `DELEGATED`, 357 `UNPROVEN`, 136 `NOT_APPLICABLE` |
| API status | Alpha/preview; no stable-export promise |
| Programme authority | B0 authorized now; F0 and R0 authorized after their dependency gates; final engineer review deferred until the integrated library is complete |

This programme must reuse, not repeat, the following completed foundations:

- `core/validation.py` already provides finite-real, dimension, material,
  load, cover, span, and reinforcement validation primitives.
- `codes/is456/_validation.py` already provides fail-fast finite/range helpers
  for pure-math functions.
- `ProjectBeamDesignInputV1` already proves that strict, lossless project
  intake can coexist with the legacy public beam API.
- `StructuralResultEnvelopeV2` and `structural-problem/v1` already define the
  orthogonal status and transport-error direction.
- Pydantic v2 and Hypothesis are already package/development dependencies.
- `api-classification.json`, `api-compatibility-ledger.json`, the capability
  authority, and the workflow catalogue already inventory public ownership and
  compatibility. This plan must extend those owners rather than create a third
  API manifest.
- The prior pre-release input-safety programme closed project/CLI import loss,
  result-envelope, release-mode, and exact-wheel control work. It did not make
  every directly callable Python route fail closed or beginner-consistent.

## 3. Root-cause solution map

| Confirmed root cause | System solution | Why a local patch is insufficient |
|---|---|---|
| Route-local validation | One contract layer plus mandatory direct-boundary validation | Fixing only `design_and_detail_beam_is456` leaves design-only, compliance, smart analysis, direct detailing, and BBS unsafe |
| Guard-presence auditing | Declarative field contracts and generated adversarial vectors | A call to a finite validator does not prove sign, domain, relation, identity, enum, collection, or consumer behavior |
| Weak structured inputs | Strict immutable public request models with cross-field validation | Dataclass comparisons do not reject `NaN`; truthiness aliases reinterpret zero and string booleans |
| Mixed signatures | New family-oriented facade plus delegating compatibility wrappers | Renaming individual parameters across 100 functions would preserve discovery overload and cause broad caller churn |
| Evidence-heavy construction | Grouped submodels and thin validated builders | Removing evidence fields would weaken truth; leaving 15–32 flat fields makes first use unnecessarily difficult |
| Mixed errors/results | One public input issue model and existing result envelope | Message-only `ValueError`, raw enum errors, dictionaries, and `is_ok`/`is_safe` variants are hard to catch and serialize consistently |
| Advertised/gated mismatch | Register advertised workflows in the existing generated classification/catalogue | A hand-maintained 21-route list can remain green while promoted compatibility routes fail open |
| Documentation drift | Generate signatures and execute recipes against the built wheel | Static prose can describe obsolete defaults, imports, versions, and result fields without failing CI |

## 4. Frozen architectural decisions

These decisions apply to all packets unless implementation evidence proves a
conflict and this plan is amended before code changes continue.

### D1 — Correct unsafe semantics immediately

Existing advertised functions will reject invalid inputs as soon as their P0
packet lands. Preserving acceptance of negative, non-finite, impossible, or
untraceable inputs is not backward compatibility.

The immediate safety correction does **not** wait for the new facade. Valid
golden calculations must remain numerically unchanged.

### D2 — Use one three-level validation architecture

| Level | Owner | Responsibility |
|---|---|---|
| Public request | strict Pydantic models in a service-contract package | Type, finite value, non-blank identity, enum, collection, simple domain, and cross-field validation; accumulate field-level issues |
| Public service boundary | `services/*_api.py` using shared core validators | Revalidate every directly callable route and translate request/compatibility inputs into one canonical command |
| Pure calculation | `codes/is456/**` fail-fast validators | Defend direct expert calls and enforce code-specific mathematical domains without importing services |

Request validation does not excuse direct calculation validation. The same
declarative contract must drive both where practical; the service layer owns
translation between accumulated public issues and fail-fast calculation
exceptions.

### D3 — Add a curated family facade; do not shrink the root namespace first

The selected long-term beginner namespace is:

```python
from structural_lib.design.is456 import beam
```

`structural_lib.design.is456` is a facade layer only. It may import services,
but contains no formulas or structural derivation. Its supported family
modules are planned as:

- `beam`, `torsion`, `column`;
- `slab`, `wall`, `staircase`, `deep_beam`, `flat_slab`;
- `isolated_footing`, `combined_footing`, `strap_footing`.

Each module exposes a deliberately small vocabulary: request types, validated
input factory/builder, `design` or `check`, typed result types, enums, and
documented downstream helpers. Exhaustive low-level functions remain available
under `codes.is456` and existing compatibility locations.

The first implementation packet must run an import-cycle and wheel-content
spike for this namespace. If it conflicts with packaging, the one allowed
fallback is `structural_lib.members.is456`; implementation must not invent a
third name.

### D4 — Retain existing signatures as delegating compatibility wrappers

The current root functions stay callable during the Alpha migration. Their
signatures are not mechanically renamed in place. They must:

1. validate their existing arguments;
2. build the canonical request/command;
3. delegate to the canonical service owner;
4. adapt the canonical result to the documented compatibility result only when
   needed;
5. carry classification, migration target, and eventual deprecation metadata.

No wrapper may retain a separate calculation path or weaker validation.

### D5 — Keep explicit units in canonical names

Canonical scalar fields retain suffixes such as `_mm`, `_mm2`, `_kn`, `_knm`,
and `_nmm2`. A quantity-library adapter can be considered after the canonical
contract is stable; it is not part of the P0 or first public-facade work.

Legacy `b`, `D`, `d`, `fck`, `fy`, `cover`, and `span` names remain only in
explicit compatibility or low-level expert APIs.

### D6 — Use magnitude actions by default

Canonical member-design actions such as `mu_knm`, `vu_kn`, `tu_knm`,
`Mux_kNm`, and `Muy_kNm` are finite non-negative magnitudes. Signed actions
must use names containing `signed`, include an axis/sign convention, and be
normalized once into the calculation convention.

Zero remains valid where the route contract permits it. The field contract,
not a global rule, owns whether zero is allowed.

### D7 — Separate invalid intake from engineering failure

- Invalid input raises one library-owned `InputContractError` containing one
  or more structured `InputIssueV1` records.
- A valid but inadequate member returns a typed result whose engineering state
  is `FAIL` or `HOLD`.
- A numerical or internal calculation failure is not converted into an intake
  error or a safe-looking result.
- Canonical functions never expose a raw Pydantic or raw enum exception.

### D8 — Reuse the existing result envelope

Canonical family results use `StructuralResultEnvelopeV2` semantics and expose
the same common properties:

- schema and library version;
- member/case/source identity;
- intake, calculation, engineering, and review states;
- typed family payload;
- limitations, assumptions, provenance, and issues;
- `to_dict()` with finite JSON output.

Compatibility properties such as `is_ok` and `is_safe` may delegate to the
engineering state, but they are not the only status representation.

### D9 — Builders reduce ceremony, not evidence

A builder may group fields, list allowed enums, load a validated JSON model,
and produce a strict request. It may not guess topology, restraint, load-case
basis, material grade, effective depth, seismic applicability, or evidence
approval.

Named templates such as `materials.m25_fe500()` are allowed only when the user
explicitly selects them and the request provenance records that selection.
There are no hidden structural defaults on canonical project/member routes.

### D10 — Documentation is executable product surface

Every promoted example has a workflow identifier, minimum package version,
supported case, expected result state, limitations, and an executable Python
file or extractable fenced block. The exact built wheel must run the example
without importing repository source.

### D11 — Minimize Git and session churn without weakening evidence

The packets in Section 10 are logical ownership and acceptance work packages;
they are not automatically separate branches, sessions, commits, pushes, pull
requests, or hosted-check runs. For the repository verification contract, each
Section 15 execution cycle is the agreed bounded delivery packet; Section 15
groups the logical work packages into the smallest safe set of those cycles.

For each execution cycle:

- keep one parent task and one session active through implementation, internal
  review, repair, documentation, and candidate preparation;
- use one task branch, one frozen candidate commit, one normal push/PR, and one
  required hosted-check cycle after all intended writes are complete;
- use internal subphases and focused reproducers for guidance without creating
  routine WIP commits, status-only commits, or PRs merely to mark progress;
- create a local recovery checkpoint only when a real data-loss or long-running
  interruption risk justifies it, and never present that checkpoint as the
  reviewed candidate;
- batch affected focused tests after content freeze, run the quick gate once,
  use normal staged hooks, and run the broad/full matrix only at the cumulative
  boundary required by Section 12;
- after an outcome-changing repair, rerun only invalidated focused evidence and
  the consolidated candidate gate once; and
- retain every required hosted, exact-wheel, release, and professional-review
  control. Efficiency never means bypassing a decisive gate.

Split an execution cycle only when an active candidate overlaps its owners, a
valid engineering result changes without explained evidence, a new source or
dependency decision is required, or the combined change cannot be reviewed as
one coherent user outcome.

## 5. Target external-user experience

### 5.1 Beam reference journey

The beam vertical slice is the reference contract for every later family:

```python
from structural_lib.design.is456 import beam

request = beam.input(
    member_id="B1",
    story="GF",
    case_id="ULS-1",
    span_mm=5000,
    b_mm=300,
    D_mm=550,
    d_mm=500,
    fck_nmm2=25,
    fy_nmm2=500,
    mu_knm=150,
    vu_kn=80,
    d_dash_mm=50,
    asv_mm2=100.53,
    detailing=beam.BeamDetailingOptionsV1(
        standard=beam.DetailingStandard.IS456,
        clear_cover_mm=40,
        tension_bar_diameter_mm=20,
        compression_bar_diameter_mm=16,
        nominal_top_steel_ratio=0.25,
        stirrup_diameter_mm=8,
        stirrup_legs=2,
        stirrup_spacing_support_mm=150,
        stirrup_spacing_mid_mm=200,
    ),
)

result = beam.design_and_detail(
    request,
    detailing_standard=beam.DetailingStandard.IS456,
)
schedule = beam.bbs(result)

print(result.engineering_status)
print(schedule.total_weight_kg)
```

Properties of this journey:

- all calculation-bearing fields are explicit;
- `member_id`, `story`, and `case_id` have distinct meanings;
- effective depth is supplied or represented by a complete derivation basis;
- detailing standard is explicit instead of a silently defaulted seismic flag;
- cover, bar, stirrup-leg, and spacing choices are explicit rather than inferred
  from the detailing-standard name;
- BBS accepts the valid combined result naturally;
- invalid input raises before any result or schedule exists.

The exact final spelling is frozen in the beam facade packet after the import
spike and before the first public export. Later family packets follow it rather
than creating their own style.

### 5.2 Canonical request composition

The flat `beam.input(...)` factory is the beginner path. It builds the same
strict nested request available to advanced users:

| Common object | Required content |
|---|---|
| `MemberIdentityV1` | `member_id`, `story`, `case_id`; trimmed, non-blank, bounded, stable character set |
| `RectangularBeamSectionV1` | `b_mm`, `D_mm`, exactly one of explicit `d_mm` or complete effective-depth basis |
| `IS456MaterialsV1` | explicit `fck_nmm2`, `fy_nmm2`, supported route domains |
| `BeamActionsV1` | `mu_knm`, `vu_kn`, optional `tu_knm`; finite magnitude convention |
| `BeamDetailingOptionsV1` | explicit detailing standard, cover/bars/stirrups/preferences when detailing is requested |

The nested model is the JSON/OpenAPI schema. The flat factory is a convenience
adapter, not a second contract.

### 5.3 Evidence-heavy families

Wall, staircase, deep-beam, flat-slab, and footing requests retain their
evidence and supported-case boundaries, but reorganize flat fields into five
or fewer coherent groups:

1. identity and source basis;
2. geometry and topology;
3. actions and load-case basis;
4. materials and reinforcement;
5. applicability, review, and evidence references.

The factory signature should normally remain under 12 direct parameters. When
the engineering case genuinely needs more information, the user passes grouped
objects rather than a longer flat call. JSON schema examples and enum values are
generated from the same request model.

### 5.4 FastAPI and generated-client migration

The existing application contract is mounted under `/api/v1` and uses transport
names such as `width`, `depth`, `moment`, and `shear`. Safety corrections apply
to those routes immediately, but the nested explicit-unit canonical request is
not silently substituted into the same versioned schema.

The transport plan is:

1. `/api/v1` remains a compatibility transport and delegates through an exact
   field-mapping adapter to the canonical service request;
2. missing, invalid, or conflicting v1 fields block rather than receive hidden
   structural defaults;
3. once the beam Python facade is frozen, `/api/v2/design/beam` exposes the same
   nested JSON schema, field paths, issue codes, and result envelope as the
   canonical Python request/result;
4. generated Python/TypeScript clients support v1 and v2 during the migration
   window and identify which version they call;
5. React moves only after the v2 generated client and parity tests pass;
6. v1 removal requires the same separate authorization and migration window as
   Python compatibility retirement.

This prevents an unversioned REST signature break while still converging Python,
OpenAPI, clients, and UI on one semantic contract.

## 6. Input and error contract

### 6.1 Strict public model rules

The common public model base uses the Pydantic v2 equivalents of:

- immutable/frozen models;
- `extra="forbid"`;
- strict booleans;
- string whitespace stripping plus non-empty/pattern constraints;
- finite numeric fields that accept ordinary Python integers/floats but reject
  booleans, numeric strings, `NaN`, and infinities;
- explicit key-presence alias resolution;
- cross-field validators for geometry, mutually exclusive fields, collections,
  uniqueness, supported cases, and downstream requirements.

Pydantic errors are converted at the facade boundary. The public Python API
does not require callers to import or catch `pydantic.ValidationError`.

### 6.2 Structured issue model

`InputIssueV1` contains:

| Field | Meaning |
|---|---|
| `code` | Stable machine code such as `INPUT_NOT_FINITE` or `ENUM_VALUE_INVALID` |
| `path` | Exact field path such as `section.d_mm` |
| `message` | Concise human explanation |
| `received` | Safe representation of the rejected value |
| `constraint` | Required predicate or domain |
| `allowed_values` | Exact values for enum/literal failures |
| `suggestion` | Actionable correction when one is unambiguous |

`InputContractError` inherits the existing library validation hierarchy,
contains `issues: tuple[InputIssueV1, ...]`, has a readable `str(error)`, and
can serialize to `structural-problem/v1` for FastAPI and CLI use.

### 6.3 Validation dimensions as data

Each advertised request field must declare applicable dimensions from this
closed vocabulary:

- type and finite value;
- lower/upper range and zero policy;
- unit and quantity;
- code/material domain;
- cross-field relation;
- identity and provenance;
- enum/topology;
- collection cardinality and uniqueness;
- downstream consumability;
- compatibility alias and migration target.

This registry extends the existing API classification/workflow catalogue. It
does not become another independent compatibility manifest.

## 7. Result and consumer contract

### 7.1 Common result protocol

All canonical results implement a maintained protocol rather than inheriting
one large concrete result class. Required behavior is:

```text
schema_version
identity
intake_status
calculation_status
engineering_status
qualified_review_required
issues
limitations
provenance
to_dict()
```

Family payloads remain typed and specific. A beam result does not pretend to
have slab or footing fields.

### 7.2 Consumer acceptance

Every downstream tool publishes exact accepted types:

- `beam.bbs()` accepts `BeamDesignAndDetailResultV1`,
  `BeamDetailingResultV1`, or an explicit sequence of the latter;
- report/export functions accept canonical envelopes or named compatibility
  adapters, never arbitrary dictionaries or duck-typed objects;
- invalid or incomplete results are rejected with `InputContractError` before
  partial item generation;
- a valid combined result and its `.detailing` payload produce identical BBS
  content and accounting totals.

Producer-to-consumer accounting asserts expected items, member identities,
lengths, weights, omissions, and error state. A late crash or silent item drop
is a P0 regression.

## 8. Compatibility and version migration

### 8.1 What changes immediately

The following are safety corrections, not optional deprecations:

- negative magnitude actions reject;
- non-finite and boolean-as-number inputs reject;
- impossible geometry/detailing rejects;
- fabricated blank identities reject where traceability is claimed;
- BBS/report/export reject invalid producer objects.

Release notes must call out the stricter behavior and show corrected inputs.

### 8.2 Staged API migration

| Stage | Public behavior |
|---|---|
| Current Alpha patch | Correct existing fail-open behavior without changing valid signature calls |
| Next planned Alpha | Introduce `structural_lib.design.is456`, canonical strict models, beam reference journey, and migration guide |
| Following Alpha | Add remaining family facades; classify root functions as canonical shortcut, advanced, compatibility, or held in user-facing docs |
| Pre-1.0 stabilization | Deprecation warnings only for routes with a complete replacement and executable migration test |
| 1.0 or later | Removal or signature breaking only with separate owner approval, published policy, caller scan, and at least one supported migration window |

Compatibility wrappers remain in the existing API ledger. The ledger gains:

- canonical target;
- validation parity status;
- result parity status;
- documentation disposition;
- deprecation introduction and earliest removal version;
- maintained-caller migration status.

No retirement/deletion is authorized by this plan.

## 9. Documentation and examples architecture

### 9.1 Navigation layers

| User need | Maintained destination |
|---|---|
| First successful design | `docs/getting-started/python-quickstart.md` |
| One supported workflow per family | family pages under `docs/cookbook/python/` |
| Errors, statuses, review, and units | one shared external-contract guide |
| Exhaustive signatures | generated `docs/reference/api.md` |
| Old-to-new migration | `docs/migration/external-python-api-v1.md` |
| Engineering benchmarks/evidence | `docs/verification/`, separate from beginner recipes |

The current monolithic `python-recipes.md` becomes a landing page plus migration
bridge. Low-level formula examples remain clearly labelled `Expert / low-level`
and are not mixed with canonical member workflows.

### 9.2 Required family recipes

Every supported family receives at least:

1. one minimal valid request;
2. one valid but engineering `FAIL` or `HOLD` interpretation;
3. one invalid-input example showing structured issues;
4. exact enum and supported-case values;
5. result serialization and review boundary;
6. downstream composition where applicable.

Beam additionally includes design-only, multi-case check, detailing, BBS,
torsion, and compatibility migration. Foundation recipes distinguish sizing,
member design, geotechnical assumptions, and load-transfer evidence.

### 9.3 Executable-document control

A maintained script discovers recipe metadata and code blocks, creates a
source-free environment, installs the exact wheel, and checks:

- import succeeds from the wheel;
- signature and request schema match the documented call;
- result type and expected status match;
- invalid example emits the documented issue code/path;
- no repository source path is importable;
- plain stable install and exact prerelease pin are described truthfully.

Generated signature blocks must never be hand-edited. Human explanations,
engineering assumptions, and limitations remain authored prose.

## 10. Dependency-ordered implementation packets

These are logical design packets used to preserve dependency order, owner
boundaries, and acceptance evidence. Only one logical packet is being changed
at a time where shared validation, facade, generated API, documentation, or
result files overlap, but adjacent packets may be delivered in one execution
cycle under Section 15. Effort ranges are planning estimates for one focused
engineer and exclude external qualified review or hosted-runner delay.

### Packet A — beam, detailing, BBS, and existing REST v1 fail-closed chain

**Estimate:** 3–5 engineer-days after adding existing REST v1 containment.

**Objective:** close `EXT-BEAM-001` through `008`, `EXT-DETAIL-001/002`,
`EXT-BBS-001`, `EXT-REST-001/003`, and the safe-result portion of
`EXT-TYPED-001/003` without changing valid numerical results.

**Likely owners:**

- `Python/structural_lib/core/validation.py`;
- `Python/structural_lib/services/beam_api.py`;
- `Python/structural_lib/codes/is456/beam/detailing.py`;
- `Python/structural_lib/services/bbs.py` or its canonical owner;
- `fastapi_app/models/beam.py` and `fastapi_app/routers/design.py`;
- affected FastAPI tests and the generated OpenAPI baseline when its schema
  changes;
- focused unit/integration tests.

**Required behavior:**

- one shared beam boundary validates finite/type, sign, geometry, materials,
  identity, reinforcement, stirrup, spacing, and relations;
- design-only, compliance, combined, smart, and direct-detailing routes call it;
- BBS validates every direct detailing input and accepts a valid combined
  result explicitly;
- the existing `/api/v1/design/beam` compatibility request rejects numeric
  string coercion, booleans-as-numbers, unknown fields, and missing
  calculation-bearing inputs instead of supplying hidden structural choices;
- the v1 route maps accepted compatibility fields into the same validated
  service boundary and returns a fail-closed 4xx response for invalid intake;
  exact v2 field-path/issue-code parity remains Packet D work;
- invalid input produces no design/detailing/BBS object;
- existing valid golden results and nine-line BBS reference remain exact.

**Acceptance:** all fixed LIB-PRO-011 beam/detail/BBS and REST P0 reproducers
reject; focused tests, producer-consumer accounting, FastAPI request/route
tests, quick gate, and staged hooks pass.

### Packet B — torsion, column, and structured beam truth

**Estimate:** 3–5 engineer-days.

**Objective:** close `EXT-TORSION-001` through `006`, `EXT-COLUMN-001/002`,
`EXT-TYPED-001` through `007`, and `EXT-ID-001`.

**Likely owners:**

- `codes/is456/beam/torsion.py` and its service adapter;
- `services/column_api.py`;
- `core/inputs.py`;
- shared validation/errors and focused tests.

**Required behavior:**

- torsion uses non-negative magnitude actions, physical closed-core geometry,
  supported material limits, and no safety-changing clamps;
- unified column rejects negative applied moment magnitudes and no longer uses
  a failing `Asc_mm2=0` default for a supplied-steel check;
- structured beam inputs reject non-finite values, numeric booleans, ambiguous
  string booleans, blank/fabricated identities, conflicts, and invalid case
  cardinality at construction;
- alias parsing preserves explicit zero by key presence.

**Acceptance:** fixed P0/P1 reproducers plus direct pure-function tests pass;
valid existing torsion/column/structured-input cases remain unchanged.

### Packet C — public input, issue, and facade foundation

**Estimate:** 4–6 engineer-days.

**Prerequisite:** the combined P0 Safety Cycle containing Packets A and B, so
the new facade cannot hide unsafe legacy owners.

**Objective:** implement the common strict model base, `InputIssueV1`,
`InputContractError`, field-contract vocabulary, and the empty
`structural_lib.design.is456` facade skeleton.

**Likely owners:**

- a bounded new `services/contracts/` package;
- `core/errors.py` and `core/result_contract.py` extensions;
- facade-only modules under `structural_lib/design/is456/`;
- API classification generator and tests.

**Acceptance:** strict numeric/boolean/extra-field/identity/enum/collection tests
pass; no import cycle; wheel contains the facade; raw Pydantic errors do not
escape; existing root imports remain identical.

### Packet D — canonical beam vertical slice

**Estimate:** 5–8 engineer-days.

**Objective:** deliver the complete target beam journey as the reference for
all later member families.

**Scope:**

- `BeamDesignInputV1` and grouped submodels;
- `beam.input`, `beam.design`, `beam.check`, `beam.detail`,
  `beam.design_and_detail`, and `beam.bbs`;
- typed canonical result/envelope;
- compatibility delegation from existing root/service functions;
- completion of `/api/v1` canonical mapping/error parity after Packet A's
  immediate containment, plus a versioned `/api/v2` beam request only after the
  Python contract freezes;
- Python/FastAPI request, issue, result, and generated-client parity for the
  supported beam subset;
- first executable cookbook and migration page.

**Acceptance:** beginner example, nested JSON example, compatibility example,
invalid example, exact-wheel replay, FastAPI parity, and BBS chain all pass.
The generated API classification names this one canonical journey.

### Packet E — result and downstream consumer convergence

**Estimate:** 3–5 engineer-days.

**Objective:** make BBS, report, export, serialization, CLI, and application
adapters consume canonical results without dictionary guessing or status loss.

**Scope:** explicit accepted types, compatibility adapters, accounting checks,
finite serialization, orthogonal status, and no partial-success artifact after
blocked intake.

**Acceptance:** safe, unsafe, held, invalid, and calculation-error cases retain
the same identity/status/content across Python result, BBS, report/export,
FastAPI, and source-free wheel paths.

### Packet F1 — torsion, column, and slab family facades

**Estimate:** 5–8 engineer-days.

These medium-complexity families follow the beam vocabulary. Torsion uses
explicit-unit names; column separates supplied-steel checking from any future
steel-selection workflow; one-way/two-way/continuous slab routes state their
supported action and serviceability boundaries.

**Acceptance:** one request/result/error style, recipes, generated schemas,
compatibility delegation, and exact-wheel negative vectors per family.

### Packet F2 — wall, staircase, deep-beam, and flat-slab facades

**Estimate:** 6–10 engineer-days.

The existing evidence-heavy requests are regrouped without removing required
truth fields. Builders list and require topology, applicability, load-case
basis, and evidence values. Exact enum errors use `InputIssueV1`.

**Acceptance:** each canonical factory has no hidden engineering choice, every
required group is represented in JSON schema, and a new external user can run
the supported recipe without reading owner-module source.

### Packet F3 — isolated, combined, and strap footing facades

**Estimate:** 5–8 engineer-days.

Owner-module builders are promoted or adapted through the facade. Sizing,
structural design, geotechnical basis, load transfer, and review state remain
explicit. Existing foundation checks and evidence boundaries are not collapsed
into one optimistic `PASS`.

**Acceptance:** all three footing recipes execute from the wheel, builder paths
are root/facade discoverable, and result/assumption provenance is preserved.

### Packet G — documentation, discovery, and migration completion

**Estimate:** 4–7 engineer-days.

**Scope:**

- replace the beginner quickstart with the canonical journey;
- split family recipes under `docs/cookbook/python/`;
- publish allowed enums, units, errors, status/review guide, and migration map;
- correct current package/install/version facts;
- make root `dir()` discovery point users to the curated facade without hiding
  compatibility exports;
- generate signature/schema blocks from live classified owners.

**Acceptance:** one evaluator can install the exact wheel and complete every
supported family recipe without source inspection; all examples are executable
and all version/signature statements match the artifact.

### Packet H — contract-generated audit and release gates

**Estimate:** 4–7 engineer-days.

**Scope:**

- extend existing API classification/workflow catalogue with advertised
  workflows and field-contract dimensions;
- recursively audit strict request fields;
- generate finite, boolean, sign, zero, range, enum, identity, relation,
  cardinality, alias, and consumer vectors;
- derive public-route safety targets from advertised workflows;
- continue direct-source vectors through exact-wheel and consumer chains;
- make unowned validation on an advertised route release-blocking unless a
  route/field/risk/expiry waiver is versioned.

**Acceptance:** deleting one validator, recipe registration, route target, or
consumer check makes the maintained gate fail. An advertised route cannot be
green while its request fields remain `UNPROVEN`.

### Packet I — cumulative external-preview candidate

**Estimate:** 3–5 engineer-days plus hosted and review time.

**Prerequisite:** A–H integrated on one exact candidate.

**Scope:** broad Python/FastAPI/React gates as impact requires, built-wheel
inspection, source-free cookbook/UAT, compatibility caller scan, release-note
migration text, hosted checks, and separate qualified review evidence.

**Acceptance:** evaluator-ready Alpha criteria in Section 13 pass. Publication,
tagging, GitHub Release, professional approval, and stable/engineering-use
claims still require their separate authorities.

## 11. Finding-to-packet ownership

| Finding family | Owning packet(s) |
|---|---|
| `EXT-BEAM-*`, `EXT-DETAIL-*`, `EXT-BBS-001` | A, then D/E for canonical composition |
| `EXT-TORSION-*` | B for safety, F1 for canonical facade |
| `EXT-COLUMN-*` | B for safety/signature truth, F1 for separated workflows |
| `EXT-TYPED-*`, `EXT-ID-001` | B, then C/D for strict public models |
| `EXT-ENUM-001` | C common error model, F1–F3 family adoption |
| `EXT-API-001/002` | C/D facade, G discovery, H advertised gate |
| `EXT-REST-001/003` | A immediate v1 containment, then D/H/I for canonical parity and artifact gates |
| `EXT-REST-002` | D versioned transport, G migration docs, H/I parity and artifact gates |
| `EXT-BUILDER-001` | F2/F3 plus G recipes |
| `EXT-DOC-001` | G and H |
| `EXT-RELEASE-001`, `EXT-INSTALL-001` | G and I |
| `EXT-BBS-002` | D/E |

No finding is closed by documentation alone when runtime behavior is invalid.
No runtime fix is closed without direct-source and exact-wheel evidence.

## 12. Verification strategy

### 12.1 Per-packet evidence

Each packet returns:

- exact before/after reproducers;
- changed owners and compatibility surfaces;
- focused deterministic tests;
- Hypothesis boundary tests for applicable scalar contracts;
- import/architecture checks;
- generated signature/classification diff;
- one consolidated quick gate after content freeze;
- clean staged hooks and task-owned session evidence.

### 12.2 Cross-surface matrix

| Vector | Direct Python | Request model | Legacy wrapper | FastAPI | Consumer | Exact wheel |
|---|---:|---:|---:|---:|---:|---:|
| Valid typical | Required | Required | Required | Required | Required | Required |
| Valid zero where allowed | Required | Required | Required | Required | If applicable | Required |
| Boolean as number | Reject | Reject | Reject | Reject | Reject | Reject |
| `NaN`, `+Inf`, `-Inf` | Reject | Reject | Reject | Reject | Reject | Reject |
| Negative magnitude | Reject | Reject | Reject | Reject | Reject | Reject |
| Invalid relation | Reject | Reject | Reject | Reject | Reject | Reject |
| Blank/fabricated identity | Reject | Reject | Reject | Reject | Reject | Reject |
| Invalid enum | Structured reject | Structured reject | Structured reject | Same issue path/code | N/A | Same issue path/code |
| Empty/duplicate collection | Reject | Reject | Reject | Reject | Reject | Reject |
| Valid engineering failure | Typed `FAIL/HOLD` | Same | Same semantics | Same | Preserved | Same |

### 12.3 Cumulative candidate evidence

After A–H integrate, run the affected focused suites, independent reproducers,
architecture/import checks, quick gate, normal hooks, and required hosted PR
checks for each packet. Run the broad Python suite and full `./run.sh check`
once for the cumulative frozen candidate, followed by exact-wheel UAT and
executable cookbook replay.

Software green does not confer qualified engineering approval.

## 13. Readiness milestones

| Milestone | Required packets | External claim permitted |
|---|---|---|
| Safety repair complete | A–B | Existing Alpha routes no longer reproduce the frozen P0 invalid-input outcomes; no usability/readiness claim yet |
| Canonical beam preview | A–E | Beam facade may be documented as an Alpha developer preview with exact limitations |
| Evaluator-ready Alpha | A–H | Careful external evaluator can use supported family recipes; package remains Alpha and review-required |
| Release candidate technically ready | A–I plus exact hosted/artifact evidence | Exact candidate may be presented for owner release decision; not automatically publishable |
| Stable/engineering-use consideration | Separate compatibility window, full scope evidence, qualified review, and owner authorization | Only the separately approved wording |

Evaluator-ready Alpha requires all of the following:

1. zero unresolved P0 findings from LIB-PRO-011;
2. zero unowned validation dimensions on advertised workflows;
3. one canonical executable recipe per advertised member family;
4. structured error and result parity across Python/FastAPI where both exist;
5. producer-to-consumer accounting with no silent omission;
6. truthful stable-versus-prerelease install guidance and artifact identity;
7. explicit supported cases, limitations, and qualified-review requirement.

## 14. Risk register and stop conditions

| Risk | Required control |
|---|---|
| A new facade becomes another duplicate API | Facade contains delegation only; classification and caller scans prove one owner |
| Pydantic leaks into pure calculations | Models remain in service-contract/facade layers; `codes/is456` imports no services |
| Strict parsing rejects legitimate Python numerics | Freeze accepted scalar protocol and test ordinary `int`/`float`; reject bool/string/non-finite deliberately |
| Migration preserves unsafe behavior | Safety semantics change immediately; compatibility covers spelling/shape only |
| Builders hide engineering choices | Every topology/material/action/evidence choice is explicit or a visibly selected named template |
| Result unification erases family detail | Common protocol plus typed family payload, not one universal result dictionary |
| Documentation project runs ahead of runtime | Recipes land with their runtime packet and exact-wheel executable test |
| Generated contract becomes a third manifest | Extend existing classification/catalogue and compatibility ledger; fail review on independent duplicate authority |
| Signature work collides with active candidates | Re-query worktrees, changed paths, branch/PR state, and integration order before each packet |
| Engineering domain changes during UX work | Stop and create a separately source-bound engineering packet |

Stop the current packet if a proposed convenience feature requires guessing a
structural input, if compatibility needs a second calculation engine, if a
valid golden vector changes without explained root cause and independent
evidence, or if another active candidate owns overlapping shared/generated
paths.

## 15. Efficient execution cycles and immediate next work

The logical packet estimates still total approximately **45–74 engineer-days**
for one focused implementation lane (roughly 9–15 working weeks), excluding
the single final engineer review, hosted queue time, and publication. The work
is not reduced by hiding it; Git, session, and unchanged-suite repetition are
reduced by grouping the work into coherent candidate cycles.

| Cycle | Included logical work | Default Git/session shape | Completion boundary |
|---|---|---|---|
| **P0 Planning integration** | LIB-PRO-011 audit plus the corrected LIB-PRO-012/013 plans | Current planning branch, one session, one candidate, one PR/check cycle | Plans and exact next-work authority are integrated on current `main` |
| **S0 P0 Safety Closure** | LIB-PRO-013 G0 exact pre-change baseline, then LIB-PRO-012 A and B | One parent session, one task branch, one frozen implementation candidate, one PR/check cycle | Every frozen Python, consumer, structured-input, column, torsion, and existing REST P0 rejects before calculation/artifact creation; valid goldens remain exact |
| **A0 Consolidated Renewal Audit** | The initial LIB-PRO-013 audit through its C2 remediation portfolio | One read-only audit session and one evidence candidate/PR; no runtime edits | Architecture, scope, transport, dependency, evidence, and usability decisions needed by later 012 work are frozen |
| **B0 Canonical Beam Contract** | LIB-PRO-012 C, D, and E | One implementation session/branch/candidate/PR after A0 | Common contract plus complete beam vertical slice and downstream convergence pass direct, FastAPI, consumer, and exact-wheel evidence |
| **F0 Family Convergence** | LIB-PRO-012 F1, F2, and F3, executed internally family by family | One implementation session/branch/candidate/PR by default; split only under D11 stop conditions | Every supported family follows the frozen request/result/error style with executable wheel recipes |
| **R0 External-Preview Candidate** | LIB-PRO-012 G, H, and I plus applicable LIB-PRO-013 closure evidence | One final implementation/evidence session and one frozen candidate/PR/check cycle | Documentation, generated gates, cumulative full checks, exact-wheel UAT, independent audit, and owner decision package are complete |

This is six planned Git/hosted cycles including the current planning integration,
instead of treating A–I and each audit lane as separate PRs. Unknown findings
from A0 join the nearest compatible later cycle when ownership and dependency
order permit; they create a separate cycle only when D11 requires isolation.

One PR/head per execution cycle does not erase the acceptance obligation of its
internal work packages. Before merge, the cycle evidence must contain a compact
coverage matrix that maps each included Section 10 work package to:

- its changed paths and outcome owner;
- its focused tests and independent reproducers;
- every required changed-path hosted check; and
- the passing status of those checks on the one exact candidate head.

The hosted workflow runs once on that shared frozen head when its changed-path
map covers the whole cycle; the evidence records that result against every
included work package. If the required hosted domains cannot be proven on one
coherent head, D11 requires the cycle to split.

The first executable cycle after planning integration is **S0 P0 Safety
Closure**. Within that one cycle, work proceeds internally as G0 baseline ->
Packet A Python/consumer containment -> Packet A REST v1 containment -> Packet B
torsion/column/structured-input containment. It is frozen and reviewed only
after all four internal phases are complete.

S0 comes before facade or signature work because:

- it closes the largest safe-looking invalid-result path;
- every future beam facade delegates to these owners;
- it creates the reference producer-to-consumer test;
- it can ship as a bounded Alpha safety correction without waiting for the
  multi-family usability programme; and
- it closes the existing REST P0 path that the earlier A–B milestone omitted.

After S0, execute A0 -> B0 -> F0 -> R0. Do not parallel-write validation,
facade, result, generated API, documentation, task, or session owners. Do not
create status-only sessions, WIP PRs, or unchanged broad reruns merely to show
progress.

Current plan verdict: **S0, A0, and B0 are integrated. F0 Packets F1, F2, and
F3 are the next authorized cycle; R0 follows accepted F0. The prepared Windows
lane is setup-ready at the B0 identity and must be rebound to the exact accepted
F0 merge before R0 uses it. Professional review occurs once after the final
integrated-library candidate.**
