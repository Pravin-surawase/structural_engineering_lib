---
owner: Main Agent
status: active
last_updated: 2026-08-23
doc_type: guide
complexity: intermediate
tags: [etabs, import, evidence, read-only]
---

# ETABS Exported Snapshot V1

## Boundary

The P5 path is export-first and evaluation-only:

`ETABS exported files -> canonical snapshot -> canonical beam request`

ETABS and the EDB remain on the Windows host. The Mac repository consumes only
exported artifacts. This workflow does not unlock a model, start or change
analysis, modify data, save a model, write back, or parse EDB binary content.
Snapshot acceptance does not validate the ETABS model or analysis and does not
establish code compliance, release approval, or qualified engineering review.

## Trial-compatible acquisition matrix

| Checkpoint | Preferred trial path | Valid fallback when the API is unavailable | Retained evidence | Never allowed in P5 |
|---|---|---|---|---|
| Source identity | Record the EDB file name and SHA-256 on Windows; open the EDB only through ETABS | Same manual identity capture | EDB name and hash, project ID, export ID, UTC export time, exact ETABS version | Copying the EDB into a parser, direct binary parsing, unlock, save, or write-back |
| Model definition | Use ETABS export to create E2K without changing the model | Manual E2K export through the ETABS UI | E2K bytes and SHA-256 | Treating E2K as analysis proof or implementing a broad model parser in P5 |
| Geometry table | Read-only selected-table export | Manual `Connectivity - Frame` CSV export | Exact CSV bytes, table identity, headers, row ledger, SHA-256 | Inferring missing sections, units, member identity, or destinations |
| Force table | Read-only selected-table export for one named case, combination, or source envelope | Manual `Element Forces - Frames` CSV export | Exact CSV bytes, result selection, local-axis mapping, units, row ledger, SHA-256 | Running/changing analysis or mixing unnamed cases and envelopes |
| Archive tables | Export selected CSV, XML, or Excel tables | Manual table export in any supported archive format | File name, table name, media type, byte count, SHA-256 | Treating an archived table as calculation input unless the canonical CSV path parses it |
| Transfer and verification | Hash files on Windows before transfer and verify exported bytes on the Mac | Manual copy followed by the same hash verification | EDB hash recorded on Windows; exported-file hashes verified from local bytes | Re-exporting merely to make hashes match or silently substituting a different file |

The trial API is optional. A complete manual ETABS table export is an equally
valid acquisition path because both paths converge on the same exported-file
contract.

## Required P5 packet

The canonical builder requires:

- project ID, export ID, source EDB name/hash, UTC export time, and ETABS version;
- one E2K model-definition artifact;
- separate geometry and frame-force CSV artifacts;
- explicit `m`, `kN`, `kN-m`, `mm`, and `N/mm2` unit declarations;
- explicit `M3 -> mu_knm` and `V2 -> vu_kn` local-axis mapping evidence;
- one exact load-case, load-combination, or source-envelope identity;
- ETABS `UniqueName` for every accepted beam geometry row;
- exact approvals for every intentional non-beam exclusion; and
- explicit effective-depth detailing diameters matching the import basis.

Additional selected CSV/XML/Excel table exports may be archived. Their bytes
and hashes enter snapshot identity, but they are not parsed as calculation
inputs.

## Row accounting

Every physical row in the two calculation-source CSV files has exactly one
disposition:

- `ACCEPTED` — normalized and mapped to a stable canonical beam member;
- `APPROVED_EXCLUSION` — an exact source row is outside beam scope and carries
  a reason plus approval reference; or
- `BLOCKED` — malformed, ambiguous, unmatched, unapproved, or otherwise unsafe.

Any blocked row or unresolved ambiguity blocks the complete snapshot and
exposes no canonical beam requests. An approval that matches no excluded row
also blocks; approvals cannot be used as broad filters.

## Deterministic identity

The snapshot SHA-256 covers the versioned project/export identity, all source
artifact identities, units, local-axis mapping, result selection, normalization
ledger hash, stable member mapping, exhaustive row dispositions, exclusion
approvals, ambiguity list, and calculation-bearing canonical request payloads.
The hash excludes itself and the request `source_metadata`; emitted requests
then carry the verified snapshot hash and full source-hash map.

The maintained entrypoint is
`structural_lib.imports.build_etabs_canonical_snapshot_v1`. It delegates CSV
parsing to `parse_dual_csv_lossless` and emits existing
`ProjectBeamDesignInputV1` objects. `ETABSAdapter` remains its internal parsing
delegate. `normalize_etabs_forces`, `load_etabs_csv`, and
`create_job_from_etabs` remain compatibility helpers and do not establish this
snapshot contract.

## Deterministic fixture

The synthetic fixture under
`Python/tests/fixtures/etabs/p5_trial_export/` contains an E2K identity artifact,
two selected calculation CSVs, and one XML table catalog. It represents two
beams plus one explicitly approved column exclusion and contains no live model
or protected-code content.
