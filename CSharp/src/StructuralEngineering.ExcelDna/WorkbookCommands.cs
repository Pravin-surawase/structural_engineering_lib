using System.Diagnostics;
using System.Runtime.InteropServices;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using ExcelDna.Integration;

namespace StructuralEngineering.ExcelDna;

/// <summary>Excel command boundary. All workbook, process and file effects enter here.</summary>
public static class WorkbookCommands
{
    public const string CreateValidateName = "STR_XL_CMD_01_CREATE_VALIDATE";
    public const string CalculateName = "STR_XL_CMD_03_CALCULATE_WORKBOOK";
    public const string OptimizeName = "STR_XL_CMD_04_OPTIMIZE_BEAMS";
    public const string ExportName = "STR_XL_CMD_06_EXPORT_PACKAGES";
    public const string MeasureName = "STR_XL_CMD_07_MEASURE_DIAGNOSE";
    public const string ReconstructName = "STR_XL_CMD_07_RECONSTRUCT_CURRENT";

    [ExcelCommand(Name = CreateValidateName, Description = "Create or validate the versioned beam workbook.")]
    public static string CreateValidate() => RunBatch(WorkbookCommandKind.CreateValidate);

    [ExcelCommand(Name = CalculateName, Description = "Calculate every beam from the current versioned input tables.")]
    public static string CalculateWorkbook() => RunBatch(WorkbookCommandKind.Calculate);

    [ExcelCommand(Name = OptimizeName, Description = "Run the bounded fixed-action search for every current beam.")]
    public static string OptimizeBeams() => RunBatch(WorkbookCommandKind.Optimize);

    [ExcelCommand(Name = ExportName, Description = "Export one verified JSON calculation-package bundle.")]
    public static string ExportPackages() => WithApplication((application, workbook, store) =>
    {
        var inputs = WorkbookInputReader.Read(store);
        var folder = string.IsNullOrWhiteSpace((string)workbook.Path)
            ? Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.MyDocuments), "StructAutomate Packages")
            : Path.Combine((string)workbook.Path, "StructAutomate Packages");
        var sink = new FileWorkbookArtifactSink(folder);
        var result = new WorkbookCommandEngine().ExportBatch(inputs, store, Timestamp(), sink);
        Ensure(result);
        return Json(new
        {
            state = State(result.Receipt.State),
            command = "XL-CMD-06",
            receipt_id = result.Receipt.ReceiptId,
            input_revision_sha256 = result.Receipt.InputRevisionSha256,
            output_revision_sha256 = result.Receipt.OutputRevisionSha256,
            artifact_path = sink.LastCommittedPath,
            artifact_sha256 = result.Receipt.ArtifactSha256,
            current = result.Freshness.IsCurrent
        });
    });

    [ExcelCommand(Name = MeasureName, Description = "Record the current runtime and a reconstructed workbook timing sample.")]
    public static string MeasureDiagnose() => WithApplication((application, workbook, store) =>
    {
        var inputs = WorkbookInputReader.Read(store);
        var timer = Stopwatch.StartNew();
        var inspected = new WorkbookCommandEngine().InspectBatchFreshness(inputs, store, Timestamp());
        timer.Stop();
        if (!inspected.IsCurrent)
            throw new InvalidOperationException("The workbook is not current; calculate it before measuring.");
        var request = new WorkbookBenchmarkRequest(RuntimeFingerprint(application),
            new[] { timer.Elapsed.TotalMilliseconds }, "BENCH-EXCEL-TYPICAL/v1");
        var result = new WorkbookCommandEngine().RecordBatchBenchmark(inputs, store, Timestamp(), request);
        Ensure(result);
        return Json(new
        {
            state = State(result.Receipt.State),
            command = "XL-CMD-07",
            receipt_id = result.Receipt.ReceiptId,
            environment = request.EnvironmentFingerprint,
            workload_revision = request.WorkloadRevision,
            reconstruction_ms = timer.Elapsed.TotalMilliseconds,
            current = result.Freshness.IsCurrent
        });
    });

    [ExcelCommand(Name = ReconstructName, Description = "Reconstruct and verify saved current result identities without writing.")]
    public static string ReconstructCurrent() => WithApplication((application, workbook, store) =>
    {
        var inputs = WorkbookInputReader.Read(store);
        var ledger = new WorkbookCommandEngine().InspectBatchFreshness(inputs, store, Timestamp());
        if (!ledger.IsCurrent)
            throw new InvalidOperationException("Saved results do not reconstruct from the current versioned inputs.");
        return Json(new
        {
            state = "completed",
            command = "XL-CMD-07-RECONSTRUCT",
            runtime = RuntimeFingerprint(application),
            ledger.InputRevisionSha256,
            ledger.OutputRevisionSha256,
            result_count = ledger.ResultIds.Count,
            current = true
        });
    });

    [ExcelCommand(Name = "STR_XL_SAMPLE_SETUP_TYPICAL", Description = "Reset this workbook to the shipped 20-member sample.")]
    public static string SetupTypicalSample() => WithApplication((application, workbook, store) =>
    {
        foreach (var output in new[]
                 {
                     WorkbookContract.ResultsTable, WorkbookContract.FreshnessTable,
                     WorkbookContract.ReceiptTable, WorkbookContract.BenchmarkTable,
                     WorkbookContract.HostEffectsTable
                 })
            store.Remove(output);
        var tables = SampleWorkbookData.CreateTypicalTables();
        store.BulkWrite(tables);
        foreach (var expected in tables)
        {
            if (!store.TryRead(expected.TableId, out var actual) ||
                WorkbookContract.HashJson(actual) != WorkbookContract.HashJson(expected))
                throw new InvalidOperationException(
                    $"Sample setup readback did not match {expected.TableId}.");
        }
        WriteOverview(workbook);
        return Json(new
        {
            state = "completed",
            command = "SAMPLE-SETUP",
            project_rows = 1,
            member_rows = 20,
            operation_rows = 200,
            input_revision_sha256 = WorkbookContract.HashTables(tables)
        });
    });

    [ExcelCommand(Name = "STR_XL_TEST_RESET_HOST_EFFECTS", Description = "Begin the installed UDF host-effect probe.")]
    public static string ResetHostEffects()
    {
        HostEffectLedger.ResetAndStart();
        return Json(new { state = "completed", command = "HOST-EFFECT-RESET" });
    }

    [ExcelCommand(Name = "STR_XL_TEST_CAPTURE_HOST_EFFECTS", Description = "End the installed UDF host-effect probe.")]
    public static string CaptureHostEffects()
    {
        var snapshot = HostEffectLedger.StopAndCapture();
        return WithApplication((application, workbook, store) =>
        {
            var rows = new List<IReadOnlyList<WorkbookCell>>
            {
                Cells("capture_id", "total_effects", "effect", "count", "captured_at_utc")
            };
            var captureId = "host_effect_capture:" + Guid.NewGuid().ToString("N");
            var timestamp = Timestamp();
            if (snapshot.Calls.Count == 0)
                rows.Add(Cells(captureId, snapshot.TotalCalls.ToString(), "(none)", "0", timestamp));
            else
                rows.AddRange(snapshot.Calls.Select(pair => Cells(captureId,
                    snapshot.TotalCalls.ToString(), pair.Key, pair.Value.ToString(), timestamp)));
            store.BulkWrite([new(WorkbookContract.HostEffectsTable, rows)]);
            return Json(new
            {
                state = "completed",
                command = "HOST-EFFECT-CAPTURE",
                total_effects = snapshot.TotalCalls,
                calls = snapshot.Calls
            });
        });
    }

    [ExcelCommand(Name = "STR_XL_TEST_FORCE_ROLLBACK", Description = "Force one mid-write error and prove exact restoration.")]
    public static string ForceRollback() => WithApplication((application, workbook, _) =>
    {
        var store = new ExcelWorkbookTableStore(workbook, failAfterWrites: 1);
        var inputs = WorkbookInputReader.Read(store);
        if (!store.TryRead(WorkbookContract.ResultsTable, out var before))
            throw new InvalidOperationException("Calculate the sample before the rollback probe.");
        var beforeHash = WorkbookContract.HashJson(before);
        var result = new WorkbookCommandEngine().ExecuteBatch(WorkbookCommandKind.Calculate,
            inputs, store, Timestamp());
        var restored = store.TryRead(WorkbookContract.ResultsTable, out var after);
        var afterHash = restored ? WorkbookContract.HashJson(after) : null;
        if (result.Receipt.State != WorkbookReceiptState.Restored || beforeHash != afterHash)
            throw new InvalidOperationException("The injected write failure did not restore StructuralResults exactly.");
        var receiptPath = RollbackReceiptPath();
        Directory.CreateDirectory(Path.GetDirectoryName(receiptPath)!);
        HostEffectLedger.Record("file.rollback_receipt.write");
        File.WriteAllText(receiptPath, Json(new
        {
            schema_version = "structautomate.excel-rollback-probe/v1",
            state = "restored",
            observed_at_utc = Timestamp(),
            structural_results_preimage_sha256 = beforeHash,
            structural_results_postimage_sha256 = afterHash,
            receipt = result.Receipt
        }), new UTF8Encoding(false));
        return Json(new
        {
            state = "restored",
            command = "FORCED-ROLLBACK",
            receipt_path = receiptPath,
            structural_results_preimage_sha256 = beforeHash,
            structural_results_postimage_sha256 = afterHash
        });
    });

    [ExcelCommand(Name = "STR_XL_TEST_PROGRESS_PROBE", Description = "Measure one command progress-yield boundary.")]
    public static string ProgressProbe() => WithApplication((application, workbook, store) =>
    {
        var timer = Stopwatch.StartNew();
        HostEffectLedger.Record("excel.application.status_bar.write");
        application.StatusBar = "StructAutomate progress probe";
        System.Windows.Forms.Application.DoEvents();
        timer.Stop();
        application.StatusBar = false;
        return Json(new { state = "completed", command = "PROGRESS-PROBE", response_ms = timer.Elapsed.TotalMilliseconds });
    });

    [ExcelCommand(Name = "STR_XL_TEST_CANCELLATION_PROBE", Description = "Prove cancellation before the next member operation.")]
    public static string CancellationProbe() => WithApplication((application, workbook, store) =>
    {
        var inputs = WorkbookInputReader.Read(store);
        var before = store.TryRead(WorkbookContract.ResultsTable, out var table)
            ? WorkbookContract.HashJson(table)
            : null;
        var timer = Stopwatch.StartNew();
        var result = new WorkbookCommandEngine().ExecuteBatch(WorkbookCommandKind.Calculate,
            inputs, store, Timestamp(), () => true);
        timer.Stop();
        var after = store.TryRead(WorkbookContract.ResultsTable, out var afterTable)
            ? WorkbookContract.HashJson(afterTable)
            : null;
        if (result.Freshness.IsCurrent || before != after)
            throw new InvalidOperationException("Cancellation changed a controlled result table.");
        return Json(new { state = "cancelled", command = "CANCELLATION-PROBE", response_ms = timer.Elapsed.TotalMilliseconds });
    });

    private static string RunBatch(WorkbookCommandKind command) => WithApplication((application, workbook, store) =>
    {
        if (command == WorkbookCommandKind.CreateValidate &&
            !store.TryRead(WorkbookContract.ProjectTable, out _) &&
            !store.TryRead(WorkbookContract.MembersTable, out _) &&
            !store.TryRead(WorkbookContract.OperationsTable, out _))
            store.BulkWrite(SampleWorkbookData.CreateTypicalTables(1, "standalone-beam-starter-r1"));
        var inputs = WorkbookInputReader.Read(store);
        var timer = Stopwatch.StartNew();
        var checks = 0;
        bool CancellationRequested()
        {
            checks++;
            if (checks % 5 == 0)
            {
                HostEffectLedger.Record("excel.application.progress_yield");
                application.StatusBar = $"StructAutomate: {command} ({checks} checkpoints)";
                System.Windows.Forms.Application.DoEvents();
            }
            return (GetAsyncKeyState(0x1B) & 0x8000) != 0;
        }
        var result = new WorkbookCommandEngine().ExecuteBatch(command, inputs, store,
            Timestamp(), CancellationRequested);
        timer.Stop();
        application.StatusBar = false;
        Ensure(result);
        return Json(new
        {
            state = State(result.Receipt.State),
            command = command switch
            {
                WorkbookCommandKind.CreateValidate => "XL-CMD-01",
                WorkbookCommandKind.Calculate => "XL-CMD-03",
                WorkbookCommandKind.Optimize => "XL-CMD-04",
                _ => command.ToString()
            },
            receipt_id = result.Receipt.ReceiptId,
            input_revision_sha256 = result.Receipt.InputRevisionSha256,
            output_revision_sha256 = result.Receipt.OutputRevisionSha256,
            current = result.Freshness.IsCurrent,
            member_count = inputs.Count,
            operation_result_count = result.Results.Count,
            reused_current_results = result.Results.Count == 0 &&
                                     result.Freshness.Reason == "current_calculation_reused",
            elapsed_ms = timer.Elapsed.TotalMilliseconds
        });
    });

    private static string WithApplication(Func<dynamic, dynamic, ExcelWorkbookTableStore, string> action)
    {
        dynamic application = ExcelDnaUtil.Application;
        dynamic? workbook = application.ActiveWorkbook;
        if (workbook is null)
            throw new InvalidOperationException("Open a workbook before running a StructAutomate command.");
        try
        {
            HostEffectLedger.Record("excel.command.invoke");
            return action(application, workbook, new ExcelWorkbookTableStore(workbook));
        }
        catch (Exception error)
        {
            try { application.StatusBar = false; } catch { }
            return Json(new
            {
                state = "rejected",
                error = error.GetType().Name,
                message = error.Message
            });
        }
        finally
        {
            ExcelWorkbookTableStore.ReleaseCom(workbook);
            ExcelWorkbookTableStore.ReleaseCom(application);
        }
    }

    private static void Ensure(WorkbookCommandResult result)
    {
        if (result.Receipt.State == WorkbookReceiptState.Completed && result.Freshness.IsCurrent) return;
        var message = string.Join("; ", result.Receipt.Diagnostics.Select(item => $"{item.Code}: {item.Message}"));
        throw new InvalidOperationException(string.IsNullOrWhiteSpace(message)
            ? $"Workbook command ended in {result.Receipt.State}."
            : message);
    }

    private static void WriteOverview(dynamic workbook)
    {
        HostEffectLedger.Record("excel.workbook.overview.write");
        dynamic worksheets = workbook.Worksheets;
        dynamic? sheet = null;
        dynamic? target = null;
        dynamic? versionCell = null;
        dynamic? areaCell = null;
        try
        {
            for (var index = 1; index <= (int)worksheets.Count; index++)
            {
                dynamic? candidate = null;
                try
                {
                    candidate = worksheets.Item(index);
                    if (!string.Equals((string)candidate.Name, "StructAutomate", StringComparison.Ordinal)) continue;
                    sheet = candidate;
                    candidate = null;
                    break;
                }
                finally { ExcelWorkbookTableStore.ReleaseCom(candidate); }
            }
            if (sheet is null)
            {
                sheet = worksheets.Add();
                sheet.Name = "StructAutomate";
            }
            target = sheet.Range["A1", "B10"];
            target.ClearContents();
            target.NumberFormat = "General";
            target.Value2 = new object[,]
            {
                { "StructAutomate standalone beam workbook", null! },
                { "Template", WorkbookContract.TemplateId },
                { "Workflow", "Validate -> Calculate -> Optimize -> Export -> Diagnose" },
                { "Members", SampleWorkbookData.TypicalMemberCount },
                { "Operation rows", SampleWorkbookData.TypicalOperationRowCount },
                { "Adapter", null! },
                { "20 mm bar area (mm2)", null! },
                { "Units", "mm, N, Nmm, N/mm2" },
                { "Input tables", "StructuralProject; StructuralMembers; StructuralOperations" },
                { "Result tables", "StructuralResults; StructuralFreshness; StructuralReceipts" }
            };
            versionCell = sheet.Range["B6"];
            versionCell.Formula = "=STR.INFO.VERSION()";
            areaCell = sheet.Range["B7"];
            areaCell.Formula = "=STR.REBAR.AREA(20)";
        }
        finally
        {
            ExcelWorkbookTableStore.ReleaseCom(areaCell);
            ExcelWorkbookTableStore.ReleaseCom(versionCell);
            ExcelWorkbookTableStore.ReleaseCom(target);
            ExcelWorkbookTableStore.ReleaseCom(sheet);
            ExcelWorkbookTableStore.ReleaseCom(worksheets);
        }
    }

    private static string RuntimeFingerprint(dynamic application)
    {
        var xllPath = ExcelDnaUtil.XllPath;
        HostEffectLedger.Record("file.xll.hash.read");
        var xllHash = File.Exists(xllPath)
            ? Convert.ToHexStringLower(SHA256.HashData(File.ReadAllBytes(xllPath)))
            : "missing";
        return string.Join("|",
            Environment.MachineName,
            RuntimeInformation.OSDescription,
            RuntimeInformation.ProcessArchitecture,
            $"excel={application.Version}.{application.Build}",
            $"excel_dna={ExcelDnaUtil.ExcelVersion}",
            $"dotnet={Environment.Version}",
            $"xll_sha256={xllHash}");
    }

    private static string RollbackReceiptPath() => Path.Combine(
        Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
        "StructAutomate", "Receipts", "excel-rollback-probe.json");

    private static string Timestamp() => DateTimeOffset.UtcNow.ToString("O");

    private static string State(WorkbookReceiptState state) =>
        JsonNamingPolicy.SnakeCaseLower.ConvertName(state.ToString());

    private static string Json<T>(T value) => JsonSerializer.Serialize(value, WorkbookContract.Json);

    private static IReadOnlyList<WorkbookCell> Cells(params string?[] values) =>
        values.Select(value => new WorkbookCell(value)).ToArray();

    [DllImport("user32.dll")]
    private static extern short GetAsyncKeyState(int virtualKey);
}
