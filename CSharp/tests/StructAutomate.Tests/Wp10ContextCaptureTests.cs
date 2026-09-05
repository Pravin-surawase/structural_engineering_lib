using StructuralEngineering.Contracts;
using StructuralEngineering.Etabs;
using Xunit;

namespace StructAutomate.Tests;

public sealed class Wp10ContextCaptureTests
{
    private static readonly DateTimeOffset Deadline = DateTimeOffset.UtcNow.AddMinutes(1);

    [Fact]
    public void UnlockedNoResultContextIsHashBoundAndUsesNoAnalysisOrResults()
    {
        using var host = new ContextHost(Identity(92001, locked: false));
        var inventory = EtabsContextCapture.Run(host, new("request-hash", Deadline), TestContext.Current.CancellationToken);
        var artifact = EtabsContextWorkerCodec.CreateArtifact(inventory);
        var bytes = EtabsContextWorkerCodec.CanonicalArtifactJsonBytes(artifact);
        var parsed = EtabsContextWorkerCodec.ParseAndValidateArtifact(bytes,
            new EtabsProcessTarget(92001, inventory.Source.ProcessStartedUtc, inventory.Source.ExecutablePath, inventory.Source.ExecutableSha256), "request-hash");

        Assert.False(parsed.Inventory.Source.ModelLocked);
        Assert.Equal(2000d, Assert.Single(parsed.Inventory.Points, point => point.SourcePointId == "p2").Xmm);
        Assert.Equal(EtabsFrameDesignOrientation.Beam, Assert.Single(parsed.Inventory.Frames).DesignOrientation);
        Assert.Equal("mat-1", Assert.Single(parsed.Inventory.Sections).SourceMaterialId);
        Assert.DoesNotContain(host.Operations, operation => operation.StartsWith("Results.", StringComparison.Ordinal) || operation.StartsWith("Analyze.", StringComparison.Ordinal));
    }

    [Fact]
    public void MismatchedBulkShapeRejectsWithoutInventory()
    {
        using var host = new ContextHost(Identity(92002, locked: false), badFrameShape: true);
        var error = Assert.Throws<InvalidOperationException>(() => EtabsContextCapture.Run(host, new("request-hash", Deadline), TestContext.Current.CancellationToken));
        Assert.Contains("ETABS.ARRAY_LENGTH_MISMATCH", error.Message, StringComparison.Ordinal);
    }

    [Fact]
    public async Task ContextAndLegacyBrokerSharePidLeaseAndTimeoutRequiresQuiescence()
    {
        var directory = Path.Combine(Path.GetTempPath(), $"wp10-context-{Guid.NewGuid():N}"); Directory.CreateDirectory(directory);
        using var entered = new ManualResetEventSlim(); using var release = new ManualResetEventSlim();
        try
        {
            var pid = 92003;
            var request = new EtabsBrokerRequest("context-timeout", pid, DateTimeOffset.UtcNow.AddMilliseconds(150), Path.Combine(directory, "context.json"));
            var context = new EtabsContextOperationBroker().Start(request,
                () => new ContextHost(Identity(pid, false)),
                (_, _) => { entered.Set(); release.Wait(); return Inventory(pid); }, TestContext.Current.CancellationToken);
            Assert.True(entered.Wait(TimeSpan.FromSeconds(3), TestContext.Current.CancellationToken));
            var timedOut = await context.Completion.WaitAsync(TimeSpan.FromSeconds(3), TestContext.Current.CancellationToken);
            Assert.Equal(EtabsContextWorkerState.TransactionUncertain, timedOut.State);
            var legacy = new EtabsOperationBroker().Start(
                new EtabsBrokerRequest("legacy", pid, DateTimeOffset.UtcNow.AddSeconds(5), Path.Combine(directory, "legacy.json")),
                () => throw new InvalidOperationException("must not attach"),
                (_, _) => throw new InvalidOperationException("must not acquire"), TestContext.Current.CancellationToken);
            Assert.Equal(EtabsBrokerState.LeaseUnavailable, (await legacy.Completion).State);
            release.Set(); await context.Quiescence.WaitAsync(TimeSpan.FromSeconds(3), TestContext.Current.CancellationToken);
            Assert.False(File.Exists(request.EvidencePath));
        }
        finally { release.Set(); Directory.Delete(directory, true); }
    }

    [Fact]
    public async Task CompletedContextRetainsExactGetterEvidenceAfterCleanup()
    {
        var directory = Path.Combine(Path.GetTempPath(), "wp10-context-proof-" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(directory);
        try
        {
            var deadline = DateTimeOffset.UtcNow.AddSeconds(10);
            var handle = new EtabsContextOperationBroker().Start(new("context-proof", 92004, deadline, Path.Combine(directory, "context.json")),
                () => new ContextHost(Identity(92004, false)), (host, token) => EtabsContextCapture.Run(host, new("request", deadline), token), TestContext.Current.CancellationToken);
            var result = await handle.Completion.WaitAsync(TimeSpan.FromSeconds(10), TestContext.Current.CancellationToken);
            await handle.Quiescence;
            Assert.Equal(EtabsContextWorkerState.Completed, result.State);
            Assert.True(result.CleanupCompleted);
            var proof = Assert.IsType<EtabsContextProvenance>(result.Artifact!.Inventory.Provenance);
            var bytes = File.ReadAllBytes(Path.Combine(directory, proof.JournalFileName));
            Assert.Equal(proof.JournalSha256, Convert.ToHexStringLower(System.Security.Cryptography.SHA256.HashData(bytes)));
            Assert.Equal(proof.GetterCalls * 2, File.ReadAllLines(Path.Combine(directory, proof.JournalFileName)).Length);
            Assert.Equal(EtabsContextGetterMatrix.Sha256, proof.GetterMatrixSha256);
        }
        finally { Directory.Delete(directory, true); }
    }

    private static EtabsContextInventory Inventory(int pid) => new("request-hash", DateTimeOffset.UtcNow, Source(Identity(pid, false)), [new("p1", 0, 0, 0), new("p2", 1000, 0, 0)], [new("f1", "s1", "story", "p1", "p2", EtabsFrameDesignOrientation.Beam)], [new("s1", "m1")], "source_geometry_only;supports=absent;spans=absent;offsets=absent;releases=absent;loads=absent;analysis=absent;strengths=absent");
    private static EtabsContextSourceIdentity Source(EtabsHostIdentity identity) => new(identity.ProcessId, identity.ProcessStartedUtc, identity.ExecutablePath, identity.ExecutableSha256, identity.ModelPath, identity.ModelBytes, identity.ModelModifiedUtc, identity.ModelSha256, identity.EtabsApiVersion, identity.ModelLocked, 6, 6);
    private static EtabsHostIdentity Identity(int pid, bool locked) => new(pid, DateTimeOffset.Parse("2026-09-05T10:00:00Z"), "ETABS.exe", "23.3.1.4563", 1, new string('a', 64), "ETABSv1.dll", "ETABSv1, Version=1.0.0.0", "2.16.0.0", new string('b', 64), "ETABSv1.tlb", 1, new string('c', 64), "model.EDB", 1, DateTimeOffset.Parse("2026-09-05T10:00:01Z"), new string('d', 64), "23.3.1", locked, 6);

    private sealed class ContextHost : IEtabsGetterHost
    {
        private readonly bool _badFrameShape;
        public ContextHost(EtabsHostIdentity identity, bool badFrameShape = false)
        {
            Identity = identity;
            _badFrameShape = badFrameShape;
        }
        public EtabsHostIdentity Identity { get; }
        public List<string> Operations { get; } = [];
        public EtabsInvocation Invoke(EtabsGetterDefinition definition, IReadOnlyList<object?> inputs, CancellationToken cancellationToken)
        {
            Operations.Add(definition.Operation);
            object?[] a(params object?[] values) => values;
            return definition.Operation switch
            {
                "SapModel.GetModelFilename" => new("model.EDB", []),
                "SapModel.GetModelIsLocked" => new(Identity.ModelLocked, []),
                "SapModel.GetPresentUnits" or "SapModel.GetDatabaseUnits" => new(6, []),
                "FrameObj.GetAllFrames" => new(0, a(1, _badFrameShape ? a() : a("f1"), a("s1"), a("story"), a("p1"), a("p2"), a(1d), a(0d), a(0d), a(2d), a(0d), a(0d), a(0d), a(0d), a(0d), a(0d), a(0d), a(0d), a(0d), a(2))),
                "PointObj.GetAllPoints" => new(0, a(2, a("p1", "p2"), a(0d, 2d), a(0d, 0d), a(0d, 0d))),
                "FrameObj.GetDesignOrientation" => new(0, a(2)),
                "PropFrame.GetMaterial" => new(0, a("mat-1")),
                _ => throw new InvalidOperationException(definition.Operation)
            };
        }
        public void Dispose() { }
    }
}
