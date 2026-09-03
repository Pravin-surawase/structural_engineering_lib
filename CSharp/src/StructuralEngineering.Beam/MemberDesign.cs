using StructuralEngineering.Contracts;
using StructuralEngineering.Core;

namespace StructuralEngineering.Beam;

public static class MemberDesignOperations
{
    public const string Operation = "is456.beam_member.design/v1";

    public static ResultEnvelope<MemberDesignOutput> Design(
        MemberDesignRequest request)
    {
        var normalizedLeaves = request.LeafResults
            .Select(item => item with { DiagnosticCodes = item.DiagnosticCodes ?? [] })
            .ToArray();
        request = request with { LeafResults = normalizedLeaves };
        var inputs = ResultFactory.Effective(("request", request));
        var source = Source(request.Project);

        var projectRequest = new BeamProjectRequest(
            request.Project.Project,
            request.Project.UnitBasis,
            request.Project.CodeDataRevisions,
            request.Project.Profile,
            request.Project.CatalogueRevisions);
        var projectValidation = BeamProjectOperations.Create(projectRequest);
        if (projectValidation.Execution != ExecutionState.Completed ||
            projectValidation.Outputs?.ProjectBasisId != request.Project.ProjectBasisId)
        {
            return Reject(
                inputs,
                source,
                "PROJECT.BASIS_INVALID",
                "The member project is not the validated immutable project basis represented by its identity.",
                "project",
                "Use the exact current output of structural.beam_project.create/v1.");
        }

        if (!AllText(
                request.Project.ProjectBasisId,
                request.MemberId,
                request.TopologyRevisionId,
                request.ActionRevisionId,
                request.ReinforcementRevisionId,
                request.DesignScopeRevisionId))
        {
            return Reject(
                inputs,
                source,
                "MEMBER.IDENTITY",
                "The project, member, topology, action, reinforcement, and scope revisions are required.",
                "request",
                "Bind the calculation to immutable current revisions.");
        }

        var requiredScopes = request.Project.Profile.CheckRules
            .Where(item => item.Scope != CheckScope.Member)
            .Select(item => item.Scope)
            .ToHashSet();
        var scopeKeys = request.ScopeInstances
            .Select(item => (item.Scope, item.ScopeId))
            .ToArray();
        if (request.MemberId.Contains('@', StringComparison.Ordinal) ||
            request.ScopeInstances.Any(item =>
                !Enum.IsDefined(item.Scope) ||
                item.Scope == CheckScope.Member ||
                !Text(item.ScopeId) ||
                item.ScopeId.Contains('@', StringComparison.Ordinal) ||
                !Text(item.SourceRevisionId) ||
                item.SourceRevisionId != request.DesignScopeRevisionId) ||
            scopeKeys.Distinct().Count() != scopeKeys.Length ||
            requiredScopes.Any(scope =>
                request.ScopeInstances.All(item => item.Scope != scope)))
        {
            return Reject(
                inputs,
                source,
                "SCOPE.INVALID",
                "Every non-member rule requires a unique scope instance from the current design-scope revision.",
                "scope_instances",
                "Supply frozen topology-derived scopes without the '@' leaf-id separator.");
        }

        var expected = ExpectedLeaves(request);
        if (expected.Count == 0)
        {
            return Reject(
                inputs,
                source,
                "LEAF.PROFILE_EMPTY",
                "The project profile and supplied scope produce no expected member leaves.",
                "project.profile.check_rules,scope_instances",
                "Correct the project required-check profile or design scope.");
        }

        var expectedIds = expected.Select(item => item.LeafId)
            .ToHashSet(StringComparer.Ordinal);
        var evidenceIds = request.LeafResults.Select(item => item.LeafId).ToArray();
        if (evidenceIds.Distinct(StringComparer.Ordinal).Count() != evidenceIds.Length ||
            request.LeafResults.Any(item =>
                !ValidEvidence(item) || !expectedIds.Contains(item.LeafId)))
        {
            return Reject(
                inputs,
                source,
                "LEAF.EVIDENCE_INVALID",
                "Leaf evidence must be valid, uniquely identified, and present in the profile-derived expected set.",
                "leaf_results",
                "Remove unexpected leaves and correct their identities, states, revisions, and numerical summaries.");
        }

        if (request.DepthIterations.Select((item, index) =>
                item.IterationNumber != index + 1 ||
                !Text(item.ReinforcementRevisionId) ||
                !Validation.Positive(item.EffectiveDepthMm) ||
                item.DependentResultIds.Count == 0 ||
                item.DependentResultIds.Any(value => !Text(value)) ||
                item.DependentResultIds.Distinct(StringComparer.Ordinal).Count() !=
                item.DependentResultIds.Count)
            .Any(invalid => invalid))
        {
            return Reject(
                inputs,
                source,
                "DEPTH.ITERATION_INVALID",
                "Effective-depth iterations must be sequential and bind positive depths to unique dependent results.",
                "depth_iterations",
                "Correct the actual-depth iteration history.");
        }

        var evidenceById = request.LeafResults
            .ToDictionary(item => item.LeafId, StringComparer.Ordinal);
        var qualifications = expected
            .Select(item => Qualify(item, evidenceById.GetValueOrDefault(item.LeafId)))
            .ToArray();
        var diagnostics = qualifications
            .SelectMany(item => item.ReasonCodes.Select(reason =>
                Error(
                    reason,
                    $"Expected member leaf {item.Expectation.LeafId} is not qualified: {reason}.",
                    $"leaf_results[{item.Expectation.LeafId}]",
                    "Recalculate the exact expected leaf against current complete inputs.")))
            .ToList();

        var applicableResultIds = qualifications
            .Where(item =>
                item.Expectation.ExpectedApplicability == ApplicabilityState.Applicable &&
                item.Evidence is not null)
            .Select(item => item.Evidence!.ResultId)
            .Order(StringComparer.Ordinal)
            .ToArray();
        var finalIteration = request.DepthIterations.LastOrDefault();
        var depthResultBindingComplete = finalIteration is not null &&
            finalIteration.DependentResultIds
                .Order(StringComparer.Ordinal)
                .SequenceEqual(applicableResultIds, StringComparer.Ordinal);
        var depthComplete = finalIteration is not null &&
            finalIteration.Converged &&
            finalIteration.ReinforcementRevisionId == request.ReinforcementRevisionId &&
            depthResultBindingComplete;
        if (!depthComplete)
        {
            var otherwiseConverged = finalIteration is not null &&
                finalIteration.Converged &&
                finalIteration.ReinforcementRevisionId == request.ReinforcementRevisionId;
            var code = otherwiseConverged && !depthResultBindingComplete
                ? "DEPTH.RESULT_BINDING"
                : "DEPTH.NOT_CONVERGED";
            diagnostics.Add(Error(
                code,
                "The final effective depth must be converged against the current reinforcement revision and every applicable leaf result.",
                "depth_iterations",
                "Iterate the physical bar arrangement and bind every applicable current leaf result to the final depth."));
        }

        var governing = qualifications
            .Where(item =>
                item.Evidence?.GoverningUtilization is not null &&
                item.ReasonCodes.All(reason => reason == "LEAF.FAIL"))
            .Select(item => item.Evidence!)
            .OrderByDescending(item => item.GoverningUtilization)
            .FirstOrDefault();
        var output = new MemberDesignOutput(
            request.Project.ProjectBasisId,
            request.Project.Profile.RevisionId,
            request.MemberId,
            request.TopologyRevisionId,
            request.ActionRevisionId,
            request.ReinforcementRevisionId,
            request.DesignScopeRevisionId,
            expected,
            qualifications,
            request.DepthIterations,
            governing?.LeafId,
            governing?.ResultId,
            governing?.GoverningUtilization,
            qualifications.All(item => item.Qualified) && depthComplete);

        var hasPartialReason = qualifications
            .SelectMany(item => item.ReasonCodes)
            .Any(reason => reason != "LEAF.FAIL");
        if (hasPartialReason || !depthComplete)
        {
            var freshness = request.LeafResults.Any(item =>
                    item.Freshness == FreshnessState.Stale)
                ? FreshnessState.Stale
                : request.LeafResults.Any(item =>
                    item.Freshness == FreshnessState.Unbound)
                    ? FreshnessState.Unbound
                    : FreshnessState.Current;
            return ResultFactory.Partial(
                Operation,
                inputs,
                output,
                source,
                freshness,
                [.. diagnostics]);
        }

        var engineering = qualifications.Any(item =>
            item.ReasonCodes.Contains("LEAF.FAIL", StringComparer.Ordinal))
                ? EngineeringState.Fail
                : EngineeringState.Pass;
        return ResultFactory.Completed(
            Operation,
            inputs,
            output,
            source,
            engineering,
            [.. diagnostics]);
    }

    private static IReadOnlyList<MemberLeafExpectation> ExpectedLeaves(
        MemberDesignRequest request)
    {
        var scopes = new Dictionary<CheckScope, List<string>>
        {
            [CheckScope.Member] = [request.MemberId]
        };
        foreach (var instance in request.ScopeInstances)
        {
            if (!scopes.TryGetValue(instance.Scope, out var ids))
            {
                ids = [];
                scopes[instance.Scope] = ids;
            }
            ids.Add(instance.ScopeId);
        }

        var codeRevisions = request.Project.CodeDataRevisions
            .ToDictionary(
                item => item.BindingId,
                item => item.RevisionId,
                StringComparer.Ordinal);
        return request.Project.Profile.CheckRules
            .SelectMany(rule =>
                scopes.GetValueOrDefault(rule.Scope, [])
                    .Order(StringComparer.Ordinal)
                    .Select(scopeId => new MemberLeafExpectation(
                        $"{rule.RuleId}@{scopeId}",
                        rule.RuleId,
                        rule.OperationSemanticId,
                        scopeId,
                        rule.Scope,
                        rule.ExpectedApplicability,
                        rule.CodeDataBindingId is null
                            ? null
                            : codeRevisions[rule.CodeDataBindingId])))
            .ToArray();
    }

    private static MemberLeafQualification Qualify(
        MemberLeafExpectation expectation,
        MemberLeafEvidence? evidence)
    {
        if (evidence is null)
        {
            return new MemberLeafQualification(
                expectation,
                null,
                false,
                ["LEAF.MISSING"]);
        }

        var reasons = new List<string>();
        if (evidence.OperationSemanticId != expectation.OperationSemanticId)
            reasons.Add("LEAF.OPERATION_MISMATCH");
        if (expectation.CodeDataRevisionId is not null &&
            evidence.CodeDataRevisionId != expectation.CodeDataRevisionId)
            reasons.Add("LEAF.CODE_DATA_MISMATCH");
        if (evidence.Execution != ExecutionState.Completed)
            reasons.Add("LEAF.EXECUTION_INCOMPLETE");
        if (evidence.Completeness != CompletenessState.CompleteForScope)
            reasons.Add("LEAF.PARTIAL");
        if (evidence.Freshness != FreshnessState.Current)
            reasons.Add($"LEAF.{evidence.Freshness.ToString().ToUpperInvariant()}");
        if (evidence.Applicability != expectation.ExpectedApplicability)
        {
            reasons.Add("LEAF.APPLICABILITY_MISMATCH");
        }
        else if (expectation.ExpectedApplicability == ApplicabilityState.Applicable)
        {
            if (evidence.Engineering == EngineeringState.Fail)
                reasons.Add("LEAF.FAIL");
            else if (evidence.Engineering != EngineeringState.Pass)
                reasons.Add("LEAF.NOT_EVALUATED");
        }
        else if (evidence.Engineering != EngineeringState.NotEvaluated)
        {
            reasons.Add("LEAF.NOT_APPLICABLE_STATE_INVALID");
        }

        return new MemberLeafQualification(
            expectation,
            evidence,
            reasons.Count == 0,
            reasons);
    }

    private static bool ValidEvidence(MemberLeafEvidence evidence)
    {
        var numericalValues = new[]
        {
            evidence.RequiredValue,
            evidence.SelectedValue,
            evidence.SuppliedValue,
            evidence.GoverningUtilization
        };
        var hasSummaryValue = numericalValues.Take(3).Any(item => item is not null);
        return Enum.IsDefined(evidence.Execution) &&
            Enum.IsDefined(evidence.Applicability) &&
            Enum.IsDefined(evidence.Engineering) &&
            Enum.IsDefined(evidence.Completeness) &&
            Enum.IsDefined(evidence.Freshness) &&
            Text(evidence.LeafId) &&
            Text(evidence.OperationSemanticId) &&
            Text(evidence.ResultId) &&
            Text(evidence.CodeDataRevisionId) &&
            Text(evidence.MethodRevisionId) &&
            Text(evidence.NormalizedInputId) &&
            (evidence.Execution != ExecutionState.Completed ||
                Text(evidence.CalculationId)) &&
            numericalValues.All(item => item is null || double.IsFinite(item.Value)) &&
            (evidence.GoverningUtilization is null ||
                evidence.GoverningUtilization >= 0) &&
            (!hasSummaryValue || Text(evidence.Unit)) &&
            (evidence.DiagnosticCodes ?? []).All(Text);
    }

    private static Provenance Source(BeamProject project) => new(
        string.Join(',', project.CodeDataRevisions.Select(item => item.RevisionId)),
        "is456-beam-member-aggregation-wp06-v1",
        [
            "PF5 AO17 complete-member aggregation contract",
            "WP01-WP05 qualified leaf result identities"
        ]);

    private static ResultEnvelope<MemberDesignOutput> Reject(
        IReadOnlyDictionary<string, EffectiveValue> inputs,
        Provenance source,
        string code,
        string message,
        string field,
        string remediation) =>
        ResultFactory.Rejected<MemberDesignOutput>(
            Operation,
            inputs,
            source,
            Error(code, message, field, remediation));

    private static Diagnostic Error(
        string code,
        string message,
        string field,
        string remediation) => new(
            code,
            "error",
            message,
            Operation,
            field,
            "beam-member",
            remediation);

    private static bool Text(string? value) => !string.IsNullOrWhiteSpace(value);

    private static bool AllText(params string?[] values) => values.All(Text);
}
