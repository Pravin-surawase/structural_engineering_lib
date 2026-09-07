using StructuralEngineering.Analysis;
using StructuralEngineering.Beam;
using StructuralEngineering.Codes.IS456;
using StructuralEngineering.Contracts;
using StructuralEngineering.Core;
using Xunit;

namespace StructuralEngineering.Tests;

public class BaselineDesignTests
{
    [Fact]
    public void PackedEvidencePreservesCanonicalResultEnvelope()
    {
        var result = BaselineFlexure.RequiredSteel(new("reference", "beam", "row", Face.Bottom, 300, 450, 25, 500, 106.8534));
        Assert.Equal(ResultFactory.CanonicalJsonBytes(result), ResultFactory.CanonicalJsonBytes(BaselineEvidence.Pack(result)));
    }
    [Fact]
    public void RequiredSteelRecoversIndependentRectangularStressBlock()
    {
        // Independent equilibrium: Ast=600, T=261000 N, xu=96.6666667,
        // lever arm=409.4 mm, Mu=106.8534 kNm for b=300,d=450,M25,Fe500.
        var result = BaselineFlexure.RequiredSteel(new("reference", "beam", "row", Face.Bottom,
            300, 450, 25, 500, 106.8534));
        Assert.Equal(EngineeringState.Pass, result.Engineering);
        Assert.Equal(600, result.Outputs!.RequiredAreaMm2, 8);
        Assert.Equal(96.66666666666667, result.Outputs.NeutralAxisDepthMm, 8);
    }

    [Fact]
    public void CapturedOwnedEtabsBeamsProduceCompleteInspectableBaseline()
    {
        var snapshot = LoadOwnedSnapshot();
        Assert.Equal("9ced40204f6db621b4b22c7a8a755d1a77ec77c69aaf9a4d76dc12316a72bf84", snapshot.SnapshotSha256);
        var inputs = FixtureInputs(snapshot);
        var result = BaselineDesignOperations.Design(snapshot, inputs,
            snapshot.Members.Select(member => member.MemberId).ToArray(), new(1000), TestContext.Current.CancellationToken);
        var output = Environment.GetEnvironmentVariable("WP11_BASELINE_RESULT_PATH");
        if (!string.IsNullOrWhiteSpace(output))
        {
            using var stream = new FileStream(output, FileMode.CreateNew);
            stream.Write(ResultFactory.CanonicalJsonBytes(result));
        }
        Assert.Equal(3, result.Members.Count);
        foreach (var member in result.Members)
        {
            Assert.True(member.State == BaselineRunState.Complete,
                $"{member.MemberId}: {member.State}: {string.Join(';', member.Diagnostics.Select(d => d.Code))}; " +
                string.Join(';', member.Design?.Checks.Where(c => !BaselineEvidence.Qualified(c.Result))
                    .Select(c => c.RuleId + ":" + string.Join(',', c.Result.Diagnostics.Select(d => d.Code))) ?? []) + "; member:" +
                string.Join(',', member.Design?.MemberResult?.Diagnostics.Select(d => d.Code) ?? []));
            Assert.True(member.Design!.MemberResult!.Outputs!.Qualified);
            Assert.Equal(34, member.Design.Checks.Count(c => c.RuleId == "crack"));
            Assert.Equal(17, member.Design.Checks.Count(c => c.RuleId == "flexure"));
            Assert.All(member.Design.Checks, check => Assert.True(BaselineEvidence.Qualified(check.Result)));
        }
    }

    internal static AnalysisSnapshot LoadOwnedSnapshot()
    {
        var path = Environment.GetEnvironmentVariable("WP11_BASELINE_SNAPSHOT") ??
            Path.Combine(AppContext.BaseDirectory, "Fixtures", "wp11-owned-snapshot.sasnap");
        using var stream = File.OpenRead(path);
        var result = Path.GetExtension(path) == ".sasnap" ? AnalysisSnapshotTransport.Read(stream) :
            AnalysisSnapshotCodec.ParseAndValidate(File.ReadAllText(path));
        Assert.NotNull(result.Snapshot);
        return result.Snapshot;
    }

    [Fact]
    public void MixedBatchMatchesSerialAndReplayAndInvalidatesChangedEngineeringBasis()
    {
        var snapshot = LoadOwnedSnapshot();
        var inputs = FixtureInputs(snapshot);
        inputs = inputs with
        {
            Catalogue = inputs.Catalogue with { LongitudinalDiametersMm = [16], LinkDiametersMm = [8], LinkSpacingsMm = [150], BarCounts = [2], Layers = [1] },
            MemberContexts = [inputs.MemberContexts[0], inputs.MemberContexts[2] with { AnchorageStartXMm = -10, AnchorageEndXMm = 4510 }]
        };
        var ids = snapshot.Members.Select(member => member.MemberId).ToArray();
        var request = BaselineReplay.Request(snapshot, inputs, ids);
        var restored = BaselineReplay.Parse(BaselineReplay.Serialize(request));
        var batch = BaselineReplay.Run(restored, snapshot, TestContext.Current.CancellationToken);
        Assert.Equal([BaselineRunState.Complete, BaselineRunState.NeedsInput, BaselineRunState.NoFeasibleArrangement], batch.Members.Select(m => m.State));
        foreach (var member in batch.Members)
        {
            var serial = BaselineDesignOperations.DesignMember(snapshot, inputs, member.MemberId, cancellationToken: TestContext.Current.CancellationToken);
            Assert.Equal(ResultFactory.CanonicalJsonBytes(serial), ResultFactory.CanonicalJsonBytes(member));
        }
        var complete = batch.Members[0];
        Assert.Equal(FreshnessState.Current, BaselineDesignOperations.Freshness(complete, snapshot, inputs));
        var changed = inputs with { MemberContexts = [inputs.MemberContexts[0] with { NominalCoverMm = 40 }, inputs.MemberContexts[1]] };
        Assert.Equal(FreshnessState.Stale, BaselineDesignOperations.Freshness(complete, snapshot, changed));
        Assert.All(BaselineReplay.Run(restored, null, TestContext.Current.CancellationToken).Members,
            member => Assert.Equal(BaselineRunState.NeedsInput, member.State));
        Assert.All(BaselineReplay.Run(restored with { EngineRevisionId = "different-build" }, snapshot, TestContext.Current.CancellationToken).Members,
            member => Assert.Equal(BaselineRunState.Stale, member.State));
    }

    [Fact]
    public void SearchBudgetCancellationAndChangedLayerDepthHaveDistinctOutcomes()
    {
        var snapshot = LoadOwnedSnapshot();
        var inputs = FixtureInputs(snapshot);
        var memberId = snapshot.Members[0].MemberId;
        var limited = BaselineDesignOperations.DesignMember(snapshot, inputs, memberId, new(1), TestContext.Current.CancellationToken);
        Assert.Equal(BaselineRunState.Incomplete, limited.State);
        using var cancellation = CancellationTokenSource.CreateLinkedTokenSource(TestContext.Current.CancellationToken);
        cancellation.Cancel();
        Assert.Equal(BaselineRunState.Cancelled,
            BaselineDesignOperations.DesignMember(snapshot, inputs, memberId, cancellationToken: cancellation.Token).State);
        var layered = inputs with { Catalogue = inputs.Catalogue with { LongitudinalDiametersMm = [16], LinkDiametersMm = [8], LinkSpacingsMm = [150], BarCounts = [4], Layers = [2] } };
        var first = BaselineDesignOperations.DesignMember(snapshot, layered, memberId, cancellationToken: TestContext.Current.CancellationToken);
        Assert.Equal(BaselineRunState.Complete, first.State);
        var second = BaselineDesignOperations.DesignMember(snapshot, layered with { Catalogue = layered.Catalogue with { LinkDiametersMm = [10] } }, memberId, cancellationToken: TestContext.Current.CancellationToken);
        Assert.Equal(BaselineRunState.Complete, second.State);
        Assert.Equal(2, first.Design!.Arrangement.BottomLayers);
        // 35 cover + 3phi inset; second row clears the real diagonal hook tail.
        Assert.Equal(410.9583694396574, first.Design.Arrangement.BottomEffectiveDepthMm, 9);
        Assert.Equal(398.4479617995717, second.Design!.Arrangement.BottomEffectiveDepthMm, 9);
        Assert.NotEqual(first.Design.Arrangement.RevisionId, second.Design.Arrangement.RevisionId);
        Assert.Empty(first.Design.Checks.Where(c => c.Result.Applicability == ApplicabilityState.Applicable).Select(c => c.Result.ResultId)
            .Intersect(second.Design.Checks.Where(c => c.Result.Applicability == ApplicabilityState.Applicable).Select(c => c.Result.ResultId)));
    }

    internal static BaselineProjectInputs FixtureInputs(AnalysisSnapshot snapshot) => new(
        new("wp11-owned-reference", "fixture-engineering-v1", "owned_fixture_engineering_definition",
            "wp11-owned-baseline-fixture/v1", true, false),
        [new("material:PF9_CONCRETE", 25, 500, 415, 200000)],
        new("reference-catalogue-v1", [12, 16, 20], [8, 10], [250, 200, 150, 100], [2, 3, 4, 6], [1, 2], [6000, 12000], 1000),
        snapshot.Members.Select((member, index) =>
        {
            var length = 4000 + 250 * index;
            return new BaselineMemberContext(member.MemberId, member.ObjectId, "span:" + member.MemberId,
                BaselineSupportCondition.SimplySupported, 500, length - 500, 0, length, length,
                -465, length + 465, 35, 20, "Mild", false, true, true, true, true, "support-definition-v1",
                new(BaselineFireRequirement.NotRequired, "owned nonbuilding calculation fixture: no specified fire rating"),
                new([0, length], "owned fixture end restraints: global Y translation and X rotation fixed"));
        }).ToArray(),
        [new("selection-case:WP11_ULS", BaselineSelectionRole.Uls),
         new("selection-case:WP11_SLS", BaselineSelectionRole.SlsTotal),
         new("selection-case:WP11_SUSTAINED", BaselineSelectionRole.SlsSustained)]);
}
