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

## Completion plan and current knowledge boundary

The owner requested reusable API knowledge before the next runtime milestone.
`ETABS-API-GUIDE` is merged in
[PR #993](https://github.com/Pravin-surawase/structural_engineering_lib/pull/993).
`ETABS-API-READINESS` completes its project setup, coverage navigation,
procedure evidence and agent handoff. Its
[acceptance contract](../verification/etabs-api-readiness-acceptance.json)
starts from `a9f0ec11cf06896e9211d7d0d13d6eb5bbd8939f`.

**Done means:** an agent can identify the correct implementation and exact
method, find its semantics and evidence, see what is still unknown, and pick
the next bounded action without redoing the inventory. It does not mean every
possible ETABS procedure has been implemented or exercised. The complete
method surface is enumerable; authored procedures expand with approved tasks.

| Step | Current state | Exit evidence / next action |
|---|---|---|
| S1 — baseline and setup | Complete | Freshly fetched #993 baseline, isolated writer, Python source binding, SDK manifest and current plan inspected; original checkout edit preserved. |
| S2 — complete surface map | Complete implementation and command replay | Fresh-worktree coverage reconciles 143 interfaces, 1,343 present methods and 126 properties. Missing/unmapped/unclassified counts remain separate. Focused regression verdict follows in S5. |
| S3 — procedure and evidence map | Complete source reconciliation | Fourteen recipes link existing source/test/evidence paths; every referenced method is indexed, including the explicitly missing design candidate. Both installed artifact hashes and reference checks pass. |
| S4 — reusable handoff and rework plan | Complete implementation | Existing skill/context/guide route setup, known issues, acceptance and step/blocker updates. Current plan, task board and next-session brief agree on the next runtime milestone. |
| S5 — acceptance and integration | Active; final verdict recorded externally | Run focused lookup/CLI and documentation checks, then independent acceptance, candidate integrity and required hosted checks on one frozen candidate. Exact verdicts stay in the task delivery ledger. |

### Project setup: read the owner of each fact

| Concern | Authority and bounded check | Meaning for this work |
|---|---|---|
| Checkout, branch, predecessor and device | [Git workflow](../git-automation/git-workflow-single-source.md); `git_state.py --json --worktrees` after an explicit fetch | Verify actual cwd/remote and candidate base. An old clean evidence worktree or locally cached remote ref is not proof of current main. Preserve other work. |
| Python execution | `./scripts/python_runtime.sh --diagnose` | A shared environment is valid only when `source_bound` points at the current worktree. Use this launcher for all discovery and tests. |
| C# runtime/build | [CSharp/global.json](../../CSharp/global.json), [solution](../../CSharp/StructAutomate.slnx), [prepared runtime plan](../planning/xll-product/etabs-design-workflow.md) | Exact SDK 10.0.400 and Microsoft.Testing.Platform are pinned. Locked restore/Release build is needed for changed C# or inventory generation; do not repeat it for unchanged documentation. |
| ETABS version/help | Catalogue source hashes and `check --assembly … --chm …` below | Offline search needs no installation. Both matching installed artifacts are required to claim installed identity; extracted help stays device-local. |
| Product architecture | [XLL entry point](../planning/xll-product/README.md), [current plan](../planning/xll-product/current-plan.md), workflow recipe owners | Native C# owns this Excel/ETABS path; Python/FastAPI/React are separate library/web layers. The Python bridge contracts retained below are not proof of a current C# production route. |
| Existing application evidence | [WP10 completion](../verification/wp10-completion-source-evidence.json), [bounded acquisition](../verification/etabs-bounded-acquisition-receipt.json), WP11 receipts in the current plan | Reuse evidence for its exact source/runtime/model/profile only. This knowledge task does not replace installed Excel acceptance or broaden beam support. |
| Session, controls and scope | Root AGENTS.md, `session begin`, `context show etabs`, [control plane](../../scripts/control-plane.json) | One parent and one bounded packet; existing operations and maintained owners come first. |

On Windows, run the shown `./run.sh` commands as `bash ./run.sh …` from the
explicit repository root. Commands in the metadata-build section alone run
from `CSharp`. Use `rg --files` before a guessed path and write edited text as
UTF-8 with LF; do not alternate Windows-default newlines with patch writes.

### Complete coverage and choosing the next procedure

```bash
./run.sh etabs-api coverage
./run.sh etabs-api coverage --filter Load --limit 12
./run.sh etabs-api coverage --filter supports
./run.sh etabs-api coverage --offset 12 --limit 12
./run.sh etabs-api workflow recovery
```

Coverage is generated from the pinned catalogue and current recipes, not a
second hand-maintained inventory. Each exported interface appears once, even
if it has no recipe. Counts separate present methods, missing candidates,
properties, matching help, registered getter names, unknown effects and
methods mapped to a recipe. Totals always refer to the entire catalogue;
filtering/paging changes only the displayed rows. Shared methods count once
per interface even when several recipes use them.

Use `interface <name>` to list its methods, then `show <interface.method>`.
A recipe link describes a sequence, not a permission or a live-test pass.
Each workflow's `verification` gives focused test paths, retained evidence
paths and the exact qualification boundary. `check` verifies these links as
well as method/implementation references. File existence does not prove a
receipt applies to the current runtime/model, or detect every semantic change;
inspect affected owners when they change.

| Need | Recipe(s) | Current boundary / remaining work |
|---|---|---|
| Target, lightweight inventory | `attach`, `overview` | Existing exact-target getter host and retained overview evidence. |
| Geometry, materials, units, physical support | `geometry`, `materials`, `units`, `supports` | Existing admitted profiles; general native-unit detail, effective material and support/span interpretation remain C0a. |
| Demands and their source definitions | `loads`, `result_selection`, `forces`, `tables` | Scoped static acquisition and retained schemas; broader dynamic/nonlinear dependency closure and arbitrary tables need named qualification. |
| Failure and cleanup | `recovery` | Existing broker/lease/journal controls; no new ETABS solver-cancel capability. |
| New model, copy/update/analyse, ETABS design | `create_model`, `owned_reanalysis`, `concrete_design` | Future procedures. Method metadata and planned order do not supply production runners or installed acceptance. |
| Any other exported interface | `coverage` → `interface` → `show` → matching help | Discoverable. If no recipe/evidence exists, record the gap and qualify only the methods needed by the approved task. |

### Update the plan after each step or blocker

Keep the active task's step table in its maintained plan, with **state,
evidence, remaining dependency and next action**. Use planned → active →
complete, or blocked with an explicit unmet dependency. A completed step needs
its exit evidence; writing code or finding a method is not an acceptance pass.
After a step, update its row and the next row before proceeding. Update sooner
when a failed experiment changes the scope, dependency, chosen procedure or
verification basis. Routine polling does not require a new plan revision.

When stuck: retain the exact failure and source identity, isolate the failing
stage with the smallest useful diagnostic, distinguish confirmed cause from
hypothesis, and amend the plan with the decision and measurable exit. Continue
independent authorized work. New input is needed only when an actual unresolved
owner decision controls the dependent action. Record material issues and
recurrence IDs in the newest task-owned SESSION_LOG entry, using the
[existing recurrence index](../verification/rework-recurrence-index.json).

Finish all versioned writes before starting the formatter and do not edit
files while its scope snapshot is active (RR-003). Before `CANDIDATE`, finish
all plan/handoff/evidence writes. After
freeze, record verification, hosted run and merge progress in the executable
session delivery ledger and external task evidence. Do not edit the frozen
candidate merely to mark a checkbox. A changed outcome/contract uses the
repository's REPAIR/REPLAN transitions and updates the plan before a new
candidate. The next task reconciles the final delivery facts at intake.

| Trigger / known rework | Required response and next exit |
|---|---|
| Installed DLL/help hash differs | Keep offline discovery usable, but refresh metadata/help and review the changed methods before installed use. New signature presence alone is insufficient live proof. |
| Missing method, unknown effects or unregistered getter | Inspect exact help and maintained adapter; add only the needed scoped contract/evidence. `cDesignConcrete.GetComboStrength` remains missing; do not infer it from its setter. |
| New units, case type, section/support or result semantics | Preserve the unsupported source outcome and route qualification to C0a/C0c. The assumed-input review uses a separately identified scenario; it cannot erase original actions or requirements. |
| Timeout, uncertain cleanup or incomplete capture | Follow `recovery`, retain journal/cleanup facts and isolate the failing stage. RR-046's hosted deadline cause is still unconfirmed; replay the affected tests before considering a code or budget change. |
| Empty Windows help extraction | RR-020: verify output files; use the documented task-local copy and 32-bit decompiler. No files means extraction did not succeed. |
| Wrong cwd/path/arguments or mixed newlines | RR-005/RR-045: explicit workdir, targeted file discovery, canonical launchers and UTF-8 LF. Check actual file bytes before candidate integrity. |
| Brief/session format or new branch upstream failure | RR-004/RR-009: retain `Current`/`Next` briefing rows and exact recurrence syntax; use the canonical Git flow and exact branch tracking. |
| First/second candidate rejection | Use the enforced repair ceiling; a second rejection requires an evidence-changing replan, not another identical attempt or relaxed checks. |

### What follows this knowledge milestone

1. **BEAM-PROVISIONAL-REVIEW U1–U5:** use the existing
   [execution card and R01–R12](../planning/xll-product/etabs-design-workflow.md#prepared-next-milestone-persistent-assumptions-and-provisional-review--2026-09-18).
   Its first exit is a complete field/consumer/fallback contract, followed by
   persistent resolution, independent provisional calculations, Excel refresh
   and installed acceptance. New runtime behavior remains unimplemented here.
2. **C0a/C0c qualification:** add only the source/method/profile gaps needed for
   the approved beam cohorts. Bind actual units, source closure, supports,
   stations and independent engineering examples; update the relevant recipe
   and evidence when each named packet passes.
3. **C1 then D/E/F/G:** practical alternatives precede copied-model reanalysis,
   bounded overnight execution and portable final outputs. Owned application
   gates and the project-end PF9 timing/memory gate remain in the product plan.

The knowledge milestone can close while future procedures remain explicitly
unqualified. It should not become an open-ended attempt to invoke every ETABS
method or rewrite the completed acquisition/design foundations.

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
overview, geometry, materials, units, loads, supports, result selection, forces,
tables, recovery, model creation, owned reanalysis and concrete design. The
last three describe future owned workflows. They
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
