---
owner: Main Agent
status: active
last_updated: 2026-09-03
doc_type: guide
complexity: intermediate
tags: [excel-dna, xll, planning, research]
---

**Dated evidence summary.** Published from the 3 September research workspace. Local paths describe the original observations; they are not prerequisites for reading this copy or proof of the current checkout. Machine-only evidence remains outside this bundle.

**StructAutomate XLL P0 — readiness check**

Checked on 3 September 2026, Asia/Calcutta. Preparation is complete and the environment appears ready to attempt the P0 build. No XLL implementation, build, unit test, or installed Excel verification has been performed. This is a preflight record, not a P0 acceptance receipt.

The launch packet is preserved in `XLL-P0-TASK.txt`. The machine-readable preparation record is `XLL-P0-PREFLIGHT.json`.

| Check | Observed result |
| --- | --- |
| New project | `C:\CodexWork\StructAutomate.Xll` does not exist. Recheck immediately before creation. |
| Optimizer reference | `C:\CodexWork\StructAutomate.EtabsOptimizer`; owner `LAPTOP-360-PRAV\P`; branch `codex/p0-foundation-bootstrap`; commit `4e1f653f6224b8f1400de2129d8b0e8bde2d379a`; clean, with no reported untracked files. |
| Starter reference | `C:\Users\P\Pravin2025\Projects\structautomate_excel\excel_addin_etabs_nightly`; owner `LAPTOP-360-PRAV\P`; not a Git repository. Its three immediate source folders also have no `.git` marker, so branch, commit, and Git dirty state are unavailable. |
| Windows | Windows 11 Home Single Language, version `10.0.26200`, 64-bit. |
| Desktop Excel | Microsoft 365, x64, `16.0.20326.20112`; executable at `C:\Program Files\Microsoft Office\root\Office16\EXCEL.EXE`. No Excel process was running during inspection. |
| .NET Framework runtime | Registry version `4.8.09221`, release `533509`, installed. |
| net48 targeting | No system v4.8 targeting pack at the standard location. NuGet packages `Microsoft.NETFramework.ReferenceAssemblies` and `.net48` version `1.0.3` are cached. The net48 `mscorlib.dll` and `System.Windows.Forms.dll` reference files are present. |
| SDK and MSBuild | .NET SDK `10.0.400`; SDK MSBuild `18.9.6+14fbf8d52`; Windows Desktop SDK present. No Visual Studio installation was found at the checked standard locations. |
| Modern runtimes | x64 `Microsoft.NETCore.App` and `Microsoft.WindowsDesktop.App` `8.0.20` and `10.0.11`; `Microsoft.AspNetCore.App` `10.0.11`. |
| net8 comparison | Installed SDK and Desktop Runtime support attempting the optional build. Only `10.0.11` reference packs are installed under the checked dotnet pack folders; net8 build references may need NuGet restore. Actual compatibility remains to be proved by build and Excel loading. |
| Excel-DNA | `ExcelDna.AddIn` `1.9.0` is cached. NuGet's package index returned HTTP 200 and includes `1.9.0`. |
| Signing | No code-signing certificate found in CurrentUser/My or LocalMachine/My. `signtool` was not on PATH, and the checked Windows SDK bin folders were absent. Record `SIGNING_HELD_NO_CERT`. |
| Trust Center | The selected Excel and Common policy registry paths were absent; the user Excel Security key had no values. This does not establish effective Trust Center settings. UI inspection and actual load behavior remain unverified. No security settings were changed. |
| Architecture evidence | The supplied handoff cites `ffd6a4f1` on `codex/xll-product-architecture-docs`. That commit does not resolve in the local optimizer repository; its content and publication state were not independently verified. The pasted P0 packet remains the immediate scope authority. |

The missing system targeting pack is not an identified build blocker: Microsoft documents using NuGet reference assemblies for this case, and the required package files are already present. Build success is still unverified. See [Microsoft's reference-assemblies guidance](https://learn.microsoft.com/en-us/dotnet/framework/migration-guide/reference-assemblies). The requested version is listed on the [ExcelDna.AddIn 1.9.0 package page](https://www.nuget.org/packages/ExcelDna.AddIn/1.9.0).

The next execution should follow the preserved packet:

1. Refresh preservation and Git checks. Stop before writes if the proposed XLL path exists. Create the isolated repository on a `codex/` branch only after checks pass.
2. Build the SDK-style C# net48 baseline with Excel-DNA 1.9.0, x64 output only, a packed Release XLL, the three Ribbon commands, one WinForms diagnostic dialog or task pane, and the two deterministic UDFs. Use the installed SDK and build-only reference assemblies.
3. Add the requested pure-function and diagnostic-formatting tests. Attempt the separate net8.0-windows comparison using the already installed Desktop Runtime without replacing the net48 baseline.
4. Use a disposable workbook to prove loading, all Ribbon buttons, dialog/panel reuse, normal/full recalculation, restart, unload/reload, and disabled-add-in recovery. Determine effective trust requirements without weakening security. Record signing as held while no suitable certificate exists.
5. Produce the actual P0 receipt with artifact size/hash, exact repository commit, commands and exit codes, observed lifecycle outcomes, and one of the packet's allowed acceptance dispositions. Do not infer acceptance from this readiness check.

Preparation made zero application-code changes to the protected references, zero ETABS/CSI calls, and no changes to `structural_engineering_lib`. It did not create the XLL project, install software or certificates, change trust settings, launch Excel, or create a new Codex task. Only the three preparation files in the current workspace were added.
