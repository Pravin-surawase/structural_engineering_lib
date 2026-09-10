using System.Diagnostics;
using System.Runtime.Loader;
using System.Security.Cryptography;
using System.Text.Json;
using StructuralEngineering.Etabs;

internal static class ApiInventoryCommand
{
    public static async Task<int> Run(string assemblyPath, string responsePath, bool includeAllInterfaces = false)
    {
        string? temporary = null;
        AssemblyLoadContext? discoveryContext = null;
        try
        {
            var source = Path.GetFullPath(assemblyPath);
            var output = Path.GetFullPath(responsePath);
            if (File.Exists(output)) throw new IOException("The inventory output already exists; choose a new evidence path.");
            var sourceHash = await Hash(source);
            // An isolated context binds this load to the requested external file even in a single-file worker.
            discoveryContext = new AssemblyLoadContext("ETABS API discovery", isCollectible: true);
            var assembly = discoveryContext.LoadFromAssemblyPath(source);
            var inventory = includeAllInterfaces ? EtabsApiDiscovery.InspectAll(assembly) : EtabsApiDiscovery.Inspect(assembly);
            if (assembly.GetType("ETABSv1.cSapModel", throwOnError: false) is null)
                throw new InvalidDataException("The requested assembly does not expose the ETABSv1.cSapModel interface.");
            var fileVersion = FileVersionInfo.GetVersionInfo(source).FileVersion;
            if (sourceHash != await Hash(source)) throw new IOException("The source assembly changed during discovery.");
            var bytes = JsonSerializer.SerializeToUtf8Bytes(new
            {
                sourceAssemblyPath = source,
                sourceAssemblySha256 = sourceHash,
                sourceAssemblyFileVersion = fileVersion,
                recordedUtc = DateTimeOffset.UtcNow,
                inventory
            }, new JsonSerializerOptions { WriteIndented = true });
            Directory.CreateDirectory(Path.GetDirectoryName(output)!);
            temporary = output + "." + Guid.NewGuid().ToString("N") + ".tmp";
            await using (var stream = new FileStream(temporary, FileMode.CreateNew, FileAccess.Write, FileShare.None))
            {
                await stream.WriteAsync(bytes);
                stream.Flush(flushToDisk: true);
            }
            File.Move(temporary, output, overwrite: false);
            temporary = null;
            Console.WriteLine($"API metadata written: {inventory.Members.Count(x => x.Methods.Count > 0)}/{inventory.Members.Count} catalogued names present; no target methods invoked.");
            return 0;
        }
        catch (Exception exception)
        {
            Console.Error.WriteLine($"API inventory failed: {exception.GetType().Name}: {exception.Message}");
            return 1;
        }
        finally
        {
            discoveryContext?.Unload();
            if (temporary is not null && File.Exists(temporary)) File.Delete(temporary);
        }
    }

    private static async Task<string> Hash(string path)
    {
        await using var stream = File.OpenRead(path);
        return Convert.ToHexStringLower(await SHA256.HashDataAsync(stream));
    }
}
