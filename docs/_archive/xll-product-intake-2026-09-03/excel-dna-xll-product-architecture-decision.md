---
owner: Main Agent
status: active
last_updated: 2026-09-03
doc_type: spec
complexity: advanced
tags: [excel, excel-dna, xll, csharp, dotnet, etabs, solver, deployment]
---

# Excel-DNA XLL Product Architecture Research Decision

## Purpose and authority

This document records the researched product and technical decision for a
focused commercial Excel product that exposes a custom Ribbon tab, performs
structural calculations, connects to ETABS, and can later include a bounded
solver and optimizer.

The recommended direction is a Windows-first C#/.NET Excel-DNA `.xll`. The XLL
is the add-in container; the Ribbon tab is the primary interface that the user
sees. A separate StructAutomate host, web server, Python installation, or
installer is not part of the proposed first product baseline.

This is a research decision, not implementation or release authority. It does
not:

- assert that an XLL has been built or accepted on Windows;
- supersede the maintained Office.js -> FastAPI/Python Excel workbench;
- authorize ETABS attachment, model reads/writes, analysis, design, save, or
  installed-Excel activity;
- authorize migration of the complete Python library;
- upgrade software output into independent validation, qualified engineering
  review, professional approval, or project certification; or
- authorize a package, tag, public release, or commercial distribution.

Implementation remains held until a separately approved Windows proof of
concept passes the acceptance matrix in this document.

## Decision summary

| Question | Decision |
|---|---|
| Can the customer see a native Excel tab instead of a separate application? | Yes. A packed Excel-DNA XLL creates the custom Ribbon tab. The tab is UI supplied by the add-in, not an alternative to an add-in. |
| Primary product language | C# for UI callbacks, calculations, ETABS integration, solver, optimizer, evidence, and licensing. Ribbon XML defines the tab layout. |
| First runtime candidate | Excel-DNA 1.9.0 stable with `net48`, validated against the installed ETABS API. Build a parallel `net8.0-windows` POC only to resolve vendor/runtime compatibility. |
| Initial Office scope | Microsoft desktop Excel x64 on Windows. Do not promise Mac, web Excel, or 32-bit Office. |
| Distribution goal | One signed packed x64 `.xll`, manually loaded as an Excel add-in, with no separately running product host. |
| Zero-prerequisite claim | Not yet proven. Excel, ETABS, Trust Center permission, architecture compatibility, and possibly a .NET Desktop Runtime remain external conditions. |
| Calculation ownership | A focused independently qualified C# kernel. Python remains version-bound differential evidence during migration, not the normal customer runtime. |
| ETABS role | ETABS remains the global-analysis authority and a separate installed process. The XLL is an external API client. |
| Initial local solver | A managed, bounded 2D linear-elastic stiffness/checking kernel only. It is not a replacement for ETABS or a general building solver. |
| Initial optimizer | Deterministic enumeration and ranking over an explicit candidate domain. Defer OR-Tools until measured scaling requires it. |
| Maximum XLL size | No useful official Excel-DNA maximum was found. Adopt an internal operability budget instead of relying on a theoretical executable limit. |
| Implementation status | Held pending the Windows proof of concept and an approved migration scope. |

## Terminology: four different deployment claims

These statements must not be treated as synonyms:

| Claim | Meaning | Proposed status |
|---|---|---|
| Single product process | All StructAutomate product code runs inside Excel rather than in a companion service | Proposed for the first product |
| Single distribution file | The selected architecture's application code and dependencies are packed into one XLL | Supported in principle; must be proved for the actual dependency graph |
| No installer | The user can load the XLL through Excel without an MSI or administrator registration | Supported in principle; customer Trust Center policy still applies |
| No prerequisites | Nothing except the downloaded XLL is required | False: Windows desktop Excel is required, ETABS is required for ETABS features, and runtime/trust conditions still apply |

If both 32-bit and 64-bit Office are supported, Excel-DNA normally emits
architecture-specific XLLs. That is two product binaries, not one universal
XLL. The first product should therefore be x64-only unless customer evidence
shows that 32-bit Office is commercially necessary.

## Proposed architecture

```text
Microsoft Excel x64
└── StructuralAutomate.xll
    ├── Ribbon XML and C# callbacks
    ├── optional WinForms custom task pane
    ├── pure worksheet UDFs
    ├── command/session coordinator
    ├── ETABS API adapter
    ├── focused C# engineering kernel
    ├── bounded managed 2D solver
    ├── deterministic candidate evaluator/optimizer
    ├── workbook projections, BBS, quantities and reports
    └── diagnostics, evidence, licensing and update metadata

ETABS.exe
└── global model, analysis/design and authoritative result source
```

"Single-process product" means that no additional StructAutomate host or
service is running. ETABS remains its own external application process.

### Internal layer boundaries

```text
Domain contracts and explicit units
                ↓
Focused C# engineering kernel and bounded solver
                ↓
Application orchestration and evidence/passport logic
                ↓
Excel Ribbon/UDF/task-pane adapters and ETABS API adapter
```

The C# design should preserve the repository's existing direction: pure
engineering logic does not import Excel or ETABS types; ETABS and Excel code
translate at the boundary; units remain explicit in names and contracts; and
result provenance remains available to the reviewer.

## Language and UI map

| Surface | Language/technology | Responsibility |
|---|---|---|
| Excel Ribbon tab | Ribbon XML | Tabs, groups, buttons, labels, images, visibility and callback names |
| Ribbon callbacks and commands | C# | User-invoked operations, validation, progress, errors and orchestration |
| Worksheet functions | C# through Excel-DNA | Pure deterministic calculations returning scalar or array results |
| Task pane/dialogs | WinForms first; WPF only if justified | Larger input forms, progress, connection selection and result review |
| Engineering functions | Pure C# | IS-code math, section properties, design/check logic and detailing rules |
| ETABS connection | C# with installed CSI API assemblies | Attach/start, identity, state checks, bounded reads and separately authorized writes |
| Solver/optimizer | Pure C#; optionally Math.NET | Bounded matrices, transparent enumeration and ranking |
| Workbook projection | C# with Excel-DNA/Excel COM on the Excel thread | Tables, schedules, formatting and evidence sheets |
| PDF | Excel's built-in fixed-format export | Export the controlled report workbook without adding a PDF engine |
| Migration verification | Python test vectors and differential runner | Compare the new C# kernel to frozen, version-bound reference results |

New Python packages, a local web server, Node, Office.js, or an embedded browser
are not needed for the proposed baseline. They remain valid technologies for
the existing workbench and are not removed by this decision.

## Proposed Ribbon product surface

The first tab should remain small and task-oriented. Later component buttons
appear only when their C# calculation and evidence scope is accepted.

| Ribbon group | Candidate buttons | Phase/boundary |
|---|---|---|
| Start | About, Diagnostics, Workbook Setup | POC baseline |
| ETABS | Select Instance, Connect, Model Identity, Read Results, Disconnect | Read-only POC before any model mutation |
| Beam | Design, Check Provided Reinforcement, Detail | First focused engineering product slice |
| Other members | Column, Slab, Footing | Later separately qualified ports; not implied by the beam POC |
| Solver | Run 2D Check, Compare with ETABS | Bounded independent check only |
| Optimize | Generate Candidates, Rank, Compare Shortlist | Explicit finite domain and transparent rejection reasons |
| Deliver | BBS, Quantities, Cost Summary, Report, Export PDF | Controlled workbook projections |
| Evidence | Input/Result Passport, Stale Status, API Ledger | Claim and replay support |

Repeated commands should reuse an explicit in-memory session while it remains
valid. Durable evidence must bind the workbook, model, API/runtime, units,
selection scope, result epoch, normalized inputs, calculation version, and
output. Cached state must fail closed when those identities change.

## Excel execution and threading rules

### Worksheet UDFs

Use UDFs only for pure calculations. A function may be registered as
thread-safe only when it:

- has no Excel COM, ETABS API, file, UI, mutable-global, or native
  thread-unsafe behavior;
- consumes copied scalar/array inputs rather than live `Range` objects;
- returns a deterministic value for the same inputs; and
- cannot save a workbook, start analysis, change a model, or write another
  cell.

Excel recalculation, `F9`, workbook opening, or formula copying must never
attach to ETABS or produce external side effects.

### Commands

ETABS activity, workbook writes, reports, and substantial solves belong behind
explicit Ribbon commands. The initial POC should serialize ETABS API objects
and calls on the Excel command/main thread. Pure compute may run on a worker,
but all Excel interaction must be queued back to Excel's main thread.

A dedicated internal STA executor remains a possible later one-process
optimization, but only after its object lifetime, message pumping, error
recovery, cancellation, and Excel handoff are proved. It must not be introduced
only to hide a long blocking ETABS call.

## ETABS integration rules

1. Prefer process-ID selection where the installed ETABS API supports it.
   Never silently attach to an arbitrary instance when several are running.
2. Record the exact ETABS version, API assembly/version, process ID, model path
   and hash, model lock state, units, selected cases/combinations, and API
   return codes.
3. Start with read-only model/result acquisition. Every write, analysis,
   design, save, unlock, or selection setter requires a separately authorized
   transaction.
4. Treat every nonzero CSI return code and unsupported interface as a typed
   failure. Do not continue with partial or stale results.
5. Do not assume CSI's in-process plugin assembly-loading instructions apply
   unchanged to an external Excel XLL. The POC must test installed assembly
   discovery and must not redistributea `CSiAPIv1.dll` or `ETABSv1.dll` without
   a verified technical and licensing basis.
6. ETABS remains the final global-analysis authority. A local member solver
   may screen or independently replay a bounded model but cannot claim full 3D
   parity from a few matching reactions or force values.

## C# migration boundary

Do not translate the entire Python repository file-by-file. Migrate one
commercial journey vertically:

```text
typed Excel input
  -> focused C# calculation
  -> detailing/candidate evaluation
  -> controlled worksheet result
  -> evidence/passport
```

For each migrated function:

1. freeze its supported cases, units, source/table provenance, rounding and
   failure behavior;
2. create language-neutral input/output vectors;
3. implement the focused pure C# function;
4. compare C# and the exact pinned Python reference over normal, boundary and
   unsafe cases;
5. independently review the formula and test vectors rather than treating
   Python agreement as engineering validation; and
6. expose it to Excel only after the kernel contract passes.

Python remains useful as version-bound differential evidence and as the source
of already accepted contracts. It is not installed for customers and does not
become an invisible normal-path fallback.

## Solver and optimizer decision

### First solver

Implement or port only a managed 2D linear-elastic kernel for the approved
problem class:

- explicit nodes, degrees of freedom and restraints;
- approved axial/beam/frame elements;
- explicit loads and combinations;
- stiffness assembly and boundary conditions;
- displacement, reaction and member-end-force recovery; and
- a singular/unstable-system diagnostic that fails closed with the implicated
  degrees of freedom.

This is an independent replay/checking capability and remains
`SURROGATE_ONLY` unless a later model-specific evidence programme establishes
a narrower accepted comparison claim. Full 3D frames, diaphragms, slabs,
meshes, nonlinear behavior, staged construction, dynamics and soil/structure
interaction remain outside the initial XLL solver.

Math.NET Numerics is the preferred optional matrix dependency if the focused
kernel benefits from it. Start with its managed provider. Do not add MKL or
OpenBLAS to the baseline package without a measured performance need and a
fresh native-deployment audit.

### First optimizer

Use deterministic enumeration or bounded branch-and-bound over declared:

- available bar diameters, counts and layer arrangements;
- section families and material grades;
- strength, serviceability and detailing checks;
- objective terms and tie-breaking order; and
- search limits, traversal, pruning and candidate counts.

Every rejected candidate must retain a reason; every selected candidate must
retain its governing checks and objective breakdown. A truncated search cannot
claim a global optimum.

Defer OR-Tools until actual candidate coupling or scale proves that the direct
approach is insufficient. OR-Tools adds native C++ runtime assets, package
size, bitness/loading risk and additional license-notice obligations.

## Runtime and packaging decision

| Option | Advantages | Costs/risks | Decision |
|---|---|---|---|
| Excel-DNA 1.9.0 + `net48` | Stable; Windows component; no separate .NET Desktop Runtime; AppDomain isolation; best fit for customer machines outside our control | Older runtime API surface; installed CSI API compatibility must be proved | Primary POC and preferred commercial baseline |
| Excel-DNA 1.9.0 + `net8.0-windows` | Modern runtime/C# APIs; aligns with CSI's current .NET 8 plugin example | Matching Desktop Runtime required; only one modern .NET runtime can load in Excel; weaker add-in isolation | Parallel compatibility POC and fallback, not the no-prerequisite baseline |
| Excel-DNA NativeAOT | Can produce an XLL that does not need an installed .NET runtime | Current Excel-DNA NativeAOT package is preview; AOT/reflection limits; different size and debugging profile | Defer until stable and independently spiked |
| External C# host | Crash isolation, durable jobs, independent lifecycle and responsive Excel | Additional executable, IPC, installation/update/security surface | Not baseline; use only if escalation triggers are met |

Excel-DNA's current SDK-style build properties support packed managed and
native dependencies and compressed resources. Older archived guidance saying
mixed/native assemblies cannot be packed is not the current authority. Actual
native solver or licensing dependencies still require a clean-Windows load
test; a documented packing switch does not prove runtime reliability.

### Signing, trust and updates

- Sign and timestamp the final packed XLL, not only an intermediate assembly.
- Publish the version, SHA-256, release notes and third-party notices.
- Document Excel's Add-ins and Trust Center steps. Do not promise that signing
  overrides an organization's Office policy.
- Use a secure product folder with per-user write/update ownership. Do not
  teach customers to trust a broad or unsafe directory.
- The baseline update flow is close Excel, verify the new signed/hash-bound
  artifact, replace it atomically, and retain the prior version for rollback.
- Automatic startup, update while loaded, Mark-of-the-Web behavior, endpoint
  protection and enterprise Trusted Location policy remain Windows-spike rows.

## Size evidence and budget

No current Excel-DNA or Microsoft source was found that defines a practical
maximum packed XLL size. A theoretical Windows executable-image limit is not a
usable product budget. Startup, extraction/loading, antivirus scanning,
working-set growth, bitness and supportability are the relevant constraints.

Current repository measurements from `origin/main` on 2026-09-03 are source
inventory, not compiled-XLL measurements:

| Surface | Measured size/count | Packaging interpretation |
|---|---:|---|
| `Python/structural_lib` | 4,059,820 bytes; 110,991 Python lines; 528 files | Entire maintained Python source surface; not the proposed C# port scope |
| `Python/tests` | 3,858,274 bytes; 301 files | Development evidence; not shipped in the product XLL |
| `excel_addin` | 725,992 bytes; 19 files | Existing Office.js surface; remains separate and is not embedded in the proposed baseline |
| Tracked C#/.NET/XLL project files | None | Confirms this is research, not an implemented XLL |

Source byte count does not predict compiled size. Use these initial product
budgets until a Windows build supplies measured evidence:

| Packed x64 XLL | Decision |
|---:|---|
| <= 10 MB | Preferred commercial target |
| > 10 MB to 25 MB | Accept only with measured cold-load, memory, scanning and update evidence |
| > 25 MB | Dependency and architecture review required |
| > 50 MB | Reconsider optional/native modules or an external component |

Planning estimates only:

- Ribbon, focused C# kernel and ETABS adapter: approximately 3-8 MB;
- managed Math.NET plus richer reporting: approximately 5-15 MB total; and
- OR-Tools or other native stacks: potentially 25 MB or more.

NuGet download sizes are compressed package sizes, not final packed-XLL sizes.
The current ExcelDna.AddIn 1.9.0 package is 2.86 MB, MathNet.Numerics 5.0.0 is
3.98 MB, and the current OR-Tools Windows x64 runtime package is about 20 MB.
Only an actual Release build can establish the product size.

## What efficient coding can and cannot solve

| Can be controlled by architecture/coding | Cannot be eliminated by code alone |
|---|---|
| Fast pure UDFs and batch range writes | Customer Trust Center or enterprise policy |
| Explicit ETABS session and model identity | Missing ETABS licence or incompatible installation |
| Deterministic caching and stale-state invalidation | 32/64-bit binary incompatibility |
| Bounded memory and transient result batches | Excel crash blast radius for in-process defects |
| Transparent solver and optimizer outputs | Long blocking vendor calls that do not expose safe cancellation |
| Safe error boundaries and typed return-code checks | Vendor API/version changes and endpoint-protection behavior |
| Signed, hash-bound update packages | Replacing a loaded XLL without a controlled close/update flow |

Good coding makes the focused product viable; it does not justify promising
that every customer machine will load one file with zero setup or that Excel
can safely host every future long-running workflow.

## Host-escalation triggers

Keep the one-XLL architecture unless measured evidence shows one or more of the
following:

- ETABS calls must continue while Excel remains independently interactive;
- reliable cancellation, timeout containment, crash isolation, queued jobs,
  resumability or unattended parameter studies are required;
- native solver/ML/rendering dependencies cause unsafe loading, memory growth,
  version conflicts or an impractical XLL size;
- multiple ETABS instances or users require durable shared job state;
- workbook/ETABS recovery cannot be made deterministic after an interrupted
  operation; or
- licensing/secrets require a security boundary outside the Excel process.

Meeting a trigger starts a new architecture decision. It does not automatically
authorize or create a host.

## Windows proof-of-concept acceptance matrix

The POC must use a clean customer-like Windows machine without Visual Studio,
Python, Node, or repository tooling. Record exact Excel, Windows, ETABS, CSI API,
.NET, XLL and certificate identities.

| Area | Required proof | Failure consequence |
|---|---|---|
| Packaging | Signed packed x64 XLL loads with all permitted application dependencies | Hold single-file claim |
| Runtime | Compare `net48` and `net8.0-windows`; prove the selected runtime and co-resident add-ins | Select compatible target or hold no-runtime-install claim |
| Ribbon/UI | Tab, buttons, task pane/dialog and error recovery work after restart | Hold product UX |
| UDF safety | Pure UDFs repeat under normal/full/multithreaded recalculation and make no Excel/ETABS/file calls | Hold UDF export |
| Solver | Hand-audited axial, restrained beam/frame and singular cases pass with explicit units and diagnostics | Hold local solver |
| Optimizer | Fixed candidate domain gives deterministic counts, rejection reasons, ranking and governing constraints | Hold optimizer |
| ETABS attach | User selects exact PID or launches an owned instance; multiple instances never cause silent first-instance attachment | Hold live ETABS route |
| ETABS read | Model/result probe matches ETABS UI/export and retains all return codes, units and identities | Hold ETABS result claim |
| Recalculation isolation | Instrumented ledger proves `F9`, workbook open and async UDF execution never invoke ETABS | Hold add-in architecture |
| Long operations | Visible busy/progress state, defined cancel boundary and recoverable controlled API failure | Escalate responsiveness/isolation review |
| Workbook/report | BBS, quantity, evidence and PDF outputs reconcile with canonical C# results | Hold delivery surface |
| Lifecycle | Restart, unload/reload, disabled-add-in recovery, update-after-close and rollback pass | Hold portable commercial distribution |
| Security | Signed/local/downloaded paths and realistic Trust Center/enterprise policy cases are documented | Hold low-friction installation claim |
| Resource use | Record packed size, cold-load time, working set and repeated connect/read/design cycles without material leak | Review dependencies or host trigger |

The POC result must use one of these dispositions:

- `ACCEPTED_SINGLE_XLL_NET48`;
- `ACCEPTED_SINGLE_XLL_NET8_RUNTIME_REQUIRED`;
- `ACCEPTED_XLL_WITH_BOUNDED_EXTERNAL_COMPONENT`;
- `HELD_WINDOWS_OR_VENDOR_COMPATIBILITY`; or
- `REJECTED_SINGLE_XLL_FOR_MEASURED_REASON`.

## Dependency-ordered implementation route

No phase starts automatically from this research decision.

1. **P0 packaging/runtime spike:** build minimal stable Excel-DNA x64 XLLs for
   `net48` and `net8.0-windows`; prove Ribbon, UDF, task pane, signing, trust,
   lifecycle and CSI assembly binding.
2. **P1 focused C# kernel:** port one approved beam journey with language-neutral
   vectors, differential evidence and independent engineering review.
3. **P2 read-only ETABS:** implement exact process/model/unit/version checks and
   one bounded result acquisition without setters.
4. **P3 bounded solver and optimizer:** add the managed 2D replay and explicit
   candidate enumeration with transparent evidence.
5. **P4 workbook delivery:** add BBS, quantities, reports, PDF and replayable
   passports without duplicating calculation logic in worksheets.
6. **P5 controlled ETABS transaction:** only after separate authority, prove an
   owned-copy mutation/reanalysis/rollback flow. Never begin with the user's
   live baseline model.
7. **P6 commercial hardening:** signing, licence notices, entitlement, update,
   rollback, diagnostics, support matrix and release-specific owner approval.

## Source register

Primary sources were refreshed during the 2026-09-02/03 research pass.

| Topic | Primary source | Used for |
|---|---|---|
| Excel-DNA installation/packing/security | [Installing Your Add-in](https://excel-dna.net/docs/guides-basic/installing-your-add-in/) | Packed XLL, manual/permanent loading, no-admin baseline, signing and Trust Center |
| Runtime selection | [.NET runtime support](https://excel-dna.net/docs/guides-basic/dotnet-runtime-support/) | `net48` versus modern .NET, Desktop Runtime and one-modern-runtime constraint |
| Current packing properties | [SDK-style project properties](https://excel-dna.net/docs/guides-basic/sdk-style-project-properties/) | 32/64-bit output, compression, managed/native dependency packing and signing properties |
| Stable package/version/license | [ExcelDna.AddIn 1.9.0 on NuGet](https://www.nuget.org/packages/ExcelDna.Addin) | Stable version, supported target families, package size and commercial-use statement |
| NativeAOT | [.NET Native AOT support](https://excel-dna.net/docs/guides-basic/dotnet-native-aot-support/) | Runtime-free future option and current preview boundary |
| Ribbon | [Customizing Ribbons](https://excel-dna.net/docs/guides-basic/customizing-ribbons/) | Ribbon XML and C# callback mechanism |
| Async/main-thread handoff | [Performing asynchronous work](https://excel-dna.net/docs/guides-advanced/performing-asynchronous-work/) | Worker restrictions and queueing work back to Excel |
| Excel UDF threading | [Microsoft multithreaded recalculation](https://learn.microsoft.com/en-us/office/client-developer/excel/multithreaded-recalculation-in-excel) | Thread-safe XLL functions and prohibited command/COM behavior |
| Async UDF restrictions | [Microsoft asynchronous UDFs](https://learn.microsoft.com/en-us/office/client-developer/excel/asynchronous-user-defined-functions) | Deep-copy and callback limits |
| Excel/Office architecture | [32/64-bit Office compatibility](https://learn.microsoft.com/en-us/office/client-developer/shared/compatibility-between-the-32-bit-and-64-bit-versions-of-office) | Architecture-specific binary boundary |
| Excel limits | [Excel specifications and limits](https://support.microsoft.com/en-us/excel/excel-specifications-and-limits) | Workbook/function/memory limits; not an XLL file-size limit |
| ETABS spreadsheet/API use | [CSI Developer](https://www.csiamerica.com/developer) | C# support, smart spreadsheets, external applications and cross-product API |
| CSI .NET 8 reference handling | [CSI .NET 8 plugin example](https://web.wiki.csiamerica.com/wiki/spaces/kb/pages/2011456/NET%2B8%2BPlugin%2BExample%2B-%2BAll%2BProducts) | Installed API library/version checks and explicit plugin-only scope warning |
| Managed numerical library | [Math.NET Numerics](https://github.com/mathnet/mathnet-numerics) | Managed matrix option and MIT licence |
| Optional optimization library | [OR-Tools .NET installation](https://developers.google.com/optimization/install/dotnet/) and [Windows runtime package](https://www.nuget.org/packages/Google.OrTools.runtime.win-x64/) | Native wrapper/deployment surface and package-size planning evidence |

## Final recommendation

Proceed only with a narrow Windows POC for a stable Excel-DNA x64 XLL. Test
`net48` first because it best matches the no-extra-runtime commercial goal, and
test `net8.0-windows` beside it because actual CSI API binding is decisive.
Begin with one Ribbon, one task pane/dialog, pure beam UDFs, a read-only
PID-selected ETABS probe, and the managed bounded solver. Keep OR-Tools,
NativeAOT, full-library migration, model mutation and a companion host outside
the first packet.

If that POC passes, the simple product is technically and commercially
credible. If it fails, the recorded acceptance row—not preference—determines
whether to change runtime, split a native dependency, or add an isolated host.
