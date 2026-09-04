using System.Text.Json;
using StructuralEngineering.Analysis;
using StructuralEngineering.Beam;
using StructuralEngineering.Codes.IS456;
using StructuralEngineering.Construction;
using StructuralEngineering.Contracts;
using StructuralEngineering.Core;
using StructuralEngineering.Optimization;
using StructuralEngineering.Reinforcement;
using StructuralEngineering.Reporting;

namespace StructuralEngineering.ExcelDna;

/// <summary>Strict JSON interchange boundary. It only dispatches to existing pure operations.</summary>
public sealed class WorkbookOperationDispatcher
{
    public WorkbookOperationResult Dispatch(WorkbookOperationRow row)
    {
        try
        {
            return row.OperationSemanticId switch
            {
                "structural.action_snapshot.normalize/v1" => Project(row, ActionNormalizer.NormalizeSnapshot(Read<RawActionSnapshot>(row))),
                "structural.beam_topology.define/v1" => Project(row, BeamTopologyBuilder.Define(Read<BeamTopologyDefinitionRequest>(row))),
                "structural.beam_line.solve/v1" => Project(row, PlanarBeamSolver.SolveBeamLine(Read<BeamLineRequest>(row))),
                "structural.reinforcement.bar_area/v1" => Project(row, ReinforcementOperations.BarArea(Read<BarAreaRequest>(row))),
                "structural.reinforcement.mass_per_length/v1" => Project(row, ReinforcementOperations.MassPerLength(Read<MassPerLengthRequest>(row))),
                "structural.reinforcement.effective_depth/v1" => DispatchEffectiveDepth(row),
                "structural.reinforcement_geometry.evaluate/v1" => Project(row, ReinforcementOperations.EvaluateGeometry(Read<GeometryRequest>(row))),
                "is456.beam.flexural_capacity/v1" => Project(row, Flexure.Capacity(Read<FlexuralCapacityRequest>(row))),
                "is456.beam.flexure.check/v1" => Project(row, BeamOperations.CheckFlexure(Read<FlexureCheckRequest>(row))),
                "is456.beam.shear_capacity/v1" => Project(row, Shear.Capacity(Read<ShearCapacityRequest>(row))),
                "is456.beam.shear.check/v1" => Project(row, BeamOperations.CheckShear(Read<ShearCheckRequest>(row))),
                "is456.beam.torsion.check/v1" => Project(row, BeamOperations.CheckTorsion(Read<TorsionCheckRequest>(row))),
                "is456.beam.deflection_limit/v1" => Project(row, Serviceability.DeflectionLimit(Read<DeflectionLimitRequest>(row))),
                "is456.beam.crack_width_limit/v1" => Project(row, Serviceability.CrackWidthLimit(Read<CrackWidthLimitRequest>(row))),
                "is456.beam.deflection.check/v1" => Project(row, Serviceability.CheckDeflection(Read<DeflectionCheckRequest>(row))),
                "is456.beam.crack_width.check/v1" => Project(row, Serviceability.CheckCrackWidth(Read<CrackWidthCheckRequest>(row))),
                "is456.reinforcement.development_length/v1" => Project(row, Detailing.DevelopmentLength(Read<DevelopmentLengthRequest>(row))),
                "is456.beam.anchorage.check/v1" => Project(row, Detailing.CheckAnchorage(Read<AnchorageCheckRequest>(row))),
                "is456.beam.lap_curtailment.check/v1" => Project(row, Detailing.CheckLapsAndCurtailment(Read<LapCurtailmentCheckRequest>(row))),
                "is456.beam.seismic_detailing.check/v1" => Project(row, Detailing.CheckSeismicDetailing(Read<SeismicDetailingCheckRequest>(row))),
                "structural.reinforcement_arrangement.check/v1" => Project(row, Detailing.CheckReinforcementArrangement(Read<ReinforcementArrangementCheckRequest>(row))),
                _ => Rejected(row, "EXCEL.OPERATION_UNSUPPORTED", "The workbook row names no supported WP01-WP08 operation.")
            };
        }
        catch (JsonException error)
        {
            return Rejected(row, "EXCEL.REQUEST_INVALID", error.Message);
        }
        catch (ArgumentException error)
        {
            return Rejected(row, "EXCEL.REQUEST_INVALID", error.Message);
        }
    }

    public WorkbookOperationResult DispatchProject(string json) =>
        Project(new("project", BeamProjectOperations.Operation, json), BeamProjectOperations.Create(Read<BeamProjectRequest>(json)));

    public WorkbookOperationResult DispatchMember(
        WorkbookMemberDesignSeed seed,
        BeamProject project,
        IReadOnlyList<(WorkbookOperationRow Row, WorkbookOperationResult Result)> leaves)
    {
        try
        {
            var evidence = leaves.Select(item => Evidence(item.Row, item.Result)).ToArray();
            var applicableResultIds = leaves
                .Where(item => item.Row.ExpectedApplicability == ApplicabilityState.Applicable)
                .Select(item => Required(item.Result.ResultId, item.Row.RowId))
                .Order(StringComparer.Ordinal)
                .ToArray();
            var iterations = seed.DepthIterations.Select(item => new EffectiveDepthIteration(
                item.IterationNumber,
                item.ReinforcementRevisionId,
                item.EffectiveDepthMm,
                applicableResultIds,
                item.Converged)).ToArray();
            var request = new MemberDesignRequest(project, seed.MemberId,
                seed.TopologyRevisionId, seed.ActionRevisionId,
                seed.ReinforcementRevisionId, seed.DesignScopeRevisionId,
                seed.ScopeInstances, iterations, evidence);
            return Project(new("member", MemberDesignOperations.Operation,
                JsonSerializer.Serialize(seed, WorkbookContract.Json)),
                MemberDesignOperations.Design(request));
        }
        catch (ArgumentException error)
        {
            return Rejected(new("member", MemberDesignOperations.Operation, string.Empty),
                "EXCEL.LEAF_EVIDENCE_DETACHED", error.Message);
        }
    }

    public WorkbookOperationResult DispatchPaths(string json) =>
        Project(new("paths", BarPathOperations.Operation, json), BarPathOperations.Resolve(Read<BarPathRequest>(json)));

    public WorkbookOperationResult DispatchBbs(string json) =>
        Project(new("bbs", BbsOperations.Operation, json), BbsOperations.Create(Read<BbsRequest>(json)));

    public WorkbookOperationResult DispatchBbs(WorkbookBbsSeed seed, WorkbookOperationResult paths)
    {
        var schedule = Output<BarPathOutput>(paths);
        var request = new BbsRequest(seed.ProfileId, seed.ProjectBasisId, seed.MemberId,
            seed.DetailRevisionId, Required(paths.ResultId, "AO18 result"), PayloadId(schedule),
            schedule, seed.ShapeConvention, seed.StockPolicy, seed.SteelDensityKgPerM3,
            seed.SpliceRecords, seed.LinkZones, seed.StationToleranceMm);
        return Project(new("bbs", BbsOperations.Operation, JsonSerializer.Serialize(seed, WorkbookContract.Json)), BbsOperations.Create(request));
    }

    public WorkbookOperationResult DispatchQuantities(string json) =>
        Project(new("quantities", QuantityOperations.Operation, json), QuantityOperations.Calculate(Read<ConstructionQuantityRequest>(json)));

    public WorkbookOperationResult DispatchQuantities(WorkbookQuantitySeed seed, WorkbookOperationResult bbs)
    {
        var output = Output<BbsOutput>(bbs);
        var request = new ConstructionQuantityRequest(seed.ProfileId, seed.ProjectBasisId,
            seed.MemberId, seed.DetailRevisionId, Required(bbs.ResultId, "AO19 result"),
            PayloadId(output), output, seed.ConcreteOverlapPolicyId,
            seed.FormworkMeasurementPolicyId, seed.ConcreteSegments, seed.FormworkFaces);
        return Project(new("quantities", QuantityOperations.Operation, JsonSerializer.Serialize(seed, WorkbookContract.Json)), QuantityOperations.Calculate(request));
    }

    public WorkbookOperationResult DispatchCost(string json) =>
        Project(new("cost", CostOperations.Operation, json), CostOperations.Estimate(Read<ConstructionCostRequest>(json)));

    public WorkbookOperationResult DispatchCost(WorkbookCostSeed seed, WorkbookOperationResult quantities)
    {
        var output = Output<ConstructionQuantityOutput>(quantities);
        var request = new ConstructionCostRequest(seed.ProfileId, seed.ProjectBasisId,
            seed.MemberId, seed.DetailRevisionId, Required(quantities.ResultId, "AO04 result"),
            PayloadId(output), output, seed.RateProfile);
        return Project(new("cost", CostOperations.Operation, JsonSerializer.Serialize(seed, WorkbookContract.Json)), CostOperations.Estimate(request));
    }

    public WorkbookOperationResult DispatchPackage(string json) =>
        Project(new("package", CalculationPackageOperations.Operation, json), CalculationPackageOperations.Create(Read<CalculationPackageRequest>(json)));

    public WorkbookOperationResult DispatchPackage(WorkbookCalculationPackageSeed seed,
        WorkbookOperationResult member, WorkbookOperationResult paths,
        WorkbookOperationResult bbs, WorkbookOperationResult quantities,
        WorkbookOperationResult? cost)
    {
        var memberOutput = Output<MemberDesignOutput>(member);
        var pathOutput = Output<BarPathOutput>(paths);
        var bbsOutput = Output<BbsOutput>(bbs);
        var quantityOutput = Output<ConstructionQuantityOutput>(quantities);
        var costOutput = cost is null ? null : Output<ConstructionCostOutput>(cost);
        var evidence = memberOutput.LeafQualifications.ToDictionary(
            item => item.Expectation.LeafId, StringComparer.Ordinal);
        var traces = seed.Traces.Select(item =>
        {
            if (!evidence.TryGetValue(item.LeafId, out var qualification))
                throw new ArgumentException($"Trace {item.TraceId} names no current AO17 leaf.");
            var leaf = qualification.Evidence;
            return new CalculationTrace(item.TraceId, item.LeafId, item.RuleReference,
                item.FormulaReference, item.NormalizedSubstitution,
                leaf?.RequiredValue, leaf?.SuppliedValue, leaf?.SelectedValue, leaf?.Unit,
                leaf?.GoverningUtilization, memberOutput.GoverningLeafId == item.LeafId);
        }).ToArray();
        var request = new CalculationPackageRequest(seed.Metadata, seed.PackageProfile,
            memberOutput, Binding(member, memberOutput), pathOutput, Binding(paths, pathOutput),
            bbsOutput, Binding(bbs, bbsOutput), quantityOutput, Binding(quantities, quantityOutput),
            costOutput, costOutput is null || cost is null ? null : Binding(cost, costOutput),
            seed.Assumptions, traces, seed.Drawings, seed.Limitations, seed.HumanActions);
        return Project(new("package", CalculationPackageOperations.Operation,
            JsonSerializer.Serialize(seed, WorkbookContract.Json)), CalculationPackageOperations.Create(request));
    }

    public WorkbookOperationResult DispatchOptimization(string json)
    {
        var request = Read<BeamOptimizationRequest>(json);
        if (request.AnalysisMode != AnalysisMode.FixedActions)
        {
            return NotRun(new("optimization", OptimizationOperations.OptimizeOperation, json), "EXCEL.COUPLED_OPTIMIZATION_BLOCKED", "WP09 supports fixed-action optimization only; coupled reanalysis starts with the ETABS workflow.");
        }
        return Project(new("optimization", OptimizationOperations.OptimizeOperation, json), BeamOptimizationOperations.Optimize(request));
    }

    public WorkbookOperationResult DispatchOptimization(WorkbookOptimizationSeed seed,
        WorkbookOperationResult member, WorkbookOperationResult quantities,
        WorkbookOperationResult? cost)
    {
        var memberOutput = Output<MemberDesignOutput>(member);
        var quantityOutput = Output<ConstructionQuantityOutput>(quantities);
        var costOutput = cost is null ? null : Output<ConstructionCostOutput>(cost);
        var domain = CandidateDomainOperations.Build(seed.Domain);
        if (domain.Outputs is null || domain.Outputs.Candidates.Count != 1)
            return NotRun(new("optimization", OptimizationOperations.OptimizeOperation,
                JsonSerializer.Serialize(seed, WorkbookContract.Json)),
                "EXCEL.FIXED_ACTION_DOMAIN_UNSUPPORTED",
                "The standalone workbook binds one fully evaluated current physical candidate; broader candidate evaluation requires explicit complete evaluation rows.");
        var candidate = domain.Outputs.Candidates[0];
        var referenceMemberBinding = CandidateBinding(member, memberOutput);
        var evaluatedMember = memberOutput with { ReinforcementRevisionId = candidate.CandidateId };
        var evaluationMemberBinding = ReboundCandidateBinding(member, evaluatedMember, candidate.CandidateId);
        var evaluatedQuantities = quantityOutput with { DetailRevisionId = candidate.CandidateId };
        var quantityBinding = ReboundCandidateBinding(quantities, evaluatedQuantities, candidate.CandidateId);
        var evaluatedCost = costOutput is null ? null : costOutput with
        {
            DetailRevisionId = candidate.CandidateId,
            QuantityResultId = quantityBinding.ResultId
        };
        var costBinding = cost is null || evaluatedCost is null
            ? null
            : ReboundCandidateBinding(cost, evaluatedCost, candidate.CandidateId);
        var context = new CandidateRankingContext(seed.Domain.ProjectBasisId,
            seed.Domain.ProfileRevisionId, seed.Domain.MemberId,
            seed.Domain.TopologyRevisionId, seed.Domain.ActionRevisionId,
            seed.Domain.DesignScopeRevisionId, seed.Domain.BaselineAnalysisRevisionId,
            Required(member.ResultId, "AO17 result"), referenceMemberBinding, memberOutput);
        var evaluation = new CandidateEvaluation(candidate.CandidateId,
            seed.Domain.BaselineAnalysisRevisionId, evaluationMemberBinding, evaluatedMember,
            quantityBinding, evaluatedQuantities, costBinding, evaluatedCost);
        var request = new BeamOptimizationRequest(seed.SearchId, context, seed.Domain,
            seed.ObjectiveProfile, AnalysisMode.FixedActions, null,
            seed.EvaluationBudget, seed.StopReason, [evaluation]);
        return Project(new("optimization", OptimizationOperations.OptimizeOperation,
            JsonSerializer.Serialize(seed, WorkbookContract.Json)),
            BeamOptimizationOperations.Optimize(request));
    }

    private WorkbookOperationResult DispatchEffectiveDepth(WorkbookOperationRow row)
    {
        var request = Read<WorkbookEffectiveDepthRequest>(row);
        return Project(row, ReinforcementOperations.EffectiveDepth(request.Geometry, request.TensionFace));
    }

    public static T Deserialize<T>(string json) => Read<T>(json);

    private static T Read<T>(WorkbookOperationRow row) => Read<T>(row.RequestJson);

    private static T Read<T>(string json) => JsonSerializer.Deserialize<T>(json, WorkbookContract.Json)
        ?? throw new JsonException("The request JSON cannot be null.");

    private static WorkbookOperationResult Project<T>(WorkbookOperationRow row, ResultEnvelope<T> result) => new(
        row.RowId, result.OperationSemanticId, result.Execution, result.Applicability,
        result.Engineering, result.Completeness, result.Freshness, result.ResultId,
        result.NormalizedInputId, result.CalculationId, result.Provenance.CodeDataRevisionId,
        result.Provenance.MethodRevisionId,
        result.Outputs is null ? null : JsonSerializer.Serialize(result.Outputs, WorkbookContract.Json),
        result.Diagnostics.Select(diagnostic => new WorkbookDiagnostic(diagnostic.Code,
            diagnostic.Severity, diagnostic.Message, row.RowId, diagnostic.FieldOrLocation)).ToArray());

    private static WorkbookOperationResult Rejected(WorkbookOperationRow row, string code, string message) => new(
        row.RowId, row.OperationSemanticId, ExecutionState.RejectedInput,
        ApplicabilityState.Unknown, EngineeringState.NotEvaluated,
        CompletenessState.Partial, FreshnessState.Unbound, null, null, null, null, null,
        null, [new WorkbookDiagnostic(code, "error", message, row.RowId, "request_json")]);

    private static WorkbookOperationResult NotRun(WorkbookOperationRow row, string code, string message) => new(
        row.RowId, row.OperationSemanticId, ExecutionState.NotRun,
        ApplicabilityState.Unknown, EngineeringState.NotEvaluated,
        CompletenessState.Partial, FreshnessState.Unbound, null, null, null, null, null,
        null, [new WorkbookDiagnostic(code, "error", message, row.RowId)]);

    private static MemberLeafEvidence Evidence(WorkbookOperationRow row, WorkbookOperationResult result)
    {
        if (string.IsNullOrWhiteSpace(row.RuleId) || string.IsNullOrWhiteSpace(row.ScopeId) ||
            row.Scope is null || row.ExpectedApplicability is null ||
            string.IsNullOrWhiteSpace(row.CodeDataBindingId) ||
            result.Execution != ExecutionState.Completed || result.ResultId is null ||
            result.NormalizedInputId is null || result.CalculationId is null ||
            result.ProvenanceCodeDataRevisionId is null || result.ProvenanceMethodRevisionId is null)
            throw new ArgumentException("Every leaf row requires rule, scope, expected applicability, code-data binding, and one completed native envelope.");
        if (!Enum.IsDefined(row.Scope.Value) || !Enum.IsDefined(row.ExpectedApplicability.Value) ||
            string.IsNullOrWhiteSpace(result.OperationSemanticId))
            throw new ArgumentException("Leaf metadata contains an unsupported enum or operation identity.");
        return new MemberLeafEvidence($"{row.RuleId}@{row.ScopeId}", result.OperationSemanticId,
            result.ResultId, result.Execution, result.Applicability, result.Engineering,
            result.Completeness, result.Freshness, result.ProvenanceCodeDataRevisionId,
            result.ProvenanceMethodRevisionId, result.NormalizedInputId,
            result.CalculationId,
            GoverningUtilization: GoverningUtilization(result.OutputJson),
            DiagnosticCodes: result.Diagnostics.Select(item => item.Code).ToArray());
    }

    private static double? GoverningUtilization(string? json)
    {
        if (string.IsNullOrWhiteSpace(json)) return null;
        using var document = JsonDocument.Parse(json);
        foreach (var name in new[] { "governing_utilization", "utilization" })
        {
            if (document.RootElement.TryGetProperty(name, out var value) &&
                value.ValueKind == JsonValueKind.Number && value.TryGetDouble(out var number) &&
                double.IsFinite(number) && number >= 0)
                return number;
        }
        return null;
    }

    private static T Output<T>(WorkbookOperationResult result) =>
        result.OutputJson is null
            ? throw new ArgumentException($"{result.RowId} has no typed output.")
            : Read<T>(result.OutputJson);

    private static string PayloadId<T>(T output) =>
        ResultFactory.SemanticId("output_payload_id", output!);

    private static string Required(string? value, string label) =>
        !string.IsNullOrWhiteSpace(value) ? value : throw new ArgumentException($"{label} identity is required.");

    private static ResultBinding Binding<T>(WorkbookOperationResult result, T output) => new(
        result.OperationSemanticId, Required(result.ResultId, result.RowId),
        Required(result.NormalizedInputId, result.RowId),
        Required(result.CalculationId, result.RowId), result.Execution, result.Applicability,
        result.Engineering, result.Completeness, result.Freshness, PayloadId(output));

    private static CandidateResultBinding CandidateBinding<T>(WorkbookOperationResult result, T output) => new(
        result.OperationSemanticId, Required(result.ResultId, result.RowId),
        Required(result.NormalizedInputId, result.RowId), Required(result.CalculationId, result.RowId),
        result.Execution, result.Applicability, result.Engineering, result.Completeness,
        result.Freshness, PayloadId(output));

    private static CandidateResultBinding ReboundCandidateBinding<T>(
        WorkbookOperationResult source,
        T output,
        string candidateId)
    {
        var sourceResultId = Required(source.ResultId, source.RowId);
        var sourceInputId = Required(source.NormalizedInputId, source.RowId);
        var sourceCalculationId = Required(source.CalculationId, source.RowId);
        return new(source.OperationSemanticId,
            ResultFactory.SemanticId("result_id", new { candidateId, sourceResultId, output }),
            ResultFactory.SemanticId("normalized_input_id", new { candidateId, sourceInputId }),
            ResultFactory.SemanticId("calculation_id", new { candidateId, sourceCalculationId, output }),
            source.Execution, source.Applicability, source.Engineering, source.Completeness,
            source.Freshness, PayloadId(output));
    }
}

public sealed record WorkbookEffectiveDepthRequest(GeometryRequest Geometry, Face TensionFace);
