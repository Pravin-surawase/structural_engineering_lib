# Python Library Workflow Improvement Plan

**Type:** Plan
**Audience:** All Agents
**Status:** Active
**Importance:** High
**Created:** 2026-09-26
**Last Updated:** 2026-09-27
**Related Tasks:** PY-LIB-IMPROVE-001, PY-LIB-IMPROVE-002
**Abstract:** Reliable Python beam design, detailing, schedule and export workflows with explicit acceptance evidence.

---

## Destination and authority

The owner requested a substantially better Python library and selected reliable,
complete design workflows as the first priority. This packet improves the existing
rectangular-beam design → detailing → BBS/report/DXF journey. It follows the
[library-first master plan](is456-library-first-master-plan.md); it does not replace
the wider family programme or the separate Excel/ETABS track.

Task `PY-LIB-IMPROVE-001` starts at main
`9cdfb4a662b4bde64ae42e1024b2a5e2fe7c5a22`. Mac is the sole writer on
`codex/python-design-workflow`. Existing worktrees and dependency PRs remain
outside this packet. The retained unpublished solver documentation candidate is
held for a future replan against then-current main.

## Confirmed problems and finish line

The public compatibility chain discarded its original strength inputs and design
status. A 300 × 500 mm beam, d=444 mm, M25/Fe500, Mu=100 kNm and Vu=200 kN
required stirrup spacing no greater than 100 mm, but `compute_detailing` generated
150/200/150 mm and allowed a nine-item BBS. At Vu=500 kN the same chain generated
a BBS after shear design failed. The README canonical example also rejected its
own d=500 mm because the stated cover and bars require d=492 mm.

Finish line: the supported Python and serialized CLI journeys retain design
inputs and outcome, bind generated bars and stirrups to those inputs, reject
failed or unbound design-derived schedules, and complete coherent positive
examples through actual exports. Required focused, cumulative and hosted checks
must pass before integration. These are software workflow claims, not whole-code
qualification or construction approval.

## Bounded units and measurable acceptance

| Unit | Acceptance |
|---|---|
| W1 Preserve inputs | Compliance and serialized pipeline outputs carry the consumed design inputs, original case identity and result envelope. Adapter geometry/materials must agree with those inputs. |
| W2 Bind generated details | Every design-derived detail checks acceptance, effective and compression depths, stirrup area and maximum spacing through the maintained binding owner. Defaults use the calculated spacing limit; explicit incompatible configuration is rejected with structured issues. |
| W3 Protect consumers | Failed compatibility combined results and failed/missing-basis serialized designs cannot generate BBS or reach CLI detail/DXF export. Mixed valid/failed projects emit no partial artifact. Standalone detailing from explicitly supplied steel remains available without a strength-acceptance claim. |
| W4 Working journeys | Fix the README and end-to-end example; verify low/high-shear positive designs, JSON round trips, BBS quantities and exports. Preserve the canonical facade and current public function signatures. |
| W5 Delivery | Complete task/log/handoff and issue records, format once, run the focused union, review one frozen candidate and deliver one PR through all required hosted checks. |

No new member families, structural formulas, automatic bar optimization,
multi-layer centroid inference, dependencies, frontend features, installed ETABS
operations, release or package publication. Existing torsion and serviceability
scope restrictions must not disappear through the compatibility adapter.
The existing unmodified span/depth screen remains supported when its span and
depth match the generated member; bar-dependent factors and crack strains are
not transferable to a new reinforcement layout.

Likely pitfalls: serialized results must not fall back to drawing defaults;
explicit user spacing must not be silently reduced; source failure must not become
a detailing PASS; input snapshots must not alias caller-owned mutable objects;
report-only failure diagnostics remain available. Legacy design JSON lacking the
strength basis must be regenerated; a drafting-only input is a different contract.

## Verification and cumulative gate

During implementation use only concrete reproducers needed to guide the fix.
After all intended writes, run the affected formatter and focused tests for the
new serialized-workflow regressions, existing depth/shear bindings, full pipeline,
canonical facade, detailing wrappers, CLI, beam pipeline and public API stability.
Replay the README snippets and the complete example. The named W5 cumulative
gate is the full Python suite plus `./run.sh check` (32 checks), justified by the
shared public result schema and CLI consumers. Run affected FastAPI consumers
where the dependency trace reaches them. Hosted CI remains required.

## Progress and next ready work

- Assessment complete: defects reproduced through public calls; no formula
  change is needed.
- W1–W4 implemented: consumed inputs and outcome are preserved, generated
  schedules bind to strength, CLI DXF shares the checked owner, and examples
  plus positive/negative regression journeys are updated.
- W5 complete: PR #1002 merged at `d0722155`; the exact repaired candidate
  passed required hosted run `36261661398` and matched the merged tree.
- Cumulative gate follow-up: regenerate the API projections and stage intended
  caller text before their scan. The synthetic CLI example exposed an overly
  broad initial serviceability guard; retain the unmodified span/depth journey
  with geometry binding. Complete all mutations before observational tests.
- Blockers: none for this software packet. Installed ETABS access is unrelated
  and remains held.
- Next: the import-depth milestone below, authorized by the owner's renewed
  request to improve the project and library.

## Milestone 2 — preserve imported effective depth

Task `PY-LIB-IMPROVE-002` starts at `d072215504ad5986631e64dc98c8a4ed83e4c5ac`.
Mac is the sole writer on `codex/python-import-depth`. No active product PR
precedes it; the ten open dependency PRs and all 32 foreign worktrees are
preserved. The unpublished solver documentation candidate remains held for a
future replan/rebind of shared records, not integration in this packet.

Confirmed baseline: the lossless generic importer rejects distinct `D (mm)`
and `d (mm)` columns as duplicate headers. Using the accepted `eff_d` alias
instead records 470 mm in the ledger but returns 442 mm from the canonical
section for D=500 mm and cover=40 mm. The API preview omits explicit depth;
the saved workspace also omits all three existing depth-input fields.

| Unit | Acceptance and owned paths |
|---|---|
| I1 Distinct headers | `services/imports.py` permits case variants only when they resolve to distinct known fields. Duplicate/ambiguous headers remain blocked. `services/adapters.py` never maps a lone D column to d. |
| I2 Preserve source depth | `core/models.py` gains optional explicit `d_mm`; `effective_depth_mm` uses it when supplied and otherwise retains the existing derivation. Generic adapter aliases preserve it; non-finite/nonpositive/depth-at-or-above-D inputs fail with row context and no partial accepted batch. |
| I3 Complete transport | `fastapi_app/routers/imports.py` exposes the optional explicit depth for file/text/dual imports; existing React import hooks carry it into batch requests. Workspace input hashing, save and restore preserve explicit depth and the existing stirrup/main-bar basis fields. |
| I4 Verify journeys | Exercise generic Python import, CLI D/d intake, HTTP preview-to-project design and React import/workspace-to-request round trips. Compare direct and imported results for the same 470 mm input. Keep no-d import behavior and real duplicate blocking. |
| I5 Deliver | Update existing guidance, task/session/handoff and affected projections; format/focused checks, essential immutable review, integrity, required CI and exact-head merge. |

Schema/cross-field contract: `d_mm` is optional, finite, positive and less than
`depth_mm`; it records the caller's explicit analysis depth, not qualification
of an automatically generated bar layout. Absent depth retains the existing
derivation. D/d spelling is significant when exact aliases distinguish fields;
multiple aliases for the same field and identical headers stay invalid. New
workspace inputs participate in its existing hash/revision contract, so changing
depth invalidates a previous result. Older saved workspaces omit these fields
and remain readable without inventing explicit depth.

Non-goals: no formulas, member families, bar optimization, force/sign semantics,
general adapter rewrite, installed ETABS work, dependency changes or release.
Do not broaden this into unrelated import/default-policy changes. No new UI
controls are needed: retain source inputs through existing data flows.

During implementation run only reproducers needed to guide the changes. After
all intended writes, run the focused Python model/import/CLI/schema tests,
affected HTTP imports/project-design tests, React CSV/workspace/batch-request
tests and the required React build. The named I5 cumulative gate is full Python
plus `./run.sh check`, justified by the shared canonical model change; keep
mutation commands outside observational tests. Required hosted checks remain
mandatory. Candidate audit is a separate read-only parent pass, with no new
tests or adjacent hardening. Record exact local evidence externally after
freeze, and keep publication/merge facts external to the frozen candidate.

Progress: I1–I3 implemented. I4 regression journeys and documentation are written;
the first diagnostic verified Python/HTTP preservation and exposed a missing
required story in the new CLI fixture, now corrected. I5 frozen verification
and delivery remain. No software blocker or installed-application dependency.

I5 repair: the focused suites, full Python (7,952 passed), mypy, React build/lint
and repository 32/32 checks passed. Immutable integrity rejected the first
unpublished candidate because the schema snapshot updater omitted its final LF.
The single consolidated repair fixes that writer with explicit UTF-8/LF output
and regenerates its snapshot. Validate parsed schema equality and the final byte,
then repeat only affected evidence, immutable review and integrity before push.
