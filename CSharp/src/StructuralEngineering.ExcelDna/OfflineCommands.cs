using System.Globalization;
using System.Runtime.InteropServices;
using System.Text.Json;
using ExcelDna.Integration;
using StructuralEngineering.Contracts;

namespace StructuralEngineering.ExcelDna;

public sealed class OfflineAddIn : IExcelAddIn
{
    public void AutoOpen() { }
    public void AutoClose() => OfflineCommands.Unload();
}

/// <summary>Commands bind the initiating workbook before dialogs; UDFs never enter this boundary.</summary>
public static partial class OfflineCommands
{
    private sealed class Entry
    {
        public OfflineSnapshotSession? Session { get; set; }
        public OfflineReviewWindow? Window { get; set; }
        public string LastOutcome { get; set; } = "{}";
        public EtabsConnectionSession? Context { get; set; }
        public string? ConnectionRequestId { get; set; }
        public CancellationTokenSource? ConnectionCancellation { get; set; }
    }
    private static readonly Dictionary<long, Entry> Entries = [];
    private static readonly Guid AppEvents = new("00024413-0000-0000-C000-000000000046");
    private delegate void BeforeClose(object workbook, ref bool cancel);
    private static readonly BeforeClose CloseHandler = OnBeforeClose;
    private static object? _eventApplication;
    private static bool _busy;

    [ExcelCommand(Name = "STR_XL_ASSUMPTIONS", Description = "Create or validate transparent demo assumptions in this workbook.")]
    public static string Assumptions() => Run((app, workbook, store, entry) =>
    {
        var state = store.CreateAssumptions();
        var input = store.ReadAssumptions(state);
        return Result("completed", "Assumptions ready. DEMO values remain editable; save the workbook to retain them.",
            new { document_id = state.DocumentId, assumption_revision = input.Revision, production_issuance_allowed = false });
    });

    [ExcelCommand(Name = "STR_XL_OPEN_SNAPSHOT", Description = "Open a completed portable snapshot for offline review.")]
    public static string OpenSnapshot() => Run((app, workbook, store, entry) =>
    {
        _ = RequireState(store);
        using var picker = new System.Windows.Forms.OpenFileDialog
        {
            Title = "Open completed analysis snapshot",
            Filter = "Portable snapshot (*.json)|*.json",
            CheckFileExists = true,
            Multiselect = false,
            RestoreDirectory = true
        };
        if (picker.ShowDialog() != System.Windows.Forms.DialogResult.OK)
            return Result("cancelled", "Snapshot selection cancelled. The accepted snapshot is unchanged.");
        return ImportInto(workbook, store, entry, picker.FileName, null, DefaultStoreDirectory(), 0);
    });

    [ExcelCommand(Name = "STR_XL_IMPORT_SNAPSHOT_FILE", Description = "Import a snapshot by explicit file and optional expected digest.")]
    public static string ImportSnapshotFile(string path, string expectedSha256, string storeDirectory) =>
        Run((app, workbook, store, entry) => ImportInto(workbook, store, entry, path,
            string.IsNullOrWhiteSpace(expectedSha256) ? null : expectedSha256,
            string.IsNullOrWhiteSpace(storeDirectory) ? DefaultStoreDirectory() : storeDirectory, 0));

    [ExcelCommand(Name = "STR_XL_REVIEW_SNAPSHOT", Description = "Review captured members and forces from saved evidence.")]
    public static string ReviewSnapshot() => Run((app, workbook, store, entry) =>
    {
        var state = RequireState(store);
        _ = store.ReadAssumptions(state);
        var session = LoadSession(state, entry);
        ShowReview(app, workbook, entry, session);
        return Summary(session, "Snapshot ready for offline review. Engineering has not been evaluated.");
    });

    [ExcelCommand(Name = "STR_XL_WRITE_MEMBER_REVIEW", Description = "Write one requested member's offline evidence review.")]
    public static string WriteMemberReview(string memberId) => WriteMemberReviewFor(null, memberId, 0);

    [ExcelCommand(Name = "STR_XL_OFFLINE_STATUS", Description = "Read this workbook's latest command outcome.")]
    public static string Status()
    {
        dynamic app = ExcelDnaUtil.Application;
        dynamic? workbook = app.ActiveWorkbook;
        try { return workbook is null ? "{}" : Entries.GetValueOrDefault(Key((object)workbook))?.LastOutcome ?? "{}"; }
        finally { OfflineWorkbookStore.Release(workbook); OfflineWorkbookStore.Release(app); }
    }

    [ExcelCommand(Name = "STR_XL_TEST_OFFLINE_FAILURE", Description = "Installed acceptance: exercise verified projection rollback.")]
    public static string FailureProbe(string operation, string argument, double boundary) => Run((app, workbook, store, entry) =>
    {
        if (operation == "assumptions") store.CreateAssumptions((int)boundary);
        else if (operation == "report") WriteReportCore(store, entry, argument, (int)boundary);
        else throw new ArgumentException("Unknown offline failure probe.");
        return Result("completed", "Probe completed without a failure.");
    });

    [ExcelCommand(Name = "STR_XL_TEST_OFFLINE_SESSION_COUNT", Description = "Installed acceptance: read resident session count.")]
    public static double SessionCount() => Entries.Values.Count(entry => entry.Session is not null);

    internal static void RequireStandalone(object workbook)
    {
        if (new OfflineWorkbookStore(workbook).ReadState() is not null)
            throw new InvalidOperationException("This is a beam workspace. Linked design mapping is not implemented yet. Use Review Snapshot; run standalone examples in a separate workbook.");
    }

    internal static void ShowLegacyOutcome(Func<string> action)
    {
        // Legacy wrappers retain their established transaction/JSON APIs. Ribbon callers now consume the outcome.
        Run((app, workbook, store, entry) => action());
    }

    internal static void Unload()
    {
        foreach (var entry in Entries.Values) { CancelEntryConnection(entry); entry.Window?.Dispose(); }
        Entries.Clear();
        if (_eventApplication is not null)
        {
            ComEventsHelper.Remove(_eventApplication, AppEvents, 1570, CloseHandler);
            OfflineWorkbookStore.Release(_eventApplication);
            _eventApplication = null;
        }
    }

    private static void OnBeforeClose(object workbook, ref bool cancel)
    {
        try { if (Entries.Remove(Key(workbook), out var entry)) { CancelEntryConnection(entry); entry.Window?.Dispose(); } }
        finally { OfflineWorkbookStore.Release(workbook); }
        // A cancelled close merely requires reloading validated evidence on the next review.
    }

    private static string ImportInto(object workbook, OfflineWorkbookStore store, Entry entry, string path,
        string? expectedSha256, string directory, int failure)
    {
        var state = RequireState(store);
        var assumptions = store.ReadAssumptions(state);
        var artifacts = new OfflineSnapshotStore(directory);
        var reference = artifacts.Import(path, expectedSha256);
        if (state.SnapshotReference is not null && state.SnapshotReference.ProjectId != reference.ProjectId)
            throw new InvalidOperationException("This workbook is bound to another project. Use a new workbook for a different project.");
        var session = new OfflineSnapshotSession(reference, artifacts.Read(reference));
        store.CommitImport(state, reference, artifacts.RootDirectory, assumptions, failure);
        entry.Session = session;
        entry.Window?.ClearReview();
        return Summary(session, "Snapshot imported and verified. Save this workbook to retain its reference. Review uses offline evidence; no live model is connected.");
    }

    private static OfflineSnapshotSession LoadSession(OfflineDocumentState state, Entry entry)
    {
        var reference = state.SnapshotReference ?? throw new InvalidOperationException("Open a completed snapshot first.");
        if (entry.Session?.Reference == reference) return entry.Session;
        var artifacts = new OfflineSnapshotStore(state.StoreDirectory ?? throw new InvalidOperationException("Snapshot store location is missing."));
        entry.Session = new(reference, artifacts.Read(reference));
        return entry.Session;
    }

    private static string WriteMemberReviewFor(long? key, string memberId, int failure) => Run((app, workbook, store, entry) =>
    {
        WriteReportCore(store, entry, memberId, failure);
        return Result("completed", "Beam Review written for " + memberId + ". This is captured evidence, not an approved design.");
    }, key);

    private static void WriteReportCore(OfflineWorkbookStore store, Entry entry, string memberId, int failure)
    {
        var state = RequireState(store);
        var session = LoadSession(state, entry);
        var actions = session.ActionsForMember(memberId);
        var member = session.Snapshot.Members.Single(item => item.MemberId == memberId);
        var rows = new object[9 + actions.Count, 13];
        rows[0, 0] = "BEAM REVIEW — " + member.SourceLabel;
        rows[1, 0] = "Offline evidence; engineering not evaluated";
        rows[2, 0] = "Model"; rows[2, 1] = session.Snapshot.Metadata.ModelName;
        rows[3, 0] = "Snapshot"; rows[3, 1] = session.Reference.SnapshotId;
        rows[4, 0] = "Member"; rows[4, 1] = member.MemberId;
        rows[5, 0] = "Source"; rows[5, 1] = session.Snapshot.SourceIdentity.SourceSystem + " " + session.Snapshot.SourceIdentity.SourceVersion;
        rows[6, 0] = "Basis"; rows[6, 1] = "Signed source local-axis actions. No strength, span design, reinforcement or approval inferred.";
        rows[7, 0] = "Input revision"; rows[7, 1] = store.ReadAssumptions(state).Revision;
        var headers = ActionHeaders;
        for (var column = 0; column < headers.Length; column++) rows[8, column] = headers[column];
        for (var row = 0; row < actions.Count; row++)
        {
            var values = ActionValues(session, actions[row]);
            for (var column = 0; column < values.Length; column++) rows[row + 9, column] = values[column];
        }
        store.WriteReport(state, rows, failure);
    }

    internal static readonly string[] ActionHeaders = ["Row ID", "Case / combination", "Station (mm)", "Step", "Step number", "P (kN)", "V2 (kN)", "V3 (kN)", "T (kNm)", "M2 (kNm)", "M3 (kNm)", "Action basis", "Source row"];
    internal static string[] ActionValues(OfflineSnapshotSession session, SnapshotActionRow row)
    {
        string Number(double value) => value.ToString("G17", CultureInfo.InvariantCulture);
        return [row.RowId, row.OutputCaseName, Number(session.StationsById[row.StationId].PhysicalStationMm),
            row.StepType, row.StepNumber is { } step ? Number(step) : "—", Number(row.PKn), Number(row.V2Kn), Number(row.V3Kn),
            Number(row.TKnm), Number(row.M2Knm), Number(row.M3Knm), row.ActionBasis.ToString(), row.SourceRowId];
    }

    private static void ShowReview(dynamic app, dynamic workbook, Entry entry, OfflineSnapshotSession session)
    {
        var key = Key(workbook);
        entry.Window ??= new OfflineReviewWindow();
        entry.Window.SetReview(session, member => ExcelAsyncUtil.QueueAsMacro(() => WriteMemberReviewFor(key, member, 0)));
        if ((bool)app.Visible) entry.Window.Show();
    }

    private static OfflineDocumentState RequireState(OfflineWorkbookStore store) => store.ReadState()
        ?? throw new InvalidOperationException("Click Assumptions first to set up this workbook.");

    private static string Run(Func<dynamic, dynamic, OfflineWorkbookStore, Entry, string> action, long? targetKey = null)
    {
        if (_busy) return Result("rejected", "Another StructAutomate command is already running.");
        dynamic? app = null; dynamic? workbook = null;
        Entry? entry = null;
        _busy = true;
        try
        {
            app = ExcelDnaUtil.Application;
            workbook = targetKey is null ? app.ActiveWorkbook : FindWorkbook(app, targetKey.Value);
            if (workbook is null) throw new InvalidOperationException("The initiating workbook is closed. Open a workbook and try again.");
            if (_eventApplication is null)
            {
                // Keep the event sink on its own RCW so command cleanup cannot disconnect it.
                var pointer = Marshal.GetIUnknownForObject((object)app);
                try { _eventApplication = Marshal.GetUniqueObjectForIUnknown(pointer); }
                finally { Marshal.Release(pointer); }
                ComEventsHelper.Combine(_eventApplication, AppEvents, 1570, CloseHandler);
            }
            var key = Key(workbook);
            if (!Entries.TryGetValue(key, out entry)) Entries[key] = entry = new();
            var store = new OfflineWorkbookStore(workbook);
            EnsureUniqueDocument(app, workbook, store.ReadState());
            HostEffectLedger.Record("excel.offline.command");
            var result = action(app, workbook, store, entry);
            Publish(app, workbook, entry, result);
            return result;
        }
        catch (Exception error)
        {
            var result = Result("rejected", error.Message);
            if (app is not null && workbook is not null && entry is not null) Publish(app, workbook, entry, result);
            else System.Windows.Forms.MessageBox.Show(error.Message, "StructAutomate");
            return result;
        }
        finally { _busy = false; OfflineWorkbookStore.Release(workbook); OfflineWorkbookStore.Release(app); }
    }

    private static void Publish(dynamic app, dynamic workbook, Entry entry, string result)
    {
        entry.LastOutcome = result;
        using var json = JsonDocument.Parse(result);
        var message = json.RootElement.TryGetProperty("message", out var text) ? text.GetString() : result;
        app.StatusBar = "StructAutomate: " + message;
        if (entry.Window?.IsDisposed == true) entry.Window = null;
        entry.Window ??= new OfflineReviewWindow();
        entry.Window.SetOutcome((string)workbook.Name, message ?? result);
        if ((bool)app.Visible) entry.Window.Show();
    }

    private static void EnsureUniqueDocument(dynamic app, dynamic workbook, OfflineDocumentState? state)
    {
        if (state is null) return;
        dynamic books = app.Workbooks;
        try
        {
            for (var i = 1; i <= (int)books.Count; i++)
            {
                dynamic other = books.Item(i);
                try
                {
                    if (Key(other) != Key(workbook) && new OfflineWorkbookStore(other).ReadState()?.DocumentId == state.DocumentId)
                        throw new InvalidOperationException("Two open workbooks share this document identity. Close one copy before continuing.");
                }
                finally { OfflineWorkbookStore.Release(other); }
            }
        }
        finally { OfflineWorkbookStore.Release(books); }
    }

    private static dynamic? FindWorkbook(dynamic app, long key)
    {
        dynamic books = app.Workbooks;
        try
        {
            for (var i = 1; i <= (int)books.Count; i++)
            {
                dynamic book = books.Item(i);
                if (Key(book) == key) return book;
                OfflineWorkbookStore.Release(book);
            }
            return null;
        }
        finally { OfflineWorkbookStore.Release(books); }
    }

    private static long Key(object workbook)
    {
        var pointer = Marshal.GetIUnknownForObject(workbook);
        try { return pointer.ToInt64(); }
        finally { Marshal.Release(pointer); }
    }
    private static string DefaultStoreDirectory() => Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "StructAutomate", "Projects");
    private static string Result(string state, string message, object? details = null) => JsonSerializer.Serialize(new { state, message, details });
    private static string Summary(OfflineSnapshotSession session, string message) => Result("completed", message,
        new
        {
            project_id = session.Reference.ProjectId,
            snapshot_id = session.Reference.SnapshotId,
            file_sha256 = session.Reference.FileSha256,
            member_count = session.Snapshot.Members.Count,
            action_count = session.Snapshot.ActionRows.Count,
            live_connected = false,
            engineering = "not_evaluated"
        });
}
