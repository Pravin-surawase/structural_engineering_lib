using StructuralEngineering.Contracts;

namespace StructuralEngineering.Analysis;

/// <summary>Host-free source units and dependency qualification; does not evaluate a member design.</summary>
public static class EtabsSourceQualification
{
    public const string SchemaVersion = "structural.etabs_source_facts/v1";
    public const int MaximumFrames = 20;
    public const int MaximumRoots = 32;
    public const int MaximumNodes = 500;
    public const int MaximumTerms = 500;

    public static void ValidateScope(EtabsSourceScope scope)
    {
        ArgumentNullException.ThrowIfNull(scope);
        if (scope.FrameNames is null || scope.CaseNames is null || scope.CombinationNames is null ||
            scope.FrameNames.Count is < 1 or > MaximumFrames ||
            scope.CaseNames.Count + scope.CombinationNames.Count is < 1 or > MaximumRoots ||
            new[] { scope.FrameNames, scope.CaseNames, scope.CombinationNames }.Any(names =>
                names.Any(string.IsNullOrWhiteSpace) || names.Distinct(StringComparer.Ordinal).Count() != names.Count))
            throw new ArgumentException("Source scope requires 1..20 unique frames and 1..32 unique case/combination roots.", nameof(scope));
    }

    public static EtabsSourceUnitBasis Units(int present, int database) => present switch
    {
        6 => new(present, database, "m", "kN", 1000, 0.001),
        9 => new(present, database, "mm", "N", 1, 1),
        _ => throw new ArgumentException("Source qualification admits only native kN-m-C (6) or N-mm-C (9) API units.")
    };

    public static double ConvertFinite(double value, double factor)
    {
        var converted = value * factor;
        return double.IsFinite(value) && double.IsFinite(converted) ? converted :
            throw new ArgumentException("A source dimension is not finite after conversion.");
    }

    public static IReadOnlyList<EtabsSourceLoadClosure> ResolveLoads(EtabsSourceScope scope,
        IReadOnlyList<EtabsSourceLoadNode> nodes)
    {
        ValidateScope(scope);
        if (nodes.Count > MaximumNodes || nodes.Any(n => n.Terms.Count > MaximumTerms))
            throw new ArgumentException("Source dependency graph exceeds its admission bound.");
        var byId = nodes.ToDictionary(n => Id(n.Kind, n.Name), StringComparer.Ordinal);
        return scope.CaseNames.Select(name => Resolve("case", name))
            .Concat(scope.CombinationNames.Select(name => Resolve("combination", name))).ToArray();

        EtabsSourceLoadClosure Resolve(string kind, string name)
        {
            var visited = new HashSet<string>(StringComparer.Ordinal);
            var active = new HashSet<string>(StringComparer.Ordinal);
            var restrictions = new List<EtabsSourceRestriction>();
            Visit(kind, name);
            if (byId.TryGetValue(Id(kind, name), out var root) && root.SelectedForOutput != true)
                restrictions.Add(new("SOURCE.SELECTION_UNAVAILABLE", Id(kind, name), "The requested root is not proved selected for output."));
            return new(kind, name, restrictions.Count == 0 ? "complete_static_source" :
                restrictions.Any(x => x.Code.Contains("UNAVAILABLE", StringComparison.Ordinal)) ? "unavailable" : "unsupported",
                visited.Order(StringComparer.Ordinal).ToArray(), restrictions.Distinct().ToArray());

            void Visit(string nodeKind, string nodeName)
            {
                var id = Id(nodeKind, nodeName);
                if (active.Contains(id)) { restrictions.Add(new("SOURCE.DEPENDENCY_CYCLE", id, "A dependency cycle prevents a complete source closure.")); return; }
                if (!visited.Add(id)) return;
                if (!byId.TryGetValue(id, out var node)) { restrictions.Add(new("SOURCE.DEPENDENCY_UNAVAILABLE", id, "A referenced source dependency was not acquired.")); return; }
                restrictions.AddRange(node.Restrictions);
                if (node.Kind == "case")
                {
                    if (node.ProviderType != 1) restrictions.Add(new("SOURCE.CASE_UNSUPPORTED", id, "Only linear-static case definitions are qualified by this source profile."));
                    if (node.CaseStatus != 4) restrictions.Add(new("SOURCE.RESULTS_UNAVAILABLE", id, "The selected dependency has no finished analysis status."));
                    if (node.ProviderType == 1 && node.InitialCase is not ("" or "None")) restrictions.Add(new("SOURCE.INITIAL_CASE_UNSUPPORTED", id, "Initial-case state is retained and is not qualified as zero initial conditions."));
                }
                else if (node.Kind == "combination" && node.ProviderType != 0)
                    restrictions.Add(new("SOURCE.COMBINATION_UNSUPPORTED", id, "Only linear-additive combinations are qualified for this static closure."));
                else if (node.Kind is not ("case" or "combination" or "pattern"))
                    restrictions.Add(new("SOURCE.LOAD_KIND_UNSUPPORTED", id, "This load dependency kind is retained but not qualified."));
                if ((node.Kind == "case" && node.ProviderType == 1 || node.Kind == "combination" && node.ProviderType == 0) && node.Terms.Count == 0)
                    restrictions.Add(new("SOURCE.DEFINITION_UNAVAILABLE", id, "No complete load terms were acquired."));
                active.Add(id);
                foreach (var term in node.Terms)
                {
                    if (!double.IsFinite(term.Factor)) restrictions.Add(new("SOURCE.FACTOR_UNAVAILABLE", id, "A load factor is not finite."));
                    Visit(term.Kind, term.Name);
                }
                if (node.Kind == "case" && !string.IsNullOrWhiteSpace(node.InitialCase) && node.InitialCase != "None")
                    Visit("case", node.InitialCase);
                active.Remove(id);
            }
        }
    }

    public static string Id(string kind, string name) => kind + ":" + name;
}
