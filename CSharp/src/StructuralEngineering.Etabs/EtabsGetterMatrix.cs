using System.Collections.ObjectModel;
using System.Security.Cryptography;
using System.Text;

namespace StructuralEngineering.Etabs;

public enum EtabsReturnSemantics
{
    DirectValue,
    FinalCsiReturnCode
}

public enum EtabsRawValueKind
{
    None,
    String,
    Boolean,
    Int32,
    Double,
    StringArray,
    BooleanArray,
    Int32Array,
    DoubleArray
}

public sealed record EtabsGetterDefinition(
    string Operation,
    string ObjectPath,
    string InterfaceType,
    string Member,
    string ManagedSignature,
    EtabsReturnSemantics ReturnSemantics,
    IReadOnlyList<string> InputNames,
    IReadOnlyList<string> OutputNames,
    string EvidenceDestination,
    int? CountOutputIndex = null,
    IReadOnlyList<int>? ParallelArrayOutputIndexes = null,
    IReadOnlyDictionary<int, int>? FixedArrayLengths = null)
{
    public IReadOnlyList<int> ParallelArrays { get; } =
        ParallelArrayOutputIndexes ?? Array.AsReadOnly(Array.Empty<int>());
    public IReadOnlyDictionary<int, int> FixedArrays { get; } =
        FixedArrayLengths ?? new ReadOnlyDictionary<int, int>(new Dictionary<int, int>());
    public EtabsRawValueKind DirectValueKind { get; } =
        ReturnSemantics is EtabsReturnSemantics.DirectValue
            ? EtabsManagedSignature.ValueKind(ManagedSignature.Split(' ', 2)[0])
            : EtabsRawValueKind.None;
    public EtabsRawValueKind[] OutputKinds { get; } =
        EtabsManagedSignature.OutputKinds(ManagedSignature);
}

internal static class EtabsManagedSignature
{
    public static EtabsRawValueKind[] OutputKinds(string signature)
    {
        var start = signature.IndexOf('(');
        var end = signature.LastIndexOf(')');
        if (start < 0 || end <= start + 1)
            return [];
        return signature[(start + 1)..end]
            .Split(',', StringSplitOptions.TrimEntries | StringSplitOptions.RemoveEmptyEntries)
            .Where(parameter => parameter.EndsWith(" ByRef", StringComparison.Ordinal))
            .Select(parameter => ValueKind(parameter[..^" ByRef".Length]))
            .ToArray();
    }

    public static EtabsRawValueKind ValueKind(string managedType)
    {
        var isArray = managedType.EndsWith("[]", StringComparison.Ordinal);
        var scalar = isArray ? managedType[..^2] : managedType;
        var kind = scalar switch
        {
            "System.String" => EtabsRawValueKind.String,
            "Boolean" or "System.Boolean" => EtabsRawValueKind.Boolean,
            "Int32" or "System.Int32" => EtabsRawValueKind.Int32,
            "Double" or "System.Double" => EtabsRawValueKind.Double,
            _ when scalar.StartsWith("ETABSv1.e", StringComparison.Ordinal) => EtabsRawValueKind.Int32,
            _ => throw new InvalidOperationException($"Unsupported frozen ETABS managed type {managedType}.")
        };
        return isArray ? kind switch
        {
            EtabsRawValueKind.String => EtabsRawValueKind.StringArray,
            EtabsRawValueKind.Boolean => EtabsRawValueKind.BooleanArray,
            EtabsRawValueKind.Int32 => EtabsRawValueKind.Int32Array,
            EtabsRawValueKind.Double => EtabsRawValueKind.DoubleArray,
            _ => throw new InvalidOperationException($"Unsupported frozen ETABS array type {managedType}.")
        } : kind;
    }
}

public static class EtabsGetterMatrix
{
    private static readonly IReadOnlyDictionary<string, EtabsGetterDefinition> Definitions =
        Array.AsReadOnly(
        [
            Direct("SapModel.GetModelFilename", "SapModel", "cSapModel", "GetModelFilename", "System.String GetModelFilename(Boolean)", ["IncludePath"], "model.metadata"),
            Direct("SapModel.GetModelIsLocked", "SapModel", "cSapModel", "GetModelIsLocked", "Boolean GetModelIsLocked()", [], "model.metadata"),
            Direct("SapModel.GetPresentUnits", "SapModel", "cSapModel", "GetPresentUnits", "ETABSv1.eUnits GetPresentUnits()", [], "model.units"),
            Direct("SapModel.GetDatabaseUnits", "SapModel", "cSapModel", "GetDatabaseUnits", "ETABSv1.eUnits GetDatabaseUnits()", [], "model.units"),
            Status("SapModel.GetPresentUnits_2", "SapModel", "cSapModel", "GetPresentUnits_2", "Int32 GetPresentUnits_2(ETABSv1.eForce ByRef, ETABSv1.eLength ByRef, ETABSv1.eTemperature ByRef)", [], ["forceUnits", "lengthUnits", "temperatureUnits"], "model.units"),
            Status("SapModel.GetDatabaseUnits_2", "SapModel", "cSapModel", "GetDatabaseUnits_2", "Int32 GetDatabaseUnits_2(ETABSv1.eForce ByRef, ETABSv1.eLength ByRef, ETABSv1.eTemperature ByRef)", [], ["forceUnits", "lengthUnits", "temperatureUnits"], "model.units"),
            Status("SapModel.GetVersion", "SapModel", "cSapModel", "GetVersion", "Int32 GetVersion(System.String ByRef, Double ByRef)", [], ["Version", "MyVersionNumber"], "source.runtime"),
            Status("Story.GetStories_2", "Story", "cStory", "GetStories_2", "Int32 GetStories_2(Double ByRef, Int32 ByRef, System.String[] ByRef, Double[] ByRef, Double[] ByRef, Boolean[] ByRef, System.String[] ByRef, Boolean[] ByRef, Double[] ByRef, Int32[] ByRef)", [], ["BaseElevation", "NumberStories", "StoryNames", "StoryElevations", "StoryHeights", "IsMasterStory", "SimilarToStory", "SpliceAbove", "SpliceHeight", "color"], "model.stories", 1, [2, 3, 4, 5, 6, 7, 8, 9]),
            Status("FrameObj.GetNameList", "FrameObj", "cFrameObj", "GetNameList", "Int32 GetNameList(Int32 ByRef, System.String[] ByRef)", [], ["NumberNames", "MyName"], "model.members", 0, [1]),
            Status("FrameObj.GetLabelFromName", "FrameObj", "cFrameObj", "GetLabelFromName", "Int32 GetLabelFromName(System.String, System.String ByRef, System.String ByRef)", ["Name"], ["Label", "Story"], "model.members"),
            Status("FrameObj.GetPoints", "FrameObj", "cFrameObj", "GetPoints", "Int32 GetPoints(System.String, System.String ByRef, System.String ByRef)", ["Name"], ["Point1", "Point2"], "model.topology"),
            Status("FrameObj.GetSection", "FrameObj", "cFrameObj", "GetSection", "Int32 GetSection(System.String, System.String ByRef, System.String ByRef)", ["Name"], ["PropName", "SAuto"], "model.assignments"),
            Status("FrameObj.GetModifiers", "FrameObj", "cFrameObj", "GetModifiers", "Int32 GetModifiers(System.String, Double[] ByRef)", ["Name"], ["Value"], "model.assignments", fixedArrays: Fixed((0, 8))),
            Status("FrameObj.GetEndLengthOffset", "FrameObj", "cFrameObj", "GetEndLengthOffset", "Int32 GetEndLengthOffset(System.String, Boolean ByRef, Double ByRef, Double ByRef, Double ByRef)", ["Name"], ["AutoOffset", "Length1", "Length2", "RZ"], "model.assignments"),
            Status("FrameObj.GetInsertionPoint_1", "FrameObj", "cFrameObj", "GetInsertionPoint_1", "Int32 GetInsertionPoint_1(System.String, Int32 ByRef, Boolean ByRef, Boolean ByRef, Boolean ByRef, Double[] ByRef, Double[] ByRef, System.String ByRef)", ["Name"], ["CardinalPoint", "Mirror2", "Mirror3", "StiffTransform", "Offset1", "Offset2", "CSys"], "model.assignments", fixedArrays: Fixed((4, 3), (5, 3))),
            Status("FrameObj.GetReleases", "FrameObj", "cFrameObj", "GetReleases", "Int32 GetReleases(System.String, Boolean[] ByRef, Boolean[] ByRef, Double[] ByRef, Double[] ByRef)", ["Name"], ["II", "JJ", "StartValue", "EndValue"], "model.assignments", fixedArrays: Fixed((0, 6), (1, 6), (2, 6), (3, 6))),
            Status("FrameObj.GetLocalAxes", "FrameObj", "cFrameObj", "GetLocalAxes", "Int32 GetLocalAxes(System.String, Double ByRef, Boolean ByRef)", ["Name"], ["Ang", "Advanced"], "model.axes"),
            Status("PointObj.GetCoordCartesian", "PointObj", "cPointObj", "GetCoordCartesian", "Int32 GetCoordCartesian(System.String, Double ByRef, Double ByRef, Double ByRef, System.String)", ["Name", "CSys"], ["X", "Y", "Z"], "model.points"),
            Status("PointObj.GetLabelFromName", "PointObj", "cPointObj", "GetLabelFromName", "Int32 GetLabelFromName(System.String, System.String ByRef, System.String ByRef)", ["Name"], ["Label", "Story"], "model.points"),
            Status("PointObj.GetRestraint", "PointObj", "cPointObj", "GetRestraint", "Int32 GetRestraint(System.String, Boolean[] ByRef)", ["Name"], ["Value"], "model.supports", fixedArrays: Fixed((0, 6))),
            Status("PointObj.GetLocalAxes", "PointObj", "cPointObj", "GetLocalAxes", "Int32 GetLocalAxes(System.String, Double ByRef, Double ByRef, Double ByRef, Boolean ByRef)", ["Name"], ["A", "B", "C", "Advanced"], "model.axes"),
            Status("PointObj.GetTransformationMatrix", "PointObj", "cPointObj", "GetTransformationMatrix", "Int32 GetTransformationMatrix(System.String, Double[] ByRef, Boolean)", ["Name", "IsGlobal"], ["Value"], "model.axes", fixedArrays: Fixed((0, 9))),
            Status("LineElm.GetObj", "LineElm", "cLineElm", "GetObj", "Int32 GetObj(System.String, System.String ByRef, Int32 ByRef, Double ByRef, Double ByRef)", ["Name"], ["Obj", "ObjType", "RDI", "RDJ"], "model.mapping"),
            Status("LineElm.GetPoints", "LineElm", "cLineElm", "GetPoints", "Int32 GetPoints(System.String, System.String ByRef, System.String ByRef)", ["Name"], ["Point1", "Point2"], "model.mapping"),
            Status("LineElm.GetLocalAxes", "LineElm", "cLineElm", "GetLocalAxes", "Int32 GetLocalAxes(System.String, Double ByRef)", ["Name"], ["Ang"], "model.axes"),
            Status("LineElm.GetTransformationMatrix", "LineElm", "cLineElm", "GetTransformationMatrix", "Int32 GetTransformationMatrix(System.String, Double[] ByRef)", ["Name"], ["Value"], "model.axes", fixedArrays: Fixed((0, 9))),
            Status("PropFrame.GetMaterial", "PropFrame", "cPropFrame", "GetMaterial", "Int32 GetMaterial(System.String, System.String ByRef)", ["Name"], ["MatProp"], "model.sections"),
            Status("PropFrame.GetRectangle", "PropFrame", "cPropFrame", "GetRectangle", "Int32 GetRectangle(System.String, System.String ByRef, System.String ByRef, Double ByRef, Double ByRef, Int32 ByRef, System.String ByRef, System.String ByRef)", ["Name"], ["FileName", "MatProp", "T3", "T2", "Color", "Notes", "GUID"], "model.sections"),
            Status("PropFrame.GetSectProps", "PropFrame", "cPropFrame", "GetSectProps", "Int32 GetSectProps(System.String, Double ByRef, Double ByRef, Double ByRef, Double ByRef, Double ByRef, Double ByRef, Double ByRef, Double ByRef, Double ByRef, Double ByRef, Double ByRef, Double ByRef)", ["Name"], ["Area", "As2", "As3", "Torsion", "I22", "I33", "S22", "S33", "Z22", "Z33", "R22", "R33"], "model.sections"),
            Status("PropFrame.GetModifiers", "PropFrame", "cPropFrame", "GetModifiers", "Int32 GetModifiers(System.String, Double[] ByRef)", ["Name"], ["Value"], "model.sections", fixedArrays: Fixed((0, 8))),
            Status("PropMaterial.GetMPIsotropic", "PropMaterial", "cPropMaterial", "GetMPIsotropic", "Int32 GetMPIsotropic(System.String, Double ByRef, Double ByRef, Double ByRef, Double ByRef, Double)", ["Name", "Temp"], ["E", "U", "A", "G"], "model.materials"),
            Status("PropMaterial.GetWeightAndMass", "PropMaterial", "cPropMaterial", "GetWeightAndMass", "Int32 GetWeightAndMass(System.String, Double ByRef, Double ByRef, Double)", ["Name", "Temp"], ["W", "M"], "model.materials"),
            Status("LoadPatterns.GetNameList", "LoadPatterns", "cLoadPatterns", "GetNameList", "Int32 GetNameList(Int32 ByRef, System.String[] ByRef)", [], ["NumberNames", "MyName"], "model.load_definitions", 0, [1]),
            Status("LoadPatterns.GetLoadType", "LoadPatterns", "cLoadPatterns", "GetLoadType", "Int32 GetLoadType(System.String, ETABSv1.eLoadPatternType ByRef)", ["Name"], ["MyType"], "model.load_definitions"),
            Status("LoadPatterns.GetSelfWTMultiplier", "LoadPatterns", "cLoadPatterns", "GetSelfWTMultiplier", "Int32 GetSelfWTMultiplier(System.String, Double ByRef)", ["Name"], ["SelfWTMultiplier"], "model.load_definitions"),
            Status("LoadCases.GetNameList", "LoadCases", "cLoadCases", "GetNameList", "Int32 GetNameList(Int32 ByRef, System.String[] ByRef, ETABSv1.eLoadCaseType)", ["CaseType"], ["NumberNames", "MyName"], "model.load_definitions", 0, [1]),
            Status("LoadCases.GetTypeOAPI", "LoadCases", "cLoadCases", "GetTypeOAPI", "Int32 GetTypeOAPI(System.String, ETABSv1.eLoadCaseType ByRef, Int32 ByRef)", ["Name"], ["CaseType", "SubType"], "model.load_definitions"),
            Status("LoadCases.GetTypeOAPI_1", "LoadCases", "cLoadCases", "GetTypeOAPI_1", "Int32 GetTypeOAPI_1(System.String, ETABSv1.eLoadCaseType ByRef, Int32 ByRef, ETABSv1.eLoadPatternType ByRef, Int32 ByRef, Int32 ByRef)", ["Name"], ["CaseType", "SubType", "DesignType", "DesignTypeOption", "Auto"], "model.load_definitions"),
            Status("LoadCases.StaticLinear.GetLoads", "LoadCases.StaticLinear", "cCaseStaticLinear", "GetLoads", "Int32 GetLoads(System.String, Int32 ByRef, System.String[] ByRef, System.String[] ByRef, Double[] ByRef)", ["Name"], ["NumberLoads", "LoadType", "LoadName", "SF"], "model.load_definitions", 0, [1, 2, 3]),
            Status("LoadCases.StaticLinear.GetInitialCase", "LoadCases.StaticLinear", "cCaseStaticLinear", "GetInitialCase", "Int32 GetInitialCase(System.String, System.String ByRef)", ["Name"], ["InitialCase"], "model.load_definitions"),
            Status("RespCombo.GetNameList", "RespCombo", "cCombo", "GetNameList", "Int32 GetNameList(Int32 ByRef, System.String[] ByRef)", [], ["NumberNames", "MyName"], "model.load_definitions", 0, [1]),
            Status("RespCombo.GetTypeOAPI", "RespCombo", "cCombo", "GetTypeOAPI", "Int32 GetTypeOAPI(System.String, Int32 ByRef)", ["name"], ["ComboType"], "model.load_definitions"),
            Status("RespCombo.GetCaseList", "RespCombo", "cCombo", "GetCaseList", "Int32 GetCaseList(System.String, Int32 ByRef, ETABSv1.eCNameType[] ByRef, System.String[] ByRef, Double[] ByRef)", ["Name"], ["NumberItems", "CNameType", "CName", "SF"], "model.load_definitions", 0, [1, 2, 3]),
            Status("Analyze.GetCaseStatus", "Analyze", "cAnalyze", "GetCaseStatus", "Int32 GetCaseStatus(Int32 ByRef, System.String[] ByRef, Int32[] ByRef)", [], ["NumberItems", "CaseName", "Status"], "source.analysis_epoch", 0, [1, 2]),
            Status("Analyze.GetRunCaseFlag", "Analyze", "cAnalyze", "GetRunCaseFlag", "Int32 GetRunCaseFlag(Int32 ByRef, System.String[] ByRef, Boolean[] ByRef)", [], ["NumberItems", "CaseName", "Run"], "source.analysis_epoch", 0, [1, 2]),
            Status("Results.Setup.GetCaseSelectedForOutput", "Results.Setup", "cAnalysisResultsSetup", "GetCaseSelectedForOutput", "Int32 GetCaseSelectedForOutput(System.String, Boolean ByRef)", ["Name"], ["Selected"], "source.result_selection"),
            Status("Results.Setup.GetComboSelectedForOutput", "Results.Setup", "cAnalysisResultsSetup", "GetComboSelectedForOutput", "Int32 GetComboSelectedForOutput(System.String, Boolean ByRef)", ["Name"], ["Selected"], "source.result_selection"),
            Status("Results.FrameForce", "Results", "cAnalysisResults", "FrameForce", "Int32 FrameForce(System.String, ETABSv1.eItemTypeElm, Int32 ByRef, System.String[] ByRef, Double[] ByRef, System.String[] ByRef, Double[] ByRef, System.String[] ByRef, System.String[] ByRef, Double[] ByRef, Double[] ByRef, Double[] ByRef, Double[] ByRef, Double[] ByRef, Double[] ByRef, Double[] ByRef)", ["Name", "ItemTypeElm"], ["NumberResults", "Obj", "ObjSta", "Elm", "ElmSta", "LoadCase", "StepType", "StepNum", "P", "V2", "V3", "T", "M2", "M3"], "results.frame_force", 0, Enumerable.Range(1, 13).ToArray())
        ]).ToDictionary(item => item.Operation, StringComparer.Ordinal);

    public static IReadOnlyDictionary<string, EtabsGetterDefinition> Allowed { get; } =
        Definitions;

    public static IReadOnlyList<string> DeniedMutationFamilies { get; } = Array.AsReadOnly(
    [
        "*.Set*",
        "SapModel.SetModelIsLocked",
        "Analyze.RunAnalysis",
        "Design*",
        "File.Save*",
        "File.Close",
        "cOAPI.ApplicationExit"
    ]);

    public static string Sha256 { get; } = Convert.ToHexStringLower(SHA256.HashData(
        Encoding.UTF8.GetBytes(string.Join('\n',
            Definitions.Values
                .OrderBy(item => item.Operation, StringComparer.Ordinal)
                .Select(item => string.Join('|', item.Operation, item.ObjectPath, item.InterfaceType,
                    item.Member, item.ManagedSignature, item.ReturnSemantics,
                    string.Join(',', item.InputNames), string.Join(',', item.OutputNames),
                    item.EvidenceDestination, item.CountOutputIndex?.ToString() ?? "none",
                    string.Join(',', item.ParallelArrays),
                    string.Join(',', item.FixedArrays.OrderBy(pair => pair.Key)
                        .Select(pair => $"{pair.Key}:{pair.Value}"))))
                .Concat(DeniedMutationFamilies.Select(item => $"deny|{item}"))))));

    private static EtabsGetterDefinition Direct(
        string operation, string path, string type, string member, string signature,
        string[] inputs, string destination) =>
        new(operation, path, $"ETABSv1.{type}", member, signature,
            EtabsReturnSemantics.DirectValue,
            Array.AsReadOnly(inputs),
            Array.AsReadOnly(Array.Empty<string>()),
            destination);

    private static EtabsGetterDefinition Status(
        string operation, string path, string type, string member, string signature,
        string[] inputs, string[] outputs, string destination, int? count = null,
        int[]? arrays = null, IReadOnlyDictionary<int, int>? fixedArrays = null) =>
        new(operation, path, $"ETABSv1.{type}", member, signature,
            EtabsReturnSemantics.FinalCsiReturnCode,
            Array.AsReadOnly(inputs),
            Array.AsReadOnly(outputs),
            destination,
            count,
            arrays is null ? null : Array.AsReadOnly(arrays),
            fixedArrays);

    private static IReadOnlyDictionary<int, int> Fixed(params (int Index, int Length)[] values) =>
        new ReadOnlyDictionary<int, int>(values.ToDictionary(item => item.Index, item => item.Length));
}
