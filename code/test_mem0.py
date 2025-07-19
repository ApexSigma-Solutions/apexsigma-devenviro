#!/usr/bin/env python3
"""Test Mem0 integration with local Qdrant"""
import os
from devenviro.terminal_output import print_success, print_error, print_warning, safe_print


def test_mem0_setup():
    safe_print("[TEST] Testing Mem0 Setup...")

    try:
        from mem0 import Memory

        print_success("Mem0 import successful")

        # Test basic connection
        config = {
            "vector_store": {
                "provider": "qdrant",
                "config": {"host": "localhost", "port": 6333, "collection_name": "apexsigma-memory"},
            }
        }

        memory = Memory.from_config(config)
        print_success("Mem0 initialized with Qdrant backend")

        # Check for OpenAI API key
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print_warning("OPENAI_API_KEY not set")
            print("   Set it to enable memory operations")
        else:
            print_success("OPENAI_API_KEY configured")

        return True

    except Exception as e:
        print_error(f"Mem0 setup failed: {e}")
        return False


if __name__ == "__main__":
    test_mem0_setup()
