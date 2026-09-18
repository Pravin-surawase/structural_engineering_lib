using System.Text.Json;
using StructuralEngineering.Beam;
using StructuralEngineering.Contracts;

namespace StructuralEngineering.ExcelDna;

public sealed record BeamReviewArtifactReference(string FileName, string FileSha256, string RequestId, string LedgerRevision, string EngineIdentity);
public sealed record BeamReviewInputReference(string FileName, string FileSha256, string LedgerRevision);
// JSON strings keep the existing workbook transaction's value-equality/readback contract.
public sealed record BeamReviewWorkbookState(string ResolvedJson, int InputRows = 0, int SummaryRows = 0,
    int DetailRows = 0, BeamReviewArtifactReference? Result = null, string? ResultDirectory = null,
    string Status = "Provisional inputs resolved", bool Cancelled = false, string SheetValuesJson = "{}",
    BeamReviewInputReference? InputArtifact = null, string? InputDirectory = null);
internal sealed record BeamCapturedEdits(IReadOnlyList<BeamInputEdit> Edits, string SheetValuesJson);

internal sealed partial class OfflineWorkbookStore
{
    public static BeamResolvedReview? ReadResolved(OfflineDocumentState state) => state.Review is null ? null :
        JsonSerializer.Deserialize<BeamResolvedReview>(state.Review.ResolvedJson, WorkbookContract.Json)
            ?? throw new InvalidDataException("Saved review inputs are missing.");

    public OfflineAssumptionInput ReadAssumptionsForReview(OfflineDocumentState state)
    {
        var entered = ReadAssumptionText(state);
        var preset = BeamReviewInputProjection.Preset();
        return new(preset.Id, false, OfflineAssumptions.Definitions.Select((d, i) =>
        {
            var key = BeamReviewPresetReader.LegacyKeys[d.Key];
            var valid = BeamReviewFields.TryNormalize(key, entered[i], out var value);
            return new AssumptionValue(d.Key, valid ? value : preset.Values[key], d.Unit,
                valid && value != preset.Values[key] ? "engineer_edit_demo_basis" : valid ? "demo_default" : "fallback_invalid_entry_retained");
        }).ToArray());
    }

    private string[] ReadAssumptionText(OfflineDocumentState state)
    {
        if (!state.HasAssumptions) throw new InvalidDataException("Assumptions sheet is not registered.");
        var rows = ReadReviewCells(OfflineAssumptions.SheetName, OfflineAssumptions.Definitions.Count + 5, 4);
        var values = new string[OfflineAssumptions.Definitions.Count];
        for (var i = 0; i < values.Length; i++)
        {
            if (Text(rows[i + 5, 0]) != OfflineAssumptions.Definitions[i].Label || Text(rows[i + 5, 2]) != OfflineAssumptions.Definitions[i].Unit)
                throw new InvalidDataException("Assumptions labels/units differ from the owned layout.");
            values[i] = Text(rows[i + 5, 1]);
        }
        return values;
    }

    public BeamCapturedEdits CaptureReviewEdits(OfflineDocumentState state, AnalysisSnapshot snapshot,
        string? changedSheet = null, int firstRow = 0, int lastRow = 0, int firstColumn = 0, int lastColumn = 0)
    {
        var saved = ReadResolved(state); var edits = saved?.Ledger.Edits ?? [];
        var sequence = edits.Count == 0 ? 0 : edits.Max(x => x.Sequence);
        var previousCells = JsonSerializer.Deserialize<Dictionary<string, string>>(state.Review?.SheetValuesJson ?? "{}")!;
        var currentCells = new Dictionary<string, string>();
        var binding = BeamReviewResolver.ModelBinding(snapshot); var preset = BeamReviewInputProjection.Preset();
        bool Changed(string sheet, int row, int column) => changedSheet == sheet && row >= firstRow && row <= lastRow && column >= firstColumn && column <= lastColumn;
        void Add(string key, BeamInputScope scope, string scopeId, string value)
        {
            var model = scope == BeamInputScope.Project ? null : binding;
            if (edits.Any(x => x.Key == key && x.Scope == scope && x.ScopeId == scopeId && x.ModelBinding == model && x.EnteredText == value)) return;
            edits = BeamReviewResolver.ApplyEdit(edits, BeamReviewResolver.Edit(key, scope, scopeId, model, value, ++sequence));
        }
        var assumptions = ReadAssumptionText(state);
        for (var i = 0; i < assumptions.Length; i++)
        {
            var key = BeamReviewPresetReader.LegacyKeys[OfflineAssumptions.Definitions[i].Key];
            var cellKey = "assumptions:" + key; currentCells[cellKey] = assumptions[i];
            var sameDefault = BeamReviewFields.TryNormalize(key, assumptions[i], out var normal) && normal == preset.Values[key];
            if (Changed(OfflineAssumptions.SheetName, i + 6, 2) || (previousCells.TryGetValue(cellKey, out var previous) ? previous != assumptions[i] : !sameDefault))
                Add(key, BeamInputScope.Project, "project", assumptions[i]);
        }
        if (state.Design is { } design && design.InputSnapshotSha256 == snapshot.SnapshotSha256)
        {
            var cells = ReadReviewCells(BaselineInputSheet.SheetName, design.InputRows, 6);
            var template = BaselineInputSheet.Create(snapshot);
            for (var r = 1; r < cells.GetLength(0); r++)
            {
                if (r >= template.GetLength(0) || Enumerable.Range(0, 3).Any(c => Text(cells[r, c]) != Text(template[r, c])))
                    throw new InvalidDataException("Design Inputs identity/layout differs from its source snapshot.");
                var category = Text(cells[r, 0]); var field = Text(cells[r, 2]);
                var key = BeamReviewInputProjection.LegacyField(category, field); if (key is null) continue;
                var text = Text(cells[r, 3]);
                var scope = category switch { "Material" => BeamInputScope.Material, "Member" => BeamInputScope.Member, "Role" => BeamInputScope.Selection, _ => BeamInputScope.Project };
                var scopeId = scope == BeamInputScope.Project ? "project" : Text(cells[r, 1]);
                var cellKey = "legacy:" + binding + ":" + category + ":" + scopeId + ":" + field;
                currentCells[cellKey] = text;
                var force = Changed(BaselineInputSheet.SheetName, r + 1, 4);
                if (!force && previousCells.TryGetValue(cellKey, out var oldText) && oldText == text) continue;
                // Initial blank/template cells are not edits. Accepted legacy workbooks retain explicit equal-default inputs.
                if (!force && !previousCells.ContainsKey(cellKey) && (text.Length == 0 || text == Text(template[r, 3]) && design.AcceptedRequest is null)) continue;
                if (key == "design.seismic") text = text.Equals("true", StringComparison.OrdinalIgnoreCase) ? "non_seismic_demo_only" : "seismic_required";
                Add(key, scope, scopeId, text);
            }
        }
        if (saved is not null && saved.Ledger.ModelBinding == binding && state.Review!.InputRows > 0)
        {
            var actual = ReadReviewCells(BeamReviewInputProjection.SheetName, state.Review.InputRows, 8);
            var expected = BeamReviewInputProjection.Inputs(saved.Ledger);
            for (var i = 0; i < saved.Ledger.Fields.Count; i++)
            {
                var row = i + 4; var field = saved.Ledger.Fields[i];
                if (Text(actual[row, 0]) != field.SubjectId || Text(actual[row, 1]) != field.Key) throw new InvalidDataException("Review Inputs field identity was edited.");
                var text = Text(actual[row, 2]);
                if (!Changed(BeamReviewInputProjection.SheetName, row + 1, 3) && text == Text(expected[row, 2])) continue;
                var selection = field.Key == "selection.role";
                var subject = selection ? field.SubjectId[(field.SubjectId.IndexOf('/') + 1)..] : field.SubjectId;
                Add(field.Key, selection ? BeamInputScope.Selection : BeamInputScope.Member, subject, text);
            }
        }
        return new(edits, JsonSerializer.Serialize(currentCells));
    }

    public IReadOnlyList<string> SelectedReviewMembers(OfflineDocumentState state, AnalysisSnapshot snapshot)
    {
        if (state.Design?.InputSnapshotSha256 != snapshot.SnapshotSha256) return snapshot.Members.Select(x => x.MemberId).ToArray();
        var rows = ReadReviewCells(BaselineInputSheet.SheetName, state.Design.InputRows, 6);
        var excluded = Enumerable.Range(1, rows.GetLength(0) - 1).Where(r => Text(rows[r, 0]) == "Member" && Text(rows[r, 2]) == "selected" && Text(rows[r, 3]).Equals("false", StringComparison.OrdinalIgnoreCase))
            .Select(r => Text(rows[r, 1])).ToHashSet(StringComparer.Ordinal);
        return snapshot.Members.Where(x => !excluded.Contains(x.MemberId)).Select(x => x.MemberId).ToArray();
    }

    public OfflineDocumentState WriteReviewInputs(OfflineDocumentState state, BeamResolvedReview resolved, bool cancelled = false, string? sheetValuesJson = null,
        AnalysisSnapshot? snapshot = null)
    {
        var rows = BeamReviewInputProjection.Inputs(resolved.Ledger);
        var review = (state.Review ?? new("")) with
        {
            ResolvedJson = JsonSerializer.Serialize(resolved, WorkbookContract.Json),
            InputRows = rows.GetLength(0),
            Status = cancelled ? "Cancelled — refresh only after a new edit or explicit review" : "Inputs resolved; previous result is historical",
            Cancelled = cancelled,
            SheetValuesJson = sheetValuesJson ?? state.Review?.SheetValuesJson ?? "{}"
        };
        var updated = state with { Review = review };
        WriteTransaction(updated, BeamReviewInputProjection.SheetName, rows, state.Review?.InputRows ?? 0, 0);
        if (snapshot is not null && state.Design?.InputSnapshotSha256 == snapshot.SnapshotSha256)
        {
            var legacy = BeamReviewInputProjection.SharedDesignInputs(snapshot, resolved, ReadReviewCells(BaselineInputSheet.SheetName, state.Design.InputRows, 6));
            var cells = JsonSerializer.Deserialize<Dictionary<string, string>>(review.SheetValuesJson)!;
            for (var r = 1; r < legacy.GetLength(0); r++)
            {
                var category = Text(legacy[r, 0]); var field = Text(legacy[r, 2]);
                if (BeamReviewInputProjection.LegacyField(category, field) is null) continue;
                var scopeId = category == "Catalogue" ? "project" : Text(legacy[r, 1]);
                cells["legacy:" + resolved.Ledger.ModelBinding + ":" + category + ":" + scopeId + ":" + field] = Text(legacy[r, 3]);
            }
            review = review with { SheetValuesJson = JsonSerializer.Serialize(cells) };
            updated = updated with { Review = review };
            WriteTransaction(updated, BaselineInputSheet.SheetName, legacy, state.Design.InputRows, 0);
        }
        return MarkReviewPending(updated);
    }

    public OfflineDocumentState MarkReviewPending(OfflineDocumentState state)
    {
        var review = state.Review! with { Status = "Inputs resolved; previous result is historical", Cancelled = false };
        var updated = state with { Review = review };
        if (review.SummaryRows > 0)
        {
            var historical = new object[2, 9];
            historical[0, 0] = "HISTORICAL PROVISIONAL REVIEW — inputs changed or refresh requested";
            historical[1, 0] = review.Status;
            WriteTransaction(updated, BeamReviewInputProjection.SummarySheet, historical, 2, 0);
        }
        else WriteTransaction(updated, null, null, 0, 0);
        return updated;
    }

    public void CommitReviewState(OfflineDocumentState state, BeamReviewWorkbookState review) => WriteTransaction(state with { Review = review }, null, null, 0, 0);

    public void WriteReviewResult(OfflineDocumentState state, BeamReviewResult result, BeamReviewArtifactReference reference, string directory)
    {
        var summary = BeamReviewInputProjection.Summary(result);
        var review = state.Review! with { Result = reference, ResultDirectory = directory, SummaryRows = summary.GetLength(0), Status = "Current provisional review — full design remains separate", Cancelled = false };
        WriteTransaction(state with { Review = review }, BeamReviewInputProjection.SummarySheet, summary, state.Review!.SummaryRows, 0);
        state = ReadState()!;
        var details = BeamReviewInputProjection.Details(result, Path.Combine(directory, reference.FileName));
        WriteTransaction(state with { Review = state.Review! with { DetailRows = details.GetLength(0) } }, BeamReviewInputProjection.DetailSheet, details, state.Review!.DetailRows, 0);
    }

    private object[,] ReadReviewCells(string name, int rows, int columns)
    {
        dynamic? sheet = FindSheet(name); dynamic? range = null;
        try
        {
            if (sheet is null) throw new InvalidDataException("Owned sheet missing: " + name);
            range = SizedRange(sheet, "A1", rows, columns);
            object[,] values = range.Value2; object[,] formulas = range.Formula;
            var result = new object[rows, columns];
            for (var r = 0; r < rows; r++) for (var c = 0; c < columns; c++)
                result[r, c] = Text(formulas[r + 1, c + 1]).StartsWith('=') ? formulas[r + 1, c + 1] : values[r + 1, c + 1];
            return result;
        }
        finally { Release(range); Release(sheet); }
    }
}
