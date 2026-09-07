using StructuralEngineering.Contracts;
using StructuralEngineering.Core;

namespace StructuralEngineering.Codes.IS456;

public static class BaselineStirrupAnchorage
{
    public const string Operation = "is456.beam.stirrup_anchorage.check/v1";
    public const string TemplateId = "ordinary-closed-rectangular-135-hook-6phi-v1";
    private const string Revision = "is456-baseline-stirrup-v1";

    public static ResultEnvelope<BaselineStirrupAnchorageOutput> Check(BaselineStirrupAnchorageRequest request)
    {
        var inputs = ResultFactory.Effective(("request", request));
        var source = Source(request.CodeDataRevisionId);
        if (!Identity(request.ProfileId, request.MemberId, request.ReinforcementRevisionId) || request.CodeDataRevisionId != Revision ||
            !Positive(request.SectionWidthMm, request.SectionDepthMm, request.NominalCoverMm))
            return Rejected(inputs, source, "INPUT.INVALID", "Identity, source revision, section dimensions, and nominal cover are required.", "request");
        if (request.Link is null || request.Bars is not { Count: > 0 })
            return Missing(inputs, source, "LINK_AND_BARS.REQUIRED", "The selected closed link and actual longitudinal bars are required.", "link/bars");
        var link = request.Link;
        if (!link.Closed || !Positive(link.DiameterMm, link.CentreWidthMm, link.CentreDepthMm) ||
            request.Bars.Any(bar => !Identity(bar.BarId) || !Positive(bar.DiameterMm) || !double.IsFinite(bar.XFromLeftMm) || !double.IsFinite(bar.YFromTopMm)))
            return Rejected(inputs, source, "GEOMETRY.INVALID", "A closed link with positive dimensions and actual positioned bars is required.", "link/bars");

        var phi = link.DiameterMm;
        var left = (request.SectionWidthMm - link.CentreWidthMm) / 2;
        var top = (request.SectionDepthMm - link.CentreDepthMm) / 2;
        var right = request.SectionWidthMm - left;
        var bottom = request.SectionDepthMm - top;
        var expected = request.NominalCoverMm + phi / 2;
        var linkCoverOk = Math.Abs(left - expected) <= 1e-6 && Math.Abs(top - expected) <= 1e-6 &&
            Math.Abs(right - (request.SectionWidthMm - expected)) <= 1e-6 && Math.Abs(bottom - (request.SectionDepthMm - expected)) <= 1e-6;
        var radius = 2 * phi;
        var bendCentreX = request.NominalCoverMm + 3 * phi;
        var bendCentreY = request.NominalCoverMm + 3 * phi;
        var tail = 6 * phi;
        var clearance = phi / 2;
        var centrelineRadius = radius + phi / 2;
        var diagonalRadius = centrelineRadius / Math.Sqrt(2);
        var diagonalTail = tail / Math.Sqrt(2);
        // Projected standard closure: both ends wrap the top-left corner bar
        // through 135 degrees and continue on their actual tangent for 6phi.
        // This is a section-fit/anchorage template, not a fabrication BBS.
        var envelopes = new[] { 1d, -1d }.Select(sign =>
        {
            var x = bendCentreX + sign * diagonalRadius;
            var y = bendCentreY - sign * diagonalRadius;
            return new StirrupHookEnvelope(bendCentreX, bendCentreY, x, y,
                x + diagonalTail, y + diagonalTail, clearance, x - clearance,
                x + diagonalTail + clearance, y - clearance, y + diagonalTail + clearance);
        }).ToArray();
        var corners = new[] { (left, top), (right, top), (left, bottom), (right, bottom) }
            .Select(corner => request.Bars.OrderBy(bar => Distance(bar.XFromLeftMm, bar.YFromTopMm, corner.Item1, corner.Item2)).First())
            .DistinctBy(bar => bar.BarId).ToArray();
        var cageClear = request.Bars.All(bar => InsideRoundedCage(bar, left, right, top, bottom, radius, phi));
        var cornerSizeOk = corners.Length == 4 && corners.All(bar => bar.DiameterMm <= 4 * phi + 1e-9);
        var tailClear = envelopes.All(envelope => request.Bars.All(bar =>
            DistanceToSegment(bar.XFromLeftMm, bar.YFromTopMm, envelope.TailStartXFromLeftMm, envelope.TailStartYFromTopMm,
                envelope.TailEndXFromLeftMm, envelope.TailEndYFromTopMm) >= bar.DiameterMm / 2 + clearance - 1e-9)) &&
            envelopes.All(envelope => envelope.MinimumXFromLeftMm >= request.NominalCoverMm &&
                envelope.MaximumXFromLeftMm <= request.SectionWidthMm - request.NominalCoverMm &&
                envelope.MinimumYFromTopMm >= request.NominalCoverMm &&
                envelope.MaximumYFromTopMm <= request.SectionDepthMm - request.NominalCoverMm &&
                InsideRoundedCage(new("hook-end", phi, envelope.TailEndXFromLeftMm,
                    envelope.TailEndYFromTopMm, Face.Top), left, right, top, bottom, radius, phi));
        var passed = linkCoverOk && cageClear && cornerSizeOk && tailClear;
        var diagnostics = new List<Diagnostic>();
        if (!linkCoverOk) diagnostics.Add(Error("LINK.COVER_GEOMETRY", "The selected link centreline does not bind to the declared nominal cover.", "link"));
        if (!cageClear) diagnostics.Add(Error("LINK.CAGE_FIT", "A longitudinal bar does not fit inside the rounded selected-link cage.", "bars"));
        if (!cornerSizeOk) diagnostics.Add(Error("LINK.CORNER_BAR_SIZE", "A corner longitudinal bar exceeds the frozen 4phi standard-template bound.", "bars"));
        if (!tailClear) diagnostics.Add(Error("LINK.HOOK_TAIL_CLEARANCE", "A 135-degree hook tail conflicts with a longitudinal bar or the section cover envelope.", "bars"));
        return ResultFactory.Completed(Operation, inputs,
            new BaselineStirrupAnchorageOutput(TemplateId, link.LinkId, 135, tail, tail, radius,
                corners.Select(bar => bar.BarId).ToArray(), corners.Max(bar => bar.DiameterMm), envelopes, passed), source,
            passed ? EngineeringState.Pass : EngineeringState.Fail, diagnostics.ToArray());
    }

    private static bool InsideRoundedCage(BarCoordinate bar, double left, double right, double top, double bottom, double radius, double phi)
    {
        var clearance = (bar.DiameterMm + phi) / 2;
        if (bar.XFromLeftMm < left + clearance || bar.XFromLeftMm > right - clearance || bar.YFromTopMm < top + clearance || bar.YFromTopMm > bottom - clearance)
            return false;
        var centrelineRadius = radius + phi / 2;
        var qx = Math.Max(0, Math.Max(left + centrelineRadius - bar.XFromLeftMm, bar.XFromLeftMm - right + centrelineRadius));
        var qy = Math.Max(0, Math.Max(top + centrelineRadius - bar.YFromTopMm, bar.YFromTopMm - bottom + centrelineRadius));
        return radius >= bar.DiameterMm / 2 && Math.Sqrt(qx * qx + qy * qy) <= radius - bar.DiameterMm / 2 + 1e-9;
    }
    private static double Distance(double x1, double y1, double x2, double y2) => Math.Sqrt(Math.Pow(x1 - x2, 2) + Math.Pow(y1 - y2, 2));
    private static double DistanceToSegment(double x, double y, double x1, double y1, double x2, double y2)
    {
        var dx = x2 - x1; var dy = y2 - y1; var lengthSquared = dx * dx + dy * dy;
        var t = lengthSquared == 0 ? 0 : Math.Clamp(((x - x1) * dx + (y - y1) * dy) / lengthSquared, 0, 1);
        return Distance(x, y, x1 + t * dx, y1 + t * dy);
    }
    private static bool Positive(params double[] values) => values.All(Validation.Positive);
    private static bool Identity(params string?[] values) => values.All(value => !string.IsNullOrWhiteSpace(value));
    private static Provenance Source(string revision) => new(revision, "is456-baseline-stirrup-anchorage-wp11-v1",
        ["IS 456:2000 26.2.2.4(b) (printed p. 43): 135-degree stirrup bend with tail at least 6phi",
         "Controlled source SHA-256: 6ec8f9033bc521420f2f550123edb6f0f444d9d3b7033a87b1b7ec569c143f8d"]);
    private static Diagnostic Error(string code, string message, string field) => new(code, "error", message, Operation, field, "is456-baseline-stirrup", "Supply a fitting actual standard-link geometry.");
    private static ResultEnvelope<BaselineStirrupAnchorageOutput> Rejected(IReadOnlyDictionary<string, EffectiveValue> inputs, Provenance source, string code, string message, string field) => ResultFactory.Rejected<BaselineStirrupAnchorageOutput>(Operation, inputs, source, Error(code, message, field));
    private static ResultEnvelope<BaselineStirrupAnchorageOutput> Missing(IReadOnlyDictionary<string, EffectiveValue> inputs, Provenance source, string code, string message, string field) => ResultFactory.NotEvaluated<BaselineStirrupAnchorageOutput>(Operation, inputs, source, Error(code, message, field));
}
