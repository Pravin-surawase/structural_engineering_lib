# Lesson 0 - Open and check the real product in VS Code

**Type:** Guide
**Audience:** Engineers learning the real C# product
**Status:** Active
**Importance:** High
**Created:** 2026-09-07
**Last Updated:** 2026-09-07
**Related Tasks:** etabs-vscode-learning-intake
**Abstract:** Set up VS Code, verify the installed environment, build the actual CSharp solution and trace real XLL and ETABS source owners before memory-only acquisition.

---

## The outcome of this first exercise

You will open the actual product solution in VS Code, check its development
environment, build it, and find the real code that connects Excel to ETABS.
There is no new demo application or invented model in this lesson.
Allow 20-30 minutes; stop after the completion checkpoint.

The XLL shell and standalone Excel foundation have recorded acceptance. The
full ETABS-to-design product is incomplete. We can use the foundation while we
learn and improve data acquisition. The immediate objective is connection,
model state, required geometry/results and efficient reuse in memory. Design
and persistence decisions come later.

[Course entry](../README.md) · [C# product](../../../../../CSharp/README.md) ·
[Open the product workspace](../../../../../CSharp/StructAutomate.code-workspace)

## 1. Open the real solution in VS Code

On the checked Windows computer, the .NET SDK and ETABS are installed. VS Code
was not found on PATH, in its usual user/system installation folders, or in
the checked uninstall registrations. A portable/custom installation may exist.
Use it if you already have one; otherwise install Windows x64 VS Code from
the [official download page](https://code.visualstudio.com/download).

In VS Code, open Extensions with **Ctrl+Shift+X**. Install **C# Dev Kit** by
Microsoft, which adds solution support and uses the C# extension for language
services/debugging. See the [official C# setup guide](https://code.visualstudio.com/docs/csharp/get-started).

Choose **File > Open Workspace from File** and select:

```text
C:\CodexWork\structural_engineering_lib\CSharp\StructAutomate.code-workspace
```

If prompted for Workspace Trust, review this repository and trust this specific
workspace to enable its build tasks. It opens the entire repository and selects
`CSharp/StructAutomate.slnx`. Open this lesson in the Explorer and press
**Ctrl+Shift+V** to read its preview in VS Code.

We keep the existing project layout. No separate learning repository is needed.
The earlier invented-data lessons remain optional C# references, not the live
product exercises requested here.

## 2. Verify the environment yourself

Open **Terminal > New Terminal** and use PowerShell. Run:

```powershell
Set-Location C:\CodexWork\structural_engineering_lib\CSharp
dotnet --version
dotnet --list-runtimes
```

The assistant observed SDK **10.0.400**, .NET runtime **10.0.11** and Windows
Desktop Runtime **10.0.11**. Your terminal output is your own current evidence.

| Item | What it does | Where to check |
| --- | --- | --- |
| VS Code | Edits, navigates and debugs source | Help > About |
| C# Dev Kit / C# extension | Loads the solution and provides C# tooling | Extensions |
| .NET SDK | Compiles, restores and builds C# | `dotnet --version`; `CSharp/global.json` |
| .NET Desktop Runtime x64 | Runs the Windows Excel add-in | `dotnet --list-runtimes` |
| Excel x64 | Hosts the XLL | Excel: File > Account > About Excel |
| ETABS 23.3.1 x64 | Owns the real model and its analysis results | ETABS: Help > About ETABS; executable properties |
| `ETABSv1.dll` | Describes the installed ETABS API | Installed ETABS directory |

The product pins .NET SDK 10.0.400 with patch roll-forward and Excel-DNA 1.9.0.
Do not replace these with versions from an old tutorial. An SDK contains build
tools; a runtime alone does not compile the source. The installed ETABS
executable was observed as **23.3.1.4563**; its API DLL has a separate version.

Check the API files without connecting to ETABS:

```powershell
Test-Path -LiteralPath 'C:\Program Files\Computers and Structures\ETABS 23\ETABSv1.dll'
Test-Path -LiteralPath 'C:\Program Files\Computers and Structures\ETABS 23\NativeAPI\x64\ETABSv1.tlb'
Test-Path -LiteralPath 'C:\Program Files\Computers and Structures\ETABS 23\CSI API ETABS v1.chm'
Get-Process ETABS -ErrorAction SilentlyContinue | Select-Object Id, ProcessName
```

The file checks should return `True` on this machine. An empty process list
means ETABS is not running; it is not an API failure. A running process is not
proof of a loaded model or available results. We will make those separate
observations in the next exercises.

`-LiteralPath` treats the path exactly as written. `Select-Object` shows only
the named properties. These commands read system information and save no model
data. If `dotnet` is unavailable after installation, restart VS Code so its
terminal inherits the current PATH. SDK downloads are on Microsoft's
[.NET 10 page](https://dotnet.microsoft.com/en-us/download/dotnet/10.0).

## 3. Learn the folders by building the product

In the same terminal, run:

```powershell
dotnet restore StructAutomate.slnx --locked-mode
dotnet build StructAutomate.slnx -c Release --no-restore
```

`restore` uses the recorded dependency versions. `build` compiles the solution.
`Release` is a build configuration. `--no-restore` reuses the completed restore.
Neither command installs the new build into Excel or connects to ETABS.

Alternatively, **Ctrl+Shift+B** runs the workspace's product build task, which
first performs the locked restore. **Terminal > Run Task > Product: inspect
.NET environment** runs `dotnet --info` from the correct folder.

```text
structural_engineering_lib/
  CSharp/
    StructAutomate.code-workspace     VS Code entry point
    StructAutomate.slnx               Actual multi-project solution
    global.json                      SDK selection
    Directory.Build.props            Shared project settings
    Directory.Packages.props         Pinned dependency versions
    src/
      StructuralEngineering.ExcelDna/ Excel ribbon, functions and session
      StructuralEngineering.Etabs/    Actual ETABS attachment/read code
      StructuralEngineering.Contracts/Typed data shared between components
      StructuralEngineering.Analysis/ Offline normalization/topology code
    tools/StructAutomate.EtabsWorker/ Current separate ETABS reader executable
    tests/                           Existing automated checks
    packaging/excel/                 Package/install/acceptance tools
  docs/planning/xll-product/learning/ These lessons
```

A `.cs` file contains C# code. A `.csproj` groups code and references into one
project. A `.slnx` groups projects. A `.dll` or `.exe` is compiled output.
The `.xll` is Excel's add-in entry point. The connected product also uses a
worker executable. It is not just one C# source file renamed to `.xll`.

The packed Release build is expected at:

```text
CSharp/src/StructuralEngineering.ExcelDna/bin/Release/net10.0-windows/publish/StructuralEngineering.ExcelDna-AddIn64-packed.xll
```

Building creates `bin` and `obj` files. This is different from saving captured
ETABS data. Do not load this new build alongside the installed add-in. Installed
and source builds have separate identities; a successful build does not prove
that Excel is running those exact bytes.

## 4. Check the actual XLL in Excel

This optional three-minute check uses the installed product. Start Excel
normally and create a blank workbook. Enter:

```excel
=STR.INFO.VERSION()
```

The current source returns:

```text
StructuralEngineering.ExcelDna 0.1.0
```

This checks that Excel can call the installed adapter. It does not establish
ETABS connection, model readiness, or an exact source-commit match. You can
close the temporary workbook without saving it.

The checked Excel startup registration points to:

```text
C:\Users\P\AppData\Local\StructAutomate\Excel\0.1.0\StructAutomate.xll
```

If Excel returns `#NAME?`, inspect **File > Options > Add-ins** and the installed
package path. Record the actual outcome; do not install another XLL or change
Trust Center settings to hide the failure. We will diagnose the specific load
problem if it occurs.

In VS Code press **Ctrl+P**, open
`CSharp/src/StructuralEngineering.ExcelDna/WorksheetFunctions.cs`, and find
`InfoVersion`. The `[ExcelFunction(Name = "STR.INFO.VERSION", ...)]` attribute
names the function Excel sees. The method returns the text you just requested.
This is real product code, not a demonstration function added for the lesson.

## 5. Trace the real connection without running it yet

Open the files below with **Ctrl+P** and find the named method. Use **F12** on a
method to go to its definition. **Shift+F12** shows callers/references when the
C# solution has finished loading. This is source navigation; F12 does not
execute a getter or attach to ETABS.

| Follow this real file | Find | What you are looking for |
| --- | --- | --- |
| [StructAutomateRibbon.cs](../../../../../CSharp/src/StructuralEngineering.ExcelDna/StructAutomateRibbon.cs) | `OnConnectEtabs` | Excel button entry point |
| [EtabsConnectionCommands.cs](../../../../../CSharp/src/StructuralEngineering.ExcelDna/EtabsConnectionCommands.cs) | `ConnectEtabsProcess` | Chooses a process; records the workbook/request; starts background work |
| [EtabsConnectionClient.cs](../../../../../CSharp/src/StructuralEngineering.ExcelDna/EtabsConnectionClient.cs) | `ConnectAsync` | Validates/launches the packaged worker and currently exchanges files |
| [Worker Program.cs](../../../../../CSharp/tools/StructAutomate.EtabsWorker/Program.cs) | `EtabsContextOperationBroker` | Owns the read operation and waits for cleanup |
| [EtabsHostDiscovery.cs](../../../../../CSharp/src/StructuralEngineering.Etabs/EtabsHostDiscovery.cs) | `Discover` | Attaches to the specified PID and reads actual host/model identity |
| [EtabsContextCapture.cs](../../../../../CSharp/src/StructuralEngineering.Etabs/EtabsContextCapture.cs) | `Run`, `ReadState` | Bulk geometry and pre/post consistency checks |
| [EtabsConnectionSession.cs](../../../../../CSharp/src/StructuralEngineering.ExcelDna/EtabsConnectionSession.cs) | Constructor, `Neighbours` | Builds dictionaries; later selections use memory |

Read only those methods today. Find `Task.Run` and `ExcelAsyncUtil.QueueAsMacro`
in the command file. They mark the move to background work and the return to
Excel's main thread. Long ETABS work must not run on Excel's UI thread; Excel
object-model access returns to its main thread. See
[Excel-DNA's object-model guidance](https://excel-dna.net/docs/archive/wiki/COM-object-model-notes/).

## 6. The memory-only change before the next live exercise

The current production Connect command writes request/response files, a getter
journal and a context artifact. This lesson does not call it. An unchanged
Connect command would not satisfy the owner's current no-captured-data-writes
preference.

Next, we will adapt the real acquisition path for a development session whose
captured data remains in typed arrays and dictionaries. That change needs to
retain exact-process attachment, the owned STA COM thread, model/units checks,
return-code and array validation, cancellation and cleanup. Keeping data in RAM
does not require discarding those controls. The transport and any control-only
locking mechanism must be explained separately from stored model data before
the live exercise.

We will run/debug the adapted product reader in VS Code against a real model.
Excel joins when testing its real caller and display. A thin development entry
point may make the product services debuggable, but it must call the same
implementation rather than duplicate extraction logic in a teaching script.
No live debugger exercise is claimed ready by this setup lesson.

| Next observation | Relevant real API/data | What it does not prove alone |
| --- | --- | --- |
| Correct connection | PID/start/executable, `GetObjectProcess`, `GetVersion`, `GetModelFilename` | Results availability |
| Current model state | `GetModelIsLocked`, present/database units | That required cases completed or returned rows are current |
| Analysis readiness | `Analyze.GetCaseStatus` for required cases | That they are selected for output |
| Output selection | `GetCaseSelectedForOutput`, `GetComboSelectedForOutput` | That force rows exist for every requested member |
| Floor geometry/properties | Bulk frame/point data, story IDs, sections/materials, axes, offsets, releases and support context | Physical spans or engineering design readiness without interpretation |
| Force completeness | Object/element identity, both stations, case/step, concurrent P/V2/V3/T/M2/M3 and row accounting | Complete serviceability/design inputs |

A locked model is not the same as available results. CSI exposes the
[lock getter](https://docs.csiamerica.com/help-files/etabs-api-2016/html/6af877a8-2784-3da8-903a-f8f32313f881.htm)
separately from [analysis-status operations](https://docs.csiamerica.com/help-files/etabs-api-2016/html/532acd95-6849-dae4-dd6c-2d3a54356aeb.htm).
These older web references explain the separation; use the installed API help
and exact signatures for the actual ETABS 23.3.1 calls.

## Your checkpoint

Stop here when you can independently:

1. Open the real solution and see the C# projects in VS Code.
2. Read your SDK/runtime versions and complete the locked product build.
3. Find `InfoVersion` and, if using Excel today, observe its installed result.
4. Follow the real connection from ribbon to worker to in-memory indexes.
5. Explain why lock state, case status, output selection and returned force
   rows require separate checks.

No learner step is pre-marked complete. Tell the assistant the first failed
step or your observed checkpoint. We then work through exact-process attachment
and state inspection in the real product, one runnable step at a time.
