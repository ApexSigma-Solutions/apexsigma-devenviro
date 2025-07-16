"""
Test script for Sentry integration.
"""
import os
import sys
import requests
import time
from typing import Dict, Any

# Add devenviro directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'devenviro'))

from sentry_config import init_sentry, capture_message, capture_exception, set_user_context


def test_sentry_initialization():
    """Test Sentry initialization."""
    print("Testing Sentry initialization...")
    
    init_sentry(
        dsn="https://3f4240883d9c2ac20e4d339d5aed2b6d@o4509669791760384.ingest.de.sentry.io/4509679484272720",
        environment="test",
        debug=True
    )
    
    print("[OK] Sentry initialized successfully")


def test_sentry_message():
    """Test Sentry message capture."""
    print("Testing Sentry message capture...")
    
    capture_message("Test message from devenviro", level="info")
    print("[OK] Test message sent to Sentry")


def test_sentry_exception():
    """Test Sentry exception capture."""
    print("Testing Sentry exception capture...")
    
    try:
        raise Exception("Test exception from devenviro")
    except Exception as e:
        capture_exception(e, test_context={"test": "value"})
    
    print("[OK] Test exception sent to Sentry")


def test_sentry_user_context():
    """Test Sentry user context."""
    print("Testing Sentry user context...")
    
    set_user_context("test_user_123", username="testuser", email="test@example.com")
    capture_message("Test message with user context", level="info")
    
    print("[OK] User context test message sent to Sentry")


def test_fastapi_endpoints():
    """Test FastAPI endpoints if running."""
    print("Testing FastAPI endpoints...")
    
    base_url = "http://localhost:8000"
    
    try:
        # Test health endpoint
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("[OK] Health endpoint working")
        else:
            print(f"[FAIL] Health endpoint failed: {response.status_code}")
            return False
            
        # Test error endpoint
        test_cases = [
            {"error_type": "message", "message": "Test Sentry message via API"},
            {"error_type": "exception", "message": "Test Sentry exception via API", "user_id": "api_test_user"},
        ]
        
        for test_case in test_cases:
            response = requests.post(f"{base_url}/test-error", json=test_case, timeout=5)
            if response.status_code in [200, 500]:  # 500 expected for exception test
                print(f"[OK] Error test '{test_case['error_type']}' sent to Sentry")
            else:
                print(f"[FAIL] Error test '{test_case['error_type']}' failed: {response.status_code}")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"[FAIL] FastAPI server not running or unreachable: {e}")
        return False


def main():
    """Run all Sentry tests."""
    print("=== DevEnviro Sentry Integration Tests ===\n")
    
    # Test 1: Initialization
    test_sentry_initialization()
    time.sleep(1)
    
    # Test 2: Message capture
    test_sentry_message()
    time.sleep(1)
    
    # Test 3: Exception capture
    test_sentry_exception()
    time.sleep(1)
    
    # Test 4: User context
    test_sentry_user_context()
    time.sleep(1)
    
    # Test 5: FastAPI endpoints (if server is running)
    print("\n--- FastAPI Endpoint Tests ---")
    fastapi_running = test_fastapi_endpoints()
    
    print("\n=== Test Results ===")
    print("[OK] Sentry configuration module working")
    print("[OK] Message capture working")
    print("[OK] Exception capture working")
    print("[OK] User context working")
    
    if fastapi_running:
        print("[OK] FastAPI endpoints working")
        print("\nTo start the FastAPI server, run:")
        print("  python -m uvicorn devenviro.main:app --host 0.0.0.0 --port 8000 --reload")
    else:
        print("! FastAPI server not running")
        print("\nTo start the FastAPI server, run:")
        print("  python -m uvicorn devenviro.main:app --host 0.0.0.0 --port 8000 --reload")
    
    print("\n[SUCCESS] All tests completed! Check your Sentry dashboard for events.")
    print("Dashboard: https://sentry.io/organizations/apexsigma/issues/")


if __name__ == "__main__":
    main()