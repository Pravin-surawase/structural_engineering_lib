# Next Session Briefing

## Latest handoff

<!-- HANDOFF:START -->
- Date: 2026-08-17
- Focus: LIB-PRO-002 cumulative A-G input safety and professional-readiness integration
- Base: Packet A merge `3986935ecb473c1f9d56dec44aeb4218d9192f84` (PR #814)
- Lane: `codex/lib-pro-002-b-lossless-import`; one isolated writer; unrelated worktrees preserved
- Candidate: Packets B-G integrated; first exact-head review rejected a bypassable presence-only publication receipt check after all local/hosted gates passed
- Release: HOLD; `docs/verification/release-publication-authorization.json` contains no exact version/tag/target authorization
- Whole-building workflow: Packet H is not activated and component-only claims remain
- Exact next action: finish the receipt head/tree/package/version/tag/target binding repair, then create one repaired immutable head and restart exact review plus hosted checks
<!-- HANDOFF:END -->

| State | Boundary |
|---|---|
| **Current** | `v0.23.1a1` Alpha; no stable, professional-approval, or whole-building claim |
| **Next** | LIB-PRO-002 A-G cumulative input/import/result/evidence/API/release-safety acceptance |
| **Held** | Publication, professional approval, Packet H, INDIA-3, dependency work, branch/worktree cleanup, and unrelated retained lanes |

## Required Reading

1. [Active A-G plan](pre-release-input-safety-and-professional-readiness-plan.md)
2. [Current task board](../TASKS.md)
3. [Git workflow single source](../git-automation/git-workflow-single-source.md)
4. [Publication authorization record](../verification/release-publication-authorization.json)
5. [Exact-candidate review receipt template](../verification/exact-candidate-review-receipt-template.json)

## Resume safely

Use only the existing cumulative worktree. Do not recreate the branch, move its
changes to a retained lane, or mutate primary `main` while the candidate is
open.

```bash
./run.sh session brief --agent orchestrator
./run.sh session start
./scripts/python_runtime.sh --diagnose
./scripts/python_runtime.sh scripts/git_state.py --json --worktrees
```

Require the expected branch/head/diff, `source_bound=true`, no operation marker,
and no new overlapping writer before mutation. The earlier Packet A Git issue
was not an unclean-start failure: a later side packet advanced shared refs and
overlapped closeout/index files after the original start check. The durable
active-candidate dependency/path-overlap gate in `AGENTS.md` and the canonical
Git workflow now covers that whole candidate lifetime.

## Integrated A-G boundary

- strict canonical beam input, explicit effective depth, stable blocking issues,
  no calculation call for blocked inputs, and accounted empty/mixed batches;
- explicit/unique adapter selection, every-row/every-field normalization ledger,
  and blocking malformed, dropped, duplicate, or unmatched records;
- one canonical service orchestration shared by HTTP/SSE/React, with old routes
  delegating or deprecated and no client structural fallback;
- orthogonal intake/calculation/engineering/review truth across beam, slab,
  column, and footing, retaining the correct insufficient-dowel FAIL;
- calculation, library, controlled-source, amendment, artifact, ledger,
  assumption, provenance, and replay identity;
- complete Alpha API classification, corrected version/claim/example surfaces,
  and installed-package preflight;
- source-free exact-wheel negative UAT plus an explicit per-version/tag/target
  owner authorization stop before publication; the repair resolves and hashes
  an actual independent-review JSON receipt, verifies reviewed Git/Python
  identity and permits only an evidence-only descendant delta.

## Acceptance and stop rules

Run the broad Python, complete FastAPI/React, full canonical, packaging,
protected-source, and exact-wheel gates once at this cumulative boundary. Bind
the immutable commit/tree to an independent software/release-evidence review
and all required hosted checks before merge.

Do not publish a package, create a tag or GitHub Release, claim professional
approval, activate Packet H, close issues/PRs, delete branches, or clean retained
worktrees without the separately required authorization.
