using System.Security.Cryptography;
using System.Text.Json;
using StructuralEngineering.Analysis;
using StructuralEngineering.Contracts;
using StructuralEngineering.ExcelDna;
using Xunit;

namespace StructAutomate.Tests;

public sealed class Wp10ForceWorkerTests
{
    [Fact]
    public void RetainedForceSnapshotReplaysWithIdenticalStreamedBytes()
    {
        var path = Environment.GetEnvironmentVariable("WP10_FORCE_REPLAY_SNAPSHOT");
        var output = Environment.GetEnvironmentVariable("WP10_FORCE_REPLAY_RECEIPT");
        Assert.SkipWhen(string.IsNullOrWhiteSpace(path) || string.IsNullOrWhiteSpace(output), "Requires retained force snapshot and a new external performance receipt.");
        Assert.False(File.Exists(output));
        var bytes = File.ReadAllBytes(path!);
        var result = AnalysisSnapshotCodec.ParseAndValidate(System.Text.Encoding.UTF8.GetString(bytes));
        Assert.True(result.Snapshot is not null, string.Join("; ", result.Diagnostics.Select(item => item.Message)));
        var allocated = GC.GetAllocatedBytesForCurrentThread();
        var watch = System.Diagnostics.Stopwatch.StartNew();
        using var streamed = new MemoryStream();
        AnalysisSnapshotCodec.WriteCanonicalJson(streamed, result.Snapshot!);
        watch.Stop();
        allocated = GC.GetAllocatedBytesForCurrentThread() - allocated;
        Assert.Equal(bytes, streamed.ToArray());
        using var receipt = new FileStream(output!, FileMode.CreateNew, FileAccess.Write);
        JsonSerializer.Serialize(receipt, new
        {
            schema_version = "wp10-streamed-replay-development/v1",
            pf9_acceptance = false,
            byte_identity_preserved = true,
            bytes = bytes.Length,
            members = result.Snapshot!.Members.Count,
            rows = result.Snapshot.ActionRows.Count,
            elapsed_ms = watch.Elapsed.TotalMilliseconds,
            allocated_bytes = allocated
        });
    }

    [Fact]
    public void RetainedCompressedSnapshotPreservesFullCanonicalEvidence()
    {
        var path = Environment.GetEnvironmentVariable("WP10_TRANSPORT_REPLAY_FILE");
        var expected = Environment.GetEnvironmentVariable("WP10_TRANSPORT_CANONICAL_SHA256");
        var output = Environment.GetEnvironmentVariable("WP10_TRANSPORT_RECEIPT");
        Assert.SkipWhen(string.IsNullOrWhiteSpace(path) || string.IsNullOrWhiteSpace(expected) || string.IsNullOrWhiteSpace(output),
            "Requires retained transport, frozen canonical digest and a new external receipt.");
        Assert.False(File.Exists(output));
        var watch = System.Diagnostics.Stopwatch.StartNew();
        using var input = File.OpenRead(path!);
        var result = AnalysisSnapshotTransport.Read(input);
        Assert.True(result.Snapshot is not null, string.Join("; ", result.Diagnostics.Select(item => item.Message)));
        var readMilliseconds = watch.Elapsed.TotalMilliseconds;
        using var hash = SHA256.Create();
        using (var sink = new CryptoStream(Stream.Null, hash, CryptoStreamMode.Write))
            AnalysisSnapshotCodec.WriteCanonicalJson(sink, result.Snapshot!);
        Assert.Equal(expected, Convert.ToHexStringLower(hash.Hash!));
        using var receipt = new FileStream(output!, FileMode.CreateNew, FileAccess.Write);
        JsonSerializer.Serialize(receipt, new
        {
            schema_version = "wp10-transport-replay-development/v1",
            pf9_acceptance = false,
            canonical_sha256 = expected,
            encoded_bytes = input.Length,
            read_validate_ms = readMilliseconds,
            members = result.Snapshot!.Members.Count,
            rows = result.Snapshot.ActionRows.Count,
            peak_process_working_set_bytes = System.Diagnostics.Process.GetCurrentProcess().PeakWorkingSet64
        });
    }

    [Fact]
    public void RequestBindsModelContextScopeAndCallerAdmission()
    {
        var request = Request();
        var bytes = EtabsForceWorkerCodec.CanonicalRequestJsonBytes(request);
        Assert.Equal(bytes, EtabsForceWorkerCodec.CanonicalRequestJsonBytes(EtabsForceWorkerCodec.ParseRequest(bytes)));
        var original = EtabsForceWorkerCodec.RequestSha256(request);
        foreach (var changed in new[]
        {
            request with { ContextArtifactSha256 = new('c', 64) },
            request with { MemberObjectNames = ["104"] },
            request with { ProjectId = "another-workbook" },
            request with { AdmissionLimits = new(1024, 2, 2) }
        }) Assert.NotEqual(original, EtabsForceWorkerCodec.RequestSha256(changed));
        Assert.Throws<InvalidDataException>(() => EtabsForceWorkerCodec.CanonicalRequestJsonBytes(request with { MemberObjectNames = [] }));
        Assert.Throws<InvalidDataException>(() => EtabsForceWorkerCodec.CanonicalRequestJsonBytes(request with { MemberObjectNames = ["100", "100"] }));
        Assert.Throws<InvalidDataException>(() => EtabsForceWorkerCodec.CanonicalRequestJsonBytes(request with { AdmissionLimits = new(1024, 2, 1) }));
        var medium = request with { AdmissionLimits = new(64 * 1024 * 1024, 100_000, 1000, EtabsForceWorkerCodec.RowsSnapshotTransport) };
        Assert.Equal(medium.AdmissionLimits, EtabsForceWorkerCodec.ParseRequest(EtabsForceWorkerCodec.CanonicalRequestJsonBytes(medium)).AdmissionLimits);
        Assert.Throws<InvalidDataException>(() => EtabsForceWorkerCodec.CanonicalRequestJsonBytes(medium with { AdmissionLimits = medium.AdmissionLimits with { MaximumBytes = 64 * 1024 * 1024 + 1 } }));
    }

    [Fact]
    public void CompletionNeedsQuiescedCleanupAndCannotCrossRequestBoundary()
    {
        var request = Request(); var sha = EtabsForceWorkerCodec.RequestSha256(request);
        var response = new EtabsForceWorkerResponse(request.RequestId, sha, EtabsContextWorkerState.Completed,
            null, null, "capture.json", new('c', 64), "snapshot.json", new('d', 64), "snapshot-id", new('e', 64), 2, 13, true, true);
        var bytes = EtabsForceWorkerCodec.CanonicalResponseJsonBytes(response);
        Assert.Equal(response, EtabsForceWorkerCodec.ParseAndValidateResponse(bytes, request.RequestId, sha));
        Assert.Throws<InvalidDataException>(() => EtabsForceWorkerCodec.ParseAndValidateResponse(bytes, "another", sha));
        Assert.Throws<InvalidDataException>(() => EtabsForceWorkerCodec.ParseAndValidateResponse(bytes, request.RequestId, new('0', 64)));
        Assert.Throws<InvalidDataException>(() => EtabsForceWorkerCodec.CanonicalResponseJsonBytes(response with { CleanupCompleted = false }));
        Assert.Throws<InvalidDataException>(() => EtabsForceWorkerCodec.CanonicalResponseJsonBytes(response with { Quiesced = false }));
        Assert.Throws<InvalidDataException>(() => EtabsForceWorkerCodec.CanonicalResponseJsonBytes(response with { State = EtabsContextWorkerState.Cancelled }));
    }

    [Fact]
    public void ProgressCannotBeAppliedToAnotherRequest()
    {
        var request = Request(); var sha = EtabsForceWorkerCodec.RequestSha256(request);
        var progress = new EtabsForceProgress(request.RequestId, sha, EtabsForceStage.Capturing, 1, 2);
        var bytes = EtabsForceWorkerCodec.CanonicalProgressJsonBytes(progress);
        Assert.Equal(progress, EtabsForceWorkerCodec.ParseProgress(bytes, request.RequestId, sha));
        Assert.Throws<InvalidDataException>(() => EtabsForceWorkerCodec.ParseProgress(bytes, "another", sha));
        Assert.Throws<InvalidDataException>(() => EtabsForceWorkerCodec.CanonicalProgressJsonBytes(progress with { CompletedMembers = 3 }));
    }

    [Fact]
    public async Task RealWorkerConnectsCapturesAndCancelsWithoutAcceptedPartialData()
    {
        var targetPath = Environment.GetEnvironmentVariable("WP10_FORCE_TARGET_PATH");
        var package = Environment.GetEnvironmentVariable("WP10_FORCE_PACKAGE");
        var directory = Environment.GetEnvironmentVariable("WP10_FORCE_EVIDENCE_DIRECTORY");
        Assert.SkipWhen(string.IsNullOrWhiteSpace(targetPath) || string.IsNullOrWhiteSpace(package) || string.IsNullOrWhiteSpace(directory),
            "Requires an explicit owned ETABS target, worker package and new external evidence directory.");
        Assert.False(Directory.Exists(directory)); Directory.CreateDirectory(directory!);
        var target = JsonSerializer.Deserialize<EtabsProcessTarget>(File.ReadAllBytes(targetPath!))!;
        var token = TestContext.Current.CancellationToken;
        var result = await EtabsConnectionClient.ConnectAsync(package!, directory!,
            new(target.ProcessId, target.ProcessStartedUtc, target.ExecutablePath, "owned qualification"), "context", token);
        Assert.True(result.Artifact is not null, result.Response.Message);
        var context = new EtabsConnectionSession(result.Artifact!, result.OperationDirectory);
        var scope = Environment.GetEnvironmentVariable("WP10_FORCE_MEMBER_IDS") ?? "104";
        var members = scope == "all" ? context.Frames.Values.Where(frame => frame.DesignOrientation == EtabsFrameDesignOrientation.Beam)
            .Select(frame => frame.SourceFrameId).Order(StringComparer.Ordinal).ToArray() : scope.Split(',', StringSplitOptions.TrimEntries);
        var loaded = await EtabsConnectionClient.GetForcesAsync(package!, directory!, Path.Combine(directory!, "store"),
            context, "worker-qualification", "forces", token, memberObjectNames: members);
        Assert.True(loaded.Session is not null, loaded.Response.Message);
        Assert.Equal(members.Order(StringComparer.Ordinal), loaded.Session!.Snapshot.Members.Select(member => member.ObjectId).Order(StringComparer.Ordinal));
        var reference = loaded.Session.Reference;
        var reopened = new OfflineSnapshotStore(Path.Combine(directory!, "store")).Read(reference);
        Assert.Equal(loaded.Session.Snapshot.SnapshotSha256, reopened.SnapshotSha256);
        Assert.Equal(loaded.Session.Snapshot.ActionRows.Count, reopened.ActionRows.Count);
        Assert.Equal(AnalysisSnapshotTransport.CompactSchemaVersion, reference.TransportSchemaVersion);
        var artifact = Path.Combine(directory!, "forces", "snapshot.sasnap");
        var before = SHA256.HashData(File.ReadAllBytes(artifact));
        using var cancellation = new CancellationTokenSource();
        var pending = EtabsConnectionClient.GetForcesAsync(package!, directory!, Path.Combine(directory!, "store"),
            context, "worker-qualification", "cancelled", cancellation.Token, memberObjectNames: members);
        cancellation.CancelAfter(TimeSpan.FromMilliseconds(500));
        var cancelled = await pending;
        Assert.Null(cancelled.Session);
        Assert.NotEqual(EtabsContextWorkerState.Completed, cancelled.Response.State);
        var deadline = DateTimeOffset.UtcNow.AddSeconds(30);
        while (EtabsConnectionClient.ActiveWorkerCount != 0 && DateTimeOffset.UtcNow < deadline) await Task.Delay(100, token);
        Assert.Equal(0, EtabsConnectionClient.ActiveWorkerCount);
        Assert.Equal(before, SHA256.HashData(File.ReadAllBytes(artifact)));
        Assert.Equal(reference, loaded.Session.Reference);
        File.WriteAllBytes(Path.Combine(directory!, "receipt.json"), JsonSerializer.SerializeToUtf8Bytes(new
        {
            schema_version = "wp10-force-worker-development/v1",
            installed_acceptance = false,
            passed = true,
            target.ProcessId,
            loaded.Response,
            cancelled = cancelled.Response,
            cleanup_completed = true,
            offline_reopen_exact = true,
            engineering_state = "not_evaluated"
        }));
    }

    private static EtabsForceWorkerRequest Request() => new("force-request",
        new(123, DateTimeOffset.Parse("2026-09-07T00:00:00Z"), "ETABS.exe", new('a', 64)),
        DateTimeOffset.Parse("2026-09-07T00:08:00Z"), "context.json", new('b', 64), "project", ["100", "104"],
        "capture.json", "snapshot.json", new(16 * 1024 * 1024, 10_000, 1000));
}
