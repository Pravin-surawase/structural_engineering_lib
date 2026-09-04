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
public static class EtabsCaptureProjector
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

    /// <summary>Returns the complete source projection or throws; never dispatches a COM call.</summary>
    public static RawAnalysisCapture Project(ReadOnlyMemory<byte> bytes, string expectedFileSha256, EtabsNormalizationOptions options)
    {
        Need(Convert.ToHexStringLower(SHA256.HashData(bytes.Span)) == expectedFileSha256,
            "The durable artifact bytes do not match the expected file SHA-256.");
        var artifact = EtabsAcquisitionArtifactCodec.ParseAndValidate(new UTF8Encoding(false, true).GetString(bytes.Span));
        var content = artifact.Content;
        var capture = content.Capture;
        var host = content.HostIdentityBefore;
        Need(!string.IsNullOrWhiteSpace(options.ProjectId) && !string.IsNullOrWhiteSpace(options.AdapterBuildId) &&
            !string.IsNullOrWhiteSpace(options.EvidenceReference), "Project, build and evidence context must be explicit.");
        Need(host.ApiFileVersion == "2.16.0.0" && host.EtabsApiVersion == "23.3.1" &&
            capture.Verdict == "LIVE_GETTER_MATRIX_COMPLETED_NO_GENERAL_COMPATIBILITY_CLAIM" &&
            capture.Request.FrameItemTypeElm == 0 && capture.Request.FinishedCaseStatus == 4 &&
            content.StartedUtc <= capture.StartedUtc && capture.CompletedUtc <= content.CompletedUtc,
            "The artifact is outside the bounded WP10 capture version or request contract.");
        var calls = capture.Calls.Select((call, index) => new Call(call, index + 1)).ToArray();
        Need(calls.Select(item => item.Raw.Operation).ToHashSet(StringComparer.Ordinal).SetEquals(EtabsGetterMatrix.Allowed.Keys),
            "The capture is missing a required getter operation or contains an unclassified operation.");
        for (var index = 0; index < calls.Length; index++)
        {
            var call = calls[index];
            var ledger = content.CallLedger.Records[index * 2];
            Need(call.Raw.GetterMatrixSha256 == EtabsGetterMatrix.Sha256 && call.Raw.HostIdentity == host &&
                call.Raw.StartedUtc >= capture.StartedUtc && call.Raw.CompletedUtc >= call.Raw.StartedUtc &&
                call.Raw.CompletedUtc <= capture.CompletedUtc && AnalysisSnapshotNormalizer.Digest(call.Inputs) == ledger.ArgumentsSha256,
                "A getter has changed identity, arguments, signature authority or acquisition interval.");
            ValidateShape(call);
        }
        Call One(string operation, string? name = null)
        {
            var matching = calls.Where(item => item.Raw.Operation == operation &&
                (name is null || item.Inputs[0].GetString() == name)).ToArray();
            Need(matching.Length > 0, $"Required evidence is missing: {operation}.");
            Need(matching.All(item => AnalysisSnapshotNormalizer.Digest(new { item.Inputs, item.Outputs, item.Direct }) ==
                AnalysisSnapshotNormalizer.Digest(new { matching[0].Inputs, matching[0].Outputs, matching[0].Direct })),
                $"Repeated observations disagree: {operation}.");
            return matching[0];
        }
        var state = capture.Preflight;
        Need(AnalysisSnapshotNormalizer.Digest(state) == AnalysisSnapshotNormalizer.Digest(capture.Postflight), "Pre/post protected facts differ.");
        Need(state.ModelSha256 == host.ModelSha256 && state.ModelPath == host.ModelPath && state.ModelBytes == host.ModelBytes &&
            state.ModelModifiedUtc == host.ModelModifiedUtc && state.ModelLocked && host.ModelLocked &&
            state.PresentUnits == 6 && state.DatabaseUnits == 6 && host.PresentUnits == 6,
            "The retained source identity, lock or units are inconsistent.");
        Need(One("SapModel.GetModelFilename").Direct.GetString() == host.ModelPath &&
            One("SapModel.GetModelIsLocked").Direct.GetBoolean() &&
            One("SapModel.GetPresentUnits").Direct.GetInt32() == 6 && One("SapModel.GetDatabaseUnits").Direct.GetInt32() == 6 &&
            One("SapModel.GetPresentUnits_2").Ints().SequenceEqual([4, 6, 2]) &&
            One("SapModel.GetDatabaseUnits_2").Ints().SequenceEqual([4, 6, 2]) &&
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
        Need(selectedCases.SequenceEqual(capture.Request.SelectedCases.Order(StringComparer.Ordinal)) &&
            selectedCombos.SequenceEqual(capture.Request.SelectedCombinations.Order(StringComparer.Ordinal)) &&
            selectedCases.SequenceEqual(state.CaseSelections.Where(item => item.Value).Select(item => item.Key).Order(StringComparer.Ordinal)) &&
            selectedCombos.SequenceEqual(state.CombinationSelections.Where(item => item.Value).Select(item => item.Key).Order(StringComparer.Ordinal)) &&
            selectedCases.Length + selectedCombos.Length > 0, "Selected output sources do not match the frozen scope.");
        var sourceRecords = new List<RawSnapshotModelRecord>();
        const string metadataId = "source:metadata";
        static string Id(string kind, string name) => $"{kind}:{name}";
        static string Source(string kind, string name) => $"source:{kind}:{name}";
        void Add<T>(RawModelRecordKind kind, string id, T data) => sourceRecords.Add(new(kind, id,
            new Dictionary<string, JsonElement> { ["data"] = AnalysisSnapshotNormalizer.SourceData(data) }));
        var memberName = capture.Request.MemberObjectName;
        var memberId = Id("member", memberName);
        Need(One("FrameObj.GetNameList").Strings(1).Contains(memberName, StringComparer.Ordinal), "The selected member is absent from the source catalogue.");
        var framePoints = One("FrameObj.GetPoints", memberName);
        Need(capture.PointNames.SequenceEqual([framePoints.Text(0), framePoints.Text(1)]), "Member connectivity disagrees with the capture summary.");
        var frameLabel = One("FrameObj.GetLabelFromName", memberName);
        Need(frameLabel.Text(0) == capture.Request.ExpectedMemberLabel && frameLabel.Text(1) == capture.Request.ExpectedStory,
            "The selected member label or story changed.");
        var stories = One("Story.GetStories_2");
        Need(stories.Strings(2).Contains(frameLabel.Text(1), StringComparer.Ordinal), "The member story is absent from the source story table.");
        for (var index = 0; index < stories.Integer(1); index++)
            Need(stories.Outputs[6][index].ValueKind != JsonValueKind.Null || stories.Outputs[5][index].GetBoolean(),
                "A non-master story has an unresolved similar-story reference.");
        foreach (var pointName in capture.PointNames.Distinct(StringComparer.Ordinal))
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
        Need(assignment.Text(0) == capture.SectionName, "The section summary differs from the actual assignment.");
        var rectangle = One("PropFrame.GetRectangle", capture.SectionName);
        var material = One("PropFrame.GetMaterial", capture.SectionName).Text(0);
        Need(material == rectangle.Text(1) && material == capture.MaterialName, "The section material getters disagree.");
        var sectionProperties = One("PropFrame.GetSectProps", capture.SectionName);
        Add(RawModelRecordKind.Section, Source("section", capture.SectionName), new SourceSnapshotSection(
            Id("section", capture.SectionName), capture.SectionName, Id("material", material),
            sectionProperties.Number(0), sectionProperties.Number(3), sectionProperties.Number(4), sectionProperties.Number(5),
            rectangle.Number(3), rectangle.Number(2), One("PropFrame.GetModifiers", capture.SectionName).Doubles(0)));
        var elastic = One("PropMaterial.GetMPIsotropic", material);
        var mass = One("PropMaterial.GetWeightAndMass", material);
        Need(elastic.Inputs[1].GetDouble() == 0 && mass.Inputs[1].GetDouble() == 0, "Temperature-dependent material sampling is outside the frozen policy.");
        Add(RawModelRecordKind.Material, Source("material", material), new SourceSnapshotMaterial(Id("material", material),
            material, elastic.Number(0), elastic.Number(1), mass.Number(1)));
        var elements = new List<SourceSnapshotElement>();
        Need(!One("FrameObj.GetLocalAxes", memberName).Bool(1), "Advanced member axes require additional source evidence.");
        foreach (var elementName in capture.ElementNames)
        {
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
            Id("section", capture.SectionName), string.IsNullOrEmpty(assignment.Text(1)) ? null : assignment.Text(1),
            One("FrameObj.GetModifiers", memberName).Doubles(0), offsets.Bool(0), offsets.Number(1), offsets.Number(2), offsets.Number(3),
            releases.Bools(0), releases.Bools(1), releases.Doubles(2), releases.Doubles(3),
            new(insertion.Integer(0), insertion.Bool(1), insertion.Bool(2), insertion.Bool(3), insertion.Doubles(4), insertion.Doubles(5), insertion.Text(6)), elements));
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
        var force = One("Results.FrameForce", memberName);
        Need(calls.Count(item => item.Raw.Operation == "Results.FrameForce") == 1 && force.Inputs[1].GetInt32() == 0 &&
            force.Integer(0) == capture.FrameForceRows && force.Integer(0) > 0, "The complete object force getter and summary disagree.");
        Need(force.Strings(3).Distinct(StringComparer.Ordinal).Order(StringComparer.Ordinal).SequenceEqual(capture.ElementNames.Order(StringComparer.Ordinal)),
            "Force elements and the retained topology inventory disagree.");
        var rawRows = new List<RawSnapshotForceRow>();
        var stationKeys = new HashSet<string>(StringComparer.Ordinal);
        for (var index = 0; index < force.Integer(0); index++)
        {
            double Number(int column) => force.Outputs[column][index].GetDouble();
            string Text(int column) => force.Outputs[column][index].GetString()!;
            Need(Text(1) == memberName && Text(6) == "Single Value" && Number(7) == 0,
                "The bounded source policy requires same-object Single Value/0 rows; unsupported rows cannot be discarded.");
            var rowId = $"source:force:{index:D8}";
            rawRows.Add(new(rowId, index, Text(1), Text(3), Number(2), Number(4), Text(5), Text(6), null,
                Number(8), Number(9), Number(10), Number(11), Number(12), Number(13)));
            var stationId = $"station:{AnalysisSnapshotNormalizer.Digest(new { Object = Text(1), Element = Text(3), ObjectStation = Number(2), ElementStation = Number(4) })}";
            if (stationKeys.Add(stationId)) Add(RawModelRecordKind.Station, $"source:{stationId}",
                new SourceSnapshotStation(stationId, memberId, Text(1), Text(3), Number(2), Number(4)));
        }
        var context = new SnapshotNormalizationContext(options.ProjectId, Path.GetFileNameWithoutExtension(host.ModelPath),
            host.EtabsApiVersion, options.AdapterBuildId,
            $"runtime-evidence:{AnalysisSnapshotNormalizer.Digest(new { host.ExecutableSha256, host.ApiSha256, host.TypeLibrarySha256 })}",
            content.CompletedUtc.UtcDateTime.ToString("O"),
            new(OptionalEvidenceState.Supplied, $"{host.ProcessId}@{host.ProcessStartedUtc.UtcDateTime:O}", null),
            new(OptionalEvidenceState.Supplied, host.ModelSha256, null), options.MaterialClassifications,
            AnalysisSnapshotNormalizer.Policy, options.EvidenceReference);
        var recordManifest = sourceRecords.Select(item => new SnapshotProjectionRecord(item.SourceRecordId, item.RecordKind))
            .Append(new(metadataId, RawModelRecordKind.ModelMetadata)).OrderBy(item => item.SourceRecordId, StringComparer.Ordinal).ToArray();
        string Target(Call call)
        {
            var operation = call.Raw.Operation;
            var name = call.Inputs.GetArrayLength() > 0 && call.Inputs[0].ValueKind == JsonValueKind.String ? call.Inputs[0].GetString()! : "";
            if (operation.StartsWith("PointObj.", StringComparison.Ordinal)) return Source("point", name);
            if (operation.StartsWith("FrameObj.", StringComparison.Ordinal) && operation != "FrameObj.GetNameList" || operation.StartsWith("LineElm.", StringComparison.Ordinal)) return Source("member", memberName);
            if (operation.StartsWith("PropFrame.", StringComparison.Ordinal)) return Source("section", name);
            if (operation.StartsWith("PropMaterial.", StringComparison.Ordinal)) return Source("material", name);
            if (operation.StartsWith("LoadCases.", StringComparison.Ordinal) && operation != "LoadCases.GetNameList" || operation == "Results.Setup.GetCaseSelectedForOutput") return Source("case", name);
            if (operation.StartsWith("RespCombo.", StringComparison.Ordinal) && operation != "RespCombo.GetNameList" || operation == "Results.Setup.GetComboSelectedForOutput") return Source("combo", name);
            return metadataId;
        }
        var evidence = calls.Select(call => new SnapshotGetterEvidence(call.Ordinal,
            content.CallLedger.Records[(call.Ordinal - 1) * 2].CallId, call.Raw.Operation, EtabsGetterMatrix.Sha256,
            Target(call), call.Inputs, call.Direct, call.Outputs, call.Raw.CsiReturnCode,
            call.Raw.StartedUtc.ToString("O"), call.Raw.CompletedUtc.ToString("O"),
            AnalysisSnapshotNormalizer.Digest(call.Raw.HostIdentity))).ToArray();
        var manifest = new SnapshotProjectionManifest(artifact.ArtifactSha256, expectedFileSha256,
            AnalysisSnapshotNormalizer.SourceData(content with { Capture = capture with { Calls = [] } }),
            recordManifest, rawRows.Select(item => item.SourceRowId).ToArray(), evidence);
        Add(RawModelRecordKind.ModelMetadata, metadataId, new SourceSnapshotMetadata(true, SnapshotAnalysisCaseStatus.Finished, context, manifest));
        var modelRevision = $"model-file-sha256:{host.ModelSha256}";
        var analysisRevision = $"analysis-evidence:{AnalysisSnapshotNormalizer.Digest(new { modelRevision, state.CaseNames, state.CaseStatuses, state.RunCaseFlags })}";
        var epoch = $"result-epoch-evidence:{AnalysisSnapshotNormalizer.Digest(new { content.OperationId, state.Sha256, Force = force.Outputs })}";
        var raw = new RawAnalysisCapture("structural.analysis_raw_capture/v1", "", "", content.OperationId,
            modelRevision, analysisRevision, epoch, new("m", "kN", "kNm", "kN/m2", "kN*s2/m4"),
            PortableLedger(content.CallLedger), sourceRecords.OrderBy(item => item.SourceRecordId, StringComparer.Ordinal).ToArray(), rawRows);
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

    private static void ValidateShape(Call call)
    {
        var definition = EtabsGetterMatrix.Allowed[call.Raw.Operation];
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
            var nullEmptyArray = count == 0 && definition.ParallelArrays.Contains(index) && value.ValueKind == JsonValueKind.Null;
            Need(nullEmptyArray || Kind(value, definition.OutputKinds[index], definition.NullableStringArrays.Contains(index)), "A getter output violates its frozen managed type.");
            if (definition.ParallelArrays.Contains(index)) Need(nullEmptyArray || value.GetArrayLength() == count, "A getter parallel array is truncated.");
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
        public EtabsRawGetterCall Raw { get; } = raw;
        public int Ordinal { get; } = ordinal;
        public JsonElement Inputs { get; } = JsonSerializer.SerializeToElement(raw.Inputs);
        public JsonElement Outputs { get; } = JsonSerializer.SerializeToElement(raw.Outputs);
        public JsonElement Direct { get; } = JsonSerializer.SerializeToElement(raw.DirectValue);
        public string Text(int index) => Outputs[index].GetString()!;
        public int Integer(int index) => Outputs[index].GetInt32();
        public double Number(int index) => Outputs[index].GetDouble();
        public bool Bool(int index) => Outputs[index].GetBoolean();
        public string[] Strings(int index) => Outputs[index].ValueKind == JsonValueKind.Null ? [] : Outputs[index].EnumerateArray().Select(item => item.GetString()!).ToArray();
        public int[] Ints(int? index = null) => (index is null ? Outputs : Outputs[index.Value]).EnumerateArray().Select(item => item.GetInt32()).ToArray();
        public double[] Doubles(int index) => Outputs[index].EnumerateArray().Select(item => item.GetDouble()).ToArray();
        public bool[] Bools(int index) => Outputs[index].EnumerateArray().Select(item => item.GetBoolean()).ToArray();
    }
}
