#!/usr/bin/env python3
"""
DevEnviro Startup Script
Enhanced initialization with session restoration and task presentation
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import asyncio

# Add devenviro to path
sys.path.append(str(Path(__file__).parent / "devenviro"))

from gemini_memory_engine import GeminiMemoryEngine
from devenviro import DevEnviroManager


class DevEnviroStartup:
    """Enhanced DevEnviro startup with session restoration and task management"""
    
    def __init__(self):
        self.manager = DevEnviroManager()
        self.memory_engine = None
        self.current_directory = Path.cwd()
        self.startup_time = datetime.now()
        
    async def run_startup_sequence(self):
        """Main startup sequence with enhanced session restoration"""
        print("DevEnviro Enhanced Startup")
        print("=" * 50)
        
        try:
            # Step 1: Initialize global workspace
            await self._initialize_global_workspace()
            
            # Step 2: Detect and handle project context
            project_info = await self._detect_project_context()
            
            # Step 3: Initialize memory engine
            await self._initialize_memory_engine()
            
            # Step 4: Restore session context
            session_context = await self._restore_session_context()
            
            # Step 5: Present unfinished tasks
            await self._present_unfinished_tasks(session_context)
            
            # Step 6: Interactive startup menu
            await self._interactive_startup_menu(project_info, session_context)
            
        except Exception as e:
            print(f"ERROR: Startup failed: {e}")
            return False
            
        return True
    
    async def _initialize_global_workspace(self):
        """Initialize global DevEnviro workspace"""
        print("\n[INIT] Initializing Global Workspace...")
        
        try:
            # Run devenviro global initialization
            result = subprocess.run(
                [sys.executable, "devenviro.py", "global"],
                capture_output=True,
                text=True,
                cwd=self.current_directory
            )
            
            if result.returncode == 0:
                print("[SUCCESS] Global workspace initialized")
                print(f"   Output: {result.stdout.strip()}")
            else:
                print(f"[WARNING] Global workspace warning: {result.stderr.strip()}")
                
        except Exception as e:
            print(f"[ERROR] Global workspace initialization failed: {e}")
            
    async def _detect_project_context(self) -> Dict:
        """Detect current project context and available projects"""
        print("\n[DETECT] Detecting Project Context...")
        
        project_info = {
            "current_project": None,
            "available_projects": [],
            "is_devenviro_project": False,
            "project_type": "unknown"
        }
        
        # Check current directory for DevEnviro project
        devenviro_dir = self.current_directory / ".devenviro"
        if devenviro_dir.exists():
            config_file = devenviro_dir / "config.json"
            if config_file.exists():
                try:
                    with open(config_file, 'r') as f:
                        config = json.load(f)
                    project_info["current_project"] = config.get("project_name", self.current_directory.name)
                    project_info["is_devenviro_project"] = True
                    project_info["project_type"] = config.get("project_type", "unknown")
                    print(f"[SUCCESS] Current project: {project_info['current_project']}")
                    print(f"   Type: {project_info['project_type']}")
                except Exception as e:
                    print(f"[WARNING] Config read error: {e}")
        
        # Scan for other DevEnviro projects
        home_dir = Path.home()
        projects_dirs = [
            home_dir / "Projects",
            home_dir / "projects", 
            Path("C:/Users/steyn/apexsigma-projects"),
            Path("C:/Users/steyn/Projects")
        ]
        
        for projects_dir in projects_dirs:
            if projects_dir.exists():
                for item in projects_dir.iterdir():
                    if item.is_dir() and (item / ".devenviro").exists():
                        if item != self.current_directory:
                            project_info["available_projects"].append({
                                "name": item.name,
                                "path": str(item),
                                "last_modified": item.stat().st_mtime
                            })
        
        print(f"   Found {len(project_info['available_projects'])} other DevEnviro projects")
        
        return project_info
    
    async def _initialize_memory_engine(self):
        """Initialize memory engine for session restoration"""
        print("\n[MEMORY] Initializing Memory Engine...")
        
        try:
            # Initialize Gemini memory engine
            self.memory_engine = GeminiMemoryEngine()
            
            # Test health
            health_status = await self._check_memory_health()
            if health_status["healthy"]:
                print("[SUCCESS] Memory engine operational")
                print(f"   Memories stored: {health_status.get('memory_count', 'Unknown')}")
                print(f"   Last operation: {health_status.get('last_operation', 'Unknown')}")
            else:
                print("[WARNING] Memory engine issues detected")
                
        except Exception as e:
            print(f"[ERROR] Memory engine initialization failed: {e}")
            self.memory_engine = None
    
    async def _check_memory_health(self) -> Dict:
        """Check memory engine health status"""
        try:
            if not self.memory_engine:
                return {"healthy": False, "error": "Memory engine not initialized"}
                
            # Run health check (implement based on existing health check)
            result = subprocess.run(
                [sys.executable, "devenviro.py", "health"],
                capture_output=True,
                text=True,
                cwd=self.current_directory
            )
            
            if result.returncode == 0:
                return {
                    "healthy": True,
                    "memory_count": "Available",
                    "last_operation": "Recent"
                }
            else:
                return {"healthy": False, "error": result.stderr.strip()}
                
        except Exception as e:
            return {"healthy": False, "error": str(e)}
    
    async def _restore_session_context(self) -> Dict:
        """Restore session context from episodic memory"""
        print("\n[SESSION] Restoring Session Context...")
        
        session_context = {
            "recent_memories": [],
            "unfinished_tasks": [],
            "last_session": None,
            "session_summary": ""
        }
        
        if not self.memory_engine:
            print("[WARNING] Memory engine unavailable - limited session restoration")
            return session_context
            
        try:
            # Search for recent episodic memories (last 72 hours)
            recent_memories = await self._search_recent_memories()
            session_context["recent_memories"] = recent_memories
            
            # Extract unfinished tasks from memories
            unfinished_tasks = await self._extract_unfinished_tasks(recent_memories)
            session_context["unfinished_tasks"] = unfinished_tasks
            
            # Generate session summary
            session_summary = await self._generate_session_summary(recent_memories)
            session_context["session_summary"] = session_summary
            
            print(f"[SUCCESS] Session context restored")
            print(f"   Recent memories: {len(recent_memories)}")
            print(f"   Unfinished tasks: {len(unfinished_tasks)}")
            
        except Exception as e:
            print(f"[ERROR] Session restoration failed: {e}")
            
        return session_context
    
    async def _search_recent_memories(self) -> List[Dict]:
        """Search for recent episodic memories"""
        try:
            # Use existing DevEnviro search functionality
            result = subprocess.run(
                [sys.executable, "devenviro.py", "search", "recent episodic"],
                capture_output=True,
                text=True,
                cwd=self.current_directory
            )
            
            if result.returncode == 0:
                # Parse search results (implement based on actual output format)
                return [{"content": "Recent memory placeholder", "timestamp": self.startup_time}]
            else:
                return []
                
        except Exception as e:
            print(f"Memory search error: {e}")
            return []
    
    async def _extract_unfinished_tasks(self, memories: List[Dict]) -> List[Dict]:
        """Extract unfinished tasks from recent memories and session signoff"""
        unfinished_tasks = []
        
        # Priority 1: Check for session signoff data
        try:
            signoff_data = await self._load_session_signoff_data()
            if signoff_data:
                unfinished_tasks.extend(signoff_data)
                print(f"[SUCCESS] Loaded {len(signoff_data)} tasks from last session signoff")
        except Exception as e:
            print(f"[WARNING] Session signoff data error: {e}")
        
        # Priority 2: Check for .ai-cli-log directory with recent activity
        log_dir = self.current_directory / ".ai-cli-log"
        if log_dir.exists():
            try:
                # Get recent log files
                log_files = sorted(log_dir.glob("*.log"), key=lambda x: x.stat().st_mtime, reverse=True)
                
                for log_file in log_files[:3]:  # Check last 3 log files
                    if log_file.stat().st_mtime > (self.startup_time - timedelta(days=1)).timestamp():
                        # Simulate task extraction (implement actual parsing)
                        unfinished_tasks.append({
                            "task": f"Continue work from {log_file.name}",
                            "priority": "medium",
                            "source": "log_file",
                            "timestamp": datetime.fromtimestamp(log_file.stat().st_mtime)
                        })
                        
            except Exception as e:
                print(f"Log analysis error: {e}")
        
        # Priority 3: Check Linear issues (if available)
        try:
            # Use existing Linear API connection
            linear_script = self.current_directory / "code" / "test_linear_wsl2.py"
            if linear_script.exists():
                unfinished_tasks.append({
                    "task": "Review open Linear issues",
                    "priority": "high",
                    "source": "linear_api",
                    "timestamp": self.startup_time
                })
        except Exception:
            pass
            
        return unfinished_tasks
    
    async def _load_session_signoff_data(self) -> List[Dict]:
        """Load unfinished tasks from session signoff data"""
        signoff_tasks = []
        
        try:
            # Check for last session data
            devenviro_dir = self.current_directory / ".devenviro"
            session_file = devenviro_dir / "last_session.json"
            
            if session_file.exists():
                with open(session_file, 'r') as f:
                    session_data = json.load(f)
                
                # Extract session todos
                unfinished_tasks = session_data.get("session_data", {}).get("unfinished_tasks", {})
                session_todos = unfinished_tasks.get("session_todos", [])
                
                for todo in session_todos:
                    priority = "high"
                    if todo.startswith("PRIORITY:"):
                        priority = "high"
                        todo = todo.replace("PRIORITY:", "").strip()
                    elif todo.startswith("BLOCKER:"):
                        priority = "urgent"
                        todo = todo.replace("BLOCKER:", "").strip()
                    elif todo.startswith("NEXT:"):
                        priority = "medium"
                        todo = todo.replace("NEXT:", "").strip()
                    
                    signoff_tasks.append({
                        "task": todo,
                        "priority": priority,
                        "source": "session_signoff",
                        "timestamp": datetime.fromisoformat(session_data.get("timestamp"))
                    })
                
                # Extract git work
                git_work = unfinished_tasks.get("git_work", {})
                if git_work.get("uncommitted_work"):
                    signoff_tasks.append({
                        "task": f"Review uncommitted changes: {', '.join(git_work['uncommitted_work'][:3])}",
                        "priority": "high",
                        "source": "git_status",
                        "timestamp": datetime.fromisoformat(session_data.get("timestamp"))
                    })
                
                if git_work.get("unpushed_commits"):
                    signoff_tasks.append({
                        "task": "Push unpushed commits to remote",
                        "priority": "medium", 
                        "source": "git_status",
                        "timestamp": datetime.fromisoformat(session_data.get("timestamp"))
                    })
                
                # Extract code TODOs
                code_todos = unfinished_tasks.get("code_todos", [])
                if code_todos:
                    signoff_tasks.append({
                        "task": f"Review {len(code_todos)} code TODOs in project files",
                        "priority": "low",
                        "source": "code_analysis",
                        "timestamp": datetime.fromisoformat(session_data.get("timestamp"))
                    })
                
                # Extract Linear issues from signoff
                linear_issues = session_data.get("session_data", {}).get("linear_issues", {})
                
                # Add Linear session updates as tasks
                session_updates = linear_issues.get("session_updates", [])
                for update in session_updates:
                    signoff_tasks.append({
                        "task": f"Follow up on Linear update: {update}",
                        "priority": "medium",
                        "source": "linear_session_update",
                        "timestamp": datetime.fromisoformat(session_data.get("timestamp"))
                    })
                
                # Add priority Linear issues as tasks
                priority_issues = linear_issues.get("priority_issues", [])
                for issue in priority_issues[:3]:  # Top 3 priority issues
                    priority_names = {0: 'low', 1: 'low', 2: 'medium', 3: 'high', 4: 'urgent'}
                    priority = priority_names.get(issue.get('priority', 0), 'medium')
                    
                    signoff_tasks.append({
                        "task": f"Linear: {issue.get('title', 'Unknown issue')} [{issue.get('state', 'Unknown')}]",
                        "priority": priority,
                        "source": "linear_priority_issue",
                        "timestamp": datetime.fromisoformat(session_data.get("timestamp")),
                        "url": issue.get('url', '')
                    })
                
                # Add Linear issues summary if significant
                issues_snapshot = linear_issues.get("issues_snapshot", {})
                if issues_snapshot.get("assigned_to_me", 0) > 0:
                    signoff_tasks.append({
                        "task": f"Review {issues_snapshot['assigned_to_me']} assigned Linear issues",
                        "priority": "medium",
                        "source": "linear_assigned",
                        "timestamp": datetime.fromisoformat(session_data.get("timestamp"))
                    })
                
        except Exception as e:
            print(f"[WARNING] Failed to load session signoff data: {e}")
        
        return signoff_tasks
    
    async def _generate_session_summary(self, memories: List[Dict]) -> str:
        """Generate a brief session summary"""
        if not memories:
            return "No recent session context available"
            
        # Simple summary generation (enhance with actual memory analysis)
        return f"Session restored with {len(memories)} recent memories. Last activity detected in DevEnviro workspace."
    
    async def _present_unfinished_tasks(self, session_context: Dict):
        """Present unfinished tasks in structured format"""
        print("\n[TASKS] Unfinished Tasks & Session Context")
        print("=" * 50)
        
        # Show session summary
        if session_context["session_summary"]:
            print(f"[SUMMARY] Session Summary:")
            print(f"   {session_context['session_summary']}")
            print()
        
        # Show unfinished tasks
        tasks = session_context["unfinished_tasks"]
        if tasks:
            print("[TASKS] Unfinished Tasks:")
            for i, task in enumerate(tasks, 1):
                priority_icon = {"high": "[HIGH]", "medium": "[MED]", "low": "[LOW]"}.get(task["priority"], "[NONE]")
                print(f"   {i}. {priority_icon} {task['task']}")
                print(f"      Source: {task['source']} | {task['timestamp'].strftime('%Y-%m-%d %H:%M')}")
            print()
        else:
            print("[SUCCESS] No unfinished tasks detected")
            print()
        
        # Show recent memories count
        if session_context["recent_memories"]:
            print(f"[MEMORY] Recent Context: {len(session_context['recent_memories'])} memories available")
            print()
    
    async def _interactive_startup_menu(self, project_info: Dict, session_context: Dict):
        """Interactive startup menu with options"""
        print("\n[MENU] DevEnviro Startup Options")
        print("=" * 50)
        
        options = [
            "1. Continue in current project",
            "2. Switch to another project", 
            "3. Create new project",
            "4. Open memory dashboard",
            "5. Run health checks",
            "6. Extract session memories",
            "7. Exit startup"
        ]
        
        for option in options:
            print(option)
        
        print("\nSelect an option (1-7):", end=" ")
        
        try:
            choice = input().strip()
            await self._handle_menu_choice(choice, project_info, session_context)
        except KeyboardInterrupt:
            print("\n[EXIT] Startup cancelled")
        except Exception as e:
            print(f"\n[ERROR] Menu error: {e}")
    
    async def _handle_menu_choice(self, choice: str, project_info: Dict, session_context: Dict):
        """Handle user menu selection"""
        print()
        
        if choice == "1":
            print("[CONTINUE] Continuing in current project...")
            if project_info["is_devenviro_project"]:
                print(f"   Project: {project_info['current_project']}")
                print(f"   Type: {project_info['project_type']}")
            else:
                print("   Initializing DevEnviro in current directory...")
                subprocess.run([sys.executable, "devenviro.py", "project"])
                
        elif choice == "2":
            await self._switch_project_menu(project_info)
            
        elif choice == "3":
            await self._create_new_project_menu()
            
        elif choice == "4":
            print("[DASHBOARD] Starting memory dashboard...")
            subprocess.run([sys.executable, "devenviro.py", "dashboard"])
            
        elif choice == "5":
            print("[HEALTH] Running health checks...")
            subprocess.run([sys.executable, "devenviro.py", "health"])
            
        elif choice == "6":
            print("[EXTRACT] Extracting session memories...")
            subprocess.run([sys.executable, "devenviro.py", "extract"])
            
        elif choice == "7":
            print("[EXIT] Exiting startup")
            
        else:
            print("[ERROR] Invalid choice")
    
    async def _switch_project_menu(self, project_info: Dict):
        """Show available projects for switching"""
        projects = project_info["available_projects"]
        
        if not projects:
            print("No other DevEnviro projects found")
            return
            
        print("[PROJECTS] Available Projects:")
        for i, project in enumerate(projects, 1):
            last_mod = datetime.fromtimestamp(project["last_modified"])
            print(f"   {i}. {project['name']} ({last_mod.strftime('%Y-%m-%d %H:%M')})")
            print(f"      Path: {project['path']}")
        
        print(f"\nSelect project (1-{len(projects)}):", end=" ")
        try:
            choice = int(input().strip())
            if 1 <= choice <= len(projects):
                selected = projects[choice - 1]
                print(f"[SWITCH] Switching to {selected['name']}...")
                print(f"   cd {selected['path']}")
                # Note: Actual directory change would need to be handled by calling script
            else:
                print("[ERROR] Invalid project selection")
        except (ValueError, KeyboardInterrupt):
            print("[ERROR] Invalid input")
    
    async def _create_new_project_menu(self):
        """Create new project workflow"""
        print("[NEW] Create New Project")
        print("Enter project name:", end=" ")
        
        try:
            project_name = input().strip()
            if project_name:
                print(f"[CREATE] Creating project: {project_name}")
                subprocess.run([sys.executable, "devenviro.py", "new", "project", project_name])
            else:
                print("[ERROR] Project name cannot be empty")
        except KeyboardInterrupt:
            print("[ERROR] Project creation cancelled")


async def main():
    """Main startup entry point"""
    startup = DevEnviroStartup()
    success = await startup.run_startup_sequence()
    
    if success:
        print("\n[SUCCESS] DevEnviro startup completed successfully!")
        print("Your cognitive collaboration workspace is ready.")
    else:
        print("\n[ERROR] DevEnviro startup encountered issues")
        print("Please check the error messages above.")


if __name__ == "__main__":
    asyncio.run(main())