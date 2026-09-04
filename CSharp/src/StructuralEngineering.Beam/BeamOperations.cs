using StructuralEngineering.Codes.IS456;
using StructuralEngineering.Contracts;
using StructuralEngineering.Core;

namespace StructuralEngineering.Beam;

public static class BeamOperations
{
    public const string FlexureCheckOperation = "is456.beam.flexure.check/v1";
    public const string ShearCheckOperation = "is456.beam.shear.check/v1";
    public const string TorsionCheckOperation = "is456.beam.torsion.check/v1";

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

    public static ResultEnvelope<ShearCheckOutput> CheckShear(ShearCheckRequest request)
    {
        var inputs = ResultFactory.Effective(("capacities", request.Capacities), ("demands", request.Demands));
        var provenance = new Provenance("is456-wp02-v1", "is456-shear-check-wp02-v1",
            ["IS 456:2000 normalized WP02 shear and torsion rules"]);
        if (request.Capacities is null || request.Capacities.Count == 0 || request.Demands is null || request.Demands.Count == 0)
            return ResultFactory.Rejected<ShearCheckOutput>(ShearCheckOperation, inputs, provenance,
                Error(ShearCheckOperation, "INPUT.REQUIRED", "At least one capacity and station demand are required.",
                    "capacities", "Supply axis-qualified capacity requests and demands."));
        if (request.Capacities.GroupBy(item => item.Axis).Any(group => group.Count() > 1))
            return ResultFactory.Rejected<ShearCheckOutput>(ShearCheckOperation, inputs, provenance,
                Error(ShearCheckOperation, "INPUT.CONFLICT", "Only one supplied capacity basis is allowed per shear axis.",
                    "capacities", "Remove the duplicate axis capacity."));
        var capacities = request.Capacities.ToDictionary(item => item.Axis, Shear.Capacity);
        foreach (var capacity in capacities.Values)
        {
            if (capacity.Execution == ExecutionState.RejectedInput)
                return ResultFactory.Rejected<ShearCheckOutput>(ShearCheckOperation, inputs, provenance,
                    [.. capacity.Diagnostics.Select(item => ForOperation(item, ShearCheckOperation))]);
            if (capacity.Engineering == EngineeringState.NotEvaluated)
                return ResultFactory.NotEvaluated<ShearCheckOutput>(ShearCheckOperation, inputs, provenance,
                    [.. capacity.Diagnostics.Select(item => ForOperation(item, ShearCheckOperation))]);
            if (capacity.Applicability == ApplicabilityState.NotApplicable)
                return ResultFactory.NotApplicable<ShearCheckOutput>(ShearCheckOperation, inputs, provenance,
                    [.. capacity.Diagnostics.Select(item => ForOperation(item, ShearCheckOperation))]);
        }
        var checks = new List<ShearStationCheck>();
        var diagnostics = new List<Diagnostic>();
        foreach (var demand in request.Demands)
        {
            if (string.IsNullOrWhiteSpace(demand.StationId) || !double.IsFinite(demand.ShearKn))
                return ResultFactory.Rejected<ShearCheckOutput>(ShearCheckOperation, inputs, provenance,
                    Error(ShearCheckOperation, "INPUT.RANGE", "Each station demand requires an id and finite shear.",
                        "demands", "Resolve the station and signed shear in kN."));
            if (!capacities.TryGetValue(demand.Axis, out var capacity))
                return ResultFactory.NotEvaluated<ShearCheckOutput>(ShearCheckOperation, inputs, provenance,
                    Error(ShearCheckOperation, "SHEAR.CAPACITY_MISSING", "No supplied capacity basis exists for a demanded axis.",
                        demand.Axis.ToString(), "Supply the actual section and link capacity basis for this axis."));
            var output = capacity.Outputs!;
            var magnitude = Math.Abs(demand.ShearKn);
            var utilization = magnitude / output.ProvidedCapacityKn;
            var pass = capacity.Engineering == EngineeringState.Pass && magnitude <= output.ProvidedCapacityKn + 1e-9;
            checks.Add(new ShearStationCheck(demand.StationId, demand.Axis, demand.ShearKn,
                output.ProvidedCapacityKn, utilization, capacity.ResultId,
                pass ? EngineeringState.Pass : EngineeringState.Fail));
            if (!pass)
                diagnostics.Add(Error(ShearCheckOperation, "SHEAR.FAIL",
                    "Station shear exceeds supplied capacity or the link arrangement fails.", demand.StationId,
                    "Revise the section or actual transverse reinforcement."));
        }
        var result = new ShearCheckOutput(checks, checks.Max(check => check.Utilization));
        return ResultFactory.Completed(ShearCheckOperation, inputs, result, provenance,
            checks.All(check => check.Engineering == EngineeringState.Pass) ? EngineeringState.Pass : EngineeringState.Fail,
            [.. diagnostics]);
    }

    public static ResultEnvelope<TorsionCheckOutput> CheckTorsion(TorsionCheckRequest request)
    {
        var inputs = ResultFactory.Effective(
            ("profile_id", request.ProfileId), ("action", request.Action),
            ("flexural_capacity", request.FlexuralCapacity), ("link", request.Link),
            ("perimeter_bar_ids", request.PerimeterBarIds),
            ("code_data_revision_id", request.CodeDataRevisionId));
        var provenance = new Provenance(request.CodeDataRevisionId, "is456-torsion-check-wp02-v1",
            ["IS 456:2000 normalized WP02 shear and torsion rules"]);
        var action = request.Action;
        if (action.ActionBasis is not ActionBasis.StaticConcurrent and not ActionBasis.StagedStep)
            return ResultFactory.Rejected<TorsionCheckOutput>(TorsionCheckOperation, inputs, provenance,
                Error(TorsionCheckOperation, "ACTION.CONCURRENCY", "Torsion interaction requires one concurrent action row.",
                    "action.action_basis", "Supply a static concurrent or staged-step row; do not combine component envelopes."));
        var components = new[] { action.V2Kn, action.V3Kn, action.TorsionKnM, action.M2KnM, action.M3KnM };
        if (string.IsNullOrWhiteSpace(action.RowId) || string.IsNullOrWhiteSpace(action.StationId) ||
            string.IsNullOrWhiteSpace(action.SourceIdentity) || components.Any(value => !double.IsFinite(value)))
            return ResultFactory.Rejected<TorsionCheckOutput>(TorsionCheckOperation, inputs, provenance,
                Error(TorsionCheckOperation, "INPUT.RANGE", "The concurrent action row requires identity and finite components.",
                    "action", "Resolve the complete source row."));
        if (Math.Abs(action.V3Kn) > 1e-12 || Math.Abs(action.M2KnM) > 1e-12)
            return ResultFactory.NotApplicable<TorsionCheckOutput>(TorsionCheckOperation, inputs, provenance,
                Information(TorsionCheckOperation, "PROFILE.UNSUPPORTED",
                    "WP02 does not ignore nonzero minor-axis shear or bending interaction.", "action",
                    "Use a profile supporting biaxial torsion interaction."));
        if (request.FlexuralCapacity.SectionKind != SectionKind.Rectangular)
            return ResultFactory.NotApplicable<TorsionCheckOutput>(TorsionCheckOperation, inputs, provenance,
                Information(TorsionCheckOperation, "PROFILE.UNSUPPORTED", "WP02 torsion is limited to solid rectangular sections.",
                    "flexural_capacity.section_kind", "Use a supported rectangular section or another profile."));
        if (request.FlexuralCapacity.ConcreteStrengthNPerMm2 is < 15 or > 40)
            return ResultFactory.NotApplicable<TorsionCheckOutput>(TorsionCheckOperation, inputs, provenance,
                Information(TorsionCheckOperation, "PROFILE.UNSUPPORTED", "Concrete grade is outside the WP02 torsion domain.",
                    "flexural_capacity.concrete_strength_n_per_mm2", "Use fck from 15 through 40 N/mm2 or another profile."));
        if (request.Link is null)
            return ResultFactory.NotEvaluated<TorsionCheckOutput>(TorsionCheckOperation, inputs, provenance,
                Error(TorsionCheckOperation, "REINFORCEMENT.REQUIRED", "Torsion checking requires an actual closed link.",
                    "link", "Supply the closed-link geometry, spacing, active legs, and grade."));
        var link = request.Link;
        if (!link.Closed)
        {
            var output = EmptyTorsion(action);
            return ResultFactory.Completed(TorsionCheckOperation, inputs, output, provenance, EngineeringState.Fail,
                Error(TorsionCheckOperation, "TORSION.CLOSED_LINK_REQUIRED",
                    "Actual transverse reinforcement is not a closed torsion link.", "link.closed",
                    "Provide a closed link around the perimeter reinforcement."));
        }
        var linkValues = new[] { link.DiameterMm, link.SpacingMm, link.SteelYieldStrengthNPerMm2,
            link.CentreWidthMm, link.CentreDepthMm };
        if (linkValues.Any(value => !Validation.Positive(value)) || link.LegsV2 < 2 || link.LegsV3 < 2)
            return ResultFactory.Rejected<TorsionCheckOutput>(TorsionCheckOperation, inputs, provenance,
                Error(TorsionCheckOperation, "INPUT.RANGE", "Closed-link dimensions, active legs, spacing, and grade must be valid.",
                    "link", "Resolve the actual closed-link geometry."));
        if (link.SteelYieldStrengthNPerMm2 is < 250 or > 500)
            return ResultFactory.NotApplicable<TorsionCheckOutput>(TorsionCheckOperation, inputs, provenance,
                Information(TorsionCheckOperation, "PROFILE.UNSUPPORTED", "Link grade is outside the WP02 torsion domain.",
                    "link.steel_yield_strength_n_per_mm2", "Use fy from 250 through 500 N/mm2 or another profile."));

        var bars = request.FlexuralCapacity.Bars;
        var b = request.FlexuralCapacity.WebWidthMm;
        var depth = request.FlexuralCapacity.DepthMm;
        if (link.CentreWidthMm >= b || link.CentreDepthMm >= depth)
            return ResultFactory.Rejected<TorsionCheckOutput>(TorsionCheckOperation, inputs, provenance,
                Error(TorsionCheckOperation, "GEOMETRY.RANGE", "Closed-link centre dimensions must fit inside the section.",
                    "link", "Resolve link centre dimensions within the concrete section."));
        var availableIds = bars.Select(bar => bar.BarId).ToHashSet(StringComparer.Ordinal);
        var perimeterIds = request.PerimeterBarIds.ToHashSet(StringComparer.Ordinal);
        var perimeterBars = bars.Where(bar => perimeterIds.Contains(bar.BarId)).ToArray();
        var topPerimeter = perimeterBars.Where(bar => bar.Face == Face.Top).ToArray();
        var bottomPerimeter = perimeterBars.Where(bar => bar.Face == Face.Bottom).ToArray();
        var fourCorners = topPerimeter.Length >= 2 && bottomPerimeter.Length >= 2 &&
            topPerimeter.Min(bar => bar.XFromLeftMm) < b / 2 && topPerimeter.Max(bar => bar.XFromLeftMm) > b / 2 &&
            bottomPerimeter.Min(bar => bar.XFromLeftMm) < b / 2 && bottomPerimeter.Max(bar => bar.XFromLeftMm) > b / 2;
        var perimeterPass = perimeterIds.Count >= 4 && perimeterIds.IsSubsetOf(availableIds) && fourCorners;
        var activeFace = action.M3KnM >= 0 ? Face.Bottom : Face.Top;
        var activeBars = bars.Where(bar => bar.Face == activeFace).ToArray();
        if (activeBars.Length == 0)
            return ResultFactory.NotEvaluated<TorsionCheckOutput>(TorsionCheckOperation, inputs, provenance,
                Error(TorsionCheckOperation, "REINFORCEMENT.REQUIRED",
                    "The primary bending face has no resolved longitudinal bars.", "flexural_capacity.bars",
                    "Supply actual bars on the primary tension face."));
        var activeArea = activeBars.Sum(bar => Math.PI * bar.DiameterMm * bar.DiameterMm / 4);
        var activeY = activeBars.Sum(bar => Math.PI * bar.DiameterMm * bar.DiameterMm / 4 * bar.YFromTopMm) / activeArea;
        var d = activeFace == Face.Bottom ? activeY : depth - activeY;
        var torsion = Math.Abs(action.TorsionKnM);
        var shear = Math.Abs(action.V2Kn);
        var bending = Math.Abs(action.M3KnM);
        var equivalentShear = shear + 1.6 * torsion * 1000 / b;
        var torsionMoment = torsion * (1 + depth / b) / 1.7;
        var primaryMoment = bending + torsionMoment;
        var oppositeMoment = Math.Max(0, torsionMoment - bending);
        var primaryPositive = action.M3KnM >= 0;
        var flexure = CheckFlexure(new FlexureCheckRequest(request.FlexuralCapacity,
            primaryPositive ? primaryMoment : oppositeMoment,
            primaryPositive ? -oppositeMoment : -primaryMoment));
        if (flexure.Execution == ExecutionState.RejectedInput)
            return ResultFactory.Rejected<TorsionCheckOutput>(TorsionCheckOperation, inputs, provenance,
                [.. flexure.Diagnostics.Select(item => ForOperation(item, TorsionCheckOperation))]);
        if (flexure.Applicability == ApplicabilityState.NotApplicable)
            return ResultFactory.NotApplicable<TorsionCheckOutput>(TorsionCheckOperation, inputs, provenance,
                [.. flexure.Diagnostics.Select(item => ForOperation(item, TorsionCheckOperation))]);
        if (flexure.Engineering == EngineeringState.NotEvaluated)
            return ResultFactory.NotEvaluated<TorsionCheckOutput>(TorsionCheckOperation, inputs, provenance,
                [.. flexure.Diagnostics.Select(item => ForOperation(item, TorsionCheckOperation))]);
        var tensionArea = bars.Where(bar => bar.Face == activeFace)
            .Sum(bar => Math.PI * bar.DiameterMm * bar.DiameterMm / 4);
        var percentage = Math.Clamp(100 * tensionArea / (b * d), 0.15, 3);
        var tauC = Shear.TauC(request.FlexuralCapacity.ConcreteStrengthNPerMm2, percentage);
        var tauCMax = Shear.TauCMax(request.FlexuralCapacity.ConcreteStrengthNPerMm2);
        var tauVe = equivalentShear * 1000 / (b * d);
        var designFy = Math.Min(415, link.SteelYieldStrengthNPerMm2);
        var requiredTorsion = torsion * 1e6 / (link.CentreWidthMm * link.CentreDepthMm * 0.87 * designFy);
        var requiredShear = shear * 1000 / (2.5 * link.CentreDepthMm * 0.87 * designFy);
        var requiredFloor = Math.Max(0, (tauVe - tauC) * b / (0.87 * designFy));
        var required = Math.Max(Math.Max(requiredTorsion + requiredShear, requiredFloor), 0.4 * b / (0.87 * designFy));
        var provided = Shear.LinkArea(link, ShearAxis.V2) / link.SpacingMm;
        var maximumSpacing = new[] { 0.75 * d, 300, link.CentreWidthMm, link.CentreDepthMm,
            (link.CentreWidthMm + link.CentreDepthMm) / 4 }.Min();
        var stressPass = tauVe <= tauCMax + 1e-12;
        var transversePass = provided + 1e-12 >= required && link.SpacingMm <= maximumSpacing + 1e-9;
        var longitudinalPass = flexure.Engineering == EngineeringState.Pass;
        var pass = stressPass && transversePass && longitudinalPass && perimeterPass;
        var diagnostics = new List<Diagnostic>();
        if (!stressPass) diagnostics.Add(Error(TorsionCheckOperation, "TORSION.SECTION_STRESS",
            "Equivalent shear stress exceeds the section limit.", action.StationId, "Increase the section or concrete grade."));
        if (!transversePass) diagnostics.Add(Error(TorsionCheckOperation, "TORSION.TRANSVERSE_REINFORCEMENT",
            "Actual closed links do not satisfy required area per spacing and spacing limits.", "link",
            "Increase closed-link area or reduce spacing."));
        if (!longitudinalPass) diagnostics.Add(Error(TorsionCheckOperation, "TORSION.LONGITUDINAL_REINFORCEMENT",
            "Actual longitudinal reinforcement does not satisfy both equivalent moments.", "flexural_capacity.bars",
            "Revise physical top and bottom longitudinal bars."));
        if (!perimeterPass) diagnostics.Add(Error(TorsionCheckOperation, "TORSION.PERIMETER_REINFORCEMENT",
            "Perimeter reinforcement must resolve at least four identified bars across top and bottom faces.",
            "perimeter_bar_ids", "Identify actual perimeter corner bars enclosed by the closed link."));
        var result = new TorsionCheckOutput(action.RowId, action.StationId, equivalentShear, torsionMoment,
            primaryMoment, oppositeMoment, tauVe, tauC, tauCMax, required, provided, maximumSpacing,
            [.. perimeterIds.Order(StringComparer.Ordinal)], flexure.ResultId, stressPass, transversePass,
            longitudinalPass, perimeterPass);
        return ResultFactory.Completed(TorsionCheckOperation, inputs, result, provenance,
            pass ? EngineeringState.Pass : EngineeringState.Fail, [.. diagnostics]);
    }

    private static TorsionCheckOutput EmptyTorsion(ConcurrentActionRow action) =>
        new(action.RowId, action.StationId, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, [], string.Empty,
            false, false, false, false);

    private static Diagnostic ForCheck(Diagnostic source) => source with { OperationSemanticId = FlexureCheckOperation };
    private static Diagnostic ForOperation(Diagnostic source, string operation) => source with { OperationSemanticId = operation };
    private static Diagnostic Error(string code, string message, string field, string remediation) =>
        Error(FlexureCheckOperation, code, message, field, remediation);
    private static Diagnostic Error(string operation, string code, string message, string field, string remediation) =>
        new(code, "error", message, operation, field, "is456-beam", remediation);
    private static Diagnostic Information(string operation, string code, string message, string field, string remediation) =>
        new(code, "information", message, operation, field, "is456-beam", remediation);
}
