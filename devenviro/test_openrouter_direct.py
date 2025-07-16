#!/usr/bin/env python3
"""Direct test of OpenRouter API"""
import os
import requests


def test_openrouter_direct():
    """Test OpenRouter API directly"""
    print("Testing OpenRouter API directly...")
    
    try:
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            print("[ERROR] OPENROUTER_API_KEY not found")
            return False
            
        print("[SUCCESS] API key found")
        
        # Test with a simple completion
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "anthropic/claude-3.5-sonnet",
            "messages": [
                {"role": "user", "content": "Say hello"}
            ],
            "max_tokens": 10
        }
        
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )
        
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("[SUCCESS] OpenRouter API working")
            print(f"Response: {result['choices'][0]['message']['content']}")
            return True
        else:
            print(f"[ERROR] API failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"[ERROR] OpenRouter test failed: {e}")
        return False


if __name__ == "__main__":
    test_openrouter_direct()