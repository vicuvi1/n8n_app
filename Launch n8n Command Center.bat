@echo off
title n8n Command Center
cd /d "%~dp0"

echo.
echo  n8n Command Center - starting...
echo.

where py >nul 2>&1
if %errorlevel%==0 (
    py -3 launcher\launcher.py
) else (
    python launcher\launcher.py
)

if errorlevel 1 (
    echo.
    echo  Launcher exited with an error.
    pause
)
