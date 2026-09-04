namespace StructuralEngineering.Contracts;

public enum ForceUnit { Newton, Kilonewton }
public enum MomentUnit { NewtonMillimetre, NewtonMetre, KilonewtonMillimetre, KilonewtonMetre }
public enum ActionConcurrency { StaticConcurrent, StagedStep, ResponseResult, ComponentEnvelope, DesignEnvelope }
public enum StationUnit { Millimetre, Metre }

/// <summary>Identity carried with an action row; actions are never envelope-mixed by this contract.</summary>
public sealed record AnalysisActionIdentity(
    string SourceIdentity, string ModelIdentity, string CaseIdentity, string StepIdentity,
    string MemberIdentity, string SpanIdentity, string ObjectIdentity, string ElementIdentity,
    string StationIdentity, string ConcurrencyIdentity);

public sealed record LocalAxes(double Xx, double Xy, double Xz, double Yx, double Yy, double Yz, double Zx, double Zy, double Zz);

/// <summary>Local member actions. P, V2, V3 are forces; T, M2, M3 are moments.</summary>
public sealed record AnalysisActionRow(
    AnalysisActionIdentity Identity, ActionBasis ActionBasis, LocalAxes Axes,
    double P, double V2, double V3, double T, double M2, double M3,
    ForceUnit ForceUnit = ForceUnit.Kilonewton, MomentUnit MomentUnit = MomentUnit.KilonewtonMetre);

public sealed record NormalizedActionRow(
    AnalysisActionIdentity Identity, ActionBasis ActionBasis, LocalAxes Axes,
    double PNewton, double V2Newton, double V3Newton, double TNewtonMm, double M2NewtonMm, double M3NewtonMm);

public sealed record SupportFace(string SupportId, double CentrelineStationMm, double ClearFaceStationMm);
public sealed record PhysicalSpan(string SpanId, string StartSupportId, string EndSupportId, double CentrelineLengthMm, double ClearLengthMm, double DesignLengthMm);
public sealed record SectionRegion(string RegionId, string PhysicalSpanId, double StartStationMm, double EndStationMm, double ElasticModulusNPerMm2, double MajorAxisInertiaMm4);
public sealed record AnalysisElementMapping(string ElementId, string PhysicalSpanId, string SectionRegionId, double StartStationMm, double EndStationMm);
public sealed record BeamTopologyRequest(IReadOnlyList<SupportFace> SupportFaces, IReadOnlyList<SectionRegion> SectionRegions, double DesignEffectiveDepthMm = 0);
public sealed record BeamTopology(IReadOnlyList<PhysicalSpan> PhysicalSpans, IReadOnlyList<AnalysisElementMapping> Elements, IReadOnlyList<SupportFace> SupportFaces, IReadOnlyList<SectionRegion> SectionRegions);

public sealed record PlanarNode(string NodeId, double StationMm, bool RestrainV2 = false, bool RestrainRotationM3 = false, double PrescribedV2DisplacementMm = 0, double PrescribedRotationRad = 0);
public sealed record UniformLoad(string ElementId, double V2NPerMm);
public sealed record NodalLoad(string NodeId, double V2N = 0, double M3Nmm = 0);
public sealed record PointLoad(string ElementId, string LoadId, double DistanceFromElementStartMm, double V2N);
public sealed record PlanarBeamSolveRequest(BeamTopology Topology, IReadOnlyList<PlanarNode> Nodes, IReadOnlyList<UniformLoad> UniformLoads, IReadOnlyList<NodalLoad> NodalLoads, IReadOnlyList<PointLoad> PointLoads);
public sealed record PlanarBeamReaction(string NodeId, double V2N, double M3Nmm);
public sealed record PlanarBeamStationResult(string NodeId, string PhysicalSpanId, string ElementId, double StationMm, double V2DisplacementMm, double RotationRad, double V2N, double M3Nmm);
public sealed record PlanarBeamSolveResult(IReadOnlyList<PlanarBeamReaction> Reactions, IReadOnlyList<PlanarBeamStationResult> Stations, double GlobalForceResidualN, double GlobalMomentResidualNmm, double MaxFreeForceResidualN, double MaxFreeMomentResidualNmm);

// WP03 snapshot and beam-line contracts mirror the vendor-neutral Python boundary.
public sealed record Vector3(double X, double Y, double Z);
public sealed record SnapshotLocalAxes(string AxisId, Vector3 E1, Vector3 E2, Vector3 E3);
public sealed record RawActionRow(string SourceRowId, string MemberId, string PhysicalSpanId, string ObjectId, string AnalysisElementId, string AxisId, double ObjectStation, double ElementStation, string LoadCaseId, string StepType, double? StepNumber, ActionConcurrency Concurrency, double P, double V2, double V3, double T, double M2, double M3);
public sealed record RawActionSnapshot(string SourceId, string ModelId, string AnalysisEpochId, string ResultEpochId, ForceUnit ForceUnit, MomentUnit MomentUnit, StationUnit StationUnit, IReadOnlyList<SnapshotLocalAxes> LocalAxes, IReadOnlyList<RawActionRow> Rows);
public sealed record ActionSnapshotOutput(string SnapshotId, string UnitBasis, IReadOnlyList<SnapshotLocalAxes> LocalAxes, IReadOnlyList<NormalizedSnapshotActionRow> Rows);
public sealed record NormalizedSnapshotActionRow(string RowId, string SourceRowId, string SourceId, string ModelId, string AnalysisEpochId, string ResultEpochId, string MemberId, string PhysicalSpanId, string ObjectId, string AnalysisElementId, string AxisId, double ObjectStationMm, double ElementStationMm, string LoadCaseId, string StepType, double? StepNumber, ActionConcurrency Concurrency, double PNewton, double V2Newton, double V3Newton, double TNewtonMm, double M2NewtonMm, double M3NewtonMm);
public sealed record PhysicalSupport(string SupportId, double CentreMm, double LeftFaceMm, double RightFaceMm);
public sealed record TopologySectionRegion(string RegionId, string SectionId, double StartMm, double EndMm);
public sealed record TopologySpan(string SpanId, string StartSupportId, string EndSupportId, double EffectiveDepthMm, IReadOnlyList<TopologySectionRegion> SectionRegions);
public sealed record TopologyElementMapping(string AnalysisElementId, string PhysicalSpanId, double StartMm, double EndMm);
public sealed record BeamTopologyDefinitionRequest(string MemberId, SnapshotLocalAxes LocalAxes, IReadOnlyList<PhysicalSupport> Supports, IReadOnlyList<TopologySpan> Spans, IReadOnlyList<TopologyElementMapping> AnalysisElements);
public sealed record DefinedPhysicalSpan(string SpanId, string StartSupportId, string EndSupportId, double StartSupportRightFaceMm, double EndSupportLeftFaceMm, double CentrelineSpanMm, double ClearSpanMm, double EffectiveSpanMm, IReadOnlyList<TopologySectionRegion> SectionRegions, IReadOnlyList<TopologyElementMapping> AnalysisElements);
public sealed record BeamTopologyDefinitionOutput(string TopologyId, string MemberId, SnapshotLocalAxes LocalAxes, IReadOnlyList<PhysicalSupport> Supports, IReadOnlyList<DefinedPhysicalSpan> Spans);
public sealed record BeamLineNode(string NodeId, double XMm, bool VerticalRestraint, bool RotationRestraint, double VerticalDisplacementMm = 0, double PrescribedRotationRad = 0, double NodalForceN = 0, double NodalMomentNmm = 0);
public sealed record BeamLineElement(string AnalysisElementId, string PhysicalSpanId, string StartNodeId, string EndNodeId, double ElasticModulusNPerMm2, double SecondMomentMm4, double UniformLoadNPerMm = 0);
public sealed record BeamLinePointLoad(string AnalysisElementId, double DistanceFromStartMm, double VerticalForceN);
public sealed record BeamLineRequest(string ModelId, string LoadCaseId, IReadOnlyList<BeamLineNode> Nodes, IReadOnlyList<BeamLineElement> Elements, IReadOnlyList<BeamLinePointLoad>? PointLoads = null, int StationIntervals = 20, string SolverIdentity = "euler_bernoulli_direct_stiffness_v1", string UnitBasis = "mm_n_nmm_rad");
public sealed record BeamLineStation(string PhysicalSpanId, string AnalysisElementId, double DistanceFromStartMm, double XMm, string Side, double VerticalDisplacementMm, double RotationRad, double V2N, double M3Nmm);
public sealed record BeamLineOutput(string SolverIdentity, string AnalysisProfile, string UnitBasis, double VerticalForceResidualN, double MomentResidualNmm, double MaxFreeForceResidualN, double MaxFreeMomentResidualNmm, IReadOnlyList<PlanarBeamReaction> Reactions, IReadOnlyList<BeamLineStation> Stations);
