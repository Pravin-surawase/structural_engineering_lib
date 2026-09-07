namespace StructuralEngineering.Contracts;

// This is a construction-policy check for an explicitly selected no-splice, straight-bar envelope.
// Anchorage remains a separately qualified IS 456 detailing leaf.
public sealed record BaselineContinuityDemand(
    string ActionRowId,
    string StationId,
    double StationXMm,
    ReinforcementRole Role,
    double RequiredAreaMm2);

public sealed record RequiredConcurrentSourceRow(
    string ActionRowId,
    string StationId,
    double StationXMm);

public sealed record AllowedStockLength(string StockId, double LengthMm);

public sealed record BarStockPieceAssignment(string BarId, string StockPieceId, string StockId);

public sealed record BaselineContinuityRequest(
    string ProfileId,
    string MemberId,
    string PhysicalSpanId,
    string DemandRevisionId,
    string ReinforcementRevisionId,
    string CatalogueRevisionId,
    double PhysicalSpanStartXMm,
    double PhysicalSpanEndXMm,
    IReadOnlyList<LongitudinalBarPath> Bars,
    IReadOnlyList<RequiredConcurrentSourceRow> RequiredSourceRows,
    IReadOnlyList<ReinforcementRole> RequiredRoles,
    IReadOnlyList<BaselineContinuityDemand> Demands,
    IReadOnlyList<AllowedStockLength> AllowedStockLengths,
    IReadOnlyList<BarStockPieceAssignment> StockAssignments,
    QualifiedCheckReference? AnchorageCheck,
    string CodeDataRevisionId = "is456-amd6-wp11-v1");

public sealed record BaselineContinuityBarCheck(
    string BarId,
    ReinforcementRole Role,
    double StartXMm,
    double EndXMm,
    double DiameterMm,
    bool FullPhysicalSpan,
    bool Passed);

public sealed record BaselineContinuityCoverageCheck(
    string ActionRowId,
    string StationId,
    double StationXMm,
    ReinforcementRole Role,
    double RequiredAreaMm2,
    double ProvidedAreaMm2,
    IReadOnlyList<string> ProvidingBarIds,
    bool Passed);

public sealed record BaselineContinuityStockCheck(
    string BarId,
    string StockPieceId,
    string StockId,
    double StraightCutLengthMm,
    double? AllowedStockLengthMm,
    bool CatalogueContainsStock,
    bool FitsAssignedStock,
    bool Passed);

public sealed record BaselineContinuityCheckOutput(
    string MemberId,
    string PhysicalSpanId,
    string DemandRevisionId,
    string ReinforcementRevisionId,
    string CatalogueRevisionId,
    string AnchorageResultId,
    bool AnchorageQualified,
    IReadOnlyList<BaselineContinuityBarCheck> BarChecks,
    IReadOnlyList<BaselineContinuityCoverageCheck> CoverageChecks,
    IReadOnlyList<BaselineContinuityStockCheck> StockChecks,
    bool Passed);
