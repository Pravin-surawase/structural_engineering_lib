using StructAutomate.Contracts;
using StructAutomate.Engineering;

namespace StructAutomate.Application;

public static class CandidateRanker
{
    // Ranks already evaluated discrete candidates for one fixed analysis revision; no ETABS mutation.
    public static CandidateRankingResult Rank(CandidateRankingRequest request)
    {
        ArgumentNullException.ThrowIfNull(request);
        Require.Version(request.SchemaVersion);
        Require.Text(request.AnalysisRevision, "analysisRevision");
        ArgumentNullException.ThrowIfNull(request.RequiredCheckIds);
        ArgumentNullException.ThrowIfNull(request.DomainCandidateIds);
        ArgumentNullException.ThrowIfNull(request.Candidates);
        Require.That(request.RequiredCheckIds.Count > 0, "requiredCheckIds", "Declare the required engineering and construction checks.");
        Require.That(request.DomainCandidateIds.Count > 0, "domainCandidateIds", "Declare the finite search domain.");
        Require.Unique(request.RequiredCheckIds, "requiredCheckIds");
        Require.Unique(request.DomainCandidateIds, "domainCandidateIds");
        Require.Unique(request.Candidates.Select(c => c.Id), "candidates.id");
        var domain = request.DomainCandidateIds.ToHashSet(StringComparer.Ordinal);
        var feasible = new List<RankedCandidate>();
        var infeasible = new List<string>();
        var resolved = new HashSet<string>(StringComparer.Ordinal);
        foreach (var candidate in request.Candidates)
        {
            Require.That(domain.Contains(candidate.Id), "candidates.id", "Candidate is absent from the declared domain.");
            Require.That(candidate.AnalysisRevision == request.AnalysisRevision, $"candidates.{candidate.Id}.analysisRevision", "Use results from the selected analysis revision.");
            Require.That(candidate.DefinitionSha256 is { Length: 64 } sha && sha.All(Uri.IsHexDigit), $"candidates.{candidate.Id}.definitionSha256", "Supply the candidate definition SHA-256.");
            Require.Finite(candidate.ObjectiveValue, $"candidates.{candidate.Id}.objectiveValue");
            ArgumentNullException.ThrowIfNull(candidate.Checks);
            Require.Unique(candidate.Checks.Select(c => c.CheckId), $"candidates.{candidate.Id}.checks");
            foreach (var check in candidate.Checks)
            {
                Require.That(Enum.IsDefined(check.Outcome), $"checks.{check.CheckId}.outcome", "Select a declared check outcome.");
                Require.Text(check.Basis, $"checks.{check.CheckId}.basis");
            }
            var checks = candidate.Checks.ToDictionary(c => c.CheckId, StringComparer.Ordinal);
            if (request.RequiredCheckIds.Any(id => !checks.ContainsKey(id) || checks[id].Outcome is CheckOutcome.NotEvaluated or CheckOutcome.NotApplicable)) continue;
            resolved.Add(candidate.Id);
            // A failed additional check is also disqualifying; callers cannot hide it by omitting its ID.
            if (candidate.Checks.Any(c => c.Outcome == CheckOutcome.Fail)) infeasible.Add(candidate.Id);
            else feasible.Add(new(candidate.Id, candidate.ObjectiveValue, candidate.DefinitionSha256));
        }
        var ordered = feasible.OrderBy(c => c.ObjectiveValue).ThenBy(c => c.Id, StringComparer.Ordinal).ToArray();
        var unevaluated = domain.Except(resolved).Order(StringComparer.Ordinal).ToArray();
        return new(ordered, infeasible.Order(StringComparer.Ordinal).ToArray(), unevaluated, unevaluated.Length == 0, ordered.FirstOrDefault()?.Id);
    }
}
