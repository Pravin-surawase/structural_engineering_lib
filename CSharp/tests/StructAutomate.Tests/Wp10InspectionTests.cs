using StructuralEngineering.Etabs;
using Xunit;

namespace StructAutomate.Tests;

public sealed class Wp10InspectionTests
{
    [Fact]
    public void CountsAreDirectValuesAndDoNotAdmitBulkCallsAboveTheLimit()
    {
        using var host = new Host { Frames = 20_001 };
        var result = EtabsInspectionReader.Read(host, DateTimeOffset.UtcNow.AddMinutes(1), true, TestContext.Current.CancellationToken);
        Assert.Equal(20_001, result.FrameCount);
        Assert.Equal(42, result.PointCount);
        Assert.Equal(17, result.AreaCount);
        Assert.Empty(result.SampleFrames);
        Assert.Contains(result.Gaps, x => x.Operation == "frame sample");
        Assert.DoesNotContain(host.Operations, x => x == "FrameObj.GetAllFrames" || x == "Results.FrameForce");
        Assert.All(result.Calls, x => Assert.Equal(EtabsInspectionGetterMatrix.Sha256, x.GetterMatrixSha256));
    }

    [Fact]
    public void OptionalUnavailableTablesDoNotEraseTheCoreInventoryOrGetRetried()
    {
        using var host = new Host { FailTables = true };
        var result = EtabsInspectionReader.Read(host, DateTimeOffset.UtcNow.AddMinutes(1), false, TestContext.Current.CancellationToken);
        Assert.Equal(4, result.Gaps.Count);
        Assert.All(result.Gaps, x => Assert.Equal("ETABS.CSI_RETURN_CODE", x.Code));
        Assert.All(result.Gaps, x => Assert.Equal(7, x.RawInvocation!.ReturnValue));
        Assert.Equal(4, host.Operations.Count(x => x.StartsWith("DatabaseTables.", StringComparison.Ordinal)));
        Assert.Equal(25, result.FrameCount);
    }

    [Fact]
    public void MalformedDisplaySelectionRetainsRawEvidenceWithoutAcceptingNames()
    {
        using var host = new Host { MalformedDisplay = true };
        var result = EtabsInspectionReader.Read(host, DateTimeOffset.UtcNow.AddMinutes(1), false, TestContext.Current.CancellationToken);
        var gap = Assert.Single(result.Gaps);
        Assert.Equal("ETABS.RETURN_TYPE_INVALID", gap.Code);
        Assert.Equal(1, gap.RawInvocation!.Outputs[0]);
        Assert.Equal(2, ((object?[])gap.RawInvocation.Outputs[1]!).Length);
        Assert.DoesNotContain(result.Calls, x => x.Operation == gap.Operation);
    }

    [Fact]
    public void ChangedUnitsRejectTheInventory()
    {
        using var host = new Host { DriftUnits = true };
        Assert.Contains("Protected state changed", Assert.Throws<InvalidOperationException>(() =>
            EtabsInspectionReader.Read(host, DateTimeOffset.UtcNow.AddMinutes(1), false, TestContext.Current.CancellationToken)).Message);
    }

    [Theory]
    [InlineData("SapModel.GetModelFilename")]
    [InlineData("Results.Setup.GetCaseSelectedForOutput")]
    public void ChangedSourceOrSelectionRejectsTheInventory(string operation)
    {
        using var host = new Host { DriftOperation = operation };
        Assert.Contains("Protected state changed", Assert.Throws<InvalidOperationException>(() =>
            EtabsInspectionReader.Read(host, DateTimeOffset.UtcNow.AddMinutes(1), false, TestContext.Current.CancellationToken)).Message);
    }

    [Fact]
    public void DefinitionSampleIsBoundedAndDoesNotReadResults()
    {
        using var host = new Host();
        var result = EtabsInspectionReader.Read(host, DateTimeOffset.UtcNow.AddMinutes(1), true, TestContext.Current.CancellationToken);
        Assert.Equal(20, result.SampleFrames.Count);
        Assert.Equal(20, result.SampleFrames.Distinct().Count());
        Assert.DoesNotContain(host.Operations, x => x == "Results.FrameForce" || x.Contains("GetTableFor", StringComparison.Ordinal));
        Assert.Equal(2, host.Operations.Count(x => x == "FrameObj.GetAllFrames"));
        Assert.Contains("forces=not_read", result.Scope);
    }

    [Fact]
    public void InspectionProfileCannotAuthorizeMutationOrResultExtraction()
    {
        Assert.DoesNotContain(EtabsInspectionGetterMatrix.Allowed.Keys,
            x => x[(x.LastIndexOf('.') + 1)..].StartsWith("Set", StringComparison.Ordinal) || x.Contains("RunAnalysis", StringComparison.Ordinal) ||
                x.Contains("StartDesign", StringComparison.Ordinal) || x.StartsWith("File.", StringComparison.Ordinal) || x == "Results.FrameForce");
        using var host = new Host();
        var adapter = new EtabsGetterAdapter(host, EtabsInspectionGetterMatrix.Allowed);
        Assert.Equal("ETABS.CALL_NOT_ALLOWED", adapter.Read("Results.FrameForce", ["All", 2], DateTimeOffset.UtcNow.AddMinutes(1), TestContext.Current.CancellationToken).DiagnosticCode);
        Assert.Empty(host.Operations);
    }

    [Fact]
    public async Task BrokerPublishesOnlyAfterCleanupWithPairedCallEvidence()
    {
        var path = Path.Combine(Path.GetTempPath(), "inspection-" + Guid.NewGuid().ToString("N"), "capture.json");
        var host = new Host();
        try
        {
            var handle = EtabsInspectionBroker.Start(new("test", host.Identity.ProcessId, DateTimeOffset.UtcNow.AddMinutes(1), path), () => host, false, TestContext.Current.CancellationToken);
            var result = await handle.Completion;
            await handle.Quiescence;
            Assert.Equal("completed", result.State);
            Assert.True(result.CleanupCompleted);
            Assert.True(host.Disposed);
            Assert.Equal(ApartmentState.STA, host.Apartment);
            Assert.True(File.Exists(path));
            Assert.Equal(host.Operations.Count * 2, File.ReadLines(path + ".journal.jsonl").Count());
        }
        finally { if (Directory.Exists(Path.GetDirectoryName(path))) Directory.Delete(Path.GetDirectoryName(path)!, true); }
    }

    [Fact]
    public async Task DeadlineRetainsLeaseUntilTheBlockedProviderReturns()
    {
        var directory = Path.Combine(Path.GetTempPath(), "inspection-timeout-" + Guid.NewGuid().ToString("N"));
        using var entered = new ManualResetEventSlim(); using var release = new ManualResetEventSlim();
        var host = new Host { Entered = entered, Release = release };
        try
        {
            var first = EtabsInspectionBroker.Start(new("timeout", host.Identity.ProcessId, DateTimeOffset.UtcNow.AddMilliseconds(500), Path.Combine(directory, "a.json")), () => host, false, TestContext.Current.CancellationToken);
            Assert.True(entered.Wait(TimeSpan.FromSeconds(5), TestContext.Current.CancellationToken));
            Assert.Equal("transaction_uncertain", (await first.Completion).State);
            Assert.False(first.Quiescence.IsCompleted);
            var second = EtabsInspectionBroker.Start(new("other", host.Identity.ProcessId, DateTimeOffset.UtcNow.AddMinutes(1), Path.Combine(directory, "b.json")), () => throw new Exception("Must not attach"), false, TestContext.Current.CancellationToken);
            Assert.Equal("lease_unavailable", (await second.Completion).State);
            release.Set(); await first.Quiescence;
            Assert.True(host.Disposed);
            Assert.False(File.Exists(Path.Combine(directory, "a.json")));
        }
        finally { release.Set(); if (Directory.Exists(directory)) Directory.Delete(directory, true); }
    }

    private sealed class Host : IEtabsGetterHost
    {
        private static int _pid = 240_000;
        public EtabsHostIdentity Identity { get; } = new(Interlocked.Increment(ref _pid), DateTimeOffset.Parse("2026-09-10T00:00:00Z"),
            "ETABS.exe", "23.3.1.4563", 1, new string('a', 64), "ETABSv1.dll", "ETABSv1, Version=1.0.0.0", "2.16.0.0",
            new string('b', 64), "ETABSv1.tlb", 1, new string('c', 64), "model.EDB", 1,
            DateTimeOffset.Parse("2026-09-10T00:00:00Z"), new string('d', 64), "23.3.1", false, 6);
        public int Frames { get; init; } = 25;
        public bool FailTables { get; init; }
        public bool MalformedDisplay { get; init; }
        public bool DriftUnits { get; init; }
        public string? DriftOperation { get; init; }
        public ManualResetEventSlim? Entered { get; init; }
        public ManualResetEventSlim? Release { get; init; }
        public bool Disposed { get; private set; }
        public ApartmentState Apartment { get; private set; }
        public List<string> Operations { get; } = [];

        public EtabsInvocation Invoke(EtabsGetterDefinition definition, IReadOnlyList<object?> inputs, CancellationToken token)
        {
            Apartment = Thread.CurrentThread.GetApartmentState(); Operations.Add(definition.Operation);
            if (Operations.Count == 1 && Entered is not null) { Entered.Set(); Release!.Wait(); token.ThrowIfCancellationRequested(); }
            if (FailTables && definition.Operation.StartsWith("DatabaseTables.", StringComparison.Ordinal)) return new(7, []);
            if (MalformedDisplay && definition.Operation == "DatabaseTables.GetLoadCasesSelectedForDisplay") return new(0, [1, new object?[] { "Dead", null }]);
            if (definition.ReturnSemantics == EtabsReturnSemantics.DirectValue)
                return new(definition.Operation switch
                {
                    "FrameObj.Count" => Frames,
                    "PointObj.Count" => 42,
                    "AreaObj.Count" => 17,
                    "SapModel.GetModelFilename" => DriftOperation == definition.Operation && Operations.Count(x => x == definition.Operation) > 1 ? "other.EDB" : Identity.ModelPath,
                    "SapModel.GetPresentUnits" => DriftUnits && Operations.Count(x => x == definition.Operation) > 1 ? 9 : 6,
                    "SapModel.GetDatabaseUnits" => 9,
                    _ => false
                }, []);
            if (definition.Operation == "FrameObj.GetAllFrames")
            {
                var output = new object?[20]; output[0] = Frames;
                for (var column = 1; column < 20; column++)
                    output[column] = Enumerable.Range(0, Frames).Select(i => column switch
                    {
                        1 => (object)$"f{i:D3}",
                        2 => "section",
                        3 => $"story{i % 5}",
                        4 => $"p{i}",
                        5 => $"p{i + 1}",
                        19 => 0,
                        _ => 0d
                    }).ToArray();
                return new(0, output);
            }
            var values = definition.OutputKinds.Select((kind, index) => Default(kind, definition.FixedArrays.GetValueOrDefault(index))).ToArray();
            if (definition.Operation == "LoadCases.GetNameList") values = [1, new object?[] { "Dead" }];
            if (DriftOperation == definition.Operation && Operations.Count(x => x == definition.Operation) > 1) values = [true];
            if (definition.Operation == "FrameObj.GetPoints") values = ["p1", "p2"];
            return new(0, values);
        }

        private static object Default(EtabsRawValueKind kind, int length) => kind switch
        {
            EtabsRawValueKind.String => "sample",
            EtabsRawValueKind.Int32 => 0,
            EtabsRawValueKind.Double => 0d,
            EtabsRawValueKind.Boolean => false,
            EtabsRawValueKind.StringArray => Array.Empty<object?>(),
            EtabsRawValueKind.BooleanArray => Enumerable.Repeat<object?>(false, length).ToArray(),
            EtabsRawValueKind.DoubleArray => Enumerable.Repeat<object?>(0d, length).ToArray(),
            _ => Array.Empty<object?>()
        };
        public void Dispose() => Disposed = true;
    }
}
