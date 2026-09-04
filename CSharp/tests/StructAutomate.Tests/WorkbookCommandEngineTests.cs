using System.Text.Json;
using System.Text.Json.Serialization;
using StructuralEngineering.Contracts;
using StructuralEngineering.ExcelDna;
using Xunit;

namespace StructAutomate.Tests;

public class WorkbookCommandEngineTests
{
    [Fact]
    public void CreateValidateProducesOneCurrentAtomicTableSet()
    {
        var store = new MemoryStore();
        var result = new WorkbookCommandEngine().Execute(
            WorkbookCommandKind.CreateValidate, Snapshot(), store, "2026-09-04T00:00:00Z");

        Assert.Equal(WorkbookReceiptState.Completed, result.Receipt.State);
        Assert.True(result.Freshness.IsCurrent);
        Assert.Equal("structural.beam_project.create/v1", result.Results.Single().OperationSemanticId);
        Assert.True(store.TryRead(WorkbookContract.ResultsTable, out _));
        Assert.True(store.TryRead(WorkbookContract.FreshnessTable, out _));
        Assert.True(store.TryRead(WorkbookContract.ReceiptTable, out _));
    }

    [Fact]
    public void ChangedInputRevisionMakesPriorOutputStale()
    {
        var engine = new WorkbookCommandEngine();
        var prior = engine.Execute(WorkbookCommandKind.CreateValidate, Snapshot(), new MemoryStore(), "2026-09-04T00:00:00Z").Freshness;

        var stale = engine.InspectFreshness(Snapshot() with { RequestId = "request-2" }, prior, "2026-09-04T00:01:00Z");

        Assert.False(stale.IsCurrent);
        Assert.Equal("input_revision_changed", stale.Reason);
    }

    [Fact]
    public void FailedWriteRestoresExactPreimageAndNeverReturnsCurrent()
    {
        var old = new WorkbookTable(WorkbookContract.ResultsTable, [[new WorkbookCell("old")]]);
        var store = new FailingStore(old, failures: 1);

        var result = new WorkbookCommandEngine().Execute(
            WorkbookCommandKind.CreateValidate, Snapshot(), store, "2026-09-04T00:00:00Z");

        Assert.Equal(WorkbookReceiptState.Restored, result.Receipt.State);
        Assert.False(result.Freshness.IsCurrent);
        Assert.True(store.TryRead(WorkbookContract.ResultsTable, out var restored));
        Assert.Equal(WorkbookContract.HashJson(old), WorkbookContract.HashJson(restored));
        Assert.False(store.TryRead(WorkbookContract.FreshnessTable, out _));
    }

    [Fact]
    public void RollbackFailureIsExplicitlyUnverified()
    {
        var store = new FailingStore(new WorkbookTable(WorkbookContract.ResultsTable, [[new WorkbookCell("old")]]), failures: int.MaxValue);
        var result = new WorkbookCommandEngine().Execute(
            WorkbookCommandKind.CreateValidate, Snapshot(), store, "2026-09-04T00:00:00Z");

        Assert.Equal(WorkbookReceiptState.RestorationUnverified, result.Receipt.State);
        Assert.Contains(result.Receipt.Diagnostics, diagnostic => diagnostic.Code == "EXCEL.ROLLBACK_UNVERIFIED");
    }

    [Fact]
    public void CancellationAndInvalidBenchmarkAreNotCurrent()
    {
        var engine = new WorkbookCommandEngine();
        var cancelled = engine.Execute(WorkbookCommandKind.CreateValidate, Snapshot(), new MemoryStore(), "2026-09-04T00:00:00Z", cancellationRequested: () => true);
        var invalidBenchmark = engine.Execute(WorkbookCommandKind.MeasureDiagnose, Snapshot(), new MemoryStore(), "2026-09-04T00:00:00Z");

        Assert.Equal(WorkbookReceiptState.Cancelled, cancelled.Receipt.State);
        Assert.False(cancelled.Freshness.IsCurrent);
        Assert.Equal(WorkbookReceiptState.RejectedInput, invalidBenchmark.Receipt.State);
        Assert.False(invalidBenchmark.Freshness.IsCurrent);
    }

    [Fact]
    public void BenchmarkPercentilesAreDeterministic()
    {
        var snapshot = Snapshot() with { Benchmark = new WorkbookBenchmarkRequest("machine-r1", [1, 2, 3, 4, 5], "workload-r1") };
        var result = new WorkbookCommandEngine().Execute(WorkbookCommandKind.MeasureDiagnose, snapshot, new MemoryStore(), "2026-09-04T00:00:00Z");

        Assert.Equal(WorkbookReceiptState.Completed, result.Receipt.State);
        Assert.Equal(3, result.Benchmark!.P50Milliseconds, 12);
        Assert.Equal(4.8, result.Benchmark.P95Milliseconds, 12);
        Assert.Equal(5, result.Benchmark.MaximumMilliseconds, 12);
    }

    [Fact]
    public void BatchCalculatesMultipleMembersBeforeOneControlledWrite()
    {
        var first = Snapshot();
        var second = Snapshot() with { MemberId = "B2", RequestId = "request-b2" };
        var store = new MemoryStore();

        var result = new WorkbookCommandEngine().ExecuteBatch(
            WorkbookCommandKind.Calculate, [first, second], store, "2026-09-04T00:00:00Z");

        Assert.Equal(WorkbookReceiptState.Completed, result.Receipt.State);
        Assert.True(result.Freshness.IsCurrent);
        Assert.Equal(2, result.Results.Count);
        Assert.True(store.TryRead(WorkbookContract.ResultsTable, out var table));
        Assert.Equal(3, table.Rows.Count);
    }

    [Fact]
    public void TypicalBatchOptimizesExportsBenchmarksAndReconstructsOneCurrentChain()
    {
        var store = new MemoryStore(SampleWorkbookData.CreateTypicalTables(2));
        var inputs = WorkbookInputReader.Read(store);
        var engine = new WorkbookCommandEngine();
        var calculated = engine.ExecuteBatch(WorkbookCommandKind.Calculate, inputs, store,
            "2026-09-04T00:00:00Z");
        var optimized = engine.ExecuteBatch(WorkbookCommandKind.Optimize, inputs, store,
            "2026-09-04T00:01:00Z");

        Assert.True(calculated.Freshness.IsCurrent);
        Assert.True(optimized.Freshness.IsCurrent,
            JsonSerializer.Serialize(new { optimized.Receipt, optimized.Results }));
        Assert.Equal(2, optimized.Results.Count(result => result.RowId.EndsWith(":optimization", StringComparison.Ordinal)));
        var directory = Path.Combine(Path.GetTempPath(), "structautomate-wp09-" + Guid.NewGuid().ToString("N"));
        try
        {
            var sink = new FileWorkbookArtifactSink(directory);
            var exported = engine.ExportBatch(inputs, store, "2026-09-04T00:02:00Z", sink);

            Assert.True(exported.Receipt.State == WorkbookReceiptState.Completed,
                JsonSerializer.Serialize(exported.Receipt));
            Assert.True(exported.Freshness.IsCurrent);
            Assert.NotNull(sink.LastCommittedPath);
            Assert.Equal(exported.Receipt.ArtifactSha256,
                WorkbookContract.HashBytes(File.ReadAllBytes(sink.LastCommittedPath!)));
            using var artifact = JsonDocument.Parse(File.ReadAllText(sink.LastCommittedPath!));
            Assert.Equal("structautomate.batch-calculation-package/v1",
                artifact.RootElement.GetProperty("schema_version").GetString());
            Assert.Equal(2, artifact.RootElement.GetProperty("packages").GetArrayLength());

            var measured = engine.RecordBatchBenchmark(inputs, store, "2026-09-04T00:03:00Z",
                new("machine-r1", [1, 2, 3], "BENCH-EXCEL-TYPICAL/v1"));
            var reconstructed = engine.InspectBatchFreshness(inputs, store, "2026-09-04T00:04:00Z");

            Assert.Equal(WorkbookReceiptState.Completed, measured.Receipt.State);
            Assert.True(reconstructed.IsCurrent);
            Assert.Equal(optimized.Freshness.OutputRevisionSha256, reconstructed.OutputRevisionSha256);
            Assert.True(store.TryRead(WorkbookContract.BenchmarkTable, out _));
            Assert.True(store.TryRead(WorkbookContract.ReceiptTable, out var receipts));
            Assert.Equal(5, receipts.Rows.Count);
        }
        finally
        {
            if (Directory.Exists(directory)) Directory.Delete(directory, true);
        }
    }

    [Fact]
    public void UnchangedCompleteBatchReusesVerifiedResultsAndAppendsAReceipt()
    {
        var store = new MemoryStore(SampleWorkbookData.CreateTypicalTables(1));
        var inputs = WorkbookInputReader.Read(store);
        var engine = new WorkbookCommandEngine();
        var first = engine.ExecuteBatch(WorkbookCommandKind.Calculate, inputs, store,
            "2026-09-04T00:00:00Z");
        Assert.True(store.TryRead(WorkbookContract.ResultsTable, out var calculatedResults));
        Assert.True(store.TryRead(WorkbookContract.FreshnessTable, out var calculatedFreshness));

        var reused = engine.ExecuteBatch(WorkbookCommandKind.Calculate, inputs, store,
            "2026-09-04T00:01:00Z");

        Assert.Equal(WorkbookReceiptState.Completed, reused.Receipt.State);
        Assert.True(reused.Freshness.IsCurrent);
        Assert.Equal("current_calculation_reused", reused.Freshness.Reason);
        Assert.Empty(reused.Results);
        Assert.True(store.TryRead(WorkbookContract.ResultsTable, out var retainedResults));
        Assert.True(store.TryRead(WorkbookContract.FreshnessTable, out var retainedFreshness));
        Assert.Equal(WorkbookContract.HashJson(calculatedResults), WorkbookContract.HashJson(retainedResults));
        Assert.Equal(WorkbookContract.HashJson(calculatedFreshness), WorkbookContract.HashJson(retainedFreshness));
        Assert.True(store.TryRead(WorkbookContract.ReceiptTable, out var receipts));
        Assert.Equal(3, receipts.Rows.Count);
    }

    [Fact]
    public void ChangedExecutionFingerprintRejectsPersistedResultsAndForcesRecalculation()
    {
        var store = new MemoryStore(SampleWorkbookData.CreateTypicalTables(1));
        var inputs = WorkbookInputReader.Read(store);
        var originalEngine = new WorkbookCommandEngine(executionFingerprint: "runtime-a");
        var calculated = originalEngine.ExecuteBatch(WorkbookCommandKind.Calculate, inputs, store,
            "2026-09-04T00:00:00Z");
        Assert.True(store.TryRead(WorkbookContract.FreshnessTable, out var originalFreshness));
        store.Replace(originalFreshness with
        {
            Rows = [.. originalFreshness.Rows.Select((row, index) => index == 0
                ? row
                : row.Select((cell, column) => column == 4
                    ? new WorkbookCell("runtime-z")
                    : cell).ToArray())]
        });
        var tampered = originalEngine.InspectBatchFreshness(inputs, store,
            "2026-09-04T00:00:30Z");

        var upgradedEngine = new WorkbookCommandEngine(executionFingerprint: "runtime-b");
        var stale = upgradedEngine.InspectBatchFreshness(inputs, store,
            "2026-09-04T00:01:00Z");
        var recalculated = upgradedEngine.ExecuteBatch(WorkbookCommandKind.Calculate, inputs, store,
            "2026-09-04T00:02:00Z");

        Assert.Equal("runtime-a", calculated.Freshness.ExecutionFingerprint);
        Assert.Equal("runtime-a", calculated.Receipt.ExecutionFingerprint);
        Assert.False(tampered.IsCurrent);
        Assert.False(stale.IsCurrent);
        Assert.Equal("persisted_batch_not_current", stale.Reason);
        Assert.NotEmpty(recalculated.Results);
        Assert.Equal("batch_completed", recalculated.Freshness.Reason);
        Assert.Equal("runtime-b", recalculated.Freshness.ExecutionFingerprint);
        Assert.Equal("runtime-b", recalculated.Receipt.ExecutionFingerprint);
        Assert.NotEqual(calculated.Freshness.InputRevisionSha256,
            recalculated.Freshness.InputRevisionSha256);
        Assert.True(store.TryRead(WorkbookContract.FreshnessTable, out var freshness));
        Assert.Equal("execution_fingerprint", freshness.Rows[0][4].Value);
        Assert.All(freshness.Rows.Skip(1), row => Assert.Equal("runtime-b", row[4].Value));
    }

    [Fact]
    public void LegacyOutputSchemasMigrateDuringTheFirstFullRecalculation()
    {
        var (tables, priorReceiptCount) = LegacyWorkbookTables();
        var store = new StrictSchemaStore(tables);
        var inputs = WorkbookInputReader.Read(store);
        var engine = new WorkbookCommandEngine(executionFingerprint: "runtime-b");

        var recalculated = engine.ExecuteBatch(WorkbookCommandKind.Calculate, inputs, store,
            "2026-09-04T00:01:00Z");

        Assert.Equal(WorkbookReceiptState.Completed, recalculated.Receipt.State);
        Assert.NotEmpty(recalculated.Results);
        Assert.True(store.TryRead(WorkbookContract.FreshnessTable, out var freshness));
        Assert.Equal("execution_fingerprint", freshness.Rows[0][4].Value);
        Assert.All(freshness.Rows.Skip(1), row => Assert.Equal("runtime-b", row[4].Value));
        Assert.True(store.TryRead(WorkbookContract.ReceiptTable, out var receipts));
        Assert.Equal("execution_fingerprint", receipts.Rows[0][8].Value);
        Assert.Equal(priorReceiptCount + 1, receipts.Rows.Count - 1);
        Assert.All(receipts.Rows.Skip(1).Take(priorReceiptCount),
            row => Assert.Equal("legacy-unbound", row[8].Value));
        Assert.Equal("runtime-b", receipts.Rows[^1][8].Value);
    }

    [Fact]
    public void FailedLegacySchemaMigrationRestoresEveryExactTablePreimage()
    {
        var (tables, _) = LegacyWorkbookTables();
        var store = new StrictSchemaStore(tables, failAfterWrites: 2);
        var inputs = WorkbookInputReader.Read(store);
        Assert.True(store.TryRead(WorkbookContract.ResultsTable, out var priorResults));
        Assert.True(store.TryRead(WorkbookContract.FreshnessTable, out var priorFreshness));
        Assert.True(store.TryRead(WorkbookContract.ReceiptTable, out var priorReceipts));

        var result = new WorkbookCommandEngine(executionFingerprint: "runtime-b")
            .ExecuteBatch(WorkbookCommandKind.Calculate, inputs, store,
                "2026-09-04T00:01:00Z");

        Assert.Equal(WorkbookReceiptState.Restored, result.Receipt.State);
        Assert.False(result.Freshness.IsCurrent);
        Assert.True(store.TryRead(WorkbookContract.ResultsTable, out var restoredResults));
        Assert.True(store.TryRead(WorkbookContract.FreshnessTable, out var restoredFreshness));
        Assert.True(store.TryRead(WorkbookContract.ReceiptTable, out var restoredReceipts));
        Assert.Equal(WorkbookContract.HashJson(priorResults), WorkbookContract.HashJson(restoredResults));
        Assert.Equal(WorkbookContract.HashJson(priorFreshness), WorkbookContract.HashJson(restoredFreshness));
        Assert.Equal(WorkbookContract.HashJson(priorReceipts), WorkbookContract.HashJson(restoredReceipts));
    }

    [Fact]
    public void CreateValidateDoesNotSubstituteForTheFirstCompleteCalculation()
    {
        var store = new MemoryStore(SampleWorkbookData.CreateTypicalTables(1));
        var inputs = WorkbookInputReader.Read(store);
        var engine = new WorkbookCommandEngine();

        var validated = engine.ExecuteBatch(WorkbookCommandKind.CreateValidate, inputs, store,
            "2026-09-04T00:00:00Z");
        var calculated = engine.ExecuteBatch(WorkbookCommandKind.Calculate, inputs, store,
            "2026-09-04T00:01:00Z");

        Assert.True(validated.Freshness.IsCurrent);
        Assert.True(calculated.Freshness.IsCurrent);
        Assert.Equal("batch_completed", calculated.Freshness.Reason);
        Assert.NotEmpty(calculated.Results);
        Assert.Contains(calculated.Results,
            result => result.OperationSemanticId == "structural.calculation_package.create/v1");
    }

    [Fact]
    public void TamperingOrFailedArtifactStageCannotReplaceCurrentCalculationTables()
    {
        var store = new MemoryStore(SampleWorkbookData.CreateTypicalTables(1));
        var inputs = WorkbookInputReader.Read(store);
        var engine = new WorkbookCommandEngine();
        var calculated = engine.ExecuteBatch(WorkbookCommandKind.Calculate, inputs, store,
            "2026-09-04T00:00:00Z");
        Assert.True(calculated.Freshness.IsCurrent);
        Assert.True(store.TryRead(WorkbookContract.ResultsTable, out var before));
        var beforeHash = WorkbookContract.HashJson(before);

        var failedExport = engine.ExportBatch(inputs, store, "2026-09-04T00:01:00Z",
            new FailingArtifactSink());

        Assert.Equal(WorkbookReceiptState.RejectedInput, failedExport.Receipt.State);
        Assert.True(store.TryRead(WorkbookContract.ResultsTable, out var afterFailure));
        Assert.Equal(beforeHash, WorkbookContract.HashJson(afterFailure));

        store.Replace(afterFailure with
        {
            Rows = [.. afterFailure.Rows.Select((row, index) => index == 1
                ? row.Select((cell, column) => column == 14 ? new WorkbookCell("tampered") : cell).ToArray()
                : row)]
        });
        var reconstructed = engine.InspectBatchFreshness(inputs, store, "2026-09-04T00:02:00Z");
        var rejected = engine.ExportBatch(inputs, store, "2026-09-04T00:03:00Z",
            new FailingArtifactSink());

        Assert.False(reconstructed.IsCurrent);
        Assert.Equal(WorkbookReceiptState.RejectedInput, rejected.Receipt.State);
    }

    private static WorkbookInputSnapshot Snapshot() => new(
        WorkbookContract.TemplateId,
        "workbook-r1",
        "project-r1",
        "B1",
        "request-r1",
        Serialize(ProjectRequest()), [], []);

    private static BeamProjectRequest ProjectRequest() => new(
        new BeamProjectDefinition("project-r1", "Workbook beam", "project-revision-r1"),
        new StructuralUnitBasis("mm", "N", "Nmm", "N/mm2"),
        [new RevisionBinding("is456", "is456-r1", "test source")],
        new BeamDesignProfile("profile-r1", "profile-revision-r1", "IS 456:2000", SeismicDesignProfile.OrdinaryIs456,
            [new DesignCheckRule("flexure", "is456.beam.flexure.check/v1", CheckScope.Member, ApplicabilityState.Applicable, "test", "is456"),
             new DesignCheckRule("seismic", "is456.beam.seismic_detailing.check/v1", CheckScope.Member, ApplicabilityState.NotApplicable, "test", "is456")],
            [new DesignCriterion("cover", 25, "mm", "test")]),
        [new RevisionBinding("rebar", "rebar-r1", "test catalogue")]);

    private static string Serialize<T>(T value) => JsonSerializer.Serialize(value, new JsonSerializerOptions
    {
        PropertyNamingPolicy = JsonNamingPolicy.SnakeCaseLower,
        Converters = { new JsonStringEnumConverter(JsonNamingPolicy.SnakeCaseLower) }
    });

    private static (IReadOnlyList<WorkbookTable> Tables, int PriorReceiptCount) LegacyWorkbookTables()
    {
        var inputs = SampleWorkbookData.CreateTypicalTables(1);
        var seed = new MemoryStore(inputs);
        var engine = new WorkbookCommandEngine(executionFingerprint: "runtime-a");
        var snapshots = WorkbookInputReader.Read(seed);
        var calculated = engine.ExecuteBatch(WorkbookCommandKind.Calculate, snapshots, seed,
            "2026-09-04T00:00:00Z");
        Assert.Equal(WorkbookReceiptState.Completed, calculated.Receipt.State);
        Assert.True(seed.TryRead(WorkbookContract.ResultsTable, out var results));
        Assert.True(seed.TryRead(WorkbookContract.FreshnessTable, out var freshness));
        Assert.True(seed.TryRead(WorkbookContract.ReceiptTable, out var receipts));
        var legacyFreshness = WithoutColumn(freshness, 4);
        var legacyReceipts = WithoutColumn(receipts, 8);
        return ([.. inputs, results, legacyFreshness, legacyReceipts], receipts.Rows.Count - 1);
    }

    private static WorkbookTable WithoutColumn(WorkbookTable table, int column) => table with
    {
        Rows = [.. table.Rows.Select(row =>
            row.Where((_, index) => index != column).ToArray())]
    };

    private class MemoryStore : IWorkbookTableStore
    {
        protected readonly Dictionary<string, WorkbookTable> Tables = new(StringComparer.Ordinal);
        public MemoryStore() { }
        public MemoryStore(IReadOnlyList<WorkbookTable> tables)
        {
            foreach (var table in tables) Tables.Add(table.TableId, table);
        }
        public bool TryRead(string tableId, out WorkbookTable table) => Tables.TryGetValue(tableId, out table!);
        public virtual void BulkWrite(IReadOnlyList<WorkbookTable> tables)
        {
            foreach (var table in tables) Tables[table.TableId] = table;
        }
        public void Remove(string tableId) => Tables.Remove(tableId);
        public void Replace(WorkbookTable table) => Tables[table.TableId] = table;
    }

    private sealed class FailingStore : MemoryStore
    {
        private int _failures;
        public FailingStore(WorkbookTable? preimage, int failures)
        {
            _failures = failures;
            if (preimage is not null) Tables[preimage.TableId] = preimage;
        }
        public override void BulkWrite(IReadOnlyList<WorkbookTable> tables)
        {
            if (_failures > 0)
            {
                _failures--;
                if (tables.Count > 0) Tables[tables[0].TableId] = tables[0];
                throw new InvalidOperationException("injected write failure");
            }
            base.BulkWrite(tables);
        }
    }

    private sealed class StrictSchemaStore : MemoryStore
    {
        private readonly int? _failAfterWrites;
        private int _writes;
        private bool _failureConsumed;

        public StrictSchemaStore(IReadOnlyList<WorkbookTable> tables, int? failAfterWrites = null)
            : base(tables) => _failAfterWrites = failAfterWrites;

        public override void BulkWrite(IReadOnlyList<WorkbookTable> tables)
        {
            foreach (var table in tables)
            {
                if (Tables.TryGetValue(table.TableId, out var prior) &&
                    !prior.Rows[0].Select(cell => cell.Value)
                        .SequenceEqual(table.Rows[0].Select(cell => cell.Value), StringComparer.Ordinal))
                    throw new InvalidOperationException($"Existing table {table.TableId} has a different schema.");
                Tables[table.TableId] = table;
                _writes++;
                if (!_failureConsumed && _failAfterWrites is { } limit && _writes >= limit)
                {
                    _failureConsumed = true;
                    throw new InvalidOperationException("injected migration write failure");
                }
            }
        }
    }

    private sealed class FailingArtifactSink : IWorkbookArtifactSink
    {
        public void Stage(string artifactName, byte[] bytes) =>
            throw new IOException("injected artifact-stage failure");
        public void Commit(string artifactName) => throw new InvalidOperationException();
        public void Rollback(string artifactName) { }
    }
}
