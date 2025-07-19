#!/usr/bin/env python3
"""
DevEnviro Session Signoff Script
Captures session state for smooth startup restoration - "Close to Open" protocol
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional
import asyncio

# Add devenviro to path
sys.path.append(str(Path(__file__).parent / "devenviro"))

try:
    from gemini_memory_engine import GeminiMemoryEngine
except ImportError:
    print("[WARNING] GeminiMemoryEngine not available - limited memory capture")
    GeminiMemoryEngine = None


class SessionSignoff:
    """Session closing and state preservation system"""
    
    def __init__(self):
        self.current_directory = Path.cwd()
        self.session_end_time = datetime.now(timezone.utc)
        self.memory_engine = None
        self.session_data = {}
        
    async def run_signoff_sequence(self):
        """Main session signoff sequence"""
        print("DevEnviro Session Signoff")
        print("=" * 50)
        print("Preparing workspace for next session...")
        print()
        
        try:
            # Step 1: Initialize memory engine
            await self._initialize_memory_engine()
            
            # Step 2: Capture current session state
            await self._capture_session_state()
            
            # Step 3: Capture project state
            await self._capture_project_state()
            
            # Step 4: Capture unfinished tasks
            await self._capture_unfinished_tasks()
            
            # Step 5: Capture Linear issues status
            await self._capture_linear_issues()
            
            # Step 6: Save session summary to memory
            await self._save_session_to_memory()
            
            # Step 7: Clean workspace
            await self._clean_workspace()
            
            # Step 8: Generate session report
            await self._generate_session_report()
            
            print("\n[SUCCESS] Session signoff completed!")
            print("Workspace prepared for next session startup.")
            return True
            
        except Exception as e:
            print(f"\n[ERROR] Session signoff failed: {e}")
            return False
    
    async def _initialize_memory_engine(self):
        """Initialize memory engine for session capture"""
        print("[MEMORY] Initializing memory engine...")
        
        try:
            if GeminiMemoryEngine:
                self.memory_engine = GeminiMemoryEngine()
                print("[SUCCESS] Memory engine ready for session capture")
            else:
                print("[WARNING] Memory engine unavailable - using file-based capture")
        except Exception as e:
            print(f"[WARNING] Memory engine initialization failed: {e}")
            print("[INFO] Continuing with file-based session capture")
    
    async def _capture_session_state(self):
        """Capture current session working state"""
        print("[CAPTURE] Capturing session state...")
        
        session_state = {
            "session_end_time": self.session_end_time.isoformat(),
            "working_directory": str(self.current_directory),
            "git_status": await self._capture_git_status(),
            "open_files": await self._capture_open_files(),
            "recent_commands": await self._capture_recent_commands(),
            "environment_vars": await self._capture_environment_state()
        }
        
        self.session_data["session_state"] = session_state
        print(f"[SUCCESS] Session state captured")
        
    async def _capture_git_status(self) -> Dict:
        """Capture git repository status"""
        git_status = {
            "is_git_repo": False,
            "current_branch": None,
            "uncommitted_changes": False,
            "untracked_files": [],
            "staged_files": [],
            "modified_files": [],
            "recent_commits": []
        }
        
        try:
            # Check if git repo
            result = subprocess.run(
                ["git", "rev-parse", "--is-inside-work-tree"],
                capture_output=True,
                text=True,
                cwd=self.current_directory
            )
            
            if result.returncode == 0:
                git_status["is_git_repo"] = True
                
                # Get current branch
                result = subprocess.run(
                    ["git", "branch", "--show-current"],
                    capture_output=True,
                    text=True,
                    cwd=self.current_directory
                )
                if result.returncode == 0:
                    git_status["current_branch"] = result.stdout.strip()
                
                # Get status
                result = subprocess.run(
                    ["git", "status", "--porcelain"],
                    capture_output=True,
                    text=True,
                    cwd=self.current_directory
                )
                if result.returncode == 0:
                    status_lines = result.stdout.strip().split('\n') if result.stdout.strip() else []
                    git_status["uncommitted_changes"] = len(status_lines) > 0
                    
                    for line in status_lines:
                        if line:
                            status_code = line[:2]
                            file_path = line[3:]
                            
                            if status_code[0] == '?':
                                git_status["untracked_files"].append(file_path)
                            elif status_code[0] in ['A', 'M', 'D', 'R', 'C']:
                                git_status["staged_files"].append(file_path)
                            elif status_code[1] in ['M', 'D']:
                                git_status["modified_files"].append(file_path)
                
                # Get recent commits
                result = subprocess.run(
                    ["git", "log", "--oneline", "-5"],
                    capture_output=True,
                    text=True,
                    cwd=self.current_directory
                )
                if result.returncode == 0:
                    git_status["recent_commits"] = result.stdout.strip().split('\n')
                    
        except Exception as e:
            print(f"[WARNING] Git status capture failed: {e}")
            
        return git_status
    
    async def _capture_open_files(self) -> List[str]:
        """Capture list of recently modified files"""
        open_files = []
        
        try:
            # Get recently modified files (last 2 hours)
            import time
            current_time = time.time()
            two_hours_ago = current_time - (2 * 60 * 60)
            
            for file_path in self.current_directory.rglob("*"):
                if file_path.is_file() and not any(part.startswith('.') for part in file_path.parts):
                    try:
                        if file_path.stat().st_mtime > two_hours_ago:
                            # Filter for code/text files
                            if file_path.suffix in ['.py', '.js', '.ts', '.html', '.css', '.md', '.txt', '.json', '.yaml', '.yml']:
                                open_files.append(str(file_path.relative_to(self.current_directory)))
                    except (OSError, ValueError):
                        continue
                        
            # Sort by modification time (most recent first)
            open_files.sort(key=lambda f: (self.current_directory / f).stat().st_mtime, reverse=True)
            open_files = open_files[:10]  # Keep top 10
            
        except Exception as e:
            print(f"[WARNING] Open files capture failed: {e}")
            
        return open_files
    
    async def _capture_recent_commands(self) -> List[str]:
        """Capture recent command history"""
        recent_commands = []
        
        try:
            # Check .ai-cli-log directory
            log_dir = self.current_directory / ".ai-cli-log"
            if log_dir.exists():
                log_files = sorted(log_dir.glob("*.log"), key=lambda x: x.stat().st_mtime, reverse=True)
                
                for log_file in log_files[:3]:  # Check last 3 log files
                    try:
                        with open(log_file, 'r', encoding='utf-8') as f:
                            lines = f.readlines()
                            # Extract command-like lines (simple heuristic)
                            for line in lines[-20:]:  # Last 20 lines per file
                                line = line.strip()
                                if line and (line.startswith('[') or line.startswith('$') or line.startswith('>')):
                                    recent_commands.append(line)
                    except Exception:
                        continue
                        
            # Limit to last 10 commands
            recent_commands = recent_commands[-10:]
            
        except Exception as e:
            print(f"[WARNING] Command history capture failed: {e}")
            
        return recent_commands
    
    async def _capture_environment_state(self) -> Dict:
        """Capture relevant environment state"""
        env_state = {
            "python_version": sys.version,
            "working_directory": str(self.current_directory),
            "project_type": "unknown",
            "key_env_vars": {}
        }
        
        try:
            # Detect project type
            if (self.current_directory / "package.json").exists():
                env_state["project_type"] = "node.js"
            elif (self.current_directory / "requirements.txt").exists() or (self.current_directory / "pyproject.toml").exists():
                env_state["project_type"] = "python"
            elif (self.current_directory / "Cargo.toml").exists():
                env_state["project_type"] = "rust"
            elif (self.current_directory / "go.mod").exists():
                env_state["project_type"] = "go"
            
            # Capture key environment variables
            key_vars = ["PATH", "NODE_ENV", "PYTHON_PATH", "VIRTUAL_ENV"]
            for var in key_vars:
                if var in os.environ:
                    env_state["key_env_vars"][var] = os.environ[var]
                    
        except Exception as e:
            print(f"[WARNING] Environment state capture failed: {e}")
            
        return env_state
    
    async def _capture_project_state(self):
        """Capture project-specific state"""
        print("[CAPTURE] Capturing project state...")
        
        project_state = {
            "devenviro_config": await self._capture_devenviro_config(),
            "project_files": await self._capture_project_structure(),
            "dependencies": await self._capture_dependencies()
        }
        
        self.session_data["project_state"] = project_state
        print(f"[SUCCESS] Project state captured")
    
    async def _capture_devenviro_config(self) -> Optional[Dict]:
        """Capture DevEnviro configuration"""
        try:
            config_file = self.current_directory / ".devenviro" / "config.json"
            if config_file.exists():
                with open(config_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"[WARNING] DevEnviro config capture failed: {e}")
        return None
    
    async def _capture_project_structure(self) -> Dict:
        """Capture high-level project structure"""
        structure = {
            "total_files": 0,
            "directories": [],
            "key_files": []
        }
        
        try:
            # Count files and directories
            for item in self.current_directory.iterdir():
                if item.name.startswith('.'):
                    continue
                    
                if item.is_dir():
                    structure["directories"].append(item.name)
                elif item.is_file():
                    structure["total_files"] += 1
                    # Track key files
                    if item.name in ["README.md", "package.json", "requirements.txt", "Cargo.toml", "go.mod", "Makefile"]:
                        structure["key_files"].append(item.name)
                        
        except Exception as e:
            print(f"[WARNING] Project structure capture failed: {e}")
            
        return structure
    
    async def _capture_dependencies(self) -> Dict:
        """Capture project dependencies info"""
        dependencies = {}
        
        try:
            # Python dependencies
            req_file = self.current_directory / "requirements.txt"
            if req_file.exists():
                with open(req_file, 'r') as f:
                    dependencies["python"] = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            
            # Node.js dependencies
            package_file = self.current_directory / "package.json"
            if package_file.exists():
                with open(package_file, 'r') as f:
                    package_data = json.load(f)
                    dependencies["node"] = {
                        "dependencies": list(package_data.get("dependencies", {}).keys()),
                        "devDependencies": list(package_data.get("devDependencies", {}).keys())
                    }
                    
        except Exception as e:
            print(f"[WARNING] Dependencies capture failed: {e}")
            
        return dependencies
    
    async def _capture_unfinished_tasks(self):
        """Capture unfinished tasks and TODOs"""
        print("[CAPTURE] Capturing unfinished tasks...")
        
        unfinished_tasks = {
            "code_todos": await self._scan_code_todos(),
            "session_todos": await self._capture_session_todos(),
            "git_work": await self._capture_git_work_status()
        }
        
        self.session_data["unfinished_tasks"] = unfinished_tasks
        print(f"[SUCCESS] Unfinished tasks captured")
    
    async def _scan_code_todos(self) -> List[Dict]:
        """Scan code files for TODO comments"""
        todos = []
        
        try:
            # Search for TODO/FIXME/XXX comments in code files
            for file_path in self.current_directory.rglob("*"):
                if file_path.is_file() and file_path.suffix in ['.py', '.js', '.ts', '.html', '.css', '.md']:
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            lines = f.readlines()
                            for i, line in enumerate(lines, 1):
                                line_lower = line.lower()
                                if any(keyword in line_lower for keyword in ['todo', 'fixme', 'xxx', 'hack']):
                                    todos.append({
                                        "file": str(file_path.relative_to(self.current_directory)),
                                        "line": i,
                                        "content": line.strip(),
                                        "type": "code_comment"
                                    })
                    except Exception:
                        continue
                        
            # Limit to most recent 20 TODOs
            todos = todos[-20:]
            
        except Exception as e:
            print(f"[WARNING] Code TODO scan failed: {e}")
            
        return todos
    
    async def _capture_session_todos(self) -> List[str]:
        """Capture session-specific todos from user input"""
        session_todos = []
        
        try:
            print("\n[INPUT] Session wrap-up (press Enter to skip each):")
            
            # Ask for unfinished work
            print("What work is unfinished and should be prioritized next session?")
            unfinished = input("Unfinished work: ").strip()
            if unfinished:
                session_todos.append(f"PRIORITY: {unfinished}")
            
            # Ask for blockers
            print("Any blockers or issues that need resolution?")
            blockers = input("Blockers: ").strip()
            if blockers:
                session_todos.append(f"BLOCKER: {blockers}")
            
            # Ask for next steps
            print("What should be the first task when returning?")
            next_steps = input("Next steps: ").strip()
            if next_steps:
                session_todos.append(f"NEXT: {next_steps}")
                
        except KeyboardInterrupt:
            print("\n[INFO] Skipping session todos input")
        except Exception as e:
            print(f"[WARNING] Session todos capture failed: {e}")
            
        return session_todos
    
    async def _capture_git_work_status(self) -> Dict:
        """Capture git work that needs attention"""
        git_work = {
            "uncommitted_work": [],
            "unpushed_commits": False,
            "merge_conflicts": False
        }
        
        try:
            git_status = self.session_data.get("session_state", {}).get("git_status", {})
            
            if git_status.get("is_git_repo"):
                # Check for uncommitted work
                if git_status.get("uncommitted_changes"):
                    git_work["uncommitted_work"] = (
                        git_status.get("staged_files", []) + 
                        git_status.get("modified_files", []) + 
                        git_status.get("untracked_files", [])
                    )
                
                # Check for unpushed commits
                result = subprocess.run(
                    ["git", "status", "--porcelain=v1", "--branch"],
                    capture_output=True,
                    text=True,
                    cwd=self.current_directory
                )
                if result.returncode == 0 and "ahead" in result.stdout:
                    git_work["unpushed_commits"] = True
                    
        except Exception as e:
            print(f"[WARNING] Git work status capture failed: {e}")
            
        return git_work
    
    async def _capture_linear_issues(self):
        """Capture Linear issues status and updates"""
        print("[CAPTURE] Capturing Linear issues status...")
        
        linear_data = {
            "issues_snapshot": await self._get_linear_issues_snapshot(),
            "session_updates": await self._capture_linear_session_updates(),
            "priority_issues": await self._identify_priority_linear_issues()
        }
        
        self.session_data["linear_issues"] = linear_data
        print(f"[SUCCESS] Linear issues status captured")
    
    async def _get_linear_issues_snapshot(self) -> Dict:
        """Get current snapshot of Linear issues"""
        issues_snapshot = {
            "total_open": 0,
            "assigned_to_me": 0,
            "high_priority": 0,
            "updated_recently": 0,
            "capture_time": self.session_end_time.isoformat()
        }
        
        try:
            # Check if Linear API test script exists
            linear_script = self.current_directory / "code" / "test_linear_wsl2.py"
            if not linear_script.exists():
                print("[INFO] Linear API script not found, skipping Linear capture")
                return issues_snapshot
            
            # Run Linear API query for open issues
            result = subprocess.run([
                sys.executable, "-c", '''
import os
import sys
import requests
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
project_root = Path(".").resolve().parent
env_file = project_root / "config" / "secrets" / ".env"
load_dotenv(env_file)

api_key = os.getenv("LINEAR_API_KEY")
if not api_key:
    print("0,0,0,0")  # Return zeros if no API key
    sys.exit(0)

headers = {
    "Authorization": api_key,
    "Content-Type": "application/json"
}

query = """
query {
    issues(filter: {state: {type: {nin: ["completed", "canceled"]}}}) {
        nodes {
            id
            title
            priority
            assignee { name }
            updatedAt
            state { name }
        }
    }
    viewer {
        name
    }
}
"""

try:
    response = requests.post("https://api.linear.app/graphql", json={"query": query}, headers=headers, timeout=10)
    if response.status_code == 200:
        data = response.json()
        issues = data.get("data", {}).get("issues", {}).get("nodes", [])
        viewer = data.get("data", {}).get("viewer", {}).get("name", "")
        
        total_open = len(issues)
        assigned_to_me = len([i for i in issues if i.get("assignee", {}).get("name") == viewer])
        high_priority = len([i for i in issues if i.get("priority", 0) >= 3])
        
        # Count recently updated (last 24 hours)
        from datetime import datetime, timedelta
        twenty_four_hours_ago = datetime.now() - timedelta(hours=24)
        updated_recently = 0
        for issue in issues:
            try:
                updated_at = datetime.fromisoformat(issue.get("updatedAt", "").replace("Z", "+00:00"))
                if updated_at > twenty_four_hours_ago:
                    updated_recently += 1
            except:
                continue
        
        print(f"{total_open},{assigned_to_me},{high_priority},{updated_recently}")
    else:
        print("0,0,0,0")
except Exception as e:
    print("0,0,0,0")
                '''
            ], capture_output=True, text=True, cwd=self.current_directory / "code")
            
            if result.returncode == 0 and result.stdout.strip():
                counts = result.stdout.strip().split(',')
                if len(counts) == 4:
                    issues_snapshot.update({
                        "total_open": int(counts[0]),
                        "assigned_to_me": int(counts[1]),
                        "high_priority": int(counts[2]),
                        "updated_recently": int(counts[3])
                    })
                    print(f"[SUCCESS] Found {counts[0]} open Linear issues ({counts[1]} assigned to you)")
                    
        except Exception as e:
            print(f"[WARNING] Linear issues snapshot failed: {e}")
            
        return issues_snapshot
    
    async def _capture_linear_session_updates(self) -> List[str]:
        """Capture any Linear issue updates made during this session"""
        session_updates = []
        
        try:
            print("\n[INPUT] Linear session updates (press Enter to skip):")
            print("Did you update any Linear issues during this session?")
            updates = input("Issue updates (e.g., 'ALPHA2-25: moved to in progress'): ").strip()
            if updates:
                session_updates.append(updates)
            
            print("Any new issues created or assigned during this session?")
            new_issues = input("New issues: ").strip()
            if new_issues:
                session_updates.append(f"NEW: {new_issues}")
                
        except (KeyboardInterrupt, EOFError):
            print("\n[INFO] Skipping Linear session updates input")
        except Exception as e:
            print(f"[WARNING] Linear session updates capture failed: {e}")
            
        return session_updates
    
    async def _identify_priority_linear_issues(self) -> List[Dict]:
        """Identify priority Linear issues for next session"""
        priority_issues = []
        
        try:
            # Get recent high-priority and assigned issues
            linear_script = self.current_directory / "code" / "test_linear_wsl2.py"
            if not linear_script.exists():
                return priority_issues
            
            result = subprocess.run([
                sys.executable, "-c", '''
import os
import sys
import requests
import json
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
project_root = Path(".").resolve().parent
env_file = project_root / "config" / "secrets" / ".env"
load_dotenv(env_file)

api_key = os.getenv("LINEAR_API_KEY")
if not api_key:
    print("[]")
    sys.exit(0)

headers = {
    "Authorization": api_key,
    "Content-Type": "application/json"
}

query = """
query {
    issues(filter: {
        state: {type: {nin: ["completed", "canceled"]}},
        or: [
            {priority: {gte: 3}},
            {assignee: {isNull: false}}
        ]
    }, first: 10) {
        nodes {
            id
            title
            priority
            assignee { name }
            state { name }
            url
        }
    }
    viewer {
        name
    }
}
"""

try:
    response = requests.post("https://api.linear.app/graphql", json={"query": query}, headers=headers, timeout=10)
    if response.status_code == 200:
        data = response.json()
        issues = data.get("data", {}).get("issues", {}).get("nodes", [])
        viewer_name = data.get("data", {}).get("viewer", {}).get("name", "")
        
        priority_issues = []
        for issue in issues:
            # Focus on high priority or assigned to current user
            is_high_priority = issue.get("priority", 0) >= 3
            is_assigned_to_me = issue.get("assignee", {}).get("name") == viewer_name
            
            if is_high_priority or is_assigned_to_me:
                priority_issues.append({
                    "id": issue.get("id"),
                    "title": issue.get("title", ""),
                    "priority": issue.get("priority", 0),
                    "state": issue.get("state", {}).get("name", ""),
                    "assignee": issue.get("assignee", {}).get("name", ""),
                    "url": issue.get("url", ""),
                    "reason": "high_priority" if is_high_priority else "assigned_to_me"
                })
        
        print(json.dumps(priority_issues))
    else:
        print("[]")
except Exception as e:
    print("[]")
                '''
            ], capture_output=True, text=True, cwd=self.current_directory / "code")
            
            if result.returncode == 0 and result.stdout.strip():
                try:
                    priority_issues = json.loads(result.stdout.strip())
                    print(f"[SUCCESS] Identified {len(priority_issues)} priority Linear issues for next session")
                except json.JSONDecodeError:
                    pass
                    
        except Exception as e:
            print(f"[WARNING] Priority Linear issues identification failed: {e}")
            
        return priority_issues
    
    async def _save_session_to_memory(self):
        """Save session data to memory engine"""
        print("[MEMORY] Saving session to memory...")
        
        try:
            # Create session summary
            session_summary = self._create_session_summary()
            
            if self.memory_engine:
                # Save to memory engine
                await self._save_to_memory_engine(session_summary)
            
            # Always save to file as backup
            await self._save_to_file(session_summary)
            
            print("[SUCCESS] Session saved to memory")
            
        except Exception as e:
            print(f"[ERROR] Session memory save failed: {e}")
    
    def _create_session_summary(self) -> str:
        """Create a summary of the session for memory storage"""
        session_state = self.session_data.get("session_state", {})
        unfinished_tasks = self.session_data.get("unfinished_tasks", {})
        
        summary_parts = [
            f"Session ended at {self.session_end_time.strftime('%Y-%m-%d %H:%M:%S UTC')}",
            f"Working directory: {session_state.get('working_directory', 'Unknown')}"
        ]
        
        # Git status
        git_status = session_state.get("git_status", {})
        if git_status.get("is_git_repo"):
            summary_parts.append(f"Git branch: {git_status.get('current_branch', 'unknown')}")
            if git_status.get("uncommitted_changes"):
                summary_parts.append("Has uncommitted changes")
        
        # Unfinished work
        session_todos = unfinished_tasks.get("session_todos", [])
        if session_todos:
            summary_parts.append("Unfinished tasks:")
            summary_parts.extend([f"  - {todo}" for todo in session_todos])
        
        # Code TODOs
        code_todos = unfinished_tasks.get("code_todos", [])
        if code_todos:
            summary_parts.append(f"Found {len(code_todos)} code TODOs")
        
        # Recent files
        open_files = session_state.get("open_files", [])
        if open_files:
            summary_parts.append(f"Recently modified files: {', '.join(open_files[:3])}")
        
        # Linear issues
        linear_issues = self.session_data.get("linear_issues", {})
        issues_snapshot = linear_issues.get("issues_snapshot", {})
        if issues_snapshot.get("total_open", 0) > 0:
            summary_parts.append(f"Linear issues: {issues_snapshot['total_open']} open ({issues_snapshot['assigned_to_me']} assigned)")
        
        session_updates = linear_issues.get("session_updates", [])
        if session_updates:
            summary_parts.append("Linear session updates:")
            summary_parts.extend([f"  - {update}" for update in session_updates])
        
        return "\n".join(summary_parts)
    
    async def _save_to_memory_engine(self, session_summary: str):
        """Save session to memory engine"""
        try:
            # This would integrate with the existing DevEnviro memory system
            # For now, we'll use a simple approach
            memory_data = {
                "content": session_summary,
                "memory_type": "episodic",
                "category": "session_signoff",
                "importance": 0.8,
                "metadata": {
                    "session_end_time": self.session_end_time.isoformat(),
                    "project_path": str(self.current_directory)
                }
            }
            
            # This would call the actual memory engine store method
            print("[INFO] Session summary prepared for memory engine")
            
        except Exception as e:
            print(f"[WARNING] Memory engine storage failed: {e}")
    
    async def _save_to_file(self, session_summary: str):
        """Save session data to file"""
        try:
            # Save to .devenviro directory
            devenviro_dir = self.current_directory / ".devenviro"
            if not devenviro_dir.exists():
                devenviro_dir.mkdir(parents=True)
            
            # Save session data
            session_file = devenviro_dir / "last_session.json"
            with open(session_file, 'w') as f:
                json.dump({
                    "session_summary": session_summary,
                    "session_data": self.session_data,
                    "timestamp": self.session_end_time.isoformat()
                }, f, indent=2)
            
            print(f"[SUCCESS] Session data saved to {session_file}")
            
        except Exception as e:
            print(f"[WARNING] File save failed: {e}")
    
    async def _clean_workspace(self):
        """Clean workspace for next session"""
        print("[CLEAN] Preparing workspace...")
        
        try:
            # Clean up temporary files
            temp_patterns = ["*.tmp", "*.temp", ".DS_Store", "Thumbs.db"]
            cleaned_files = 0
            
            for pattern in temp_patterns:
                for temp_file in self.current_directory.rglob(pattern):
                    try:
                        temp_file.unlink()
                        cleaned_files += 1
                    except Exception:
                        continue
            
            if cleaned_files > 0:
                print(f"[SUCCESS] Cleaned {cleaned_files} temporary files")
            else:
                print("[SUCCESS] Workspace already clean")
                
        except Exception as e:
            print(f"[WARNING] Workspace cleaning failed: {e}")
    
    async def _generate_session_report(self):
        """Generate final session report"""
        print("\n" + "=" * 50)
        print("SESSION SIGNOFF REPORT")
        print("=" * 50)
        
        # Session overview
        session_state = self.session_data.get("session_state", {})
        print(f"Session ended: {self.session_end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Working directory: {session_state.get('working_directory', 'Unknown')}")
        
        # Git status summary
        git_status = session_state.get("git_status", {})
        if git_status.get("is_git_repo"):
            print(f"Git branch: {git_status.get('current_branch', 'unknown')}")
            if git_status.get("uncommitted_changes"):
                print("[WARNING] Uncommitted changes detected")
                if git_status.get("staged_files"):
                    print(f"   Staged files: {len(git_status['staged_files'])}")
                if git_status.get("modified_files"):
                    print(f"   Modified files: {len(git_status['modified_files'])}")
                if git_status.get("untracked_files"):
                    print(f"   Untracked files: {len(git_status['untracked_files'])}")
            else:
                print("[SUCCESS] Working tree clean")
        
        # Linear issues summary
        linear_issues = self.session_data.get("linear_issues", {})
        issues_snapshot = linear_issues.get("issues_snapshot", {})
        session_updates = linear_issues.get("session_updates", [])
        priority_issues = linear_issues.get("priority_issues", [])
        
        if issues_snapshot.get("total_open", 0) > 0:
            print(f"\n[LINEAR] LINEAR ISSUES STATUS:")
            print(f"   Total open: {issues_snapshot['total_open']}")
            print(f"   Assigned to you: {issues_snapshot['assigned_to_me']}")
            print(f"   High priority: {issues_snapshot['high_priority']}")
            print(f"   Updated recently: {issues_snapshot['updated_recently']}")
            
            if session_updates:
                print(f"   Session updates:")
                for update in session_updates:
                    print(f"     - {update}")
            
            if priority_issues:
                print(f"   Priority issues for next session: {len(priority_issues)}")
                for issue in priority_issues[:3]:  # Show top 3
                    priority_names = {0: 'None', 1: 'Low', 2: 'Medium', 3: 'High', 4: 'Urgent'}
                    priority_str = priority_names.get(issue.get('priority', 0), 'Unknown')
                    print(f"     - [{priority_str}] {issue.get('title', '')[:50]}...")
        
        # Unfinished work summary
        unfinished_tasks = self.session_data.get("unfinished_tasks", {})
        session_todos = unfinished_tasks.get("session_todos", [])
        code_todos = unfinished_tasks.get("code_todos", [])
        
        if session_todos or code_todos:
            print("\n[TASKS] UNFINISHED WORK:")
            for todo in session_todos:
                print(f"   - {todo}")
            if code_todos:
                print(f"   - {len(code_todos)} code TODOs found")
        else:
            print("\n[SUCCESS] No unfinished work noted")
        
        # Next session prep
        print("\n[READY] NEXT SESSION READY:")
        print("   - Session state captured")
        print("   - Project state preserved")
        print("   - Unfinished tasks recorded")
        print("   - Workspace cleaned")
        
        print("\nRun startup script to restore session context!")


async def main():
    """Main signoff entry point"""
    signoff = SessionSignoff()
    success = await signoff.run_signoff_sequence()
    
    if not success:
        print("\n[WARNING] Session signoff completed with warnings")
        print("Check error messages above for details.")
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[EXIT] Session signoff cancelled")
        sys.exit(0)