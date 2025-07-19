@echo off
REM DevEnviro + Gemini CLI Integrated Launcher (Windows)
REM Flexible launcher with multiple options

setlocal EnableDelayedExpansion

echo DevEnviro + Gemini CLI Integrated Launcher
echo ==========================================

REM Change to script directory
cd /d "%~dp0"

REM Parse command line arguments
set DEVENVIRO_ONLY=0
set GEMINI_ONLY=0
set SKIP_INTERACTIVE=0
set PROJECT_PATH=
set GEMINI_MODE=chat
set SHOW_HELP=0

:parse_args
if "%~1"=="" goto end_parse
if "%~1"=="--devenviro-only" (
    set DEVENVIRO_ONLY=1
    shift
    goto parse_args
)
if "%~1"=="--gemini-only" (
    set GEMINI_ONLY=1
    shift
    goto parse_args
)
if "%~1"=="--skip-interactive" (
    set SKIP_INTERACTIVE=1
    shift
    goto parse_args
)
if "%~1"=="--project-path" (
    set PROJECT_PATH=%~2
    shift
    shift
    goto parse_args
)
if "%~1"=="--gemini-mode" (
    set GEMINI_MODE=%~2
    shift
    shift
    goto parse_args
)
if "%~1"=="--help" (
    set SHOW_HELP=1
    shift
    goto parse_args
)
if "%~1"=="-h" (
    set SHOW_HELP=1
    shift
    goto parse_args
)
REM Unknown argument, skip it
shift
goto parse_args

:end_parse

REM Show help if requested
if %SHOW_HELP%==1 (
    echo.
    echo Usage: launch_gemini.bat [OPTIONS]
    echo.
    echo Options:
    echo   --devenviro-only     Run DevEnviro startup only ^(no Gemini CLI^)
    echo   --gemini-only        Launch Gemini CLI only ^(skip DevEnviro^)
    echo   --skip-interactive   Skip DevEnviro interactive menu
    echo   --project-path PATH  Launch in specific project directory
    echo   --gemini-mode MODE   Gemini CLI mode ^(chat, code, generate, analyze^)
    echo   --help, -h           Show this help message
    echo.
    echo Examples:
    echo   launch_gemini.bat                          # Full integrated launch
    echo   launch_gemini.bat --devenviro-only         # DevEnviro only
    echo   launch_gemini.bat --gemini-only            # Gemini CLI only
    echo   launch_gemini.bat --skip-interactive       # Non-interactive mode
    echo   launch_gemini.bat --gemini-mode code       # Start in code mode
    echo.
    goto end
)

REM Handle project path change
if not "%PROJECT_PATH%"=="" (
    echo [INFO] Switching to project: %PROJECT_PATH%
    if exist "%PROJECT_PATH%" (
        cd /d "%PROJECT_PATH%"
    ) else (
        echo [ERROR] Project path does not exist: %PROJECT_PATH%
        goto error_exit
    )
)

REM Step 1: Run DevEnviro startup (unless gemini-only)
if %GEMINI_ONLY%==0 (
    echo.
    echo [LAUNCHER] Starting DevEnviro initialization...
    
    if %SKIP_INTERACTIVE%==1 (
        echo [INFO] Running DevEnviro in non-interactive mode
        echo 7 | python devenviro_startup.py
    ) else (
        python devenviro_startup.py
    )
    
    if %ERRORLEVEL% neq 0 (
        echo [WARNING] DevEnviro startup failed, continuing anyway...
    ) else (
        echo [SUCCESS] DevEnviro startup completed
    )
)

REM Step 2: Launch Gemini CLI (unless devenviro-only)
if %DEVENVIRO_ONLY%==0 (
    echo.
    echo [LAUNCHER] Starting Gemini CLI...
    
    REM Try different Gemini CLI commands
    where gemini >nul 2>&1
    if %ERRORLEVEL%==0 (
        echo [INFO] Launching Gemini CLI in %GEMINI_MODE% mode...
        if "%GEMINI_MODE%"=="chat" (
            gemini chat
        ) else if "%GEMINI_MODE%"=="code" (
            gemini generate --type code
        ) else if "%GEMINI_MODE%"=="generate" (
            gemini generate
        ) else if "%GEMINI_MODE%"=="analyze" (
            gemini analyze --path .
        ) else (
            gemini chat
        )
        echo [SUCCESS] Gemini CLI session ended
    ) else (
        where gemini-cli >nul 2>&1
        if %ERRORLEVEL%==0 (
            echo [INFO] Launching Gemini CLI in %GEMINI_MODE% mode...
            gemini-cli %GEMINI_MODE%
            echo [SUCCESS] Gemini CLI session ended
        ) else (
            REM Try python-based approach
            python -c "import google.generativeai" >nul 2>&1
            if %ERRORLEVEL%==0 (
                echo [INFO] Using Python Gemini API in %GEMINI_MODE% mode...
                python -c "
import google.generativeai as genai
import os
print('[INFO] Starting Gemini CLI session...')
print('=' * 50)
print('Gemini CLI session would start here')
print('Install official Gemini CLI for full functionality')
print('=' * 50)
"
                echo [SUCCESS] Python Gemini session completed
            ) else (
                echo [ERROR] Gemini CLI not found
                echo [INFO] Please install Gemini CLI:
                echo         pip install google-generativeai
                echo         or visit: https://ai.google.dev/gemini-api/docs/quickstart
                goto error_exit
            )
        )
    )
)

echo.
echo [SUCCESS] Launch sequence completed!
if %DEVENVIRO_ONLY%==1 (
    echo DevEnviro workspace is ready for development.
) else if %GEMINI_ONLY%==1 (
    echo Gemini CLI session has ended.
) else (
    echo DevEnviro workspace is initialized and Gemini CLI session has ended.
)

goto end

:error_exit
echo.
echo [ERROR] Launch sequence encountered issues
pause
exit /b 1

:end
pause
exit /b 0