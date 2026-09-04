**Type:** Architecture
**Audience:** Developers
**Status:** Complete
**Importance:** Critical
**Created:** 2026-09-04
**Last Updated:** 2026-09-04

# WP09 — standalone Windows Excel product

WP09 delivers the first complete application over the native
`StructuralEngineering.*` libraries implemented in WP01–WP08. The product is a
Windows x64 Excel-DNA add-in for standalone reinforced-concrete beam work. It
does not require Python, FastAPI, Node, ETABS, or a companion application at
runtime.

## Public boundary

The canonical adapter is `StructuralEngineering.ExcelDna`. It references the
native WP01–WP08 packages directly. The earlier `StructAutomate.Excel` demo
calculation chain is replaced by compatibility functions that delegate to the
same native operations, so Excel and ordinary .NET callers receive the same
units, identities, result states, diagnostics, and provenance.

Worksheet calculations use the PF8 `STR.*` families. Simple operations have
typed scalar/range arguments. Complex operations accept a strict immutable JSON
request matching the public .NET record and return a bounded spill containing
the operation identity, independent result states, provenance, calculation
identities, output, and diagnostics. A worksheet function never reads or writes
the workbook object model, uses COM or ETABS, accesses a file or network,
starts a process, records approval/currentness, or runs a large search.

The standalone workbook uses versioned Excel tables and stable row identities.
Commands run outside recalculation and own bulk input reads, calculation,
controlled output writes, preimage/readback/rollback, freshness, progress,
cancellation, export, and diagnostics. Only named product tables are controlled;
unrelated sheets, formulas, comments, names, and user content are outside the
write set.

## Delivery slices

1. **Adapter and worksheet functions.** Create the canonical Excel-DNA project,
   reference the native packages, implement the PF8 function families, retain
   the four legacy names as delegates, and prove deterministic projection and
   zero host effects.
2. **Workbook contract and commands.** Implement workbook template version 1,
   stable project/member/request identities, `XL-CMD-01`, `XL-CMD-03`,
   `XL-CMD-04`, `XL-CMD-06`, and `XL-CMD-07`, bulk table I/O, cancellation,
   command receipts, current/stale transitions, controlled readback, and exact
   rollback.
3. **Product package.** Supply the packed AMD64 XLL, Ribbon, function and table
   reference, sample workbook, manifest, checksums, preflight, per-user
   install/repair/uninstall scripts, and Authenticode signing workflow. The
   WP09 installed candidate may use an identified local validation certificate;
   public distribution still requires the separately authorized release
   certificate and release process.
4. **Installed acceptance.** Exercise the unchanged signed candidate in actual
   64-bit Microsoft Excel: load, recalculate pure functions, create/calculate a
   workbook, verify controlled-write rollback, save, close, reopen, reconstruct
   current results, export a calculation package, and uninstall/repair. Retain
   source, artifact, runtime, workbook, receipt, and evidence hashes.
5. **Performance.** Freeze `BENCH-EXCEL-TYPICAL` at 20 members and 200 action or
   check rows. The first warm-up must perform the full calculation after sample
   creation. Later unchanged calls may use the calculation engine's verified,
   content-addressed current-result cache; every measured warm call must prove
   that reuse in its command response. Run five untimed warm-ups, thirty warm
   measurements, and ten cold Excel launches. Report the initial full-compute
   time separately from the cache-backed warm median, p95, maximum,
   progress/cancellation response, working-set change, exact machine/runtime
   identities, raw samples, and the PF9 budget verdict: warm median at most
   750 ms, warm p95 at most 1 s, cold ready at most 3 s,
   progress/cancellation response at most 250 ms, and Excel working-set growth
   at most 256 MiB. A cold-ready sample starts immediately before creating a
   new Excel automation process and ends when that process returns the installed
   XLL version probe. Startup-registration preconditions, acceptance-host
   configuration, AddIns lifecycle enumeration, and workbook inspection remain
   separate functional evidence.

## Completion evidence

WP09 completed on 4 September 2026 at source commit
`6d03be23ec4964034def3b74492f9722cfdd3bee` and tree
`000807f80d8356aaac63b48b6e777f88b3564c47`. Independent source review passed
that candidate. The local distribution zip has SHA-256
`0d2a33dee0ff7041bb1b35dcfdeca66643114e7ff3179711b454087c6b36b0d4`;
its manifest has SHA-256
`5b25f555238baa7fb9d312aecf4c900f95a7b68f757089aa5a20db03a66e7cae`,
and its signed AMD64 XLL has SHA-256
`36da1b297ae20e50629e3e8168c2af68356296b8f0ee61409598a47aaf2fd1d5`.
That manifest hash is the byte-exact packaged file; distribution evidence also
records the repository's LF-normalized semantic copy separately.

The unchanged signed package passed preflight, clean per-user installation,
repair, the complete installed Excel workflow, uninstall, and cleanup on the
recorded Windows/Excel/.NET environment. The 20 member rows repeat one frozen
physical beam scenario to exercise the batch and workbook paths; they are
performance and workflow evidence, not engineering-case diversity. The final
accepted run recorded a 7,352.117 ms initial full calculation, 356.715 ms warm
median, 413.457 ms warm p95, 2,018.668 ms maximum cold-ready time, 202.059 MiB
Excel working-set growth, 2.4877 ms progress response, and 23.4521 ms
cancellation response. It also passed the legacy 9/13-column schema upgrade and
saved-workbook runtime-fingerprint invalidation probes. All raw samples and
verdicts are retained in the
[installed acceptance receipt](../../verification/wp09-excel-installed-acceptance.json).
The [distribution evidence](../../verification/wp09-excel-distribution-evidence.json)
binds the artifact and lifecycle receipts; the
[cleanup receipt](../../verification/wp09-excel-cleanup.json) proves the test
installation, startup registration, Excel processes, and local validation
certificate were removed.

The exact candidate was exercised three times during final verification. Two
runs passed every unchanged gate. The middle repeat passed every functional and
timing check but recorded 275.438 MiB working-set growth against the locked
256 MiB limit; the final run recorded 202.059 MiB. The
[distribution evidence](../../verification/wp09-excel-distribution-evidence.json)
retains this variance rather than changing the budget or measurement boundary.

The validation certificate established local installed behaviour only. No XLL,
zip, private key, package publication, or GitHub Release is committed or
authorized by this milestone.

## Acceptance

WP09 closes only when one unchanged candidate has all of the following:

- a non-empty packed AMD64 XLL and verified Authenticode signature;
- the `STR.INFO`, `STR.REBAR`, `STR.IS456.FLEXURE`, `STR.IS456.SHEAR`,
  `STR.IS456.TORSION`, `STR.IS456.SLS`, `STR.IS456.DETAIL`, `STR.BEAM.LINE`,
  and `STR.CONSTRUCTION` families over native operations;
- runtime instrumentation showing worksheet recalculation made zero host-effect
  calls;
- successful controlled writes with matching readback and a forced-failure
  self-test that restores the exact preimage;
- receipts for project validation, workbook calculation, current-candidate evaluation,
  calculation-package export, and diagnostics/performance;
- a sample workbook that saves, closes, reopens, and retains a current result
  whose input revision reconstructs exactly;
- installed Excel evidence for PF8 E5-01, E5-05, E5-06, and E5-10, including
  ten independent cold-ready probes and saved-workbook runtime-drift
  invalidation; and
- raw and summarized `PERF-WORKBOOK` evidence against the frozen workload.

Live ETABS acquisition and mutation remain WP10 and WP11. Package publication,
a GitHub Release, and commercial distribution remain governed by the separate
per-release authorization and evidence gates.
