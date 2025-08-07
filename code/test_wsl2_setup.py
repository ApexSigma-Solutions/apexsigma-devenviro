#!/usr/bin/env python3
"""
Test script for WSL2 environment setup
"""
import os
import platform
import subprocess
from pathlib import Path
from devenviro.terminal_output import print_success, print_error, print_warning, safe_print, print_info


def test_wsl2_environment():
    """Test our WSL2 development environment"""
    print_info("[TEST] Testing WSL2 ApexSigma DevEnviro Setup")

    # Check we're in WSL2
    safe_print("[SYSTEM] Environment Check:")
    print(f"   Platform: {platform.system()}")
    print(f"   Machine: {platform.machine()}")

    # Check if we're in WSL
    try:
        with open("/proc/version", "r") as f:
            version_info = f.read()
            if "Microsoft" in version_info or "WSL" in version_info:
                safe_print("   [SUCCESS] Running in WSL2")
            else:
                print("   ❓ May not be in WSL2 (or /proc/version doesn't contain 'Microsoft' or 'WSL')")
    except FileNotFoundError:
        safe_print("   [ERROR] Not running in a standard Linux environment (/proc/version not found).")

    print()

    # Check project structure
    project_root = Path.home() / "apexsigma-project"
    safe_print("[FOLDER] Project Structure:")

    required_folders = ["code", "config", "docs", "logs"]
    for folder in required_folders:
        if (project_root / folder).exists():
            safe_print(f"   [SUCCESS] {folder}/ folder exists")
        else:
            safe_print(f"   [ERROR] {folder}/ folder missing")

    # Check secrets file
    secrets_file = project_root / "config" / "secrets" / ".env"
    if secrets_file.exists():
        safe_print("   [SUCCESS] Secrets file exists")

        # Check if API key is configured
        with open(secrets_file) as f:
            content = f.read()
            if "LINEAR_API_KEY=" in content and "YOUR_ACTUAL_KEY_HERE" not in content:
                safe_print("   [SUCCESS] Linear API key is configured")
            else:
                safe_print("   [ERROR] Linear API key needs to be set properly")
    else:
        safe_print("   [ERROR] Secrets file missing")

    print()

    # Check Docker
    safe_print("[DOCKER] Docker Check:")
    try:
        result = subprocess.run(["docker", "--version"], capture_output=True, text=True, timeout=10, check=False)
        if result.returncode == 0:
            safe_print(f"   [SUCCESS] Docker available: {result.stdout.strip()}")
        else:
            safe_print(f"   [ERROR] Docker command failed: {result.stderr.strip()}")
    except FileNotFoundError:
        safe_print("   [ERROR] Docker command not found. Is Docker Desktop installed and running?")
    except subprocess.TimeoutExpired:
        safe_print("   [ERROR] Docker command timed out.")

    # Check Python virtual environment
    print()
    safe_print("[PYTHON] Python Environment:")
    if "VIRTUAL_ENV" in os.environ:
        safe_print(f"   [SUCCESS] Virtual environment active: {os.environ['VIRTUAL_ENV']}")
    else:
        safe_print("   [ERROR] Virtual environment not active")

    # Check Python packages
    try:
        import requests

        safe_print("   [SUCCESS] requests package available")
    except ImportError:
        safe_print("   [ERROR] requests package missing")

    try:
        import dotenv

        safe_print("   [SUCCESS] python-dotenv package available")
    except ImportError:
        safe_print("   [ERROR] python-dotenv package missing")

    print()
    safe_print("[READY] WSL2 environment test complete!")


if __name__ == "__main__":
    test_wsl2_environment()
