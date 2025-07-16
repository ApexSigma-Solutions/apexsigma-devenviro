#!/usr/bin/env python3
"""
Test script for WSL2 environment setup
"""
import os
import platform
import subprocess
from pathlib import Path


def test_wsl2_environment():
    """Test our WSL2 development environment"""
    print("🧪 Testing WSL2 ApexSigma DevEnviro Setup...")
    print()

    # Check we're in WSL2
    print("🐧 Environment Check:")
    print(f"   Platform: {platform.system()}")
    print(f"   Machine: {platform.machine()}")

    # Check if we're in WSL
    try:
        with open("/proc/version", "r") as f:
            version_info = f.read()
            if "Microsoft" in version_info or "WSL" in version_info:
                print("   ✅ Running in WSL2")
            else:
                print("   ❓ May not be in WSL2 (or /proc/version doesn't contain 'Microsoft' or 'WSL')")
    except FileNotFoundError:
        print("   ❌ Not running in a standard Linux environment (/proc/version not found).")

    print()

    # Check project structure
    project_root = Path.home() / "apexsigma-project"
    print("📁 Project Structure:")

    required_folders = ["code", "config", "docs", "logs"]
    for folder in required_folders:
        if (project_root / folder).exists():
            print(f"   ✅ {folder}/ folder exists")
        else:
            print(f"   ❌ {folder}/ folder missing")

    # Check secrets file
    secrets_file = project_root / "config" / "secrets" / ".env"
    if secrets_file.exists():
        print("   ✅ Secrets file exists")

        # Check if API key is configured
        with open(secrets_file) as f:
            content = f.read()
            if "LINEAR_API_KEY=" in content and "YOUR_ACTUAL_KEY_HERE" not in content:
                print("   ✅ Linear API key is configured")
            else:
                print("   ❌ Linear API key needs to be set properly")
    else:
        print("   ❌ Secrets file missing")

    print()

    # Check Docker
    print("🐳 Docker Check:")
    try:
        result = subprocess.run(["docker", "--version"], capture_output=True, text=True, timeout=10, check=False)
        if result.returncode == 0:
            print(f"   ✅ Docker available: {result.stdout.strip()}")
        else:
            print(f"   ❌ Docker command failed: {result.stderr.strip()}")
    except FileNotFoundError:
        print("   ❌ Docker command not found. Is Docker Desktop installed and running?")
    except subprocess.TimeoutExpired:
        print("   ❌ Docker command timed out.")

    # Check Python virtual environment
    print()
    print("🐍 Python Environment:")
    if "VIRTUAL_ENV" in os.environ:
        print(f"   ✅ Virtual environment active: {os.environ['VIRTUAL_ENV']}")
    else:
        print("   ❌ Virtual environment not active")

    # Check Python packages
    try:
        import requests

        print("   ✅ requests package available")
    except ImportError:
        print("   ❌ requests package missing")

    try:
        import dotenv

        print("   ✅ python-dotenv package available")
    except ImportError:
        print("   ❌ python-dotenv package missing")

    print()
    print("🎉 WSL2 environment test complete!")


if __name__ == "__main__":
    test_wsl2_environment()
