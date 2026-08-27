---
owner: Main Agent
status: active
last_updated: 2026-08-27
doc_type: reference
complexity: advanced
tags: [external-user, public-api, validation, signatures, usability, comparison]
---

# LIB-PRO-011 External API Readiness Audit

## 1. Purpose and decision boundary

This is the durable audit authority for the next external-user safety and
usability repair. It records what a user can observe from the published Python
package, not only what repository scanners or internal typed workflows prove.

The audit may identify, reproduce, classify, and plan corrections. It does not
change engineering formulas, public signatures, supported cases, release
metadata, or package artifacts. Implementation requires separately frozen
repair packets after this evidence is complete.

## 2. Exact artifact identity

| Item | Bound observation |
|---|---|
| Package | `structural-lib-is456==0.24.0a1` |
| Public wheel SHA-256 | `b5e0df7b561e8c715f37c602200eaae2c369ec5dc992eec87110a77c1026201a` |
| Public tag commit | `71b7065216d4266d63ad6b31bd39bba81fa16efc` |
| Audit base | `6a4683eb8b21bff77f2991230b4458463e61f419` |
| Runtime drift after tag | No changed paths under `Python/structural_lib/` |
| Public source | <https://pypi.org/project/structural-lib-is456/0.24.0a1/> |

The wheel was downloaded from PyPI, its hash was checked before installation,
and calls ran from an isolated Python 3.11 environment whose import origin was
the installed wheel rather than the repository source tree.

## 3. Initial exact-wheel finding register

Priority is based on the external main-process outcome. `P0` can produce a
safe-looking result or materially incomplete downstream artifact from invalid
input. `P1` blocks a predictable public contract or traceable workflow. `P2`
is a material usability or trust defect that should be corrected before a
stability claim.

| ID | Pri | Reproduction | Exact external outcome | Required disposition |
|---|---:|---|---|---|
| EXT-BEAM-001 | P0 | `design_and_detail_beam_is456(span_mm=-1)` | Returns `DesignAndDetailResult(is_ok=True)` and preserves `span_mm=-1` | Reject non-positive span before calculation |
| EXT-BEAM-002 | P0 | Same route with `span_mm=0`, `NaN`, `+Infinity`, or `-Infinity` | Every case returns `is_ok=True` | Require a finite positive span |
| EXT-BEAM-003 | P0 | Same route with `mu_knm=-50` | Returns `is_ok=True` | Freeze a non-negative magnitude contract or an explicit signed-action model; do not silently treat the value as an ordinary sagging design |
| EXT-BEAM-004 | P0 | Same route with `vu_kn=-10` | Returns `is_ok=True` | Apply the same explicit action convention at every beam entry point |
| EXT-BEAM-005 | P0 | `design_beam_is456` with negative `mu_knm` or `vu_kn` | Returns `ComplianceCaseResult(is_ok=True)` while echoing the negative action | Correct the shared direct-service boundary, not only the combined wrapper |
| EXT-BEAM-006 | P1 | Combined or design-only route with `b_mm<=0` | Returns a structured `FAIL` but continues into calculation; the combined route also creates detailing with impossible spacing | Classify as invalid input and stop before design/detailing |
| EXT-BEAM-007 | P0 | `check_beam_is456` case with negative `mu_knm` or `vu_kn` | Returns `ComplianceReport(is_ok=True)` | Validate action semantics before aggregating cases |
| EXT-BEAM-008 | P0 | `smart_analyze_design(mu_knm=-50, vu_kn=-10)` | Returns `design_status='PASS'`, a safety score of `0.8004`, and no warning | The high-level analysis route must share the canonical action boundary |
| EXT-DETAIL-001 | P0 | Combined route with support or mid stirrup spacing `0`, negative, or `NaN` | Returns `is_ok=True` and `Detailing complete` | Validate every supplied detailing scalar before creating arrangements |
| EXT-DETAIL-002 | P0 | Direct `detail_beam_is456` with non-positive/`NaN` span, negative cover, zero stirrup diameter, or non-positive/`NaN` spacing | Returns a `BeamDetailingResult` instead of rejecting intake | Make direct detailing fail closed independently of its callers |
| EXT-BBS-001 | P0 | BBS after invalid span or stirrup spacing | Non-positive span produces six rather than nine items; invalid support spacing produces seven rather than nine; `NaN` span crashes | Downstream consumers must never receive invalid detailing; they must also validate their direct inputs |
| EXT-TORSION-001 | P0 | `design_torsion(tu_knm=-5)` | Returns `is_safe=True`; the negative sign reduces `Ve` from `106.67` to `53.33 kN` for the probe instead of applying a documented magnitude convention | Reject negative magnitude input or implement and document a coherent signed convention |
| EXT-TORSION-002 | P0 | Negative `vu_kn` or `mu_knm` | Returns `is_safe=True`; different helpers apply signs and absolute values inconsistently | Normalize once before every torsion equation |
| EXT-TORSION-003 | P0 | `cover<=0`, `stirrup_dia<=0`, or `d>D` | Returns `is_safe=True` | Require physical geometry and a positive closed-stirrup core |
| EXT-TORSION-004 | P0 | `fy=600` although the route documents `fy<=500` | Returns `is_safe=True` | Enforce the advertised supported material domain |
| EXT-TORSION-005 | P0 | Impossible closed-stirrup core or zero stirrup diameter | Core dimensions are clamped to `50 x 100 mm`; zero diameter is converted into a reported `75 mm` spacing and a safe result | Remove safety-changing clamps; reject invalid supplied geometry |
| EXT-TORSION-006 | P2 | `b=0` | Raises `DimensionError` saying the width is below minimum `0 mm` and should be increased to at least `0 mm` | Use a positive lower-bound message consistent with the predicate |
| EXT-ID-001 | P1 | Empty `beam_id` and `story` on the combined route | Returns `is_ok=True` with empty result identity | Require non-blank identity before calculation |
| EXT-BBS-002 | P1 | `compute_bbs(design_and_detail_result)` | Raises `TypeError`; `[result.detailing]` returns the expected nine-item document | Add an explicit convenience adapter or improve the accepted-type error |
| EXT-COLUMN-001 | P1 | Omit `Asc_mm2` from `design_column_is456` | Signature default supplies `0.0`, then the route raises `DimensionError` | Make supplied reinforcement required or expose a separately named steel-design workflow |
| EXT-COLUMN-002 | P0 | `design_column_is456(Mux_kNm=-120)` or negative `Muy_kNm` | The negative applied moment is replaced by the positive minimum-eccentricity moment; the probe returns `is_safe=True` | Treat `Mux_kNm`/`Muy_kNm` as documented non-negative magnitudes; retain signed end-moment semantics only in explicitly signed fields |
| EXT-TYPED-001 | P0 | `BeamGeometryInput(span_mm=NaN)` followed by `design_from_input` | Construction succeeds and design returns `is_ok=True` with `span=NaN` | Finite/physical validation belongs in the structured input itself and again at the public calculation boundary |
| EXT-TYPED-002 | P1 | Construct `BeamGeometryInput`, `MaterialsInput`, or `LoadsInput` with `NaN`/infinity; use negative stirrup diameter | Constructors described as validated accept the values; downstream action checks reject some, but geometry does not | Replace comparison-only post-init checks with common finite/domain/relational validators |
| EXT-TYPED-003 | P0 | Negative/`NaN` `DetailingConfigInput` values followed by design and BBS | Configuration construction succeeds; design returns a detailing result containing negative/`NaN` stirrups and BBS drops from nine to six items | Validate the configuration at construction and at direct detailing/BBS boundaries |
| EXT-TYPED-004 | P1 | `DetailingConfigInput.from_dict({'is_seismic': 'false'})` | Python truthiness converts the string to `True` | Use strict boolean parsing; reject rather than reinterpret ambiguous JSON values |
| EXT-TYPED-005 | P1 | `BeamInput(load_cases=[one_case], loads=None)` followed by `design_from_input` | Raises `ValueError` even though the model accepts `load_cases` and documents multi-case use | Treat one or more supplied cases consistently or state and enforce the actual cardinality contract at construction |
| EXT-TYPED-006 | P1 | `BeamInput.from_dict` without `beam_id` or `story` | Invents `BEAM`/`STORY`; design returns `is_ok=True` with fabricated identity | Require explicit identity for traceable design imports |
| EXT-TYPED-007 | P2 | `LoadsInput.from_dict({'mu_knm': 0, 'vu_kn': 0})` | Raises a misleading missing-field error because `or` treats zero as absent | Test key presence rather than truthiness; preserve valid numerical zero |
| EXT-ENUM-001 | P2 | Invalid wall/stair/deep-beam public enum strings | Wall/deep errors do not list allowed values; staircase leaks the raw enum `ValueError` for `support_case` | Use one structured public error format with field path, rejected value, and allowed values |
| EXT-API-001 | P1 | Inspect the root package surface | 222 exports include 100 functions but only one canonical task; 30 functions retain unit-ambiguous dimensional names and public styles mix long positional calls, keyword-only calls, request objects, dictionaries, and typed results | Publish a small canonical journey per member family and classify every other root export as advanced or compatibility in user-facing docs |
| EXT-API-002 | P1 | Compare API classification to user-facing quick starts | Combined beam, BBS, torsion, optimization, and smart analysis are classified `compatibility` while README/API material advertises them as primary workflows | Safety gates must follow the advertised surface, not only the internal claim disposition |
| EXT-BUILDER-001 | P2 | Search root/service facades for evidence-heavy request builders | Flat-slab, combined-footing, and strap-footing builders exist only in owner modules and are neither root-exported nor documented in the public guide; wall, stair, deep-beam, and isolated-footing workflows have none | Export and document supported builders or provide complete validated request examples and JSON schemas |
| EXT-DOC-001 | P1 | Compare `docs/reference/api.md` column heading with `inspect.signature` | The reference shows legacy `fck=25`, `fy=415` defaults while the live route requires `fck_nmm2`/`fy_nmm2`; several builder paths are absent | Generate signature blocks from the live classified API and execute examples against the built wheel |
| EXT-RELEASE-001 | P1 | Read the published PyPI description and current READMEs | They say `0.24.0a1` is unpublished and `0.23.1a2` remains current, contradicting the live release | Publication metadata must be truthful before artifact upload and current docs must be updated after release |
| EXT-INSTALL-001 | P2 | Plain `pip install structural-lib-is456` | Pip selects stable `0.23.0`, not prerelease `0.24.0a1` | Keep exact-pin and prerelease guidance prominent; do not imply an unpinned install selects the alpha |

## 4. Confirmed distinctions and non-findings

- `beam_id` and `case_id` are different identities. A compatibility alias that
  treats them as interchangeable would damage traceability. A future public
  request may expose both, while the combined legacy wrapper can continue to
  derive its internal case identity explicitly.
- `load_case_basis` on the flanged-beam route is an intentional evidence and
  scope boundary. It should remain required; examples and allowed-value errors
  should make the contract easier to discover.
- Exact wall, staircase, deep-beam, flat-slab, and foundation enums are
  appropriate for bounded typed workflows. Errors should list accepted values,
  but the library should not silently guess an engineering case.
- Zero action is a valid numerical boundary in some check workflows. The
  release UAT deliberately treats explicit zero shear as valid. A complete
  member-design convenience route may add a visible note, but zero must not be
  rejected globally without a route-specific contract.
- `check_code(code_id)` intentionally validates one named design-code
  implementation and is documented with `check_code("is456")`; a zero-argument
  call is not part of its current contract.

## 5. Broader public-surface inventory

### 5.1 Root API shape

The generated API classification and live `inspect.signature()` inventory give
the following current root-package shape. Counts describe inconsistency and
review burden; a positional parameter or compatibility export is not a defect
by itself.

| Measure | Live count | External implication |
|---|---:|---|
| Declared root exports | 222 | `dir(structural_lib)` is not a curated beginner surface |
| Root functions | 100 | A user must distinguish workflows, helpers, compatibility functions, and held visualisation functions |
| Canonical functions | 1 | Only `design_beam_is456` is classified as a canonical task |
| Advanced functions | 30 | Many real member workflows are public but not part of one consistent journey |
| Compatibility functions | 58 | Several are nevertheless promoted in READMEs as primary workflows |
| Held functions | 11 | Held and usable-looking names share the same root namespace |
| Functions with positional parameters | 70 | Calling style differs materially from the canonical keyword-only beam route |
| Request-object style functions | 10 | Newer INDIA workflows use a different, stronger boundary style |
| Functions with bare dimensional names such as `b`, `D`, `d`, `fck`, or `fy` | 30 | Six advanced functions and numerous compatibility helpers retain unit-ambiguous names |
| Functions with zero/empty scalar defaults | 15 | Some are valid neutral defaults; others, such as column `Asc_mm2=0`, fail only after entry |

The mixed surface includes all of the following result styles: dictionaries,
frozen dataclasses, compatibility mixins, reports with `is_ok`, results with
`is_safe`, and INDIA-family results with `PASS`/`FAIL`/`HOLD`-like status plus
`qualified_review_required`. That history is understandable for an Alpha, but
it is not yet predictable for an external caller.

### 5.2 Evidence-heavy request burden

The newer member workflows are more honest and substantially safer than the
legacy beam/torsion functions. Direct probes confirmed that wall, stair, deep
beam, slab, and footing routes reject non-finite or physically invalid inputs.
Their external cost is construction and discovery:

| Public request | Required top-level fields | Public builder at root/service facade | Finding |
|---|---:|---|---|
| `BracedWallDesignInput` | 15 | No | Exact bracing/evidence fields are justified; first-use recipe is needed |
| `StraightFlightStaircaseInput` | 24 | No | Exact case is justified; invalid `support_case` leaks a raw enum error |
| `SimplySupportedDeepBeamDesignInput` | 32 | No | Bounded truth is strong; construction is difficult without a fixture/builder |
| `RegularInteriorFlatSlabDesignInput` | 17 plus nested inputs | No | A builder exists only in the owner module and is absent from public docs |
| `ConcentricIsolatedFootingInput` | 31 | No | Provenance requirements are strong but need a supported construction path |
| `SymmetricCombinedFootingDesignInput` | 3 plus nested footing | No | Owner-module builder exists but is not facade-exported or publicly documented |
| `PropertyLineStrapFootingDesignInput` | 3 plus nested footing | No | Owner-module builder exists but is not facade-exported or publicly documented |

The 4,651-line API reference contains several full member examples, but the
206-line Python quickstart remains beam/column oriented and does not route a
new user to one copy-paste recipe per supported family. Builder examples are
stored mainly in acceptance-evidence documents rather than user documentation.

### 5.3 Control-group observations

The expanded audit did not find the same gap everywhere:

- `design_flanged_beam_is456` rejects a negative moment at its bounded
  flange-in-compression boundary.
- `optimize_beam_cost` rejects negative actions before its search.
- One-way slab public design rejects non-positive/non-finite spans, loads, and
  bar spacing.
- Footing sizing, flexure, one-way shear, punching, and bearing reject the
  sampled non-finite, negative-load, and non-positive geometry cases.
- Wall, staircase, and deep-beam routes reject sampled non-finite geometry and
  unsupported topology flags. Their principal issue in this audit is external
  construction and error discoverability, not a reproduced safe-looking
  result from garbage input.

These controls show that a fail-closed model already exists in the codebase.
The repair should reuse it rather than create a third validation architecture.

## 6. Why previous audits did not close these issues

### 6.1 The unresolved state was visible

The issues were not entirely invisible. Running the maintained static input
ownership audit at the audit base reported:

| Status | Parameters |
|---|---:|
| `PROVEN` | 148 |
| `DELEGATED` | 122 |
| `UNPROVEN` | 357 |
| `NOT_APPLICABLE` | 136 |
| **Total** | **763 across 110 functions** |

For example, it already marks 14 combined-beam scalars and 12 direct-detailing
scalars `UNPROVEN`. The readiness system therefore carried a truthful
`PARTIAL` warning, but Alpha release policy did not make resolution of every
advertised Python route a hard artifact gate.

### 6.2 What each current audit proves, and what it misses

| Mechanism | What it currently proves | Why the external defects remain |
|---|---|---|
| `audit_input_validation.py` | Static ownership for discovered scalar parameters | A called finite validator can be labelled `DELEGATED` even when sign, relation, or material-domain rules are absent. It does not recursively audit dataclass fields: `design_from_input(beam)` is marked `PROVEN` from a local guard although `beam.geometry.span_mm=NaN` reaches a safe-looking result. String fields are usually `NOT_APPLICABLE`, so blank identity is outside its model. |
| `check_public_route_safety.py` | A frozen list of 21 Python and 5 FastAPI regressions passes | The list is hand-maintained, not generated from advertised entry points. It includes torsion `NaN` but not negative torsion, direct detailing, combined-beam spacing/span, negative direct actions, structured-input recursion, or BBS propagation. |
| Exact-wheel release UAT | 29 source-free cases cover project intake, CLI commands, adapters, selected footing/column cases, and a valid downstream CLI chain | Its negative matrix is concentrated on the strict project/CLI intake. The Python README example calls combined beam only with valid values; it does not apply the negative matrix to the callable or to direct BBS/detailing consumers. |
| `audit_readiness_report.py` | Required contract tests fail the verdict; advisory diagnostics produce `PARTIAL` | Public-route safety is required, but the broad input audit and function-quality scan are explicitly non-required warnings. A frozen safety list can pass while 357 parameters remain unproven. |
| `check_function_quality.py` | Clause-function documentation, return, and unit-name conventions | Its explicit legacy-unit ledger correctly avoids breaking APIs, but that exemption proves documentation of units, not runtime validation or a beginner-safe signature. |
| API classification | Every root export has a claim disposition | The user-facing README promotes compatibility routes such as combined beam, BBS, torsion, smart analysis, and optimization. Internal `compatibility` classification did not reduce their external safety obligation. |

### 6.3 Confirmed root causes

The failures are not isolated missing `if` statements. They come from five
system causes:

1. **Route-local validators.** Project intake, slabs, footings, and newer typed
   INDIA workflows use stronger boundaries, while older public functions
   duplicate partial plausibility checks or call calculations directly.
2. **Incomplete validation semantics.** The audit vocabulary records the
   presence of a guard, not the full contract dimensions: finite, type,
   physical range, code domain, cross-field relation, identity, collection,
   topology, and downstream consumability.
3. **No recursive public-input contract.** Structured dataclasses claim
   construction-time validation but rely on comparisons that do not reject
   `NaN`; JSON helpers use truthiness coercion and can invent defaults.
4. **Advertised-surface/gated-surface mismatch.** Release gates inventory 12
   CLI commands and selected Python regressions, while READMEs expose a much
   broader root Python surface.
5. **Invalid intake and valid engineering failure are conflated.** Some routes
   return `FAIL` after impossible geometry instead of raising a validation
   error before any design/detailing/BBS work.

The result is **route-local safety**, not yet **public-surface safety**.

## 7. Comparison with maintained peer libraries and validation practice

This is a pattern comparison, not a claim that another project is universally
safer or directly interchangeable with an IS 456 member-design library. Sources
were read from official project documentation on 2026-08-27.

| Source | Observable public pattern | Relevant change for StructLib |
|---|---|---|
| [StructuralCodes quickstart](https://fib-international.github.io/structuralcodes/quickstart/index.html), [usage guide](https://fib-international.github.io/structuralcodes/usage/index.html), and [section results](https://fib-international.github.io/structuralcodes/usage/sections/index.html) | A five-minute progressive journey builds design-code materials, geometry, a section object, then calculation-specific result objects. Section documentation links to sign conventions and exposes further inspection through typed results. | Give every supported member one progressive canonical journey and one typed result protocol. State action/axis sign conventions next to signatures instead of letting negative values acquire accidental meaning. |
| [concreteproperties user guide](https://robbievanleeuwen.github.io/concrete-properties/user_guide.html), [examples](https://robbievanleeuwen.github.io/concrete-properties/examples.html), and [AS 3600 API](https://robbievanleeuwen.github.io/concrete-properties/gen/concreteproperties.design_codes.as3600.AS3600.html) | Documentation is organised as materials, geometry, analysis, results, and design codes, followed by worked examples. Code-specific material factories document supported strength ranges and allowed categorical values with explicit `ValueError` behavior. | Separate beginner workflows from exhaustive reference; put supported domains and allowed values in the public signature/error contract; prefer material/request factories over repeated unvalidated scalars. |
| [sectionproperties documentation](https://sectionproperties.readthedocs.io/en/stable/) and [examples](https://sectionproperties.readthedocs.io/en/stable/examples.html) | Installation, user guide, API, examples, and validation examples are distinct navigation lanes. Examples are grouped by geometry, materials, analysis, results, benchmark validation, and advanced use; the engineering disclaimer remains visible. | Add an external validation cookbook and keep worked workflows separate from internal acceptance evidence. A disclaimer complements, but does not replace, fail-closed intake. |
| [Pint dimensional checks](https://pint.readthedocs.io/en/latest/api/base.html) | Functions can require quantities of an expected dimension and raise `DimensionalityError` on mismatch. | Keep explicit `*_mm`, `*_kn`, and `*_nmm2` canonical names; consider an optional quantity adapter later. Do not require a unit package for the immediate P0 repair. |
| [Pydantic strict mode](https://pydantic.dev/docs/validation/latest/concepts/strict_mode/) and [structured errors](https://pydantic.dev/docs/validation/latest/errors/errors/) | Strict mode prevents silent coercion; validation errors carry field location, rejected input, human message, and machine-readable type, and can report multiple input errors together. | Replace `bool('false')`, truthiness-based numeric aliases, and one-off opaque messages with strict parsing and structured field-level errors. The repository already depends on Pydantic at transport boundaries, but the Python API may implement the same contract without converting every core dataclass. |
| [SciPy `curve_fit`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.curve_fit.html) | Its documented default finite check raises before calculation; disabling it explicitly risks nonsensical results. | Finite rejection should be the non-optional default for engineering design inputs. If a specialist low-level helper permits non-finite values, it must not be an advertised member-design route. |

Patterns not to copy blindly:

- StructuralCodes explicitly documents that some section calculations are
  unitless and require a consistent unit system. StructLib's unit-bearing
  canonical names are safer for its intended external audience and should be
  strengthened, not removed.
- A global mutable active design code is convenient in a general multi-code
  library but would weaken StructLib's per-result IS 456 provenance. Keep code
  identity explicit in results and requests.
- Object composition does not replace domain validation. The main lesson is a
  curated journey and consistent result/exception model, not merely more
  classes.

## 8. Target external public contract

Every advertised member-design route should meet all of these rules before a
future readiness claim:

| Contract dimension | Required behavior |
|---|---|
| Finite/type | Reject booleans used as numbers, `NaN`, and infinities before calculation |
| Physical geometry | Require positive dimensions, cover/bar/stirrup values where physical, and valid relations such as `0 < d < D` and a positive torsion core |
| Actions | Use named non-negative magnitude inputs by default; signed actions must use explicitly signed fields with documented axis conventions and normalization |
| Materials/code domain | Enforce the route's advertised grade/table domain at the public boundary |
| Identity/provenance | Require non-blank member, case, story, and evidence references where the result claims traceability; never invent them silently |
| Categorical values | Use enums/Literals or strict strings; errors list the exact allowed values and rejected value |
| Collections | Require correct element types, non-empty cardinality where needed, unique identities, and consistent single/multiple-case semantics |
| Invalid versus inadequate | Invalid intake raises a validation/contract error and produces no design; a valid but inadequate section returns structured `FAIL` |
| Composition | Every downstream consumer validates its direct boundary; a valid combined result can flow naturally into BBS/report/export without manual attribute ceremony |
| Results | Canonical results expose a consistent status, review boundary, serialization method, provenance, and compatibility property where needed |

Identity must remain semantically precise: `beam_id` identifies a member and
`case_id` identifies an action case. The repair must not alias one to the other.

## 9. Implementation-ready repair packets

### Packet A — fail-closed public calculation chain (P0)

1. Introduce or extend shared beam validators for actions, geometry, identity,
   and detailing scalars. Apply them at `design_beam_is456`,
   `check_beam_is456`, `detail_beam_is456`,
   `design_and_detail_beam_is456`, and `smart_analyze_design`.
2. Validate `BeamDetailingResult` objects at `compute_bbs` intake and accept a
   valid `DesignAndDetailResult` through an explicit adapter.
3. Freeze torsion action semantics as non-negative magnitudes for the current
   API, enforce `0 < d < D`, positive cover/stirrup/core geometry and supported
   material grades, remove safety-changing minimum clamps, and correct the
   width error message.
4. Reject negative unified-column `Mux_kNm`/`Muy_kNm`; keep signed end moments
   (`M1*`/`M2*`) separate and document their convention.
5. Add outcome-focused regressions for every `P0` finding before any API polish.

Owned findings: `EXT-BEAM-001` through `008`, `EXT-DETAIL-001/002`,
`EXT-BBS-001`, `EXT-TORSION-001` through `005`, `EXT-COLUMN-002`, and the
safe-result portion of `EXT-TYPED-001/003`.

### Packet B — structured input and JSON truth

1. Give `BeamGeometryInput`, `MaterialsInput`, `LoadsInput`,
   `LoadCaseInput`, and `DetailingConfigInput` shared finite/domain validation.
2. Replace `a or alias` lookups with key-presence resolution so zero remains a
   value. Parse booleans strictly and reject unknown/ambiguous values.
3. Require imported member identity rather than defaulting to `BEAM`/`STORY`.
4. Resolve the one-case `load_cases` contract and reject conflicting `loads`
   plus `load_cases` unless an explicit precedence rule is documented.
5. Make column supplied reinforcement required on the check route, or create a
   separately named steel-selection/design workflow.

Owned findings: `EXT-TYPED-001` through `007`, `EXT-ID-001`, and
`EXT-COLUMN-001`.

### Packet C — one discoverable public style

1. Publish one canonical request/result journey for beam, column, slab, wall,
   stair, deep beam, flat slab, and each supported footing family.
2. Root-export supported request builders for evidence-heavy workflows, or
   provide equivalent validated `from_dict`/JSON schemas and full examples.
3. Add explicit-unit canonical torsion and footing aliases while retaining old
   signatures as documented compatibility wrappers with deprecation policy.
4. Standardize public enum/contract errors and result status/serialization.
5. Keep `beam_id` and `case_id` distinct.

Owned findings: `EXT-API-001/002`, `EXT-BUILDER-001`, `EXT-ENUM-001`,
`EXT-BBS-002`, and `EXT-TORSION-006`.

### Packet D — outsider-success documentation and release truth

1. Correct repository, wheel long-description, badge, and release-history facts
   for the actually published `0.24.0a1` artifact.
2. Generate public signature blocks from the live classified surface and fail
   documentation checks on drift.
3. Create a short cookbook with exact imports and one executable recipe per
   supported family, including BBS chaining, enum values, basis references,
   review flags, and expected PASS/FAIL/HOLD interpretation.
4. State that plain pip selects the stable release; show an exact prerelease pin
   and verify it in a clean environment.
5. Execute all public cookbook snippets against the built wheel in CI.

Owned findings: `EXT-RELEASE-001`, `EXT-INSTALL-001`, and `EXT-DOC-001`.

### Packet E — make the audit hard to evade

1. Extend the advertised-entry-point inventory from CLI commands to every
   README/cookbook Python workflow and its direct downstream consumer.
2. Define parameter contracts as data: finite/type, sign, physical range,
   code domain, relation, identity, enum, collection, and consumer rules.
3. Generate adversarial tests from that contract for direct source and exact
   wheel. Recursively audit request-object fields rather than marking a whole
   object proven from one local guard.
4. Generate the public-route safety target list from the advertised manifest;
   retain hand-written tests for relational and engineering-specific cases.
5. Make unresolved validation on an advertised route a release failure, or
   require an explicit owner waiver naming the route, parameter, risk, and
   expiry. Do not let a generic `PARTIAL` warning coexist with an unqualified
   readiness statement.
6. Continue every valid/invalid producer case through BBS, report, and export
   consumers to detect silent omission and late crashes.

## 10. Minimum regression matrix for the next implementation

The following test names are an implementation checklist; names may be adapted
to local modules, but the asserted outcome must not weaken.

| Proposed regression | Required assertion |
|---|---|
| `test_combined_beam_rejects_nonfinite_or_nonpositive_span` | Every `-1`, `0`, `NaN`, `+Inf`, `-Inf` case raises `DimensionError`/`ValidationError`; no result exists |
| `test_all_advertised_beam_routes_reject_negative_action_magnitudes` | Design-only, compliance, combined, and smart routes reject negative `mu_knm` and `vu_kn` |
| `test_direct_detailing_rejects_invalid_geometry_cover_and_stirrups` | Direct detailing rejects invalid span, cover, diameter, and all three spacing zones |
| `test_bbs_validates_direct_items_and_accepts_combined_result` | Invalid detailing is rejected before item generation; valid combined result produces the same nine items as `[result.detailing]` |
| `test_torsion_rejects_negative_actions_and_invalid_closed_core` | Negative actions, non-positive cover/diameter, `d>=D`, invalid core, and unsupported grades raise before equations |
| `test_unified_column_rejects_negative_applied_moment_magnitudes` | `Mux_kNm`/`Muy_kNm<0` raise rather than being replaced by minimum moments |
| `test_structured_beam_inputs_reject_nonfinite_values_at_construction` | Every numeric field class rejects `NaN`/infinity and boolean-as-number |
| `test_detailing_config_from_dict_is_strict_and_zero_preserving` | String booleans and invalid spacing reject; valid numerical zero is not treated as a missing key where zero is allowed |
| `test_beam_input_requires_identity_and_supports_one_load_case` | Missing/blank identity rejects; exactly one `LoadCaseInput` follows the documented path |
| `test_public_enum_errors_include_field_value_and_allowed_values` | Wall/stair/deep/flat/foundation categorical errors have one structured shape |
| `test_published_cookbook_executes_against_exact_wheel` | Every documented recipe imports from the wheel and reaches its documented result/status |

Property-based coverage should then generate boundary vectors from the public
contract registry. It supplements, rather than replaces, the fixed engineering
regressions above.

## 11. Acceptance gates and present verdict

The library can move from `PARTIAL / ALPHA ONLY` toward external readiness only
when all of these are true:

1. Every `P0` reproduction rejects invalid intake before calculation and the
   exact-wheel regression is locked.
2. The advertised Python surface has zero unowned validation parameters for
   the frozen release scope; unrelated low-level helpers may remain explicitly
   compatibility/internal.
3. Producer-to-consumer tests prove no invalid detail can silently lose BBS,
   report, or export content.
4. One clean-environment cookbook recipe per supported family passes against
   the wheel, and signature/documentation drift is zero.
5. Public metadata names the artifact that pip actually installs and makes the
   prerelease/stable distinction explicit.
6. Focused tests, quick gate, broad package gates, exact-wheel UAT, hosted
   checks, and required professional review evidence all pass for the frozen
   candidate. A green software gate remains separate from professional design
   approval and owner release authorization.

Current decision:

| Use level | Verdict |
|---|---|
| Research/portfolio Alpha with exact pin, bounded cases, and expert review | Usable with the documented limitations |
| Misuse-resistant default for students or junior engineers | **No** — safe-looking invalid beam, torsion, column, and BBS outcomes block it |
| Predictable external Python API for evaluators | **Not yet** — canonical journey, errors, builders, and release truth need Packets B-D |
| Consultant daily driver or construction/production authority | **No** — Alpha status, P0 intake gaps, case bounds, and qualified review requirements remain |

This audit packet is complete as an implementation-planning artifact. The
library itself remains `PARTIAL / ALPHA ONLY`; no code fix or release approval
is asserted by this document.
