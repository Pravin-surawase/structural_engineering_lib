using System.Security.Cryptography;
using System.Text.Json;
using StructuralEngineering.Contracts;

namespace StructuralEngineering.Etabs;

public sealed record EtabsContextCaptureRequest(string RequestSha256, DateTimeOffset DeadlineUtc);

public static class EtabsContextCapture
{
    private const string Coverage = "source_geometry_only;supports=absent;spans=absent;offsets=absent;releases=absent;loads=absent;analysis=absent;strengths=absent";

    public static EtabsContextInventory Run(IEtabsGetterHost host, EtabsContextCaptureRequest request, CancellationToken cancellationToken = default)
    {
        ArgumentNullException.ThrowIfNull(host);
        ArgumentNullException.ThrowIfNull(request);
        if (string.IsNullOrWhiteSpace(request.RequestSha256)) throw new ArgumentException("Context request identity is required.", nameof(request));
        var adapter = new EtabsGetterAdapter(host, EtabsContextGetterMatrix.Allowed);
        var before = ReadState(adapter, request, cancellationToken);
        var frames = before.Frames;
        var points = before.Points;
        var orientations = frames.Rows.Select(row => row.Name).ToDictionary(name => name, name => Orientation(adapter, request, name, cancellationToken), StringComparer.Ordinal);
        var materials = frames.SectionNames.ToDictionary(section => section, section => Material(adapter, request, section, cancellationToken), StringComparer.Ordinal);
        var after = ReadState(adapter, request, cancellationToken);
        var postOrientations = after.Frames.Rows.Select(row => row.Name).ToDictionary(name => name, name => Orientation(adapter, request, name, cancellationToken), StringComparer.Ordinal);
        var postMaterials = after.Frames.SectionNames.ToDictionary(section => section, section => Material(adapter, request, section, cancellationToken), StringComparer.Ordinal);
        var finalState = ReadState(adapter, request, cancellationToken);
        if (before.Identity != after.Identity || before.Locked != after.Locked || before.PresentUnits != after.PresentUnits ||
            before.DatabaseUnits != after.DatabaseUnits || !Same(frames, after.Frames) || !Same(points, after.Points) ||
            !orientations.OrderBy(item => item.Key).SequenceEqual(postOrientations.OrderBy(item => item.Key)) ||
            !materials.OrderBy(item => item.Key).SequenceEqual(postMaterials.OrderBy(item => item.Key)) || host.InspectIdentity() != before.Identity ||
            finalState.Locked != before.Locked || finalState.PresentUnits != before.PresentUnits || finalState.DatabaseUnits != before.DatabaseUnits ||
            !Same(frames, finalState.Frames) || !Same(points, finalState.Points))
            throw new InvalidOperationException("The model, units, or bulk context changed during capture.");

        var source = new EtabsContextSourceIdentity(before.Identity.ProcessId, before.Identity.ProcessStartedUtc, before.Identity.ExecutablePath,
            before.Identity.ExecutableSha256, before.Identity.ModelPath, before.Identity.ModelBytes, before.Identity.ModelModifiedUtc,
            before.Identity.ModelSha256, before.Identity.EtabsApiVersion, before.Locked, before.PresentUnits, before.DatabaseUnits);
        var sections = frames.SectionNames.Order(StringComparer.Ordinal).Select(section => new EtabsContextSection(section, materials[section])).ToArray();
        var contextFrames = frames.Rows.Select(row => new EtabsContextFrame(row.Name, row.Section, row.Story, row.Point1, row.Point2, orientations[row.Name])).ToArray();
        var contextPoints = points.Rows.Select(row => new EtabsContextPoint(row.Name, Mm(row.X), Mm(row.Y), Mm(row.Z))).ToArray();
        return new EtabsContextInventory(request.RequestSha256, DateTimeOffset.UtcNow, source, contextPoints, contextFrames, sections, Coverage);
    }

    private static State ReadState(EtabsGetterAdapter adapter, EtabsContextCaptureRequest request, CancellationToken token)
    {
        var model = Call(adapter, request, "SapModel.GetModelFilename", [true], token);
        var identity = model.HostIdentity;
        var path = (string)model.DirectValue!;
        var locked = Direct<bool>(adapter, request, "SapModel.GetModelIsLocked", [], token);
        var present = Direct<int>(adapter, request, "SapModel.GetPresentUnits", [], token);
        var database = Direct<int>(adapter, request, "SapModel.GetDatabaseUnits", [], token);
        if (!string.Equals(Path.GetFullPath(path), Path.GetFullPath(identity.ModelPath), StringComparison.OrdinalIgnoreCase) || present != 6 || database != 6)
            throw new InvalidOperationException("Context capture supports only the observed saved model in ETABS unit profile 6 (kN-m-C).");
        return new(identity, locked, present, database, Frames(adapter, request, token), Points(adapter, request, token));
    }

    private static BulkFrames Frames(EtabsGetterAdapter adapter, EtabsContextCaptureRequest request, CancellationToken token)
    {
        var call = Call(adapter, request, "FrameObj.GetAllFrames", ["Global"], token);
        var count = Int(call, 0); var outputs = call.Outputs;
        var rows = Enumerable.Range(0, count).Select(index => new FrameRow(Text(outputs, 1, index), Text(outputs, 2, index), Text(outputs, 3, index), Text(outputs, 4, index), Text(outputs, 5, index))).ToArray();
        if (rows.Any(row => string.IsNullOrWhiteSpace(row.Name) || string.IsNullOrWhiteSpace(row.Section) || string.IsNullOrWhiteSpace(row.Story) || string.IsNullOrWhiteSpace(row.Point1) || string.IsNullOrWhiteSpace(row.Point2) || row.Point1 == row.Point2) || rows.Select(row => row.Name).Distinct(StringComparer.Ordinal).Count() != rows.Length)
            throw new InvalidOperationException("GetAllFrames returned incomplete or duplicate source identities.");
        if (Enumerable.Range(6, 13).SelectMany(output => ((object?[])outputs[output]!).Cast<double>()).Any(value => !double.IsFinite(value)))
            throw new InvalidOperationException("GetAllFrames returned a non-finite source coordinate or offset.");
        return new(rows, rows.Select(row => row.Section).Distinct(StringComparer.Ordinal).Order(StringComparer.Ordinal).ToArray(), Shape(call));
    }

    private static BulkPoints Points(EtabsGetterAdapter adapter, EtabsContextCaptureRequest request, CancellationToken token)
    {
        var call = Call(adapter, request, "PointObj.GetAllPoints", ["Global"], token);
        var count = Int(call, 0); var outputs = call.Outputs;
        var rows = Enumerable.Range(0, count).Select(index => new PointRow(Text(outputs, 1, index), Number(outputs, 2, index), Number(outputs, 3, index), Number(outputs, 4, index))).ToArray();
        if (rows.Any(row => string.IsNullOrWhiteSpace(row.Name) || !double.IsFinite(row.X) || !double.IsFinite(row.Y) || !double.IsFinite(row.Z)) || rows.Select(row => row.Name).Distinct(StringComparer.Ordinal).Count() != rows.Length)
            throw new InvalidOperationException("GetAllPoints returned incomplete, duplicate, or non-finite source coordinates.");
        return new(rows, Shape(call));
    }

    private static EtabsFrameDesignOrientation Orientation(EtabsGetterAdapter adapter, EtabsContextCaptureRequest request, string name, CancellationToken token)
    {
        var call = Call(adapter, request, "FrameObj.GetDesignOrientation", [name], token);
        var value = Int(call, 0);
        return value is >= 1 and <= 5 ? (EtabsFrameDesignOrientation)value : throw new InvalidOperationException("Frame design orientation is unsupported.");
    }
    private static string Material(EtabsGetterAdapter adapter, EtabsContextCaptureRequest request, string section, CancellationToken token) =>
        Call(adapter, request, "PropFrame.GetMaterial", [section], token).Outputs[0] as string ?? throw new InvalidOperationException("A section has no source material identity.");
    private static T Direct<T>(EtabsGetterAdapter adapter, EtabsContextCaptureRequest request, string operation, IReadOnlyList<object?> inputs, CancellationToken token) => (T)(Call(adapter, request, operation, inputs, token).DirectValue ?? throw new InvalidOperationException($"{operation} returned null."));
    private static EtabsRawGetterCall Call(EtabsGetterAdapter adapter, EtabsContextCaptureRequest request, string operation, IReadOnlyList<object?> inputs, CancellationToken token)
    {
        var result = adapter.Read(operation, inputs, request.DeadlineUtc, token);
        return result.State == EtabsGetterState.Completed && result.RawCall is not null ? result.RawCall : throw new InvalidOperationException($"{result.DiagnosticCode}: {result.Message}");
    }
    private static int Int(EtabsRawGetterCall call, int index) => (int)call.Outputs[index]!;
    private static string Text(IReadOnlyList<object?> outputs, int index, int item) => ((object?[])outputs[index]!)[item] as string ?? throw new InvalidOperationException("A source identifier is null.");
    private static double Number(IReadOnlyList<object?> outputs, int index, int item) => (double)((object?[])outputs[index]!)[item]!;
    private static string Shape(EtabsRawGetterCall call) => Convert.ToHexStringLower(SHA256.HashData(JsonSerializer.SerializeToUtf8Bytes(call.Outputs)));
    private static double Mm(double meters) => meters * 1000d;
    private static bool Same(BulkFrames left, BulkFrames right) => left.Rows.SequenceEqual(right.Rows) && left.SectionNames.SequenceEqual(right.SectionNames) && left.Shape == right.Shape;
    private static bool Same(BulkPoints left, BulkPoints right) => left.Rows.SequenceEqual(right.Rows) && left.Shape == right.Shape;
    private sealed record State(EtabsHostIdentity Identity, bool Locked, int PresentUnits, int DatabaseUnits, BulkFrames Frames, BulkPoints Points);
    private sealed record BulkFrames(IReadOnlyList<FrameRow> Rows, IReadOnlyList<string> SectionNames, string Shape);
    private sealed record BulkPoints(IReadOnlyList<PointRow> Rows, string Shape);
    private sealed record FrameRow(string Name, string Section, string Story, string Point1, string Point2);
    private sealed record PointRow(string Name, double X, double Y, double Z);
}
