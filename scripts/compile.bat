@echo off

echo ========================================
echo   SimpleIcoCreator Compiler
echo ========================================

setlocal ENABLEDELAYEDEXPANSION

REM --- Define paths ---
set PROJECT_ROOT=%~dp0..
set VENV_PYTHON=%PROJECT_ROOT%\.venv\Scripts\python.exe

echo.
echo Checking dependencies...

REM --- Check if virtual environment exists ---
if not exist "%VENV_PYTHON%" (
    echo ERROR: Virtual environment not found: %VENV_PYTHON%
    echo Please create a virtual environment first.
    pause
    exit /b 1
)

echo.
echo Starting compilation...
echo.

REM --- Run PyInstaller command ---
"%VENV_PYTHON%" -m PyInstaller ^
    --noconfirm ^
    --onedir ^
    --windowed ^
    --icon "E:\GitHub Repositories\SimpleIcoCreator\src\static\icon.ico" ^
    --name "SimpleIcoCreator" ^
    --add-data "E:\GitHub Repositories\SimpleIcoCreator\src\static;static/" ^
    --distpath "E:\GitHub Repositories\SimpleIcoCreator\dist" ^
    "E:\GitHub Repositories\SimpleIcoCreator\src\main.py"

if %errorlevel% neq 0 (
    echo ERROR: Compilation failed
    pause
    exit /b 1
)

echo.
echo Compilation completed successfully!

echo.
echo Cleaning up build files...

REM --- Remove PyInstaller build folder in current working directory ---
if exist "%CD%\build" (
    rmdir /s /q "%CD%\build"
)

REM --- Remove spec file in current working directory ---
if exist "%CD%\SimpleIcoCreator.spec" (
    del /q "%CD%\SimpleIcoCreator.spec"
)

echo Cleanup completed.

pause
