using StructuralEngineering.Contracts;
using StructuralEngineering.Core;

namespace StructuralEngineering.Codes.IS456;

/// <summary>Bounded IS 456 / IS 13920 beam-detailing operations for WP05.</summary>
public static class Detailing
{
    public const string DevelopmentLengthOperation = "is456.reinforcement.development_length/v1";
    public const string AnchorageCheckOperation = "is456.beam.anchorage.check/v1";
    public const string LapCurtailmentCheckOperation = "is456.beam.lap_curtailment.check/v1";
    public const string SeismicDetailingCheckOperation = "is456.beam.seismic_detailing.check/v1";
    public const string ArrangementCheckOperation = "structural.reinforcement_arrangement.check/v1";
    private const string Is456Revision = "is456-amd6-wp05-v1";
    private const string Is13920Revision = "is13920-2016-amd2-wp05-v1";
    private const string ShearCheckOperation = "is456.beam.shear.check/v1";

    public static ResultEnvelope<DevelopmentLengthOutput> DevelopmentLength(DevelopmentLengthRequest request)
    {
        var inputs = Inputs(request);
        var source = Source("is456-development-length-amd6-wp05-v1", request.CodeDataRevisionId);
        if (!Text(request.ProfileId) || request.CodeDataRevisionId != Is456Revision ||
            !Positive(request.BarDiameterMm) || !Positive(request.BarStressNPerMm2) ||
            !Positive(request.SteelYieldStrengthNPerMm2) || !Positive(request.ConcreteGradeNPerMm2) ||
            !Enum.IsDefined(request.BarSurface) || !Enum.IsDefined(request.StressState) ||
            request.BundleSize is < 1 or > 4)
            return Rejected<DevelopmentLengthOutput>(DevelopmentLengthOperation, inputs, source, "INPUT.INVALID",
                "Development length requires explicit positive material, bar, stress-state, surface, and bundle inputs.", "request");
        if (request.BarStressNPerMm2 > .87 * request.SteelYieldStrengthNPerMm2 + 1e-12)
            return Rejected<DevelopmentLengthOutput>(DevelopmentLengthOperation, inputs, source, "STRESS.OUTSIDE_PROFILE",
                "Bar stress exceeds the bounded 0.87fy limit-state profile.", "bar_stress_n_per_mm2");
        var plain = request.ConcreteGradeNPerMm2 switch { 20 => 1.2, 25 => 1.4, 30 => 1.5, 35 => 1.7, >= 40 => 1.9, _ => 0d };
        if (plain == 0)
            return ResultFactory.NotApplicable<DevelopmentLengthOutput>(DevelopmentLengthOperation, inputs, source,
                Info(DevelopmentLengthOperation, "PROFILE.CONCRETE_GRADE", "The WP05 IS 456 profile supports M20, M25, M30, M35, and M40 or higher.", "concrete_grade_n_per_mm2"));
        var surface = request.BarSurface switch { BarSurface.Plain => 1d, BarSurface.Deformed => 1.6, BarSurface.FusionBondedEpoxyDeformed => 1.28, _ => 0d };
        var stress = request.StressState == StressState.Compression ? 1.25 : 1d;
        var bond = plain * surface * stress;
        var unbundled = request.BarDiameterMm * request.BarStressNPerMm2 / (4 * bond);
        var bundle = request.BundleSize switch { 1 => 1d, 2 => 1.1, 3 => 1.2, 4 => 1.33, _ => 0d };
        return ResultFactory.Completed(DevelopmentLengthOperation, inputs,
            new DevelopmentLengthOutput(plain, surface, stress, bond, unbundled, bundle, unbundled * bundle), source);
    }

    public static ResultEnvelope<AnchorageCheckOutput> CheckAnchorage(AnchorageCheckRequest request)
    {
        var inputs = Inputs(request);
        var source = Source("is456-anchorage-path-check-wp05-v1", request.CodeDataRevisionId);
        if (!Text(request.ProfileId) || !Text(request.MemberId) || !Text(request.ReinforcementRevisionId) || request.CodeDataRevisionId != Is456Revision)
            return Missing<AnchorageCheckOutput>(AnchorageCheckOperation, inputs, source, "Member and reinforcement-revision identity is required.", "identity");
        if (request.Paths is not { Count: > 0 }) return Missing<AnchorageCheckOutput>(AnchorageCheckOperation, inputs, source, "Actual longitudinal bar-end paths are required.", "paths");
        if (request.Paths.Any(p => !Text(p.BarId)) || request.Paths.Select(p => p.BarId).Distinct().Count() != request.Paths.Count)
            return Rejected<AnchorageCheckOutput>(AnchorageCheckOperation, inputs, source, "PATH.IDENTITY", "Anchorage paths require unique nonblank bar ids.", "paths");
        var checks = new List<AnchorageBarCheck>();
        var diagnostics = new List<Diagnostic>();
        foreach (var path in request.Paths)
        {
            if (!Text(path.CriticalSectionId) || !Enum.IsDefined(path.Location) || !Enum.IsDefined(path.Direction) ||
                !Finite(path.PathStartXMm, path.PathEndXMm, path.CriticalSectionXMm) || path.PathStartXMm >= path.PathEndXMm ||
                path.CriticalSectionXMm < path.PathStartXMm || path.CriticalSectionXMm > path.PathEndXMm)
                return Rejected<AnchorageCheckOutput>(AnchorageCheckOperation, inputs, source, "PATH.GEOMETRY", "Each bar needs an ordered path, critical section, direction, and location.", $"paths[{path.BarId}]");
            var atSupport = path.Location is AnchorageLocation.SimpleSupport or AnchorageLocation.ContinuousSupport;
            if (atSupport && (!Text(path.SupportId) || path.SupportNearFaceXMm is null || path.SupportCentreXMm is null ||
                !Finite(path.SupportNearFaceXMm.Value, path.SupportCentreXMm.Value) || Math.Abs(path.CriticalSectionXMm - path.SupportNearFaceXMm.Value) > 1e-9))
                return Rejected<AnchorageCheckOutput>(AnchorageCheckOperation, inputs, source, "SUPPORT.FACE_REQUIRED", "Support anchorage requires separate support identity, near-face, and centre coordinates; the critical section is the near face.", $"paths[{path.BarId}].support");
            var bend = BendCredit(path, out var bendError);
            if (bendError is not null) return ResultFactory.Rejected<AnchorageCheckOutput>(AnchorageCheckOperation, inputs, source, bendError);
            var development = DevelopmentLength(path.Development);
            if (development.Execution != ExecutionState.Completed) return ResultFactory.Rejected<AnchorageCheckOutput>(AnchorageCheckOperation, inputs, source, development.Diagnostics.ToArray());
            if (development.Applicability != ApplicabilityState.Applicable) return ResultFactory.NotApplicable<AnchorageCheckOutput>(AnchorageCheckOperation, inputs, source, development.Diagnostics.ToArray());
            var required = development.Outputs!.RequiredDevelopmentLengthMm;
            var straight = path.Direction == AnchorageDirection.IncreasingX ? path.PathEndXMm - path.CriticalSectionXMm : path.CriticalSectionXMm - path.PathStartXMm;
            var available = straight + bend;
            var contribution = 0d;
            var beyondCentre = 0d;
            var criterion = "direct_development";
            if (path.Location == AnchorageLocation.SimpleSupport)
            {
                var evidence = path.SimpleSupportEvidence;
                if (evidence is null || !Nonnegative(evidence.MomentResistanceNmm) || !Positive(evidence.SupportShearN) || !Identifiers(evidence.ActionRowIds))
                    return Missing<AnchorageCheckOutput>(AnchorageCheckOperation, inputs, source, "Simple-support anchorage requires moment resistance, support shear, and source action rows.", $"paths[{path.BarId}].simple_support_evidence");
                beyondCentre = Math.Max(0, path.Direction == AnchorageDirection.IncreasingX ? path.PathEndXMm - path.SupportCentreXMm!.Value : path.SupportCentreXMm!.Value - path.PathStartXMm) + bend;
                contribution = evidence.MomentResistanceNmm / evidence.SupportShearN;
                available = contribution + beyondCentre;
                criterion = "simple_support_moment_shear_plus_lo";
            }
            var passed = required <= available + 1e-9;
            if (!passed) diagnostics.Add(Error(AnchorageCheckOperation, "ANCHORAGE.DEFICIT", "Actual straight path and credited bends do not satisfy the applicable development criterion.", $"paths[{path.BarId}]"));
            checks.Add(new(path.BarId, path.CriticalSectionId, path.Location, criterion, development.ResultId, required, straight, bend, contribution, beyondCentre, available, Math.Max(0, required - available), available > 0 ? required / available : null, passed));
        }
        var passedAll = diagnostics.Count == 0;
        var utilizationValues = checks.Where(c => c.Utilization is not null).Select(c => c.Utilization!.Value).ToArray();
        return ResultFactory.Completed(AnchorageCheckOperation, inputs, new AnchorageCheckOutput(request.MemberId, request.ReinforcementRevisionId, checks, utilizationValues.Length == 0 ? null : utilizationValues.Max(), passedAll), source, passedAll ? EngineeringState.Pass : EngineeringState.Fail, diagnostics.ToArray());
    }

    public static ResultEnvelope<LapCurtailmentCheckOutput> CheckLapsAndCurtailment(LapCurtailmentCheckRequest request)
    {
        var inputs = Inputs(request);
        var source = Source("is456-lap-curtailment-evidence-check-wp05-v1", request.CodeDataRevisionId);
        if (!Text(request.ProfileId) || !Text(request.MemberId) || !Text(request.PhysicalSpanId) || !Text(request.DemandRevisionId) || !Text(request.ReinforcementRevisionId) || request.CodeDataRevisionId != Is456Revision || !Positive(request.EffectiveDepthMm) || !Positive(request.ConcreteGradeNPerMm2) || !Positive(request.SteelYieldStrengthNPerMm2) || !Enum.IsDefined(request.BarSurface) || !Finite(request.MemberStartXMm, request.MemberEndXMm) || request.MemberStartXMm >= request.MemberEndXMm)
            return Rejected<LapCurtailmentCheckOutput>(LapCurtailmentCheckOperation, inputs, source, "INPUT.INVALID", "The lap and curtailment check requires complete identities, member geometry, materials, and revision binding.", "request");
        if (request.Bars is not { Count: > 0 } || request.Demands is not { Count: > 0 }) return Missing<LapCurtailmentCheckOutput>(LapCurtailmentCheckOperation, inputs, source, "Actual bar paths and the current station steel-demand envelope are required.", "bars,demands");
        if (request.Splices.Count == 0 && request.Curtailments.Count == 0) return Missing<LapCurtailmentCheckOutput>(LapCurtailmentCheckOperation, inputs, source, "At least one actual splice or curtailment detail is required.", "splices,curtailments");
        if (request.Bars.Any(b => !ValidBar(b)) || request.Bars.Select(b => b.BarId).Distinct().Count() != request.Bars.Count || request.Demands.Any(d => !Text(d.StationId) || !Text(d.ActionRowId) || !Enum.IsDefined(d.Role) || !Finite(d.StationXMm) || d.StationXMm < request.MemberStartXMm || d.StationXMm > request.MemberEndXMm || !Nonnegative(d.RequiredAreaMm2) || !Nonnegative(d.ShearDemandN) || !Nonnegative(d.ShearCapacityN)))
            return Rejected<LapCurtailmentCheckOutput>(LapCurtailmentCheckOperation, inputs, source, "DETAIL.IDENTITY_OR_GEOMETRY", "Bars and demand records require valid geometry and unique identities.", "bars,demands");
        if ((request.ProhibitedSpliceZones ?? []).Any(zone =>
                !Text(zone.ZoneId) ||
                !Finite(zone.StartXMm, zone.EndXMm) ||
                zone.StartXMm >= zone.EndXMm))
            return Rejected<LapCurtailmentCheckOutput>(LapCurtailmentCheckOperation, inputs, source, "ZONE.INVALID", "Every prohibited splice zone requires identity and an ordered interval.", "prohibited_splice_zones");
        var bars = request.Bars.ToDictionary(b => b.BarId);
        var demands = request.Demands.ToDictionary(d => d.StationId);
        var diagnostics = new List<Diagnostic>();
        var spliceChecks = new List<SpliceCheck>();
        foreach (var splice in request.Splices)
        {
            if (!Text(splice.SpliceId) || !Enum.IsDefined(splice.Kind) || !Enum.IsDefined(splice.StressState) || !Identifiers(splice.BarIds) || splice.BarIds.Distinct().Count() != splice.BarIds.Count || splice.BarIds.Any(id => !bars.ContainsKey(id)) || !Finite(splice.StartXMm, splice.EndXMm) || splice.StartXMm >= splice.EndXMm || splice.PercentageSplicedAtSection is <= 0 or > 100 || !Text(splice.StaggerGroup) || (splice.DirectTension && splice.StressState != StressState.Tension) || splice.StartXMm < request.MemberStartXMm || splice.EndXMm > request.MemberEndXMm)
                return Rejected<LapCurtailmentCheckOutput>(LapCurtailmentCheckOperation, inputs, source, "SPLICE.INVALID", "Every splice requires an ordered zone, actual bar ids, stress state, percentage, and stagger group.", $"splices[{splice.SpliceId}]");
            var spliceBars = splice.BarIds.Select(id => bars[id]).ToArray();
            var zoneAllowed = !(request.ProhibitedSpliceZones ?? []).Any(z =>
                Overlap(splice.StartXMm, splice.EndXMm, z.StartXMm, z.EndXMm));
            var percentOk = splice.PercentageSplicedAtSection <= 50;
            var lapAllowed = splice.Kind != SpliceKind.Lap || spliceBars.All(b => b.DiameterMm <= 36);
            var ids = new List<string>();
            double? required = null;
            var qualification = true;
            if (splice.Kind == SpliceKind.Lap)
            {
                var lengths = new List<double>();
                foreach (var bar in spliceBars)
                {
                    var d = DevelopmentLength(new(
                        request.ProfileId,
                        bar.DiameterMm,
                        .87 * request.SteelYieldStrengthNPerMm2,
                        request.SteelYieldStrengthNPerMm2,
                        request.ConcreteGradeNPerMm2,
                        request.BarSurface,
                        splice.StressState,
                        bar.BundleSize,
                        request.CodeDataRevisionId));
                    if (d.Applicability == ApplicabilityState.NotApplicable)
                    {
                        return ResultFactory.NotApplicable<LapCurtailmentCheckOutput>(LapCurtailmentCheckOperation, inputs, source, d.Diagnostics.ToArray());
                    }
                    if (d.Execution != ExecutionState.Completed || d.Outputs is null)
                    {
                        return ResultFactory.Rejected<LapCurtailmentCheckOutput>(LapCurtailmentCheckOperation, inputs, source, d.Diagnostics.ToArray());
                    }
                    ids.Add(d.ResultId);
                    lengths.Add(splice.StressState == StressState.Compression
                        ? Math.Max(d.Outputs.RequiredDevelopmentLengthMm, 24 * bar.DiameterMm)
                        : Math.Max(
                            (splice.DirectTension ? 2 : 1) * d.Outputs.RequiredDevelopmentLengthMm,
                            30 * bar.DiameterMm));
                }
                required = lengths.Max();
                qualification = splice.EndXMm - splice.StartXMm + 1e-9 >= required;
            }
            else qualification = Text(splice.CouplerQualificationReference) && Text(splice.InstallationReference);
            var passed = zoneAllowed && percentOk && lapAllowed && qualification;
            if (!passed) diagnostics.Add(Error(LapCurtailmentCheckOperation, "SPLICE.NONCOMPLIANT", "The splice fails its length or qualification, permitted bar diameter, percentage, staggering, or zone rule.", $"splices[{splice.SpliceId}]"));
            spliceChecks.Add(new(splice.SpliceId, splice.Kind, splice.BarIds, spliceBars.Max(b => b.DiameterMm), splice.EndXMm - splice.StartXMm, required, ids, lapAllowed, percentOk, splice.StaggerGroup, zoneAllowed, qualification, passed));
        }
        var cutoffChecks = new List<CurtailmentCheck>();
        foreach (var cutoff in request.Curtailments)
        {
            if (!Text(cutoff.CutoffId) || !bars.ContainsKey(cutoff.BarId) || !demands.TryGetValue(cutoff.DemandStationId, out var demand) || !Enum.IsDefined(cutoff.Direction) || !Positive(cutoff.RequiredExtensionMm) || !Identifiers(cutoff.ContinuingBarIds) || cutoff.ContinuingBarIds.Distinct().Count() != cutoff.ContinuingBarIds.Count || cutoff.ContinuingBarIds.Any(id => !bars.ContainsKey(id)) || cutoff.ContinuingBarIds.Contains(cutoff.BarId) || !Finite(cutoff.TheoreticalCutoffXMm, cutoff.ActualEndXMm))
                return Rejected<LapCurtailmentCheckOutput>(LapCurtailmentCheckOperation, inputs, source, "CURTAILMENT.INVALID", "Every curtailment requires its actual bar, demand station, direction, required extension, and identified continuing bars.", $"curtailments[{cutoff.CutoffId}]");
            var extension = cutoff.Direction == AnchorageDirection.IncreasingX
                ? cutoff.ActualEndXMm - cutoff.TheoreticalCutoffXMm
                : cutoff.TheoreticalCutoffXMm - cutoff.ActualEndXMm;
            var continuing = cutoff.ContinuingBarIds
                .Select(id => bars[id])
                .Where(b => b.Role == demand.Role && b.StartStationMm <= demand.StationXMm && demand.StationXMm <= b.EndStationMm)
                .Sum(Area);
            var extensionOk = extension + 1e-9 >= cutoff.RequiredExtensionMm;
            var steelOk = continuing + 1e-9 >= demand.RequiredAreaMm2;
            var anchorageOk = cutoff.AnchorageCheck.Qualifies(AnchorageCheckOperation);
            var shearOk = cutoff.ShearCutoffCheck.Qualifies(ShearCheckOperation);
            var linksOk = !cutoff.ExtraLinksRequired || cutoff.ExtraLinksCheck?.Qualifies(ShearCheckOperation) == true;
            var passed = extensionOk && steelOk && anchorageOk && shearOk && linksOk;
            if (!passed) diagnostics.Add(Error(LapCurtailmentCheckOperation, "CURTAILMENT.NONCOMPLIANT", "The actual termination fails extension, remaining-steel, anchorage, shear-at-cutoff, or extra-link evidence.", $"curtailments[{cutoff.CutoffId}]"));
            cutoffChecks.Add(new(cutoff.CutoffId, cutoff.BarId, cutoff.DemandStationId, demand.ActionRowId, extension, cutoff.RequiredExtensionMm, extensionOk, cutoff.ContinuingBarIds, continuing, demand.RequiredAreaMm2, steelOk, cutoff.AnchorageCheck.ResultId, anchorageOk, cutoff.ShearCutoffCheck.ResultId, shearOk, cutoff.ExtraLinksRequired, cutoff.ExtraLinksCheck?.ResultId, linksOk, passed));
        }
        var passedAll = diagnostics.Count == 0;
        return ResultFactory.Completed<LapCurtailmentCheckOutput>(
            LapCurtailmentCheckOperation,
            inputs,
            new(request.MemberId, request.PhysicalSpanId, request.DemandRevisionId, request.ReinforcementRevisionId, spliceChecks, cutoffChecks, passedAll),
            source,
            passedAll ? EngineeringState.Pass : EngineeringState.Fail,
            diagnostics.ToArray());
    }

    public static ResultEnvelope<SeismicDetailingCheckOutput> CheckSeismicDetailing(SeismicDetailingCheckRequest request)
    {
        var inputs = Inputs(request);
        var source = Source("is13920-beam-detailing-amd2-wp05-v1", request.CodeDataRevisionId, true);
        if (!Text(request.ProfileId) || !Enum.IsDefined(request.Applicability) || request.CodeDataRevisionId != Is13920Revision) return Rejected<SeismicDetailingCheckOutput>(SeismicDetailingCheckOperation, inputs, source, "INPUT.INVALID", "The seismic detailing request requires a supported profile, applicability, and exact code-data revision.", "request");
        if (request.Applicability == SeismicApplicability.OrdinaryIs456) return ResultFactory.NotApplicable<SeismicDetailingCheckOutput>(SeismicDetailingCheckOperation, inputs, source, Info(SeismicDetailingCheckOperation, "PROFILE.NOT_SEISMIC", "The selected member is outside the IS 13920 beam detailing profile.", "applicability"));
        var c = request.Context;
        if (c is null) return Missing<SeismicDetailingCheckOutput>(SeismicDetailingCheckOperation, inputs, source, "A complete member, system, joint, reinforcement, and capacity-design context is required.", "context");
        if (new[] { c.SystemId, c.SeismicDesignRevisionId, c.MemberId, c.PhysicalSpanId, c.LeftJointId, c.RightJointId }.Any(x => !Text(x)) || !Finite(c.LeftJointFaceXMm, c.RightJointFaceXMm, c.WidthMm, c.OverallDepthMm, c.EffectiveDepthMm, c.ConcreteGradeNPerMm2, c.SteelYieldStrengthNPerMm2, c.ImportedAnalysisShearN, c.GravityShearN, c.LeftPositiveProbableMomentNmm, c.LeftNegativeProbableMomentNmm, c.RightPositiveProbableMomentNmm, c.RightNegativeProbableMomentNmm, c.ProvidedShearCapacityN) || c.LeftJointFaceXMm >= c.RightJointFaceXMm || !Positive(c.WidthMm) || !Positive(c.OverallDepthMm) || !Positive(c.EffectiveDepthMm) || c.EffectiveDepthMm >= c.OverallDepthMm || !Positive(c.ConcreteGradeNPerMm2) || !Positive(c.SteelYieldStrengthNPerMm2) || !Positive(c.ProvidedShearCapacityN) || new[] { c.LeftPositiveProbableMomentNmm, c.LeftNegativeProbableMomentNmm, c.RightPositiveProbableMomentNmm, c.RightNegativeProbableMomentNmm }.Any(x => x < 0)) return Rejected<SeismicDetailingCheckOutput>(SeismicDetailingCheckOperation, inputs, source, "CONTEXT.INVALID", "The seismic member requires valid identities, joint faces, section/material values, actions, strengths, and effective depth.", "context");
        if (!new[] { 415d, 500d, 550d }.Contains(c.SteelYieldStrengthNPerMm2)) return ResultFactory.NotApplicable<SeismicDetailingCheckOutput>(SeismicDetailingCheckOperation, inputs, source, Info(SeismicDetailingCheckOperation, "PROFILE.STEEL_GRADE", "The WP05 seismic profile supports Fe 415, Fe 500, and Fe 550 reinforcement.", "context.steel_yield_strength_n_per_mm2"));
        if (c.Bars.Count == 0 || c.LinkZones.Count == 0 || c.AnchorageChecks.Count < 4 || c.DependentJointChecks.Count < 2) return Missing<SeismicDetailingCheckOutput>(SeismicDetailingCheckOperation, inputs, source, "Actual bars, link zones, four face anchorage results, and both dependent joint checks are required.", "context");
        var expectedAnchorageLocations = new HashSet<(BeamEnd End, ReinforcementRole Role)>
        {
            (BeamEnd.Left, ReinforcementRole.TopLongitudinal),
            (BeamEnd.Left, ReinforcementRole.BottomLongitudinal),
            (BeamEnd.Right, ReinforcementRole.TopLongitudinal),
            (BeamEnd.Right, ReinforcementRole.BottomLongitudinal)
        };
        var actualAnchorageLocations = c.AnchorageChecks
            .Select(binding => (binding.BeamEnd, binding.Role))
            .ToArray();
        var actualJointIds = c.DependentJointChecks
            .Select(binding => binding.JointId)
            .ToArray();
        if (actualAnchorageLocations.Length != 4 ||
            !expectedAnchorageLocations.SetEquals(actualAnchorageLocations) ||
            actualJointIds.Length != 2 ||
            !actualJointIds.ToHashSet().SetEquals([c.LeftJointId, c.RightJointId]))
            return Rejected<SeismicDetailingCheckOutput>(
                SeismicDetailingCheckOperation,
                inputs,
                source,
                "DEPENDENCY.BINDING_INVALID",
                "Seismic dependencies must bind one anchorage result to each beam-end/face pair and one joint result to each named joint.",
                "context.anchorage_checks,context.dependent_joint_checks");
        if (c.Bars.Any(b => !ValidBar(b))) return Rejected<SeismicDetailingCheckOutput>(SeismicDetailingCheckOperation, inputs, source, "BAR.INVALID", "Every seismic longitudinal bar requires valid identity, role, geometry, and stress data.", "context.bars");
        if (c.Bars.Select(bar => bar.BarId).Distinct().Count() != c.Bars.Count ||
            c.LinkZones.Any(zone => !Text(zone.ZoneId) ||
                !Finite(zone.StartXMm, zone.EndXMm, zone.SpacingMm, zone.LinkDiameterMm) ||
                zone.StartXMm >= zone.EndXMm || !Positive(zone.SpacingMm) ||
                !Positive(zone.LinkDiameterMm) || zone.FirstHoopOffsetFromJointFaceMm is < 0) ||
            c.LinkZones.Select(zone => zone.ZoneId).Distinct().Count() != c.LinkZones.Count ||
            c.Splices.Any(splice => !Text(splice.SpliceId) ||
                !Enum.IsDefined(splice.Kind) || !Enum.IsDefined(splice.StressState) ||
                !Identifiers(splice.BarIds) ||
                splice.BarIds.Distinct().Count() != splice.BarIds.Count ||
                splice.BarIds.Any(id => !c.Bars.Any(bar => bar.BarId == id)) ||
                !Finite(splice.StartXMm, splice.EndXMm) ||
                splice.StartXMm >= splice.EndXMm ||
                splice.PercentageSplicedAtSection is <= 0 or > 100 ||
                !Text(splice.StaggerGroup) ||
                (splice.DirectTension && splice.StressState != StressState.Tension)) ||
            c.Splices.Select(splice => splice.SpliceId).Distinct().Count() != c.Splices.Count)
            return Rejected<SeismicDetailingCheckOutput>(SeismicDetailingCheckOperation, inputs, source, "DETAIL.INVALID", "Seismic bars, link zones, and splice records require unique identities and valid geometry.", "context");
        var diagnostics = new List<Diagnostic>();
        var rules = new List<SeismicRuleCheck>();
        void Rule(string id, bool pass, object actual, object limit, string field, string message)
        {
            rules.Add(new(id, actual, limit, pass));
            if (!pass)
            {
                diagnostics.Add(Error(SeismicDetailingCheckOperation, "SEISMIC." + id, message, field));
            }
        }
        var widthDepth = c.WidthMm / c.OverallDepthMm;
        Rule("GEOMETRY_WIDTH", c.WidthMm >= 200, c.WidthMm, 200d, "context.width_mm", "Beam width is below the supported IS 13920 minimum.");
        Rule("GEOMETRY_RATIO", widthDepth > .3, widthDepth, ">0.3", "context.width_mm,context.overall_depth_mm", "Beam width-to-depth ratio does not exceed 0.3.");
        var minRatio = .24 * Math.Sqrt(c.ConcreteGradeNPerMm2) / c.SteelYieldStrengthNPerMm2;
        const double maxRatio = .025;
        var steel = new List<SeismicSteelFaceCheck>();
        foreach (var (face, station) in new[] { ("left", c.LeftJointFaceXMm), ("right", c.RightJointFaceXMm) })
        {
            foreach (var role in new[] { ReinforcementRole.TopLongitudinal, ReinforcementRole.BottomLongitudinal })
            {
                var active = c.Bars.Where(b => b.Role == role && b.StartStationMm <= station && station <= b.EndStationMm).ToArray();
                var area = active.Sum(Area);
                var ratio = area / (c.WidthMm * c.EffectiveDepthMm);
                var pass = minRatio <= ratio && ratio <= maxRatio;
                steel.Add(new(face, role, active.Select(b => b.BarId).ToArray(), area, ratio, minRatio, maxRatio, pass));
                Rule($"STEEL_{face.ToUpperInvariant()}_{RoleWireName(role).ToUpperInvariant()}", pass, ratio, new { minimum = minRatio, maximum = maxRatio }, "context.bars", "Actual face reinforcement is outside the permitted longitudinal-steel range.");
            }
        }
        var top = c.Bars
            .Where(b => b.Role == ReinforcementRole.TopLongitudinal &&
                b.StartStationMm <= c.LeftJointFaceXMm &&
                b.EndStationMm >= c.RightJointFaceXMm)
            .Select(b => b.BarId)
            .ToArray();
        var bottom = c.Bars
            .Where(b => b.Role == ReinforcementRole.BottomLongitudinal &&
                b.StartStationMm <= c.LeftJointFaceXMm &&
                b.EndStationMm >= c.RightJointFaceXMm)
            .Select(b => b.BarId)
            .ToArray();
        Rule(
            "TOP_CONTINUITY",
            top.Length >= 2,
            top,
            "at least two continuous bars",
            "context.bars",
            "Fewer than two top bars continue through the clear span.");
        Rule(
            "BOTTOM_CONTINUITY",
            bottom.Length >= 2,
            bottom,
            "at least two continuous bars",
            "context.bars",
            "Fewer than two bottom bars continue through the clear span.");

        var zoneLength = 2 * c.EffectiveDepthMm;
        var maxSpacing = Math.Min(
            c.EffectiveDepthMm / 4,
            Math.Min(6 * c.Bars.Min(b => b.DiameterMm), 100));
        var leftZones = c.LinkZones
            .Where(z => z.StartXMm <= c.LeftJointFaceXMm &&
                z.EndXMm >= c.LeftJointFaceXMm + zoneLength)
            .ToArray();
        var rightZones = c.LinkZones
            .Where(z => z.StartXMm <= c.RightJointFaceXMm - zoneLength &&
                z.EndXMm >= c.RightJointFaceXMm)
            .ToArray();
        bool ZoneOk(IEnumerable<SeismicLinkZone> zones) =>
            zones.Any() && zones.All(z =>
                Positive(z.SpacingMm) &&
                Positive(z.LinkDiameterMm) &&
                z.SpacingMm <= maxSpacing + 1e-9 &&
                z.Closed &&
                z.HookAngleDegrees >= 135 &&
                z.FirstHoopOffsetFromJointFaceMm is >= 0 and <= 50);
        Rule(
            "LEFT_END_LINK_ZONE",
            ZoneOk(leftZones),
            leftZones.Select(z => z.ZoneId).ToArray(),
            zoneLength,
            "context.link_zones",
            "The left end lacks a complete qualifying close-link zone.");
        Rule(
            "RIGHT_END_LINK_ZONE",
            ZoneOk(rightZones),
            rightZones.Select(z => z.ZoneId).ToArray(),
            zoneLength,
            "context.link_zones",
            "The right end lacks a complete qualifying close-link zone.");
        Rule(
            "ANCHORAGE_RESULTS",
            c.AnchorageChecks.All(binding => binding.Check.Qualifies(AnchorageCheckOperation)),
            c.AnchorageChecks.Select(binding => new Dictionary<string, string>
            {
                ["beam_end"] = BeamEndWireName(binding.BeamEnd),
                ["role"] = RoleWireName(binding.Role),
                ["result_id"] = binding.Check.ResultId
            }).ToArray(),
            "one current passing complete anchorage result per left/right top/bottom pair",
            "context.anchorage_checks",
            "One or more required face anchorage results do not qualify.");
        Rule(
            "JOINT_RESULTS",
            c.DependentJointChecks.All(binding => binding.Check.Qualifies()),
            c.DependentJointChecks.Select(binding => new Dictionary<string, string>
            {
                ["joint_id"] = binding.JointId,
                ["result_id"] = binding.Check.ResultId
            }).ToArray(),
            "one current passing complete result for each named joint",
            "context.dependent_joint_checks",
            "One or more dependent joint/system results do not qualify.");
        var spliceChecks = new List<SeismicSpliceCheck>();
        foreach (var s in c.Splices)
        {
            var outside = !Overlap(s.StartXMm, s.EndXMm, c.LeftJointFaceXMm, c.LeftJointFaceXMm + zoneLength) && !Overlap(s.StartXMm, s.EndXMm, c.RightJointFaceXMm - zoneLength, c.RightJointFaceXMm);
            var percent = s.PercentageSplicedAtSection is > 0 and <= 50;
            var evidence = s.Kind == SpliceKind.Lap || (Text(s.CouplerQualificationReference) && Text(s.InstallationReference));
            var pass = outside && percent && evidence;
            spliceChecks.Add(new(s.SpliceId, outside, percent, evidence, pass));
            Rule("SPLICE_" + s.SpliceId, pass, spliceChecks[^1], "outside end zones, at most 50 percent, qualified if mechanical", "context.splices", "A longitudinal splice is in an end zone, exceeds the permitted percentage, or lacks mechanical-splice evidence.");
        }
        var clear = c.RightJointFaceXMm - c.LeftJointFaceXMm;
        var positive = Math.Abs(c.GravityShearN) +
            1.4 * (c.LeftPositiveProbableMomentNmm + c.RightNegativeProbableMomentNmm) / clear;
        var negative = Math.Abs(c.GravityShearN) +
            1.4 * (c.LeftNegativeProbableMomentNmm + c.RightPositiveProbableMomentNmm) / clear;
        var governing = Math.Max(
            Math.Abs(c.ImportedAnalysisShearN),
            Math.Max(positive, negative));
        Rule(
            "CAPACITY_SHEAR",
            c.ShearCheck.Qualifies(ShearCheckOperation) &&
                c.ProvidedShearCapacityN + 1e-9 >= governing,
            new { governing, c.ProvidedShearCapacityN, c.ShearCheck.ResultId },
            "qualified provided capacity",
            "context.shear_check",
            "The qualified provided shear capacity is below the governing imported or capacity-design shear.");

        var seismicPassed = diagnostics.Count == 0;
        var output = new SeismicDetailingCheckOutput(
            c.SystemId,
            c.SeismicDesignRevisionId,
            c.MemberId,
            c.PhysicalSpanId,
            minRatio,
            maxRatio,
            steel,
            top,
            bottom,
            zoneLength,
            maxSpacing,
            spliceChecks,
            positive,
            negative,
            governing,
            rules,
            seismicPassed);
        return ResultFactory.Completed<SeismicDetailingCheckOutput>(
            SeismicDetailingCheckOperation,
            inputs,
            output,
            source,
            seismicPassed ? EngineeringState.Pass : EngineeringState.Fail,
            diagnostics.ToArray());
    }

    public static ResultEnvelope<ReinforcementArrangementCheckOutput> CheckReinforcementArrangement(ReinforcementArrangementCheckRequest request)
    {
        var inputs = Inputs(request);
        var source = Source("reinforcement-arrangement-coordinate-check-wp05-v1", request.CodeDataRevisionId);
        if (!Text(request.ProfileId) || !Text(request.MemberId) || !Text(request.StationId) || !Text(request.ReinforcementRevisionId) || request.CodeDataRevisionId != Is456Revision || !Positive(request.SectionWidthMm) || !Positive(request.SectionDepthMm) || !Positive(request.NominalCoverMm) || !Positive(request.MaximumAggregateSizeMm) || !Nonnegative(request.VerticalAlignmentToleranceMm)) return Rejected<ReinforcementArrangementCheckOutput>(ArrangementCheckOperation, inputs, source, "INPUT.INVALID", "The arrangement check requires complete identities, positive section/cover/aggregate geometry, and an alignment tolerance.", "request");
        var requiredFaces = new[] { ReinforcementRole.TopLongitudinal, ReinforcementRole.BottomLongitudinal };
        if (request.Bars is not { Count: > 0 } || request.Links is not { Count: > 0 } || request.RequiredRoles is not { Count: > 0 } || requiredFaces.Any(r => !request.RequiredRoles.Contains(r))) return Missing<ReinforcementArrangementCheckOutput>(ArrangementCheckOperation, inputs, source, "A full arrangement requires actual bars, links, and both top and bottom longitudinal roles.", "bars,links,required_roles");
        if (request.RequirePlacementPlan && (request.PlacementOpening is null || !Text(request.PlacementOpening.SequenceReference))) return Missing<ReinforcementArrangementCheckOutput>(ArrangementCheckOperation, inputs, source, "The selected construction-fit scope requires a placement opening and sequence reference.", "placement_opening");
        var obstacles = request.Obstacles ?? [];
        if (request.Bars.Any(b => !ValidBar(b)) || request.Bars.Select(b => b.BarId).Distinct().Count() != request.Bars.Count || request.Links.Any(l => !Text(l.LinkId)) || request.Links.Select(l => l.LinkId).Distinct().Count() != request.Links.Count || obstacles.Any(o => !Text(o.ObstacleId)) || obstacles.Select(o => o.ObstacleId).Distinct().Count() != obstacles.Count || request.RequiredRoles.Any(r => !Enum.IsDefined(r)) || request.RequiredRoles.Distinct().Count() != request.RequiredRoles.Count)
        {
            return Rejected<ReinforcementArrangementCheckOutput>(ArrangementCheckOperation, inputs, source, "ARRANGEMENT.INVALID", "Bars, links, obstacles, and required roles need valid geometry and unique identities.", "bars,links,obstacles,required_roles");
        }
        var diagnostics = new List<Diagnostic>();
        void Fail(string code, string msg, string field) => diagnostics.Add(Error(ArrangementCheckOperation, code, msg, field));
        var linkChecks = new List<LinkCageCheck>();
        foreach (var link in request.Links)
        {
            if (!Positive(link.DiameterMm) ||
                !Nonnegative(link.InternalBendRadiusMm) ||
                !Finite(
                    link.LeftCentreXMm,
                    link.RightCentreXMm,
                    link.TopCentreYMm,
                    link.BottomCentreYMm) ||
                link.LeftCentreXMm >= link.RightCentreXMm ||
                link.TopCentreYMm >= link.BottomCentreYMm)
            {
                return Rejected<ReinforcementArrangementCheckOutput>(
                    ArrangementCheckOperation,
                    inputs,
                    source,
                    "LINK.INVALID",
                    "Every link cage requires an ordered centreline rectangle, diameter, and nonnegative bend radius.",
                    $"links[{link.LinkId}]");
            }

            var radius = link.DiameterMm / 2;
            var covers = new Dictionary<string, double>
            {
                ["left"] = link.LeftCentreXMm - radius,
                ["right"] = request.SectionWidthMm - (link.RightCentreXMm + radius),
                ["top"] = link.TopCentreYMm - radius,
                ["bottom"] = request.SectionDepthMm - (link.BottomCentreYMm + radius)
            };
            var coverOk = covers.Values.Min() + 1e-9 >= request.NominalCoverMm;
            var width = link.RightCentreXMm - link.LeftCentreXMm;
            var height = link.BottomCentreYMm - link.TopCentreYMm;
            var minimumBendExtent = 2 * (link.InternalBendRadiusMm + radius);
            var bendFitOk = width + 1e-9 >= minimumBendExtent &&
                height + 1e-9 >= minimumBendExtent;
            var passed = coverOk && bendFitOk && link.Closed;
            if (!passed)
            {
                Fail(
                    "LINK.NONCOMPLIANT",
                    "A link cage fails cover to its steel surface, bend enclosure, or closure.",
                    $"links[{link.LinkId}]");
            }
            linkChecks.Add(new(
                link.LinkId,
                covers,
                request.NominalCoverMm,
                coverOk,
                width,
                height,
                minimumBendExtent,
                bendFitOk,
                link.Closed,
                passed));
        }

        var missingRoles = request.RequiredRoles
            .Where(role => !request.Bars.Any(b => b.Role == role))
            .ToArray();
        if (missingRoles.Length > 0)
        {
            Fail(
                "ROLE.MISSING",
                "One or more declared reinforcement roles have no actual bars.",
                "required_roles");
        }

        var enclosure = new List<BarEnclosureCheck>();
        foreach (var bar in request.Bars)
        {
            var radius = bar.DiameterMm / 2;
            var withinSection = radius <= bar.XFromLeftMm &&
                bar.XFromLeftMm <= request.SectionWidthMm - radius &&
                radius <= bar.YFromTopMm &&
                bar.YFromTopMm <= request.SectionDepthMm - radius;
            var enclosingLinkIds = request.Links
                .Where(link =>
                    bar.XFromLeftMm - radius >=
                        link.LeftCentreXMm + link.DiameterMm / 2 - 1e-9 &&
                    bar.XFromLeftMm + radius <=
                        link.RightCentreXMm - link.DiameterMm / 2 + 1e-9 &&
                    bar.YFromTopMm - radius >=
                        link.TopCentreYMm + link.DiameterMm / 2 - 1e-9 &&
                    bar.YFromTopMm + radius <=
                        link.BottomCentreYMm - link.DiameterMm / 2 + 1e-9)
                .Select(link => link.LinkId)
                .ToArray();
            var passed = withinSection && enclosingLinkIds.Length > 0;
            if (!passed)
            {
                Fail(
                    "BAR.NOT_ENCLOSED",
                    "A longitudinal bar lies outside the section or is not enclosed by a supplied closed link cage.",
                    $"bars[{bar.BarId}]");
            }
            enclosure.Add(new(bar.BarId, withinSection, enclosingLinkIds, passed));
        }

        var pairs = new List<BarPairCheck>();
        for (var firstIndex = 0; firstIndex < request.Bars.Count; firstIndex++)
        {
            for (var secondIndex = firstIndex + 1; secondIndex < request.Bars.Count; secondIndex++)
            {
                var first = request.Bars[firstIndex];
                var second = request.Bars[secondIndex];
                var distance = Distance(
                    first.XFromLeftMm - second.XFromLeftMm,
                    first.YFromTopMm - second.YFromTopMm);
                var minimumDistance = (first.DiameterMm + second.DiameterMm) / 2;
                var passed = distance + 1e-9 >= minimumDistance;
                if (!passed)
                {
                    Fail(
                        "BAR.COLLISION",
                        "Two longitudinal bar circles overlap.",
                        $"bars[{first.BarId},{second.BarId}]");
                }
                pairs.Add(new(
                    first.BarId,
                    second.BarId,
                    distance,
                    minimumDistance,
                    passed));
            }
        }
        var horizontal = new List<HorizontalClearanceCheck>();
        var vertical = new List<VerticalClearanceCheck>();
        var groupedLayers = request.Bars
            .GroupBy(bar => (bar.Role, bar.Layer))
            .ToDictionary(group => group.Key, group => group.ToArray());

        for (var firstIndex = 0; firstIndex < request.Bars.Count; firstIndex++)
        {
            for (var secondIndex = firstIndex + 1; secondIndex < request.Bars.Count; secondIndex++)
            {
                var first = request.Bars[firstIndex];
                var second = request.Bars[secondIndex];
                if (Math.Abs(first.YFromTopMm - second.YFromTopMm) <=
                    request.VerticalAlignmentToleranceMm + 1e-9)
                {
                    var actual = Math.Abs(second.XFromLeftMm - first.XFromLeftMm) -
                        (first.DiameterMm + second.DiameterMm) / 2;
                    var required = Math.Max(
                        Math.Max(first.DiameterMm, second.DiameterMm),
                        request.MaximumAggregateSizeMm + 5);
                    var horizontalPassed = actual + 1e-9 >= required;
                    if (!horizontalPassed)
                        Fail("SPACING.HORIZONTAL", "Bars within one physical row lack the required horizontal clear distance.", $"bars[{first.BarId},{second.BarId}]");
                    horizontal.Add(new(first.Role, first.Layer, second.Role, second.Layer,
                        first.BarId, second.BarId, actual, required, horizontalPassed));
                }

                if (Math.Abs(first.XFromLeftMm - second.XFromLeftMm) <=
                    request.VerticalAlignmentToleranceMm + 1e-9)
                {
                    var actual = Math.Abs(second.YFromTopMm - first.YFromTopMm) -
                        (first.DiameterMm + second.DiameterMm) / 2;
                    var required = Math.Max(15, Math.Max(
                        2 * request.MaximumAggregateSizeMm / 3,
                        Math.Max(first.DiameterMm, second.DiameterMm)));
                    var alignedPassed = actual + 1e-9 >= required;
                    if (!alignedPassed)
                        Fail("SPACING.VERTICAL", "Vertically aligned bars lack the required clear distance.", $"bars[{first.BarId},{second.BarId}]");
                    vertical.Add(new("aligned_pair", first.BarId, second.BarId, null,
                        null, null, actual, required,
                        request.VerticalAlignmentToleranceMm, alignedPassed));
                }
            }
        }

        foreach (var role in request.Bars.Select(bar => bar.Role).Distinct())
        {
            var physicalRows = groupedLayers
                .Where(pair => pair.Key.Role == role)
                .OrderBy(pair => pair.Value.Average(bar => bar.YFromTopMm))
                .ToArray();
            for (var index = 0; index + 1 < physicalRows.Length; index++)
            {
                var upper = physicalRows[index];
                var lower = physicalRows[index + 1];
                var actual = lower.Value.Min(bar => bar.YFromTopMm - bar.DiameterMm / 2) -
                    upper.Value.Max(bar => bar.YFromTopMm + bar.DiameterMm / 2);
                var required = Math.Max(15, Math.Max(
                    2 * request.MaximumAggregateSizeMm / 3,
                    upper.Value.Concat(lower.Value).Max(bar => bar.DiameterMm)));
                var layerGapPassed = actual + 1e-9 >= required;
                if (!layerGapPassed)
                    Fail("SPACING.VERTICAL", "Adjacent physical bar rows lack the required vertical clearance.", $"bars[{role},layers {upper.Key.Layer}-{lower.Key.Layer}]");
                vertical.Add(new("physical_layer_gap", null, null, role,
                    upper.Key.Layer, lower.Key.Layer, actual, required, null, layerGapPassed));
            }
        }
        var centroids = request.Bars
            .GroupBy(b => b.Role)
            .OrderBy(g => g.Key)
            .Select(g =>
            {
                var area = g.Sum(Area);
                return new RoleCentroid(
                    g.Key,
                    g.Select(b => b.BarId).ToArray(),
                    area,
                    g.Sum(b => Area(b) * b.XFromLeftMm) / area,
                    g.Sum(b => Area(b) * b.YFromTopMm) / area);
            })
            .ToArray();
        var obstacleChecks = new List<ObstacleCheck>();
        foreach (var o in obstacles)
        {
            if (!Positive(o.DiameterMm) || !Nonnegative(o.RequiredClearanceMm) || !Finite(o.XFromLeftMm, o.YFromTopMm)) return Rejected<ReinforcementArrangementCheckOutput>(ArrangementCheckOperation, inputs, source, "OBSTACLE.INVALID", "Every construction obstacle requires a circle and nonnegative required clearance.", $"obstacles[{o.ObstacleId}]");
            foreach (var b in request.Bars)
            {
                var d = Distance(o.XFromLeftMm - b.XFromLeftMm, o.YFromTopMm - b.YFromTopMm);
                var need = o.DiameterMm / 2 + b.DiameterMm / 2 + o.RequiredClearanceMm;
                var pass = d + 1e-9 >= need;
                if (!pass) Fail("OBSTACLE.CLASH", "A reinforcement bar clashes with a resolved joint or construction obstacle.", $"obstacles[{o.ObstacleId}],bars[{b.BarId}]");
                obstacleChecks.Add(new(o.ObstacleId, "bar", b.BarId, null, null, d, need, pass));
            }
            foreach (var link in request.Links)
            {
                foreach (var (index, x1, y1, x2, y2) in LinkSegments(link))
                {
                    var distance = PointSegmentDistance(
                        o.XFromLeftMm,
                        o.YFromTopMm,
                        x1,
                        y1,
                        x2,
                        y2);
                    var requiredDistance = o.DiameterMm / 2 +
                        link.DiameterMm / 2 +
                        o.RequiredClearanceMm;
                    var passed = distance + 1e-9 >= requiredDistance;
                    if (!passed)
                    {
                        Fail(
                            "OBSTACLE.CLASH",
                            "A supplied link cage clashes with a resolved joint or construction obstacle.",
                            $"obstacles[{o.ObstacleId}],links[{link.LinkId}]");
                    }
                    obstacleChecks.Add(new(
                        o.ObstacleId,
                        "link_segment",
                        null,
                        link.LinkId,
                        index,
                        distance,
                        requiredDistance,
                        passed));
                }
            }
        }
        PlacementCheck? placement = null;
        if (request.PlacementOpening is not null)
        {
            var opening = request.PlacementOpening;
            if (!Text(opening.OpeningId) ||
                !Positive(opening.ClearWidthMm) ||
                !Positive(opening.ClearHeightMm) ||
                !Text(opening.SequenceReference))
            {
                return Rejected<ReinforcementArrangementCheckOutput>(
                    ArrangementCheckOperation,
                    inputs,
                    source,
                    "PLACEMENT.INVALID",
                    "A placement opening requires identity, positive clear dimensions, and a sequence reference.",
                    "placement_opening");
            }
            var requiredWidth = request.Links.Max(link =>
                link.RightCentreXMm - link.LeftCentreXMm + link.DiameterMm);
            var requiredHeight = request.Links.Max(link =>
                link.BottomCentreYMm - link.TopCentreYMm + link.DiameterMm);
            var passed = opening.ClearWidthMm + 1e-9 >= requiredWidth &&
                opening.ClearHeightMm + 1e-9 >= requiredHeight;
            if (!passed)
            {
                Fail(
                    "PLACEMENT.DOES_NOT_FIT",
                    "The resolved link cage cannot pass through the supplied placement opening.",
                    "placement_opening");
            }
            placement = new(
                opening.OpeningId,
                opening.SequenceReference,
                opening.ClearWidthMm,
                opening.ClearHeightMm,
                requiredWidth,
                requiredHeight,
                passed);
        }
        var arrangementPassed = diagnostics.Count == 0;
        var output = new ReinforcementArrangementCheckOutput(
            request.MemberId,
            request.StationId,
            request.ReinforcementRevisionId,
            linkChecks,
            enclosure,
            pairs,
            horizontal,
            vertical,
            centroids,
            obstacleChecks,
            placement,
            arrangementPassed);
        return ResultFactory.Completed<ReinforcementArrangementCheckOutput>(
            ArrangementCheckOperation,
            inputs,
            output,
            source,
            arrangementPassed ? EngineeringState.Pass : EngineeringState.Fail,
            diagnostics.ToArray());
    }

    private static double BendCredit(AnchoragePath path, out Diagnostic? error)
    {
        error = null;
        if (path.Bends.Count == 0)
        {
            return 0;
        }
        if (!Text(path.BendScheduleReference))
        {
            error = Error(AnchorageCheckOperation, "BEND.EVIDENCE", "Bend credit requires a fabrication schedule reference.", $"paths[{path.BarId}].bend_schedule_reference");
            return 0;
        }
        if (path.Bends.Any(b => !Text(b.BendId) || b.AngleDegrees is not (45 or 90 or 135 or 180)))
        {
            error = Error(AnchorageCheckOperation, "BEND.INVALID", "Every credited bend requires identity and a supported 45-degree increment.", $"paths[{path.BarId}].bends");
            return 0;
        }
        return Math.Min(16 * path.Development.BarDiameterMm, path.Bends.Sum(b => 4 * path.Development.BarDiameterMm * b.AngleDegrees / 45));
    }
    private static IEnumerable<(int Index, double X1, double Y1, double X2, double Y2)> LinkSegments(LinkCage l)
    {
        yield return (1, l.LeftCentreXMm, l.TopCentreYMm, l.RightCentreXMm, l.TopCentreYMm);
        yield return (2, l.RightCentreXMm, l.TopCentreYMm, l.RightCentreXMm, l.BottomCentreYMm);
        yield return (3, l.RightCentreXMm, l.BottomCentreYMm, l.LeftCentreXMm, l.BottomCentreYMm);
        yield return (4, l.LeftCentreXMm, l.BottomCentreYMm, l.LeftCentreXMm, l.TopCentreYMm);
    }
    private static string RoleWireName(ReinforcementRole role) => role switch
    {
        ReinforcementRole.TopLongitudinal => "top_longitudinal",
        ReinforcementRole.BottomLongitudinal => "bottom_longitudinal",
        ReinforcementRole.SideLeft => "side_left",
        ReinforcementRole.SideRight => "side_right",
        ReinforcementRole.Corner => "corner",
        _ => string.Empty
    };

    private static string BeamEndWireName(BeamEnd beamEnd) => beamEnd switch
    {
        BeamEnd.Left => "left",
        BeamEnd.Right => "right",
        _ => string.Empty
    };
    private static double PointSegmentDistance(double px, double py, double x1, double y1, double x2, double y2)
    {
        var dx = x2 - x1;
        var dy = y2 - y1;
        var q = dx * dx + dy * dy;
        var t = q == 0 ? 0 : Math.Clamp(((px - x1) * dx + (py - y1) * dy) / q, 0, 1);
        return Distance(px - (x1 + t * dx), py - (y1 + t * dy));
    }
    private static double Distance(double x, double y) => Math.Sqrt(x * x + y * y);
    private static double Area(LongitudinalBarPath bar) => Math.PI * bar.DiameterMm * bar.DiameterMm / 4;
    private static bool ValidBar(LongitudinalBarPath b) =>
        Text(b.BarId) &&
        Text(b.BarMark) &&
        Enum.IsDefined(b.Role) &&
        Positive(b.DiameterMm) &&
        b.Layer >= 1 &&
        Finite(b.XFromLeftMm, b.YFromTopMm, b.StartStationMm, b.EndStationMm, b.DesignStressNPerMm2) &&
        b.StartStationMm < b.EndStationMm &&
        b.DesignStressNPerMm2 >= 0 &&
        b.BundleSize is >= 1 and <= 4;
    private static bool Overlap(double a, double b, double c, double d) => Math.Max(a, c) < Math.Min(b, d);
    private static bool Text(string? value) => !string.IsNullOrWhiteSpace(value);
    private static bool Positive(double value) => Validation.Positive(value);
    private static bool Nonnegative(double value) => Validation.Nonnegative(value);
    private static bool Finite(params double[] values) => values.All(double.IsFinite);
    private static bool Identifiers(IReadOnlyList<string>? values) => values is { Count: > 0 } && values.All(Text);
    private static IReadOnlyDictionary<string, EffectiveValue> Inputs(object request) => ResultFactory.Effective(("request", request));

    private static Provenance Source(string method, string revision, bool seismic = false)
    {
        IReadOnlyList<string> references = seismic
            ? [
                "IS 13920:2016 with Amendments 1 and 2; bounded beam detailing profile",
                "IS 456:2000 with Amendment 6; development, anchorage, laps and spacing"
            ]
            : [
                "IS 456:2000 with Amendment 6 (2024)",
                "IS 456 clauses 26.2, 26.3 and 26.4 normalized for WP05"
            ];
        return new(revision, method, references);
    }

    private static Diagnostic Error(string op, string code, string message, string field) => new(code, "error", message, op, field, "is456-detailing", "Supply the named detailing evidence.");
    private static Diagnostic Info(string op, string code, string message, string field) => new(code, "information", message, op, field, "is456-detailing", "Use the applicable supported profile.");
    private static ResultEnvelope<T> Rejected<T>(string op, IReadOnlyDictionary<string, EffectiveValue> inputs, Provenance source, string code, string message, string field) => ResultFactory.Rejected<T>(op, inputs, source, Error(op, code, message, field));
    private static ResultEnvelope<T> Missing<T>(string op, IReadOnlyDictionary<string, EffectiveValue> inputs, Provenance source, string message, string field) => ResultFactory.NotEvaluated<T>(op, inputs, source, Error(op, "EVIDENCE.REQUIRED", message, field));
}
