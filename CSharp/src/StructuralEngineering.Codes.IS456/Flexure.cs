using StructuralEngineering.Contracts;
using StructuralEngineering.Core;

namespace StructuralEngineering.Codes.IS456;

public static class Flexure
{
    public const string CapacityOperation = "is456.beam.flexural_capacity/v1";

    public static ResultEnvelope<FlexuralCapacityOutput> Capacity(FlexuralCapacityRequest request)
    {
        var inputs = Inputs(request);
        var provenance = Source(request.CodeDataRevisionId, "is456-flexural-capacity-wp01-v3");
        var required = new[]
        {
            request.WebWidthMm, request.DepthMm, request.ConcreteStrengthNPerMm2,
            request.SteelYieldStrengthNPerMm2
        };
        if (required.Any(value => !Validation.Positive(value)) || request.Bars is null || request.Bars.Count == 0)
            return ResultFactory.Rejected<FlexuralCapacityOutput>(CapacityOperation, inputs, provenance,
                Error("INPUT.REQUIRED", "Section, materials, and actual reinforcement must be finite and positive.",
                    "capacity_request", "Supply the complete supported capacity request."));
        if (!double.IsFinite(request.AxialForceKn))
            return ResultFactory.Rejected<FlexuralCapacityOutput>(CapacityOperation, inputs, provenance,
                Error("INPUT.NON_FINITE", "Axial force must be finite.", "axial_force_kn", "Supply a finite axial force."));
        if (Math.Abs(request.AxialForceKn) > 1e-12)
            return ResultFactory.NotApplicable<FlexuralCapacityOutput>(CapacityOperation, inputs, provenance,
                Information("PROFILE.UNSUPPORTED", "The WP01 flexure profile excludes axial-force interaction.",
                    "axial_force_kn", "Use a profile that implements axial-flexural interaction."));
        if (request.SectionKind != SectionKind.Rectangular &&
            (request.FlangeWidthMm is null || request.FlangeThicknessMm is null ||
             !double.IsFinite(request.FlangeWidthMm.Value) || !double.IsFinite(request.FlangeThicknessMm.Value) ||
             request.FlangeWidthMm < request.WebWidthMm || request.FlangeThicknessMm <= 0 ||
             request.FlangeThicknessMm >= request.DepthMm))
            return ResultFactory.Rejected<FlexuralCapacityOutput>(CapacityOperation, inputs, provenance,
                Error("INPUT.RANGE", "A flanged section requires an eligible flange width and thickness.",
                    "flange_width_mm", "Supply bf >= bw and 0 < Df < D."));
        var fy = request.SteelYieldStrengthNPerMm2;
        if (fy < 250 || fy > 550)
            return ResultFactory.NotApplicable<FlexuralCapacityOutput>(CapacityOperation, inputs, provenance,
                Information("PROFILE.UNSUPPORTED", "Steel grade is outside the WP01 IS 456 material domain.",
                    "steel_yield_strength_n_per_mm2", "Use a supported 250-550 N/mm2 grade or another profile."));
        var invalidBar = request.Bars.FirstOrDefault(bar => string.IsNullOrWhiteSpace(bar.BarId) ||
            !Validation.Positive(bar.DiameterMm) || !double.IsFinite(bar.YFromTopMm) ||
            bar.YFromTopMm <= 0 || bar.YFromTopMm >= request.DepthMm);
        if (invalidBar is not null)
            return ResultFactory.Rejected<FlexuralCapacityOutput>(CapacityOperation, inputs, provenance,
                Error("INPUT.RANGE", "Every bar requires a positive diameter and a coordinate inside the section.",
                    $"bars[{invalidBar.BarId}]", "Resolve the actual physical bar geometry."));

        var tension = request.Bars.Where(bar => bar.Face == request.TensionFace).ToArray();
        var compressionFace = request.TensionFace == Face.Bottom ? Face.Top : Face.Bottom;
        var compression = request.Bars.Where(bar => bar.Face == compressionFace).ToArray();
        if (tension.Length == 0)
            return ResultFactory.Rejected<FlexuralCapacityOutput>(CapacityOperation, inputs, provenance,
                Error("AXIS.UNRESOLVED", "The requested tension face has no actual bars.", "tension_face",
                    "Assign bars to the physical tension face."));
        var ast = tension.Sum(Area);
        var asc = compression.Sum(Area);
        var d = DepthFromCompressionFace(request.DepthMm, request.TensionFace, tension);
        double? dPrime = compression.Length == 0
            ? null
            : DepthFromCompressionFace(request.DepthMm, request.TensionFace, compression);
        if (d <= 0 || d >= request.DepthMm || dPrime >= d)
            return ResultFactory.Rejected<FlexuralCapacityOutput>(CapacityOperation, inputs, provenance,
                Error("AXIS.UNRESOLVED", "Bar coordinates do not resolve valid tension and compression depths.",
                    "bars", "Correct the physical face and y-coordinate assignments."));

        double Residual(double x)
        {
            var concrete = ConcreteBlock(request, x, d);
            return concrete.ForceN + BarResponses(request, x).Sum(row => row.NetForceN);
        }
        var low = 1e-9;
        var high = request.DepthMm;
        if (Residual(high) < 0)
            return ResultFactory.NotApplicable<FlexuralCapacityOutput>(CapacityOperation, inputs, provenance,
                Information("PROFILE.UNSUPPORTED",
                    "Supplied tension force cannot equilibrate inside the supported section depth.", "bars",
                    "Revise the arrangement or use a fuller strain-compatibility profile."));
        for (var iteration = 0; iteration < 100; iteration++)
        {
            var mid = (low + high) / 2d;
            if (Residual(mid) >= 0) high = mid; else low = mid;
        }
        var equilibriumX = (low + high) / 2d;
        var extremeDepth = request.Bars.Max(bar => request.TensionFace == Face.Bottom
            ? bar.YFromTopMm : request.DepthMm - bar.YFromTopMm);
        var minimumTensionStrain = fy / (1.15 * 200_000) + 0.002;
        var xuMax = 0.0035 * extremeDepth / (0.0035 + minimumTensionStrain);
        var overReinforced = equilibriumX > xuMax + 1e-8;
        var usedX = equilibriumX;
        var concreteBlock = ConcreteBlock(request, usedX, d);
        var responses = BarResponses(request, usedX);
        var steelMoment = responses.Sum(row => row.NetForceN * (d - row.DepthFromCompressionFaceMm));
        var compressionForce = responses.Sum(row => Math.Max(0, row.NetForceN));
        var capacity = (concreteBlock.MomentNmm + steelMoment) / 1_000_000d;
        var output = new FlexuralCapacityOutput(
            request.TensionFace, capacity, equilibriumX, xuMax, usedX, d, dPrime,
            ast, asc, 0.85 * request.WebWidthMm * d / fy,
            0.04 * request.WebWidthMm * request.DepthMm, concreteBlock.ForceN,
            compressionForce, overReinforced, concreteBlock.UsesFlange)
        {
            BarResponses = responses,
            ForceResidualN = Residual(usedX),
            MaximumTensionStrain = responses.Max(row => -row.Strain),
            MinimumTensionStrain = minimumTensionStrain,
            ExtremeTensionDepthMm = extremeDepth
        };
        var diagnostics = overReinforced
            ? new[] { Error("FLEXURE.OVER_REINFORCED", "The equilibrium neutral axis exceeds the limiting depth.",
                "bars", "Revise the supplied longitudinal reinforcement or section.") }
            : [];
        return ResultFactory.Completed(CapacityOperation, inputs, output, provenance,
            overReinforced ? EngineeringState.Fail : EngineeringState.Pass, diagnostics);
    }

    private static IReadOnlyDictionary<string, EffectiveValue> Inputs(FlexuralCapacityRequest request) =>
        ResultFactory.Effective(
            ("profile_id", request.ProfileId),
            ("section_kind", request.SectionKind),
            ("web_width_mm", request.WebWidthMm),
            ("depth_mm", request.DepthMm),
            ("concrete_strength_n_per_mm2", request.ConcreteStrengthNPerMm2),
            ("steel_yield_strength_n_per_mm2", request.SteelYieldStrengthNPerMm2),
            ("bars", request.Bars),
            ("tension_face", request.TensionFace),
            ("flange_width_mm", request.FlangeWidthMm),
            ("flange_thickness_mm", request.FlangeThicknessMm),
            ("axial_force_kn", request.AxialForceKn),
            ("code_data_revision_id", request.CodeDataRevisionId));

    private static (double ForceN, double MomentNmm, bool UsesFlange) ConcreteBlock(
        FlexuralCapacityRequest request, double x, double d)
    {
        var fck = request.ConcreteStrengthNPerMm2;
        var bw = request.WebWidthMm;
        var usesFlange = request.SectionKind != SectionKind.Rectangular && request.TensionFace == Face.Bottom;
        if (!usesFlange)
        {
            var force = 0.36 * fck * bw * x;
            return (force, force * (d - 0.42 * x), false);
        }
        var bf = request.FlangeWidthMm!.Value;
        var df = request.FlangeThicknessMm!.Value;
        if (x <= df)
        {
            var force = 0.36 * fck * bf * x;
            return (force, force * (d - 0.42 * x), true);
        }
        var yf = Math.Min(df, 0.15 * x + 0.65 * df);
        var webForce = 0.36 * fck * bw * x;
        var flangeForce = 0.45 * fck * (bf - bw) * yf;
        return (webForce + flangeForce,
            webForce * (d - 0.42 * x) + flangeForce * (d - 0.5 * yf), true);
    }

    private static FlexuralBarResponse[] BarResponses(FlexuralCapacityRequest request, double x)
    {
        return request.Bars.Select(bar =>
        {
            var depth = request.TensionFace == Face.Bottom ? bar.YFromTopMm : request.DepthMm - bar.YFromTopMm;
            var strain = 0.0035 * (1 - depth / x);
            var stress = SteelStress(strain, request.SteelYieldStrengthNPerMm2);
            var ratio = Math.Clamp(strain / 0.002, 0, 1);
            var concreteStress = (0.67 / 1.5) * request.ConcreteStrengthNPerMm2 * (2 * ratio - ratio * ratio);
            var area = Area(bar);
            return new FlexuralBarResponse(bar.BarId, bar.Face, bar.Layer, depth, area, strain,
                stress, concreteStress, area * (stress - concreteStress));
        }).ToArray();
    }

    private static double SteelStress(double strain, double fy)
    {
        const double elasticModulus = 200_000;
        var designStrength = fy / 1.15;
        var magnitude = Math.Abs(strain);
        if (Math.Abs(fy - 250) < 0.5)
            return Math.CopySign(Math.Min(magnitude * elasticModulus, designStrength), strain);
        double previousStrain = 0, previousStress = 0;
        // IS 456 Fig 23A: normalized stress fractions and inelastic strains.
        foreach (var (fraction, plasticStrain) in new[]
                 { (0.8, 0.0), (0.85, 0.0001), (0.9, 0.0003), (0.95, 0.0007), (0.975, 0.001), (1.0, 0.002) })
        {
            var pointStress = fraction * designStrength;
            var pointStrain = pointStress / elasticModulus + plasticStrain;
            if (magnitude <= pointStrain)
                return Math.CopySign(previousStress + (pointStress - previousStress) *
                    (magnitude - previousStrain) / (pointStrain - previousStrain), strain);
            previousStrain = pointStrain;
            previousStress = pointStress;
        }
        return Math.CopySign(designStrength, strain);
    }

    private static double DepthFromCompressionFace(double depth, Face tensionFace, IReadOnlyList<BarCoordinate> bars)
    {
        var area = bars.Sum(Area);
        var y = bars.Sum(bar => Area(bar) * bar.YFromTopMm) / area;
        return tensionFace == Face.Bottom ? y : depth - y;
    }

    private static double Area(BarCoordinate bar) => Math.PI * bar.DiameterMm * bar.DiameterMm / 4d;

    private static Diagnostic Error(string code, string message, string field, string remediation) =>
        new(code, "error", message, CapacityOperation, field, "is456-flexure", remediation);
    private static Diagnostic Information(string code, string message, string field, string remediation) =>
        new(code, "information", message, CapacityOperation, field, "is456-flexure", remediation);
    private static Provenance Source(string revision, string method) =>
        new(revision, method, ["IS 456:2000 38.1, Fig 21-23 and Annex G; per-bar section profile"]);
}
