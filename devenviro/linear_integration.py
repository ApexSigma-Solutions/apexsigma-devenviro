#!/usr/bin/env python3
"""
Linear integration for DevEnviro project tracking
"""

import os
import requests
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from typing import Dict, List, Optional, Any
import json


class LinearIntegration:
    """Linear API integration for project tracking"""
    
    def __init__(self, api_key: Optional[str] = None):
        if not api_key:
            # Load from environment
            project_root = Path(__file__).resolve().parent.parent
            env_file = project_root / "config" / "secrets" / ".env"
            load_dotenv(env_file)
            api_key = os.getenv("LINEAR_API_KEY")
        
        if not api_key:
            raise ValueError("LINEAR_API_KEY not found in environment")
        
        self.api_key = api_key
        self.headers = {
            "Authorization": api_key,
            "Content-Type": "application/json",
            "User-Agent": "ApexSigma-DevEnviro/1.0",
        }
        self.base_url = "https://api.linear.app/graphql"
    
    def _make_request(self, query: str, variables: Optional[Dict] = None) -> Dict:
        """Make a GraphQL request to Linear API"""
        payload = {"query": query}
        if variables:
            payload["variables"] = variables
        
        response = requests.post(
            self.base_url,
            json=payload,
            headers=self.headers,
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Linear API request failed: {response.status_code} - {response.text}")
    
    def get_user_info(self) -> Dict:
        """Get current user information"""
        query = """
        query {
            viewer {
                name
                email
                id
            }
            organization {
                name
                id
            }
        }
        """
        return self._make_request(query)
    
    def get_teams(self) -> List[Dict]:
        """Get available teams"""
        query = """
        query {
            teams {
                nodes {
                    id
                    name
                    key
                    description
                }
            }
        }
        """
        result = self._make_request(query)
        return result.get("data", {}).get("teams", {}).get("nodes", [])
    
    def get_project_issues(self, team_id: str, limit: int = 50) -> List[Dict]:
        """Get issues for a specific team"""
        query = """
        query($teamId: String!, $first: Int!) {
            team(id: $teamId) {
                issues(first: $first, orderBy: updatedAt) {
                    nodes {
                        id
                        title
                        description
                        state {
                            name
                        }
                        priority
                        createdAt
                        updatedAt
                        assignee {
                            name
                        }
                        labels {
                            nodes {
                                name
                            }
                        }
                    }
                }
            }
        }
        """
        variables = {"teamId": team_id, "first": limit}
        result = self._make_request(query, variables)
        return result.get("data", {}).get("team", {}).get("issues", {}).get("nodes", [])
    
    def create_issue(self, team_id: str, title: str, description: str, priority: int = 0) -> Dict:
        """Create a new issue"""
        query = """
        mutation($teamId: String!, $title: String!, $description: String, $priority: Int) {
            issueCreate(input: {
                teamId: $teamId
                title: $title
                description: $description
                priority: $priority
            }) {
                success
                issue {
                    id
                    title
                    url
                }
            }
        }
        """
        variables = {
            "teamId": team_id,
            "title": title,
            "description": description,
            "priority": priority
        }
        return self._make_request(query, variables)
    
    def update_issue(self, issue_id: str, title: Optional[str] = None, 
                    description: Optional[str] = None, state_id: Optional[str] = None) -> Dict:
        """Update an existing issue"""
        query = """
        mutation($issueId: String!, $title: String, $description: String, $stateId: String) {
            issueUpdate(id: $issueId, input: {
                title: $title
                description: $description
                stateId: $stateId
            }) {
                success
                issue {
                    id
                    title
                    url
                }
            }
        }
        """
        variables = {"issueId": issue_id}
        if title:
            variables["title"] = title
        if description:
            variables["description"] = description
        if state_id:
            variables["stateId"] = state_id
        
        return self._make_request(query, variables)
    
    def get_workflow_states(self, team_id: str) -> List[Dict]:
        """Get workflow states for a team"""
        query = """
        query($teamId: String!) {
            team(id: $teamId) {
                states {
                    nodes {
                        id
                        name
                        type
                    }
                }
            }
        }
        """
        variables = {"teamId": team_id}
        result = self._make_request(query, variables)
        return result.get("data", {}).get("team", {}).get("states", {}).get("nodes", [])


def update_linear_project_status():
    """Update Linear with current project status"""
    print("[LINEAR] Updating Linear project status...")
    
    try:
        linear = LinearIntegration()
        
        # Get user info
        user_info = linear.get_user_info()
        viewer = user_info.get("data", {}).get("viewer", {})
        org = user_info.get("data", {}).get("organization", {})
        
        print(f"[INFO] Connected as: {viewer.get('name')} ({viewer.get('email')})")
        print(f"[INFO] Organization: {org.get('name')}")
        
        # Get teams
        teams = linear.get_teams()
        devenviro_team = None
        
        for team in teams:
            if "devenviro" in team.get("name", "").lower():
                devenviro_team = team
                break
        
        if not devenviro_team:
            print("[WARNING] DevEnviro team not found, using first available team")
            devenviro_team = teams[0] if teams else None
        
        if not devenviro_team:
            print("[ERROR] No teams available")
            return False
        
        print(f"[INFO] Using team: {devenviro_team['name']}")
        
        # Get current issues
        issues = linear.get_project_issues(devenviro_team["id"])
        print(f"[INFO] Found {len(issues)} existing issues")
        
        # Create status update issue
        status_title = f"DevEnviro Status Update - {datetime.now().strftime('%Y-%m-%d')}"
        status_description = f"""
# DevEnviro Project Status Update

## ✅ Recently Completed
- **Sentry Integration**: Comprehensive error tracking and monitoring implemented
- **FastAPI Application**: Production-ready web API with health checks
- **Docker Deployment**: Container-based deployment configuration ready
- **Code Quality**: Linting, type checking, and security scanning in place
- **Documentation**: Complete setup guides and API documentation

## 🔧 Current Architecture
- **devenviro/main.py**: FastAPI app with Sentry integration
- **devenviro/sentry_config.py**: Error tracking configuration
- **devenviro/monitoring.py**: Performance monitoring
- **docker-compose.yml**: Production deployment
- **Sentry Dashboard**: https://sentry.io/organizations/apexsigma/

## 🚀 Active Services
- **DevEnviro API**: http://localhost:8001 (FastAPI + Sentry)
- **Memory Service**: http://localhost:8000 (SQLite)
- **Qdrant Vector DB**: http://localhost:6333
- **Error Tracking**: Real-time monitoring active

## 📊 Integration Status
- ✅ **Sentry**: Error tracking and performance monitoring
- ✅ **FastAPI**: Web framework with async support
- ✅ **Docker**: Production deployment ready
- ✅ **Qdrant**: Vector database for AI operations
- ✅ **Linear**: Project tracking integration (this update!)
- ⏳ **OpenRouter**: AI model integration pending

## 🔄 Next Steps
1. Expand AI-powered memory operations with OpenRouter
2. Implement user authentication and authorization
3. Add real-time collaboration features
4. Enhance vector search capabilities
5. Deploy to production environment

## 🛠️ Technical Details
- **Commit**: f2bb042 - Sentry integration
- **Documentation**: README.md, SENTRY_INTEGRATION.md updated
- **Testing**: All integration tests passing
- **Monitoring**: Real-time error tracking operational

Auto-generated by DevEnviro Linear Integration
Generated at: {datetime.now().isoformat()}
"""
        
        # Check if similar issue exists (avoid duplicates)
        existing_status = None
        for issue in issues:
            if "status update" in issue.get("title", "").lower() and datetime.now().strftime('%Y-%m-%d') in issue.get("title", ""):
                existing_status = issue
                break
        
        if existing_status:
            print(f"[INFO] Updating existing status issue: {existing_status['title']}")
            result = linear.update_issue(
                existing_status["id"],
                title=status_title,
                description=status_description
            )
        else:
            print("[INFO] Creating new status update issue")
            result = linear.create_issue(
                devenviro_team["id"],
                status_title,
                status_description,
                priority=1  # Medium priority
            )
        
        if result.get("data", {}).get("issueCreate", {}).get("success") or result.get("data", {}).get("issueUpdate", {}).get("success"):
            issue_data = result.get("data", {}).get("issueCreate", {}).get("issue") or result.get("data", {}).get("issueUpdate", {}).get("issue")
            print(f"[SUCCESS] Issue updated: {issue_data.get('title')}")
            print(f"[URL] View at: {issue_data.get('url')}")
            return True
        else:
            print(f"[ERROR] Failed to update issue: {result}")
            return False
    
    except Exception as e:
        print(f"[ERROR] Linear integration failed: {e}")
        return False


if __name__ == "__main__":
    success = update_linear_project_status()
    if success:
        print("\n[STATUS] Linear project status updated successfully!")
    else:
        print("\n[STATUS] Linear project status update failed!")