[CmdletBinding()]
param(
    [string]$Configuration = 'Release',
    [string]$OutputDirectory = (Join-Path $PSScriptRoot '..\..\..\tmp\wp09-distribution'),
    [Parameter(Mandatory)][string]$CertificateThumbprint,
    [switch]$SkipBuild
)

. (Join-Path $PSScriptRoot 'Common.ps1')

$repository = Get-StructAutomateRepositoryRoot
$csharp = Join-Path $repository 'CSharp'
$output = Assert-StructAutomateSafeRepositoryOutput $OutputDirectory
$status = & git -C $repository status --porcelain
if ($LASTEXITCODE -ne 0) { throw 'Unable to inspect the repository candidate.' }
if ($status) { throw 'Create the immutable source candidate commit before packaging.' }

if (-not $SkipBuild) {
    Push-Location $csharp
    try {
        & dotnet restore StructAutomate.slnx --locked-mode
        if ($LASTEXITCODE -ne 0) { throw 'Locked .NET restore failed.' }
        & dotnet build StructAutomate.slnx -c $Configuration --no-restore
        if ($LASTEXITCODE -ne 0) { throw 'Release .NET build failed.' }
    }
    finally { Pop-Location }
}

$publish = Join-Path $csharp "src\StructuralEngineering.ExcelDna\bin\$Configuration\net10.0-windows\publish"
$packed = Join-Path $publish 'StructuralEngineering.ExcelDna-AddIn64-packed.xll'
if (-not (Test-Path -LiteralPath $packed -PathType Leaf)) { throw "Packed x64 XLL is missing: $packed" }
if ((Get-StructAutomatePeMachine $packed) -ne 'AMD64') { throw 'The packed XLL is not AMD64.' }

if (Test-Path -LiteralPath $output) {
    $verified = Assert-StructAutomateSafeRepositoryOutput $output
    Remove-Item -LiteralPath $verified -Recurse -Force
}
[void](New-Item -ItemType Directory -Path $output -Force)

$xll = Join-Path $output 'StructAutomate.xll'
Copy-Item -LiteralPath $packed -Destination $xll
$preSign = Get-StructAutomateFileIdentity $xll

$certificate = Get-Item -LiteralPath ("Cert:\CurrentUser\My\$CertificateThumbprint") -ErrorAction Stop
if (-not $certificate.HasPrivateKey) { throw 'The selected certificate has no accessible private key.' }
$signature = Set-AuthenticodeSignature -LiteralPath $xll -Certificate $certificate -HashAlgorithm SHA256
if ($signature.SignerCertificate.Thumbprint -ne $certificate.Thumbprint) { throw 'The packed XLL signature did not bind the selected certificate.' }
$verifiedSignature = Get-AuthenticodeSignature -LiteralPath $xll
if (-not $verifiedSignature.SignerCertificate) { throw 'The packed XLL has no Authenticode signer after signing.' }
if ([string]$verifiedSignature.Status -ne 'Valid') { throw "The packed XLL signature is not valid: $($verifiedSignature.Status) $($verifiedSignature.StatusMessage)" }

$sample = Join-Path $csharp 'samples\StructAutomate-Standalone-Beam.xlsx'
$help = Join-Path $repository 'docs\library\excel\README.md'
foreach ($required in @($sample, $help)) {
    if (-not (Test-Path -LiteralPath $required -PathType Leaf)) { throw "Distribution input is missing: $required" }
}
Copy-Item -LiteralPath $sample -Destination (Join-Path $output 'StructAutomate-Standalone-Beam.xlsx')
Copy-Item -LiteralPath $help -Destination (Join-Path $output 'README.md')
foreach ($scriptName in @(
    'Common.ps1',
    'Test-Preflight.ps1',
    'Install-PerUser.ps1',
    'Repair-PerUser.ps1',
    'Uninstall-PerUser.ps1')) {
    Copy-Item -LiteralPath (Join-Path $PSScriptRoot $scriptName) `
        -Destination (Join-Path $output $scriptName)
}

$sourceCommit = (& git -C $repository rev-parse HEAD).Trim()
$sourceTree = (& git -C $repository rev-parse 'HEAD^{tree}').Trim()
$files = Get-ChildItem -LiteralPath $output -File | ForEach-Object { Get-StructAutomateFileIdentity $_.FullName }
$manifest = [ordered]@{
    schema_version = 'structautomate.excel-distribution/v1'
    product = 'StructAutomate Excel'
    version = '0.1.0'
    source_commit = $sourceCommit
    source_tree = $sourceTree
    target = 'win-x64'
    excel_target = 'Microsoft 365 Excel 64-bit on Windows 11'
    runtime_target = '.NET 10 Desktop Runtime x64'
    excel_dna_version = '1.9.0'
    workbook_template_version = 'structural-excel-workbook/v1'
    file_digest_algorithm = 'SHA-256'
    pre_sign_xll_sha256 = $preSign.sha256
    signed_xll = Get-StructAutomateFileIdentity $xll
    pe_machine = Get-StructAutomatePeMachine $xll
    signature = [ordered]@{
        status = [string]$verifiedSignature.Status
        status_message = [string]$verifiedSignature.StatusMessage
        signature_type = [string]$verifiedSignature.SignatureType
        subject = $verifiedSignature.SignerCertificate.Subject
        thumbprint = $verifiedSignature.SignerCertificate.Thumbprint
        authenticode_file_digest_algorithm = 'SHA-256'
        certificate_signature_algorithm = $verifiedSignature.SignerCertificate.SignatureAlgorithm.FriendlyName
        timestamp_subject = if ($verifiedSignature.TimeStamperCertificate) { $verifiedSignature.TimeStamperCertificate.Subject } else { $null }
        purpose = 'WP09 local installed candidate'
    }
    files = @($files)
    public_release_authorized = $false
}
$manifestPath = Join-Path $output 'manifest.json'
Write-StructAutomateJson -Value $manifest -Path $manifestPath

$checksumLines = Get-ChildItem -LiteralPath $output -File | Sort-Object Name | ForEach-Object {
    $hash = (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
    "$hash  $($_.Name)"
}
$checksumLines | Set-Content -LiteralPath (Join-Path $output 'SHA256SUMS') -Encoding ascii

$zipPath = "$output.zip"
if (Test-Path -LiteralPath $zipPath) { Remove-Item -LiteralPath $zipPath -Force }
Compress-Archive -Path (Join-Path $output '*') -DestinationPath $zipPath -CompressionLevel Optimal

[ordered]@{
    distribution_directory = $output
    distribution_zip = Get-StructAutomateFileIdentity $zipPath
    manifest = Get-StructAutomateFileIdentity $manifestPath
    signed_xll = Get-StructAutomateFileIdentity $xll
    signature_status = [string]$verifiedSignature.Status
} | ConvertTo-Json -Depth 10
