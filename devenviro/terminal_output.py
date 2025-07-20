"""
Windows-safe terminal output functions
Provides Unicode-safe printing for Windows Command Prompt and PowerShell
"""
import sys
import os


def safe_print(message, end='\n', flush=False):
    """
    Print message safely handling Windows terminal encoding issues
    """
    try:
        # Try to print normally first
        print(message, end=end, flush=flush)
    except UnicodeEncodeError:
        # Fallback to ASCII-safe output
        safe_message = message.encode('ascii', 'replace').decode('ascii')
        print(safe_message, end=end, flush=flush)


def print_success(message):
    """Print success message with safe formatting"""
    safe_print(f"[SUCCESS] {message}")


def print_error(message):
    """Print error message with safe formatting"""
    safe_print(f"[ERROR] {message}")


def print_warning(message):
    """Print warning message with safe formatting"""
    safe_print(f"[WARNING] {message}")


def print_info(message):
    """Print info message with safe formatting"""
    safe_print(f"[INFO] {message}")


def print_api(message):
    """Print API message with safe formatting"""
    safe_print(f"[API] {message}")


def print_ready(message):
    """Print ready message with safe formatting"""
    safe_print(f"[READY] {message}")


def print_help(message):
    """Print help message with safe formatting"""
    safe_print(f"[HELP] {message}")


def print_launch(message):
    """Print launch message with safe formatting"""
    safe_print(f"[LAUNCH] {message}")


def print_stats(message):
    """Print stats message with safe formatting"""
    safe_print(f"[STATS] {message}")


def print_loading(message):
    """Print loading message with safe formatting"""
    safe_print(f"[LOADING] {message}")


def print_memory(message):
    """Print memory message with safe formatting"""
    safe_print(f"[MEMORY] {message}")


def print_search(message):
    """Print search message with safe formatting"""
    safe_print(f"[SEARCH] {message}")


# Unicode replacement mapping
UNICODE_REPLACEMENTS = {
    "✅": "[SUCCESS]",
    "❌": "[ERROR]", 
    "⚠️": "[WARNING]",
    "🔗": "[LINK]",
    "📡": "[API]",
    "🎉": "[READY]",
    "🔧": "[HELP]",
    "💡": "[INFO]",
    "🚀": "[LAUNCH]",
    "📊": "[STATS]",
    "🔄": "[LOADING]",
    "🧠": "[MEMORY]",
    "📋": "[TASKS]",
    "📂": "[FILES]",
    "🔍": "[SEARCH]",
    "⚙️": "[CONFIG]",
    "🌟": "[HIGHLIGHT]",
    "📝": "[NOTE]",
    "🎯": "[TARGET]",
    "🔐": "[SECURE]",
    "⏳": "[WAIT]",
    "🔀": "[MERGE]",
    "📈": "[TREND]",
    "🛠️": "[TOOLS]",
    "📦": "[PACKAGE]",
    "🌐": "[NETWORK]",
    "🔥": "[PRIORITY]",
    "🚫": "[BLOCKED]",
    "➡️": "[NEXT]",
    "💻": "[CODE]",
    "📱": "[MOBILE]",
    "🖥️": "[DESKTOP]",
    "☁️": "[CLOUD]",
    "🔒": "[LOCKED]",
    "🔓": "[UNLOCKED]"
}


def replace_unicode(text):
    """Replace Unicode characters with Windows-safe equivalents"""
    for unicode_char, replacement in UNICODE_REPLACEMENTS.items():
        text = text.replace(unicode_char, replacement)
    return text