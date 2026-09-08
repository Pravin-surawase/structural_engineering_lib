using StructuralEngineering.Analysis;
using StructuralEngineering.Beam;
using StructuralEngineering.Contracts;
using StructuralEngineering.ExcelDna;
using Xunit;

namespace StructAutomate.Tests;

public class Wp11DesignProjectionTests
{
    [Fact]
    public void SummaryAndDetailsAreBoundedTwelveColumnPresentations()
    {
        var snapshot = Snapshot(); var inputs = Wp11DesignStoreTestsInputs.Build(snapshot); var result = BaselineDesignOperations.Design(snapshot, inputs, snapshot.Members.Select(x => x.MemberId).ToArray(), new(1000), TestContext.Current.CancellationToken);
        var summary = BaselineDesignProjection.Summary(result, "Current"); var details = BaselineDesignProjection.Details(result.Members[0], snapshot, "Current", "external/result.json");
        Assert.Equal(12, summary.GetLength(1)); Assert.Equal(12, details.GetLength(1)); Assert.Equal("BASELINE BEAM DESIGNS", summary[0, 0]); Assert.Equal("BASELINE DESIGN DETAILS", details[0, 0]); Assert.True(details.GetLength(0) <= 500); Assert.DoesNotContain("p_kn", details.Cast<object>().Select(x => x?.ToString()));
    }
    private static AnalysisSnapshot Snapshot() { var d = new DirectoryInfo(AppContext.BaseDirectory); while (d is not null) { var p = Path.Combine(d.FullName, "CSharp", "tests", "StructuralEngineering.Tests", "Fixtures", "wp11-owned-snapshot.sasnap"); if (File.Exists(p)) { using var s = File.OpenRead(p); return Assert.IsType<AnalysisSnapshot>(AnalysisSnapshotTransport.Read(s).Snapshot); } d = d.Parent; } throw new FileNotFoundException(); }
}
internal static class Wp11DesignStoreTestsInputs { internal static BaselineProjectInputs Build(AnalysisSnapshot s) => new(new("p", "r", "o", "e", true, false), [new("material:PF9_CONCRETE", 25, 500, 415, 200000)], new("c", [12], [8], [150], [2], [1], [6000], 1000), s.Members.Select((m, i) => { var l = 4000 + 250 * i; return new BaselineMemberContext(m.MemberId, m.ObjectId, "span:" + m.MemberId, BaselineSupportCondition.SimplySupported, 500, l - 500, 0, l, l, -465, l + 465, 35, 20, "Mild", false, true, true, true, true, "e", new(BaselineFireRequirement.NotRequired, "e"), new([0, l], "e")); }).ToArray(), [new("selection-case:WP11_ULS", BaselineSelectionRole.Uls), new("selection-case:WP11_SLS", BaselineSelectionRole.SlsTotal), new("selection-case:WP11_SUSTAINED", BaselineSelectionRole.SlsSustained)]); }
