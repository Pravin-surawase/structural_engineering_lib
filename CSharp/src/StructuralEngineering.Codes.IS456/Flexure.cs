using StructuralEngineering.Contracts;
using StructuralEngineering.Core;

namespace StructuralEngineering.Codes.IS456;

public static class Flexure
{
    public const string CapacityOperation = "is456.beam.flexural_capacity/v1";

    public static ResultEnvelope<FlexuralCapacityOutput> Capacity(FlexuralCapacityRequest request)
    {
        var inputs = Inputs(request);
        var provenance = Source(request.CodeDataRevisionId, "is456-flexural-capacity-wp01-v1");
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
            !Validation.Positive(bar.DiameterMm) || !double.IsFinite(bar.YFromTopMm));
        if (invalidBar is not null)
            return ResultFactory.Rejected<FlexuralCapacityOutput>(CapacityOperation, inputs, provenance,
                Error("INPUT.RANGE", "Every bar requires a positive diameter and finite coordinate.",
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

        var tensionForce = 0.87 * fy * ast;
        double Residual(double x)
        {
            var concrete = ConcreteBlock(request, x, d);
            var compressionSteel = CompressionSteel(request, x, d, dPrime, asc);
            return concrete.ForceN + compressionSteel.ForceN - tensionForce;
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
        var xuMax = XuMaxRatio(fy) * d;
        var overReinforced = equilibriumX > xuMax + 1e-8;
        var usedX = Math.Min(equilibriumX, xuMax);
        var concreteBlock = ConcreteBlock(request, usedX, d);
        var compressionBlock = CompressionSteel(request, usedX, d, dPrime, asc);
        var capacity = (concreteBlock.MomentNmm + compressionBlock.MomentNmm) / 1_000_000d;
        var output = new FlexuralCapacityOutput(
            request.TensionFace, capacity, equilibriumX, xuMax, usedX, d, dPrime,
            ast, asc, 0.85 * request.WebWidthMm * d / fy,
            0.04 * request.WebWidthMm * request.DepthMm, concreteBlock.ForceN,
            compressionBlock.ForceN, overReinforced, concreteBlock.UsesFlange);
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

    private static (double ForceN, double MomentNmm) CompressionSteel(
        FlexuralCapacityRequest request, double x, double d, double? dPrime, double area)
    {
        if (dPrime is null || area <= 0 || x <= dPrime) return (0, 0);
        var strain = 0.0035 * (x - dPrime.Value) / x;
        var stress = SteelStress(strain, request.SteelYieldStrengthNPerMm2);
        var netStress = Math.Max(0, stress - 0.446 * request.ConcreteStrengthNPerMm2);
        var force = netStress * area;
        return (force, force * (d - dPrime.Value));
    }

    private static double SteelStress(double strain, double fy)
    {
        const double elasticModulus = 200_000;
        if (Math.Abs(fy - 250) < 0.5) return Math.Min(strain * elasticModulus, 0.87 * fy);
        var points = Math.Abs(fy - 415) < 0.5
            ? new[] { (0.00144, 288.7), (0.00163, 306.7), (0.00192, 324.8), (0.00241, 342.8), (0.00380, 360.9) }
            : Math.Abs(fy - 500) < 0.5
                ? new[] { (0.00174, 347.8), (0.00195, 369.6), (0.00226, 391.3), (0.00277, 413.0), (0.00417, 434.8) }
                : [];
        if (points.Length == 0) return Math.Min(strain * elasticModulus, 0.87 * fy);
        if (strain < points[0].Item1) return strain * elasticModulus;
        for (var index = 0; index < points.Length - 1; index++)
        {
            var first = points[index];
            var second = points[index + 1];
            if (strain >= first.Item1 && strain <= second.Item1)
                return first.Item2 + (second.Item2 - first.Item2) *
                    (strain - first.Item1) / (second.Item1 - first.Item1);
        }
        return points[^1].Item2;
    }

    private static double DepthFromCompressionFace(double depth, Face tensionFace, IReadOnlyList<BarCoordinate> bars)
    {
        var area = bars.Sum(Area);
        var y = bars.Sum(bar => Area(bar) * bar.YFromTopMm) / area;
        return tensionFace == Face.Bottom ? y : depth - y;
    }

    private static double Area(BarCoordinate bar) => Math.PI * bar.DiameterMm * bar.DiameterMm / 4d;
    private static double XuMaxRatio(double fy) => Math.Abs(fy - 250) < 0.5 ? 0.53 :
        Math.Abs(fy - 415) < 0.5 ? 0.48 : Math.Abs(fy - 500) < 0.5 ? 0.46 :
        700 / (1100 + 0.87 * fy);

    private static Diagnostic Error(string code, string message, string field, string remediation) =>
        new(code, "error", message, CapacityOperation, field, "is456-flexure", remediation);
    private static Diagnostic Information(string code, string message, string field, string remediation) =>
        new(code, "information", message, CapacityOperation, field, "is456-flexure", remediation);
    private static Provenance Source(string revision, string method) =>
        new(revision, method, ["IS 456:2000 normalized WP01 flexure rules"]);
}
