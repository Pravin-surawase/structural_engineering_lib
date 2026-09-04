using StructuralEngineering.Contracts;
using StructuralEngineering.Core;
using StructuralEngineering.Optimization;
using Xunit;

namespace StructuralEngineering.Tests;

public sealed class Wp08Tests
{
    private static readonly Provenance TestProvenance = new(
        "test-data-r1", "test-method-r1", ["WP08 test fixture"]);

    [Fact]
    public void OneCandidateDomainMatchesPythonCanonicalIds()
    {
        var output = CandidateDomainOperations.Build(
            Domain(longitudinal: [Longitudinal("L1", 3)])).Outputs!;
        var candidate = Assert.Single(output.Candidates);

        Assert.Equal(
            "candidate_physical_definition_id:pf4-canonical-json-v1:" +
            "90ee7462f17213d30ad5db1b1ffa7b3b6e457da10fb1af83a40c730d8ce600b1",
            candidate.PhysicalDefinitionId);
        Assert.Equal(
            "beam_candidate_id:pf4-canonical-json-v1:" +
            "8e1523fd24a52bde7a96f47fa8608e98301aebf4f17319082ddc1e910084873e",
            candidate.CandidateId);
        Assert.Equal(
            "candidate_domain_id:pf4-canonical-json-v1:" +
            "cf3a07c34d286a5336bd7f1a3c1d8a748cecc31e66f3a849539ae4f251917807",
            output.DomainSemanticId);
    }

    [Fact]
    public void PhysicalDuplicateLabelsAreRetainedAndEvaluatedOnce()
    {
        var domainRequest = Domain(longitudinal:
        [
            Longitudinal("L-A", 3),
            Longitudinal("L-B", 3)
        ]);
        var domain = CandidateDomainOperations.Build(domainRequest).Outputs!;
        var result = Rank(
            domainRequest,
            [Evaluation(domain.Candidates[0].CandidateId)]);

        Assert.Equal(
            domain.Candidates[0].PhysicalDefinitionId,
            domain.Candidates[1].PhysicalDefinitionId);
        Assert.Equal(1, result.Outputs!.Performance.DuplicatePhysicalCandidateCount);
        Assert.Contains(
            result.Outputs.Exclusions,
            item => item.Disposition ==
                    CandidateDisposition.DuplicatePhysicalDefinition);
        Assert.Equal(2, result.Outputs.EvaluationRecords.Count);
    }

    [Fact]
    public void DomainBoundAndPortableSafetyCeilingAreEnforced()
    {
        var tooSmall = CandidateDomainOperations.Build(
            Domain(maximum: 1));
        var tooLarge = CandidateDomainOperations.Build(
            Domain(maximum: 100_001));

        Assert.Equal(ExecutionState.RejectedInput, tooSmall.Execution);
        Assert.Equal(ExecutionState.RejectedInput, tooLarge.Execution);
    }

    [Fact]
    public void OnlyThirdCandidateFeasibleIsSelectedAfterCompleteSearch()
    {
        var domainRequest = Domain();
        var candidates = CandidateDomainOperations.Build(domainRequest).Outputs!.Candidates;
        var evaluations = candidates.Select((item, index) => Evaluation(
            item.CandidateId,
            engineering: index == 2
                ? EngineeringState.Pass
                : EngineeringState.Fail)).ToArray();

        var result = Rank(domainRequest, evaluations);

        Assert.Equal(EngineeringState.Pass, result.Engineering);
        Assert.Equal(candidates[2].CandidateId, result.Outputs!.SelectedCandidateId);
        Assert.True(result.Outputs.OptimalityClaimed);
        Assert.Equal(2, result.Outputs.Performance.EngineeringFailCount);
    }

    [Fact]
    public void OrderedNumericObjectivesAndCandidateIdTieAreDeterministic()
    {
        var domainRequest = Domain();
        var candidates = CandidateDomainOperations.Build(domainRequest).Outputs!.Candidates;
        var evaluations = new[]
        {
            Evaluation(candidates[0].CandidateId, steelKg: 100, cost: 20),
            Evaluation(candidates[1].CandidateId, steelKg: 20, cost: 100),
            Evaluation(candidates[2].CandidateId, steelKg: 20, cost: 90)
        };
        var profile = Profile(
            CandidateObjectiveKind.SteelMass,
            CandidateObjectiveKind.Cost);

        var result = Rank(domainRequest, evaluations, profile: profile);

        Assert.Equal(
            candidates[2].CandidateId,
            result.Outputs!.RankedCandidates[0].CandidateId);
        Assert.Equal(
            CandidateTieBreaker.CandidateId,
            result.Outputs.EffectiveTieBreakers[^1]);
        Assert.Equal(
            [20d, 90d],
            result.Outputs.RankedCandidates[0].ObjectiveMetrics
                .Select(item => item.Value));
    }

    [Fact]
    public void MissingRequiredSlsLeafIsIncompleteAfterFullEnumeration()
    {
        var expected = new[] { Expectation(), Expectation("sls@member") };
        var context = Context(expected);
        var domainRequest = Domain(longitudinal: [Longitudinal("L1", 3)]);
        var candidate = CandidateDomainOperations.Build(domainRequest).Outputs!
            .Candidates[0];

        var result = Rank(
            domainRequest,
            [Evaluation(candidate.CandidateId)],
            context: context);

        Assert.Equal(SearchTerminalState.EvidenceIncomplete, result.Outputs!.TerminalState);
        Assert.True(result.Outputs.EnumerationComplete);
        Assert.False(result.Outputs.OptimalityClaimed);
    }

    [Fact]
    public void ProfileExpectedNotApplicableQualifies()
    {
        var expected = new[]
        {
            Expectation("torsion@member", ApplicabilityState.NotApplicable)
        };
        var context = Context(expected);
        var domainRequest = Domain(longitudinal: [Longitudinal("L1", 3)]);
        var candidate = CandidateDomainOperations.Build(domainRequest).Outputs!
            .Candidates[0];

        var result = Rank(
            domainRequest,
            [Evaluation(candidate.CandidateId, expected: expected)],
            context: context);

        Assert.Equal(SearchTerminalState.CompleteEnumeration, result.Outputs!.TerminalState);
        Assert.True(result.Outputs.OptimalityClaimed);
    }

    [Fact]
    public void RequiredApplicableNotApplicableCannotBecomeWinner()
    {
        var expected = new[] { Expectation("sls@member") };
        var context = Context(expected);
        var domainRequest = Domain(longitudinal: [Longitudinal("L1", 3)]);
        var candidate = CandidateDomainOperations.Build(domainRequest).Outputs!
            .Candidates[0];
        var evaluation = Evaluation(
            candidate.CandidateId,
            engineering: EngineeringState.NotEvaluated,
            expected: expected,
            applicabilityOverride: ApplicabilityState.NotApplicable);

        var result = Rank(domainRequest, [evaluation], context: context);

        Assert.Equal(SearchTerminalState.EvidenceIncomplete, result.Outputs!.TerminalState);
        Assert.Empty(result.Outputs.RankedCandidates);
        Assert.False(result.Outputs.OptimalityClaimed);
    }

    [Fact]
    public void BudgetAndCancellationRetainOnlyProvisionalResults()
    {
        var domainRequest = Domain();
        var candidates = CandidateDomainOperations.Build(domainRequest).Outputs!.Candidates;
        var evaluation = Evaluation(candidates[0].CandidateId, cost: 500);

        var budget = Rank(
            domainRequest,
            [evaluation],
            budget: 1,
            stop: SearchStopReason.EvaluationBudgetReached);
        var cancelled = Rank(
            domainRequest,
            [evaluation],
            budget: 3,
            stop: SearchStopReason.Cancelled);

        Assert.Equal(
            SearchTerminalState.BudgetExhaustedIncomplete,
            budget.Outputs!.TerminalState);
        Assert.Equal(candidates[0].CandidateId, budget.Outputs.BestEvaluatedCandidateId);
        Assert.Null(budget.Outputs.SelectedCandidateId);
        Assert.True(budget.Outputs.ProvisionalShortlist);
        Assert.Equal(
            SearchTerminalState.CancelledIncomplete,
            cancelled.Outputs!.TerminalState);
        Assert.False(cancelled.Outputs.OptimalityClaimed);
        Assert.False(cancelled.Outputs.InfeasibleClaimed);
    }

    [Fact]
    public void CompleteAllFailDomainCanClaimFiniteDomainInfeasibility()
    {
        var domainRequest = Domain();
        var candidates = CandidateDomainOperations.Build(domainRequest).Outputs!.Candidates;
        var evaluations = candidates.Select(item => Evaluation(
            item.CandidateId, engineering: EngineeringState.Fail)).ToArray();

        var result = Rank(domainRequest, evaluations);

        Assert.Equal(EngineeringState.Fail, result.Engineering);
        Assert.Equal(
            SearchTerminalState.NoFeasibleCandidate,
            result.Outputs!.TerminalState);
        Assert.True(result.Outputs.InfeasibleClaimed);
    }

    [Fact]
    public void FixedActionsAllowsSectionStudyWithCommonForceScope()
    {
        var domainRequest = Domain(
            sections:
            [
                new SectionCandidateChoice("S1", 300, 500, 25),
                new SectionCandidateChoice("S2", 300, 600, 25)
            ],
            longitudinal: [Longitudinal("L1", 3)]);
        var candidates = CandidateDomainOperations.Build(domainRequest).Outputs!.Candidates;
        var changed = Assert.Single(candidates, item =>
            item.ChangeCategories.Contains(
                CandidateChangeCategory.SectionDimensionsProperty));

        var result = Rank(
            domainRequest,
            candidates.Select(item => Evaluation(item.CandidateId)).ToArray());

        Assert.Equal(CandidateCouplingClass.ReanalysisRequired, changed.CouplingClass);
        Assert.Equal(
            "finite_domain_fixed_actions_common_force_assumption",
            result.Outputs!.OptimalityScope);
        Assert.True(result.Outputs.OptimalityClaimed);
    }

    [Fact]
    public void CoupledSectionChangeRequiresFreshCandidateAnalysis()
    {
        var domainRequest = SectionStudyDomain();
        var candidates = CandidateDomainOperations.Build(domainRequest).Outputs!.Candidates;
        var evaluations = candidates.Select(item => Evaluation(item.CandidateId)).ToArray();

        var result = Rank(
            domainRequest,
            evaluations,
            mode: AnalysisMode.CoupledReanalysis,
            policy: new ReanalysisPolicy("P1", "r1", true, "owned model"));

        Assert.Equal(SearchTerminalState.EvidenceIncomplete, result.Outputs!.TerminalState);
        Assert.Contains(
            result.Outputs.Exclusions,
            item => item.ReasonCodes.Contains("REANALYSIS.EVIDENCE_REQUIRED"));
    }

    [Fact]
    public void CoupledSectionChangeAcceptsBoundFreshAnalysis()
    {
        var domainRequest = SectionStudyDomain();
        var candidates = CandidateDomainOperations.Build(domainRequest).Outputs!.Candidates;
        var evaluations = candidates.Select(item =>
        {
            if (item.CouplingClass == CandidateCouplingClass.FixedAction)
            {
                return Evaluation(item.CandidateId);
            }

            var analysisId = $"analysis-{item.CandidateId}";
            return Evaluation(
                item.CandidateId,
                analysisRevisionId: analysisId,
                reanalysis: new CandidateReanalysisEvidence(
                    item.CandidateId,
                    item.PhysicalDefinitionId,
                    "analysis-r1",
                    analysisId,
                    $"snapshot-{item.CandidateId}",
                    $"snapshot-payload-{item.CandidateId}",
                    true,
                    true));
        }).ToArray();

        var result = Rank(
            domainRequest,
            evaluations,
            mode: AnalysisMode.CoupledReanalysis,
            policy: new ReanalysisPolicy("P1", "r1", true, "owned model"));

        Assert.Equal(
            SearchTerminalState.CompleteEnumeration,
            result.Outputs!.TerminalState);
        Assert.True(result.Outputs.OptimalityClaimed);
    }

    [Fact]
    public void DetachedQuantityPayloadIsIncomplete()
    {
        var domainRequest = Domain(longitudinal: [Longitudinal("L1", 3)]);
        var candidate = CandidateDomainOperations.Build(domainRequest).Outputs!
            .Candidates[0];
        var evaluation = Evaluation(candidate.CandidateId);
        var detached = evaluation with
        {
            Quantities = evaluation.Quantities with { SteelScheduledMassKg = 1 }
        };

        var result = Rank(domainRequest, [detached]);

        Assert.Equal(SearchTerminalState.EvidenceIncomplete, result.Outputs!.TerminalState);
        Assert.Contains(
            "QUANTITY.PAYLOAD_MISMATCH",
            result.Outputs.Exclusions[0].ReasonCodes);
    }

    [Fact]
    public void CostObjectiveRejectsNonportableDecimalNotation()
    {
        var domainRequest = Domain(longitudinal: [Longitudinal("L1", 3)]);
        var candidate = CandidateDomainOperations.Build(domainRequest).Outputs!
            .Candidates[0];
        var evaluation = Evaluation(candidate.CandidateId);
        var invalidCost = evaluation.Cost! with { TotalDecimal = "1e3" };
        var invalidEnvelope = Envelope(
            invalidCost,
            "structural.construction_cost.estimate/v1",
            EngineeringState.Pass);
        var invalid = evaluation with
        {
            Cost = invalidCost,
            CostBinding = OptimizationOperations.CandidateResultBinding(
                invalidEnvelope, invalidCost)
        };

        var result = Rank(domainRequest, [invalid]);

        Assert.Equal(SearchTerminalState.EvidenceIncomplete, result.Outputs!.TerminalState);
        Assert.Contains("COST.TOTAL_INVALID", result.Outputs.Exclusions[0].ReasonCodes);
    }

    [Fact]
    public void StaleFailedLeafCannotSupportInfeasibilityClaim()
    {
        var domainRequest = Domain(longitudinal: [Longitudinal("L1", 3)]);
        var candidate = CandidateDomainOperations.Build(domainRequest).Outputs!
            .Candidates[0];
        var evaluation = Evaluation(
            candidate.CandidateId, engineering: EngineeringState.Fail);
        var qualification = evaluation.MemberResult.LeafQualifications[0];
        var staleEvidence = qualification.Evidence! with
        {
            Freshness = FreshnessState.Stale
        };
        var staleMember = evaluation.MemberResult with
        {
            LeafQualifications =
            [
                qualification with { Evidence = staleEvidence }
            ]
        };
        var memberEnvelope = Envelope(
            staleMember,
            "is456.beam_member.design/v1",
            EngineeringState.Fail);
        var stale = evaluation with
        {
            MemberResult = staleMember,
            MemberBinding = OptimizationOperations.CandidateResultBinding(
                memberEnvelope, staleMember)
        };

        var result = Rank(domainRequest, [stale]);

        Assert.Equal(SearchTerminalState.EvidenceIncomplete, result.Outputs!.TerminalState);
        Assert.False(result.Outputs.InfeasibleClaimed);
        Assert.Contains(
            result.Outputs.Exclusions[0].ReasonCodes,
            reason => reason.EndsWith("FAIL_STATE_INVALID", StringComparison.Ordinal));
    }

    [Fact]
    public void NegativeCouplerCountIsIncompleteQuantityEvidence()
    {
        var domainRequest = Domain(longitudinal: [Longitudinal("L1", 3)]);
        var candidate = CandidateDomainOperations.Build(domainRequest).Outputs!
            .Candidates[0];
        var evaluation = Evaluation(candidate.CandidateId);
        var invalidQuantities = evaluation.Quantities with { CouplerCount = -1 };
        var quantityEnvelope = Envelope(
            invalidQuantities,
            "structural.construction_quantities.calculate/v1",
            EngineeringState.Pass);
        var invalid = evaluation with
        {
            QuantityBinding = OptimizationOperations.CandidateResultBinding(
                quantityEnvelope, invalidQuantities),
            Quantities = invalidQuantities,
            CostBinding = null,
            Cost = null
        };

        var result = Rank(
            domainRequest,
            [invalid],
            profile: Profile(CandidateObjectiveKind.SteelMass));

        Assert.Equal(SearchTerminalState.EvidenceIncomplete, result.Outputs!.TerminalState);
        Assert.Contains("QUANTITY.NONFINITE", result.Outputs.Exclusions[0].ReasonCodes);
    }

    [Fact]
    public void CostObjectiveRequiresNonblankCurrency()
    {
        var domainRequest = Domain(longitudinal: [Longitudinal("L1", 3)]);
        var candidate = CandidateDomainOperations.Build(domainRequest).Outputs!
            .Candidates[0];
        var evaluation = Evaluation(candidate.CandidateId);
        var invalidCost = evaluation.Cost! with { Currency = "" };
        var costEnvelope = Envelope(
            invalidCost,
            "structural.construction_cost.estimate/v1",
            EngineeringState.Pass);
        var invalid = evaluation with
        {
            Cost = invalidCost,
            CostBinding = OptimizationOperations.CandidateResultBinding(
                costEnvelope, invalidCost)
        };

        var result = Rank(domainRequest, [invalid]);

        Assert.Equal(SearchTerminalState.EvidenceIncomplete, result.Outputs!.TerminalState);
        Assert.Contains(
            "OBJECTIVE.COST_MISSING",
            result.Outputs.Exclusions[0].ReasonCodes);
    }

    [Fact]
    public void ForgedDomainCandidateIdentityIsRejected()
    {
        var domainRequest = Domain(longitudinal: [Longitudinal("L1", 3)]);
        var domain = CandidateDomainOperations.Build(domainRequest).Outputs!;
        var forged = domain with
        {
            Candidates =
            [
                domain.Candidates[0] with
                {
                    Physical = domain.Candidates[0].Physical with
                    {
                        OverallDepthMm = 999
                    }
                }
            ]
        };
        var evaluation = Evaluation(domain.Candidates[0].CandidateId);
        var request = RankingRequest(
            forged,
            [evaluation],
            Context(),
            Profile(),
            AnalysisMode.FixedActions,
            null,
            1,
            SearchStopReason.Completed);

        var result = CandidateRankingOperations.Rank(request);

        Assert.Equal(ExecutionState.RejectedInput, result.Execution);
        Assert.Equal("DOMAIN.CANDIDATE_IDENTITY", result.Diagnostics[0].Code);
    }

    private static ResultEnvelope<CandidateRankingOutput> Rank(
        DiscreteCandidateDomain domainRequest,
        IReadOnlyList<CandidateEvaluation> evaluations,
        CandidateRankingContext? context = null,
        CandidateObjectiveProfile? profile = null,
        AnalysisMode mode = AnalysisMode.FixedActions,
        ReanalysisPolicy? policy = null,
        int? budget = null,
        SearchStopReason stop = SearchStopReason.Completed)
    {
        var domain = CandidateDomainOperations.Build(domainRequest).Outputs!;
        return CandidateRankingOperations.Rank(RankingRequest(
            domain,
            evaluations,
            context ?? Context(),
            profile ?? Profile(),
            mode,
            policy,
            budget ?? evaluations.Count,
            stop));
    }

    private static CandidateRankingRequest RankingRequest(
        CandidateDomainOutput domain,
        IReadOnlyList<CandidateEvaluation> evaluations,
        CandidateRankingContext context,
        CandidateObjectiveProfile profile,
        AnalysisMode mode,
        ReanalysisPolicy? policy,
        int budget,
        SearchStopReason stop) => new(
            "rank-r1",
            context,
            domain,
            profile,
            mode,
            policy,
            budget,
            stop,
            evaluations);

    private static DiscreteCandidateDomain SectionStudyDomain() => Domain(
        sections:
        [
            new SectionCandidateChoice("S1", 300, 500, 25),
            new SectionCandidateChoice("S2", 300, 600, 25)
        ],
        longitudinal: [Longitudinal("L1", 3)]);

    private static DiscreteCandidateDomain Domain(
        IReadOnlyList<SectionCandidateChoice>? sections = null,
        IReadOnlyList<LongitudinalCandidateChoice>? longitudinal = null,
        int maximum = 100) => new(
            "domain-r1",
            "domain-revision-r1",
            "project-r1",
            "profile-r1",
            "B1",
            "topology-r1",
            "actions-r1",
            "scope-r1",
            "analysis-r1",
            "S1",
            sections ?? [new SectionCandidateChoice("S1", 300, 500, 25)],
            longitudinal ??
            [
                Longitudinal("L1", 3),
                Longitudinal("L2", 4),
                Longitudinal("L3", 5)
            ],
            [new TransverseCandidateChoice("T1", 8, 500, 2, 150)],
            maximum,
            ["WP08 test domain"],
            ["Finite declared choices only"]);

    private static LongitudinalCandidateChoice Longitudinal(
        string id,
        int bottomCount) => new(
            id, 2, 16, 1, bottomCount, 20, 1, 500);

    private static CandidateObjectiveProfile Profile(
        params CandidateObjectiveKind[] objectives) => new(
            "objectives-r1",
            "objectives-revision-r1",
            objectives.Length == 0 ? [CandidateObjectiveKind.Cost] : objectives,
            [
                CandidateTieBreaker.LowerUtilization,
                CandidateTieBreaker.FewerBarMarks
            ]);

    private static CandidateRankingContext Context(
        IReadOnlyList<MemberLeafExpectation>? expected = null)
    {
        var member = Member("reference", expected: expected);
        var envelope = Envelope(
            member, "is456.beam_member.design/v1", EngineeringState.Pass);
        return new CandidateRankingContext(
            "project-r1",
            "profile-r1",
            "B1",
            "topology-r1",
            "actions-r1",
            "scope-r1",
            "analysis-r1",
            envelope.ResultId,
            OptimizationOperations.CandidateResultBinding(envelope, member),
            member);
    }

    private static CandidateEvaluation Evaluation(
        string candidateId,
        EngineeringState engineering = EngineeringState.Pass,
        IReadOnlyList<MemberLeafExpectation>? expected = null,
        ApplicabilityState? applicabilityOverride = null,
        double steelKg = 100,
        double cost = 1000,
        double utilization = 0.8,
        string analysisRevisionId = "analysis-r1",
        CandidateReanalysisEvidence? reanalysis = null)
    {
        var member = Member(
            candidateId,
            engineering,
            expected,
            applicabilityOverride,
            utilization);
        var memberEnvelope = Envelope(
            member,
            "is456.beam_member.design/v1",
            engineering);
        var quantities = Quantities(candidateId, steelKg);
        var quantityEnvelope = Envelope(
            quantities,
            "structural.construction_quantities.calculate/v1",
            EngineeringState.Pass);
        var costOutput = Cost(candidateId, quantityEnvelope.ResultId, cost);
        var costEnvelope = Envelope(
            costOutput,
            "structural.construction_cost.estimate/v1",
            EngineeringState.Pass);
        return new CandidateEvaluation(
            candidateId,
            analysisRevisionId,
            OptimizationOperations.CandidateResultBinding(memberEnvelope, member),
            member,
            OptimizationOperations.CandidateResultBinding(
                quantityEnvelope, quantities),
            quantities,
            OptimizationOperations.CandidateResultBinding(costEnvelope, costOutput),
            costOutput,
            ReanalysisEvidence: reanalysis);
    }

    private static MemberDesignOutput Member(
        string candidateId,
        EngineeringState state = EngineeringState.Pass,
        IReadOnlyList<MemberLeafExpectation>? expected = null,
        ApplicabilityState? applicabilityOverride = null,
        double utilization = 0.8)
    {
        var expectations = expected ?? [Expectation()];
        var qualifications = new List<MemberLeafQualification>();
        foreach (var expectation in expectations)
        {
            var applicability = applicabilityOverride ??
                                expectation.ExpectedApplicability;
            var evidenceState = applicability == ApplicabilityState.NotApplicable
                ? EngineeringState.NotEvaluated
                : state;
            var qualified = applicability == expectation.ExpectedApplicability &&
                (applicability == ApplicabilityState.Applicable
                    ? evidenceState == EngineeringState.Pass
                    : evidenceState == EngineeringState.NotEvaluated);
            var evidence = new MemberLeafEvidence(
                expectation.LeafId,
                expectation.OperationSemanticId,
                $"leaf-result-{candidateId}-{expectation.LeafId}",
                ExecutionState.Completed,
                applicability,
                evidenceState,
                CompletenessState.CompleteForScope,
                FreshnessState.Current,
                "test-data-r1",
                "test-method-r1",
                $"leaf-input-{candidateId}-{expectation.LeafId}",
                $"leaf-calc-{candidateId}-{expectation.LeafId}",
                GoverningUtilization: utilization,
                DiagnosticCodes: []);
            qualifications.Add(new MemberLeafQualification(
                expectation,
                evidence,
                qualified,
                qualified
                    ? []
                    : evidenceState == EngineeringState.Fail
                        ? ["LEAF.FAIL"]
                        : ["LEAF.APPLICABILITY_MISMATCH"]));
        }

        var qualifiedMember = qualifications.All(item => item.Qualified);
        return new MemberDesignOutput(
            "project-r1",
            "profile-r1",
            "B1",
            "topology-r1",
            "actions-r1",
            candidateId,
            "scope-r1",
            expectations,
            qualifications,
            [],
            expectations[0].LeafId,
            qualifications[0].Evidence!.ResultId,
            utilization,
            qualifiedMember);
    }

    private static MemberLeafExpectation Expectation(
        string leafId = "uls@member",
        ApplicabilityState applicability = ApplicabilityState.Applicable)
    {
        var rule = leafId.Split('@')[0];
        return new MemberLeafExpectation(
            leafId,
            rule,
            $"test.{rule}/v1",
            "B1",
            CheckScope.Member,
            applicability,
            "test-data-r1");
    }

    private static ResultEnvelope<T> Envelope<T>(
        T payload,
        string operation,
        EngineeringState engineering) => ResultFactory.Completed(
            operation,
            ResultFactory.Effective(("fixture", "wp08")),
            payload,
            TestProvenance,
            engineering);

    private static ConstructionQuantityOutput Quantities(
        string candidateId,
        double steelKg) => new(
            "profile-r1",
            "project-r1",
            "B1",
            candidateId,
            $"bbs-{candidateId}",
            "concrete-policy-r1",
            "formwork-policy-r1",
            [],
            [],
            [],
            new WasteLedger(0, 0, 0),
            steelKg,
            steelKg,
            0.9,
            7.8,
            0);

    private static ConstructionCostOutput Cost(
        string candidateId,
        string quantityResultId,
        double total)
    {
        var value = total.ToString("F2", System.Globalization.CultureInfo.InvariantCulture);
        return new ConstructionCostOutput(
            "profile-r1",
            "project-r1",
            "B1",
            candidateId,
            quantityResultId,
            "rates-r1",
            "rates-revision-r1",
            "INR",
            "2026-09-04",
            "India",
            "test-rate-source",
            [],
            [],
            [],
            value,
            "0.00",
            value,
            "0.00",
            value);
    }
}
