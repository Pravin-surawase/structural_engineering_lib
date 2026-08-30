---
owner: Main Agent
status: active
last_updated: 2026-08-30
doc_type: spec
complexity: advanced
tags: [public-api, signatures, documentation, examples, openapi, etabs, compatibility]
---

# LIB-PRO-015 Professional API and Documentation Renewal Plan

## 1. Decision and intended outcome

The library has strong calculation coverage and evidence controls, but its
external product surface still reflects several generations of growth. The
next renewal programme will make the supported library easier to discover,
call, document, integrate, and migrate without rewriting accepted engineering
owners or breaking retained callers.

The intended outcome is:

1. one unambiguous recommended Python namespace for new engineering workflows;
2. short, typed, unit-explicit, semantically named public operations;
3. compatibility wrappers that remain usable but are visibly separate from the
   recommended surface;
4. generated, searchable, ETABS-style reference pages bound to live code;
5. executable examples for every promoted workflow and appropriately scoped
   examples for expert functions;
6. complete request, result, error, evidence, and migration documentation;
7. an ETABS wrapper catalogue bound to installed API metadata and explicit
   side-effect guards; and
8. automated checks that fail when signatures, documentation, examples,
   OpenAPI, or migration metadata drift.

This document is an audit and implementation plan. It authorizes no runtime
change, public signature break, compatibility removal, dependency addition,
ETABS mutation, release, or professional-use claim.

## 2. Relationship to accepted programmes

`LIB-PRO-012` and `LIB-PRO-013` correctly introduced strict common contracts,
11 family-facade modules covering 13 journeys, compatibility classification, generated family schemas, and
exact-wheel recipes. `LIB-PRO-014` then closed two cumulative main-process
controls. This plan does not reopen their accepted calculation or evidence
results.

It addresses the remaining product-quality gap those programmes exposed but
did not fully close: the recommended facades and reference system are not yet
professional at the individual operation and field level, and the current API
documentation gate proves name presence rather than documentation correctness.

The separately authorized ETABS W3 campaign remains the owner of ETABS demand,
analysis, and optimization contracts. This plan may document accepted W3
operations and wrappers; it may not expand the W3 getter/setter or model-mutation
scope.

## 3. Bound current baseline

The final audit baseline is `origin/main` commit
`17494b53c84c273f4eef1d3d9224f234186d3eca` (tree
`9b89431b8ecce1cee9e132780869945727b8fa24`), after accepted W3D/E/F and W3R
integration plus the resolved-merge hook/API-manifest repair (PR #911).
Counts below are reproducible from that exact source and
frozen in the [machine-readable audit evidence](../verification/lib-pro-015-professional-api-audit-evidence.json).

| Surface | Current evidence | Product implication |
|---|---:|---|
| Root public functions | 117 | Too large to serve simultaneously as beginner discovery, expert reference, and compatibility namespace |
| Root functions missing a docstring | 9/117 | Some public IDE entries have no purpose or contract at all |
| Root functions with an `Example:` or `Examples:` docstring section | 41/117 | A user cannot rely on IDE help for a runnable call |
| Root functions with a parameter-doc section | 63/117 | Public hover/reference content is incomplete |
| Root functions with a return-doc section | 63/117 | Public hover/reference content is incomplete |
| Root functions with a documented raises section | 36/117 | Failure behavior is often undiscoverable |
| Root functions with more than 12 parameters | 17 | Several calls expose orchestration data as long scalar lists |
| Root functions with an unsuffixed `fck`, `fy`, `b`, or `d` parameter | 26 | Legacy dimensional names and unit-bearing names coexist |
| Root signatures mentioning `Any` | 17 | Type checkers and generated reference cannot explain accepted shapes |
| Root functions returning `dict`, `tuple`, or `list` annotations | 23 | Consumer fields and status semantics are not consistently discoverable |
| Canonical family-facade function projections | 41 | This is the correct-sized recommended surface to improve first |
| Family-facade functions missing docstrings | 33/41 | The newly recommended surface is less documented in IDEs than several legacy functions |
| Family-facade functions with examples/Args/Returns/Raises sections | 0/41 | Generated `mkdocstrings` pages cannot yet become complete professional references |
| Family request-field leaves | 562 across 13 journeys | The machine contract is strong, but its human reference is a dense aggregate table |
| OpenAPI | 97 operations, 96 paths, 543 schemas, 4,255 direct schema properties | Breadth is substantial and needs generated field-level documentation |
| OpenAPI operation descriptions | 17 operations missing | The affected endpoints include workflow, Excel, and ETABS bridge journeys |
| OpenAPI property descriptions | 3,348/4,255 missing | Unit-bearing names alone do not explain basis, range, provenance, or status |
| OpenAPI inline property examples | 148/4,255 | Swagger/ReDoc do not provide a representative payload for most fields |
| Human API reference | 4,780 manually composed lines | It mentions every root symbol, but mixes manual prose, old signatures, compatibility APIs, VBA/Excel history, and current workflows |
| Auto API index | Selected service, kernel, insight, and visualization modules | It omits the recommended 11 family-facade modules and newer W3/gravity surfaces |

These are inventory signals, not a claim that every long signature or typed
container return is defective. Section counts use complete Google-style section
header lines; both singular and plural example headers count. The earlier saved
draft accidentally counted only singular `Example:` headers. Module count (11)
and workflow-journey count (13) are distinct; the evidence now records both.

### 3.1 Decisive documentation-control defect

`./scripts/python_runtime.sh scripts/check_api.py --all` passes on the baseline,
but its Python documentation check only searches `docs/reference/api.md` for an
`api.<symbol>` token or a textual `def <symbol>(` occurrence. It does not
compare the documented and installed signatures, parameter descriptions,
return type, raises contract, examples, maturity, or replacement path. Its
`--signatures` selector checks React call sites against OpenAPI routes, not
Python reference signatures.

This is the confirmed root cause of the gap between the repository's written
documentation standards and the current published reference. The standards
already require complete Google-style public docstrings and runnable examples;
the maintained gate does not enforce them.

### 3.2 Discoverability conflict

The quickstart and top-level README recommend
`structural_lib.design.is456.<family>`, while
`docs/reference/api-levels.md` still calls the 117-function package root or
`structural_lib.services.api` the recommended Level 1 API. Both routes work,
but a new user should not need to choose between two differently described
"recommended" surfaces.

### 3.3 ETABS reference conflict

CSI's current developer page and OAPI FAQ say the installed CHM is the API
documentation authority. The accepted W3B evidence further binds ETABS 23.3.1
to the installed managed assembly, x64 type library, generated `comtypes`
metadata, output order, and Python container shape. Accepted W3C adds a
transport-neutral, complete-or-no-result catalogue adapter for that exact
operation matrix; it does not itself add live model evidence. Accepted
[W3D evidence](../verification/etabs-w3d-live-catalogue-and-demand-evidence.json)
now proves the bounded live catalogue/demand read, including the separately
repaired initial-condition sentinel and raw auto-flag semantics. Accepted
[W3F evidence](../verification/etabs-w3f-installed-signature-evidence.json)
adds 38 static signatures and a readback adapter; that is not blanket installed
live acceptance for W3F. The reference must preserve these distinct levels.

The tracked `docs/reference/vendor/etabs/README.md` predates those controls. It
calls its extracted CHM the latest API, recommends `RunAnalysis`, mentions
`GetPresentAnalysisStatus`, `SapModel.GetUnit`, `PropFrame.GetUnits`, and a
retired Streamlit handoff, and does not carry the current W3 side-effect and
installed-version gates. The extracted CHM contains `RunAnalysis`, but the
other named convenience methods were not found in the tracked CHM index. The
README must therefore be treated as stale integration guidance, not wrapper
authority.

### 3.4 Representative signature hot spots

The long-signature finding is concentrated enough to sequence, not a reason for
a wholesale rewrite.

| Current function | Top-level parameters | Specific product problem | Planned treatment |
|---|---:|---|---|
| `design_two_way_slab_panel_is456` | 40 | Topology, coefficient provenance, loads, materials, four reinforcement zones, torsion, and serviceability review are flattened | Group accepted domain owners into typed topology, actions, reinforcement, and review-evidence requests |
| `design_continuous_one_way_slab_is456` | 32 | Coefficients and their approval evidence compete with geometry and reinforcement in one call | Typed coefficient/evidence and reinforcement groups; retain scalar wrapper |
| `design_two_way_slab_panel_builtin_is456` | 31 | Built-in source selection is encoded mainly by a second long function | One canonical request with an explicit coefficient-source variant |
| `detail_beam_is456` | 24 | Three-station reinforcement and detailing preferences are scalar repetitions | Named station reinforcement plus detailing-policy request |
| `design_flanged_beam_is456` | 24 | Identity, flange geometry, actions, shear, serviceability, and torsion are flattened | Reuse common member/section/action/evidence groups |
| `design_column_is456` | 19 | Mixed `Pu_kN`/`Mux_kNm`/`Asc_mm2` spelling, legacy `fck`/`fy` aliases, and `dict[str, Any]` result obscure that this checks supplied steel | Canonical `check_supplied_steel(request) -> typed result`; compatibility wrapper preserves the old call |
| `smart_analyze_design` | 17 | Four booleans and a generic weight mapping form an implicit analysis policy | Named analysis-options/policy type and typed weights |
| `check_column_ductility_is13920` | 17 | Explicit inputs still return an untyped `dict` | Typed ductility result with stable issue/status fields |
| `extract_etabs_result_catalogue_v1` | 2 | The accepted W3C adapter exposes the provider boundary as raw `Any` | Define a narrow structural provider protocol while preserving dynamic COM adaptation behind the service boundary |

The evidence inventory contains all 17 root functions above the 12-parameter
threshold. Packet S1 freezes the reusable grouping primitives; F1-F3 migrate
families without copying formulas.

## 4. Root causes

| Root cause | Confirmed manifestation | Corrective design |
|---|---|---|
| API generations accumulated through root re-exports | 117 root functions, 26 functions with selected unsuffixed dimensional parameters, mixed result shapes | Curated recommended facade plus classified expert and compatibility namespaces |
| Strong machine schemas were not projected into per-operation human pages | 562 family leaves exist, but the reference is one dense aggregate file | Generate one module/operation/type page from the maintained registry and live docstrings |
| Documentation gates check presence rather than truth | All current checks pass despite 33/41 facade functions lacking docstrings | Exact-wheel signature, section, example, and migration validation |
| Convenience builders flattened engineering data | 17 root calls exceed 12 parameters; slab calls reach 40 | Typed request groups and explicit builders; keep long calls only as compatibility wrappers |
| Compatibility and beginner discovery share the same visible namespace | Root API is both recommended and retained | Make compatibility explicit in docs and autocomplete without deleting it |
| REST schema generation lacks enough authored field metadata | 3,348 OpenAPI properties lack descriptions | Generate field descriptions, units, constraints, examples, and issue codes from one field contract owner |
| ETABS documentation was treated as static prose | Stale method names and mutation guidance survived newer installed evidence | Version-bound wrapper operation registry and generated guarded reference |

## 5. Research baseline and decisions

The programme adapts patterns from current primary or project-owned sources;
it does not add these libraries as dependencies merely because they are useful
benchmarks.

| Source | Useful pattern | Decision for this library |
|---|---|---|
| [NumPy routines by topic](https://numpy.org/doc/stable/reference/routines.html) | Concept-grouped reference and routine examples | `ADAPT`: group by supported engineering family and show compact examples |
| [SciPy public API guidance](https://docs.scipy.org/doc/scipy/reference/) | Public submodule namespaces rather than one giant root | `ADAPT`: `structural_lib.design.is456.<family>` is recommended; root remains compatibility |
| [NumPy module structure](https://numpy.org/doc/stable/reference/module_structure.html) and [NEP 23](https://numpy.org/neps/nep-0023-backwards-compatibility.html) | Recommended vs legacy namespaces and deliberate compatibility | `ADAPT`: published migration metadata and caller-bound deprecation; no blind removal |
| [Pydantic strict mode](https://pydantic.dev/docs/validation/latest/concepts/strict_mode/) | Boundary-specific strict validation | `ADAPT`: keep strict request construction and stable translated issues |
| [FastAPI response documentation](https://fastapi.tiangolo.com/advanced/additional-responses/) and [OpenAPI parameter guidance](https://learn.openapis.org/specification/parameters.html) | Typed success/error schemas, descriptions, and examples in generated OpenAPI | `ADAPT`: one semantic contract across Python, REST, and generated clients |
| [concreteproperties API](https://concrete-properties.readthedocs.io/en/stable/api.html) | Engineering-concept modules and analysis-specific result types | `ADAPT`: family modules and typed results |
| [sectionproperties API and examples](https://sectionproperties.readthedocs.io/en/stable/api.html) | Separate user journeys from exhaustive reference | `ADAPT`: cookbook plus generated per-symbol reference |
| [PyNite documentation](https://pynite.readthedocs.io/en/stable/) | Short domain navigation and model journey | `ADAPT` selectively; do not copy incomplete-doc limitations |
| [OpenSeesPy documentation](https://openseespydoc.readthedocs.io/en/latest/) | Broad command catalogue plus examples | `ADAPT` navigation; `REJECT` mutable global command state for design intake |
| [Diataxis](https://www.diataxis.fr/start-here/) | Tutorials, how-to guides, reference, and explanation answer different needs | `ADAPT`: stop mixing these content types in one API file |
| [Sphinx autodoc](https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html), [Sphinx doctest](https://www.sphinx-doc.org/en/master/usage/extensions/doctest.html), and [numpydoc style](https://numpydoc.readthedocs.io/en/v1.10.0/format.html) | Live signatures/docstrings and executable examples | `ADAPT` through the repository's existing MkDocs/mkdocstrings stack; no Sphinx dependency is required |
| [CSI developer page](https://www.csiamerica.com/developer), [CSI OAPI FAQ](https://web.wiki.csiamerica.com/wiki/spaces/kb/pages/2000456/OAPI%2BFAQ), and [official ETABS API method pages](https://docs.csiamerica.com/help-files/etabs-api-2016/html/15293a27-a035-e64b-a4b4-78356479aa98.htm) | Interface -> member -> syntax -> parameters -> return -> example hierarchy; installed CHM is current authority | `ADAPT`: generate wrapper pages from installed evidence; old web help is explanatory corroboration only |
| [Pint quantity wrappers](https://pint.readthedocs.io/en/latest/advanced/wrapping.html) | Optional dimension-aware boundaries | `HOLD`: explicit unit suffixes remain the contract; add no dependency without a measured safety/integration benefit |

## 6. Target public API architecture

### 6.1 Four visible levels

| Level | Namespace | User | Contract |
|---|---|---|---|
| Recommended workflow | `structural_lib.design.is456.<family>` | New engineering integrations | Typed request groups, strict parsing, typed result, stable issue/status protocol, complete examples |
| Expert calculation | `structural_lib.codes.is456.<topic>` | Engineers composing low-level checks | Pure math, explicit units/sign convention, result type or scalar meaning, code/source locator, focused example where non-obvious |
| Service/transport | `structural_lib.services`, CLI, FastAPI | Applications and automation | Orchestration, serialization, artifact and transport rules; not presented as a second calculation owner |
| Compatibility | package root, `structural_lib.services.api`, `structural_lib.api`, retained stubs | Existing callers | Delegation only, migration target, stability state, warning/removal policy where applicable |

Only the first level is called "recommended" in beginner documentation. Expert
modules are supported for their documented scope. Compatibility routes remain
public and tested, but they do not compete for first-use discovery.

### 6.2 Naming standard

Canonical Python names will use:

- lower snake case for parameters and fields;
- `_mm`, `_mm2`, `_kn`, `_knm`, `_nmm2`, `_kn_per_m`, `_kn_per_m2`, or
  `_percent` suffixes for dimensional values;
- `member_id`, `case_id`, `story`, and source/reference fields consistently;
- action names that preserve sign and basis instead of relying on an implicit
  absolute-value convention;
- verbs that describe the actual operation: `design`, `check_supplied_steel`,
  `detail`, `generate_bbs`, `build_request`, and `parse_request`; and
- version suffixes only on serialized/versioned contracts, not every ordinary
  helper name.

Legacy names such as `Pu_kN`, `Mux_kNm`, `Asc_mm2`, `fck`, `fy`, `b`, and `d`
remain available only through classified compatibility routes until a separate
removal authority is granted.

### 6.3 Signature standard

1. Canonical operations consume one typed request and return one typed result.
2. Canonical builders expose no more than 12 top-level arguments; evidence-heavy
   data is grouped into named immutable request objects rather than hidden.
3. Canonical facade signatures contain no raw `Any`, untyped `dict`, tuple
   protocol, or ambiguous boolean where an enum/status is clearer.
4. JSON/Python parsing accepts a named recursive `JSONValue`/mapping carrier,
   returns the typed request, and translates validation failures into
   `InputContractError` with stable issue paths/codes.
5. Defaults are allowed only when they are universal software behavior or a
   clearly documented standard default. Project/engineering assumptions remain
   explicit inputs.
6. Result types always separate intake, calculation completion, engineering
   `PASS`/`FAIL`/`HOLD`, and qualified-review state.
7. A compatibility wrapper delegates to the canonical owner and never contains
   a second formula.

### 6.4 Example canonical shape

The exact class names will be frozen in the first vertical-slice packet, but the
shape is:

```python
from structural_lib.design.is456 import beam

request = beam.build_request(
    identity=beam.MemberCase(member_id="B1", story="L1", case_id="ULS-1"),
    section=beam.RectangularSection(span_mm=6000, width_mm=300, overall_depth_mm=550),
    materials=beam.Materials(fck_nmm2=30, fy_nmm2=500),
    actions=beam.Actions(mu_knm=180, vu_kn=120),
    reinforcement=beam.ReinforcementBasis(
        effective_depth_mm=500,
        compression_steel_depth_mm=50,
        asv_mm2=100.53,
    ),
)
result = beam.design(request)
```

This is illustrative, not an implementation spelling decision. The packet must
reuse or migrate the accepted request/result owners rather than create a second
model hierarchy.

## 7. Documentation product

### 7.1 Information architecture

The MkDocs site will implement four distinct paths:

1. **Tutorials:** first beam, first family, first REST client, and first ETABS
   read-only integration.
2. **How-to guides:** family recipes, batch/CLI, error recovery, migration,
   Excel/ETABS evidence, and artifact generation.
3. **Reference:** one generated page per promoted module, function, request,
   result, error, enum, REST operation, and accepted ETABS wrapper operation.
4. **Explanation:** units, sign convention, status semantics, provenance,
   supported/held scope, compatibility, evidence classes, and professional
   boundaries.

The existing 4,780-line `docs/reference/api.md` becomes a short landing and
compatibility index. Hand-maintained signatures are retired in favor of
generated live signatures.

### 7.2 Required per-operation reference fields

Every promoted operation page contains:

- fully qualified import path and stability/classification;
- exact live signature and version introduced;
- purpose and supported/held engineering case;
- parameter table with type, units, range/domain, optionality, default basis,
  sign/axis, and provenance expectation;
- return type and field/status interpretation;
- stable exceptions/issues and whether calculation/artifact creation begins;
- assumptions, limitations, source/clause locators, and review boundary;
- minimal valid example;
- invalid-input example with exact issue code/path;
- engineering `FAIL` or `HOLD` example where meaningful;
- links to related high-level, expert, REST, and compatibility routes; and
- migration target for compatibility functions.

### 7.3 Example policy

"Example for each function" is applied by public role:

| Public role | Required example |
|---|---|
| Canonical workflow operation | At least one executable docstring example plus valid, invalid, and `FAIL`/`HOLD` cookbook journeys |
| Canonical request/result/enum | Construction or interpretation example on its reference page |
| Expert calculation function | One deterministic doctest or linked module example when behavior is not trivial |
| Compatibility wrapper | A short migration example and link to the canonical journey; do not duplicate a large recipe |
| Internal/private helper | No public-example obligation |

All promoted examples execute from the built wheel in an empty temporary
workspace. Output assertions check semantic fields and stable issue codes, not
fragile full `repr` strings.

### 7.4 Generator and gate design

Do not create a third public API manifest. Extend the maintained API
classification/workflow owners with documentation-class fields, then generate:

- module and symbol navigation;
- exact signature blocks;
- parameter/result/error tables;
- family and REST cross-links;
- compatibility/migration badges; and
- a machine-readable example inventory.

Replace the misleading `check_api.py --signatures` label or split it into clear
React/OpenAPI and Python-reference selectors. The Python documentation gate
must compare the exact built wheel against the generated reference and enforce:

- every promoted symbol classified and documented;
- exact signature equality;
- complete required docstring sections by public role;
- no undocumented canonical parameter/result field;
- every example registered and executable;
- no new documentation debt; and
- zero hand-edited generated output drift.

Existing debt is frozen in a temporary baseline during the first packet so the
gate blocks regression immediately. The baseline is removed family by family
and must be empty before the cumulative candidate.

## 8. OpenAPI and generated-client documentation

For every advertised REST operation:

1. bind it to a canonical Python workflow or explicitly classify it as
   transport/tooling-only;
2. author a summary, detailed description, request example, success example,
   structured invalid-input response, and engineering `FAIL`/`HOLD` response;
3. generate field descriptions, units, constraints, and enums from the same
   field contracts used by Python;
4. preserve operation IDs or publish a generated-client migration when a change
   is necessary;
5. compile and run the exact generated client against the exact OpenAPI head;
6. keep HTTP success separate from engineering status; and
7. document WebSocket/stream lifecycle, timeout, cancellation, and errors
   separately from request/response endpoints.

No `/api/v2` is introduced merely to improve documentation. A semantic break
requires a separately approved compatibility decision.

## 9. ETABS-style wrapper reference

### 9.1 Source hierarchy

For each supported ETABS version, evidence authority is:

1. installed signed application and exact version;
2. installed managed assembly and x64 type library;
3. installed CHM and generated wrapper metadata;
4. controlled live getter evidence where the packet authorizes it;
5. CSI's current developer/FAQ pages; and
6. old public web help only as historical corroboration.

No method is declared supported from name recall or an old web page alone.

### 9.2 Wrapper operation registry

Each accepted operation record contains:

- product/version and source hashes;
- CSI interface, method/overload, GUID/dispid, and managed signature;
- input order/defaults and output order;
- CSI return-code position and nonzero handling;
- Python/comtypes outer and SAFEARRAY shapes;
- present/database unit behavior;
- required model identity, lock, selection, and result state;
- side-effect class: `PURE_METADATA`, `READ_MODEL`, `READ_RESULTS`,
  `CHANGE_SELECTION`, `CHANGE_UNITS`, `RUN_ANALYSIS`, `MUTATE_MODEL`, or
  `SAVE/EXPORT`;
- current authorization and guard IDs;
- fake-provider test, installed-static test, and installed-live evidence state;
- typed wrapper request/result/error; and
- minimal guarded example.

### 9.3 Generated reference page

The page hierarchy mirrors the useful part of CSI's API help:

`ETABS version -> interface -> operation -> syntax -> parameters -> decoded
result -> return/error -> guards -> example -> evidence`.

It also adds what raw CSI help does not provide for this product: Python
container shape, stable wrapper errors, side-effect policy, source identity,
preservation requirements, and whether the operation is software-tested,
installed-static, installed-live, engineering-reviewed, or held.

The stale vendor README is replaced by an authority index. It must not recommend
`RunAnalysis`, unit/selection changes, model writes, or retired handoffs unless
the current ETABS packet explicitly authorizes and proves them.

## 10. Sourcebook and StructProof boundaries

- **Sourcebook:** may provide source-bound examples, comparison vectors,
  clause/table locators, assumptions, and discrepancy evidence. It remains a
  separate calculation/evidence project and is not imported at runtime.
- **StructProof:** may inform evidence presentation, review state, proof-step
  navigation, and qualified-review UX. Its schemas and approval state are not
  silently copied into this library.
- **Library:** owns runtime calculations, public Python/REST/CLI contracts,
  packaging, documentation, examples, compatibility, and software evidence.
- **Qualified engineer:** separately owns any professional review or approval.

Protected source prose and images do not enter generated public documentation.
Only normalized in-scope data, locators, provenance, examples, and owner-approved
distribution content are used.

## 11. Dependency-ordered implementation programme

Estimates are rough engineer-day classes for sequencing, not calendar promises.

### Packet D0 — documentation contract and exact-wheel gate (3–5 days)

**Scope:** freeze the public-role inventory; extend existing classification with
documentation obligations; implement exact-wheel signature/docstring/example
checks; rename the misleading current selectors; record current debt without
blocking unrelated work.

**Acceptance:** current counts reproduce; every promoted symbol has one public
role; the gate detects altered signatures, missing sections, stale examples, and
unowned symbols; new debt fails; no runtime behavior changes.

### Packet D1 — canonical facade reference vertical slice (4–7 days)

**Scope:** complete beam and column facade docstrings; generate their module,
operation, request/result/error pages; add valid, invalid, and `FAIL`/`HOLD`
examples; reduce `api.md` to a navigable landing/index for those routes.

**Acceptance:** exact wheel runs every example; IDE help is complete; generated
and live signatures match; no calculation/result golden changes.

### Packet S1 — canonical signature primitives and migration contract (4–7 days)

**Scope:** freeze common identity/material/action/reinforcement naming; define
typed JSON parsing; replace raw `Any` group arguments in the recommended facade;
freeze `build_request`/`parse_request` semantics; define compatibility wrapper
metadata and caller gates.

**Acceptance:** no `Any` or generic container result remains in the selected
canonical vertical slice; legacy calls still pass exact compatibility fixtures;
no formula is duplicated.

### Packet F1 — beam, torsion, column, and slab convergence (6–10 days)

**Scope:** apply S1 patterns to the highest-use families; replace misleading
operation verbs such as column `design` where the workflow is a supplied-steel
check; move long scalar construction to typed groups; complete references and
examples.

**Acceptance:** all promoted functions in these modules meet the signature and
documentation standards; existing callers and accepted goldens remain exact.

### Packet F2 — wall, staircase, deep-beam, and flat-slab convergence (5–8 days)

**Scope and acceptance:** same contract as F1, preserving every supported/held
topology and evidence acknowledgement.

### Packet F3 — isolated, combined, and strap-footing convergence (5–8 days)

**Scope and acceptance:** same contract as F1, with explicit geotechnical,
load, pressure, reinforcement, and qualified-review ownership; no automatic
assumption generation.

### Packet R1 — expert and compatibility reference (4–7 days)

**Scope:** classify the 117 root functions and expert module functions as
recommended shortcut, expert, compatibility, tooling, or held; generate their
reference/migration pages; add focused examples without promoting internal
helpers.

**Acceptance:** the root remains import-compatible; every visible route has an
owner, stability state, and replacement/related route; beginner navigation no
longer presents the root as the preferred starting surface.

### Packet R2 — OpenAPI, error, and generated-client documentation (5–8 days)

**Scope:** fill promoted operation/field descriptions and examples from the
common contract; document WebSocket/stream behavior; compile and run generated
clients.

**Acceptance:** every advertised field has a human description and unit/domain
decision; every promoted operation has request/success/invalid/engineering
examples; Python/REST status semantics reconcile.

### Packet E1 — version-bound ETABS wrapper reference (4–7 days)

**Prerequisite:** exact accepted W3 operation matrix and no overlapping W3
candidate on shared registry/docs paths.

**Scope:** convert accepted ETABS operation evidence into the wrapper registry
and generated reference; replace stale vendor guidance; add fake-provider
examples and installed-evidence badges. Do not expand operation authority.

**Acceptance:** every supported wrapper operation is version/source/shape/
side-effect/guard bound; no unproved method is advertised; Windows evidence
remains distinct from Mac/unit tests and professional review.

### Packet C1 — cumulative documentation/product candidate (3–5 days)

**Scope:** remove the temporary debt baseline; build the exact wheel and strict
docs site; execute all promoted examples and generated clients; run browser
search/navigation and copy-paste journeys; freeze migration and release truth.

**Acceptance:** Section 12 scorecard passes on one immutable artifact. Release
and professional review still require their own authorities.

**Total planning class:** approximately 43–72 engineer-days (the sum of the ten
packet ranges, correcting the earlier draft's understated total). Compatible packets
may be batched into fewer implementation cycles after shared-path and predecessor
inspection; their acceptance obligations do not disappear.

## 12. Cumulative acceptance scorecard

| Gate | Required outcome |
|---|---|
| Recommended namespace | One clearly labelled `structural_lib.design.is456.<family>` path; no contradictory beginner guidance |
| Canonical signatures | Zero raw `Any`, generic `dict`/tuple/list returns, hidden units, or ambiguous operation verbs in promoted functions |
| Constructor complexity | No canonical builder exceeds 12 top-level arguments; complex evidence remains explicit in typed groups |
| Canonical docstrings | 100% summary, parameters, returns, raises, examples, limitations/provenance where applicable |
| Canonical examples | 100% valid; invalid and `FAIL`/`HOLD` coverage for every promoted workflow |
| Expert/compatibility docs | 100% classified; every route has exact reference and related/migration destination |
| Exact-wheel truth | Generated signatures and examples match the installed candidate, not source-path imports |
| OpenAPI | 100% advertised operations and fields documented; request/success/error/engineering examples execute through generated client |
| ETABS wrapper | 100% advertised operations carry installed source, signature, decoded shape, return, units/state, side-effect, guard, and evidence status |
| Compatibility | Existing valid callers pass; any warning/removal has owner-approved migration and timing |
| Engineering truth | No golden calculation changes without a separately source-bound engineering packet |
| Documentation site | Strict build, links, search, navigation, copy-paste examples, and version/maturity truth pass |
| Cross-project boundary | Sourcebook/StructProof evidence is cited and transformed deliberately; no hidden runtime or approval coupling |

## 13. Prioritized finding register

| Finding | Severity/state | Main-process impact | Owner/packet |
|---|---|---|---|
| `LIB-PRO-015-DOC-GATE-001` | P1 `CONFIRMED` | Current checks pass stale/incomplete Python reference content | D0 |
| `LIB-PRO-015-FACADE-DOC-001` | P1 `CONFIRMED` | 33/41 recommended facade projections lack docstrings; none has a complete example contract | D1, F1–F3 |
| `LIB-PRO-015-SIGNATURE-001` | P1 `CONFIRMED` | Long, `Any`, legacy-unit, and generic-result signatures weaken autocomplete, type safety, and integration | S1, F1–F3, R1 |
| `LIB-PRO-015-DISCOVERY-001` | P1 `CONFIRMED` | Two surfaces are described as recommended; auto reference omits the actual family facade | D1, R1 |
| `LIB-PRO-015-OPENAPI-DOC-001` | P1 `CONFIRMED` | Most generated fields lack human meaning/examples despite schema breadth | R2 |
| `LIB-PRO-015-ETABS-REF-001` | P1 `CONFIRMED` | Stale guidance can lead implementers to nonexistent methods or unauthorized analysis/state changes | E1 |
| `LIB-PRO-015-ROOT-SURFACE-001` | P2 `CONFIRMED` | 117 root functions remain noisy even after facade introduction | R1; compatibility preserved |
| `LIB-PRO-015-DOC-ARCH-001` | P2 `CONFIRMED` | One long manual reference mixes tutorial, reference, history, and compatibility content | D1, R1, C1 |
| `LIB-PRO-015-QUANTITY-ADAPTER-001` | Hold | A quantity dependency may help units but has no demonstrated current outcome benefit | Separate future decision only |

No new engineering-calculation P0 was reproduced in this planning audit. That
does not upgrade software evidence into professional approval.

## 14. Stop conditions and non-goals

Stop a packet if:

- a proposed rename lacks an exact valid-caller and compatibility inventory;
- a documentation change requires guessing an engineering default, supported
  case, sign convention, or source basis;
- a new facade would duplicate calculation logic;
- an ETABS method lacks installed signature/output/return evidence;
- an ETABS example would cross the packet's side-effect authority;
- a generated/client change would silently break a stable operation ID or
  serialized schema;
- Sourcebook or StructProof ownership would be copied rather than explicitly
  consulted and transformed; or
- an active predecessor overlaps shared registry/generated/documentation paths.

Non-goals include:

- no immediate shrinkage of the package root;
- no wholesale signature rewrite;
- no automatic deprecation merely because a route is old;
- no NumPy, Pint, Sphinx, or other dependency addition from research alone;
- no formula, normalized table, supported-case, or engineering-status change;
- no ETABS analysis, setter, unlock, model save/write, or optimization expansion;
- no release/tag/publication; and
- no professional, engineering-use, or construction-use approval.

## 15. Immediate next action

After this plan is accepted and integration order is rechecked, execute Packet
D0 only. It is the lowest-risk root-cause packet: make the documentation
contract measurable against the exact wheel, freeze existing debt, and prevent
new drift before changing any public signature or facade spelling.

Do not start D0 while an active W3 candidate overlaps API classification,
compatibility-ledger, generated OpenAPI, `docs/reference/api.md`, task, or
session owners. Integrate the predecessor or explicitly rebind both candidates
first.
