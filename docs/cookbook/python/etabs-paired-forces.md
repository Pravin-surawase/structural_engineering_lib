---
owner: Main Agent
status: active
last_updated: 2026-11-13
doc_type: guide
tags: [etabs, import, beam, column]
---

# Reconcile paired ETABS beam and column actions

Use `structural_lib.services.etabs_paired_forces.import_etabs_paired_forces` to
reconcile two ETABS 22.7.0 Element Forces table projections against a declared
model, member, station and combination inventory. This API preserves source
rows in ETABS local axes and normalizes stations, forces and moments to mm, N
and N·mm.

## Replay the reference

From the repository root, run:

```bash
./scripts/python_runtime.sh Python/examples/etabs_paired_forces.py
./scripts/python_runtime.sh Python/examples/etabs_paired_forces.py --alternate-units
./scripts/python_runtime.sh Python/examples/etabs_paired_forces.py --missing-combination
```

The first two commands reconcile eight rows for `L2/B1` and `L2/C1`, with
four combinations at one station on each member. Beam B1's signed torque
and moment become −2,250,000 and +18,750,000 N·mm at 1250 mm. Column C1's
axial force becomes −412,500 N at 750 mm in ETABS' compression-negative
convention. The [frozen reference](../../verification/library-029-flow04-paired-intake.json)
gives all six independent expected components for each member.

## Supply your own tables

1. Save each native Element Forces table projection as UTF-8 CSV. Keep its
   title, header, unit row, and all force columns. The beam header includes
   `Step Type`. The column header ends with `Location`. This profile
   accepts blank values for those fields.
2. Create `EtabsForceTable` records using the CSV bytes, ETABS release,
   capture ID and action basis from the same run. The action basis identifies
   the model SHA-256, analysis revision and the section, stiffness and
   connectivity revision. Supply the current action basis separately.
3. Bind each unmeshed member to its ETABS story, label, object and element.
   Supply I/J coordinates in mm and a right-handed local basis. List
   the required object stations in mm and exact combination IDs per member.
4. Declare the native units in `EtabsTableUnits`. For each combination,
   use the source definition's type and declare its ultimate, service or
   sustained-service use. Only static Linear Add combinations are admitted.
5. Call `import_etabs_paired_forces` with an `EtabsPairedForcesRequest`.
   Read `result.to_dict()` for structured status, diagnostics and source rows.

A complete intake returns `COMPLETE_FOR_DECLARED_ROWS` and
`normalized_snapshot`. Engineering status remains `not_evaluated`. A
missing combination returns HOLD and keeps available normalized rows under
`diagnostic_snapshot`. A stale or mixed capture retains source rows and
withholds both normalized snapshots. Duplicate rows, mismatched units and
invalid axes reject the intake. Beam axial or minor-axis actions and column
uplift return HOLD with the signed actions preserved for diagnosis.

This profile covers one object-to-element mapping per member and one row
per declared station and combination. Member transformations, meshed
station-side pairs, automatic combination generation, and downstream
engineering qualification need their own evidence. The
[ETABS source review](../../verification/library-029-flow04-etabs-source-review.md)
records the pending replay against a matched real beam and column export.
