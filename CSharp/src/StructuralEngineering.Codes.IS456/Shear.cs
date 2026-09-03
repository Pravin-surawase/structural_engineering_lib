using StructuralEngineering.Contracts;
using StructuralEngineering.Core;

namespace StructuralEngineering.Codes.IS456;

public static class Shear
{
    public const string CapacityOperation = "is456.beam.shear_capacity/v1";
    private static readonly double[] PercentageRows = [0.15, 0.25, 0.5, 0.75, 1, 1.25, 1.5, 1.75, 2, 2.25, 2.5, 2.75, 3];
    private static readonly IReadOnlyDictionary<int, double[]> TauCColumns = new Dictionary<int, double[]>
    {
        [15] = [0.28, 0.35, 0.46, 0.54, 0.6, 0.64, 0.68, 0.71, 0.71, 0.71, 0.71, 0.71, 0.71],
        [20] = [0.28, 0.36, 0.48, 0.56, 0.62, 0.67, 0.72, 0.75, 0.79, 0.81, 0.82, 0.82, 0.82],
        [25] = [0.29, 0.36, 0.49, 0.57, 0.64, 0.7, 0.74, 0.78, 0.82, 0.85, 0.88, 0.9, 0.92],
        [30] = [0.29, 0.37, 0.5, 0.59, 0.66, 0.71, 0.76, 0.8, 0.84, 0.88, 0.91, 0.94, 0.96],
        [35] = [0.29, 0.37, 0.5, 0.59, 0.67, 0.73, 0.78, 0.82, 0.86, 0.9, 0.93, 0.96, 0.99],
        [40] = [0.3, 0.38, 0.51, 0.6, 0.68, 0.74, 0.79, 0.84, 0.88, 0.92, 0.95, 0.98, 1.01]
    };

    public static ResultEnvelope<ShearCapacityOutput> Capacity(ShearCapacityRequest request)
    {
        var inputs = Inputs(request);
        var provenance = Source(request.CodeDataRevisionId, "is456-shear-capacity-wp02-v1");
        var required = new[]
        {
            request.ResistingWidthMm, request.EffectiveDepthMm,
            request.ConcreteStrengthNPerMm2, request.LongitudinalTensionAreaMm2
        };
        if (required.Any(value => !Validation.Positive(value)))
            return ResultFactory.Rejected<ShearCapacityOutput>(CapacityOperation, inputs, provenance,
                Error("INPUT.RANGE", "Section, material, and longitudinal steel values must be finite and positive.",
                    "capacity_request", "Supply the required values in their declared units."));
        if (request.ConcreteStrengthNPerMm2 is < 15 or > 40)
            return ResultFactory.NotApplicable<ShearCapacityOutput>(CapacityOperation, inputs, provenance,
                Information("PROFILE.UNSUPPORTED", "Concrete grade is outside the WP02 Table 19/20 domain.",
                    "concrete_strength_n_per_mm2", "Use fck from 15 through 40 N/mm2 or another profile."));
        if (request.Link is null)
            return ResultFactory.NotEvaluated<ShearCapacityOutput>(CapacityOperation, inputs, provenance,
                Error("REINFORCEMENT.REQUIRED", "Provided shear capacity requires an actual transverse link.",
                    "link", "Supply the link diameter, active legs, spacing, grade, closure, and centre dimensions."));
        var link = request.Link;
        var activeLegs = request.Axis == ShearAxis.V2 ? link.LegsV2 : link.LegsV3;
        if (string.IsNullOrWhiteSpace(link.LinkId) || !Validation.Positive(link.DiameterMm) ||
            !Validation.Positive(link.SpacingMm) || !Validation.Positive(link.SteelYieldStrengthNPerMm2) || activeLegs < 2)
            return ResultFactory.Rejected<ShearCapacityOutput>(CapacityOperation, inputs, provenance,
                Error("INPUT.RANGE", "The actual link requires an id, positive dimensions and grade, and at least two active legs.",
                    "link", "Resolve a valid link for the requested shear axis."));
        if (link.SteelYieldStrengthNPerMm2 is < 250 or > 500)
            return ResultFactory.NotApplicable<ShearCapacityOutput>(CapacityOperation, inputs, provenance,
                Information("PROFILE.UNSUPPORTED", "Link steel grade is outside the WP02 material domain.",
                    "link.steel_yield_strength_n_per_mm2", "Use fy from 250 through 500 N/mm2 or another profile."));

        var b = request.ResistingWidthMm;
        var d = request.EffectiveDepthMm;
        var percentageActual = 100 * request.LongitudinalTensionAreaMm2 / (b * d);
        var percentageTable = Math.Clamp(percentageActual, 0.15, 3);
        var tauC = TauC(request.ConcreteStrengthNPerMm2, percentageTable);
        var tauCMax = TauCMax(request.ConcreteStrengthNPerMm2);
        var area = LinkArea(link, request.Axis);
        var designFy = Math.Min(415, link.SteelYieldStrengthNPerMm2);
        var concreteCapacity = tauC * b * d / 1000;
        var linkCapacity = 0.87 * designFy * area * d / link.SpacingMm / 1000;
        var limitingCapacity = tauCMax * b * d / 1000;
        var providedCapacity = Math.Min(concreteCapacity + linkCapacity, limitingCapacity);
        var maximumSpacing = Math.Min(0.75 * d, 300);
        var spacingPass = link.SpacingMm <= maximumSpacing + 1e-9;
        var minimumPass = area / (b * link.SpacingMm) + 1e-12 >= 0.4 / (0.87 * designFy);
        var diagnostics = new List<Diagnostic>();
        if (!spacingPass)
            diagnostics.Add(Error("SHEAR.SPACING", "Actual link spacing exceeds the permitted maximum.",
                "link.spacing_mm", "Reduce the link spacing."));
        if (!minimumPass)
            diagnostics.Add(Error("SHEAR.MINIMUM_REINFORCEMENT", "Actual link provision is below minimum shear reinforcement.",
                "link", "Increase active link area or reduce spacing."));
        var output = new ShearCapacityOutput(request.Axis, percentageActual, percentageTable, tauC, tauCMax,
            area, designFy, concreteCapacity, linkCapacity, limitingCapacity, providedCapacity,
            maximumSpacing, spacingPass, minimumPass);
        return ResultFactory.Completed(CapacityOperation, inputs, output, provenance,
            spacingPass && minimumPass ? EngineeringState.Pass : EngineeringState.Fail, [.. diagnostics]);
    }

    public static double TauC(double fck, double percentage)
    {
        var grade = TauCColumns.Keys.Where(value => value <= fck).Max();
        var values = TauCColumns[grade];
        var pt = Math.Clamp(percentage, PercentageRows[0], PercentageRows[^1]);
        for (var index = 0; index < PercentageRows.Length - 1; index++)
        {
            if (pt < PercentageRows[index] || pt > PercentageRows[index + 1]) continue;
            var ratio = (pt - PercentageRows[index]) / (PercentageRows[index + 1] - PercentageRows[index]);
            return values[index] + ratio * (values[index + 1] - values[index]);
        }
        return values[^1];
    }

    public static double TauCMax(double fck)
    {
        var grades = new[] { 15d, 20, 25, 30, 35, 40 };
        var values = new[] { 2.5, 2.8, 3.1, 3.5, 3.7, 4.0 };
        if (fck <= 15) return values[0];
        if (fck >= 40) return values[^1];
        for (var index = 0; index < grades.Length - 1; index++)
        {
            if (fck >= grades[index + 1]) continue;
            var ratio = (fck - grades[index]) / (grades[index + 1] - grades[index]);
            return values[index] + ratio * (values[index + 1] - values[index]);
        }
        return values[^1];
    }

    public static double LinkArea(TransverseLink link, ShearAxis axis)
    {
        var legs = axis == ShearAxis.V2 ? link.LegsV2 : link.LegsV3;
        return legs * Math.PI * link.DiameterMm * link.DiameterMm / 4;
    }

    private static IReadOnlyDictionary<string, EffectiveValue> Inputs(ShearCapacityRequest request) =>
        ResultFactory.Effective(
            ("profile_id", request.ProfileId), ("axis", request.Axis),
            ("resisting_width_mm", request.ResistingWidthMm), ("effective_depth_mm", request.EffectiveDepthMm),
            ("concrete_strength_n_per_mm2", request.ConcreteStrengthNPerMm2),
            ("longitudinal_tension_area_mm2", request.LongitudinalTensionAreaMm2),
            ("link", request.Link), ("code_data_revision_id", request.CodeDataRevisionId));

    private static Diagnostic Error(string code, string message, string field, string remediation) =>
        new(code, "error", message, CapacityOperation, field, "is456-shear", remediation);
    private static Diagnostic Information(string code, string message, string field, string remediation) =>
        new(code, "information", message, CapacityOperation, field, "is456-shear", remediation);
    private static Provenance Source(string revision, string method) =>
        new(revision, method, ["IS 456:2000 normalized WP02 shear and torsion rules"]);
}
