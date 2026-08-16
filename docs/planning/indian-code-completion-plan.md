---
task: INDIA-COMPLETION-PLAN
title: Indian-Code Completion Waves
status: active
owner: Main Agent and repository owner
created: 2026-08-15
last_updated: 2026-08-16
doc_type: spec
---

# Indian-Code Completion Waves

## 1. Purpose and authority

This is the canonical finish plan for the repository's Indian-code program.
It defines the meaning and order of INDIA-0 through INDIA-4 without claiming
that every provision of any standard will be implemented.

The generated
[Indian-code capability/coverage manifest](../verification/indian-code-capability-coverage.json)
remains the authority for executable support and registration status.
[TASKS.md](../TASKS.md) remains the short current-work board. The
[library-first master plan](is456-library-first-master-plan.md) is the completed
bounded-product milestone, and the
[library expansion blueprint](library-expansion-blueprint-v5.md) remains the
long-range architecture roadmap. Neither historical document overrides this
wave order or the generated manifest.

Historical PRs, evidence files, and task IDs are immutable receipts. In
particular, the completed staircase packets named `INDIA-2A` through
`INDIA-2D` are not renamed. This plan maps them to `INDIA-2-STAIR`, one
completed family inside the larger INDIA-2 wave.

## 2. Finish-line status

| Wave | Outcome | Current state |
|---|---|---|
| INDIA-0 — Truth baseline | One generated, standard-namespaced capability/coverage manifest; repaired coverage consumers; reconciled status ledgers | **Complete** |
| INDIA-1 — Existing-family closure | Close or explicitly hold limitations for beam, rectangular column, isolated footing, and solid slab | **Complete** |
| INDIA-2 — Remaining practical IS 456 elements | Separately verify wall, stair, deep-beam, flat-slab/punching, and distinct foundation-system packets | **In progress** — bounded wall, stair, deep-beam, flat-slab/punching, and combined-footing families accepted; strap, pile-cap, and raft decisions remain pending |
| INDIA-3 — Companion Indian codes | Complete the bounded IS 13920 surface, then add IS 875 inputs before IS 1893 equivalent-static actions and Indian combinations | **Planned** |
| INDIA-4 — Final acceptance | Run cumulative engineering, cross-layer, repository, and artifact acceptance for the explicitly supported subset | **Planned** |

“Complete” means the bounded accepted scope and its explicit exclusions are
closed. It does not mean whole-standard coverage, professional approval, or
release authorization.

## 3. INDIA-2 family packets

Every family starts with a decision packet that freezes one useful case, its
source, independent benchmark, assumptions, and exclusions before calculation
code is authorized.

The complete packet sequence, family boundaries, and exit criteria are in the
dedicated [INDIA-2 execution plan](india-2-remaining-is456-elements-plan.md).
That document controls INDIA-2 execution within this parent wave.

| Packet | Bounded objective | State and boundary |
|---|---|---|
| `INDIA-2-WALL` | IS 456 Clause 32 wall program | **Complete within its bounded case.** Alternate and seismic wall systems remain held. |
| `INDIA-2-STAIR` | IS 456 Clause 33 longitudinal straight waist-slab flight with collinear landings | **Complete.** Historical `INDIA-2A`–`INDIA-2D` plus the cumulative gate are its evidence. Alternate stairs remain held. |
| `INDIA-2-DEEP` | IS 456 Clause 29 deep-beam program | **Complete within its bounded case.** One simply supported positive-moment workflow is accepted; alternate deep-beam systems remain held. |
| `INDIA-2-FLAT` | Flat-slab and column-punching program | **Complete within its bounded case.** One regular interior direct-design and concrete-only punching workflow is accepted; alternate systems remain held. |
| `INDIA-2-FOUNDATION-COMBINED` | Combined-footing program | **Complete within its bounded case.** One symmetric equal-load two-column rigid rectangular workflow is accepted; alternate systems remain held. |
| `INDIA-2-FOUNDATION-STRAP` | Strap-footing program | **Held; distinct analysis model required.** |
| `INDIA-2-FOUNDATION-RAFT` | Raft-foundation program | **Held; distinct analysis model required.** |
| `INDIA-2-FOUNDATION-PILE-CAP` | Pile-cap program | **Held; distinct analysis model required.** |

The next packet is decision-only `INDIA-2-FOUNDATION-STRAP-G0`. Combined
footing is accepted without adding another topology; alternate combined-
footing systems remain held. Strap footing requires its own source, analysis
model, benchmark, supported boundary, exclusions, and GO before calculation
code. The dedicated
[next-session and finish plan](india-2-next-session-publication-and-closeout-plan.md)
controls the remaining order through INDIA-2 closeout.

## 4. INDIA-3 companion-code order

INDIA-3 is not another IS 456 element. It is the companion Indian-code wave:

1. Finish and advertise the already bounded IS 13920 beam, column, and joint
   checks without inflating registration into implementation.
2. Add separately sourced and benchmarked IS 13920 wall provisions.
3. Add separately sourced and benchmarked IS 13920 foundation provisions.
4. Implement bounded IS 875 gravity and wind input programs.
5. Only then implement IS 1893 equivalent-static seismic actions and the
   accepted Indian load combinations that consume those inputs.

Response-spectrum, dynamic, and FEM analysis are a separate analysis program.
They are not implied by an equivalent-static or load-combination capability.

## 5. INDIA-4 final acceptance

After the accepted INDIA-2 and INDIA-3 scope is frozen, INDIA-4 performs:

- source-to-result benchmark review for every advertised calculation packet;
- cross-layer user-acceptance testing for supported Python, API, and UI paths;
- the full repository gate and exact-artifact verification;
- cumulative qualified structural-engineering review of the advertised subset.

INDIA-4 does not authorize professional use or release. Stable-release,
engineering-use, package publication, tag, GitHub Release, and professional
approval remain separate owner-controlled decisions.

## 6. Required contract for every calculation packet

Before a packet can claim support, it must record all of the following:

1. Governing standard edition, clause/table identifier, and source provenance.
2. Explicit units plus supported geometry, material, support, and loading
   assumptions.
3. An independent benchmark and justified numerical tolerance.
4. Governing unsafe cases and out-of-domain cases that fail closed.
5. Pure-math acceptance before Python service, FastAPI, or React publication.
6. Truthful capability wording and machine-visible exclusions.
7. Focused tests, benchmark checks, architecture checks, and the quick gate for
   the packet, followed by one cumulative full gate at the milestone boundary.

The expensive broad Python and 30-check repository gates run once after a
milestone's packets are integrated. Run them earlier only when a confirmed
repository-wide issue could change the outcome.

## 7. Claim boundaries

- Generated registration or metadata is not proof of calculation capability.
- Passing software tests is not qualified engineering review.
- Qualified review is not release or professional-use authorization.
- A completed bounded packet does not activate adjacent geometry, loads,
  elements, companion codes, analysis systems, API, UI, or release work.
- Unknown or unsupported cases must remain explicit holds, never inferred
  support.
