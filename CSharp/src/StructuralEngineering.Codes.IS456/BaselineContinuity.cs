using StructuralEngineering.Contracts;
using StructuralEngineering.Core;

namespace StructuralEngineering.Codes.IS456;

public static class BaselineContinuity
{
    public const string CheckOperation = "is456.beam.no_splice_continuity.check/v1";
    private const string AnchorageOperation = "is456.beam.anchorage.check/v1";

    public static ResultEnvelope<BaselineContinuityCheckOutput> Check(BaselineContinuityRequest request)
    {
        var inputs = ResultFactory.Effective(("request", request));
        var source = new Provenance(request.CodeDataRevisionId, "wp11-baseline-continuity-v1",
            ["IS 456:2000 with Amendment 6 (2024); anchorage is evaluated separately", "WP11 construction policy: explicit straight, full-length, unspliced bars only"]);

        if (!ValidIdentity(request) || !Finite(request.PhysicalSpanStartXMm, request.PhysicalSpanEndXMm) || request.PhysicalSpanStartXMm >= request.PhysicalSpanEndXMm)
            return Rejected(inputs, source, "INPUT.INVALID", "Member, revision, and ordered physical-span identities are required.", "request");
        if (request.Bars is not { Count: > 0 } || request.RequiredSourceRows is not { Count: > 0 } || request.RequiredRoles is not { Count: > 0 } || request.Demands is not { Count: > 0 })
            return Missing(inputs, source, "Actual bars, required source rows and roles, and station demands are required.", "bars,required_source_rows,required_roles,demands");
        if (request.AllowedStockLengths is not { Count: > 0 } || request.StockAssignments is not { Count: > 0 } || request.AnchorageCheck is null)
            return Missing(inputs, source, "Stock catalogue, one stock assignment per physical bar, and a separate anchorage result are required.", "allowed_stock_lengths,stock_assignments,anchorage_check");
        if (!UniqueBy(request.RequiredSourceRows, row => row.ActionRowId) || request.RequiredSourceRows.Any(row => !ValidRequiredRow(row, request)) || !UniqueRoles(request.RequiredRoles) || request.RequiredRoles.Any(role => role is not ReinforcementRole.TopLongitudinal and not ReinforcementRole.BottomLongitudinal))
            return Rejected(inputs, source, "DEMAND.IDENTITY", "Required source rows and top/bottom longitudinal roles must be unique and station-bound.", "required_source_rows,required_roles");
        if (!UniqueBy(request.Bars, bar => bar.BarId) || request.Bars.Any(bar => !ValidBar(bar)) || request.Bars.Any(bar => bar.StartStationMm < request.PhysicalSpanStartXMm || bar.EndStationMm > request.PhysicalSpanEndXMm))
            return Rejected(inputs, source, "BAR.IDENTITY_OR_GEOMETRY", "Each physical bar needs a unique identity and valid straight geometry within the physical span.", "bars");
        if (!UniqueBy(request.Demands, demand => $"{demand.ActionRowId}|{demand.StationId}|{demand.Role}") || request.Demands.Any(demand => !ValidDemand(demand, request)))
            return Rejected(inputs, source, "DEMAND.INVALID", "Demand rows require unique action-row/station/role identities, valid stations, and non-negative required steel.", "demands");
        if (!UniqueBy(request.AllowedStockLengths, stock => stock.StockId) || request.AllowedStockLengths.Any(stock => !Text(stock.StockId) || !Positive(stock.LengthMm)))
            return Rejected(inputs, source, "STOCK.CATALOGUE_INVALID", "Allowed stock lengths require unique identities and positive lengths.", "allowed_stock_lengths");
        if (!UniqueBy(request.StockAssignments, assignment => assignment.BarId) || !UniqueBy(request.StockAssignments, assignment => assignment.StockPieceId) || request.StockAssignments.Any(assignment => !Text(assignment.BarId) || !Text(assignment.StockPieceId) || !Text(assignment.StockId)) || request.StockAssignments.Any(assignment => !request.Bars.Any(bar => bar.BarId == assignment.BarId)))
            return Rejected(inputs, source, "STOCK.ASSIGNMENT_INVALID", "Stock assignments need unique physical-bar and stock-piece identities bound to known bars.", "stock_assignments");
        if (request.Bars.Any(bar => !request.StockAssignments.Any(assignment => assignment.BarId == bar.BarId)))
            return Missing(inputs, source, "Every physical bar requires one actual stock-piece assignment.", "stock_assignments");
        if (request.RequiredSourceRows.Any(row => request.RequiredRoles.Any(role => !request.Demands.Any(demand => demand.ActionRowId == row.ActionRowId && demand.StationId == row.StationId && demand.StationXMm == row.StationXMm && demand.Role == role))))
            return Missing(inputs, source, "Every required source row, station, and declared longitudinal role requires a matching demand.", "demands");

        var anchorageQualified = request.AnchorageCheck.Qualifies(AnchorageOperation);
        var barChecks = request.Bars.Select(bar =>
        {
            var fullSpan = bar.StartStationMm == request.PhysicalSpanStartXMm && bar.EndStationMm == request.PhysicalSpanEndXMm;
            return new BaselineContinuityBarCheck(bar.BarId, bar.Role, bar.StartStationMm, bar.EndStationMm, bar.DiameterMm, fullSpan, fullSpan);
        }).ToArray();
        var coverage = request.Demands.Select(demand =>
        {
            var providers = request.Bars.Where(bar => bar.Role == demand.Role && bar.StartStationMm <= demand.StationXMm && bar.EndStationMm >= demand.StationXMm).ToArray();
            var provided = providers.Sum(Area);
            return new BaselineContinuityCoverageCheck(demand.ActionRowId, demand.StationId, demand.StationXMm, demand.Role, demand.RequiredAreaMm2, provided, providers.Select(bar => bar.BarId).ToArray(), provided >= demand.RequiredAreaMm2);
        }).ToArray();
        var stock = request.StockAssignments.Select(assignment =>
        {
            var bar = request.Bars.Single(candidate => candidate.BarId == assignment.BarId);
            var catalogue = request.AllowedStockLengths.SingleOrDefault(candidate => candidate.StockId == assignment.StockId);
            var length = bar.EndStationMm - bar.StartStationMm;
            var exists = catalogue is not null;
            var fits = exists && length <= catalogue!.LengthMm;
            return new BaselineContinuityStockCheck(bar.BarId, assignment.StockPieceId, assignment.StockId, length, catalogue?.LengthMm, exists, fits, exists && fits);
        }).ToArray();
        var passed = anchorageQualified && barChecks.All(check => check.Passed) && coverage.All(check => check.Passed) && stock.All(check => check.Passed);
        var output = new BaselineContinuityCheckOutput(request.MemberId, request.PhysicalSpanId, request.DemandRevisionId, request.ReinforcementRevisionId, request.CatalogueRevisionId, request.AnchorageCheck.ResultId, anchorageQualified, barChecks, coverage, stock, passed);
        var diagnostics = new List<Diagnostic>();
        if (!anchorageQualified) diagnostics.Add(Error("ANCHORAGE.NOT_QUALIFIED", "A separate current, passing anchorage leaf is required.", "anchorage_check"));
        if (barChecks.Any(check => !check.Passed)) diagnostics.Add(Error("BAR.INTERNAL_TERMINATION", "A no-splice continuity bar does not cover the full physical span.", "bars"));
        if (coverage.Any(check => !check.Passed)) diagnostics.Add(Error("STEEL.INSUFFICIENT", "Provided station steel is below the concurrent source-row demand.", "demands"));
        if (stock.Any(check => !check.Passed)) diagnostics.Add(Error("STOCK.NOT_FEASIBLE", "The assigned stock is absent from the catalogue or shorter than the actual straight cut.", "stock_assignments"));
        return ResultFactory.Completed(CheckOperation, inputs, output, source, passed ? EngineeringState.Pass : EngineeringState.Fail, diagnostics.ToArray());
    }

    private static bool ValidIdentity(BaselineContinuityRequest request) => new[] { request.ProfileId, request.MemberId, request.PhysicalSpanId, request.DemandRevisionId, request.ReinforcementRevisionId, request.CatalogueRevisionId, request.CodeDataRevisionId }.All(Text);
    private static bool ValidBar(LongitudinalBarPath bar) => Text(bar.BarId) && Text(bar.BarMark) && (bar.Role is ReinforcementRole.TopLongitudinal or ReinforcementRole.BottomLongitudinal) && Positive(bar.DiameterMm) && bar.Layer >= 1 && Finite(bar.XFromLeftMm, bar.YFromTopMm, bar.StartStationMm, bar.EndStationMm, bar.DesignStressNPerMm2) && bar.StartStationMm < bar.EndStationMm && bar.DesignStressNPerMm2 >= 0 && bar.BundleSize is >= 1 and <= 4;
    private static bool ValidRequiredRow(RequiredConcurrentSourceRow row, BaselineContinuityRequest request) => Text(row.ActionRowId) && Text(row.StationId) && Finite(row.StationXMm) && row.StationXMm >= request.PhysicalSpanStartXMm && row.StationXMm <= request.PhysicalSpanEndXMm;
    private static bool ValidDemand(BaselineContinuityDemand demand, BaselineContinuityRequest request) => Text(demand.ActionRowId) && Text(demand.StationId) && request.RequiredSourceRows.Any(row => row.ActionRowId == demand.ActionRowId && row.StationId == demand.StationId && row.StationXMm == demand.StationXMm) && request.RequiredRoles.Contains(demand.Role) && Finite(demand.StationXMm, demand.RequiredAreaMm2) && demand.RequiredAreaMm2 >= 0;
    private static double Area(LongitudinalBarPath bar) => Math.PI * bar.DiameterMm * bar.DiameterMm / 4;
    private static bool UniqueRoles(IReadOnlyList<ReinforcementRole> values) => values.Distinct().Count() == values.Count;
    private static bool UniqueBy<T>(IReadOnlyList<T> values, Func<T, string> identity) => values.Select(identity).All(Text) && values.Select(identity).Distinct(StringComparer.Ordinal).Count() == values.Count;
    private static bool Text(string? value) => !string.IsNullOrWhiteSpace(value);
    private static bool Positive(double value) => Validation.Positive(value);
    private static bool Finite(params double[] values) => values.All(double.IsFinite);
    private static Diagnostic Error(string code, string message, string field) => new(code, "error", message, CheckOperation, field, "is456-baseline-continuity", "Supply or correct the named continuity evidence.");
    private static ResultEnvelope<BaselineContinuityCheckOutput> Rejected(IReadOnlyDictionary<string, EffectiveValue> inputs, Provenance source, string code, string message, string field) => ResultFactory.Rejected<BaselineContinuityCheckOutput>(CheckOperation, inputs, source, Error(code, message, field));
    private static ResultEnvelope<BaselineContinuityCheckOutput> Missing(IReadOnlyDictionary<string, EffectiveValue> inputs, Provenance source, string message, string field) => ResultFactory.NotEvaluated<BaselineContinuityCheckOutput>(CheckOperation, inputs, source, Error("EVIDENCE.REQUIRED", message, field));
}
