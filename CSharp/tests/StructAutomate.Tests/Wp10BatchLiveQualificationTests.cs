using System.Security.Cryptography;
using System.Text.Json;
using StructuralEngineering.Analysis;
using StructuralEngineering.Contracts;
using StructuralEngineering.Etabs;
using Xunit;

namespace StructAutomate.Tests;

public sealed class Wp10BatchLiveQualificationTests
{
    [Fact]
    public void RetainedBatchMeasuresCompleteOfflineNormalization()
    {
        var path = Environment.GetEnvironmentVariable("WP10_BATCH_REPLAY_ARTIFACT");
        var expected = Environment.GetEnvironmentVariable("WP10_BATCH_REPLAY_SHA256");
        var output = Environment.GetEnvironmentVariable("WP10_BATCH_REPLAY_DIRECTORY");
        Assert.SkipWhen(string.IsNullOrWhiteSpace(path) || string.IsNullOrWhiteSpace(expected) || string.IsNullOrWhiteSpace(output),
            "Requires an exact retained batch and a new external replay directory.");
        Assert.False(Directory.Exists(output)); Directory.CreateDirectory(output!);
        var bytes = File.ReadAllBytes(path!); Assert.Equal(expected, Sha(bytes));
        var allocated = GC.GetAllocatedBytesForCurrentThread();
        var watch = System.Diagnostics.Stopwatch.StartNew();
        var result = EtabsCaptureProjector.Normalize(bytes, expected!, new("retained-batch-development", "wp10-shared-capture/v1", path!,
            new Dictionary<string, SnapshotMaterialClassification>()));
        Assert.True(result.Snapshot is not null, string.Join("; ", result.Diagnostics.Select(item => item.Message)));
        var normalizeMilliseconds = watch.Elapsed.TotalMilliseconds;
        watch.Restart();
        var snapshotPath = Path.Combine(output!, "snapshot.json");
        using (var stream = new FileStream(snapshotPath, FileMode.CreateNew, FileAccess.Write))
            AnalysisSnapshotCodec.WriteCanonicalJson(stream, result.Snapshot!);
        watch.Stop();
        allocated = GC.GetAllocatedBytesForCurrentThread() - allocated;
        File.WriteAllBytes(Path.Combine(output!, "receipt.json"), AnalysisSnapshotCodec.CanonicalJsonBytes(new
        {
            schema_version = "wp10-retained-batch-normalization-development/v1",
            pf9_acceptance = false,
            source_sha256 = expected,
            members = result.Snapshot!.Members.Count,
            rows = result.Snapshot.ActionRows.Count,
            normalize_ms = normalizeMilliseconds,
            persist_ms = watch.Elapsed.TotalMilliseconds,
            allocated_bytes = allocated,
            snapshot_bytes = new FileInfo(snapshotPath).Length,
            peak_process_working_set_bytes = System.Diagnostics.Process.GetCurrentProcess().PeakWorkingSet64,
            source_unchanged = Sha(File.ReadAllBytes(path!)) == expected,
            engineering_state = "not_evaluated"
        }));
    }

    [Fact]
    public async Task ExactOwnedProcessProducesContextAndForceEvidence()
    {
        var targetPath = Environment.GetEnvironmentVariable("WP10_BATCH_TARGET_PATH");
        var directory = Environment.GetEnvironmentVariable("WP10_BATCH_EVIDENCE_DIRECTORY");
        Assert.SkipWhen(string.IsNullOrWhiteSpace(targetPath) || string.IsNullOrWhiteSpace(directory), "Requires explicit external process identity and a new qualification directory.");
        Assert.False(Directory.Exists(directory));
        Directory.CreateDirectory(directory!);
        var target = JsonSerializer.Deserialize<EtabsProcessTarget>(File.ReadAllBytes(targetPath!))!;
        var requestSha = Sha(File.ReadAllBytes(targetPath!));
        var deadline = DateTimeOffset.UtcNow.AddMinutes(8);
        var contextHandle = new EtabsContextOperationBroker().Start(new("live-context", target.ProcessId, deadline, Path.Combine(directory!, "context.json")),
            () => EtabsReflectionGetterHost.AttachContext(EtabsHostDiscovery.Discover(target)),
            (host, token) => EtabsContextCapture.Run(host, new(requestSha, deadline), token), TestContext.Current.CancellationToken);
        var contextResult = await contextHandle.Completion;
        await contextHandle.Quiescence;
        Assert.True(contextResult.State == EtabsContextWorkerState.Completed, contextResult.Message);
        var context = contextResult.Artifact!.Inventory;
        var explicitMembers = Environment.GetEnvironmentVariable("WP10_BATCH_MEMBER_IDS");
        var members = string.IsNullOrWhiteSpace(explicitMembers)
            ? context.Frames.Where(frame => frame.DesignOrientation == EtabsFrameDesignOrientation.Beam).Select(frame => frame.SourceFrameId).ToArray()
            : explicitMembers.Split(',', StringSplitOptions.TrimEntries | StringSplitOptions.RemoveEmptyEntries);
        var watch = System.Diagnostics.Stopwatch.StartNew();
        var profile = Environment.GetEnvironmentVariable("WP10_BATCH_PROFILE") ?? "batch";
        Assert.True(profile is "batch" or "bulk" or "group", "WP10_BATCH_PROFILE must be batch, bulk or group.");
        var batchHandle = new EtabsBatchOperationBroker().Start(new("live-forces", target.ProcessId, deadline, Path.Combine(directory!, "forces.json")),
            () => profile == "group" ? EtabsReflectionGetterHost.AttachGroup(EtabsHostDiscovery.Discover(target))
                : profile == "bulk" ? EtabsReflectionGetterHost.AttachBulk(EtabsHostDiscovery.Discover(target)) : EtabsReflectionGetterHost.AttachForces(EtabsHostDiscovery.Discover(target)),
            (host, token) => profile == "group" ? EtabsLiveGetterProbe.RunGroup(host, new(requestSha, context, members, deadline), token)
                : profile == "bulk" ? EtabsLiveGetterProbe.RunBulk(host, new(requestSha, context, members, deadline), token) : EtabsLiveGetterProbe.RunBatch(host, new(requestSha, context, members, deadline), token),
            TestContext.Current.CancellationToken, profile == "group" ? EtabsGroupGetterMatrix.Sha256 : profile == "bulk" ? EtabsBulkGetterMatrix.Sha256 : null);
        var batchResult = await batchHandle.Completion;
        await batchHandle.Quiescence;
        watch.Stop();
        EtabsSnapshotResult? normalized = null;
        if (batchResult.Artifact is not null)
        {
            var bytes = File.ReadAllBytes(batchResult.EvidencePath);
            normalized = EtabsCaptureProjector.Normalize(batchResult.Artifact, bytes, Sha(bytes), new("live-qualification", "wp10-shared-capture/v1", batchResult.EvidencePath,
                new Dictionary<string, SnapshotMaterialClassification>()));
            if (normalized.Snapshot is not null)
            {
                using (var snapshotOutput = File.Create(Path.Combine(directory!, "snapshot.json")))
                    AnalysisSnapshotCodec.WriteCanonicalJson(snapshotOutput, normalized.Snapshot);
                var interpretation = EtabsModelInterpreter.Interpret(new(contextResult.Artifact!, normalized.Snapshot, members));
                Assert.Equal(members.Length, interpretation.Beams.Count);
                Assert.Equal(context.Frames.Count, interpretation.Frames.Count);
                File.WriteAllBytes(Path.Combine(directory!, "interpretation.json"), AnalysisSnapshotCodec.CanonicalJsonBytes(interpretation));
            }
        }
        File.WriteAllBytes(Path.Combine(directory!, "receipt.json"), AnalysisSnapshotCodec.CanonicalJsonBytes(new
        {
            schema_version = "wp10-batch-development-qualification/v1",
            installed_acceptance = false,
            capture_completed = batchResult.State == EtabsContextWorkerState.Completed,
            normalized = normalized?.Snapshot is not null,
            required_members = members.Length,
            source_frames = context.Frames.Count,
            source_points = context.Points.Count,
            captured_members = batchResult.Artifact?.Content.Capture.Members.Count,
            profile = batchResult.Artifact?.Content.Capture.ProfileId,
            action_rows = normalized?.Snapshot?.ActionRows.Count,
            elapsed_ms = watch.Elapsed.TotalMilliseconds,
            batchResult.State,
            batchResult.DiagnosticCode,
            batchResult.Message,
            batchResult.CleanupCompleted,
            diagnostics = normalized?.Diagnostics,
            engineering_state = "not_evaluated"
        }));
        var rejection = Environment.GetEnvironmentVariable("WP10_BATCH_EXPECTED_REJECTION");
        if (!string.IsNullOrWhiteSpace(rejection))
        {
            Assert.Null(batchResult.Artifact);
            Assert.Contains(rejection, batchResult.Message ?? "", StringComparison.Ordinal);
        }
        else
        {
            Assert.True(batchResult.State == EtabsContextWorkerState.Completed, batchResult.Message);
            Assert.True(normalized?.Snapshot is not null, string.Join("; ", normalized?.Diagnostics.Select(item => item.Message) ?? []));
        }
    }

    private static string Sha(byte[] bytes) => Convert.ToHexStringLower(SHA256.HashData(bytes));
}
