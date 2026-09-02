@echo off
REM SICE SOC MAIN Portal Launcher
REM Double-click this file to open the portal in your default browser

setlocal enabledelayedexpansion

REM Get the directory where this batch file is located
set "SCRIPT_DIR=%~dp0"
set "PORTAL_FILE=%SCRIPT_DIR%SICE_SOC_MAIN.html"

REM Check if the file exists
if not exist "%PORTAL_FILE%" (
    echo.
    echo ERROR: SICE_SOC_MAIN.html not found!
    echo.
    echo Please make sure SICE_SOC_MAIN.html is in the same folder as this launcher.
    echo.
    pause
    exit /b 1
)

REM Open the portal in default browser
start "" "%PORTAL_FILE%"

REM Optional: Wait a moment then exit
timeout /t 2 /nobreak
exit /b 0
