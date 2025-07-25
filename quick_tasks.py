#!/usr/bin/env python3
"""
Quick task status check without full DevEnviro startup
"""
import json
import os
import sys
from pathlib import Path
from datetime import datetime

# Simple output functions without dependencies
def print_success(msg): print(f"[SUCCESS] {msg}")
def print_error(msg): print(f"[ERROR] {msg}")
def print_info(msg): print(f"[INFO] {msg}")
def safe_print(msg): print(msg)
def print_section_header(title):
    print(f"\n{title}")
    print("=" * 50)


def load_cached_tasks():
    """Load tasks from last session cache"""
    session_file = Path('.devenviro/last_session.json')
    
    if not session_file.exists():
        print_error("No cached session found. Run 'python devenviro_startup.py' first.")
        return None
    
    try:
        with open(session_file, 'r') as f:
            session_data = json.load(f)
        return session_data
    except Exception as e:
        print_error(f"Failed to load session cache: {e}")
        return None


def show_cached_tasks():
    """Display cached tasks quickly"""
    print_section_header("[CACHE] Quick Task Status")
    
    session_data = load_cached_tasks()
    if not session_data:
        return False
    
    # Extract timestamp
    timestamp = session_data.get('timestamp', '')
    if timestamp:
        cache_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        safe_print(f"[INFO] Cache from: {cache_time.strftime('%Y-%m-%d %H:%M:%S UTC')}")
    
    # Extract unfinished tasks
    unfinished_tasks = session_data.get('session_data', {}).get('unfinished_tasks', {})
    
    # Git work
    git_work = unfinished_tasks.get('git_work', {})
    if git_work.get('uncommitted_work') or git_work.get('unpushed_commits'):
        print_info("Git Tasks:")
        if git_work.get('uncommitted_work'):
            files = git_work['uncommitted_work']
            safe_print(f"  [HIGH] Review uncommitted changes: {', '.join(files[:3])}")
        if git_work.get('unpushed_commits'):
            safe_print(f"  [MED] Push unpushed commits to remote")
        safe_print("")
    
    # Code TODOs
    code_todos = unfinished_tasks.get('code_todos', [])
    if code_todos:
        safe_print(f"[LOW] Review {len(code_todos)} code TODOs in project files")
        safe_print("")
    
    # Linear issues
    linear_issues = unfinished_tasks.get('linear_issues', {})
    if linear_issues:
        issues_snapshot = linear_issues.get('issues_snapshot', {})
        total_open = issues_snapshot.get('total_open', 0)
        if total_open > 0:
            safe_print(f"[HIGH] Review {total_open} open Linear issues")
        safe_print("")
    
    # Session todos
    session_todos = unfinished_tasks.get('session_todos', [])
    if session_todos:
        print_info("Session TODOs:")
        for todo in session_todos[:5]:  # Show first 5
            safe_print(f"  - {todo}")
        if len(session_todos) > 5:
            safe_print(f"  ... and {len(session_todos) - 5} more")
        safe_print("")
    
    print_success(f"Quick task overview complete! Use 'python devenviro_startup.py' for full details.")
    return True


def update_task_status(task_description, status='completed'):
    """Mark a cached task as completed"""
    session_data = load_cached_tasks()
    if not session_data:
        return False
    
    # Simple task completion tracking
    completed_tasks = session_data.get('completed_tasks', [])
    
    completion_entry = {
        'task': task_description,
        'status': status,
        'completed_at': datetime.utcnow().isoformat() + 'Z'
    }
    
    completed_tasks.append(completion_entry)
    session_data['completed_tasks'] = completed_tasks
    
    # Save back to cache
    try:
        with open('.devenviro/last_session.json', 'w') as f:
            json.dump(session_data, f, indent=2)
        print_success(f"Marked task as {status}: {task_description}")
        return True
    except Exception as e:
        print_error(f"Failed to update task status: {e}")
        return False


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == 'complete' and len(sys.argv) > 2:
            task_desc = ' '.join(sys.argv[2:])
            update_task_status(task_desc)
        elif sys.argv[1] == 'help':
            safe_print("Quick Tasks Usage:")
            safe_print("  python quick_tasks.py           # Show cached tasks")
            safe_print("  python quick_tasks.py complete TASK_DESCRIPTION")
            safe_print("  python quick_tasks.py help")
        else:
            show_cached_tasks()
    else:
        show_cached_tasks()