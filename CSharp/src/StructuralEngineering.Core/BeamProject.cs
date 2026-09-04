using StructuralEngineering.Contracts;

namespace StructuralEngineering.Core;

public static class BeamProjectOperations
{
    public const string Operation = "structural.beam_project.create/v1";

    private static readonly Provenance Source = new(
        "project-basis-wp06-v1",
        "structural-beam-project-wp06-v1",
        [
            "PF4 semantic identity and effective-input rules",
            "PF5 AO14 versioned beam project contract"
        ]);

    public static ResultEnvelope<BeamProject> Create(BeamProjectRequest request)
    {
        var catalogues = request.CatalogueRevisions ?? [];
        var normalizedRequest = request with { CatalogueRevisions = catalogues };
        var inputs = ResultFactory.Effective(("request", normalizedRequest));

        if (!AllText(
                request.Project.ProjectId,
                request.Project.Name,
                request.Project.RevisionId,
                request.Profile.ProfileId,
                request.Profile.RevisionId,
                request.Profile.DesignCode))
        {
            return Reject(
                inputs,
                "PROJECT.IDENTITY",
                "Project and profile identities, names, revisions, and design code are required.",
                "project,profile",
                "Supply immutable project and profile revision identities.");
        }

        if (request.UnitBasis != new StructuralUnitBasis("mm", "N", "Nmm", "N/mm2"))
        {
            return Reject(
                inputs,
                "UNITS.UNSUPPORTED",
                "WP06 requires the canonical mm, N, Nmm, and N/mm2 unit basis.",
                "unit_basis",
                "Normalize values at the adapter boundary before creating the project.");
        }

        if (!Enum.IsDefined(request.Profile.SeismicDesignProfile))
        {
            return Reject(
                inputs,
                "PROFILE.SEISMIC",
                "The design profile requires an explicit supported seismic applicability.",
                "profile.seismic_design_profile",
                "Select ordinary_is456 or is13920_2016.");
        }

        if (request.CodeDataRevisions.Count == 0 ||
            !HasUniqueText(request.CodeDataRevisions, item => item.BindingId))
        {
            return Reject(
                inputs,
                "REVISION.CODE_DATA",
                "Code-data bindings are required and their binding ids must be unique.",
                "code_data_revisions",
                "Supply one identified current revision per code-data family.");
        }

        var allRevisions = request.CodeDataRevisions.Concat(catalogues).ToArray();
        if (allRevisions.Any(item =>
                !Text(item.RevisionId) || !Text(item.SourceReference)) ||
            !HasUniqueText(allRevisions, item => item.BindingId))
        {
            return Reject(
                inputs,
                "REVISION.INVALID",
                "Every code-data and catalogue binding requires a unique id, revision, and source reference.",
                "code_data_revisions,catalogue_revisions",
                "Correct duplicate or incomplete revision bindings.");
        }

        var rules = request.Profile.CheckRules;
        if (rules.Count == 0 || !HasUniqueText(rules, item => item.RuleId))
        {
            return Reject(
                inputs,
                "PROFILE.CHECK_RULES",
                "At least one uniquely identified required-check rule is needed.",
                "profile.check_rules",
                "Declare each required operation and scope once.");
        }

        if (rules.Any(item => item.RuleId.Contains('@', StringComparison.Ordinal)))
        {
            return Reject(
                inputs,
                "PROFILE.RULE_ID_INVALID",
                "Check-rule ids cannot contain the leaf-id separator '@'.",
                "profile.check_rules",
                "Use stable rule ids without '@'.");
        }

        var codeBindingIds = request.CodeDataRevisions
            .Select(item => item.BindingId)
            .ToHashSet(StringComparer.Ordinal);
        if (rules.Any(item =>
                !Text(item.OperationSemanticId) ||
                !Text(item.SourceReference) ||
                !Enum.IsDefined(item.Scope) ||
                item.ExpectedApplicability is not (
                    ApplicabilityState.Applicable or ApplicabilityState.NotApplicable) ||
                item.CodeDataBindingId is not null &&
                !codeBindingIds.Contains(item.CodeDataBindingId)))
        {
            return Reject(
                inputs,
                "PROFILE.CHECK_RULE_INVALID",
                "Each check rule needs an operation, scope, expected applicability, source, and valid code-data binding.",
                "profile.check_rules",
                "Correct the check-rule operation and revision references.");
        }

        if (rules
            .Select(item => (item.OperationSemanticId, item.Scope))
            .Distinct()
            .Count() != rules.Count)
        {
            return Reject(
                inputs,
                "PROFILE.CHECK_RULE_CONFLICT",
                "Two rules define the same operation and scope.",
                "profile.check_rules",
                "Remove the conflicting project default.");
        }

        var seismicRules = rules
            .Where(item => item.OperationSemanticId ==
                "is456.beam.seismic_detailing.check/v1")
            .ToArray();
        var expectedSeismic = request.Profile.SeismicDesignProfile ==
            SeismicDesignProfile.OrdinaryIs456
                ? ApplicabilityState.NotApplicable
                : ApplicabilityState.Applicable;
        if (seismicRules.Length != 1 ||
            seismicRules[0].ExpectedApplicability != expectedSeismic)
        {
            return Reject(
                inputs,
                "PROFILE.SEISMIC_CONFLICT",
                "The seismic check rule must match the selected seismic design profile.",
                "profile.check_rules",
                "Declare one seismic rule with the profile-resolved applicability.");
        }

        var criteria = request.Profile.Criteria;
        if (criteria.Count == 0 ||
            !HasUniqueText(criteria, item => item.CriterionId) ||
            criteria.Any(item =>
                !double.IsFinite(item.Value) ||
                !Text(item.Unit) ||
                !Text(item.SourceReference)))
        {
            return Reject(
                inputs,
                "PROFILE.CRITERIA",
                "Design criteria require unique ids, finite values, units, and sources.",
                "profile.criteria",
                "Resolve conflicting or incomplete design criteria.");
        }

        var output = new BeamProject(
            ResultFactory.SemanticId("beam_project_basis_id", normalizedRequest),
            request.Project,
            request.UnitBasis,
            request.CodeDataRevisions,
            catalogues,
            request.Profile);
        return ResultFactory.Completed(Operation, inputs, output, Source);
    }

    private static ResultEnvelope<BeamProject> Reject(
        IReadOnlyDictionary<string, EffectiveValue> inputs,
        string code,
        string message,
        string field,
        string remediation) =>
        ResultFactory.Rejected<BeamProject>(
            Operation,
            inputs,
            Source,
            new Diagnostic(
                code,
                "error",
                message,
                Operation,
                field,
                "beam-project",
                remediation));

    private static bool Text(string? value) => !string.IsNullOrWhiteSpace(value);

    private static bool AllText(params string?[] values) => values.All(Text);

    private static bool HasUniqueText<T>(
        IEnumerable<T> values,
        Func<T, string?> selector)
    {
        var selected = values.Select(selector).ToArray();
        return selected.All(Text) &&
            selected.Distinct(StringComparer.Ordinal).Count() == selected.Length;
    }
}
