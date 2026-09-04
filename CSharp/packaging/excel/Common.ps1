Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Get-StructAutomateRepositoryRoot {
    return [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..\..'))
}

function Get-StructAutomateFileIdentity {
    param([Parameter(Mandatory)][string]$Path)

    $item = Get-Item -LiteralPath $Path -ErrorAction Stop
    return [ordered]@{
        name = $item.Name
        length_bytes = $item.Length
        sha256 = (Get-FileHash -LiteralPath $item.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
    }
}

function Get-StructAutomatePeMachine {
    param([Parameter(Mandatory)][string]$Path)

    $stream = [System.IO.File]::Open($Path, 'Open', 'Read', 'Read')
    try {
        $reader = [System.IO.BinaryReader]::new($stream)
        if ($reader.ReadUInt16() -ne 0x5A4D) { return 'not_pe' }
        $stream.Position = 0x3C
        $peOffset = $reader.ReadInt32()
        $stream.Position = $peOffset
        if ($reader.ReadUInt32() -ne 0x00004550) { return 'not_pe' }
        $machine = $reader.ReadUInt16()
        switch ($machine) {
            0x8664 { return 'AMD64' }
            0x014c { return 'I386' }
            0xAA64 { return 'ARM64' }
            default { return ('0x{0:X4}' -f $machine) }
        }
    }
    finally {
        $stream.Dispose()
    }
}

function Get-StructAutomateExcelEnvironment {
    $configuration = Get-ItemProperty -Path 'HKLM:\SOFTWARE\Microsoft\Office\ClickToRun\Configuration' -ErrorAction SilentlyContinue
    $installationPath = if ($configuration) { [string]$configuration.InstallationPath } else { '' }
    $excelPath = if ($installationPath) { Join-Path $installationPath 'root\Office16\EXCEL.EXE' } else { '' }
    if (-not $excelPath -or -not (Test-Path -LiteralPath $excelPath -PathType Leaf)) {
        $excelPath = 'C:\Program Files\Microsoft Office\root\Office16\EXCEL.EXE'
    }
    return [ordered]@{
        executable = if (Test-Path -LiteralPath $excelPath -PathType Leaf) { $excelPath } else { $null }
        platform = if ($configuration) { [string]$configuration.Platform } else { $null }
        version = if ($configuration) { [string]$configuration.VersionToReport } else { $null }
        products = if ($configuration) { [string]$configuration.ProductReleaseIds } else { $null }
    }
}

function Get-StructAutomateExcelStartupRegistrations {
    param([Parameter(Mandatory)][string]$XllPath)

    $optionsPath = 'HKCU:\Software\Microsoft\Office\16.0\Excel\Options'
    $expectedValue = '/R "' + [System.IO.Path]::GetFullPath($XllPath) + '"'
    $properties = Get-ItemProperty -Path $optionsPath -ErrorAction SilentlyContinue
    if (-not $properties) { return @() }
    return @($properties.PSObject.Properties | Where-Object {
        $_.Name -match '^OPEN\d*$' -and
        [string]::Equals([string]$_.Value, $expectedValue, [System.StringComparison]::OrdinalIgnoreCase)
    } | ForEach-Object {
        [ordered]@{ registry_path = $optionsPath; value_name = $_.Name; value = [string]$_.Value }
    })
}

function Register-StructAutomateExcelStartup {
    param([Parameter(Mandatory)][string]$XllPath)

    $existing = @(Get-StructAutomateExcelStartupRegistrations -XllPath $XllPath)
    if ($existing.Count -gt 0) {
        return [ordered]@{
            registry_path = $existing[0].registry_path
            value_name = $existing[0].value_name
            value = $existing[0].value
            created = $false
        }
    }

    $optionsPath = 'HKCU:\Software\Microsoft\Office\16.0\Excel\Options'
    [void](New-Item -Path $optionsPath -Force)
    $properties = Get-ItemProperty -Path $optionsPath
    $usedNames = @($properties.PSObject.Properties | Where-Object Name -Match '^OPEN\d*$' | ForEach-Object Name)
    $valueName = 'OPEN'
    if ($usedNames -contains $valueName) {
        for ($index = 1; $index -le 999; $index++) {
            $candidate = "OPEN$index"
            if ($usedNames -notcontains $candidate) { $valueName = $candidate; break }
        }
        if ($usedNames -contains $valueName) { throw 'No free Excel OPEN registration slot was found.' }
    }
    $value = '/R "' + [System.IO.Path]::GetFullPath($XllPath) + '"'
    [void](New-ItemProperty -Path $optionsPath -Name $valueName -PropertyType String -Value $value -Force)
    return [ordered]@{ registry_path = $optionsPath; value_name = $valueName; value = $value; created = $true }
}

function Unregister-StructAutomateExcelStartup {
    param([Parameter(Mandatory)][string]$XllPath)

    $registrations = @(Get-StructAutomateExcelStartupRegistrations -XllPath $XllPath)
    foreach ($registration in $registrations) {
        Remove-ItemProperty -Path $registration.registry_path -Name $registration.value_name -ErrorAction Stop
    }
    return $registrations
}

function Get-StructAutomateDesktopRuntimes {
    $lines = & dotnet --list-runtimes 2>&1
    if ($LASTEXITCODE -ne 0) { throw "dotnet --list-runtimes failed: $lines" }
    return @($lines | Where-Object { $_ -match '^Microsoft\.WindowsDesktop\.App\s' } | ForEach-Object { [string]$_ })
}

function Write-StructAutomateJson {
    param(
        [Parameter(Mandatory)][object]$Value,
        [Parameter(Mandatory)][string]$Path,
        [int]$Depth = 30
    )

    $fullPath = [System.IO.Path]::GetFullPath($Path)
    $directory = Split-Path -Parent $fullPath
    [void](New-Item -ItemType Directory -Path $directory -Force)
    $temporary = Join-Path $directory ('.' + [System.IO.Path]::GetFileName($fullPath) + '.' + [guid]::NewGuid().ToString('N') + '.tmp')
    try {
        $json = $Value | ConvertTo-Json -Depth $Depth
        [System.IO.File]::WriteAllText(
            $temporary,
            $json + [Environment]::NewLine,
            [System.Text.UTF8Encoding]::new($false))
        Move-Item -LiteralPath $temporary -Destination $fullPath -Force
    }
    finally {
        if (Test-Path -LiteralPath $temporary) { Remove-Item -LiteralPath $temporary -Force }
    }
}

function Assert-StructAutomateSafeRepositoryOutput {
    param([Parameter(Mandatory)][string]$Path)

    $repository = (Get-StructAutomateRepositoryRoot).TrimEnd('\') + '\'
    $candidate = [System.IO.Path]::GetFullPath($Path)
    if (-not $candidate.StartsWith($repository, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Output must remain inside the repository: $candidate"
    }
    if ($candidate -eq $repository.TrimEnd('\')) {
        throw 'The repository root cannot be used as a package output directory.'
    }
    return $candidate
}

function Get-StructAutomateInstallRoot {
    $localData = [Environment]::GetFolderPath([Environment+SpecialFolder]::LocalApplicationData)
    return [System.IO.Path]::GetFullPath((Join-Path $localData 'StructAutomate\Excel'))
}

function Get-StructAutomateReceiptRoot {
    $localData = [Environment]::GetFolderPath([Environment+SpecialFolder]::LocalApplicationData)
    return [System.IO.Path]::GetFullPath((Join-Path $localData 'StructAutomate\Receipts'))
}

function Assert-StructAutomateSafeInstallPath {
    param([Parameter(Mandatory)][string]$Path)

    $root = (Get-StructAutomateInstallRoot).TrimEnd('\') + '\'
    $candidate = [System.IO.Path]::GetFullPath($Path)
    if (-not $candidate.StartsWith($root, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Install path is outside the per-user StructAutomate Excel root: $candidate"
    }
    return $candidate
}

function Assert-StructAutomateSafeReceiptPath {
    param([Parameter(Mandatory)][string]$Path)

    $root = (Get-StructAutomateReceiptRoot).TrimEnd('\') + '\'
    $candidate = [System.IO.Path]::GetFullPath($Path)
    if (-not $candidate.StartsWith($root, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Receipt path is outside the per-user StructAutomate receipt root: $candidate"
    }
    return $candidate
}

function Release-StructAutomateComObject {
    param([AllowNull()][object]$Value)

    if ($null -ne $Value -and [Runtime.InteropServices.Marshal]::IsComObject($Value)) {
        [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($Value)
    }
}

function Close-StructAutomateExcelApplication {
    param([AllowNull()][object]$Excel)

    if ($null -eq $Excel) { return }
    try { $Excel.Quit() }
    finally {
        Release-StructAutomateComObject $Excel
        [GC]::Collect()
        [GC]::WaitForPendingFinalizers()
        [GC]::Collect()
        [GC]::WaitForPendingFinalizers()
    }
}

function Get-StructAutomatePercentile {
    param(
        [Parameter(Mandatory)][double[]]$Values,
        [Parameter(Mandatory)][ValidateRange(0, 100)][double]$Percentile
    )

    if ($Values.Count -eq 0) { throw 'At least one sample is required.' }
    $ordered = @($Values | Sort-Object)
    $rank = [Math]::Ceiling(($Percentile / 100.0) * $ordered.Count)
    $index = [Math]::Max(0, [Math]::Min($ordered.Count - 1, $rank - 1))
    return [double]$ordered[$index]
}
