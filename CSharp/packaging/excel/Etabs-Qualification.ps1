#requires -Version 7.5
# Typed reflection for owned-host qualification scripts only. The caller must prove process/model ownership before a mutation.
function Invoke-StructAutomateEtabsMethod {
    param([Reflection.Assembly]$Assembly, [string]$TypeName, [object]$Target, [string]$MethodName,
        [hashtable]$Inputs = @{}, [switch]$AllowStatusFailure)
    $method = $Assembly.GetType('ETABSv1.' + $TypeName, $true).GetMethod($MethodName)
    if ($null -eq $method) { throw "Missing exact method $TypeName.$MethodName" }
    $parameters = $method.GetParameters()
    foreach ($name in $Inputs.Keys) {
        if ($name -notin $parameters.Name) { throw "Unknown source parameter $TypeName.$MethodName.$name" }
    }
    $arguments = [object[]]::new($parameters.Length)
    for ($index = 0; $index -lt $parameters.Length; $index++) {
        $parameter = $parameters[$index]; $type = $parameter.ParameterType
        if ($type.IsByRef) { $type = $type.GetElementType() }
        if ($Inputs.ContainsKey($parameter.Name)) {
            if ($null -eq $Inputs[$parameter.Name]) { $arguments[$index] = $null; continue }
            # Assign directly: an if-expression pipeline unrolls a typed array into Object[].
            if ($type.IsEnum) { $converted = [Enum]::ToObject($type, [int]$Inputs[$parameter.Name]) }
            else { $converted = [Management.Automation.LanguagePrimitives]::ConvertTo($Inputs[$parameter.Name], $type) }
            $arguments[$index] = $converted.PSObject.BaseObject
        } elseif ($type.IsValueType) { $arguments[$index] = [Activator]::CreateInstance($type) }
    }
    $watch = [Diagnostics.Stopwatch]::StartNew()
    $value = $method.Invoke($Target, $arguments)
    $watch.Stop()
    if (-not $AllowStatusFailure -and $method.ReturnType -eq [int] -and $value -ne 0) { throw "$TypeName.$MethodName returned $value" }
    $outputs = [ordered]@{}
    for ($index = 0; $index -lt $parameters.Length; $index++) {
        if ($parameters[$index].ParameterType.IsByRef) { $outputs[$parameters[$index].Name] = $arguments[$index] }
    }
    [pscustomobject]@{method="$TypeName.$MethodName";signature=$method.ToString();inputs=$Inputs;value=$value;outputs=$outputs;elapsed_ms=$watch.Elapsed.TotalMilliseconds}
}
