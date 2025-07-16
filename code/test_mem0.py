# \!/usr/bin/env python3
"""Test Mem0 integration with local Qdrant"""
import os


def test_mem0_setup():
    print("🧪 Testing Mem0 Setup...")

    try:
        from mem0 import Memory

        print("✅ Mem0 import successful")

        # Test basic connection
        config = {
            "vector_store": {
                "provider": "qdrant",
                "config": {"host": "localhost", "port": 6333, "collection_name": "apexsigma-memory"},
            }
        }

        memory = Memory.from_config(config)
        print("✅ Mem0 initialized with Qdrant backend")

        # Check for API keys (OpenAI or OpenRouter)
        openai_key = os.getenv("OPENAI_API_KEY")
        openrouter_key = os.getenv("OPENROUTER_API_KEY")
        
        if openrouter_key:
            print("✅ OPENROUTER_API_KEY configured")
        elif openai_key:
            print("✅ OPENAI_API_KEY configured")
        else:
            print("⚠️  No API key set (OPENAI_API_KEY or OPENROUTER_API_KEY)")
            print("   Set one to enable AI-powered memory operations")

        return True

    except Exception as e:
        print(f"❌ Mem0 setup failed: {e}")
        return False


if __name__ == "__main__":
    test_mem0_setup()
