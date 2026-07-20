param(
    [string]$ProtosDir = $env:PROTOS_DIR,
    [string]$ApiServerRoot = $env:APISERVER_ROOT,
    [string]$BaseBranch = "origin/develop",
    [string[]]$ProtoFiles,
    [switch]$SkipClean,
    [switch]$SkipInstall,
    [switch]$DryRun,
    [switch]$AllowNoVenv
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Write-Step {
    param([string]$Message)
    Write-Host "`n==> $Message" -ForegroundColor Cyan
}

function Assert-CommandExists {
    param([string]$Name)
    $cmd = Get-Command $Name -ErrorAction SilentlyContinue
    if (-not $cmd) {
        throw "Required command '$Name' was not found in PATH."
    }
}

function Assert-PathExists {
    param([string]$PathValue, [string]$Name)
    if ([string]::IsNullOrWhiteSpace($PathValue)) {
        throw "$Name is not set. Pass -$Name explicitly or define the matching environment variable."
    }
    if (-not (Test-Path -LiteralPath $PathValue)) {
        throw "$Name path does not exist: $PathValue"
    }
}

function Require-Venv {
    param([switch]$Bypass)

    if ($Bypass) {
        Write-Host "Skipping virtual environment check because -AllowNoVenv was provided." -ForegroundColor Yellow
        return
    }

    $venvPath = $env:VIRTUAL_ENV
    $condaPath = $env:CONDA_PREFIX

    if ([string]::IsNullOrWhiteSpace($venvPath) -and [string]::IsNullOrWhiteSpace($condaPath)) {
        throw @"
No active Python virtual environment detected.
Activate your environment first, then re-run this script.
Examples:
  Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
  & .\.venv\Scripts\Activate.ps1
"@
    }

    if (-not [string]::IsNullOrWhiteSpace($venvPath)) {
        Write-Host "Active venv: $venvPath" -ForegroundColor Green
    } elseif (-not [string]::IsNullOrWhiteSpace($condaPath)) {
        Write-Host "Active conda env: $condaPath" -ForegroundColor Green
    }
}

function Resolve-ChangedProtoFiles {
    param(
        [string]$RepoRoot,
        [string]$ComparedToBranch
    )

    $diffOutput = git -C $RepoRoot diff --name-only HEAD $ComparedToBranch -- "DomainModel/DomainModel.Protobuffer/ansys/api/discovery/*.proto"
    if (-not $diffOutput) {
        return @()
    }

    return @($diffOutput | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
}

function Copy-ProtoFiles {
    param(
        [string]$RepoRoot,
        [string]$PackageRoot,
        [string[]]$SourceRelativePaths
    )

    $copied = New-Object System.Collections.Generic.List[string]

    foreach ($rel in $SourceRelativePaths) {
        $normalizedRel = $rel.Replace("/", "\")
        $src = Join-Path $RepoRoot $normalizedRel

        if (-not (Test-Path -LiteralPath $src)) {
            throw "Source proto not found in ApiServer: $src"
        }

        $suffix = $normalizedRel.Replace("DomainModel\DomainModel.Protobuffer\", "")
        $dst = Join-Path $PackageRoot $suffix

        $dstDir = Split-Path -Parent $dst
        if (-not (Test-Path -LiteralPath $dstDir)) {
            if (-not $DryRun) {
                New-Item -ItemType Directory -Path $dstDir -Force | Out-Null
            }
        }

        if ($DryRun) {
            Write-Host "[DRY-RUN] Copy $src -> $dst"
        } else {
            Copy-Item -LiteralPath $src -Destination $dst -Force
            Write-Host "Copied: $rel"
        }

        $copied.Add($rel)
    }

    return $copied
}

Assert-CommandExists -Name "git"
Assert-CommandExists -Name "pip"

Assert-PathExists -PathValue $ProtosDir -Name "ProtosDir"
Assert-PathExists -PathValue $ApiServerRoot -Name "ApiServerRoot"
Require-Venv -Bypass:$AllowNoVenv

$protosDiscoveryDir = Join-Path $ProtosDir "ansys\api\discovery"
if (-not (Test-Path -LiteralPath $protosDiscoveryDir)) {
    throw "This does not look like an ansys-api-discovery clone: missing $protosDiscoveryDir"
}

Write-Host "\nThis workflow is local-only. Do not commit changes from ansys-api-discovery after running it." -ForegroundColor Yellow

if (-not $SkipClean) {
    Write-Step "Cleaning ansys-api-discovery with git clean -fdx"
    if ($DryRun) {
        Write-Host "[DRY-RUN] git -C $ProtosDir clean -fdx"
    } else {
        git -C $ProtosDir clean -fdx
    }
} else {
    Write-Host "Skipping clean because -SkipClean was provided." -ForegroundColor Yellow
}

$filesToCopy = @()

if ($ProtoFiles -and $ProtoFiles.Count -gt 0) {
    Write-Step "Using explicitly provided proto files"
    foreach ($file in $ProtoFiles) {
        $normalized = $file.Replace("/", "\")
        if ($normalized -notlike "DomainModel\DomainModel.Protobuffer\*") {
            $normalized = Join-Path "DomainModel\DomainModel.Protobuffer\ansys\api\discovery" $normalized
        }
        $filesToCopy += $normalized
    }
} else {
    Write-Step "Detecting changed discovery proto files in ApiServer (HEAD vs $BaseBranch)"
    $filesToCopy = Resolve-ChangedProtoFiles -RepoRoot $ApiServerRoot -ComparedToBranch $BaseBranch
}

if (-not $filesToCopy -or $filesToCopy.Count -eq 0) {
    Write-Host "No changed proto files detected or supplied. Nothing to copy." -ForegroundColor Yellow
} else {
    Write-Step "Copying proto source files to ansys-api-discovery"
    $copied = Copy-ProtoFiles -RepoRoot $ApiServerRoot -PackageRoot $ProtosDir -SourceRelativePaths $filesToCopy
    Write-Host "Total proto files copied: $($copied.Count)" -ForegroundColor Green
}

if (-not $SkipInstall) {
    Write-Step "Installing ansys-api-discovery from local clone"
    if ($DryRun) {
        Write-Host "[DRY-RUN] pip install . (cwd: $ProtosDir)"
    } else {
        Push-Location $ProtosDir
        try {
            pip install .
        } finally {
            Pop-Location
        }
    }
} else {
    Write-Host "Skipping installation because -SkipInstall was provided." -ForegroundColor Yellow
}

Write-Step "Done"
Write-Host "Local proto reinstall workflow completed." -ForegroundColor Green
Write-Host "Reminder: keep ansys-api-discovery changes local and uncommitted." -ForegroundColor Yellow
 