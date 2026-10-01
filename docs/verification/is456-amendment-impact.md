---
owner: Main Agent
status: active
last_updated: 2026-10-01
doc_type: reference
---

# IS 456 Amendment 3-6 source and supported-caller reconciliation

The original documentation packet identifies two supported-slab discrepancies and
retains the unresolved edition and applicability qualifications. It changes no
calculation code. The accepted PR #1020 numerical candidate remains unchanged
at merge commit `32576ae0893bc246de152e6e9912efec89642717`.

The separately authorized
[bounded slab correction packet](slab-issued-amendment-corrections.md) implements
those two findings. The matrix rows, diagnostics and owner hashes below retain
their original numerical baseline; they do not describe the corrected candidate.

The [dated source inventory](is456-official-source-inventory.json) binds the
official Fourth Revision status, six numbered amendments and two controlled
PDF hashes. All 20 physical Amendment 3-6 pages were visually inspected: 18
content pages and two blank versos. The [impact matrix](is456-amendment-impact.json)
indexes 95 instruction blocks, including their numbered subtargets: 18 in A3,
33 in A4, 25 in A5 and 19 in A6. Original prose, images and watermark details
remain private. The source collection is not uniformly consolidated: its base
PDF47/printed46 retains 450 mm while appended A3 PDF112/printed2 substitutes
300 mm for Cl. 26.3.3(b)(2).

## Supported caller coverage

The matrix freezes 13 family journeys and 25 advanced exports from the current
facade registry, capability boundaries and API classification. Each of the 95
rows assigns all 38 callers exactly one disposition through a default and
disjoint overrides: 3,610 source/caller dispositions. This count includes
explicit unknowns and cases outside the changed provision; it is not a count
of qualified cases. Every caller has its actual implementation owner; every
disposition has scope/owner anchors whose file hashes bind this source commit.
Shared material eligibility is retained separately from construction-process
exclusions. The two geometry-only bearing/sizing primitives have no RC material
or reinforcement calculation to qualify.

The supported coefficient slab routes retain Tables 12/13/26/27 and their
declared case restrictions. A4's redistributed panel-moment rule does not
extend routes that explicitly require no redistribution. Table 21 and Annex B
working-stress changes are distinguished from limit-state bond and the selected
elastic serviceability material law. Annex F remains a beam serviceability
owner; it does not close slab direct deflection or crack width.

## Outcome-changing findings and existing conformance

| Row and primary source | Current supported outcome | Disposition |
|---|---|---|
| AMD3-014; A3 PDF112/printed2; Cl. 26.3.3(b)(2) | Complete one-way slab with `d=125 mm`, distribution bars `14@400 mm`: detailing reports adequate using a 450 mm cap. The amended maximum is `min(5d,300)=300 mm`. Continuous/two-way shared distribution owners also retain 450 mm. | Confirmed discrepancy; demonstrated through the complete one-way service. Overall professional/construction approval remains false. |
| AMD5-022; A5 PDF125/printed5; Cl. 40.2.3.1; Table 20 PDF74/printed73 | Solid M20 slab, `V=200 kN`, `b=1000 mm`, `d=100 mm`: `tau_v=2 N/mm2`. Required maximum is half of `2.8`, or `1.4 N/mm2`; current owner returns 2.8 and the wrong remediation classification. | Confirmed limit/classification discrepancy. `safe_without_reinforcement` already returns false; an unsafe overall PASS was not demonstrated. |
| AMD3-013; A3 PDF112/printed2; Cl. 26.2.5.1(a) | Canonical and advanced beam detailing restrict generated longitudinal bar choices to 32 mm and reject 36 mm. | Current conformance in those generated workflows. Direct low-level lap-helper acceptance above 32 mm does not establish a promoted caller defect. |
| AMD3-017; A3 PDF112/printed2; Cl. 29.3.4 | Existing deep-beam owner and accepted ledger use corrected Cl. 32.5. | Current conformance; accepted repair and evidence reused unchanged. |
| AMD4-029; A4 PDF119/printed5; Cl. 35.3.2 | Canonical beam crack contract uses 0.1 mm for VERY_SEVERE/EXTREME exposure. | Current conformance within explicit Level-A beam inputs. Other bindings and direct slab crack width retain their matrix limits. |
| AMD6-018; A6 PDF3/printed3; Cl. 41.3.2/41.4.2 | Composed rectangular torsion derives equivalent moments and designs both required longitudinal faces. | Current conformance within the existing bounded torsion composition. |

The exact diagnostic inputs, independent arithmetic and actual results are in
`read_only_diagnostics` in the matrix. Simulated review acknowledgements in the
spacing diagnostic are labelled diagnostic fixtures; they are not engineering
approval. No tests were added during this source review.

The basic `design_one_way_slab_is456` export also delegates to the same
provided-bar checker and is affected by AMD3-014. Its independently replayed
`d=125 mm`, `14@400 mm` input returns a 450 mm maximum and adequate detailing
on the original numerical baseline. It performs no shear check, so it is not
an AMD5-022 shear consumer. The flexure-only `design_two_way_slab_is456` remains
distinct from both provided-bar and shear consumers.

## Remaining qualifications

- A1-2 cumulative provision/caller coverage is not requalified here. Their
  presence and accepted historical anchors do not close the full six-amendment
  impact gate.
- A4 Table 2 Note 2 requires separate substantiation above M60. Column and
  advanced detailing accept M80; their generic review flag and numeric range
  checks do not supply that substantiation. This is unresolved applicability,
  without a demonstrated numerical mismatch.
- Material production, cement/admixture families, coatings and manufacturer
  steel properties require their declared physical eligibility evidence.
  A6's epoxy-coated bond basis supersedes A4's earlier table-value basis.
  Combined/strap cases explicitly exclude coated bars; generic bond helpers
  do not qualify a new coated material domain.
- Staircase distribution spacing, foundation main/distribution classification
  and solid-slab-like shear applicability require the exact owner/case evidence
  identified in the matrix before their conclusions can be closed.
- Beam placement notes also reach torsion/strap beam composition; untraced
  member bindings remain unknown. The general crack limit requires a verified
  crack owner or an explicit held-crack boundary. A foundation family name
  alone does not resolve solid-slab maximum-shear applicability.
- A4 Cl. 40.5.2 corrects total shear-reinforcement notation for sections close
  to supports. Its accumulated reinforcement/caller binding remains unverified;
  vertical-stirrup spacing alone does not establish conformance to that rule.
- AMD5-018's new formwork strength clause references table columns that do not
  match the simultaneously replaced table's labels. AMD6-002 does not identify
  the subsequent clause to renumber. These source interpretations remain
  unresolved; neither is repaired by guessing.
- Installed Windows/ETABS/Excel/XLL evidence, finite creep histories,
  arbitrary reinforcement layouts and manufacturer steel-family applicability
  retain their existing gates. Hosted platform tests do not close them.

## Proposed next correction packet

Subject to a separate explicit implementation scope, correct the demonstrated
slab distribution cap and solid-slab maximum-shear classification in their
actual owners. Apply half of Table 20 locally to the supported solid-slab check;
retain the shared table and beam/torsion rules. Reconcile the exact affected
callers, source references and independent boundary evidence in one bounded
candidate. Staircase, foundation and flat-slab extensions need separate traced
evidence before inclusion.

Acceptance is finite: the 400 mm provided distribution case fails the amended
300 mm check; the M20 `tau_v=2` case reports maximum 1.4 and
`exceeds_maximum_shear_stress`; affected promoted results preserve provenance
and their existing approval/HOLD boundaries; focused evidence and essential
independent review pass on the frozen correction candidate. This documentation
packet authorizes no formula edit, publication, new PR, merge or release.
