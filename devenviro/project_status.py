#!/usr/bin/env python3
"""
Quick project status check
"""
import subprocess
import os
from pathlib import Path


def show_project_status():
    """Show current project status"""
    print("📊 ApexSigma DevEnviro Project Status")
    print("=" * 50)
    print()

    # Project location
    project_path = Path.home() / "apexsigma-project"
    print(f"📁 Project Location: {project_path}")
    print()

    # Git status
    try:
        os.chdir(project_path)
        result = subprocess.run(["git", "log", "--oneline", "-5"], capture_output=True, text=True)
        if result.returncode == 0:
            print("📜 Recent Git History:")
            for line in result.stdout.strip().split("\n"):
                print(f"   {line}")
        print()
    except:
        print("❌ Git not available\n")

    # Virtual environment reminder
    if "VIRTUAL_ENV" in os.environ:
        print("✅ Virtual environment is active")
    else:
        print("⚠️  Remember to activate virtual environment:")
        print("   source venv/bin/activate")
    print()

    # Quick commands reminder
    print("🚀 Quick Commands:")
    print("   cd ~/apexsigma-project")
    print("   source venv/bin/activate")
    print("   python code/test_wsl2_setup.py")
    print("   python code/test_linear_wsl2.py")
    print()


if __name__ == "__main__":
    show_project_status()
