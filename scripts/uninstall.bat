@echo off

setlocal ENABLEDELAYEDEXPANSION

:: --- Store script directory BEFORE elevation ---
set "SCRIPT_DIR=%~dp0"

:: --- Auto-elevate to admin ---
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo Requesting administrative privileges...
    powershell -Command "Start-Process '%~f0' -ArgumentList \"%SCRIPT_DIR%\" -Verb RunAs"
    exit /b
)

:: --- Restore script directory after elevation ---
if not "%~1"=="" set "SCRIPT_DIR=%~1"

echo ========================================
echo   Remove Context Menu Entry
echo ========================================

echo Removing context menu...

reg delete "HKCR\SystemFileAssociations\image\shell\ConvertToIco" /f

echo.
echo Context menu entry removed.
echo Files remain in Program Files.
echo.

pause