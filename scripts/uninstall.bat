@echo off

:: --- Auto-elevate to admin ---
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo Requesting administrative privileges...
    powershell -Command "Start-Process '%~f0' -ArgumentList 'elevated' -Verb RunAs"
    exit /b
)
if "%1"=="elevated" shift

echo ========================================
echo   Remove Context Menu Entry
echo ========================================

echo Removing context menu...

reg delete "HKCR\SystemFileAssociations\image\shell\ConvertToIco" /f
reg delete "HKCR\.webp\shell\ConvertToIco" /f

echo.
echo Context menu entry removed.
echo Files remain in Program Files.
echo.

pause