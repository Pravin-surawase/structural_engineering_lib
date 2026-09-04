[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$DistributionDirectory,
    [string]$ReceiptPath = (Join-Path $PSScriptRoot '..\..\..\tmp\wp09-preflight.json')
)

. (Join-Path $PSScriptRoot 'Common.ps1')

$distribution = [System.IO.Path]::GetFullPath($DistributionDirectory)
$manifestPath = Join-Path $distribution 'manifest.json'
$xllPath = Join-Path $distribution 'StructAutomate.xll'
if (-not (Test-Path -LiteralPath $manifestPath -PathType Leaf)) { throw "Manifest is missing: $manifestPath" }
if (-not (Test-Path -LiteralPath $xllPath -PathType Leaf)) { throw "XLL is missing: $xllPath" }
$manifest = Get-Content -Raw -LiteralPath $manifestPath | ConvertFrom-Json
$excel = Get-StructAutomateExcelEnvironment
$runtimes = Get-StructAutomateDesktopRuntimes
$signature = Get-AuthenticodeSignature -LiteralPath $xllPath
$actualXll = Get-StructAutomateFileIdentity $xllPath

$fileChecks = @()
foreach ($file in $manifest.files) {
    $isLeafName = [System.IO.Path]::GetFileName([string]$file.name) -eq [string]$file.name
    $path = if ($isLeafName) { Join-Path $distribution ([string]$file.name) } else { $null }
    $exists = [bool]($path -and (Test-Path -LiteralPath $path -PathType Leaf))
    $actual = if ($exists) { Get-StructAutomateFileIdentity $path } else { $null }
    $fileChecks += [ordered]@{
        name = [string]$file.name
        exists = $exists
        expected_sha256 = [string]$file.sha256
        actual_sha256 = if ($actual) { $actual.sha256 } else { $null }
        matches = [bool]($isLeafName -and $actual -and $actual.sha256 -eq [string]$file.sha256)
    }
}

$checksumPath = Join-Path $distribution 'SHA256SUMS'
$checksumChecks = @()
if (Test-Path -LiteralPath $checksumPath -PathType Leaf) {
    foreach ($line in Get-Content -LiteralPath $checksumPath) {
        if ($line -match '^(?<hash>[a-fA-F0-9]{64})  (?<name>.+)$') {
            $isLeafName = [System.IO.Path]::GetFileName($Matches.name) -eq $Matches.name
            $path = if ($isLeafName) { Join-Path $distribution $Matches.name } else { $null }
            $actual = if ($path -and (Test-Path -LiteralPath $path -PathType Leaf)) { Get-StructAutomateFileIdentity $path } else { $null }
            $checksumChecks += [ordered]@{
                name = $Matches.name
                expected_sha256 = $Matches.hash.ToLowerInvariant()
                actual_sha256 = if ($actual) { $actual.sha256 } else { $null }
                matches = [bool]($isLeafName -and $actual -and $actual.sha256 -eq $Matches.hash.ToLowerInvariant())
            }
        }
        elseif ($line) {
            $checksumChecks += [ordered]@{ name = $line; expected_sha256 = $null; actual_sha256 = $null; matches = $false }
        }
    }
}

$openValues = @()
foreach ($path in @('HKCU:\Software\Microsoft\Office\16.0\Excel\Options', 'HKLM:\Software\Microsoft\Office\16.0\Excel\Options')) {
    $record = Get-ItemProperty -Path $path -ErrorAction SilentlyContinue
    if ($record) {
        $openValues += @($record.PSObject.Properties | Where-Object Name -Like 'OPEN*' | ForEach-Object {
            [ordered]@{ registry_path = $path; name = $_.Name; value = [string]$_.Value }
        })
    }
}

$checks = [ordered]@{
    windows_x64 = [Environment]::Is64BitOperatingSystem
    excel_present = [bool]$excel.executable
    excel_x64 = $excel.platform -eq 'x64'
    desktop_runtime_10_x64 = [bool]($runtimes | Where-Object { $_ -match '^Microsoft\.WindowsDesktop\.App 10\.' -and $_ -match '\[C:\\Program Files\\dotnet' })
    xll_amd64 = (Get-StructAutomatePeMachine $xllPath) -eq 'AMD64'
    xll_hash_matches = $actualXll.sha256 -eq [string]$manifest.signed_xll.sha256
    file_digest_algorithm_declared = [string]$manifest.file_digest_algorithm -eq 'SHA-256'
    signature_present = [bool]$signature.SignerCertificate
    signature_valid = [string]$signature.Status -eq 'Valid'
    signature_identity_matches = [bool]($signature.SignerCertificate -and $signature.SignerCertificate.Thumbprint -eq [string]$manifest.signature.thumbprint)
    authenticode_file_digest_algorithm_declared = [string]$manifest.signature.authenticode_file_digest_algorithm -eq 'SHA-256'
    certificate_signature_algorithm_declared = -not [string]::IsNullOrWhiteSpace([string]$manifest.signature.certificate_signature_algorithm)
    package_files_match = -not ($fileChecks | Where-Object { -not $_.matches })
    sha256sums_present = Test-Path -LiteralPath $checksumPath -PathType Leaf
    sha256sums_match = $checksumChecks.Count -gt 0 -and -not ($checksumChecks | Where-Object { -not $_.matches })
}
$passed = -not ($checks.GetEnumerator() | Where-Object { -not [bool]$_.Value })
$receipt = [ordered]@{
    schema_version = 'structautomate.excel-preflight/v1'
    passed = $passed
    observed_at_utc = [DateTimeOffset]::UtcNow.ToString('o')
    source_commit = [string]$manifest.source_commit
    distribution_manifest_sha256 = (Get-StructAutomateFileIdentity $manifestPath).sha256
    xll = $actualXll
    pe_machine = Get-StructAutomatePeMachine $xllPath
    authenticode = [ordered]@{
        status = [string]$signature.Status
        message = [string]$signature.StatusMessage
        signature_type = [string]$signature.SignatureType
        thumbprint = if ($signature.SignerCertificate) { $signature.SignerCertificate.Thumbprint } else { $null }
        file_digest_algorithm = [string]$manifest.signature.authenticode_file_digest_algorithm
        certificate_signature_algorithm = [string]$manifest.signature.certificate_signature_algorithm
    }
    excel = $excel
    desktop_runtimes = $runtimes
    registered_open_addins = $openValues
    checks = $checks
    file_checks = $fileChecks
    sha256sum_checks = $checksumChecks
}
Write-StructAutomateJson -Value $receipt -Path $ReceiptPath
$receipt | ConvertTo-Json -Depth 20
if (-not $passed) { throw 'StructAutomate Excel preflight failed one or more required checks.' }
