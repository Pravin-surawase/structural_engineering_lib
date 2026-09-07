#requires -Version 7.5
[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$TargetPath,
    [Parameter(Mandatory)][string]$ExpectedModelPath,
    [Parameter(Mandatory)][string]$ExpectedModelSha256,
    [Parameter(Mandatory)][string]$OutputDirectory
)

# Getter-only qualification of a real whole-model result call against every source frame.
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'Etabs-Qualification.ps1')
$target = Get-Content -LiteralPath $TargetPath -Raw | ConvertFrom-Json -DateKind String
$process = Get-Process -Id $target.ProcessId
if ($process.StartTime.ToUniversalTime().ToString('o') -ne $target.ProcessStartedUtc -or
    $process.Path -ne $target.ExecutablePath -or
    (Get-FileHash -LiteralPath $process.Path -Algorithm SHA256).Hash -ne $target.ExecutableSha256) { throw 'The exact target process changed.' }
$model = [IO.Path]::GetFullPath($ExpectedModelPath)
if ((Get-FileHash -LiteralPath $model -Algorithm SHA256).Hash -ne $ExpectedModelSha256) { throw 'The source model changed.' }
$output = [IO.Path]::GetFullPath($OutputDirectory)
if (Test-Path -LiteralPath $output) { throw 'Use a new evidence directory.' }
New-Item -ItemType Directory -Path $output | Out-Null
$assembly = [Reflection.Assembly]::LoadFrom((Join-Path (Split-Path -Parent $process.Path) 'ETABSv1.dll'))
$ownedRefs = [Collections.Generic.List[object]]::new()
$calls = [Collections.Generic.List[object]]::new()
$receipt = [ordered]@{schema_version='wp10-whole-model-force-qualification/v1';passed=$false;target=$target;model_path=$model;model_sha256=$ExpectedModelSha256;started_utc=[DateTimeOffset]::UtcNow.ToString('o');failure=$null}
function Read-Source([string]$TypeName, [object]$Object, [string]$Method, [hashtable]$Inputs = @{}) {
    $result = Invoke-StructAutomateEtabsMethod -Assembly $assembly -TypeName $TypeName -Target $Object -MethodName $Method -Inputs $Inputs
    $calls.Add($result)
    return $result
}
function Keep-Reference([object]$Value) { $ownedRefs.Add($Value); return $Value }
try {
    $helper = Keep-Reference ([Activator]::CreateInstance($assembly.GetType('ETABSv1.Helper', $true)))
    $oapi = Keep-Reference ($assembly.GetType('ETABSv1.cHelper', $true).GetMethod('GetObjectProcess').Invoke($helper, @('CSI.ETABS.API.ETABSObject', [int]$process.Id)))
    $sapType = $assembly.GetType('ETABSv1.cSapModel', $true)
    $sap = Keep-Reference ($assembly.GetType('ETABSv1.cOAPI', $true).GetProperty('SapModel').GetValue($oapi))
    $frames = Keep-Reference ($sapType.GetProperty('FrameObj').GetValue($sap))
    $groups = Keep-Reference ($sapType.GetProperty('GroupDef').GetValue($sap))
    $results = Keep-Reference ($sapType.GetProperty('Results').GetValue($sap))
    $analyze = Keep-Reference ($sapType.GetProperty('Analyze').GetValue($sap))
    function Protected-State {
        $path = (Read-Source cSapModel $sap GetModelFilename @{IncludePath=$true}).value
        if ([IO.Path]::GetFullPath($path) -ne $model) { throw 'The active model is not the exact expected source.' }
        return [ordered]@{
            path=$path
            sha256=(Get-FileHash -LiteralPath $model -Algorithm SHA256).Hash
            locked=(Read-Source cSapModel $sap GetModelIsLocked).value
            present=(Read-Source cSapModel $sap GetPresentUnits).value
            database=(Read-Source cSapModel $sap GetDatabaseUnits).value
            statuses=(Read-Source cAnalyze $analyze GetCaseStatus).outputs
        }
    }
    $before = Protected-State
    if (-not $before.locked -or $before.present -ne 6) { throw 'Qualification requires current locked results in kN-m-C API units.' }
    $names = (Read-Source cFrameObj $frames GetNameList).outputs.MyName
    $groupNames = (Read-Source cGroup $groups GetNameList).outputs.MyName
    if ('All' -notin $groupNames) { throw 'The source All group is absent.' }
    $assignments = Read-Source cGroup $groups GetAssignments @{Name='All'}
    $bulk = Read-Source cAnalysisResults $results FrameForce @{Name='All';ItemTypeElm=2}
    if ($bulk.outputs.NumberResults -le 0) { throw 'The whole-model getter returned no results.' }
    $rowFields = @('Obj','ObjSta','Elm','ElmSta','LoadCase','StepType','StepNum','P','V2','V3','T','M2','M3')
    $rowsByObject = [Collections.Generic.Dictionary[string,Collections.Generic.List[int]]]::new([StringComparer]::Ordinal)
    for ($index = 0; $index -lt $bulk.outputs.NumberResults; $index++) {
        $name = $bulk.outputs.Obj[$index]
        if (-not $rowsByObject.ContainsKey($name)) { $rowsByObject.Add($name, [Collections.Generic.List[int]]::new()) }
        $rowsByObject[$name].Add($index)
    }
    if (@($rowsByObject.Keys | Where-Object { $_ -notin $names }).Count -ne 0) { throw 'A group result object is absent from the full source frame catalogue.' }
    $directRows = 0; $directElapsed = [double]0
    foreach ($name in $names) {
        $direct = Read-Source cAnalysisResults $results FrameForce @{Name=$name;ItemTypeElm=0}
        $directElapsed += $direct.elapsed_ms
        $indices = if ($rowsByObject.ContainsKey($name)) { $rowsByObject[$name] } else { @() }
        if ($direct.outputs.NumberResults -ne $indices.Count) { throw "Result row count differs for $name." }
        for ($local = 0; $local -lt $direct.outputs.NumberResults; $local++) {
            foreach ($field in $rowFields) {
                if ($direct.outputs[$field][$local] -cne $bulk.outputs[$field][$indices[$local]]) { throw "The actual result differs at $name row $local field $field." }
            }
        }
        $directRows += $direct.outputs.NumberResults
    }
    $final = Read-Source cAnalysisResults $results FrameForce @{Name='All';ItemTypeElm=2}
    if (($bulk.outputs | ConvertTo-Json -Depth 7 -Compress) -cne ($final.outputs | ConvertTo-Json -Depth 7 -Compress)) { throw 'The complete group result changed during qualification.' }
    $after = Protected-State
    if (($before | ConvertTo-Json -Depth 7 -Compress) -cne ($after | ConvertTo-Json -Depth 7 -Compress)) { throw 'Protected source facts changed.' }
    if ($directRows -ne $bulk.outputs.NumberResults) { throw 'The direct and group inventories do not conserve every actual row.' }
    $receipt.source_members = $names.Count
    $receipt.group_result_members = $rowsByObject.Count
    $receipt.rows = $directRows
    $receipt.group_elapsed_ms = $bulk.elapsed_ms
    $receipt.direct_elapsed_ms = $directElapsed
    $receipt.protected_before = $before
    $receipt.protected_after = $after
    $receipt.passed = $true
} catch { $receipt.failure = $_.Exception.ToString() }
finally {
    $callPath = Join-Path $output 'calls.json'
    $calls | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath $callPath
    $receipt.calls_sha256 = (Get-FileHash -LiteralPath $callPath -Algorithm SHA256).Hash.ToLowerInvariant()
    $receipt.completed_utc = [DateTimeOffset]::UtcNow.ToString('o')
    $receipt | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath (Join-Path $output 'receipt.json')
    for ($index = $ownedRefs.Count - 1; $index -ge 0; $index--) {
        if ([Runtime.InteropServices.Marshal]::IsComObject($ownedRefs[$index])) { [void][Runtime.InteropServices.Marshal]::ReleaseComObject($ownedRefs[$index]) }
    }
}
$receipt | ConvertTo-Json -Depth 10
if (-not $receipt.passed) { throw $receipt.failure }
