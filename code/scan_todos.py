#!/usr/bin/env python3
"""
Proper TODO scanner that only finds actual TODO/FIXME/XXX comments
"""
import re
from pathlib import Path
from collections import defaultdict


def find_real_todos():
    """Find actual TODO comments, not just any line containing 'todo'"""
    # Patterns for actual TODO comments (must start with # and have TODO: or TODO - etc)
    todo_patterns = [
        r'#\s*TODO\s*[:\-]',      # # TODO: or # TODO -
        r'#\s*FIXME\s*[:\-]',     # # FIXME: or # FIXME -  
        r'#\s*XXX\s*[:\-]',       # # XXX: or # XXX -
        r'#\s*HACK\s*[:\-]',      # # HACK: or # HACK -
        r'#\s*NOTE\s*[:\-]',      # # NOTE: or # NOTE -
        r'#\s*BUG\s*[:\-]',       # # BUG: or # BUG -
    ]
    
    todos = defaultdict(list)
    total_count = 0
    
    for py_file in Path('.').rglob('*.py'):
        # Skip certain directories
        if any(skip in str(py_file) for skip in ['venv', '__pycache__', '.git', 'build', 'dist']):
            continue
            
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            for line_num, line in enumerate(lines, 1):
                line_stripped = line.strip()
                
                # Skip lines that are regex pattern definitions or comments about TODOs
                if 'r\'' in line_stripped or 'regex' in line_stripped.lower() or 'pattern' in line_stripped.lower():
                    continue
                
                # Check if line matches any TODO pattern
                for pattern in todo_patterns:
                    if re.search(pattern, line_stripped, re.IGNORECASE):
                        # Extract the TODO type
                        match = re.search(r'#\s*(TODO|FIXME|XXX|HACK|NOTE|BUG)', line_stripped, re.IGNORECASE)
                        todo_type = match.group(1).upper() if match else 'TODO'
                        
                        todos[str(py_file)].append({
                            'line': line_num,
                            'content': line_stripped,
                            'type': todo_type,
                            'priority': 'high' if todo_type in ['FIXME', 'BUG'] else 'medium'
                        })
                        total_count += 1
                        break  # Only match one pattern per line
                        
        except Exception as e:
            print(f"[WARNING] Could not scan {py_file}: {e}")
    
    return dict(todos), total_count


def categorize_todos(todos_by_file):
    """Categorize TODOs by type and priority"""
    categories = {
        'CRITICAL': [],    # FIXME, BUG
        'IMPORTANT': [],   # TODO with specific implementation details
        'CLEANUP': [],     # General TODOs, NOTEs
        'RESEARCH': []     # XXX, HACK
    }
    
    for file_path, file_todos in todos_by_file.items():
        for todo in file_todos:
            todo_info = {
                'file': file_path,
                'line': todo['line'],
                'content': todo['content'],
                'type': todo['type']
            }
            
            if todo['type'] in ['FIXME', 'BUG']:
                categories['CRITICAL'].append(todo_info)
            elif todo['type'] == 'TODO' and any(word in todo['content'].lower() 
                                               for word in ['implement', 'add', 'create', 'fix']):
                categories['IMPORTANT'].append(todo_info)
            elif todo['type'] in ['XXX', 'HACK']:
                categories['RESEARCH'].append(todo_info)
            else:
                categories['CLEANUP'].append(todo_info)
    
    return categories


def main():
    """Main TODO scanning function"""
    print("[SCAN] Scanning for actual TODO comments...")
    print()
    
    todos_by_file, total_count = find_real_todos()
    
    if total_count == 0:
        print("[SUCCESS] No TODO comments found - codebase is clean!")
        return
    
    print(f"[INFO] Found {total_count} actual TODO comments")
    print()
    
    # Show by file
    print("[BREAKDOWN] TODOs by file:")
    for file_path, file_todos in sorted(todos_by_file.items()):
        print(f"  {file_path}: {len(file_todos)} items")
    print()
    
    # Categorize and show priorities
    categories = categorize_todos(todos_by_file)
    
    for category, items in categories.items():
        if items:
            print(f"[{category}] {len(items)} items:")
            for item in items[:3]:  # Show first 3 per category
                print(f"  {item['file']}:{item['line']} - {item['content']}")
            if len(items) > 3:
                print(f"  ... and {len(items) - 3} more")
            print()
    
    # Summary recommendations
    critical_count = len(categories['CRITICAL'])
    important_count = len(categories['IMPORTANT'])
    
    if critical_count > 0:
        print(f"[PRIORITY] Address {critical_count} critical items (FIXME/BUG) first")
    if important_count > 0:
        print(f"[NEXT] Then tackle {important_count} important implementation TODOs")
    
    cleanup_count = len(categories['CLEANUP']) + len(categories['RESEARCH'])
    if cleanup_count > 0:
        print(f"[LATER] {cleanup_count} general cleanup items can be addressed over time")


if __name__ == "__main__":
    main()