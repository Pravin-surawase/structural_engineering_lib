#requires -Version 7.5
[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$OwnedPreflightReceipt,
    [Parameter(Mandatory)][string]$SourceModelPath,
    [Parameter(Mandatory)][string]$OutputDirectory,
    [Parameter(Mandatory)][string]$ProbeMemberId,
    [string[]]$OutputCases = @(),
    [string[]]$OutputCombinations = @(),
    [string]$ProbeAnalysisPointId,
    [switch]$InspectBulkTables,
    [switch]$RequestAllTableFields,
    [switch]$ReadEditingTables,
    [switch]$UseKnMUnits,
    [string[]]$TableKeys = @(),
    [switch]$KeepExistingAnalysis
)

# Explicit qualification setup on the exact copy created by Invoke-EtabsForcePreflight.
# This script is never loaded by the XLL, worker, or production getter adapter.
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$owner = Get-Content -LiteralPath $OwnedPreflightReceipt -Raw | ConvertFrom-Json -DateKind String
if (-not $owner.passed) { throw 'A passed owned-copy preflight receipt is required.' }
$process = Get-Process -Id $owner.owned_process.id
if ($process.StartTime.ToUniversalTime().ToString('o') -ne $owner.owned_process.started_utc -or $process.Path -ne $owner.owned_process.executable) { throw 'The owned process identity changed.' }
$model = [IO.Path]::GetFullPath($owner.model_path)
$ownedRoot = [IO.Path]::GetFullPath((Join-Path (Split-Path -Parent $OwnedPreflightReceipt) 'model')).TrimEnd('\') + '\'
$source = [IO.Path]::GetFullPath($SourceModelPath)
if (-not $model.StartsWith($ownedRoot, [StringComparison]::OrdinalIgnoreCase) -or $model -eq $source) { throw 'The target must be the receipt-owned model copy.' }
$sourceSha = (Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash.ToLowerInvariant()
if ($sourceSha -ne $owner.source_sha256) { throw 'The original source hash differs from preflight.' }
$output = [IO.Path]::GetFullPath($OutputDirectory)
if (Test-Path -LiteralPath $output) { throw 'Use a new evidence directory.' }
New-Item -ItemType Directory -Path $output | Out-Null
$assembly = [Reflection.Assembly]::LoadFrom((Join-Path (Split-Path -Parent $process.Path) 'ETABSv1.dll'))
$helper = $null; $oapi = $null; $sap = $null; $analyze = $null; $results = $null; $setup = $null; $pointElm = $null; $tables = $null; $failure = $null
$receipt = [ordered]@{schema_version='wp10-owned-analysis-setup/v1';passed=$false;owned_process=$owner.owned_process;model_path=$model;source_path=$source;source_sha256=$sourceSha;started_utc=[DateTimeOffset]::UtcNow.ToString('o');observations=@{};failure=$null}
function Check-Status([object]$Status, [string]$Operation) { if ($Status -ne 0) { throw "$Operation returned CSI status $Status" } }
try {
    $helper = [Activator]::CreateInstance($assembly.GetType('ETABSv1.Helper', $true))
    $oapi = $assembly.GetType('ETABSv1.cHelper', $true).GetMethod('GetObjectProcess').Invoke($helper, @('CSI.ETABS.API.ETABSObject', [int]$process.Id))
    $sap = $assembly.GetType('ETABSv1.cOAPI', $true).GetProperty('SapModel').GetValue($oapi)
    $sapType = $assembly.GetType('ETABSv1.cSapModel', $true)
    $activePath = $sapType.GetMethod('GetModelFilename').Invoke($sap, @($true))
    if ([IO.Path]::GetFullPath($activePath) -ne $model) { throw 'The owned process no longer has the owned model open.' }
    $receipt.observations.initial_present_units = $sapType.GetMethod('GetPresentUnits').Invoke($sap, $null)
    if ($UseKnMUnits) {
        Check-Status ($sapType.GetMethod('SetPresentUnits').Invoke($sap, @([Enum]::ToObject($assembly.GetType('ETABSv1.eUnits', $true), 6)))) 'SetPresentUnits(kN_m_C) on the owned fixture'
    }
    $analyze = $sapType.GetProperty('Analyze').GetValue($sap)
    $analyzeType = $assembly.GetType('ETABSv1.cAnalyze', $true)
    $flags = [object[]]@(0, $null, $null)
    Check-Status ($analyzeType.GetMethod('GetRunCaseFlag').Invoke($analyze, $flags)) 'GetRunCaseFlag'
    $receipt.observations.run_cases = @($flags[1])
    $receipt.observations.run_flags = @($flags[2])
    if ($flags[0] -eq 0 -or @($flags[2] | Where-Object { -not $_ }).Count -ne 0) { throw 'Qualification requires all existing cases selected to run; no flags are silently changed.' }
    $receipt.observations.analysis_rerun = -not $KeepExistingAnalysis
    if (-not $KeepExistingAnalysis) {
        Check-Status ($sapType.GetMethod('SetModelIsLocked').Invoke($sap, @($false))) 'SetModelIsLocked(false)'
        Write-Output 'Running fresh analysis on the verified owned copy.'
        Check-Status ($analyzeType.GetMethod('RunAnalysis').Invoke($analyze, $null)) 'RunAnalysis'
    }
    $statuses = [object[]]@(0, $null, $null)
    Check-Status ($analyzeType.GetMethod('GetCaseStatus').Invoke($analyze, $statuses)) 'GetCaseStatus'
    $receipt.observations.case_names = @($statuses[1]); $receipt.observations.case_statuses = @($statuses[2])
    $results = $sapType.GetProperty('Results').GetValue($sap)
    if ($OutputCases.Count + $OutputCombinations.Count -gt 0) {
        $setup = $assembly.GetType('ETABSv1.cAnalysisResults', $true).GetProperty('Setup').GetValue($results)
        $setupType = $assembly.GetType('ETABSv1.cAnalysisResultsSetup', $true)
        Check-Status ($setupType.GetMethod('DeselectAllCasesAndCombosForOutput').Invoke($setup, $null)) 'DeselectAllCasesAndCombosForOutput'
        foreach ($name in $OutputCases) { Check-Status ($setupType.GetMethod('SetCaseSelectedForOutput').Invoke($setup, @($name.PSObject.BaseObject, $true))) 'SetCaseSelectedForOutput' }
        foreach ($name in $OutputCombinations) { Check-Status ($setupType.GetMethod('SetComboSelectedForOutput').Invoke($setup, @($name.PSObject.BaseObject, $true))) 'SetComboSelectedForOutput' }
        $receipt.observations.fixture_output_cases = $OutputCases
        $receipt.observations.fixture_output_combinations = $OutputCombinations
    }
    $forceArgs = [object[]]::new(16)
    $forceArgs[0] = $ProbeMemberId.PSObject.BaseObject
    $forceArgs[1] = [Enum]::ToObject($assembly.GetType('ETABSv1.eItemTypeElm', $true), 0)
    $forceArgs[2] = 0
    $forceStatus = $assembly.GetType('ETABSv1.cAnalysisResults', $true).GetMethod('FrameForce').Invoke($results, $forceArgs)
    $receipt.observations.force_status = $forceStatus; $receipt.observations.force_rows = $forceArgs[2]
    $receipt.observations.probe_member = $ProbeMemberId
    Check-Status $forceStatus 'FrameForce'
    if ($forceArgs[2] -le 0) { throw 'Fresh analysis returned no force rows for the probe member.' }
    $protectedBefore = [ordered]@{locked=$sapType.GetMethod('GetModelIsLocked').Invoke($sap,$null); units=$sapType.GetMethod('GetPresentUnits').Invoke($sap,$null); database_units=$sapType.GetMethod('GetDatabaseUnits').Invoke($sap,$null); status=$statuses; forces=$forceArgs; model_sha256=(Get-FileHash -LiteralPath $model -Algorithm SHA256).Hash}
    if (-not [string]::IsNullOrWhiteSpace($ProbeAnalysisPointId)) {
        $pointElm = $sapType.GetProperty('PointElm').GetValue($sap)
        $pointMethod = $assembly.GetType('ETABSv1.cPointElm', $true).GetMethod('GetCoordCartesian')
        $pointArgs = [object[]]@($ProbeAnalysisPointId.PSObject.BaseObject, [double]0, [double]0, [double]0, 'Global')
        Check-Status ($pointMethod.Invoke($pointElm, $pointArgs)) 'PointElm.GetCoordCartesian'
        $receipt.observations.analysis_point = [ordered]@{name=$ProbeAnalysisPointId;signature=$pointMethod.ToString();coordinates=@($pointArgs[1..3]);coordinate_system='Global'}
    }
    if ($InspectBulkTables -or $TableKeys.Count -gt 0) {
        $tables = $sapType.GetProperty('DatabaseTables').GetValue($sap)
        $tablesType = $assembly.GetType('ETABSv1.cDatabaseTables', $true)
        $catalogArgs = [object[]]@(0, $null, $null, $null, $null)
        Check-Status ($tablesType.GetMethod('GetAllTables').Invoke($tables, $catalogArgs)) 'DatabaseTables.GetAllTables'
        $catalog = @(for ($index = 0; $index -lt $catalogArgs[0]; $index++) { [ordered]@{key=$catalogArgs[1][$index];name=$catalogArgs[2][$index];import_type=$catalogArgs[3][$index];empty=$catalogArgs[4][$index]} })
        $catalog | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $output 'table-catalog.json')
        $receipt.observations.table_catalog_count = $catalogArgs[0]
        $tableResults = @()
        foreach ($key in $TableKeys) {
            $receipt.observations.last_table = $key
            if ($key -notin $catalogArgs[1]) { throw "Requested table key is absent: $key" }
            $fieldArgs = [object[]]@($key.PSObject.BaseObject, 0, 0, $null, $null, $null, $null, $null)
            Check-Status ($tablesType.GetMethod('GetAllFieldsInTable').Invoke($tables, $fieldArgs)) 'DatabaseTables.GetAllFieldsInTable'
            $tableArgs = [object[]]@($key.PSObject.BaseObject, $null, 'All', 0, $null, 0, $null)
            if ($RequestAllTableFields) { $tableArgs[1] = [string[]]$fieldArgs[3] }
            $timer = [Diagnostics.Stopwatch]::StartNew()
            $tableStatus = $tablesType.GetMethod('GetTableForDisplayArray').Invoke($tables, $tableArgs)
            $timer.Stop()
            $tableResult = [ordered]@{key=$key;status=$tableStatus;group='All';requested_all_fields=[bool]$RequestAllTableFields;field_version=$fieldArgs[1];field_count=$fieldArgs[2];field_keys=$fieldArgs[3];field_names=$fieldArgs[4];field_descriptions=$fieldArgs[5];field_units=$fieldArgs[6];field_importable=$fieldArgs[7];returned_field_key_list=$tableArgs[1];version=$tableArgs[3];included=$tableArgs[4];count=$tableArgs[5];data=$tableArgs[6];elapsed_ms=$timer.Elapsed.TotalMilliseconds}
            if ($ReadEditingTables) {
                $editingArgs = [object[]]@($key.PSObject.BaseObject, 'All', 0, $null, 0, $null)
                $timer.Restart()
                $editingStatus = $tablesType.GetMethod('GetTableForEditingArray').Invoke($tables, $editingArgs)
                $timer.Stop()
                $tableResult.editing = [ordered]@{status=$editingStatus;version=$editingArgs[2];included=$editingArgs[3];count=$editingArgs[4];data=$editingArgs[5];elapsed_ms=$timer.Elapsed.TotalMilliseconds}
            }
            $tableResults += $tableResult
            $tableResults | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath (Join-Path $output 'tables.json')
        }
        if ($tableResults.Count -gt 0) { $tableResults | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath (Join-Path $output 'tables.json') }
    }
    $finalStatuses = [object[]]@(0,$null,$null)
    Check-Status ($analyzeType.GetMethod('GetCaseStatus').Invoke($analyze,$finalStatuses)) 'GetCaseStatus(postflight)'
    $finalForces = [object[]]::new(16); $finalForces[0]=$ProbeMemberId.PSObject.BaseObject; $finalForces[1]=$forceArgs[1]; $finalForces[2]=0
    Check-Status ($assembly.GetType('ETABSv1.cAnalysisResults',$true).GetMethod('FrameForce').Invoke($results,$finalForces)) 'FrameForce(postflight)'
    $protectedAfter = [ordered]@{locked=$sapType.GetMethod('GetModelIsLocked').Invoke($sap,$null); units=$sapType.GetMethod('GetPresentUnits').Invoke($sap,$null); database_units=$sapType.GetMethod('GetDatabaseUnits').Invoke($sap,$null); status=$finalStatuses; forces=$finalForces; model_sha256=(Get-FileHash -LiteralPath $model -Algorithm SHA256).Hash}
    $receipt.observations.protected_before=$protectedBefore
    $receipt.observations.protected_after=$protectedAfter
    if (($protectedBefore | ConvertTo-Json -Depth 8 -Compress) -ne ($protectedAfter | ConvertTo-Json -Depth 8 -Compress)) { throw 'Protected model, units, analysis status or result payload changed during table getters.' }
    $receipt.passed = $true
} catch { $failure = $_; $receipt.failure = $_.Exception.ToString() }
finally {
    foreach ($value in @($tables,$pointElm,$setup,$results,$analyze,$sap,$oapi,$helper)) { if ($null -ne $value -and [Runtime.InteropServices.Marshal]::IsComObject($value)) { [void][Runtime.InteropServices.Marshal]::ReleaseComObject($value) } }
    $receipt.original_preserved = (Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash.ToLowerInvariant() -eq $sourceSha
    if (-not $receipt.original_preserved) { $receipt.passed = $false }
    $receipt.completed_utc = [DateTimeOffset]::UtcNow.ToString('o')
    $receipt | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath (Join-Path $output 'receipt.json')
}
if ($null -ne $failure) { throw $failure }
$receipt | ConvertTo-Json -Depth 10
