using System.Collections.ObjectModel;
using System.Security.Cryptography;
using System.Text;

namespace StructuralEngineering.Etabs;

/// <summary>Count-first discovery and a bounded definition sample; no force or table-data retrieval.</summary>
public static class EtabsInspectionGetterMatrix
{
    public const string ProfileId = "etabs-model-inspection/v1";
    public static IReadOnlyDictionary<string, EtabsGetterDefinition> Allowed { get; } = Create();
    public static string Sha256 { get; } = Convert.ToHexStringLower(SHA256.HashData(Encoding.UTF8.GetBytes(
        ProfileId + "\n" + string.Join('\n', Allowed.Values.OrderBy(x => x.Operation, StringComparer.Ordinal)
            .Select(x => string.Join('|', x.Operation, x.ManagedSignature, x.ReturnSemantics,
                string.Join(',', x.InputNames), string.Join(',', x.OutputNames), x.CountOutputIndex,
                string.Join(',', x.ParallelArrays), string.Join(',', x.FixedArrays.OrderBy(p => p.Key)),
                string.Join(',', x.NullableStringArrays)))))));

    private static IReadOnlyDictionary<string, EtabsGetterDefinition> Create()
    {
        var operations = new[]
        {
            "SapModel.GetModelFilename", "SapModel.GetModelIsLocked", "SapModel.GetPresentUnits", "SapModel.GetDatabaseUnits",
            "SapModel.GetVersion", "Story.GetStories_2", "LoadPatterns.GetNameList", "LoadCases.GetNameList", "LoadCases.GetTypeOAPI",
            "RespCombo.GetNameList", "RespCombo.GetTypeOAPI", "Analyze.GetCaseStatus", "Analyze.GetRunCaseFlag",
            "Results.Setup.GetCaseSelectedForOutput", "Results.Setup.GetComboSelectedForOutput",
            "FrameObj.GetLabelFromName", "FrameObj.GetSection", "FrameObj.GetPoints", "FrameObj.GetModifiers",
            "FrameObj.GetEndLengthOffset", "FrameObj.GetInsertionPoint_1", "FrameObj.GetReleases", "FrameObj.GetLocalAxes",
            "PointObj.GetRestraint", "PropFrame.GetMaterial", "PropFrame.GetSectProps", "PropFrame.GetModifiers",
            "PropMaterial.GetMPIsotropic", "PropMaterial.GetWeightAndMass"
        };
        var result = operations.ToDictionary(x => x, x => EtabsGetterMatrix.Allowed[x], StringComparer.Ordinal);
        foreach (var operation in new[] { "FrameObj.GetAllFrames", "FrameObj.GetDesignOrientation" })
            result.Add(operation, EtabsContextGetterMatrix.Allowed[operation]);
        Direct("FrameObj.Count", "cFrameObj", "Int32 Count(System.String)", ["MyType"]);
        Direct("PointObj.Count", "cPointObj", "Int32 Count()", []);
        Direct("AreaObj.Count", "cAreaObj", "Int32 Count()", []);
        Direct("DesignConcrete.GetResultsAvailable", "cDesignConcrete", "Boolean GetResultsAvailable()", []);
        Status("DesignConcrete.GetCode", "cDesignConcrete", "Int32 GetCode(System.String ByRef)", [], ["CodeName"]);
        Status("DatabaseTables.GetAllTables", "cDatabaseTables",
            "Int32 GetAllTables(Int32 ByRef, System.String[] ByRef, System.String[] ByRef, Int32[] ByRef, Boolean[] ByRef)",
            [], ["NumberTables", "TableKey", "TableName", "ImportType", "IsEmpty"], 0, [1, 2, 3, 4]);
        foreach (var (kind, countName, listName) in new[]
        {
            ("LoadCases", "NumberSelectedLoadCases", "LoadCaseList"),
            ("LoadCombinations", "NumberSelectedLoadCombinations", "LoadCombinationList"),
            ("LoadPatterns", "NumberSelectedLoadPatterns", "LoadPatternList")
        })
            Status($"DatabaseTables.Get{kind}SelectedForDisplay", "cDatabaseTables",
                $"Int32 Get{kind}SelectedForDisplay(Int32 ByRef, System.String[] ByRef)", [], [countName, listName], 0, [1]);
        return new ReadOnlyDictionary<string, EtabsGetterDefinition>(result);

        void Direct(string operation, string type, string signature, string[] inputs) =>
            Add(operation, type, signature, EtabsReturnSemantics.DirectValue, inputs, []);
        void Status(string operation, string type, string signature, string[] inputs, string[] outputs, int? count = null, int[]? arrays = null) =>
            Add(operation, type, signature, EtabsReturnSemantics.FinalCsiReturnCode, inputs, outputs, count, arrays);
        void Add(string operation, string type, string signature, EtabsReturnSemantics semantics,
            string[] inputs, string[] outputs, int? count = null, int[]? arrays = null) =>
            result.Add(operation, new(operation, operation[..operation.LastIndexOf('.')], "ETABSv1." + type,
                operation[(operation.LastIndexOf('.') + 1)..], signature, semantics,
                Array.AsReadOnly(inputs), Array.AsReadOnly(outputs), "inspection.only", count,
                arrays is null ? null : Array.AsReadOnly(arrays)));
    }
}
