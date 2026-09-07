#requires -Version 7.5
[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$OwnedPreflightReceipt,
    [Parameter(Mandatory)][string]$SourceModelPath,
    [Parameter(Mandatory)][string]$OutputDirectory,
    [Parameter(Mandatory)][string]$MemberId,
    [switch]$IncludeEditingTables
)

. (Join-Path $PSScriptRoot 'Etabs-Qualification.ps1')
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$owner = Get-Content -LiteralPath $OwnedPreflightReceipt -Raw | ConvertFrom-Json -DateKind String
if (-not $owner.passed) { throw 'A passed owned-copy preflight is required.' }
$process = Get-Process -Id $owner.owned_process.id
if ($process.StartTime.ToUniversalTime().ToString('o') -ne $owner.owned_process.started_utc -or $process.Path -ne $owner.owned_process.executable) { throw 'The owned process changed.' }
$model = [IO.Path]::GetFullPath($owner.model_path)
$ownedRoot = [IO.Path]::GetFullPath((Join-Path (Split-Path -Parent $OwnedPreflightReceipt) 'model')).TrimEnd('\') + '\'
$source = [IO.Path]::GetFullPath($SourceModelPath)
if (-not $model.StartsWith($ownedRoot, [StringComparison]::OrdinalIgnoreCase) -or $model -eq $source) { throw 'Only the exact receipt-owned copy may be changed.' }
$sourceSha = (Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash.ToLowerInvariant()
if ($sourceSha -ne $owner.source_sha256) { throw 'The source model differs from its owner receipt.' }
$output = [IO.Path]::GetFullPath($OutputDirectory)
if (Test-Path -LiteralPath $output) { throw 'Use a new evidence directory.' }
New-Item -ItemType Directory -Path $output | Out-Null
$assembly = [Reflection.Assembly]::LoadFrom((Join-Path (Split-Path -Parent $process.Path) 'ETABSv1.dll'))
$helper=$null; $oapi=$null; $sap=$null; $frames=$null; $tables=$null; $failure=$null; $attachedOwned=$false
$receipt=[ordered]@{schema_version='wp10-table-assignment-qualification/v1';passed=$false;owned_process=$owner.owned_process;model_path=$model;source_sha256=$sourceSha;member=$MemberId;observations=@();cleanup=@{owned_exit=$false;source_preserved=$false};failure=$null}
function Call([string]$Type, [object]$Target, [string]$Method, [hashtable]$Inputs=@{}, [switch]$AllowStatusFailure) {
    Invoke-StructAutomateEtabsMethod -Assembly $assembly -TypeName $Type -Target $Target -MethodName $Method -Inputs $Inputs -AllowStatusFailure:$AllowStatusFailure
}
function Observe([string]$Name) {
    $facts=[ordered]@{label=$Name;getters=@();tables=@()}
    foreach ($method in @('GetModifiers','GetReleases','GetInsertionPoint_1','GetLocalAxes','GetEndLengthOffset')) {
        $facts.getters += Call cFrameObj $frames $method @{Name=$MemberId}
    }
    $facts.all_frames=Call cFrameObj $frames GetAllFrames @{csys='Global'}
    $facts.catalogue=Call cDatabaseTables $tables GetAllTables
    foreach ($key in @('Frame Assignments - Summary','Frame Assignments - Property Modifiers','Frame Assignments - Releases and Partial Fixity','Frame Assignments - Insertion Point','Frame Assignments - Local Axes','Frame Assignments - End Length Offsets','Frame Assignments - Output Stations')) {
        $table = [ordered]@{
            key=$key
            fields=(Call cDatabaseTables $tables GetAllFieldsInTable @{TableKey=$key})
            data=(Call cDatabaseTables $tables GetTableForDisplayArray @{TableKey=$key;GroupName='All'} -AllowStatusFailure)
        }
        if ($IncludeEditingTables) { $table.editing = Call cDatabaseTables $tables GetTableForEditingArray @{TableKey=$key;GroupName='All'} -AllowStatusFailure }
        $facts.tables += $table
    }
    $path=Join-Path $output ($Name + '.json')
    $facts | ConvertTo-Json -Depth 20 | Set-Content -LiteralPath $path
    $receipt.observations += [ordered]@{label=$Name;path=$path;sha256=(Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()}
    return $facts
}
try {
    $helper=[Activator]::CreateInstance($assembly.GetType('ETABSv1.Helper',$true))
    $oapi=(Call cHelper $helper GetObjectProcess @{typeName='CSI.ETABS.API.ETABSObject';pid=[int]$process.Id}).value
    $sap=$assembly.GetType('ETABSv1.cOAPI',$true).GetProperty('SapModel').GetValue($oapi)
    $active=(Call cSapModel $sap GetModelFilename @{IncludePath=$true}).value
    if ([IO.Path]::GetFullPath($active) -ne $model) { throw 'The owned process no longer has the qualified copy open.' }
    $attachedOwned=$true
    $frames=$assembly.GetType('ETABSv1.cSapModel',$true).GetProperty('FrameObj').GetValue($sap)
    $tables=$assembly.GetType('ETABSv1.cSapModel',$true).GetProperty('DatabaseTables').GetValue($sap)
    $baseline=Observe 'baseline'
    $saved=@{}; foreach ($getter in $baseline.getters) { $saved[$getter.method] = $getter.outputs }
    $null=Call cSapModel $sap SetModelIsLocked @{LockIt=$false}
    $experiments=@(
        @{label='modifiers';method='SetModifiers';change=@{Value=[double[]]@(1,1,1,1,1,0.73123456789,1,1)};restore=@{Value=$saved['cFrameObj.GetModifiers'].Value}},
        @{label='releases';method='SetReleases';change=@{II=[bool[]]@($false,$false,$false,$false,$true,$false);JJ=[bool[]]@($false,$false,$false,$false,$false,$false);StartValue=[double[]]@(0,0,0,0,123.456789,0);EndValue=[double[]]@(0,0,0,0,0,0)};restore=@{}},
        @{label='insertion';method='SetInsertionPoint_1';change=@{CardinalPoint=8;Mirror2=$true;Mirror3=$false;StiffTransform=$true;Offset1=[double[]]@(0.01,0.02,0.03);Offset2=[double[]]@(0,0,0);CSys='Global'};restore=@{}},
        @{label='axes';method='SetLocalAxes';change=@{Ang=30.0};restore=@{Ang=$saved['cFrameObj.GetLocalAxes'].Ang}},
        @{label='end-offset';method='SetEndLengthOffset';change=@{AutoOffset=$false;Length1=0.123456789;Length2=0.234567891;RZ=0.32123456789};restore=@{}}
    )
    foreach ($name in @('II','JJ','StartValue','EndValue')) { $experiments[1].restore[$name]=$saved['cFrameObj.GetReleases'][$name] }
    foreach ($name in @('CardinalPoint','Mirror2','Mirror3','StiffTransform','Offset1','Offset2','CSys')) { $experiments[2].restore[$name]=$saved['cFrameObj.GetInsertionPoint_1'][$name] }
    foreach ($name in @('AutoOffset','Length1','Length2','RZ')) { $experiments[4].restore[$name]=$saved['cFrameObj.GetEndLengthOffset'][$name] }
    foreach ($experiment in $experiments) {
        $experiment.change.Name=$MemberId; $experiment.change.ItemType=0
        $experiment.restore.Name=$MemberId; $experiment.restore.ItemType=0
        try { $null=Call cFrameObj $frames $experiment.method $experiment.change; $null=Observe $experiment.label }
        finally { $null=Call cFrameObj $frames $experiment.method $experiment.restore }
    }
    $null=Observe 'restored'
    $receipt.passed=$true
} catch { $failure=$_; $receipt.failure=$_.Exception.ToString(); $receipt.failure_location=$_.ScriptStackTrace }
finally {
    if ($attachedOwned -and $null -ne $oapi) {
        try { $null=Call cOAPI $oapi ApplicationExit @{FileSave=$false}; $process.WaitForExit(20000) | Out-Null; $receipt.cleanup.owned_exit=$process.HasExited }
        catch { $receipt.cleanup.failure=$_.Exception.ToString(); $receipt.passed=$false }
    }
    foreach ($value in @($tables,$frames,$sap,$oapi,$helper)) { if ($null -ne $value -and [Runtime.InteropServices.Marshal]::IsComObject($value)) { [void][Runtime.InteropServices.Marshal]::ReleaseComObject($value) } }
    $receipt.cleanup.source_preserved=(Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash.ToLowerInvariant() -eq $sourceSha
    if (-not $receipt.cleanup.source_preserved -or -not $receipt.cleanup.owned_exit) { $receipt.passed=$false }
    $receipt | ConvertTo-Json -Depth 15 | Set-Content -LiteralPath (Join-Path $output 'receipt.json')
}
$receipt | ConvertTo-Json -Depth 15
if ($null -ne $failure) { throw $failure }
if (-not $receipt.passed) { throw 'Owned table qualification did not pass with clean source/host cleanup.' }
