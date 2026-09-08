using ExcelDna.Integration;
using StructuralEngineering.Contracts;

namespace StructuralEngineering.ExcelDna;

public static partial class OfflineCommands
{
    [ExcelCommand(Name = "STR_XL_GET_FORCES", Description = "Capture the connected model's required beam forces without force worksheets.")]
    public static string GetForces() => StartForces(null);

    [ExcelCommand(Name = "STR_XL_GET_FORCES_SCOPE", Description = "Qualification/automation: read an explicit comma-separated beam scope from the connected model.")]
    public static string GetForcesScope(string sourceMemberIds) => StartForces(sourceMemberIds.Split(',', StringSplitOptions.TrimEntries | StringSplitOptions.RemoveEmptyEntries));

    private static string StartForces(IReadOnlyList<string>? members) => Run((app, workbook, store, entry) =>
    {
        var context = entry.Context ?? throw new InvalidOperationException("Connect ETABS first to identify the model.");
        if (entry.ConnectionRequestId is not null || entry.ForceRequestId is not null)
            throw new InvalidOperationException("This workbook already has a model read running. Wait or cancel it.");
        var state = store.ReadState() ?? store.CreateAssumptions();
        _ = store.ReadAssumptions(state);
        var documentId = state.DocumentId;
        var projectId = state.SnapshotReference?.ProjectId ?? documentId;
        var contextId = context.Artifact.ArtifactSha256;
        var key = Key((object)workbook);
        var requestId = Guid.NewGuid().ToString("N");
        var package = Path.GetDirectoryName(ExcelDnaUtil.XllPath) ?? throw new InvalidOperationException("The add-in package directory is unavailable.");
        var storeDirectory = DefaultStoreDirectory();
        entry.ForceRequestId = requestId;
        entry.ForceCancellation = new();
        var token = entry.ForceCancellation.Token;
        entry.Window ??= new OfflineReviewWindow();
        entry.Window.SetPendingForces(() => ExcelAsyncUtil.QueueAsMacro(() => CancelForcesFor(key, entry, requestId)));
        _ = Task.Run(async () =>
        {
            EtabsForceLoadResult? result = null; Exception? failure = null;
            try
            {
                result = await EtabsConnectionClient.GetForcesAsync(package, Path.Combine(storeDirectory, "ForceReads"), storeDirectory,
                    context, projectId, requestId, token, new ForceProgressSink(key, entry, requestId), members).ConfigureAwait(false);
            }
            catch (Exception error) { failure = error; }
            if (token.IsCancellationRequested) return;
            try { ExcelAsyncUtil.QueueAsMacro(() => CompleteForces(key, entry, requestId, documentId, contextId, storeDirectory, result, failure)); }
            catch (InvalidOperationException) { /* The client still owns reader cleanup after Excel unloads. */ }
        });
        return Result("started", "Reading completed ETABS beam forces in the background. You can continue using Excel.",
            new { request_id = requestId, context_id = contextId, requested_members = members?.Count ?? context.Frames.Values.Count(frame => frame.DesignOrientation == EtabsFrameDesignOrientation.Beam) });
    });

    [ExcelCommand(Name = "STR_XL_FORCE_STATUS", Description = "Read this workbook's force state without another ETABS call.")]
    public static string ForceStatus() => Run((app, workbook, store, entry) =>
        entry.ForceRequestId is { } requestId ? Result("started", "The force read is running.", new { request_id = requestId })
        : entry.Session is { } session && entry.ForceContextArtifactSha256 is { } bound && entry.Context?.Artifact.ArtifactSha256 == bound
            ? Summary(session, "Forces captured for this connected context. Review uses memory; engineering checks have not run.", connected: true)
            : Result("not_loaded", "No force capture is bound to this connection. Saved snapshots remain available for offline review."));

    [ExcelCommand(Name = "STR_XL_CANCEL_FORCES", Description = "Cancel this workbook's pending force read.")]
    public static string CancelForces() => Run((app, workbook, store, entry) =>
    {
        CancelEntryForces(entry);
        entry.Window?.EndPendingConnection();
        return Result("cancelled", "Force read cancelled. The reader retains ownership until cleanup finishes; saved data remains available.");
    });

    [ExcelCommand(Name = "STR_XL_TEST_FORCE_SESSION_COUNT", Description = "Installed acceptance: count resident force captures bound to a connection.")]
    public static double ForceSessionCount() => Entries.Values.Count(entry => entry.Session is not null && entry.ForceContextArtifactSha256 is not null);

    private static void CompleteForces(long key, Entry expected, string requestId, string documentId, string contextId,
        string storeDirectory, EtabsForceLoadResult? result, Exception? failure)
    {
        if (!CurrentForce(key, expected, requestId)) return;
        Run((app, workbook, store, entry) =>
        {
            if (!ReferenceEquals(entry, expected) || entry.ForceRequestId != requestId) throw new InvalidOperationException("The initiating force read is no longer current.");
            entry.ForceRequestId = null;
            entry.ForceCancellation?.Dispose(); entry.ForceCancellation = null;
            entry.Window?.EndPendingConnection();
            var state = RequireState(store);
            if (state.DocumentId != documentId || entry.Context?.Artifact.ArtifactSha256 != contextId)
                throw new InvalidOperationException("The workbook or connected model changed while forces were being read. Start a new force read.");
            if (failure is not null) return Result("rejected", "Force capture failed: " + failure.Message);
            if (result?.Response.State != EtabsContextWorkerState.Completed || result.Session is null)
                return Result("rejected", result?.Response.Message ?? "No complete force snapshot was returned.", result?.Response);
            var session = result.Session;
            if (state.SnapshotReference is { } previous && previous.ProjectId != session.Reference.ProjectId)
                throw new InvalidOperationException("The workbook project changed before the force result could be attached.");
            CancelEntryDesign(entry);
            entry.DesignInvalidated = true;
            store.CommitImport(state, session.Reference, storeDirectory, store.ReadAssumptions(state), 0);
            store.MarkDesignHistorical(RequireState(store), "Historical — force snapshot replaced; accept inputs and design again");
            entry.Session = session;
            entry.ForceContextArtifactSha256 = contextId;
            entry.Window ??= new OfflineReviewWindow();
            entry.Window.SetReview(session, member => ExcelAsyncUtil.QueueAsMacro(() => WriteMemberReviewFor(key, member, 0)), capturedHere: true);
            return Summary(session, "Forces captured and verified. Member selection uses memory. Save the workbook to retain its snapshot reference; engineering checks have not run.", connected: true);
        }, key);
    }

    private static void CancelForcesFor(long key, Entry expected, string requestId)
    {
        if (!CurrentForce(key, expected, requestId)) return;
        Run((app, workbook, store, entry) =>
        {
            CancelEntryForces(entry); entry.Window?.EndPendingConnection();
            return Result("cancelled", "Force read cancelled. Reader cleanup continues; saved data remains available.");
        }, key);
    }
    private static bool CurrentForce(long key, Entry expected, string requestId) =>
        Entries.TryGetValue(key, out var current) && ReferenceEquals(current, expected) && current.ForceRequestId == requestId;
    private static void CancelEntryForces(Entry entry)
    {
        entry.ForceRequestId = null;
        entry.ForceCancellation?.Cancel(); entry.ForceCancellation?.Dispose(); entry.ForceCancellation = null;
    }
    private sealed class ForceProgressSink(long key, Entry entry, string requestId) : IProgress<EtabsForceProgress>
    {
        public void Report(EtabsForceProgress value)
        {
            try
            {
                ExcelAsyncUtil.QueueAsMacro(() =>
                {
                    if (!CurrentForce(key, entry, requestId)) return;
                    var text = value.Stage switch
                    {
                        EtabsForceStage.Capturing => $"Reading beam forces: {value.CompletedMembers} of {value.TotalMembers}.",
                        EtabsForceStage.Normalizing => "Checking units, geometry and complete force rows.",
                        _ => "Saving verified evidence outside the workbook."
                    };
                    entry.Window?.SetForceProgress(text);
                });
            }
            catch (InvalidOperationException) { }
        }
    }
}
