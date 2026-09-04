using StructuralEngineering.Contracts;
using StructuralEngineering.Core;

namespace StructuralEngineering.Reinforcement;

public static class ReinforcementOperations
{
    public const string BarAreaOperation = "structural.reinforcement.bar_area/v1";
    public const string MassOperation = "structural.reinforcement.mass_per_length/v1";
    public const string DepthOperation = "structural.reinforcement.effective_depth/v1";
    public const string GeometryOperation = "structural.reinforcement_geometry.evaluate/v1";

    public static ResultEnvelope<ScalarOutput> BarArea(BarAreaRequest request)
    {
        var inputs = ResultFactory.Effective(
            ("profile_id", request.ProfileId),
            ("diameter_mm", request.DiameterMm));
        var provenance = Source(request.CodeDataRevisionId, "reinforcement-bar-area-v1");
        if (!Validation.Positive(request.DiameterMm))
            return ResultFactory.Rejected<ScalarOutput>(BarAreaOperation, inputs, provenance,
                Error(BarAreaOperation, "INPUT.RANGE", "Diameter must be finite and greater than zero.",
                    "diameter_mm", "Supply a positive bar diameter in mm."));
        return ResultFactory.Completed(BarAreaOperation, inputs,
            new ScalarOutput(Math.PI * request.DiameterMm * request.DiameterMm / 4d, "mm2"), provenance);
    }

    public static ResultEnvelope<ScalarOutput> MassPerLength(MassPerLengthRequest request)
    {
        var inputs = ResultFactory.Effective(
            ("profile_id", request.ProfileId),
            ("diameter_mm", request.DiameterMm),
            ("density_kg_per_m3", request.DensityKgPerM3));
        var provenance = Source(request.CodeDataRevisionId, "reinforcement-mass-per-length-v1");
        var badField = !Validation.Positive(request.DiameterMm) ? "diameter_mm" :
            !Validation.Positive(request.DensityKgPerM3) ? "density_kg_per_m3" : null;
        if (badField is not null)
            return ResultFactory.Rejected<ScalarOutput>(MassOperation, inputs, provenance,
                Error(MassOperation, "INPUT.RANGE", $"{badField} must be finite and greater than zero.",
                    badField, "Supply the required positive value in its declared unit."));
        var area = Math.PI * request.DiameterMm * request.DiameterMm / 4d;
        return ResultFactory.Completed(MassOperation, inputs,
            new ScalarOutput(area * request.DensityKgPerM3 / 1_000_000d, "kg/m"), provenance);
    }

    public static ResultEnvelope<FaceGeometryOutput> EffectiveDepth(GeometryRequest request, Face tensionFace)
    {
        var inputs = Inputs(request, ("tension_face", tensionFace));
        var provenance = Source(request.CodeDataRevisionId, "reinforcement-actual-geometry-v1");
        var diagnostics = Validate(DepthOperation, request);
        if (diagnostics.Count > 0)
            return ResultFactory.Rejected<FaceGeometryOutput>(DepthOperation, inputs, provenance, [.. diagnostics]);
        var bars = request.Bars.Where(bar => bar.Face == tensionFace).ToArray();
        if (bars.Length == 0)
            return ResultFactory.Rejected<FaceGeometryOutput>(DepthOperation, inputs, provenance,
                Error(DepthOperation, "AXIS.UNRESOLVED",
                    "No bars are assigned to the requested physical tension face.", "tension_face",
                    "Resolve physical faces before calculating effective depth."));
        return ResultFactory.Completed(DepthOperation, inputs, FaceOutput(request.DepthMm, tensionFace, bars), provenance);
    }

    public static ResultEnvelope<GeometryOutput> EvaluateGeometry(GeometryRequest request)
    {
        var inputs = Inputs(request);
        var provenance = Source(request.CodeDataRevisionId, "reinforcement-actual-geometry-v1");
        var invalid = Validate(GeometryOperation, request);
        if (invalid.Count > 0)
            return ResultFactory.Rejected<GeometryOutput>(GeometryOperation, inputs, provenance, [.. invalid]);

        var diagnostics = new List<Diagnostic>();
        var inset = request.NominalCoverMm + request.LinkDiameterMm;
        for (var index = 0; index < request.Bars.Count; index++)
        {
            var bar = request.Bars[index];
            var radius = bar.DiameterMm / 2d;
            if (bar.XFromLeftMm - radius < inset || bar.XFromLeftMm + radius > request.WidthMm - inset ||
                bar.YFromTopMm - radius < inset || bar.YFromTopMm + radius > request.DepthMm - inset)
                diagnostics.Add(Error(GeometryOperation, "GEOMETRY.COVER",
                    "Bar crosses the clear rectangle inside nominal cover and links.", $"bars[{index}]",
                    "Move the bar or revise the section, cover, link, or diameter."));
        }

        double? minimumGap = null;
        string[]? governingPair = null;
        for (var index = 0; index < request.Bars.Count; index++)
        {
            var bar = request.Bars[index];
            for (var previous = 0; previous < index; previous++)
            {
                var other = request.Bars[previous];
                if (bar.Face != other.Face) continue;
                var deltaX = bar.XFromLeftMm - other.XFromLeftMm;
                var deltaY = bar.YFromTopMm - other.YFromTopMm;
                var gap = Math.Sqrt(deltaX * deltaX + deltaY * deltaY) -
                    (bar.DiameterMm + other.DiameterMm) / 2d;
                if (minimumGap is null || gap < minimumGap)
                {
                    minimumGap = gap;
                    governingPair = [other.BarId, bar.BarId];
                }
                if (gap < request.MinimumClearSpacingMm)
                    diagnostics.Add(Error(GeometryOperation, "GEOMETRY.SPACING",
                        "Clear spacing is below the declared minimum.", $"bars[{other.BarId},{bar.BarId}]",
                        "Increase the bar separation or revise the arrangement."));
            }
        }

        var faces = Enum.GetValues<Face>()
            .Select(face => (Face: face, Bars: request.Bars.Where(bar => bar.Face == face).ToArray()))
            .Where(group => group.Bars.Length > 0)
            .ToDictionary(group => group.Face.ToString().ToLowerInvariant(),
                group => FaceOutput(request.DepthMm, group.Face, group.Bars), StringComparer.Ordinal);
        var output = new GeometryOutput(faces, minimumGap, governingPair, request.Bars.Count);
        var engineering = diagnostics.Count == 0 ? EngineeringState.Pass : EngineeringState.Fail;
        return ResultFactory.Completed(GeometryOperation, inputs, output, provenance, engineering, [.. diagnostics]);
    }

    private static IReadOnlyDictionary<string, EffectiveValue> Inputs(
        GeometryRequest request, params (string Key, object? Value)[] extra)
    {
        var values = new List<(string, object?)>
        {
            ("profile_id", request.ProfileId),
            ("width_mm", request.WidthMm),
            ("depth_mm", request.DepthMm),
            ("nominal_cover_mm", request.NominalCoverMm),
            ("link_diameter_mm", request.LinkDiameterMm),
            ("minimum_clear_spacing_mm", request.MinimumClearSpacingMm),
            ("bars", request.Bars),
            ("code_data_revision_id", request.CodeDataRevisionId)
        };
        values.AddRange(extra);
        return ResultFactory.Effective([.. values]);
    }

    private static List<Diagnostic> Validate(string operation, GeometryRequest request)
    {
        var diagnostics = new List<Diagnostic>();
        foreach (var item in new[]
        {
            ("width_mm", request.WidthMm, false),
            ("depth_mm", request.DepthMm, false),
            ("nominal_cover_mm", request.NominalCoverMm, true),
            ("link_diameter_mm", request.LinkDiameterMm, true),
            ("minimum_clear_spacing_mm", request.MinimumClearSpacingMm, true)
        })
        {
            if (!(double.IsFinite(item.Item2) && (item.Item3 ? item.Item2 >= 0 : item.Item2 > 0)))
                diagnostics.Add(Error(operation, "INPUT.RANGE", $"{item.Item1} is outside its finite range.",
                    item.Item1, "Supply a value in mm within the declared range."));
        }
        if (request.Bars is null || request.Bars.Count == 0)
        {
            diagnostics.Add(Error(operation, "INPUT.REQUIRED", "At least one actual bar coordinate is required.",
                "bars", "Supply resolved physical bars."));
            return diagnostics;
        }
        var ids = new HashSet<string>(StringComparer.Ordinal);
        for (var index = 0; index < request.Bars.Count; index++)
        {
            var bar = request.Bars[index];
            var location = $"bars[{index}]";
            if (string.IsNullOrWhiteSpace(bar.BarId))
                diagnostics.Add(Error(operation, "INPUT.REQUIRED", "Every bar requires an identifier.",
                    location + ".bar_id", "Supply a unique non-blank bar identifier."));
            else if (!ids.Add(bar.BarId))
                diagnostics.Add(Error(operation, "INPUT.CONFLICT", "Bar identifiers must be unique.",
                    location + ".bar_id", "Assign a unique identifier to every physical bar."));
            if (!Validation.Positive(bar.DiameterMm) || !double.IsFinite(bar.XFromLeftMm) ||
                !double.IsFinite(bar.YFromTopMm) || bar.Layer < 1)
                diagnostics.Add(Error(operation, "INPUT.RANGE",
                    "Every bar requires a positive diameter, finite coordinates, and a positive layer.", location,
                    "Resolve the actual bar geometry."));
        }
        return diagnostics;
    }

    private static FaceGeometryOutput FaceOutput(double depthMm, Face face, IReadOnlyList<BarCoordinate> bars)
    {
        var area = bars.Sum(Area);
        var x = bars.Sum(bar => Area(bar) * bar.XFromLeftMm) / area;
        var y = bars.Sum(bar => Area(bar) * bar.YFromTopMm) / area;
        var d = face == Face.Bottom ? y : depthMm - y;
        return new FaceGeometryOutput(face, area, x, y, d, bars.Select(bar => bar.BarId).ToArray());
    }

    private static double Area(BarCoordinate bar) => Math.PI * bar.DiameterMm * bar.DiameterMm / 4d;

    private static Diagnostic Error(string operation, string code, string message, string field, string remediation) =>
        new(code, "error", message, operation, field,
            code.StartsWith("INPUT", StringComparison.Ordinal) ? "input-validation" : "geometry", remediation);

    private static Provenance Source(string revision, string method) =>
        new(revision, method, ["IS 456:2000 normalized WP01 rules"]);
}
