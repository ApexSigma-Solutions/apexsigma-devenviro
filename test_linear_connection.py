#!/usr/bin/env python3
"""
Test Linear API connection with found API key
"""

import os
import requests
from pathlib import Path
from dotenv import load_dotenv

def test_linear_connection():
    """Test Linear API connection with found API key"""
    print("[LINEAR] Testing Linear API Connection...")
    print()

    # Load environment variables
    project_root = Path(__file__).resolve().parent
    env_file = project_root / "config" / "secrets" / ".env"
    
    if not env_file.exists():
        print(f"[ERROR] Environment file not found: {env_file}")
        return False
    
    load_dotenv(env_file)
    api_key = os.getenv("LINEAR_API_KEY")

    if not api_key:
        print("[ERROR] LINEAR_API_KEY not found in environment")
        return False

    print(f"[INFO] Found API key: {api_key[:15]}...")
    
    # Test connection
    headers = {
        "Authorization": api_key,
        "Content-Type": "application/json",
        "User-Agent": "ApexSigma-DevEnviro/1.0",
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
        teams {
            nodes {
                name
                id
            }
        }
    }
    """

    try:
        print("[REQUEST] Connecting to Linear API...")
        response = requests.post(
            "https://api.linear.app/graphql",
            json={"query": query},
            headers=headers,
            timeout=15,
        )

        if response.status_code == 200:
            data = response.json()
            if "data" in data:
                viewer = data["data"].get("viewer", {})
                org = data["data"].get("organization", {})
                teams = data["data"].get("teams", {}).get("nodes", [])

                print("[SUCCESS] Connected to Linear API!")
                print(f"   User: {viewer.get('name', 'Unknown')} ({viewer.get('email', 'Unknown')})")
                if org.get("name"):
                    print(f"   Organization: {org['name']}")
                
                if teams:
                    print(f"   Teams: {len(teams)} available")
                    for team in teams[:3]:  # Show first 3 teams
                        print(f"      - {team['name']}")
                    if len(teams) > 3:
                        print(f"      ... and {len(teams) - 3} more")
                
                print()
                print("[READY] Linear integration is ready for use!")
                return True
            else:
                print(f"[ERROR] Unexpected response format: {data}")
                return False
        else:
            print(f"[ERROR] API request failed with status: {response.status_code}")
            print(f"   Response: {response.text}")
            return False

    except requests.exceptions.Timeout:
        print("[ERROR] Connection timeout - check internet connection")
        return False
    except requests.exceptions.ConnectionError:
        print("[ERROR] Cannot connect to Linear - check internet connection")
        return False
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_linear_connection()
    if success:
        print("\n[STATUS] Linear API connection successful!")
        print("         Ready to implement Linear integration features.")
    else:
        print("\n[STATUS] Linear API connection failed!")
        print("         Check API key and network connectivity.")