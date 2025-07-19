@echo off
REM DevEnviro Session Signoff (Windows)
REM Quick launcher for session closing protocol

echo DevEnviro Session Signoff
echo ========================

REM Change to script directory
cd /d "%~dp0"

REM Run the Python signoff script
python session_signoff.py

REM Keep window open if there were errors
if %ERRORLEVEL% neq 0 (
    echo.
    echo Press any key to continue...
    pause >nul
)