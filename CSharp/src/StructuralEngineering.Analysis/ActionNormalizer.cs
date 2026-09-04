using StructuralEngineering.Contracts;
using StructuralEngineering.Core;

namespace StructuralEngineering.Analysis;

public static class ActionNormalizer
{
    public static NormalizedActionRow Normalize(AnalysisActionRow row)
    {
        ValidateIdentity(row.Identity);
        ValidateAxes(row.Axes);
        var values = new[] { row.P, row.V2, row.V3, row.T, row.M2, row.M3 };
        if (values.Any(value => !double.IsFinite(value))) throw new ArgumentException("Action components must be finite.", nameof(row));
        var force = row.ForceUnit == ForceUnit.Kilonewton ? 1000d : 1d;
        var moment = MomentFactor(row.MomentUnit);
        return new(row.Identity, row.ActionBasis, row.Axes, row.P * force, row.V2 * force, row.V3 * force,
            row.T * moment, row.M2 * moment, row.M3 * moment);
    }
    public static ResultEnvelope<ActionSnapshotOutput> NormalizeSnapshot(RawActionSnapshot snapshot)
    {
        const string operation = "structural.action_snapshot.normalize/v1";
        var inputs = ResultFactory.Effective(("snapshot", snapshot));
        var provenance = new Provenance("structural-analysis-wp03-v1", "action-normalization-wp03-v1", ["PF4 action identity and unit conventions"]);
        try
        {
            if (string.IsNullOrWhiteSpace(snapshot.SourceId) || string.IsNullOrWhiteSpace(snapshot.ModelId) || string.IsNullOrWhiteSpace(snapshot.AnalysisEpochId) || string.IsNullOrWhiteSpace(snapshot.ResultEpochId) || snapshot.Rows.Count == 0 || snapshot.LocalAxes.Count == 0) throw new ArgumentException("Snapshot identities, axes, and rows are required.");
            var axes = snapshot.LocalAxes.ToDictionary(a => a.AxisId, StringComparer.Ordinal);
            if (axes.Count != snapshot.LocalAxes.Count) throw new ArgumentException("Axis identities must be unique.");
            foreach (var axis in snapshot.LocalAxes) { if (string.IsNullOrWhiteSpace(axis.AxisId)) throw new ArgumentException("Axis identity is required."); ValidateSnapshotAxes(axis); }
            if (snapshot.Rows.Select(row => row.SourceRowId).Distinct(StringComparer.Ordinal).Count() != snapshot.Rows.Count) throw new ArgumentException("Source row identities must be unique.");
            var force = snapshot.ForceUnit == ForceUnit.Kilonewton ? 1000d : 1d; var moment = MomentFactor(snapshot.MomentUnit); var station = snapshot.StationUnit == StationUnit.Metre ? 1000d : 1d;
            var rows = new List<NormalizedSnapshotActionRow>();
            foreach (var row in snapshot.Rows)
            {
                if (new[] { row.SourceRowId, row.MemberId, row.PhysicalSpanId, row.ObjectId, row.AnalysisElementId, row.AxisId, row.LoadCaseId, row.StepType }.Any(string.IsNullOrWhiteSpace) || !axes.ContainsKey(row.AxisId) || new[] { row.ObjectStation, row.ElementStation, row.P, row.V2, row.V3, row.T, row.M2, row.M3 }.Any(x => !double.IsFinite(x)) || row.StepNumber is { } step && !double.IsFinite(step)) throw new ArgumentException("Every snapshot row requires complete identity, declared axes, and finite values.");
                var normalized = new { source_row_id = row.SourceRowId, source_id = snapshot.SourceId, model_id = snapshot.ModelId, analysis_epoch_id = snapshot.AnalysisEpochId, result_epoch_id = snapshot.ResultEpochId, member_id = row.MemberId, physical_span_id = row.PhysicalSpanId, object_id = row.ObjectId, analysis_element_id = row.AnalysisElementId, axis_id = row.AxisId, object_station_mm = row.ObjectStation * station, element_station_mm = row.ElementStation * station, load_case_id = row.LoadCaseId, step_type = row.StepType, step_number = row.StepNumber, concurrency = row.Concurrency, p_n = row.P * force, v2_n = row.V2 * force, v3_n = row.V3 * force, t_nmm = row.T * moment, m2_nmm = row.M2 * moment, m3_nmm = row.M3 * moment };
                rows.Add(new(ResultFactory.NormalizedInputId(normalized).Replace("normalized_input_id", "action_row_id"), row.SourceRowId, snapshot.SourceId, snapshot.ModelId, snapshot.AnalysisEpochId, snapshot.ResultEpochId, row.MemberId, row.PhysicalSpanId, row.ObjectId, row.AnalysisElementId, row.AxisId, row.ObjectStation * station, row.ElementStation * station, row.LoadCaseId, row.StepType, row.StepNumber, row.Concurrency, row.P * force, row.V2 * force, row.V3 * force, row.T * moment, row.M2 * moment, row.M3 * moment));
            }
            var hashRows = rows.Select(r => new { source_row_id = r.SourceRowId, source_id = r.SourceId, model_id = r.ModelId, analysis_epoch_id = r.AnalysisEpochId, result_epoch_id = r.ResultEpochId, member_id = r.MemberId, physical_span_id = r.PhysicalSpanId, object_id = r.ObjectId, analysis_element_id = r.AnalysisElementId, axis_id = r.AxisId, object_station_mm = r.ObjectStationMm, element_station_mm = r.ElementStationMm, load_case_id = r.LoadCaseId, step_type = r.StepType, step_number = r.StepNumber, concurrency = r.Concurrency, p_n = r.PNewton, v2_n = r.V2Newton, v3_n = r.V3Newton, t_nmm = r.TNewtonMm, m2_nmm = r.M2NewtonMm, m3_nmm = r.M3NewtonMm, row_id = r.RowId }).ToArray();
            var payload = new { source_id = snapshot.SourceId, model_id = snapshot.ModelId, analysis_epoch_id = snapshot.AnalysisEpochId, result_epoch_id = snapshot.ResultEpochId, unit_basis = "mm_n_nmm", local_axes = snapshot.LocalAxes, rows = hashRows };
            return ResultFactory.Completed(operation, inputs, new ActionSnapshotOutput(ResultFactory.NormalizedInputId(payload).Replace("normalized_input_id", "action_snapshot_id"), "mm_n_nmm", snapshot.LocalAxes, rows), provenance);
        }
        catch (ArgumentException e) { var code = e.Message.Contains("axes", StringComparison.OrdinalIgnoreCase) ? "AXIS.INVALID" : "INPUT.INVALID"; return ResultFactory.Rejected<ActionSnapshotOutput>(operation, inputs, provenance, new Diagnostic(code, "error", e.Message, operation, "snapshot", "structural-analysis")); }
    }

    public static void ValidateAxes(LocalAxes axes)
    {
        var x = new[] { axes.Xx, axes.Xy, axes.Xz }; var y = new[] { axes.Yx, axes.Yy, axes.Yz }; var z = new[] { axes.Zx, axes.Zy, axes.Zz };
        if (x.Concat(y).Concat(z).Any(value => !double.IsFinite(value)) || Math.Abs(Dot(x, x) - 1) > 1e-9 || Math.Abs(Dot(y, y) - 1) > 1e-9 || Math.Abs(Dot(z, z) - 1) > 1e-9 || Math.Abs(Dot(x, y)) > 1e-9 || Math.Abs(Dot(x, z)) > 1e-9 || Math.Abs(Dot(y, z)) > 1e-9 || Dot(Cross(x, y), z) < 1 - 1e-9)
            throw new ArgumentException("Local axes must be finite, right-handed, and orthonormal.", nameof(axes));
    }
    private static void ValidateIdentity(AnalysisActionIdentity id) { if (new[] { id.SourceIdentity, id.ModelIdentity, id.CaseIdentity, id.StepIdentity, id.MemberIdentity, id.SpanIdentity, id.ObjectIdentity, id.ElementIdentity, id.StationIdentity, id.ConcurrencyIdentity }.Any(string.IsNullOrWhiteSpace)) throw new ArgumentException("Action identity is incomplete.", nameof(id)); }
    private static double MomentFactor(MomentUnit unit) => unit switch { MomentUnit.NewtonMillimetre => 1, MomentUnit.NewtonMetre => 1000, MomentUnit.KilonewtonMillimetre => 1000, MomentUnit.KilonewtonMetre => 1_000_000, _ => throw new ArgumentOutOfRangeException(nameof(unit)) };
    private static void ValidateSnapshotAxes(SnapshotLocalAxes axes) => ValidateAxes(new(axes.E1.X, axes.E1.Y, axes.E1.Z, axes.E2.X, axes.E2.Y, axes.E2.Z, axes.E3.X, axes.E3.Y, axes.E3.Z));
    private static double Dot(IReadOnlyList<double> a, IReadOnlyList<double> b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
    private static double[] Cross(IReadOnlyList<double> a, IReadOnlyList<double> b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
}
