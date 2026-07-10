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
    Write-Host "Preparing the GUI environment for the first launch..." -ForegroundColor Yellow
    & (Join-Path $repoRoot "setup_app_env.ps1")
    if ($LASTEXITCODE -ne 0 -or -not (Test-PythonModule -PythonPath $guiVenvPython -ModuleName "PyQt6")) {
        Write-Host "Cannot launch IEC app: GUI environment setup did not complete." -ForegroundColor Red
        exit 1
    }
    $pythonPath = $guiVenvPython
}

Set-Location $appDir
Write-Host "Launching IEC app with: $pythonPath" -ForegroundColor Green
if ($CheckOnly) {
    & $pythonPath -c "from PyQt6.QtWidgets import QApplication; import main; print('IEC app launch check OK')"
    exit $LASTEXITCODE
}
& $pythonPath "main.py"
