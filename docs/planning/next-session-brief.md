# Next Session Briefing

## Latest Handoff

<!-- HANDOFF:START -->
- Date: 2026-08-10
- Focus: ADOPT-001 Packets A-G are locally complete; owner decides publication workflow
<!-- HANDOFF:END -->

**Current release:** `v0.23.0` Alpha
**Branch:** `codex/trust-surface-foundation`
**Base:** `origin/main` at `44e85587`
**Task board:** [TASKS.md](../TASKS.md)

| State | Target | Decision |
|---|---|---|
| **Current** | v0.23.0 Alpha | Released; this branch adds local adoption/trust improvements only |
| **Next** | Owner review | Decide whether to push and open a draft PR |
| **Held** | Stable/engineering use | Requires cumulative qualified structural-engineering review |

## Required Reading

- [Adoption and trust surface plan](adoption-trust-surface-plan.md)
- [Bundled sample BOQ evidence](../verification/bundled-sample-boq-evidence.md)
- [Release policy](../getting-started/releases.md)

## Completed outcome

- Packet A made public Python/REST examples executable.
- Packet B exposed one canonical capability inventory through Python, CLI, and REST.
- Packet C typed all 63 HTTP operations without changing JSON envelopes.
- Packet D made production-like startup fail closed when auth or its secret is unsafe.
- Packet E added canonical beam calculation evidence to REST and report outputs.
- Packet F added exact PASS/FAIL/HOLD presentation, export holds, REST/WebSocket
  parity, and the dataset-bound bundled-sample BOQ record.
- Packet G made documentation CI build-only until Pages is configured and
  restricted future public releases to PEP 440 Alpha identifiers.
- The full-suite report regression found during closeout was fixed without
  refreshing legacy goldens: evidence-free HTML remains byte-identical.

## Verification

- Tests: 5,485 Python + 373 FastAPI + 152 React = 6,010 passed.
- Repository controls: check 30/30, audit 19/19, health 100/100, efficiency PASS.
- OpenAPI: 63 endpoints, 228 schemas, no breaking drift.
- Browser happy path: bundled dataset, 153/153 PASS, 1,928.5 kg steel,
  48.7 m³ concrete, exact dataset/calculation identities, exports enabled.
- Browser negative path: ratio 6.494420, margin -5.494420, FAIL, export disabled.
- Live public state: `v0.23.0` is a GitHub prerelease and current PyPI artifact;
  GitHub Pages is not configured.

## Owner-only holds

- Provision and manage the real production JWT secret.
- Decide whether to enable GitHub Pages and verify its resulting URL.
- Authorize any push, pull request, merge, tag, TestPyPI/PyPI publication, or
  GitHub Release action.
- Retain cumulative qualified structural-engineering review before any stable
  or engineering-use approval.

## Next action

If the owner approves publication of this branch, inspect the final diff, push
`codex/trust-surface-foundation`, open a draft PR, and wait for all required
checks. Do not merge or publish without a separate explicit confirmation.
Dependency maintenance remains a separate queued task.

## Terminal issues recorded

- The stale `check_api_drift.py` handoff path was replaced by the maintained
  `check_openapi_drift.py` command.
- `check_links.py --fail-fast` is unsupported here; the default checker passed
  all 1,069 internal links.
- `mkdocs` was not on the shell PATH; `.venv/bin/python -m mkdocs` passed strict
  builds.
- The generic safe-YAML hook could not parse MkDocs' callable tag; `mkdocs.yml`
  is now validated by strict PR/main workflow builds while ordinary YAML keeps
  the safe loader.
- `agent-browser` was not globally installed; the pinned `npx --yes
  agent-browser` path completed the browser verification.
- The first full suite exposed optional-evidence whitespace in report HTML; the
  renderer boundary was fixed and all four goldens now pass unchanged.
