using StructuralEngineering.Contracts;
using StructuralEngineering.Core;

namespace StructuralEngineering.Codes.IS456;

public static class BaselineFlexure
{
    public const string Operation = "is456.beam.rectangular_required_steel/v1";
    public static ResultEnvelope<BaselineRequiredSteelOutput> RequiredSteel(BaselineRequiredSteelRequest r)
    {
        var inputs = ResultFactory.Effective(("request", r));
        var source = new Provenance("is456-wp01-v1", "is456-baseline-singly-required-steel-v1",
            ["IS 456:2000 Annex G rectangular stress block; 26.5.1.1 minimum tension steel; WP01 normalized capacity basis"]);
        if (new[] { r.ProfileId, r.MemberId, r.ActionRowId }.Any(string.IsNullOrWhiteSpace) ||
            new[] { r.WidthMm, r.EffectiveDepthMm, r.ConcreteStrengthNPerMm2, r.SteelYieldStrengthNPerMm2 }.Any(x => !Validation.Positive(x)) ||
            !Validation.Nonnegative(r.MomentMagnitudeKnM) || !Enum.IsDefined(r.TensionFace))
            return ResultFactory.Rejected<BaselineRequiredSteelOutput>(Operation, inputs, source,
                new Diagnostic("INPUT.INVALID", "error", "Complete identities, positive section/material inputs and nonnegative moment are required.", Operation, "request"));
        var fy = r.SteelYieldStrengthNPerMm2;
        if (fy < 250 || fy > 550)
            return ResultFactory.NotApplicable<BaselineRequiredSteelOutput>(Operation, inputs, source,
                new Diagnostic("PROFILE.STEEL_GRADE", "information", "The qualified steel range is 250–550 N/mm².", Operation, "steel_yield_strength_n_per_mm2"));
        var d = r.EffectiveDepthMm;
        var c = .36 * r.ConcreteStrengthNPerMm2 * r.WidthMm;
        var xMax = (Math.Abs(fy - 250) < .5 ? .53 : Math.Abs(fy - 415) < .5 ? .48 :
            Math.Abs(fy - 500) < .5 ? .46 : 700 / (1100 + .87 * fy)) * d;
        var limit = c * xMax * (d - .42 * xMax) / 1e6;
        if (r.MomentMagnitudeKnM > limit + 1e-9)
            return ResultFactory.NotApplicable<BaselineRequiredSteelOutput>(Operation, inputs, source,
                new Diagnostic("PROFILE.SINGLY_REINFORCED_LIMIT", "information", "Demand exceeds the singly reinforced domain at this actual depth.", Operation, "moment_magnitude_knm"));
        // Stable smaller quadratic root of M = .36 fck b x (d - .42 x).
        var m = r.MomentMagnitudeKnM * 1e6;
        var x = m == 0 ? 0 : 2 * m / (c * (d + Math.Sqrt(d * d - 1.68 * m / c)));
        var minimum = .85 * r.WidthMm * d / fy;
        return ResultFactory.Completed(Operation, inputs,
            new BaselineRequiredSteelOutput(r.MemberId, r.ActionRowId, r.TensionFace, d,
                Math.Max(minimum, c * x / (.87 * fy)), minimum, limit, x), source);
    }
}
