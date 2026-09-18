using System.Text.Json;
using StructuralEngineering.Contracts;
using StructuralEngineering.Core;

namespace StructuralEngineering.Beam;

public static class BeamReviewOperations
{
    public static string EngineIdentity { get; } = ResultFactory.SemanticId("review_engine", new
    { baseline = BaselineDesignOperations.EngineIdentity, cost = typeof(StructuralEngineering.Construction.CostOperations).Assembly.ManifestModule.ModuleVersionId });
    public static readonly string[] StageIds = ["source", "core", "serviceability", "fire", "quantities", "cost", "section_alternatives", "reanalysis", "optimization", "overnight", "issued_report"];

    public static BeamReviewResult Review(AnalysisSnapshot? snapshot, BeamResolvedReview resolved,
        BeamReviewExample? example = null, BeamReviewResult? previous = null, CancellationToken cancellationToken = default,
        Func<AnalysisSnapshot, BeamResolvedMember, CancellationToken, BeamCorePreviewResult>? coreEvaluator = null,
        IReadOnlyDictionary<string, BeamReviewQuantityEvidence>? quantities = null, bool allowCostExample = false)
    {
        var reviews = new List<BeamMemberReview>();
        BaselineSnapshotIndex? index = null;
        BaselineMemberDesignResult? exampleCore = null;
        foreach (var scenario in resolved.Members)
        {
            var stages = StageIds.ToDictionary(x => x, x => new BeamReviewStage(x, BeamReviewAvailability.Unavailable,
                "Not evaluated", "Outside this provisional review's available evidence", []));
            var diagnostics = new List<Diagnostic>();
            BeamCorePreviewResult? core = null;
            IReadOnlyList<BaselineCheckEvidence> service = [];
            var prior = previous?.EngineIdentity == EngineIdentity && previous.SnapshotSha256 == resolved.Ledger.SnapshotSha256
                ? previous.Members.SingleOrDefault(x => x.MemberId == scenario.MemberId && x.StructuralRevision == scenario.StructuralRevision) : null;
            var sourceStatus = snapshot is null ? "Unavailable — retained source file is missing" : snapshot.Freshness.State != FreshnessState.Current
                ? "Historical captured source: " + snapshot.Freshness.State : "Captured offline source; live model not verified";
            stages["source"] = new("source", snapshot is null ? BeamReviewAvailability.Unavailable : BeamReviewAvailability.Available,
                sourceStatus, resolved.Ledger.SnapshotSha256, []);
            try
            {
                if (cancellationToken.IsCancellationRequested)
                    stages["core"] = new("core", BeamReviewAvailability.Cancelled, "Cancelled by user", scenario.StructuralRevision, []);
                else if (snapshot is not null)
                {
                    var code = resolved.Ledger.Fields.Single(x => x.SubjectId == scenario.MemberId && x.Key == "design.code").Value;
                    if (code != "IS 456:2000") throw new NotSupportedException("The selected design code has no qualified core profile.");
                    core = prior?.Core?.State is not (BaselineRunState.Cancelled or BaselineRunState.Failed) && prior?.Core is not null
                        ? prior.Core : coreEvaluator is not null ? coreEvaluator(snapshot, scenario, cancellationToken)
                            : BaselineDesignOperations.PreviewCore(index ??= new BaselineSnapshotIndex(snapshot), scenario, cancellationToken);
                    stages["core"] = new("core", core.Design is null ? BeamReviewAvailability.Unavailable : BeamReviewAvailability.Available,
                        core.State == BaselineRunState.Complete ? "Provisional core passes; required checks remain" : core.State.ToString(),
                        scenario.StructuralRevision, core.Design?.Checks.Select(x => x.Result.ResultId).ToArray() ?? []);
                    diagnostics.AddRange(core.Diagnostics);
                    if (core.State == BaselineRunState.Complete && core.Design is { } candidate)
                    {
                        service = prior?.ServiceChecks ?? ServiceChecks(index ??= new BaselineSnapshotIndex(snapshot), scenario, candidate.Arrangement);
                        stages["serviceability"] = new("serviceability", service.Count == 0 ? BeamReviewAvailability.Unavailable : BeamReviewAvailability.Available,
                            service.Count == 0 ? "Pending — distinct total and sustained SLS, screening permission and supported span required"
                                : service.All(x => BaselineEvidence.Qualified(x.Result)) ? "Provisional checks pass" : "Checks fail or remain unresolved",
                            "Uses captured SLS rows only; no scaling or fabricated service cases", service.Select(x => x.Result.ResultId).ToArray());
                    }
                }
            }
            catch (OperationCanceledException) { stages["core"] = new("core", BeamReviewAvailability.Cancelled, "Cancelled by user", scenario.StructuralRevision, []); }
            catch (Exception error)
            {
                stages["core"] = new("core", BeamReviewAvailability.Unavailable, "Calculation failed; peers continue", error.Message, []);
                diagnostics.Add(new("REVIEW.MEMBER_FAILED", "error", error.Message, "beam.provisional_review/v1", scenario.MemberId));
            }
            var fire = scenario.Inputs.MemberContexts[0].FireBasis!;
            stages["fire"] = new("fire", BeamReviewAvailability.Unavailable,
                fire.Requirement == BaselineFireRequirement.Required ? $"Pending — required {fire.RequiredMinutes} minute fire profile unavailable"
                    : "Scenario says no fire rating; project decision is unverified", fire.DecisionReference, []);
            stages["section_alternatives"] = new("section_alternatives", BeamReviewAvailability.Unavailable,
                scenario.AnalysisAlternative ? "Changed section — actions unverified until copied-model reanalysis" : "No section alternative verified",
                "Milestone D is required before an alternative becomes an analyzed design", []);
            stages["quantities"] = new("quantities", BeamReviewAvailability.Unavailable,
                "No compatible complete BBS/quantity package", "Core bar paths alone do not establish complete links, stock waste, concrete overlap or formwork ownership", []);
            stages["cost"] = new("cost", BeamReviewAvailability.Unavailable,
                "Rates saved; compatible quantities required", "No total is inferred from an incomplete quantity package", []);
            var cost = BeamReviewCostProjection.Project(scenario, resolved.Ledger, core, quantities?.GetValueOrDefault(scenario.MemberId), allowCostExample);
            if (cost is not null)
            {
                var label = cost.Availability == BeamReviewAvailability.Example
                    ? "Separate teaching example: 100 kg steel, 1 m3 concrete, 3 m2 formwork; not this beam's quantities"
                    : "Compatible current quantity package";
                stages["quantities"] = new("quantities", cost.Availability, label, cost.BasisId, [cost.Result.Outputs?.QuantityResultId ?? "unavailable"]);
                stages["cost"] = new("cost", cost.Result.Outputs is null ? BeamReviewAvailability.Unavailable : cost.Availability,
                    (cost.Availability == BeamReviewAvailability.Example ? "EXAMPLE ONLY: " : "Illustrative rates: ") +
                    (cost.Result.Outputs is { } priced ? priced.Currency + " " + priced.TotalDecimal : "Cost inputs rejected"),
                    cost.BasisId + "; excluded labour, plant, couplers, overhead and tax", [cost.Result.ResultId]);
            }
            BaselineMemberDesignResult? shownExample = null;
            if (core?.Design is null && !cancellationToken.IsCancellationRequested && example is not null)
            {
                try
                {
                    exampleCore ??= BaselineDesignOperations.DesignMember(example.Snapshot, example.Inputs, example.MemberId, cancellationToken: cancellationToken);
                    shownExample = exampleCore;
                    // The original source/core stage and member remain unchanged. Example evidence has its own identity.
                    stages.Add("named_example", new("named_example", BeamReviewAvailability.Example, exampleCore.State.ToString(),
                        example.Id + " / " + example.Snapshot.SnapshotSha256 + " / " + example.MemberId,
                        exampleCore.Design?.Checks.Select(x => x.Result.ResultId).ToArray() ?? []));
                }
                catch (Exception error) when (error is not OperationCanceledException)
                { stages.Add("named_example", new("named_example", BeamReviewAvailability.Unavailable, "Example unavailable", error.Message, [])); }
            }
            reviews.Add(new(scenario.MemberId, sourceStatus,
                scenario.AnalysisAlternative ? "Assumed section alternative; analysis unverified" : "Persistent provisional assumptions; source facts preserved",
                stages["core"].Status, "Not qualified — provisional inputs and required checks are not a full design", true,
                scenario.StructuralRevision, core, null, stages.Values.ToArray(), diagnostics, shownExample, service, cost));
        }
        return new(ResultFactory.SemanticId("beam_review", new
        {
            resolved.Ledger.Revision,
            EngineIdentity,
            sourceAvailable = snapshot is not null,
            example = example?.Id,
            allowCostExample,
            quantities = quantities?.OrderBy(x => x.Key, StringComparer.Ordinal).Select(x => new { x.Key, x.Value.StructuralRevision, x.Value.Result.ResultId }).ToArray()
        }),
            EngineIdentity, resolved.Ledger.SnapshotSha256, resolved.Ledger, reviews, true,
            example?.Id ?? "unavailable", "Not requested — this operation performs no ETABS acquisition, analysis or save");
    }

    private static IReadOnlyList<BaselineCheckEvidence> ServiceChecks(BaselineSnapshotIndex index, BeamResolvedMember scenario, BaselineArrangement arrangement)
    {
        var context = scenario.Inputs.MemberContexts[0];
        var map = BaselineInputMapper.MapCore(index, scenario.Inputs, scenario.MemberId);
        if (map.Beam is not { } beam || !context.ScreeningPermitted || context.EffectiveSpanMm > 10000 ||
            new[] { BaselineSelectionRole.SlsTotal, BaselineSelectionRole.SlsSustained }.Any(role => !beam.ActionRows.Any(x => x.Role == role))) return [];
        beam = beam with { WidthMm = scenario.WidthMm, DepthMm = scenario.DepthMm };
        var checks = new List<BaselineCheckEvidence>();
        BaselineServiceChecks.Evaluate(beam, arrangement, BaselineDesignOperations.ProfileId, checks, new List<ResultEnvelope<JsonElement>>());
        return checks;
    }
}
