#!/usr/bin/env python3
"""Test basic memory functionality without AI features"""
import os


def test_basic_memory_storage():
    """Test memory storage using simple memory service"""
    print("Testing basic memory storage...")
    
    try:
        import requests
        
        # Test memory service health
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            print("[SUCCESS] Memory service is healthy")
        else:
            print(f"[ERROR] Memory service unhealthy: {response.status_code}")
            return False
            
        # Add a test memory
        memory_data = {
            "message": "Test memory - cognitive system functional",
            "user_id": "system-test",
            "metadata": {
                "type": "system_test",
                "timestamp": "2025-07-16",
                "status": "operational"
            }
        }
        
        response = requests.post(
            "http://localhost:8000/memory/add",
            json=memory_data
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"[SUCCESS] Memory added: {result['memory_id']}")
        else:
            print(f"[ERROR] Failed to add memory: {response.status_code}")
            return False
            
        # Search for memories
        search_data = {
            "query": "cognitive system",
            "user_id": "system-test",
            "limit": 5
        }
        
        response = requests.post(
            "http://localhost:8000/memory/search",
            json=search_data
        )
        
        if response.status_code == 200:
            results = response.json()
            print(f"[SUCCESS] Found {results['count']} memories")
        else:
            print(f"[ERROR] Search failed: {response.status_code}")
            return False
            
        # Get memory stats
        response = requests.get("http://localhost:8000/memory/stats")
        if response.status_code == 200:
            stats = response.json()
            print(f"[SUCCESS] Total memories: {stats['total_memories']}, Users: {stats['unique_users']}")
        else:
            print(f"[ERROR] Stats failed: {response.status_code}")
            return False
            
        return True
        
    except Exception as e:
        print(f"[ERROR] Basic memory test failed: {e}")
        return False


if __name__ == "__main__":
    success = test_basic_memory_storage()
    if success:
        print("[SUCCESS] Basic memory system is operational")
    else:
        print("[ERROR] Basic memory system has issues")