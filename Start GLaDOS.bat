@echo off
setlocal
cd /d "%~dp0"
where uv >nul 2>nul
if errorlevel 1 (
    echo uv was not found. Install uv, then run this file again.
    pause
    exit /b 1
)
where wt >nul 2>nul
if errorlevel 1 (
    echo Windows Terminal was not found. Install Windows Terminal, then run this file again.
    pause
    exit /b 1
)
wt -d "%~dp0" cmd /k "uv run glados-tui"
