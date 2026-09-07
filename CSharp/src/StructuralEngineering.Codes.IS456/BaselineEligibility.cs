using StructuralEngineering.Contracts;
using StructuralEngineering.Core;

namespace StructuralEngineering.Codes.IS456;

public static class BaselineEligibility
{
    public const string DurabilityOperation = "is456.beam.durability_cover.check/v1";
    public const string LateralStabilityOperation = "is456.beam.lateral_stability.check/v1";
    private const string Revision = "is456-baseline-eligibility-v1";

    public static ResultEnvelope<BaselineDurabilityOutput> CheckDurability(BaselineDurabilityRequest request)
    {
        var inputs = ResultFactory.Effective(("request", request));
        var source = Source("is456-baseline-durability-cover-wp11-v1", request.CodeDataRevisionId);
        if (!Identity(request.ProfileId, request.MemberId, request.ReinforcementRevisionId) || request.CodeDataRevisionId != Revision ||
            !Positive(request.ConcreteStrengthNPerMm2, request.NominalCoverMm, request.SectionWidthMm, request.SectionDepthMm) || !Enum.IsDefined(request.Exposure))
            return Rejected<BaselineDurabilityOutput>(DurabilityOperation, inputs, source, "INPUT.INVALID", "Identity, exposure, current source revision, material, cover, and section inputs are required.", "request");
        if (request.Bars is not { Count: > 0 } || request.Link is null)
            return Missing<BaselineDurabilityOutput>(DurabilityOperation, inputs, source, "REINFORCEMENT.REQUIRED", "Actual bars and the outer closed link are required.", "bars/link");
        if (!request.Link.Closed || !Positive(request.Link.DiameterMm, request.Link.CentreWidthMm, request.Link.CentreDepthMm) ||
            request.Bars.Any(bar => !Identity(bar.BarId) || !Positive(bar.DiameterMm) || !double.IsFinite(bar.XFromLeftMm) || !double.IsFinite(bar.YFromTopMm)))
            return Rejected<BaselineDurabilityOutput>(DurabilityOperation, inputs, source, "REINFORCEMENT.INVALID", "Actual positioned bars and a closed outer link with positive dimensions are required.", "bars/link");

        var (minimumGrade, tableCover) = request.Exposure switch
        {
            ExposureClass.Mild => (20d, 20d),
            ExposureClass.Moderate => (25d, 30d),
            ExposureClass.Severe => (30d, 45d),
            ExposureClass.VerySevere => (35d, 50d),
            ExposureClass.Extreme => (40d, 75d),
            _ => throw new InvalidOperationException()
        };
        var checks = request.Bars.Select(bar =>
        {
            var actual = Math.Min(Math.Min(bar.XFromLeftMm - bar.DiameterMm / 2, request.SectionWidthMm - bar.XFromLeftMm - bar.DiameterMm / 2),
                Math.Min(bar.YFromTopMm - bar.DiameterMm / 2, request.SectionDepthMm - bar.YFromTopMm - bar.DiameterMm / 2));
            var required = Math.Max(tableCover, bar.DiameterMm);
            return new BaselineCoverCheck(bar.BarId, "longitudinal_bar", actual, required, actual + 1e-9 >= required);
        }).ToList();
        var linkCover = Math.Min((request.SectionWidthMm - request.Link.CentreWidthMm) / 2 - request.Link.DiameterMm / 2,
            (request.SectionDepthMm - request.Link.CentreDepthMm) / 2 - request.Link.DiameterMm / 2);
        var linkRequired = Math.Max(tableCover, request.Link.DiameterMm);
        checks.Add(new BaselineCoverCheck(request.Link.LinkId, "outer_closed_link", linkCover, linkRequired, linkCover + 1e-9 >= linkRequired));
        var declaredRequired = Math.Max(tableCover, request.Bars.Max(bar => bar.DiameterMm));
        checks.Add(new BaselineCoverCheck("declared-nominal-cover", "declared_nominal_cover", request.NominalCoverMm,
            declaredRequired, request.NominalCoverMm + 1e-9 >= declaredRequired));
        var passed = request.ConcreteStrengthNPerMm2 + 1e-9 >= minimumGrade && checks.All(check => check.Passed);
        var diagnostics = new List<Diagnostic>();
        if (request.ConcreteStrengthNPerMm2 + 1e-9 < minimumGrade)
            diagnostics.Add(Error(DurabilityOperation, "DURABILITY.GRADE", "Concrete grade is below the exposure minimum.", "concrete_strength_n_per_mm2"));
        if (checks.Any(check => !check.Passed))
            diagnostics.Add(Error(DurabilityOperation, "DURABILITY.COVER", "Actual cover is below the conservative Table 16/bar-diameter requirement.", "bars/link"));
        return ResultFactory.Completed(DurabilityOperation, inputs,
            new BaselineDurabilityOutput(request.Exposure, request.ConcreteStrengthNPerMm2, minimumGrade, tableCover, checks, passed), source,
            passed ? EngineeringState.Pass : EngineeringState.Fail, diagnostics.ToArray());
    }

    public static ResultEnvelope<BaselineLateralStabilityOutput> CheckLateralStability(BaselineLateralStabilityRequest request)
    {
        var inputs = ResultFactory.Effective(("request", request));
        var source = Source("is456-baseline-lateral-stability-wp11-v1", request.CodeDataRevisionId);
        if (!Identity(request.ProfileId, request.MemberId, request.ReinforcementRevisionId) || request.CodeDataRevisionId != Revision ||
            !Positive(request.WidthMm, request.EffectiveDepthMm, request.UnrestrainedLengthMm))
            return Rejected<BaselineLateralStabilityOutput>(LateralStabilityOperation, inputs, source, "INPUT.INVALID", "Identity, current source revision, width, effective depth, and unrestrained length are required.", "request");
        if (!Identity(request.RestraintEvidenceReference))
            return Missing<BaselineLateralStabilityOutput>(LateralStabilityOperation, inputs, source, "RESTRAINT.EVIDENCE_REQUIRED", "A current physical lateral-restraint evidence reference is required.", "restraint_evidence_reference");
        var widthLimit = 60 * request.WidthMm;
        var depthLimit = 250 * request.WidthMm * request.WidthMm / request.EffectiveDepthMm;
        var governing = Math.Min(widthLimit, depthLimit);
        var passed = request.UnrestrainedLengthMm <= governing + 1e-9;
        return ResultFactory.Completed(LateralStabilityOperation, inputs,
            new BaselineLateralStabilityOutput(request.UnrestrainedLengthMm, request.WidthMm, request.EffectiveDepthMm,
                widthLimit, depthLimit, governing, request.RestraintEvidenceReference!, passed), source,
            passed ? EngineeringState.Pass : EngineeringState.Fail,
            passed ? [] : [Error(LateralStabilityOperation, "LATERAL_STABILITY.EXCEEDED", "Clear distance between lateral restraints exceeds the Clause 23.3 limit.", "unrestrained_length_mm")]);
    }

    private static bool Positive(params double[] values) => values.All(Validation.Positive);
    private static bool Identity(params string?[] values) => values.All(value => !string.IsNullOrWhiteSpace(value));
    private static Provenance Source(string method, string revision) => new(revision, method,
        ["IS 456:2000 Table 5 (printed p. 20), 26.4.1/26.4.2/Table 16 (printed pp. 46-47), 23.3 (printed p. 39)",
         "Controlled source SHA-256: 6ec8f9033bc521420f2f550123edb6f0f444d9d3b7033a87b1b7ec569c143f8d"]);
    private static Diagnostic Error(string operation, string code, string message, string field) =>
        new(code, "error", message, operation, field, "is456-baseline-eligibility", "Supply current bounded eligibility evidence.");
    private static ResultEnvelope<T> Rejected<T>(string operation, IReadOnlyDictionary<string, EffectiveValue> inputs, Provenance source, string code, string message, string field) =>
        ResultFactory.Rejected<T>(operation, inputs, source, Error(operation, code, message, field));
    private static ResultEnvelope<T> Missing<T>(string operation, IReadOnlyDictionary<string, EffectiveValue> inputs, Provenance source, string code, string message, string field) =>
        ResultFactory.NotEvaluated<T>(operation, inputs, source, Error(operation, code, message, field));
}
