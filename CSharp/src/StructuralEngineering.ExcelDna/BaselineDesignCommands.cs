using System.Runtime.InteropServices;
using ExcelDna.Integration;
using StructuralEngineering.Beam;
using StructuralEngineering.Contracts;

namespace StructuralEngineering.ExcelDna;

public static partial class OfflineCommands
{
    private delegate void SheetChange(object sheet, object target);
    private delegate void WorkbookOpen(object workbook);
    private static readonly SheetChange ChangeHandler = OnSheetChange;
    private static readonly WorkbookOpen OpenHandler = OnWorkbookOpen;
    private static readonly Dictionary<string, Task<BaselineBatchDesignResult>> DesignDispatches = [];
    private static readonly System.Collections.Concurrent.ConcurrentDictionary<string, string> DesignDispatchPhases = new();

    [ExcelCommand(Name = "STR_XL_TEST_DESIGN_DISPATCH", Description = "Acceptance: inspect the actual dispatched task, including after workbook close/cancel.")]
    public static string DesignDispatchStatus(string requestId)
    {
        if (!DesignDispatches.TryGetValue(requestId, out var task)) return Result("unknown", "No matching dispatched design task.");
        return Result(task.IsCanceled ? "cancelled" : task.IsFaulted ? "failed" : task.IsCompleted ? "completed" : "running",
            "Actual design task state.", new
            {
                request_id = requestId,
                completed = task.IsCompleted,
                phase = DesignDispatchPhases.GetValueOrDefault(requestId),
                resident = Entries.Values.Any(x => x.DesignWork?.RequestId == requestId)
            });
    }

    internal static void InitializeEvents()
    {
        object? app = null;
        try { app = TakeUniqueCom(ExcelDnaUtil.Application); EnsureEvents(app!); }
        finally { OfflineWorkbookStore.Release(app); }
    }

    private static void EnsureEvents(object app)
    {
        if (_eventApplication is not null) return;
        var pointer = Marshal.GetIUnknownForObject(app);
        try { _eventApplication = Marshal.GetUniqueObjectForIUnknown(pointer); }
        finally { Marshal.Release(pointer); }
        ComEventsHelper.Combine(_eventApplication, AppEvents, 1570, CloseHandler);
        ComEventsHelper.Combine(_eventApplication, AppEvents, 1564, ChangeHandler);
        ComEventsHelper.Combine(_eventApplication, AppEvents, 1567, OpenHandler);
    }

    [ExcelCommand(Name = "STR_XL_DESIGN_INPUTS", Description = "Prepare explicit project, member and service-action inputs for captured beams.")]
    public static string DesignInputs() => Run((app, workbook, store, entry) =>
    {
        var state = RequireState(store);
        _ = store.CreateDesignInputs(state, LoadSession(state, entry).Snapshot);
        return Result("needs_input", "Edit the Value column in Design Inputs, then click Accept Inputs. Source facts are fixed; demo catalogue values remain labelled. Acceptance is not professional approval.");
    });

    [ExcelCommand(Name = "STR_XL_ACCEPT_DESIGN_INPUTS", Description = "Accept calculation inputs for selected beams; not professional approval.")]
    public static string AcceptDesignInputs() => Run((app, workbook, store, entry) =>
    {
        var state = RequireState(store); var snapshot = LoadSession(state, entry).Snapshot;
        var input = store.ReadDesignInputs(state, snapshot);
        if (input.MemberIds.Count == 0) throw new InvalidOperationException("Select at least one member in Design Inputs.");
        var reference = DesignArtifacts(state).SaveRequest(BaselineReplay.Request(snapshot, input.Inputs, input.MemberIds,
            new BaselineDesignOptions(input.Inputs.Catalogue.MaximumCandidates)));
        CancelEntryDesign(entry);
        var design = state.Design! with
        {
            AcceptedRequest = reference,
            AcceptedInputRevision = input.Revision,
            AcceptedAssumptionRevision = store.ReadAssumptions(state).Revision,
            Status = "Inputs accepted — design has not been run for this basis"
        };
        store.CommitAcceptedDesignInputs(state, design, snapshot);
        store.MarkDesignHistorical(RequireState(store), design.Status);
        entry.DesignInvalidated = false;
        return Result("accepted", $"Calculation inputs accepted for {input.MemberIds.Count} selected beams. {input.Issues.Count} unresolved input messages remain. Professional approval remains unreviewed.",
            new { input_revision = input.Revision, selected_members = input.MemberIds, issues = input.Issues });
    });

    [ExcelCommand(Name = "STR_XL_DESIGN", Description = "Design selected captured beams from accepted inputs in the background.")]
    public static string Design() => Run((app, workbook, store, entry) =>
    {
        if (entry.DesignWork is not null) throw new InvalidOperationException("A design is running. Wait or click Cancel Design.");
        if (entry.ForceRequestId is not null || entry.ConnectionRequestId is not null)
            throw new InvalidOperationException("Wait for the model read before designing its snapshot.");
        var state = RequireState(store); var snapshot = LoadSession(state, entry).Snapshot;
        var request = RequireAcceptedDesign(store, state, entry, snapshot);
        var key = Key((object)workbook);
        store.MarkDesignHistorical(state, "Design running — previous results are historical");
        var sink = new DesignProgressSink(key, entry);
        var work = BaselineDesignWork.Start(snapshot, request.AcceptedInputs, request.MemberIds, request.Options, sink);
        foreach (var old in DesignDispatches.Where(x => x.Value.IsCompleted).Take(Math.Max(0, DesignDispatches.Count - 31)).Select(x => x.Key).ToArray())
        {
            DesignDispatches.Remove(old);
            DesignDispatchPhases.TryRemove(old, out _);
        }
        DesignDispatches.Add(work.RequestId, work.Completion);
        DesignDispatchPhases[work.RequestId] = "dispatched";
        entry.DesignWork = work; sink.DispatchId = work.RequestId;
        entry.Window ??= new OfflineReviewWindow();
        entry.Window.SetPendingDesign(() => ExcelAsyncUtil.QueueAsMacro(() => CancelDesignFor(key, entry, work.RequestId)));
        _ = ObserveDesign(work, key, entry, state.DocumentId, state.Design!.AcceptedInputRevision!, snapshot.SnapshotSha256,
            DesignDirectory(state), state.Design.AcceptedRequest!);
        return Result("started", $"Designing {request.MemberIds.Count} selected beams. You can continue using Excel.",
            new { request_id = work.RequestId, selected_members = request.MemberIds.Count });
    });

    private static async Task ObserveDesign(BaselineDesignWork work, long key, Entry expected,
        string documentId, string inputRevision, string snapshotSha256, string resultDirectory, BaselineRequestReference requestReference)
    {
        BaselineBatchDesignResult? result = null; BaselineResultReference? reference = null; Exception? error = null;
        try
        {
            result = await work.Completion.ConfigureAwait(false);
            reference = await Task.Run(() => new BaselineDesignStore(resultDirectory).SaveResult(result, requestReference)).ConfigureAwait(false);
        }
        catch (Exception failure) { error = failure; }
        try
        {
            DesignDispatchPhases[work.RequestId] = "completion queued";
            ExcelAsyncUtil.QueueAsMacro(() =>
            {
                try { CompleteDesign(key, expected, work, documentId, inputRevision, snapshotSha256, result, reference, error); }
                catch (Exception callbackError)
                {
                    DesignDispatchPhases[work.RequestId] = "callback failed: " + callbackError;
                    expected.LastOutcome = Result("failed", callbackError.Message, new { request_id = work.RequestId });
                    work.Dispose();
                }
            });
        }
        catch (InvalidOperationException failure) { DesignDispatchPhases[work.RequestId] = "queue unavailable: " + failure.Message; work.Dispose(); }
    }

    private static void CompleteDesign(long key, Entry expected, BaselineDesignWork work,
        string documentId, string inputRevision, string snapshotSha256, BaselineBatchDesignResult? result, BaselineResultReference? reference, Exception? failure)
    {
        if (!CurrentDesign(key, expected, work.RequestId)) { DesignDispatchPhases[work.RequestId] = "completion discarded: " + expected.LastOutcome; work.Dispose(); return; }
        DesignDispatchPhases[work.RequestId] = "completion callback";
        Run((app, workbook, store, entry) =>
        {
            entry.DesignWork = null; work.Dispose(); entry.Window?.EndPendingConnection();
            DesignDispatchPhases[work.RequestId] = "reading workbook basis";
            var state = RequireState(store); var snapshot = LoadSession(state, entry).Snapshot;
            if (state.DocumentId != documentId || state.Design?.AcceptedInputRevision != inputRevision || snapshot.SnapshotSha256 != snapshotSha256)
                throw new InvalidOperationException("The design basis changed before completion. Accept inputs and design again.");
            _ = RequireAcceptedDesign(store, state, entry, snapshot);
            DesignDispatchPhases[work.RequestId] = "basis verified";
            if (failure is OperationCanceledException) return Result("cancelled", "Design cancelled; previous results remain historical.");
            if (failure is not null) return Result("failed", "Design failed: " + failure.Message);
            if (result is null || reference is null) throw new InvalidOperationException("The worker returned no saved design result.");
            DesignDispatchPhases[work.RequestId] = "result persisted";
            var design = state.Design! with
            {
                Result = reference,
                ResultSnapshot = state.SnapshotReference,
                ResultStoreDirectory = state.StoreDirectory,
                Status = "Current for accepted offline snapshot and inputs — professional approval unreviewed"
            };
            store.WriteDesignSummary(state, design, BaselineDesignProjection.Summary(result, design.Status));
            DesignDispatchPhases[work.RequestId] = "summary written";
            return Result("completed", $"Design finished: {result.Members.Count(x => x.State == BaselineRunState.Complete)} complete of {result.Members.Count}. Select a member in Beam Designs for Details.",
                new { request_id = work.RequestId, result_reference = reference, members = result.Members.Select(x => new { member_id = x.MemberId, state = x.State.ToString() }) });
        }, key);
        DesignDispatchPhases[work.RequestId] = "completion callback returned: " + expected.LastOutcome;
    }

    [ExcelCommand(Name = "STR_XL_CANCEL_DESIGN", Description = "Cancel this workbook's pending design.")]
    public static string CancelDesign() => Run((app, workbook, store, entry) => CancelDesignCore(store, entry));

    private static string CancelDesignCore(OfflineWorkbookStore store, Entry entry)
    {
        var dispatch = entry.DesignWork?.RequestId;
        CancelEntryDesign(entry); entry.Window?.EndPendingConnection();
        if (store.ReadState() is { } state) store.MarkDesignHistorical(state, "Design cancelled — previous results are historical");
        return Result("cancelled", "Design cancelled. The dispatched worker retains cleanup ownership until its completion task settles.", new { request_id = dispatch });
    }

    private static void CancelDesignFor(long key, Entry expected, string dispatch)
    {
        if (CurrentDesign(key, expected, dispatch)) Run((app, workbook, store, entry) => CancelDesignCore(store, entry), key);
    }

    [ExcelCommand(Name = "STR_XL_DESIGN_STATUS", Description = "Check saved design currentness against this workbook's input basis.")]
    public static string DesignStatus() => DesignStatusFor(null);

    private static string DesignStatusFor(long? key) => Run((app, workbook, store, entry) =>
    {
        if (entry.DesignWork is { } work) return Result("started", "Design is running.", new { request_id = work.RequestId });
        var state = RequireState(store);
        if (state.Design?.Result is null) return Result("not_run", "No saved baseline design is available.");
        var result = ReadDesignResult(store, state, entry, out var status);
        store.WriteDesignSummary(state, state.Design with { Status = status }, BaselineDesignProjection.Summary(result, status));
        store.Activate(OfflineWorkbookStore.DesignSummarySheet);
        return Result(status.StartsWith("Current", StringComparison.Ordinal) ? "current" : "stale", status,
            new { request_id = result.RequestId, members = result.Members.Select(x => new { member_id = x.MemberId, state = x.State.ToString() }) });
    }, key);

    [ExcelCommand(Name = "STR_XL_DESIGN_DETAILS", Description = "Inspect saved reinforcement and required checks for a member.")]
    public static string DesignDetails(string memberId) => Run((app, workbook, store, entry) =>
    {
        var state = RequireState(store); var result = ReadDesignResult(store, state, entry, out var status);
        var member = result.Members.SingleOrDefault(x => x.MemberId == memberId) ?? throw new InvalidOperationException("Select a member from Beam Designs.");
        var historicalSnapshot = new OfflineSnapshotStore(state.Design!.ResultStoreDirectory ?? state.StoreDirectory!).Read(
            state.Design.ResultSnapshot ?? throw new InvalidOperationException("The saved design's exact snapshot reference is missing."));
        store.WriteDesignDetails(state, BaselineDesignProjection.Details(member, historicalSnapshot, status,
            Path.Combine(ResultDirectory(state), state.Design.Result!.FileName)));
        return Result("completed", "Saved design details shown for " + memberId + ". " + status);
    });

    public static string SelectedDesignDetails()
    {
        string? memberId = null;
        var selection = Run((app, workbook, store, entry) =>
        {
            dynamic? sheet = null; dynamic? activeCell = null; dynamic? cell = null;
            try
            {
                sheet = workbook.ActiveSheet; activeCell = app.ActiveCell;
                if ((string)sheet.Name != OfflineWorkbookStore.DesignSummarySheet || (int)activeCell.Row < 10)
                    throw new InvalidOperationException("Select a member row in Beam Designs, then click Details.");
                cell = sheet.Range["A" + (int)activeCell.Row]; memberId = Convert.ToString(cell.Value2);
                return Result("selected", "Opening selected design details.");
            }
            finally { OfflineWorkbookStore.Release(cell); OfflineWorkbookStore.Release(activeCell); OfflineWorkbookStore.Release(sheet); }
        });
        return memberId is null ? selection : DesignDetails(memberId);
    }

    private static BaselineBatchDesignResult ReadDesignResult(OfflineWorkbookStore store, OfflineDocumentState state, Entry entry, out string status)
    {
        var reference = state.Design?.Result ?? throw new InvalidOperationException("Run Design first.");
        BaselineBatchDesignResult result;
        try { result = new BaselineDesignStore(ResultDirectory(state)).ReadResult(reference); }
        catch (Exception error) when (error is IOException or System.Text.Json.JsonException or ArgumentException or InvalidOperationException)
        {
            store.MarkDesignHistorical(state, "Historical — saved design evidence is unavailable: " + error.Message);
            throw new InvalidOperationException("Saved design evidence is unavailable. Restore the referenced file or run Design again. " + error.Message, error);
        }
        try
        {
            var snapshot = LoadSession(state, entry).Snapshot;
            _ = RequireAcceptedDesign(store, state, entry, snapshot);
            if (state.Design!.AcceptedRequest?.FileSha256 != reference.RequestFileSha256)
                throw new InvalidOperationException("Saved results use a different source, input or engine revision.");
            status = "Current for accepted offline snapshot and inputs — professional approval unreviewed";
        }
        catch (Exception error) when (error is ArgumentException or InvalidOperationException or IOException)
        { status = "Historical — " + error.Message; }
        return result;
    }

    private static BaselineReplayRequest RequireAcceptedDesign(OfflineWorkbookStore store, OfflineDocumentState state, Entry entry, AnalysisSnapshot snapshot)
    {
        var design = state.Design ?? throw new InvalidOperationException("Click Design Inputs first.");
        var reference = design.AcceptedRequest ?? throw new InvalidOperationException("Click Accept Inputs before designing.");
        var current = store.ReadDesignInputs(state, snapshot);
        if (entry.DesignInvalidated || design.AcceptedInputRevision != current.Revision ||
            design.AcceptedAssumptionRevision != store.ReadAssumptions(state).Revision)
            throw new InvalidOperationException("Inputs changed. Accept the current inputs and design again.");
        var request = DesignArtifacts(state).ReadRequest(reference);
        if (request.SnapshotSha256 != snapshot.SnapshotSha256 || request.EngineRevisionId != BaselineDesignOperations.EngineIdentity)
            throw new InvalidOperationException("Snapshot or engine changed. Accept inputs and design again.");
        if (WorkbookContract.HashBytes(BaselineReplay.Serialize(BaselineReplay.Request(snapshot, current.Inputs, current.MemberIds, request.Options))) != reference.FileSha256)
            throw new InvalidOperationException("The accepted request does not match the current input values and member selection.");
        return request;
    }

    private static string DesignDirectory(OfflineDocumentState state) => Path.Combine(state.StoreDirectory ?? throw new InvalidOperationException("External snapshot store is missing."), "Designs");
    private static BaselineDesignStore DesignArtifacts(OfflineDocumentState state) => new(DesignDirectory(state));
    private static string ResultDirectory(OfflineDocumentState state) => Path.Combine(state.Design?.ResultStoreDirectory ?? state.StoreDirectory
        ?? throw new InvalidOperationException("Saved design store is missing."), "Designs");
    private static bool CurrentDesign(long key, Entry expected, string dispatch) =>
        Entries.TryGetValue(key, out var entry) && ReferenceEquals(entry, expected) && entry.DesignWork?.RequestId == dispatch;
    private static void CancelEntryDesign(Entry entry)
    {
        var work = entry.DesignWork; entry.DesignWork = null;
        if (work is null) return;
        work.Cancel(); work.Dispose();
    }

    private static void OnSheetChange(object sheet, object target)
    {
        object? workbook = null; var entered = false;
        try
        {
            if (_busy) return;
            dynamic source = sheet; string name = source.Name;
            if (name != BaselineInputSheet.SheetName && name != OfflineAssumptions.SheetName) return;
            workbook = source.Parent; var key = Key(workbook);
            if (!Entries.TryGetValue(key, out var entry)) Entries[key] = entry = new();
            entry.DesignInvalidated = true; CancelEntryDesign(entry); entry.Window?.EndPendingConnection();
            const string message = "Historical — inputs edited; accept inputs and design again";
            entry.LastOutcome = Result("stale", message);
            _busy = true; entered = true;
            var store = new OfflineWorkbookStore(workbook);
            if (store.ReadState() is { Design: not null } state) store.MarkDesignHistorical(state, message);
        }
        catch (Exception error) { HostEffectLedger.Record("excel.design.invalidate.failed:" + error.GetType().Name); }
        finally
        {
            if (entered) _busy = false;
            OfflineWorkbookStore.Release(workbook);
            // Owned write transactions suppress events until their RCWs are released,
            // so these user-event arguments cannot alias an active output transaction.
            OfflineWorkbookStore.Release(target); OfflineWorkbookStore.Release(sheet);
        }
    }

    private static void OnWorkbookOpen(object workbook)
    {
        try
        {
            if (new OfflineWorkbookStore(workbook).ReadState()?.Design?.Result is null) return;
            var key = Key(workbook);
            ExcelAsyncUtil.QueueAsMacro(() => DesignStatusFor(key));
        }
        finally { OfflineWorkbookStore.Release(workbook); }
    }

    private sealed class DesignProgressSink(long key, Entry expected) : IProgress<(int Completed, int Total, string MemberId)>
    {
        public string? DispatchId { get; set; }
        public void Report((int Completed, int Total, string MemberId) value)
        {
            try
            {
                ExcelAsyncUtil.QueueAsMacro(() =>
                {
                    if (DispatchId is { } id && CurrentDesign(key, expected, id))
                        expected.Window?.SetForceProgress($"Designing beams: {value.Completed} of {value.Total} — {value.MemberId}");
                });
            }
            catch (InvalidOperationException) { }
        }
    }
}
