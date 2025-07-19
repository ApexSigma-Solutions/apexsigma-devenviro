@echo off
REM DevEnviro Enhanced Startup Script
REM Quick launcher for cognitive collaboration workspace

echo DevEnviro Enhanced Startup
echo ========================

REM Change to DevEnviro directory
cd /d "%~dp0"

REM Run the Python startup script
python devenviro_startup.py

REM Keep window open if there were errors
if %ERRORLEVEL% neq 0 (
    echo.
    echo Press any key to continue...
    pause >nul
)