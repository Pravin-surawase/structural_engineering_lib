#requires -Version 7.5
[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$SourceModelPath,
    [Parameter(Mandatory)][string]$OutputDirectory,
    [string]$EtabsExecutable = 'C:\Program Files\Computers and Structures\ETABS 23\ETABS.exe',
    [switch]$KeepOpen
)

# Qualification setup only. Production acquisition never launches, opens or analyses a model.
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$destination = [IO.Path]::GetFullPath($OutputDirectory)
if (Test-Path -LiteralPath $destination) { throw 'Use a new external evidence directory.' }
$source = Get-Item -LiteralPath $SourceModelPath
$repository = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../..')).TrimEnd('\') + '\'
if ($destination.StartsWith($repository, [StringComparison]::OrdinalIgnoreCase)) { throw 'Private qualification evidence must stay outside the repository.' }
$sourceHash = (Get-FileHash -LiteralPath $source.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
New-Item -ItemType Directory -Path $destination | Out-Null
$modelDirectory = Join-Path $destination 'model'
New-Item -ItemType Directory -Path $modelDirectory | Out-Null
# Preserve the analyzed model's associated result files under the same basename.
$sourceFiles = @(Get-ChildItem -LiteralPath $source.DirectoryName -File | Where-Object { $_.Name.StartsWith($source.BaseName + '.', [StringComparison]::OrdinalIgnoreCase) })
foreach ($sourceFile in $sourceFiles) { Copy-Item -LiteralPath $sourceFile.FullName -Destination (Join-Path $modelDirectory $sourceFile.Name) }
$modelPath = Join-Path $modelDirectory $source.Name
$assembly = [Reflection.Assembly]::LoadFrom((Join-Path (Split-Path -Parent $EtabsExecutable) 'ETABSv1.dll'))
$objects = [Collections.Generic.List[object]]::new()
$helper = $null; $oapi = $null; $sap = $null; $failure = $null; $owned = $null
$receipt = [ordered]@{schema_version='structautomate.etabs-force-preflight/v1';passed=$false;started_utc=[DateTimeOffset]::UtcNow.ToString('o');source_sha256=$sourceHash;model_path=$modelPath;owned_process=$null;signatures=@{};observations=@{};cleanup=@{};failure=$null}
function Invoke-Source([string]$TypeName, [object]$Target, [string]$MethodName, [hashtable]$Inputs = @{}) {
    $method = $assembly.GetType('ETABSv1.' + $TypeName, $true).GetMethod($MethodName)
    if ($null -eq $method) { throw "Missing exact method $TypeName.$MethodName" }
    $receipt.signatures["$TypeName.$MethodName"] = $method.ToString()
    $parameters = $method.GetParameters()
    $arguments = [object[]]::new($parameters.Length)
    for ($index = 0; $index -lt $parameters.Length; $index++) {
        $parameter = $parameters[$index]
        $type = $parameter.ParameterType
        if ($type.IsByRef) { $type = $type.GetElementType() }
        if ($Inputs.ContainsKey($parameter.Name)) {
            $converted = if ($type.IsEnum) { [Enum]::ToObject($type, [int]$Inputs[$parameter.Name]) } else { [Management.Automation.LanguagePrimitives]::ConvertTo($Inputs[$parameter.Name], $type) }
            $arguments[$index] = $converted.PSObject.BaseObject
        } elseif ($type.IsValueType) { $arguments[$index] = [Activator]::CreateInstance($type) }
    }
    $value = $method.Invoke($Target, $arguments)
    if ($method.ReturnType -eq [int] -and $value -ne 0) { throw "$TypeName.$MethodName returned $value" }
    $outputs = [ordered]@{}
    for ($index = 0; $index -lt $parameters.Length; $index++) {
        if ($parameters[$index].ParameterType.IsByRef) { $outputs[$parameters[$index].Name] = $arguments[$index] }
    }
    [pscustomobject]@{value=$value;outputs=$outputs}
}
function Get-SourceObject([string]$Property) {
    $value = $assembly.GetType('ETABSv1.cSapModel', $true).GetProperty($Property).GetValue($sap)
    $objects.Add($value)
    return $value
}
try {
    $before = @(Get-Process -Name ETABS -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id)
    $helper = [Activator]::CreateInstance($assembly.GetType('ETABSv1.Helper', $true))
    $oapi = $assembly.GetType('ETABSv1.cHelper', $true).GetMethod('CreateObject').Invoke($helper, @($EtabsExecutable))
    $null = Invoke-Source cOAPI $oapi ApplicationStart
    $newProcesses = @(Get-Process -Name ETABS | Where-Object { $_.Id -notin $before })
    if ($newProcesses.Count -ne 1) { throw 'Owned ETABS startup did not produce one uniquely identified process.' }
    $owned = $newProcesses[0]
    $receipt.owned_process = [ordered]@{id=$owned.Id;started_utc=$owned.StartTime.ToUniversalTime().ToString('o');executable=$owned.Path}
    $sap = $assembly.GetType('ETABSv1.cOAPI', $true).GetProperty('SapModel').GetValue($oapi)
    $file = Get-SourceObject File
    $null = Invoke-Source cFile $file OpenFile @{FileName=$modelPath}
    $receipt.observations.version = (Invoke-Source cSapModel $sap GetVersion).outputs
    $receipt.observations.locked = (Invoke-Source cSapModel $sap GetModelIsLocked).value
    $receipt.observations.units = (Invoke-Source cSapModel $sap GetPresentUnits).value
    $receipt.observations.cases = (Invoke-Source cAnalyze (Get-SourceObject Analyze) GetCaseStatus).outputs
    $frames = (Invoke-Source cFrameObj (Get-SourceObject FrameObj) GetAllFrames @{csys='Global'}).outputs
    $receipt.observations.frames = $frames
    $materials = Get-SourceObject PropMaterial
    $names = (Invoke-Source cPropMaterial $materials GetNameList @{MatType=0}).outputs
    $receipt.observations.materials = @($names.MyName | ForEach-Object {
        $kind = (Invoke-Source cPropMaterial $materials GetTypeOAPI @{Name=$_}).outputs
        [ordered]@{name=$_;classification=$kind}
    })
    $receipt.passed = $true
} catch { $failure = $_; $receipt.failure = $_.Exception.ToString() }
finally {
    if ($null -ne $oapi -and (-not $KeepOpen -or $null -ne $failure)) {
        try { $null = Invoke-Source cOAPI $oapi ApplicationExit @{FileSave=$false}; $receipt.cleanup.exit_requested=$true }
        catch { $receipt.cleanup.exit_failure=$_.Exception.Message; if ($null -eq $failure) { $failure=$_; $receipt.passed=$false } }
    }
    $objects.Reverse()
    foreach ($value in @($objects.ToArray()) + @($sap,$oapi,$helper)) {
        if ($null -ne $value -and [Runtime.InteropServices.Marshal]::IsComObject($value)) { [void][Runtime.InteropServices.Marshal]::ReleaseComObject($value) }
    }
    if ($null -ne $owned) {
        if (-not $KeepOpen -or $null -ne $failure) { $receipt.cleanup.owned_process_exited=$owned.WaitForExit(15000) }
        else { $receipt.cleanup.retained_for_qualification=$true }
        $owned.Dispose()
    }
    $receipt.cleanup.original_preserved = ((Get-FileHash -LiteralPath $source.FullName -Algorithm SHA256).Hash.ToLowerInvariant() -eq $sourceHash)
    $receipt.completed_utc = [DateTimeOffset]::UtcNow.ToString('o')
    [IO.File]::WriteAllText((Join-Path $destination 'receipt.json'), ($receipt | ConvertTo-Json -Depth 30), [Text.UTF8Encoding]::new($false))
}
if ($null -ne $failure) { throw $failure }
[pscustomobject]@{passed=$receipt.passed;receipt=(Join-Path $destination 'receipt.json');owned_process=$receipt.owned_process;frames=$receipt.observations.frames.NumberNames;locked=$receipt.observations.locked;source_preserved=$receipt.cleanup.original_preserved}
