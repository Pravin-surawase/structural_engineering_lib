---
owner: Main Agent
status: active
last_updated: 2026-11-23
doc_type: guide
complexity: intermediate
tags: [local, floor, etabs, review]
---

# Review one floor locally

Use the local `floor-review` command to create a portable JSON package for one
story's geometry, signed actions, source provenance, scoped calculation results,
and exceptions. Every package carries `QUALIFIED_REVIEW_REQUIRED` and `UNREVIEWED` even when
the scoped calculation passes.

```bash
./scripts/python_runtime.sh -m structural_lib floor-review \
  {preview,review} <file> --profile <profile> [-o <new.json>]
```

`preview` reports the accepted local intake without calculation. `review` runs
only the calculation scope admitted by its profile. With `-o`, the command
creates a new JSON file exclusively; without it, it writes JSON to standard
output. A non-accepted intake exits nonzero.

## Start with a prepared beam file

The prepared profile is for an engineer-supplied, single-story list of already
selected factored `mu_knm` and `vu_kn` actions. It does not claim an ETABS case,
combination, station, or analysis result. Download the [CSV template](../../Python/examples/floor_review/prepared.csv),
[Excel template](../../Python/examples/floor_review/prepared.xlsx), or
[JSON template](../../Python/examples/floor_review/prepared.json).

```bash
./scripts/python_runtime.sh -m structural_lib floor-review preview \
  Python/examples/floor_review/prepared.csv --profile prepared-csv
./scripts/python_runtime.sh -m structural_lib floor-review review \
  Python/examples/floor_review/prepared.json --profile prepared-json \
  -o /tmp/prepared-floor-review.json
./scripts/python_runtime.sh -m structural_lib floor-review preview \
  Python/examples/floor_review/prepared.xlsx --profile prepared-xlsx
```

The `.xlsx` template requires a worksheet named `Beams`, literal values only,
and exactly this header row in this order:

```text
beam_id, story, b_mm, D_mm, tension_bar_diameter_mm, span_mm, cover_mm,
fck_nmm2, fy_nmm2, mu_knm, vu_kn, stirrup_diameter_mm, stirrup_spacing_mm
```

The prepared CSV uses the Generic adapter. The JSON template uses
`cli-beam-design-input/v1` with a `beams` array. Empty, multiple
story, missing-unit/value, formula, error-cell, extra-column, or incompatible
office-sheet inputs are blocked with a source location. Map an office-specific
sheet explicitly to this template before importing; do not rename or guess its
columns. `.xlsx` needs the optional local `[xlsx]` dependency.

Prepared `review` sizes rectangular sections using signed factored actions
and evaluates the proposed two-leg link pitch. The displayed source actions
retain their signs. The sizing input uses action magnitudes and selects top
tension for negative moment and bottom tension for positive moment. The
profile uses the same longitudinal centroid distance from each face, derived
as `D - d`, and the supplied steel grade as the sizing material basis.
Use this profile when those settings describe the intended design. An
existing cage requires the actual section inputs in the paired review.

## ETABS export profiles

ETABS remains the licensed Windows analysis environment. The local package
never parses an `.edb`, unlocks a model, changes result selection, runs
analysis/design, or writes back. Capture the EDB name/hash and exact ETABS
release on Windows, then export the selected data and transfer only the
manifest packet and its listed artifacts.

1. On Windows, confirm the saved model, analysis revision, units, and exact
   case and combination selection. Record a capture ID and the
   section/stiffness/connectivity revision before exporting.
2. Export the required tables from the same run through ETABS **Display →
   Show Tables**. Keep the native title, header, units, all components, and
   original signs for the paired profile. Export E2K from ETABS for the
   snapshot profile.
3. Copy the matching example manifest and substitute the recorded facts.
   Record the model identity and inspect each artifact's SHA-256 before
   transfer. In PowerShell, use `Get-FileHash -Algorithm SHA256 <path>`.
   Keep each artifact next to or under the manifest directory. The CLI
   verifies the supplied artifact hashes against local bytes and checks the
   declared capture identities. The operator supplies the evidence linking
   those exported files to the saved model and analysis.
4. Run `preview` and inspect the row dispositions before running `review`.
   Preserve the complete packet and review JSON for audit.

### Strict exported snapshot

Use `etabs-snapshot` for the established export-first packet: an E2K identity
artifact, `Connectivity - Frame` CSV, `Element Forces - Frames` CSV, declared
units, local-axis mapping, selected result identity, source hashes, and exact
non-beam exclusion approvals. It requires `UniqueName` and exhaustively
disposes every source row; any blocked or ambiguous row blocks the packet.

```bash
./scripts/python_runtime.sh -m structural_lib floor-review preview \
  Python/tests/fixtures/etabs/p5_trial_export/floor-packet.json \
  --profile etabs-snapshot
```

The [snapshot manifest](../../Python/tests/fixtures/etabs/p5_trial_export/floor-packet.json)
uses the distinct two-component envelope basis. It is
preview only: no section review is performed from this snapshot.

See [ETABS Exported Snapshot V1](etabs-exported-snapshot-v1.md) for its full
export contract and row-accounting boundary.

### Paired native beam and column actions

Use `etabs-paired` for the narrower native ETABS 22.7.0 Element Forces profile.
The [paired manifest](../../Python/examples/floor_review/etabs-paired/packet.json)
binds separate beam and column tables to one model hash, analysis
revision, section/stiffness/connectivity revision, capture ID, I/J orientation,
right-handed local axes, member/object/element binding, declared stations, and
exact combinations.

```bash
./scripts/python_runtime.sh -m structural_lib floor-review preview \
  Python/examples/floor_review/etabs-paired/packet.json --profile etabs-paired
./scripts/python_runtime.sh -m structural_lib floor-review review \
  Python/examples/floor_review/etabs-paired/packet.json --profile etabs-paired \
  -o /tmp/etabs-paired-floor-review.json
```

Native preview preserves all six signed ETABS components (`P`, `V2`, `V3`, `T`,
`M2`, `M3`) at their source combination and station. It includes columns and
service combinations as intake evidence only. The scoped beam review admits
only horizontal beams with local 2 up, ultimate static Linear Add rows, and
zero `P`, `V3`, `T`, and `M2`; it evaluates signed `M3` and `V2` against the
declared rectangular section, actual bar layers, and two-leg links tied to the
same analysis revision. Declare physical sections in the object I→J station
basis and use that same declared reinforcement at each requested station of
the member. Only the listed sections and combinations are checked. Service
and column rows remain visible for review. A station or action outside the
admitted member check is held or unevaluated.

The sign and local-axis meaning must be reviewed against the ETABS model and
the [CSI ETABS Analysis Reference Manual](https://docs.csiamerica.com/manuals/etabs/Analysis%20Reference.pdf).
The paired API details and its frozen synthetic replay are in
[Reconcile paired ETABS beam and column actions](../cookbook/python/etabs-paired-forces.md).

### ETABS Excel table export

A bounded `.xlsx` table projection is allowed only when the packet names the
exact worksheet. It reads literal cells, rejects formula and error cells, and
projects the worksheet to the same UTF-8 CSV contract while recording both the
original workbook hash and projected CSV hash. Set the artifact's `file` to
the workbook, `worksheet` to the exact sheet, and `sha256` to the workbook's
digest. Keep identifiers with leading zeroes as text. Numeric cells use their
stored values. The projection preserves interior blank lines and the downstream
table contract determines whether those lines are admissible.

## Support and qualification matrix

| Source/profile | Local behavior | Evidence status | Disposition |
|---|---|---|---|
| Prepared CSV/JSON | Preview and rectangular beam sizing review | Implemented local fixture | Supported prepared inputs only |
| Prepared XLSX `Beams` template | Literal worksheet intake | Implemented local fixture; optional dependency | Supported only with exact sheet/header contract |
| ETABS snapshot CSV/E2K packet | Traceable preview and canonical beam requests | Synthetic P5 fixture | Preview only for the provided envelope basis |
| ETABS paired native tables | Signed six-component intake; restricted ULS M3/V2 beam section review | Synthetic fixture | Fixture-only; installed replay and authorized real export pending |
| ETABS table `.xlsx` projection | Explicit worksheet to CSV boundary | Local equivalence test | Requires manifest hash and worksheet declaration |
| ETABS `.edb` | Retained in ETABS only | Historical W2C installed 23.3.1 read-only evidence | Not a local parser; current runtime/model verification required |
| Legacy CSV adapters | Existing compatibility import | Maintained separately | No snapshot identity or complete row-accounting claim |

The [historical Windows W2C receipt](../verification/etabs-excel-beam-w2c-installed-acceptance-transactional-evidence.json)
is limited to its exact ETABS 23.3.1 copied
model and approved read-only scope. It does not qualify the new 22.7.0 paired
fixture profile. Conversely, the paired fixture does not establish an installed
ETABS bridge or a real-export result.

## Review package and limitations

Every package declares its profile, mode, review boundary, source artifact
identity, member geometry, station/combination rows where admitted, evaluation
state, and exception summary. Preserve that JSON with the exact input revision
for reviewer traceability. `NOT_EVALUATED` means no engineering calculation was
made; `HOLD` means a known scope or evidence condition prevents the requested
calculation; `FAIL` and `PASS` are only emitted inside the stated calculation
scope.

BBS and 3D reinforcement remain held pending verified identity between the
checked physical bar paths and the schedule at the same input revision.
Workbench and FastAPI compatibility importers still use the shared CSV
intake. The local workflow emits versioned JSON for a later UI or report.

## Reproduce the fixture evidence

```bash
./scripts/python_runtime.sh -m pytest \
  Python/tests/integration/test_floor_review.py \
  Python/tests/unit/test_floor_prepared.py \
  Python/tests/unit/test_floor_etabs_excel.py \
  Python/tests/unit/test_etabs_snapshot.py \
  Python/tests/integration/test_etabs_paired_forces.py -q
```

The prepared fixtures contain the same two beams and produce the same sizing
results across CSV, XLSX and JSON with different file hashes and row locations.
In the native paired fixture, L2/B1 passes the scoped section checks. L2/B2
fails hogging flexure at 200 mm in `ULS-G1`, with concurrent M3 of −238 kN·m
and V2 of +128 kN. The governing row points to beam-table line 13 and its
source artifact digest. L2/C1 remains intake-only with all six components
retained. The review command writes the full example review package.
