using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using StructAutomate.Contracts;
using StructAutomate.Engineering;

namespace StructAutomate.Application;

public static class ForceNormalizer
{
    public static IReadOnlyList<BeamActionRow> Normalize(EtabsForceBatch request)
    {
        ArgumentNullException.ThrowIfNull(request);
        Require.Version(request.SchemaVersion);
        ArgumentNullException.ThrowIfNull(request.Source);
        Require.Text(request.Source.ModelId, "source.modelId");
        Require.Text(request.Source.ModelRevision, "source.modelRevision");
        Require.Text(request.Source.AnalysisRevision, "source.analysisRevision");
        Require.Text(request.Source.EtabsVersion, "source.etabsVersion");
        Require.That(request.Source.AcquiredAtUtc != default && request.Source.AcquiredAtUtc.Offset == TimeSpan.Zero, "source.acquiredAtUtc", "Supply the acquisition timestamp in UTC.");
        Require.That(request.Source.ExportSha256 is { Length: 64 } hash && hash.All(Uri.IsHexDigit), "source.exportSha256", "Supply the source export SHA-256.");
        Require.That(request.IsAnalysisCurrent, "isAnalysisCurrent", "Reanalyse the current model before importing results.", "stale_analysis");
        double force = request.ForceUnit switch { ForceUnit.Newton => .001, ForceUnit.Kilonewton => 1, ForceUnit.PoundForce => .0044482216152605, _ => throw BadUnit("forceUnit") };
        double length = request.LengthUnit switch { LengthUnit.Millimetre => 1, LengthUnit.Metre => 1000, LengthUnit.Inch => 25.4, _ => throw BadUnit("lengthUnit") };
        double moment = request.MomentUnit switch
        {
            MomentUnit.NewtonMillimetre => 1e-6, MomentUnit.NewtonMetre => .001,
            MomentUnit.KilonewtonMillimetre => .001, MomentUnit.KilonewtonMetre => 1,
            MomentUnit.PoundForceInch => .0001129848290276167, MomentUnit.PoundForceFoot => .0013558179483314004,
            _ => throw BadUnit("momentUnit")
        };
        ArgumentNullException.ThrowIfNull(request.Rows);
        ArgumentNullException.ThrowIfNull(request.ObjectAxes);
        Require.That(request.Rows.Count > 0, "rows", "The selected cases contain no force rows.");
        foreach (var pair in request.ObjectAxes) ValidateAxes(pair.Value, "objectAxes." + pair.Key);
        var indices = new HashSet<int>();
        var output = new List<BeamActionRow>(request.Rows.Count);
        var options = ContractJson.CreateOptions();
        foreach (var row in request.Rows)
        {
            var path = $"rows[{row.RowIndex}]";
            Require.That(row.RowIndex >= 0 && indices.Add(row.RowIndex), path, "Source row indices must be nonnegative and unique.");
            Require.Text(row.MemberId, path + ".memberId");
            Require.Text(row.ObjectId, path + ".objectId");
            Require.Text(row.ElementId, path + ".elementId");
            Require.Text(row.OutputCaseName, path + ".outputCaseName");
            Require.That(row.StepType is not null, path + ".stepType", "Use the source step type; an empty string is allowed for static results.");
            ArgumentNullException.ThrowIfNull(row.Selection);
            Require.Text(row.Selection.Id, path + ".selection.id");
            Require.Text(row.Selection.Name, path + ".selection.name");
            Require.That(Enum.IsDefined(row.Selection.Kind), path + ".selection.kind", "Select case or combination.");
            Require.Nonnegative(row.ObjectStation, path + ".objectStation");
            Require.Nonnegative(row.ElementStation, path + ".elementStation");
            foreach (var (name, value) in new[] { ("stepNumber", row.StepNumber), ("p", row.P), ("v2", row.V2), ("v3", row.V3), ("t", row.T), ("m2", row.M2), ("m3", row.M3) }) Require.Finite(value, path + "." + name);
            Require.That(request.ObjectAxes.TryGetValue(row.ObjectId, out var axes), path + ".objectId", "Supply the local axis basis for this object.");
            var identityBytes = JsonSerializer.Serialize(new { request.Source, request.ForceUnit, request.LengthUnit, request.MomentUnit, Row = row, Axes = axes }, options);
            var id = Convert.ToHexStringLower(SHA256.HashData(Encoding.UTF8.GetBytes(identityBytes)));
            var result = new BeamActionRow(id, request.Source, row.RowIndex, row.MemberId, row.ObjectId, row.ObjectStation * length,
                row.ElementId, row.ElementStation * length, row.Selection, row.OutputCaseName, row.StepType!, row.StepNumber,
                row.P * force, row.V2 * force, row.V3 * force, row.T * moment, row.M2 * moment, row.M3 * moment, axes!);
            foreach (var value in new[] { result.ObjectStationMm, result.ElementStationMm, result.PKn, result.V2Kn, result.V3Kn, result.TKnM, result.M2KnM, result.M3KnM }) Require.Finite(value, path);
            output.Add(result);
        }
        return output.ToArray();
    }

    private static InputValidationException BadUnit(string path) => new(new InputProblem("unknown_unit", path, "Select a supported explicit unit."));
    private static double Dot(Vector3 a, Vector3 b) => a.X * b.X + a.Y * b.Y + a.Z * b.Z;
    private static void ValidateAxes(LocalAxes axes, string path)
    {
        ArgumentNullException.ThrowIfNull(axes);
        Vector3[] vectors = [axes.Local1, axes.Local2, axes.Local3];
        foreach (var v in vectors)
        {
            ArgumentNullException.ThrowIfNull(v);
            Require.That(double.IsFinite(Dot(v, v)) && Math.Abs(Dot(v, v) - 1) <= 1e-8, path, "Local axes must be unit vectors.");
        }
        Require.That(Math.Abs(Dot(vectors[0], vectors[1])) <= 1e-8 && Math.Abs(Dot(vectors[1], vectors[2])) <= 1e-8 && Math.Abs(Dot(vectors[0], vectors[2])) <= 1e-8, path, "Local axes must be perpendicular.");
        var a = axes.Local1; var b = axes.Local2;
        var cross = new Vector3(a.Y * b.Z - a.Z * b.Y, a.Z * b.X - a.X * b.Z, a.X * b.Y - a.Y * b.X);
        Require.That(Dot(cross, axes.Local3) >= 1 - 1e-8, path, "Local axes must form a right-handed basis.");
    }
}
