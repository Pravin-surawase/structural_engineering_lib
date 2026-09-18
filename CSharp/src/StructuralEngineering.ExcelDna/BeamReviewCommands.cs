using System.Text.Json;
using ExcelDna.Integration;
using StructuralEngineering.Analysis;
using StructuralEngineering.Beam;
using StructuralEngineering.Contracts;

namespace StructuralEngineering.ExcelDna;

public static partial class OfflineCommands
{
    private static readonly Dictionary<string, Task<BeamReviewResult>> ReviewDispatches = [];
    private static readonly System.Collections.Concurrent.ConcurrentDictionary<string, string> ReviewDispatchPhases = new();
    private static readonly HashSet<System.Windows.Forms.Timer> ReviewTimers = [];

    private static void QueueReviewMacro(Action action) => ExcelAsyncUtil.QueueAsMacro(() =>
    {
        if (!_busy) { action(); return; }
        // Excel can pump an async macro during another command's COM call. Defer the whole callback;
        // never consume/discard a completed dispatch merely because the workbook transaction owns the host.
        var timer = new System.Windows.Forms.Timer { Interval = 50 };
        ReviewTimers.Add(timer);
        timer.Tick += (_, _) => { timer.Stop(); ReviewTimers.Remove(timer); timer.Dispose(); QueueReviewMacro(action); };
        timer.Start();
    });

    [ExcelCommand(Name = "STR_XL_PROVISIONAL_REVIEW", Description = "Resolve persistent assumptions and review every selected member without an acceptance prerequisite.")]
    public static string ProvisionalReview() => ReviewFor(null);

    private static string ReviewFor(long? key) => Run((app, workbook, store, entry) => StartReview(workbook, store, entry), key);

    private static string StartReview(object workbook, OfflineWorkbookStore store, Entry entry, string? failureMember = null)
    {
        var state = store.ReadState() ?? store.CreateAssumptions();
        if (entry.DesignWork is not null || entry.ForceRequestId is not null || entry.ConnectionRequestId is not null)
            return Result("deferred", "A requested design or model read is still running; review its completed evidence next.");
        CancelEntryReview(entry);
        AnalysisSnapshot? snapshot = null;
        try
        {
            if (state.SnapshotReference is { } source && state.StoreDirectory is { } root && File.Exists(new OfflineSnapshotStore(root).GetArtifactPath(source)))
                snapshot = LoadSession(state, entry).Snapshot;
        }
        catch (IOException) { entry.Session = null; }
        catch (InvalidDataException) { entry.Session = null; }
        var saved = OfflineWorkbookStore.ReadResolved(state);
        BeamResolvedReview resolved;
        string? sheetValues = null;
        if (snapshot is not null)
        {
            var captured = store.CaptureReviewEdits(state, snapshot);
            resolved = BeamReviewResolver.Resolve(snapshot, store.SelectedReviewMembers(state, snapshot), BeamReviewInputProjection.Preset(), saved?.Ledger, captured.Edits);
            sheetValues = captured.SheetValuesJson;
        }
        else if (saved is not null) resolved = saved;
        else
        {
            using var stream = typeof(BeamReviewWork).Assembly.GetManifestResourceStream("StructAutomate.ReviewExample.sasnap")!;
            var example = AnalysisSnapshotTransport.Read(stream).Snapshot ?? throw new InvalidDataException("Named example is unavailable.");
            var captured = store.CaptureReviewEdits(state, example);
            resolved = BeamReviewResolver.Resolve(example, [example.Members[0].MemberId], BeamReviewInputProjection.Preset(), edits: captured.Edits);
            sheetValues = captured.SheetValuesJson;
        }
        state = saved?.Ledger.Revision == resolved.Ledger.Revision
            ? store.MarkReviewPending(state)
            : store.WriteReviewInputs(state, resolved, sheetValuesJson: sheetValues, snapshot: snapshot);
        BeamReviewResult? previous = null;
        if (state.Review?.Result is { } resultReference && state.Review.ResultDirectory is { } previousDirectory)
            try { previous = new BaselineDesignStore(previousDirectory).ReadReview(resultReference); }
            catch (IOException) { }
            catch (InvalidDataException) { }
        if (failureMember is not null && (snapshot?.SnapshotSha256 != BeamReviewExamples.OwnedSnapshotSha256 || !resolved.Members.Any(x => x.MemberId == failureMember)))
            throw new InvalidOperationException("Failure acceptance is restricted to a selected member of the exact owned WP11 fixture.");
        var work = BeamReviewWork.Start(snapshot, resolved, failureMember is null ? previous : null, failureMember);
        var owner = Key(workbook);
        var directory = Path.Combine(state.StoreDirectory ?? DefaultStoreDirectory(), "Reviews");
        var inputReference = new BaselineDesignStore(directory).SaveReviewInputs(resolved);
        store.CommitReviewState(state, state.Review! with { InputArtifact = inputReference, InputDirectory = directory });
        entry.ReviewWork = work;
        entry.ReviewDispatchCount++;
        foreach (var old in ReviewDispatches.Where(x => x.Value.IsCompleted).Take(Math.Max(0, ReviewDispatches.Count - 31)).Select(x => x.Key).ToArray())
        { ReviewDispatches.Remove(old); ReviewDispatchPhases.TryRemove(old, out _); }
        ReviewDispatches[work.DispatchId] = work.Completion; ReviewDispatchPhases[work.DispatchId] = "dispatched";
        entry.Window ??= new OfflineReviewWindow();
        entry.Window.SetPendingDesign(() => ExcelAsyncUtil.QueueAsMacro(() => CancelReviewFor(owner)));
        _ = ObserveReview(work, owner, entry, state.DocumentId, resolved.Ledger.Revision, directory);
        return Result("started", $"Reviewing {resolved.Members.Count} members using visible persistent assumptions.",
            new { request_id = work.DispatchId, input_revision = resolved.Ledger.Revision, selected_members = resolved.Members.Count });
    }

    private static async Task ObserveReview(BeamReviewWork work, long key, Entry expected, string documentId, string revision, string directory)
    {
        BeamReviewResult? result = null; BeamReviewArtifactReference? reference = null; Exception? failure = null;
        try
        {
            result = await work.Completion.ConfigureAwait(false);
            reference = await Task.Run(() => new BaselineDesignStore(directory).SaveReview(result)).ConfigureAwait(false);
        }
        catch (Exception error) { failure = error; }
        try
        {
            // Closing the last workbook prevents Excel from running queued macros. Cancellation
            // therefore records the terminal discard on the host immediately, before any callback.
            if (!ReviewDispatchPhases.TryUpdate(work.DispatchId, "completion queued", "dispatched"))
            { work.Dispose(); return; }
            QueueReviewMacro(() =>
            {
                if (!Entries.TryGetValue(key, out var entry) || !ReferenceEquals(entry, expected) || entry.ReviewWork?.DispatchId != work.DispatchId)
                { ReviewDispatchPhases[work.DispatchId] = "obsolete completion discarded"; work.Dispose(); return; }
                var outcome = Run((app, workbook, store, current) =>
                {
                    current.ReviewWork = null; work.Dispose(); current.Window?.EndPendingConnection();
                    ReviewDispatchPhases[work.DispatchId] = "reading workbook basis";
                    var state = RequireState(store);
                    if (state.DocumentId != documentId || state.Review?.Cancelled == true || OfflineWorkbookStore.ReadResolved(state)?.Ledger.Revision != revision)
                    { ReviewDispatchPhases[work.DispatchId] = "changed basis discarded"; return Result("stale", "Review completion discarded because its workbook or input basis changed."); }
                    if (failure is not null || result is null || reference is null)
                    { ReviewDispatchPhases[work.DispatchId] = "failed"; return Result("failed", failure?.Message ?? "Review produced no result."); }
                    ReviewDispatchPhases[work.DispatchId] = "writing review result";
                    store.WriteReviewResult(state, result, reference, directory);
                    ReviewDispatchPhases[work.DispatchId] = "committed";
                    return Result("completed", $"Provisional review complete for {result.Members.Count} members. Required checks, source gaps and examples remain visible.",
                        new { request_id = work.DispatchId, input_revision = result.Ledger.Revision, result_reference = reference, selected_members = result.Members.Count });
                }, key);
                if (ReviewDispatchPhases[work.DispatchId] != "committed") ReviewDispatchPhases[work.DispatchId] = "callback returned: " + outcome;
            });
        }
        catch (InvalidOperationException error) { ReviewDispatchPhases[work.DispatchId] = "queue unavailable: " + error.Message; work.Dispose(); }
    }

    private static void QueueReview(long key, Entry expected)
    {
        if (expected.ReviewQueued) return;
        expected.ReviewQueued = true;
        QueueReviewMacro(() =>
        {
            if (!Entries.TryGetValue(key, out var entry) || !ReferenceEquals(entry, expected) || !entry.ReviewQueued) return;
            entry.ReviewQueued = false;
            ReviewFor(key);
        });
    }

    private static void CancelEntryReview(Entry entry)
    {
        entry.ReviewQueued = false;
        var work = entry.ReviewWork; entry.ReviewWork = null;
        if (work is not null)
        {
            ReviewDispatchPhases[work.DispatchId] = "obsolete completion discarded";
            work.Cancel(); work.Dispose();
        }
    }

    [ExcelCommand(Name = "STR_XL_CANCEL_REVIEW", Description = "Cancel provisional review without automatically retrying.")]
    public static string CancelReview() => CancelReviewFor(null);
    private static string CancelReviewFor(long? key) => Run((app, workbook, store, entry) =>
    {
        CancelEntryReview(entry); entry.Window?.EndPendingConnection();
        var state = RequireState(store);
        if (state.Review is { } review) store.CommitReviewState(state, review with { Cancelled = true, Status = "Cancelled — new edit or explicit review required" });
        return Result("cancelled", "Provisional review cancelled. It will not retry automatically.");
    }, key);

    [ExcelCommand(Name = "STR_XL_REVIEW_STATE", Description = "Read persisted review provenance and effective typed inputs.")]
    public static string ReviewState()
    {
        if (_busy) return Result("busy", "Workbook transaction in progress.");
        dynamic? app = null; dynamic? workbook = null;
        try
        {
            app = TakeUniqueCom(ExcelDnaUtil.Application); workbook = TakeUniqueCom((object?)app?.ActiveWorkbook);
            if (workbook is null) return Result("unavailable", "No active workbook.");
            var store = new OfflineWorkbookStore(workbook); var state = RequireState(store);
            var entry = Entries.GetValueOrDefault(Key((object)workbook)); var resolved = OfflineWorkbookStore.ReadResolved(state);
            var input = state.Review?.InputArtifact; var result = state.Review?.Result;
            return Result(entry?.ReviewWork is null ? state.Review?.Cancelled == true ? "cancelled" : "idle" : "running", state.Review?.Status ?? "Review not yet run",
                new
                {
                    workbook = state.DocumentId,
                    input_revision = resolved?.Ledger.Revision,
                    input = input is null ? null : new { file_name = input.FileName, file_sha256 = input.FileSha256, ledger_revision = input.LedgerRevision },
                    input_directory = state.Review?.InputDirectory,
                    result = result is null ? null : new { file_name = result.FileName, file_sha256 = result.FileSha256, ledger_revision = result.LedgerRevision, request_id = result.RequestId },
                    directory = state.Review?.ResultDirectory,
                    dispatch_id = entry?.ReviewWork?.DispatchId,
                    dispatch_count = entry?.ReviewDispatchCount ?? 0
                });
        }
        finally { OfflineWorkbookStore.Release(workbook); OfflineWorkbookStore.Release(app); }
    }

    [ExcelCommand(Name = "STR_XL_TEST_REVIEW_DISPATCH", Description = "Acceptance: inspect actual review dispatch and ownership.")]
    public static string ReviewDispatchStatus(string dispatchId) => ReviewDispatches.TryGetValue(dispatchId, out var task)
        ? Result(task.IsCompleted ? "completed" : "running", ReviewDispatchPhases.GetValueOrDefault(dispatchId) ?? "unknown",
            new { completed = task.IsCompleted, phase = ReviewDispatchPhases.GetValueOrDefault(dispatchId), resident = Entries.Values.Any(x => x.ReviewWork?.DispatchId == dispatchId) })
        : Result("unknown", "Unknown review dispatch.");

    [ExcelCommand(Name = "STR_XL_TEST_REVIEW_MEMBER_FAILURE", Description = "Acceptance: fail one member of the exact owned WP11 fixture while its peers continue.")]
    public static string ReviewMemberFailure(string memberId) => Run((app, workbook, store, entry) => StartReview(workbook, store, entry, memberId));

    [ExcelCommand(Name = "STR_XL_TEST_REVIEW_MODEL_BINDING", Description = "Acceptance: exercise repeated IDs under a distinct model identity in the pure resolver; no capture or engineering claim.")]
    public static string ReviewModelBinding() => Run((app, workbook, store, entry) =>
    {
        var snapshot = LoadSession(RequireState(store), entry).Snapshot;
        if (snapshot.SnapshotSha256 != BeamReviewExamples.OwnedSnapshotSha256) throw new InvalidOperationException("Owned fixture required.");
        var id = snapshot.Members[0].MemberId;
        var edits = new[] { BeamReviewResolver.Edit("design.cover", BeamInputScope.Project, "project", null, "40", 1),
            BeamReviewResolver.Edit("design.fck", BeamInputScope.Member, id, BeamReviewResolver.ModelBinding(snapshot), "30", 2) };
        var original = BeamReviewResolver.Resolve(snapshot, [id], BeamReviewInputProjection.Preset(), edits: edits);
        var identityVariant = snapshot with { Metadata = snapshot.Metadata with { ModelName = "acceptance-only different identity" } };
        var other = BeamReviewResolver.Resolve(identityVariant, [id], BeamReviewInputProjection.Preset(), original.Ledger);
        return Result("completed", "Resolver-only identity exercise; the changed metadata is not a validated source snapshot.", new
        {
            same_member_id = original.Members[0].MemberId == other.Members[0].MemberId,
            different_model = original.Ledger.ModelBinding != other.Ledger.ModelBinding,
            original_fck = original.Members[0].Inputs.Materials[0].ConcreteStrengthNPerMm2,
            other_fck = other.Members[0].Inputs.Materials[0].ConcreteStrengthNPerMm2,
            retained_project_cover = other.Members[0].Inputs.MemberContexts[0].NominalCoverMm
        });
    });

    [ExcelCommand(Name = "STR_XL_TEST_REVIEW_RETAINED", Description = "Acceptance: retained 153-beam evidence keeps known nonzero actions unsupported.")]
    public static string ReviewRetained(string path)
    {
        const string expectedFileSha = "a6170c04cbeb45c7b7eca308ddec2b45a4e2248e345fe93f5a80b47d23f7b4ed";
        using var stream = File.OpenRead(path);
        var hash = Convert.ToHexStringLower(System.Security.Cryptography.SHA256.HashData(stream));
        if (hash != expectedFileSha) return Result("rejected", "This acceptance command requires the exact retained group-reference snapshot.");
        stream.Position = 0;
        var snapshot = JsonSerializer.Deserialize<AnalysisSnapshot>(stream, WorkbookContract.Json) ?? throw new InvalidDataException("Retained snapshot is missing.");
        const string member = "member:82";
        var source = snapshot.ActionRows.Where(x => x.MemberId == member).ToArray();
        var before = source.Select(x => (x.PKn, x.V2Kn, x.V3Kn, x.TKnm, x.M2Knm, x.M3Knm)).ToArray();
        var resolved = BeamReviewResolver.Resolve(snapshot, [member], BeamReviewInputProjection.Preset());
        var result = BaselineDesignOperations.PreviewCore(snapshot, resolved.Members[0]);
        return Result("completed", "Retained-source core admission only; no ETABS call or model mutation.", new
        {
            source_file_sha256 = hash,
            members = snapshot.Members.Count,
            member_id = member,
            maximum_axial_kn = source.Max(x => Math.Abs(x.PKn)),
            outcome = result.State.ToString(),
            diagnostics = result.Diagnostics.Select(x => x.Code).ToArray(),
            vectors_preserved = before.SequenceEqual(source.Select(x => (x.PKn, x.V2Kn, x.V3Kn, x.TKnm, x.M2Knm, x.M3Knm)))
        });
    }
}
