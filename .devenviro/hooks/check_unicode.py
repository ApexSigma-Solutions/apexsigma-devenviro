#!/usr/bin/env python3
"""
Pre-commit hook to check for unicode characters in terminal output.
Prevents Windows terminal compatibility issues by flagging emoji/unicode usage.
"""
import sys
import re
from pathlib import Path

# Common problematic unicode characters in terminal output
PROBLEMATIC_UNICODE = [
    # Status emojis
    '✅', '❌', '⚠️', '⚠', '🔗', '📡', '🎉', '🔧', '💡', '🚀', '📊', '🔍',
    # File/folder emojis  
    '📁', '📄', '📜', '📦', '🗂️',
    # System emojis
    '🖥️', '⚙️', '🔒', '🔑', '⏱️', '🌐', '💾', '🔄',
    # Development emojis
    '🏗️', '🧪', '🎯', '📈', '⭐', '🔥', '✨', '🐛', '🎨', '📝',
    # Animal/misc emojis commonly used in dev
    '🐧', '🐳', '🐍', '🦀', '🦄', '🚨', '🔔', '📢',
    # Warning/alert
    '💸', '🚨', '⛔', '🛑'
]

def check_file_for_unicode(file_path: Path) -> list:
    """Check a Python file for problematic unicode characters."""
    violations = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        for line_num, line in enumerate(lines, 1):
            # Skip comments that document the unicode (like this file)
            if line.strip().startswith('#') and 'unicode' in line.lower():
                continue
                
            # Check for problematic unicode characters
            for char in PROBLEMATIC_UNICODE:
                if char in line:
                    # Check if it's in a print statement or string
                    if re.search(r'(print\s*\(|f"|f\'|"|\')', line):
                        violations.append({
                            'file': file_path,
                            'line': line_num,
                            'char': char,
                            'content': line.strip()
                        })
                        
    except UnicodeDecodeError:
        # Skip binary files
        pass
    except Exception as e:
        print(f"Error checking {file_path}: {e}")
        
    return violations

def main():
    """Main pre-commit hook function."""
    if len(sys.argv) < 2:
        print("Usage: python check_unicode.py <file1> [file2] ...")
        sys.exit(1)
        
    all_violations = []
    
    for file_path in sys.argv[1:]:
        path = Path(file_path)
        if path.suffix == '.py' and path.exists():
            violations = check_file_for_unicode(path)
            all_violations.extend(violations)
    
    if all_violations:
        print("[ERROR] Unicode characters detected in terminal output:")
        print()
        
        for violation in all_violations:
            print(f"  File: {violation['file']}")
            print(f"  Line {violation['line']}: {violation['content']}")
            print(f"  Character: '{violation['char']}'")
            print()
            
        print("[INFO] Fix suggestions:")
        print("  1. Use the devenviro.terminal_output module:")
        print("     from devenviro.terminal_output import print_success, print_error")
        print("     print_success('message') instead of print('[SUCCESS] message')")
        print()
        print("  2. Replace unicode manually:")
        print("     ✅ → [SUCCESS]")
        print("     ❌ → [ERROR]") 
        print("     ⚠️ → [WARNING]")
        print("     🔗 → [LINK]")
        print("     📡 → [API]")
        print("     🎉 → [READY]")
        print("     🔧 → [HELP]")
        print()
        
        sys.exit(1)
    
    print("[SUCCESS] No problematic unicode characters found")
    sys.exit(0)

if __name__ == "__main__":
    main()