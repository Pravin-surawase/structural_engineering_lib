using System.Collections.ObjectModel;
using System.Security.Cryptography;
using System.Text;

namespace StructuralEngineering.Etabs;

/// <summary>Source capture plus bounded connected-object geometry; no mutation or force getters.</summary>
public static class EtabsTopologyGetterMatrix
{
    public const string ProfileId = "etabs-topology/v1";
    public static IReadOnlyDictionary<string, EtabsGetterDefinition> Allowed { get; } = Create();
    public static string Sha256 { get; } = Convert.ToHexStringLower(SHA256.HashData(Encoding.UTF8.GetBytes(
        ProfileId + "\n" + EtabsSourceGetterMatrix.Sha256 + "\n" +
        string.Join('\n', Allowed.Values.OrderBy(x => x.Operation, StringComparer.Ordinal)
            .Select(x => string.Join('|', x.Operation, x.ManagedSignature, string.Join(',', x.InputNames),
                string.Join(',', x.OutputNames), x.CountOutputIndex, string.Join(',', x.ParallelArrays),
                string.Join(',', x.FixedArrays.OrderBy(p => p.Key))))))));

    private static IReadOnlyDictionary<string, EtabsGetterDefinition> Create()
    {
        var result = EtabsSourceGetterMatrix.Allowed.ToDictionary(p => p.Key, p => p.Value, StringComparer.Ordinal);
        result.Add("FrameObj.GetAllFrames", EtabsContextGetterMatrix.Allowed["FrameObj.GetAllFrames"]);
        result.Add("FrameObj.GetTransformationMatrix", EtabsBulkGetterMatrix.Allowed["FrameObj.GetTransformationMatrix"]);
        result.Add("PointElm.GetCoordCartesian", EtabsForceGetterMatrix.Allowed["PointElm.GetCoordCartesian"]);
        Add("FrameObj.GetCurved_2", "cFrameObj",
            "Int32 GetCurved_2(System.String, Int32 ByRef, Double ByRef, Int32 ByRef, Double[] ByRef, Double[] ByRef, Double[] ByRef)",
            ["Name"], ["CurveType", "Tension", "NumPnts", "gx", "gy", "gz"], 2, [3, 4, 5]);
        Add("AreaObj.GetDesignOrientation", "cAreaObj",
            "Int32 GetDesignOrientation(System.String, ETABSv1.eAreaDesignOrientation ByRef)", ["Name"], ["DesignOrientation"]);
        Add("AreaObj.GetPoints", "cAreaObj", "Int32 GetPoints(System.String, Int32 ByRef, System.String[] ByRef)",
            ["Name"], ["NumberPoints", "Point"], 0, [1]);
        Add("AreaObj.GetProperty", "cAreaObj", "Int32 GetProperty(System.String, System.String ByRef)", ["Name"], ["PropName"]);
        Add("AreaObj.GetOpening", "cAreaObj", "Int32 GetOpening(System.String, Boolean ByRef)", ["Name"], ["IsOpening"]);
        Add("AreaObj.GetOffsets3", "cAreaObj", "Int32 GetOffsets3(System.String, Int32 ByRef, Double[] ByRef)",
            ["Name"], ["NumberPoints", "Offsets"], 0, [1]);
        Add("PropArea.GetWall", "cPropArea",
            "Int32 GetWall(System.String, ETABSv1.eWallPropType ByRef, ETABSv1.eShellType ByRef, System.String ByRef, Double ByRef, Int32 ByRef, System.String ByRef, System.String ByRef)",
            ["Name"], ["WallPropType", "ShellType", "MatProp", "Thickness", "color", "notes", "GUID"]);
        return new ReadOnlyDictionary<string, EtabsGetterDefinition>(result);

        void Add(string operation, string type, string signature, string[] inputs, string[] outputs, int? count = null, int[]? arrays = null) =>
            result.Add(operation, new(operation, operation[..operation.LastIndexOf('.')], "ETABSv1." + type,
                operation[(operation.LastIndexOf('.') + 1)..], signature, EtabsReturnSemantics.FinalCsiReturnCode,
                inputs, outputs, "topology.geometry", count, arrays));
    }
}
