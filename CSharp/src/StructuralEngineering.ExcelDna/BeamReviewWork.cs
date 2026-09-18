using System.Text.Json;
using StructuralEngineering.Analysis;
using StructuralEngineering.Beam;
using StructuralEngineering.Contracts;

namespace StructuralEngineering.ExcelDna;

public sealed class BeamReviewWork : IDisposable
{
    private readonly CancellationTokenSource _cts = new();
    public string DispatchId { get; } = Guid.NewGuid().ToString("N");
    public Task<BeamReviewResult> Completion { get; }
    private BeamReviewWork(AnalysisSnapshot? snapshot, BeamResolvedReview resolved, BeamReviewResult? previous, string? failureMember)
    {
        var frozen = JsonSerializer.Deserialize<BeamResolvedReview>(JsonSerializer.Serialize(resolved, WorkbookContract.Json), WorkbookContract.Json)!;
        Completion = Task.Run(() =>
        {
            AnalysisSnapshot? detached = null;
            if (snapshot is not null)
            {
                using var transport = new MemoryStream();
                AnalysisSnapshotTransport.WriteCompact(transport, snapshot); transport.Position = 0;
                detached = AnalysisSnapshotTransport.Read(transport).Snapshot ?? throw new InvalidDataException("Snapshot freeze failed.");
                if (detached.SnapshotSha256 != frozen.Ledger.SnapshotSha256) throw new InvalidDataException("Review source revision differs.");
            }
            using var exampleStream = typeof(BeamReviewWork).Assembly.GetManifestResourceStream("StructAutomate.ReviewExample.sasnap")!;
            var exampleSnapshot = AnalysisSnapshotTransport.Read(exampleStream).Snapshot ?? throw new InvalidDataException("Named example is unavailable.");
            return BeamReviewOperations.Review(detached, frozen, BeamReviewExamples.Owned(exampleSnapshot), previous, _cts.Token,
                coreEvaluator: failureMember is null ? null : (s, member, token) => member.MemberId == failureMember
                    ? throw new InvalidOperationException("Acceptance-injected member calculation failure") : BaselineDesignOperations.PreviewCore(s, member, token),
                allowCostExample: true);
        });
        _ = Completion.ContinueWith(_ => _cts.Dispose(), CancellationToken.None, TaskContinuationOptions.ExecuteSynchronously, TaskScheduler.Default);
    }
    public static BeamReviewWork Start(AnalysisSnapshot? snapshot, BeamResolvedReview resolved, BeamReviewResult? previous = null, string? failureMember = null) => new(snapshot, resolved, previous, failureMember);
    public void Cancel() { if (!Completion.IsCompleted) try { _cts.Cancel(); } catch (ObjectDisposedException) { } }
    public void Dispose() => Cancel();
}
