using StructuralEngineering.Contracts;
using StructuralEngineering.Core;
namespace StructuralEngineering.Beam;

public static class BaselineInputMapper
{
    public static BaselineMappingResult Map(AnalysisSnapshot snapshot, BaselineProjectInputs inputs, string memberId)
       => Map(new BaselineSnapshotIndex(snapshot), inputs, memberId);
    internal static BaselineMappingResult Map(BaselineSnapshotIndex index, BaselineProjectInputs inputs, string memberId)
    {
        var snapshot = index.Snapshot;
        if (!index.Valid) return Result(null, BaselineDesignState.NeedsInput, "SNAPSHOT.INVALID", "Snapshot failed the maintained validation authority.", "snapshot");
        if (string.IsNullOrWhiteSpace(memberId)) return Result(null, BaselineDesignState.NeedsInput, "MEMBER.MISSING", "A source member ID is required.", "member_id");
        if (snapshot.Freshness.State != FreshnessState.Current) return Result(null, BaselineDesignState.Stale, "SNAPSHOT.STALE", "Snapshot is not current for its recorded offline basis.", "snapshot.freshness");
        if (index.Actions[memberId].Any(x => Math.Abs(x.PKn) > 1e-12 || Math.Abs(x.V3Kn) > 1e-12 || Math.Abs(x.M2Knm) > 1e-12 || Math.Abs(x.TKnm) > 1e-12))
            return Result(null, BaselineDesignState.Unsupported, "ACTION.UNSUPPORTED_COMPONENT", "Captured axial, minor-axis or torsional actions exceed the declared 1e-12 numerical-zero tolerance. This is known before supplemental project inputs are requested.", "action_rows");
        if (inputs?.Project is null || !Text(inputs.Project.ProjectId, inputs.Project.RevisionId, inputs.Project.Origin, inputs.Project.EvidenceReference) ||
           inputs.Materials is null || inputs.MemberContexts is null || inputs.SelectionRoles is null ||
           !Unique(inputs.Materials.Select(x => x?.MaterialId)) || !Unique(inputs.MemberContexts.Select(x => x?.MemberId)) || !Unique(inputs.SelectionRoles.Select(x => x?.SelectionId)))
            return Result(null, BaselineDesignState.NeedsInput, "INPUT.IDENTITY", "Accepted input bindings require complete, unique identities and provenance.", "project,materials,member_contexts,selection_roles");
        var catalogue = inputs.Catalogue;
        if (catalogue is null || !Text(catalogue.RevisionId) || catalogue.MaximumCandidates is < 1 or > 10000 ||
           !Numbers(catalogue.LongitudinalDiametersMm) || !Numbers(catalogue.LinkDiametersMm) || !Numbers(catalogue.LinkSpacingsMm) || !Numbers(catalogue.StockLengthsMm) ||
           catalogue.BarCounts is not { Count: > 0 and <= 16 } || catalogue.BarCounts.Any(x => x is < 2 or > 20) || catalogue.BarCounts.Distinct().Count() != catalogue.BarCounts.Count ||
           catalogue.Layers is not { Count: > 0 and <= 3 } || catalogue.Layers.Any(x => x is < 1 or > 3) || catalogue.Layers.Distinct().Count() != catalogue.Layers.Count)
            return Result(null, BaselineDesignState.NeedsInput, "CATALOGUE.INVALID", "A finite positive bounded bar, link and stock catalogue is required.", "catalogue");
        var member = index.Members.GetValueOrDefault(memberId); var context = inputs.MemberContexts.SingleOrDefault(x => x.MemberId == memberId);
        if (member is null || context is null || !inputs.Project.ValuesAccepted) return Result(null, BaselineDesignState.NeedsInput, "INPUT.ACCEPTANCE", "Member context and explicitly accepted calculation inputs are required; professional approval remains a separate project fact.", "member_context,project");
        if (context.FireBasis is null || !Enum.IsDefined(context.FireBasis.Requirement) || context.FireBasis.Requirement == BaselineFireRequirement.Unspecified || !Text(context.FireBasis.DecisionReference))
            return Result(null, BaselineDesignState.NeedsInput, "FIRE.REQUIREMENT_MISSING", "A project fire requirement and decision reference are required.", "fire_basis");
        if (context.FireBasis.Requirement != BaselineFireRequirement.NotRequired || context.FireBasis.RequiredMinutes is not null)
            return Result(null, BaselineDesignState.Unsupported, "FIRE.PROFILE_UNSUPPORTED", "A required fire rating needs a qualified fire-design profile; this first baseline profile only admits an explicit project decision that fire rating is not required.", "fire_basis");
        var restraints = context.LateralRestraints;
        if (restraints is null || !Text(restraints.EvidenceReference) || restraints.RestraintStationsMm is not { Count: >= 2 and <= 1000 } || restraints.RestraintStationsMm.Any(x => !double.IsFinite(x)) || restraints.RestraintStationsMm.Distinct().Count() != restraints.RestraintStationsMm.Count || !restraints.RestraintStationsMm.SequenceEqual(restraints.RestraintStationsMm.Order()) || restraints.RestraintStationsMm[0] != context.LeftSupportCentreXMm || restraints.RestraintStationsMm[^1] != context.RightSupportCentreXMm)
            return Result(null, BaselineDesignState.NeedsInput, "LATERAL.RESTRAINTS_MISSING", "Ordered lateral-restraint locations across the full support span and their engineering evidence are required.", "lateral_restraints");
        if (!Text(context.PhysicalSpanId, context.SourceMemberId, context.EvidenceRevisionId) ||
           new[] { context.EffectiveSpanMm, context.NominalCoverMm, context.MaximumAggregateSizeMm }.Any(x => !Validation.Positive(x)) ||
           new[] { context.LeftSupportFaceXMm, context.RightSupportFaceXMm, context.LeftSupportCentreXMm, context.RightSupportCentreXMm, context.AnchorageStartXMm, context.AnchorageEndXMm }.Any(x => !double.IsFinite(x)) ||
           !Enum.TryParse<ExposureClass>(context.Exposure, true, out var exposure) || !Enum.IsDefined(exposure) ||
           !(context.AnchorageStartXMm < context.LeftSupportCentreXMm && context.LeftSupportCentreXMm <= context.LeftSupportFaceXMm && context.LeftSupportFaceXMm < context.RightSupportFaceXMm && context.RightSupportFaceXMm <= context.RightSupportCentreXMm && context.RightSupportCentreXMm < context.AnchorageEndXMm))
            return Result(null, BaselineDesignState.NeedsInput, "CONTEXT.GEOMETRY", "Ordered physical support faces, centres, anchorage limits, cover, aggregate and exposure are required.", "member_context");
        var section = index.Sections.GetValueOrDefault(member.SectionId); var material = section is null ? null : inputs.Materials.SingleOrDefault(x => x.MaterialId == section.MaterialId);
        if (section is not null && section.Shape != SnapshotSectionShape.Rectangular) return Result(null, BaselineDesignState.Unsupported, "SECTION.PROFILE_UNSUPPORTED", "The first baseline profile requires a prismatic rectangular section.", "section");
        if (section is null || material is null || section.WidthMm is not > 0 || section.DepthMm is not > 0 || !double.IsFinite(material.SteelModulusNPerMm2) || material.SteelModulusNPerMm2 <= 0) return Result(null, BaselineDesignState.NeedsInput, "SECTION_OR_MATERIAL.MISSING", "A mapped rectangular section and explicit material strengths and steel modulus are required.", "section,material_mapping");
        if (new[] { material.ConcreteStrengthNPerMm2, material.SteelYieldStrengthNPerMm2, material.LinkSteelYieldStrengthNPerMm2 }.Any(x => !Validation.Positive(x)))
            return Result(null, BaselineDesignState.NeedsInput, "MATERIAL.MISSING", "Explicit finite positive strengths are required for the source material ID.", "material_mapping");
        if (!new[] { 20d, 25, 30, 35, 40 }.Contains(material.ConcreteStrengthNPerMm2) || material.SteelYieldStrengthNPerMm2 is < 250 or > 550 || material.LinkSteelYieldStrengthNPerMm2 is < 250 or > 500 || section.DepthMm > 750 || (context.RightSupportFaceXMm - context.LeftSupportFaceXMm) / section.DepthMm <= 2 || member.AssignmentKind != SectionAssignmentKind.Direct)
            return Result(null, BaselineDesignState.Unsupported, "PROFILE.MATERIAL_OR_SECTION", "Deep-beam, side-face-reinforcement and other material domains require a separately qualified profile.", "section,material_mapping");
        var pointI = index.Points.GetValueOrDefault(member.PointIId); var pointJ = index.Points.GetValueOrDefault(member.PointJId); var axis = index.Axes.GetValueOrDefault(member.AxisId);
        var length = pointI is null || pointJ is null ? 0 : Math.Sqrt(Math.Pow(pointJ.XMm - pointI.XMm, 2) + Math.Pow(pointJ.YMm - pointI.YMm, 2) + Math.Pow(pointJ.ZMm - pointI.ZMm, 2));
        if (memberId.Contains('@') || context.PhysicalSpanId.Contains('@') || axis is null || Math.Abs(axis.E2.Z - 1) > 1e-9 || Math.Abs(context.LeftSupportCentreXMm) > 1e-6 || Math.Abs(context.RightSupportCentreXMm - length) > 1e-6 || Math.Abs(context.EffectiveSpanMm - length) > 1e-6 || member.Offsets.EndIMm != 0 || member.Offsets.EndJMm != 0)
            return Result(null, BaselineDesignState.Unsupported, "PROFILE.GEOMETRY", "The first profile requires zero source offsets, vertical local-2 and the conservative centre-to-centre design span.", "member_context,source_geometry");
        if (!context.ScreeningPermitted) return Result(null, BaselineDesignState.NeedsInput, "DEFLECTION.METHOD_REQUIRED", "Explicit acceptance of span/depth screening is required; this profile does not calculate displacement.", "screening_permitted");
        if (context.EffectiveSpanMm > 10000) return Result(null, BaselineDesignState.Unsupported, "DEFLECTION.SPAN_UNSUPPORTED", "The qualified screening method is limited to spans at most 10 m.", "effective_span_mm");
        if (context.SourceMemberId != member.MemberId && context.SourceMemberId != member.ObjectId || !context.Horizontal || !context.TopMappingNormal || context.SupportCondition != BaselineSupportCondition.SimplySupported || pointI is null || pointJ is null || axis is null || pointI.ZMm != pointJ.ZMm || axis.PhysicalTopFace != SnapshotLocal2Face.PositiveLocal2 || !context.OrdinarySeismic || context.EffectiveSpanMm <= 0 || context.LeftSupportFaceXMm >= context.RightSupportFaceXMm) return Result(null, BaselineDesignState.Unsupported, "PROFILE.UNSUPPORTED", "Only snapshot-verified horizontal, ordinary, positive-local-2-top simply-supported spans are supported.", "member_context,snapshot.axes,snapshot.points");
        var roles = inputs.SelectionRoles.ToDictionary(x => x.SelectionId, x => x.Role, StringComparer.Ordinal); var rows = index.Actions[memberId].ToArray();
        if (rows.Length == 0 || roles.Count == 0 || inputs.SelectionRoles.Any(x => !Enum.IsDefined(x.Role)) || rows.Any(x => !roles.ContainsKey(x.SelectionId))) return Result(null, BaselineDesignState.NeedsInput, "ACTION.ROLE_MISSING", "Every member action row requires an explicit ULS/SLS role binding.", "action_rows,selection_roles");
        if (rows.Any(x => x.ActionBasis != SnapshotActionBasis.StaticConcurrent || x.RowId.Contains('@'))) return Result(null, BaselineDesignState.Unsupported, "ACTION.BASIS_UNSUPPORTED", "Only same-row static concurrent actions are qualified by this profile.", "action_rows");
        if (new[] { BaselineSelectionRole.Uls, BaselineSelectionRole.SlsTotal, BaselineSelectionRole.SlsSustained }.Any(role => !rows.Any(x => roles[x.SelectionId] == role))) return Result(null, BaselineDesignState.NeedsInput, "ACTION.ROLE_COVERAGE", "ULS, total-SLS, and sustained-SLS rows are required.", "action_rows");
        var stations = index.Stations[memberId].ToDictionary(x => x.StationId, x => x.PhysicalStationMm, StringComparer.Ordinal);
        if (rows.Any(x => !stations.ContainsKey(x.StationId)) || rows.GroupBy(x => x.SelectionId).Any(g => g.Select(x => x.StationId).Distinct().Count() != stations.Count)) return Result(null, BaselineDesignState.NeedsInput, "STATION.MISSING", "Each selected role requires every physical member station.", "stations");
        var bound = rows.Select(x => new BoundBaselineActionRow(x.RowId, x.SourceRowId, x.StationId, stations[x.StationId], x.SelectionId, x.OutputCaseName, x.StepType, x.StepNumber, x.ActionBasis, roles[x.SelectionId], x.PKn, x.V2Kn, x.V3Kn, x.TKnm, x.M2Knm, x.M3Knm, x.Provenance.EvidenceReference)).ToArray();
        var id = ResultFactory.NormalizedInputId(new { snapshot.SnapshotId, snapshot.SnapshotSha256, inputs.Project, material, inputs.Catalogue, context, memberId, bound });
        return new(new BoundBaselineBeam(id, snapshot.SnapshotId, snapshot.SnapshotSha256, memberId, member.ObjectId, context.PhysicalSpanId, section.SectionId, section.MaterialId, section.WidthMm.Value, section.DepthMm.Value, material.ConcreteStrengthNPerMm2, material.SteelYieldStrengthNPerMm2, material.LinkSteelYieldStrengthNPerMm2, material.SteelModulusNPerMm2, context, inputs.Catalogue, bound), BaselineDesignState.Supported, []);
    }
    private static bool Numbers(IReadOnlyList<double>? values) => values is { Count: > 0 and <= 16 } && values.All(Validation.Positive) && values.Distinct().Count() == values.Count;
    private static bool Unique(IEnumerable<string?> ids) { var values = ids.ToArray(); return values.All(x => !string.IsNullOrWhiteSpace(x)) && values.Distinct().Count() == values.Length; }
    private static bool Text(params string?[] values) => values.All(x => !string.IsNullOrWhiteSpace(x));
    private static BaselineMappingResult Result(BoundBaselineBeam? b, BaselineDesignState s, string code, string message, string field) => new(b, s, [new(code, "error", message, "is456.beam.baseline_input.map/v1", field, "baseline-input-mapper", "Supply a supported, revision-bound input.")]);
}
