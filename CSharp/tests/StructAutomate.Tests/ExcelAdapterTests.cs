using ExcelDna.Integration;
using StructuralEngineering.ExcelDna;
using Xunit;

namespace StructAutomate.Tests;

public class ExcelAdapterTests
{
    [Fact]
    public void RebarAreaReturnsNativeEnvelopeIdentityAndState()
    {
        Assert.Equal(Math.PI * 100d, Assert.IsType<double>(WorksheetFunctions.RebarArea(20d)), 12);
        var spill = Assert.IsType<object[,]>(WorksheetFunctions.RebarAreaResult(20d));
        var values = Rows(spill);

        Assert.Equal("structural.reinforcement.bar_area/v1", values["operation_semantic_id"]);
        Assert.Equal("completed", values["execution"]);
        Assert.Equal("applicable", values["applicability"]);
        Assert.StartsWith("result_id:pf4-canonical-json-v1:", values["result_id"]);
        Assert.Contains("reinforcement-bar-area-v1", values["provenance"]);
        var valueRow = Enumerable.Range(0, spill.GetLength(0))
            .Single(row => Equals(spill[row, 0], "outputs.value"));
        Assert.IsType<double>(spill[valueRow, 1]);
    }

    [Fact]
    public void StrictJsonRejectsUnknownMembersAndInvalidJson()
    {
        var unknown = Rows(WorksheetFunctions.RebarGeometry("{\"unknown\":true}"));
        var malformed = Rows(WorksheetFunctions.RebarGeometry("{not-json}"));

        Assert.Equal("rejected_input", unknown["execution"]);
        Assert.Equal("INPUT.JSON_INVALID", unknown["diagnostic_code"]);
        Assert.Equal("INPUT.JSON_INVALID", malformed["diagnostic_code"]);
    }

    [Fact]
    public void BlankLoadIsRejectedButExplicitZeroProducesZeroResponse()
    {
        var missing = Assert.IsType<object[,]>(LegacyFunctions.SimplySupportedUdl(6000d, ExcelEmpty.Value, 25000d, 3125000000d));
        Assert.Equal("Input error", missing[0, 0]);
        Assert.Contains("uniform_load_kn_per_m", Assert.IsType<string>(missing[0, 1]));

        var zero = Assert.IsType<object[,]>(LegacyFunctions.SimplySupportedUdl(6000d, 0d, 25000d, 3125000000d));
        Assert.Equal(0d, zero[2, 1]);
    }

    [Fact]
    public void RepeatedImmutableInputHasTheSameResultIdentity()
    {
        var first = Rows(WorksheetFunctions.RebarAreaResult(20d));
        var second = Rows(WorksheetFunctions.RebarAreaResult(20d));

        Assert.Equal(first["normalized_input_id"], second["normalized_input_id"]);
        Assert.Equal(first["calculation_id"], second["calculation_id"]);
        Assert.Equal(first["result_id"], second["result_id"]);
    }

    [Fact]
    public void CompatibilityFunctionsPreserveTheirPriorShapes()
    {
        var mass = LegacyFunctions.BarMass(20d, 6000d, 2d, 7850d);
        var geometry = Assert.IsType<object[,]>(LegacyFunctions.RebarGeometry(300d, 500d, 25d, 8d, 25d, "bottom",
            new object[,] { { 20d, 60d, 450d } }));

        Assert.IsType<double>(mass);
        Assert.Equal(6, geometry.GetLength(0));
        Assert.Equal(2, geometry.GetLength(1));
        Assert.Equal("Area (mm²)", geometry[0, 0]);
    }

    private static IReadOnlyDictionary<string, string> Rows(object result)
    {
        var spill = Assert.IsType<object[,]>(result);
        return Enumerable.Range(0, spill.GetLength(0)).ToDictionary(
            row => Assert.IsType<string>(spill[row, 0]),
            row => spill[row, 1].ToString() ?? string.Empty,
            StringComparer.Ordinal);
    }
}
