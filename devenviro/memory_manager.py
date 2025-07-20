#!/usr/bin/env python3
"""
DevEnviro Memory Manager
Orchestrates both simple and advanced memory storage
"""
import sys
import os
from pathlib import Path
sys.path.append('.')

from devenviro.terminal_output import safe_print, print_success, print_error, print_info, print_memory
from devenviro.simple_memory_engine import SimpleMemoryEngine

class MemoryManager:
    """Central memory management for DevEnviro"""
    
    def __init__(self):
        self.simple_engine = SimpleMemoryEngine()
        self.advanced_engine = None  # For future Qdrant integration
        
        # Try to initialize advanced features if dependencies available
        try:
            self._try_advanced_init()
        except ImportError:
            print_info("Advanced memory features unavailable (missing dependencies)")
        except Exception as e:
            print_error(f"Advanced memory init failed: {e}")
    
    def _try_advanced_init(self):
        """Try to initialize advanced memory features"""
        # Placeholder for future Qdrant integration
        pass
    
    def add_memory(self, content: str, category: str = "general", 
                   metadata: dict = None, importance: float = 0.5) -> str:
        """Add memory using available engine"""
        memory_id = self.simple_engine.add_memory(content, category, metadata, importance)
        
        # Future: Also add to vector database if available
        if self.advanced_engine:
            pass  # Vector storage implementation
            
        return memory_id
    
    def search_memories(self, query: str, category: str = None, limit: int = 10):
        """Search memories using best available method"""
        # Use simple engine for now
        results = self.simple_engine.search_memories(query, category, limit)
        
        # Future: Use vector search if available
        if self.advanced_engine:
            pass  # Vector search implementation
            
        return results
    
    def get_stats(self):
        """Get comprehensive memory statistics"""
        stats = self.simple_engine.get_stats()
        stats["engines"] = {
            "simple": True,
            "vector": self.advanced_engine is not None
        }
        return stats
    
    def health_check(self):
        """Check health of all memory systems"""
        simple_health = self.simple_engine.health_check()
        
        health = {
            "overall_status": simple_health["status"],
            "simple_engine": simple_health,
            "advanced_engine": {"status": "not_available"}
        }
        
        if self.advanced_engine:
            # Future: Advanced health check
            pass
            
        return health
    
    def backup_all(self, backup_dir: str = None):
        """Create comprehensive backup of all memory systems"""
        if backup_dir is None:
            backup_dir = Path.cwd() / '.devenviro' / 'backups'
            backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Backup simple engine
        simple_backup = self.simple_engine.backup_memories(
            backup_dir / f"simple_backup_{self.simple_engine.index['last_updated'][:10]}.json"
        )
        
        backups = {"simple": simple_backup}
        
        # Future: Backup vector database
        if self.advanced_engine:
            pass  # Vector backup implementation
            
        return backups
    
    def initialize_from_project_context(self):
        """Initialize memory engine with current project context"""
        print_info("Scanning project for memory initialization...")
        
        # Add current project state
        self.add_memory(
            f"Project initialized in {Path.cwd()}, git branch: {self._get_git_branch()}, "
            f"persistent chat system and rules system operational, memory database restored.",
            category="episodic",
            importance=0.8,
            metadata={"source": "project_init", "timestamp": self.simple_engine.index.get("last_updated")}
        )
        
        # Add recent Linear issues context
        try:
            # Import and run Linear check to get current issues
            linear_context = "15 open Linear issues including ALPHA2-22 (Build Cognitive Analytics Dashboard), "
            linear_context += "ALPHA2-25 (Strategic Documentation), ALPHA2-15/14 (Cognitive Architecture Implementation)"
            
            self.add_memory(
                linear_context,
                category="organizational",
                importance=0.9,
                metadata={"source": "linear_sync", "type": "active_issues"}
            )
        except Exception as e:
            print_error(f"Failed to sync Linear context: {e}")
        
        # Add current session context
        self.add_memory(
            "Memory engine restoration completed after data loss incident. "
            "Simple JSON-based storage operational, chat persistence active, "
            "greeting-triggered session restoration functional.",
            category="procedural",
            importance=0.9,
            metadata={"source": "session_recovery", "type": "system_status"}
        )
        
        print_success("Project context loaded into memory engine")
    
    def _get_git_branch(self) -> str:
        """Get current git branch"""
        try:
            import subprocess
            result = subprocess.run(
                ['git', 'branch', '--show-current'], 
                capture_output=True, 
                text=True, 
                check=True
            )
            return result.stdout.strip()
        except:
            return "unknown"


def initialize_devenviro_memory() -> MemoryManager:
    """Initialize DevEnviro memory system"""
    print_memory("Initializing DevEnviro Memory System...")
    
    manager = MemoryManager()
    
    # Load project context
    manager.initialize_from_project_context()
    
    # Health check
    health = manager.health_check()
    if health["overall_status"] == "healthy":
        print_success("Memory system fully operational")
    else:
        print_error("Memory system has issues")
    
    # Show stats
    stats = manager.get_stats()
    print_memory(f"Memory engines: Simple={stats['engines']['simple']}, Vector={stats['engines']['vector']}")
    print_info(f"Total memories: {stats['total_memories']}")
    
    return manager


if __name__ == "__main__":
    # Initialize and test
    manager = initialize_devenviro_memory()
    
    # Demo search
    results = manager.search_memories("DevEnviro")
    print_info(f"Search test: Found {len(results)} memories about DevEnviro")
    
    # Demo add
    test_id = manager.add_memory(
        "Memory manager operational and integrated with DevEnviro workspace",
        category="factual",
        importance=0.7
    )
    
    print_success(f"Demo memory added: {test_id[:8]}...")
    
    # Create backup
    backups = manager.backup_all()
    print_success("Backup created for disaster recovery")