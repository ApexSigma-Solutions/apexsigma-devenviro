#!/bin/bash
# DevEnviro + Claude Code Integrated Launcher (Linux/WSL)
# Flexible launcher with multiple options

# Default values
DEVENVIRO_ONLY=0
CLAUDE_ONLY=0
SKIP_INTERACTIVE=0
PROJECT_PATH=""
SHOW_HELP=0

# Function to show help
show_help() {
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --devenviro-only     Run DevEnviro startup only (no Claude Code)"
    echo "  --claude-only        Launch Claude Code only (skip DevEnviro)"
    echo "  --skip-interactive   Skip DevEnviro interactive menu"
    echo "  --project-path PATH  Launch in specific project directory"
    echo "  --help, -h           Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                          # Full integrated launch"
    echo "  $0 --devenviro-only         # DevEnviro only"
    echo "  $0 --claude-only            # Claude Code only"
    echo "  $0 --skip-interactive       # Non-interactive mode"
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
        --claude-only)
            CLAUDE_ONLY=1
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

echo "DevEnviro + Claude Code Integrated Launcher"
echo "==========================================="

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

# Step 1: Run DevEnviro startup (unless claude-only)
if [ $CLAUDE_ONLY -eq 0 ]; then
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

# Step 2: Launch Claude Code (unless devenviro-only)
if [ $DEVENVIRO_ONLY -eq 0 ]; then
    echo ""
    echo "[LAUNCHER] Starting Claude Code..."
    
    # Try claude-code command first
    if command -v claude-code >/dev/null 2>&1; then
        echo "[INFO] Launching Claude Code..."
        claude-code . &
        echo "[SUCCESS] Claude Code launched"
    elif command -v code >/dev/null 2>&1; then
        # Fallback to VS Code
        echo "[INFO] Claude Code not found, launching VS Code as fallback..."
        code . &
        echo "[SUCCESS] VS Code launched as fallback"
    else
        echo "[ERROR] Neither 'claude-code' nor 'code' commands found"
        echo "[INFO] Please install Claude Code CLI or VS Code"
        exit 1
    fi
fi

echo ""
echo "[SUCCESS] Launch sequence completed!"
if [ $DEVENVIRO_ONLY -eq 1 ]; then
    echo "DevEnviro workspace is ready for development."
elif [ $CLAUDE_ONLY -eq 1 ]; then
    echo "Claude Code is starting..."
else
    echo "DevEnviro workspace is initialized and Claude Code is starting..."
fi

# Wait a moment for processes to start
sleep 1