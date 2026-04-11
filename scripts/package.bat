@echo off

echo ========================================
echo   SimpleIcoCreator Package Builder
echo ========================================

setlocal ENABLEDELAYEDEXPANSION

REM --- Define paths ---
set PROJECT_ROOT=%~dp0..
set DIST_DIR=%PROJECT_ROOT%\dist\SimpleIcoCreator
set SCRIPTS_DIR=%PROJECT_ROOT%\scripts
set BUILD_DIR=%PROJECT_ROOT%\build
set TEMP_DIR=%BUILD_DIR\temp_package

REM --- Get timestamp ---
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "YYYY=%dt:~0,4%"
set "MM=%dt:~4,2%"
set "DD=%dt:~6,2%"
set "HH=%dt:~8,2%"
set "Min=%dt:~10,2%"
set "Sec=%dt:~12,2%"
set "timestamp=%YYYY%%MM%%DD%_%HH%%Min%%Sec%"

set "ZIP_NAME=SimpleIcoCreator_%timestamp%.zip"
set "ZIP_PATH=%BUILD_DIR%\%ZIP_NAME%"

echo.
echo Creating package: %ZIP_NAME%
echo.

REM --- Verify required directories and files exist ---
if not exist "%DIST_DIR%" (
    echo ERROR: Dist directory not found: %DIST_DIR%
    echo Please build the project first.
    pause
    exit /b 1
)

if not exist "%DIST_DIR%\SimpleIcoCreator.exe" (
    echo ERROR: SimpleIcoCreator.exe not found in %DIST_DIR%
    echo Please build the project first.
    pause
    exit /b 1
)

if not exist "%SCRIPTS_DIR%\install.bat" (
    echo ERROR: install.bat not found in %SCRIPTS_DIR%
    pause
    exit /b 1
)

if not exist "%SCRIPTS_DIR%\uninstall.bat" (
    echo ERROR: uninstall.bat not found in %SCRIPTS_DIR%
    pause
    exit /b 1
)

REM --- Create build directory if it doesn't exist ---
if not exist "%BUILD_DIR%" (
    mkdir "%BUILD_DIR%"
)

REM --- Clean up previous temp directory if it exists ---
if exist "%TEMP_DIR%" (
    echo Cleaning up previous temp directory...
    rmdir /s /q "%TEMP_DIR%"
)

REM --- Create temporary package directory ---
mkdir "%TEMP_DIR%"

echo Copying files...

REM --- Copy the compiled program and its internal files ---
xcopy "%DIST_DIR%\*" "%TEMP_DIR%\" /E /H /C /I /Y

REM --- Copy install and uninstall scripts to the top level ---
copy "%SCRIPTS_DIR%\install.bat" "%TEMP_DIR%\" >nul
copy "%SCRIPTS_DIR%\uninstall.bat" "%TEMP_DIR%\" >nul

echo.
echo Creating zip file...

REM --- Create zip file using PowerShell ---
powershell -Command "Compress-Archive -Path '%TEMP_DIR%\*' -DestinationPath '%ZIP_PATH%' -Force"

if %errorlevel% neq 0 (
    echo ERROR: Failed to create zip file
    pause
    exit /b 1
)

REM --- Clean up temp directory ---
rmdir /s /q "%TEMP_DIR%"

echo.
echo Package created successfully!
echo Location: %ZIP_PATH%
echo.

pause
