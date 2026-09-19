using System.Collections.ObjectModel;
using System.Security.Cryptography;
using System.Text;

namespace StructuralEngineering.Etabs;

/// <summary>Bounded definition getters only. Existing capture profile identities are unchanged.</summary>
public static class EtabsSourceGetterMatrix
{
    public const string ProfileId = "etabs-source-qualification/v1";
    public static IReadOnlyDictionary<string, EtabsGetterDefinition> Allowed { get; } = Create();
    public static string Sha256 { get; } = Convert.ToHexStringLower(SHA256.HashData(Encoding.UTF8.GetBytes(
        ProfileId + "\n" + string.Join('\n', Allowed.Values.OrderBy(x => x.Operation, StringComparer.Ordinal)
            .Select(x => string.Join('|', x.Operation, x.ObjectPath, x.InterfaceType, x.ManagedSignature,
                x.ReturnSemantics, string.Join(',', x.InputNames), string.Join(',', x.OutputNames),
                x.CountOutputIndex, string.Join(',', x.ParallelArrays), string.Join(',', x.FixedArrays.OrderBy(p => p.Key)),
                string.Join(',', x.NullableStringArrays), string.Join(',', x.TableArrays.OrderBy(p => p.Key))))))));

    private static IReadOnlyDictionary<string, EtabsGetterDefinition> Create()
    {
        var operations = new[]
        {
            "SapModel.GetModelFilename", "SapModel.GetModelIsLocked", "SapModel.GetPresentUnits", "SapModel.GetDatabaseUnits", "SapModel.GetVersion",
            "FrameObj.GetLabelFromName", "FrameObj.GetSection", "FrameObj.GetPoints", "FrameObj.GetModifiers",
            "FrameObj.GetEndLengthOffset", "FrameObj.GetInsertionPoint_1", "FrameObj.GetReleases", "FrameObj.GetLocalAxes",
            "PointObj.GetCoordCartesian", "PointObj.GetRestraint", "PointObj.GetTransformationMatrix",
            "LineElm.GetObj", "LineElm.GetPoints", "LineElm.GetTransformationMatrix",
            "PropFrame.GetMaterial", "PropFrame.GetRectangle", "PropFrame.GetModifiers", "PropMaterial.GetMPIsotropic",
            "LoadPatterns.GetLoadType", "LoadPatterns.GetSelfWTMultiplier", "LoadCases.GetTypeOAPI",
            "LoadCases.StaticLinear.GetLoads", "LoadCases.StaticLinear.GetInitialCase", "RespCombo.GetTypeOAPI", "RespCombo.GetCaseList",
            "Analyze.GetCaseStatus", "Analyze.GetRunCaseFlag", "Results.Setup.GetCaseSelectedForOutput", "Results.Setup.GetComboSelectedForOutput"
        };
        var definitions = operations.ToDictionary(x => x, x => EtabsGetterMatrix.Allowed[x], StringComparer.Ordinal);
        definitions.Add("FrameObj.GetDesignOrientation", EtabsContextGetterMatrix.Allowed["FrameObj.GetDesignOrientation"]);
        definitions.Add("PropMaterial.GetTypeOAPI", EtabsForceGetterMatrix.Allowed["PropMaterial.GetTypeOAPI"]);
        definitions.Add("FrameObj.Count", EtabsInspectionGetterMatrix.Allowed["FrameObj.Count"]);
        definitions.Add("DatabaseTables.GetAllTables", EtabsInspectionGetterMatrix.Allowed["DatabaseTables.GetAllTables"]);
        foreach (var operation in new[] { "DatabaseTables.GetAllFieldsInTable", "DatabaseTables.GetTableForDisplayArray", "DatabaseTables.GetTableForEditingArray" })
            definitions.Add(operation, EtabsBulkGetterMatrix.Allowed[operation]);
        Add("FrameObj.GetOutputStations", "cFrameObj", "Int32 GetOutputStations(System.String, Int32 ByRef, Double ByRef, Int32 ByRef, Boolean ByRef, Boolean ByRef)",
            ["Name"], ["MyType", "MaxSegSize", "MinSections", "NoOutPutAndDesignAtElementEnds", "NoOutPutAndDesignAtPointLoads"]);
        Add("PointObj.GetConnectivity", "cPointObj", "Int32 GetConnectivity(System.String, Int32 ByRef, Int32[] ByRef, System.String[] ByRef, Int32[] ByRef)",
            ["Name"], ["NumberItems", "ObjectType", "ObjectName", "PointNumber"], 0, [1, 2, 3]);
        Add("PropFrame.GetTypeOAPI", "cPropFrame", "Int32 GetTypeOAPI(System.String, ETABSv1.eFramePropType ByRef)", ["Name"], ["PropType"]);
        Add("PropMaterial.GetOConcrete", "cPropMaterial", "Int32 GetOConcrete(System.String, Double ByRef, Boolean ByRef, Double ByRef, Int32 ByRef, Int32 ByRef, Double ByRef, Double ByRef, Double ByRef, Double ByRef, Double)",
            ["Name", "Temp"], ["Fc", "IsLightweight", "FcsFactor", "SSType", "SSHysType", "StrainAtFc", "StrainUltimate", "FrictionAngle", "DilatationalAngle"]);
        return new ReadOnlyDictionary<string, EtabsGetterDefinition>(definitions);

        void Add(string operation, string type, string signature, string[] inputs, string[] outputs, int? count = null, int[]? arrays = null) =>
            definitions.Add(operation, new(operation, operation[..operation.LastIndexOf('.')], "ETABSv1." + type,
                operation[(operation.LastIndexOf('.') + 1)..], signature, EtabsReturnSemantics.FinalCsiReturnCode,
                inputs, outputs, "source.qualification", count, arrays));
    }
}
