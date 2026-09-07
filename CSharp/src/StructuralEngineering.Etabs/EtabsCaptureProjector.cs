using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using StructuralEngineering.Analysis;
using StructuralEngineering.Contracts;

namespace StructuralEngineering.Etabs;

public sealed record EtabsNormalizationOptions(
    string ProjectId, string AdapterBuildId, string EvidenceReference,
    IReadOnlyDictionary<string, SnapshotMaterialClassification> MaterialClassifications);

/// <summary>Decodes a durable capture without a getter host, broker, clock, or application.</summary>
public static partial class EtabsCaptureProjector
{
    public static EtabsSnapshotResult Normalize(ReadOnlyMemory<byte> bytes, string expectedFileSha256, EtabsNormalizationOptions options)
    {
        try { return AnalysisSnapshotNormalizer.Normalize(Project(bytes, expectedFileSha256, options)); }
        catch (Exception error) when (error is InvalidDataException or JsonException or ArgumentException or
            InvalidOperationException or KeyNotFoundException or NullReferenceException or IndexOutOfRangeException)
        {
            return AnalysisSnapshotNormalizer.Failure("ETABS.CAPTURE_INVALID", error.Message);
        }
    }

    /// <summary>Projects a broker-retained batch only when it is bound byte-for-byte to the durable artifact.</summary>
    public static EtabsSnapshotResult Normalize(EtabsBatchArtifact artifact, ReadOnlyMemory<byte> persistedBytes, string expectedFileSha256, EtabsNormalizationOptions options)
    {
        try
        {
            Need(Convert.ToHexStringLower(SHA256.HashData(persistedBytes.Span)) == expectedFileSha256,
                "The durable artifact bytes do not match the expected file SHA-256.");
            artifact = EtabsBatchArtifactCodec.Validate(artifact);
            Need(AnalysisSnapshotCodec.CanonicalDigest(artifact) == expectedFileSha256,
                "The in-memory batch artifact does not exactly match its durable canonical bytes.");
            return AnalysisSnapshotNormalizer.Normalize(ProjectValidatedBatch(artifact, expectedFileSha256, options));
        }
        catch (Exception error) when (error is InvalidDataException or JsonException or ArgumentException or
            InvalidOperationException or KeyNotFoundException or NullReferenceException or IndexOutOfRangeException)
        {
            return AnalysisSnapshotNormalizer.Failure("ETABS.CAPTURE_INVALID", error.Message);
        }
    }

    /// <summary>Returns the complete source projection or throws; never dispatches a COM call.</summary>
    public static RawAnalysisCapture Project(ReadOnlyMemory<byte> bytes, string expectedFileSha256, EtabsNormalizationOptions options)
    {
        Need(Convert.ToHexStringLower(SHA256.HashData(bytes.Span)) == expectedFileSha256,
            "The durable artifact bytes do not match the expected file SHA-256.");
        string? schemaVersion;
        using (var document = JsonDocument.Parse(bytes)) schemaVersion = document.RootElement.GetProperty("schema_version").GetString();
        if (schemaVersion == EtabsBatchArtifactCodec.SchemaVersion)
        {
            var batch = EtabsBatchArtifactCodec.ParseAndValidate(bytes);
            return ProjectValidatedBatch(batch, expectedFileSha256, options);
        }
        var artifact = EtabsAcquisitionArtifactCodec.ParseAndValidate(new UTF8Encoding(false, true).GetString(bytes.Span));
        var content = artifact.Content;
        var capture = content.Capture;
        var host = content.HostIdentityBefore;
        Need(host.ApiFileVersion == "2.16.0.0" && host.EtabsApiVersion == "23.3.1" &&
            capture.Verdict == "LIVE_GETTER_MATRIX_COMPLETED_NO_GENERAL_COMPATIBILITY_CLAIM" &&
            capture.Request.FrameItemTypeElm == 0 && capture.Request.FinishedCaseStatus == 4 &&
            content.StartedUtc <= capture.StartedUtc && capture.CompletedUtc <= content.CompletedUtc,
            "The artifact is outside the bounded WP10 capture version or request contract.");
        return ProjectCore(new(content.OperationId, content.CompletedUtc, artifact.ArtifactSha256, content.CallLedger,
            AnalysisSnapshotNormalizer.SourceData(content with { Capture = capture with { Calls = [] } }), host,
            capture.StartedUtc, capture.CompletedUtc, capture.Preflight, capture.Postflight,
            capture.Request.SelectedCases, capture.Request.SelectedCombinations,
            [new(capture.Request.MemberObjectName, capture.Request.ExpectedMemberLabel, capture.Request.ExpectedStory,
                capture.PointNames, capture.ElementNames, capture.SectionName, capture.MaterialName, capture.FrameForceRows)],
            capture.Calls, false), expectedFileSha256, options);
    }

    private static RawAnalysisCapture ProjectValidatedBatch(EtabsBatchArtifact batch, string expectedFileSha256, EtabsNormalizationOptions options)
    {
        var acquisition = batch.Content;
        var source = acquisition.Capture;
        return ProjectCore(new(acquisition.OperationId, acquisition.CompletedUtc, batch.ArtifactSha256,
            acquisition.CallLedger, AnalysisSnapshotNormalizer.SourceData(new
            {
                Format = "wp10-batch-acquisition-summary/v1",
                acquisition.OperationId,
                acquisition.LeaseKey,
                acquisition.StartedUtc,
                acquisition.CompletedUtc,
                acquisition.HostIdentityBefore,
                acquisition.HostIdentityAfter,
                acquisition.Cleanup,
                Capture = source with { Calls = [] },
                CallLedgerReceipt = new
                {
                    acquisition.CallLedger.OperationId,
                    acquisition.CallLedger.RecordCount,
                    acquisition.CallLedger.HeadRecordSha256,
                    acquisition.CallLedger.LedgerSha256
                }
            }),
            source.HostIdentity, source.StartedUtc, source.CompletedUtc, source.Preflight, source.Postflight,
            source.Preflight.CaseSelections.Where(item => item.Value).Select(item => item.Key).ToArray(),
            source.Preflight.CombinationSelections.Where(item => item.Value).Select(item => item.Key).ToArray(),
            source.Members, source.Calls, true, source.ProfileId is EtabsBulkGetterMatrix.ProfileId or EtabsGroupGetterMatrix.ProfileId,
            source.Context, source.ProfileId == EtabsGroupGetterMatrix.ProfileId), expectedFileSha256, options);
    }

    private sealed record ProjectionInput(string OperationId, DateTimeOffset CompletedUtc, string ArtifactSha256,
        SnapshotCallLedger CallLedger, JsonElement AcquisitionEvidence, EtabsHostIdentity Host,
        DateTimeOffset CaptureStartedUtc, DateTimeOffset CaptureCompletedUtc, EtabsProtectedState Preflight, EtabsProtectedState Postflight,
        IReadOnlyList<string> SelectedCases, IReadOnlyList<string> SelectedCombinations,
        IReadOnlyList<EtabsMemberCaptureSummary> Members, IReadOnlyList<EtabsRawGetterCall> Calls, bool Batch, bool Bulk = false,
        EtabsContextInventory? Context = null, bool Group = false);

    private static RawAnalysisCapture ProjectCore(ProjectionInput capture, string expectedFileSha256, EtabsNormalizationOptions options)
    {
        var host = capture.Host;
        Need(!string.IsNullOrWhiteSpace(options.ProjectId) && !string.IsNullOrWhiteSpace(options.AdapterBuildId) &&
            !string.IsNullOrWhiteSpace(options.EvidenceReference), "Project, build and evidence context must be explicit.");
        Need(host.ApiFileVersion == "2.16.0.0" && host.EtabsApiVersion == "23.3.1", "The runtime version is outside the qualified profile.");
        var matrix = capture.Group ? EtabsGroupGetterMatrix.Allowed : capture.Bulk ? EtabsBulkGetterMatrix.Allowed : capture.Batch ? EtabsForceGetterMatrix.Allowed : EtabsGetterMatrix.Allowed;
        var matrixSha = capture.Group ? EtabsGroupGetterMatrix.Sha256 : capture.Bulk ? EtabsBulkGetterMatrix.Sha256 : capture.Batch ? EtabsForceGetterMatrix.Sha256 : EtabsGetterMatrix.Sha256;
        var calls = capture.Calls.Select((call, index) => new Call(call, index + 1)).ToArray();
        var operations = calls.Select(item => item.Raw.Operation).ToHashSet(StringComparer.Ordinal);
        Need(capture.Batch ? operations.IsSubsetOf(matrix.Keys) : operations.SetEquals(matrix.Keys),
            "The capture is missing a required getter operation or contains an unclassified operation.");
        for (var index = 0; index < calls.Length; index++)
        {
            var call = calls[index];
            var ledger = capture.CallLedger.Records[index * 2];
            Need(call.Raw.GetterMatrixSha256 == matrixSha && call.Raw.HostIdentity == host &&
                call.Raw.StartedUtc >= capture.CaptureStartedUtc && call.Raw.CompletedUtc >= call.Raw.StartedUtc &&
                call.Raw.CompletedUtc <= capture.CaptureCompletedUtc && AnalysisSnapshotNormalizer.Digest(call.Inputs) == ledger.ArgumentsSha256,
                "A getter has changed identity, arguments, signature authority or acquisition interval.");
            ValidateShape(call, matrix[call.Raw.Operation]);
        }
        var groupedCalls = calls.GroupBy(item => (item.Raw.Operation, Name: item.Inputs.GetArrayLength() > 0 && item.Inputs[0].ValueKind == JsonValueKind.String ? item.Inputs[0].GetString() : null))
            .ToDictionary(group => group.Key, group => group.ToArray());
        foreach (var matching in groupedCalls.Values.Where(group => group.Length > 1))
        {
            var reference = AnalysisSnapshotNormalizer.Digest(new { matching[0].Inputs, matching[0].Outputs, matching[0].Direct });
            Need(matching.Skip(1).All(item => AnalysisSnapshotNormalizer.Digest(new { item.Inputs, item.Outputs, item.Direct }) == reference),
                $"Repeated observations disagree: {matching[0].Raw.Operation}.");
        }
        Call One(string operation, string? name = null)
        {
            Need(groupedCalls.TryGetValue((operation, name), out var matching), $"Required evidence is missing: {operation} ({name}).");
            matching ??= [];
            return matching[0];
        }
        var state = capture.Preflight;
        Need(AnalysisSnapshotNormalizer.Digest(state) == AnalysisSnapshotNormalizer.Digest(capture.Postflight), "Pre/post protected facts differ.");
        Need(state.ModelSha256 == host.ModelSha256 && state.ModelPath == host.ModelPath && state.ModelBytes == host.ModelBytes &&
            state.ModelModifiedUtc == host.ModelModifiedUtc && state.ModelLocked && host.ModelLocked &&
            state.PresentUnits == 6 && (state.DatabaseUnits == 6 || capture.Batch && state.DatabaseUnits == 9) && host.PresentUnits == 6,
            "The retained source identity, lock or units are inconsistent.");
        Need(One("SapModel.GetModelFilename").Direct.GetString() == host.ModelPath &&
            One("SapModel.GetModelIsLocked").Direct.GetBoolean() &&
            One("SapModel.GetPresentUnits").Direct.GetInt32() == 6 && One("SapModel.GetDatabaseUnits").Direct.GetInt32() == state.DatabaseUnits &&
            One("SapModel.GetPresentUnits_2").Ints().SequenceEqual([4, 6, 2]) &&
            One("SapModel.GetDatabaseUnits_2").Ints().SequenceEqual(state.DatabaseUnits == 9 ? [3, 4, 2] : [4, 6, 2]) &&
            One("SapModel.GetVersion").Text(0) == host.EtabsApiVersion && state.ApiVersion == host.EtabsApiVersion,
            "The actual metadata getters do not prove the source unit and runtime facts.");
        var caseNames = One("LoadCases.GetNameList").Strings(1);
        var comboNames = One("RespCombo.GetNameList").Strings(1);
        Need(caseNames.SequenceEqual(state.CaseNames) && One("Analyze.GetCaseStatus").Strings(1).SequenceEqual(caseNames) &&
            One("Analyze.GetCaseStatus").Ints(2).SequenceEqual(state.CaseStatuses) && state.CaseStatuses.All(status => status == 4) &&
            One("Analyze.GetRunCaseFlag").Strings(1).SequenceEqual(caseNames) &&
            One("Analyze.GetRunCaseFlag").Bools(2).SequenceEqual(state.RunCaseFlags) &&
            comboNames.Order(StringComparer.Ordinal).SequenceEqual(state.CombinationSelections.Keys.Order(StringComparer.Ordinal)),
            "Case, combination, status or run-flag inventories disagree.");
        Need(state.CaseSelections.Keys.Order(StringComparer.Ordinal).SequenceEqual(caseNames.Order(StringComparer.Ordinal)),
            "Case selection inventory differs from the retained case catalogue.");
        var selectedCases = caseNames.Where(name => One("Results.Setup.GetCaseSelectedForOutput", name).Bool(0)).Order(StringComparer.Ordinal).ToArray();
        var selectedCombos = comboNames.Where(name => One("Results.Setup.GetComboSelectedForOutput", name).Bool(0)).Order(StringComparer.Ordinal).ToArray();
        Need(selectedCases.SequenceEqual(capture.SelectedCases.Order(StringComparer.Ordinal)) &&
            selectedCombos.SequenceEqual(capture.SelectedCombinations.Order(StringComparer.Ordinal)) &&
            selectedCases.SequenceEqual(state.CaseSelections.Where(item => item.Value).Select(item => item.Key).Order(StringComparer.Ordinal)) &&
            selectedCombos.SequenceEqual(state.CombinationSelections.Where(item => item.Value).Select(item => item.Key).Order(StringComparer.Ordinal)) &&
            selectedCases.Length + selectedCombos.Length > 0, "Selected output sources do not match the frozen scope.");
        var sourceRecords = new List<RawSnapshotModelRecord>();
        const string metadataId = "source:metadata";
        static string Id(string kind, string name) => $"{kind}:{name}";
        static string Source(string kind, string name) => $"source:{kind}:{name}";
        var retainedRecords = new Dictionary<string, RawSnapshotModelRecord>(StringComparer.Ordinal);
        void Add<T>(RawModelRecordKind kind, string id, T data)
        {
            var record = new RawSnapshotModelRecord(kind, id,
                new Dictionary<string, JsonElement> { ["data"] = AnalysisSnapshotNormalizer.SourceData(data) });
            if (retainedRecords.TryGetValue(id, out var existing))
                Need(AnalysisSnapshotNormalizer.Digest(existing) == AnalysisSnapshotNormalizer.Digest(record), "Shared source records disagree.");
            else { retainedRecords.Add(id, record); sourceRecords.Add(record); }
        }
        var classifications = new Dictionary<string, SnapshotMaterialClassification>(options.MaterialClassifications, StringComparer.Ordinal);
        var elementOwners = new Dictionary<string, string>(StringComparer.Ordinal);
        SourceSnapshotBulkProjectionEvidence? bulkEvidence = null;
        void AddProperties(EtabsMemberCaptureSummary member)
        {
            var rectangle = One("PropFrame.GetRectangle", member.SectionName);
            var material = One("PropFrame.GetMaterial", member.SectionName).Text(0);
            Need(material == rectangle.Text(1) && material == member.MaterialName, "The section material getters disagree.");
            var sectionProperties = One("PropFrame.GetSectProps", member.SectionName);
            Add(RawModelRecordKind.Section, Source("section", member.SectionName), new SourceSnapshotSection(
                Id("section", member.SectionName), member.SectionName, Id("material", material),
                sectionProperties.Number(0), sectionProperties.Number(3), sectionProperties.Number(4), sectionProperties.Number(5),
                rectangle.Number(3), rectangle.Number(2), One("PropFrame.GetModifiers", member.SectionName).Doubles(0)));
            var elastic = One("PropMaterial.GetMPIsotropic", material);
            var mass = One("PropMaterial.GetWeightAndMass", material);
            Need(elastic.Inputs[1].GetDouble() == 0 && mass.Inputs[1].GetDouble() == 0, "Temperature-dependent material sampling is outside the frozen policy.");
            Add(RawModelRecordKind.Material, Source("material", material), new SourceSnapshotMaterial(Id("material", material),
                material, elastic.Number(0), elastic.Number(1), mass.Number(1)));
            if (capture.Batch)
            {
                var classification = One("PropMaterial.GetTypeOAPI", material);
                Need(classification.Integer(0) == 2, "This beam profile requires a source-classified concrete material.");
                classifications[material] = new("concrete", $"{options.EvidenceReference}#getter-{classification.Ordinal}");
                if (!capture.Bulk) Need(One("FrameObj.GetDesignOrientation", member.ObjectName).Integer(0) == 2, "The member is not a source-classified beam.");
            }
        }
        if (capture.Bulk)
        {
            var model = ProjectBulkModel(capture, One);
            bulkEvidence = model.Evidence;
            foreach (var point in model.Points) Add(RawModelRecordKind.Point, Source("point", point.Name), point);
            foreach (var member in model.Members)
            {
                AddProperties(capture.Members.Single(item => item.ObjectName == member.ObjectId));
                Add(RawModelRecordKind.Member, Source("member", member.ObjectId), member);
                foreach (var element in member.Elements) Need(elementOwners.TryAdd(element.Id, member.ObjectId), "An analysis element has multiple owners.");
            }
        }
        else
        {
            var analysisPointStories = capture.Members.SelectMany(member => member.ElementNames.SelectMany(element =>
                One("LineElm.GetPoints", element).StringsFromOutputs().Select(point => (Point: point, member.Story))))
                .GroupBy(item => item.Point, StringComparer.Ordinal).ToDictionary(group => group.Key,
                    group => group.Select(item => item.Story).Distinct(StringComparer.Ordinal).ToArray(), StringComparer.Ordinal);
            if (capture.Batch)
                foreach (var coordinate in calls.Where(call => call.Raw.Operation is "PointObj.GetCoordCartesian" or "PointElm.GetCoordCartesian"))
                {
                    var pointName = coordinate.Inputs[0].GetString()!;
                    Need(coordinate.Inputs[1].GetString() == "Global", "All mesh/source point coordinates must be explicitly global.");
                    // Analysis nodes have no PointObj story. Bind their unique source-frame story;
                    // the retained LineElm ownership and point getters prove this derivation.
                    if (coordinate.Raw.Operation == "PointElm.GetCoordCartesian")
                        Need(analysisPointStories[pointName].Length == 1, "An analysis node has ambiguous source-frame story ownership.");
                    var story = coordinate.Raw.Operation == "PointObj.GetCoordCartesian" ? One("PointObj.GetLabelFromName", pointName).Text(1) : analysisPointStories[pointName][0];
                    Add(RawModelRecordKind.Point, Source("point", pointName), new SourceSnapshotPoint(Id("point", pointName), pointName,
                        coordinate.Number(0), coordinate.Number(1), coordinate.Number(2), story));
                }
            foreach (var member in capture.Members)
            {
                var memberName = member.ObjectName;
                var memberId = Id("member", memberName);
                Need(One("FrameObj.GetNameList").Strings(1).Contains(memberName, StringComparer.Ordinal), "The selected member is absent from the source catalogue.");
                var framePoints = One("FrameObj.GetPoints", memberName);
                Need(member.PointNames.SequenceEqual([framePoints.Text(0), framePoints.Text(1)]), "Member connectivity disagrees with the capture summary.");
                var frameLabel = One("FrameObj.GetLabelFromName", memberName);
                Need(frameLabel.Text(0) == member.Label && frameLabel.Text(1) == member.Story,
                    "The selected member label or story changed.");
                var stories = One("Story.GetStories_2");
                Need(stories.Strings(2).Contains(frameLabel.Text(1), StringComparer.Ordinal), "The member story is absent from the source story table.");
                for (var index = 0; index < stories.Integer(1); index++)
                    Need(stories.Outputs[6][index].ValueKind != JsonValueKind.Null || stories.Outputs[5][index].GetBoolean(),
                        "A non-master story has an unresolved similar-story reference.");
                foreach (var pointName in member.PointNames.Distinct(StringComparer.Ordinal))
                {
                    var coordinate = One("PointObj.GetCoordCartesian", pointName);
                    Need(coordinate.Inputs[1].GetString() == "Global", "Point coordinates must be explicitly global.");
                    var label = One("PointObj.GetLabelFromName", pointName);
                    Need(!One("PointObj.GetLocalAxes", pointName).Bool(3) && One("PointObj.GetTransformationMatrix", pointName).Inputs[1].GetBoolean(),
                        "Advanced point axes or a nonglobal transform require a different source policy.");
                    Add(RawModelRecordKind.Point, Source("point", pointName), new SourceSnapshotPoint(Id("point", pointName),
                        pointName, coordinate.Number(0), coordinate.Number(1), coordinate.Number(2), label.Text(1)));
                }
                var assignment = One("FrameObj.GetSection", memberName);
                Need(assignment.Text(0) == member.SectionName, "The section summary differs from the actual assignment.");
                AddProperties(member);
                var elements = new List<SourceSnapshotElement>();
                Need(!One("FrameObj.GetLocalAxes", memberName).Bool(1), "Advanced member axes require additional source evidence.");
                foreach (var elementName in member.ElementNames)
                {
                    Need(elementOwners.TryAdd(elementName, memberName), "An analysis element has more than one source owner.");
                    var owner = One("LineElm.GetObj", elementName);
                    var endpoints = One("LineElm.GetPoints", elementName);
                    Need(owner.Text(0) == memberName && owner.Integer(1) == 0, "An analysis element does not belong to the selected frame object.");
                    Need(One("LineElm.GetLocalAxes", elementName).Number(0) == One("FrameObj.GetLocalAxes", memberName).Number(0),
                        "Object and element local axis angles disagree.");
                    elements.Add(new(elementName, memberName, Id("point", endpoints.Text(0)), Id("point", endpoints.Text(1)),
                        owner.Number(2), owner.Number(3), One("LineElm.GetTransformationMatrix", elementName).Doubles(0)));
                }
                var offsets = One("FrameObj.GetEndLengthOffset", memberName);
                var releases = One("FrameObj.GetReleases", memberName);
                var insertion = One("FrameObj.GetInsertionPoint_1", memberName);
                Add(RawModelRecordKind.Member, Source("member", memberName), new SourceSnapshotMember(memberId, memberName,
                    frameLabel.Text(0), frameLabel.Text(1), Id("point", framePoints.Text(0)), Id("point", framePoints.Text(1)),
                    Id("section", member.SectionName), string.IsNullOrEmpty(assignment.Text(1)) ? null : assignment.Text(1),
                    One("FrameObj.GetModifiers", memberName).Doubles(0), offsets.Bool(0), offsets.Number(1), offsets.Number(2), offsets.Number(3),
                    releases.Bools(0), releases.Bools(1), releases.Doubles(2), releases.Doubles(3),
                    new(insertion.Integer(0), insertion.Bool(1), insertion.Bool(2), insertion.Bool(3), insertion.Doubles(4), insertion.Doubles(5), insertion.Text(6)), elements));
            }
        }
        var patterns = One("LoadPatterns.GetNameList").Strings(1);
        foreach (var pattern in patterns)
        {
            _ = One("LoadPatterns.GetLoadType", pattern);
            _ = One("LoadPatterns.GetSelfWTMultiplier", pattern);
        }
        foreach (var name in caseNames)
        {
            var type = One("LoadCases.GetTypeOAPI", name);
            var extended = One("LoadCases.GetTypeOAPI_1", name);
            Need(type.Integer(0) == extended.Integer(0) && type.Integer(1) == extended.Integer(1), "Case type/subtype observations disagree.");
            var kind = type.Integer(0) switch { 1 => SnapshotLoadCaseKind.LinearStatic, 3 => SnapshotLoadCaseKind.Modal, 4 => SnapshotLoadCaseKind.ResponseSpectrum, _ => SnapshotLoadCaseKind.Other };
            string? initial = null;
            if (kind == SnapshotLoadCaseKind.LinearStatic)
            {
                Need(type.Integer(1) == 0, "The linear-static subtype is unsupported.");
                initial = One("LoadCases.StaticLinear.GetInitialCase", name).Text(0);
                var loads = One("LoadCases.StaticLinear.GetLoads", name);
                for (var index = 0; index < loads.Integer(0); index++)
                    Need(loads.Outputs[1][index].GetString() is "Load" or "Accel" &&
                        (loads.Outputs[1][index].GetString() != "Load" || patterns.Contains(loads.Outputs[2][index].GetString(), StringComparer.Ordinal)),
                        "A static load references an unavailable pattern or unsupported load type.");
            }
            Add(RawModelRecordKind.LoadCase, Source("case", name), new SourceSnapshotLoadCase(Id("case", name), name, kind, SnapshotAnalysisCaseStatus.Finished, initial));
        }
        foreach (var name in comboNames)
        {
            var type = One("RespCombo.GetTypeOAPI", name).Integer(0);
            var factors = One("RespCombo.GetCaseList", name);
            var terms = new List<SnapshotCombinationFactor>();
            for (var index = 0; index < factors.Integer(0); index++)
            {
                var sourceType = factors.Outputs[1][index].GetInt32();
                Need(sourceType is 0 or 1, "Unknown combination reference enum.");
                terms.Add(new(index, sourceType == 0 ? SnapshotResultSelectionKind.LoadCase : SnapshotResultSelectionKind.LoadCombination,
                    Id(sourceType == 0 ? "case" : "combo", factors.Outputs[2][index].GetString()!), factors.Outputs[3][index].GetDouble()));
            }
            Add(RawModelRecordKind.LoadCombination, Source("combo", name), new SourceSnapshotCombination(Id("combo", name), name,
                type switch { 0 => SnapshotCombinationKind.LinearAdd, 1 => SnapshotCombinationKind.Envelope, _ => SnapshotCombinationKind.Other }, terms));
        }
        foreach (var name in selectedCases)
            Add(RawModelRecordKind.ResultSelection, Source("selection-case", name), new SourceSnapshotSelection(Id("selection-case", name), SnapshotResultSelectionKind.LoadCase, Id("case", name), name, true));
        foreach (var name in selectedCombos)
            Add(RawModelRecordKind.ResultSelection, Source("selection-combo", name), new SourceSnapshotSelection(Id("selection-combo", name), SnapshotResultSelectionKind.LoadCombination, Id("combo", name), name, true));
        if (capture.Batch)
        {
            var selectedDependencies = new HashSet<string>(StringComparer.Ordinal);
            void Visit(string name, bool combo)
            {
                if (!selectedDependencies.Add((combo ? "combo:" : "case:") + name)) return;
                if (!combo) { Need(One("LoadCases.GetTypeOAPI_1", name).Integer(4) == 0, "Automatic/internal cases are outside the qualified batch result profile."); return; }
                var terms = One("RespCombo.GetCaseList", name);
                for (var index = 0; index < terms.Integer(0); index++) Visit(terms.Outputs[2][index].GetString()!, terms.Outputs[1][index].GetInt32() == 1);
            }
            foreach (var name in selectedCases) Visit(name, false);
            foreach (var name in selectedCombos) Visit(name, true);
        }
        var rawRows = new List<RawSnapshotForceRow>();
        var stationKeys = new HashSet<string>(StringComparer.Ordinal);
        var groupStationIds = new Dictionary<(string Object, string Element, double ObjectStation, double ElementStation), string>();
        var forces = calls.Where(item => item.Raw.Operation == "Results.FrameForce").ToArray();
        Need(forces.Length == (capture.Group ? 1 : capture.Members.Count), "The actual force getter count differs from the declared capture profile.");
        if (capture.Group)
        {
            Need(One("GroupDef.GetNameList").Strings(1).Contains("All", StringComparer.Ordinal), "The source All group is absent.");
            var assignments = One("GroupDef.GetAssignments", "All");
            var names = assignments.Strings(2); var types = assignments.Ints(1);
            var assignedFrames = names.Where((_, index) => types[index] == 2).ToArray();
            var frameSet = capture.Context!.Frames.Select(frame => frame.SourceFrameId).ToHashSet(StringComparer.Ordinal);
            Need((assignments.Integer(0) == 0 || assignedFrames.Length == assignedFrames.Distinct(StringComparer.Ordinal).Count() && frameSet.SetEquals(assignedFrames)) &&
                forces[0].Inputs[0].GetString() == "All" && forces[0].Inputs[1].GetInt32() == 2 &&
                forces[0].Integer(0) is > 0 and <= 100_000 && forces[0].Column(1).All(value => frameSet.Contains(value.GetString()!)),
                "The complete group result has unknown owners, a changed group, or an unqualified scope.");
        }
        foreach (var member in capture.Members)
        {
            var memberName = member.ObjectName;
            var memberId = Id("member", memberName);
            var force = One("Results.FrameForce", capture.Group ? "All" : memberName);
            var indices = force.ForceIndices(memberName);
            Need(force.Inputs[1].GetInt32() == (capture.Group ? 2 : 0) && indices.Length == member.FrameForceRows && indices.Length > 0 &&
                (capture.Group || indices.Length == force.Integer(0)),
                "The complete object force getter and summary disagree.");
            Need(indices.Select(index => force.Column(3)[index].GetString()!).Distinct(StringComparer.Ordinal).Order(StringComparer.Ordinal).SequenceEqual(member.ElementNames.Order(StringComparer.Ordinal)),
                "Force elements and the retained topology inventory disagree.");
            Need(indices.Select(index => force.Column(5)[index].GetString()!).Distinct(StringComparer.Ordinal).Order(StringComparer.Ordinal).SequenceEqual(
                selectedCases.Concat(selectedCombos).Distinct(StringComparer.Ordinal).Order(StringComparer.Ordinal)),
                "A required member lacks a selected result or contains an unselected result.");
            foreach (var index in indices)
            {
                double Number(int column) => force.Column(column)[index].GetDouble();
                string Text(int column) => force.Column(column)[index].GetString()!;
                Need(Text(1) == memberName && Text(6) == "Single Value" && Number(7) == 0,
                    "The bounded source policy requires same-object Single Value/0 rows; unsupported rows cannot be discarded.");
                var rowId = capture.Group ? $"source:force:All:{index:D8}" : capture.Batch ? $"source:force:{memberName}:{index:D8}" : $"source:force:{index:D8}";
                rawRows.Add(new(rowId, index, Text(1), Text(3), Number(2), Number(4), Text(5), Text(6), null,
                    Number(8), Number(9), Number(10), Number(11), Number(12), Number(13)));
                string stationId;
                if (capture.Group)
                {
                    var location = (Text(1), Text(3), Number(2), Number(4));
                    // A station has no native ETABS ID. The first actual group row at its exact
                    // location is a compact acquisition-local ID, bound by the full snapshot hash.
                    if (!groupStationIds.TryGetValue(location, out stationId!))
                        groupStationIds.Add(location, stationId = $"station:All:{index:D8}");
                }
                else stationId = $"station:{AnalysisSnapshotNormalizer.Digest(new { Object = Text(1), Element = Text(3), ObjectStation = Number(2), ElementStation = Number(4) })}";
                if (stationKeys.Add(stationId)) Add(RawModelRecordKind.Station, $"source:{stationId}",
                    new SourceSnapshotStation(stationId, memberId, Text(1), Text(3), Number(2), Number(4)));
            }
        }
        rawRows = rawRows.OrderBy(row => row.SourceRowIndex).ThenBy(row => row.SourceRowId, StringComparer.Ordinal).ToList();
        var context = new SnapshotNormalizationContext(options.ProjectId, Path.GetFileNameWithoutExtension(host.ModelPath),
            host.EtabsApiVersion, options.AdapterBuildId,
            $"runtime-evidence:{AnalysisSnapshotNormalizer.Digest(new { host.ExecutableSha256, host.ApiSha256, host.TypeLibrarySha256 })}",
            capture.CompletedUtc.UtcDateTime.ToString("O"),
            new(OptionalEvidenceState.Supplied, $"{host.ProcessId}@{host.ProcessStartedUtc.UtcDateTime:O}", null),
            new(OptionalEvidenceState.Supplied, host.ModelSha256, null), classifications,
            capture.Group ? AnalysisSnapshotNormalizer.GroupPolicy : capture.Bulk ? AnalysisSnapshotNormalizer.BulkPolicy : capture.Batch ? AnalysisSnapshotNormalizer.BatchPolicy : AnalysisSnapshotNormalizer.Policy, options.EvidenceReference);
        var recordManifest = sourceRecords.Select(item => new SnapshotProjectionRecord(item.SourceRecordId, item.RecordKind))
            .Append(new(metadataId, RawModelRecordKind.ModelMetadata)).OrderBy(item => item.SourceRecordId, StringComparer.Ordinal).ToArray();
        string Target(Call call)
        {
            var operation = call.Raw.Operation;
            var name = call.Inputs.GetArrayLength() > 0 && call.Inputs[0].ValueKind == JsonValueKind.String ? call.Inputs[0].GetString()! : "";
            if (operation.StartsWith("PointObj.", StringComparison.Ordinal) && operation != "PointObj.GetAllPoints") return Source("point", name);
            if (operation.StartsWith("PointElm.", StringComparison.Ordinal)) return Source("point", name);
            if (operation.StartsWith("FrameObj.", StringComparison.Ordinal) && operation is not "FrameObj.GetNameList" and not "FrameObj.GetAllFrames") return Source("member", name);
            if (operation.StartsWith("LineElm.", StringComparison.Ordinal)) return Source("member", elementOwners[name]);
            if (operation.StartsWith("PropFrame.", StringComparison.Ordinal)) return Source("section", name);
            if (operation.StartsWith("PropMaterial.", StringComparison.Ordinal)) return Source("material", name);
            if (operation.StartsWith("LoadCases.", StringComparison.Ordinal) && operation != "LoadCases.GetNameList" || operation == "Results.Setup.GetCaseSelectedForOutput") return Source("case", name);
            if (operation.StartsWith("RespCombo.", StringComparison.Ordinal) && operation != "RespCombo.GetNameList" || operation == "Results.Setup.GetComboSelectedForOutput") return Source("combo", name);
            return metadataId;
        }
        var evidence = calls.Select(call => new SnapshotGetterEvidence(call.Ordinal,
            capture.CallLedger.Records[(call.Ordinal - 1) * 2].CallId, call.Raw.Operation, matrixSha,
            Target(call), call.Inputs, call.Direct, call.Outputs, call.Raw.CsiReturnCode,
            call.Raw.StartedUtc.ToString("O"), call.Raw.CompletedUtc.ToString("O"),
            AnalysisSnapshotNormalizer.Digest(call.Raw.HostIdentity))).ToArray();
        var manifest = new SnapshotProjectionManifest(capture.ArtifactSha256, expectedFileSha256,
            capture.AcquisitionEvidence,
            recordManifest, rawRows.Select(item => item.SourceRowId).ToArray(), evidence);
        SourceSnapshotGroupForceScope? groupScope = capture.Group ? new("wp10-group-force-scope/v1",
            capture.CallLedger.Records[(forces[0].Ordinal - 1) * 2].CallId,
            capture.Members.Select(member => member.ObjectName).Order(StringComparer.Ordinal).ToArray(),
            forces[0].Integer(0), rawRows.Count, forces[0].Integer(0) - rawRows.Count,
            "Rows outside the requested beam objects remain in the complete getter payload as model context; no required beam row is excluded.") : null;
        Add(RawModelRecordKind.ModelMetadata, metadataId, new SourceSnapshotMetadata(true, SnapshotAnalysisCaseStatus.Finished, context, manifest, bulkEvidence, groupScope));
        var modelRevision = $"model-file-sha256:{host.ModelSha256}";
        var analysisRevision = $"analysis-evidence:{AnalysisSnapshotNormalizer.Digest(new { modelRevision, state.CaseNames, state.CaseStatuses, state.RunCaseFlags })}";
        var epoch = $"result-epoch-evidence:{AnalysisSnapshotNormalizer.Digest(new { capture.OperationId, state.Sha256, Force = capture.Batch ? (object)forces.Select(call => call.Outputs).ToArray() : forces[0].Outputs })}";
        var raw = new RawAnalysisCapture("structural.analysis_raw_capture/v1", "", "", capture.OperationId,
            modelRevision, analysisRevision, epoch, new("m", "kN", "kNm", "kN/m2", "kN*s2/m4"),
            PortableLedger(capture.CallLedger), sourceRecords.OrderBy(item => item.SourceRecordId, StringComparer.Ordinal).ToArray(), rawRows);
        var sha = AnalysisSnapshotCodec.RawCaptureSha256(raw);
        return raw with { RawCaptureSha256 = sha, RawCaptureId = $"raw_capture_id:{AnalysisSnapshotCodec.CanonicalizationVersion}:{sha}" };
    }

    private static SnapshotCallLedger PortableLedger(SnapshotCallLedger source)
    {
        // The durable envelope retains the original ledger. The portable schema requires Z,
        // so equivalent instants receive a separately chained portable representation.
        var records = new List<SnapshotCallRecord>();
        string? previous = null;
        foreach (var item in source.Records)
        {
            var record = item with
            {
                RecordedAtUtc = DateTimeOffset.Parse(item.RecordedAtUtc, System.Globalization.CultureInfo.InvariantCulture).UtcDateTime.ToString("O"),
                PreviousRecordSha256 = previous
            };
            record = record with { RecordSha256 = AnalysisSnapshotCodec.CallRecordSha256(record) };
            previous = record.RecordSha256;
            records.Add(record);
        }
        var ledger = source with { Records = records, HeadRecordSha256 = previous };
        return ledger with { LedgerSha256 = AnalysisSnapshotCodec.CallLedgerSha256(ledger) };
    }

    private static void ValidateShape(Call call, EtabsGetterDefinition definition)
    {
        Need(call.Inputs.GetArrayLength() == definition.InputNames.Count && call.Outputs.GetArrayLength() == definition.OutputNames.Count,
            "A getter has an incomplete input or output shape.");
        if (definition.ReturnSemantics == EtabsReturnSemantics.FinalCsiReturnCode)
            Need(call.Raw.CsiReturnCode == 0 && call.Direct.ValueKind == JsonValueKind.Null, "A status getter did not succeed.");
        else
            Need(call.Raw.CsiReturnCode is null && Kind(call.Direct, definition.DirectValueKind, false), "A direct getter has the wrong return type.");
        int? count = definition.CountOutputIndex is int countIndex ? call.Integer(countIndex) : null;
        Need(count is null or >= 0, "Negative source array count.");
        for (var index = 0; index < definition.OutputKinds.Length; index++)
        {
            var value = call.Outputs[index];
            var nullEmptyArray = count == 0 && (definition.ParallelArrays.Contains(index) || definition.TableArrays.ContainsKey(index)) && value.ValueKind == JsonValueKind.Null;
            Need(nullEmptyArray || Kind(value, definition.OutputKinds[index], definition.NullableStringArrays.Contains(index)), "A getter output violates its frozen managed type.");
            if (definition.ParallelArrays.Contains(index)) Need(nullEmptyArray || value.GetArrayLength() == count, "A getter parallel array is truncated.");
            if (definition.TableArrays.TryGetValue(index, out var fields)) Need(nullEmptyArray || value.GetArrayLength() == (long)count! * call.Outputs[fields].GetArrayLength(), "A flattened table is truncated.");
            if (definition.FixedArrays.TryGetValue(index, out var length)) Need(value.GetArrayLength() == length, "A fixed getter array is truncated.");
        }
    }
    private static bool Kind(JsonElement value, EtabsRawValueKind kind, bool nullableString) => kind switch
    {
        EtabsRawValueKind.String => value.ValueKind == JsonValueKind.String,
        EtabsRawValueKind.Boolean => value.ValueKind is JsonValueKind.True or JsonValueKind.False,
        EtabsRawValueKind.Int32 => value.ValueKind == JsonValueKind.Number && value.TryGetInt32(out _),
        EtabsRawValueKind.Double => value.ValueKind == JsonValueKind.Number && value.TryGetDouble(out var number) && double.IsFinite(number),
        EtabsRawValueKind.StringArray => value.ValueKind == JsonValueKind.Array && value.EnumerateArray().All(item => Kind(item, EtabsRawValueKind.String, false) || nullableString && item.ValueKind == JsonValueKind.Null),
        EtabsRawValueKind.BooleanArray => value.ValueKind == JsonValueKind.Array && value.EnumerateArray().All(item => Kind(item, EtabsRawValueKind.Boolean, false)),
        EtabsRawValueKind.Int32Array => value.ValueKind == JsonValueKind.Array && value.EnumerateArray().All(item => Kind(item, EtabsRawValueKind.Int32, false)),
        EtabsRawValueKind.DoubleArray => value.ValueKind == JsonValueKind.Array && value.EnumerateArray().All(item => Kind(item, EtabsRawValueKind.Double, false)),
        _ => false
    };
    private static void Need(bool condition, string message) { if (!condition) throw new InvalidDataException(message); }
    private sealed class Call(EtabsRawGetterCall raw, int ordinal)
    {
        private readonly Dictionary<int, JsonElement[]> _columns = new();
        private Dictionary<string, int[]>? _forceIndices;
        public EtabsRawGetterCall Raw { get; } = raw;
        public int Ordinal { get; } = ordinal;
        public JsonElement Inputs { get; } = JsonSerializer.SerializeToElement(raw.Inputs);
        public JsonElement Outputs { get; } = JsonSerializer.SerializeToElement(raw.Outputs);
        public JsonElement Direct { get; } = JsonSerializer.SerializeToElement(raw.DirectValue);
        public JsonElement[] Column(int index)
        {
            if (!_columns.TryGetValue(index, out var values)) _columns.Add(index, values = Outputs[index].EnumerateArray().ToArray());
            return values;
        }
        public int[] ForceIndices(string name)
        {
            _forceIndices ??= Column(1).Select((owner, index) => (Name: owner.GetString()!, index)).GroupBy(item => item.Name, StringComparer.Ordinal)
                .ToDictionary(group => group.Key, group => group.Select(item => item.index).ToArray(), StringComparer.Ordinal);
            return _forceIndices.TryGetValue(name, out var indices) ? indices : [];
        }
        public string Text(int index) => Outputs[index].GetString()!;
        public int Integer(int index) => Outputs[index].GetInt32();
        public double Number(int index) => Outputs[index].GetDouble();
        public bool Bool(int index) => Outputs[index].GetBoolean();
        public string[] Strings(int index) => Outputs[index].ValueKind == JsonValueKind.Null ? [] : Outputs[index].EnumerateArray().Select(item => item.GetString()!).ToArray();
        public string[] StringsFromOutputs() => Outputs.EnumerateArray().Select(item => item.GetString()!).ToArray();
        public int[] Ints(int? index = null) => (index is null ? Outputs : Outputs[index.Value]).EnumerateArray().Select(item => item.GetInt32()).ToArray();
        public double[] Doubles(int index) => Outputs[index].EnumerateArray().Select(item => item.GetDouble()).ToArray();
        public bool[] Bools(int index) => Outputs[index].EnumerateArray().Select(item => item.GetBoolean()).ToArray();
    }
}
