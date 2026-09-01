---
owner: Main Agent
status: active
last_updated: 2026-09-02
doc_type: guide
complexity: advanced
tags: [etabs, com, safety, evidence, integration]
---

# ETABS API integration guide

This guide defines the maintained safety boundary for ETABS automation in this
repository. It describes software contracts, not permission to attach to or
change an installed ETABS session. Installed read-only evidence is acquired only
in a separately authorized A1/C1 session; setters, analysis, design, save,
unlock, model switching and exit remain forbidden until their later owned-copy
milestones are accepted.

## Versioned authority

The tracked API reference is
`docs/reference/CSI API ETABS v1.chm`, 4,000,373 bytes, SHA-256
`a730756ccd283ffc17f592a2e21c973d50b5a14ed3489244fca1524e58f3a700`.
That exact CHM is the signature authority for this guide. Retained installed
metadata separately records ETABS 23.3.1.4563, ETABSv1 assembly 2.16.0.0 and
`comtypes` 1.4.16; those observations do not make a different installation
compatible automatically.

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
