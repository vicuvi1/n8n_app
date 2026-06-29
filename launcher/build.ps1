# Build "n8n Command Center.exe" and copy to Desktop
$ErrorActionPreference = "Stop"
$LauncherDir = $PSScriptRoot
$Root = Split-Path $LauncherDir -Parent
$Desktop = [Environment]::GetFolderPath("Desktop")

Write-Host ""
Write-Host "=== n8n Command Center - Build EXE ===" -ForegroundColor Cyan
Write-Host ""

Set-Location $LauncherDir

$Python = @(
    "$Root\.venv\Scripts\python.exe",
    (Get-Command py -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source),
    (Get-Command python -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source)
) | Where-Object { $_ -and (Test-Path $_) } | Select-Object -First 1

if (-not $Python) {
    Write-Host "ERROR: Python 3.10+ not found. Install from https://www.python.org/downloads/" -ForegroundColor Red
    exit 1
}

Write-Host "Using Python: $Python"
& $Python -m pip install -q -r requirements-build.txt

if (-not (Test-Path "$Root\assets\icon.ico")) {
    Write-Host "Generating icon..."
    & $Python generate_icon.py
}

Write-Host "Building executable (PyInstaller)..."
& $Python -m PyInstaller --noconfirm --clean n8n_command_center.spec

$ExePath = Join-Path $LauncherDir "dist\n8n Command Center.exe"
if (-not (Test-Path $ExePath)) {
    Write-Host "ERROR: Build failed - exe not found." -ForegroundColor Red
    exit 1
}

$DesktopExe = Join-Path $Desktop "n8n Command Center.exe"
Copy-Item -Path $ExePath -Destination $DesktopExe -Force

Write-Host ""
Write-Host "SUCCESS!" -ForegroundColor Green
Write-Host "  Built:  $ExePath"
Write-Host "  Copied: $DesktopExe"
Write-Host ""
Write-Host "Double-click the Desktop icon to:"
Write-Host "  1. Pull latest code from GitHub"
Write-Host "  2. Install/update Python packages"
Write-Host "  3. Open http://localhost:8501 in your browser"
Write-Host ""
Write-Host "Requires: Python 3.10+ and Git (installed once on your PC)."
Write-Host ""
