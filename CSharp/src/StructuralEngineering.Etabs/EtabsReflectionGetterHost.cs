using System.Diagnostics;
using System.Reflection;
using System.Runtime.InteropServices;
using System.Security.Cryptography;

namespace StructuralEngineering.Etabs;

public sealed record EtabsHostExpectation(
    int ProcessId,
    DateTimeOffset ProcessStartedUtc,
    string ExecutablePath,
    string ExecutableFileVersion,
    long ExecutableBytes,
    string ExecutableSha256,
    string ApiAssemblyPath,
    string ApiAssemblyIdentity,
    string ApiFileVersion,
    string ApiSha256,
    string TypeLibraryPath,
    long TypeLibraryBytes,
    string TypeLibrarySha256,
    string ModelPath,
    long ModelBytes,
    DateTimeOffset ModelModifiedUtc,
    string ModelSha256,
    string EtabsApiVersion,
    bool ModelLocked,
    int PresentUnits);

public sealed class EtabsReflectionGetterHost : IEtabsGetterHost
{
    private const string EtabsProgId = "CSI.ETABS.API.ETABSObject";
    private readonly Assembly _apiAssembly;
    private readonly object _helper;
    private readonly object _oapi;
    private readonly object _sapModel;
    private readonly Dictionary<string, object> _objectCache = new(StringComparer.Ordinal);
    private readonly List<object> _releaseOrder = [];
    private bool _disposed;

    private EtabsReflectionGetterHost(
        Assembly apiAssembly,
        object helper,
        object oapi,
        object sapModel,
        EtabsHostIdentity identity)
    {
        _apiAssembly = apiAssembly;
        _helper = helper;
        _oapi = oapi;
        _sapModel = sapModel;
        Identity = identity;
        _objectCache["SapModel"] = sapModel;
        Track(helper);
        Track(oapi);
        Track(sapModel);
    }

    public EtabsHostIdentity Identity { get; }

    public EtabsHostIdentity InspectIdentity()
    {
        ObjectDisposedException.ThrowIf(_disposed, this);
        using var process = Process.GetProcessById(Identity.ProcessId);
        var executable = process.MainModule?.FileName
            ?? throw new InvalidOperationException("The ETABS executable path is unavailable.");
        var model = new FileInfo(Identity.ModelPath);
        return Identity with
        {
            ProcessStartedUtc = new DateTimeOffset(process.StartTime.ToUniversalTime(), TimeSpan.Zero),
            ExecutablePath = executable,
            ExecutableFileVersion = FileVersionInfo.GetVersionInfo(executable).FileVersion ?? string.Empty,
            ExecutableBytes = new FileInfo(executable).Length,
            ExecutableSha256 = Sha256File(executable),
            ModelBytes = model.Length,
            ModelModifiedUtc = new DateTimeOffset(model.LastWriteTimeUtc, TimeSpan.Zero),
            ModelSha256 = Sha256File(model.FullName)
        };
    }

    public static EtabsReflectionGetterHost Attach(EtabsHostExpectation expected)
    {
        ArgumentNullException.ThrowIfNull(expected);
        if (!OperatingSystem.IsWindows())
            throw new PlatformNotSupportedException("The ETABS host adapter requires Windows.");

        ValidateExpectedFiles(expected);
        using var process = Process.GetProcessById(expected.ProcessId);
        var processStart = new DateTimeOffset(process.StartTime.ToUniversalTime(), TimeSpan.Zero);
        var executable = process.MainModule?.FileName
            ?? throw new InvalidOperationException("The ETABS executable path is unavailable.");
        var executableVersion = FileVersionInfo.GetVersionInfo(executable).FileVersion ?? string.Empty;
        RequireEqual("process start", expected.ProcessStartedUtc, processStart);
        RequirePath("executable", expected.ExecutablePath, executable);
        RequireEqual("executable version", expected.ExecutableFileVersion, executableVersion);
        RequireEqual("executable byte count", expected.ExecutableBytes, new FileInfo(executable).Length);
        RequireEqual("executable SHA-256", expected.ExecutableSha256, Sha256File(executable));

        var assembly = Assembly.LoadFrom(Path.GetFullPath(expected.ApiAssemblyPath));
        RequireEqual("API assembly identity", expected.ApiAssemblyIdentity, assembly.FullName ?? string.Empty);
        ValidateMatrix(assembly);

        object? helper = null;
        object? oapi = null;
        object? sapModel = null;
        try
        {
            var helperType = RequireType(assembly, "ETABSv1.Helper");
            var helperInterface = RequireType(assembly, "ETABSv1.cHelper");
            var oapiInterface = RequireType(assembly, "ETABSv1.cOAPI");
            var sapInterface = RequireType(assembly, "ETABSv1.cSapModel");
            helper = Activator.CreateInstance(helperType)
                ?? throw new InvalidOperationException("ETABS helper activation returned null.");
            oapi = helperInterface.GetMethod("GetObjectProcess")!.Invoke(
                helper, [EtabsProgId, expected.ProcessId])
                ?? throw new InvalidOperationException("Exact-PID ETABS attachment returned null.");
            sapModel = oapiInterface.GetProperty("SapModel")!.GetValue(oapi)
                ?? throw new InvalidOperationException("The attached ETABS process returned no SapModel.");

            var modelPath = (string?)sapInterface.GetMethod("GetModelFilename")!.Invoke(sapModel, [true])
                ?? throw new InvalidOperationException("ETABS returned no model filename.");
            var locked = (bool)sapInterface.GetMethod("GetModelIsLocked")!.Invoke(sapModel, null)!;
            var presentUnits = Convert.ToInt32(
                sapInterface.GetMethod("GetPresentUnits")!.Invoke(sapModel, null),
                System.Globalization.CultureInfo.InvariantCulture);
            var versionArguments = new object?[] { null, 0d };
            var versionStatus = sapInterface.GetMethod("GetVersion")!.Invoke(sapModel, versionArguments);
            if (versionStatus is not int exactStatus || exactStatus != 0 || versionArguments[0] is not string apiVersion)
                throw new InvalidOperationException("ETABS GetVersion did not return a successful exact shape.");

            RequirePath("model", expected.ModelPath, modelPath);
            RequireEqual("model lock", expected.ModelLocked, locked);
            RequireEqual("present units", expected.PresentUnits, presentUnits);
            RequireEqual("ETABS API version", expected.EtabsApiVersion, apiVersion);
            ValidateModelFile(expected, modelPath);

            var identity = new EtabsHostIdentity(
                expected.ProcessId,
                processStart,
                executable,
                executableVersion,
                new FileInfo(executable).Length,
                Sha256File(executable),
                Path.GetFullPath(expected.ApiAssemblyPath),
                assembly.FullName ?? string.Empty,
                FileVersionInfo.GetVersionInfo(expected.ApiAssemblyPath).FileVersion ?? string.Empty,
                Sha256File(expected.ApiAssemblyPath),
                Path.GetFullPath(expected.TypeLibraryPath),
                new FileInfo(expected.TypeLibraryPath).Length,
                Sha256File(expected.TypeLibraryPath),
                modelPath,
                new FileInfo(modelPath).Length,
                new DateTimeOffset(File.GetLastWriteTimeUtc(modelPath), TimeSpan.Zero),
                Sha256File(modelPath),
                apiVersion,
                locked,
                presentUnits);
            return new EtabsReflectionGetterHost(assembly, helper, oapi, sapModel, identity);
        }
        catch (Exception attachException)
        {
            var cleanupErrors = ReleaseAll([sapModel, oapi, helper]);
            if (cleanupErrors.Count > 0)
                throw new AggregateException(
                    "ETABS attachment failed and one or more acquired COM references could not be released.",
                    [attachException, .. cleanupErrors]);
            throw;
        }
    }

    public EtabsInvocation Invoke(
        EtabsGetterDefinition definition,
        IReadOnlyList<object?> inputs,
        CancellationToken cancellationToken)
    {
        ObjectDisposedException.ThrowIf(_disposed, this);
        cancellationToken.ThrowIfCancellationRequested();
        if (!EtabsGetterMatrix.Allowed.TryGetValue(definition.Operation, out var frozen) || frozen != definition)
            throw new InvalidOperationException("Only an unchanged frozen getter definition may be invoked.");

        var target = ResolveObject(definition.ObjectPath);
        var interfaceType = RequireType(_apiAssembly, definition.InterfaceType);
        var method = SingleMethod(interfaceType, definition.Member);
        if (!string.Equals(method.ToString(), definition.ManagedSignature, StringComparison.Ordinal))
            throw new InvalidOperationException($"Installed signature drift for {definition.Operation}.");

        var parameters = method.GetParameters();
        var arguments = new object?[parameters.Length];
        var inputIndex = 0;
        for (var index = 0; index < parameters.Length; index++)
        {
            var parameter = parameters[index];
            if (parameter.ParameterType.IsByRef)
            {
                arguments[index] = DefaultFor(parameter.ParameterType.GetElementType()!);
                continue;
            }

            object? value;
            if (inputIndex < inputs.Count)
                value = inputs[inputIndex++];
            else if (parameter.HasDefaultValue)
                value = parameter.DefaultValue;
            else
                throw new ArgumentException(
                    $"{definition.Operation} requires input {parameter.Name}.", nameof(inputs));
            arguments[index] = CoerceInput(value, parameter.ParameterType, parameter.Name ?? $"arg{index}");
        }
        if (inputIndex != inputs.Count)
            throw new ArgumentException(
                $"{definition.Operation} received {inputs.Count} inputs; {inputIndex} are accepted.", nameof(inputs));

        var returnValue = method.Invoke(target, arguments);
        cancellationToken.ThrowIfCancellationRequested();
        var outputs = parameters
            .Select((parameter, index) => (parameter, index))
            .Where(item => item.parameter.ParameterType.IsByRef)
            .Select(item => Normalize(arguments[item.index]))
            .ToArray();
        return new EtabsInvocation(Normalize(returnValue), outputs);
    }

    public void Dispose()
    {
        if (_disposed)
            return;
        _disposed = true;
        var cleanupErrors = ReleaseAll(_releaseOrder.AsEnumerable().Reverse());
        _objectCache.Clear();
        GC.Collect();
        GC.WaitForPendingFinalizers();
        if (cleanupErrors.Count > 0)
            throw new AggregateException(
                "One or more acquired ETABS COM references could not be released.",
                cleanupErrors);
    }

    private object ResolveObject(string path)
    {
        if (_objectCache.TryGetValue(path, out var cached))
            return cached;
        var segments = path.Split('.');
        object current = _sapModel;
        var currentType = RequireType(_apiAssembly, "ETABSv1.cSapModel");
        var currentPath = string.Empty;
        foreach (var segment in segments)
        {
            if (segment == "SapModel")
                continue;
            currentPath = currentPath.Length == 0 ? segment : $"{currentPath}.{segment}";
            var property = currentType.GetProperty(segment)
                ?? throw new InvalidOperationException($"Installed accessor {currentType.FullName}.{segment} is absent.");
            if (_objectCache.TryGetValue(currentPath, out cached))
            {
                current = cached;
                currentType = property.PropertyType;
                continue;
            }
            current = property.GetValue(current)
                ?? throw new InvalidOperationException($"Installed accessor {currentType.FullName}.{segment} returned null.");
            currentType = property.PropertyType;
            _objectCache[currentPath] = current;
            Track(current);
        }
        _objectCache[path] = current;
        return current;
    }

    private void Track(object value)
    {
        if (Marshal.IsComObject(value) && !_releaseOrder.Any(item => ReferenceEquals(item, value)))
            _releaseOrder.Add(value);
    }

    private static void ValidateMatrix(Assembly assembly)
    {
        foreach (var definition in EtabsGetterMatrix.Allowed.Values)
        {
            var type = RequireType(assembly, definition.InterfaceType);
            var method = SingleMethod(type, definition.Member);
            if (!string.Equals(method.ToString(), definition.ManagedSignature, StringComparison.Ordinal))
                throw new InvalidOperationException(
                    $"Installed signature drift for {definition.Operation}: {method}.");
            var inputs = method.GetParameters().Count(parameter => !parameter.ParameterType.IsByRef);
            var outputs = method.GetParameters().Count(parameter => parameter.ParameterType.IsByRef);
            if (inputs != definition.InputNames.Count || outputs != definition.OutputNames.Count)
                throw new InvalidOperationException($"Frozen parameter-direction drift for {definition.Operation}.");
            var inputNames = method.GetParameters()
                .Where(parameter => !parameter.ParameterType.IsByRef)
                .Select(parameter => parameter.Name ?? string.Empty);
            var outputNames = method.GetParameters()
                .Where(parameter => parameter.ParameterType.IsByRef)
                .Select(parameter => parameter.Name ?? string.Empty);
            if (!inputNames.SequenceEqual(definition.InputNames, StringComparer.Ordinal) ||
                !outputNames.SequenceEqual(definition.OutputNames, StringComparer.Ordinal))
                throw new InvalidOperationException($"Frozen parameter-name drift for {definition.Operation}.");
        }
    }

    private static MethodInfo SingleMethod(Type type, string member)
    {
        var methods = type.GetMethods().Where(method => method.Name == member).ToArray();
        return methods.Length == 1
            ? methods[0]
            : throw new InvalidOperationException(
                $"Expected one installed method {type.FullName}.{member}; found {methods.Length}.");
    }

    private static Type RequireType(Assembly assembly, string fullName) =>
        assembly.GetType(fullName, throwOnError: true)
        ?? throw new TypeLoadException(fullName);

    private static object? DefaultFor(Type type)
    {
        if (type.IsArray)
            return null;
        if (type == typeof(string))
            return string.Empty;
        return type.IsValueType ? Activator.CreateInstance(type) : null;
    }

    private static object? CoerceInput(object? value, Type targetType, string parameterName)
    {
        if (value is null)
            return null;
        if (targetType.IsInstanceOfType(value))
            return value;
        if (targetType.IsEnum && value is int enumValue)
            return Enum.ToObject(targetType, enumValue);
        try
        {
            return Convert.ChangeType(value, targetType, System.Globalization.CultureInfo.InvariantCulture);
        }
        catch (Exception exception) when (exception is InvalidCastException or FormatException or OverflowException)
        {
            throw new ArgumentException(
                $"Input {parameterName} cannot be converted to {targetType.FullName}.", parameterName, exception);
        }
    }

    private static object? Normalize(object? value)
    {
        if (value is null)
            return null;
        var type = value.GetType();
        if (type.IsEnum)
            return Convert.ToInt32(value, System.Globalization.CultureInfo.InvariantCulture);
        if (value is Array array)
            return array.Cast<object?>().Select(Normalize).ToArray();
        return value;
    }

    private static void ValidateExpectedFiles(EtabsHostExpectation expected)
    {
        if (!File.Exists(expected.ApiAssemblyPath))
            throw new FileNotFoundException("The exact ETABS API assembly is absent.", expected.ApiAssemblyPath);
        RequireEqual("API file version", expected.ApiFileVersion,
            FileVersionInfo.GetVersionInfo(expected.ApiAssemblyPath).FileVersion ?? string.Empty);
        RequireEqual("API SHA-256", expected.ApiSha256, Sha256File(expected.ApiAssemblyPath));
        if (!File.Exists(expected.TypeLibraryPath))
            throw new FileNotFoundException("The exact ETABS x64 type library is absent.", expected.TypeLibraryPath);
        RequireEqual("type-library byte count", expected.TypeLibraryBytes,
            new FileInfo(expected.TypeLibraryPath).Length);
        RequireEqual("type-library SHA-256", expected.TypeLibrarySha256,
            Sha256File(expected.TypeLibraryPath));
    }

    private static void ValidateModelFile(EtabsHostExpectation expected, string modelPath)
    {
        var file = new FileInfo(modelPath);
        RequireEqual("model byte count", expected.ModelBytes, file.Length);
        RequireEqual("model modified UTC", expected.ModelModifiedUtc,
            new DateTimeOffset(file.LastWriteTimeUtc, TimeSpan.Zero));
        RequireEqual("model SHA-256", expected.ModelSha256, Sha256File(modelPath));
    }

    private static string Sha256File(string path)
    {
        using var stream = File.OpenRead(path);
        return Convert.ToHexStringLower(SHA256.HashData(stream));
    }

    private static void RequirePath(string label, string expected, string actual)
    {
        if (!string.Equals(Path.GetFullPath(expected), Path.GetFullPath(actual), StringComparison.OrdinalIgnoreCase))
            throw new InvalidOperationException($"Exact {label} path mismatch.");
    }

    private static void RequireEqual<T>(string label, T expected, T actual)
    {
        if (!EqualityComparer<T>.Default.Equals(expected, actual))
            throw new InvalidOperationException($"Exact {label} mismatch: expected {expected}; observed {actual}.");
    }

    private static List<Exception> ReleaseAll(IEnumerable<object?> values)
    {
        var errors = new List<Exception>();
        foreach (var value in values)
        {
            try
            {
                if (value is not null && Marshal.IsComObject(value))
                    Marshal.FinalReleaseComObject(value);
            }
            catch (Exception exception)
            {
                errors.Add(exception);
            }
        }
        return errors;
    }
}
