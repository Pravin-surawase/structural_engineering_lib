---
owner: Main Agent
status: active
last_updated: 2026-08-24
doc_type: guide
complexity: intermediate
tags: [api, compatibility, migration, lib-pro-007]
---

# LIB-PRO-007-P7 compatibility migration

P7 converges imports and compatibility metadata after the P1-P6 calculation
owners are established. It does not remove a public name, promise a removal
version, authorize a release, or promote engineering suitability.

## Recommended imports

For end-user workflows, use the package-root facade when it exports the
required object:

```python
from structural_lib import design_beam_is456
```

For library implementation code, import the owning module so the architecture
and calculation authority are explicit:

```python
from structural_lib.services.beam_api import design_beam_is456
from structural_lib.codes.is456.beam.flexure import design_singly_reinforced
```

`structural_lib.services.api` is a supported explicit service facade.
`structural_lib.api` remains import-compatible and exposes the same objects,
but it is retained for compatibility rather than recommended for new callers:

```python
from structural_lib.api import design_beam_is456  # retained compatibility
```

The retained facade does not wrap the function, change its signature, fill a
default, or run another calculation. A stable re-export is not deprecated just
because it is a facade, so importing `structural_lib.api` does not emit a
warning and has no removal schedule.

## ETABS compatibility boundary

The maintained P5 exported-file snapshot entrypoint remains
`structural_lib.imports.build_etabs_canonical_snapshot_v1`. It produces the
project/export-bound snapshot with complete row dispositions, ambiguity
accounting, source hashes, and snapshot identity.

The historical helpers `normalize_etabs_forces`, `load_etabs_csv`,
`create_job_from_etabs`, and `create_jobs_from_etabs_csv` remain callable but
are `HELD_COMPATIBILITY`. Their legacy return contracts cannot represent the
accepted P5 snapshot identity and some accept historical material defaults.
Their outputs must not be described as accepted canonical snapshots.

`ETABSAdapter` remains the parsing delegate. Calculation intake uses
`parse_single_csv_lossless` or `parse_dual_csv_lossless`; no P7 path accesses a
live ETABS model, EDB file, analysis controls, or write-back.

## Machine-readable dispositions

The deterministic [compatibility ledger](../reference/api-compatibility-ledger.json)
uses exactly one of these dispositions for each in-scope record:

- `CANONICAL_OWNER`
- `INTENTIONAL_PUBLIC_FACADE`
- `DELEGATING_COMPATIBILITY_SHIM`
- `MAINTAINED_CALLER_MIGRATED`
- `HELD_COMPATIBILITY`
- `RETIREMENT_CANDIDATE_PENDING_APPROVAL`
- `OUT_OF_SCOPE_PRESERVED`
- `BLOCKED_AMBIGUOUS_OWNER`

The checked-in JSON uses the generator's lossless `column-dictionary-v1`
encoding so the complete record set remains below the repository file-size
limit; generation and tests expand it before comparing the full contract.

The ledger reconciles every root, service, and legacy facade projection with
the live [API classification](../reference/api-classification.json). Archives,
historical migration material, vendor content, fixtures/golden evidence, and
foreign branches or worktrees remain preserved and out of scope.

No P7 item is authorized for deletion. A future retirement requires an exact
caller census, canonical replacement, behavior difference, retention impact,
rollback path, and separate owner approval.
