# Excel -> Python -> ETABS Beam Pilot V1

**Type:** Guide
**Audience:** Developers
**Status:** Complete
**Next Phase:** W2 Integrated; Installed Retry Held Fail-Closed; Mac Evidence Review
**Created:** 2026-08-28
**Last Updated:** 2026-09-01
**Importance:** High

## Outcome

The repository now contains a bounded Windows pilot that lets the existing
macro-free Excel Office.js task pane call local Python, attach to an already-open
ETABS model, read an exact result case or combination, design up to five beams
with the canonical IS 456 library, and write a controlled result table back to
Excel.

```text
Excel Office.js task pane
        | trusted localhost HTTPS
        v
FastAPI /api/v1/etabs-bridge/v1
        | worker-thread COM apartment
        v
already-open ETABS copied model
        |
        +-- geometry + every FrameForce station
        v
canonical Python beam design/detailing
        |
        v
Excel ETABS_Pilot / tbl_ETABS_Pilot_V1
```

Excel is the operator and review surface. ETABS remains the global-analysis
source. Python owns validation, action selection, and the canonical beam design.
No VBA module is required for this route.

## Why this route

Python in Excel is not the local integration runtime for this task. Microsoft
documents that its Python calculations run in a secure Microsoft Cloud
container and cannot access the local computer or network. That prevents it
from attaching to a desktop ETABS COM process or importing an arbitrary local
repository checkout. See [Microsoft's Python in Excel data-security
documentation](https://support.microsoft.com/en-us/office/data-security-and-python-in-excel-33cc88a4-4a87-485e-9ff9-f35958278327).

The existing Office.js add-in already has a trusted localhost HTTPS server and
same-origin `/api/` proxy, so the pilot extends that maintained transport. A
direct desktop-Python Excel add-in such as PyXLL could be evaluated later, but it
would add a second deployment and trust model and is not needed for this proof.

## Implemented contract

| Operation | Endpoint | Effect |
|---|---|---|
| Check Python/library/COM readiness | `GET /api/v1/etabs-bridge/v1/status` | Read-only; does not attach to ETABS |
| Prove the open model identity | `POST /api/v1/etabs-bridge/v1/connect` | Attaches, reads model path/name and ETABS version, then releases the COM apartment |
| Extract and design beams | `POST /api/v1/etabs-bridge/v1/beam-pilot` | Temporarily changes result selection/present units, restores both, and makes no model-data edit |

### Live-route startup and request gate

The default application mounts only `status` and the retained-evidence
`beam-demand` calculation. COM-attaching routes are absent from both routing
and OpenAPI until `ETABS_LIVE_BRIDGE_ENABLED=true`. That startup opt-in is
accepted only for a loopback `HOST`, enabled JWT authentication, and a
non-default secret. Each live request is then checked again for a loopback peer
and the `etabs:live:read` scope before any COM boundary can run.

`beam-pilot` is classified separately because it temporarily changes ETABS
present units and output selection even though it restores the prior state and
does not edit model data. It remains absent unless
`ETABS_LIVE_MUTATION_ENABLED=true` and requires the narrower
`etabs:live:mutate` scope. Container entrypoints bind publicly only with both
live flags disabled.

The beam-pilot request must explicitly provide:

- exact ETABS case or combination name and kind;
- beam count from 1 to 5;
- `fck` and `fy`;
- clear cover, selected longitudinal bar diameters, stirrup diameter/legs and
  support/midspan spacing;
- compression-steel depth `d'`; and
- IS 456 or IS 13920 detailing selection.

ETABS supplies frame identity, storey, endpoints, span, rectangular section
width/depth, section material-property name, and all returned `FrameForce`
rows. The pilot retains signed station results and sends the absolute governing
`V2`, `T`, and `M3` magnitudes to the canonical beam design. It never infers
concrete or reinforcement grades from an ETABS material-property label.

## Windows setup

### Machine role

The Mac is the programme's primary development/integration machine. Windows is
the installed Excel/ETABS testing and evidence machine. Keep normal feature
work, PR integration, and current `main` on the Mac; use Windows only for exact
installed behavior, copied-model/workbook evidence, and bounded host-specific
repairs. Tracked work moves only through GitHub under the one-branch/one-writer
rule. Never copy repository source between the machines through OneDrive/SMB,
and never commit proprietary model/workbook bytes or credentials.

The Windows W2A preparation verified Git `2.55.0.windows.3`, GitHub CLI
`2.98.0`, `uv 0.12.7`, Node `24.19.0`, npm `11.17.0`, Python `3.11.15`, and
`comtypes 1.4.16`. The primary checkout owns the shared `.venv`; linked
evidence worktrees use `scripts/python_runtime.sh`, which binds imports back to
the invoking worktree. The old unusable environment is retained recoverably as
`.venv-broken-20260829` rather than deleted.

After installing or changing machine-level tools, start a fresh terminal/Codex
process so the user `PATH` is inherited. Then verify:

```bash
./scripts/python_runtime.sh --diagnose
./scripts/python_runtime.sh scripts/node_runtime.py --show-runtime
./scripts/agent_start.sh --quick
gh api user --jq .login
```

The expected source diagnosis must name the current task worktree and report
`source_bound=true`. On Windows, the onboarding check now canonicalizes MSYS
and Python paths before comparing them; a path-separator difference is not
source shadowing. The launcher also defaults Python to UTF-8, recognizes
`.venv/Scripts/python.exe`, and the Node selector recognizes `.exe`/`.cmd`.

System Git uses `core.autocrlf=true` on this host. `.gitattributes` therefore
forces LF for byte-frozen ETABS export/source formats and executable shell
scripts. If a snapshot hash
changes, compare the Git blob and worktree bytes; do not regenerate expected
hashes to conceal CRLF conversion.

Prerequisites:

- 64-bit Windows with a supported 64-bit Python and ETABS installation;
- Microsoft Excel capable of sideloading the existing Office.js manifest;
- Node.js for the local task-pane HTTPS server;
- a trusted localhost certificate as described in
  [the add-in README](../../excel_addin/README.md); and
- a saved copied ETABS model with the requested case/combination already
  analyzed.

Run ETABS and the FastAPI process at the same Windows privilege level. For
example, do not run one as Administrator and the other as a normal user.

For a new Windows primary environment, prefer the installed `uv` runtime from
repository root in PowerShell:

```powershell
uv python install 3.11
uv venv --python 3.11 .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip install -e "Python[etabs]"
```

The prepared W2A host installed the complete repository extras because it is a
general evidence machine. A minimal pilot host needs only the maintained base
requirements and `Python[etabs]`; do not reinstall or replace a healthy shared
environment from a linked worktree.

Start FastAPI from repository root:

```powershell
.\.venv\Scripts\python.exe -m uvicorn fastapi_app.main:app --host 127.0.0.1 --port 8000
```

In a second PowerShell window, start the existing trusted add-in origin:

```powershell
Set-Location excel_addin
npm install
$env:E1_OFFICE_KEY_PATH = "C:\absolute\path\localhost.key"
$env:E1_OFFICE_CERT_PATH = "C:\absolute\path\localhost.crt"
npm run serve
```

Then:

1. Open ETABS and the saved copied `.edb` model. Confirm the intended result
   case or combination exists and has current analysis results.
2. Sideload `excel_addin/manifest.xml` and open the task pane in Excel.
3. In **ETABS beam pilot**, confirm that bridge status is
   `READY_TO_CONNECT`.
4. Select **Connect to open ETABS model** and verify the displayed `.edb` name
   and ETABS version.
5. Enter the exact result name and all explicit design/detailing values.
6. Select **Read and design first beams**.
7. Review `ETABS_Pilot / tbl_ETABS_Pilot_V1`. The add-in creates this surface
   only when absent, updates only the exact V1 table, and refuses to overwrite a
   colliding worksheet or altered table.

## Windows ETABS/Excel recurring-pitfall checklist

Read this section before launching ETABS, attaching COM, or opening Excel for
any W2 continuation. It records repeated symptoms from W1/W2 so a later agent
does not spend an installed session rediscovering them.

| Repeated symptom | Confirmed cause | Prevention and required proof |
|---|---|---|
| Work runs from protected/stale Windows `main` or the wrong worktree | The Windows primary checkout is intentionally a `HOLD_MAIN` lane while GitHub/Mac owns integration | Fetch first; print repository root, branch, head, tree, upstream, and `source_bound=true`; create a fresh one-writer worktree from the exact authorized SHA. Never copy repository files between machines. |
| GitHub commands fail or target the wrong identity | CLI authentication or repository binding was assumed rather than checked | Run `gh auth status`, verify the active account, query the exact repository, then prove the target remote branch/PR state. Authentication is setup evidence, not authority to create/merge a PR. |
| `session begin` refuses a new W2 task | A historical unmatched Phase A checkpoint remains in the shared store | Record the exact refusal, do not invent timing, and do not close or overwrite another task's checkpoint. Continue only from exact Git/source/runtime evidence when the task packet permits it. |
| Python cannot import `comtypes`, or a large untracked `Python/uv.lock` appears | `comtypes` is in the optional `etabs` extra; a bare `uv run` can resolve a new environment and generate a lock | Use the maintained runtime with the `etabs` extra and 64-bit Python. Check `git status` immediately; remove only a task-generated untracked lock after resolving its exact in-worktree path. |
| COM attach behaves differently from the tested bridge | Python/ETABS bitness or Windows privilege levels differ | Prove 64-bit Python, ETABS, typelib, wrapper/runtime hashes, and matching ETABS/API-process privilege before attachment. Do not keep retrying attachment under mixed elevation. |
| A combo looks highlighted in ETABS but the API says it is inactive | Visible list focus or display-table selection is not proof of `Results.Setup` output state; live selection is transient | Treat `GetComboSelectedForOutput(exact_name)` as authoritative. Read it once after identity preflight. If false, stop before `FrameForce`; do not loop, guess, or reinterpret the UI. |
| An agent tries to activate a result inside the read-only acceptance | The result-selection prerequisite and the getter-only acceptance boundary were conflated | A setter requires separate explicit owner authority naming the exact combo and action. If authorized, call only `SetComboSelectedForOutput(exact_name, true)`, check return zero and before/after getter state, then prove model hash/size/mtime, lock, and units unchanged. The acceptance path itself still calls no selection setter. |
| The model path is empty, relative, or names only a directory | `GetModelFilepath()` returned the containing folder on the installed version | Use `GetModelFilename(True)` and require an exact saved approved `.edb` copy. Bind path, SHA-256, size, UTC mtime, lock, ETABS version, and runtime identity before result reads. |
| Story arrays appear one row longer than `NumberStories` | CSI's contract excludes `Base` from the count but includes it as the first item in every returned array | Require `NumberStories + 1` aligned entries, retain `Base` as an explicit excluded disposition, and create stable story identities only from the remaining rows. Any other shape fails closed. |
| Fake COM passes while installed COM decodes differently | Generated `comtypes` methods return list/tuple/SAFEARRAY combinations and place the CSI return code according to the typelib signature | Use the frozen getter matrix, accept only the proved tuple/list variants, validate every array length, and check every CSI return code. Never infer output order from memory or silently discard a trailing scalar. |
| Forces are read from stale or unintended results | Analysis completeness and exact selected case/combination were not proved before `FrameForce` | Require the approved exact case/combination, completed analysis status for its constituent cases, supported topology, and explicit `ItemTypeElm=0`. Any mismatch stops before the first force call; W2 never runs analysis or design. |
| ETABS remains in temporary units after an exception | Unit restoration was treated as a success-only step | Capture the original enum, set only the frozen read units when necessary, restore in `finally`, check every setter return, and re-get the original enum after both success and failure. Preserve the model lock throughout. |
| Direct and REST counts match but canonical hashes differ | Volatile file-observation wall-clock instants were included in cross-transport identity | Retain both `observed_at_utc` values in full provenance but exclude only those two instants from the hash basis. Continue hashing stable file identity, runtime, model/lock/units, topology, results, and dispositions. Diagnose structural diffs before changing any frozen digest. |
| `ETABS_W2_JSON` fails at `Range.values` although the server hash is valid | Arbitrary JSON chunks can begin with `+`, `-`, or `=`; Excel interprets those strings as formulas | Use typed `valuesAsJson` string cells, never formula-coercing `Range.values`, and verify exact rejoined bytes/SHA-256 after readback. Regressions cover all three prefixes without changing canonical JSON. |
| Six W2 tables remain after the seventh table fails | Collision preflight prevents overwrites but does not make a multi-sheet write atomic | Snapshot every touched controlled range. On failure, delete newly created controlled sheets and restore every pre-existing controlled table's exact cells/dimensions; verify rollback before reporting the error. Installed retry and regressions now prove this behavior. |
| Exact readback reports `""` versus blank or a small numeric tail difference | Typed empty strings become blank cells, while desktop Excel stores standard numeric cells at 15 significant digits | Normalize structured-table blanks and numbers to Excel's storage semantics before comparison. Keep the server-canonical JSON full precision and require its byte/hash-exact reconstruction separately. |
| A restarted laptop still appears to have the prior installed state | Open model, COM object, add-in server, workbook, and result selection are session state, not file state | Treat every restart as a fresh installed preflight. Reprove repository/source/process identity, reopen only the approved copied model/workbook, and getter-check lock/units/analysis/selection before any force read. |
| The installed run is repeated immediately after a blocker | Failure evidence was treated as an invitation to probe or repair live state | Stop at the earliest safe boundary, close task-owned servers, preserve before/after hashes and the exact symptom, and continue only under a new reviewed packet. Do not rerun forces merely to confirm a failure. |
| A green software path is described as structural approval | Software reconciliation and professional engineering review were conflated | Report only installed/software acceptance. Preserve `HELD_NOT_SUPPORTED` for independent frame analysis and require qualified structural-engineer review for design or construction use. |

Use this fixed order for the next installed packet:

1. Prove Git/worktree/GitHub authority and a clean source-bound runtime.
2. Prove 64-bit ETABS/Python/comtypes/type-library identities without touching
   the model.
3. Require the approved copied model already open; snapshot file, lock, units,
   analysis, and exact result-selection getter state.
4. Stop before forces if any identity or state differs. A selection change is
   a separate owner-authorized prerequisite, never an implicit repair.
5. Run direct service once, then source-bound REST once, and require exact
   canonical byte/hash/count equality.
6. Start installed Excel only from the reviewed typed-literal/transactional
   implementation and require rollback proof for any failed attempt.
7. Reconcile all seven tables, then prove model/workbook preservation, restored
   units, locked state, and unchanged result selection.
8. On any failure, freeze evidence and stop; do not loop. Keep proprietary
   paths, model/workbook bytes, inventories, and forces outside Git.

Repository-wide Windows runs can also report unrelated shell-execution,
backslash-normalization, symlink-privilege, local timing-budget, session-store,
or frozen-workbook-manifest failures. Record their exact tests separately;
never use them to overwrite a green focused W2 result or to broaden an installed
ETABS packet into general Windows maintenance.

## COM and unit behavior

The optional dependency is `comtypes>=1.4,<2` and is installed only by the
`etabs` package extra on Windows. The service creates and tears down COM inside
the FastAPI worker thread that owns the request.

After attaching to the running ETABS object, the service identifies the exact
open model with `SapModel.GetModelFilename(True)`. The explicit `True` requests
the filename with its full path; the bridge rejects an empty value, a directory,
a relative filename, or a path that is not a saved `.edb` model. It does not use
`GetModelFilepath()`, which ETABS 23.3.1 returned as the containing directory in
the installed Windows pilot. See CSI's API documentation for
[GetModelFilename](https://docs.csiamerica.com/help-files/etabs-api-2016/html/375b5267-61cc-04c2-d39c-34940d011f52.htm).

The pilot records the current ETABS present-unit enumeration, temporarily sets
`kN_mm_C` (CSI enumeration value 5), reads geometry and results, and restores
the original setting in a `finally` path. In the installed ETABS 23 typelib,
the nineteen `GetAllFrames` output parameters precede the optional `CSys`
input. The Python COM call therefore omits positional arguments and uses the
documented `Global` default; passing `"Global"` positionally binds it to the
first integer output and fails before inventory can be decoded. Exact result
names remain caller-owned identities and may include parentheses, as in common
factored-combination labels. CSI's API documentation identifies
`SetPresentUnits`, `GetAllFrames`, `GetRectangle`, result-selection setup, and
`FrameForce` as the relevant calls. See the official CSI API pages for
[units](https://docs.csiamerica.com/help-files/etabs-api-2016/html/cff40d28-9b1a-7f00-cfb9-0386da2464cc.htm),
[frame inventory](https://docs.csiamerica.com/help-files/etabs-api-2016/html/9346cf4e-be74-b7be-d1eb-afe69d0f609c.htm), and
[frame forces](https://docs.csiamerica.com/help-files/etabs-api-2016/html/87689f3e-4175-1627-618b-c4ebae5e89b5.htm).

### ETABS 23.3.1 static W2 signature proof

The Windows Phase A audit binds the merged W2A matrix to the exact installed
x64 type library without creating a COM object or calling a live model. The
tracked evidence is
[`etabs-excel-beam-w2c-com-signature-audit-evidence.json`](../verification/etabs-excel-beam-w2c-com-signature-audit-evidence.json).
Its authority is ETABS `23.3.1.4563`, `ETABSv1.tlb` LIBID
`{542F7A9D-3A7D-4061-97B3-3A1276FF83BD}` version `1.0`, SHA-256
`3823416b...24ef0e`, 64-bit Python `3.11.15`, and `comtypes 1.4.16`.

All 18 W2A getters and the sole `SetPresentUnits` call are statically
`PROVED` for exact exposed method, interface, parameter order/direction,
optional/default inputs, output order/count, CSI return-code position, and the
installed Python shape. Multi-output ETABS methods use `[in,out]` parameters;
the inspected `comtypes` implementation therefore returns an outer list and,
by default, one-dimensional SAFEARRAY values as tuples. A lone `[out,retval]`
is returned as a direct scalar. W2A deliberately accepts both tuple/list
containers, validates every trailing CSI return code and inner array length,
and is compatible with the installed provider.

Two exact-call details should remain visible during W2B/W2C:

- `LoadCases.GetNameList` also exposes optional `CaseType=0` after its two
  `[in,out]` parameters. Omitting arguments, as W2A does, requests the complete
  inventory.
- `Results.FrameForce` has a required `ItemTypeElm` input. W2A explicitly
  supplies enum 0 (`ObjectElm`); zero is not a typelib default.

Static metadata cannot prove model values, live return-code values, result
freshness, lock/unit restoration, topology, dispositions, force rows, or
canonical extraction hashes. The evidence therefore includes exact W2C proof
points and abort criteria for each of those claims. ETABS design-summary reads
remain blocked because no design getter is frozen, and independent frame
analysis remains `HELD_NOT_SUPPORTED`.

CSI's [official `Story.GetStories` contract](https://docs.csiamerica.com/help-files/etabs-api-2016/html/3f804fa8-9fef-a9f0-8517-87676c0ea8ef.htm)
has one important count convention: the reported `NumberStories` excludes
`Base`, while each returned array contains a leading Base row and has
`NumberStories + 1` entries. W2 retains that non-story row as an explicit
exclusion and builds stable story identities only from the following rows. Any
different count or leading sentinel fails closed.

## W2 complete-baseline surface

The maintained Office.js pane now keeps the W1 design pilot and adds a separate
W2 read-only baseline journey. First call
`POST /api/v1/etabs-bridge/v1/beam-baseline/preflight`; compare the returned
path/hash/size/time, ETABS/runtime/getter identities, locked state, and present
unit enum with the approved copied-model evidence. Confirm that identity only
when it is exact, then send the returned identities plus one exact already-
selected case or combination to
`POST /api/v1/etabs-bridge/v1/beam-baseline`.

The W2 call is serialized with every other maintained ETABS COM operation,
runs inside one worker-thread COM apartment, and supplies the real read-only
file observer required by W2A. It refuses runtime/getter/version/path/hash/size/
timestamp/unit/lock drift before extraction, resolves topology and selection
blockers before any `FrameForce` call, and re-gets the lock and original unit
enum after W2A has restored units. It never calls a result-selection setter.

Accepted output is written only after the server-canonical W2A hash-basis JSON
is independently hashed in the pane. Seven `ETABS_W2_*` sheets retain summary,
stories, frames, endpoint links, every station, every disposition, and 15,000-
code-point JSON chunks. Rejoining the chunk column must reproduce the exact
server string and `baseline_sha256`. All seven sheet/table/header identities are
preflighted before the first cell change; collisions, duplicate stable row IDs,
count drift, more than 100,000 projected rows, or a blocked service result write
nothing. A zero-row inventory is represented by a header-only controlled table.

Installed W2C exposed and then closed one Excel-specific exception to this
contract. Arbitrary 15,000-character boundaries can leave a JSON chunk starting
with `+`, `-`, or `=`; formula-coercing writes failed after six tables. The
maintained path now uses typed literal cells, verifies every structured cell,
rejoins and hashes the JSON, and treats all seven writes as one transaction.
New-sheet failures remove all new output; existing-sheet failures restore the
previous controlled contents and dimensions exactly. Blank cells and desktop
Excel's 15-significant-digit numeric storage are normalized only for structured
tables; the canonical JSON remains full precision and byte-exact.

This is software evidence, not ETABS design or professional approval. It does
not infer materials, reinforcement, slabs, supports, or engineering intent;
does not run analysis/design; and retains `HELD_NOT_SUPPORTED` for independent
frame analysis.

## W3 read-only catalogue and demand surface

After an exact copied-model preflight, the Windows-only
`POST /api/v1/etabs-bridge/v1/result-catalogue` operation reads one complete
load-pattern, load-case, response-combination, ordered-factor, case-status, and
current output-selection catalogue. Its request freezes the saved file digest,
ETABS/runtime/getter identities, present units, lock requirement, and exact
already-selected result identity. The response includes before/after file and
live-state brackets plus the canonical catalogue hash basis. Any incomplete
provider result or any state/file drift fails closed without a partial
catalogue.

`POST /api/v1/etabs-bridge/v1/beam-demand` then derives the accepted W3 demand
snapshot only from retained W2 baseline and W3 catalogue evidence. It performs
no COM operation. Same-row signed actions remain distinct from signed extrema
and independent-absolute screening references. Neither endpoint selects
output, calls `FrameForce`, runs ETABS analysis/design, unlocks/saves a model,
writes Excel, supplies an independent solver, or creates professional approval.

## Fail-closed boundaries

The current pilot blocks when:

- the host is not Windows or the optional COM dependency is missing;
- no already-open ETABS model can be attached or the copied model is unsaved;
- the exact case/combination cannot be selected or has no frame-force results;
- no horizontal frame candidates exist within the fixed 1 mm vertical
  tolerance;
- one of the selected first beams is not rectangular;
- a returned COM tuple or result-array count differs from the declared CSI API
  shape;
- any beam returns more than 2,000 result rows; or
- canonical beam intake rejects the section, materials, actions, or detailing
  basis.

The pilot does **not** run ETABS analysis, unlock/save the model, change member
sizes, perform a second frame analysis, optimize sections, check slabs/columns/
joints/foundations, evaluate serviceability, coordinate bars across adjacent
beams, check congestion/layers/site sequence, or claim professional approval.
All returned designs require qualified structural-engineer review.

For the later W2C read-only baseline acceptance, abort even earlier when the
approved source head/tree, x64 typelib hash, ETABS/comtypes versions, copied
model allowlist/hash/time/lock, result selection/status, or unit-restoration
capability differs from its preflight. During the approved run, abort on any
method/shape/count/return-code drift, incomplete connected topology, empty
requested beam/result selection, changed post-read file identity, unlocked
state, un-restored units, or need for a setter beyond `SetPresentUnits`.
Detailed result/model/workbook payloads remain external; Git receives only
safe hashes, counts, verdicts, and limitations.

## Installed Windows evidence and next gate

`ETABS-EXCEL-PILOT-W1` completed the bounded installed-software acceptance on
Windows 11 with 64-bit Excel, ETABS 23.3.1, Python 3.11.15, and `comtypes`
1.4.16. The exact copied, locked, already-analyzed model passed `/status`,
`/connect`, a mandatory one-beam request, and the conditional five-beam request.
The installed Office.js pane created then updated only
`ETABS_Pilot / tbl_ETABS_Pilot_V1`. Every projected field and canonical JSON
row reconciled to the corresponding direct API response, every retained force
station used the selected combination, the original units were restored, and
the copied model hash, size, and timestamp remained unchanged. The safe tracked
receipt is
[`etabs-excel-python-pilot-w1-evidence.json`](../verification/etabs-excel-python-pilot-w1-evidence.json);
proprietary model paths, workbook contents, and force payloads remain outside
Git.

This proves the bounded software path only. A qualified structural engineer
must still review the ETABS actions and canonical design before engineering use.
Any next phase that proposes a section change, writes to ETABS, reruns analysis,
checks global response, or optimizes members requires a separate reviewed scope
and explicit write-back controls.

The accepted next sequence is recorded in the
[Excel + ETABS beam next-phase plan](../planning/excel-etabs-beam-next-phase-plan.md).
W2A is merged, the static installed signature audit and W2B transport are
complete, and the Windows W2C path was exercised only through its safe blocker.
The exact approved combination was present but inactive, so direct service,
source-bound REST, and installed Excel all returned
`RESULT_SELECTION_NOT_ACTIVE` before `FrameForce`; Excel wrote no W2 table and
the model/workbook identities, lock, and units remained unchanged. The tracked
safe receipt is
[`etabs-excel-beam-w2c-installed-acceptance-evidence.json`](../verification/etabs-excel-beam-w2c-installed-acceptance-evidence.json).
This does not pass installed W2 baseline acceptance. A retry requires separate
authorization and an ETABS session where the exact approved combination is
already active before Codex attaches, followed by the complete preflight again.
Design/detailing expansion, construction-practice checks, offline optimization,
and copied-model write-back/reanalysis remain separate later gates.

PR #897 subsequently integrated the reviewed cumulative W2 campaign unchanged
as `ee50aaa3...`. In the separately authorized installed retry, the owner
confirmed the approved copy open and exact combination active before attachment,
but the authoritative read-only getter still returned the combination inactive
with zero selected combinations. The workflow stopped before constructing a
run request: zero `FrameForce` calls and force stations, no REST or Excel start,
no unit/result-selection setter, and no analysis, design, save, or mutation.
The model and copied-workbook file identities remained unchanged. The safe
retry receipt is
[`etabs-excel-beam-w2c-installed-retry-evidence.json`](../verification/etabs-excel-beam-w2c-installed-retry-evidence.json).
The confirmation/getter mismatch root cause is unconfirmed; do not retry under
the same authorization or attempt to repair selection through the API. W2C
remains `BLOCKED_SAFE_NO_FORCE_READ`, and independent frame analysis remains
`HELD_NOT_SUPPORTED`.

A later owner-authorized prerequisite set the exact combination active with the
single `SetComboSelectedForOutput(..., true)` call and return code zero; model
hash/size/mtime, lock, and units were unchanged, and no force, analysis, design,
or save occurred in that prerequisite. The continuation then completed direct
and source-bound REST extraction against the same identity. Both paths returned
`ACCEPTED`, baseline SHA-256 `d4c28586...`, 6 stories, 225 frames, 549 links,
153 result sets, 3,502 force stations, 4,348 dispositions, and exact canonical
byte equality with units restored.

The first direct/REST comparison had differed only at the two wall-clock
`observed_at_utc` file-observation instants. The bounded repair keeps both
instants in full provenance but excludes only those volatile values from the
cross-transport hash identity; file hash/size/mtime/path, model/lock/units,
runtime, topology, results, and dispositions remain hashed. A regression proves
two different observation times retain equal canonical hashes.

That partial artifact remains immutable blocked evidence in
[`etabs-excel-beam-w2c-installed-acceptance-retry2-evidence.json`](../verification/etabs-excel-beam-w2c-installed-acceptance-retry2-evidence.json).
The later transactional retry used the same copied model and exact combination.
Direct service and REST returned the same canonical 3,626,096 bytes and
`d4c28586...` digest; installed Excel saved all seven tables, including 242
literal JSON chunks. Independent read-only workbook inspection matched every
cell to the normalized direct projection and reconstructed the exact canonical
bytes/hash. Final getter-only postflight preserved model SHA-256/size/mtime,
locked state, units enum `6`, and active combination. The durable receipt is
[`etabs-excel-beam-w2c-installed-acceptance-transactional-evidence.json`](../verification/etabs-excel-beam-w2c-installed-acceptance-transactional-evidence.json).
This passes W2C installed software workflow acceptance on the bounded copied
model only; `HELD_NOT_SUPPORTED` and qualified-engineer review remain.
