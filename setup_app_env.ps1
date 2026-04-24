$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$guiVenvDir = Join-Path $repoRoot ".venv_gui"
$guiPython = Join-Path $guiVenvDir "Scripts\python.exe"
$requirements = Join-Path $repoRoot "python_app\requirements.txt"
$bundledPython = Join-Path $env:USERPROFILE ".cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"

if (-not (Test-Path $bundledPython)) {
    Write-Host "Cannot find bundled Python:" -ForegroundColor Red
    Write-Host "  $bundledPython"
    exit 1
}

if (-not (Test-Path $guiPython)) {
Write-Host "Creating GUI virtual environment: $guiVenvDir" -ForegroundColor Green
    & $bundledPython -m venv $guiVenvDir
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
    & $bundledPython -m pip install --upgrade -r $requirements --target $sitePackages
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
