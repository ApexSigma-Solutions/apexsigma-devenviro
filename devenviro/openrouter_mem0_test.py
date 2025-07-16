#!/usr/bin/env python3
"""Test Mem0 with OpenRouter API integration"""
import os
from typing import Optional


def create_openrouter_config() -> dict:
    """Create mem0 config for OpenRouter API"""
    openrouter_key = os.getenv("OPENROUTER_API_KEY")
    
    if not openrouter_key:
        raise ValueError("OPENROUTER_API_KEY environment variable not set")
    
    config = {
        "llm": {
            "provider": "openai",
            "config": {
                "model": "anthropic/claude-3.5-sonnet",
                "api_key": openrouter_key
            }
        },
        "embedder": {
            "provider": "openai", 
            "config": {
                "model": "text-embedding-3-small",
                "api_key": openrouter_key
            }
        },
        "vector_store": {
            "provider": "qdrant",
            "config": {
                "host": "localhost", 
                "port": 6333, 
                "collection_name": "apexsigma-memory"
            }
        }
    }
    return config


def test_openrouter_mem0():
    """Test mem0 with OpenRouter configuration"""
    print("Testing Mem0 with OpenRouter...")
    
    try:
        # Check API key
        openrouter_key = os.getenv("OPENROUTER_API_KEY")
        if not openrouter_key:
            print("[ERROR] OPENROUTER_API_KEY not set")
            return False
            
        print("[SUCCESS] OPENROUTER_API_KEY found")
        
        # Import mem0
        from mem0 import Memory
        print("[SUCCESS] Mem0 import successful")
        
        # Create config
        config = create_openrouter_config()
        print("[SUCCESS] OpenRouter config created")
        
        # Initialize memory
        memory = Memory.from_config(config)
        print("[SUCCESS] Mem0 initialized with OpenRouter backend")
        
        # Test basic memory operation
        test_message = "This is a test memory using OpenRouter API"
        result = memory.add(test_message, user_id="test-user")
        print(f"[SUCCESS] Memory added: {result}")
        
        # Test search
        search_results = memory.search("test memory", user_id="test-user")
        print(f"[SUCCESS] Search results: {len(search_results)} memories found")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] OpenRouter mem0 test failed: {e}")
        return False


if __name__ == "__main__":
    test_openrouter_mem0()