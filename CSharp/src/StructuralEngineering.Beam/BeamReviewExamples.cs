using StructuralEngineering.Contracts;

namespace StructuralEngineering.Beam;

public static class BeamReviewExamples
{
    public const string OwnedSnapshotSha256 = "9ced40204f6db621b4b22c7a8a755d1a77ec77c69aaf9a4d76dc12316a72bf84";
    public const string OwnedExampleId = "wp11-owned-nonbuilding-beam-example/v1";

    public static BeamReviewExample Owned(AnalysisSnapshot snapshot)
    {
        if (snapshot.SnapshotSha256 != OwnedSnapshotSha256 || snapshot.Members.Count != 3)
            throw new ArgumentException("The named example requires the exact retained WP11 snapshot.");
        var inputs = new BaselineProjectInputs(
            new("wp11-owned-reference", "fixture-engineering-v1", "owned_fixture_engineering_definition", "wp11-owned-baseline-fixture/v1", true, false),
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
            [new("selection-case:WP11_ULS", BaselineSelectionRole.Uls), new("selection-case:WP11_SLS", BaselineSelectionRole.SlsTotal),
             new("selection-case:WP11_SUSTAINED", BaselineSelectionRole.SlsSustained)]);
        return new(OwnedExampleId, snapshot, inputs, snapshot.Members[0].MemberId);
    }
}
