#!/usr/bin/env python3
"""
Chat Persistence System for DevEnviro
Inspired by ai-cli-log patterns for reliable session history
"""
import os
import json
import datetime
from pathlib import Path
from typing import Dict, List, Optional
import sys
sys.path.append('.')
from devenviro.terminal_output import safe_print, print_success, print_error, print_info


class ChatSession:
    def __init__(self, session_id: str = None):
        self.devenviro_root = Path.cwd() / '.devenviro'
        self.chat_dir = self.devenviro_root / 'chat_history'
        self.config_file = self.devenviro_root / 'config.json'
        
        # Ensure directories exist
        self.chat_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate session ID if not provided
        if session_id is None:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            session_id = f"session_{timestamp}"
        
        self.session_id = session_id
        self.session_file = self.chat_dir / f"{session_id}.json"
        
        # Initialize session data
        self.session_data = {
            "session_id": session_id,
            "start_time": datetime.datetime.now().isoformat(),
            "git_branch": self._get_git_branch(),
            "working_directory": str(Path.cwd()),
            "conversations": [],
            "metadata": {
                "total_exchanges": 0,
                "last_updated": datetime.datetime.now().isoformat(),
                "session_status": "active"
            }
        }
        
        # Load existing session if file exists
        if self.session_file.exists():
            self._load_session()

    def _get_git_branch(self) -> str:
        """Get current git branch"""
        try:
            import subprocess
            result = subprocess.run(
                ['git', 'branch', '--show-current'], 
                capture_output=True, 
                text=True, 
                check=True
            )
            return result.stdout.strip()
        except:
            return "unknown"

    def _load_session(self):
        """Load existing session data"""
        try:
            with open(self.session_file, 'r', encoding='utf-8') as f:
                self.session_data = json.load(f)
            print_info(f"Loaded existing session: {self.session_id}")
        except Exception as e:
            print_error(f"Failed to load session: {e}")

    def add_exchange(self, user_message: str, assistant_response: str, context: Dict = None):
        """Add a conversation exchange to the session"""
        exchange = {
            "timestamp": datetime.datetime.now().isoformat(),
            "user_message": user_message,
            "assistant_response": assistant_response,
            "context": context or {},
            "exchange_id": len(self.session_data["conversations"]) + 1
        }
        
        self.session_data["conversations"].append(exchange)
        self.session_data["metadata"]["total_exchanges"] += 1
        self.session_data["metadata"]["last_updated"] = datetime.datetime.now().isoformat()
        
        # Save after each exchange
        self._save_session()

    def _save_session(self):
        """Save session data to file"""
        try:
            with open(self.session_file, 'w', encoding='utf-8') as f:
                json.dump(self.session_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print_error(f"Failed to save session: {e}")

    def close_session(self, summary: str = None):
        """Close the session with optional summary"""
        self.session_data["metadata"]["session_status"] = "closed"
        self.session_data["metadata"]["end_time"] = datetime.datetime.now().isoformat()
        if summary:
            self.session_data["metadata"]["summary"] = summary
        
        self._save_session()
        print_success(f"Session {self.session_id} closed and saved")

    def get_recent_exchanges(self, count: int = 5) -> List[Dict]:
        """Get recent conversation exchanges"""
        return self.session_data["conversations"][-count:]

    def search_conversations(self, query: str) -> List[Dict]:
        """Search conversations for specific content"""
        results = []
        for exchange in self.session_data["conversations"]:
            if (query.lower() in exchange["user_message"].lower() or 
                query.lower() in exchange["assistant_response"].lower()):
                results.append(exchange)
        return results


class ChatPersistenceManager:
    """Manager for all chat sessions and persistence operations"""
    
    def __init__(self):
        self.devenviro_root = Path.cwd() / '.devenviro'
        self.chat_dir = self.devenviro_root / 'chat_history'
        self.config_file = self.devenviro_root / 'config.json'
        
        # Ensure directories exist
        self.chat_dir.mkdir(parents=True, exist_ok=True)
        
        self.config = self._load_config()

    def _load_config(self) -> Dict:
        """Load chat persistence configuration"""
        default_config = {
            "chat_persistence": {
                "enabled": True,
                "max_sessions": 100,
                "auto_backup": True,
                "backup_interval_hours": 24,
                "compression": False
            },
            "current_session": None,
            "last_backup": None
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    # Merge with defaults
                    for key, value in default_config.items():
                        if key not in config:
                            config[key] = value
                    return config
            except:
                pass
        
        return default_config

    def _save_config(self):
        """Save configuration"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print_error(f"Failed to save config: {e}")

    def create_session(self, session_id: str = None) -> ChatSession:
        """Create a new chat session"""
        session = ChatSession(session_id)
        self.config["current_session"] = session.session_id
        self._save_config()
        print_success(f"Created new chat session: {session.session_id}")
        return session

    def get_current_session(self) -> Optional[ChatSession]:
        """Get the current active session"""
        if self.config["current_session"]:
            try:
                return ChatSession(self.config["current_session"])
            except:
                pass
        return None

    def list_sessions(self) -> List[str]:
        """List all available sessions"""
        session_files = list(self.chat_dir.glob("session_*.json"))
        return [f.stem for f in sorted(session_files, key=lambda x: x.stat().st_mtime, reverse=True)]

    def get_session_summary(self, session_id: str) -> Dict:
        """Get summary of a specific session"""
        session_file = self.chat_dir / f"{session_id}.json"
        if session_file.exists():
            try:
                with open(session_file, 'r') as f:
                    data = json.load(f)
                    return {
                        "session_id": data["session_id"],
                        "start_time": data["start_time"],
                        "total_exchanges": data["metadata"]["total_exchanges"],
                        "last_updated": data["metadata"]["last_updated"],
                        "status": data["metadata"].get("session_status", "unknown"),
                        "git_branch": data.get("git_branch", "unknown")
                    }
            except:
                pass
        return None

    def restore_session_context(self) -> Dict:
        """Restore context from the most recent session"""
        sessions = self.list_sessions()
        if not sessions:
            return {"message": "No previous sessions found"}
        
        latest_session_id = sessions[0]
        session = ChatSession(latest_session_id)
        recent_exchanges = session.get_recent_exchanges(3)
        
        context = {
            "previous_session": latest_session_id,
            "git_branch": session.session_data.get("git_branch"),
            "last_activity": session.session_data["metadata"]["last_updated"],
            "recent_conversations": recent_exchanges,
            "total_exchanges": session.session_data["metadata"]["total_exchanges"]
        }
        
        print_info(f"Restored context from session: {latest_session_id}")
        print_info(f"Previous session had {len(recent_exchanges)} recent exchanges")
        
        return context


def initialize_chat_persistence():
    """Initialize chat persistence system"""
    manager = ChatPersistenceManager()
    
    # Check if there's an existing session to restore
    current_session = manager.get_current_session()
    
    if current_session is None:
        # Create new session
        session = manager.create_session()
        print_success("Chat persistence initialized with new session")
    else:
        print_info(f"Resuming existing session: {current_session.session_id}")
        session = current_session
    
    return manager, session


if __name__ == "__main__":
    # Demo usage
    manager, session = initialize_chat_persistence()
    
    # Simulate adding a conversation
    session.add_exchange(
        user_message="good morning, im guessing you have amnesia again",
        assistant_response="Good morning! You're right - I start fresh each session. Let me check what's been happening in the project...",
        context={"greeting": True, "session_start": True}
    )
    
    print_success("Chat persistence demo completed")