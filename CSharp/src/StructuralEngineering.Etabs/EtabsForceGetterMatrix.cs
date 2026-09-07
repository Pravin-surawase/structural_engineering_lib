using System.Collections.ObjectModel;
using System.Security.Cryptography;
using System.Text;

namespace StructuralEngineering.Etabs;

/// <summary>Batch-force profile. The retained 48-getter matrix and context profile stay unchanged.</summary>
public static class EtabsForceGetterMatrix
{
    public const string ProfileId = "wp10-shared-static-frame-capture/v1";
    public static IReadOnlyDictionary<string, EtabsGetterDefinition> Allowed { get; } = Create();
    public static string Sha256 { get; } = Convert.ToHexStringLower(SHA256.HashData(Encoding.UTF8.GetBytes(
        ProfileId + "\n" + string.Join('\n', Allowed.Values.OrderBy(item => item.Operation, StringComparer.Ordinal)
            .Select(item => string.Join('|', item.Operation, item.ObjectPath, item.InterfaceType, item.Member,
                item.ManagedSignature, item.ReturnSemantics, string.Join(',', item.InputNames), string.Join(',', item.OutputNames),
                item.CountOutputIndex?.ToString() ?? "none", string.Join(',', item.ParallelArrays),
                string.Join(',', item.FixedArrays.OrderBy(pair => pair.Key).Select(pair => $"{pair.Key}:{pair.Value}")),
                string.Join(',', item.NullableStringArrays)))))));

    private static IReadOnlyDictionary<string, EtabsGetterDefinition> Create()
    {
        var definitions = EtabsGetterMatrix.Allowed.ToDictionary(item => item.Key, item => item.Value, StringComparer.Ordinal);
        foreach (var item in EtabsContextGetterMatrix.Allowed) definitions.TryAdd(item.Key, item.Value);
        definitions.Add("PropMaterial.GetTypeOAPI", new("PropMaterial.GetTypeOAPI", "PropMaterial", "ETABSv1.cPropMaterial",
            "GetTypeOAPI", "Int32 GetTypeOAPI(System.String, ETABSv1.eMatType ByRef, Int32 ByRef)",
            EtabsReturnSemantics.FinalCsiReturnCode, ["Name"], ["MatType", "SymType"], "model.material_classification"));
        definitions.Add("PointElm.GetCoordCartesian", new("PointElm.GetCoordCartesian", "PointElm", "ETABSv1.cPointElm",
            "GetCoordCartesian", "Int32 GetCoordCartesian(System.String, Double ByRef, Double ByRef, Double ByRef, System.String)",
            EtabsReturnSemantics.FinalCsiReturnCode, ["Name", "CSys"], ["X", "Y", "Z"], "model.analysis_point"));
        return new ReadOnlyDictionary<string, EtabsGetterDefinition>(definitions);
    }
}
