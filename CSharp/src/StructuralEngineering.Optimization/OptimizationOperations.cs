using System.Globalization;
using System.Text.RegularExpressions;
using StructuralEngineering.Contracts;
using StructuralEngineering.Core;

namespace StructuralEngineering.Optimization;

public static class OptimizationOperations
{
    public const string RankOperation = "structural.candidate.rank/v1";
    public const string OptimizeOperation = "structural.beam.optimize/v1";
    public const int MaximumCandidateCount = 100_000;

    private const string MemberOperation = "is456.beam_member.design/v1";
    private const string QuantityOperation =
        "structural.construction_quantities.calculate/v1";
    private const string CostOperation =
        "structural.construction_cost.estimate/v1";
    private const string Traversal = "candidate_id_ordinal_ascending";

    private static readonly Provenance Source = new(
        "optimization-policy-wp08-v1",
        "structural-beam-optimization-wp08-v1",
        [
            "docs/planning/xll-product/library-definition/pf7/baseline.json",
            "docs/planning/xll-product/library-definition/pf8/baseline.json",
            "docs/planning/xll-product/library-definition/pf11/baseline.json"
        ]);

    public static CandidateResultBinding CandidateResultBinding<T>(
        ResultEnvelope<T> result,
        T output) => new(
            result.OperationSemanticId,
            result.ResultId,
            result.NormalizedInputId,
            result.CalculationId,
            result.Execution,
            result.Applicability,
            result.Engineering,
            result.Completeness,
            result.Freshness,
            ResultFactory.SemanticId("output_payload_id", output!));

    public static ResultEnvelope<CandidateDomainOutput> BuildCandidateDomain(
        DiscreteCandidateDomain domain)
    {
        domain = NormalizeDomain(domain);
        var inputs = ResultFactory.Effective(("domain", domain));
        try
        {
            return ResultFactory.Completed(
                OptimizeOperation, inputs, Build(domain), Source);
        }
        catch (ArgumentException error)
        {
            return ResultFactory.Rejected<CandidateDomainOutput>(
                OptimizeOperation,
                inputs,
                Source,
                Error(OptimizeOperation, error.Message));
        }
    }

    public static ResultEnvelope<CandidateRankingOutput> RankCandidates(
        CandidateRankingRequest request)
    {
        var inputs = ResultFactory.Effective(("request", request));
        try
        {
            var output = Rank(request);
            if (output.TerminalState == SearchTerminalState.CompleteEnumeration)
            {
                return ResultFactory.Completed(
                    RankOperation, inputs, output, Source);
            }

            if (output.TerminalState == SearchTerminalState.NoFeasibleCandidate)
            {
                return ResultFactory.Completed(
                    RankOperation,
                    inputs,
                    output,
                    Source,
                    EngineeringState.Fail,
                    Error(RankOperation, "SEARCH.NO_FEASIBLE_CANDIDATE"));
            }

            return ResultFactory.Partial(
                RankOperation,
                inputs,
                output,
                Source,
                FreshnessState.Current,
                Error(
                    RankOperation,
                    "SEARCH." + TerminalWire(output.TerminalState).ToUpperInvariant()));
        }
        catch (ArgumentException error)
        {
            return ResultFactory.Rejected<CandidateRankingOutput>(
                RankOperation,
                inputs,
                Source,
                Error(RankOperation, error.Message));
        }
    }

    public static ResultEnvelope<BeamOptimizationOutput> OptimizeBeam(
        BeamOptimizationRequest request)
    {
        request = request with { Domain = NormalizeDomain(request.Domain) };
        var inputs = ResultFactory.Effective(("request", request));
        try
        {
            var domain = Build(request.Domain);
            var ranking = Rank(new CandidateRankingRequest(
                request.SearchId,
                request.Context,
                domain,
                request.ObjectiveProfile,
                request.AnalysisMode,
                request.ReanalysisPolicy,
                request.EvaluationBudget,
                request.StopReason,
                request.Evaluations));
            var output = new BeamOptimizationOutput(
                request.SearchId, domain, ranking);

            if (ranking.TerminalState == SearchTerminalState.CompleteEnumeration)
            {
                return ResultFactory.Completed(
                    OptimizeOperation, inputs, output, Source);
            }

            if (ranking.TerminalState == SearchTerminalState.NoFeasibleCandidate)
            {
                return ResultFactory.Completed(
                    OptimizeOperation,
                    inputs,
                    output,
                    Source,
                    EngineeringState.Fail,
                    Error(OptimizeOperation, "SEARCH.NO_FEASIBLE_CANDIDATE"));
            }

            return ResultFactory.Partial(
                OptimizeOperation,
                inputs,
                output,
                Source,
                FreshnessState.Current,
                Error(
                    OptimizeOperation,
                    "SEARCH." + TerminalWire(ranking.TerminalState).ToUpperInvariant()));
        }
        catch (ArgumentException error)
        {
            return ResultFactory.Rejected<BeamOptimizationOutput>(
                OptimizeOperation,
                inputs,
                Source,
                Error(OptimizeOperation, error.Message));
        }
    }

    private static CandidateDomainOutput Build(DiscreteCandidateDomain domain)
    {
        ValidateDomainRequest(domain);
        var baseline = domain.SectionChoices.Single(
            item => item.ChoiceId == domain.BaselineSectionChoiceId);
        var candidates = new List<BeamCandidateDefinition>();

        foreach (var rawSection in domain.SectionChoices)
        {
            var section = rawSection with
            {
                AdditionalChangeCategories =
                    rawSection.AdditionalChangeCategories ?? []
            };
            foreach (var longitudinal in domain.LongitudinalChoices)
            {
                foreach (var transverse in domain.TransverseChoices)
                {
                    var physical = Physical(section, longitudinal, transverse);
                    var physicalId = ResultFactory.SemanticId(
                        "candidate_physical_definition_id", physical);
                    var changes = Changes(section, baseline);
                    var candidateId = CandidateId(
                        domain.DomainId,
                        domain.RevisionId,
                        section.ChoiceId,
                        longitudinal.ChoiceId,
                        transverse.ChoiceId,
                        physicalId,
                        changes);
                    candidates.Add(new BeamCandidateDefinition(
                        candidateId,
                        physicalId,
                        domain.DomainId,
                        domain.RevisionId,
                        section,
                        longitudinal,
                        transverse,
                        physical,
                        changes,
                        Coupling(changes)));
                }
            }
        }

        var ordered = candidates
            .OrderBy(item => item.CandidateId, StringComparer.Ordinal)
            .ToArray();
        var domainId = DomainSemanticId(
            domain.DomainId,
            domain.RevisionId,
            domain.ProjectBasisId,
            domain.ProfileRevisionId,
            domain.MemberId,
            domain.TopologyRevisionId,
            domain.ActionRevisionId,
            domain.DesignScopeRevisionId,
            domain.BaselineAnalysisRevisionId,
            domain.BaselineSectionChoiceId,
            ordered.Select(item => item.CandidateId).ToArray());

        return new CandidateDomainOutput(
            domain.DomainId,
            domain.RevisionId,
            domainId,
            domain.ProjectBasisId,
            domain.ProfileRevisionId,
            domain.MemberId,
            domain.TopologyRevisionId,
            domain.ActionRevisionId,
            domain.DesignScopeRevisionId,
            domain.BaselineAnalysisRevisionId,
            domain.BaselineSectionChoiceId,
            Traversal,
            ordered,
            ordered.Length);
    }

    private static DiscreteCandidateDomain NormalizeDomain(
        DiscreteCandidateDomain domain) => domain with
        {
            SectionChoices = domain.SectionChoices
                .Select(item => item with
                {
                    AdditionalChangeCategories =
                        item.AdditionalChangeCategories ?? []
                })
                .ToArray()
        };

    private static void ValidateDomainRequest(DiscreteCandidateDomain domain)
    {
        if (!AllText(
                domain.DomainId,
                domain.RevisionId,
                domain.ProjectBasisId,
                domain.ProfileRevisionId,
                domain.MemberId,
                domain.TopologyRevisionId,
                domain.ActionRevisionId,
                domain.DesignScopeRevisionId,
                domain.BaselineAnalysisRevisionId,
                domain.BaselineSectionChoiceId))
        {
            throw new ArgumentException("DOMAIN.IDENTITY");
        }

        if (domain.SectionChoices.Count == 0 ||
            domain.LongitudinalChoices.Count == 0 ||
            domain.TransverseChoices.Count == 0)
        {
            throw new ArgumentException("DOMAIN.EMPTY_AXIS");
        }

        if (!UniqueChoiceIds(domain.SectionChoices.Select(item => item.ChoiceId)) ||
            !UniqueChoiceIds(
                domain.LongitudinalChoices.Select(item => item.ChoiceId)) ||
            !UniqueChoiceIds(domain.TransverseChoices.Select(item => item.ChoiceId)))
        {
            throw new ArgumentException("DOMAIN.CHOICE_ID");
        }

        if (domain.SectionChoices.Count(
                item => item.ChoiceId == domain.BaselineSectionChoiceId) != 1)
        {
            throw new ArgumentException("DOMAIN.BASELINE_SECTION");
        }

        if (domain.SectionChoices.Any(item => !Valid(item)) ||
            domain.LongitudinalChoices.Any(item => !Valid(item)) ||
            domain.TransverseChoices.Any(item => !Valid(item)))
        {
            throw new ArgumentException("DOMAIN.CHOICE_INVALID");
        }

        if (domain.MaximumDomainCandidates is < 1 or > MaximumCandidateCount)
        {
            throw new ArgumentException("DOMAIN.BOUND_EXCEEDED");
        }

        var count = (long)domain.SectionChoices.Count *
                    domain.LongitudinalChoices.Count *
                    domain.TransverseChoices.Count;
        if (count > domain.MaximumDomainCandidates)
        {
            throw new ArgumentException("DOMAIN.BOUND_EXCEEDED");
        }

        if (domain.SourceReferences.Count == 0 ||
            domain.Limitations.Count == 0 ||
            domain.SourceReferences.Any(item => !Text(item)) ||
            domain.Limitations.Any(item => !Text(item)) ||
            domain.SourceReferences.Distinct(StringComparer.Ordinal).Count() !=
            domain.SourceReferences.Count)
        {
            throw new ArgumentException("DOMAIN.PROVENANCE");
        }
    }

    private static CandidateRankingOutput Rank(CandidateRankingRequest request)
    {
        ValidateObjectiveProfile(request.ObjectiveProfile);
        ValidateContext(request.Context);
        ValidateDomainOutput(request.Context, request.Domain);

        var (eligible, initialExclusions) = BuildEvaluationPlan(request.Domain);
        ValidateSearchShape(request, eligible);

        var evaluations = request.Evaluations.ToDictionary(
            item => item.CandidateId, StringComparer.Ordinal);
        var candidates = request.Domain.Candidates.ToDictionary(
            item => item.CandidateId, StringComparer.Ordinal);
        var exclusions = new List<CandidateExclusion>(initialExclusions);
        var records = new List<CandidateEvaluationRecord>();
        var feasible = new List<EvaluatedCandidate>();
        var engineeringFailCount = 0;
        var incompleteCount = exclusions.Count(
            item => item.Disposition == CandidateDisposition.Incomplete);

        foreach (var candidate in eligible)
        {
            if (!evaluations.TryGetValue(candidate.CandidateId, out var evaluation))
            {
                var notEvaluatedReasons = new[] { "SEARCH.NOT_EVALUATED" };
                exclusions.Add(new CandidateExclusion(
                    candidate.CandidateId,
                    CandidateDisposition.NotEvaluated,
                    notEvaluatedReasons,
                    null));
                records.Add(new CandidateEvaluationRecord(
                    candidate.CandidateId,
                    candidate.PhysicalDefinitionId,
                    CandidateDisposition.NotEvaluated,
                    null,
                    null,
                    null,
                    null,
                    [],
                    notEvaluatedReasons));
                continue;
            }

            var (reasonCodes, engineeringFail) = EvaluateEvidence(
                candidate, evaluation, request);
            var metrics = ObjectiveMetrics(
                candidate,
                evaluation,
                request.ObjectiveProfile,
                reasonCodes);
            var distinctReasons = reasonCodes.Distinct(StringComparer.Ordinal).ToArray();
            var disposition = distinctReasons.Length > 0
                ? CandidateDisposition.Incomplete
                : engineeringFail
                    ? CandidateDisposition.EngineeringFail
                    : CandidateDisposition.Feasible;

            if (disposition == CandidateDisposition.Incomplete)
            {
                incompleteCount++;
            }
            else if (disposition == CandidateDisposition.EngineeringFail)
            {
                engineeringFailCount++;
                distinctReasons = ["ENGINEERING.REQUIRED_CHECK_FAILED"];
            }

            records.Add(new CandidateEvaluationRecord(
                candidate.CandidateId,
                candidate.PhysicalDefinitionId,
                disposition,
                evaluation.AnalysisRevisionId,
                evaluation.MemberBinding,
                evaluation.QuantityBinding,
                evaluation.CostBinding,
                metrics,
                distinctReasons));

            if (disposition == CandidateDisposition.Feasible)
            {
                feasible.Add(new EvaluatedCandidate(candidate, evaluation, metrics));
            }
            else
            {
                exclusions.Add(new CandidateExclusion(
                    candidate.CandidateId,
                    disposition,
                    distinctReasons,
                    evaluation.MemberBinding.ResultId));
            }
        }

        var recordedIds = records
            .Select(item => item.CandidateId)
            .ToHashSet(StringComparer.Ordinal);
        foreach (var exclusion in exclusions)
        {
            if (recordedIds.Add(exclusion.CandidateId))
            {
                var candidate = candidates[exclusion.CandidateId];
                records.Add(new CandidateEvaluationRecord(
                    candidate.CandidateId,
                    candidate.PhysicalDefinitionId,
                    exclusion.Disposition,
                    null,
                    null,
                    null,
                    null,
                    [],
                    exclusion.ReasonCodes));
            }
        }

        var tieBreakers = request.ObjectiveProfile.TieBreakers
            .Where(item => item != CandidateTieBreaker.CandidateId)
            .Append(CandidateTieBreaker.CandidateId)
            .ToArray();
        var ranked = feasible
            .OrderBy(item => item, CandidateComparer(tieBreakers))
            .Select((item, index) => new RankedCandidate(
                index + 1,
                item.Candidate.CandidateId,
                item.Candidate.PhysicalDefinitionId,
                item.Candidate.CouplingClass,
                item.Evaluation.AnalysisRevisionId,
                item.Evaluation.MemberBinding.ResultId,
                item.Evaluation.QuantityBinding.ResultId,
                item.Evaluation.CostBinding?.ResultId,
                item.Metrics))
            .ToArray();

        var duplicateCount = exclusions.Count(
            item => item.Disposition ==
                    CandidateDisposition.DuplicatePhysicalDefinition);
        var enumerationComplete =
            request.StopReason == SearchStopReason.Completed &&
            request.Evaluations.Count == eligible.Count;
        var hasUnresolved = request.Domain.Candidates.Any(
            item => item.CouplingClass == CandidateCouplingClass.Unresolved);
        var terminal = TerminalState(
            request.StopReason,
            enumerationComplete,
            hasUnresolved,
            incompleteCount,
            ranked.Length);
        var optimum = terminal == SearchTerminalState.CompleteEnumeration;
        var infeasible = terminal == SearchTerminalState.NoFeasibleCandidate;

        return new CandidateRankingOutput(
            request.RankingId,
            request.Domain.DomainId,
            request.Domain.DomainSemanticId,
            ResultFactory.SemanticId(
                "expected_leaf_set_id",
                request.Context.ReferenceMember.ExpectedLeaves),
            request.AnalysisMode,
            request.Context.BaselineAnalysisRevisionId,
            request.ObjectiveProfile.ProfileId,
            request.ObjectiveProfile.RevisionId,
            tieBreakers,
            records.OrderBy(item => item.CandidateId, StringComparer.Ordinal).ToArray(),
            ranked,
            exclusions.OrderBy(item => item.CandidateId, StringComparer.Ordinal).ToArray(),
            new SearchPerformance(
                request.Domain.Candidates.Count,
                request.Domain.Candidates.Count - duplicateCount,
                duplicateCount,
                request.EvaluationBudget,
                request.Evaluations.Count,
                ranked.Length,
                engineeringFailCount,
                incompleteCount),
            terminal,
            enumerationComplete,
            ranked.FirstOrDefault()?.CandidateId,
            optimum ? ranked[0].CandidateId : null,
            optimum,
            infeasible,
            ranked.Length > 0 && !optimum,
            request.AnalysisMode == AnalysisMode.FixedActions
                ? "finite_domain_fixed_actions_common_force_assumption"
                : "finite_domain_candidate_specific_coupled_reanalysis");
    }

    private static void ValidateObjectiveProfile(CandidateObjectiveProfile profile)
    {
        if (!AllText(profile.ProfileId, profile.RevisionId) ||
            profile.Objectives.Count == 0 ||
            profile.Objectives.Distinct().Count() != profile.Objectives.Count ||
            profile.TieBreakers.Distinct().Count() != profile.TieBreakers.Count ||
            profile.Objectives.Any(item =>
                !Enum.IsDefined(typeof(CandidateObjectiveKind), item)) ||
            profile.TieBreakers.Any(item =>
                !Enum.IsDefined(typeof(CandidateTieBreaker), item)))
        {
            throw new ArgumentException("OBJECTIVE_PROFILE.INVALID");
        }
    }

    private static void ValidateContext(CandidateRankingContext context)
    {
        if (!AllText(
                context.ProjectBasisId,
                context.ProfileRevisionId,
                context.MemberId,
                context.TopologyRevisionId,
                context.ActionRevisionId,
                context.DesignScopeRevisionId,
                context.BaselineAnalysisRevisionId,
                context.ReferenceMemberResultId) ||
            context.ReferenceMember.ExpectedLeaves.Count == 0 ||
            !UniqueChoiceIds(
                context.ReferenceMember.ExpectedLeaves.Select(item => item.LeafId)))
        {
            throw new ArgumentException("CONTEXT.IDENTITY");
        }

        var bindingReasons = BindingReasons(
            context.ReferenceMemberBinding,
            context.ReferenceMember,
            MemberOperation,
            "REFERENCE_MEMBER",
            allowEngineeringFail: true);
        if (bindingReasons.Count > 0 ||
            context.ReferenceMemberResultId != context.ReferenceMemberBinding.ResultId)
        {
            throw new ArgumentException("REFERENCE_MEMBER.BINDING_INVALID");
        }

        var member = context.ReferenceMember;
        if (member.ProjectBasisId != context.ProjectBasisId ||
            member.ProfileRevisionId != context.ProfileRevisionId ||
            member.MemberId != context.MemberId ||
            member.TopologyRevisionId != context.TopologyRevisionId ||
            member.ActionRevisionId != context.ActionRevisionId ||
            member.DesignScopeRevisionId != context.DesignScopeRevisionId)
        {
            throw new ArgumentException("REFERENCE_MEMBER.CONTEXT_MISMATCH");
        }
    }

    private static void ValidateDomainOutput(
        CandidateRankingContext context,
        CandidateDomainOutput domain)
    {
        if (!AllText(
                domain.DomainId,
                domain.DomainRevisionId,
                domain.DomainSemanticId,
                domain.ProjectBasisId,
                domain.ProfileRevisionId,
                domain.MemberId,
                domain.TopologyRevisionId,
                domain.ActionRevisionId,
                domain.DesignScopeRevisionId,
                domain.BaselineAnalysisRevisionId,
                domain.BaselineSectionChoiceId) ||
            domain.TraversalOrder != Traversal ||
            domain.GeneratedCount != domain.Candidates.Count ||
            domain.Candidates.Count == 0 ||
            domain.Candidates.Select(item => item.CandidateId)
                .Distinct(StringComparer.Ordinal).Count() != domain.Candidates.Count ||
            !domain.Candidates.SequenceEqual(
                domain.Candidates.OrderBy(
                    item => item.CandidateId, StringComparer.Ordinal)))
        {
            throw new ArgumentException("DOMAIN.OUTPUT_INVALID");
        }

        if (domain.ProjectBasisId != context.ProjectBasisId ||
            domain.ProfileRevisionId != context.ProfileRevisionId ||
            domain.MemberId != context.MemberId ||
            domain.TopologyRevisionId != context.TopologyRevisionId ||
            domain.ActionRevisionId != context.ActionRevisionId ||
            domain.DesignScopeRevisionId != context.DesignScopeRevisionId ||
            domain.BaselineAnalysisRevisionId != context.BaselineAnalysisRevisionId)
        {
            throw new ArgumentException("DOMAIN.CONTEXT_MISMATCH");
        }

        var baselineSections = domain.Candidates
            .Where(item =>
                item.Section.ChoiceId == domain.BaselineSectionChoiceId)
            .Select(item => item.Section)
            .ToArray();
        if (baselineSections.Length == 0 ||
            baselineSections.Skip(1).Any(item =>
                !SameSection(item, baselineSections[0])))
        {
            throw new ArgumentException("DOMAIN.BASELINE_SECTION");
        }

        var baseline = baselineSections[0];
        foreach (var candidate in domain.Candidates)
        {
            if (candidate.DomainId != domain.DomainId ||
                candidate.DomainRevisionId != domain.DomainRevisionId ||
                !Valid(candidate.Section) ||
                !Valid(candidate.Longitudinal) ||
                !Valid(candidate.Transverse))
            {
                throw new ArgumentException("DOMAIN.CANDIDATE_BINDING");
            }

            var physical = Physical(
                candidate.Section,
                candidate.Longitudinal,
                candidate.Transverse);
            var physicalId = ResultFactory.SemanticId(
                "candidate_physical_definition_id", physical);
            var changes = Changes(candidate.Section, baseline);
            var candidateId = CandidateId(
                domain.DomainId,
                domain.DomainRevisionId,
                candidate.Section.ChoiceId,
                candidate.Longitudinal.ChoiceId,
                candidate.Transverse.ChoiceId,
                physicalId,
                changes);
            if (!SamePhysical(candidate.Physical, physical) ||
                candidate.PhysicalDefinitionId != physicalId ||
                candidate.CandidateId != candidateId ||
                !candidate.ChangeCategories.SequenceEqual(changes) ||
                candidate.CouplingClass != Coupling(changes))
            {
                throw new ArgumentException("DOMAIN.CANDIDATE_IDENTITY");
            }
        }

        var expectedDomainId = DomainSemanticId(
            domain.DomainId,
            domain.DomainRevisionId,
            domain.ProjectBasisId,
            domain.ProfileRevisionId,
            domain.MemberId,
            domain.TopologyRevisionId,
            domain.ActionRevisionId,
            domain.DesignScopeRevisionId,
            domain.BaselineAnalysisRevisionId,
            domain.BaselineSectionChoiceId,
            domain.Candidates.Select(item => item.CandidateId).ToArray());
        if (domain.DomainSemanticId != expectedDomainId)
        {
            throw new ArgumentException("DOMAIN.SEMANTIC_ID_MISMATCH");
        }
    }

    private static (
        List<BeamCandidateDefinition> Eligible,
        List<CandidateExclusion> Exclusions) BuildEvaluationPlan(
            CandidateDomainOutput domain)
    {
        var seenPhysical = new HashSet<string>(StringComparer.Ordinal);
        var eligible = new List<BeamCandidateDefinition>();
        var exclusions = new List<CandidateExclusion>();
        foreach (var candidate in domain.Candidates)
        {
            if (!seenPhysical.Add(candidate.PhysicalDefinitionId))
            {
                exclusions.Add(new CandidateExclusion(
                    candidate.CandidateId,
                    CandidateDisposition.DuplicatePhysicalDefinition,
                    ["DOMAIN.DUPLICATE_PHYSICAL_DEFINITION"],
                    null));
            }
            else if (candidate.CouplingClass == CandidateCouplingClass.Unresolved)
            {
                exclusions.Add(new CandidateExclusion(
                    candidate.CandidateId,
                    CandidateDisposition.Incomplete,
                    ["COUPLING.UNRESOLVED"],
                    null));
            }
            else
            {
                eligible.Add(candidate);
            }
        }

        return (eligible, exclusions);
    }

    private static void ValidateSearchShape(
        CandidateRankingRequest request,
        IReadOnlyList<BeamCandidateDefinition> eligible)
    {
        if (request.EvaluationBudget is < 1 or > MaximumCandidateCount ||
            request.Evaluations.Count > request.EvaluationBudget ||
            request.Evaluations.Select(item => item.CandidateId)
                .Distinct(StringComparer.Ordinal).Count() != request.Evaluations.Count)
        {
            throw new ArgumentException("SEARCH.BUDGET");
        }

        if (!request.Evaluations.Select(item => item.CandidateId).SequenceEqual(
                eligible.Take(request.Evaluations.Count)
                    .Select(item => item.CandidateId)))
        {
            throw new ArgumentException("EVALUATION.NOT_CANONICAL_PREFIX");
        }

        if (request.StopReason == SearchStopReason.Completed &&
            request.Evaluations.Count != eligible.Count)
        {
            throw new ArgumentException("SEARCH.COMPLETED_WITHOUT_FULL_EVALUATION");
        }

        if (request.StopReason == SearchStopReason.EvaluationBudgetReached &&
            (request.Evaluations.Count != request.EvaluationBudget ||
             request.Evaluations.Count >= eligible.Count))
        {
            throw new ArgumentException("SEARCH.BUDGET_STOP_INVALID");
        }
    }

    private static (List<string> Reasons, bool EngineeringFail) EvaluateEvidence(
        BeamCandidateDefinition candidate,
        CandidateEvaluation evaluation,
        CandidateRankingRequest request)
    {
        var reasons = new List<string>();
        reasons.AddRange(ReanalysisReasons(candidate, evaluation, request));

        var (memberReasons, engineeringFail) = MemberReasons(
            candidate, evaluation, request.Context);
        reasons.AddRange(memberReasons);
        reasons.AddRange(QuantityReasons(candidate, evaluation, request.Context));

        if (evaluation.Cost is not null || evaluation.CostBinding is not null)
        {
            reasons.AddRange(CostReasons(candidate, evaluation, request.Context));
        }

        return (reasons, engineeringFail);
    }

    private static List<string> ReanalysisReasons(
        BeamCandidateDefinition candidate,
        CandidateEvaluation evaluation,
        CandidateRankingRequest request)
    {
        if (candidate.CouplingClass == CandidateCouplingClass.Unresolved)
        {
            return ["COUPLING.UNRESOLVED"];
        }

        if (request.AnalysisMode == AnalysisMode.FixedActions)
        {
            return evaluation.AnalysisRevisionId ==
                   request.Context.BaselineAnalysisRevisionId
                ? []
                : ["ANALYSIS.FIXED_ACTION_REVISION_MISMATCH"];
        }

        if (candidate.CouplingClass == CandidateCouplingClass.FixedAction)
        {
            return evaluation.AnalysisRevisionId ==
                   request.Context.BaselineAnalysisRevisionId
                ? []
                : ["ANALYSIS.FIXED_CHANGE_REVISION_MISMATCH"];
        }

        var reasons = new List<string>();
        var policy = request.ReanalysisPolicy;
        if (policy is null ||
            !AllText(policy.PolicyId, policy.RevisionId, policy.SourceReference))
        {
            reasons.Add("REANALYSIS.POLICY_REQUIRED");
        }
        else if (!policy.OwnedCopyRequired)
        {
            reasons.Add("REANALYSIS.OWNED_COPY_REQUIRED");
        }

        var evidence = evaluation.ReanalysisEvidence;
        if (evidence is null)
        {
            reasons.Add("REANALYSIS.EVIDENCE_REQUIRED");
        }
        else if (evidence.CandidateId != candidate.CandidateId ||
                 evidence.CandidateDefinitionId != candidate.PhysicalDefinitionId ||
                 evidence.BaselineAnalysisRevisionId !=
                 request.Context.BaselineAnalysisRevisionId ||
                 evidence.CandidateAnalysisRevisionId !=
                 evaluation.AnalysisRevisionId ||
                 evidence.CandidateAnalysisRevisionId ==
                 request.Context.BaselineAnalysisRevisionId ||
                 !AllText(
                     evidence.SnapshotResultId,
                     evidence.SnapshotOutputPayloadId) ||
                 !evidence.ExecutionCompleted ||
                 !evidence.FreshnessCurrent)
        {
            reasons.Add("REANALYSIS.EVIDENCE_INVALID");
        }

        return reasons;
    }

    private static (List<string> Reasons, bool EngineeringFail) MemberReasons(
        BeamCandidateDefinition candidate,
        CandidateEvaluation evaluation,
        CandidateRankingContext context)
    {
        var member = evaluation.MemberResult;
        var reasons = BindingReasons(
            evaluation.MemberBinding,
            member,
            MemberOperation,
            "MEMBER",
            allowEngineeringFail: true);

        if (member.ProjectBasisId != context.ProjectBasisId ||
            member.ProfileRevisionId != context.ProfileRevisionId ||
            member.MemberId != context.MemberId ||
            member.TopologyRevisionId != context.TopologyRevisionId ||
            member.ActionRevisionId != context.ActionRevisionId ||
            member.DesignScopeRevisionId != context.DesignScopeRevisionId ||
            member.ReinforcementRevisionId != candidate.CandidateId)
        {
            reasons.Add("MEMBER.CONTEXT_MISMATCH");
        }

        var referenceLeaves = context.ReferenceMember.ExpectedLeaves;
        if (member.ExpectedLeaves.Count != referenceLeaves.Count ||
            ResultFactory.SemanticId("expected_leaf_set_id", member.ExpectedLeaves) !=
            ResultFactory.SemanticId("expected_leaf_set_id", referenceLeaves))
        {
            reasons.Add("MEMBER.EXPECTED_LEAF_SET_MISMATCH");
        }

        var qualificationGroups = member.LeafQualifications
            .GroupBy(item => item.Expectation.LeafId, StringComparer.Ordinal)
            .ToDictionary(
                group => group.Key,
                group => group.ToArray(),
                StringComparer.Ordinal);
        var expectedIds = referenceLeaves
            .Select(item => item.LeafId)
            .ToHashSet(StringComparer.Ordinal);
        if (qualificationGroups.Count != expectedIds.Count ||
            qualificationGroups.Keys.Except(expectedIds, StringComparer.Ordinal).Any() ||
            expectedIds.Except(qualificationGroups.Keys, StringComparer.Ordinal).Any() ||
            qualificationGroups.Values.Any(items => items.Length != 1))
        {
            reasons.Add("MEMBER.LEAF_COVERAGE");
        }

        var leafReasons = new List<string>();
        var engineeringFail = false;
        foreach (var expectation in referenceLeaves)
        {
            if (!qualificationGroups.TryGetValue(
                    expectation.LeafId, out var qualifications) ||
                qualifications.Length != 1)
            {
                continue;
            }

            var qualification = qualifications[0];
            if (qualification.Expectation != expectation)
            {
                leafReasons.Add(
                    $"LEAF.{expectation.LeafId}.EXPECTATION_MISMATCH");
                continue;
            }

            var evidence = qualification.Evidence;
            if (!ValidLeafIdentity(expectation, evidence))
            {
                leafReasons.Add($"LEAF.{expectation.LeafId}.IDENTITY_INVALID");
                continue;
            }

            if (expectation.ExpectedApplicability ==
                ApplicabilityState.NotApplicable)
            {
                if (!qualification.Qualified ||
                    evidence!.Execution != ExecutionState.Completed ||
                    evidence.Applicability != ApplicabilityState.NotApplicable ||
                    evidence.Engineering != EngineeringState.NotEvaluated ||
                    evidence.Completeness != CompletenessState.CompleteForScope ||
                    evidence.Freshness != FreshnessState.Current)
                {
                    leafReasons.Add(
                        $"LEAF.{expectation.LeafId}.EXCLUDED_NA_INVALID");
                }
                continue;
            }

            if (evidence!.Engineering == EngineeringState.Fail)
            {
                engineeringFail = true;
                if (qualification.Qualified ||
                    !qualification.ReasonCodes.Contains(
                        "LEAF.FAIL", StringComparer.Ordinal) ||
                    evidence.Execution != ExecutionState.Completed ||
                    evidence.Applicability != ApplicabilityState.Applicable ||
                    evidence.Completeness != CompletenessState.CompleteForScope ||
                    evidence.Freshness != FreshnessState.Current)
                {
                    leafReasons.Add(
                        $"LEAF.{expectation.LeafId}.FAIL_STATE_INVALID");
                }
            }
            else if (!qualification.Qualified ||
                     evidence.Execution != ExecutionState.Completed ||
                     evidence.Applicability != ApplicabilityState.Applicable ||
                     evidence.Engineering != EngineeringState.Pass ||
                     evidence.Completeness != CompletenessState.CompleteForScope ||
                     evidence.Freshness != FreshnessState.Current)
            {
                leafReasons.Add($"LEAF.{expectation.LeafId}.INCOMPLETE");
            }
        }

        reasons.AddRange(leafReasons);
        var memberEvidenceComplete = leafReasons.Count == 0 &&
                                     !reasons.Contains(
                                         "MEMBER.LEAF_COVERAGE",
                                         StringComparer.Ordinal) &&
                                     !reasons.Contains(
                                         "MEMBER.EXPECTED_LEAF_SET_MISMATCH",
                                         StringComparer.Ordinal);
        if (member.Qualified != (memberEvidenceComplete && !engineeringFail))
        {
            reasons.Add("MEMBER.QUALIFIED_FLAG_MISMATCH");
        }

        if ((member.Qualified &&
             evaluation.MemberBinding.Engineering != EngineeringState.Pass) ||
            (engineeringFail && memberEvidenceComplete &&
             evaluation.MemberBinding.Engineering != EngineeringState.Fail) ||
            (!member.Qualified && !engineeringFail && memberEvidenceComplete &&
             evaluation.MemberBinding.Engineering != EngineeringState.NotEvaluated))
        {
            reasons.Add("MEMBER.ENGINEERING_STATE_MISMATCH");
        }

        return (reasons, engineeringFail);
    }

    private static List<string> QuantityReasons(
        BeamCandidateDefinition candidate,
        CandidateEvaluation evaluation,
        CandidateRankingContext context)
    {
        var quantities = evaluation.Quantities;
        var reasons = BindingReasons(
            evaluation.QuantityBinding,
            quantities,
            QuantityOperation,
            "QUANTITY",
            allowEngineeringFail: false);
        if (quantities.ProjectBasisId != context.ProjectBasisId ||
            quantities.MemberId != context.MemberId ||
            quantities.DetailRevisionId != candidate.CandidateId)
        {
            reasons.Add("QUANTITY.CONTEXT_MISMATCH");
        }

        if (!Nonnegative(quantities.SteelScheduledMassKg) ||
            !Nonnegative(quantities.SteelStockMassKg) ||
            !Nonnegative(quantities.ConcreteVolumeM3) ||
            !Nonnegative(quantities.FormworkAreaM2) ||
            quantities.CouplerCount < 0)
        {
            reasons.Add("QUANTITY.NONFINITE");
        }

        return reasons;
    }

    private static List<string> CostReasons(
        BeamCandidateDefinition candidate,
        CandidateEvaluation evaluation,
        CandidateRankingContext context)
    {
        if (evaluation.Cost is null || evaluation.CostBinding is null)
        {
            return ["COST.PAIR_REQUIRED"];
        }

        var reasons = BindingReasons(
            evaluation.CostBinding,
            evaluation.Cost,
            CostOperation,
            "COST",
            allowEngineeringFail: false);
        if (evaluation.Cost.ProjectBasisId != context.ProjectBasisId ||
            evaluation.Cost.MemberId != context.MemberId ||
            evaluation.Cost.DetailRevisionId != candidate.CandidateId ||
            evaluation.Cost.QuantityResultId != evaluation.QuantityBinding.ResultId)
        {
            reasons.Add("COST.CONTEXT_MISMATCH");
        }
        return reasons;
    }

    private static ObjectiveMetric[] ObjectiveMetrics(
        BeamCandidateDefinition candidate,
        CandidateEvaluation evaluation,
        CandidateObjectiveProfile profile,
        List<string> reasons)
    {
        var metrics = new List<ObjectiveMetric>();
        foreach (var objective in profile.Objectives)
        {
            switch (objective)
            {
                case CandidateObjectiveKind.Cost:
                    if (evaluation.Cost is null ||
                        evaluation.CostBinding is null)
                    {
                        reasons.Add("OBJECTIVE.COST_MISSING");
                    }
                    else if (!TryNonnegativeDecimal(
                                 evaluation.Cost.TotalDecimal, out var total))
                    {
                        reasons.Add("COST.TOTAL_INVALID");
                    }
                    else if (!Text(evaluation.Cost.Currency))
                    {
                        reasons.Add("OBJECTIVE.COST_MISSING");
                    }
                    else
                    {
                        metrics.Add(new ObjectiveMetric(
                            objective,
                            total,
                            evaluation.Cost.Currency,
                            evaluation.CostBinding.ResultId));
                    }
                    break;
                case CandidateObjectiveKind.SteelMass:
                    AddNonnegativeMetric(
                        metrics,
                        reasons,
                        objective,
                        evaluation.Quantities.SteelScheduledMassKg,
                        "kg",
                        evaluation.QuantityBinding.ResultId);
                    break;
                case CandidateObjectiveKind.SectionDepth:
                    AddNonnegativeMetric(
                        metrics,
                        reasons,
                        objective,
                        candidate.Physical.OverallDepthMm,
                        "mm",
                        candidate.PhysicalDefinitionId);
                    break;
                case CandidateObjectiveKind.ConcreteVolume:
                    AddNonnegativeMetric(
                        metrics,
                        reasons,
                        objective,
                        evaluation.Quantities.ConcreteVolumeM3,
                        "m3",
                        evaluation.QuantityBinding.ResultId);
                    break;
                case CandidateObjectiveKind.FormworkArea:
                    AddNonnegativeMetric(
                        metrics,
                        reasons,
                        objective,
                        evaluation.Quantities.FormworkAreaM2,
                        "m2",
                        evaluation.QuantityBinding.ResultId);
                    break;
                case CandidateObjectiveKind.Carbon:
                    AddOptionalMetric(
                        metrics,
                        reasons,
                        objective,
                        evaluation.EmbodiedCarbonKgCo2e,
                        "kg_co2e",
                        evaluation.CarbonBasisId);
                    break;
                case CandidateObjectiveKind.Congestion:
                    AddOptionalMetric(
                        metrics,
                        reasons,
                        objective,
                        evaluation.CongestionScore,
                        "ratio",
                        evaluation.CongestionBasisId);
                    break;
                case CandidateObjectiveKind.UtilizationReserve:
                    if (evaluation.MemberResult.GoverningUtilization is not double
                            utilization ||
                        !Nonnegative(utilization))
                    {
                        reasons.Add("OBJECTIVE.UTILIZATION_MISSING");
                    }
                    else
                    {
                        metrics.Add(new ObjectiveMetric(
                            objective,
                            Math.Max(0, 1 - utilization),
                            "ratio",
                            evaluation.MemberBinding.ResultId));
                    }
                    break;
                default:
                    reasons.Add("OBJECTIVE.UNKNOWN");
                    break;
            }
        }
        return [.. metrics];
    }

    private static void AddNonnegativeMetric(
        ICollection<ObjectiveMetric> metrics,
        ICollection<string> reasons,
        CandidateObjectiveKind objective,
        double value,
        string unit,
        string sourceIdentity)
    {
        if (!Nonnegative(value) || !AllText(unit, sourceIdentity))
        {
            reasons.Add($"OBJECTIVE.{ObjectiveWire(objective).ToUpperInvariant()}_MISSING");
            return;
        }
        metrics.Add(new ObjectiveMetric(objective, value, unit, sourceIdentity));
    }

    private static void AddOptionalMetric(
        ICollection<ObjectiveMetric> metrics,
        ICollection<string> reasons,
        CandidateObjectiveKind objective,
        double? value,
        string unit,
        string? sourceIdentity)
    {
        if (value is not double actual ||
            !Nonnegative(actual) ||
            !AllText(unit, sourceIdentity))
        {
            reasons.Add($"OBJECTIVE.{ObjectiveWire(objective).ToUpperInvariant()}_MISSING");
            return;
        }
        metrics.Add(new ObjectiveMetric(objective, actual, unit, sourceIdentity!));
    }

    private static List<string> BindingReasons<T>(
        CandidateResultBinding binding,
        T payload,
        string expectedOperation,
        string prefix,
        bool allowEngineeringFail)
    {
        var reasons = new List<string>();
        if (!AllText(
                binding.ResultId,
                binding.NormalizedInputId,
                binding.CalculationId,
                binding.OutputPayloadId))
        {
            reasons.Add($"{prefix}.BINDING_IDENTITY");
        }
        if (binding.OperationSemanticId != expectedOperation)
        {
            reasons.Add($"{prefix}.OPERATION_MISMATCH");
        }
        if (binding.OutputPayloadId !=
            ResultFactory.SemanticId("output_payload_id", payload!))
        {
            reasons.Add($"{prefix}.PAYLOAD_MISMATCH");
        }
        if (binding.Execution != ExecutionState.Completed)
        {
            reasons.Add($"{prefix}.EXECUTION_INCOMPLETE");
        }
        if (binding.Applicability != ApplicabilityState.Applicable)
        {
            reasons.Add($"{prefix}.NOT_APPLICABLE");
        }
        if (binding.Completeness != CompletenessState.CompleteForScope)
        {
            reasons.Add($"{prefix}.PARTIAL");
        }
        if (binding.Freshness != FreshnessState.Current)
        {
            reasons.Add($"{prefix}.STALE");
        }
        if (binding.Engineering == EngineeringState.NotEvaluated)
        {
            reasons.Add($"{prefix}.NOT_EVALUATED");
        }
        else if (binding.Engineering == EngineeringState.Fail &&
                 !allowEngineeringFail)
        {
            reasons.Add($"{prefix}.FAIL");
        }
        return reasons;
    }

    private static bool ValidLeafIdentity(
        MemberLeafExpectation expectation,
        MemberLeafEvidence? evidence) =>
        evidence is not null &&
        evidence.LeafId == expectation.LeafId &&
        evidence.OperationSemanticId == expectation.OperationSemanticId &&
        (expectation.CodeDataRevisionId is null ||
         evidence.CodeDataRevisionId == expectation.CodeDataRevisionId) &&
        AllText(
            evidence.ResultId,
            evidence.CodeDataRevisionId,
            evidence.MethodRevisionId,
            evidence.NormalizedInputId,
            evidence.CalculationId);

    private static IComparer<EvaluatedCandidate> CandidateComparer(
        IReadOnlyList<CandidateTieBreaker> tieBreakers) =>
        Comparer<EvaluatedCandidate>.Create((left, right) =>
        {
            for (var index = 0; index < left.Metrics.Count; index++)
            {
                var leftValue = ObjectiveSortValue(left.Metrics[index]);
                var rightValue = ObjectiveSortValue(right.Metrics[index]);
                var comparison = leftValue.CompareTo(rightValue);
                if (comparison != 0)
                {
                    return comparison;
                }
            }

            foreach (var tieBreaker in tieBreakers)
            {
                var comparison = CompareTie(left, right, tieBreaker);
                if (comparison != 0)
                {
                    return comparison;
                }
            }
            return 0;
        });

    private static int CompareTie(
        EvaluatedCandidate left,
        EvaluatedCandidate right,
        CandidateTieBreaker tieBreaker) => tieBreaker switch
        {
            CandidateTieBreaker.LowerUtilization => NullableUtilization(left)
                .CompareTo(NullableUtilization(right)),
            CandidateTieBreaker.FewerBarMarks => left.Evaluation.Quantities
                .SteelItems.Count.CompareTo(
                    right.Evaluation.Quantities.SteelItems.Count),
            CandidateTieBreaker.LowerSectionDepth => left.Candidate.Physical
                .OverallDepthMm.CompareTo(
                    right.Candidate.Physical.OverallDepthMm),
            _ => StringComparer.Ordinal.Compare(
                left.Candidate.CandidateId,
                right.Candidate.CandidateId)
        };

    private static double NullableUtilization(EvaluatedCandidate item) =>
        item.Evaluation.MemberResult.GoverningUtilization ??
        double.PositiveInfinity;

    private static double ObjectiveSortValue(ObjectiveMetric metric) =>
        metric.Kind == CandidateObjectiveKind.UtilizationReserve
            ? -metric.Value
            : metric.Value;

    private static SearchTerminalState TerminalState(
        SearchStopReason stopReason,
        bool enumerationComplete,
        bool hasUnresolved,
        int incompleteCount,
        int rankedCount)
    {
        if (stopReason == SearchStopReason.EvaluationBudgetReached)
        {
            return SearchTerminalState.BudgetExhaustedIncomplete;
        }
        if (stopReason == SearchStopReason.Cancelled)
        {
            return SearchTerminalState.CancelledIncomplete;
        }
        if (!enumerationComplete || hasUnresolved || incompleteCount > 0)
        {
            return SearchTerminalState.EvidenceIncomplete;
        }
        return rankedCount == 0
            ? SearchTerminalState.NoFeasibleCandidate
            : SearchTerminalState.CompleteEnumeration;
    }

    private static CandidatePhysicalDefinition Physical(
        SectionCandidateChoice section,
        LongitudinalCandidateChoice longitudinal,
        TransverseCandidateChoice transverse) => new(
            section.WidthMm,
            section.OverallDepthMm,
            section.ConcreteStrengthNPerMm2,
            longitudinal.TopBarCount,
            longitudinal.TopBarDiameterMm,
            longitudinal.TopLayerCount,
            longitudinal.BottomBarCount,
            longitudinal.BottomBarDiameterMm,
            longitudinal.BottomLayerCount,
            longitudinal.SteelGradeNPerMm2,
            transverse.LinkDiameterMm,
            transverse.SteelGradeNPerMm2,
            transverse.Legs,
            transverse.SpacingMm);

    private static CandidateChangeCategory[] Changes(
        SectionCandidateChoice section,
        SectionCandidateChoice baseline)
    {
        var changes = new HashSet<CandidateChangeCategory>
        {
            CandidateChangeCategory.ActualBars,
            CandidateChangeCategory.Detailing,
            CandidateChangeCategory.BarPaths,
            CandidateChangeCategory.Bbs
        };
        foreach (var category in section.AdditionalChangeCategories ?? [])
        {
            changes.Add(category);
        }
        if (section.WidthMm != baseline.WidthMm ||
            section.OverallDepthMm != baseline.OverallDepthMm)
        {
            changes.Add(CandidateChangeCategory.SectionDimensionsProperty);
        }
        if (section.ConcreteStrengthNPerMm2 !=
            baseline.ConcreteStrengthNPerMm2)
        {
            changes.Add(CandidateChangeCategory.MaterialStiffness);
        }
        return changes.OrderBy(ChangeWire, StringComparer.Ordinal).ToArray();
    }

    private static CandidateCouplingClass Coupling(
        IEnumerable<CandidateChangeCategory> categories)
    {
        var values = categories.ToHashSet();
        if (values.Contains(CandidateChangeCategory.Unknown))
        {
            return CandidateCouplingClass.Unresolved;
        }
        return values.Any(IsReanalysisChange)
            ? CandidateCouplingClass.ReanalysisRequired
            : CandidateCouplingClass.FixedAction;
    }

    private static bool IsReanalysisChange(CandidateChangeCategory value) =>
        value is CandidateChangeCategory.SectionDimensionsProperty or
            CandidateChangeCategory.MaterialStiffness or
            CandidateChangeCategory.Releases or
            CandidateChangeCategory.Offsets or
            CandidateChangeCategory.MassSelfWeight or
            CandidateChangeCategory.AppliedLoad or
            CandidateChangeCategory.LoadCaseCombination or
            CandidateChangeCategory.SupportRestraint or
            CandidateChangeCategory.Meshing or
            CandidateChangeCategory.AnalysisSettings;

    private static string CandidateId(
        string domainId,
        string domainRevisionId,
        string sectionChoiceId,
        string longitudinalChoiceId,
        string transverseChoiceId,
        string physicalDefinitionId,
        IReadOnlyList<CandidateChangeCategory> changes) =>
        ResultFactory.SemanticId(
            "beam_candidate_id",
            new Dictionary<string, object?>
            {
                ["change_categories"] = changes.Select(ChangeWire).ToArray(),
                ["domain_id"] = domainId,
                ["domain_revision_id"] = domainRevisionId,
                ["longitudinal_choice_id"] = longitudinalChoiceId,
                ["physical_definition_id"] = physicalDefinitionId,
                ["section_choice_id"] = sectionChoiceId,
                ["transverse_choice_id"] = transverseChoiceId
            });

    private static string DomainSemanticId(
        string domainId,
        string domainRevisionId,
        string projectBasisId,
        string profileRevisionId,
        string memberId,
        string topologyRevisionId,
        string actionRevisionId,
        string designScopeRevisionId,
        string baselineAnalysisRevisionId,
        string baselineSectionChoiceId,
        IReadOnlyList<string> candidateIds) =>
        ResultFactory.SemanticId(
            "candidate_domain_id",
            new Dictionary<string, object?>
            {
                ["action_revision_id"] = actionRevisionId,
                ["baseline_analysis_revision_id"] = baselineAnalysisRevisionId,
                ["baseline_section_choice_id"] = baselineSectionChoiceId,
                ["candidate_ids"] = candidateIds,
                ["design_scope_revision_id"] = designScopeRevisionId,
                ["domain_id"] = domainId,
                ["domain_revision_id"] = domainRevisionId,
                ["member_id"] = memberId,
                ["profile_revision_id"] = profileRevisionId,
                ["project_basis_id"] = projectBasisId,
                ["topology_revision_id"] = topologyRevisionId,
                ["traversal_order"] = Traversal
            });

    private static bool Valid(SectionCandidateChoice item) =>
        Text(item.ChoiceId) &&
        Positive(item.WidthMm) &&
        Positive(item.OverallDepthMm) &&
        Positive(item.ConcreteStrengthNPerMm2) &&
        (item.AdditionalChangeCategories ?? []).Distinct().Count() ==
        (item.AdditionalChangeCategories ?? []).Count &&
        (item.AdditionalChangeCategories ?? []).All(category =>
            Enum.IsDefined(typeof(CandidateChangeCategory), category));

    private static bool Valid(LongitudinalCandidateChoice item) =>
        Text(item.ChoiceId) &&
        item.TopBarCount > 0 &&
        item.TopLayerCount > 0 &&
        item.BottomBarCount > 0 &&
        item.BottomLayerCount > 0 &&
        Positive(item.TopBarDiameterMm) &&
        Positive(item.BottomBarDiameterMm) &&
        Positive(item.SteelGradeNPerMm2);

    private static bool Valid(TransverseCandidateChoice item) =>
        Text(item.ChoiceId) &&
        item.Legs > 0 &&
        Positive(item.LinkDiameterMm) &&
        Positive(item.SteelGradeNPerMm2) &&
        Positive(item.SpacingMm);

    private static bool SameSection(
        SectionCandidateChoice left,
        SectionCandidateChoice right) =>
        left.ChoiceId == right.ChoiceId &&
        left.WidthMm == right.WidthMm &&
        left.OverallDepthMm == right.OverallDepthMm &&
        left.ConcreteStrengthNPerMm2 == right.ConcreteStrengthNPerMm2 &&
        (left.AdditionalChangeCategories ?? []).SequenceEqual(
            right.AdditionalChangeCategories ?? []);

    private static bool SamePhysical(
        CandidatePhysicalDefinition left,
        CandidatePhysicalDefinition right) =>
        left.WidthMm == right.WidthMm &&
        left.OverallDepthMm == right.OverallDepthMm &&
        left.ConcreteStrengthNPerMm2 == right.ConcreteStrengthNPerMm2 &&
        left.TopBarCount == right.TopBarCount &&
        left.TopBarDiameterMm == right.TopBarDiameterMm &&
        left.TopLayerCount == right.TopLayerCount &&
        left.BottomBarCount == right.BottomBarCount &&
        left.BottomBarDiameterMm == right.BottomBarDiameterMm &&
        left.BottomLayerCount == right.BottomLayerCount &&
        left.LongitudinalSteelGradeNPerMm2 ==
        right.LongitudinalSteelGradeNPerMm2 &&
        left.LinkDiameterMm == right.LinkDiameterMm &&
        left.LinkSteelGradeNPerMm2 == right.LinkSteelGradeNPerMm2 &&
        left.LinkLegs == right.LinkLegs &&
        left.LinkSpacingMm == right.LinkSpacingMm;

    private static bool UniqueChoiceIds(IEnumerable<string> values)
    {
        var items = values.ToArray();
        return items.All(Text) &&
               items.Distinct(StringComparer.Ordinal).Count() == items.Length;
    }

    private static bool TryNonnegativeDecimal(string value, out double result)
    {
        if (!Regex.IsMatch(
                value,
                "^(0|[0-9]+)(\\.[0-9]+)?$",
                RegexOptions.CultureInvariant) ||
            !decimal.TryParse(
                value,
                NumberStyles.AllowLeadingSign | NumberStyles.AllowDecimalPoint,
                CultureInfo.InvariantCulture,
                out var parsed) ||
            parsed < 0)
        {
            result = 0;
            return false;
        }
        result = (double)parsed;
        return double.IsFinite(result);
    }

    private static bool Positive(double value) =>
        double.IsFinite(value) && value > 0;

    private static bool Nonnegative(double value) =>
        double.IsFinite(value) && value >= 0;

    private static bool Text(string? value) =>
        !string.IsNullOrWhiteSpace(value);

    private static bool AllText(params string?[] values) =>
        values.All(Text);

    private static Diagnostic Error(string operation, string code) => new(
        code,
        "error",
        code,
        operation,
        "request",
        "optimization");

    private static string ChangeWire(CandidateChangeCategory value) => value switch
    {
        CandidateChangeCategory.ActualBars => "actual_bars",
        CandidateChangeCategory.Detailing => "detailing",
        CandidateChangeCategory.BarPaths => "bar_paths",
        CandidateChangeCategory.Bbs => "bbs",
        CandidateChangeCategory.RatesCost => "rates_cost",
        CandidateChangeCategory.ReportOptions => "report_options",
        CandidateChangeCategory.SectionDimensionsProperty =>
            "section_dimensions_property",
        CandidateChangeCategory.MaterialStiffness => "material_stiffness",
        CandidateChangeCategory.Releases => "releases",
        CandidateChangeCategory.Offsets => "offsets",
        CandidateChangeCategory.MassSelfWeight => "mass_self_weight",
        CandidateChangeCategory.AppliedLoad => "applied_load",
        CandidateChangeCategory.LoadCaseCombination => "load_case_combination",
        CandidateChangeCategory.SupportRestraint => "support_restraint",
        CandidateChangeCategory.Meshing => "meshing",
        CandidateChangeCategory.AnalysisSettings => "analysis_settings",
        CandidateChangeCategory.Unknown => "unknown",
        _ => throw new ArgumentOutOfRangeException(nameof(value))
    };

    private static string ObjectiveWire(CandidateObjectiveKind value) => value switch
    {
        CandidateObjectiveKind.Cost => "cost",
        CandidateObjectiveKind.SteelMass => "steel_mass",
        CandidateObjectiveKind.SectionDepth => "section_depth",
        CandidateObjectiveKind.Carbon => "carbon",
        CandidateObjectiveKind.ConcreteVolume => "concrete_volume",
        CandidateObjectiveKind.FormworkArea => "formwork_area",
        CandidateObjectiveKind.Congestion => "congestion",
        CandidateObjectiveKind.UtilizationReserve => "utilization_reserve",
        _ => "unknown"
    };

    private static string TerminalWire(SearchTerminalState value) => value switch
    {
        SearchTerminalState.CompleteEnumeration => "complete_enumeration",
        SearchTerminalState.BudgetExhaustedIncomplete =>
            "budget_exhausted_incomplete",
        SearchTerminalState.CancelledIncomplete => "cancelled_incomplete",
        SearchTerminalState.EvidenceIncomplete => "evidence_incomplete",
        SearchTerminalState.NoFeasibleCandidate => "no_feasible_candidate",
        _ => "unknown"
    };

    private sealed record EvaluatedCandidate(
        BeamCandidateDefinition Candidate,
        CandidateEvaluation Evaluation,
        IReadOnlyList<ObjectiveMetric> Metrics);
}

public static class CandidateDomainOperations
{
    public static ResultEnvelope<CandidateDomainOutput> Build(
        DiscreteCandidateDomain domain) =>
        OptimizationOperations.BuildCandidateDomain(domain);
}

public static class CandidateRankingOperations
{
    public static ResultEnvelope<CandidateRankingOutput> Rank(
        CandidateRankingRequest request) =>
        OptimizationOperations.RankCandidates(request);
}

public static class BeamOptimizationOperations
{
    public static ResultEnvelope<BeamOptimizationOutput> Optimize(
        BeamOptimizationRequest request) =>
        OptimizationOperations.OptimizeBeam(request);
}
