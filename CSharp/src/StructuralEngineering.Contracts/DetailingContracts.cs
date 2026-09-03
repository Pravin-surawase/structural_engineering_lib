namespace StructuralEngineering.Contracts;

public enum BarSurface { Plain, Deformed, FusionBondedEpoxyDeformed }
public enum StressState { Tension, Compression }
public enum AnchorageDirection { IncreasingX, DecreasingX }
public enum AnchorageLocation { SimpleSupport, ContinuousSupport, Discontinuity }
public enum SpliceKind { Lap, QualifiedCoupler }
public enum ReinforcementRole { TopLongitudinal, BottomLongitudinal, SideLeft, SideRight, Corner }
public enum BeamEnd { Left, Right }
public enum SeismicApplicability { OrdinaryIs456, Is13920_2016 }

public sealed record DevelopmentLengthRequest(
    string ProfileId, double BarDiameterMm, double BarStressNPerMm2,
    double SteelYieldStrengthNPerMm2, double ConcreteGradeNPerMm2,
    BarSurface BarSurface, StressState StressState, int BundleSize = 1,
    string CodeDataRevisionId = "is456-amd6-wp05-v1");

public sealed record DevelopmentLengthOutput(
    double PlainBarTensionBondStressNPerMm2, double SurfaceFactor,
    double StressStateFactor, double DesignBondStressNPerMm2,
    double UnbundledDevelopmentLengthMm, double BundleFactor,
    double RequiredDevelopmentLengthMm);

public sealed record AnchorageBend(string BendId, int AngleDegrees);
public sealed record SimpleSupportAnchorageEvidence(
    double MomentResistanceNmm, double SupportShearN, IReadOnlyList<string> ActionRowIds);
public sealed record AnchoragePath(
    string BarId, string CriticalSectionId, AnchorageLocation Location,
    AnchorageDirection Direction, double PathStartXMm, double PathEndXMm,
    double CriticalSectionXMm, string? SupportId, double? SupportNearFaceXMm,
    double? SupportCentreXMm, IReadOnlyList<AnchorageBend> Bends,
    string? BendScheduleReference, DevelopmentLengthRequest Development,
    SimpleSupportAnchorageEvidence? SimpleSupportEvidence = null);
public sealed record AnchorageCheckRequest(
    string ProfileId, string MemberId, string ReinforcementRevisionId,
    IReadOnlyList<AnchoragePath> Paths,
    string CodeDataRevisionId = "is456-amd6-wp05-v1");
public sealed record AnchorageBarCheck(
    string BarId, string CriticalSectionId, AnchorageLocation Location, string Criterion,
    string DevelopmentResultId, double RequiredDevelopmentLengthMm,
    double AvailableStraightLengthMm, double BendAnchorageValueMm,
    double MomentShearContributionMm, double AnchorageBeyondSupportCentreMm,
    double AvailableForCriterionMm, double DeficitMm, double? Utilization, bool Passed);
public sealed record AnchorageCheckOutput(
    string MemberId, string ReinforcementRevisionId,
    IReadOnlyList<AnchorageBarCheck> Checks, double? GoverningUtilization, bool Passed);

public sealed record QualifiedCheckReference(
    string OperationSemanticId, string ResultId, ExecutionState Execution,
    ApplicabilityState Applicability, EngineeringState Engineering,
    CompletenessState Completeness, FreshnessState Freshness)
{
    public bool Qualifies(string? expectedOperationSemanticId = null) =>
        !string.IsNullOrWhiteSpace(OperationSemanticId) &&
        !string.IsNullOrWhiteSpace(ResultId) &&
        (expectedOperationSemanticId is null || OperationSemanticId == expectedOperationSemanticId) &&
        Execution == ExecutionState.Completed && Applicability == ApplicabilityState.Applicable &&
        Engineering == EngineeringState.Pass && Completeness == CompletenessState.CompleteForScope &&
        Freshness == FreshnessState.Current;
}

public sealed record LongitudinalBarPath(
    string BarId, string BarMark, ReinforcementRole Role, double DiameterMm, int Layer,
    double XFromLeftMm, double YFromTopMm, double StartStationMm, double EndStationMm,
    double DesignStressNPerMm2, int BundleSize = 1);
public sealed record StationSteelDemand(
    string StationId, double StationXMm, ReinforcementRole Role, double RequiredAreaMm2,
    double ShearDemandN, double ShearCapacityN, string ActionRowId);
public sealed record StationZone(string ZoneId, double StartXMm, double EndXMm);
public sealed record SpliceDetail(
    string SpliceId, SpliceKind Kind, IReadOnlyList<string> BarIds,
    double StartXMm, double EndXMm, StressState StressState, bool DirectTension,
    double PercentageSplicedAtSection, string StaggerGroup,
    string? CouplerQualificationReference = null, string? InstallationReference = null);
public sealed record CurtailmentDetail(
    string CutoffId, string BarId, double TheoreticalCutoffXMm, double ActualEndXMm,
    AnchorageDirection Direction, string DemandStationId, double RequiredExtensionMm,
    IReadOnlyList<string> ContinuingBarIds, QualifiedCheckReference AnchorageCheck,
    QualifiedCheckReference ShearCutoffCheck, bool ExtraLinksRequired,
    QualifiedCheckReference? ExtraLinksCheck = null);
public sealed record LapCurtailmentCheckRequest(
    string ProfileId, string MemberId, string PhysicalSpanId, string DemandRevisionId,
    string ReinforcementRevisionId, double MemberStartXMm, double MemberEndXMm,
    double EffectiveDepthMm, double ConcreteGradeNPerMm2, double SteelYieldStrengthNPerMm2,
    BarSurface BarSurface, IReadOnlyList<LongitudinalBarPath> Bars,
    IReadOnlyList<StationSteelDemand> Demands, IReadOnlyList<SpliceDetail> Splices,
    IReadOnlyList<CurtailmentDetail> Curtailments,
    IReadOnlyList<StationZone>? ProhibitedSpliceZones = null,
    string CodeDataRevisionId = "is456-amd6-wp05-v1");
public sealed record SpliceCheck(
    string SpliceId, SpliceKind Kind, IReadOnlyList<string> BarIds, double MaximumBarDiameterMm,
    double ActualLengthMm, double? RequiredLengthMm, IReadOnlyList<string> DevelopmentResultIds,
    bool LapPermittedForDiameter, bool PercentageAllowed, string StaggerGroup,
    bool ZoneAllowed, bool QualificationAndInstallationEvidence, bool Passed);
public sealed record CurtailmentCheck(
    string CutoffId, string BarId, string DemandStationId, string ActionRowId,
    double ActualExtensionMm, double RequiredExtensionMm, bool ExtensionOk,
    IReadOnlyList<string> ContinuingBarIds, double ContinuingAreaMm2, double RequiredAreaMm2,
    bool RemainingSteelOk, string AnchorageResultId, bool AnchorageOk,
    string ShearCutoffResultId, bool ShearCutoffOk, bool ExtraLinksRequired,
    string? ExtraLinksResultId, bool ExtraLinksOk, bool Passed);
public sealed record LapCurtailmentCheckOutput(
    string MemberId, string PhysicalSpanId, string DemandRevisionId, string ReinforcementRevisionId,
    IReadOnlyList<SpliceCheck> SpliceChecks, IReadOnlyList<CurtailmentCheck> CurtailmentChecks,
    bool Passed);

public sealed record SeismicLinkZone(
    string ZoneId, double StartXMm, double EndXMm, double SpacingMm, double LinkDiameterMm,
    bool Closed, int HookAngleDegrees, double? FirstHoopOffsetFromJointFaceMm);
public sealed record SeismicAnchorageCheck(
    BeamEnd BeamEnd, ReinforcementRole Role, QualifiedCheckReference Check);
public sealed record DependentJointCheck(
    string JointId, QualifiedCheckReference Check);
public sealed record SeismicBeamContext(
    string SystemId, string SeismicDesignRevisionId, string MemberId, string PhysicalSpanId,
    string LeftJointId, string RightJointId, double LeftJointFaceXMm, double RightJointFaceXMm,
    double WidthMm, double OverallDepthMm, double EffectiveDepthMm,
    double ConcreteGradeNPerMm2, double SteelYieldStrengthNPerMm2,
    IReadOnlyList<LongitudinalBarPath> Bars, IReadOnlyList<SeismicLinkZone> LinkZones,
    IReadOnlyList<SpliceDetail> Splices, double ImportedAnalysisShearN, double GravityShearN,
    double LeftPositiveProbableMomentNmm, double LeftNegativeProbableMomentNmm,
    double RightPositiveProbableMomentNmm, double RightNegativeProbableMomentNmm,
    double ProvidedShearCapacityN, QualifiedCheckReference ShearCheck,
    IReadOnlyList<SeismicAnchorageCheck> AnchorageChecks,
    IReadOnlyList<DependentJointCheck> DependentJointChecks);
public sealed record SeismicDetailingCheckRequest(
    string ProfileId, SeismicApplicability Applicability, SeismicBeamContext? Context = null,
    string CodeDataRevisionId = "is13920-2016-amd2-wp05-v1");
public sealed record SeismicSteelFaceCheck(
    string Face, ReinforcementRole Role, IReadOnlyList<string> BarIds, double AreaMm2,
    double Ratio, double MinimumRatio, double MaximumRatio, bool Passed);
public sealed record SeismicRuleCheck(string RuleId, object Actual, object Limit, bool Passed);
public sealed record SeismicSpliceCheck(string SpliceId, bool OutsideEndZones,
    bool PercentageOk, bool QualificationAndInstallationEvidence, bool Passed);
public sealed record SeismicDetailingCheckOutput(
    string SystemId, string SeismicDesignRevisionId, string MemberId, string PhysicalSpanId,
    double MinimumLongitudinalRatio, double MaximumLongitudinalRatio,
    IReadOnlyList<SeismicSteelFaceCheck> SteelFaceChecks,
    IReadOnlyList<string> ContinuousTopBarIds, IReadOnlyList<string> ContinuousBottomBarIds,
    double RequiredEndZoneLengthMm, double MaximumEndLinkSpacingMm,
    IReadOnlyList<SeismicSpliceCheck> SpliceChecks, double CapacityShearPositiveN,
    double CapacityShearNegativeN, double GoverningShearN,
    IReadOnlyList<SeismicRuleCheck> RuleChecks, bool Passed);

public sealed record LinkCage(string LinkId, double DiameterMm, double LeftCentreXMm,
    double RightCentreXMm, double TopCentreYMm, double BottomCentreYMm,
    double InternalBendRadiusMm, bool Closed);
public sealed record CircularObstacle(string ObstacleId, double XFromLeftMm,
    double YFromTopMm, double DiameterMm, double RequiredClearanceMm);
public sealed record PlacementOpening(string OpeningId, double ClearWidthMm,
    double ClearHeightMm, string SequenceReference);
public sealed record ReinforcementArrangementCheckRequest(
    string ProfileId, string MemberId, string StationId, string ReinforcementRevisionId,
    double SectionWidthMm, double SectionDepthMm, double NominalCoverMm,
    double MaximumAggregateSizeMm, IReadOnlyList<LongitudinalBarPath> Bars,
    IReadOnlyList<LinkCage> Links, IReadOnlyList<ReinforcementRole> RequiredRoles,
    double VerticalAlignmentToleranceMm, IReadOnlyList<CircularObstacle>? Obstacles = null,
    PlacementOpening? PlacementOpening = null, bool RequirePlacementPlan = false,
    string CodeDataRevisionId = "is456-amd6-wp05-v1");
public sealed record LinkCageCheck(string LinkId, IReadOnlyDictionary<string, double> SurfaceCoversMm,
    double RequiredCoverMm, bool CoverOk, double CentrelineWidthMm, double CentrelineHeightMm,
    double MinimumBendExtentMm, bool BendFitOk, bool Closed, bool Passed);
public sealed record BarEnclosureCheck(string BarId, bool WithinSection,
    IReadOnlyList<string> EnclosingLinkIds, bool Passed);
public sealed record BarPairCheck(string FirstBarId, string SecondBarId,
    double CentreDistanceMm, double MinimumNonoverlapDistanceMm, bool Passed);
public sealed record HorizontalClearanceCheck(
    ReinforcementRole FirstRole,
    int FirstLayer,
    ReinforcementRole SecondRole,
    int SecondLayer,
    string FirstBarId,
    string SecondBarId,
    double ActualClearMm,
    double RequiredClearMm,
    bool Passed);
public sealed record VerticalClearanceCheck(
    string Kind,
    string? FirstBarId,
    string? SecondBarId,
    ReinforcementRole? Role,
    int? UpperLayer,
    int? LowerLayer,
    double ActualClearMm,
    double RequiredClearMm,
    double? AlignmentToleranceMm,
    bool Passed);
public sealed record RoleCentroid(ReinforcementRole Role, IReadOnlyList<string> BarIds, double AreaMm2,
    double CentroidXFromLeftMm, double CentroidYFromTopMm);
public sealed record ObstacleCheck(
    string ObstacleId,
    string ReinforcementKind,
    string? BarId,
    string? LinkId,
    int? SegmentIndex,
    double CentreDistanceMm,
    double RequiredDistanceMm,
    bool Passed);
public sealed record PlacementCheck(string OpeningId, string SequenceReference,
    double ClearWidthMm, double ClearHeightMm, double RequiredWidthMm,
    double RequiredHeightMm, bool Passed);
public sealed record ReinforcementArrangementCheckOutput(
    string MemberId, string StationId, string ReinforcementRevisionId,
    IReadOnlyList<LinkCageCheck> LinkChecks, IReadOnlyList<BarEnclosureCheck> BarEnclosureChecks,
    IReadOnlyList<BarPairCheck> PairCollisionChecks,
    IReadOnlyList<HorizontalClearanceCheck> HorizontalClearanceChecks,
    IReadOnlyList<VerticalClearanceCheck> VerticalClearanceChecks,
    IReadOnlyList<RoleCentroid> RoleCentroids,
    IReadOnlyList<ObstacleCheck> ObstacleChecks, PlacementCheck? PlacementCheck, bool Passed);
