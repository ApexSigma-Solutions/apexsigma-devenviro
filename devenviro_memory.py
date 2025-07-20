#!/usr/bin/env python3
"""
DevEnviro Memory CLI
Command-line interface for memory management
"""
import sys
import argparse
from pathlib import Path
sys.path.append('.')

from devenviro.terminal_output import safe_print, print_success, print_error, print_info, print_memory
from devenviro.memory_manager import MemoryManager, initialize_devenviro_memory

def cmd_health(args):
    """Check memory system health"""
    manager = MemoryManager()
    health = manager.health_check()
    
    print_memory("Memory System Health Check")
    print_info(f"Overall Status: {health['overall_status']}")
    
    # Simple engine health
    simple = health['simple_engine']
    safe_print(f"Simple Engine: {simple['status']}")
    safe_print(f"  Can Read: {simple['can_read']}")
    safe_print(f"  Can Write: {simple['can_write']}")
    safe_print(f"  Data Consistent: {simple['data_consistent']}")
    safe_print(f"  Total Memories: {simple['total_memories']}")
    
    # Advanced engine health
    advanced = health['advanced_engine']
    safe_print(f"Vector Engine: {advanced['status']}")

def cmd_stats(args):
    """Show memory statistics"""
    manager = MemoryManager()
    stats = manager.get_stats()
    
    print_memory("Memory System Statistics")
    safe_print(f"Total Memories: {stats['total_memories']}")
    safe_print(f"Storage Location: {stats['storage_location']}")
    safe_print(f"Last Updated: {stats['last_updated']}")
    
    safe_print("Categories:")
    for category, count in stats['categories'].items():
        safe_print(f"  {category}: {count}")
    
    safe_print("Engines:")
    for engine, available in stats['engines'].items():
        status = "Available" if available else "Not Available"
        safe_print(f"  {engine}: {status}")

def cmd_search(args):
    """Search memories"""
    manager = MemoryManager()
    results = manager.search_memories(args.query, args.category, args.limit)
    
    print_memory(f"Search Results for '{args.query}'")
    if not results:
        print_info("No memories found")
        return
    
    for i, memory in enumerate(results, 1):
        safe_print(f"{i}. [{memory['category']}] {memory['content'][:100]}...")
        safe_print(f"   ID: {memory['id'][:8]}... | Importance: {memory['importance']} | {memory['timestamp'][:10]}")
        safe_print("")

def cmd_add(args):
    """Add a new memory"""
    manager = MemoryManager()
    
    memory_id = manager.add_memory(
        args.content,
        args.category,
        {"source": "cli", "manual_entry": True},
        args.importance
    )
    
    print_success(f"Memory added: {memory_id[:8]}...")

def cmd_backup(args):
    """Create backup"""
    manager = MemoryManager()
    backups = manager.backup_all(args.backup_dir)
    
    print_success("Backup completed:")
    for engine, path in backups.items():
        safe_print(f"  {engine}: {path}")

def cmd_init(args):
    """Initialize memory system"""
    manager = initialize_devenviro_memory()
    print_success("Memory system initialized successfully")

def cmd_extract(args):
    """Extract memories from current session"""
    print_info("Memory extraction from current session...")
    
    manager = MemoryManager()
    
    # Add current session summary
    session_summary = f"DevEnviro session on {manager._get_git_branch()} branch. "
    session_summary += "Memory engine restored, chat persistence active, rules system operational. "
    
    if args.context:
        session_summary += f"User context: {args.context}"
    
    memory_id = manager.add_memory(
        session_summary,
        "episodic",
        {"source": "session_extract", "manual": True},
        0.7
    )
    
    print_success(f"Session memory extracted: {memory_id[:8]}...")

def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(
        description="DevEnviro Memory Management CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python devenviro_memory.py health              # Check system health
  python devenviro_memory.py stats               # Show statistics
  python devenviro_memory.py search "dashboard"  # Search for memories
  python devenviro_memory.py add "New insight"   # Add memory
  python devenviro_memory.py backup              # Create backup
  python devenviro_memory.py init                # Initialize system
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Health command
    parser_health = subparsers.add_parser('health', help='Check memory system health')
    parser_health.set_defaults(func=cmd_health)
    
    # Stats command
    parser_stats = subparsers.add_parser('stats', help='Show memory statistics')
    parser_stats.set_defaults(func=cmd_stats)
    
    # Search command
    parser_search = subparsers.add_parser('search', help='Search memories')
    parser_search.add_argument('query', help='Search query')
    parser_search.add_argument('--category', help='Filter by category')
    parser_search.add_argument('--limit', type=int, default=10, help='Maximum results')
    parser_search.set_defaults(func=cmd_search)
    
    # Add command
    parser_add = subparsers.add_parser('add', help='Add new memory')
    parser_add.add_argument('content', help='Memory content')
    parser_add.add_argument('--category', default='general', help='Memory category')
    parser_add.add_argument('--importance', type=float, default=0.5, help='Importance (0.0-1.0)')
    parser_add.set_defaults(func=cmd_add)
    
    # Backup command
    parser_backup = subparsers.add_parser('backup', help='Create backup')
    parser_backup.add_argument('--backup-dir', help='Backup directory')
    parser_backup.set_defaults(func=cmd_backup)
    
    # Init command
    parser_init = subparsers.add_parser('init', help='Initialize memory system')
    parser_init.set_defaults(func=cmd_init)
    
    # Extract command
    parser_extract = subparsers.add_parser('extract', help='Extract memories from current session')
    parser_extract.add_argument('--context', help='Additional context for extraction')
    parser_extract.set_defaults(func=cmd_extract)
    
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        return
    
    try:
        args.func(args)
    except Exception as e:
        print_error(f"Command failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())