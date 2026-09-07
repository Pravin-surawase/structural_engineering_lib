using System.Security.Cryptography;
using StructuralEngineering.Analysis;
using StructuralEngineering.Contracts;
using StructuralEngineering.Etabs;
using Xunit;

namespace StructAutomate.Tests;

public sealed class Wp10BatchCaptureTests
{
    [Theory]
    [InlineData(false)]
    [InlineData(true)]
    public async Task AdjacentMembersShareSourcesAndKeepDistinctGetterRowProvenance(bool mesh)
    {
        var directory = Path.Combine(Path.GetTempPath(), "wp10-batch-" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(directory);
        try
        {
            var host = new BatchHost(mesh ? "mesh" : null);
            var deadline = DateTimeOffset.UtcNow.AddSeconds(30);
            var handle = new EtabsBatchOperationBroker().Start(new("batch", host.Identity.ProcessId, deadline, Path.Combine(directory, "capture.json")),
                () => host, (source, token) => EtabsLiveGetterProbe.RunBatch(source, new("request", host.Context, ["beam", "beam2"], deadline), token), TestContext.Current.CancellationToken);
            var result = await handle.Completion;
            await handle.Quiescence;
            Assert.True(result.State == EtabsContextWorkerState.Completed, result.Message);
            Assert.True(host.Disposed);
            var bytes = File.ReadAllBytes(result.EvidencePath);
            var normalized = EtabsCaptureProjector.Normalize(bytes, Sha(bytes), Wp10SyntheticCapture.Options);
            Assert.True(normalized.Snapshot is not null, string.Join("; ", normalized.Diagnostics.Select(item => item.Message)));
            var artifact = Assert.IsType<EtabsBatchArtifact>(result.Artifact);
            var inMemory = EtabsCaptureProjector.Normalize(artifact, bytes, Sha(bytes), Wp10SyntheticCapture.Options);
            Assert.True(inMemory.Snapshot is not null, string.Join("; ", inMemory.Diagnostics.Select(item => item.Message)));
            Assert.Equal(normalized.Snapshot.SnapshotSha256, inMemory.Snapshot!.SnapshotSha256);
            Assert.Null(EtabsCaptureProjector.Normalize(artifact with { ArtifactSha256 = new('0', 64) }, bytes, Sha(bytes), Wp10SyntheticCapture.Options).Snapshot);
            var different = EtabsBatchArtifactCodec.Create(artifact.Content with
            {
                Capture = artifact.Content.Capture with { RequestSha256 = "different-but-self-consistent-request" }
            });
            Assert.Null(EtabsCaptureProjector.Normalize(different, bytes, Sha(bytes), Wp10SyntheticCapture.Options).Snapshot);
            var snapshot = normalized.Snapshot!;
            Assert.Equal(2, snapshot.Members.Count);
            Assert.Equal(mesh ? 4 : 3, snapshot.Points.Count);
            Assert.Equal(6, snapshot.ActionRows.Count);
            Assert.Single(snapshot.Materials);
            Assert.Single(snapshot.Sections);
            Assert.Equal(2, snapshot.ActionRows.Select(row => row.Provenance.CallId).Distinct().Count());
            Assert.All(snapshot.ActionRows.GroupBy(row => row.ObjectId), group =>
                Assert.Equal(new[] { 0, 1, 2 }, group.Select(row => row.Provenance.SourceRowIndex).Order()));
            Assert.Single(host.Operations, item => item == "PropMaterial.GetMPIsotropic");
            Assert.Single(host.Operations, item => item == "PropFrame.GetSectProps");
            Assert.Equal(3, host.Operations.Count(item => item == "PointObj.GetCoordCartesian"));
            Assert.Equal(2, host.Operations.Count(item => item == "Results.FrameForce"));
            Assert.Equal(2, host.Operations.Count(item => item == "FrameObj.GetAllFrames"));
            Assert.DoesNotContain(host.Operations, item => item.Contains("Set", StringComparison.Ordinal) && !item.StartsWith("Results.Setup.", StringComparison.Ordinal));
            Assert.Equal(snapshot.RawCapture.ModelRecords.Count + snapshot.RawCapture.ForceRows.Count, snapshot.RowLedger.AcceptedCount);
            var output = Environment.GetEnvironmentVariable("WP10_BATCH_SYNTHETIC_OUTPUT");
            if (!string.IsNullOrWhiteSpace(output)) File.WriteAllBytes(mesh ? output + ".mesh.json" : output, AnalysisSnapshotCodec.CanonicalJsonBytes(snapshot));
        }
        finally { Directory.Delete(directory, true); }
    }

    [Theory]
    [InlineData("dynamic")]
    [InlineData("initial-case")]
    [InlineData("envelope")]
    [InlineData("automatic")]
    [InlineData("stale-context")]
    public void UnsupportedOrStaleSourceStopsBeforeForces(string fault)
    {
        using var host = new BatchHost(fault);
        var context = fault == "stale-context" ? host.Context with { Source = host.Context.Source with { ModelSha256 = new('9', 64) } } : host.Context;
        var error = Assert.Throws<EtabsLiveGetterProbeException>(() => EtabsLiveGetterProbe.RunBatch(host,
            new("request", context, ["beam", "beam2"], DateTimeOffset.UtcNow.AddSeconds(10)), TestContext.Current.CancellationToken));
        Assert.Contains("ETABS.", error.Message, StringComparison.Ordinal);
        Assert.DoesNotContain("Results.FrameForce", host.Operations);
    }

    [Fact]
    public async Task TimedOutBatchKeepsContextLeaseUntilActualQuiescence()
    {
        var directory = Path.Combine(Path.GetTempPath(), "wp10-batch-timeout-" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(directory);
        using var entered = new ManualResetEventSlim(); using var release = new ManualResetEventSlim();
        try
        {
            var host = new BatchHost();
            var handle = new EtabsBatchOperationBroker().Start(new("timeout", 94101, DateTimeOffset.UtcNow.AddMilliseconds(250), Path.Combine(directory, "batch.json")),
                () => host, (_, _) => { entered.Set(); release.Wait(); throw new OperationCanceledException(); }, TestContext.Current.CancellationToken);
            Assert.True(entered.Wait(TimeSpan.FromSeconds(5), TestContext.Current.CancellationToken));
            Assert.Equal(EtabsContextWorkerState.TransactionUncertain, (await handle.Completion).State);
            var competing = new EtabsContextOperationBroker().Start(new("context", 94101, DateTimeOffset.UtcNow.AddSeconds(5), Path.Combine(directory, "context.json")),
                () => throw new InvalidOperationException("must not attach"), (_, _) => throw new InvalidOperationException("must not acquire"), TestContext.Current.CancellationToken);
            Assert.Equal(EtabsContextWorkerState.LeaseUnavailable, (await competing.Completion).State);
            release.Set(); await handle.Quiescence;
            Assert.True(host.Disposed);
            Assert.False(File.Exists(Path.Combine(directory, "batch.json")));
        }
        finally { release.Set(); Directory.Delete(directory, true); }
    }

    private static string Sha(byte[] bytes) => Convert.ToHexStringLower(SHA256.HashData(bytes));

    // Two invented adjacent spans, distinct actions, one shared point/material/section.
    internal sealed class BatchHost(string? fault = null) : IEtabsGetterHost
    {
        private readonly EtabsLiveGetterProbeCapture _seed = Wp10SyntheticCapture.Create().Content.Capture;
        public EtabsHostIdentity Identity => _seed.HostIdentity with { ProcessId = 94101 };
        public bool Disposed { get; private set; }
        public List<string> Operations { get; } = [];
        public EtabsContextInventory Context => new("context-request", DateTimeOffset.UtcNow,
            new(Identity.ProcessId, Identity.ProcessStartedUtc, Identity.ExecutablePath, Identity.ExecutableSha256,
                Identity.ModelPath, Identity.ModelBytes, Identity.ModelModifiedUtc, Identity.ModelSha256, Identity.EtabsApiVersion, true, 6, 6),
            [new("pI", 1000, 2000, 3000), new("pJ", 1000, 6000, 3000), new("pK", 1000, 10000, 3000)],
            [new("beam", "section", "story", "pI", "pJ", EtabsFrameDesignOrientation.Beam), new("beam2", "section", "story", "pJ", "pK", EtabsFrameDesignOrientation.Beam)],
            [new("section", "material")], "synthetic source geometry");

        public EtabsInvocation Invoke(EtabsGetterDefinition definition, IReadOnlyList<object?> inputs, CancellationToken cancellationToken)
        {
            Operations.Add(definition.Operation);
            var operation = definition.Operation;
            var name = inputs.Count > 0 ? inputs[0] as string : null;
            if (operation == "FrameObj.GetAllFrames") return new(0,
                [2, new[] { "beam", "beam2" }, new[] { "section", "section" }, new[] { "story", "story" }, new[] { "pI", "pJ" }, new[] { "pJ", "pK" },
                    new[] { 1d, 1d }, new[] { 2d, 6d }, new[] { 3d, 3d }, new[] { 1d, 1d }, new[] { 6d, 10d }, new[] { 3d, 3d },
                    new double[2], new double[2], new double[2], new double[2], new double[2], new double[2], new double[2], new[] { 8, 8 }]);
            if (operation == "PointObj.GetAllPoints") return new(0, [3, new[] { "pI", "pJ", "pK" }, new[] { 1d, 1d, 1d }, new[] { 2d, 6d, 10d }, new[] { 3d, 3d, 3d }]);
            if (operation == "FrameObj.GetNameList") return new(0, [2, new[] { "beam", "beam2" }]);
            if (operation == "FrameObj.GetDesignOrientation") return new(0, [2]);
            if (operation == "PropMaterial.GetTypeOAPI") return new(0, [2, 0]);
            if (operation == "PointObj.GetCoordCartesian") return new(0, [1d, name == "pI" ? 2d : name == "pJ" ? 6d : 10d, 3d]);
            if (operation == "PointObj.GetLabelFromName") return new(0, [name, "story"]);
            if (fault == "dynamic" && operation == "LoadCases.GetTypeOAPI") return new(0, [4, 0]);
            if (fault == "dynamic" && operation == "LoadCases.GetTypeOAPI_1") return new(0, [4, 0, 1, 0, 0]);
            if (fault == "automatic" && operation == "LoadCases.GetTypeOAPI_1") return new(0, [1, 0, 8, 0, 5]);
            if (fault == "initial-case" && operation == "LoadCases.StaticLinear.GetInitialCase") return new(0, ["prior"]);
            if (fault == "envelope" && operation == "RespCombo.GetTypeOAPI") return new(0, [1]);
            if (fault == "mesh")
            {
                if (operation == "PointElm.GetCoordCartesian" && name == "mesh-point") return new(0, [1d, 4d, 3d]);
                if (operation == "LineElm.GetObj" && name is "element" or "element-mid") return new(0, ["beam", 0, name == "element" ? 0d : 0.5, name == "element" ? 0.5 : 1d]);
                if (operation == "LineElm.GetPoints" && name is "element" or "element-mid") return new(0, name == "element" ? ["pI", "mesh-point"] : ["mesh-point", "pJ"]);
            }
            var original = _seed.Calls.First(call => call.Operation == operation);
            var second = name is "beam2" or "element2";
            object? Map(object? value) => value switch
            {
                string text when second => text switch { "beam" => "beam2", "element" => "element2", "pI" => "pJ", "pJ" => "pK", _ => text },
                string[] values => values.Select(value => (string)Map(value)!).ToArray(),
                double[] values when second && operation == "Results.FrameForce" => values.ToArray(),
                _ => value
            };
            var outputs = original.Outputs.Select(Map).ToArray();
            if (fault == "mesh" && operation == "Results.FrameForce" && name == "beam")
            {
                outputs[3] = new[] { "element", "element-mid", "element-mid" };
                outputs[4] = new[] { 0.2, 0d, 1.7 };
            }
            if (second && operation == "Results.FrameForce")
                for (var column = 8; column < 14; column++) outputs[column] = ((double[])outputs[column]!).Select(value => value * 2).ToArray();
            return new(original.CsiReturnCode is null ? original.DirectValue : 0, outputs);
        }
        public void Dispose() => Disposed = true;
    }
}
