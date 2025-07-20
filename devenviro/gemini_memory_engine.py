#!/usr/bin/env python3
"""
ApexSigma DevEnviro Native Gemini Memory Engine
Direct integration with Gemini 2.5 Flash for intelligent memory operations
"""

import os
import json
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
import hashlib
import uuid

# Google AI imports
try:
    import google.generativeai as genai
    from google.generativeai.types import HarmCategory, HarmBlockThreshold
except ImportError:
    genai = None

# Vector operations
try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
except ImportError:
    QdrantClient = None

# A2A Protocol imports
try:
    from .a2a_protocol import A2AProtocol, MessageType, MessagePriority, A2AMessage
    A2A_AVAILABLE = True
except ImportError:
    A2A_AVAILABLE = False

# Database operations
try:
    import asyncpg
except ImportError:
    asyncpg = None

from dotenv import load_dotenv
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GeminiMemoryError(Exception):
    """Custom exception for Gemini memory operations"""
    pass

class GeminiMemoryEngine:
    """
    Native Gemini 2.5 Flash Memory Engine
    Provides intelligent memory extraction, categorization, and retrieval
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize Gemini memory engine"""
        self.config = self._load_config(config_path)
        
        # Initialize components
        self.gemini_client = None
        self.qdrant_client = None
        self.postgres_pool = None
        self.a2a_protocol = None
        
        # Memory categories and importance thresholds
        self.memory_categories = {
            "factual": "Concrete facts, data, and specific information",
            "procedural": "How-to instructions, processes, and workflows", 
            "episodic": "Events, interactions, and experiences",
            "semantic": "Concepts, relationships, and general knowledge",
            "organizational": "Company-specific patterns, standards, and decisions",
            "architectural": "System design, technical decisions, and patterns",
            "temporal": "Time-sensitive information and deadlines",
            "inter_agent": "Agent-to-agent messages, requests, and coordination data"
        }
        
        # Performance tracking
        self.operation_stats = {
            "extractions": 0,
            "searches": 0,
            "stores": 0,
            "errors": 0,
            "total_response_time": 0.0
        }
    
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load configuration from environment"""
        env_file = Path(__file__).parent.parent / "config" / "secrets" / ".env"
        if env_file.exists():
            load_dotenv(env_file)
        
        config = {
            "gemini": {
                "api_key": os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"),
                "model": "gemini-2.5-flash",
                "temperature": 0.1,  # Low temperature for consistent memory operations
                "top_p": 0.8,
                "top_k": 40,
                "max_output_tokens": 8192
            },
            "qdrant": {
                "host": "localhost",
                "port": 6333,
                "collection_name": "gemini-memory",
                "vector_size": 768  # We'll generate our own embeddings
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
        """Initialize all components of the memory engine"""
        try:
            logger.info("Initializing Gemini Memory Engine...")
            
            # Initialize Gemini
            await self._initialize_gemini()
            
            # Initialize Qdrant
            await self._initialize_qdrant()
            
            # Initialize PostgreSQL (optional)
            await self._initialize_postgres()
            
            # Initialize A2A Protocol for agent communication
            await self._initialize_a2a()
            
            logger.info("Gemini Memory Engine initialization complete")
            return True
            
        except Exception as e:
            logger.error(f"Gemini Memory Engine initialization failed: {e}")
            raise GeminiMemoryError(f"Initialization failed: {e}")
    
    async def _initialize_gemini(self):
        """Initialize Gemini 2.5 Flash"""
        if not genai:
            raise GeminiMemoryError("google-generativeai package not installed")
        
        if not self.config["gemini"]["api_key"]:
            raise GeminiMemoryError("No Gemini API key configured (GEMINI_API_KEY or GOOGLE_API_KEY)")
        
        try:
            # Configure Gemini
            genai.configure(api_key=self.config["gemini"]["api_key"])
            
            # Initialize the model with safety settings
            generation_config = {
                "temperature": self.config["gemini"]["temperature"],
                "top_p": self.config["gemini"]["top_p"],
                "top_k": self.config["gemini"]["top_k"],
                "max_output_tokens": self.config["gemini"]["max_output_tokens"],
            }
            
            safety_settings = {
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            }
            
            self.gemini_client = genai.GenerativeModel(
                model_name=self.config["gemini"]["model"],
                generation_config=generation_config,
                safety_settings=safety_settings
            )
            
            # Test the connection
            response = await asyncio.to_thread(
                self.gemini_client.generate_content,
                "Test connection. Respond with 'OK'."
            )
            
            if "OK" in response.text.upper():
                logger.info("Gemini 2.5 Flash client initialized successfully")
            else:
                logger.warning("Gemini client initialized but test response unexpected")
                
        except Exception as e:
            logger.error(f"Gemini initialization failed: {e}")
            raise GeminiMemoryError(f"Gemini setup failed: {e}")
    
    async def _initialize_qdrant(self):
        """Initialize Qdrant for vector storage"""
        if not QdrantClient:
            logger.warning("Qdrant client not available - vector storage disabled")
            return
        
        try:
            self.qdrant_client = QdrantClient(
                host=self.config["qdrant"]["host"],
                port=self.config["qdrant"]["port"]
            )
            
            # Create collection if not exists
            collection_name = self.config["qdrant"]["collection_name"]
            try:
                collections = await asyncio.to_thread(self.qdrant_client.get_collections)
                collection_exists = any(c.name == collection_name for c in collections.collections)
                
                if not collection_exists:
                    await asyncio.to_thread(
                        self.qdrant_client.create_collection,
                        collection_name=collection_name,
                        vectors_config=VectorParams(
                            size=self.config["qdrant"]["vector_size"], 
                            distance=Distance.COSINE
                        )
                    )
                    logger.info(f"Created Qdrant collection: {collection_name}")
                
            except Exception as e:
                logger.warning(f"Qdrant collection setup issue: {e}")
            
            logger.info("Qdrant client initialized successfully")
            
        except Exception as e:
            logger.warning(f"Qdrant initialization failed: {e}")
            self.qdrant_client = None
    
    async def _initialize_postgres(self):
        """Initialize PostgreSQL for metadata (optional)"""
        logger.info("PostgreSQL initialization deferred")
        # We'll implement this when needed
    
    async def extract_memory(self, content: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Extract and categorize memories from content using Gemini 2.5 Flash
        """
        start_time = datetime.now()
        
        try:
            if not self.gemini_client:
                raise GeminiMemoryError("Gemini client not initialized")
            
            # Create extraction prompt
            extraction_prompt = self._create_extraction_prompt(content, context)
            
            # Generate extraction using Gemini
            response = await asyncio.to_thread(
                self.gemini_client.generate_content,
                extraction_prompt
            )
            
            # Parse the response
            extraction_result = self._parse_extraction_response(response.text)
            
            # Track performance
            self.operation_stats["extractions"] += 1
            response_time = (datetime.now() - start_time).total_seconds()
            self.operation_stats["total_response_time"] += response_time
            
            logger.info(f"Memory extraction completed in {response_time:.3f}s")
            
            return {
                "success": True,
                "extraction": extraction_result,
                "response_time_ms": response_time * 1000,
                "model": self.config["gemini"]["model"]
            }
            
        except Exception as e:
            self.operation_stats["errors"] += 1
            logger.error(f"Memory extraction failed: {e}")
            raise GeminiMemoryError(f"Failed to extract memory: {e}")
    
    def _create_extraction_prompt(self, content: str, context: Optional[Dict[str, Any]]) -> str:
        """Create a prompt for memory extraction"""
        
        context_info = ""
        if context:
            context_info = f"\\nContext: {json.dumps(context, indent=2)}"
        
        categories_list = "\\n".join([f"- {cat}: {desc}" for cat, desc in self.memory_categories.items()])
        
        prompt = f"""You are an intelligent memory extraction system for ApexSigma DevEnviro, a cognitive collaboration platform. 

Analyze the following content and extract important memories that should be stored for future reference.

CONTENT TO ANALYZE:
{content}
{context_info}

MEMORY CATEGORIES:
{categories_list}

EXTRACTION REQUIREMENTS:
1. Extract 1-5 key memories from the content
2. For each memory, provide:
   - memory_text: The actual information to remember (concise but complete)
   - category: One of the categories above
   - importance: Score from 1-10 (10 = critical organizational knowledge)
   - tags: 3-5 relevant keywords
   - relationships: Connected entities or concepts
   - decay_hours: How many hours this memory should remain relevant (24-8760)

3. Focus on:
   - Actionable information
   - Decisions made
   - Technical specifications
   - Process improvements
   - Problem solutions
   - Organizational patterns

4. Ignore:
   - Temporary debugging info
   - Casual conversation
   - Already well-known facts

RESPOND ONLY WITH VALID JSON:
{{
  "memories": [
    {{
      "memory_text": "string",
      "category": "string", 
      "importance": number,
      "tags": ["string", "string"],
      "relationships": ["entity1", "entity2"],
      "decay_hours": number
    }}
  ]
}}"""
        
        return prompt
    
    def _parse_extraction_response(self, response_text: str) -> Dict[str, Any]:
        """Parse Gemini's extraction response"""
        try:
            import re
            # Use regex to extract the first JSON code block (handles ```json, ```python, etc.)
            code_block_match = re.search(r"```(?:\w+)?\s*([\s\S]*?)\s*```", response_text)
            if code_block_match:
                cleaned_response = code_block_match.group(1).strip()
            else:
                cleaned_response = response_text.strip()
            
            # Parse JSON
            result = json.loads(cleaned_response.strip())
            
            # Validate structure
            if "memories" not in result:
                raise ValueError("No 'memories' key in response")
            
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse extraction response: {e}")
            logger.error(f"Response text: {response_text}")
            # Return result with explicit error for debugging
            return {
                "memories": [],
                "error": f"JSONDecodeError: {e}. Raw response: {response_text}"
            }
        except Exception as e:
            logger.error(f"Error parsing extraction: {e}")
            return {
                "memories": [],
                "error": f"Exception: {e}"
            }
    
    async def store_memory(
        self, 
        memory_text: str, 
        category: str = "general",
        importance: int = 5,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Store a memory in the vector database
        """
        start_time = datetime.now()
        
        try:
            if not self.qdrant_client:
                raise GeminiMemoryError("Qdrant client not initialized")
            
            # Generate vector embedding for the memory
            vector = await self._generate_embedding(memory_text)
            
            # Create memory ID
            memory_id = str(uuid.uuid4())
            
            # Prepare metadata
            memory_metadata = {
                "text": memory_text,
                "category": category,
                "importance": importance,
                "tags": tags or [],
                "organization_id": self.config["organization"]["id"],
                "timestamp": datetime.now().isoformat(),
                "model": self.config["gemini"]["model"]
            }
            
            if metadata:
                memory_metadata.update(metadata)
            
            # Store in Qdrant
            point = PointStruct(
                id=memory_id,
                vector=vector,
                payload=memory_metadata
            )
            
            await asyncio.to_thread(
                self.qdrant_client.upsert,
                collection_name=self.config["qdrant"]["collection_name"],
                points=[point]
            )
            
            # Track performance
            self.operation_stats["stores"] += 1
            response_time = (datetime.now() - start_time).total_seconds()
            self.operation_stats["total_response_time"] += response_time
            
            logger.info(f"Memory stored successfully in {response_time:.3f}s")
            
            return {
                "success": True,
                "memory_id": memory_id,
                "response_time_ms": response_time * 1000,
                "metadata": memory_metadata
            }
            
        except Exception as e:
            self.operation_stats["errors"] += 1
            logger.error(f"Memory storage failed: {e}")
            raise GeminiMemoryError(f"Failed to store memory: {e}")
    
    async def search_memory(
        self,
        query: str,
        limit: int = 10,
        category_filter: Optional[str] = None,
        importance_threshold: int = 1
    ) -> List[Dict[str, Any]]:
        """
        Search memories using vector similarity and intelligent ranking
        """
        start_time = datetime.now()
        
        try:
            if not self.qdrant_client:
                raise GeminiMemoryError("Qdrant client not initialized")
            
            # Generate query vector
            query_vector = await self._generate_embedding(query)
            
            # Build filter conditions
            filter_conditions = []
            
            if category_filter:
                filter_conditions.append(
                    FieldCondition(
                        key="category",
                        match=MatchValue(value=category_filter)
                    )
                )
            
            if importance_threshold > 1:
                filter_conditions.append(
                    FieldCondition(
                        key="importance",
                        range={"gte": importance_threshold}
                    )
                )
            
            # Add organizational filter
            filter_conditions.append(
                FieldCondition(
                    key="organization_id",
                    match=MatchValue(value=self.config["organization"]["id"])
                )
            )
            
            # Search in Qdrant
            search_filter = Filter(must=filter_conditions) if filter_conditions else None
            
            results = await asyncio.to_thread(
                self.qdrant_client.search,
                collection_name=self.config["qdrant"]["collection_name"],
                query_vector=query_vector,
                query_filter=search_filter,
                limit=limit * 2  # Get more results for re-ranking
            )
            
            # Re-rank results using Gemini for better contextual relevance
            ranked_results = await self._rerank_results(query, results, limit)
            
            # Track performance
            self.operation_stats["searches"] += 1
            response_time = (datetime.now() - start_time).total_seconds()
            self.operation_stats["total_response_time"] += response_time
            
            logger.info(f"Memory search completed in {response_time:.3f}s, found {len(ranked_results)} results")
            
            return ranked_results
            
        except Exception as e:
            self.operation_stats["errors"] += 1
            logger.error(f"Memory search failed: {e}")
            raise GeminiMemoryError(f"Failed to search memory: {e}")
    
    async def _generate_embedding(self, text: str) -> List[float]:
        """
        Generate vector embedding for text using a simple approach
        Since we're using Gemini for intelligence, we'll create a simple hash-based vector
        In a production system, you'd use a proper embedding model
        """
        # Simple embedding generation using text characteristics
        # This is a placeholder - in production, use proper embeddings
        
        # Create a hash-based vector
        text_hash = hashlib.md5(text.lower().encode()).hexdigest()
        
        # Convert to vector
        vector = []
        for i in range(0, len(text_hash), 2):
            hex_pair = text_hash[i:i+2]
            vector.append(int(hex_pair, 16) / 255.0)  # Normalize to 0-1
        
        # Pad or truncate to desired size
        target_size = self.config["qdrant"]["vector_size"]
        while len(vector) < target_size:
            vector.extend(vector[:min(len(vector), target_size - len(vector))])
        
        vector = vector[:target_size]
        
        # Normalize to unit length for cosine similarity
        norm = sum(x ** 2 for x in vector) ** 0.5
        if norm > 0:
            vector = [x / norm for x in vector]
        
        return vector
    
    async def _rerank_results(self, query: str, results: List, limit: int) -> List[Dict[str, Any]]:
        """Use Gemini to re-rank search results for better relevance"""
        if not results or not self.gemini_client:
            return [self._format_search_result(r) for r in results[:limit]]
        
        try:
            # Prepare results for re-ranking
            results_text = []
            for i, result in enumerate(results):
                results_text.append(f"{i}: {result.payload.get('text', '')}")
            
            # Create re-ranking prompt
            rerank_prompt = f"""You are re-ranking search results for relevance to a query.

QUERY: {query}

RESULTS:
{chr(10).join(results_text[:20])}  # Limit to avoid token overflow

Rank these results by relevance to the query. Consider:
1. Direct relevance to the query
2. Importance score in the metadata
3. Recency of the information
4. Organizational context

Respond with only the result numbers in order of relevance (most relevant first):
Example: 3,1,7,2,5"""
            
            response = await asyncio.to_thread(
                self.gemini_client.generate_content,
                rerank_prompt
            )
            
            # Parse ranking
            ranking_text = response.text.strip()
            indices = [int(x.strip()) for x in ranking_text.split(',') if x.strip().isdigit()]
            
            # Apply ranking
            reranked_results = []
            for idx in indices:
                if idx < len(results):
                    reranked_results.append(self._format_search_result(results[idx]))
                if len(reranked_results) >= limit:
                    break
            
            # Add remaining results if needed
            used_indices = set(indices[:len(reranked_results)])
            for i, result in enumerate(results):
                if i not in used_indices and len(reranked_results) < limit:
                    reranked_results.append(self._format_search_result(result))
            
            return reranked_results[:limit]
            
        except Exception as e:
            logger.warning(f"Re-ranking failed, using original order: {e}")
            return [self._format_search_result(r) for r in results[:limit]]
    
    def _format_search_result(self, result) -> Dict[str, Any]:
        """Format a Qdrant search result"""
        return {
            "id": result.id,
            "text": result.payload.get("text", ""),
            "category": result.payload.get("category", "unknown"),
            "importance": result.payload.get("importance", 0),
            "tags": result.payload.get("tags", []),
            "score": result.score,
            "timestamp": result.payload.get("timestamp", ""),
            "metadata": {k: v for k, v in result.payload.items() 
                        if k not in ["text", "category", "importance", "tags", "timestamp"]}
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on all components"""
        status = {
            "gemini_memory_engine": "healthy",
            "gemini": "unknown",
            "qdrant": "unknown"
        }
        
        # Test Gemini
        try:
            if self.gemini_client:
                response = await asyncio.to_thread(
                    self.gemini_client.generate_content,
                    "Health check. Respond with 'HEALTHY'."
                )
                if "HEALTHY" in response.text.upper():
                    status["gemini"] = "healthy"
                else:
                    status["gemini"] = "responding_unusually"
            else:
                status["gemini"] = "not_initialized"
        except Exception as e:
            status["gemini"] = f"error: {str(e)}"
        
        # Test Qdrant
        try:
            if self.qdrant_client:
                await asyncio.to_thread(self.qdrant_client.get_collections)
                status["qdrant"] = "healthy"
            else:
                status["qdrant"] = "not_initialized"
        except Exception as e:
            status["qdrant"] = f"error: {str(e)}"
        
        return status
    
    async def _initialize_a2a(self):
        """Initialize A2A Protocol for agent communication"""
        if not A2A_AVAILABLE:
            logger.warning("A2A Protocol not available - agent communication disabled")
            return
        
        try:
            self.a2a_protocol = A2AProtocol("gemini-memory", str(self.config_path.parent if self.config_path else Path.cwd()))
            logger.info("A2A Protocol initialized for agent communication")
        except Exception as e:
            logger.warning(f"A2A Protocol initialization failed: {e}")
            self.a2a_protocol = None
    
    async def send_agent_message(self, target_agent: str, content: Dict[str, Any], 
                               msg_type: MessageType = MessageType.NOTIFICATION,
                               priority: MessagePriority = MessagePriority.NORMAL) -> str:
        """Send message to another agent via A2A protocol"""
        if not self.a2a_protocol:
            logger.warning("A2A Protocol not initialized - cannot send agent message")
            return ""
        
        try:
            message_id = await self.a2a_protocol.send_message(
                target_agent, msg_type, content, priority
            )
            
            # Store the message in memory for persistence
            await self.store_memory({
                "id": str(uuid.uuid4()),
                "content": f"Sent A2A message to {target_agent}: {content.get('text', str(content))}",
                "category": "inter_agent",
                "importance": 0.7,
                "tags": ["a2a", "outbound", target_agent],
                "metadata": {
                    "message_id": message_id,
                    "target_agent": target_agent,
                    "message_type": msg_type.value,
                    "priority": priority.value
                }
            })
            
            return message_id
            
        except Exception as e:
            logger.error(f"Failed to send agent message: {e}")
            return ""
    
    async def get_agent_messages(self, unread_only: bool = True) -> List[A2AMessage]:
        """Get messages for this agent from A2A protocol"""
        if not self.a2a_protocol:
            logger.warning("A2A Protocol not initialized - cannot get agent messages")
            return []
        
        try:
            messages = await self.a2a_protocol.get_messages(unread_only)
            
            # Store received messages in memory for persistence
            for message in messages:
                if not message.acknowledged:  # Only store new messages
                    await self.store_memory({
                        "id": str(uuid.uuid4()),
                        "content": f"Received A2A message from {message.sender_agent}: {message.content.get('text', str(message.content))}",
                        "category": "inter_agent",
                        "importance": 0.8,
                        "tags": ["a2a", "inbound", message.sender_agent],
                        "metadata": {
                            "message_id": message.id,
                            "sender_agent": message.sender_agent,
                            "message_type": message.message_type.value,
                            "priority": message.priority.value,
                            "timestamp": message.timestamp
                        }
                    })
            
            return messages
            
        except Exception as e:
            logger.error(f"Failed to get agent messages: {e}")
            return []
    
    async def acknowledge_agent_message(self, message_id: str):
        """Acknowledge receipt of an agent message"""
        if not self.a2a_protocol:
            return
        
        try:
            await self.a2a_protocol.acknowledge_message(message_id)
        except Exception as e:
            logger.error(f"Failed to acknowledge message {message_id}: {e}")
    
    async def respond_to_agent_message(self, original_message: A2AMessage, response_content: Dict[str, Any]):
        """Send response to an agent message"""
        if not self.a2a_protocol:
            return
        
        try:
            await self.a2a_protocol.respond_to_message(original_message, response_content)
            
            # Store the response in memory
            await self.store_memory({
                "id": str(uuid.uuid4()),
                "content": f"Responded to A2A message from {original_message.sender_agent}: {response_content.get('text', str(response_content))}",
                "category": "inter_agent", 
                "importance": 0.7,
                "tags": ["a2a", "response", original_message.sender_agent],
                "metadata": {
                    "original_message_id": original_message.id,
                    "target_agent": original_message.sender_agent,
                    "conversation_id": original_message.conversation_id
                }
            })
            
        except Exception as e:
            logger.error(f"Failed to respond to agent message: {e}")
    
    async def broadcast_agent_status(self, status_info: Dict[str, Any]):
        """Broadcast status update to all active agents"""
        if not self.a2a_protocol:
            return
        
        try:
            active_agents = self.a2a_protocol.get_active_agents()
            
            for agent in active_agents:
                await self.send_agent_message(
                    agent.agent_id,
                    {
                        "status_update": status_info,
                        "timestamp": datetime.now().isoformat(),
                        "from": "gemini-memory"
                    },
                    MessageType.STATUS,
                    MessagePriority.LOW
                )
                
        except Exception as e:
            logger.error(f"Failed to broadcast agent status: {e}")
    
    async def search_agent_communications(self, agent_id: str = None, 
                                        message_type: str = None,
                                        days_back: int = 7) -> List[Dict[str, Any]]:
        """Search for agent communication history in memory"""
        try:
            # Build search query
            search_terms = ["A2A", "agent message"]
            if agent_id:
                search_terms.append(agent_id)
            if message_type:
                search_terms.append(message_type)
            
            query = " ".join(search_terms)
            
            # Search with filters
            cutoff_date = datetime.now() - timedelta(days=days_back)
            filters = {
                "category": "inter_agent",
                "min_timestamp": cutoff_date.isoformat()
            }
            
            results = await self.search_memories(query, filters=filters, limit=50)
            return results
            
        except Exception as e:
            logger.error(f"Failed to search agent communications: {e}")
            return []
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        total_ops = sum([
            self.operation_stats["extractions"],
            self.operation_stats["searches"], 
            self.operation_stats["stores"]
        ])
        
        avg_response_time = (
            self.operation_stats["total_response_time"] / total_ops 
            if total_ops > 0 else 0
        )
        
        return {
            "total_operations": total_ops,
            "extractions": self.operation_stats["extractions"],
            "searches": self.operation_stats["searches"],
            "stores": self.operation_stats["stores"],
            "errors": self.operation_stats["errors"],
            "average_response_time_ms": avg_response_time * 1000,
            "error_rate": self.operation_stats["errors"] / total_ops if total_ops > 0 else 0,
            "model": self.config["gemini"]["model"]
        }

# Convenience functions for global usage
_global_engine = None

async def get_gemini_memory_engine() -> GeminiMemoryEngine:
    """Get or create global Gemini memory engine instance"""
    global _global_engine
    
    if _global_engine is None:
        _global_engine = GeminiMemoryEngine()
        await _global_engine.initialize()
    
    return _global_engine

async def extract_and_store_memory(content: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Convenience function to extract and store memories"""
    engine = await get_gemini_memory_engine()
    
    # Extract memories
    extraction = await engine.extract_memory(content, context)
    
    # Store each extracted memory
    stored_memories = []
    if extraction["success"]:
        for memory in extraction["extraction"]["memories"]:
            store_result = await engine.store_memory(
                memory_text=memory["memory_text"],
                category=memory["category"],
                importance=memory["importance"],
                tags=memory.get("tags", []),
                metadata={
                    "relationships": memory.get("relationships", []),
                    "decay_hours": memory.get("decay_hours", 168)  # Default 1 week
                }
            )
            stored_memories.append(store_result)
    
    return {
        "extraction": extraction,
        "stored_memories": stored_memories
    }

async def search_organizational_memory(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Convenience function to search organizational memory"""
    engine = await get_gemini_memory_engine()
    return await engine.search_memory(query, limit=limit)

# Session Continuity via Enhanced Episodic Memory
async def capture_session_episodic_memory(session_summary: str) -> Dict[str, Any]:
    """Capture session as episodic memory with chronological context"""
    timestamp = datetime.now()
    session_id = f"session-{timestamp.strftime('%Y%m%d-%H%M%S')}"
    
    # Create episodic memory extraction focusing on continuity
    episodic_content = f"""SESSION EPISODE - {timestamp.strftime('%Y-%m-%d %H:%M:%S')}

{session_summary}

This session episode should be remembered for future continuity, including:
- Key decisions and their context
- Technical work completed
- Problems solved and approaches used
- Important discoveries or insights
- Next steps and open tasks
- User working patterns and preferences
"""
    
    context = {
        "episode_type": "work_session",
        "session_id": session_id,
        "chronological_timestamp": timestamp.isoformat(),
        "continuity_purpose": "session_flow"
    }
    
    return await extract_and_store_memory(episodic_content, context)

async def get_chronological_session_context(hours_back: int = 72) -> List[Dict[str, Any]]:
    """Get recent episodic memories in chronological order for context restoration"""
    engine = await get_gemini_memory_engine()
    
    # Search for recent episodic memories (sessions + other episodes)
    recent_episodes = await engine.search_memory(
        query="session episode work decisions context continuity",
        limit=20,
        category_filter="episodic",
        importance_threshold=5
    )
    
    # Filter by timestamp and sort chronologically
    cutoff_time = datetime.now() - timedelta(hours=hours_back)
    
    chronological_context = []
    for episode in recent_episodes:
        timestamp_str = episode.get("metadata", {}).get("chronological_timestamp") or episode.get("timestamp", "")
        
        if timestamp_str:
            try:
                episode_time = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
                episode_time = episode_time.replace(tzinfo=None)  # Remove timezone for comparison
                
                if episode_time >= cutoff_time:
                    chronological_context.append({
                        "timestamp": episode_time,
                        "memory": episode,
                        "hours_ago": (datetime.now() - episode_time).total_seconds() / 3600
                    })
            except Exception:
                continue
    
    # Sort by timestamp (most recent first)
    chronological_context.sort(key=lambda x: x["timestamp"], reverse=True)
    
    return chronological_context

async def restore_session_continuity_brief() -> str:
    """Generate brief continuity context for session initialization"""
    context = await get_chronological_session_context(hours_back=72)
    
    if not context:
        return "No recent session context available for continuity."
    
    brief = ["=== RECENT SESSION CONTINUITY ===\n"]
    
    for i, item in enumerate(context[:3]):  # Last 3 episodes
        hours_ago = item["hours_ago"]
        memory = item["memory"]
        
        time_desc = f"{int(hours_ago)}h ago" if hours_ago < 24 else f"{int(hours_ago/24)}d ago"
        brief.append(f"[{time_desc}] {memory.get('text', '')[:120]}...")
        
        if i < 2:  # Add separator except for last item
            brief.append("")
    
    brief.append(f"\n[INFO] {len(context)} episodes available for context")
    return "\n".join(brief)

if __name__ == "__main__":
    # Test the Gemini memory engine
    async def test_gemini_memory_engine():
        """Test Gemini memory engine functionality"""
        print("Testing Gemini Memory Engine...")
        
        try:
            engine = GeminiMemoryEngine()
            await engine.initialize()
            
            # Test health check
            health = await engine.health_check()
            print(f"Health Status: {health}")
            
            # Test memory extraction
            test_content = """
            ApexSigma DevEnviro is implementing a cognitive collaboration architecture.
            We decided to use Gemini 2.5 Flash for memory operations because it provides
            better cost efficiency and performance compared to OpenAI alternatives.
            The system uses Qdrant for vector storage and implements hierarchical context loading.
            """
            
            extraction = await engine.extract_memory(test_content)
            print(f"Extraction Result: {extraction}")
            
            # Test memory storage
            if extraction["success"] and extraction["extraction"]["memories"]:
                memory = extraction["extraction"]["memories"][0]
                store_result = await engine.store_memory(
                    memory_text=memory["memory_text"],
                    category=memory["category"],
                    importance=memory["importance"]
                )
                print(f"Store Result: {store_result}")
                
                # Test memory search
                search_results = await engine.search_memory("Gemini 2.5 Flash memory")
                print(f"Search Results: {len(search_results)} memories found")
                for result in search_results:
                    print(f"  - {result['text'][:100]}...")
            
            # Performance stats
            stats = engine.get_performance_stats()
            print(f"Performance: {stats}")
            
        except Exception as e:
            print(f"Test failed: {e}")
    
    # Run test
    asyncio.run(test_gemini_memory_engine())