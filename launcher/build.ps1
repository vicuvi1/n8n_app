# Build "n8n Command Center.exe" — run from project root or launcher folder
$ErrorActionPreference = "Stop"
$LauncherDir = $PSScriptRoot
$Root = Split-Path $LauncherDir -Parent

Write-Host "=== Building n8n Command Center.exe ===" -ForegroundColor Cyan

Set-Location $LauncherDir

# Use project venv or system Python
$Python = @(
    "$Root\.venv\Scripts\python.exe",
    (Get-Command py -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source),
    (Get-Command python -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source)
) | Where-Object { $_ -and (Test-Path $_) } | Select-Object -First 1

if (-not $Python) {
    Write-Host "ERROR: Python not found. Install Python 3.10+ first." -ForegroundColor Red
    exit 1
}

Write-Host "Using Python: $Python"
& $Python -m pip install -q -r requirements-build.txt

Write-Host "Generating icon..."
& $Python generate_icon.py

Write-Host "Running PyInstaller..."
& $Python -m PyInstaller --noconfirm --clean n8n_command_center.spec

$ExePath = Join-Path $LauncherDir "dist\n8n Command Center.exe"
if (Test-Path $ExePath) {
    Write-Host ""
    Write-Host "SUCCESS! Executable created:" -ForegroundColor Green
    Write-Host "  $ExePath"
    Write-Host ""
    Write-Host "Copy this .exe to your Desktop. On first run it will:"
    Write-Host "  - Clone/update from GitHub"
    Write-Host "  - Install Python dependencies"
    Write-Host "  - Open the dashboard in your browser"
} else {
    Write-Host "ERROR: Build failed - exe not found." -ForegroundColor Red
    exit 1
}
