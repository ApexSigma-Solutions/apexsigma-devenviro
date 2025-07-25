# Unicode Policy for Windows Terminal Compatibility

## Problem Statement

Unicode characters (emojis) in terminal output cause encoding issues on Windows systems, particularly in Command Prompt and PowerShell environments. This leads to:

- `UnicodeEncodeError: 'charmap' codec can't encode character` errors
- Inconsistent display across different terminal environments
- Poor user experience for Windows developers

## Policy

**NO UNICODE CHARACTERS** are allowed in terminal output within Python print statements or logging.

## Approved Replacements

Use text-based equivalents for all visual indicators:

| Unicode | Replacement | Usage |
|---------|-------------|-------|
| ✅ | `[SUCCESS]` | Success messages |
| ❌ | `[ERROR]` | Error messages |
| ⚠️ | `[WARNING]` | Warning messages |
| 🔗 | `[LINK]` | Connection/linking |
| 📡 | `[API]` | API operations |
| 🎉 | `[READY]` | Ready/completion |
| 🔧 | `[HELP]` | Help/troubleshooting |
| 💡 | `[INFO]` | Information |
| 🚀 | `[LAUNCH]` | Launch/startup |
| 📊 | `[STATS]` | Statistics/metrics |
| 🔍 | `[SEARCH]` | Search operations |
| 📁 | `[FOLDER]` | Directory references |
| 🐧 | `[SYSTEM]` | System information |
| 🐳 | `[DOCKER]` | Docker operations |
| 🐍 | `[PYTHON]` | Python environment |
| 🧪 | `[TEST]` | Testing operations |

## Implementation

### 1. Use Terminal Output Module

```python
from devenviro.terminal_output import print_success, print_error, print_warning, safe_print

# Good
print_success("Operation completed")
print_error("Something failed")
print_warning("Check your configuration")

# Bad  
print("✅ Operation completed")
print("❌ Something failed")
print("⚠️ Check your configuration")
```

### 2. Pre-commit Hook

A pre-commit hook automatically checks for unicode violations:

```yaml
- repo: local
  hooks:
    - id: no-unicode-terminal-output
      name: No Unicode in Terminal Output
      entry: python
      args: [.devenviro/hooks/check_unicode.py]
      language: system
      files: \.py$
      exclude: ^(devenviro/terminal_output\.py|tests/.*|docs/.*)$
```

### 3. Manual Testing

Test the unicode checker:

```bash
python .devenviro/hooks/check_unicode.py path/to/file.py
```

## Exceptions

Unicode is allowed in:

1. **Documentation files** (`.md`, `.rst`, `.txt`)
2. **Test files** in the `tests/` directory
3. **The terminal_output module** itself (`devenviro/terminal_output.py`)
4. **Comments that document unicode** (not in output strings)

## Benefits

1. **Cross-platform compatibility** - Works on Windows, Linux, and macOS
2. **Consistent display** - Same appearance across all terminal environments
3. **No encoding errors** - Eliminates UnicodeEncodeError issues
4. **Professional appearance** - Clean, structured output format
5. **Automated enforcement** - Pre-commit hooks prevent violations

## Migration

All existing files have been updated to follow this policy:

- ✅ `code/test_linear_wsl2.py` - Fixed
- ✅ `code/project_status.py` - Fixed  
- ✅ `code/test_mem0.py` - Fixed
- ✅ `code/test_wsl2_setup.py` - Fixed
- ✅ `devenviro/terminal_output.py` - Created
- ✅ `.devenviro/hooks/check_unicode.py` - Created
- ✅ `.pre-commit-config.yaml` - Updated

## Enforcement

The pre-commit hook will:

1. **Scan** all Python files for problematic unicode characters
2. **Report** violations with file, line number, and character
3. **Suggest** replacements using the terminal_output module
4. **Block commits** until violations are fixed

This ensures consistent, Windows-compatible terminal output across the entire ApexSigma DevEnviro project.