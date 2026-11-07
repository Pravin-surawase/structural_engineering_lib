# Next Session Briefing

## Latest Handoff (auto)

<!-- HANDOFF:START -->
- Date: 2026-11-07
- Focus: 0.27.0 publication authorization handoff — use only the qualified replacement pair in 5c79c3b07dcb/dist. Final required check/review/merge facts are owned by PR #1063; publication remains unauthorized.
- Completed: R1–R5 source and installed repairs; all 18 replacement profiles PASS, with 408 tests per archive and preserved FAIL/HOLD controls. Independent final wheel reviews accepted; all 19 changed report PDF pages visually passed. Retained record binds the clean source, new hashes and rejected-candidate history. GitHub owns the final required hosted/integration gate.
- Recurrence controls: None encountered in S5. Historical RR-004 x36 remains unchanged.
<!-- HANDOFF:END -->

## Current boundary

| Release | Current state |
|---|---|
| **Current** | 0.26.0 is published and verified in the [release ledger](../getting-started/releases.md#v0260-published-and-verified). |
| **Next** | R1–R5 repairs and exact replacement archive qualification pass. Final required GitHub acceptance and separate publication authorization precede delivery. |

## Next work — final acceptance and publication handoff

**Selected goal:** `LIB027-REPAIR-QUALIFY`, started by the owner on
7 November 2026. The
[acceptance specification](library-usability-improvement.md#repair-goal--acceptance-history)
retains the agreed scope and authority. Source repairs, independent
installed review and replacement archive qualification pass. Final required
hosted/integration facts belong to PR #1063. Publication is not authorized.

1. Read PR #1063's immutable-head required PR and Weekly/cross-platform
   checks, independent review and merge facts. Complete any remaining gate.
2. Bind the accepted merge and unchanged Python/build/verifier inputs to the
   selected 5c79c3b07dcb archive pair; rerun retained-check on the accepted tree.
3. Report readiness and leave publication for separate owner authorization.

The five repair steps in the [detailed plan](library-usability-improvement.md#027-pre-release-repair-plan)
are completed implementation/qualification history, not instructions to
restart R1–R5 or rebuild a passing archive pair.

**Merge order:** this repair precedes draft
[research PR #1064](https://github.com/Pravin-surawase/structural_engineering_lib/pull/1064),
whose head is `97743f405ed8987a047c43dc6929ff5225b184d9` on base
`1c35d9485fa3499e69f1926657e91e84fe0d7bb8`. That proposal overlaps the shared
plan and must rebind to the accepted repair/current main before later
integration. Its existing draft already records this order. It does not
expand this repair or authorize its proposed implementation.

The [repair results](library-usability-improvement.md#repair-qualification-results--7-november-2026)
bind the new pair in `output/releases/0.27.0/5c79c3b07dcb/dist/`. Preserve the
original 9a78d2be9314 archives. The 423097e8 intermediate directory is invalid
for delivery; only its historical receipts remain valid evidence. New column layouts, arbitrary P–M–M
and broader beam member cases are outside this repair packet; 0.28 retains
the slab/footing theme. Keep professional and installed-native HOLDs visible.


Goal 1 froze and replayed the
[four section references](../verification/library-027-comparator-reference.md).
Goal 2 delivered the [beam comparison guide and example](../cookbook/python/beam-comparator-reference.md).
All 21 numerical outputs and both method identifiers passed using the
installed 0.26.0 wheel. The separate doubly reinforced member check returned HOLD.

Goal 3 delivered the layered rectangular section API and verified the
900 mm case and `xu = D` boundary. The example runs both depths and the
result keeps member and detailing acceptance unevaluated.
[Layered column guide](../cookbook/python/layered-column-section.md)

Goal 4 reconciled the single-layer and multilayer member examples across
JSON, BBS, and HTML. The supplied-beam controls recorded missing support
as HOLD and depth mismatch and insufficient steel as FAIL. Both full
member overload replays produced draft artifacts.
[Member guide and replay](../cookbook/python/ordinary-beam-member.md)

The owner selected beam and column closure for 0.27 and slabs and footings
for 0.28. Packet A qualified layered column sections with partial
compression and mixed diameters. Packet B qualified supplied inclined and
bent-up shear reinforcement and sagging flexure within the flange and in
the web. Packet C adds the physical four-corner column, independent x/y
benchmarks and matching JSON/HTML with overload, inadequate-tie and
missing-tie controls. Packet D1 corrects the torsion station basis. The
[D2 worked profile](../cookbook/python/physical-torsion-member.md) now supplies
physical load path, both-face direct tension anchorage, cage/hooks and draft
outputs. Its receiver boundary is section flexure/shear; bearing/contact,
receiver connections and foundations remain with the supporting-system owner.
D3 now adds its independently frozen transient service basis: permanent
G5 concentric, imposed Q3 at400/3mm, immediate after-finishes assessment,
supplementary cracked torsional stiffness, code edge-deflection limits and
indirect service stress/detail crack control. The full31-leaf case produces
issue_ready outputs; the original D2-only command remains HOLD. Nonzero
permanent torque, finite imposed duration and missing/asymmetric boundary
evidence remain HOLD. Follow the guide's actual source and model boundaries.
[LIB-13](https://pravinsurawase.atlassian.net/browse/LIB-13) owns Goal 5;
the local repair plan now precedes its publication handoff. This planning
task does not assert that external Jira/Confluence status was synchronized.
[Closure plan](library-usability-improvement.md#beam-and-column-closure-before-goal-5)

The [Packet E delivery record](library-usability-improvement.md#packet-e-implementation-plan--ordinary-sagging-t-beam-member)
and [guide](../cookbook/python/t-beam-member.md) now include actual T material,
all-six-bar cage/hooks, full-stress anchorage at both ends, separately owned
local flange provision, web shear, lateral restraint and actual-T service
evidence. Physical/effective flange widths remain distinct (1000/1000 mm
and 2500/2200 mm), with a 300 mm web. The complete flanged span/depth screen
does not calculate millimetre deflection. The Python zero-torsion admission
operation proves zero demand, not T torsion resistance. Native changes only
preserve the two new generic path-role metadata values.

The [qualification receipt](../verification/library-027-t-beam-qualification.json)
binds the source-matching development wheel (0.26.0 metadata), 13 installed
journeys, strict schema/API replay and artifact agreement. Both adequate
members retain issue_ready with engineering approval unreviewed; eight
failure and three missing-evidence controls remain draft. Goal 5 must replay
these and D3 controls from **both** exact 0.27.0 archives. No tag, registry
publication or GitHub Release was performed by Packet E. Required hosted
checks and exact integration identities are recorded in GitHub.

Goal 5 initially qualified the exact **0.27.0** wheel and sdist, superseding the
development-wheel evidence for release preparation. See the
[retained artifact record](../verification/library-0270-release-artifacts.json).
All 18 profiles pass; each archive's copied beam/column corpus passes 378
tests with no failures/errors/skips, plus independent and public-driver
replays. Both base installs pass 29 UAT cases and 106 inherited numerical
comparisons. Initial broad source-gate failures were repaired in generated
manifests and explicit-unit recognition, with focused evidence; packaged
bytes and frozen Python tree remained unchanged during initial qualification.
Later isolated reviews reproduced R1–R5 in that retained candidate. Preserve
the files in `output/releases/0.27.0/9a78d2be9314/dist/` as baseline evidence;
do not upload them. Bind the replacement pair and final required PR/Weekly
checks only after the repair plan passes. The user
authorized qualification/readiness reporting, not publication. Professional,
unsupported engineering and installed-native boundaries remain explicit.

## Historical S6 handoff — 29 October 2026

Preserved in the [dated handoff archive](../_archive/2026-11/library-handoffs-through-20261029.md).

## Historical handoff boundary — 1 October 2026

Preserved in the [dated handoff archive](../_archive/2026-11/library-handoffs-through-20261029.md).

## Parent-selected isolated-footing shear continuation — 1 October 2026

Preserved in the [dated handoff archive](../_archive/2026-11/library-handoffs-through-20261029.md).

## Separate isolated-footing provided-bar role trace — 1 October 2026

Preserved in the [dated handoff archive](../_archive/2026-11/library-handoffs-through-20261029.md).

## Selected qualification packet and next justified work on the Mac

Preserved in the [dated handoff archive](../_archive/2026-11/library-handoffs-through-20261029.md).

## Separate solver and installed-host boundaries

Preserved in the [dated handoff archive](../_archive/2026-11/library-handoffs-through-20261029.md).

## Native library and Excel implementation order

Preserved in the [dated handoff archive](../_archive/2026-11/library-handoffs-through-20261029.md).

## Required Reading

For Python work, start with the [API chooser](../reference/api-levels.md),
[executable examples](../../Python/examples/README.md), and
[completed usability scope](library-usability-improvement.md).
For installed Excel/ETABS work, use the
[WP10 plan](xll-product/wp10-etabs-read-adapter.md),
[PF11 blueprint](xll-product/library-definition/pf11/README.md), and
[current XLL plan](xll-product/current-plan.md).
All deliveries follow the [canonical Git workflow](../git-automation/git-workflow-single-source.md).
