using System.Globalization;
using StructuralEngineering.Contracts;
using StructuralEngineering.Core;

namespace StructuralEngineering.Beam;

public static class BeamReviewResolver
{
    public const string SchemaVersion = "beam-input-ledger/v1";

    public static string ModelBinding(AnalysisSnapshot snapshot) => ResultFactory.SemanticId("review_model", new
    {
        snapshot.Metadata.ProjectId,
        snapshot.Metadata.ModelName,
        identity = snapshot.Metadata.ModelGuid.Value ?? snapshot.SourceIdentity.ModelFileSha256.Value ?? snapshot.SourceIdentity.ModelRevisionId
    });

    public static BeamInputEdit Edit(string key, BeamInputScope scope, string scopeId, string? modelBinding,
        string enteredText, long sequence) => new(ResultFactory.SemanticId("review_edit", new
        { key, scope, scopeId, modelBinding, enteredText, sequence }), key, scope, scopeId, modelBinding, enteredText, sequence);

    /// <summary>Replace a scope's current entry, retaining other scopes and models. Equal-to-default is still an edit.</summary>
    public static IReadOnlyList<BeamInputEdit> ApplyEdit(IReadOnlyList<BeamInputEdit> edits, BeamInputEdit edit) =>
        edits.Where(x => !(x.Key == edit.Key && x.Scope == edit.Scope && x.ScopeId == edit.ScopeId && x.ModelBinding == edit.ModelBinding))
            .Append(edit).OrderBy(x => x.Id, StringComparer.Ordinal).ToArray();

    public static BeamResolvedReview Resolve(AnalysisSnapshot snapshot, IReadOnlyList<string> memberIds,
        BeamReviewPreset preset, BeamInputLedger? saved = null, IReadOnlyList<BeamInputEdit>? edits = null)
    {
        var binding = ModelBinding(snapshot);
        edits ??= saved?.Edits ?? [];
        var fields = new List<BeamEffectiveField>();
        var members = new List<BeamResolvedMember>();
        var points = snapshot.Points.ToDictionary(x => x.PointId, StringComparer.Ordinal);
        var sections = snapshot.Sections.ToDictionary(x => x.SectionId, StringComparer.Ordinal);
        foreach (var id in memberIds.Distinct(StringComparer.Ordinal))
        {
            var member = snapshot.Members.SingleOrDefault(x => x.MemberId == id);
            var section = member is null ? null : sections.GetValueOrDefault(member.SectionId);
            var pi = member is null ? null : points.GetValueOrDefault(member.PointIId);
            var pj = member is null ? null : points.GetValueOrDefault(member.PointJId);
            var length = pi is null || pj is null ? 4000 : Math.Sqrt(Math.Pow(pj.XMm - pi.XMm, 2) + Math.Pow(pj.YMm - pi.YMm, 2) + Math.Pow(pj.ZMm - pi.ZMm, 2));
            if (!double.IsFinite(length) || length <= 0) length = 4000;
            var materialId = section?.MaterialId ?? "missing-material";
            var span = "assumed-span:" + id;
            var defaults = new Dictionary<string, string>(preset.Values, StringComparer.Ordinal)
            {
                ["member.physical_span"] = span,
                ["member.support"] = "SimplySupported",
                ["member.left_face"] = N(Math.Min(500, length / 4)),
                ["member.right_face"] = N(length - Math.Min(500, length / 4)),
                ["member.left_centre"] = "0",
                ["member.right_centre"] = N(length),
                ["member.effective_span"] = N(length),
                ["member.anchor_start"] = "-1000",
                ["member.anchor_end"] = N(length + 1000),
                ["member.restraints"] = "0," + N(length),
                ["member.width"] = N(section?.WidthMm ?? 300),
                ["member.depth"] = N(section?.DepthMm ?? 500)
            };
            defaults["member.horizontal"] = pi is not null && pj is not null && pi.ZMm == pj.ZMm ? "true" : "false";
            defaults["member.top_mapping_normal"] = "true";
            defaults["member.evidence_reference"] = "Provisional support scenario; verify physical support and anchorage space";
            defaults["member.fire_decision"] = "Provisional fire requirement; not a project decision";
            defaults["member.restraint_reference"] = "Provisional end restraints; verify actual restraint locations";
            var values = new Dictionary<string, string>(StringComparer.Ordinal);
            foreach (var definition in BeamReviewFields.All.Where(x => x.Key != "selection.role"))
            {
                var source = definition.Key switch { "member.width" => section?.WidthMm, "member.depth" => section?.DepthMm, _ => null };
                var field = ResolveField(definition, id, materialId, member?.StoryId ?? "", span, source is null ? null : N(source.Value), defaults[definition.Key]);
                fields.Add(field); values.Add(field.Key, field.Value);
                if (field.Key == "member.physical_span") span = field.Value;
            }
            var roles = new List<BaselineSelectionBinding>();
            foreach (var selection in snapshot.ActionRows.Where(x => x.MemberId == id).Select(x => x.SelectionId).Distinct(StringComparer.Ordinal))
            {
                // Role names are user/project decisions. Case-name substrings do not prove SLS or ULS.
                var field = ResolveField(BeamReviewFields.All.Single(x => x.Key == "selection.role"), id + "/" + selection,
                    materialId, member?.StoryId ?? "", span, null, "Uls", selection);
                fields.Add(field); roles.Add(new(selection, Enum.Parse<BaselineSelectionRole>(field.Value)));
            }
            var structural = ResultFactory.SemanticId("review_structural_input", new
            {
                binding,
                snapshot.SnapshotSha256,
                id,
                preset = preset.Id,
                rules = BeamReviewFields.RuleRevision,
                values = values.Where(x => BeamReviewFields.All.Single(f => f.Key == x.Key).AffectsStructure).ToArray(),
                roles,
                engine = BaselineDesignOperations.EngineIdentity
            });
            var catalogue = new BaselineCatalogue(structural, List("detailing.bars"), List("detailing.links"), List("detailing.link_spacings"),
                List("detailing.bar_counts").Select(x => (int)x).ToArray(),
                List("detailing.layers").Select(x => (int)x).OrderBy(x => x == Number("detailing.preferred_layers") ? 0 : 1).ThenBy(x => x).ToArray(),
                List("detailing.stock"), (int)Number("catalogue.maximum_candidates"));
            var context = new BaselineMemberContext(id, member?.ObjectId ?? id, values["member.physical_span"],
                Enum.Parse<BaselineSupportCondition>(values["member.support"]), Number("member.left_face"), Number("member.right_face"),
                Number("member.left_centre"), Number("member.right_centre"), Number("member.effective_span"), Number("member.anchor_start"), Number("member.anchor_end"),
                Number("design.cover"), Number("design.aggregate"), values["design.exposure"], bool.Parse(values["design.cracking_harmful"]),
                values["design.seismic"] == "non_seismic_demo_only", bool.Parse(values["design.screening_permitted"]),
                bool.Parse(values["member.horizontal"]), bool.Parse(values["member.top_mapping_normal"]), structural + ":" + values["member.evidence_reference"],
                new(Enum.Parse<BaselineFireRequirement>(values["design.fire_requirement"]),
                    values["member.fire_decision"], values["design.fire_requirement"] == "NotRequired" ? null : Number("design.fire_minutes")),
                new(List("member.restraints"), values["member.restraint_reference"]));
            var inputs = new BaselineProjectInputs(new(snapshot.Metadata.ProjectId, structural, "provisional_assumption_ledger", structural, false, false),
                [new(materialId, Number("design.fck"), Number("design.fy"), Number("design.link_fy"), Number("design.steel_modulus"))], catalogue, [context], roles);
            members.Add(new(id, inputs, Number("member.width"), Number("member.depth"),
                Number("member.width") != section?.WidthMm || Number("member.depth") != section?.DepthMm, structural));

            double Number(string key) => double.Parse(values[key], CultureInfo.InvariantCulture);
            double[] List(string key) => values[key].Split(',').Select(x => double.Parse(x, CultureInfo.InvariantCulture)).ToArray();

            BeamEffectiveField ResolveField(BeamFieldDefinition definition, string subject, string material, string story,
                string physicalSpan, string? sourceText, string fallback, string? selectionId = null)
            {
                if (!BeamReviewFields.TryNormalize(definition.Key, fallback, out fallback)) throw new ArgumentException("Invalid resolution rule: " + definition.Key);
                var candidates = edits.Where(x => x.Key == definition.Key &&
                    (x.Scope == BeamInputScope.Project || x.ModelBinding == binding) && (x.Scope switch
                    {
                        BeamInputScope.Project => true,
                        BeamInputScope.Member => x.ScopeId == id,
                        BeamInputScope.Material => x.ScopeId == material,
                        BeamInputScope.Story => x.ScopeId == story,
                        BeamInputScope.PhysicalSpan => x.ScopeId == physicalSpan,
                        BeamInputScope.Selection => x.ScopeId == selectionId,
                        _ => false
                    })).ToArray();
                var priority = candidates.Length == 0 ? -1 : candidates.Max(x => Priority(x.Scope));
                candidates = candidates.Where(x => Priority(x.Scope) == priority).OrderBy(x => x.Id, StringComparer.Ordinal).ToArray();
                var old = saved?.ModelBinding == binding ? saved.Fields.SingleOrDefault(x => x.SubjectId == subject && x.Key == definition.Key) : null;
                var value = sourceText ?? fallback;
                var origin = sourceText is not null ? BeamValueOrigin.Source : preset.Values.ContainsKey(definition.Key) ? BeamValueOrigin.Preset : BeamValueOrigin.Rule;
                var reason = sourceText is not null ? "Immutable captured value" : definition.FallbackRule;
                string? last = null;
                if (candidates.Length > 0)
                {
                    var valid = candidates.Select(x => BeamReviewFields.TryNormalize(x.Key, x.EnteredText, out var v) ? v : null).ToArray();
                    if (valid.All(x => x is not null) && valid.Distinct(StringComparer.Ordinal).Count() == 1)
                    { value = valid[0]!; last = value; origin = BeamValueOrigin.Override; reason = "Explicit " + candidates[0].Scope + " input, including values equal to the preset"; }
                    else if (old?.LastValidOverride is not null && BeamReviewFields.TryNormalize(definition.Key, old.LastValidOverride, out var previous))
                    { value = previous; last = previous; origin = candidates.Length > 1 ? BeamValueOrigin.ConflictFallback : BeamValueOrigin.LastValid; reason = "Invalid/blank/formula/conflicting entry retained; last valid override selected"; }
                    else
                    { origin = candidates.Length > 1 ? BeamValueOrigin.ConflictFallback : origin; reason = "Invalid/blank/formula/conflicting entry retained; deterministic source/preset/rule fallback: " + reason; }
                }
                return new(subject, definition.Key, definition.Unit, sourceText,
                    candidates.Length == 0 ? null : string.Join(" | ", candidates.Select(x => x.EnteredText)), value, origin, reason,
                    BeamReviewFields.RuleRevision, preset.Revision, candidates.Select(x => x.Id).ToArray(), last);
            }
        }
        var orderedEdits = edits.OrderBy(x => x.Id, StringComparer.Ordinal).ToArray();
        var revision = ResultFactory.SemanticId("review_ledger", new { binding, snapshot.SnapshotSha256, preset.Revision, memberIds, orderedEdits, fields });
        return new(new(SchemaVersion, binding, snapshot.SnapshotSha256, preset.Revision, memberIds.Distinct(StringComparer.Ordinal).ToArray(), orderedEdits, fields, revision), members);
    }

    private static int Priority(BeamInputScope scope) => scope switch
    { BeamInputScope.Project => 0, BeamInputScope.Material or BeamInputScope.Story => 1, BeamInputScope.PhysicalSpan => 2, _ => 3 };
    private static string N(double value) => value.ToString("G17", CultureInfo.InvariantCulture);
}
