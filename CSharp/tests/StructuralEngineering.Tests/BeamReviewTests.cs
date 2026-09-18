using System.Text.Json;
using StructuralEngineering.Beam;
using StructuralEngineering.Contracts;
using StructuralEngineering.Construction;
using StructuralEngineering.Core;
using Xunit;

namespace StructuralEngineering.Tests;

public class BeamReviewTests
{
    private static BeamReviewPreset Preset()
    {
        using var stream = typeof(BeamReviewTests).Assembly.GetManifestResourceStream("DemoPreset.json")!;
        using var reader = new StreamReader(stream);
        return BeamReviewPresetReader.Parse(reader.ReadToEnd());
    }

    [Fact]
    public void BlankSupplementalInputsResolveAllFieldsWithoutChangingSourceOrFire()
    {
        var snapshot = BaselineDesignTests.LoadOwnedSnapshot();
        var before = ResultFactory.CanonicalJsonBytes(snapshot);
        var resolved = BeamReviewResolver.Resolve(snapshot, snapshot.Members.Select(x => x.MemberId).ToArray(), Preset());
        Assert.Equal(3, resolved.Members.Count);
        Assert.All(resolved.Members, member =>
        {
            Assert.False(member.Inputs.Project.ValuesAccepted);
            Assert.Equal(60, member.Inputs.MemberContexts[0].FireBasis!.RequiredMinutes);
            Assert.Equal(25, member.Inputs.Materials[0].ConcreteStrengthNPerMm2);
            Assert.Equal(30, member.Inputs.MemberContexts[0].NominalCoverMm);
            Assert.Equal([12000d], member.Inputs.Catalogue.StockLengthsMm);
        });
        Assert.All(resolved.Ledger.Fields, field => Assert.False(string.IsNullOrWhiteSpace(field.Value)));
        Assert.Equal(before, ResultFactory.CanonicalJsonBytes(snapshot));
    }

    [Fact]
    public void ScopedValuesAndEqualDefaultEditsReachTypedRequestsAndSurviveInvalidEntries()
    {
        var snapshot = BaselineDesignTests.LoadOwnedSnapshot();
        var ids = snapshot.Members.Select(x => x.MemberId).ToArray();
        var binding = BeamReviewResolver.ModelBinding(snapshot);
        var edits = new[]
        {
            BeamReviewResolver.Edit("design.cover", BeamInputScope.Project, "", null, "40", 1),
            BeamReviewResolver.Edit("design.cover", BeamInputScope.Member, ids[0], binding, "30", 2),
            BeamReviewResolver.Edit("design.fck", BeamInputScope.Member, ids[0], binding, "30", 3),
            BeamReviewResolver.Edit("design.fy", BeamInputScope.Member, ids[0], binding, "415", 4),
            BeamReviewResolver.Edit("detailing.bars", BeamInputScope.Member, ids[0], binding, "16,20", 5),
            BeamReviewResolver.Edit("detailing.links", BeamInputScope.Member, ids[0], binding, "10", 6),
            BeamReviewResolver.Edit("detailing.stock", BeamInputScope.Member, ids[0], binding, "6000,12000", 7)
        };
        var first = BeamReviewResolver.Resolve(snapshot, ids, Preset(), edits: edits);
        Assert.Equal(30, first.Members[0].Inputs.MemberContexts[0].NominalCoverMm);
        Assert.Equal(40, first.Members[1].Inputs.MemberContexts[0].NominalCoverMm);
        Assert.Equal(BeamValueOrigin.Override, first.Ledger.Fields.Single(x => x.SubjectId == ids[0] && x.Key == "design.cover").Origin);
        Assert.Equal(30, first.Members[0].Inputs.Materials[0].ConcreteStrengthNPerMm2);
        Assert.Equal(415, first.Members[0].Inputs.Materials[0].SteelYieldStrengthNPerMm2);
        Assert.Equal([16d, 20], first.Members[0].Inputs.Catalogue.LongitudinalDiametersMm);
        Assert.Equal([10d], first.Members[0].Inputs.Catalogue.LinkDiametersMm);
        Assert.Equal([6000d, 12000], first.Members[0].Inputs.Catalogue.StockLengthsMm);
        foreach (var invalid in new[] { "", "=1+1", "NaN", "wrong" })
        {
            var saved = JsonSerializer.Deserialize<BeamInputLedger>(JsonSerializer.Serialize(first.Ledger))!;
            var changed = BeamReviewResolver.ApplyEdit(saved.Edits, BeamReviewResolver.Edit("design.cover", BeamInputScope.Member, ids[0], binding, invalid, 8));
            var restored = BeamReviewResolver.Resolve(snapshot, ids, Preset(), saved, changed);
            var field = restored.Ledger.Fields.Single(x => x.SubjectId == ids[0] && x.Key == "design.cover");
            Assert.Equal(invalid, field.EnteredText); Assert.Equal("30", field.Value); Assert.Equal(BeamValueOrigin.LastValid, field.Origin);
        }
    }

    [Fact]
    public void ConflictingScopesAreVisibleAndDifferentModelCannotInheritMemberEdits()
    {
        var snapshot = BaselineDesignTests.LoadOwnedSnapshot(); var id = snapshot.Members[0].MemberId;
        var edits = new[]
        {
            BeamReviewResolver.Edit("design.cover", BeamInputScope.Material, snapshot.Sections[0].MaterialId, BeamReviewResolver.ModelBinding(snapshot), "40", 1),
            BeamReviewResolver.Edit("design.cover", BeamInputScope.Story, snapshot.Members[0].StoryId, BeamReviewResolver.ModelBinding(snapshot), "50", 2),
            BeamReviewResolver.Edit("design.fck", BeamInputScope.Project, "", null, "30", 3)
        };
        var first = BeamReviewResolver.Resolve(snapshot, [id], Preset(), edits: edits);
        var conflict = first.Ledger.Fields.Single(x => x.Key == "design.cover");
        Assert.Equal(BeamValueOrigin.ConflictFallback, conflict.Origin); Assert.Equal(2, conflict.EditIds.Count); Assert.Equal("30", conflict.Value);
        var other = snapshot with { Metadata = snapshot.Metadata with { ModelName = "different model with reused object IDs" } };
        var next = BeamReviewResolver.Resolve(other, [id], Preset(), first.Ledger);
        Assert.Equal(BeamValueOrigin.Preset, next.Ledger.Fields.Single(x => x.Key == "design.cover").Origin);
        Assert.Equal(30, next.Members[0].Inputs.Materials[0].ConcreteStrengthNPerMm2);
    }

    [Fact]
    public void CoreContinuesWithRequiredFireAndMissingSlsWithoutQualifyingFullDesign()
    {
        var snapshot = BaselineDesignTests.LoadOwnedSnapshot(); var id = snapshot.Members[0].MemberId;
        var resolved = BeamReviewResolver.Resolve(snapshot, [id], Preset());
        var review = BeamReviewOperations.Review(snapshot, resolved, cancellationToken: TestContext.Current.CancellationToken);
        var member = Assert.Single(review.Members);
        Assert.Equal(BaselineRunState.Complete, member.Core!.State);
        Assert.Null(member.FullDesign); Assert.Null(member.Core.Design!.MemberResult);
        Assert.DoesNotContain(member.Core.Design.Checks, x => x.RuleId is "fire_scope" or "crack" or "deflection");
        Assert.Contains(member.Stages, x => x.StageId == "fire" && x.Status.Contains("60") && x.Availability == BeamReviewAvailability.Unavailable);
        Assert.Contains(member.Stages, x => x.StageId == "serviceability" && x.Availability == BeamReviewAvailability.Unavailable);
        Assert.True(review.WorkflowComplete);
        Assert.Equal(BaselineRunState.NeedsInput, BaselineDesignOperations.DesignMember(snapshot, resolved.Members[0].Inputs, id, cancellationToken: TestContext.Current.CancellationToken).State);
    }

    [Fact]
    public void RatesDoNotRerunStructuralWorkAndChangedCoverChangesActualArrangement()
    {
        var snapshot = BaselineDesignTests.LoadOwnedSnapshot(); var id = snapshot.Members[0].MemberId;
        var resolved = BeamReviewResolver.Resolve(snapshot, [id], Preset());
        var first = BeamReviewOperations.Review(snapshot, resolved, cancellationToken: TestContext.Current.CancellationToken);
        var rates = BeamReviewResolver.Resolve(snapshot, [id], Preset(), resolved.Ledger,
            [BeamReviewResolver.Edit("rates.steel", BeamInputScope.Project, "", null, "90", 1)]);
        Assert.Equal(resolved.Members[0].StructuralRevision, rates.Members[0].StructuralRevision);
        var second = BeamReviewOperations.Review(snapshot, rates, previous: first, cancellationToken: TestContext.Current.CancellationToken,
            coreEvaluator: (_, _, _) => throw new Exception("Rate-only edit reran structural calculations"));
        Assert.Same(first.Members[0].Core, second.Members[0].Core);
        var cover = BeamReviewResolver.Resolve(snapshot, [id], Preset(), resolved.Ledger,
            [BeamReviewResolver.Edit("design.cover", BeamInputScope.Project, "", null, "40", 2)]);
        var third = BeamReviewOperations.Review(snapshot, cover, previous: first, cancellationToken: TestContext.Current.CancellationToken);
        Assert.NotEqual(first.Members[0].Core!.Design!.Arrangement.BottomEffectiveDepthMm, third.Members[0].Core!.Design!.Arrangement.BottomEffectiveDepthMm);
    }

    [Fact]
    public void RateEditRepricesSameDeclaredExampleWithoutClaimingMemberQuantities()
    {
        var snapshot = BaselineDesignTests.LoadOwnedSnapshot(); var id = snapshot.Members[0].MemberId;
        var first = BeamReviewResolver.Resolve(snapshot, [id], Preset());
        var before = BeamReviewCostProjection.Project(first.Members[0], first.Ledger, null, null, true)!;
        var next = BeamReviewResolver.Resolve(snapshot, [id], Preset(), first.Ledger,
            [BeamReviewResolver.Edit("rates.steel", BeamInputScope.Project, "project", null, "90", 1)]);
        var after = BeamReviewCostProjection.Project(next.Members[0], next.Ledger, null, null, true)!;
        Assert.Equal(BeamReviewAvailability.Example, after.Availability);
        Assert.Equal(before.Result.Outputs!.QuantityResultId, after.Result.Outputs!.QuantityResultId);
        Assert.Equal("17700.00", before.Result.Outputs.TotalDecimal);
        Assert.Equal("19200.00", after.Result.Outputs.TotalDecimal);
        Assert.NotEqual(id, after.Quantities.MemberId);
        Assert.Null(BeamReviewCostProjection.Project(next.Members[0], next.Ledger, null, null, false));
    }

    [Fact]
    public void CompatibleMeasuredQuantitiesRepriceAndRejectAChangedStructuralBasis()
    {
        var snapshot = BaselineDesignTests.LoadOwnedSnapshot(); var id = snapshot.Members[0].MemberId;
        var first = BeamReviewResolver.Resolve(snapshot, [id], Preset());
        var scenario = first.Members[0];
        var core = BaselineDesignOperations.PreviewCore(snapshot, scenario, TestContext.Current.CancellationToken);
        var detail = core.Design!.Arrangement.RevisionId;
        // Retained measurement fixture: the quantity owner consumes a passing, identity-bound BBS.
        var bbs = new BbsOutput("review-fixture", scenario.StructuralRevision, id, detail,
            "owned-schedule-result", "shape-r1", "cut-r1", [], [], [], [],
            24000, 24000, 0, 0, 0, 59.18760559, 59.18760559, "heuristic_first_fit_decreasing", true);
        var quantity = QuantityOperations.Calculate(new(bbs.ProfileId, bbs.ProjectBasisId, id, detail,
            "owned-bbs-result", ResultFactory.SemanticId("output_payload_id", bbs), bbs,
            "beam-owns-net-prism-v1", "contact-face-v1",
            [new("C1", id, "M25", "VOL-1", 300 * 500, 6000, false)],
            [new("F1", id, FormworkFaceCategory.Soffit, "FACE-1", 300 * 6000, FormworkMeasurementState.Included)]));
        Assert.Equal(EngineeringState.Pass, quantity.Engineering);
        var evidence = new BeamReviewQuantityEvidence(scenario.StructuralRevision, quantity);
        var before = BeamReviewCostProjection.Project(scenario, first.Ledger, core, evidence, false)!;
        Assert.Equal(BeamReviewAvailability.Available, before.Availability);
        Assert.Equal(0.9, before.Quantities.ConcreteVolumeM3, 12);
        var rates = BeamReviewResolver.Resolve(snapshot, [id], Preset(), first.Ledger,
            [BeamReviewResolver.Edit("rates.steel", BeamInputScope.Project, "", null, "90", 1)]);
        var after = BeamReviewCostProjection.Project(rates.Members[0], rates.Ledger, core, evidence, false)!;
        Assert.Equal(quantity.ResultId, after.Result.Outputs!.QuantityResultId);
        Assert.NotEqual(before.Result.Outputs!.TotalDecimal, after.Result.Outputs.TotalDecimal);
        var changed = BeamReviewResolver.Resolve(snapshot, [id], Preset(), rates.Ledger,
            [BeamReviewResolver.Edit("design.cover", BeamInputScope.Project, "", null, "40", 2)]);
        Assert.Null(BeamReviewCostProjection.Project(changed.Members[0], changed.Ledger, core, evidence, false));
    }

    [Fact]
    public void UnsupportedAndNoFitMembersDoNotStopSupportedPeer()
    {
        var snapshot = BaselineDesignTests.LoadOwnedSnapshot(); var ids = snapshot.Members.Select(x => x.MemberId).ToArray();
        var binding = BeamReviewResolver.ModelBinding(snapshot);
        var resolved = BeamReviewResolver.Resolve(snapshot, ids, Preset(), edits:
        [BeamReviewResolver.Edit("member.support", BeamInputScope.Member, ids[1], binding, "Continuous", 1),
         BeamReviewResolver.Edit("detailing.stock", BeamInputScope.Member, ids[2], binding, "100", 2),
         BeamReviewResolver.Edit("detailing.bars", BeamInputScope.Member, ids[2], binding, "12", 3),
         BeamReviewResolver.Edit("detailing.links", BeamInputScope.Member, ids[2], binding, "8", 4),
         BeamReviewResolver.Edit("detailing.link_spacings", BeamInputScope.Member, ids[2], binding, "150", 5),
         BeamReviewResolver.Edit("detailing.bar_counts", BeamInputScope.Member, ids[2], binding, "2", 6),
         BeamReviewResolver.Edit("detailing.layers", BeamInputScope.Member, ids[2], binding, "1", 7)]);
        var result = BeamReviewOperations.Review(snapshot, resolved, cancellationToken: TestContext.Current.CancellationToken);
        Assert.Equal([BaselineRunState.Complete, BaselineRunState.Unsupported, BaselineRunState.NoFeasibleArrangement], result.Members.Select(x => x.Core!.State));
        Assert.All(result.Members, x => Assert.True(x.WorkflowComplete));
    }

    [Fact]
    public void FailureAndMissingSourceAccountForEveryMemberWithSeparateNamedExample()
    {
        var snapshot = BaselineDesignTests.LoadOwnedSnapshot(); var example = BeamReviewExamples.Owned(snapshot);
        Assert.Equal(ResultFactory.CanonicalJsonBytes(BaselineDesignTests.FixtureInputs(snapshot)), ResultFactory.CanonicalJsonBytes(example.Inputs));
        var resolved = BeamReviewResolver.Resolve(snapshot, snapshot.Members.Select(x => x.MemberId).ToArray(), Preset());
        var calls = 0;
        var review = BeamReviewOperations.Review(snapshot, resolved, example, cancellationToken: TestContext.Current.CancellationToken, coreEvaluator: (s, member, token) =>
            ++calls == 1 ? throw new InvalidOperationException("Injected member calculation failure") : BaselineDesignOperations.PreviewCore(s, member, token));
        Assert.Equal(3, review.Members.Count); Assert.Equal(3, calls);
        Assert.NotNull(review.Members[0].ExampleCore); Assert.Null(review.Members[0].Core);
        Assert.Equal(BaselineRunState.Complete, review.Members[1].Core!.State);
        Assert.All(review.Members, member => Assert.All(BeamReviewOperations.StageIds, stage => Assert.Contains(member.Stages, x => x.StageId == stage)));
        var missing = BeamReviewOperations.Review(null, resolved, example, cancellationToken: TestContext.Current.CancellationToken);
        Assert.All(missing.Members, x => { Assert.Null(x.Core); Assert.NotNull(x.ExampleCore); Assert.Contains("Unavailable", x.SourceStatus); });
        Assert.Contains("Not requested", missing.LiveAcquisitionStatus);
    }
}
