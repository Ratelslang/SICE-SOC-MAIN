@echo off
REM SICE SOC Portal launcher. Runs from the folder containing this file.
setlocal

set "SCRIPT_DIR=%~dp0"
set "PORT=8743"
set "URL=http://127.0.0.1:%PORT%/"
set "SERVER=%SCRIPT_DIR%sice_server.py"

if not exist "%SERVER%" (
  echo.
  echo ERROR: sice_server.py was not found next to this launcher.
  echo Download or clone the complete SICE SOC repository, then run this file again.
  echo.
  pause
  exit /b 1
)

powershell -NoProfile -Command "try { Invoke-WebRequest -UseBasicParsing -TimeoutSec 2 '%URL%health' ^| Out-Null; exit 0 } catch { exit 1 }" >nul 2>&1
if errorlevel 1 (
  echo Starting SICE portal server on port %PORT%...
  where py >nul 2>&1
  if not errorlevel 1 (
    start "SICE Portal Server" /b py -3 "%SERVER%" > "%TEMP%\sice_portal_server_%PORT%.log" 2>&1
  ) else (
    where python >nul 2>&1
    if not errorlevel 1 (
      start "SICE Portal Server" /b python "%SERVER%" > "%TEMP%\sice_portal_server_%PORT%.log" 2>&1
    ) else (
      echo.
      echo ERROR: Python 3 is required to start the SICE portal server.
      echo Install Python 3, then run this launcher again.
      echo.
      pause
      exit /b 1
    )
  )
  timeout /t 2 /nobreak >nul
)

start "" "%URL%"
exit /b 0
