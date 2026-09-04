[CmdletBinding()]
param([string]$Version = '0.1.0')

. (Join-Path $PSScriptRoot 'Common.ps1')

$installDirectory = Assert-StructAutomateSafeInstallPath (Join-Path (Get-StructAutomateInstallRoot) $Version)
$installedXll = Join-Path $installDirectory 'StructAutomate.xll'
$installedManifestPath = Join-Path $installDirectory 'manifest.json'
$installedManifest = if (Test-Path -LiteralPath $installedManifestPath -PathType Leaf) { Get-Content -Raw -LiteralPath $installedManifestPath | ConvertFrom-Json } else { $null }
$installedManifestIdentity = if (Test-Path -LiteralPath $installedManifestPath -PathType Leaf) { Get-StructAutomateFileIdentity $installedManifestPath } else { $null }
if (Get-Process -Name EXCEL -ErrorAction SilentlyContinue) {
    throw 'Close Excel before uninstalling the add-in.'
}

$registration = [ordered]@{ found = $false; removed = $false; full_name = $installedXll }
if (Test-Path -LiteralPath $installedXll -PathType Leaf) {
    $excel = New-Object -ComObject Excel.Application
    $addIns = $null
    $workbooks = $null
    $bootstrapWorkbook = $null
    try {
        $excel.Visible = $false
        $excel.DisplayAlerts = $false
        $workbooks = $excel.Workbooks
        $bootstrapWorkbook = $workbooks.Add()
        $addIns = $excel.AddIns
        for ($index = 1; $index -le $addIns.Count; $index++) {
            $addin = $null
            try {
                $addin = $addIns.Item($index)
                if ([string]::Equals([string]$addin.FullName, $installedXll, [System.StringComparison]::OrdinalIgnoreCase)) {
                    $registration.found = $true
                    $addin.Installed = $false
                    $registration.removed = -not [bool]$addin.Installed
                }
            }
            finally {
                Release-StructAutomateComObject $addin
            }
        }
    }
    finally {
        if ($bootstrapWorkbook) {
            try { $bootstrapWorkbook.Close($false) }
            finally { Release-StructAutomateComObject $bootstrapWorkbook }
        }
        Release-StructAutomateComObject $workbooks
        Release-StructAutomateComObject $addIns
        Close-StructAutomateExcelApplication $excel
    }
}

$removedFiles = @()
if (Test-Path -LiteralPath $installDirectory) {
    $removedFiles = @(Get-ChildItem -LiteralPath $installDirectory -Recurse -File | ForEach-Object { Get-StructAutomateFileIdentity $_.FullName })
    $verified = Assert-StructAutomateSafeInstallPath $installDirectory
    Remove-Item -LiteralPath $verified -Recurse -Force
}

$receiptDirectory = Get-StructAutomateReceiptRoot
[void](New-Item -ItemType Directory -Path $receiptDirectory -Force)
$receipt = [ordered]@{
    schema_version = 'structautomate.excel-uninstall/v1'
    completed_at_utc = [DateTimeOffset]::UtcNow.ToString('o')
    source_commit = if ($installedManifest) { [string]$installedManifest.source_commit } else { $null }
    version = $Version
    install_directory = $installDirectory
    registration = $registration
    removed_files = $removedFiles
    installed_manifest_sha256 = if ($installedManifestIdentity) { $installedManifestIdentity.sha256 } else { $null }
    directory_removed = -not (Test-Path -LiteralPath $installDirectory)
}
$receiptPath = Join-Path $receiptDirectory 'excel-uninstall.json'
Write-StructAutomateJson -Value $receipt -Path $receiptPath
$receipt | ConvertTo-Json -Depth 20
