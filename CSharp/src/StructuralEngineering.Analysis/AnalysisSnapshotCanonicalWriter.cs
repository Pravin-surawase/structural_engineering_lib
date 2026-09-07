using System.Collections;
using System.Collections.Concurrent;
using System.Buffers;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using System.Text.Json.Nodes;
using System.Text.Json.Serialization.Metadata;
using System.Text.Encodings.Web;
using StructuralEngineering.Contracts;

namespace StructuralEngineering.Analysis;

public static partial class AnalysisSnapshotCodec
{
    private static readonly ConcurrentDictionary<Type, CanonicalProperty[]> CanonicalProperties = new();
    private static readonly JsonWriterOptions CanonicalWriterOptions = new()
    {
        Encoder = Pf4JavaScriptEncoder.Instance,
        SkipValidation = true
    };
    private sealed record CanonicalProperty(JsonPropertyInfo Property, JsonEncodedText SerializedName);

    /// <summary>Writes the same PF4 bytes without a second JSON object graph or a whole-document UTF-16 string.</summary>
    public static void WriteCanonicalJson(Stream destination, object value)
        => WriteCanonicalJsonCore(destination, value, 16 * 1024);

    private static void WriteCanonicalJsonCore(Stream destination, object value, int bufferSize)
    {
        ArgumentNullException.ThrowIfNull(destination); ArgumentNullException.ThrowIfNull(value);
        using var output = new PooledStreamBuffer(destination, bufferSize);
        using var writer = new Utf8JsonWriter(output, CanonicalWriterOptions);
        WriteCanonical(writer, value); writer.Flush();
    }

    private static string CanonicalSha256(object value, params string[] excluded)
    {
        using var hash = IncrementalHash.CreateHash(HashAlgorithmName.SHA256);
        using var sink = new CanonicalHashSink(hash);
        // Most identity calls hash one small row. A document-sized buffer per row
        // would allocate gigabytes across a batch even though hashing is streamed.
        var bufferSize = value is AnalysisSnapshot or RawAnalysisCapture or SnapshotCallLedger or SourceSnapshotMetadata ? 16 * 1024 : 128;
        using var output = new PooledStreamBuffer(sink, bufferSize);
        using (var writer = new Utf8JsonWriter(output, CanonicalWriterOptions))
        {
            WriteCanonical(writer, value, excluded);
            writer.Flush();
        }
        return Convert.ToHexStringLower(hash.GetHashAndReset());
    }


    // CryptoStream routes even synchronous writes through an async state machine.
    // A document hash otherwise allocates on every small encoder flush. This sink
    // appends exactly those UTF-8 bytes synchronously, with no identity-rule change.
    private sealed class CanonicalHashSink(IncrementalHash hash) : Stream
    {
        public override bool CanRead => false;
        public override bool CanSeek => false;
        public override bool CanWrite => true;
        public override long Length => throw new NotSupportedException();
        public override long Position { get => throw new NotSupportedException(); set => throw new NotSupportedException(); }
        public override void Write(byte[] buffer, int offset, int count) => hash.AppendData(buffer, offset, count);
        public override void Write(ReadOnlySpan<byte> buffer) => hash.AppendData(buffer);
        public override void Flush() { }
        public override int Read(byte[] buffer, int offset, int count) => throw new NotSupportedException();
        public override long Seek(long offset, SeekOrigin origin) => throw new NotSupportedException();
        public override void SetLength(long value) => throw new NotSupportedException();
    }

    private static void WriteCanonical(Utf8JsonWriter writer, object? value, IReadOnlyList<string>? excluded = null)
    {
        if (value is null) { writer.WriteNullValue(); return; }
        if (value is JsonElement element) { WriteElement(writer, element, excluded); return; }
        if (value is JsonObject jsonObject) { WritePairs(writer, jsonObject.Select(pair => new KeyValuePair<string, object?>(pair.Key, pair.Value)), excluded); return; }
        if (value is JsonArray jsonArray) { WriteItems(writer, jsonArray); return; }
        if (value is JsonValue jsonValue) { WriteElement(writer, JsonSerializer.SerializeToElement(jsonValue, JsonOptions)); return; }
        if (value is string text) { WriteCanonicalString(writer, text); return; }
        if (value is double number) { writer.WriteRawValue(CanonicalNumber(number), skipInputValidation: true); return; }
        if (value is bool boolean) { writer.WriteBooleanValue(boolean); return; }
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
                .OrderBy(property => property.Name, StringComparer.Ordinal)
                .Select(property => new CanonicalProperty(property, JsonEncodedText.Encode(property.Name, Pf4JavaScriptEncoder.Instance))).ToArray());
            writer.WriteStartObject();
            foreach (var property in properties)
            {
                if (excluded?.Contains(property.Property.Name, StringComparer.Ordinal) == true) continue;
                var item = property.Property.Get!(value);
                if (property.Property.ShouldSerialize?.Invoke(value, item) == false) continue;
                writer.WritePropertyName(property.SerializedName); WriteCanonical(writer, item);
            }
            writer.WriteEndObject(); return;
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

    private static void WritePairs(Utf8JsonWriter writer, IEnumerable<KeyValuePair<string, object?>> pairs, IReadOnlyList<string>? excluded)
    {
        writer.WriteStartObject();
        foreach (var pair in pairs.OrderBy(pair => pair.Key, StringComparer.Ordinal))
        {
            if (excluded?.Contains(pair.Key, StringComparer.Ordinal) == true) continue;
            // JsonEncodedText invokes the frozen PF4 encoder for arbitrary source-evidence keys.
            if (!IsAscii(pair.Key)) _ = CanonicalString(pair.Key); // retain PF4's invalid-surrogate rejection.
            writer.WritePropertyName(pair.Key); WriteCanonical(writer, pair.Value);
        }
        writer.WriteEndObject();
    }

    private static void WriteItems(Utf8JsonWriter writer, IEnumerable items)
    {
        writer.WriteStartArray();
        foreach (var item in items)
        {
            WriteCanonical(writer, item);
        }
        writer.WriteEndArray();
    }

    private static void WriteElement(Utf8JsonWriter writer, JsonElement value, IReadOnlyList<string>? excluded = null)
    {
        switch (value.ValueKind)
        {
            case JsonValueKind.Object:
                WritePairs(writer, value.EnumerateObject().Select(property => new KeyValuePair<string, object?>(property.Name, property.Value)), excluded); break;
            case JsonValueKind.Array: WriteItems(writer, value.EnumerateArray()); break;
            case JsonValueKind.String: WriteCanonicalString(writer, value.GetString()!); break;
            case JsonValueKind.Number: writer.WriteRawValue(CanonicalNumber(value.GetDouble()), skipInputValidation: true); break;
            case JsonValueKind.True: writer.WriteBooleanValue(true); break;
            case JsonValueKind.False: writer.WriteBooleanValue(false); break;
            case JsonValueKind.Null: writer.WriteNullValue(); break;
            default: throw new ArgumentException("Undefined JSON cannot enter canonical evidence.");
        }
    }

    private static void WriteCanonicalString(Utf8JsonWriter writer, string value)
    {
        if (IsAscii(value)) writer.WriteStringValue(value);
        else writer.WriteRawValue(CanonicalString(value), skipInputValidation: true);
    }

    private static bool IsAscii(string value) => value.All(character => character is >= ' ' and <= '~');

    /// <summary>Bounded bridge from Utf8JsonWriter to a stream: every Advance is written immediately.</summary>
    private sealed class PooledStreamBuffer(Stream destination, int initialSize) : IBufferWriter<byte>, IDisposable
    {
        private byte[] _buffer = ArrayPool<byte>.Shared.Rent(initialSize);
        public void Advance(int count)
        {
            if ((uint)count > (uint)_buffer.Length) throw new ArgumentOutOfRangeException(nameof(count));
            destination.Write(_buffer.AsSpan(0, count));
        }
        public Memory<byte> GetMemory(int sizeHint = 0) => GetBuffer(sizeHint);
        public Span<byte> GetSpan(int sizeHint = 0) => GetBuffer(sizeHint).Span;
        private Memory<byte> GetBuffer(int sizeHint)
        {
            var required = Math.Max(1, sizeHint);
            if (required <= _buffer.Length) return _buffer;
            var replacement = ArrayPool<byte>.Shared.Rent(required);
            ArrayPool<byte>.Shared.Return(_buffer); _buffer = replacement;
            return _buffer;
        }
        public void Dispose()
        {
            if (_buffer.Length != 0) { ArrayPool<byte>.Shared.Return(_buffer); _buffer = []; }
        }
    }

    /// <summary>Minimal PF4 string encoder: only JSON's required ASCII escapes are encoded.</summary>
    private sealed unsafe class Pf4JavaScriptEncoder : JavaScriptEncoder
    {
        internal static readonly Pf4JavaScriptEncoder Instance = new();
        public override int MaxOutputCharactersPerInputCharacter => 6;
        public override bool WillEncode(int unicodeScalar) => unicodeScalar < 0x20 || unicodeScalar is '"' or '\\';
        public override int FindFirstCharacterToEncode(char* text, int textLength)
        {
            for (var index = 0; index < textLength; index++) if (WillEncode(text[index])) return index;
            return -1;
        }
        public override bool TryEncodeUnicodeScalar(int unicodeScalar, char* buffer, int bufferLength, out int numberOfCharactersWritten)
        {
            var escaped = unicodeScalar switch
            {
                '"' => "\\\"", '\\' => "\\\\", '\b' => "\\b", '\f' => "\\f", '\n' => "\\n", '\r' => "\\r", '\t' => "\\t", _ => null
            };
            if (escaped is not null)
            {
                if (bufferLength < escaped.Length) { numberOfCharactersWritten = 0; return false; }
                escaped.AsSpan().CopyTo(new Span<char>(buffer, escaped.Length)); numberOfCharactersWritten = escaped.Length; return true;
            }
            if (unicodeScalar is < 0 or >= 0x20 || bufferLength < 6) { numberOfCharactersWritten = 0; return false; }
            buffer[0] = '\\'; buffer[1] = 'u'; buffer[2] = '0'; buffer[3] = '0';
            buffer[4] = Hex(unicodeScalar >> 4); buffer[5] = Hex(unicodeScalar); numberOfCharactersWritten = 6; return true;
        }
        private static char Hex(int value) => "0123456789abcdef"[value & 15];
    }
}
