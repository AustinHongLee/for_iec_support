param(
    [switch]$CheckOnly
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$appDir = Join-Path $repoRoot "python_app"
$guiVenvPython = Join-Path $repoRoot ".venv_gui\Scripts\python.exe"
$venvPython = Join-Path $repoRoot ".venv\Scripts\python.exe"
$bundledPython = Join-Path $env:USERPROFILE ".cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"

function Test-PythonModule {
    param(
        [string]$PythonPath,
        [string]$ModuleName
    )

    if (-not (Test-Path $PythonPath)) {
        return $false
    }

    & $PythonPath -c "import $ModuleName" *> $null
    return ($LASTEXITCODE -eq 0)
}

$pythonPath = $null

if (Test-PythonModule -PythonPath $guiVenvPython -ModuleName "PyQt6") {
    $pythonPath = $guiVenvPython
} elseif (Test-PythonModule -PythonPath $venvPython -ModuleName "PyQt6") {
    $pythonPath = $venvPython
} elseif (Test-PythonModule -PythonPath $bundledPython -ModuleName "PyQt6") {
    $pythonPath = $bundledPython
}

if (-not $pythonPath) {
    Write-Host "Cannot launch IEC app: no usable Python with PyQt6 was found." -ForegroundColor Red
    Write-Host ""
    Write-Host "Checked:" -ForegroundColor Yellow
    Write-Host "  $guiVenvPython"
    Write-Host "  $venvPython"
    Write-Host "  $bundledPython"
    Write-Host ""
    Write-Host "Suggested fix:" -ForegroundColor Yellow
    Write-Host "  Run .\setup_app_env.ps1 once, then run:"
    Write-Host "  .\run_app.ps1"
    exit 1
}

Set-Location $appDir
Write-Host "Launching IEC app with: $pythonPath" -ForegroundColor Green
if ($CheckOnly) {
    & $pythonPath -c "from PyQt6.QtWidgets import QApplication; import main; print('IEC app launch check OK')"
    exit $LASTEXITCODE
}
& $pythonPath "main.py"
