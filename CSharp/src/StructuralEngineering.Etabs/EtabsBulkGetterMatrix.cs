using System.Collections.ObjectModel;
using System.Security.Cryptography;
using System.Text;

namespace StructuralEngineering.Etabs;

/// <summary>Qualified table getters plus real per-object forces. No table setter, apply, unlock or analysis call.</summary>
public static class EtabsBulkGetterMatrix
{
    public const string ProfileId = "wp10-bulk-static-frame-capture/v1";
    public static IReadOnlyDictionary<string, EtabsGetterDefinition> Allowed { get; } = Create();
    public static string Sha256 { get; } = Convert.ToHexStringLower(SHA256.HashData(Encoding.UTF8.GetBytes(
        ProfileId + "\n" + EtabsForceGetterMatrix.Sha256 + "\n" + string.Join('\n', Allowed.Values
            .Where(item => !EtabsForceGetterMatrix.Allowed.ContainsKey(item.Operation)).OrderBy(item => item.Operation, StringComparer.Ordinal)
            .Select(item => string.Join('|', item.Operation, item.ManagedSignature, string.Join(',', item.InputNames),
                string.Join(',', item.OutputNames), item.CountOutputIndex, string.Join(',', item.ParallelArrays),
                string.Join(',', item.FixedArrays.OrderBy(pair => pair.Key).Select(pair => $"{pair.Key}:{pair.Value}")),
                string.Join(',', item.NullableStringArrays), string.Join(',', item.TableArrays.Select(pair => $"{pair.Key}:{pair.Value}"))))))));

    private static IReadOnlyDictionary<string, EtabsGetterDefinition> Create()
    {
        var result = EtabsForceGetterMatrix.Allowed.ToDictionary(item => item.Key, item => item.Value, StringComparer.Ordinal);
        result.Add("FrameObj.GetTransformationMatrix", new("FrameObj.GetTransformationMatrix", "FrameObj", "ETABSv1.cFrameObj", "GetTransformationMatrix",
            "Int32 GetTransformationMatrix(System.String, Double[] ByRef, Boolean)", EtabsReturnSemantics.FinalCsiReturnCode,
            ["Name", "IsGlobal"], ["Value"], "model.frame_axes", FixedArrayLengths: new Dictionary<int, int> { [0] = 9 }));
        Add("GetAllFieldsInTable", "Int32 GetAllFieldsInTable(System.String, Int32 ByRef, Int32 ByRef, System.String[] ByRef, System.String[] ByRef, System.String[] ByRef, System.String[] ByRef, Boolean[] ByRef)",
            ["TableKey"], ["TableVersion", "NumberFields", "FieldKey", "FieldName", "Description", "UnitsString", "IsImportable"], 1, [2, 3, 4, 5, 6]);
        Add("GetTableForEditingArray", "Int32 GetTableForEditingArray(System.String, System.String, Int32 ByRef, System.String[] ByRef, Int32 ByRef, System.String[] ByRef)",
            ["TableKey", "GroupName"], ["TableVersion", "FieldsKeysIncluded", "NumberRecords", "TableData"], 2, [], [3], new Dictionary<int, int> { [3] = 1 });
        Add("GetTableForDisplayArray", "Int32 GetTableForDisplayArray(System.String, System.String[] ByRef, System.String, Int32 ByRef, System.String[] ByRef, Int32 ByRef, System.String[] ByRef)",
            ["TableKey", "FieldKeyList", "GroupName"], ["FieldKeyList", "TableVersion", "FieldsKeysIncluded", "NumberRecords", "TableData"], 3, [], [4], new Dictionary<int, int> { [4] = 2 });
        return new ReadOnlyDictionary<string, EtabsGetterDefinition>(result);

        void Add(string name, string signature, string[] inputs, string[] outputs, int count, int[] arrays,
            int[]? nullable = null, IReadOnlyDictionary<int, int>? tables = null) => result.Add("DatabaseTables." + name,
                new("DatabaseTables." + name, "DatabaseTables", "ETABSv1.cDatabaseTables", name, signature,
                    EtabsReturnSemantics.FinalCsiReturnCode, inputs, outputs, "model.bulk_tables", count, arrays,
                    NullableStringArrayOutputIndexes: nullable, TableArrayFieldIndexes: tables));
    }
}
