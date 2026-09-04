**Type:** Architecture
**Audience:** Developers
**Status:** Active
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
   at most 256 MiB.

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
- receipts for project validation, workbook calculation, fixed-action search,
  calculation-package export, and diagnostics/performance;
- a sample workbook that saves, closes, reopens, and retains a current result
  whose input revision reconstructs exactly;
- installed Excel evidence for PF8 E5-01, E5-05, E5-06, and restart/runtime
  fingerprint invalidation; and
- raw and summarized `PERF-WORKBOOK` evidence against the frozen workload.

Live ETABS acquisition and mutation remain WP10 and WP11. Package publication,
a GitHub Release, and commercial distribution remain governed by the separate
per-release authorization and evidence gates.
