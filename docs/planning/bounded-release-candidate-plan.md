---
task: LIB-PRO-010-RC
title: Bounded Release Candidate and Qualified Review Plan
status: active
owner: Main Agent and repository owner
created: 2026-08-24
last_updated: 2026-08-24
doc_type: spec
---

# Bounded Release Candidate and Qualified Review Plan

## 1. Decision

Prioritize trust in the currently supported bounded subset before adding more
engineering scope. The present library may become a release candidate only
after the three internal closeout items in this packet are integrated. A stable
release, engineering-use approval, and professional approval remain separate
owner decisions.

The current subset review is not called `INDIA-4` final acceptance unless the
repository owner explicitly freezes that subset as the INDIA-4 scope. Until
then it is a qualified review of one exact bounded candidate.

## 2. LIB-PRO-009 internal closeout

| Item | Required outcome |
|---|---|
| Public `bar_count` input | Accept only a positive Python/JSON integer; reject booleans, strings, fractional values, zero, and negatives through the structured validation result |
| Evidence status | Keep benchmark replay, calculation completion, engineering disposition, and qualified review as separate fields |
| Living status | Record INDIA-3 M0 as integrated and remove instructions to merge its already-merged candidate |
| Historical evidence | Preserve the immutable INDIA-3 M0 evidence and handoff receipts; add a current clarification instead of rewriting them |

No structural formula, supported family, API route, version, artifact, source,
or professional claim changes in LIB-PRO-009.

## 3. Ordered candidate gates

1. LIB-PRO-009 integrated through PR #870 at merge `b3309260`; its candidate
   and merged trees both equal `90894f2f`.
2. Freeze the exact supported subset, exclusions, candidate version, commit,
   and artifact identities. Later IS 13920 wall/foundation and IS 875/1893 work
   remains outside that candidate.
3. Build the immutable wheel and source distribution, then test the installed
   artifact outside the source checkout:
   - clean installation and imports;
   - one bounded one-storey gravity example without implying complete building
     design;
   - independent hand-calculation comparisons for every advertised family;
   - public API and function-name review;
   - limitations and `NOT_EVALUATED`/`FAIL`/`HOLD` visibility in every result;
   - package, version, documentation, and artifact-digest consistency.
4. Give a qualified structural engineer that exact unchanged candidate,
   artifact set, source/clause map, benchmarks, unsafe cases, limitations, and
   review ledger. Any outcome-changing repair creates a new candidate and
   invalidates the earlier review receipt.
5. After the exact-candidate review is accepted, obtain a separate owner
   decision for stable release and any engineering-use wording. Tagging,
   package publication, and GitHub Release creation require that decision.
6. Expand only after this bounded release decision: IS 13920 walls, IS 13920
   foundations, IS 875 actions, and then IS 1893 equivalent-static actions and
   accepted combinations.

## 4. Verification efficiency

Reuse immutable evidence for unchanged calculations and artifacts. During an
implementation packet, run only the focused reproducer needed to guide the
change. After content freezes, batch the affected focused checks, run the quick
gate once, normal commit hooks, and the required hosted checks. Run the broad
Python and full repository gates once for the integrated candidate, with a
repeat only when an outcome-changing repair invalidates their evidence.

## 5. Preserved holds

- No claim of complete code-compliant building design.
- No qualified-engineer receipt or professional approval in this packet.
- Candidate version preparation and local wheel/sdist verification are in scope
  only for `0.24.0a1`; no tag, package upload, GitHub Release, stable claim, or
  public-distribution action is authorized.
- No IS 13920 wall/foundation, IS 875, IS 1893, dynamic, response-spectrum,
  FEM, ETABS write-back, or additional building-workflow scope.
- No branch, worktree, archive, source-copy, alias, or unrelated-file cleanup.
