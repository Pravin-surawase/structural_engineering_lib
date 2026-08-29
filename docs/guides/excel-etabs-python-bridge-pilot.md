# Excel -> Python -> ETABS Beam Pilot V1

**Type:** Guide
**Audience:** Developers
**Status:** Complete
**Next Phase:** W2A Merged; Static W2C Audit Complete; W2B/W2C Campaign Authorized
**Created:** 2026-08-28
**Last Updated:** 2026-08-29
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
| Extract and design beams | `POST /api/v1/etabs-bridge/v1/beam-pilot` | Reads an exact result selection and writes nothing to ETABS |

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
W2A is merged and the static installed signature audit is complete. The
Windows campaign next freezes W2B's read-only observer/REST/Excel surface, then
runs W2C only after all preflight gates pass against that exact checkpoint.
Design/detailing expansion, construction-practice checks, offline optimization,
and copied-model write-back/reanalysis remain separate later gates.
