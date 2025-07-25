#!/usr/bin/env python3
"""
Simplified Memory Engine for DevEnviro
Bootstrap version without complex dependencies
"""
import os
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import hashlib
import uuid

# Add project root to path
sys.path.append('.')
from devenviro.terminal_output import safe_print, print_success, print_error, print_info, print_memory

# Environment setup
from dotenv import load_dotenv

class SimpleMemoryEngine:
    """Simplified memory engine for bootstrapping DevEnviro"""
    
    def __init__(self, memory_dir: str = None):
        self.project_root = Path.cwd()
        self.devenviro_root = self.project_root / '.devenviro'
        
        if memory_dir:
            self.memory_dir = Path(memory_dir)
        else:
            self.memory_dir = self.devenviro_root / 'memory'
            
        # Ensure directories exist
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize storage files
        self.memories_file = self.memory_dir / 'memories.json'
        self.index_file = self.memory_dir / 'index.json'
        self.config_file = self.memory_dir / 'config.json'
        
        # Load or initialize data
        self.memories = self._load_memories()
        self.index = self._load_index()
        self.config = self._load_config()
        
        # Load environment
        env_file = self.project_root / 'config' / 'secrets' / '.env'
        if env_file.exists():
            load_dotenv(env_file)
        
        print_success("Simple Memory Engine initialized")
        
    def _load_memories(self) -> List[Dict]:
        """Load memories from JSON file"""
        if self.memories_file.exists():
            try:
                with open(self.memories_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print_error(f"Failed to load memories: {e}")
        return []
    
    def _load_index(self) -> Dict:
        """Load memory index"""
        if self.index_file.exists():
            try:
                with open(self.index_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print_error(f"Failed to load index: {e}")
        return {"total_memories": 0, "categories": {}, "last_updated": None}
    
    def _load_config(self) -> Dict:
        """Load memory configuration"""
        default_config = {
            "engine_type": "simple",
            "version": "1.0.0",
            "max_memories": 1000,
            "auto_backup": True,
            "categories": [
                "factual", "procedural", "episodic", "semantic", 
                "organizational", "architectural", "temporal"
            ]
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # Merge with defaults
                    for key, value in default_config.items():
                        if key not in config:
                            config[key] = value
                    return config
            except Exception as e:
                print_error(f"Failed to load config: {e}")
        
        return default_config
    
    def _save_memories(self):
        """Save memories to file"""
        try:
            with open(self.memories_file, 'w', encoding='utf-8') as f:
                json.dump(self.memories, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print_error(f"Failed to save memories: {e}")
    
    def _save_index(self):
        """Save index to file"""
        try:
            with open(self.index_file, 'w', encoding='utf-8') as f:
                json.dump(self.index, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print_error(f"Failed to save index: {e}")
    
    def _save_config(self):
        """Save configuration"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print_error(f"Failed to save config: {e}")
    
    def add_memory(self, content: str, category: str = "general", 
                   metadata: Dict = None, importance: float = 0.5) -> str:
        """Add a new memory"""
        memory_id = str(uuid.uuid4())
        
        memory = {
            "id": memory_id,
            "content": content,
            "category": category,
            "importance": importance,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {},
            "hash": hashlib.md5(content.encode()).hexdigest()
        }
        
        self.memories.append(memory)
        
        # Update index
        self.index["total_memories"] = len(self.memories)
        self.index["last_updated"] = datetime.now().isoformat()
        
        if category not in self.index["categories"]:
            self.index["categories"][category] = 0
        self.index["categories"][category] += 1
        
        # Save to disk
        self._save_memories()
        self._save_index()
        
        print_success(f"Memory added: {memory_id[:8]}... ({category})")
        return memory_id
    
    def search_memories(self, query: str, category: str = None, limit: int = 10) -> List[Dict]:
        """Simple text search in memories"""
        query_lower = query.lower()
        results = []
        
        for memory in self.memories:
            # Basic text matching
            if query_lower in memory["content"].lower():
                if category is None or memory["category"] == category:
                    results.append(memory)
        
        # Sort by importance and recency
        results.sort(key=lambda x: (x["importance"], x["timestamp"]), reverse=True)
        
        return results[:limit]
    
    def get_memory(self, memory_id: str) -> Optional[Dict]:
        """Get specific memory by ID"""
        for memory in self.memories:
            if memory["id"] == memory_id:
                return memory
        return None
    
    def get_memories_by_category(self, category: str) -> List[Dict]:
        """Get all memories in a category"""
        return [m for m in self.memories if m["category"] == category]
    
    def delete_memory(self, memory_id: str) -> bool:
        """Delete a memory"""
        for i, memory in enumerate(self.memories):
            if memory["id"] == memory_id:
                category = memory["category"]
                del self.memories[i]
                
                # Update index
                self.index["total_memories"] = len(self.memories)
                self.index["categories"][category] -= 1
                if self.index["categories"][category] == 0:
                    del self.index["categories"][category]
                
                self._save_memories()
                self._save_index()
                print_success(f"Memory deleted: {memory_id[:8]}...")
                return True
        
        print_error(f"Memory not found: {memory_id[:8]}...")
        return False
    
    def get_stats(self) -> Dict:
        """Get memory engine statistics"""
        return {
            "total_memories": len(self.memories),
            "categories": dict(self.index["categories"]),
            "last_updated": self.index["last_updated"],
            "engine_type": self.config["engine_type"],
            "storage_location": str(self.memory_dir)
        }
    
    def health_check(self) -> Dict:
        """Check memory engine health"""
        try:
            # Check file permissions
            can_read = self.memories_file.exists() and os.access(self.memories_file, os.R_OK)
            can_write = os.access(self.memory_dir, os.W_OK)
            
            # Check data integrity
            total_memories = len(self.memories)
            index_total = self.index.get("total_memories", 0)
            data_consistent = total_memories == index_total
            
            health = {
                "status": "healthy" if can_read and can_write and data_consistent else "unhealthy",
                "can_read": can_read,
                "can_write": can_write,
                "data_consistent": data_consistent,
                "total_memories": total_memories,
                "index_total": index_total,
                "last_check": datetime.now().isoformat()
            }
            
            if health["status"] == "healthy":
                print_success("Memory engine health check passed")
            else:
                print_error("Memory engine health check failed")
                
            return health
            
        except Exception as e:
            print_error(f"Health check failed: {e}")
            return {"status": "error", "error": str(e)}
    
    def backup_memories(self, backup_path: str = None) -> str:
        """Create backup of all memories"""
        if backup_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = self.memory_dir / f"backup_{timestamp}.json"
        
        backup_data = {
            "timestamp": datetime.now().isoformat(),
            "version": self.config["version"],
            "total_memories": len(self.memories),
            "memories": self.memories,
            "index": self.index,
            "config": self.config
        }
        
        try:
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=2, ensure_ascii=False)
            
            print_success(f"Backup created: {backup_path}")
            return str(backup_path)
            
        except Exception as e:
            print_error(f"Backup failed: {e}")
            return ""
    
    def restore_from_backup(self, backup_path: str) -> bool:
        """Restore memories from backup"""
        try:
            with open(backup_path, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
            
            self.memories = backup_data["memories"]
            self.index = backup_data["index"]
            self.config = backup_data.get("config", self.config)
            
            self._save_memories()
            self._save_index()
            self._save_config()
            
            print_success(f"Restored {len(self.memories)} memories from backup")
            return True
            
        except Exception as e:
            print_error(f"Restore failed: {e}")
            return False


def initialize_memory_engine() -> SimpleMemoryEngine:
    """Initialize the simple memory engine"""
    engine = SimpleMemoryEngine()
    
    # Add some bootstrap memories if empty
    if len(engine.memories) == 0:
        print_info("Initializing with bootstrap memories...")
        
        engine.add_memory(
            "ApexSigma DevEnviro is a cognitive collaboration platform that transforms AI agents from stateless tools into persistent, organizationally-aware development partners.",
            category="organizational",
            importance=1.0,
            metadata={"source": "bootstrap", "type": "mission_statement"}
        )
        
        engine.add_memory(
            "Memory engine uses Gemini Flash 2.5 for natural language processing and Qdrant for vector storage with 7 memory categories: factual, procedural, episodic, semantic, organizational, architectural, temporal.",
            category="architectural",
            importance=0.9,
            metadata={"source": "bootstrap", "type": "technical_architecture"}
        )
        
        engine.add_memory(
            "Data persistence systems implemented after critical data loss incident. Chat history stored in .devenviro/chat_history/, session restoration triggered by user greetings.",
            category="procedural",
            importance=0.8,
            metadata={"source": "bootstrap", "type": "operational_procedure"}
        )
        
        print_success("Bootstrap memories added")
    
    return engine


if __name__ == "__main__":
    # Demo usage
    engine = initialize_memory_engine()
    
    # Show stats
    stats = engine.get_stats()
    print_memory(f"Memory Engine Stats: {stats['total_memories']} memories")
    for category, count in stats['categories'].items():
        safe_print(f"  {category}: {count}")
    
    # Health check
    health = engine.health_check()
    print_info(f"Health Status: {health['status']}")
    
    # Search demo
    results = engine.search_memories("DevEnviro")
    print_info(f"Search results for 'DevEnviro': {len(results)} found")