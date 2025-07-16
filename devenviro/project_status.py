#!/usr/bin/env python3
"""
Quick project status check
"""
import subprocess
import os
from pathlib import Path


def show_project_status():
    """Show current project status"""
    print("[STATUS] ApexSigma DevEnviro Project Status")
    print("=" * 50)
    print()

    # Project location - updated to current location
    project_path = Path(__file__).resolve().parent.parent
    print(f"[LOCATION] Project Location: {project_path}")
    print()

    # Git status
    try:
        os.chdir(project_path)
        result = subprocess.run(["git", "log", "--oneline", "-5"], capture_output=True, text=True)
        if result.returncode == 0:
            print("[GIT] Recent Git History:")
            for line in result.stdout.strip().split("\n"):
                print(f"   {line}")
        print()
    except:
        print("[ERROR] Git not available\n")

    # Check current architecture
    print("[ARCHITECTURE] Current Project Structure:")
    print("   - devenviro/main.py - FastAPI app with Sentry integration")
    print("   - devenviro/sentry_config.py - Error tracking configuration")
    print("   - devenviro/monitoring.py - Performance monitoring")
    print("   - docker-compose.yml - Production deployment")
    print("   - requirements.txt - Updated dependencies")
    print()

    # Services status
    print("[SERVICES] Current Services:")
    print("   - DevEnviro API: http://localhost:8001 (FastAPI + Sentry)")
    print("   - Memory Service: http://localhost:8000 (SQLite)")
    print("   - Qdrant Vector DB: http://localhost:6333")
    print("   - Sentry Dashboard: https://sentry.io/organizations/apexsigma/")
    print()

    # Virtual environment reminder
    if "VIRTUAL_ENV" in os.environ:
        print("[ENV] Virtual environment is active")
    else:
        print("[WARNING] Remember to activate virtual environment:")
        print("   source venv/bin/activate")
    print()

    # Updated quick commands
    print("[COMMANDS] Quick Commands:")
    print("   # Start FastAPI with Sentry")
    print("   python -m uvicorn devenviro.main:app --host 0.0.0.0 --port 8001 --reload")
    print("   # Test Sentry integration")
    print("   python test_sentry.py")
    print("   # Docker deployment")
    print("   docker-compose up -d")
    print("   # Check health")
    print("   curl http://localhost:8001/health")
    print()

    # Integration status
    print("[INTEGRATIONS] Integration Status:")
    print("   [OK] Sentry - Error tracking and performance monitoring")
    print("   [OK] FastAPI - Web framework with async support")
    print("   [OK] Docker - Production deployment ready")
    print("   [OK] Qdrant - Vector database for AI operations")
    print("   [PENDING] Linear - Project tracking integration")
    print("   [PENDING] OpenRouter - AI model integration")
    print()


if __name__ == "__main__":
    show_project_status()
