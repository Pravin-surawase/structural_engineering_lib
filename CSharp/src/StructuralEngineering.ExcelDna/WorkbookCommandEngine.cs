using System.Text.Json;
using StructuralEngineering.Construction;
using StructuralEngineering.Contracts;
using StructuralEngineering.Core;
using StructuralEngineering.Reinforcement;

namespace StructuralEngineering.ExcelDna;

/// <summary>Pure application core: a workbook host supplies bulk table I/O and optional artifact storage.</summary>
public sealed class WorkbookCommandEngine
{
    private readonly WorkbookOperationDispatcher _dispatcher;
    private readonly string _executionFingerprint;

    public WorkbookCommandEngine(
        WorkbookOperationDispatcher? dispatcher = null,
        string? executionFingerprint = null)
    {
        if (executionFingerprint is not null && string.IsNullOrWhiteSpace(executionFingerprint))
            throw new ArgumentException("The execution fingerprint cannot be blank.", nameof(executionFingerprint));
        _dispatcher = dispatcher ?? new WorkbookOperationDispatcher();
        _executionFingerprint = executionFingerprint ?? WorkbookContract.CalculationEngineRevision;
    }

    public WorkbookFreshnessLedger InspectFreshness(
        WorkbookInputSnapshot input,
        WorkbookFreshnessLedger? prior,
        string suppliedTimestampUtc)
    {
        var revision = InputRevision(input);
        var executionMatches = prior?.ExecutionFingerprint == _executionFingerprint;
        var current = prior is not null && prior.IsCurrent && executionMatches &&
            prior.InputRevisionSha256 == revision &&
            prior.WorkbookId == input.WorkbookId && prior.ProjectId == input.ProjectId &&
            prior.MemberId == input.MemberId;
        return new(input.WorkbookId, input.ProjectId, input.MemberId, revision,
            _executionFingerprint,
            current ? prior!.OutputRevisionSha256 : null, current,
            current ? prior!.ResultIds : [], suppliedTimestampUtc,
            current ? "input_revision_matches" : executionMatches || prior is null
                ? "input_revision_changed"
                : "execution_fingerprint_changed");
    }

    public WorkbookCommandResult Execute(
        WorkbookCommandKind command,
        WorkbookInputSnapshot input,
        IWorkbookTableStore store,
        string suppliedTimestampUtc,
        WorkbookFreshnessLedger? prior = null,
        IWorkbookArtifactSink? artifactSink = null,
        Func<bool>? cancellationRequested = null)
    {
        var inputRevision = InputRevision(input);
        var declared = DeclaredTables(command);
        var results = new List<WorkbookOperationResult>();
        var diagnostics = new List<WorkbookDiagnostic>();
        var initial = InspectFreshness(input, prior, suppliedTimestampUtc);
        if (input.TemplateId != WorkbookContract.TemplateId ||
            string.IsNullOrWhiteSpace(input.WorkbookId) || string.IsNullOrWhiteSpace(input.ProjectId) ||
            string.IsNullOrWhiteSpace(input.MemberId) || string.IsNullOrWhiteSpace(input.RequestId))
        {
            diagnostics.Add(new("EXCEL.WORKBOOK_IDENTITY_INVALID", "error", "Template, workbook, project, member, and request identities are required."));
            return Finish(command, WorkbookReceiptState.RejectedInput, null, initial with { IsCurrent = false, Reason = "input_invalid" }, results, diagnostics, declared, input, suppliedTimestampUtc);
        }

        try
        {
            if (command == WorkbookCommandKind.MeasureDiagnose)
            {
                var benchmark = Measure(input.Benchmark);
                if (benchmark is null)
                {
                    diagnostics.Add(new("EXCEL.BENCHMARK_INVALID", "error", "XL-CMD-07 requires a named environment, workload revision, and finite nonnegative samples."));
                    return Finish(command, WorkbookReceiptState.RejectedInput, null, initial with { IsCurrent = false, Reason = "benchmark_invalid" }, results, diagnostics, declared, input, suppliedTimestampUtc);
                }
                IReadOnlyList<WorkbookTable> tables = [BenchmarkTable(benchmark)];
                return Write(command, input, inputRevision, store, suppliedTimestampUtc, initial, results, diagnostics, tables, declared, cancellationRequested, null, benchmark);
            }

            if (Cancelled(cancellationRequested))
                return Cancel(command, input, inputRevision, initial, results, diagnostics, declared, suppliedTimestampUtc);

            if (command == WorkbookCommandKind.ExportPackage)
                return ExportSingle(input, inputRevision, store, suppliedTimestampUtc,
                    initial, results, diagnostics, declared, artifactSink);

            var project = _dispatcher.DispatchProject(input.ProjectRequestJson);
            results.Add(project);
            if (command == WorkbookCommandKind.CreateValidate)
            {
                foreach (var row in input.TopologyRows)
                {
                    if (Cancelled(cancellationRequested))
                        return Cancel(command, input, inputRevision, initial, results, diagnostics, declared, suppliedTimestampUtc);
                    results.Add(_dispatcher.Dispatch(row));
                }
                return Write(command, input, inputRevision, store, suppliedTimestampUtc, initial, results, diagnostics, ResultTables(results, null), declared, cancellationRequested);
            }

            foreach (var row in input.AllOperationRows)
            {
                if (Cancelled(cancellationRequested))
                    return Cancel(command, input, inputRevision, initial, results, diagnostics, declared, suppliedTimestampUtc);
                results.Add(_dispatcher.Dispatch(row));
            }

            if (command is WorkbookCommandKind.Calculate or WorkbookCommandKind.Optimize)
            {
                DispatchMemberSeed(input, project, results, diagnostics);
                DispatchOptional(input.BarPathRequestJson, _dispatcher.DispatchPaths, results, cancellationRequested);
                DispatchBbsSeed(input.BbsRequestJson, results, diagnostics);
                DispatchQuantitySeed(input.QuantityRequestJson, results, diagnostics);
                DispatchCostSeed(input.CostRequestJson, results, diagnostics);
                DispatchPackageSeed(input.CalculationPackageRequestJson, results, diagnostics);
            }
            if (command == WorkbookCommandKind.Optimize)
            {
                if (string.IsNullOrWhiteSpace(input.OptimizationRequestJson))
                    diagnostics.Add(new("EXCEL.OPTIMIZATION_REQUEST_REQUIRED", "error", "XL-CMD-04 requires a strict optimization request."));
                else DispatchOptimizationSeed(input.OptimizationRequestJson, results, diagnostics);
            }
            return Write(command, input, inputRevision, store, suppliedTimestampUtc, initial, results, diagnostics, ResultTables(results, null), declared, cancellationRequested);
        }
        catch (Exception error) when (error is ArgumentException or InvalidOperationException or JsonException)
        {
            diagnostics.Add(new("EXCEL.COMMAND_FAILED", "error", error.Message));
            return Finish(command, WorkbookReceiptState.RejectedInput, null, initial with { IsCurrent = false, Reason = "command_failed" }, results, diagnostics, declared, input, suppliedTimestampUtc);
        }
    }

    /// <summary>
    /// Evaluates every member against an isolated in-memory table host, then performs one
    /// controlled write to the supplied workbook store. A failed member therefore never
    /// leaves a mixed 20-member result table in the host.
    /// </summary>
    public WorkbookCommandResult ExecuteBatch(
        WorkbookCommandKind command,
        IReadOnlyList<WorkbookInputSnapshot> inputs,
        IWorkbookTableStore store,
        string suppliedTimestampUtc,
        Func<bool>? cancellationRequested = null)
    {
        if (command is not (WorkbookCommandKind.Calculate or WorkbookCommandKind.CreateValidate or WorkbookCommandKind.Optimize))
            throw new ArgumentException("A batch requires one workbook/project and XL-CMD-01, XL-CMD-03, or XL-CMD-04.", nameof(inputs));
        ValidateBatchIdentity(inputs);

        var first = inputs[0];
        var inputRevision = BatchInputRevision(inputs);
        var declared = DeclaredTables(command);
        var batchInput = first with { RequestId = "batch:" + first.RequestId, MemberId = "batch" };
        if (command == WorkbookCommandKind.Calculate && !Cancelled(cancellationRequested) &&
            TryCurrentTables(first.WorkbookId, first.ProjectId, "batch", inputRevision,
                suppliedTimestampUtc, store, out var currentResults, out _, out var currentLedger) &&
            TryPackages(currentResults, currentLedger,
                inputs.Select(item => item.MemberId).ToArray(), out _, out _))
        {
            return Transaction(command, batchInput, inputRevision, store, suppliedTimestampUtc,
                currentLedger with
                {
                    Reason = "current_calculation_reused",
                    UpdatedAtUtc = suppliedTimestampUtc
                },
                [], [], [], declared, null, null);
        }

        var scratch = new ScratchStore();
        var individual = new List<WorkbookCommandResult>();
        foreach (var input in inputs)
        {
            if (Cancelled(cancellationRequested)) break;
            individual.Add(Execute(command, input, scratch, suppliedTimestampUtc, cancellationRequested: cancellationRequested));
        }
        var results = individual.SelectMany((item, index) => item.Results.Select(result =>
            result with { RowId = inputs[index].MemberId + ":" + result.RowId })).ToArray();
        var diagnostics = individual.SelectMany(item => item.Receipt.Diagnostics).ToList();
        if (Cancelled(cancellationRequested) || individual.Count != inputs.Count || individual.Any(item =>
                item.Receipt.State != WorkbookReceiptState.Completed || !item.Freshness.IsCurrent))
        {
            diagnostics.Add(new("EXCEL.BATCH_ABORTED", "error", "No workbook table was changed because one batch member was cancelled, rejected, or not current."));
            var stale = new WorkbookFreshnessLedger(first.WorkbookId, first.ProjectId, "batch", inputRevision,
                _executionFingerprint, null, false, [], suppliedTimestampUtc, "batch_aborted");
            return Finish(command, WorkbookReceiptState.RejectedInput, null, stale, results, diagnostics, declared, first with { RequestId = "batch:" + first.RequestId, MemberId = "batch" }, suppliedTimestampUtc);
        }

        var ledger = new WorkbookFreshnessLedger(first.WorkbookId, first.ProjectId, "batch", inputRevision,
            _executionFingerprint, null, true,
            results.Where(result => result.ResultId is not null).Select(result => result.ResultId!)
                .Distinct(StringComparer.Ordinal).ToArray(), suppliedTimestampUtc, "batch_completed");
        var resultTables = ResultTables(results, null);
        ledger = ledger with { OutputRevisionSha256 = WorkbookContract.HashTables(resultTables) };
        var tables = resultTables.Concat([FreshnessTable(ledger)]).ToArray();
        return Transaction(command, batchInput, inputRevision, store, suppliedTimestampUtc, ledger, results, diagnostics, tables, declared, null, null);
    }

    /// <summary>Reconstructs and verifies the persisted batch identity without changing the workbook.</summary>
    public WorkbookFreshnessLedger InspectBatchFreshness(
        IReadOnlyList<WorkbookInputSnapshot> inputs,
        IWorkbookTableStore store,
        string suppliedTimestampUtc)
    {
        ValidateBatchIdentity(inputs);
        var first = inputs[0];
        var revision = BatchInputRevision(inputs);
        return TryCurrentTables(first.WorkbookId, first.ProjectId, "batch", revision,
                suppliedTimestampUtc, store, out _, out _, out var ledger)
            ? ledger with { Reason = "persisted_batch_reconstructed" }
            : new(first.WorkbookId, first.ProjectId, "batch", revision, _executionFingerprint, null, false, [],
                suppliedTimestampUtc, "persisted_batch_not_current");
    }

    /// <summary>Exports every current member package from one verified batch as one immutable JSON bundle.</summary>
    public WorkbookCommandResult ExportBatch(
        IReadOnlyList<WorkbookInputSnapshot> inputs,
        IWorkbookTableStore store,
        string suppliedTimestampUtc,
        IWorkbookArtifactSink artifactSink)
    {
        ArgumentNullException.ThrowIfNull(artifactSink);
        ValidateBatchIdentity(inputs);
        var first = inputs[0];
        var inputRevision = BatchInputRevision(inputs);
        var batchInput = first with { MemberId = "batch", RequestId = "batch-export:" + first.RequestId };
        var declared = DeclaredTables(WorkbookCommandKind.ExportPackage);
        var diagnostics = new List<WorkbookDiagnostic>();
        string? packageError = null;
        IReadOnlyList<WorkbookExportPackage> packages = [];
        var current = TryCurrentTables(first.WorkbookId, first.ProjectId, "batch", inputRevision,
            suppliedTimestampUtc, store, out var resultTable, out var freshnessTable, out var ledger);
        if (!current || !TryPackages(resultTable, ledger, inputs.Select(item => item.MemberId).ToArray(),
                out packages, out packageError))
        {
            diagnostics.Add(new("EXCEL.PACKAGE_NOT_EXPORTED", "error",
                packageError ?? "XL-CMD-06 requires a current, untampered AO24 package for every batch member."));
            var stale = new WorkbookFreshnessLedger(first.WorkbookId, first.ProjectId, "batch",
                inputRevision, _executionFingerprint, null, false, [], suppliedTimestampUtc, "package_export_rejected");
            return Finish(WorkbookCommandKind.ExportPackage, WorkbookReceiptState.RejectedInput,
                null, stale, [], diagnostics, declared, batchInput, suppliedTimestampUtc);
        }

        var bundle = new
        {
            schema_version = "structautomate.batch-calculation-package/v1",
            workbook_id = first.WorkbookId,
            project_id = first.ProjectId,
            input_revision_sha256 = inputRevision,
            execution_fingerprint = _executionFingerprint,
            exported_at_utc = suppliedTimestampUtc,
            packages
        };
        var bytes = JsonSerializer.SerializeToUtf8Bytes(bundle, WorkbookContract.Json);
        return ExportArtifact(batchInput, inputRevision, store, suppliedTimestampUtc, ledger,
            [resultTable, freshnessTable], declared, diagnostics, artifactSink, bytes,
            "StructAutomate-calculation-packages");
    }

    /// <summary>Records warm workbook evidence while preserving the verified calculation revision.</summary>
    public WorkbookCommandResult RecordBatchBenchmark(
        IReadOnlyList<WorkbookInputSnapshot> inputs,
        IWorkbookTableStore store,
        string suppliedTimestampUtc,
        WorkbookBenchmarkRequest request)
    {
        ValidateBatchIdentity(inputs);
        var first = inputs[0];
        var inputRevision = BatchInputRevision(inputs);
        var batchInput = first with
        {
            MemberId = "batch",
            RequestId = "batch-benchmark:" + first.RequestId,
            Benchmark = request
        };
        var declared = DeclaredTables(WorkbookCommandKind.MeasureDiagnose);
        var diagnostics = new List<WorkbookDiagnostic>();
        var summary = Measure(request);
        if (summary is null || !TryCurrentTables(first.WorkbookId, first.ProjectId, "batch",
                inputRevision, suppliedTimestampUtc, store, out _, out var freshness, out var ledger))
        {
            diagnostics.Add(new("EXCEL.BENCHMARK_NOT_RECORDED", "error",
                "XL-CMD-07 requires finite samples and one current reconstructed batch."));
            var stale = new WorkbookFreshnessLedger(first.WorkbookId, first.ProjectId, "batch",
                inputRevision, _executionFingerprint, null, false, [], suppliedTimestampUtc, "benchmark_rejected");
            return Finish(WorkbookCommandKind.MeasureDiagnose, WorkbookReceiptState.RejectedInput,
                null, stale, [], diagnostics, declared, batchInput, suppliedTimestampUtc);
        }
        return Transaction(WorkbookCommandKind.MeasureDiagnose, batchInput, inputRevision, store,
            suppliedTimestampUtc, ledger, [], diagnostics, [BenchmarkTable(summary), freshness],
            declared, null, summary);
    }

    private static void DispatchOptional(string? json, Func<string, WorkbookOperationResult> dispatch, ICollection<WorkbookOperationResult> results, Func<bool>? cancellationRequested)
    {
        if (!string.IsNullOrWhiteSpace(json) && !Cancelled(cancellationRequested)) results.Add(dispatch(json));
    }

    private static void DispatchMemberSeed(WorkbookInputSnapshot input, WorkbookOperationResult project, ICollection<WorkbookOperationResult> results, ICollection<WorkbookDiagnostic> diagnostics)
    {
        if (string.IsNullOrWhiteSpace(input.MemberDesignRequestJson)) return;
        try
        {
            if (project.Execution != ExecutionState.Completed || project.OutputJson is null)
                throw new ArgumentException("AO17 requires the current AO14 project envelope.");
            var seed = WorkbookOperationDispatcher.Deserialize<WorkbookMemberDesignSeed>(input.MemberDesignRequestJson);
            var basis = WorkbookOperationDispatcher.Deserialize<BeamProject>(project.OutputJson);
            var leafResults = input.LeafOperationRows.Select(row =>
            {
                var result = results.SingleOrDefault(item => item.RowId == row.RowId)
                    ?? throw new ArgumentException($"Leaf row {row.RowId} did not dispatch exactly once.");
                return (row, result);
            }).ToArray();
            results.Add(new WorkbookOperationDispatcher().DispatchMember(seed, basis, leafResults));
        }
        catch (ArgumentException error)
        {
            diagnostics.Add(new("EXCEL.LEAF_EVIDENCE_DETACHED", "error", error.Message, "member", "member_design_seed"));
        }
        catch (JsonException error)
        {
            diagnostics.Add(new("EXCEL.LEAF_EVIDENCE_DETACHED", "error", error.Message, "member", "member_design_seed"));
        }
    }

    private static void DispatchBound(string? json, ICollection<WorkbookOperationResult> results, ICollection<WorkbookDiagnostic> diagnostics, string upstreamRowId, string dependencyField, string payloadField, Func<string, WorkbookOperationResult> dispatch)
    {
        if (string.IsNullOrWhiteSpace(json)) return;
        var upstream = results.LastOrDefault(item => item.RowId == upstreamRowId);
        if (upstream?.ResultId is null || !JsonDependencyMatches(json, dependencyField, upstream.ResultId) ||
            PayloadId(upstream) is not { } payload || !JsonDependencyMatches(json, payloadField, payload))
        {
            diagnostics.Add(new("EXCEL.DEPENDENCY_MISMATCH", "error", $"The supplied downstream request is not bound to the current {upstreamRowId} result.", upstreamRowId, dependencyField));
            return;
        }
        results.Add(dispatch(json));
    }

    private void DispatchPackageBound(string? json, ICollection<WorkbookOperationResult> results, ICollection<WorkbookDiagnostic> diagnostics)
    {
        if (string.IsNullOrWhiteSpace(json)) return;
        var bindings = new[]
        {
            ("member", "member_binding.result_id", "member_binding.output_payload_id"),
            ("paths", "schedule_binding.result_id", "schedule_binding.output_payload_id"),
            ("bbs", "bbs_binding.result_id", "bbs_binding.output_payload_id"),
            ("quantities", "quantity_binding.result_id", "quantity_binding.output_payload_id")
        };
        foreach (var (rowId, resultField, payloadField) in bindings)
        {
            var upstream = results.LastOrDefault(item => item.RowId == rowId);
            if (upstream?.ResultId is null || PayloadId(upstream) is not { } payload ||
                !JsonDependencyMatches(json, resultField, upstream.ResultId) ||
                !JsonDependencyMatches(json, payloadField, payload))
            {
                diagnostics.Add(new("EXCEL.DEPENDENCY_MISMATCH", "error", $"AO24 is not bound to the current {rowId} output.", rowId, resultField));
                return;
            }
        }
        var cost = results.LastOrDefault(item => item.RowId == "cost");
        if (cost is not null && (cost.ResultId is null || PayloadId(cost) is not { } costPayload ||
            !JsonDependencyMatches(json, "cost_binding.result_id", cost.ResultId) ||
            !JsonDependencyMatches(json, "cost_binding.output_payload_id", costPayload)))
        {
            diagnostics.Add(new("EXCEL.DEPENDENCY_MISMATCH", "error", "AO24 cost binding is not current.", "cost", "cost_binding.result_id"));
            return;
        }
        results.Add(_dispatcher.DispatchPackage(json));
    }

    private static string? PayloadId(WorkbookOperationResult result)
    {
        if (result.OutputJson is null) return null;
        return result.RowId switch
        {
            "member" => ResultFactory.SemanticId("output_payload_id", WorkbookOperationDispatcher.Deserialize<MemberDesignOutput>(result.OutputJson)),
            "paths" => ResultFactory.SemanticId("output_payload_id", WorkbookOperationDispatcher.Deserialize<BarPathOutput>(result.OutputJson)),
            "bbs" => ResultFactory.SemanticId("output_payload_id", WorkbookOperationDispatcher.Deserialize<BbsOutput>(result.OutputJson)),
            "quantities" => ResultFactory.SemanticId("output_payload_id", WorkbookOperationDispatcher.Deserialize<ConstructionQuantityOutput>(result.OutputJson)),
            "cost" => ResultFactory.SemanticId("output_payload_id", WorkbookOperationDispatcher.Deserialize<ConstructionCostOutput>(result.OutputJson)),
            _ => null
        };
    }

    private static bool JsonDependencyMatches(string json, string field, string expected)
    {
        using var document = JsonDocument.Parse(json);
        var element = document.RootElement;
        foreach (var segment in field.Split('.'))
        {
            if (!element.TryGetProperty(segment, out element)) return false;
        }
        return element.ValueKind == JsonValueKind.String && element.GetString() == expected;
    }

    private void DispatchBbsSeed(string? json, ICollection<WorkbookOperationResult> results, ICollection<WorkbookDiagnostic> diagnostics)
    {
        if (string.IsNullOrWhiteSpace(json)) return;
        try
        {
            var paths = RequiredResult(results, "paths");
            results.Add(_dispatcher.DispatchBbs(WorkbookOperationDispatcher.Deserialize<WorkbookBbsSeed>(json), paths));
        }
        catch (ArgumentException error) { diagnostics.Add(new("EXCEL.DEPENDENCY_MISMATCH", "error", error.Message, "bbs", "paths")); }
        catch (JsonException error) { diagnostics.Add(new("EXCEL.REQUEST_INVALID", "error", error.Message, "bbs", "request_json")); }
    }

    private void DispatchQuantitySeed(string? json, ICollection<WorkbookOperationResult> results, ICollection<WorkbookDiagnostic> diagnostics)
    {
        if (string.IsNullOrWhiteSpace(json)) return;
        try
        {
            var bbs = RequiredResult(results, "bbs");
            results.Add(_dispatcher.DispatchQuantities(WorkbookOperationDispatcher.Deserialize<WorkbookQuantitySeed>(json), bbs));
        }
        catch (ArgumentException error) { diagnostics.Add(new("EXCEL.DEPENDENCY_MISMATCH", "error", error.Message, "quantities", "bbs")); }
        catch (JsonException error) { diagnostics.Add(new("EXCEL.REQUEST_INVALID", "error", error.Message, "quantities", "request_json")); }
    }

    private void DispatchCostSeed(string? json, ICollection<WorkbookOperationResult> results, ICollection<WorkbookDiagnostic> diagnostics)
    {
        if (string.IsNullOrWhiteSpace(json)) return;
        try
        {
            var quantities = RequiredResult(results, "quantities");
            results.Add(_dispatcher.DispatchCost(WorkbookOperationDispatcher.Deserialize<WorkbookCostSeed>(json), quantities));
        }
        catch (ArgumentException error) { diagnostics.Add(new("EXCEL.DEPENDENCY_MISMATCH", "error", error.Message, "cost", "quantities")); }
        catch (JsonException error) { diagnostics.Add(new("EXCEL.REQUEST_INVALID", "error", error.Message, "cost", "request_json")); }
    }

    private void DispatchPackageSeed(string? json, ICollection<WorkbookOperationResult> results, ICollection<WorkbookDiagnostic> diagnostics)
    {
        if (string.IsNullOrWhiteSpace(json)) return;
        try
        {
            results.Add(_dispatcher.DispatchPackage(WorkbookOperationDispatcher.Deserialize<WorkbookCalculationPackageSeed>(json),
                RequiredResult(results, "member"), RequiredResult(results, "paths"),
                RequiredResult(results, "bbs"), RequiredResult(results, "quantities"),
                results.LastOrDefault(result => result.RowId == "cost")));
        }
        catch (ArgumentException error) { diagnostics.Add(new("EXCEL.DEPENDENCY_MISMATCH", "error", error.Message, "package", "current_result_chain")); }
        catch (JsonException error) { diagnostics.Add(new("EXCEL.REQUEST_INVALID", "error", error.Message, "package", "request_json")); }
    }

    private void DispatchOptimizationSeed(string json, ICollection<WorkbookOperationResult> results,
        ICollection<WorkbookDiagnostic> diagnostics)
    {
        try
        {
            results.Add(_dispatcher.DispatchOptimization(
                WorkbookOperationDispatcher.Deserialize<WorkbookOptimizationSeed>(json),
                RequiredResult(results, "member"), RequiredResult(results, "quantities"),
                results.LastOrDefault(result => result.RowId == "cost")));
        }
        catch (ArgumentException error) { diagnostics.Add(new("EXCEL.DEPENDENCY_MISMATCH", "error", error.Message, "optimization", "current_result_chain")); }
        catch (JsonException error) { diagnostics.Add(new("EXCEL.REQUEST_INVALID", "error", error.Message, "optimization", "request_json")); }
    }

    private static WorkbookOperationResult RequiredResult(IEnumerable<WorkbookOperationResult> results, string rowId) =>
        results.LastOrDefault(result => result.RowId == rowId && result.Execution == ExecutionState.Completed && result.OutputJson is not null)
        ?? throw new ArgumentException($"The current {rowId} result is required.");

    private WorkbookCommandResult ExportSingle(
        WorkbookInputSnapshot input,
        string inputRevision,
        IWorkbookTableStore store,
        string timestamp,
        WorkbookFreshnessLedger initial,
        IReadOnlyList<WorkbookOperationResult> results,
        List<WorkbookDiagnostic> diagnostics,
        IReadOnlyList<string> declared,
        IWorkbookArtifactSink? artifactSink)
    {
        if (artifactSink is null)
        {
            diagnostics.Add(new("EXCEL.PACKAGE_NOT_EXPORTED", "error",
                "XL-CMD-06 requires an artifact destination."));
            return Finish(WorkbookCommandKind.ExportPackage, WorkbookReceiptState.RejectedInput,
                null, initial with { IsCurrent = false, Reason = "package_export_rejected" },
                results, diagnostics, declared, input, timestamp);
        }
        if (!TryCurrentPackage(input, store, inputRevision, timestamp,
                out _, out var packageJson, out var currentTables, out var currentLedger))
        {
            diagnostics.Add(new("EXCEL.PACKAGE_NOT_EXPORTED", "error",
                "XL-CMD-06 requires a current, untampered AO24 package in the controlled result tables."));
            return Finish(WorkbookCommandKind.ExportPackage, WorkbookReceiptState.RejectedInput,
                null, initial with { IsCurrent = false, Reason = "package_export_rejected" },
                results, diagnostics, declared, input, timestamp);
        }
        return ExportArtifact(input, inputRevision, store, timestamp, currentLedger,
            currentTables, declared, diagnostics, artifactSink,
            System.Text.Encoding.UTF8.GetBytes(packageJson), "StructAutomate-calculation-package");
    }

    private WorkbookCommandResult ExportArtifact(
        WorkbookInputSnapshot input,
        string inputRevision,
        IWorkbookTableStore store,
        string timestamp,
        WorkbookFreshnessLedger ledger,
        IReadOnlyList<WorkbookTable> currentTables,
        IReadOnlyList<string> declared,
        List<WorkbookDiagnostic> diagnostics,
        IWorkbookArtifactSink artifactSink,
        byte[] bytes,
        string filePrefix)
    {
        var hash = WorkbookContract.HashBytes(bytes);
        var artifactName = $"{filePrefix}-{hash[..16]}.json";
        try
        {
            artifactSink.Stage(artifactName, bytes);
        }
        catch (Exception error)
        {
            try { artifactSink.Rollback(artifactName); }
            catch { /* The staging exception remains the actionable failure. */ }
            diagnostics.Add(new("EXCEL.PACKAGE_STAGE_FAILED", "error", error.Message));
            return Finish(WorkbookCommandKind.ExportPackage, WorkbookReceiptState.RejectedInput,
                ledger.OutputRevisionSha256, ledger with { Reason = "package_stage_failed" }, [],
                diagnostics, declared, input, timestamp);
        }
        return Transaction(WorkbookCommandKind.ExportPackage, input, inputRevision, store,
            timestamp, ledger, [], diagnostics, currentTables, declared, hash, null,
            () => artifactSink.Commit(artifactName), () => artifactSink.Rollback(artifactName));
    }

    private static void ValidateBatchIdentity(IReadOnlyList<WorkbookInputSnapshot> inputs)
    {
        ArgumentNullException.ThrowIfNull(inputs);
        if (inputs.Count == 0 ||
            inputs.Select(input => input.WorkbookId).Distinct(StringComparer.Ordinal).Count() != 1 ||
            inputs.Select(input => input.ProjectId).Distinct(StringComparer.Ordinal).Count() != 1 ||
            inputs.Select(input => input.MemberId).Distinct(StringComparer.Ordinal).Count() != inputs.Count ||
            inputs.Select(input => input.RequestId).Distinct(StringComparer.Ordinal).Count() != inputs.Count)
            throw new ArgumentException("A batch requires one workbook/project and unique member/request identities.", nameof(inputs));
    }

    private bool TryCurrentTables(
        string workbookId,
        string projectId,
        string memberId,
        string inputRevision,
        string timestamp,
        IWorkbookTableStore store,
        out WorkbookTable results,
        out WorkbookTable freshness,
        out WorkbookFreshnessLedger ledger)
    {
        results = new(WorkbookContract.ResultsTable, []);
        freshness = new(WorkbookContract.FreshnessTable, []);
        ledger = new(workbookId, projectId, memberId, inputRevision, _executionFingerprint, null, false, [],
            timestamp, "not_current");
        if (!store.TryRead(WorkbookContract.ResultsTable, out results) ||
            !store.TryRead(WorkbookContract.FreshnessTable, out freshness) ||
            results.Rows.Count < 2 || freshness.Rows.Count < 2 ||
            results.Rows.Skip(1).Any(row => row.Count != 16)) return false;
        string?[] expectedResultHeader = ["row_id", "operation", "execution", "applicability",
            "engineering", "completeness", "freshness", "result_id", "normalized_input_id",
            "calculation_id", "code_data_revision_id", "method_revision_id",
            "payload_chunk_index", "payload_chunk_count", "output_json_chunk", "diagnostics"];
        string?[] expectedFreshnessHeader = ["workbook_id", "project_id", "member_id",
            "input_revision", "execution_fingerprint", "output_revision", "is_current",
            "updated_at_utc", "reason", "result_id"];
        if (!HeaderMatches(results, expectedResultHeader) ||
            !HeaderMatches(freshness, expectedFreshnessHeader)) return false;
        var rows = freshness.Rows.Skip(1).ToArray();
        if (rows.Any(row => row.Count != expectedFreshnessHeader.Length ||
            row[0].Value != workbookId || row[1].Value != projectId || row[2].Value != memberId ||
            row[3].Value != inputRevision || row[4].Value != _executionFingerprint ||
            row[6].Value != bool.TrueString)) return false;
        var outputRevision = rows[0][5].Value;
        if (string.IsNullOrWhiteSpace(outputRevision) ||
            rows.Any(row => row[5].Value != outputRevision) ||
            WorkbookContract.HashTables([results]) != outputRevision) return false;
        var resultIds = results.Rows.Skip(1).Select(row => row[7].Value)
            .Where(value => !string.IsNullOrWhiteSpace(value)).Select(value => value!)
            .Distinct(StringComparer.Ordinal).ToArray();
        var freshnessIds = rows.Select(row => row[9].Value)
            .Where(value => !string.IsNullOrWhiteSpace(value)).Select(value => value!).ToArray();
        if (freshnessIds.Length != freshnessIds.Distinct(StringComparer.Ordinal).Count() ||
            !resultIds.ToHashSet(StringComparer.Ordinal).SetEquals(freshnessIds)) return false;
        ledger = new(workbookId, projectId, memberId, inputRevision, _executionFingerprint,
            outputRevision, true, freshnessIds, rows[0][7].Value ?? timestamp,
            rows[0][8].Value ?? "command_completed");
        return true;
    }

    private static bool HeaderMatches(WorkbookTable table, IReadOnlyList<string?> expected) =>
        table.Rows.Count > 0 && table.Rows[0].Count == expected.Count &&
        table.Rows[0].Select(cell => cell.Value).SequenceEqual(expected, StringComparer.Ordinal);

    private static bool TryPackages(
        WorkbookTable results,
        WorkbookFreshnessLedger ledger,
        IReadOnlyList<string> expectedMemberIds,
        out IReadOnlyList<WorkbookExportPackage> packages,
        out string? error)
    {
        var found = new Dictionary<string, WorkbookExportPackage>(StringComparer.Ordinal);
        var packageRows = results.Rows.Skip(1).Where(row =>
            row.Count == 16 && row[1].Value == "structural.calculation_package.create/v1" &&
            row[2].Value == ExecutionState.Completed.ToString() &&
            row[6].Value == FreshnessState.Current.ToString() &&
            !string.IsNullOrWhiteSpace(row[7].Value)).ToArray();
        foreach (var group in packageRows.GroupBy(row => row[7].Value!, StringComparer.Ordinal))
        {
            if (!ledger.ResultIds.Contains(group.Key, StringComparer.Ordinal) ||
                !TryAssemblePayload(group, out var payload)) continue;
            var rowId = group.First()[0].Value ?? string.Empty;
            const string suffix = ":package";
            if (!rowId.EndsWith(suffix, StringComparison.Ordinal)) continue;
            var memberId = rowId[..^suffix.Length];
            if (found.ContainsKey(memberId))
            {
                packages = [];
                error = $"Member {memberId} has more than one current AO24 package.";
                return false;
            }
            try
            {
                using var document = JsonDocument.Parse(payload);
                found.Add(memberId, new(memberId, group.Key, document.RootElement.Clone()));
            }
            catch (JsonException)
            {
                // A malformed stored payload is not a current exportable package.
            }
        }
        var expected = expectedMemberIds.ToHashSet(StringComparer.Ordinal);
        if (!expected.SetEquals(found.Keys))
        {
            packages = [];
            error = "Every requested member must have exactly one current AO24 package.";
            return false;
        }
        packages = expectedMemberIds.Select(memberId => found[memberId]).ToArray();
        error = null;
        return true;
    }

    private static bool TryAssemblePayload(
        IEnumerable<IReadOnlyList<WorkbookCell>> rows,
        out string payload)
    {
        payload = string.Empty;
        IReadOnlyList<IReadOnlyList<WorkbookCell>> ordered;
        try
        {
            ordered = rows.OrderBy(row => int.Parse(row[12].Value!,
                System.Globalization.CultureInfo.InvariantCulture)).ToArray();
        }
        catch (Exception error) when (error is ArgumentException or FormatException or OverflowException)
        {
            return false;
        }
        if (ordered.Count == 0 || !int.TryParse(ordered[0][13].Value, out var expectedChunks) ||
            ordered.Count != expectedChunks ||
            ordered.Select((row, index) => int.TryParse(row[12].Value, out var actual) &&
                actual == index + 1).Any(valid => !valid) || ordered.Any(row => row[14].Value is null))
            return false;
        payload = string.Concat(ordered.Select(row => row[14].Value));
        return true;
    }

    private bool TryCurrentPackage(WorkbookInputSnapshot input, IWorkbookTableStore store,
        string inputRevision, string timestamp, out string packageId, out string packageJson,
        out IReadOnlyList<WorkbookTable> currentTables, out WorkbookFreshnessLedger ledger)
    {
        packageId = string.Empty;
        packageJson = string.Empty;
        currentTables = [];
        ledger = new(input.WorkbookId, input.ProjectId, input.MemberId, inputRevision,
            _executionFingerprint, null, false, [], timestamp, "not_current");
        if (!TryCurrentTables(input.WorkbookId, input.ProjectId, input.MemberId, inputRevision,
                timestamp, store, out var results, out var freshness, out ledger)) return false;
        var packageRows = results.Rows.Skip(1).Where(row =>
            row.Count >= 16 && row[1].Value == "structural.calculation_package.create/v1" &&
            row[2].Value == ExecutionState.Completed.ToString() &&
            row[6].Value == FreshnessState.Current.ToString() &&
            !string.IsNullOrWhiteSpace(row[7].Value)).ToArray();
        foreach (var group in packageRows.GroupBy(row => row[7].Value!, StringComparer.Ordinal))
        {
            if (!ledger.ResultIds.Contains(group.Key, StringComparer.Ordinal) ||
                !TryAssemblePayload(group, out packageJson)) continue;
            packageId = group.Key;
            try { using var _ = JsonDocument.Parse(packageJson); }
            catch (JsonException) { continue; }
            currentTables = [results, freshness];
            return true;
        }
        return false;
    }

    private WorkbookCommandResult Write(
        WorkbookCommandKind command, WorkbookInputSnapshot input, string inputRevision,
        IWorkbookTableStore store, string timestamp, WorkbookFreshnessLedger initial,
        IReadOnlyList<WorkbookOperationResult> results, List<WorkbookDiagnostic> diagnostics,
        IReadOnlyList<WorkbookTable> baseTables, IReadOnlyList<string> declared,
        Func<bool>? cancellationRequested, string? artifactHash = null,
        WorkbookBenchmarkSummary? benchmark = null)
    {
        if (Cancelled(cancellationRequested)) return Cancel(command, input, inputRevision, initial, results, diagnostics, declared, timestamp);
        var allSuccessful = diagnostics.Count == 0 && results.All(result =>
            result.Execution == ExecutionState.Completed &&
            result.Completeness == CompletenessState.CompleteForScope &&
            result.Freshness == FreshnessState.Current);
        var ledger = new WorkbookFreshnessLedger(input.WorkbookId, input.ProjectId, input.MemberId,
            inputRevision, _executionFingerprint, null, allSuccessful,
            results.Where(result => result.ResultId is not null).Select(result => result.ResultId!)
                .Distinct(StringComparer.Ordinal).ToArray(),
            timestamp, allSuccessful ? "command_completed" : "operation_incomplete");
        var outputRevision = WorkbookContract.HashTables(baseTables);
        ledger = ledger with { OutputRevisionSha256 = outputRevision };
        var tables = baseTables.Concat([FreshnessTable(ledger)]).ToArray();
        return Transaction(command, input, inputRevision, store, timestamp, ledger, results, diagnostics, tables, declared, artifactHash, benchmark);
    }

    private WorkbookCommandResult Transaction(
        WorkbookCommandKind command, WorkbookInputSnapshot input, string inputRevision,
        IWorkbookTableStore store, string timestamp, WorkbookFreshnessLedger ledger,
        IReadOnlyList<WorkbookOperationResult> results, List<WorkbookDiagnostic> diagnostics,
        IReadOnlyList<WorkbookTable> tables, IReadOnlyList<string> declared,
        string? artifactHash, WorkbookBenchmarkSummary? benchmark,
        Action? afterReadback = null, Action? onRollback = null)
    {
        var mutationIds = tables.Select(table => table.TableId)
            .Append(WorkbookContract.ReceiptTable).Distinct(StringComparer.Ordinal).ToArray();
        var prior = mutationIds.ToDictionary(id => id,
            id => store.TryRead(id, out var table) ? table : null, StringComparer.Ordinal);
        var provisionalReceipt = Receipt(command, WorkbookReceiptState.Completed, ledger.OutputRevisionSha256, ledger, diagnostics, declared, input, timestamp, artifactHash);
        var priorReceipts = prior.GetValueOrDefault(WorkbookContract.ReceiptTable);
        var tablesWithReceipt = tables.Concat([ReceiptTable(provisionalReceipt, priorReceipts)]).ToArray();
        try
        {
            store.BulkWrite(tablesWithReceipt);
            var expected = tablesWithReceipt.ToDictionary(table => table.TableId, StringComparer.Ordinal);
            foreach (var pair in expected)
            {
                if (!store.TryRead(pair.Key, out var actual))
                    throw new InvalidOperationException($"EXCEL.READBACK_MISSING {pair.Key}");
                var expectedHash = WorkbookContract.HashJson(pair.Value);
                var actualHash = WorkbookContract.HashJson(actual);
                if (actualHash != expectedHash)
                    throw new InvalidOperationException(
                        $"EXCEL.READBACK_MISMATCH {pair.Key} {FirstDifference(pair.Value, actual)} " +
                        $"expected {expectedHash} actual {actualHash}");
            }
            afterReadback?.Invoke();
            return Finish(command, WorkbookReceiptState.Completed, ledger.OutputRevisionSha256, ledger, results, diagnostics, declared, input, timestamp, tablesWithReceipt, artifactHash, benchmark);
        }
        catch (Exception error)
        {
            diagnostics.Add(new("EXCEL.WRITE_FAILED", "error", error.Message));
            var rollbackErrors = new List<string>();
            try { onRollback?.Invoke(); }
            catch (Exception rollbackError) { rollbackErrors.Add(rollbackError.Message); }
            foreach (var entry in prior)
            {
                try
                {
                    if (entry.Value is null) store.Remove(entry.Key);
                    else store.BulkWrite([entry.Value]);
                }
                catch (Exception rollbackError) { rollbackErrors.Add($"{entry.Key}: {rollbackError.Message}"); }
            }
            foreach (var entry in prior)
            {
                try
                {
                    if (!RestoredExactly(store, entry.Key, entry.Value))
                        rollbackErrors.Add($"{entry.Key}: EXCEL.ROLLBACK_READBACK_MISMATCH");
                }
                catch (Exception rollbackError) { rollbackErrors.Add($"{entry.Key}: {rollbackError.Message}"); }
            }
            if (rollbackErrors.Count == 0)
                return Finish(command, WorkbookReceiptState.Restored, null, ledger with { IsCurrent = false, OutputRevisionSha256 = null, Reason = "write_failed_restored" }, results, diagnostics, declared, input, timestamp, [], artifactHash, benchmark);
            diagnostics.Add(new("EXCEL.ROLLBACK_UNVERIFIED", "error", string.Join(" | ", rollbackErrors)));
            return Finish(command, WorkbookReceiptState.RestorationUnverified, null, ledger with { IsCurrent = false, OutputRevisionSha256 = null, Reason = "restoration_unverified" }, results, diagnostics, declared, input, timestamp, [], artifactHash, benchmark);
        }
    }

    private static bool RestoredExactly(IWorkbookTableStore store, string tableId, WorkbookTable? expected)
    {
        if (expected is null) return !store.TryRead(tableId, out _);
        return store.TryRead(tableId, out var restored) && WorkbookContract.HashJson(restored) == WorkbookContract.HashJson(expected);
    }

    private static string FirstDifference(WorkbookTable expected, WorkbookTable actual)
    {
        if (expected.Rows.Count != actual.Rows.Count)
            return $"row_count expected {expected.Rows.Count} actual {actual.Rows.Count}";
        for (var row = 0; row < expected.Rows.Count; row++)
        {
            if (expected.Rows[row].Count != actual.Rows[row].Count)
                return $"row {row + 1} column_count expected {expected.Rows[row].Count} actual {actual.Rows[row].Count}";
            for (var column = 0; column < expected.Rows[row].Count; column++)
            {
                var expectedValue = expected.Rows[row][column].Value;
                var actualValue = actual.Rows[row][column].Value;
                if (expectedValue != actualValue)
                    return $"cell R{row + 1}C{column + 1} expected {Preview(expectedValue)} actual {Preview(actualValue)}";
            }
        }
        return "serialized shape differs";
    }

    private static string Preview(string? value)
    {
        if (value is null) return "<null>";
        var flattened = value.Replace("\r", "\\r", StringComparison.Ordinal)
            .Replace("\n", "\\n", StringComparison.Ordinal);
        return flattened.Length <= 120 ? $"'{flattened}'" : $"'{flattened[..120]}…'";
    }

    private static WorkbookCommandResult Cancel(WorkbookCommandKind command, WorkbookInputSnapshot input, string inputRevision, WorkbookFreshnessLedger initial, IReadOnlyList<WorkbookOperationResult> results, List<WorkbookDiagnostic> diagnostics, IReadOnlyList<string> declared, string timestamp)
    {
        diagnostics.Add(new("EXCEL.COMMAND_CANCELLED", "warning", "The command was cancelled before the next operation row."));
        return Finish(command, WorkbookReceiptState.Cancelled, null, initial with { IsCurrent = false, OutputRevisionSha256 = null, Reason = "cancelled" }, results, diagnostics, declared, input, timestamp);
    }

    private static bool Cancelled(Func<bool>? requested) => requested?.Invoke() == true;

    private string InputRevision(WorkbookInputSnapshot input) =>
        WorkbookContract.HashJson(new
        {
            WorkbookContract.CalculationEngineRevision,
            ExecutionFingerprint = _executionFingerprint,
            Input = input
        });

    private string BatchInputRevision(IReadOnlyList<WorkbookInputSnapshot> inputs) =>
        WorkbookContract.HashJson(new
        {
            WorkbookContract.CalculationEngineRevision,
            ExecutionFingerprint = _executionFingerprint,
            Inputs = inputs
        });

    private static IReadOnlyList<string> DeclaredTables(WorkbookCommandKind command) => command switch
    {
        WorkbookCommandKind.MeasureDiagnose => [WorkbookContract.BenchmarkTable, WorkbookContract.FreshnessTable, WorkbookContract.ReceiptTable],
        _ => [WorkbookContract.ResultsTable, WorkbookContract.FreshnessTable, WorkbookContract.ReceiptTable]
    };

    private static WorkbookBenchmarkSummary? Measure(WorkbookBenchmarkRequest? request)
    {
        if (request is null || string.IsNullOrWhiteSpace(request.EnvironmentFingerprint) || string.IsNullOrWhiteSpace(request.WorkloadRevision) || request.SamplesMilliseconds.Count == 0 || request.SamplesMilliseconds.Any(value => !double.IsFinite(value) || value < 0)) return null;
        var values = request.SamplesMilliseconds.Order().ToArray();
        return new(request.EnvironmentFingerprint, request.WorkloadRevision, values.Length, Percentile(values, .5), Percentile(values, .95), values[^1]);
    }

    private static double Percentile(IReadOnlyList<double> values, double position)
    {
        var index = (values.Count - 1) * position;
        var lower = (int)Math.Floor(index); var upper = (int)Math.Ceiling(index);
        return values[lower] + (values[upper] - values[lower]) * (index - lower);
    }

    private static IReadOnlyList<WorkbookTable> ResultTables(IReadOnlyList<WorkbookOperationResult> results, WorkbookBenchmarkSummary? benchmark) =>
        benchmark is null ? [ResultsTable(results)] : [ResultsTable(results), BenchmarkTable(benchmark)];

    private static WorkbookTable ResultsTable(IReadOnlyList<WorkbookOperationResult> results) => new(WorkbookContract.ResultsTable,
        [
            [new("row_id"), new("operation"), new("execution"), new("applicability"), new("engineering"), new("completeness"), new("freshness"), new("result_id"), new("normalized_input_id"), new("calculation_id"), new("code_data_revision_id"), new("method_revision_id"), new("payload_chunk_index"), new("payload_chunk_count"), new("output_json_chunk"), new("diagnostics")],
            .. results.SelectMany(ResultRows)
        ]);

    private static IEnumerable<IReadOnlyList<WorkbookCell>> ResultRows(WorkbookOperationResult result)
    {
        const int maximumChunkCharacters = 30_000;
        var chunks = string.IsNullOrEmpty(result.OutputJson)
            ? new string?[] { null }
            : Enumerable.Range(0, (result.OutputJson.Length + maximumChunkCharacters - 1) / maximumChunkCharacters)
                .Select(index => result.OutputJson.Substring(index * maximumChunkCharacters,
                    Math.Min(maximumChunkCharacters, result.OutputJson.Length - index * maximumChunkCharacters)))
                .Cast<string?>().ToArray();
        var diagnostics = JsonSerializer.Serialize(result.Diagnostics, WorkbookContract.Json);
        for (var index = 0; index < chunks.Length; index++)
            yield return [new(result.RowId), new(result.OperationSemanticId), new(result.Execution.ToString()), new(result.Applicability.ToString()), new(result.Engineering.ToString()), new(result.Completeness.ToString()), new(result.Freshness.ToString()), new(result.ResultId), new(result.NormalizedInputId), new(result.CalculationId), new(result.ProvenanceCodeDataRevisionId), new(result.ProvenanceMethodRevisionId), new((index + 1).ToString(System.Globalization.CultureInfo.InvariantCulture)), new(chunks.Length.ToString(System.Globalization.CultureInfo.InvariantCulture)), new(chunks[index]), new(index == 0 ? diagnostics : null)];
    }

    private static WorkbookTable FreshnessTable(WorkbookFreshnessLedger ledger)
    {
        var resultIds = ledger.ResultIds.Count == 0 ? new string?[] { null } : ledger.ResultIds.Cast<string?>().ToArray();
        return new(WorkbookContract.FreshnessTable,
            [[new("workbook_id"), new("project_id"), new("member_id"), new("input_revision"), new("execution_fingerprint"), new("output_revision"), new("is_current"), new("updated_at_utc"), new("reason"), new("result_id")],
             .. resultIds.Select(resultId => (IReadOnlyList<WorkbookCell>)[new(ledger.WorkbookId), new(ledger.ProjectId), new(ledger.MemberId), new(ledger.InputRevisionSha256), new(ledger.ExecutionFingerprint), new(ledger.OutputRevisionSha256), new(ledger.IsCurrent.ToString()), new(ledger.UpdatedAtUtc), new(ledger.Reason), new(resultId)])]);
    }

    private static WorkbookTable BenchmarkTable(WorkbookBenchmarkSummary summary) => new(WorkbookContract.BenchmarkTable,
        [[new("environment"), new("workload_revision"), new("sample_count"), new("p50_ms"), new("p95_ms"), new("max_ms")], [new(summary.EnvironmentFingerprint), new(summary.WorkloadRevision), new(summary.SampleCount.ToString(System.Globalization.CultureInfo.InvariantCulture)), new(summary.P50Milliseconds.ToString("R", System.Globalization.CultureInfo.InvariantCulture)), new(summary.P95Milliseconds.ToString("R", System.Globalization.CultureInfo.InvariantCulture)), new(summary.MaximumMilliseconds.ToString("R", System.Globalization.CultureInfo.InvariantCulture))]]);

    private static WorkbookCommandReceipt Receipt(WorkbookCommandKind command, WorkbookReceiptState state, string? outputRevision, WorkbookFreshnessLedger ledger, IReadOnlyList<WorkbookDiagnostic> diagnostics, IReadOnlyList<string> declared, WorkbookInputSnapshot input, string timestamp, string? artifactHash) =>
        new("workbook_receipt:" + WorkbookContract.HashJson(new { input.RequestId, command, state, outputRevision, ledger.ExecutionFingerprint, timestamp }), command, state, input.WorkbookId, input.ProjectId, input.MemberId, input.RequestId, ledger.InputRevisionSha256, ledger.ExecutionFingerprint, outputRevision, timestamp, declared, artifactHash, diagnostics);

    private static WorkbookTable ReceiptTable(WorkbookCommandReceipt receipt, WorkbookTable? prior = null)
    {
        IReadOnlyList<WorkbookCell> header = [new("receipt_id"), new("command"), new("state"), new("workbook_id"), new("project_id"), new("member_id"), new("request_id"), new("input_revision"), new("execution_fingerprint"), new("output_revision"), new("issued_at_utc"), new("artifact_sha256"), new("declared_output_tables"), new("diagnostics")];
        IReadOnlyList<WorkbookCell> row = [new(receipt.ReceiptId), new(receipt.Command.ToString()), new(receipt.State.ToString()), new(receipt.WorkbookId), new(receipt.ProjectId), new(receipt.MemberId), new(receipt.RequestId), new(receipt.InputRevisionSha256), new(receipt.ExecutionFingerprint), new(receipt.OutputRevisionSha256), new(receipt.IssuedAtUtc), new(receipt.ArtifactSha256), new(string.Join(",", receipt.DeclaredOutputTables)), new(JsonSerializer.Serialize(receipt.Diagnostics, WorkbookContract.Json))];
        var retained = prior is not null && prior.Rows.Count > 0 &&
            prior.Rows[0].Select(cell => cell.Value).SequenceEqual(header.Select(cell => cell.Value), StringComparer.Ordinal)
                ? prior.Rows.Skip(1)
                : [];
        return new(WorkbookContract.ReceiptTable, [header, .. retained, row]);
    }

    private static WorkbookCommandResult Finish(WorkbookCommandKind command, WorkbookReceiptState state, string? outputRevision, WorkbookFreshnessLedger ledger, IReadOnlyList<WorkbookOperationResult> results, IReadOnlyList<WorkbookDiagnostic> diagnostics, IReadOnlyList<string> declared, WorkbookInputSnapshot input, string timestamp, IReadOnlyList<WorkbookTable>? tables = null, string? artifactHash = null, WorkbookBenchmarkSummary? benchmark = null)
    {
        var receipt = Receipt(command, state, outputRevision, ledger, diagnostics, declared, input, timestamp, artifactHash);
        return new(results, ledger, receipt, tables ?? [], benchmark);
    }

    private sealed class ScratchStore : IWorkbookTableStore
    {
        private readonly Dictionary<string, WorkbookTable> _tables = new(StringComparer.Ordinal);
        public bool TryRead(string tableId, out WorkbookTable table) => _tables.TryGetValue(tableId, out table!);
        public void BulkWrite(IReadOnlyList<WorkbookTable> tables)
        {
            foreach (var table in tables) _tables[table.TableId] = table;
        }
        public void Remove(string tableId) => _tables.Remove(tableId);
    }

    private sealed record WorkbookExportPackage(
        string MemberId,
        string ResultId,
        JsonElement Package);
}
