---
owner: Main Agent
status: active
last_updated: 2026-08-16
doc_type: reference
task: INDIA-2-DEEP-D
---

# INDIA-2-DEEP-D Publication Evidence

## Published transport

`POST /api/v1/design/deep-beam/simply-supported` is a thin typed transport over
the canonical `design_simply_supported_deep_beam_is456` service. Its request
forbids unknown fields and non-finite numbers and requires every topology,
external bearing/nodal prerequisite, explicit unit-bearing quantity, and
caller evidence reference. The router performs no engineering arithmetic.

The typed response exposes effective span/classification, Clause 29.2 lever
arm, required/provided tie steel, placement, continuity, both anchorages, both
side-face directions, the bounded shear statement, exact provenance,
supported/held cases, qualified-review requirement, and false complete-
engineering-approval flag.

## Capability and semantic truth

The canonical capability registry now lists exactly one public `deep_beam`
workflow: `design_simply_supported_deep_beam_is456`. Its supported case is one
simply supported solid rectangular top-loaded Clause 29 member with caller-
supplied positive factored moment, provided reinforcement, and external
bearing/compression-nodal verification.

The semantic contract names the mm, kN m, N/mm2, boolean, result/status, and
approval meanings. It states that `PASS` requires classification, positive
tie, placement, continuity, both anchorages, both side-face directions, and
the external prerequisite. It does not represent bearing/nodal capacity or
professional approval.

Continuous/cantilever/negative-moment members, openings, dapped ends, corbels,
coupling or irregular members, prestress, hanging action, load/reaction
generation, bearing/nodal calculation, automatic sizing, bundles, splices,
transverse enclosure, serviceability, fire, seismic/IS 13920, generalized
strut-and-tie, nonlinear analysis, and FEM remain explicitly held.

## Deterministic truth and verification boundary

The Indian-code manifest promotes `deep_beam` from held to one bounded
implemented family only after the public workflow, typed route, capability,
semantic contract, clauses, sources, benchmark, tests, and A-D evidence are all
present. Its evidence chain includes DEEP-G0 and DEEP-A-D. This is a supported
software subset, not whole-standard completeness or professional approval.

Focused transport tests prove the exact hand benchmark, JSON-safe `PASS` and
valid-inadequacy `FAIL`, safe service-error envelope, unknown/non-finite and
held-topology rejection, external-verification enforcement, typed OpenAPI
schema, main-app mounting, and cross-surface capability truth. React and
release work are excluded.

The combined deep-beam, public workflow, semantic contract, clause,
traceability, Indian/API manifest, transport, and capability selection passes
157 tests. Black, Ruff, mypy, and Bandit pass; architecture reports 0
violations across 177 files and imports report 0 broken across 607 scanned
files. Deterministic truth is current at 10 supported and 11 held families;
actionable parity is 100 percent and all 78 endpoints are directly tested. All
three API checks, schema snapshots, all 1,180 internal links, touched indexes,
and quick gate 10/10 pass. Required hosted checks must pass on the unchanged
reviewed head before integration.

The broad Python suite and 30-check repository gate remain deferred to the one
whole-INDIA-2 closeout. At the owner's requested stop point, DEEP focused family
acceptance is the first task for the next work session; no flat-slab or
foundation work begins before it.
