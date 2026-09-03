using ExcelDna.Integration;
using StructAutomate.Excel;
using Xunit;

namespace StructAutomate.Tests;

public class ExcelAdapterTests
{
    [Fact]
    public void BlankLoadIsRejectedButExplicitZeroProducesZeroResponse()
    {
        var missing = Assert.IsType<object[,]>(Functions.SimplySupportedUdl(6000d,ExcelEmpty.Value,25000d,3125000000d));
        Assert.Equal("Input error",missing[0,0]);
        Assert.Contains("uniformLoadKnPerM",Assert.IsType<string>(missing[0,1]));
        var zero = Assert.IsType<object[,]>(Functions.SimplySupportedUdl(6000d,0d,25000d,3125000000d));
        Assert.Equal(0d,zero[2,1]);
    }

    [Fact]
    public void BlankCoverIsNotConvertedToZeroAndFractionalBarCountFails()
    {
        var missing = Assert.IsType<object[,]>(Functions.RebarGeometry(300d,500d,ExcelEmpty.Value,8d,25d,"bottom",new object[,] {{20d,60d,450d}}));
        Assert.Equal("Input error",missing[0,0]);
        var fractional = Assert.IsType<object[,]>(Functions.BarMass(20d,6000d,1.5d,7850d));
        Assert.Equal("Input error",fractional[0,0]);
    }
}
