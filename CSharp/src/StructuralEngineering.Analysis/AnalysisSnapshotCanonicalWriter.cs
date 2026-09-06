using System.Collections;
using System.Collections.Concurrent;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using System.Text.Json.Nodes;
using System.Text.Json.Serialization.Metadata;

namespace StructuralEngineering.Analysis;

public static partial class AnalysisSnapshotCodec
{
    private static readonly ConcurrentDictionary<Type, JsonPropertyInfo[]> CanonicalProperties = new();

    /// <summary>Writes the same PF4 bytes without a second JSON object graph or a whole-document UTF-16 string.</summary>
    public static void WriteCanonicalJson(Stream destination, object value)
        => WriteCanonicalJsonCore(destination, value, 16 * 1024);

    private static void WriteCanonicalJsonCore(Stream destination, object value, int bufferSize)
    {
        ArgumentNullException.ThrowIfNull(destination); ArgumentNullException.ThrowIfNull(value);
        using var writer = new StreamWriter(destination, new UTF8Encoding(false, true), bufferSize, leaveOpen: true);
        WriteCanonical(writer, value);
    }

    private static string CanonicalSha256(object value, params string[] excluded)
    {
        using var hash = SHA256.Create();
        using var sink = new CryptoStream(Stream.Null, hash, CryptoStreamMode.Write);
        // Most identity calls hash one small row. A document-sized buffer per row
        // would allocate gigabytes across a batch even though hashing is streamed.
        using (var writer = new StreamWriter(sink, new UTF8Encoding(false, true), 128, leaveOpen: true))
            WriteCanonical(writer, value, excluded);
        sink.FlushFinalBlock();
        return Convert.ToHexStringLower(hash.Hash!);
    }

    private static void WriteCanonical(TextWriter writer, object? value, IReadOnlyList<string>? excluded = null)
    {
        if (value is null) { writer.Write("null"); return; }
        if (value is JsonElement element) { WriteElement(writer, element, excluded); return; }
        if (value is JsonObject jsonObject) { WritePairs(writer, jsonObject.Select(pair => new KeyValuePair<string, object?>(pair.Key, pair.Value)), excluded); return; }
        if (value is JsonArray jsonArray) { WriteItems(writer, jsonArray); return; }
        if (value is JsonValue jsonValue) { WriteElement(writer, JsonSerializer.SerializeToElement(jsonValue, JsonOptions)); return; }
        if (value is string text) { writer.Write(CanonicalString(text)); return; }
        if (value is double number) { writer.Write(CanonicalNumber(number)); return; }
        if (value is bool boolean) { writer.Write(boolean ? "true" : "false"); return; }
        var type = value.GetType();
        var info = JsonOptions.GetTypeInfo(type);
        if (info.Kind == JsonTypeInfoKind.Dictionary)
        {
            WritePairs(writer, DictionaryPairs(value), excluded); return;
        }
        if (info.Kind == JsonTypeInfoKind.Enumerable) { WriteItems(writer, (IEnumerable)value); return; }
        if (info.Kind == JsonTypeInfoKind.Object)
        {
            var properties = CanonicalProperties.GetOrAdd(type, _ => info.Properties.Where(property => property.Get is not null)
                .OrderBy(property => property.Name, StringComparer.Ordinal).ToArray());
            writer.Write('{'); var first = true;
            foreach (var property in properties)
            {
                if (excluded?.Contains(property.Name, StringComparer.Ordinal) == true) continue;
                var item = property.Get!(value);
                if (property.ShouldSerialize?.Invoke(value, item) == false) continue;
                if (!first) writer.Write(','); first = false;
                writer.Write(CanonicalString(property.Name)); writer.Write(':'); WriteCanonical(writer, item);
            }
            writer.Write('}'); return;
        }
        // Enum/date/numeric scalar converters retain the serializer's frozen token rules.
        WriteElement(writer, JsonSerializer.SerializeToElement(value, type, JsonOptions));
    }

    private static IEnumerable<KeyValuePair<string, object?>> DictionaryPairs(object value)
    {
        if (value is IDictionary dictionary)
        {
            foreach (DictionaryEntry entry in dictionary)
                yield return new(entry.Key as string ?? throw new ArgumentException("Portable dictionary keys must be strings."), entry.Value);
        }
        else
        {
            foreach (var entry in (IEnumerable)value)
            {
                var type = entry.GetType();
                yield return new(type.GetProperty("Key")!.GetValue(entry) as string ?? throw new ArgumentException("Portable dictionary keys must be strings."),
                    type.GetProperty("Value")!.GetValue(entry));
            }
        }
    }

    private static void WritePairs(TextWriter writer, IEnumerable<KeyValuePair<string, object?>> pairs, IReadOnlyList<string>? excluded)
    {
        writer.Write('{'); var first = true;
        foreach (var pair in pairs.OrderBy(pair => pair.Key, StringComparer.Ordinal))
        {
            if (excluded?.Contains(pair.Key, StringComparer.Ordinal) == true) continue;
            if (!first) writer.Write(','); first = false;
            writer.Write(CanonicalString(pair.Key)); writer.Write(':'); WriteCanonical(writer, pair.Value);
        }
        writer.Write('}');
    }

    private static void WriteItems(TextWriter writer, IEnumerable items)
    {
        writer.Write('['); var first = true;
        foreach (var item in items)
        {
            if (!first) writer.Write(','); first = false;
            WriteCanonical(writer, item);
        }
        writer.Write(']');
    }

    private static void WriteElement(TextWriter writer, JsonElement value, IReadOnlyList<string>? excluded = null)
    {
        switch (value.ValueKind)
        {
            case JsonValueKind.Object:
                WritePairs(writer, value.EnumerateObject().Select(property => new KeyValuePair<string, object?>(property.Name, property.Value)), excluded); break;
            case JsonValueKind.Array: WriteItems(writer, value.EnumerateArray()); break;
            case JsonValueKind.String: writer.Write(CanonicalString(value.GetString()!)); break;
            case JsonValueKind.Number: writer.Write(CanonicalNumber(value.GetDouble())); break;
            case JsonValueKind.True: writer.Write("true"); break;
            case JsonValueKind.False: writer.Write("false"); break;
            case JsonValueKind.Null: writer.Write("null"); break;
            default: throw new ArgumentException("Undefined JSON cannot enter canonical evidence.");
        }
    }
}
