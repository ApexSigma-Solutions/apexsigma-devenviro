#Requires -Version 5.1
<#
.SYNOPSIS
    DevEnviro + Claude Code Integrated Launcher (PowerShell)

.DESCRIPTION
    Flexible launcher with multiple options for DevEnviro and Claude Code integration.
    Cross-platform PowerShell script that works on Windows, Linux, and macOS.

.PARAMETER DevEnviroOnly
    Run DevEnviro startup only (no Claude Code)

.PARAMETER ClaudeOnly
    Launch Claude Code only (skip DevEnviro)

.PARAMETER SkipInteractive
    Skip DevEnviro interactive menu

.PARAMETER ProjectPath
    Launch in specific project directory

.PARAMETER Help
    Show help message

.EXAMPLE
    .\launch_claude.ps1
    Full integrated launch

.EXAMPLE
    .\launch_claude.ps1 -DevEnviroOnly
    DevEnviro startup only

.EXAMPLE
    .\launch_claude.ps1 -ClaudeOnly
    Claude Code only

.EXAMPLE
    .\launch_claude.ps1 -SkipInteractive
    Non-interactive mode
#>

[CmdletBinding()]
param(
    [switch]$DevEnviroOnly,
    [switch]$ClaudeOnly, 
    [switch]$SkipInteractive,
    [string]$ProjectPath,
    [switch]$Help
)

# Windows-safe output functions
function Write-Status {
    param([string]$Status, [string]$Message)
    $prefix = switch ($Status) {
        'SUCCESS' { '[SUCCESS]' }
        'ERROR' { '[ERROR]' }
        'WARNING' { '[WARNING]' }
        'INFO' { '[INFO]' }
        'LAUNCHER' { '[LAUNCHER]' }
        default { "[$Status]" }
    }
    Write-Host "$prefix $Message"
}

function Write-Success { param([string]$Message) Write-Status 'SUCCESS' $Message }
function Write-Error { param([string]$Message) Write-Status 'ERROR' $Message }
function Write-Warning { param([string]$Message) Write-Status 'WARNING' $Message }
function Write-Info { param([string]$Message) Write-Status 'INFO' $Message }
function Write-Launcher { param([string]$Message) Write-Status 'LAUNCHER' $Message }

# Show help
if ($Help) {
    Write-Host ""
    Write-Host "DevEnviro + Claude Code Integrated Launcher"
    Write-Host "=========================================="
    Write-Host ""
    Write-Host "Usage: .\launch_claude.ps1 [PARAMETERS]"
    Write-Host ""
    Write-Host "Parameters:"
    Write-Host "  -DevEnviroOnly     Run DevEnviro startup only (no Claude Code)"
    Write-Host "  -ClaudeOnly        Launch Claude Code only (skip DevEnviro)"
    Write-Host "  -SkipInteractive   Skip DevEnviro interactive menu"
    Write-Host "  -ProjectPath PATH  Launch in specific project directory"
    Write-Host "  -Help              Show this help message"
    Write-Host ""
    Write-Host "Examples:"
    Write-Host "  .\launch_claude.ps1                    # Full integrated launch"
    Write-Host "  .\launch_claude.ps1 -DevEnviroOnly     # DevEnviro only"
    Write-Host "  .\launch_claude.ps1 -ClaudeOnly        # Claude Code only"
    Write-Host "  .\launch_claude.ps1 -SkipInteractive   # Non-interactive mode"
    Write-Host ""
    exit 0
}

Write-Host "DevEnviro + Claude Code Integrated Launcher"
Write-Host "=========================================="

# Change to script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

# Handle project path change
if ($ProjectPath) {
    Write-Info "Switching to project: $ProjectPath"
    if (Test-Path $ProjectPath) {
        Set-Location $ProjectPath
    } else {
        Write-Error "Project path does not exist: $ProjectPath"
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# Step 1: Run DevEnviro startup (unless claude-only)
if (-not $ClaudeOnly) {
    Write-Host ""
    Write-Launcher "Starting DevEnviro initialization..."
    
    try {
        if ($SkipInteractive) {
            Write-Info "Running DevEnviro in non-interactive mode"
            # Send "7" (exit option) to DevEnviro startup
            "7" | python devenviro_startup.py
        } else {
            python devenviro_startup.py
        }
        
        if ($LASTEXITCODE -ne 0) {
            Write-Warning "DevEnviro startup failed, continuing anyway..."
        } else {
            Write-Success "DevEnviro startup completed"
        }
    } catch {
        Write-Warning "DevEnviro startup encountered an error: $_"
    }
}

# Step 2: Launch Claude Code (unless devenviro-only)
if (-not $DevEnviroOnly) {
    Write-Host ""
    Write-Launcher "Starting Claude Code..."
    
    # Try claude-code command first
    if (Get-Command "claude-code" -ErrorAction SilentlyContinue) {
        Write-Info "Launching Claude Code..."
        try {
            Start-Process "claude-code" -ArgumentList "." -NoNewWindow:$false
            Write-Success "Claude Code launched"
        } catch {
            Write-Error "Failed to launch Claude Code: $_"
        }
    } 
    # Fallback to VS Code
    elseif (Get-Command "code" -ErrorAction SilentlyContinue) {
        Write-Info "Claude Code not found, launching VS Code as fallback..."
        try {
            Start-Process "code" -ArgumentList "." -NoNewWindow:$false
            Write-Success "VS Code launched as fallback"
        } catch {
            Write-Error "Failed to launch VS Code: $_"
        }
    }
    else {
        Write-Error "Neither 'claude-code' nor 'code' commands found"
        Write-Info "Please install Claude Code CLI or VS Code"
        Read-Host "Press Enter to exit"
        exit 1
    }
}

Write-Host ""
Write-Success "Launch sequence completed!"

if ($DevEnviroOnly) {
    Write-Host "DevEnviro workspace is ready for development."
} elseif ($ClaudeOnly) {
    Write-Host "Claude Code is starting..."
} else {
    Write-Host "DevEnviro workspace is initialized and Claude Code is starting..."
}

Write-Host ""
Read-Host "Press Enter to exit"
exit 0