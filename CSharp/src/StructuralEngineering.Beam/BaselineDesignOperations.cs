using System.Text.Json;
using System.Runtime.InteropServices;
using StructuralEngineering.Analysis;
using StructuralEngineering.Codes.IS456;
using StructuralEngineering.Contracts;
using StructuralEngineering.Core;
using StructuralEngineering.Reinforcement;

namespace StructuralEngineering.Beam;

public static class BaselineDesignOperations
{
    public const string EngineRevision = "is456-baseline-design-wp11-v1";
    public static string EngineIdentity { get; } = ResultFactory.SemanticId("baseline_engine", new
    {
        semantic_revision = EngineRevision,
        runtime = Environment.Version.ToString(),
        platform = RuntimeInformation.RuntimeIdentifier,
        modules = new[] { typeof(BaselineDesignOperations), typeof(Flexure), typeof(BarPathOperations),
            typeof(ResultFactory), typeof(AnalysisSnapshotCodec), typeof(BaselineProjectInputs) }
            .Select(type => type.Assembly.ManifestModule.ModuleVersionId.ToString("D")).ToArray()
    });
    public const string ProfileId = "is456-ordinary-rectangular-simple-span-baseline-v1";
    public const string FireScopeOperation = "structural.beam.fire_scope/v1";

    public static FreshnessState Freshness(BaselineMemberDesignResult result, AnalysisSnapshot snapshot, BaselineProjectInputs inputs)
    {
        var mapped = BaselineInputMapper.Map(snapshot, inputs, result.MemberId);
        return result.EngineRevisionId == EngineIdentity && mapped.Beam?.EffectiveInputId == result.EffectiveInputId &&
            mapped.State == BaselineDesignState.Supported ? FreshnessState.Current : FreshnessState.Stale;
    }

    private static readonly DesignCheckRule[] Rules =
    [
        Rule("flexure", BeamOperations.FlexureCheckOperation, CheckScope.Station, "wp01"),
        Rule("shear", BeamOperations.ShearCheckOperation, CheckScope.Station, "wp02"),
        Rule("torsion", BeamOperations.TorsionCheckOperation, CheckScope.Station, "wp02"),
        Rule("arrangement", Detailing.ArrangementCheckOperation, CheckScope.Arrangement, "wp05"),
        Rule("anchorage", Detailing.AnchorageCheckOperation, CheckScope.BarEnd, "wp05"),
        Rule("stirrup_anchorage", BaselineStirrupAnchorage.Operation, CheckScope.Member, "stirrup"),
        Rule("continuity", BaselineContinuity.CheckOperation, CheckScope.Member, "continuity"),
        Rule("durability", BaselineEligibility.DurabilityOperation, CheckScope.Member, "eligibility"),
        Rule("lateral", BaselineEligibility.LateralStabilityOperation, CheckScope.Member, "eligibility"),
        Rule("paths", BarPathOperations.Operation, CheckScope.Member, null),
        Rule("seismic", Detailing.SeismicDetailingCheckOperation, CheckScope.Member, "seismic", ApplicabilityState.NotApplicable),
        Rule("fire_scope", FireScopeOperation, CheckScope.Member, null, ApplicabilityState.NotApplicable),
        Rule("deflection", Serviceability.DeflectionCheckOperation, CheckScope.Span, "wp04"),
        Rule("crack", Serviceability.CrackWidthCheckOperation, CheckScope.Face, "wp04")
    ];

    public static BaselineBatchDesignResult Design(AnalysisSnapshot snapshot, BaselineProjectInputs inputs,
        IReadOnlyList<string> memberIds, BaselineDesignOptions? options = null, CancellationToken cancellationToken = default,
        IProgress<(int Completed, int Total, string MemberId)>? progress = null)
    {
        options ??= new();
        var index = new BaselineSnapshotIndex(snapshot);
        var results = new List<BaselineMemberDesignResult>();
        foreach (var memberId in memberIds)
        {
            results.Add(DesignMapped(BaselineInputMapper.Map(index, inputs, memberId), inputs, memberId, options, cancellationToken));
            progress?.Report((results.Count, memberIds.Count, memberId));
        }
        return new(ResultFactory.SemanticId("baseline_request", new { snapshot.SnapshotSha256, inputs, memberIds, options, EngineIdentity }),
            snapshot.SnapshotId, inputs, options, results);
    }

    public static BaselineMemberDesignResult DesignMember(AnalysisSnapshot snapshot, BaselineProjectInputs inputs,
        string memberId, BaselineDesignOptions? options = null, CancellationToken cancellationToken = default)
    {
        options ??= new();
        var mapped = BaselineInputMapper.Map(snapshot, inputs, memberId);
        return DesignMapped(mapped, inputs, memberId, options, cancellationToken);
    }

    private static BaselineMemberDesignResult DesignMapped(BaselineMappingResult mapped, BaselineProjectInputs inputs,
        string memberId, BaselineDesignOptions options, CancellationToken cancellationToken)
    {
        if (mapped.Beam is null)
            return new(memberId, string.Empty, EngineIdentity, mapped.State switch
            {
                BaselineDesignState.Stale => BaselineRunState.Stale,
                BaselineDesignState.Unsupported => BaselineRunState.Unsupported,
                _ => BaselineRunState.NeedsInput
            }, 0, 0, null, mapped.Diagnostics);
        var beam = mapped.Beam;
        var seen = new HashSet<string>(StringComparer.Ordinal);
        if (options.MaximumCandidates <= 0)
            return Outcome(BaselineRunState.NeedsInput, 0, null, "SEARCH.INVALID_BUDGET", "A positive candidate limit is required.");
        var limit = Math.Min(options.MaximumCandidates, beam.Catalogue.MaximumCandidates);
        var evaluated = 0;
        BaselineCandidateEvaluation? last = null;
        BaselineCandidateEvaluation? unresolved = null;
        foreach (var arrangement in BaselineArrangements.Enumerate(beam))
        {
            if (cancellationToken.IsCancellationRequested)
                return Outcome(BaselineRunState.Cancelled, evaluated, last, "SEARCH.CANCELLED", "Design was cancelled; retained calculations are incomplete.");
            if (evaluated >= limit)
                return Outcome(BaselineRunState.Incomplete, evaluated, last, "SEARCH.BUDGET_EXHAUSTED", "The allowed candidate budget ended before the domain was exhausted.");
            if (!seen.Add(arrangement.RevisionId))
                return Outcome(BaselineRunState.Incomplete, evaluated, last, "SEARCH.REPEATED_ARRANGEMENT", "The deterministic search repeated an arrangement.");
            evaluated++;
            last = Evaluate(beam, inputs.Project, arrangement);
            if (last.Qualified)
                return Outcome(BaselineRunState.Complete, evaluated, last);
            if (last.Checks.Any(check => check.Result.Engineering == EngineeringState.NotEvaluated &&
                    check.Result.Applicability != ApplicabilityState.NotApplicable) ||
                last.MemberResult is { Engineering: EngineeringState.NotEvaluated })
                unresolved ??= last;
        }
        return unresolved is not null
            ? Outcome(BaselineRunState.NeedsInput, evaluated, unresolved, "CHECK.INCOMPLETE", "The finite domain contains unresolved required checks; no complete design is available.")
            : Outcome(BaselineRunState.NoFeasibleArrangement, evaluated, last, "SEARCH.NO_FEASIBLE_ARRANGEMENT",
                "No arrangement passed within the declared fixed-section catalogue and aligned-layer layout policy.");

        BaselineMemberDesignResult Outcome(BaselineRunState state, int count, BaselineCandidateEvaluation? design,
            string? code = null, string? message = null) => new(memberId, beam.EffectiveInputId, EngineIdentity, state,
                count, seen.Count, design, code is null ? [] : [new(code, "information", message!, EngineRevision,
                    "member:" + memberId, "baseline-design")]);
    }

    internal static BaselineCandidateEvaluation Evaluate(BoundBaselineBeam beam, BaselineProjectIdentity projectIdentity, BaselineArrangement arrangement)
    {
        var checks = new List<BaselineCheckEvidence>();
        var derivations = new List<ResultEnvelope<JsonElement>>();
        BaselineStrengthDetailChecks.Evaluate(beam, arrangement, ProfileId, checks, derivations);
        // Proven failed strength/fit/path candidates cannot qualify; avoid spending
        // service calculations on them. These are explicit failed search trials.
        if (checks.Any(check => check.Result.Engineering == EngineeringState.Fail))
            return new(arrangement, checks, derivations, null, false);
        BaselineServiceChecks.Evaluate(beam, arrangement, ProfileId, checks, derivations);
        var revisions = new[]
        {
            new RevisionBinding("wp01", "is456-wp01-v1", "WP01 normalized IS 456 source"),
            new RevisionBinding("wp02", "is456-wp02-v1", "WP02 normalized IS 456 source"),
            new RevisionBinding("wp04", "is456-wp04-v1", "WP04 normalized IS 456 source"),
            new RevisionBinding("wp05", "is456-amd6-wp05-v1", "WP05 normalized IS 456 source"),
            new RevisionBinding("continuity", "is456-amd6-wp11-v1", "WP11 explicit full-length construction policy"),
            new RevisionBinding("eligibility", "is456-baseline-eligibility-v1", "IS456 Tables 5/16 and clauses 26.4/23.3"),
            new RevisionBinding("stirrup", "is456-baseline-stirrup-v1", "IS456 clause 26.2.2.4(b) standard closed link"),
            new RevisionBinding("seismic", "is13920-2016-amd2-wp05-v1", "WP05 explicit applicability"),
            new RevisionBinding("service-producers", "is456-baseline-serviceability-v1", "WP11 controlled Figure4 and AnnexF source")
        };
        var project = BeamProjectOperations.Create(new(
            new(projectIdentity.ProjectId, projectIdentity.ProjectId, projectIdentity.RevisionId),
            new("mm", "N", "Nmm", "N/mm2"), revisions,
            new(ProfileId, EngineRevision, "IS 456:2000", SeismicDesignProfile.OrdinaryIs456, Rules,
                [new("nominal-cover", beam.Context.NominalCoverMm, "mm", beam.Context.EvidenceRevisionId)]),
            [new("reinforcement-catalogue", beam.Catalogue.RevisionId, projectIdentity.EvidenceReference)]));
        derivations.Add(BaselineEvidence.Pack(project));
        if (project.Outputs is null)
            return new(arrangement, checks, derivations, null, false);
        var scopes = new List<MemberScopeInstance>();
        var scopeRevision = ResultFactory.SemanticId("design_scope", new { beam.EffectiveInputId, arrangement.RevisionId, Rules });
        scopes.AddRange(beam.ActionRows.Where(r => r.Role == BaselineSelectionRole.Uls)
            .Select(r => new MemberScopeInstance(r.RowId, CheckScope.Station, scopeRevision)));
        scopes.AddRange(beam.ActionRows.Where(r => r.Role != BaselineSelectionRole.Uls)
            .Select(r => new MemberScopeInstance(r.RowId, CheckScope.Face, scopeRevision)));
        scopes.Add(new(beam.PhysicalSpanId, CheckScope.Span, scopeRevision));
        scopes.Add(new(arrangement.RevisionId, CheckScope.Arrangement, scopeRevision));
        scopes.AddRange(new[] { "left-support", "right-support", "left-full-development", "right-full-development" }
            .Select(id => new MemberScopeInstance(id, CheckScope.BarEnd, scopeRevision)));
        var leaves = checks.Select(check =>
        {
            var r = check.Result;
            return new MemberLeafEvidence(check.RuleId + "@" + check.ScopeId, r.OperationSemanticId, r.ResultId,
                r.Execution, r.Applicability, r.Engineering, r.Completeness, r.Freshness,
                r.Provenance.CodeDataRevisionId, r.Provenance.MethodRevisionId, r.NormalizedInputId, r.CalculationId,
                DiagnosticCodes: r.Diagnostics.Select(d => d.Code).ToArray());
        }).ToArray();
        var applicableRules = Rules.Where(rule => rule.ExpectedApplicability == ApplicabilityState.Applicable).Select(rule => rule.RuleId).ToHashSet();
        var dependentResults = checks.Where(check => applicableRules.Contains(check.RuleId)).Select(check => check.Result.ResultId)
            .Distinct(StringComparer.Ordinal).ToArray();
        var member = MemberDesignOperations.Design(new(project.Outputs, beam.MemberId, beam.Context.EvidenceRevisionId,
            beam.SnapshotId, arrangement.RevisionId, scopeRevision, scopes,
            [new(1, arrangement.RevisionId, Math.Min(arrangement.BottomEffectiveDepthMm, arrangement.TopEffectiveDepthMm), dependentResults, true)], leaves));
        return new(arrangement, checks, derivations, member, member.Outputs?.Qualified == true && BaselineEvidence.Qualified(member));
    }

    private static DesignCheckRule Rule(string id, string operation, CheckScope scope, string? binding,
        ApplicabilityState applicability = ApplicabilityState.Applicable) =>
        new(id, operation, scope, applicability, "WP11 frozen required-check profile", binding);
}
