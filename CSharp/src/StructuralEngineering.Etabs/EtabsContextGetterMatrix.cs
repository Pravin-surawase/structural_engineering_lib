using System.Collections.ObjectModel;
using System.Security.Cryptography;
using System.Text;

namespace StructuralEngineering.Etabs;

/// <summary>
/// Read-only bulk context inventory.  This is intentionally independent from the retained
/// force-capture matrix and contains no Results, Analyze, Set, Save, Open, or Design call.
/// </summary>
public static class EtabsContextGetterMatrix
{
    private static readonly IReadOnlyDictionary<string, EtabsGetterDefinition> Definitions =
        new ReadOnlyDictionary<string, EtabsGetterDefinition>(DefinitionsArray().ToDictionary(item => item.Operation, StringComparer.Ordinal));

    public static IReadOnlyDictionary<string, EtabsGetterDefinition> Allowed => Definitions;

    public static string Sha256 { get; } = Convert.ToHexStringLower(SHA256.HashData(Encoding.UTF8.GetBytes(
        string.Join('\n', Definitions.Values.OrderBy(item => item.Operation, StringComparer.Ordinal).Select(Describe)))));

    private static EtabsGetterDefinition[] DefinitionsArray() =>
    [
        Legacy("SapModel.GetModelFilename"),
        Legacy("SapModel.GetModelIsLocked"),
        Legacy("SapModel.GetPresentUnits"),
        Legacy("SapModel.GetDatabaseUnits"),
        Legacy("SapModel.GetVersion"),
        Status("FrameObj.GetAllFrames", "FrameObj", "cFrameObj", "GetAllFrames",
            "Int32 GetAllFrames(Int32 ByRef, System.String[] ByRef, System.String[] ByRef, System.String[] ByRef, System.String[] ByRef, System.String[] ByRef, Double[] ByRef, Double[] ByRef, Double[] ByRef, Double[] ByRef, Double[] ByRef, Double[] ByRef, Double[] ByRef, Double[] ByRef, Double[] ByRef, Double[] ByRef, Double[] ByRef, Double[] ByRef, Double[] ByRef, Int32[] ByRef, System.String)",
            ["csys"], ["NumberNames", "MyName", "PropName", "StoryName", "PointName1", "PointName2", "Point1X", "Point1Y", "Point1Z", "Point2X", "Point2Y", "Point2Z", "Angle", "Offset1X", "Offset2X", "Offset1Y", "Offset2Y", "Offset1Z", "Offset2Z", "CardinalPoint"], 0, Enumerable.Range(1, 19).ToArray()),
        Status("PointObj.GetAllPoints", "PointObj", "cPointObj", "GetAllPoints",
            "Int32 GetAllPoints(Int32 ByRef, System.String[] ByRef, Double[] ByRef, Double[] ByRef, Double[] ByRef, System.String)",
            ["csys"], ["NumberNames", "MyName", "X", "Y", "Z"], 0, [1, 2, 3, 4]),
        Status("FrameObj.GetDesignOrientation", "FrameObj", "cFrameObj", "GetDesignOrientation",
            "Int32 GetDesignOrientation(System.String, ETABSv1.eFrameDesignOrientation ByRef)", ["Name"], ["DesignOrientation"]),
        Legacy("PropFrame.GetMaterial")
    ];

    private static EtabsGetterDefinition Legacy(string operation) => EtabsGetterMatrix.Allowed[operation];

    private static EtabsGetterDefinition Status(
        string operation, string path, string type, string member, string signature,
        string[] inputs, string[] outputs, int? count = null, int[]? arrays = null) =>
        new(operation, path, $"ETABSv1.{type}", member, signature, EtabsReturnSemantics.FinalCsiReturnCode,
            Array.AsReadOnly(inputs), Array.AsReadOnly(outputs), "context.inventory", count,
            arrays is null ? null : Array.AsReadOnly(arrays));

    private static string Describe(EtabsGetterDefinition item) => string.Join('|', item.Operation, item.ObjectPath,
        item.InterfaceType, item.Member, item.ManagedSignature, item.ReturnSemantics,
        string.Join(',', item.InputNames), string.Join(',', item.OutputNames), item.CountOutputIndex?.ToString() ?? "none",
        string.Join(',', item.ParallelArrays));
}
