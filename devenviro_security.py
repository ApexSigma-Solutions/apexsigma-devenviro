#!/usr/bin/env python3
"""
DevEnviro Security CLI
Command-line interface for security operations
"""
import sys
import argparse
from pathlib import Path
sys.path.append('.')

from devenviro.terminal_output import safe_print, print_success, print_error, print_info, print_warning
from devenviro.security_manager import SecurityManager, initialize_security

def cmd_status(args):
    """Show security system status"""
    security = SecurityManager()
    status = security.get_security_status()
    
    print_info("DevEnviro Security Status")
    safe_print(f"Security Manager: {'Active' if status['security_manager_active'] else 'Inactive'}")
    safe_print(f"Background Monitoring: {'Active' if status['monitoring_active'] else 'Inactive'}")
    safe_print(f"Total Backups: {status['total_backups']}")
    safe_print(f"Critical Files Monitored: {status['critical_files_count']}")
    safe_print(f"Last Backup: {status['last_backup'] or 'Never'}")
    safe_print(f"Last Integrity Check: {status['last_integrity_check'] or 'Never'}")
    
    # Show backup settings
    config = status['config']
    safe_print("")
    safe_print("Configuration:")
    safe_print(f"  Auto Backup Interval: {config['auto_backup_interval_minutes']} minutes")
    safe_print(f"  Integrity Check Interval: {config['integrity_check_interval_minutes']} minutes")
    safe_print(f"  Max Backups: {config['max_backups']}")
    safe_print(f"  Checksum Algorithm: {config['checksum_algorithm']}")

def cmd_backup(args):
    """Create immediate backup"""
    security = SecurityManager()
    backup_path = security.create_versioned_backup()
    
    if backup_path:
        print_success(f"Backup created: {Path(backup_path).name}")
    else:
        print_error("Backup creation failed")

def cmd_integrity(args):
    """Run integrity check"""
    security = SecurityManager()
    results = security.verify_integrity()
    
    safe_print(f"Integrity Check Results ({results['timestamp'][:19]}):")
    safe_print(f"Overall Status: {results['overall_status'].upper()}")
    safe_print(f"Files Checked: {results['files_checked']}")
    safe_print(f"Files Healthy: {results['files_healthy']}")
    safe_print(f"Files Corrupted: {results['files_corrupted']}")
    safe_print(f"Missing Files: {results['missing_files']}")
    
    if args.verbose:
        safe_print("")
        safe_print("File Details:")
        for file_path, status in results['details'].items():
            status_icon = "✓" if status == "HEALTHY" else "✗" if status == "CORRUPTED" else "?"
            safe_print(f"  {status_icon} {Path(file_path).name}: {status}")

def cmd_restore(args):
    """Emergency restore from backup"""
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
            age_days = (Path.cwd().stat().st_ctime - backup.stat().st_ctime) / 86400
            safe_print(f"  {i+1}. {timestamp} ({age_days:.1f} days ago)")
        return
    
    if not args.backup_name:
        print_error("No backup specified. Use --list-backups to see available backups")
        return
    
    if not args.confirm:
        print_warning("Emergency restore will overwrite current data!")
        print_warning("Use --confirm to proceed with restore")
        return
    
    success = security.emergency_restore(args.backup_name)
    if success:
        print_success("Emergency restore completed")
    else:
        print_error("Emergency restore failed")

def cmd_checksums(args):
    """Manage checksums"""
    security = SecurityManager()
    
    if args.create:
        checksums = security.store_checksums()
        print_success(f"Checksums created for {len(checksums)} files")
    elif args.verify:
        results = security.verify_integrity()
        if results['overall_status'] == 'healthy':
            print_success("All checksums verified successfully")
        else:
            print_error(f"Checksum verification failed: {results['files_corrupted']} corrupted files")

def cmd_init(args):
    """Initialize security system"""
    security = initialize_security()
    print_success("Security system initialized with full protection")

def cmd_monitor(args):
    """Security monitoring commands"""
    security = SecurityManager()
    
    if args.start:
        if not security.monitor_thread or not security.monitor_thread.is_alive():
            security._start_monitoring()
            print_success("Background monitoring started")
        else:
            print_info("Background monitoring already active")
    elif args.stop:
        if security.monitor_thread and security.monitor_thread.is_alive():
            # Note: Can't cleanly stop thread, need to restart process
            print_warning("To stop monitoring, restart the application")
        else:
            print_info("Background monitoring not active")
    else:
        status = security.get_security_status()
        if status['monitoring_active']:
            print_success("Background monitoring is active")
        else:
            print_warning("Background monitoring is not active")

def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(
        description="DevEnviro Security Management CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python devenviro_security.py status              # Show security status
  python devenviro_security.py backup              # Create immediate backup
  python devenviro_security.py integrity           # Run integrity check
  python devenviro_security.py restore --list      # List available backups
  python devenviro_security.py checksums --create  # Generate checksums
  python devenviro_security.py init                # Initialize security
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Status command
    parser_status = subparsers.add_parser('status', help='Show security system status')
    parser_status.set_defaults(func=cmd_status)
    
    # Backup command
    parser_backup = subparsers.add_parser('backup', help='Create immediate backup')
    parser_backup.set_defaults(func=cmd_backup)
    
    # Integrity command
    parser_integrity = subparsers.add_parser('integrity', help='Run integrity check')
    parser_integrity.add_argument('--verbose', '-v', action='store_true', help='Show detailed results')
    parser_integrity.set_defaults(func=cmd_integrity)
    
    # Restore command
    parser_restore = subparsers.add_parser('restore', help='Emergency restore from backup')
    parser_restore.add_argument('--backup-name', help='Specific backup to restore')
    parser_restore.add_argument('--list-backups', '--list', action='store_true', help='List available backups')
    parser_restore.add_argument('--confirm', action='store_true', help='Confirm destructive restore operation')
    parser_restore.set_defaults(func=cmd_restore)
    
    # Checksums command
    parser_checksums = subparsers.add_parser('checksums', help='Manage checksums')
    parser_checksums.add_argument('--create', action='store_true', help='Create new checksums')
    parser_checksums.add_argument('--verify', action='store_true', help='Verify existing checksums')
    parser_checksums.set_defaults(func=cmd_checksums)
    
    # Init command
    parser_init = subparsers.add_parser('init', help='Initialize security system')
    parser_init.set_defaults(func=cmd_init)
    
    # Monitor command
    parser_monitor = subparsers.add_parser('monitor', help='Security monitoring controls')
    parser_monitor.add_argument('--start', action='store_true', help='Start background monitoring')
    parser_monitor.add_argument('--stop', action='store_true', help='Stop background monitoring')
    parser_monitor.set_defaults(func=cmd_monitor)
    
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