using StructuralEngineering.Codes.IS456;
using StructuralEngineering.Contracts;
using StructuralEngineering.Core;

namespace StructuralEngineering.Beam;

public static class BeamOperations
{
    public const string FlexureCheckOperation = "is456.beam.flexure.check/v1";

    public static ResultEnvelope<FlexureCheckOutput> CheckFlexure(FlexureCheckRequest request)
    {
        var inputs = ResultFactory.Effective(
            ("capacity_request", request.Capacity),
            ("positive_design_moment_knm", request.PositiveDesignMomentKnM),
            ("negative_design_moment_knm", request.NegativeDesignMomentKnM));
        var provenance = new Provenance(request.Capacity.CodeDataRevisionId,
            "is456-flexure-check-wp01-v1", ["IS 456:2000 normalized WP01 flexure rules"]);
        var demands = new List<(string Sign, Face Face, double Demand)>();
        if (request.PositiveDesignMomentKnM is { } positive)
        {
            if (!double.IsFinite(positive) || positive < 0)
                return ResultFactory.Rejected<FlexureCheckOutput>(FlexureCheckOperation, inputs, provenance,
                    Error("INPUT.RANGE", "Positive design moment must be finite and nonnegative.",
                        "positive_design_moment_knm", "Supply the positive-moment magnitude in kNm."));
            demands.Add(("positive", Face.Bottom, positive));
        }
        if (request.NegativeDesignMomentKnM is { } negative)
        {
            if (!double.IsFinite(negative) || negative > 0)
                return ResultFactory.Rejected<FlexureCheckOutput>(FlexureCheckOperation, inputs, provenance,
                    Error("INPUT.RANGE", "Negative design moment must be finite and nonpositive.",
                        "negative_design_moment_knm", "Supply the signed negative moment in kNm."));
            demands.Add(("negative", Face.Top, Math.Abs(negative)));
        }
        if (demands.Count == 0)
            return ResultFactory.Rejected<FlexureCheckOutput>(FlexureCheckOperation, inputs, provenance,
                Error("INPUT.REQUIRED", "At least one signed bending demand is required.", "design_moment",
                    "Supply a positive and/or negative design moment."));

        var checks = new List<FlexureSignCheck>();
        var diagnostics = new List<Diagnostic>();
        var anyRejected = false;
        var anyNotApplicable = false;
        foreach (var demand in demands)
        {
            var capacity = Flexure.Capacity(request.Capacity with { TensionFace = demand.Face });
            if (capacity.Execution == ExecutionState.RejectedInput)
            {
                anyRejected = true;
                diagnostics.AddRange(capacity.Diagnostics.Select(ForCheck));
                continue;
            }
            if (capacity.Applicability == ApplicabilityState.NotApplicable)
            {
                anyNotApplicable = true;
                diagnostics.AddRange(capacity.Diagnostics.Select(ForCheck));
                continue;
            }
            var output = capacity.Outputs!;
            var totalArea = output.TensionSteelAreaMm2 + output.CompressionSteelAreaMm2;
            var minimumPass = output.TensionSteelAreaMm2 + 1e-9 >= output.MinimumTensionSteelAreaMm2;
            var maximumPass = totalArea <= output.MaximumTotalSteelAreaMm2 + 1e-9;
            var utilization = demand.Demand / output.CapacityKnM;
            var pass = capacity.Engineering == EngineeringState.Pass && minimumPass && maximumPass &&
                       demand.Demand <= output.CapacityKnM + 1e-9;
            checks.Add(new FlexureSignCheck(demand.Sign, demand.Face, demand.Demand, output.CapacityKnM,
                utilization, minimumPass, maximumPass, capacity.ResultId,
                pass ? EngineeringState.Pass : EngineeringState.Fail));
            diagnostics.AddRange(capacity.Diagnostics.Select(ForCheck));
            if (!pass)
                diagnostics.Add(Error("FLEXURE.FAIL",
                    $"The {demand.Sign} bending check does not satisfy every capacity and reinforcement criterion.",
                    $"{demand.Sign}_design_moment_knm", "Revise the section or actual reinforcement."));
        }
        if (anyRejected)
            return ResultFactory.Rejected<FlexureCheckOutput>(FlexureCheckOperation, inputs, provenance, [.. diagnostics]);
        if (anyNotApplicable)
            return ResultFactory.NotApplicable<FlexureCheckOutput>(FlexureCheckOperation, inputs, provenance, [.. diagnostics]);
        var result = new FlexureCheckOutput(checks, checks.Max(check => check.Utilization));
        var engineering = checks.All(check => check.Engineering == EngineeringState.Pass)
            ? EngineeringState.Pass : EngineeringState.Fail;
        return ResultFactory.Completed(FlexureCheckOperation, inputs, result, provenance, engineering, [.. diagnostics]);
    }

    private static Diagnostic ForCheck(Diagnostic source) => source with { OperationSemanticId = FlexureCheckOperation };
    private static Diagnostic Error(string code, string message, string field, string remediation) =>
        new(code, "error", message, FlexureCheckOperation, field, "is456-flexure", remediation);
}
