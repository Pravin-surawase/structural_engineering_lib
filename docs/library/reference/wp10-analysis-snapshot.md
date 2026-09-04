# WP10-01 portable analysis snapshot

WP10-01 freezes AO16, `etabs.beam_snapshot.import/v1`, as a reusable offline
contract. It defines what a later getter-only adapter must supply, and what
ordinary Python and .NET callers can validate and replay without ETABS, Excel,
COM, or CSI assemblies.

## Public operations

| Language | Request parsing | Snapshot replay |
|---|---|---|
| Python | `structural_lib.analysis_snapshot.parse_etabs_import_request_json` | `structural_lib.analysis_snapshot.parse_analysis_snapshot_json` |
| .NET | `AnalysisSnapshotCodec.ParseImportRequest` | `AnalysisSnapshotCodec.ParseAndValidate` |

The language-neutral manifest is
`contracts/structural-engineering/operations/wp10.json`; the strict JSON Schema
is `contracts/structural-engineering/schemas/wp10.schema.json`; and both
implementations consume
`contracts/structural-engineering/conformance/wp10-vectors.json`.

## Request and optional evidence

An import request names the expected source/version/model revision, project,
members, selected result sources, result kinds, stations, required provenance,
request identity, and UTC deadline. Member and station scope use tagged modes:
an empty array means all only with `all_beams` or `all_available`; `explicit`
requires at least one identity.

Process identity and model-file SHA-256 are explicit optional evidence records.
`supplied` carries a non-empty value and no reason. `not_requested`,
`unavailable`, and `not_applicable` carry no value and a non-empty reason. A
missing JSON key never silently acquires one of those meanings.

## Raw evidence and normalized snapshot

The embedded raw capture retains:

- acquisition, model, analysis, and result-epoch identities;
- the original length, force, moment, stress, and mass-density units;
- ordered raw records for metadata, points, materials, sections, members, load
  cases, load combinations, result selections, and stations;
- every force row in source order, including object and element stations,
  case/combination, step type/number, and signed P/V2/V3/T/M2/M3 values;
- a chained started/returned ledger for getter calls, including method,
  signature authority, argument digest, return code, raw shape, and UTC time.

The normalized snapshot uses mm, kN, kNm, N/mm², and kg/m³ and retains the
original unit record plus positive one-time conversion factors. It includes
right-handed member axes, the source-to-common transform, physical top/left
faces, point geometry, material and section properties, section assignment
kind, auto-select identity when applicable, modifiers, offsets, releases,
analysis elements, load definitions, selections, and stations in physical,
object, and element coordinates.

Each action row is one concurrent source row; components are never assembled
from unrelated maxima. It binds the member/object/element, station, selected
case or combination, step, action basis, six converted signed components,
getter signature/call, source-row ordinal, concurrency basis, and raw evidence.

Every raw model record and force row appears exactly once in the disposition
ledger as `accepted`, `approved_exclusion`, or `blocked`. Accepted rows bind a
canonical identity. An approved exclusion requires a reason and approval
reference. Any blocked row prevents snapshot acceptance.

## Determinism and result states

Identity-bearing arrays are unique and sorted; force rows retain source ordinal
order. Canonicalization is PF4 compact UTF-8 JSON: object keys sort
lexicographically, arrays preserve declared order, enum values are strings,
numbers are finite, negative zero serializes as `0`, integer-valued floats
serialize as integers, and non-ASCII text remains unescaped UTF-8. The
record, call-ledger, raw-capture, action-row, and snapshot hashes exclude only
their own derived identity/digest fields.

String canonicalization escapes JSON quotation marks, reverse solidus, and
U+0000–U+001F controls only. Other valid Unicode scalar values, including
U+2028 and U+2029, remain literal UTF-8 in both runtimes.

Successful replay reports `completed`, `applicable`, `not_evaluated`,
`complete_for_scope`, `current`, and `unreviewed`. Schema or hash failure is
`rejected_input` and `unbound`. Unresolved units, axes, mapping, selection,
result epoch, or row disposition is a completed acquisition fenced as partial
and current. An incomplete or discontinuous getter ledger is
`transaction_uncertain`, `not_run`, partial, and unbound. Non-success results
never expose a snapshot.

## Boundary

Offline replay proves the integrity and internal consistency of the supplied
portable artifact. It does not prove compatibility with an installed ETABS
version, repeat a structural analysis, mutate a model, validate the vendor's
analysis method, optimize a beam, approve engineering, import a workbook, or
issue a report. Those responsibilities remain with later explicitly gated
packets and existing design/report operations.
