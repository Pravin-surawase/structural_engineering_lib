# StructAutomate Excel user and function reference

**Type:** Guide
**Audience:** Users and .NET Developers
**Status:** Active
**Importance:** High
**Created:** 2026-09-04
**Last Updated:** 2026-09-04
**Related Tasks:** WP09
**Abstract:** Install, use, diagnose, and integrate the standalone Windows Excel XLL over the native .NET beam library.

---
## Summary

StructAutomate Excel is a packed AMD64 Excel-DNA XLL for standalone reinforced
concrete beam work in 64-bit Microsoft Excel on Windows. It calls the reusable
`StructuralEngineering.*` .NET libraries directly and needs no Python,
FastAPI, Node, ETABS, or network connection at runtime.

The shipped workbook demonstrates 20 beams and 200 versioned topology and check
rows. It covers flexure, shear, torsion, deflection, crack width, development
length, anchorage, lap and curtailment, reinforcement arrangement, bar paths,
BBS, concrete/steel/formwork quantities, illustrative cost, calculation
packages, and bounded fixed-action candidate search.

## Supported installation

The WP09 package targets:

- 64-bit Windows and 64-bit Microsoft 365 Excel;
- the Microsoft .NET 10 Desktop Runtime for x64;
- an AMD64 `StructAutomate.xll` signed with the certificate identified in
  `manifest.json`; and
- the unchanged files and SHA-256 values recorded by `manifest.json` and
  `SHA256SUMS`.

Close Excel before installation, repair, or removal. From PowerShell in the
unpacked distribution directory, run:

```powershell
.\Test-Preflight.ps1 -DistributionDirectory .
.\Install-PerUser.ps1 -DistributionDirectory .
```

The per-user installation is placed under
`%LOCALAPPDATA%\StructAutomate\Excel\0.1.0` and adds an exact per-user Excel
startup entry for that XLL. Uninstall removes that entry and only that version's
files. Open
`StructAutomate-Standalone-Beam.xlsx` after installation. The **StructAutomate**
Ribbon tab exposes the normal workflow.

Repair the installed files from the same unchanged distribution, or remove the
installed version, with:

```powershell
.\Repair-PerUser.ps1 -DistributionDirectory .
.\Uninstall-PerUser.ps1 -Version 0.1.0
```

Each lifecycle command produces a machine-readable receipt under
`%LOCALAPPDATA%\StructAutomate\Receipts`.

## Worksheet functions

All `STR.*` functions are deterministic, thread-safe projections over native
.NET operations. They do not read or write workbook objects, files, processes,
network services, or ETABS. Blank scalar inputs are rejected instead of being
treated as zero. JSON arguments require exact `snake_case` property and enum
names; unknown properties are rejected.

| Function | Arguments | Result |
| --- | --- | --- |
| `STR.INFO.VERSION` | none | Adapter version text |
| `STR.INFO.REVISIONS` | none | Adapter, result-schema, and canonicalization revisions |
| `STR.REBAR.AREA` | `diameter_mm` | Scalar area in mm² |
| `STR.REBAR.AREA.RESULT` | `diameter_mm` | Full result envelope |
| `STR.REBAR.MASS_PER_LENGTH` | `diameter_mm`, `density_kg_per_m3` | Scalar kg/m |
| `STR.REBAR.MASS_PER_LENGTH.RESULT` | `diameter_mm`, `density_kg_per_m3` | Full result envelope |
| `STR.REBAR.GEOMETRY` | strict JSON | Bar-group geometry and fit |
| `STR.IS456.FLEXURE.CHECK` | strict JSON | Signed flexure check |
| `STR.IS456.SHEAR.CHECK` | strict JSON | Axis-specific shear check |
| `STR.IS456.TORSION.CHECK` | strict JSON | Concurrent torsion interaction check |
| `STR.IS456.SLS.DEFLECTION` | strict JSON | Screening or calculated-component deflection check |
| `STR.IS456.SLS.CRACK_WIDTH` | strict JSON | Arrangement-sensitive crack-width check |
| `STR.IS456.DETAIL.DEVELOPMENT_LENGTH` | strict JSON | Development length calculation |
| `STR.IS456.DETAIL.ANCHORAGE` | strict JSON | Physical bar-path anchorage check |
| `STR.IS456.DETAIL.LAP_CURTAILMENT` | strict JSON | Lap, cutoff, and continuing-steel check |
| `STR.IS456.DETAIL.SEISMIC` | strict JSON | Explicit IS 13920 applicability/detailing check |
| `STR.REBAR.ARRANGEMENT` | strict JSON | Cover, spacing, cage, bend, obstacle, and placement check |
| `STR.BEAM.LINE.SOLVE` | strict JSON | Bounded planar V2/M3 beam-line solve |
| `STR.CONSTRUCTION.BBS` | strict JSON | Bar bending and cutting-stock schedule |
| `STR.CONSTRUCTION.QUANTITIES` | strict JSON | Steel, concrete, and formwork quantities |
| `STR.CONSTRUCTION.COST` | strict JSON | Dated, sourced rate-profile estimate |

Examples:

```excel
=STR.INFO.VERSION()
=STR.REBAR.AREA(20)
=STR.REBAR.MASS_PER_LENGTH(20,7850)
=STR.IS456.DETAIL.DEVELOPMENT_LENGTH(A2)
```

Cell `A2` in the final example can contain:

```json
{"profile_id":"ordinary_beam","bar_diameter_mm":20,"bar_stress_n_per_mm2":361.05,"steel_yield_strength_n_per_mm2":415,"concrete_grade_n_per_mm2":25,"bar_surface":"deformed","stress_state":"tension"}
```

Structured functions spill two columns. The left column names the result field;
the right column contains a scalar or compact JSON value. The envelope keeps
execution, applicability, engineering, completeness, freshness, result ID,
normalized-input ID, calculation ID, code-data revision, method revision,
outputs, and diagnostics separate. A rejected input therefore cannot appear as
an engineering failure or pass. One spill cell cannot exceed Excel's 32,767
character limit.

The compatibility names `SA.VERSION`, `SA.BAR.MASS`, `SA.REBAR.GEOMETRY`, and
`SA.BEAM.SS.UDL` remain available and delegate to the native operations. New
workbooks should use `STR.*` names.

## Standalone workbook workflow

The Ribbon invokes these stable command bindings:

| Ribbon action | Command binding | Behaviour |
| --- | --- | --- |
| Create / Validate | `STR_XL_CMD_01_CREATE_VALIDATE` | Validate version, identities, schemas, topology, and declared check rows |
| Calculate Workbook | `STR_XL_CMD_03_CALCULATE_WORKBOOK` | Calculate every member and write one atomic current result set |
| Optimize Beams | `STR_XL_CMD_04_OPTIMIZE_BEAMS` | Run the bounded fixed-action candidate domain for every member |
| Export Packages | `STR_XL_CMD_06_EXPORT_PACKAGES` | Export one hash-bound JSON bundle containing one current package per member |
| Measure / Diagnose | `STR_XL_CMD_07_MEASURE_DIAGNOSE` | Record runtime identity, reconstruction timing, and a benchmark receipt |

`Calculate Workbook` hashes the complete versioned input plus the calculation
engine revision. The first run computes the full result chain. If neither the
input nor engine revision changed, a later run verifies the saved result table,
freshness rows, and all member packages, preserves those results, and appends a
new command receipt. Any input edit or changed calculation engine causes a full
calculation.

The command boundary reads only the three declared input tables and writes only
the five declared result/evidence tables. A write succeeds after exact readback.
If a write or artifact commit fails, the command restores and verifies every
changed table against its preimage.

## Input table contract

Table names, header spelling, and header order are part of
`structural-excel-workbook/v1`.

| Table | Required columns in order |
| --- | --- |
| `StructuralProject` | `template_id`, `workbook_id`, `project_id`, `project_request_json` |
| `StructuralMembers` | `member_id`, `request_id`, `member_design_seed_json`, `bar_path_request_json`, `bbs_seed_json`, `quantity_seed_json`, `cost_seed_json`, `package_seed_json`, `optimization_seed_json` |
| `StructuralOperations` | `member_id`, `request_id`, `row_id`, `phase`, `operation_semantic_id`, `request_json`, `rule_id`, `scope_id`, `check_scope`, `expected_applicability`, `code_data_binding_id` |

`StructuralProject` has exactly one data row. Member and request identities are
unique. Each member has exactly one `topology` row and at least one `leaf` row.
Topology uses `structural.beam_topology.define/v1`; leaf rows use a declared
WP01–WP08 semantic operation. Project, member, request, scope, code-data, and
downstream dependency identities must agree. Optional downstream seeds stay
blank when the corresponding construction or optimization operation is not
requested.

Use the shipped workbook as the executable example. Its compact transverse-link
pattern expands to physical link paths during input normalization, keeping every
source cell within Excel's character limit.

## Result, freshness, and receipt tables

| Table | Purpose |
| --- | --- |
| `StructuralResults` | Result states, identities, provenance, diagnostics, and chunked output JSON for every member operation |
| `StructuralFreshness` | One row per distinct result ID bound to workbook, project, batch input revision, and output-table SHA-256 |
| `StructuralReceipts` | Append-only command history, declared write set, input/output revisions, artifact hash, and diagnostics |
| `StructuralBenchmark` | Named environment/workload, sample count, median, p95, and maximum |
| `StructuralHostEffects` | Installed acceptance capture proving worksheet-function host-effect count |

Large output JSON is split into ordered chunks of at most 30,000 characters.
Freshness is reconstructed from the exact input revision, result-table hash,
and set of result IDs. Editing a controlled result or freshness cell prevents
export and current-result reconstruction.

Calculation-package bundles are written beside the workbook under
`StructAutomate Packages`. The returned command receipt binds the file SHA-256.
The sample package contains assumptions, source and calculation revisions,
member check evidence, bar geometry, BBS, quantities, cost, drawing data,
limitations, and signature actions.

## Diagnostics and recovery

- Run `Test-Preflight.ps1` when Excel does not load the XLL. It checks Windows
  and Excel bitness, .NET Desktop Runtime, PE machine type, Authenticode signer,
  manifest hashes, and `SHA256SUMS`.
- A JSON function that spills `execution = rejected_input` also spills a stable
  diagnostic code and message. Correct the named field; do not replace a blank
  with zero unless zero is the intended engineering value.
- A command returning `state = rejected` includes its error type and message.
  Correct the versioned input row and run Create / Validate again.
- If inputs changed, run Calculate Workbook before export. Export accepts only
  one current, untampered calculation package for every requested member.
- Use `Repair-PerUser.ps1` when installed file hashes differ from the
  distribution. The script repeats preflight, replaces the per-user files,
  registers the XLL, and writes a repair receipt.

## .NET library use

The XLL is an adapter over the same `StructuralEngineering.Contracts`,
`Core`, `Reinforcement`, `Codes.IS456`, `Beam`, `Analysis`, `Construction`,
`Optimization`, and `Reporting` projects used by ordinary .NET callers. An
application can reference only the packages it needs and call typed operations
without Excel. Units remain explicit in public names and contracts: mm, N,
Nmm, N/mm², kg, m³, and m².

ETABS force acquisition is added by WP10, and copied-model reanalysis is added
by WP11. Those adapters will feed the same immutable member and operation
contracts used by this standalone workbook.

---
