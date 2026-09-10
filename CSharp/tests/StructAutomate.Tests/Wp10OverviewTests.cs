using System.Security.Cryptography;
using System.Text.Json;
using StructuralEngineering.Contracts;
using StructuralEngineering.Etabs;
using StructuralEngineering.ExcelDna;
using Xunit;

namespace StructAutomate.Tests;

public sealed class Wp10OverviewTests
{
    [Fact]
    public void OverviewDoesNotScaleItsCallsWithFrameCountOrReadGeometry()
    {
        using var small = new Wp10InspectionTests.Host { Frames = 2, Units = 9 };
        using var large = new Wp10InspectionTests.Host { Frames = 100_000, Units = 9 };
        var first = EtabsInspectionReader.Read(small, DateTimeOffset.UtcNow.AddMinutes(1), false, TestContext.Current.CancellationToken, overviewOnly: true);
        var second = EtabsInspectionReader.Read(large, DateTimeOffset.UtcNow.AddMinutes(1), false, TestContext.Current.CancellationToken, overviewOnly: true);
        Assert.Equal(EtabsInspectionReader.OverviewScope, second.Scope);
        Assert.Equal(100_000, second.FrameCount);
        Assert.Equal(small.Operations, large.Operations);
        Assert.Equal(33, second.Calls.Count);
        Assert.Empty(first.SampleFrames); Assert.Empty(second.SampleFrames);
        Assert.DoesNotContain(large.Operations, operation => operation.Contains("GetAllFrames", StringComparison.Ordinal) ||
            operation.Contains("GetAllPoints", StringComparison.Ordinal) || operation.StartsWith("DatabaseTables.", StringComparison.Ordinal) ||
            operation.StartsWith("Results.", StringComparison.Ordinal));
        Assert.Throws<ArgumentException>(() => EtabsInspectionReader.Read(large, DateTimeOffset.UtcNow.AddMinutes(1), true, TestContext.Current.CancellationToken, overviewOnly: true));
    }

    [Theory]
    [InlineData(false, false)]
    [InlineData(true, false)]
    [InlineData(false, true)]
    public async Task CompletedOverviewBindsNativeUnitsCountsSourceAndExternalEvidence(bool failDesign, bool nullEmptyArrays)
    {
        var host = new Wp10InspectionTests.Host { Units = 9, FailDesign = failDesign, NullEmptyArrays = nullEmptyArrays };
        var directory = Path.Combine(Path.GetTempPath(), "overview-" + Guid.NewGuid().ToString("N"));
        var rawPath = Path.Combine(directory, "inspection.json");
        var request = new EtabsContextWorkerRequest("overview", Target(host.Identity), DateTimeOffset.UtcNow.AddMinutes(1), Path.Combine(directory, "overview.json"));
        var sha = EtabsOverviewWorkerCodec.RequestSha256(request);
        try
        {
            var handle = EtabsInspectionBroker.Start(new(request.RequestId, host.Identity.ProcessId, request.DeadlineUtc, rawPath),
                () => host, false, TestContext.Current.CancellationToken, overviewOnly: true);
            var result = await handle.Completion; await handle.Quiescence;
            Assert.Equal("completed", result.State); Assert.True(result.CleanupCompleted);
            var raw = File.ReadAllBytes(rawPath); var journal = File.ReadAllBytes(rawPath + ".journal.jsonl");
            var artifact = EtabsOverviewProjector.Project(raw, "inspection.json", journal, "inspection.json.journal.jsonl", request.RequestId, sha, request.Target);
            var overview = artifact.Overview;
            Assert.Equal(9, overview.Source.PresentUnits); Assert.Equal(9, overview.Source.DatabaseUnits);
            Assert.Equal(25, overview.FrameCount); Assert.Equal(42, overview.PointCount); Assert.Equal(17, overview.AreaCount);
            Assert.Equal(1, overview.CaseCount); Assert.Equal(1, overview.CompletedCaseCount);
            Assert.Equal(failDesign ? null : false, overview.ConcreteDesignResultsAvailable);
            Assert.Equal(failDesign ? 2 : 0, overview.Gaps.Count);
            var bytes = EtabsOverviewWorkerCodec.CanonicalArtifactJsonBytes(artifact);
            Assert.Equal(bytes, EtabsOverviewWorkerCodec.CanonicalArtifactJsonBytes(EtabsOverviewWorkerCodec.ParseAndValidateArtifact(bytes, request.Target, sha)));
            EtabsConnectionClient.ValidateOverviewEvidence(artifact, directory);
            Assert.Throws<InvalidDataException>(() => EtabsOverviewWorkerCodec.ParseAndValidateArtifact(bytes, request.Target with { ProcessId = 99 }, sha));
            Assert.Throws<InvalidDataException>(() => EtabsOverviewWorkerCodec.ParseAndValidateArtifact(bytes, request.Target, new('e', 64)));
            Assert.Throws<InvalidDataException>(() => EtabsContextWorkerCodec.ParseAndValidateArtifact(bytes));
            Assert.Throws<InvalidDataException>(() => EtabsOverviewWorkerCodec.CreateArtifact(overview with { CompletedCaseCount = 2 }));
            var changed = JsonSerializer.Deserialize<EtabsInspectionArtifact>(raw)!;
            Assert.Throws<InvalidDataException>(() => EtabsOverviewProjector.Project(JsonSerializer.SerializeToUtf8Bytes(changed with
            { Cleanup = changed.Cleanup with { HostDisposed = false } }), "inspection.json", journal, "inspection.json.journal.jsonl", request.RequestId, sha, request.Target));
            File.AppendAllText(rawPath, "changed");
            Assert.Throws<InvalidDataException>(() => EtabsConnectionClient.ValidateOverviewEvidence(artifact, directory));
        }
        finally { if (Directory.Exists(directory)) Directory.Delete(directory, true); }
    }

    [Fact]
    public void SeparateWirePurposeAndQuiescentCompletionAreRequired()
    {
        using var host = new Wp10InspectionTests.Host();
        var request = new EtabsContextWorkerRequest("overview", Target(host.Identity), DateTimeOffset.UtcNow.AddMinutes(1), "overview.json");
        var sha = EtabsOverviewWorkerCodec.RequestSha256(request);
        var bytes = EtabsOverviewWorkerCodec.CanonicalRequestJsonBytes(request);
        Assert.Equal(request, EtabsOverviewWorkerCodec.ParseRequest(bytes));
        Assert.NotEqual(sha, EtabsContextWorkerCodec.RequestSha256(request));
        Assert.Throws<InvalidDataException>(() => EtabsContextWorkerCodec.ParseRequest(bytes));
        var response = new EtabsContextWorkerResponse(request.RequestId, sha, EtabsContextWorkerState.Completed, null, null, "overview.json", new('a', 64), true, true);
        var responseBytes = EtabsOverviewWorkerCodec.CanonicalResponseJsonBytes(response);
        Assert.Equal(response, EtabsOverviewWorkerCodec.ParseAndValidateResponse(responseBytes, request.RequestId, sha));
        Assert.Throws<InvalidDataException>(() => EtabsOverviewWorkerCodec.ParseAndValidateResponse(responseBytes, "other", sha));
        Assert.Throws<ArgumentException>(() => EtabsOverviewWorkerCodec.CanonicalResponseJsonBytes(response with { Quiesced = false }));
    }

    [Fact]
    public void DetailedHandoffRejectsAChangedModelOrUnits()
    {
        var source = new EtabsContextSourceIdentity(123, DateTimeOffset.UtcNow, "ETABS.exe", new('a', 64), "model.EDB", 1,
            DateTimeOffset.UtcNow, new('b', 64), "23.3.1", true, 6, 9);
        var overview = EtabsOverviewWorkerCodec.CreateArtifact(new(new('c', 64), DateTimeOffset.UtcNow, source, 0, 0, 0, 0, 0, 0, 0,
            null, null, [], new(new('d', 64), "inspection.json", new('e', 64), "journal.jsonl", new('f', 64), 33)));
        var context = EtabsContextWorkerCodec.CreateArtifact(new(new('c', 64), DateTimeOffset.UtcNow, source, [], [], [],
            "source_geometry_only;supports=absent;spans=absent;offsets=absent;releases=absent;loads=absent;analysis=absent;strengths=absent"));
        EtabsOverviewWorkerCodec.ValidateDetailedSource(overview, context);
        foreach (var changed in new[] { source with { ModelSha256 = new('e', 64) }, source with { ProcessStartedUtc = source.ProcessStartedUtc.AddSeconds(1) },
            source with { PresentUnits = 9 }, source with { ModelLocked = false } })
            Assert.Throws<InvalidDataException>(() => EtabsOverviewWorkerCodec.ValidateDetailedSource(overview, context with { Inventory = context.Inventory with { Source = changed } }));
    }

    [Fact]
    public async Task InstalledOverviewPreservesSourceAndRecordsMeasuredAcquisition()
    {
        var targetPath = Environment.GetEnvironmentVariable("ETABS_OVERVIEW_TARGET_PATH");
        var package = Environment.GetEnvironmentVariable("ETABS_OVERVIEW_PACKAGE");
        var directory = Environment.GetEnvironmentVariable("ETABS_OVERVIEW_EVIDENCE_DIRECTORY");
        var modelPath = Environment.GetEnvironmentVariable("ETABS_OVERVIEW_MODEL_PATH");
        Assert.SkipWhen(new[] { targetPath, package, directory, modelPath }.Any(string.IsNullOrWhiteSpace), "Requires an exact live target, model, candidate package and new external evidence directory.");
        Assert.False(Directory.Exists(directory));
        var target = JsonSerializer.Deserialize<EtabsProcessTarget>(File.ReadAllBytes(targetPath!))!;
        var before = SHA256.HashData(File.ReadAllBytes(modelPath!));
        var watch = System.Diagnostics.Stopwatch.StartNew();
        var result = await EtabsConnectionClient.InspectAsync(package!, directory!,
            new(target.ProcessId, target.ProcessStartedUtc, target.ExecutablePath, "read-only qualification"), "overview", TestContext.Current.CancellationToken);
        watch.Stop();
        Assert.True(result.Artifact is not null, result.Response.Message);
        Assert.Equal(EtabsContextWorkerState.Completed, result.Response.State);
        Assert.Equal(0, EtabsConnectionClient.ActiveWorkerCount);
        Assert.Equal(before, SHA256.HashData(File.ReadAllBytes(modelPath!)));
        Assert.Equal(Convert.ToHexStringLower(before), result.Artifact!.Overview.Source.ModelSha256);
        File.WriteAllBytes(Path.Combine(directory!, "receipt.json"), JsonSerializer.SerializeToUtf8Bytes(new
        {
            schema_version = "etabs-overview-development/v1",
            passed = true,
            pf9_acceptance = false,
            elapsed_ms = watch.Elapsed.TotalMilliseconds,
            source_preserved = true,
            result.Response,
            result.Artifact.Overview,
            result.OperationDirectory
        }));
    }

    private static EtabsProcessTarget Target(EtabsHostIdentity identity) => new(identity.ProcessId, identity.ProcessStartedUtc, identity.ExecutablePath, identity.ExecutableSha256);
}
