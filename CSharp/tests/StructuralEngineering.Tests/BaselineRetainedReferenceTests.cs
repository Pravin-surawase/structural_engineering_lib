using System.Text.Json;
using System.Text.Json.Serialization;
using StructuralEngineering.Analysis;
using StructuralEngineering.Beam;
using StructuralEngineering.Contracts;
using Xunit;

namespace StructuralEngineering.Tests;

public class BaselineRetainedReferenceTests
{
    [Fact]
    public void RealBuildingAxialDemandIsUnsupportedBeforeSupplementalInputsAreRequested()
    {
        var path = Environment.GetEnvironmentVariable("WP11_BUILDING_SNAPSHOT");
        Assert.SkipWhen(string.IsNullOrWhiteSpace(path), "Requires the external retained proprietary building snapshot.");
        // WP10's older expanded JSON exceeds the text parser byte limit. Its
        // typed snapshot still goes through the full maintained identity/ledger
        // validator, exactly as a native caller with a normalized snapshot does.
        var options = new JsonSerializerOptions { PropertyNamingPolicy = JsonNamingPolicy.SnakeCaseLower };
        options.Converters.Add(new JsonStringEnumConverter(JsonNamingPolicy.SnakeCaseLower));
        var snapshot = JsonSerializer.Deserialize<AnalysisSnapshot>(File.ReadAllBytes(path!), options)!;
        Assert.NotNull(AnalysisSnapshotCodec.Validate(snapshot).Snapshot);
        Assert.Equal(153, snapshot.Members.Count);
        const string memberId = "member:82";
        var rows = snapshot.ActionRows.Where(row => row.MemberId == memberId).ToArray();
        Assert.NotEmpty(rows);
        Assert.True(rows.Max(row => Math.Abs(row.PKn)) > .02);
        var inputs = BaselineDesignTests.FixtureInputs(snapshot) with { Materials = [], MemberContexts = [] };
        var result = BaselineInputMapper.Map(snapshot, inputs, memberId);
        Assert.Equal(BaselineDesignState.Unsupported, result.State);
        Assert.Equal("ACTION.UNSUPPORTED_COMPONENT", result.Diagnostics[0].Code);
        Assert.Null(result.Beam);
        Assert.True(rows.Max(row => Math.Abs(row.PKn)) > .02);
    }
}
