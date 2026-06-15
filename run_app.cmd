@echo off
setlocal
pwsh -NoProfile -ExecutionPolicy Bypass -File "%~dp0run_app.ps1"
endlocal
