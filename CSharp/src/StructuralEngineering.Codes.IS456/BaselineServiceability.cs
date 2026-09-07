using StructuralEngineering.Contracts;
using StructuralEngineering.Core;

namespace StructuralEngineering.Codes.IS456;

/// <summary>Bounded, actual-bar inputs for the WP11 rectangular baseline profile.</summary>
public static class BaselineServiceability
{
    public const string Figure4TensionFactorOperation = "is456.beam.deflection.tension_factor/v1";
    public const string AnnexFServiceSectionOperation = "is456.beam.service_section.annex_f/v1";
    private const string Revision = "is456-baseline-serviceability-v1";
    private static readonly (double UpperPercentage, double Factor)[] ConservativeFigure4 =
    [(.4, 1.0), (.6, .9), (.8, .8), (1.0, .8), (1.2, .8), (1.4, .7), (1.6, .7),
     (1.8, .7), (2.0, .6), (2.2, .6), (2.4, .6), (2.6, .6), (2.8, .6), (3.0, .6)];

    public static ResultEnvelope<Figure4TensionFactorOutput> Figure4TensionFactor(Figure4TensionFactorRequest request)
    {
        var inputs = ResultFactory.Effective(("request", request));
        var source = Source("is456-figure4-conservative-envelope-wp11-v1", request.CodeDataRevisionId);
        if (!Identity(request.ProfileId, request.MemberId, request.StationId, request.ReinforcementRevisionId, request.UlsActionRowId) ||
            request.CodeDataRevisionId != Revision ||
            !Positive(request.RequiredTensionAreaMm2, request.ProvidedTensionAreaMm2, request.SectionWidthMm, request.EffectiveDepthMm, request.SteelYieldStrengthNPerMm2))
            return Rejected<Figure4TensionFactorOutput>(Figure4TensionFactorOperation, inputs, source, "INPUT.INVALID", "Identity, revision, areas, section dimensions, and steel strength are required.", "request");

        var pt = 100 * request.ProvidedTensionAreaMm2 / (request.SectionWidthMm * request.EffectiveDepthMm);
        var fs = .58 * request.SteelYieldStrengthNPerMm2 * request.RequiredTensionAreaMm2 / request.ProvidedTensionAreaMm2;
        if (pt > 3 || fs > 290)
            return Missing<Figure4TensionFactorOutput>(Figure4TensionFactorOperation, inputs, source, "FIGURE4.OUTSIDE_PROFILE", "Figure 4 conservative-envelope data supports tension steel through 3.0 percent and bounds actual service stress only through 290 N/mm2.", "required/provided_tension_area");

        var selected = ConservativeFigure4.First(item => pt <= item.UpperPercentage + 1e-12);
        return ResultFactory.Completed(Figure4TensionFactorOperation, inputs,
            new Figure4TensionFactorOutput(request.MemberId, request.StationId, request.ReinforcementRevisionId, request.UlsActionRowId,
                pt, fs, 290, selected.Factor, selected.UpperPercentage, "figure4_290_n_per_mm2_lower_envelope_next_higher_percentage"),
            source, EngineeringState.Pass);
    }

    public static ResultEnvelope<AnnexFServiceSectionOutput> AnnexFServiceSection(AnnexFServiceSectionRequest request)
    {
        var inputs = ResultFactory.Effective(("request", request));
        var source = Source("is456-annex-f-cracked-rectangular-wp11-v1", request.CodeDataRevisionId);
        if (!Identity(request.ProfileId, request.MemberId, request.StationId, request.ServiceActionRowId, request.ReinforcementRevisionId) ||
            request.CodeDataRevisionId != Revision || !Positive(request.SectionWidthMm, request.SectionDepthMm, request.ConcreteStrengthNPerMm2, request.SteelModulusNPerMm2, request.SteelYieldStrengthNPerMm2) ||
            !double.IsFinite(request.SignedServiceMomentKnM) || !Enum.IsDefined(request.TensionFace) || !Enum.IsDefined(request.DurationBasis))
            return Rejected<AnnexFServiceSectionOutput>(AnnexFServiceSectionOperation, inputs, source, "INPUT.INVALID", "Identity, current revision, finite service moment, material data, and section data are required.", "request");
        if (request.Bars is not { Count: > 0 })
            return Missing<AnnexFServiceSectionOutput>(AnnexFServiceSectionOperation, inputs, source, "BARS.REQUIRED", "Actual final longitudinal bars are required.", "bars");
        var expectedFace = request.SignedServiceMomentKnM >= 0 ? Face.Bottom : Face.Top;
        if (Math.Abs(request.SignedServiceMomentKnM) > 1e-12 && request.TensionFace != expectedFace)
            return Rejected<AnnexFServiceSectionOutput>(AnnexFServiceSectionOperation, inputs, source, "FACE.MOMENT_MISMATCH", "The declared tension face does not match the signed service moment.", "tension_face");
        var bars = request.Bars.Where(bar => bar.Face == request.TensionFace).ToArray();
        if (bars.Length == 0 || bars.Any(bar => !Text(bar.BarId) || !Positive(bar.DiameterMm) || !double.IsFinite(bar.XFromLeftMm) || !double.IsFinite(bar.YFromTopMm)))
            return Rejected<AnnexFServiceSectionOutput>(AnnexFServiceSectionOperation, inputs, source, "BARS.INVALID", "Actual bars on the physical tension face require identities, positive diameters, and coordinates.", "bars");
        var area = bars.Sum(Area);
        var depths = bars.Select(bar => request.TensionFace == Face.Bottom
            ? bar.YFromTopMm
            : request.SectionDepthMm - bar.YFromTopMm).ToArray();
        var d = bars.Zip(depths, (bar, depth) => Area(bar) * depth).Sum() / area;
        if (!(0 < d && d < request.SectionDepthMm))
            return Rejected<AnnexFServiceSectionOutput>(AnnexFServiceSectionOperation, inputs, source, "DEPTH.INVALID", "Actual tension bars do not resolve an effective depth inside the section.", "bars");

        var ec = 5000 * Math.Sqrt(request.ConcreteStrengthNPerMm2);
        var modular = request.SteelModulusNPerMm2 / ec;
        var moment = Math.Abs(request.SignedServiceMomentKnM) * 1_000_000;
        var q = request.DurationBasis == ServiceDurationBasis.ShortTerm ? 1d : .55d;
        var x = (-modular * area + Math.Sqrt(modular * modular * area * area + 2 * request.SectionWidthMm * modular * area * d)) / request.SectionWidthMm;
        var inertia = request.SectionWidthMm * Math.Pow(x, 3) / 3 +
            modular * bars.Zip(depths, (bar, depth) => Area(bar) * Math.Pow(depth - x, 2)).Sum();
        if (!(0 < x && x < d) || !Positive(inertia))
            return Rejected<AnnexFServiceSectionOutput>(AnnexFServiceSectionOperation, inputs, source, "SECTION.INVALID", "The cracked transformed section did not resolve a physical neutral axis and inertia.", "bars/section");

        var curvature = moment / (ec * inertia);
        var fs = request.SteelModulusNPerMm2 * curvature * (d - x);
        var maximumFs = request.SteelModulusNPerMm2 * curvature * (depths.Max() - x);
        if (maximumFs > .8 * request.SteelYieldStrengthNPerMm2 + 1e-12)
            return Missing<AnnexFServiceSectionOutput>(AnnexFServiceSectionOperation, inputs, source, "STRESS.OUTSIDE_PROFILE", "Annex F baseline scope requires service steel stress no greater than 0.8fy.", "signed_service_moment/steel_yield_strength");
        var epsilon1 = fs / request.SteelModulusNPerMm2 * (request.SectionDepthMm - x) / (d - x);
        var reduction = q * request.SectionWidthMm * Math.Pow(request.SectionDepthMm - x, 2) /
            (3 * request.SteelModulusNPerMm2 * area * (d - x));
        var rawEpsilonM = epsilon1 - reduction;
        var useElasticUpperBound = rawEpsilonM < 0;
        var epsilonM = useElasticUpperBound ? epsilon1 : rawEpsilonM;
        var strainMethod = Math.Abs(request.SignedServiceMomentKnM) <= 1e-12
            ? "zero_service_moment"
            : useElasticUpperBound
                ? "fully_cracked_no_tension_stiffening_upper_bound"
                : "annex_f_tension_stiffening";
        var output = new AnnexFServiceSectionOutput(request.MemberId, request.StationId, request.ServiceActionRowId,
            request.ReinforcementRevisionId, request.TensionFace, area, d, ec, modular, x, inertia, fs, maximumFs,
            epsilon1, epsilonM, q, Math.Abs(request.SignedServiceMomentKnM) <= 1e-12, strainMethod);
        return ResultFactory.Completed(AnnexFServiceSectionOperation, inputs, output, source, EngineeringState.Pass);
    }

    private static double Area(BarCoordinate bar) => Math.PI * bar.DiameterMm * bar.DiameterMm / 4;
    private static bool Positive(params double[] values) => values.All(Validation.Positive);
    private static bool Identity(params string?[] values) => values.All(Text);
    private static bool Text(string? value) => !string.IsNullOrWhiteSpace(value);
    private static Provenance Source(string method, string revision) => new(revision, method,
        ["IS 456:2000 Figure 4 (printed p. 38), Figure 5/6 (printed p. 39), Annex F (printed p. 95)",
         "Controlled source SHA-256: 6ec8f9033bc521420f2f550123edb6f0f444d9d3b7033a87b1b7ec569c143f8d"]);
    private static Diagnostic Error(string operation, string code, string message, string field) =>
        new(code, "error", message, operation, field, "is456-baseline-serviceability", "Supply current bounded serviceability evidence.");
    private static ResultEnvelope<T> Rejected<T>(string operation, IReadOnlyDictionary<string, EffectiveValue> inputs, Provenance source, string code, string message, string field) =>
        ResultFactory.Rejected<T>(operation, inputs, source, Error(operation, code, message, field));
    private static ResultEnvelope<T> Missing<T>(string operation, IReadOnlyDictionary<string, EffectiveValue> inputs, Provenance source, string code, string message, string field) =>
        ResultFactory.NotEvaluated<T>(operation, inputs, source, Error(operation, code, message, field));
}
