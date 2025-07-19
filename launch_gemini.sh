#!/bin/bash
# DevEnviro + Gemini CLI Integrated Launcher (Linux/WSL)
# Flexible launcher with multiple options

# Default values
DEVENVIRO_ONLY=0
GEMINI_ONLY=0
SKIP_INTERACTIVE=0
PROJECT_PATH=""
GEMINI_MODE="chat"
SHOW_HELP=0

# Function to show help
show_help() {
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --devenviro-only     Run DevEnviro startup only (no Gemini CLI)"
    echo "  --gemini-only        Launch Gemini CLI only (skip DevEnviro)"
    echo "  --skip-interactive   Skip DevEnviro interactive menu"
    echo "  --project-path PATH  Launch in specific project directory"
    echo "  --gemini-mode MODE   Gemini CLI mode (chat, code, generate, analyze)"
    echo "  --help, -h           Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                          # Full integrated launch"
    echo "  $0 --devenviro-only         # DevEnviro only"
    echo "  $0 --gemini-only            # Gemini CLI only"
    echo "  $0 --skip-interactive       # Non-interactive mode"
    echo "  $0 --gemini-mode code       # Start in code mode"
    echo "  $0 --project-path /path/to/project  # Specific project"
    echo ""
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --devenviro-only)
            DEVENVIRO_ONLY=1
            shift
            ;;
        --gemini-only)
            GEMINI_ONLY=1
            shift
            ;;
        --skip-interactive)
            SKIP_INTERACTIVE=1
            shift
            ;;
        --project-path)
            PROJECT_PATH="$2"
            shift 2
            ;;
        --gemini-mode)
            GEMINI_MODE="$2"
            shift 2
            ;;
        --help|-h)
            SHOW_HELP=1
            shift
            ;;
        *)
            echo "[WARNING] Unknown option: $1"
            shift
            ;;
    esac
done

echo "DevEnviro + Gemini CLI Integrated Launcher"
echo "=========================================="

# Show help if requested
if [ $SHOW_HELP -eq 1 ]; then
    show_help
    exit 0
fi

# Change to script directory
cd "$(dirname "$0")"

# Handle project path change
if [ -n "$PROJECT_PATH" ]; then
    echo "[INFO] Switching to project: $PROJECT_PATH"
    if [ -d "$PROJECT_PATH" ]; then
        cd "$PROJECT_PATH"
    else
        echo "[ERROR] Project path does not exist: $PROJECT_PATH"
        exit 1
    fi
fi

# Step 1: Run DevEnviro startup (unless gemini-only)
if [ $GEMINI_ONLY -eq 0 ]; then
    echo ""
    echo "[LAUNCHER] Starting DevEnviro initialization..."
    
    if [ $SKIP_INTERACTIVE -eq 1 ]; then
        echo "[INFO] Running DevEnviro in non-interactive mode"
        echo "7" | python3 devenviro_startup.py
    else
        python3 devenviro_startup.py
    fi
    
    if [ $? -ne 0 ]; then
        echo "[WARNING] DevEnviro startup failed, continuing anyway..."
    else
        echo "[SUCCESS] DevEnviro startup completed"
    fi
fi

# Step 2: Launch Gemini CLI (unless devenviro-only)
if [ $DEVENVIRO_ONLY -eq 0 ]; then
    echo ""
    echo "[LAUNCHER] Starting Gemini CLI..."
    
    # Try different Gemini CLI commands
    if command -v gemini >/dev/null 2>&1; then
        echo "[INFO] Launching Gemini CLI in $GEMINI_MODE mode..."
        case $GEMINI_MODE in
            chat)
                gemini chat
                ;;
            code)
                gemini generate --type code
                ;;
            generate)
                gemini generate
                ;;
            analyze)
                gemini analyze --path .
                ;;
            *)
                gemini chat
                ;;
        esac
        echo "[SUCCESS] Gemini CLI session ended"
    elif command -v gemini-cli >/dev/null 2>&1; then
        echo "[INFO] Launching Gemini CLI in $GEMINI_MODE mode..."
        gemini-cli $GEMINI_MODE
        echo "[SUCCESS] Gemini CLI session ended"
    elif python3 -c "import google.generativeai" >/dev/null 2>&1; then
        echo "[INFO] Using Python Gemini API in $GEMINI_MODE mode..."
        python3 -c "
import google.generativeai as genai
import os
print('[INFO] Starting Gemini CLI session...')
print('=' * 50)
print('Gemini CLI session would start here')
print('Install official Gemini CLI for full functionality')
print('Visit: https://ai.google.dev/gemini-api/docs/quickstart')
print('=' * 50)
"
        echo "[SUCCESS] Python Gemini session completed"
    else
        echo "[ERROR] Gemini CLI not found"
        echo "[INFO] Please install Gemini CLI:"
        echo "       pip install google-generativeai"
        echo "       or visit: https://ai.google.dev/gemini-api/docs/quickstart"
        exit 1
    fi
fi

echo ""
echo "[SUCCESS] Launch sequence completed!"
if [ $DEVENVIRO_ONLY -eq 1 ]; then
    echo "DevEnviro workspace is ready for development."
elif [ $GEMINI_ONLY -eq 1 ]; then
    echo "Gemini CLI session has ended."
else
    echo "DevEnviro workspace is initialized and Gemini CLI session has ended."
fi

# Wait a moment for processes to complete
sleep 1