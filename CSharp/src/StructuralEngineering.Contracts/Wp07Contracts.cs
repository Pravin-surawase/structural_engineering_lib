namespace StructuralEngineering.Contracts;

public enum FormworkFaceCategory
{
    Soffit,
    SideLeft,
    SideRight,
    EndBulkhead,
    SlabInterface,
    SupportInterface,
    OtherDeclared
}

public enum FormworkMeasurementState { Included, Excluded }
public enum CostCategory { Material, Formwork, Coupler, Labour, Plant }

public enum CostBasis
{
    SteelScheduledMassKg,
    SteelStockMassKg,
    ConcreteVolumeM3,
    FormworkAreaM2,
    CouplerCount
}

public enum WastePricingBasis { ScheduledSteel, PurchasedStock }
public enum HumanActionKind { Prepared, Checked, Approved, Rejected }
public enum BbsSpliceKind { Lap, Coupler }

public sealed record ShapeConvention(
    string ConventionId,
    string RevisionId,
    string LengthBasis = "resolved_centreline_v1");

public sealed record CuttingStockPolicy(
    string PolicyId,
    string RevisionId,
    IReadOnlyList<double> StockLengthsMm,
    double KerfMm,
    double ReusableOffcutMinMm,
    string AllocationMethod = "first_fit_decreasing_v1");

public sealed record SpliceRecord(
    string SpliceId,
    BbsSpliceKind Kind,
    double StationXMm,
    string QualificationReference,
    int CouplerCount = 0);

public sealed record LinkPlacementZone(
    string ZoneId,
    string BarMark,
    double StartStationXMm,
    double EndStationXMm,
    double SpacingMm,
    bool IncludeStart,
    bool IncludeEnd);

public sealed record BbsRequest(
    string ProfileId,
    string ProjectBasisId,
    string MemberId,
    string DetailRevisionId,
    string ScheduleResultId,
    string ScheduleOutputPayloadId,
    BarPathOutput Schedule,
    ShapeConvention ShapeConvention,
    CuttingStockPolicy StockPolicy,
    double SteelDensityKgPerM3,
    IReadOnlyList<SpliceRecord>? SpliceRecords = null,
    IReadOnlyList<LinkPlacementZone>? LinkZones = null,
    double StationToleranceMm = 1e-6);

public sealed record ShapeDimension(
    string DimensionId,
    string SegmentKind,
    double CentrelineLengthMm,
    double? BendRadiusMm,
    double? BendAngleDegrees);

public sealed record BbsRow(
    string BarMark,
    BarPathRole Role,
    double DiameterMm,
    double SteelGradeNPerMm2,
    int BundleSize,
    int PlacementCount,
    int ScheduledBarCount,
    string ShapeCode,
    IReadOnlyList<ShapeDimension> Dimensions,
    double CentrelineDevelopedLengthEachMm,
    double FabricationCutLengthEachMm,
    double ScheduledCutLengthMm,
    double TheoreticalMassKg,
    IReadOnlyList<string> SourcePathIds,
    IReadOnlyList<string> SpliceIds);

public sealed record PlacedLinkZone(
    string ZoneId,
    string BarMark,
    IReadOnlyList<double> StationsXMm,
    int Count);

public sealed record StockCut(
    string CutId,
    string BarMark,
    double LengthMm);

public sealed record StockPiece(
    string StockPieceId,
    double DiameterMm,
    double SteelGradeNPerMm2,
    double StockLengthMm,
    IReadOnlyList<StockCut> Cuts,
    double KerfLengthMm,
    double ReusableOffcutLengthMm,
    double WasteLengthMm);

public sealed record CouplerItem(
    string SpliceId,
    double StationXMm,
    int Count,
    string QualificationReference);

public sealed record BbsOutput(
    string ProfileId,
    string ProjectBasisId,
    string MemberId,
    string DetailRevisionId,
    string ScheduleResultId,
    string ShapeConventionRevisionId,
    string CuttingPolicyRevisionId,
    IReadOnlyList<BbsRow> Rows,
    IReadOnlyList<PlacedLinkZone> LinkZones,
    IReadOnlyList<StockPiece> StockPieces,
    IReadOnlyList<CouplerItem> Couplers,
    double ScheduledCutLengthMm,
    double StockLengthMm,
    double KerfLengthMm,
    double ReusableOffcutLengthMm,
    double WasteLengthMm,
    double ScheduledSteelMassKg,
    double PurchasedStockMassKg,
    string AllocationOptimality,
    bool Passed);

public sealed record VolumeDeduction(
    string DeductionId,
    double VolumeM3,
    string OwnershipId,
    string Reason);

public sealed record AreaDeduction(
    string DeductionId,
    double AreaMm2,
    string OwnershipId,
    string Reason);

public sealed record ConcreteNetSegment(
    string SegmentId,
    string MemberId,
    string MaterialId,
    string OwnershipId,
    double CrossSectionAreaMm2,
    double PhysicalLengthMm,
    bool OwnsMonolithicInterface,
    IReadOnlyList<VolumeDeduction>? Deductions = null);

public sealed record FormworkContactFace(
    string FaceId,
    string MemberId,
    FormworkFaceCategory Category,
    string OwnershipId,
    double GrossAreaMm2,
    FormworkMeasurementState MeasurementState,
    string? ExclusionReason = null,
    IReadOnlyList<AreaDeduction>? Deductions = null);

public sealed record ConstructionQuantityRequest(
    string ProfileId,
    string ProjectBasisId,
    string MemberId,
    string DetailRevisionId,
    string BbsResultId,
    string BbsOutputPayloadId,
    BbsOutput Bbs,
    string ConcreteOverlapPolicyId,
    string FormworkMeasurementPolicyId,
    IReadOnlyList<ConcreteNetSegment> ConcreteSegments,
    IReadOnlyList<FormworkContactFace> FormworkFaces);

public sealed record QuantitySteelItem(
    string BarMark,
    double DiameterMm,
    double SteelGradeNPerMm2,
    int ScheduledBarCount,
    double ScheduledCutLengthMm,
    double ScheduledMassKg);

public sealed record ConcreteQuantity(
    string SegmentId,
    string MaterialId,
    string OwnershipId,
    double GrossVolumeM3,
    double DeductionVolumeM3,
    double NetVolumeM3,
    bool OwnsMonolithicInterface);

public sealed record FormworkQuantity(
    string FaceId,
    FormworkFaceCategory Category,
    string OwnershipId,
    FormworkMeasurementState MeasurementState,
    double GrossAreaM2,
    double DeductionAreaM2,
    double NetAreaM2,
    string? ExclusionReason);

public sealed record WasteLedger(
    double KerfLengthMm,
    double ReusableOffcutLengthMm,
    double UnreusableWasteLengthMm);

public sealed record ConstructionQuantityOutput(
    string ProfileId,
    string ProjectBasisId,
    string MemberId,
    string DetailRevisionId,
    string BbsResultId,
    string ConcreteOverlapPolicyId,
    string FormworkMeasurementPolicyId,
    IReadOnlyList<QuantitySteelItem> SteelItems,
    IReadOnlyList<ConcreteQuantity> ConcreteItems,
    IReadOnlyList<FormworkQuantity> FormworkItems,
    WasteLedger Waste,
    double SteelScheduledMassKg,
    double SteelStockMassKg,
    double ConcreteVolumeM3,
    double FormworkAreaM2,
    int CouplerCount,
    decimal? DirectCost = null);

public sealed record CostRate(
    string RateId,
    CostCategory Category,
    CostBasis Basis,
    string Description,
    string UnitRateDecimal,
    string SourceReference);

public sealed record HumanCostScope(
    IReadOnlyList<CostCategory> IncludedCategories,
    IReadOnlyList<CostCategory> ExcludedCategories);

public sealed record MeasuredRateProfile(
    string ProfileId,
    string RevisionId,
    string Currency,
    string ValuationDate,
    string TimeZone,
    string Geography,
    string Source,
    HumanCostScope Scope,
    IReadOnlyList<CostRate> Rates,
    WastePricingBasis WastePricingBasis,
    string OverheadPercentDecimal,
    string TaxPercentDecimal);

public sealed record ConstructionCostRequest(
    string ProfileId,
    string ProjectBasisId,
    string MemberId,
    string DetailRevisionId,
    string QuantityResultId,
    string QuantityOutputPayloadId,
    ConstructionQuantityOutput Quantities,
    MeasuredRateProfile RateProfile);

public sealed record CostLine(
    string RateId,
    CostCategory Category,
    CostBasis Basis,
    string Description,
    string SourceQuantityResultId,
    string QuantityDecimal,
    string Unit,
    string UnitRateDecimal,
    string AmountDecimal);

public sealed record ConstructionCostOutput(
    string ProfileId,
    string ProjectBasisId,
    string MemberId,
    string DetailRevisionId,
    string QuantityResultId,
    string RateProfileId,
    string RateProfileRevisionId,
    string Currency,
    string ValuationDate,
    string Geography,
    string Source,
    IReadOnlyList<CostLine> Lines,
    IReadOnlyList<CostCategory> IncludedCategories,
    IReadOnlyList<CostCategory> ExcludedCategories,
    string DirectSubtotalDecimal,
    string OverheadDecimal,
    string PreTaxTotalDecimal,
    string TaxDecimal,
    string TotalDecimal);

public sealed record ResultBinding(
    string OperationSemanticId,
    string ResultId,
    string NormalizedInputId,
    string CalculationId,
    ExecutionState Execution,
    ApplicabilityState Applicability,
    EngineeringState Engineering,
    CompletenessState Completeness,
    FreshnessState Freshness,
    string OutputPayloadId);

public sealed record CalculationPackageMetadata(
    string ProjectId,
    string ProjectName,
    string ProjectRevisionId,
    string MemberId,
    string PackageRevisionId,
    string EngineBuild,
    IReadOnlyList<string> DatasetRevisionIds,
    string IssuedAtUtc);

public sealed record CalculationPackageProfile(
    string ProfileId,
    string RevisionId,
    string TemplateId,
    IReadOnlyList<string> RequiredLeafIds,
    IReadOnlyList<string> RequiredSectionIds);

public sealed record CalculationTrace(
    string TraceId,
    string LeafId,
    string RuleReference,
    string FormulaReference,
    string NormalizedSubstitution,
    double? RequiredValue,
    double? ProvidedValue,
    double? SelectedValue,
    string? Unit,
    double? Utilization,
    bool Governing);

public sealed record DrawingDatum(
    string DatumId,
    string SourceIdentity,
    string Label,
    string Value,
    string? Unit = null);

public sealed record DrawingView(
    string ViewId,
    string Kind,
    string DetailRevisionId,
    IReadOnlyList<DrawingDatum> Data);

public sealed record HumanAction(
    string ActionId,
    string ActorId,
    string ActorDisplayName,
    string ProfessionalRole,
    HumanActionKind Action,
    string RecordedAtUtc,
    string ScopeId,
    string BoundResultId);

public sealed record PackageLeaf(
    string LeafId,
    string OperationSemanticId,
    string? ResultId,
    double? RequiredValue,
    double? ProvidedValue,
    double? SelectedValue,
    string? Unit,
    double? Utilization,
    bool Governing,
    bool Qualified,
    IReadOnlyList<string> ReasonCodes);

public sealed record RenderSection(
    string SectionId,
    IReadOnlyList<string> SourceIdentities,
    string SemanticPayloadKind);

public sealed record CalculationPackageRequest(
    CalculationPackageMetadata Metadata,
    CalculationPackageProfile PackageProfile,
    MemberDesignOutput MemberResult,
    ResultBinding MemberBinding,
    BarPathOutput Schedule,
    ResultBinding ScheduleBinding,
    BbsOutput Bbs,
    ResultBinding BbsBinding,
    ConstructionQuantityOutput Quantities,
    ResultBinding QuantityBinding,
    ConstructionCostOutput? Cost,
    ResultBinding? CostBinding,
    IReadOnlyList<string> Assumptions,
    IReadOnlyList<CalculationTrace> Traces,
    IReadOnlyList<DrawingView> Drawings,
    IReadOnlyList<string> Limitations,
    IReadOnlyList<HumanAction>? HumanActions = null);

public sealed record CalculationPackageOutput(
    string CalculationPackageId,
    CalculationPackageMetadata Metadata,
    string PackageProfileId,
    string PackageProfileRevisionId,
    IReadOnlyList<ResultBinding> DependencyBindings,
    IReadOnlyList<string> Assumptions,
    IReadOnlyList<PackageLeaf> Leaves,
    IReadOnlyList<CalculationTrace> Traces,
    string? GoverningLeafId,
    BarPathOutput ReinforcementSchedule,
    BbsOutput Bbs,
    ConstructionQuantityOutput Quantities,
    ConstructionCostOutput? Cost,
    IReadOnlyList<DrawingView> Drawings,
    IReadOnlyList<RenderSection> RenderSections,
    string RendererInterfaceRevision,
    IReadOnlyList<string> Limitations,
    IReadOnlyList<HumanAction> HumanActions,
    string IssueState,
    bool ActiveApproval);
