using StructuralEngineering.Contracts;

namespace StructuralEngineering.ExcelDna;

public sealed record BaselineWorkbookState(int InputRows, string InputSnapshotSha256,
    string? AcceptedInputRevision = null, string? AcceptedAssumptionRevision = null,
    BaselineRequestReference? AcceptedRequest = null, BaselineResultReference? Result = null,
    int SummaryRows = 0, int DetailRows = 0, string Status = "Needs Input — resolve and accept the design basis",
    OfflineSnapshotReference? ResultSnapshot = null, string? ResultStoreDirectory = null);

internal sealed partial class OfflineWorkbookStore
{
    public const string DesignSummarySheet = "Beam Designs";
    public const string DesignDetailSheet = "Design Details";

    public OfflineDocumentState CreateDesignInputs(OfflineDocumentState state, AnalysisSnapshot snapshot)
    {
        if (state.Design is { } existing && existing.InputSnapshotSha256 == snapshot.SnapshotSha256)
        {
            _ = ReadDesignInputCells(state);
            Activate(BaselineInputSheet.SheetName);
            return state;
        }
        var cells = BaselineInputSheet.Create(snapshot);
        // Preserve explicit edits for matching fields when recapturing the same source members.
        if (state.Design is { } old)
        {
            var previous = ReadDesignInputCells(state);
            var r0 = previous.GetLowerBound(0); var c0 = previous.GetLowerBound(1);
            var edits = new Dictionary<string, object?>();
            for (var row = 0; row < previous.GetLength(0); row++)
            {
                var key = string.Join("|", new[] { 0, 1, 2, 4 }.Select(c => Text(previous[row + r0, c + c0])));
                edits[key] = previous[row + r0, 3 + c0];
            }
            for (var row = 0; row < cells.GetLength(0); row++)
            {
                var key = string.Join("|", new[] { 0, 1, 2, 4 }.Select(c => Text(cells[row, c])));
                if (Text(cells[row, 0]) != "Source" &&
                    edits.TryGetValue(key, out var value)) cells[row, 3] = value!;
            }
        }
        var design = (state.Design ?? new(cells.GetLength(0), snapshot.SnapshotSha256)) with
        {
            InputRows = cells.GetLength(0),
            InputSnapshotSha256 = snapshot.SnapshotSha256,
            AcceptedRequest = null,
            AcceptedInputRevision = null,
            Status = "Needs Input — resolve and accept the design basis"
        };
        var updated = state with { Design = design };
        WriteTransaction(updated, BaselineInputSheet.SheetName, cells, state.Design?.InputRows ?? 0, 0);
        Activate(BaselineInputSheet.SheetName);
        return updated;
    }

    public object[,] ReadDesignInputCells(OfflineDocumentState state)
    {
        var design = state.Design ?? throw new InvalidOperationException("Click Design Inputs first.");
        dynamic? sheet = FindSheet(BaselineInputSheet.SheetName); dynamic? range = null;
        try
        {
            if (sheet is null) throw new InvalidOperationException("The owned Design Inputs sheet is missing.");
            if (design.InputRows is < 1 or > 100000) throw new InvalidOperationException("Design Inputs layout is incompatible.");
            range = SizedRange(sheet, "A1", design.InputRows, 6);
            object[,] formulas = range.Formula;
            foreach (var cell in formulas)
                if (Text(cell).StartsWith('=')) throw new InvalidOperationException("Design Inputs requires explicit values; formulas are not accepted.");
            return (object[,])range.Value2;
        }
        finally { Release(range); Release(sheet); }
    }

    public BaselineInputReadResult ReadDesignInputs(OfflineDocumentState state, AnalysisSnapshot snapshot) =>
        BaselineInputSheet.Read(snapshot, ReadDesignInputCells(state));

    public void CommitDesignState(OfflineDocumentState state, BaselineWorkbookState design)
    {
        WriteTransaction(state with { Design = design }, null, null, 0, 0);
    }

    public void CommitAcceptedDesignInputs(OfflineDocumentState state, BaselineWorkbookState design, AnalysisSnapshot snapshot)
    {
        var rows = BaselineInputSheet.NormalizeOrigins(snapshot, ReadDesignInputCells(state));
        WriteTransaction(state with { Design = design }, BaselineInputSheet.SheetName, rows, design.InputRows, 0);
    }

    public void WriteDesignSummary(OfflineDocumentState state, BaselineWorkbookState design, object[,] rows, int failAfterWrite = 0)
    {
        design = design with { SummaryRows = rows.GetLength(0) };
        WriteTransaction(state with { Design = design }, DesignSummarySheet, rows, state.Design?.SummaryRows ?? 0, failAfterWrite);
    }

    public void WriteDesignDetails(OfflineDocumentState state, object[,] rows)
    {
        var design = state.Design ?? throw new InvalidOperationException("Design metadata is missing.");
        WriteTransaction(state with { Design = design with { DetailRows = rows.GetLength(0) } }, DesignDetailSheet, rows, design.DetailRows, 0);
        Activate(DesignDetailSheet);
    }

    public void MarkDesignHistorical(OfflineDocumentState state, string reason)
    {
        if (state.Design is not { } design) return;
        var updated = state with { Design = design with { Status = reason } };
        // Mark the existing summary without changing its owned footprint or switching the active sheet.
        object[,]? rows = null;
        if (design.SummaryRows > 0)
        {
            dynamic? sheet = FindSheet(DesignSummarySheet); dynamic? range = null;
            try
            {
                if (sheet is not null)
                {
                    range = sheet.Range["A1:L2"];
                    object[,] current = range.Value2;
                    rows = new object[2, 12];
                    for (var r = 0; r < 2; r++) for (var c = 0; c < 12; c++) rows[r, c] = current[r + 1, c + 1];
                    rows[1, 0] = reason;
                }
            }
            finally { Release(range); Release(sheet); }
        }
        WriteTransaction(updated, rows is null ? null : DesignSummarySheet, rows, rows is null ? 0 : 2, 0);
    }
}
