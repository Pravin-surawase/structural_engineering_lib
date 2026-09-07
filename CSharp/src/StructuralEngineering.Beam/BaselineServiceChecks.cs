using System.Text.Json;
using StructuralEngineering.Codes.IS456;
using StructuralEngineering.Contracts;
using StructuralEngineering.Core;

namespace StructuralEngineering.Beam;

/// <summary>Produces the bounded WP11 service leaves from the final, positioned bars.</summary>
public static class BaselineServiceChecks
{
    private const string ServiceRevision = "is456-baseline-serviceability-v1";

    public static void Evaluate(
        BoundBaselineBeam beam,
        BaselineArrangement arrangement,
        string profileId,
        List<BaselineCheckEvidence> checks,
        List<ResultEnvelope<JsonElement>> derivations)
    {
        var uls = beam.ActionRows.Where(row => row.Role == BaselineSelectionRole.Uls).ToArray();
        EvaluateDeflection(beam, arrangement, profileId, uls, checks, derivations);

        foreach (var row in beam.ActionRows.Where(row => row.Role is BaselineSelectionRole.SlsTotal or BaselineSelectionRole.SlsSustained))
            EvaluateCrackRow(beam, arrangement, profileId, row, checks, derivations);
    }

    private static void EvaluateDeflection(BoundBaselineBeam beam, BaselineArrangement arrangement, string profileId,
        IReadOnlyList<BoundBaselineActionRow> uls, List<BaselineCheckEvidence> checks,
        List<ResultEnvelope<JsonElement>> derivations)
    {
        var factors = new List<(Face Face, double Factor)>();
        var producerIds = new List<string>();
        var factorGroups = uls.GroupBy(row => (row.StationId, Face: FaceFor(row.M3Knm))).ToArray();
        foreach (var group in factorGroups)
        {
            var row = group.OrderByDescending(item => Math.Abs(item.M3Knm)).First();
            var faceBars = arrangement.Bars.Where(bar => bar.Face == group.Key.Face).ToArray();
            var depth = EffectiveDepth(arrangement, group.Key.Face);
            var required = BaselineFlexure.RequiredSteel(new BaselineRequiredSteelRequest(profileId, beam.MemberId,
                row.RowId, group.Key.Face, beam.WidthMm, depth, beam.ConcreteStrengthNPerMm2,
                beam.SteelYieldStrengthNPerMm2, Math.Abs(row.M3Knm)));
            derivations.Add(BaselineEvidence.Pack(required));
            producerIds.Add(required.ResultId);
            if (!BaselineEvidence.Qualified(required) || required.Outputs is null || faceBars.Length == 0)
                continue;

            var factor = BaselineServiceability.Figure4TensionFactor(new Figure4TensionFactorRequest(profileId,
                beam.MemberId, row.StationId, arrangement.RevisionId, row.RowId, required.Outputs.RequiredAreaMm2,
                faceBars.Sum(Area), beam.WidthMm, depth, beam.SteelYieldStrengthNPerMm2, ServiceRevision));
            derivations.Add(BaselineEvidence.Pack(factor));
            producerIds.Add(factor.ResultId);
            if (BaselineEvidence.Qualified(factor) && factor.Outputs is not null)
                factors.Add((group.Key.Face, factor.Outputs.ModificationFactor));
        }

        ResultEnvelope<DeflectionCheckOutput> result;
        var support = ToSupportCondition(beam.Context.SupportCondition);
        if (uls.Count == 0 || factors.Count != factorGroups.Length || support is null || !beam.Context.ScreeningPermitted)
        {
            result = Missing<DeflectionCheckOutput>(Serviceability.DeflectionCheckOperation, profileId, beam, arrangement, null, producerIds,
                "DEFLECTION.PRODUCER_REQUIRED", "Current ULS/final-bar Figure 4 factors and an eligible support screen are required.", "uls/final_bars/context");
        }
        else
        {
            var governing = factors.OrderByDescending(item => beam.Context.EffectiveSpanMm / (item.Factor * EffectiveDepth(arrangement, item.Face))).First();
            result = Serviceability.CheckDeflection(new DeflectionCheckRequest(profileId,
                DeflectionMethod.SpanDepthScreening,
                new DeflectionScreeningBasis(beam.Context.EffectiveSpanMm,
                    EffectiveDepth(arrangement, governing.Face), support.Value, governing.Factor, 1, 1,
                    "IS 456:2000 23.2.1", "IS 456:2000 Figure 4 conservative lower envelope")));
        }
        derivations.Add(BaselineEvidence.Pack(result));
        checks.Add(new BaselineCheckEvidence("deflection", CheckScope.Span, beam.PhysicalSpanId,
            uls.Select(row => row.RowId).ToArray(), BaselineEvidence.Pack(result)));
    }

    private static void EvaluateCrackRow(BoundBaselineBeam beam, BaselineArrangement arrangement, string profileId,
        BoundBaselineActionRow row, List<BaselineCheckEvidence> checks, List<ResultEnvelope<JsonElement>> derivations)
    {
        var face = FaceFor(row.M3Knm);
        var duration = row.Role == BaselineSelectionRole.SlsSustained ? ServiceDurationBasis.LongTerm : ServiceDurationBasis.ShortTerm;
        var section = BaselineServiceability.AnnexFServiceSection(new AnnexFServiceSectionRequest(profileId,
            beam.MemberId, row.StationId, row.RowId, arrangement.RevisionId, beam.WidthMm, beam.DepthMm,
            beam.ConcreteStrengthNPerMm2, beam.SteelModulusNPerMm2, beam.SteelYieldStrengthNPerMm2, row.M3Knm, face,
            arrangement.Bars, duration, ServiceRevision));
        derivations.Add(BaselineEvidence.Pack(section));

        ResultEnvelope<CrackWidthCheckOutput> leaf;
        var leafAlreadyRecorded = false;
        var producerIds = new List<string> { section.ResultId };
        if (!BaselineEvidence.Qualified(section) || section.Outputs is null ||
            !Enum.TryParse<ExposureClass>(beam.Context.Exposure, true, out var exposure))
        {
            leaf = Missing<CrackWidthCheckOutput>(Serviceability.CrackWidthCheckOperation, profileId, beam, arrangement, row.RowId, producerIds,
                "CRACK.PRODUCER_REQUIRED", "A current Annex F service section and a recognized exposure classification are required.", "service_section/exposure");
        }
        else
        {
            var points = CriticalSurfacePoints(arrangement.Bars.Where(bar => bar.Face == face), beam.WidthMm, beam.DepthMm, face).ToArray();
            var calculations = points.Select(point => Serviceability.CheckCrackWidth(new CrackWidthCheckRequest(profileId,
                beam.MemberId, row.StationId, row.RowId, arrangement.RevisionId, beam.WidthMm, beam.DepthMm,
                section.Outputs.NeutralAxisDepthMm, face, arrangement.Bars, point,
                section.Outputs.ServiceSteelStressNPerMm2, beam.SteelYieldStrengthNPerMm2, beam.SteelModulusNPerMm2,
                section.Outputs.MeanSurfaceStrain, new CrackWidthLimitRequest(profileId, exposure, beam.Context.CrackingHarmful)))).ToArray();
            foreach (var calculation in calculations)
            {
                derivations.Add(BaselineEvidence.Pack(calculation));
                producerIds.Add(calculation.ResultId);
            }
            leaf = calculations.Length == 0 || calculations.Any(result => !Evaluated(result))
                ? Missing<CrackWidthCheckOutput>(Serviceability.CrackWidthCheckOperation, profileId, beam, arrangement, row.RowId, producerIds,
                    "CRACK.SURFACE_POINTS_INCOMPLETE", "Every physical tension-face critical surface point must produce current crack evidence.", "surface_points")
                : calculations.OrderByDescending(result => result.Outputs!.Utilization).First();
            leafAlreadyRecorded = calculations.Contains(leaf);
        }
        if (!leafAlreadyRecorded)
            derivations.Add(BaselineEvidence.Pack(leaf));
        checks.Add(new BaselineCheckEvidence("crack", CheckScope.Face, row.RowId,
            [row.RowId], BaselineEvidence.Pack(leaf)));
    }

    public static IReadOnlyList<double> CriticalSurfacePoints(IEnumerable<BarCoordinate> bars, double width, double depth, Face face)
    {
        var tension = bars.OrderBy(bar => bar.XFromLeftMm).ToArray();
        if (tension.Length == 0 || tension.Any(bar => Math.Abs(bar.DiameterMm - tension[0].DiameterMm) > 1e-9))
            return [];
        var surfaceY = face == Face.Bottom ? depth : 0;
        var points = new HashSet<double> { 0, width };
        for (var i = 0; i < tension.Length; i++)
            for (var j = i + 1; j < tension.Length; j++)
            {
                var left = tension[i];
                var right = tension[j];
                var dx = right.XFromLeftMm - left.XFromLeftMm;
                if (Math.Abs(dx) < 1e-12)
                    continue;
                var crossing = (right.XFromLeftMm * right.XFromLeftMm + Math.Pow(right.YFromTopMm - surfaceY, 2) -
                    left.XFromLeftMm * left.XFromLeftMm - Math.Pow(left.YFromTopMm - surfaceY, 2)) / (2 * dx);
                if (crossing > 0 && crossing < width)
                    points.Add(crossing);
            }
        return points.OrderBy(point => point).ToArray();
    }

    private static Face FaceFor(double signedMoment) => signedMoment < 0 ? Face.Top : Face.Bottom;
    private static double EffectiveDepth(BaselineArrangement arrangement, Face face) =>
        face == Face.Bottom ? arrangement.BottomEffectiveDepthMm : arrangement.TopEffectiveDepthMm;
    private static double Area(BarCoordinate bar) => Math.PI * bar.DiameterMm * bar.DiameterMm / 4;
    private static SupportCondition? ToSupportCondition(BaselineSupportCondition support) => support switch
    {
        BaselineSupportCondition.SimplySupported => SupportCondition.SimplySupported,
        BaselineSupportCondition.Continuous => SupportCondition.Continuous,
        _ => null
    };
    private static bool Evaluated<T>(ResultEnvelope<T> result) => result.Execution == ExecutionState.Completed &&
        result.Applicability == ApplicabilityState.Applicable && result.Completeness == CompletenessState.CompleteForScope &&
        result.Freshness == FreshnessState.Current && result.Outputs is not null;
    private static ResultEnvelope<T> Missing<T>(string operation, string profileId, BoundBaselineBeam beam,
        BaselineArrangement arrangement, string? actionRowId, IReadOnlyList<string> dependencies, string code, string message, string field) =>
        ResultFactory.NotEvaluated<T>(operation, new Dictionary<string, EffectiveValue>
        {
            ["profile_id"] = new(profileId, Dependencies: dependencies),
            ["effective_input_id"] = new(beam.EffectiveInputId, Dependencies: dependencies),
            ["reinforcement_revision_id"] = new(arrangement.RevisionId, Dependencies: dependencies),
            ["service_action_row_id"] = new(actionRowId, Dependencies: dependencies)
        },
            new Provenance(ServiceRevision, "is456-baseline-service-checks-wp11-v1", ["WP11 baseline service-check dependency mapping"]),
            new Diagnostic(code, "error", message, operation, field, "is456-baseline-service-checks", "Supply current bounded serviceability evidence."));
}
