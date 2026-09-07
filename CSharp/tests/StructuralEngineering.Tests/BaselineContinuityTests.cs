using StructuralEngineering.Codes.IS456;
using StructuralEngineering.Contracts;
using Xunit;

namespace StructuralEngineering.Tests;

public class BaselineContinuityTests
{
    private static QualifiedCheckReference Anchorage() => new(
        "is456.beam.anchorage.check/v1", "anchorage:R1", ExecutionState.Completed,
        ApplicabilityState.Applicable, EngineeringState.Pass,
        CompletenessState.CompleteForScope, FreshnessState.Current);

    private static LongitudinalBarPath Bar(string id, ReinforcementRole role, double diameter = 20, double end = 6000) =>
        new(id, "M-" + id, role, diameter, 1, 100, role == ReinforcementRole.TopLongitudinal ? 60 : 440, 0, end, 360);

    private static BaselineContinuityRequest Request() => new(
        "IS456-WP11", "B-1", "SPAN-1", "demand:R1", "reinforcement:R1", "catalogue:R1", 0, 6000,
        [Bar("T1", ReinforcementRole.TopLongitudinal), Bar("T2", ReinforcementRole.TopLongitudinal), Bar("B1", ReinforcementRole.BottomLongitudinal), Bar("B2", ReinforcementRole.BottomLongitudinal)],
        [new("ULS-3000", "S-3000", 3000)],
        [ReinforcementRole.TopLongitudinal, ReinforcementRole.BottomLongitudinal],
        [new("ULS-3000", "S-3000", 3000, ReinforcementRole.TopLongitudinal, 300), new("ULS-3000", "S-3000", 3000, ReinforcementRole.BottomLongitudinal, 600)],
        [new("STOCK-6000", 6000)],
        [new("T1", "PIECE-T1", "STOCK-6000"), new("T2", "PIECE-T2", "STOCK-6000"), new("B1", "PIECE-B1", "STOCK-6000"), new("B2", "PIECE-B2", "STOCK-6000")],
        Anchorage());

    [Fact]
    public void CompleteStraightUnsplicedBarsQualifyDeterministically()
    {
        var first = BaselineContinuity.Check(Request());
        var second = BaselineContinuity.Check(Request());

        Assert.Equal(BaselineContinuity.CheckOperation, first.OperationSemanticId);
        Assert.Equal(EngineeringState.Pass, first.Engineering);
        Assert.Equal(CompletenessState.CompleteForScope, first.Completeness);
        Assert.True(first.Outputs!.Passed);
        Assert.All(first.Outputs.CoverageChecks, check => Assert.True(check.Passed));
        Assert.All(first.Outputs.StockChecks, check => Assert.True(check.Passed));
        Assert.Equal(first.ResultId, second.ResultId);
    }

    [Fact]
    public void InsufficientSteelInternalTerminationAndShortStockFailEngineering()
    {
        var result = BaselineContinuity.Check(Request() with
        {
            Bars = [Bar("T1", ReinforcementRole.TopLongitudinal, 12, 5500), Bar("T2", ReinforcementRole.TopLongitudinal, 12), Bar("B1", ReinforcementRole.BottomLongitudinal), Bar("B2", ReinforcementRole.BottomLongitudinal)],
            AllowedStockLengths = [new("STOCK-6000", 5000)]
        });

        Assert.Equal(EngineeringState.Fail, result.Engineering);
        Assert.False(result.Outputs!.Passed);
        Assert.Contains(result.Outputs.BarChecks, check => !check.FullPhysicalSpan);
        Assert.Contains(result.Outputs.CoverageChecks, check => !check.Passed);
        Assert.Contains(result.Outputs.StockChecks, check => !check.FitsAssignedStock);
    }

    [Fact]
    public void MissingRowRoleDemandOrStockBindingRemainsPartial()
    {
        var missingDemand = BaselineContinuity.Check(Request() with
        {
            Demands = [new("ULS-3000", "S-3000", 3000, ReinforcementRole.TopLongitudinal, 300)]
        });
        var missingStock = BaselineContinuity.Check(Request() with
        {
            StockAssignments = [new("T1", "PIECE-T1", "STOCK-6000")]
        });

        Assert.Equal(CompletenessState.Partial, missingDemand.Completeness);
        Assert.Equal("EVIDENCE.REQUIRED", missingDemand.Diagnostics[0].Code);
        Assert.Equal(CompletenessState.Partial, missingStock.Completeness);
    }

    [Fact]
    public void DuplicateSourceRowsAndStockPiecesAreRejected()
    {
        var duplicateRow = BaselineContinuity.Check(Request() with
        {
            RequiredSourceRows = [new("ULS-3000", "S-3000", 3000), new("ULS-3000", "S-4000", 4000)]
        });
        var duplicatePiece = BaselineContinuity.Check(Request() with
        {
            StockAssignments = [new("T1", "PIECE-1", "STOCK-6000"), new("T2", "PIECE-1", "STOCK-6000"), new("B1", "PIECE-B1", "STOCK-6000"), new("B2", "PIECE-B2", "STOCK-6000")]
        });

        Assert.Equal(ExecutionState.RejectedInput, duplicateRow.Execution);
        Assert.Equal("DEMAND.IDENTITY", duplicateRow.Diagnostics[0].Code);
        Assert.Equal(ExecutionState.RejectedInput, duplicatePiece.Execution);
        Assert.Equal("STOCK.ASSIGNMENT_INVALID", duplicatePiece.Diagnostics[0].Code);
    }
}
