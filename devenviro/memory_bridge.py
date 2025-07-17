#!/usr/bin/env python3
"""
ApexSigma DevEnviro Memory Bridge
Unified interface for Mem0 and complementary memory systems
"""

import os
import json
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from pathlib import Path

# Third-party imports
try:
    from mem0 import Memory
except ImportError:
    Memory = None
    
try:
    import asyncpg
except ImportError:
    asyncpg = None

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, VectorParams, PointStruct
except ImportError:
    QdrantClient = None

from dotenv import load_dotenv

# Import our native Gemini memory engine
try:
    from .gemini_memory_engine import GeminiMemoryEngine
except ImportError:
    try:
        from gemini_memory_engine import GeminiMemoryEngine
    except ImportError:
        GeminiMemoryEngine = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MemoryBridgeError(Exception):
    """Custom exception for memory bridge operations"""
    pass

class ApexSigmaMemoryBridge:
    """
    Unified memory bridge for ApexSigma DevEnviro
    Integrates Mem0 with complementary database systems
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize memory bridge with configuration"""
        self.config = self._load_config(config_path)
        
        # Initialize components
        self.mem0_client = None
        self.gemini_engine = None  # Native Gemini memory engine
        self.qdrant_client = None
        self.postgres_pool = None
        
        # Memory strategy: prefer Gemini engine over Mem0
        self.use_gemini = True
        
        # Performance tracking
        self.operation_stats = {
            "stores": 0,
            "searches": 0,
            "errors": 0,
            "total_response_time": 0.0
        }
    
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load configuration from environment and config files"""
        
        # Load environment variables
        env_file = Path(__file__).parent.parent / "config" / "secrets" / ".env"
        if env_file.exists():
            load_dotenv(env_file)
        
        # Determine provider and API key based on availability
        # Note: Mem0 doesn't currently support Google/Gemini provider directly
        # We'll add native Gemini support to our custom memory engine later
        if os.getenv("KIMIK2_API_KEY"):
            provider = "openai"
            api_key = os.getenv("KIMIK2_API_KEY")
            base_url = "https://api.kimik2.com/v1"
            model = "gpt-4o-mini"
        elif os.getenv("OPENROUTER_API_KEY"):
            provider = "openrouter"
            api_key = os.getenv("OPENROUTER_API_KEY")
            base_url = None
            model = "gpt-4o-mini"
        elif os.getenv("OPENAI_API_KEY"):
            provider = "openai"
            api_key = os.getenv("OPENAI_API_KEY")
            base_url = None
            model = "gpt-4o-mini"
        else:
            # No supported API key found
            provider = "openai"
            api_key = None
            base_url = None
            model = "gpt-4o-mini"
        
        config = {
            "mem0": {
                "provider": provider,
                "api_key": api_key,
                "base_url": base_url,
                "model": model,  # Dynamic model based on provider
                "vector_store": {
                    "provider": "qdrant",
                    "config": {
                        "host": "localhost",
                        "port": 6333,
                        "collection_name": "apexsigma-memory"
                    }
                }
            },
            "qdrant": {
                "host": "localhost",
                "port": 6333,
                "collection_name": "organizational-patterns"
            },
            "postgres": {
                "host": "localhost",
                "port": 5432,
                "database": "apexsigma",
                "user": os.getenv("POSTGRES_USER", "apexsigma"),
                "password": os.getenv("POSTGRES_PASSWORD", "")
            },
            "organization": {
                "id": "apexsigma",
                "name": "ApexSigma Solutions"
            }
        }
        
        return config
    
    async def initialize(self) -> bool:
        """Initialize all memory system components"""
        try:
            logger.info("Initializing ApexSigma Memory Bridge...")
            
            # Initialize Gemini Engine (preferred)
            if GeminiMemoryEngine and self.use_gemini:
                await self._initialize_gemini_engine()
            
            # Initialize Mem0 (fallback)
            if not self.gemini_engine:
                await self._initialize_mem0()
            
            # Initialize Qdrant (for organizational patterns)
            await self._initialize_qdrant()
            
            # Initialize PostgreSQL (for metadata)
            await self._initialize_postgres()
            
            logger.info("Memory Bridge initialization complete")
            return True
            
        except Exception as e:
            logger.error(f"Memory Bridge initialization failed: {e}")
            raise MemoryBridgeError(f"Initialization failed: {e}")
    
    async def _initialize_gemini_engine(self):
        """Initialize native Gemini memory engine"""
        try:
            logger.info("Initializing native Gemini Memory Engine...")
            self.gemini_engine = GeminiMemoryEngine()
            await self.gemini_engine.initialize()
            logger.info("Gemini Memory Engine initialized successfully")
        except Exception as e:
            logger.error(f"Gemini engine initialization failed: {e}")
            self.gemini_engine = None
            raise MemoryBridgeError(f"Gemini engine setup failed: {e}")
    
    async def _initialize_mem0(self):
        """Initialize Mem0 memory service"""
        if not Memory:
            raise MemoryBridgeError("mem0ai package not installed")
        
        if not self.config["mem0"]["api_key"]:
            raise MemoryBridgeError("No API key configured (GEMINI_API_KEY, GOOGLE_API_KEY, KIMIK2_API_KEY, OPENROUTER_API_KEY, or OPENAI_API_KEY)")
        
        try:
            # Configure Mem0 with our settings
            llm_config = {
                "model": self.config["mem0"]["model"],
                "api_key": self.config["mem0"]["api_key"]
            }
            
            # Add site_url if provided (for KIMIK2 or custom endpoints)
            if self.config["mem0"]["base_url"]:
                llm_config["site_url"] = self.config["mem0"]["base_url"]
            
            mem0_config = {
                "llm": {
                    "provider": self.config["mem0"]["provider"],
                    "config": llm_config
                },
                "vector_store": self.config["mem0"]["vector_store"]
            }
            
            self.mem0_client = Memory.from_config(mem0_config)
            logger.info("Mem0 client initialized successfully")
            
        except Exception as e:
            logger.error(f"Mem0 initialization failed: {e}")
            raise MemoryBridgeError(f"Mem0 setup failed: {e}")
    
    async def _initialize_qdrant(self):
        """Initialize Qdrant for organizational patterns"""
        if not QdrantClient:
            logger.warning("Qdrant client not available - organizational patterns disabled")
            return
        
        try:
            self.qdrant_client = QdrantClient(
                host=self.config["qdrant"]["host"],
                port=self.config["qdrant"]["port"]
            )
            
            # Create collection for organizational patterns if not exists
            collection_name = self.config["qdrant"]["collection_name"]
            try:
                collections = await asyncio.to_thread(self.qdrant_client.get_collections)
                collection_exists = any(c.name == collection_name for c in collections.collections)
                
                if not collection_exists:
                    await asyncio.to_thread(
                        self.qdrant_client.create_collection,
                        collection_name=collection_name,
                        vectors_config=VectorParams(size=1536, distance=Distance.COSINE)
                    )
                    logger.info(f"Created Qdrant collection: {collection_name}")
                
            except Exception as e:
                logger.warning(f"Qdrant collection setup issue: {e}")
            
            logger.info("Qdrant client initialized successfully")
            
        except Exception as e:
            logger.warning(f"Qdrant initialization failed: {e}")
            self.qdrant_client = None
    
    async def _initialize_postgres(self):
        """Initialize PostgreSQL for metadata storage"""
        if not asyncpg:
            logger.warning("asyncpg not available - metadata storage disabled")
            return
        
        try:
            postgres_config = self.config["postgres"]
            dsn = f"postgresql://{postgres_config['user']}:{postgres_config['password']}@{postgres_config['host']}:{postgres_config['port']}/{postgres_config['database']}"
            
            # For now, just test connection - we'll implement pool later
            # self.postgres_pool = await asyncpg.create_pool(dsn)
            logger.info("PostgreSQL configuration loaded (pool creation deferred)")
            
        except Exception as e:
            logger.warning(f"PostgreSQL initialization failed: {e}")
            self.postgres_pool = None
    
    async def store_memory(
        self, 
        content: str, 
        metadata: Optional[Dict[str, Any]] = None,
        category: str = "general",
        user_id: str = "apexsigma_system",
        agent_id: str = "devenviro_bridge"
    ) -> Dict[str, Any]:
        """
        Store memory using Gemini engine (preferred) or Mem0 (fallback)
        """
        start_time = datetime.now()
        
        try:
            # Use Gemini engine if available
            if self.gemini_engine:
                return await self._store_memory_gemini(content, metadata, category)
            
            # Fallback to Mem0
            if not self.mem0_client:
                raise MemoryBridgeError("No memory engine available (Gemini or Mem0)")
            
            # Enhance metadata with organizational context
            enhanced_metadata = {
                "organization_id": self.config["organization"]["id"],
                "category": category,
                "timestamp": start_time.isoformat(),
                "source": "apexsigma_devenviro"
            }
            
            if metadata:
                enhanced_metadata.update(metadata)
            
            # Store in Mem0 with required identifiers
            result = await asyncio.to_thread(
                self.mem0_client.add,
                content,
                user_id=user_id,
                agent_id=agent_id,
                metadata=enhanced_metadata
            )
            
            # Track performance
            self.operation_stats["stores"] += 1
            response_time = (datetime.now() - start_time).total_seconds()
            self.operation_stats["total_response_time"] += response_time
            
            logger.info(f"Memory stored successfully in {response_time:.3f}s")
            
            return {
                "success": True,
                "memory_id": result.get("id"),
                "response_time_ms": response_time * 1000,
                "metadata": enhanced_metadata
            }
            
        except Exception as e:
            self.operation_stats["errors"] += 1
            logger.error(f"Memory storage failed: {e}")
            raise MemoryBridgeError(f"Failed to store memory: {e}")
    
    async def _store_memory_gemini(self, content: str, metadata: Optional[Dict[str, Any]], category: str) -> Dict[str, Any]:
        """Store memory using native Gemini engine"""
        try:
            # Extract and store memories using Gemini
            extraction = await self.gemini_engine.extract_memory(content, metadata)
            
            if extraction["success"] and extraction["extraction"]["memories"]:
                # Store each extracted memory
                stored_memories = []
                for memory in extraction["extraction"]["memories"]:
                    store_result = await self.gemini_engine.store_memory(
                        memory_text=memory["memory_text"],
                        category=memory.get("category", category),
                        importance=memory.get("importance", 5),
                        tags=memory.get("tags", []),
                        metadata={
                            "source": "memory_bridge",
                            "original_category": category,
                            "relationships": memory.get("relationships", []),
                            "decay_hours": memory.get("decay_hours", 168),
                            **(metadata or {})
                        }
                    )
                    stored_memories.append(store_result)
                
                # Track performance
                self.operation_stats["stores"] += len(stored_memories)
                
                return {
                    "success": True,
                    "engine": "gemini",
                    "extraction": extraction,
                    "stored_memories": stored_memories,
                    "total_memories": len(stored_memories)
                }
            else:
                return {
                    "success": False,
                    "engine": "gemini",
                    "error": "No memories extracted",
                    "extraction": extraction
                }
        
        except Exception as e:
            logger.error(f"Gemini memory storage failed: {e}")
            raise MemoryBridgeError(f"Gemini storage failed: {e}")
    
    async def search_memory(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 10,
        user_id: str = "apexsigma_system",
        agent_id: str = "devenviro_bridge"
    ) -> List[Dict[str, Any]]:
        """
        Search memories using Mem0 with organizational context
        """
        start_time = datetime.now()
        
        try:
            # Use Gemini engine if available
            if self.gemini_engine:
                return await self._search_memory_gemini(query, filters, limit)
            
            # Fallback to Mem0
            if not self.mem0_client:
                raise MemoryBridgeError("No memory engine available (Gemini or Mem0)")
            
            # Add organizational filter
            search_filters = {
                "organization_id": self.config["organization"]["id"]
            }
            
            if filters:
                search_filters.update(filters)
            
            # Search in Mem0 with required identifiers
            results = await asyncio.to_thread(
                self.mem0_client.search,
                query=query,
                user_id=user_id,
                agent_id=agent_id,
                filters=search_filters,
                limit=limit
            )
            
            # Track performance
            self.operation_stats["searches"] += 1
            response_time = (datetime.now() - start_time).total_seconds()
            self.operation_stats["total_response_time"] += response_time
            
            logger.info(f"Memory search completed in {response_time:.3f}s, found {len(results)} results")
            
            return results
            
        except Exception as e:
            self.operation_stats["errors"] += 1
            logger.error(f"Memory search failed: {e}")
            raise MemoryBridgeError(f"Failed to search memory: {e}")
    
    async def _search_memory_gemini(self, query: str, filters: Optional[Dict[str, Any]], limit: int) -> List[Dict[str, Any]]:
        """Search memory using native Gemini engine"""
        try:
            # Extract category filter if provided
            category_filter = filters.get("category") if filters else None
            importance_threshold = filters.get("importance", 1) if filters else 1
            
            # Search using Gemini engine
            results = await self.gemini_engine.search_memory(
                query=query,
                limit=limit,
                category_filter=category_filter,
                importance_threshold=importance_threshold
            )
            
            # Track performance
            self.operation_stats["searches"] += 1
            
            return results
            
        except Exception as e:
            logger.error(f"Gemini memory search failed: {e}")
            raise MemoryBridgeError(f"Gemini search failed: {e}")
    
    async def load_context_hierarchy(self, project_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Load context in hierarchical order: Global → Project → Local
        """
        context = {}
        
        try:
            # 1. Load organizational memory
            org_memories = await self.search_memory(
                "organizational standards patterns architecture",
                filters={"category": "organizational"},
                limit=20
            )
            context["organizational_memory"] = org_memories
            
            # 2. Load project-specific context if provided
            if project_id:
                project_memories = await self.search_memory(
                    f"project {project_id} context",
                    filters={"project_id": project_id},
                    limit=10
                )
                context["project_memory"] = project_memories
            
            # 3. Load global context files
            context["global_context"] = await self._load_global_context_files()
            
            logger.info(f"Context hierarchy loaded for project: {project_id or 'global'}")
            
            return context
            
        except Exception as e:
            logger.error(f"Context loading failed: {e}")
            return {"error": str(e)}
    
    async def _load_global_context_files(self) -> Dict[str, str]:
        """Load global context files from the project"""
        context_files = {}
        
        base_path = Path(__file__).parent.parent
        
        # Load key context files
        files_to_load = [
            "CLAUDE.md",
            "GEMINI.md", 
            "LEARNED_KNOWLEDGE.md"
        ]
        
        for filename in files_to_load:
            file_path = base_path / filename
            if file_path.exists():
                try:
                    context_files[filename] = file_path.read_text(encoding='utf-8')
                except Exception as e:
                    logger.warning(f"Failed to load {filename}: {e}")
        
        return context_files
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        total_ops = self.operation_stats["stores"] + self.operation_stats["searches"]
        avg_response_time = (
            self.operation_stats["total_response_time"] / total_ops 
            if total_ops > 0 else 0
        )
        
        return {
            "total_operations": total_ops,
            "stores": self.operation_stats["stores"],
            "searches": self.operation_stats["searches"],
            "errors": self.operation_stats["errors"],
            "average_response_time_ms": avg_response_time * 1000,
            "error_rate": self.operation_stats["errors"] / total_ops if total_ops > 0 else 0
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on all memory systems"""
        status = {
            "memory_bridge": "healthy",
            "gemini_engine": "unknown",
            "mem0": "unknown",
            "qdrant": "unknown", 
            "postgres": "unknown"
        }
        
        # Test Gemini Engine
        try:
            if self.gemini_engine:
                gemini_health = await self.gemini_engine.health_check()
                if gemini_health.get("gemini") == "healthy":
                    status["gemini_engine"] = "healthy"
                else:
                    status["gemini_engine"] = "degraded"
            else:
                status["gemini_engine"] = "not_initialized"
        except Exception as e:
            status["gemini_engine"] = f"error: {str(e)}"
        
        # Test Mem0
        try:
            if self.mem0_client:
                # Try a simple search to test connection
                await self.search_memory(
                    "health check", 
                    limit=1,
                    user_id="health_check",
                    agent_id="system"
                )
                status["mem0"] = "healthy"
            else:
                status["mem0"] = "not_initialized"
        except Exception as e:
            status["mem0"] = f"error: {str(e)}"
        
        # Test Qdrant
        try:
            if self.qdrant_client:
                await asyncio.to_thread(self.qdrant_client.get_collections)
                status["qdrant"] = "healthy"
            else:
                status["qdrant"] = "not_initialized"
        except Exception as e:
            status["qdrant"] = f"error: {str(e)}"
        
        # Test PostgreSQL
        try:
            if self.postgres_pool:
                # Test connection when pool is implemented
                status["postgres"] = "healthy"
            else:
                status["postgres"] = "not_initialized"
        except Exception as e:
            status["postgres"] = f"error: {str(e)}"
        
        return status

# Convenience functions for global usage
_global_bridge = None

async def get_memory_bridge() -> ApexSigmaMemoryBridge:
    """Get or create global memory bridge instance"""
    global _global_bridge
    
    if _global_bridge is None:
        _global_bridge = ApexSigmaMemoryBridge()
        await _global_bridge.initialize()
    
    return _global_bridge

async def store_organizational_knowledge(content: str, category: str = "general") -> Dict[str, Any]:
    """Convenience function to store organizational knowledge"""
    bridge = await get_memory_bridge()
    return await bridge.store_memory(content, category=category)

async def search_organizational_memory(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Convenience function to search organizational memory"""
    bridge = await get_memory_bridge()
    return await bridge.search_memory(query, limit=limit)

if __name__ == "__main__":
    # Test the memory bridge
    async def test_memory_bridge():
        """Test memory bridge functionality"""
        print("Testing ApexSigma Memory Bridge...")
        
        try:
            bridge = ApexSigmaMemoryBridge()
            await bridge.initialize()
            
            # Test health check
            health = await bridge.health_check()
            print(f"Health Status: {health}")
            
            # Test memory operations
            result = await bridge.store_memory(
                "ApexSigma DevEnviro uses FastAPI for the web framework",
                category="technical_fact"
            )
            print(f"Store Result: {result}")
            
            # Test search
            search_results = await bridge.search_memory("FastAPI web framework")
            print(f"Search Results: {len(search_results)} memories found")
            
            # Performance stats
            stats = bridge.get_performance_stats()
            print(f"Performance: {stats}")
            
        except Exception as e:
            print(f"Test failed: {e}")
    
    # Run test
    asyncio.run(test_memory_bridge())