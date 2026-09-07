#requires -Version 7.5
[CmdletBinding()]
param(
    [Parameter(Mandatory)][ValidateSet('small','medium')][string]$Size,
    [Parameter(Mandatory)][string]$OutputDirectory,
    [string]$EtabsExecutable = 'C:\Program Files\Computers and Structures\ETABS 23\ETABS.exe',
    [switch]$KeepOpen
)

# Qualification setup only: create a new owned model, never attach to or edit a user's model.
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'Etabs-Qualification.ps1')
$destination = [IO.Path]::GetFullPath($OutputDirectory)
$repository = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../..')).TrimEnd('\') + '\'
if ($destination.StartsWith($repository, [StringComparison]::OrdinalIgnoreCase) -or (Test-Path -LiteralPath $destination)) {
    throw 'Use a new external evidence directory for the owned fixture.'
}
$memberCount = if ($Size -eq 'small') { 100 } else { 1000 }
$expectedRows = $memberCount * 100
New-Item -ItemType Directory -Path (Join-Path $destination 'model') -Force | Out-Null
$modelPath = Join-Path $destination "model\BENCH-ETABS-$($Size.ToUpperInvariant()).EDB"
$assembly = [Reflection.Assembly]::LoadFrom((Join-Path (Split-Path -Parent $EtabsExecutable) 'ETABSv1.dll'))
$objects = [Collections.Generic.List[object]]::new()
$helper = $null; $oapi = $null; $sap = $null; $owned = $null; $failure = $null
$journal = [IO.StreamWriter]::new((Join-Path $destination 'setup.jsonl'), $false, [Text.UTF8Encoding]::new($false))
$receipt = [ordered]@{
    schema_version='wp10-owned-performance-fixture/v1'; passed=$false; pf9_acceptance=$false
    workload="BENCH-ETABS-$($Size.ToUpperInvariant())"; started_utc=[DateTimeOffset]::UtcNow.ToString('o')
    model_path=$modelPath; owned_process=$null; expected_members=$memberCount; expected_rows=$expectedRows
    fixture_basis='Distinct straight horizontal concrete frame objects with fixed end restraints, varying source lengths and uniform loads; 100 actual output stations per member in one ordinary static case. No copied or padded force rows.'
    units='kN_m_C'; output_cases=@('PF9_STATIC'); member_ids=@(); observations=@{}; cleanup=@{}; failure=$null
}
function Invoke-Fixture([string]$TypeName, [object]$Target, [string]$MethodName, [hashtable]$Inputs=@{}) {
    $result = Invoke-StructAutomateEtabsMethod -Assembly $assembly -TypeName $TypeName -Target $Target -MethodName $MethodName -Inputs $Inputs
    $journal.WriteLine(($result | ConvertTo-Json -Depth 12 -Compress)); $journal.Flush()
    return $result
}
function Get-FixtureObject([string]$Property) {
    $value=$assembly.GetType('ETABSv1.cSapModel',$true).GetProperty($Property).GetValue($sap)
    $objects.Add($value)
    return $value
}
try {
    $before=@(Get-Process -Name ETABS -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id)
    $helper=[Activator]::CreateInstance($assembly.GetType('ETABSv1.Helper',$true))
    $oapi=$assembly.GetType('ETABSv1.cHelper',$true).GetMethod('CreateObject').Invoke($helper,@($EtabsExecutable))
    $null=Invoke-Fixture cOAPI $oapi ApplicationStart
    $created=@(Get-Process -Name ETABS | Where-Object Id -notin $before)
    if ($created.Count -ne 1) { throw 'Startup must identify exactly one new owned ETABS process.' }
    $owned=$created[0]
    $receipt.owned_process=[ordered]@{id=$owned.Id;started_utc=$owned.StartTime.ToUniversalTime().ToString('o');executable=$owned.Path}
    $sap=$assembly.GetType('ETABSv1.cOAPI',$true).GetProperty('SapModel').GetValue($oapi)
    $null=Invoke-Fixture cSapModel $sap InitializeNewModel @{Units=6}
    $file=Get-FixtureObject File
    $null=Invoke-Fixture cFile $file NewBlank
    $null=Invoke-Fixture cStory (Get-FixtureObject Story) SetStories_2 @{
        BaseElevation=0.0;NumberStories=1;StoryNames=[string[]]@('PF9');StoryHeights=[double[]]@(3.0)
        IsMasterStory=[bool[]]@($true);SimilarToStory=[string[]]@('None');SpliceAbove=[bool[]]@($false)
        SpliceHeight=[double[]]@(0.0);color=[int[]]@(0)
    }
    $material=Get-FixtureObject PropMaterial
    $null=Invoke-Fixture cPropMaterial $material SetMaterial @{Name='PF9_CONCRETE';MatType=2;Color=-1;Notes='Owned acquisition performance fixture';GUID=''}
    $null=Invoke-Fixture cPropMaterial $material SetMPIsotropic @{Name='PF9_CONCRETE';E=25000000.0;U=0.2;A=0.00001;Temp=0.0}
    $null=Invoke-Fixture cPropFrame (Get-FixtureObject PropFrame) SetRectangle @{Name='PF9_RECT';MatProp='PF9_CONCRETE';T3=0.5;T2=0.3;Color=-1;Notes='Owned fixture section';GUID=''}
    $null=Invoke-Fixture cLoadPatterns (Get-FixtureObject LoadPatterns) Add @{Name='PF9_STATIC';MyType=1;SelfWTMultiplier=0.0;AddAnalysisCase=$true}
    $loadCases=Get-FixtureObject LoadCases
    foreach($name in @('Dead','Live','Modal')) { $null=Invoke-Fixture cLoadCases $loadCases Delete @{Name=$name} }
    $frames=Get-FixtureObject FrameObj; $points=Get-FixtureObject PointObj
    $members=[Collections.Generic.List[string]]::new()
    for($index=0;$index -lt $memberCount;$index++) {
        $x=10.0*($index%10);$y=5.0*[Math]::Floor($index/10);$length=4.0+0.25*($index%9)
        $frame=Invoke-Fixture cFrameObj $frames AddByCoord @{XI=$x;YI=$y;ZI=3.0;XJ=($x+$length);YJ=$y;ZJ=3.0;Name='';PropName='PF9_RECT';UserName=('PF9_B'+($index+1).ToString('D4'));CSys='Global'}
        $name=[string]$frame.outputs.Name; $members.Add($name)
        $ends=(Invoke-Fixture cFrameObj $frames GetPoints @{Name=$name}).outputs
        foreach($point in @($ends.Point1,$ends.Point2)) {
            $null=Invoke-Fixture cPointObj $points SetRestraint @{Name=$point;Value=[bool[]]@($true,$true,$true,$true,$true,$true);ItemType=0}
        }
        $null=Invoke-Fixture cFrameObj $frames SetOutputStations @{Name=$name;MyType=2;MaxSegSize=0.0;MinSections=100;NoOutPutAndDesignAtElementEnds=$false;NoOutPutAndDesignAtPointLoads=$false;ItemType=0}
        $load=8.0+0.125*($index%17)
        $null=Invoke-Fixture cFrameObj $frames SetLoadDistributed @{Name=$name;LoadPat='PF9_STATIC';MyType=1;Dir=10;Dist1=0.0;Dist2=1.0;Val1=$load;Val2=$load;CSys='Global';RelDist=$true;Replace=$true;ItemType=0}
        if (($index+1)%100 -eq 0) { Write-Output "Prepared $($index+1)/$memberCount actual frame objects." }
    }
    $receipt.member_ids=$members.ToArray()
    $null=Invoke-Fixture cFile $file Save @{FileName=$modelPath}
    $analyze=Get-FixtureObject Analyze
    $null=Invoke-Fixture cAnalyze $analyze SetRunCaseFlag @{Name='';Run=$false;All=$true}
    $null=Invoke-Fixture cAnalyze $analyze SetRunCaseFlag @{Name='PF9_STATIC';Run=$true;All=$false}
    Write-Output "Analyzing owned $memberCount-member fixture."
    $null=Invoke-Fixture cAnalyze $analyze RunAnalysis
    $results=Get-FixtureObject Results
    $setup=$assembly.GetType('ETABSv1.cAnalysisResults',$true).GetProperty('Setup').GetValue($results);$objects.Add($setup)
    $null=Invoke-Fixture cAnalysisResultsSetup $setup DeselectAllCasesAndCombosForOutput
    $null=Invoke-Fixture cAnalysisResultsSetup $setup SetCaseSelectedForOutput @{Name='PF9_STATIC';Selected=$true}
    $rowCount=0
    foreach($name in $members) {
        $force=(Invoke-Fixture cAnalysisResults $results FrameForce @{Name=$name;ItemTypeElm=0}).outputs
        if($force.NumberResults -ne 100 -or @($force.Obj | Where-Object {$_ -ne $name}).Count -gt 0 -or @($force.LoadCase | Where-Object {$_ -ne 'PF9_STATIC'}).Count -gt 0) {
            throw "Source member $name does not have exactly 100 genuine same-object static rows."
        }
        if(@($force.ObjSta | Sort-Object -Unique).Count -ne 100) { throw 'Output rows must represent 100 distinct actual source stations.' }
        $index=$members.IndexOf($name);$length=4.0+0.25*($index%9);$load=8.0+0.125*($index%17)
        if([Math]::Abs($force.ObjSta[99]-$length) -gt 1e-8 -or
            [Math]::Abs([Math]::Abs($force.V2[0])-$load*$length/2) -gt 1e-7 -or
            [Math]::Abs([Math]::Abs($force.M3[0])-$load*$length*$length/12) -gt 1e-7) { throw 'Source stations/forces do not match the defined metre, kN and kN-m fixed-end fixture basis.' }
        $rowCount+=$force.NumberResults
    }
    $receipt.observations.actual_rows=$rowCount
    $receipt.observations.frames=(Invoke-Fixture cFrameObj $frames GetAllFrames @{csys='Global'}).outputs.NumberNames
    $receipt.observations.case_statuses=(Invoke-Fixture cAnalyze $analyze GetCaseStatus).outputs
    $receipt.observations.locked=(Invoke-Fixture cSapModel $sap GetModelIsLocked).value
    $receipt.observations.present_units=(Invoke-Fixture cSapModel $sap GetPresentUnits).value
    $receipt.observations.database_units=(Invoke-Fixture cSapModel $sap GetDatabaseUnits).value
    $receipt.observations.present_components=(Invoke-Fixture cSapModel $sap GetPresentUnits_2).outputs
    $receipt.observations.database_components=(Invoke-Fixture cSapModel $sap GetDatabaseUnits_2).outputs
    if($receipt.observations.frames -ne $memberCount -or $rowCount -ne $expectedRows -or -not $receipt.observations.locked -or $receipt.observations.present_units -ne 6 -or $receipt.observations.database_units -notin @(6,9) -or @($receipt.observations.case_statuses.Status | Where-Object {$_ -ne 4}).Count -gt 0) { throw 'The owned source workload is incomplete or outside the qualified unit profile.' }
    # RunAnalysis saved the analyzed source. A subsequent explicit Save(FileName)
    # resets the analysis lock in the installed host; freeze the verified state here.
    $receipt.observations.active_model_path=(Invoke-Fixture cSapModel $sap GetModelFilename @{IncludePath=$true}).value
    if([IO.Path]::GetFullPath($receipt.observations.active_model_path) -ne $modelPath){throw 'The analyzed fixture is no longer the exact owned model path.'}
    $receipt.model_sha256=(Get-FileHash -LiteralPath $modelPath -Algorithm SHA256).Hash.ToLowerInvariant()
    $target=[ordered]@{ProcessId=$owned.Id;ProcessStartedUtc=$receipt.owned_process.started_utc;ExecutablePath=$owned.Path;ExecutableSha256=(Get-FileHash -LiteralPath $owned.Path -Algorithm SHA256).Hash.ToLowerInvariant()}
    [IO.File]::WriteAllText((Join-Path $destination 'target.json'),($target | ConvertTo-Json),[Text.UTF8Encoding]::new($false))
    $receipt.passed=$true
} catch { $failure=$_;$receipt.failure=$_.Exception.ToString() }
finally {
    if($null -ne $oapi -and (-not $KeepOpen -or $null -ne $failure)) {
        try { $null=Invoke-Fixture cOAPI $oapi ApplicationExit @{FileSave=$false};$receipt.cleanup.exit_requested=$true }
        catch { $receipt.cleanup.exit_failure=$_.Exception.Message;$receipt.passed=$false;if($null -eq $failure){$failure=$_} }
    }
    $objects.Reverse()
    foreach($value in @($objects.ToArray())+@($sap,$oapi,$helper)) {
        if($null -ne $value -and [Runtime.InteropServices.Marshal]::IsComObject($value)){[void][Runtime.InteropServices.Marshal]::ReleaseComObject($value)}
    }
    if($null -ne $owned){
        if(-not $KeepOpen -or $null -ne $failure){$receipt.cleanup.owned_process_exited=$owned.WaitForExit(15000)}
        else{$receipt.cleanup.retained_for_qualification=$true}
        $owned.Dispose()
    }
    $journal.Dispose()
    $receipt.setup_journal_sha256=(Get-FileHash -LiteralPath (Join-Path $destination 'setup.jsonl') -Algorithm SHA256).Hash.ToLowerInvariant()
    $receipt.completed_utc=[DateTimeOffset]::UtcNow.ToString('o')
    [IO.File]::WriteAllText((Join-Path $destination 'receipt.json'),($receipt | ConvertTo-Json -Depth 12),[Text.UTF8Encoding]::new($false))
}
if($null -ne $failure){throw $failure}
[pscustomobject]@{passed=$receipt.passed;receipt=(Join-Path $destination 'receipt.json');target=(Join-Path $destination 'target.json');members=$memberCount;rows=$receipt.observations.actual_rows;owned_process=$receipt.owned_process}
