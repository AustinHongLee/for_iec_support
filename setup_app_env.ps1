$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$guiVenvDir = Join-Path $repoRoot ".venv_gui"
$guiPython = Join-Path $guiVenvDir "Scripts\python.exe"
$requirements = Join-Path $repoRoot "python_app\requirements.txt"
$bundledPython = Join-Path $env:USERPROFILE ".cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"

function Get-BootstrapPython {
    if (Test-Path $bundledPython) {
        return @{ Executable = $bundledPython; PrefixArgs = @() }
    }

    $py = Get-Command py -ErrorAction SilentlyContinue
    if ($py) {
        & $py.Source -3 -c "import venv" *> $null
        if ($LASTEXITCODE -eq 0) {
            return @{ Executable = $py.Source; PrefixArgs = @("-3") }
        }
    }

    $python = Get-Command python -ErrorAction SilentlyContinue
    if ($python) {
        & $python.Source -c "import venv" *> $null
        if ($LASTEXITCODE -eq 0) {
            return @{ Executable = $python.Source; PrefixArgs = @() }
        }
    }

    return $null
}

$bootstrap = Get-BootstrapPython
if (-not $bootstrap) {
    Write-Host "Cannot create the GUI environment: Python 3 with venv was not found." -ForegroundColor Red
    Write-Host "Install Python 3.10+ from python.org, then run run_app.cmd again." -ForegroundColor Yellow
    exit 1
}

if (-not (Test-Path $guiPython)) {
    Write-Host "Creating GUI virtual environment: $guiVenvDir" -ForegroundColor Green
    & $bootstrap.Executable @($bootstrap.PrefixArgs) -m venv $guiVenvDir
}

$venvHasPip = $false
& $guiPython -m pip --version *> $null
if ($LASTEXITCODE -eq 0) {
    $venvHasPip = $true
}

if ($venvHasPip) {
    Write-Host "Upgrading pip..." -ForegroundColor Green
    & $guiPython -m pip install --upgrade pip

    Write-Host "Installing GUI requirements..." -ForegroundColor Green
    & $guiPython -m pip install -r $requirements
} else {
    $sitePackages = Join-Path $guiVenvDir "Lib\site-packages"
    Write-Host "Venv pip is unavailable; installing via bundled pip target:" -ForegroundColor Yellow
    Write-Host "  $sitePackages"
    & $bootstrap.Executable @($bootstrap.PrefixArgs) -m pip install --upgrade -r $requirements --target $sitePackages
}

& $guiPython -c "import PyQt6" *> $null
if ($LASTEXITCODE -ne 0) {
    Write-Host "GUI environment setup failed: PyQt6 is still unavailable." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "GUI environment is ready." -ForegroundColor Green
Write-Host "Run the app with:"
Write-Host "  .\run_app.ps1"
