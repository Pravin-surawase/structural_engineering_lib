using System.Text.Json;
using ExcelDna.Integration;
using StructuralEngineering.Contracts;

namespace StructuralEngineering.ExcelDna;

public static partial class OfflineCommands
{
    [ExcelCommand(Name = "STR_XL_CONNECT_ETABS", Description = "Read source geometry from a uniquely identified running ETABS model.")]
    public static string ConnectEtabs() => ConnectEtabsProcess(0);

    [ExcelCommand(Name = "STR_XL_CONNECT_ETABS_PROCESS", Description = "Connect to an explicit running ETABS PID; zero offers available processes.")]
    public static string ConnectEtabsProcess(double processId) => Run((app, workbook, store, entry) =>
    {
        if (entry.ConnectionRequestId is not null) throw new InvalidOperationException("A connection is already running for this workbook. Wait or cancel it.");
        if (!double.IsFinite(processId) || processId < 0 || processId != Math.Truncate(processId) || processId > int.MaxValue)
            throw new ArgumentException("Enter a valid ETABS process ID.");
        var choices = EtabsConnectionClient.FindRunningModels();
        if (choices.Count == 0) throw new InvalidOperationException("Open ETABS and its model, then click Connect ETABS again.");
        var choice = processId > 0 ? choices.SingleOrDefault(item => item.ProcessId == (int)processId)
            ?? throw new InvalidOperationException("The selected ETABS process is no longer available.")
            : choices.Count == 1 ? choices[0] : EtabsProcessSelector.Choose(choices);
        if (choice is null) return Result("cancelled", "Connection selection cancelled.");
        var key = Key((object)workbook);
        var requestId = Guid.NewGuid().ToString("N");
        entry.ConnectionRequestId = requestId;
        entry.ConnectionCancellation = new();
        var token = entry.ConnectionCancellation.Token;
        var package = Path.GetDirectoryName(ExcelDnaUtil.XllPath) ?? throw new InvalidOperationException("The add-in package directory is unavailable.");
        var root = Path.Combine(DefaultStoreDirectory(), "Connections");
        entry.Window ??= new OfflineReviewWindow();
        entry.Window.SetPendingConnection(() => ExcelAsyncUtil.QueueAsMacro(() => CancelConnectionFor(key, entry, requestId)));
        _ = Task.Run(async () =>
        {
            EtabsConnectionResult? result = null; Exception? failure = null;
            try { result = await EtabsConnectionClient.ConnectAsync(package, root, choice, requestId, token).ConfigureAwait(false); }
            catch (Exception error) { failure = error; }
            if (token.IsCancellationRequested) return;
            try
            {
                ExcelAsyncUtil.QueueAsMacro(() => CompleteConnection(key, entry, requestId, result, failure));
            }
            catch (InvalidOperationException) { /* Excel has unloaded; the worker client still owns cleanup. */ }
        });
        return Result("started", "Reading the selected ETABS model in the background. You can continue using Excel.", new { request_id = requestId, process_id = choice.ProcessId });
    });

    [ExcelCommand(Name = "STR_XL_CONNECTION_STATUS", Description = "Read current connection state without starting a worker.")]
    public static string ConnectionStatus()
    {
        dynamic app = ExcelDnaUtil.Application; dynamic? workbook = app.ActiveWorkbook;
        try
        {
            var entry = workbook is null ? null : Entries.GetValueOrDefault(Key((object)workbook));
            return entry?.ConnectionRequestId is { } pending ? Result("started", "ETABS connection is running.", new { request_id = pending })
                : entry?.Context is { } context ? ContextSummary(context)
                : Result("disconnected", "Connect ETABS to read model context. Saved force snapshots are separate.");
        }
        finally { OfflineWorkbookStore.Release(workbook); OfflineWorkbookStore.Release(app); }
    }

    [ExcelCommand(Name = "STR_XL_REVIEW_CONTEXT_FRAME", Description = "Review one source frame locally without another ETABS read.")]
    public static string ReviewContextFrame(string frameId) => Run((app, workbook, store, entry) =>
    {
        var context = entry.Context ?? throw new InvalidOperationException("Connect ETABS first to load source geometry.");
        if (!context.Frames.TryGetValue(frameId, out var frame)) throw new ArgumentException("That source frame is absent from the captured context.");
        entry.Window ??= new OfflineReviewWindow();
        entry.Window.SetContext(context, frameId);
        return Result("completed", "Source frame reviewed from memory. Shared joints describe connectivity; supports and physical spans are not yet classified.",
            new { frame, point1 = context.Points[frame.SourcePoint1Id], point2 = context.Points[frame.SourcePoint2Id], neighbours = context.Neighbours(frameId), etabs_reads = 0 });
    });

    [ExcelCommand(Name = "STR_XL_TEST_CONNECTION_SESSION_COUNT", Description = "Installed acceptance: count resident model contexts.")]
    public static double ConnectionSessionCount() => Entries.Values.Count(entry => entry.Context is not null);
    [ExcelCommand(Name = "STR_XL_TEST_CONNECTION_WORKER_COUNT", Description = "Installed acceptance: count active or cleaning-up reader processes.")]
    public static double ConnectionWorkerCount() => EtabsConnectionClient.ActiveWorkerCount;

    private static void CompleteConnection(long key, Entry expectedEntry, string requestId, EtabsConnectionResult? result, Exception? failure)
    {
        if (!Entries.TryGetValue(key, out var current) || !ReferenceEquals(current, expectedEntry) || current.ConnectionRequestId != requestId) return;
        Run((app, workbook, store, entry) =>
        {
            if (!ReferenceEquals(entry, expectedEntry) || entry.ConnectionRequestId != requestId) throw new InvalidOperationException("The initiating connection is no longer current.");
            entry.ConnectionRequestId = null;
            entry.ConnectionCancellation?.Dispose(); entry.ConnectionCancellation = null;
            entry.Window?.EndPendingConnection();
            if (failure is not null) return Result("rejected", "ETABS connection failed: " + failure.Message);
            if (result?.Artifact is null || result.Response.State != EtabsContextWorkerState.Completed)
                return Result("rejected", result?.Response.Message ?? "No completed model context was returned.", result?.Response);
            entry.Context = new(result.Artifact, result.OperationDirectory);
            entry.Window ??= new OfflineReviewWindow();
            entry.Window.SetContext(entry.Context);
            return ContextSummary(entry.Context);
        }, key);
    }

    private static void CancelConnectionFor(long key, Entry expectedEntry, string requestId)
    {
        if (!Entries.TryGetValue(key, out var current) || !ReferenceEquals(current, expectedEntry) || current.ConnectionRequestId != requestId) return;
        Run((app, workbook, store, entry) =>
        {
            CancelEntryConnection(entry);
            entry.Window?.EndPendingConnection();
            return Result("cancelled", "Connection cancelled. The reader retains ownership until cleanup finishes; previous captured data is unchanged.");
        }, key);
    }
    private static void CancelEntryConnection(Entry entry)
    {
        entry.ConnectionRequestId = null;
        entry.ConnectionCancellation?.Cancel(); entry.ConnectionCancellation?.Dispose(); entry.ConnectionCancellation = null;
    }
    private static string ContextSummary(EtabsConnectionSession context) => Result("completed",
        "Model context captured. Frame selection uses memory. Forces, physical spans and design checks have not been acquired by this connection.",
        new
        {
            context_id = context.Artifact.ArtifactSha256,
            source = context.Artifact.Inventory.Source,
            captured_utc = context.Artifact.Inventory.CapturedUtc,
            frame_count = context.Frames.Count,
            point_count = context.Points.Count,
            section_count = context.Sections.Count,
            beam_count = context.Frames.Values.Count(frame => frame.DesignOrientation == EtabsFrameDesignOrientation.Beam),
            column_count = context.Frames.Values.Count(frame => frame.DesignOrientation == EtabsFrameDesignOrientation.Column),
            operation_directory = context.OperationDirectory,
            getter_calls = context.Artifact.Inventory.Provenance?.GetterCalls,
            coordinates = "global mm",
            coverage = context.Artifact.Inventory.Coverage,
            forces_loaded = false,
            engineering = "not_evaluated"
        });
}
