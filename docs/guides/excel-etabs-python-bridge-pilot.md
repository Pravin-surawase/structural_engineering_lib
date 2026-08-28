# Excel -> Python -> ETABS Beam Pilot V1

**Type:** Guide
**Audience:** Developers
**Status:** In Progress
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

From repository root in PowerShell:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip install -e "Python[etabs]"
```

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
