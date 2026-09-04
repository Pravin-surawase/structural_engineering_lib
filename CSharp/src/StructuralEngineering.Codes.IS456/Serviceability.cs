using StructuralEngineering.Contracts;
using StructuralEngineering.Core;

namespace StructuralEngineering.Codes.IS456;

public static class Serviceability
{
    public const string DeflectionLimitOperation = "is456.beam.deflection_limit/v1";
    public const string CrackWidthLimitOperation = "is456.beam.crack_width_limit/v1";
    public const string DeflectionCheckOperation = "is456.beam.deflection.check/v1";
    public const string CrackWidthCheckOperation = "is456.beam.crack_width.check/v1";
    private const string CodeDataRevision = "is456-wp04-v1";

    public static ResultEnvelope<DeflectionLimitOutput> DeflectionLimit(
        DeflectionLimitRequest request)
    {
        var inputs = Inputs(request);
        var provenance = Source("is456-deflection-limit-wp04-v1", request.CodeDataRevisionId);
        if (!HasText(request.ProfileId) ||
            request.CodeDataRevisionId != CodeDataRevision ||
            !Validation.Positive(request.SpanMm) ||
            !Enum.IsDefined(request.Criterion))
        {
            return Rejected<DeflectionLimitOutput>(
                DeflectionLimitOperation,
                inputs,
                provenance,
                "INPUT.INVALID",
                "Profile, code revision, positive span, and criterion are required.",
                "request",
                "Supply the complete limit request.");
        }

        var codeLimit = request.Criterion == DeflectionCriterion.TotalFinal
            ? request.SpanMm / 250
            : Math.Min(request.SpanMm / 350, 20);
        var selected = SelectLimit(
            DeflectionLimitOperation,
            request.SelectedSource,
            codeLimit,
            request.ProjectLimitMm,
            request.SuppliedLimitMm);
        if (selected.Diagnostic is not null)
            return ResultFactory.Rejected<DeflectionLimitOutput>(
                DeflectionLimitOperation, inputs, provenance, selected.Diagnostic);

        var output = new DeflectionLimitOutput(
            request.Criterion, selected.Value, codeLimit, selected.Source);
        return ResultFactory.Completed(
            DeflectionLimitOperation, inputs, output, provenance);
    }

    public static ResultEnvelope<CrackWidthLimitOutput> CrackWidthLimit(
        CrackWidthLimitRequest request)
    {
        var inputs = Inputs(request);
        var provenance = Source("is456-crack-width-limit-wp04-v1", request.CodeDataRevisionId);
        if (!HasText(request.ProfileId) ||
            request.CodeDataRevisionId != CodeDataRevision ||
            !Enum.IsDefined(request.ExposureClass))
        {
            return Rejected<CrackWidthLimitOutput>(
                CrackWidthLimitOperation,
                inputs,
                provenance,
                "INPUT.INVALID",
                "Profile, code revision, exposure, and harmful-cracking classification are required.",
                "request",
                "Supply the complete crack-limit request.");
        }

        var codeCeiling = request.ExposureClass is
            ExposureClass.VerySevere or ExposureClass.Extreme
                ? 0.1
                : request.CrackingHarmful || request.ExposureClass != ExposureClass.Mild
                    ? 0.2
                    : 0.3;
        var selected = SelectLimit(
            CrackWidthLimitOperation,
            request.SelectedSource,
            codeCeiling,
            request.ProjectLimitMm,
            request.SuppliedLimitMm);
        if (selected.Diagnostic is not null)
            return ResultFactory.Rejected<CrackWidthLimitOutput>(
                CrackWidthLimitOperation, inputs, provenance, selected.Diagnostic);

        var output = new CrackWidthLimitOutput(
            request.ExposureClass,
            request.CrackingHarmful,
            selected.Value,
            codeCeiling,
            selected.Source);
        return ResultFactory.Completed(
            CrackWidthLimitOperation, inputs, output, provenance);
    }

    public static ResultEnvelope<DeflectionCheckOutput> CheckDeflection(
        DeflectionCheckRequest request)
    {
        var inputs = Inputs(request);
        var provenance = Source("is456-deflection-check-wp04-v1", request.CodeDataRevisionId);
        if (!HasText(request.ProfileId) ||
            request.CodeDataRevisionId != CodeDataRevision ||
            !Enum.IsDefined(request.Method))
        {
            return Rejected<DeflectionCheckOutput>(
                DeflectionCheckOperation,
                inputs,
                provenance,
                "INPUT.INVALID",
                "Profile, method, and code-data revision are required.",
                "request",
                "Supply the complete deflection request.");
        }

        if (request.Method == DeflectionMethod.SpanDepthScreening)
            return CheckDeflectionScreening(request, inputs, provenance);

        return CheckCalculatedDeflection(request, inputs, provenance);
    }

    public static ResultEnvelope<CrackWidthCheckOutput> CheckCrackWidth(
        CrackWidthCheckRequest request)
    {
        var inputs = Inputs(request);
        var provenance = Source(
            "is456-annex-f-crack-width-wp04-v1", request.CodeDataRevisionId);
        var identity = new[]
        {
            request.ProfileId,
            request.MemberId,
            request.StationId,
            request.ServiceActionRowId,
            request.ReinforcementRevisionId
        };
        if (identity.Any(value => !HasText(value)) ||
            request.CodeDataRevisionId != CodeDataRevision)
        {
            return Missing<CrackWidthCheckOutput>(
                CrackWidthCheckOperation,
                inputs,
                provenance,
                "Member, service-row, and reinforcement-revision evidence is required.",
                "identity");
        }
        if (request.MeanStrainAtTensionSurface is null)
        {
            return Missing<CrackWidthCheckOutput>(
                CrackWidthCheckOperation,
                inputs,
                provenance,
                "A supplied mean tension-surface strain is required; it is not inferred from fs/Es.",
                "mean_strain_at_tension_surface");
        }
        if (request.Bars is null || request.Bars.Count == 0)
        {
            return Missing<CrackWidthCheckOutput>(
                CrackWidthCheckOperation,
                inputs,
                provenance,
                "Actual positioned reinforcement is required.",
                "bars");
        }
        if (request.Limit is null)
        {
            return Missing<CrackWidthCheckOutput>(
                CrackWidthCheckOperation,
                inputs,
                provenance,
                "An exposure-based crack-width limit is required.",
                "limit");
        }

        var limit = CrackWidthLimit(request.Limit);
        if (limit.Execution != ExecutionState.Completed || limit.Outputs is null)
            return ResultFactory.Rejected<CrackWidthCheckOutput>(
                CrackWidthCheckOperation, inputs, provenance, limit.Diagnostics.ToArray());

        var dimensions = new[]
        {
            request.SectionWidthMm,
            request.SectionDepthMm,
            request.NeutralAxisDepthFromCompressionFaceMm,
            request.SteelYieldStrengthNPerMm2,
            request.SteelModulusNPerMm2
        };
        if (dimensions.Any(value => !Validation.Positive(value)) ||
            !Nonnegative(request.ServiceSteelStressNPerMm2) ||
            !Nonnegative(request.MeanStrainAtTensionSurface) ||
            !Enum.IsDefined(request.TensionFace) ||
            request.SurfacePointXFromLeftMm < 0 ||
            request.SurfacePointXFromLeftMm > request.SectionWidthMm)
        {
            return Rejected<CrackWidthCheckOutput>(
                CrackWidthCheckOperation,
                inputs,
                provenance,
                "INPUT.INVALID",
                "Section, material, stress/strain, tension face, and surface point must be finite and physically valid.",
                "request",
                "Correct the declared crack calculation inputs.");
        }

        foreach (var bar in request.Bars)
        {
            var radius = bar.DiameterMm / 2;
            if (!HasText(bar.BarId) ||
                !Enum.IsDefined(bar.Face) ||
                !Validation.Positive(bar.DiameterMm) ||
                bar.Layer < 1 ||
                bar.XFromLeftMm < radius ||
                bar.XFromLeftMm > request.SectionWidthMm - radius ||
                bar.YFromTopMm < radius ||
                bar.YFromTopMm > request.SectionDepthMm - radius)
            {
                return Rejected<CrackWidthCheckOutput>(
                    CrackWidthCheckOperation,
                    inputs,
                    provenance,
                    "BAR.GEOMETRY",
                    "Every bar surface must fit within the section and retain identity, face, and layer.",
                    $"bars[{bar.BarId}]",
                    "Correct the actual reinforcement arrangement.");
            }
        }

        var tensionBars = request.Bars
            .Where(bar => bar.Face == request.TensionFace)
            .ToArray();
        if (tensionBars.Length == 0)
        {
            return Missing<CrackWidthCheckOutput>(
                CrackWidthCheckOperation,
                inputs,
                provenance,
                "No actual bars are assigned to the physical tension face.",
                "bars");
        }

        var areas = tensionBars
            .Select(bar => Math.PI * bar.DiameterMm * bar.DiameterMm / 4)
            .ToArray();
        var depths = tensionBars
            .Select(bar => request.TensionFace == Face.Bottom
                ? bar.YFromTopMm
                : request.SectionDepthMm - bar.YFromTopMm)
            .ToArray();
        var covers = tensionBars
            .Select(bar => request.TensionFace == Face.Bottom
                ? request.SectionDepthMm - bar.YFromTopMm - bar.DiameterMm / 2
                : bar.YFromTopMm - bar.DiameterMm / 2)
            .ToArray();
        var effectiveDepth = areas
            .Zip(depths, (area, depth) => area * depth)
            .Sum() / areas.Sum();
        var neutralAxis = request.NeutralAxisDepthFromCompressionFaceMm;
        var cmin = covers.Min();
        if (!(0 < neutralAxis &&
              neutralAxis < effectiveDepth &&
              effectiveDepth < request.SectionDepthMm) ||
            cmin <= 0)
        {
            return Rejected<CrackWidthCheckOutput>(
                CrackWidthCheckOperation,
                inputs,
                provenance,
                "SECTION.GEOMETRY",
                "Require 0 < neutral-axis depth < tension-steel effective depth < section depth and positive cover.",
                "neutral_axis/bars",
                "Correct the service section analysis or reinforcement geometry.");
        }

        if (request.ServiceSteelStressNPerMm2 >
            0.8 * request.SteelYieldStrengthNPerMm2)
        {
            return Rejected<CrackWidthCheckOutput>(
                CrackWidthCheckOperation,
                inputs,
                provenance,
                "STRESS.OUTSIDE_PROFILE",
                "Service steel stress exceeds the bounded 0.8fy profile.",
                "service_steel_stress_n_per_mm2",
                "Supply a supported service state or use another method.");
        }

        var elasticSurfaceStrain =
            request.ServiceSteelStressNPerMm2 /
            request.SteelModulusNPerMm2 *
            (request.SectionDepthMm - neutralAxis) /
            (effectiveDepth - neutralAxis);
        if (request.MeanStrainAtTensionSurface > elasticSurfaceStrain + 1e-12)
        {
            return Rejected<CrackWidthCheckOutput>(
                CrackWidthCheckOperation,
                inputs,
                provenance,
                "STRAIN.OUTSIDE_PROFILE",
                "Mean strain exceeds the unmodified elastic tension-surface strain.",
                "mean_strain_at_tension_surface",
                "Reconcile the supplied strain with the service section analysis.");
        }

        var surfaceY = request.TensionFace == Face.Bottom
            ? request.SectionDepthMm
            : 0;
        var nearest = tensionBars
            .Select(bar => new
            {
                Distance = Math.Sqrt(
                    Math.Pow(bar.XFromLeftMm - request.SurfacePointXFromLeftMm, 2) +
                    Math.Pow(bar.YFromTopMm - surfaceY, 2)) - bar.DiameterMm / 2,
                Bar = bar
            })
            .OrderBy(item => item.Distance)
            .First();
        var acr = nearest.Distance;
        var denominator =
            1 + 2 * (acr - cmin) / (request.SectionDepthMm - neutralAxis);
        if (acr < cmin || denominator <= 0)
        {
            return Rejected<CrackWidthCheckOutput>(
                CrackWidthCheckOperation,
                inputs,
                provenance,
                "CRACK_GEOMETRY.INVALID",
                "Derived surface-to-bar geometry is outside the Annex F profile.",
                "surface_point/bars",
                "Correct the surface point and actual bar geometry.");
        }

        var width =
            3 * acr * request.MeanStrainAtTensionSurface.Value / denominator;
        var passed = width <= limit.Outputs.LimitMm;
        var output = new CrackWidthCheckOutput(
            request.MemberId,
            request.StationId,
            request.ServiceActionRowId,
            request.ReinforcementRevisionId,
            request.TensionFace,
            nearest.Bar.BarId,
            effectiveDepth,
            acr,
            cmin,
            neutralAxis,
            request.ServiceSteelStressNPerMm2,
            elasticSurfaceStrain,
            request.MeanStrainAtTensionSurface.Value,
            denominator,
            width,
            limit.Outputs.LimitMm,
            width / limit.Outputs.LimitMm,
            passed);
        Diagnostic[] diagnostics = passed
            ? []
            : new[]
            {
                Error(
                    CrackWidthCheckOperation,
                    "CRACK_WIDTH.LIMIT_EXCEEDED",
                    "Calculated flexural crack width exceeds the selected limit.",
                    "calculated_crack_width_mm",
                    "Revise the actual reinforcement arrangement or section/service response.")
            };
        return ResultFactory.Completed(
            CrackWidthCheckOperation,
            inputs,
            output,
            provenance,
            passed ? EngineeringState.Pass : EngineeringState.Fail,
            diagnostics);
    }

    private static ResultEnvelope<DeflectionCheckOutput> CheckDeflectionScreening(
        DeflectionCheckRequest request,
        IReadOnlyDictionary<string, EffectiveValue> inputs,
        Provenance provenance)
    {
        if (request.Screening is null)
        {
            return Missing<DeflectionCheckOutput>(
                DeflectionCheckOperation,
                inputs,
                provenance,
                "The screening basis is missing.",
                "screening");
        }
        if (request.Calculated is not null ||
            request.TotalLimit is not null ||
            request.AfterFinishesLimit is not null)
        {
            return Rejected<DeflectionCheckOutput>(
                DeflectionCheckOperation,
                inputs,
                provenance,
                "INPUT.CONFLICT",
                "A screening request cannot also contain calculated-deflection inputs or displacement limits.",
                "calculated/limits",
                "Select one method and its matching input branch.");
        }

        var basis = request.Screening;
        var factors = new[]
        {
            basis.TensionSteelModificationFactor,
            basis.CompressionSteelModificationFactor,
            basis.FlangedSectionModificationFactor
        };
        if (!Validation.Positive(basis.EffectiveSpanMm) ||
            basis.EffectiveSpanMm > 10_000 ||
            !Validation.Positive(basis.EffectiveDepthMm) ||
            !Enum.IsDefined(basis.SupportCondition) ||
            factors.Any(value => !Validation.Positive(value)) ||
            !HasText(basis.SpanSupportReference) ||
            !HasText(basis.ModificationFactorsReference))
        {
            return Rejected<DeflectionCheckOutput>(
                DeflectionCheckOperation,
                inputs,
                provenance,
                "SCREENING.INVALID",
                "Screening requires an eligible span, depth, support, explicit positive factors, and references.",
                "screening",
                "Correct the bounded screening basis.");
        }

        var basic = basis.SupportCondition switch
        {
            SupportCondition.Cantilever => 7,
            SupportCondition.SimplySupported => 20,
            SupportCondition.Continuous => 26,
            _ => throw new InvalidOperationException("Validated support condition is unreachable.")
        };
        var actual = basis.EffectiveSpanMm / basis.EffectiveDepthMm;
        var allowable = basic * factors.Aggregate(1d, (value, factor) => value * factor);
        var passed = actual <= allowable;
        var output = new DeflectionCheckOutput(
            request.Method,
            "screening_not_calculated_displacement",
            passed,
            ActualSpanDepthRatio: actual,
            BasicSpanDepthRatio: basic,
            AllowableSpanDepthRatio: allowable);
        var diagnostics = passed
            ? []
            : new[]
            {
                Error(
                    DeflectionCheckOperation,
                    "DEFLECTION.SCREENING_EXCEEDED",
                    "The actual span/depth ratio exceeds the declared modified limit.",
                    "screening",
                    "Increase effective depth or revise the supported design.")
            };
        return ResultFactory.Completed(
            DeflectionCheckOperation,
            inputs,
            output,
            provenance,
            passed ? EngineeringState.Pass : EngineeringState.Fail,
            diagnostics);
    }

    private static ResultEnvelope<DeflectionCheckOutput> CheckCalculatedDeflection(
        DeflectionCheckRequest request,
        IReadOnlyDictionary<string, EffectiveValue> inputs,
        Provenance provenance)
    {
        if (request.Screening is not null)
        {
            return Rejected<DeflectionCheckOutput>(
                DeflectionCheckOperation,
                inputs,
                provenance,
                "INPUT.CONFLICT",
                "A calculated request cannot also contain screening inputs.",
                "screening",
                "Select one method and its matching input branch.");
        }
        if (request.Calculated is null ||
            request.TotalLimit is null ||
            request.AfterFinishesLimit is null)
        {
            return Missing<DeflectionCheckOutput>(
                DeflectionCheckOperation,
                inputs,
                provenance,
                "Calculated deflection requires component evidence and both limits.",
                "calculated/limits");
        }

        var basis = request.Calculated;
        var requiredStrings = new[]
        {
            basis.ServiceActionSnapshotId,
            basis.AnalysisResultId,
            basis.ReinforcementRevisionId,
            basis.StiffnessMethod,
            basis.CrackingMethod,
            basis.CreepMethod,
            basis.ShrinkageMethod
        };
        var history = new[]
        {
            basis.AgeAtLoadingDays,
            basis.FinishInstallationAgeDays,
            basis.AssessmentAgeDays,
            basis.SustainedDurationDays,
            basis.RelativeHumidityPercent,
            basis.NotionalSizeMm,
            basis.DeflectionAtFinishInstallationMm
        };
        if (requiredStrings.Any(value => !HasText(value)) ||
            !HasIdentifiers(basis.TotalServiceActionRowIds) ||
            !HasIdentifiers(basis.SustainedServiceActionRowIds) ||
            history.Any(value => value is null))
        {
            return Missing<DeflectionCheckOutput>(
                DeflectionCheckOperation,
                inputs,
                provenance,
                "The calculated route is missing action, method, load-history, environment, finish, or reinforcement evidence.",
                "calculated");
        }

        var components = new double?[]
        {
            basis.InstantaneousTotalDeflectionMm,
            basis.InstantaneousSustainedDeflectionMm,
            basis.CreepMultiplier,
            basis.ShrinkageDeflectionMm,
            basis.DeflectionAtFinishInstallationMm
        };
        if (components.Any(value => !Nonnegative(value)) ||
            !Validation.Positive(basis.EffectiveSpanMm) ||
            history.Take(4).Any(value => !Positive(value)) ||
            basis.RelativeHumidityPercent is not > 0 or > 100 ||
            !Positive(basis.NotionalSizeMm) ||
            !(basis.AgeAtLoadingDays <= basis.FinishInstallationAgeDays &&
              basis.FinishInstallationAgeDays <= basis.AssessmentAgeDays))
        {
            return Rejected<DeflectionCheckOutput>(
                DeflectionCheckOperation,
                inputs,
                provenance,
                "CALCULATION_BASIS.INVALID",
                "Deflection components/history must be finite, nonnegative, and chronologically valid.",
                "calculated",
                "Correct the explicit calculation basis.");
        }

        var totalLimit = DeflectionLimit(request.TotalLimit);
        var finishLimit = DeflectionLimit(request.AfterFinishesLimit);
        if (totalLimit.Execution != ExecutionState.Completed || totalLimit.Outputs is null)
            return ResultFactory.Rejected<DeflectionCheckOutput>(
                DeflectionCheckOperation, inputs, provenance, totalLimit.Diagnostics.ToArray());
        if (finishLimit.Execution != ExecutionState.Completed || finishLimit.Outputs is null)
            return ResultFactory.Rejected<DeflectionCheckOutput>(
                DeflectionCheckOperation, inputs, provenance, finishLimit.Diagnostics.ToArray());
        if (request.TotalLimit.Criterion != DeflectionCriterion.TotalFinal ||
            request.AfterFinishesLimit.Criterion != DeflectionCriterion.AfterFinishes ||
            request.TotalLimit.SpanMm != request.AfterFinishesLimit.SpanMm ||
            request.TotalLimit.SpanMm != basis.EffectiveSpanMm)
        {
            return Rejected<DeflectionCheckOutput>(
                DeflectionCheckOperation,
                inputs,
                provenance,
                "LIMIT.CONFLICT",
                "Calculated deflection requires matching-span total-final and after-finishes limits.",
                "limits",
                "Supply both criteria for the same effective span.");
        }

        var creep =
            basis.InstantaneousSustainedDeflectionMm * basis.CreepMultiplier;
        var total =
            basis.InstantaneousTotalDeflectionMm +
            creep +
            basis.ShrinkageDeflectionMm;
        var afterFinishes = Math.Max(
            0,
            total - basis.DeflectionAtFinishInstallationMm!.Value);
        var totalPass = total <= totalLimit.Outputs.LimitMm;
        var afterFinishesPass = afterFinishes <= finishLimit.Outputs.LimitMm;
        var passed = totalPass && afterFinishesPass;
        var output = new DeflectionCheckOutput(
            request.Method,
            "calculated_component_aggregation",
            passed,
            InstantaneousTotalDeflectionMm: basis.InstantaneousTotalDeflectionMm,
            InstantaneousSustainedDeflectionMm: basis.InstantaneousSustainedDeflectionMm,
            CreepAdditionalDeflectionMm: creep,
            ShrinkageDeflectionMm: basis.ShrinkageDeflectionMm,
            TotalFinalDeflectionMm: total,
            DeflectionAtFinishInstallationMm: basis.DeflectionAtFinishInstallationMm,
            AfterFinishesDeflectionMm: afterFinishes,
            TotalLimitMm: totalLimit.Outputs.LimitMm,
            AfterFinishesLimitMm: finishLimit.Outputs.LimitMm,
            TotalPass: totalPass,
            AfterFinishesPass: afterFinishesPass,
            ServiceActionSnapshotId: basis.ServiceActionSnapshotId,
            TotalServiceActionRowIds: basis.TotalServiceActionRowIds,
            SustainedServiceActionRowIds: basis.SustainedServiceActionRowIds,
            AnalysisResultId: basis.AnalysisResultId,
            ReinforcementRevisionId: basis.ReinforcementRevisionId);
        Diagnostic[] diagnostics = passed
            ? []
            : new[]
            {
                Error(
                    DeflectionCheckOperation,
                    "DEFLECTION.LIMIT_EXCEEDED",
                    "A calculated total or after-finishes deflection exceeds its limit.",
                    "calculated",
                    "Revise stiffness, geometry, reinforcement, or service response.")
            };
        return ResultFactory.Completed(
            DeflectionCheckOperation,
            inputs,
            output,
            provenance,
            passed ? EngineeringState.Pass : EngineeringState.Fail,
            diagnostics);
    }

    private static (
        double Value,
        string Source,
        Diagnostic? Diagnostic) SelectLimit(
            string operation,
            LimitSource source,
            double codeLimit,
            double? projectLimit,
            double? suppliedLimit)
    {
        if (!Enum.IsDefined(source))
        {
            return (
                codeLimit,
                "code",
                Error(
                    operation,
                    "INPUT.ENUM",
                    "selected_source is invalid.",
                    "selected_source",
                    "Select code, project, or supplied."));
        }
        if (source == LimitSource.Code)
        {
            var diagnostic = projectLimit is not null || suppliedLimit is not null
                ? Error(
                    operation,
                    "INPUT.CONFLICT",
                    "Code source cannot be selected while an override value is supplied.",
                    "selected_source",
                    "Remove overrides or explicitly select their source.")
                : null;
            return (codeLimit, "code", diagnostic);
        }

        var selected = source == LimitSource.Project
            ? projectLimit
            : suppliedLimit;
        var other = source == LimitSource.Project
            ? suppliedLimit
            : projectLimit;
        var field = source == LimitSource.Project
            ? "project_limit_mm"
            : "supplied_limit_mm";
        if (!Positive(selected) || other is not null)
        {
            return (
                codeLimit,
                "code",
                Error(
                    operation,
                    "INPUT.CONFLICT",
                    "Exactly one positive limit must match the explicitly selected source.",
                    field,
                    "Supply one limit and select its source."));
        }
        if (selected > codeLimit)
        {
            return (
                codeLimit,
                "code",
                Error(
                    operation,
                    "LIMIT.EXCEEDS_CODE",
                    "The selected limit exceeds the applicable code ceiling.",
                    field,
                    "Use the code ceiling or a stricter project limit."));
        }
        return (selected.GetValueOrDefault(), source.ToString().ToLowerInvariant(), null);
    }

    private static IReadOnlyDictionary<string, EffectiveValue> Inputs(object request) =>
        ResultFactory.Effective(("request", request));

    private static Provenance Source(string method, string revision) =>
        new(
            revision,
            method,
            [
                "IS 456:2000 serviceability provisions with Amendment 4 exposure ceiling",
                "IS 456 Annex F flexural crack-width relationship"
            ]);

    private static bool HasText(string? value) =>
        !string.IsNullOrWhiteSpace(value);

    private static bool HasIdentifiers(IReadOnlyList<string>? values) =>
        values is { Count: > 0 } && values.All(HasText);

    private static bool Positive(double? value) =>
        value is double number && Validation.Positive(number);

    private static bool Nonnegative(double? value) =>
        value is double number && Validation.Nonnegative(number);

    private static Diagnostic Error(
        string operation,
        string code,
        string message,
        string field,
        string remediation) =>
        new(
            code,
            "error",
            message,
            operation,
            field,
            "is456-serviceability",
            remediation);

    private static ResultEnvelope<TOutput> Rejected<TOutput>(
        string operation,
        IReadOnlyDictionary<string, EffectiveValue> inputs,
        Provenance provenance,
        string code,
        string message,
        string field,
        string remediation) =>
        ResultFactory.Rejected<TOutput>(
            operation,
            inputs,
            provenance,
            Error(operation, code, message, field, remediation));

    private static ResultEnvelope<TOutput> Missing<TOutput>(
        string operation,
        IReadOnlyDictionary<string, EffectiveValue> inputs,
        Provenance provenance,
        string message,
        string field) =>
        ResultFactory.NotEvaluated<TOutput>(
            operation,
            inputs,
            provenance,
            Error(
                operation,
                "EVIDENCE.REQUIRED",
                message,
                field,
                "Supply the named serviceability evidence."));
}
