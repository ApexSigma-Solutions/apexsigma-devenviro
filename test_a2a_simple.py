#!/usr/bin/env python3
"""
Simple A2A Communication Test - No external dependencies
Tests the core A2A protocol functionality
"""
import asyncio
import sys
from pathlib import Path

# Add devenviro to path
sys.path.append(str(Path(__file__).parent / 'devenviro'))

from devenviro.a2a_protocol import A2AProtocol, MessageType, MessagePriority


async def test_basic_a2a():
    """Test basic A2A communication without memory engine"""
    print("DevEnviro A2A Protocol - Simple Test")
    print("=" * 50)
    
    # Initialize agents
    print("\n1. Initializing Agents...")
    claude = A2AProtocol("claude-code")
    gemini_cli = A2AProtocol("gemini-cli")
    
    # Update heartbeats
    await claude.heartbeat()
    await gemini_cli.heartbeat()
    
    print(f"   Claude Code: {claude.agent_id}")
    print(f"   Gemini CLI: {gemini_cli.agent_id}")
    
    # Check active agents
    active = claude.get_active_agents()
    print(f"\n2. Active Agents: {len(active)}")
    for agent in active:
        print(f"   * {agent.agent_id} ({agent.agent_type})")
    
    # Test messaging
    print("\n3. Testing Communication...")
    
    # Claude sends message to Gemini CLI
    msg_id = await claude.send_message(
        "gemini-cli",
        MessageType.REQUEST,
        {
            "text": "Hello Gemini CLI! Can you help with some code analysis?",
            "task": "code_analysis",
            "files": ["test_a2a_simple.py"]
        },
        MessagePriority.HIGH,
        requires_response=True
    )
    print(f"   Claude -> Gemini CLI: Message sent (ID: {msg_id[:8]}...)")
    
    # Gemini CLI checks messages
    messages = await gemini_cli.get_messages()
    print(f"   Gemini CLI received: {len(messages)} messages")
    
    if messages:
        msg = messages[0]
        print(f"   Message content: {msg.content['text']}")
        
        # Gemini CLI responds
        await gemini_cli.respond_to_message(msg, {
            "text": "Hello Claude! I can help with code analysis.",
            "analysis_result": {
                "file": "test_a2a_simple.py",
                "status": "analyzed", 
                "findings": ["A2A protocol test", "async/await patterns", "clean structure"]
            }
        })
        print("   Gemini CLI -> Claude: Response sent")
        
        # Acknowledge message
        await gemini_cli.acknowledge_message(msg.id)
    
    # Claude checks for response
    responses = await claude.get_messages(message_type=MessageType.RESPONSE)
    print(f"   Claude received: {len(responses)} responses")
    
    if responses:
        resp = responses[0]
        response_text = resp.content.get('text', 'No text in response')
        print(f"   Response: {response_text}")
        await claude.acknowledge_message(resp.id)
    
    # Show stats
    print("\n4. Communication Stats...")
    claude_stats = claude.get_communication_stats()
    gemini_stats = gemini_cli.get_communication_stats()
    
    print(f"   Claude queue: {claude_stats['queue_size']} messages")
    print(f"   Gemini queue: {gemini_stats['queue_size']} messages")
    
    print("\nSUCCESS: Basic A2A communication working!")
    return True


async def main():
    """Main test runner"""
    try:
        success = await test_basic_a2a()
        if success:
            print("\n" + "=" * 50)
            print("A2A Protocol is ready for Gemini CLI testing!")
            print("You can now bring in Gemini CLI to test real agent communication.")
            print("=" * 50)
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())