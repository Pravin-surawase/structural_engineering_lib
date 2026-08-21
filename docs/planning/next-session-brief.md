# Next Session Briefing

## Latest handoff

<!-- HANDOFF:START -->
- Date: 2026-08-21
- Focus: finish the last Windows W0 catalog step, then run the separate frozen E1 real-Excel G3 journey
- E1 candidate: `codex/e1-excel-routine-workbench` at `ef5ee05c785904e1a01c2d09cc65649edc8745ab`
- E1 PR: #826, draft, clean, required hosted checks passing
- Follow-up record lane: `codex/e1-w0-maintenance-plan`, stacked on the exact E1 head and held behind PR #826
- Windows evidence: `docs/verification/e1-windows-w0-setup-evidence.md`
- Current verdict: `SETUP_BLOCKED`; one administrator SMB-share action remains, G3 has not started
- Held: ETABS file/live integration, ETABS analysis, write-back, optimization, nightly work, release publication, and professional approval
<!-- HANDOFF:END -->

| State | Boundary |
|---|---|
| **Current** | A1, A2, B1, and B2 are merged; E1 software/hosted checks pass in draft PR #826; W0 host/runtime/identity/HTTPS checks pass but setup remains `SETUP_BLOCKED` |
| **Next** | Create the restricted catalog share, then register/load the E1 add-in in a blank workbook and stop at `READY_FOR_G3` or `SETUP_BLOCKED` |
| **After W0** | Run the separately controlled product-workbook G3 journey only after `READY_FOR_G3` |
| **Held** | ETABS work, publication, release, and professional approval were not run |

## First user action on the Windows laptop

Open PowerShell as Administrator and run:

```powershell
New-SmbShare `
  -Name 'E1W0Addin' `
  -Path 'C:\CodexWork\office-addin-catalog' `
  -ReadAccess 'LAPTOP-360-PRAV\P' `
  -FolderEnumerationMode AccessBased
```

Do not grant `Everyone` access. Preserve all existing `C:\CodexWork` content.

## Then resume W0 only

1. Inspect the share and existing catalog manifest; do not recreate passing
   runtime, wheel, certificate, or service work.
2. Register the network-share catalog using Excel's supported trusted-catalog
   flow.
3. Open a blank workbook only and prove the `Excel Routine Workbench V1` task
   pane loads from the trusted localhost service.
4. Stop with exactly `READY_FOR_G3` or `SETUP_BLOCKED`.
5. Keep the E1 product workbook closed; W0 must not claim G3.

If the old remote task remains unreadable, a small continuation task may use the
same host and paths after first verifying the recorded identities. The remote
visibility failure is unconfirmed and did not invalidate the completed setup.

## Frozen G3 journey after `READY_FOR_G3`

Use unchanged candidate head `ef5ee05c` and record the exact Windows/Excel,
manifest, workbook, wheel, Python, and library-content identities.

1. Open the exact packaged workbook.
2. Select `tbl_Beam_Workbench_V1` and preview the visible mapping.
3. Run the frozen PASS, FAIL, HOLD, and blocked vectors.
4. Reconcile every source row with the ledger and canonical result/passport.
5. Edit one calculation-bearing input and observe `STALE`.
6. Recalculate to `CURRENT` and export the deterministic review bundle.
7. Close and reopen Excel; prove identities, results, and freshness persist.
8. Capture the receipt and stop. Do not start ETABS in the G3 task.

## Product sequence after G3

1. Review the G3 receipt against the frozen E1 acceptance matrix.
2. If it passes and the head is unchanged, move PR #826 through final review and
   integration without editing the frozen candidate for status-only notes.
3. Integrate this stacked maintenance/evidence record after E1 so shared docs
   remain ordered.
4. Start a planning-only ETABS snapshot/CSV intake packet using the preserved
   legacy VBA/API material as reference and parity evidence.
5. Approve a narrow read-only live COM probe only after snapshot intake passes;
   analysis, model changes, write-back, and optimization stay separately gated.

## Maintenance result

- Health issue found and corrected: four stale endpoint/router counts.
- Runtime/wiring status: 88/88 endpoints directly tested, 13/13 React hooks
  connected, source binding valid.
- Cleanup status: no destructive cleanup authorized. All 25 classified local
  branches remain `HOLD_UNKNOWN_OWNER`; existing dirty/detached and task-owned
  worktrees remain preserved.
- Index maintenance: three inherited E1 parent-index drifts and three current
  documentation-index drifts were repaired; the new verification record was
  added to its targeted folder index.
- Verification economy: run documentation and focused governance checks after
  content freezes, then one quick gate. Do not rerun broad Python/full suites
  for this documentation/evidence-only packet unless an outcome-changing shared
  failure requires them.

## Required Reading

1. [Windows W0 evidence](../verification/e1-windows-w0-setup-evidence.md)
2. [E1 evidence](../verification/e1-excel-routine-workbench-v1-evidence.md)
3. [E1 execution plan](e1-excel-routine-workbench-v1-plan.md)
4. [Current task board](../TASKS.md)
5. [Git workflow single source](../git-automation/git-workflow-single-source.md)

Historical handoff files are preserved on Windows at
`C:\CodexWork\reference\etabs-vba-handoff`. Treat them as unvalidated reference
material, open legacy workbooks with macros disabled, and use only copied
disposable ETABS models in any later approved probe.
