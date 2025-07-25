#!/usr/bin/env python3
"""
DevEnviro Unified CLI
Central command interface for all DevEnviro operations
"""
import sys
import argparse
from pathlib import Path
sys.path.append('.')

from devenviro.terminal_output import safe_print, print_success, print_error, print_info, print_memory
from devenviro.memory_manager import MemoryManager
from devenviro.security_manager import SecurityManager

def cmd_health(args):
    """Comprehensive system health check"""
    print_info("DevEnviro System Health Check")
    
    # Memory system health
    print_memory("Memory System:")
    memory = MemoryManager()
    memory_health = memory.health_check()
    
    safe_print(f"  Overall Status: {memory_health['overall_status']}")
    safe_print(f"  Simple Engine: {memory_health['simple_engine']['status']}")
    safe_print(f"  Total Memories: {memory_health['simple_engine']['total_memories']}")
    
    # Security system health
    print_info("Security System:")
    security = SecurityManager()
    security_status = security.get_security_status()
    
    safe_print(f"  Security Manager: {'Active' if security_status['security_manager_active'] else 'Inactive'}")
    safe_print(f"  Background Monitoring: {'Active' if security_status['monitoring_active'] else 'Inactive'}")
    safe_print(f"  Total Backups: {security_status['total_backups']}")
    
    # Integrity check
    print_info("Data Integrity:")
    integrity_results = security.verify_integrity()
    safe_print(f"  Overall Status: {integrity_results['overall_status']}")
    safe_print(f"  Files Healthy: {integrity_results['files_healthy']}")
    safe_print(f"  Files Corrupted: {integrity_results['files_corrupted']}")
    
    # Overall assessment
    overall_healthy = (
        memory_health['overall_status'] == 'healthy' and
        security_status['security_manager_active'] and
        integrity_results['overall_status'] == 'healthy'
    )
    
    if overall_healthy:
        print_success("DevEnviro system is fully operational and secure")
    else:
        print_error("DevEnviro system has issues requiring attention")

def cmd_stats(args):
    """Show comprehensive system statistics"""
    print_info("DevEnviro System Statistics")
    
    # Memory stats
    memory = MemoryManager()
    memory_stats = memory.get_stats()
    
    print_memory("Memory Engine:")
    safe_print(f"  Total Memories: {memory_stats['total_memories']}")
    safe_print(f"  Categories: {len(memory_stats['categories'])}")
    for category, count in memory_stats['categories'].items():
        safe_print(f"    {category}: {count}")
    
    # Security stats
    security = SecurityManager()
    security_status = security.get_security_status()
    
    print_info("Security System:")
    safe_print(f"  Total Backups: {security_status['total_backups']}")
    safe_print(f"  Last Backup: {security_status['last_backup'] or 'Never'}")
    safe_print(f"  Last Integrity Check: {security_status['last_integrity_check'] or 'Never'}")
    safe_print(f"  Critical Files Monitored: {security_status['critical_files_count']}")

def cmd_backup(args):
    """Create comprehensive backup"""
    print_info("Creating comprehensive DevEnviro backup...")
    
    # Memory backup
    memory = MemoryManager()
    memory_backups = memory.backup_all()
    
    # Security backup (includes everything)
    security = SecurityManager()
    security_backup = security.create_versioned_backup()
    
    if security_backup:
        print_success("Comprehensive backup completed")
        safe_print(f"Backup location: {Path(security_backup).name}")
    else:
        print_error("Backup failed")

def cmd_search(args):
    """Search memories with context"""
    memory = MemoryManager()
    results = memory.search_memories(args.query, args.category, args.limit)
    
    print_memory(f"Search Results for '{args.query}'")
    if not results:
        print_info("No memories found")
        return
    
    for i, result in enumerate(results, 1):
        safe_print(f"{i}. [{result['category']}] {result['content'][:100]}...")
        safe_print(f"   Importance: {result['importance']} | {result['timestamp'][:10]}")
        if args.verbose and result.get('metadata'):
            safe_print(f"   Metadata: {result['metadata']}")
        safe_print("")

def cmd_remember(args):
    """Add new memory with automatic categorization"""
    memory = MemoryManager()
    
    # Auto-detect category based on content keywords
    content_lower = args.content.lower()
    auto_category = "general"
    
    if any(word in content_lower for word in ["organization", "mission", "strategy", "company"]):
        auto_category = "organizational"
    elif any(word in content_lower for word in ["architecture", "technical", "system", "design"]):
        auto_category = "architectural"
    elif any(word in content_lower for word in ["procedure", "process", "steps", "how to"]):
        auto_category = "procedural"
    elif any(word in content_lower for word in ["session", "conversation", "meeting", "event"]):
        auto_category = "episodic"
    elif any(word in content_lower for word in ["fact", "information", "data", "definition"]):
        auto_category = "factual"
    
    category = args.category or auto_category
    importance = args.importance or 0.5
    
    memory_id = memory.add_memory(
        args.content,
        category,
        {"source": "cli", "auto_categorized": args.category is None},
        importance
    )
    
    print_success(f"Memory added: {memory_id[:8]}... (category: {category})")

def cmd_restore(args):
    """Emergency restore with verification"""
    if not args.confirm:
        print_error("Emergency restore requires --confirm flag")
        print_warning("This will overwrite current data with backup!")
        return
    
    security = SecurityManager()
    
    if args.list_backups:
        backups_dir = Path.cwd() / '.devenviro' / 'backups'
        backup_dirs = [d for d in backups_dir.iterdir() 
                      if d.is_dir() and d.name.startswith('devenviro_backup_')]
        
        if not backup_dirs:
            print_info("No backups available")
            return
        
        print_info("Available Backups:")
        backup_dirs.sort(key=lambda x: x.stat().st_ctime, reverse=True)
        for i, backup in enumerate(backup_dirs):
            timestamp = backup.name.replace('devenviro_backup_', '')
            safe_print(f"  {i+1}. {timestamp}")
        return
    
    # Perform restore
    success = security.emergency_restore(args.backup_name)
    
    if success:
        print_success("Emergency restore completed")
        
        # Verify restoration
        print_info("Verifying restored data...")
        integrity_results = security.verify_integrity()
        
        if integrity_results['overall_status'] == 'healthy':
            print_success("Data restoration verified successfully")
        else:
            print_warning("Restored data has integrity issues")
    else:
        print_error("Emergency restore failed")

def cmd_secure(args):
    """Security operations"""
    security = SecurityManager()
    
    if args.integrity:
        results = security.verify_integrity()
        if results['overall_status'] == 'healthy':
            print_success("All files passed integrity check")
        else:
            print_error(f"Integrity issues: {results['files_corrupted']} corrupted, {results['missing_files']} missing")
    
    elif args.checksums:
        checksums = security.store_checksums()
        print_success(f"Checksums updated for {len(checksums)} files")
    
    elif args.status:
        status = security.get_security_status()
        print_info("Security Status:")
        safe_print(f"  Monitoring: {'Active' if status['monitoring_active'] else 'Inactive'}")
        safe_print(f"  Backups: {status['total_backups']}")
        safe_print(f"  Last Check: {status['last_integrity_check'] or 'Never'}")
    
    else:
        # Default: run full security check
        print_info("Running comprehensive security check...")
        security.verify_integrity()
        security.create_versioned_backup()
        print_success("Security check and backup completed")

def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(
        description="DevEnviro Unified Command Line Interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  devenviro health                           # Complete system health check
  devenviro stats                            # System statistics
  devenviro search "dashboard"               # Search memories
  devenviro remember "New insight about AI"  # Add memory
  devenviro backup                           # Create backup
  devenviro secure --integrity              # Check data integrity
  devenviro restore --list                  # List backups
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Health command
    parser_health = subparsers.add_parser('health', help='Complete system health check')
    parser_health.set_defaults(func=cmd_health)
    
    # Stats command
    parser_stats = subparsers.add_parser('stats', help='Show system statistics')
    parser_stats.set_defaults(func=cmd_stats)
    
    # Search command
    parser_search = subparsers.add_parser('search', help='Search memories')
    parser_search.add_argument('query', help='Search query')
    parser_search.add_argument('--category', help='Filter by category')
    parser_search.add_argument('--limit', type=int, default=10, help='Maximum results')
    parser_search.add_argument('--verbose', '-v', action='store_true', help='Show detailed results')
    parser_search.set_defaults(func=cmd_search)
    
    # Remember command
    parser_remember = subparsers.add_parser('remember', help='Add new memory')
    parser_remember.add_argument('content', help='Memory content')
    parser_remember.add_argument('--category', help='Memory category (auto-detected if not specified)')
    parser_remember.add_argument('--importance', type=float, help='Importance (0.0-1.0)')
    parser_remember.set_defaults(func=cmd_remember)
    
    # Backup command
    parser_backup = subparsers.add_parser('backup', help='Create comprehensive backup')
    parser_backup.set_defaults(func=cmd_backup)
    
    # Restore command
    parser_restore = subparsers.add_parser('restore', help='Emergency restore from backup')
    parser_restore.add_argument('--backup-name', help='Specific backup to restore')
    parser_restore.add_argument('--list-backups', '--list', action='store_true', help='List available backups')
    parser_restore.add_argument('--confirm', action='store_true', help='Confirm destructive restore operation')
    parser_restore.set_defaults(func=cmd_restore)
    
    # Secure command
    parser_secure = subparsers.add_parser('secure', help='Security operations')
    parser_secure.add_argument('--integrity', action='store_true', help='Run integrity check')
    parser_secure.add_argument('--checksums', action='store_true', help='Update checksums')
    parser_secure.add_argument('--status', action='store_true', help='Show security status')
    parser_secure.set_defaults(func=cmd_secure)
    
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