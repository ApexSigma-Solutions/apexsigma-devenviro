#!/usr/bin/env python3
"""
DevEnviro Security Manager
Comprehensive security for memory database and critical data
"""
import os
import json
import sys
import hashlib
import shutil
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import threading
import schedule

sys.path.append('.')
from devenviro.terminal_output import safe_print, print_success, print_error, print_info, print_warning

class SecurityManager:
    """Manages security for DevEnviro memory and data systems"""
    
    def __init__(self, devenviro_root: str = None):
        self.project_root = Path.cwd()
        self.devenviro_root = Path(devenviro_root) if devenviro_root else self.project_root / '.devenviro'
        
        # Security directories
        self.security_dir = self.devenviro_root / 'security'
        self.backups_dir = self.devenviro_root / 'backups'
        self.checksums_dir = self.devenviro_root / 'checksums'
        self.snapshots_dir = self.devenviro_root / 'snapshots'
        
        # Ensure security infrastructure exists
        for directory in [self.security_dir, self.backups_dir, self.checksums_dir, self.snapshots_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        # Security configuration
        self.config_file = self.security_dir / 'security_config.json'
        self.audit_log = self.security_dir / 'audit.log'
        self.integrity_log = self.security_dir / 'integrity.log'
        
        # Load or create security config
        self.config = self._load_security_config()
        
        # Initialize integrity tracking
        self.critical_files = [
            self.devenviro_root / 'memory' / 'memories.json',
            self.devenviro_root / 'memory' / 'index.json',
            self.devenviro_root / 'memory' / 'config.json',
            self.devenviro_root / 'chat_history',
            self.project_root / 'CLAUDE.md',
            self.project_root / 'rules',
            self.project_root / 'devenviro'
        ]
        
        # Start background security monitor if enabled
        self.monitor_thread = None
        if self.config.get('auto_monitoring', True):
            self._start_monitoring()
        
        print_success("Security Manager initialized")
    
    def _load_security_config(self) -> Dict:
        """Load security configuration"""
        default_config = {
            "version": "1.0.0",
            "auto_backup_interval_minutes": 30,
            "max_backups": 50,
            "integrity_check_interval_minutes": 15,
            "auto_monitoring": True,
            "backup_compression": True,
            "checksum_algorithm": "sha256",
            "critical_file_monitoring": True,
            "cloud_backup_enabled": False,
            "cloud_backup_path": "G:\\ApexSigmaSolutions\\Backups\\DevEnviro",
            "cloud_backup_providers": {
                "development": {
                    "type": "local_drive",
                    "path": "G:\\ApexSigmaSolutions\\Backups\\DevEnviro",
                    "enabled": True
                },
                "production": {
                    "type": "flexible",
                    "providers": ["aws_s3", "azure_blob", "gcp_storage"],
                    "enabled": False
                }
            },
            "encryption_enabled": False,
            "last_backup": None,
            "last_cloud_backup": None,
            "last_integrity_check": None
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
            except Exception as e:
                print_error(f"Failed to load security config: {e}")
        
        return default_config
    
    def _save_security_config(self):
        """Save security configuration"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print_error(f"Failed to save security config: {e}")
    
    def _log_audit(self, action: str, details: str = ""):
        """Log security audit event"""
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] {action}: {details}\n"
        
        try:
            with open(self.audit_log, 'a') as f:
                f.write(log_entry)
        except Exception as e:
            print_error(f"Failed to write audit log: {e}")
    
    def _log_integrity(self, file_path: str, status: str, details: str = ""):
        """Log integrity check result"""
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] {file_path}: {status} - {details}\n"
        
        try:
            with open(self.integrity_log, 'a') as f:
                f.write(log_entry)
        except Exception as e:
            print_error(f"Failed to write integrity log: {e}")
    
    def calculate_checksum(self, file_path: str, algorithm: str = "sha256") -> str:
        """Calculate file checksum"""
        file_path = Path(file_path)
        if not file_path.exists():
            return ""
        
        hash_func = hashlib.new(algorithm)
        
        try:
            if file_path.is_file():
                with open(file_path, 'rb') as f:
                    for chunk in iter(lambda: f.read(4096), b""):
                        hash_func.update(chunk)
            elif file_path.is_dir():
                # For directories, hash all files recursively
                for file in sorted(file_path.rglob('*')):
                    if file.is_file():
                        with open(file, 'rb') as f:
                            hash_func.update(file.name.encode())
                            for chunk in iter(lambda: f.read(4096), b""):
                                hash_func.update(chunk)
            
            return hash_func.hexdigest()
        except Exception as e:
            print_error(f"Failed to calculate checksum for {file_path}: {e}")
            return ""
    
    def store_checksums(self) -> Dict[str, str]:
        """Store checksums for all critical files"""
        checksums = {}
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        for file_path in self.critical_files:
            if file_path.exists():
                checksum = self.calculate_checksum(str(file_path))
                checksums[str(file_path)] = checksum
                
                # Store individual checksum file
                checksum_file = self.checksums_dir / f"{file_path.name}_{timestamp}.sha256"
                try:
                    with open(checksum_file, 'w') as f:
                        f.write(f"{checksum}  {file_path}\n")
                except Exception as e:
                    print_error(f"Failed to store checksum: {e}")
        
        # Store master checksum file
        master_file = self.checksums_dir / f"master_checksums_{timestamp}.json"
        try:
            with open(master_file, 'w') as f:
                json.dump({
                    "timestamp": datetime.now().isoformat(),
                    "algorithm": self.config["checksum_algorithm"],
                    "checksums": checksums
                }, f, indent=2)
        except Exception as e:
            print_error(f"Failed to store master checksums: {e}")
        
        self._log_audit("CHECKSUM_STORE", f"Stored checksums for {len(checksums)} files")
        print_success(f"Checksums stored for {len(checksums)} critical files")
        
        return checksums
    
    def verify_integrity(self) -> Dict[str, Any]:
        """Verify integrity of critical files"""
        results = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "healthy",
            "files_checked": 0,
            "files_healthy": 0,
            "files_corrupted": 0,
            "missing_files": 0,
            "details": {}
        }
        
        # Get latest checksums
        checksum_files = list(self.checksums_dir.glob("master_checksums_*.json"))
        if not checksum_files:
            print_warning("No baseline checksums found - creating initial checksums")
            self.store_checksums()
            return results
        
        latest_checksum_file = max(checksum_files, key=lambda x: x.stat().st_mtime)
        
        try:
            with open(latest_checksum_file, 'r') as f:
                baseline = json.load(f)
                baseline_checksums = baseline["checksums"]
        except Exception as e:
            print_error(f"Failed to load baseline checksums: {e}")
            return results
        
        # Check each critical file
        for file_path, baseline_checksum in baseline_checksums.items():
            results["files_checked"] += 1
            file_path_obj = Path(file_path)
            
            if not file_path_obj.exists():
                results["missing_files"] += 1
                results["details"][file_path] = "MISSING"
                self._log_integrity(file_path, "MISSING", "File not found")
                continue
            
            current_checksum = self.calculate_checksum(file_path)
            
            if current_checksum == baseline_checksum:
                results["files_healthy"] += 1
                results["details"][file_path] = "HEALTHY"
                self._log_integrity(file_path, "HEALTHY", "Checksum match")
            else:
                results["files_corrupted"] += 1
                results["details"][file_path] = "CORRUPTED"
                results["overall_status"] = "corrupted"
                self._log_integrity(file_path, "CORRUPTED", 
                                  f"Checksum mismatch: expected {baseline_checksum[:8]}..., got {current_checksum[:8]}...")
        
        # Update config
        self.config["last_integrity_check"] = results["timestamp"]
        self._save_security_config()
        
        self._log_audit("INTEGRITY_CHECK", 
                       f"Checked {results['files_checked']} files, "
                       f"{results['files_healthy']} healthy, "
                       f"{results['files_corrupted']} corrupted, "
                       f"{results['missing_files']} missing")
        
        if results["overall_status"] == "healthy":
            print_success("Integrity check passed - all files healthy")
        else:
            print_error(f"Integrity issues detected: {results['files_corrupted']} corrupted, {results['missing_files']} missing")
        
        return results
    
    def _should_exclude_from_backup(self, path: Path) -> bool:
        """Check if file/folder should be excluded from backup"""
        exclude_patterns = [
            '__pycache__',
            '.pyc',
            'node_modules',
            '.git',
            '.venv',
            'venv',
            '.env',
            'env',
            '.DS_Store',
            'Thumbs.db',
            '*.tmp',
            '*.temp',
            '*.log',
            '.pytest_cache',
            '.coverage'
        ]
        
        path_str = str(path).lower()
        return any(pattern.lower() in path_str for pattern in exclude_patterns)
    
    def _copy_with_exclusions(self, src: Path, dst: Path):
        """Copy directory while excluding problematic files"""
        def ignore_function(dir_path, contents):
            ignored = []
            for item in contents:
                item_path = Path(dir_path) / item
                if self._should_exclude_from_backup(item_path):
                    ignored.append(item)
            return ignored
        
        shutil.copytree(src, dst, ignore=ignore_function)

    def create_versioned_backup(self) -> str:
        """Create versioned backup of all critical data"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"devenviro_backup_{timestamp}"
        backup_path = self.backups_dir / backup_name
        
        try:
            backup_path.mkdir(exist_ok=True)
            
            # Backup memory database
            memory_src = self.devenviro_root / 'memory'
            if memory_src.exists():
                memory_dst = backup_path / 'memory'
                self._copy_with_exclusions(memory_src, memory_dst)
            
            # Backup chat history
            chat_src = self.devenviro_root / 'chat_history'
            if chat_src.exists():
                chat_dst = backup_path / 'chat_history'
                self._copy_with_exclusions(chat_src, chat_dst)
            
            # Backup security data (exclude logs)
            security_dst = backup_path / 'security'
            security_dst.mkdir()
            for item in self.security_dir.iterdir():
                if not self._should_exclude_from_backup(item) and item.name not in ['audit.log', 'integrity.log']:
                    if item.is_file():
                        shutil.copy2(item, security_dst)
                    else:
                        self._copy_with_exclusions(item, security_dst / item.name)
            
            # Backup critical project files
            project_backup = backup_path / 'project'
            project_backup.mkdir()
            
            for file_path in [self.project_root / 'CLAUDE.md', 
                            self.project_root / 'rules', 
                            self.project_root / 'devenviro']:
                if file_path.exists():
                    if file_path.is_file():
                        shutil.copy2(file_path, project_backup)
                    else:
                        self._copy_with_exclusions(file_path, project_backup / file_path.name)
            
            # Create backup manifest
            manifest = {
                "backup_id": backup_name,
                "timestamp": datetime.now().isoformat(),
                "backup_path": str(backup_path),
                "files_backed_up": len(list(backup_path.rglob('*'))),
                "integrity_checksums": self.store_checksums(),
                "backup_size_bytes": sum(f.stat().st_size for f in backup_path.rglob('*') if f.is_file())
            }
            
            with open(backup_path / 'manifest.json', 'w') as f:
                json.dump(manifest, f, indent=2)
            
            # Update config
            self.config["last_backup"] = manifest["timestamp"]
            self._save_security_config()
            
            # Clean old backups if needed
            self._cleanup_old_backups()
            
            self._log_audit("BACKUP_CREATE", f"Created backup: {backup_name}")
            print_success(f"Versioned backup created: {backup_name}")
            
            return str(backup_path)
            
        except Exception as e:
            print_error(f"Backup creation failed: {e}")
            self._log_audit("BACKUP_FAILED", str(e))
            return ""
    
    def _cleanup_old_backups(self):
        """Remove old backups beyond max_backups limit"""
        backup_dirs = [d for d in self.backups_dir.iterdir() 
                      if d.is_dir() and d.name.startswith('devenviro_backup_')]
        
        if len(backup_dirs) > self.config["max_backups"]:
            # Sort by creation time, keep newest
            backup_dirs.sort(key=lambda x: x.stat().st_ctime, reverse=True)
            old_backups = backup_dirs[self.config["max_backups"]:]
            
            for old_backup in old_backups:
                try:
                    shutil.rmtree(old_backup)
                    self._log_audit("BACKUP_CLEANUP", f"Removed old backup: {old_backup.name}")
                except Exception as e:
                    print_error(f"Failed to remove old backup {old_backup}: {e}")
    
    def _start_monitoring(self):
        """Start background security monitoring"""
        def monitor_worker():
            # Schedule integrity checks
            schedule.every(self.config["integrity_check_interval_minutes"]).minutes.do(self.verify_integrity)
            
            # Schedule automatic backups (with cloud sync if enabled)
            if self.config.get("cloud_backup_enabled", False):
                schedule.every(self.config["auto_backup_interval_minutes"]).minutes.do(self.create_cloud_backup)
            else:
                schedule.every(self.config["auto_backup_interval_minutes"]).minutes.do(self.create_versioned_backup)
            
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        
        self.monitor_thread = threading.Thread(target=monitor_worker, daemon=True)
        self.monitor_thread.start()
        print_info("Background security monitoring started")
    
    def get_security_status(self) -> Dict[str, Any]:
        """Get comprehensive security status"""
        backup_dirs = list(self.backups_dir.glob('devenviro_backup_*'))
        checksum_files = list(self.checksums_dir.glob('master_checksums_*.json'))
        
        status = {
            "security_manager_active": True,
            "last_backup": self.config.get("last_backup"),
            "last_integrity_check": self.config.get("last_integrity_check"),
            "total_backups": len(backup_dirs),
            "total_checksum_sets": len(checksum_files),
            "monitoring_active": self.monitor_thread is not None and self.monitor_thread.is_alive(),
            "critical_files_count": len(self.critical_files),
            "config": self.config
        }
        
        return status
    
    def emergency_restore(self, backup_name: str = None) -> bool:
        """Emergency restore from backup"""
        if backup_name is None:
            # Find latest backup
            backup_dirs = [d for d in self.backups_dir.iterdir() 
                          if d.is_dir() and d.name.startswith('devenviro_backup_')]
            if not backup_dirs:
                print_error("No backups available for emergency restore")
                return False
            
            latest_backup = max(backup_dirs, key=lambda x: x.stat().st_ctime)
            backup_path = latest_backup
        else:
            backup_path = self.backups_dir / backup_name
            if not backup_path.exists():
                print_error(f"Backup not found: {backup_name}")
                return False
        
        try:
            print_warning(f"Starting emergency restore from: {backup_path.name}")
            
            # Restore memory database
            if (backup_path / 'memory').exists():
                if (self.devenviro_root / 'memory').exists():
                    shutil.rmtree(self.devenviro_root / 'memory')
                shutil.copytree(backup_path / 'memory', self.devenviro_root / 'memory')
            
            # Restore chat history
            if (backup_path / 'chat_history').exists():
                if (self.devenviro_root / 'chat_history').exists():
                    shutil.rmtree(self.devenviro_root / 'chat_history')
                shutil.copytree(backup_path / 'chat_history', self.devenviro_root / 'chat_history')
            
            self._log_audit("EMERGENCY_RESTORE", f"Restored from backup: {backup_path.name}")
            print_success(f"Emergency restore completed from: {backup_path.name}")
            
            return True
            
        except Exception as e:
            print_error(f"Emergency restore failed: {e}")
            self._log_audit("RESTORE_FAILED", str(e))
            return False
    
    def sync_to_cloud(self, backup_path: str) -> bool:
        """Sync backup to cloud storage (G: drive for development)"""
        if not self.config.get("cloud_backup_enabled", False):
            return True  # Skip if cloud backup disabled
        
        try:
            backup_path_obj = Path(backup_path)
            if not backup_path_obj.exists():
                print_error(f"Backup path does not exist: {backup_path}")
                return False
            
            cloud_config = self.config.get("cloud_backup_providers", {}).get("development", {})
            if not cloud_config.get("enabled", False):
                print_info("Development cloud backup disabled")
                return True
            
            cloud_base_path = Path(cloud_config.get("path", "G:\\ApexSigmaSolutions\\Backups\\DevEnviro"))
            
            # Ensure cloud backup directory exists
            try:
                cloud_base_path.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                print_error(f"Failed to create cloud backup directory: {e}")
                return False
            
            # Create cloud backup with same name
            cloud_backup_path = cloud_base_path / backup_path_obj.name
            
            print_info(f"Syncing backup to cloud: {cloud_backup_path}")
            
            # Copy backup to cloud location
            if cloud_backup_path.exists():
                shutil.rmtree(cloud_backup_path)
            
            shutil.copytree(backup_path_obj, cloud_backup_path)
            
            # Verify cloud backup
            cloud_size = sum(f.stat().st_size for f in cloud_backup_path.rglob('*') if f.is_file())
            local_size = sum(f.stat().st_size for f in backup_path_obj.rglob('*') if f.is_file())
            
            if cloud_size != local_size:
                print_error(f"Cloud backup size mismatch: local={local_size}, cloud={cloud_size}")
                return False
            
            # Update config with cloud backup timestamp
            self.config["last_cloud_backup"] = datetime.now().isoformat()
            self._save_security_config()
            
            # Clean old cloud backups
            self._cleanup_old_cloud_backups(cloud_base_path)
            
            self._log_audit("CLOUD_BACKUP_SUCCESS", f"Synced to cloud: {cloud_backup_path}")
            print_success(f"Cloud backup completed: {cloud_backup_path}")
            
            return True
            
        except Exception as e:
            print_error(f"Cloud backup failed: {e}")
            self._log_audit("CLOUD_BACKUP_FAILED", str(e))
            return False
    
    def _cleanup_old_cloud_backups(self, cloud_base_path: Path):
        """Remove old cloud backups beyond max_backups limit"""
        try:
            cloud_backup_dirs = [d for d in cloud_base_path.iterdir() 
                               if d.is_dir() and d.name.startswith('devenviro_backup_')]
            
            if len(cloud_backup_dirs) > self.config["max_backups"]:
                # Sort by creation time, keep newest
                cloud_backup_dirs.sort(key=lambda x: x.stat().st_ctime, reverse=True)
                old_cloud_backups = cloud_backup_dirs[self.config["max_backups"]:]
                
                for old_backup in old_cloud_backups:
                    try:
                        shutil.rmtree(old_backup)
                        self._log_audit("CLOUD_BACKUP_CLEANUP", f"Removed old cloud backup: {old_backup.name}")
                    except Exception as e:
                        print_error(f"Failed to remove old cloud backup {old_backup}: {e}")
        except Exception as e:
            print_error(f"Cloud backup cleanup failed: {e}")
    
    def create_cloud_backup(self) -> str:
        """Create backup and sync to cloud in one operation"""
        # Create local backup first
        local_backup_path = self.create_versioned_backup()
        
        if local_backup_path:
            # Sync to cloud
            cloud_success = self.sync_to_cloud(local_backup_path)
            if cloud_success:
                print_success("Complete backup (local + cloud) created successfully")
            else:
                print_warning("Local backup created, but cloud sync failed")
        
        return local_backup_path
    
    def get_cloud_backup_status(self) -> Dict[str, Any]:
        """Get cloud backup status and information"""
        status = {
            "cloud_backup_enabled": self.config.get("cloud_backup_enabled", False),
            "last_cloud_backup": self.config.get("last_cloud_backup"),
            "cloud_provider": "development_local_drive",
            "cloud_backup_path": None,
            "cloud_backups_count": 0,
            "cloud_backup_accessible": False
        }
        
        cloud_config = self.config.get("cloud_backup_providers", {}).get("development", {})
        if cloud_config.get("enabled", False):
            cloud_path = Path(cloud_config.get("path", ""))
            status["cloud_backup_path"] = str(cloud_path)
            
            try:
                if cloud_path.exists():
                    status["cloud_backup_accessible"] = True
                    cloud_backups = [d for d in cloud_path.iterdir() 
                                   if d.is_dir() and d.name.startswith('devenviro_backup_')]
                    status["cloud_backups_count"] = len(cloud_backups)
            except Exception:
                status["cloud_backup_accessible"] = False
        
        return status


def initialize_security() -> SecurityManager:
    """Initialize DevEnviro security system"""
    print_info("Initializing DevEnviro Security System...")
    
    security = SecurityManager()
    
    # Perform initial security setup
    print_info("Creating initial checksums...")
    security.store_checksums()
    
    print_info("Performing initial integrity check...")
    security.verify_integrity()
    
    print_info("Creating initial backup...")
    security.create_versioned_backup()
    
    return security


if __name__ == "__main__":
    # Initialize and test security system
    security = initialize_security()
    
    # Show security status
    status = security.get_security_status()
    print_success("Security system operational")
    safe_print(f"Backups: {status['total_backups']}")
    safe_print(f"Monitoring: {'Active' if status['monitoring_active'] else 'Inactive'}")
    safe_print(f"Last backup: {status['last_backup']}")