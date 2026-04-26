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
echo   SimpleIcoCreator Installation
echo ========================================

REM --- Define install directory ---
set "INSTALL_DIR=%ProgramFiles%\SimpleIcoCreator"

REM --- Source directory ---
set "SOURCE_DIR=%SCRIPT_DIR%"

echo.
echo Installing from:
echo %SOURCE_DIR%
echo Installing to:
echo %INSTALL_DIR%
echo.

REM --- Create install directory if it doesn't exist ---
if not exist "%INSTALL_DIR%" (
    mkdir "%INSTALL_DIR%"
)

REM --- Copy all files ---
echo Copying files...
xcopy "%SOURCE_DIR%*" "%INSTALL_DIR%\" /E /H /C /I /Y

REM --- Define exe path ---
set "EXE_PATH=%INSTALL_DIR%\SimpleIcoCreator.exe"

REM --- Verify exe exists ---
if not exist "%EXE_PATH%" (
    echo ERROR: EXE not found after copy!
    echo Expected: %EXE_PATH%
    pause
    exit /b
)

REM --- Add context menu entry for general image types ---
echo Adding context menu...

REM --- Add .webp to general image group ---

reg add "HKCR\SystemFileAssociations\image\shell\ConvertToIco" /ve /d "Convert to ICO" /f
reg add "HKCR\SystemFileAssociations\image\shell\ConvertToIco" /v "Icon" /d "\"%EXE_PATH%\"" /f
reg add "HKCR\SystemFileAssociations\image\shell\ConvertToIco\command" /ve /d "\"%EXE_PATH%\" \"%%1\"" /f

reg add "HKCR\SystemFileAssociations\.webp\shell\ConvertToIco" /ve /d "Convert to ICO" /f
reg add "HKCR\SystemFileAssociations\.webp\shell\ConvertToIco" /v "Icon" /d "\"%EXE_PATH%\"" /f
reg add "HKCR\SystemFileAssociations\.webp\shell\ConvertToIco\command" /ve /d "\"%EXE_PATH%\" \"%%1\"" /f

echo.
echo Installation complete.
echo Right-click any image to use "Convert to ICO".
echo.

pause