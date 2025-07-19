#!/usr/bin/env python3
"""
Quick project status check
"""
import subprocess
import os
from pathlib import Path
from devenviro.terminal_output import print_section_header, print_success, print_error, print_warning, safe_print


def show_project_status():
    """Show current project status"""
    print_section_header("[STATS] ApexSigma DevEnviro Project Status")
    print()

    # Project location
    project_path = Path.home() / "apexsigma-project"
    safe_print(f"[FOLDER] Project Location: {project_path}")
    print()

    # Git status
    try:
        os.chdir(project_path)
        result = subprocess.run(["git", "log", "--oneline", "-5"], capture_output=True, text=True)
        if result.returncode == 0:
            safe_print("[GIT] Recent Git History:")
            for line in result.stdout.strip().split("\n"):
                print(f"   {line}")
        print()
    except:
        print_error("Git not available\n")

    # Virtual environment reminder
    if "VIRTUAL_ENV" in os.environ:
        print_success("Virtual environment is active")
    else:
        print_warning("Remember to activate virtual environment:")
        print("   source venv/bin/activate")
    print()

    # Quick commands reminder
    safe_print("[LAUNCH] Quick Commands:")
    print("   cd ~/apexsigma-project")
    print("   source venv/bin/activate")
    print("   python code/test_wsl2_setup.py")
    print("   python code/test_linear_wsl2.py")
    print()


if __name__ == "__main__":
    show_project_status()
