# WP10 portable analysis snapshot and offline normalization

WP10-01 freezes AO16, `etabs.beam_snapshot.import/v1`, as a reusable offline
contract. It defines what a later getter-only adapter must supply, and what
ordinary Python and .NET callers can validate and replay without ETABS, Excel,
COM, or CSI assemblies.

## Public operations

| Language | Request parsing | Snapshot replay |
|---|---|---|
| Python | `structural_lib.analysis_snapshot.parse_etabs_import_request_json` | `structural_lib.analysis_snapshot.parse_analysis_snapshot_json` |
| .NET | `AnalysisSnapshotCodec.ParseImportRequest` | `AnalysisSnapshotCodec.ParseAndValidate` |

WP10-04 adds the production offline normalization route:

```csharp
// Bytes are supplied by the caller; neither operation attaches to a host.
var options = new EtabsNormalizationOptions(
    projectId, adapterBuildId, sourceEvidenceReference, materialClassifications);
EtabsSnapshotResult result = EtabsCaptureProjector.Normalize(
    capturedBytes, expectedFileSha256, options);
// result.Snapshot is supplied only after complete normalization and validation.
```

The optional ETABS assembly owns durable vendor decoding.
`EtabsCaptureProjector.Project` returns the complete hash-bound portable raw
projection or throws on invalid acquisition evidence. Raw projection alone
does not establish snapshot acceptance. `AnalysisSnapshotNormalizer.Normalize`
accepts that raw projection in the pure Analysis assembly and returns a typed
all-or-nothing result. The same raw input and context reproduce the same output;
neither operation consults an application, filesystem or current clock.

Supply a material-name mapping to `SnapshotMaterialClassification` with an
explicit kind and evidence reference. Classification is separate from captured
elastic properties and does not establish concrete or reinforcement strength.

The current `wp10-offline-horizontal-frame/v1` policy uses m/kN/kNm/kN/m2/
kN*s2/m4 source units, horizontal geometry, row-major local-to-global matrices,
global +Z as top, and left as viewed from I toward J. It proves the selected
linear-static dependency closure before accepting `Single Value` rows with
portable null steps. All six signed force components remain from one source row.
Physical stations originate at object I, even when the first available result
is inside an end offset; element station origins remain independent.

Raw metadata contains a complete projection manifest and original acquisition
evidence. Every getter is bound to its ledger ID, ordinal, arguments, return,
outputs, timing, signature and destination record. Catalogue/story/pattern
facts remain metadata evidence; all captured case/combination definitions are
retained. No exclusion approval is invented. Raw member data retains insertion
cardinal point and stiffness-transform state; raw section data retains section
modifiers separately from canonical object modifiers. Consumers must honor
that reference line and those assignments: the normalizer performs no centroid
relocation. Mirroring, nonzero joint offsets or springs, transformed stiffness
and unresolved axes/topology are blocked by this policy.

The original durable ledger stays intact in acquisition evidence. A portable
ledger represents the same instants with UTC `Z` and its own recomputed chain.
Portable numbers use PF4/Python shortest-roundtrip scientific spelling with
lowercase `e`; the existing durable-artifact v1 serializer retains its original
numeric spelling so old captures still validate. Snapshot revision and epoch
IDs are deterministic evidence-derived identities. `current` means internally
consistent at capture, without asserting current live-model freshness.

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
