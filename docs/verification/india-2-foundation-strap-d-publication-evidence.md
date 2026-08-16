---
owner: Main Agent
status: active
last_updated: 2026-08-16
doc_type: reference
task: INDIA-2-FOUNDATION-STRAP-D
---

# INDIA-2-FOUNDATION-STRAP-D Publication Evidence

## Published boundary

`POST /api/v1/design/strap-footing/property-line` is a thin typed transport
over the canonical `design_property_line_strap_footing_is456` service accepted
in STRAP-C. The nested request forbids unknown and non-finite values, requires
actual JSON booleans for every topology, isolation, approval, and review
boundary, and admits only the frozen property-line two-footing contract. The
router converts the transport models into the existing domain types, delegates
once to the public service, and performs no engineering arithmetic.

The typed response exposes the complete action and strength disposition:
geometry, service and factored reactions, equal net and gross pressure,
equilibrium, clear-strap shear/moment, exact stress-block flexure, minimum and
provided steel, side-face steel, Table 19/20 shear and vertical stirrups,
spacing, cover, bilateral anchorage, exact provenance, supported and held
cases, qualified-review requirement, and false complete-engineering-approval
flag. A valid in-domain inadequacy remains HTTP 200 with aggregate `FAIL`;
unsupported scope returns the maintained safe HTTP 422 envelope.

## Capability and semantic truth

The canonical capability registry publishes exactly one `strap_footing`
workflow: `design_property_line_strap_footing_is456`. Its supported case is
exactly two separate rectangular constant-depth footings on soil with one
property-line exterior square column, one centred interior square column, and
one straight prismatic no-soil-contact strap under approved equal uniform net
pressure and common-factor vertical actions.

The semantic contract names the nested geometry, actions, external approvals,
materials, reinforcement, action, flexure, side-face, shear, review, and
approval meanings. `PASS` means that the bounded bearing and every represented
strap strength and detailing comparison passes. It does not represent footing-
slab or connection design, soil capacity or settlement calculation,
construction approval, or professional approval.

The deterministic Indian-code manifest promotes strap footing from held to
supported only after the G0-D chain, public workflow, route, capability,
semantic contract, exact clauses and sources, benchmark, and tests are
present. Live deterministic truth becomes 13 supported / 8 held with 81/81
directly tested endpoints. Focused family acceptance remains a separate next
packet and does not widen this supported case.

## Retained holds

Automatic footing sizing or slab/transfer/connection design, unequal or
nonuniform pressure, strap soil bearing, alternate layouts, column moments,
lateral or seismic actions, uplift, reversal, independent factoring or
patterning, nonlinear soil response, torsion, deep/haunched/skewed/crossed or
multiple straps, coated/bundled/spliced/curtailed bars, pile caps, raft
foundations, React, release, construction approval, and professional approval
remain held.

The bounded software result always requires qualified engineering review and
never grants complete engineering approval. Public distribution permission is
already recorded; no source PDF, scan, page image, watermark, or protected
clause prose is added by this packet.

## Verification boundary

Direct transport tests cover the frozen `PASS` benchmark, strict unknown,
non-finite, non-boolean, and held-scope rejection, safe domain-error mapping,
JSON-safe valid `FAIL`, typed OpenAPI success schema, and main-app mounting.
The focused packet gate also covers all strap G0-D tests, public workflow,
capability and semantic contracts, deterministic manifests, exact OpenAPI
drift, architecture/import/link/index checks, source binding, token efficiency,
and the quick gate. Required hosted checks must pass on the unchanged reviewed
head before integration.

All 6 direct D tests, all 85 cumulative strap A-D tests, and the 143-test
focused strap/public-contract selection pass. Black, Ruff, focused mypy, and
Bandit pass. Architecture reports 0 violations across 200 files; circular-
import analysis reports none across 181 files/147 modules; import validation
reports 0 broken internal imports across 647 Python files and 2,054 internal
imports. The three API contract checks pass. Independently reviewable OpenAPI
drift is limited to one new path and 20 new strap-footing schemas; no existing
path or schema changed. The deterministic snapshot contains 81 endpoints and
360 schemas.

Using the accepted cadence: focused gates run for every packet, with the broad
Python suite and full 30-check repository gate only at the final INDIA-2
integration boundary unless a confirmed repository-wide failure forces them
earlier. The next packet after D integration is a fresh acceptance-only lane;
no pile-cap or raft work begins in D.
