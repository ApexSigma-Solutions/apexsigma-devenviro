"""
Windows-safe terminal output utilities for DevEnviro.

This module provides unicode-safe output functions that work consistently
across Windows Command Prompt, PowerShell, and WSL2 environments.
"""

import sys
from typing import Optional


# Emoji to text mapping for Windows compatibility
EMOJI_MAP = {
    # Status indicators
    "✅": "[SUCCESS]",
    "❌": "[ERROR]",
    "⚠️": "[WARNING]", 
    "⚠": "[WARNING]",
    "🔗": "[LINK]",
    "📡": "[API]",
    "🎉": "[READY]",
    "🔧": "[HELP]",
    "💡": "[INFO]",
    "🚀": "[LAUNCH]",
    "📊": "[STATS]",
    "🔍": "[SEARCH]",
    "📁": "[FOLDER]",
    "📄": "[FILE]",
    "🖥️": "[SYSTEM]",
    "🔒": "[SECURE]",
    "🔑": "[KEY]",
    "⏱️": "[TIME]",
    "🌐": "[WEB]",
    "💾": "[SAVE]",
    "🔄": "[SYNC]",
    "📦": "[PACKAGE]",
    "🏗️": "[BUILD]",
    "🧪": "[TEST]",
    "🎯": "[TARGET]",
    "📈": "[METRICS]",
    "🔧": "[CONFIG]",
    "⭐": "[STAR]",
    "🔥": "[HOT]",
    "✨": "[NEW]",
    "🐛": "[BUG]",
    "🎨": "[STYLE]",
    "📝": "[DOCS]",
    "💸": "[COST]",
    "🚨": "[ALERT]",
    "🔔": "[NOTIFY]",
    "📢": "[ANNOUNCE]"
}


def safe_print(message: str, prefix: Optional[str] = None, **kwargs) -> None:
    """
    Print message with unicode characters converted to Windows-safe text.
    
    Args:
        message: The message to print
        prefix: Optional prefix to add (will also be converted)
        **kwargs: Additional arguments passed to print()
    """
    # Convert unicode characters to safe text
    safe_message = _convert_unicode(message)
    
    if prefix:
        safe_prefix = _convert_unicode(prefix)
        safe_message = f"{safe_prefix} {safe_message}"
    
    print(safe_message, **kwargs)


def _convert_unicode(text: str) -> str:
    """Convert unicode characters to Windows-safe text equivalents."""
    for emoji, replacement in EMOJI_MAP.items():
        text = text.replace(emoji, replacement)
    return text


def format_status(status: str, message: str) -> str:
    """
    Format a status message with consistent styling.
    
    Args:
        status: Status type ('success', 'error', 'warning', 'info')
        message: The message to format
        
    Returns:
        Formatted message string
    """
    status_map = {
        'success': '[SUCCESS]',
        'error': '[ERROR]', 
        'warning': '[WARNING]',
        'info': '[INFO]',
        'api': '[API]',
        'link': '[LINK]',
        'ready': '[READY]',
        'help': '[HELP]',
        'launch': '[LAUNCH]',
        'stats': '[STATS]',
        'search': '[SEARCH]'
    }
    
    prefix = status_map.get(status.lower(), f'[{status.upper()}]')
    return f"{prefix} {message}"


def print_status(status: str, message: str, **kwargs) -> None:
    """Print a formatted status message."""
    formatted_message = format_status(status, message)
    print(formatted_message, **kwargs)


def print_success(message: str, **kwargs) -> None:
    """Print a success message."""
    print_status('success', message, **kwargs)


def print_error(message: str, **kwargs) -> None:
    """Print an error message."""
    print_status('error', message, **kwargs)


def print_warning(message: str, **kwargs) -> None:
    """Print a warning message."""
    print_status('warning', message, **kwargs)


def print_info(message: str, **kwargs) -> None:
    """Print an info message."""
    print_status('info', message, **kwargs)


# Convenience functions for common patterns
def print_section_header(title: str) -> None:
    """Print a section header with consistent formatting."""
    separator = "=" * 50
    safe_print(f"\n{title}")
    safe_print(separator)


def print_subsection(title: str) -> None:
    """Print a subsection header."""
    safe_print(f"\n{title}")
    safe_print("-" * len(title))


if __name__ == "__main__":
    # Test the unicode conversion
    test_messages = [
        "✅ Success message",
        "❌ Error occurred", 
        "⚠️ Warning message",
        "🔗 Testing connection",
        "📡 API call in progress",
        "🎉 Ready to go!",
        "🔧 Need help with configuration"
    ]
    
    print("Testing unicode conversion:")
    for msg in test_messages:
        safe_print(f"Original: {repr(msg)}")
        safe_print(f"Converted: {_convert_unicode(msg)}")
        safe_print("")