using System.Collections.ObjectModel;
using System.Security.Cryptography;
using System.Text;

namespace StructuralEngineering.Etabs;

/// <summary>Whole-source group results with exact original row indices and the qualified bulk geometry profile.</summary>
public static class EtabsGroupGetterMatrix
{
    public const string ProfileId = "wp10-group-static-frame-capture/v1";
    public static IReadOnlyDictionary<string, EtabsGetterDefinition> Allowed { get; } = Create();
    public static string Sha256 { get; } = Convert.ToHexStringLower(SHA256.HashData(Encoding.UTF8.GetBytes(
        ProfileId + "\n" + EtabsBulkGetterMatrix.Sha256 + "\nFrameForce:Name=All;ItemTypeElm=2;source_row_index=original_group_index;implicit_All=complete_frame_context\n" +
        string.Join('\n', Allowed.Values.Where(item => item.ObjectPath == "GroupDef").OrderBy(item => item.Operation, StringComparer.Ordinal)
            .Select(item => string.Join('|', item.Operation, item.ManagedSignature, string.Join(',', item.InputNames), string.Join(',', item.OutputNames), item.CountOutputIndex, string.Join(',', item.ParallelArrays)))))));

    private static IReadOnlyDictionary<string, EtabsGetterDefinition> Create()
    {
        var result = EtabsBulkGetterMatrix.Allowed.ToDictionary(item => item.Key, item => item.Value, StringComparer.Ordinal);
        result.Add("GroupDef.GetNameList", new("GroupDef.GetNameList", "GroupDef", "ETABSv1.cGroup", "GetNameList",
            "Int32 GetNameList(Int32 ByRef, System.String[] ByRef)", EtabsReturnSemantics.FinalCsiReturnCode,
            [], ["NumberNames", "MyName"], "model.result_group", 0, [1]));
        result.Add("GroupDef.GetAssignments", new("GroupDef.GetAssignments", "GroupDef", "ETABSv1.cGroup", "GetAssignments",
            "Int32 GetAssignments(System.String, Int32 ByRef, Int32[] ByRef, System.String[] ByRef)", EtabsReturnSemantics.FinalCsiReturnCode,
            ["Name"], ["NumberItems", "ObjectType", "ObjectName"], "model.result_group", 0, [1, 2]));
        return new ReadOnlyDictionary<string, EtabsGetterDefinition>(result);
    }
}
