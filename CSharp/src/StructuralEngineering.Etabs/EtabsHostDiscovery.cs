using System.Diagnostics;
using System.Reflection;
using System.Runtime.InteropServices;
using System.Security.Cryptography;
using StructuralEngineering.Contracts;

namespace StructuralEngineering.Etabs;

/// <summary>Builds a strict host expectation from one already user-selected ETABS PID. It never enumerates or launches processes.</summary>
public static class EtabsHostDiscovery
{
    public static EtabsHostExpectation Discover(EtabsProcessTarget target)
    {
        ArgumentNullException.ThrowIfNull(target);
        if (!OperatingSystem.IsWindows())
            throw new PlatformNotSupportedException("ETABS discovery requires Windows.");

        using var process = Process.GetProcessById(target.ProcessId);
        var started = new DateTimeOffset(process.StartTime.ToUniversalTime(), TimeSpan.Zero);
        var executable = process.MainModule?.FileName ?? throw new InvalidOperationException("The ETABS executable path is unavailable.");
        Require(target.ProcessStartedUtc == started, "Selected ETABS process start differs.");
        Require(PathsEqual(target.ExecutablePath, executable), "Selected ETABS executable differs.");
        Require(string.Equals(target.ExecutableSha256, Sha256File(executable), StringComparison.Ordinal), "Selected ETABS executable digest differs.");

        var directory = Path.GetDirectoryName(executable) ?? throw new InvalidOperationException("The ETABS executable has no directory.");
        var apiPath = Path.Combine(directory, "ETABSv1.dll");
        var typeLibraryPath = Path.Combine(directory, "NativeAPI", "x64", "ETABSv1.tlb");
        Require(File.Exists(apiPath) && File.Exists(typeLibraryPath), "The selected ETABS API files are absent.");
        var assembly = Assembly.LoadFrom(apiPath);
        var helper = Activator.CreateInstance(RequireType(assembly, "ETABSv1.Helper"))
            ?? throw new InvalidOperationException("ETABS helper activation returned null.");
        object? oapi = null;
        object? sapModel = null;
        try
        {
            oapi = RequireType(assembly, "ETABSv1.cHelper").GetMethod("GetObjectProcess")!.Invoke(helper, ["CSI.ETABS.API.ETABSObject", target.ProcessId])
                ?? throw new InvalidOperationException("Exact-PID ETABS attachment returned null.");
            sapModel = RequireType(assembly, "ETABSv1.cOAPI").GetProperty("SapModel")!.GetValue(oapi)
                ?? throw new InvalidOperationException("The selected ETABS process returned no SapModel.");
            var sap = RequireType(assembly, "ETABSv1.cSapModel");
            var modelPath = (string?)sap.GetMethod("GetModelFilename")!.Invoke(sapModel, [true]);
            Require(!string.IsNullOrWhiteSpace(modelPath) && File.Exists(modelPath), "The selected ETABS model is not a saved readable file.");
            var locked = (bool)sap.GetMethod("GetModelIsLocked")!.Invoke(sapModel, null)!;
            var units = Convert.ToInt32(sap.GetMethod("GetPresentUnits")!.Invoke(sapModel, null), System.Globalization.CultureInfo.InvariantCulture);
            var versionArgs = new object?[] { null, 0d };
            var versionStatus = sap.GetMethod("GetVersion")!.Invoke(sapModel, versionArgs);
            var version = versionArgs[0] as string;
            Require(versionStatus is int status && status == 0 && !string.IsNullOrWhiteSpace(version), "ETABS GetVersion returned an unsupported shape.");
            var model = new FileInfo(modelPath!);
            return new(target.ProcessId, started, executable,
                FileVersionInfo.GetVersionInfo(executable).FileVersion ?? string.Empty, new FileInfo(executable).Length, Sha256File(executable),
                apiPath, assembly.FullName ?? string.Empty, FileVersionInfo.GetVersionInfo(apiPath).FileVersion ?? string.Empty, Sha256File(apiPath),
                typeLibraryPath, new FileInfo(typeLibraryPath).Length, Sha256File(typeLibraryPath),
                model.FullName, model.Length, new DateTimeOffset(model.LastWriteTimeUtc, TimeSpan.Zero), Sha256File(model.FullName),
                version!, locked, units);
        }
        finally
        {
            Release(sapModel);
            Release(oapi);
            Release(helper);
        }
    }

    private static Type RequireType(Assembly assembly, string name) => assembly.GetType(name, throwOnError: true) ?? throw new TypeLoadException(name);
    private static void Require(bool condition, string message)
    {
        if (!condition) throw new InvalidOperationException(message);
    }
    private static bool PathsEqual(string left, string right) => string.Equals(Path.GetFullPath(left), Path.GetFullPath(right), StringComparison.OrdinalIgnoreCase);
    private static string Sha256File(string path)
    {
        using var stream = File.OpenRead(path);
        return Convert.ToHexStringLower(SHA256.HashData(stream));
    }
    private static void Release(object? value)
    {
        if (value is not null && Marshal.IsComObject(value)) Marshal.FinalReleaseComObject(value);
    }
}
