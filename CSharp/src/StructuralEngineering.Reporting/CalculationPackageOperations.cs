using System.Globalization;
using StructuralEngineering.Contracts;
using StructuralEngineering.Core;

namespace StructuralEngineering.Reporting;

public static class CalculationPackageOperations
{
    public const string Operation = "structural.calculation_package.create/v1";

    private static readonly Provenance Source = new(
        "calculation-package-wp07-v1",
        "structural-calculation-package-wp07-v1",
        [
            "PF5 AO24 calculation-package contract",
            "PF7 AR24 reproducible leaf, identity, drawing, and human-action evidence"
        ]);

    public static ResultBinding Bind<T>(ResultEnvelope<T> result)
    {
        if (result.Outputs is null)
        {
            throw new ArgumentException(
                "Only a result with a typed output can be bound.", nameof(result));
        }
        return new ResultBinding(
            result.OperationSemanticId,
            result.ResultId,
            result.NormalizedInputId,
            result.CalculationId,
            result.Execution,
            result.Applicability,
            result.Engineering,
            result.Completeness,
            result.Freshness,
            ResultFactory.SemanticId("output_payload_id", result.Outputs));
    }

    public static ResultEnvelope<CalculationPackageOutput> Create(
        CalculationPackageRequest request)
    {
        var inputs = ResultFactory.Effective(("request", request));
        var metadata = request.Metadata;
        var profile = request.PackageProfile;
        var identityValues = new[]
        {
            metadata.ProjectId,
            metadata.ProjectName,
            metadata.ProjectRevisionId,
            metadata.MemberId,
            metadata.PackageRevisionId,
            metadata.EngineBuild,
            metadata.IssuedAtUtc,
            profile.ProfileId,
            profile.RevisionId,
            profile.TemplateId
        };
        if (identityValues.Any(value => !Text(value)) ||
            metadata.DatasetRevisionIds.Count == 0 ||
            metadata.DatasetRevisionIds.Any(value => !Text(value)) ||
            !Timestamp(metadata.IssuedAtUtc))
        {
            return Reject(inputs, "PACKAGE.METADATA",
                "Complete project, member, engine, dataset, and issue-time metadata are required.",
                "metadata");
        }

        if (profile.RequiredLeafIds.Count == 0 ||
            profile.RequiredSectionIds.Count == 0 ||
            HasDuplicates(profile.RequiredLeafIds) ||
            HasDuplicates(profile.RequiredSectionIds) ||
            profile.RequiredLeafIds.Concat(profile.RequiredSectionIds)
                .Any(value => !Text(value)))
        {
            return Reject(inputs, "PACKAGE.PROFILE",
                "The package profile requires unique leaf and section identities.",
                "package_profile");
        }

        var bindings = new List<ResultBinding>
        {
            request.MemberBinding,
            request.ScheduleBinding,
            request.BbsBinding,
            request.QuantityBinding
        };
        if (request.Cost is null && request.CostBinding is not null)
        {
            return Reject(inputs, "PACKAGE.COST_BINDING",
                "A cost binding cannot be supplied without a cost result.",
                "cost_binding");
        }
        if (request.Cost is not null && request.CostBinding is null)
        {
            return Reject(inputs, "PACKAGE.COST_BINDING",
                "A supplied cost result requires its semantic binding.",
                "cost_binding");
        }
        if (request.CostBinding is not null)
        {
            bindings.Add(request.CostBinding);
        }

        var expectedOperations = new List<string>
        {
            "is456.beam_member.design/v1",
            "structural.reinforcement_paths.resolve/v1",
            "structural.bbs.create/v1",
            "structural.construction_quantities.calculate/v1"
        };
        if (request.Cost is not null)
        {
            expectedOperations.Add("structural.construction_cost.estimate/v1");
        }
        if (bindings.Any(binding => !BindingValid(binding)) ||
            !bindings.Select(binding => binding.OperationSemanticId)
                .SequenceEqual(expectedOperations))
        {
            return Reject(inputs, "PACKAGE.BINDING",
                "Every dependency requires its exact operation and semantic result binding.",
                "dependency_bindings");
        }

        var payloads = new List<object>
        {
            request.MemberResult,
            request.Schedule,
            request.Bbs,
            request.Quantities
        };
        if (request.Cost is not null)
        {
            payloads.Add(request.Cost);
        }
        if (bindings.Where((binding, index) => binding.OutputPayloadId !=
            ResultFactory.SemanticId("output_payload_id", payloads[index])).Any())
        {
            return Reject(inputs, "PACKAGE.PAYLOAD_BINDING",
                "A dependency binding does not identify its supplied output payload.",
                "dependency_bindings");
        }

        var member = request.MemberResult;
        var schedule = request.Schedule;
        var bbs = request.Bbs;
        var quantities = request.Quantities;
        var identityConflict =
            metadata.MemberId != member.MemberId ||
            schedule.MemberId != member.MemberId ||
            bbs.MemberId != member.MemberId ||
            quantities.MemberId != member.MemberId ||
            schedule.ProjectBasisId != member.ProjectBasisId ||
            bbs.ProjectBasisId != member.ProjectBasisId ||
            quantities.ProjectBasisId != member.ProjectBasisId ||
            bbs.DetailRevisionId != schedule.DetailRevisionId ||
            quantities.DetailRevisionId != schedule.DetailRevisionId ||
            bbs.ScheduleResultId != request.ScheduleBinding.ResultId ||
            quantities.BbsResultId != request.BbsBinding.ResultId ||
            request.Cost is not null &&
            (request.Cost.MemberId != member.MemberId ||
             request.Cost.ProjectBasisId != member.ProjectBasisId ||
             request.Cost.DetailRevisionId != schedule.DetailRevisionId ||
             request.Cost.QuantityResultId != request.QuantityBinding.ResultId);
        if (identityConflict)
        {
            return Reject(inputs, "PACKAGE.IDENTITY_CONFLICT",
                "Package dependencies must describe one project, member, detail, and result chain.",
                "request");
        }

        var expectedLeafIds = member.ExpectedLeaves
            .Select(item => item.LeafId)
            .ToArray();
        if (!profile.RequiredLeafIds.ToHashSet(StringComparer.Ordinal)
            .SetEquals(expectedLeafIds))
        {
            return Reject(inputs, "PACKAGE.LEAF_PROFILE",
                "The package profile must retain the complete member leaf set.",
                "package_profile.required_leaf_ids");
        }
        if (HasDuplicates(member.LeafQualifications.Select(
                item => item.Expectation.LeafId)) ||
            !member.LeafQualifications.Select(item => item.Expectation.LeafId)
                .ToHashSet(StringComparer.Ordinal).SetEquals(expectedLeafIds))
        {
            return Reject(inputs, "PACKAGE.LEAF_SET",
                "Member leaf qualifications do not match the expected leaf set.",
                "member_result.leaf_qualifications");
        }

        var traceIds = request.Traces.Select(item => item.TraceId).ToArray();
        var traceLeafIds = request.Traces.Select(item => item.LeafId).ToArray();
        if (HasDuplicates(traceIds) ||
            request.Traces.Count != expectedLeafIds.Length ||
            !traceLeafIds.ToHashSet(StringComparer.Ordinal).SetEquals(expectedLeafIds) ||
            request.Traces.Any(item =>
                !Text(item.TraceId) || !Text(item.LeafId) ||
                !Text(item.RuleReference) || !Text(item.FormulaReference) ||
                !Text(item.NormalizedSubstitution)))
        {
            return Reject(inputs, "PACKAGE.TRACE",
                "Every required leaf needs one unique rule, formula, and substitution trace.",
                "traces");
        }

        if (request.Assumptions.Count == 0 ||
            request.Assumptions.Any(value => !Text(value)) ||
            request.Limitations.Any(value => !Text(value)))
        {
            return Reject(inputs, "PACKAGE.NARRATIVE",
                "At least one assumption and only nonblank limitations are required.",
                "assumptions,limitations");
        }

        var drawingIds = request.Drawings.Select(item => item.ViewId).ToArray();
        var datumIds = request.Drawings.SelectMany(item => item.Data)
            .Select(item => item.DatumId).ToArray();
        if (request.Drawings.Count == 0 ||
            HasDuplicates(drawingIds) || HasDuplicates(datumIds) ||
            request.Drawings.Any(view =>
                !Text(view.ViewId) || !Text(view.Kind) ||
                !Text(view.DetailRevisionId) ||
                view.DetailRevisionId != schedule.DetailRevisionId ||
                view.Data.Count == 0 ||
                view.Data.Any(datum =>
                    !Text(datum.DatumId) || !Text(datum.SourceIdentity) ||
                    !Text(datum.Label) || !Text(datum.Value))))
        {
            return Reject(inputs, "PACKAGE.DRAWING",
                "Drawing views require unique identities, current detail revision, and sourced data.",
                "drawings");
        }

        var actions = request.HumanActions ?? [];
        var dependencyIds = bindings.Select(item => item.ResultId)
            .ToHashSet(StringComparer.Ordinal);
        if (HasDuplicates(actions.Select(item => item.ActionId)) ||
            actions.Any(item =>
                !Text(item.ActionId) || !Text(item.ActorId) ||
                !Text(item.ActorDisplayName) || !Text(item.ProfessionalRole) ||
                !Text(item.RecordedAtUtc) || !Text(item.ScopeId) ||
                !Text(item.BoundResultId) || !Enum.IsDefined(item.Action) ||
                !Timestamp(item.RecordedAtUtc) ||
                !dependencyIds.Contains(item.BoundResultId)))
        {
            return Reject(inputs, "PACKAGE.HUMAN_ACTION",
                "Human actions require a real actor, time, scope, and dependency identity.",
                "human_actions");
        }

        var qualifications = member.LeafQualifications.ToDictionary(
            item => item.Expectation.LeafId, StringComparer.Ordinal);
        var leaves = profile.RequiredLeafIds.Select(leafId =>
        {
            var qualification = qualifications[leafId];
            var evidence = qualification.Evidence;
            return new PackageLeaf(
                leafId,
                qualification.Expectation.OperationSemanticId,
                evidence?.ResultId,
                evidence?.RequiredValue,
                evidence?.SuppliedValue,
                evidence?.SelectedValue,
                evidence?.Unit,
                evidence?.GoverningUtilization,
                member.GoverningLeafId == leafId,
                qualification.Qualified,
                qualification.ReasonCodes);
        }).ToArray();
        var traces = request.Traces.ToDictionary(
            item => item.LeafId, StringComparer.Ordinal);
        foreach (var leaf in leaves)
        {
            var trace = traces[leaf.LeafId];
            if (trace.RequiredValue != leaf.RequiredValue ||
                trace.ProvidedValue != leaf.ProvidedValue ||
                trace.SelectedValue != leaf.SelectedValue ||
                trace.Unit != leaf.Unit ||
                trace.Utilization != leaf.Utilization ||
                trace.Governing != leaf.Governing)
            {
                return Reject(inputs, "PACKAGE.TRACE_VALUE",
                    "Calculation traces must reproduce the exact member leaf evidence.",
                    $"traces[{leaf.LeafId}]");
            }
        }

        var current = member.Qualified &&
            bindings.All(BindingCurrent) &&
            leaves.All(item => item.Qualified);
        var memberActions = actions
            .Where(item => item.ScopeId == metadata.MemberId &&
                item.BoundResultId == request.MemberBinding.ResultId)
            .OrderBy(item => ParseTimestamp(item.RecordedAtUtc))
            .ThenBy(item => item.ActionId, StringComparer.Ordinal)
            .ToArray();
        var activeApproval = current && memberActions.Length > 0 &&
            memberActions[^1].Action == HumanActionKind.Approved;
        var sections = profile.RequiredSectionIds.Select(sectionId =>
            new RenderSection(
                sectionId,
                bindings.Select(item => item.ResultId).ToArray(),
                SectionPayloadKind(sectionId))).ToArray();

        var packagePayload = new Dictionary<string, object?>
        {
            ["metadata"] = metadata,
            ["profile"] = profile,
            ["bindings"] = bindings,
            ["assumptions"] = request.Assumptions,
            ["leaves"] = leaves,
            ["traces"] = request.Traces,
            ["schedule"] = schedule,
            ["bbs"] = bbs,
            ["quantities"] = quantities,
            ["cost"] = request.Cost,
            ["drawings"] = request.Drawings,
            ["limitations"] = request.Limitations,
            ["human_actions"] = actions
        };
        var output = new CalculationPackageOutput(
            ResultFactory.SemanticId("calculation_package_id", packagePayload),
            metadata,
            profile.ProfileId,
            profile.RevisionId,
            bindings,
            request.Assumptions,
            leaves,
            request.Traces,
            member.GoverningLeafId,
            schedule,
            bbs,
            quantities,
            request.Cost,
            request.Drawings,
            sections,
            "structural-calculation-renderer/v1",
            request.Limitations,
            actions,
            current ? "issue_ready" : "draft",
            activeApproval);
        if (current)
        {
            return ResultFactory.Completed(Operation, inputs, output, Source);
        }
        var freshness = bindings.Any(item => item.Freshness == FreshnessState.Stale)
            ? FreshnessState.Stale
            : FreshnessState.Current;
        return ResultFactory.Partial(
            Operation,
            inputs,
            output,
            Source,
            freshness,
            new Diagnostic(
                "PACKAGE.EVIDENCE_INCOMPLETE",
                "error",
                "The package is a draft because required evidence is incomplete or stale.",
                Operation,
                "dependency_bindings,leaves",
                "calculation-package"));
    }

    private static bool BindingValid(ResultBinding binding) =>
        Text(binding.OperationSemanticId) && Text(binding.ResultId) &&
        Text(binding.NormalizedInputId) && Text(binding.CalculationId) &&
        Text(binding.OutputPayloadId) && Enum.IsDefined(binding.Execution) &&
        Enum.IsDefined(binding.Applicability) && Enum.IsDefined(binding.Engineering) &&
        Enum.IsDefined(binding.Completeness) && Enum.IsDefined(binding.Freshness);

    private static bool BindingCurrent(ResultBinding binding) =>
        binding.Execution == ExecutionState.Completed &&
        binding.Applicability == ApplicabilityState.Applicable &&
        binding.Engineering == EngineeringState.Pass &&
        binding.Completeness == CompletenessState.CompleteForScope &&
        binding.Freshness == FreshnessState.Current;

    private static bool Timestamp(string value)
    {
        var timeSeparator = value.IndexOf('T');
        var hasOffset = timeSeparator >= 0 &&
            (value.EndsWith('Z') || value.IndexOf('+', timeSeparator) >= 0 ||
             value.IndexOf('-', timeSeparator) >= 0);
        return hasOffset && DateTimeOffset.TryParse(value,
            CultureInfo.InvariantCulture, DateTimeStyles.None, out _);
    }

    private static DateTimeOffset ParseTimestamp(string value) =>
        DateTimeOffset.Parse(value, CultureInfo.InvariantCulture,
            DateTimeStyles.None).ToUniversalTime();

    private static string SectionPayloadKind(string sectionId) => sectionId switch
    {
        "inputs" => "effective_inputs_and_assumptions",
        "calculations" => "leaf_traces",
        "reinforcement" => "resolved_paths_and_bbs",
        "quantities" => "construction_quantities",
        "cost" => "dated_direct_cost",
        "drawings" => "drawing_views",
        "signatures" => "recorded_human_actions",
        _ => "declared_semantic_section"
    };

    private static bool HasDuplicates(IEnumerable<string> values)
    {
        var items = values.ToArray();
        return items.Distinct(StringComparer.Ordinal).Count() != items.Length;
    }

    private static bool Text(string? value) => !string.IsNullOrWhiteSpace(value);

    private static ResultEnvelope<CalculationPackageOutput> Reject(
        IReadOnlyDictionary<string, EffectiveValue> inputs,
        string code,
        string message,
        string field) => ResultFactory.Rejected<CalculationPackageOutput>(
            Operation,
            inputs,
            Source,
            new Diagnostic(code, "error", message, Operation, field,
                "calculation-package"));
}
