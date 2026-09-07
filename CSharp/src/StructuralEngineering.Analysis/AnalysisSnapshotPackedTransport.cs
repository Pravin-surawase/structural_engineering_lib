using System.Reflection;
using System.Text.Json;
using System.Text.Json.Serialization;
using StructuralEngineering.Contracts;

namespace StructuralEngineering.Analysis;

/// <summary>Compact, versioned row encoding. Only repeated leaf records use positional arrays.</summary>
public static partial class AnalysisSnapshotCodec
{
    private static readonly JsonSerializerOptions PackedJsonOptions = CreatePackedOptions();

    internal static void WritePackedJson(Stream destination, AnalysisSnapshot snapshot) =>
        JsonSerializer.Serialize(destination, snapshot, PackedJsonOptions);

    internal static EtabsSnapshotResult ParseAndValidatePackedStream(Stream source, int maximumBytes)
    {
        try
        {
            using var bounded = new AnalysisSnapshotTransport.LimitedStream(source, maximumBytes);
            using var checkedJson = new DuplicateCheckingStream(bounded);
            var snapshot = JsonSerializer.Deserialize<AnalysisSnapshot>(checkedJson, PackedJsonOptions)
                ?? throw new JsonException("Snapshot cannot be null.");
            checkedJson.RequireEnd();
            return Validate(snapshot);
        }
        catch (Exception exception) when (exception is JsonException or ArgumentException or InvalidOperationException or NullReferenceException or IOException or InvalidDataException)
        {
            return Rejected("INPUT.SCHEMA", "$", $"The compact snapshot does not match the strict bounded rows-1 schema: {exception.Message}",
                "Restore a complete supported snapshot within the transport limits.");
        }
    }

    private static JsonSerializerOptions CreatePackedOptions()
    {
        var options = new JsonSerializerOptions(JsonOptions);
        options.Converters.Add(new PositionalRecordConverter<SnapshotActionRow>(
            ["action_basis", "analysis_element_id", "force_unit", "m2_knm", "m3_knm", "member_id", "moment_unit", "object_id", "output_case_name", "p_kn", "provenance", "row_id", "selection_id", "source_row_id", "station_id", "step_number", "step_type", "t_knm", "v2_kn", "v3_kn"]));
        options.Converters.Add(new PositionalRecordConverter<SnapshotStation>(
            ["analysis_element_id", "element_station_mm", "evidence_reference", "member_id", "normalized_ratio", "object_id", "object_station_mm", "physical_station_mm", "side", "station_id"]));
        options.Converters.Add(new PositionalRecordConverter<SnapshotRowDispositionRecord>(
            ["approval_reference", "canonical_id", "diagnostic_codes", "disposition", "reason_code", "record_kind", "source_record_id"]));
        options.Converters.Add(new PositionalRecordConverter<RawSnapshotForceRow>(
            ["analysis_element_id", "element_station", "m2", "m3", "object_id", "object_station", "output_case_name", "p", "source_row_id", "source_row_index", "step_number", "step_type", "t", "v2", "v3"]));
        options.Converters.Add(new PositionalRecordConverter<SnapshotForceResultProvenance>(
            ["call_id", "concurrency_basis", "evidence_reference", "getter_method", "signature_authority_sha256", "source_row_index"]));
        return options;
    }

    private sealed class PositionalRecordConverter<T>(IReadOnlyList<string> columns) : JsonConverter<T> where T : class
    {
        private static readonly JsonNamingPolicy Naming = JsonNamingPolicy.SnakeCaseLower;
        private static readonly NullabilityInfoContext Nullability = new();
        private readonly PropertyInfo[] _properties = Resolve(columns);
        private readonly ConstructorInfo _constructor = typeof(T).GetConstructors().Single(constructor =>
            constructor.GetParameters().Length == columns.Count);
        private readonly bool[] _nullable = Resolve(columns).Select(AllowsNull).ToArray();
        private readonly int[] _argumentColumns = typeof(T).GetConstructors().Single(constructor => constructor.GetParameters().Length == columns.Count)
            .GetParameters().Select(parameter => Array.FindIndex(Resolve(columns), property => string.Equals(property.Name, parameter.Name, StringComparison.OrdinalIgnoreCase))).ToArray();

        public override T Read(ref Utf8JsonReader reader, Type typeToConvert, JsonSerializerOptions options)
        {
            if (reader.TokenType != JsonTokenType.StartArray) throw new JsonException($"{typeof(T).Name} must be a positional array.");
            var values = new object?[columns.Count];
            for (var index = 0; index < values.Length; index++)
            {
                if (!reader.Read()) throw new JsonException($"{typeof(T).Name} is incomplete.");
                if (reader.TokenType == JsonTokenType.Null && !_nullable[index])
                    throw new JsonException($"{typeof(T).Name} column '{columns[index]}' cannot be null.");
                values[index] = JsonSerializer.Deserialize(ref reader, _properties[index].PropertyType, options);
            }
            if (!reader.Read() || reader.TokenType != JsonTokenType.EndArray)
                throw new JsonException($"{typeof(T).Name} must have exactly {columns.Count} columns.");
            var arguments = _argumentColumns.Select(index => values[index]).ToArray();
            return (T)_constructor.Invoke(arguments);
        }

        public override void Write(Utf8JsonWriter writer, T value, JsonSerializerOptions options)
        {
            writer.WriteStartArray();
            foreach (var property in _properties)
                JsonSerializer.Serialize(writer, property.GetValue(value), property.PropertyType, options);
            writer.WriteEndArray();
        }

        private static PropertyInfo[] Resolve(IReadOnlyList<string> names)
        {
            var properties = typeof(T).GetProperties(BindingFlags.Instance | BindingFlags.Public);
            var resolved = names.Select(name => properties.SingleOrDefault(property => Naming.ConvertName(property.Name) == name)
                ?? throw new InvalidOperationException($"Unknown frozen compact column '{name}' for {typeof(T).Name}.")).ToArray();
            if (resolved.Length != properties.Length || resolved.Distinct().Count() != resolved.Length)
                throw new InvalidOperationException($"Frozen compact columns for {typeof(T).Name} do not cover its record properties exactly.");
            return resolved;
        }

        private static bool AllowsNull(PropertyInfo property)
        {
            return Nullable.GetUnderlyingType(property.PropertyType) is not null ||
                (!property.PropertyType.IsValueType && Nullability.Create(property).ReadState == NullabilityState.Nullable);
        }
    }
}
