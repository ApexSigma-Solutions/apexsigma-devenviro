#!/usr/bin/env python3
"""
Test Linear API connection from WSL2
"""

import os
import requests
from pathlib import Path
from dotenv import load_dotenv
from devenviro.terminal_output import print_success, print_error, print_warning, safe_print


def test_linear_from_wsl2():
    """Test Linear API connection from WSL2"""
    print("[LINK] Testing Linear Connection from WSL2...")
    print()

    # Load environment variables
    # Determine project root dynamically to find the .env file
    project_root = Path(__file__).resolve().parent.parent
    env_file = project_root / "config" / "secrets" / ".env"
    load_dotenv(env_file)

    api_key = os.getenv("LINEAR_API_KEY")

    if not api_key or api_key == "YOUR_ACTUAL_KEY_HERE":
        print("[ERROR] Please set your Linear API key in config/secrets/.env")
        print("   Use: nano config/secrets/.env")
        return False

    # Test connection
    headers = {
        "Authorization": api_key,
        "Content-Type": "application/json",
        "User-Agent": "ApexSigma-DevEnviro-WSL2/1.0",
    }

    query = """
    query {
        viewer {
            name
            email
        }
        organization {
            name
        }
    }
    """

    try:
        print("[API] Connecting to Linear API...")
        response = requests.post(
            "https://api.linear.app/graphql",
            json={"query": query},
            headers=headers,
            timeout=15,
        )

        if response.status_code == 200:
            data = response.json()
            if "data" in data and "viewer" in data["data"]:
                user = data["data"]["viewer"]
                org = data["data"].get("organization", {})

                print(f"[SUCCESS] Connected successfully!")
                print(f"   User: {user['name']} ({user['email']})")
                if org.get("name"):
                    print(f"   Organization: {org['name']}")
                print()
                print("[READY] Linear integration ready!")
                return True
            else:
                print("[ERROR] Unexpected response from Linear API:")
                print(f"   {data}")
                return False
        else:
            print(f"[ERROR] API request failed with status: {response.status_code}")
            print(f"   Response: {response.text.strip()}")
            return False

    except requests.exceptions.Timeout:
        print("[ERROR] Connection timeout - check your internet connection")
        return False
    except requests.exceptions.ConnectionError:
        print("[ERROR] Cannot connect to Linear - check your internet connection")
        return False
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        return False


if __name__ == "__main__":
    success = test_linear_from_wsl2()
    if not success:
        print("\n[HELP] Troubleshooting tips:")
        print("1. Check your Linear API key in config/secrets/.env")
        print("2. Make sure you have internet access from WSL2")
        print("3. Try: nano config/secrets/.env to edit your API key")
