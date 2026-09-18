---
owner: Main Agent
status: active
last_updated: 2026-09-18
doc_type: guide
complexity: advanced
tags: [etabs, com, safety, evidence, integration]
---

# ETABS API integration guide

This is the entry point for finding and using ETABS API methods in this
repository. The portable catalogue and task recipes support discovery without
starting ETABS. Actual use follows the maintained C# getter host, scoped worker
and installed evidence for the selected operation. The integration boundaries
below also retain the earlier Python bridge contracts; they are not a reason
to create another adapter. Owned-copy mutation remains a separate milestone.

## Start with one task

```bash
./run.sh context show etabs
./run.sh etabs-api search "beam forces"
./run.sh etabs-api workflow forces
./run.sh etabs-api show cAnalysisResults.FrameForce
```

The method card supplies the exact parameter names, ref/out directions,
optional/default values, return type, enum values, object path, installed help
topic and registered getter profiles. Read the workflow's source owners before
writing another wrapper. `interface cSapModel` shows object navigation;
`enum eItemTypeElm` explains the available enum values. `search` returns twelve
matches by default; page with `--offset` and `--limit`.

`./run.sh etabs-api summary` derives coverage and source identity from the
catalogue. The September 18 intake contains every exported interface method
from the installed DLL, and every present method has a matching help topic.
These are documentation/metadata coverage claims, not claims that all methods
have been exercised. Missing maintained candidates stay visible.

`./run.sh etabs-api workflows` lists the authored procedures: attachment,
overview, geometry, materials, forces, tables, model creation, owned reanalysis
and concrete design. The last three describe future owned workflows. They
are not production runners. Arbitrary API sequences are not assumed to work
merely because their individual methods exist.

### How agents obtain the right knowledge

| Need | Maintained source |
|---|---|
| Exact callable, defaults, types, property navigation | Generated assembly metadata in [the compressed catalogue](../reference/etabs-api-catalog.json.gz), queried through `etabs-api` |
| Units, constraints, return meaning, examples | Matching installed CHM, reached through the method's pinned topic |
| Call order, prerequisites, efficiency choices | [Workflow recipes](../reference/etabs-api-workflows.json) and their implementation owners |
| Approved getter shape and decoding | Current C# getter matrices, hosts and focused tests |
| What has actually worked in ETABS | Exact installed receipts; for current acquisition see [bounded acquisition evidence](../verification/etabs-bounded-acquisition-receipt.json) |
| Agent entry point | Existing [API discovery skill](../../.github/skills/api-discovery/SKILL.md), beam skill, context and operation registry |

This uses small on-demand lookups rather than a second documentation service.
Keep the full vendor manual outside version control. The portable catalogue
contains functional metadata and topic identities/hashes, not copied help prose
or examples. Agents on another device can search it without ETABS installed;
reading local help or using a live API requires the matching installation.

### Efficiency rules for implementation

Start with overview, acquire geometry/context only when required, and request
forces only for the selected members and cases. Reuse the existing member,
batch and group paths. Cache accepted definitions by source identity and bind
forces to their own current result epoch. Retain the actual rows and API-call
counts when comparing alternatives. The catalogue lookup is fast; it makes no
claim that a particular live API call is fast on every model.

Do not infer effects from method names. For example, a CSV-file getter writes a
file. Do not infer return meaning from `int`: counts and status codes need their
own documented interpretation, while `GetPresentUnits` returns an enum.
Registration, help coverage and static signature matching are separate from
installed behavior and engineering qualification.

## Versioned authority

The generated catalogue pins ETABSv1 assembly file version `2.16.0.0`, DLL
SHA-256 `393492bd1649ee705c97449cf7d485c61b73ec649ed1d01f47f54f957b277e54`
and installed `CSI API ETABS v1.chm` SHA-256
`0108deeb19fd054ea03a9be89244dac5c8f5995cc44865eaa508b17f675b9d88`.
Its source identity is printed by `summary` and each method card. The older
tracked CHM (`a730756c…`) remains a historical reference; do not substitute it
for the matching installed help. Assembly reflection supplies current callable
signatures; the help supplies semantics. Neither alone establishes live behavior.

Before using a different installation, compare both artifacts:

```bash
./run.sh etabs-api check --assembly "C:/Program Files/Computers and Structures/ETABS 23/ETABSv1.dll" --chm "C:/Program Files/Computers and Structures/ETABS 23/CSI API ETABS v1.chm"
```

Without those arguments, `check` validates repository references only and
explicitly reports that installed identity was not checked. A mismatch fails;
it does not silently select newer signatures.

### Rebuild and read installed help

Use a fresh task-owned evidence directory. From `CSharp`, build the maintained
worker using the pinned SDK and locked restore, then generate metadata:

```powershell
dotnet restore tools/StructAutomate.EtabsWorker/StructAutomate.EtabsWorker.csproj --locked-mode
dotnet build tools/StructAutomate.EtabsWorker/StructAutomate.EtabsWorker.csproj -c Release --no-restore
dotnet run --project tools/StructAutomate.EtabsWorker/StructAutomate.EtabsWorker.csproj -c Release --no-build -- --api-inventory-all "C:\Program Files\Computers and Structures\ETABS 23\ETABSv1.dll" --response "C:\CodexWork\evidence\NEW-TASK\inventory.json"
```

This worker uses reflection only and never creates ETABS objects. It refuses
to overwrite its evidence output. Extract the matching installed help into a
new empty directory, without executing any example. On this Windows host the
32-bit HTML Help decompiler worked; the 64-bit executable produced no files:

```powershell
$apiEvidence = 'C:\CodexWork\evidence\NEW-TASK'
Copy-Item -LiteralPath 'C:\Program Files\Computers and Structures\ETABS 23\CSI API ETABS v1.chm' -Destination (Join-Path $apiEvidence 'etabs-api.chm')
Start-Process -FilePath 'C:\Windows\SysWOW64\hh.exe' -ArgumentList '-decompile help etabs-api.chm' -WorkingDirectory $apiEvidence -WindowStyle Hidden -Wait
```

Confirm HTML files exist. Return to repository root and rebuild the portable
catalogue from the original CHM, copied help extraction and static inventory:

```bash
./run.sh etabs-api build --inventory "C:/CodexWork/evidence/NEW-TASK/inventory.json" --assembly "C:/Program Files/Computers and Structures/ETABS 23/ETABSv1.dll" --chm "C:/Program Files/Computers and Structures/ETABS 23/CSI API ETABS v1.chm" --help-root "C:/CodexWork/evidence/NEW-TASK/help" --output docs/reference/etabs-api-catalog.json.gz
./run.sh etabs-api help cAnalysisResults.FrameForce --root "C:/CodexWork/evidence/NEW-TASK/help" --section parameters
```

`help` verifies the selected topic hash and emits a bounded plain-text section.
Use `--section returns` for its return contract, or `--section all --offset N`
for remarks/examples. The tool does not execute HTML scripts. Build output is
deterministic for identical inputs; it excludes machine paths and capture time.
It checks DLL identity and help topic assembly versions. The operator owns the
fresh CHM extraction; a topic absent from help is reported as a gap.

After refresh, review the changed method/default/property surface and help
coverage, run `check` and the focused `EtabsApiDiscoveryTests` /
`Python/tests/test_etabs_api.py` checks, then qualify only the live operations
needed by the task. Update a workflow when its maintained source behavior or
evidence changes. Do not mark every method qualified to improve a coverage count.

CSI describes the searchable help as containing function syntax, parameters,
history and usage examples on its [official developer page](https://www.csiamerica.com/developer).
This supports using version-matched local help alongside assembly metadata;
unversioned tutorials are not the signature authority.

Refresh signatures by hashing the installed ETABS executable, registered type
library, ETABSv1 assembly, generated wrapper if used, Python executable,
`comtypes`, and installed CHM. Review the changed CHM topics and wrapper shapes,
update fake adapters and strict decoders, then obtain a new installed acceptance.
Do not silently reuse evidence across a runtime-fingerprint change.

## Target discovery and attachment

`discover_etabs_processes_v1()` uses operating-system process information only.
Each `ETABSProcessInstanceV1` binds PID, start time, executable path, version,
hash and architecture. PID without start time is never an identity: PID reuse,
restart, executable drift or architecture drift invalidates the target.

After explicit operator selection, an installed A1 identity probe may call the
CHM-defined `cHelper.GetObjectProcess(typeName, pid)` and getter-only model
identity methods. It displays the selected PID, start time, ETABS version and
model path and creates a short-lived `ETABSTargetObservationV1`. The observation
is revalidated immediately before and after an operation; expiry or any target,
runtime or model mismatch returns `HOLD`.

## Attached and owned lifecycles

Attached access is `ATTACHED_OBSERVE` and getter-only. It must not call
`SetPresentUnits`, result/table-selection setters, run-flag setters, unlock,
save, analysis, design, open, close or exit. If the required units, selection or
finished results are not already observable, the operation returns `HOLD` and
normalizes retained values offline.

Owned-copy mutation is a different future lifecycle. It requires a clean,
operator-saved checkpoint; a new non-existing copy; an owned ETABS process; a
reviewed change set; a single-use mutation capability; and stage-by-stage
readback, recovery and postflight evidence. An attached session can never be
promoted to owned merely because a setter appears reversible.

Live routes remain disabled by default, loopback-only and authenticated. A
server-issued capability binds the exact target observation, access mode,
transaction and expiry. Mutation capabilities are separate and single-use.

## Runtime, lease and supervised execution

`ETABSRuntimeFingerprintV1` measures the library/Python/runtime and every
installed ETABS binding artifact used by the bridge. One OS-wide
`ETABSOperationLeaseV1`, keyed by PID plus process start time, excludes another
API worker, CLI or Excel-launched bridge. The lease is not stolen after heartbeat
loss; uncertainty fences the target for operator review.

COM work runs in a supervised child broker whose COM apartment is initialized,
used and uninitialized on its one STA thread. The parent owns the lease,
heartbeat, deadline and ledger. A deadline terminates only the broker, never the
attached ETABS process. COM cancellation or broker termination does not prove
that ETABS stopped processing, so timeout yields `RESTORATION_UNVERIFIED` or
`TRANSACTION_UNCERTAIN`, with no automatic reconnect or replay.

## Binding shapes and strict decoding

The retained 23.3.1 metadata shows both direct-return and return-code shapes.
For example, `GetPresentUnits()` is a direct enum value, while multi-output
methods expose by-reference outputs plus a final CSI integer return code in the
observed `comtypes` shape. Arrays may arrive as tuples or lists; single outputs
may be scalar; empty/singleton/null shapes must be handled per the proved method,
not by a generic guess.

Before every call, append and durably flush a bounded `STARTED` record. Before
decoding, append the raw shape and return value as `RETURNED`. Strict decoding
then checks the exact output count, integer return code, array lengths, finite
numbers, enum domain, duplicate identities and row bounds. Decode failure never
erases the raw call evidence. The hash-chained ledger verifier rejects gaps,
truncation, corruption, duplicate JSON keys and unmatched `STARTED` records.

## Units, signs and identities

Read present/database units with getters and convert offline into the canonical
library units documented by each contract. Never change an attached model's
present units for convenience.

Retain signed `P`, `V2`, `V3`, `T`, `M2` and `M3` from the same ETABS result row.
Do not create a synthetic row from independent component extrema. The project
criteria must map positive and negative local M3 to opposite physical
TOP/BOTTOM tension faces and record the local-axis and factored-action basis.
Magnitude may be used only after the physical face is fixed.

Keep object unique name, label/story, element identity, object/element station,
case or combination identity, step type/number and item type distinct. Database
table-display selection is also distinct from `Results.Setup` selection. A
conversion between these identities needs explicit retained evidence.

## State, freshness and result epochs

Attached operations capture declared getter-only state before and after and
require exact equality. They do not restore state with setters. Drift or an
incomplete postflight fences the process instance.

An open session defaults to `SESSION_UNSAVED_OR_UNKNOWN`. A file hash or lock
state cannot prove that in-memory edits are absent. `SAVED_CLEAN_CONFIRMED`
requires an installed cleanliness signal with call identity or an explicit
operator-saved `ETABSSavedCheckpointV1` bound to PID, session, path, size, hash,
mtime and timing. Any later file/session drift invalidates it.

`ETABSResultEpochV1` is separate from model freshness. It binds the uninterrupted
process/runtime, model or copy, transaction/change set, complete authorized case
dependency closure, pre/post case statuses, run flags, analysis/design call
identities, selection and result digest. Existing `FINISHED` status alone cannot
create a fresh epoch, and reconnect/timeout invalidates the epoch.

## Tables, export and matched design

Table catalogue, field schema, display selection and table rows are different
operations. `GetAvailableTables`, `GetAllFieldsInTable` and
`GetTableForDisplayArray` require their individually proved signatures and
bounds. C0 defines only generic requested-table and export-manifest contracts;
it deliberately claims no installed ETABS table, column, type or parser support.

Until an installed API export signature is proved, acquisition mode is
`OPERATOR_UI_EXPORT`. C1 must create a new destination, bind target/runtime/
model/result epoch and pre/post state, wait for completion, reject pending WAL
or SHM files, freeze and hash the artifact, and inventory the actual schema.
C2 alone may implement the allowlisted offline SQLite parser for that accepted
schema. It opens only the frozen copy read-only, disables extensions and
attachment, checks integrity and enforces file/table/field/type/row/null/key and
duplicate bounds. It never writes to or imports data into ETABS.

Matched concrete-design comparison also binds the exact design combinations,
preferences, explicit/default overwrite meaning, design procedure, resolved
section and auto-select state, beam rebar definition, concrete material,
separate longitudinal/transverse reinforcement materials and grades, result
item type, warnings and result epoch. The comparison is diagnostic, never an
approval verdict.

## Supported and forbidden operations

The current attached boundary permits only explicitly allowlisted identity,
state, catalogue, status and already-selected result getters whose exact
signature and strict decoder are retained. It stops before a getter if its
required selection, unit, result freshness or physical interpretation is not
already proved.

Forbidden on attached sessions are all setters and every operation that can
open/switch/save/unlock/change/close a model, change units or selections, set run
flags, run analysis/design, export through an unproved API shape, or exit ETABS.
Legacy adapters that temporarily changed units are deprecated and are not the
A0/A1 attached path.

Failures are classified rather than retried: target/runtime/model drift,
capability expiry/replay, lease contention/loss, broker hang, call/decode error,
state drift, unmatched ledger record, evidence corruption, unknown freshness or
result epoch, incomplete criteria and unobserved export schema each yield a
typed `HOLD`, fence or uncertain transaction as appropriate.

## Evidence levels and examples

A0 examples and tests use fake process providers, getter-only readers and
supervised broker callables. They inject PID reuse, target/runtime drift,
capability replay, lease contention/loss, broker hang, call/decode failure,
ledger truncation and artifact corruption. B0 fake rows prove signed-face and
same-row action handling. B1A uses authored criteria/catalogue fixtures marked
`AUTHORED_FIXTURE_HOLD`. C0 uses generic bytes and asserts that `sqlite3`, ETABS,
COM and UI are never invoked.

These are software acceptance tests only. A1/C1 installed observations require
separate user authorization and new target/runtime/pre-post evidence. No fake,
static signature audit, prior installed run, selected candidate or diagnostic
comparison is professional review, construction approval or release authority.
