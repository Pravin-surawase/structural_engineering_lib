using StructuralEngineering.Analysis;
using StructuralEngineering.Beam;
using StructuralEngineering.Contracts;
namespace StructuralEngineering.ExcelDna;

public sealed class BaselineDesignWork : IDisposable
{
    private readonly CancellationTokenSource _cts; private int _disposed; private int _cancelled; public string RequestId { get; }
    public BaselineReplayRequest Request { get; }
    public Task<BaselineBatchDesignResult> Completion { get; }
    private BaselineDesignWork(string id, BaselineReplayRequest request, CancellationTokenSource cts, Task<BaselineBatchDesignResult> completion) { RequestId = id; Request = request; _cts = cts; Completion = completion; _ = Completion.ContinueWith(_ => _cts.Dispose(), CancellationToken.None, TaskContinuationOptions.ExecuteSynchronously, TaskScheduler.Default); }
    public static BaselineDesignWork Start(AnalysisSnapshot snapshot, BaselineProjectInputs inputs, IReadOnlyList<string> memberIds, BaselineDesignOptions? options = null, IProgress<(int Completed, int Total, string MemberId)>? progress = null)
    {
        ArgumentNullException.ThrowIfNull(snapshot); ArgumentNullException.ThrowIfNull(inputs); ArgumentNullException.ThrowIfNull(memberIds);
        var frozen = BaselineReplay.Parse(BaselineReplay.Serialize(BaselineReplay.Request(snapshot, inputs, memberIds, options)));
        var cts = new CancellationTokenSource();
        var task = Task.Run(() =>
        {
            cts.Token.ThrowIfCancellationRequested();
            // The host owns the captured snapshot. Verify and detach its heavy evidence on the worker thread.
            using var transport = new MemoryStream();
            AnalysisSnapshotTransport.WriteCompact(transport, snapshot); transport.Position = 0;
            var frozenSnapshot = AnalysisSnapshotTransport.Read(transport).Snapshot ?? throw new InvalidDataException("Snapshot cannot be frozen for design dispatch.");
            if (frozenSnapshot.SnapshotSha256 != frozen.SnapshotSha256 || frozenSnapshot.SnapshotId != frozen.SnapshotId)
                throw new InvalidDataException("Snapshot changed before design dispatch.");
            cts.Token.ThrowIfCancellationRequested();
            return BaselineDesignOperations.Design(frozenSnapshot, frozen.AcceptedInputs, frozen.MemberIds, frozen.Options, cts.Token, progress);
        }, CancellationToken.None);
        return new(Guid.NewGuid().ToString("N"), frozen, cts, task);
    }
    public void Cancel() { if (Interlocked.Exchange(ref _cancelled, 1) == 0 && !Completion.IsCompleted) try { _cts.Cancel(); } catch (ObjectDisposedException) { } }
    public void Dispose() { if (Interlocked.Exchange(ref _disposed, 1) == 0) Cancel(); }
}
