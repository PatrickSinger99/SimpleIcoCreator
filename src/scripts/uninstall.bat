@echo off

echo ========================================
echo   Remove Context Menu Entry
echo ========================================

REM --- Check for admin rights ---
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo Please run this script as Administrator.
    pause
    exit /b
)

echo Removing context menu...

reg delete "HKCR\SystemFileAssociations\image\shell\ConvertToIco" /f

echo.
echo Context menu entry removed.
echo Files remain in Program Files.
echo.

pause