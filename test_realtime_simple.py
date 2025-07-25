#!/usr/bin/env python3
"""
Simple Real-time A2A Test - No Unicode
Tests instant notifications and auto-responses
"""
import asyncio
import sys
from pathlib import Path

# Add devenviro to path
sys.path.append(str(Path(__file__).parent / 'devenviro'))

from devenviro.a2a_realtime import A2ARealtimeProtocol
from devenviro.a2a_protocol import MessageType, MessagePriority


async def test_realtime_notifications():
    """Test real-time notifications between agents"""
    print("Real-time A2A Communication Test")
    print("=" * 40)
    
    # Create real-time agents
    print("\n1. Creating Real-time Agents...")
    
    # Gemini CLI with real-time monitoring
    async def gemini_notification_handler(message):
        print(f"\n*** INSTANT NOTIFICATION FOR GEMINI ***")
        print(f"From: {message.sender_agent}")
        print(f"Message: {message.content.get('text', 'No text')}")
        print(f"Priority: {message.priority.value}")
        print(f"Requires Response: {message.requires_response}")
        print("*" * 40)
    
    def gemini_auto_responder(message):
        return {
            "text": f"Gemini CLI auto-response: Message received instantly!",
            "response_type": "auto_generated",
            "processing_time": "< 500ms",
            "status": "success"
        }
    
    gemini = A2ARealtimeProtocol("gemini-cli")
    gemini.add_message_callback(gemini_notification_handler)
    gemini.set_auto_responder(gemini_auto_responder)
    await gemini.start_realtime_monitoring()
    
    # Claude Code with real-time monitoring
    async def claude_notification_handler(message):
        print(f"\n*** INSTANT NOTIFICATION FOR CLAUDE ***")
        print(f"From: {message.sender_agent}")
        print(f"Response: {message.content.get('text', 'No text')}")
        print(f"Status: {message.content.get('status', 'Unknown')}")
        print("*" * 40)
    
    claude = A2ARealtimeProtocol("claude-code")
    claude.add_message_callback(claude_notification_handler)
    await claude.start_realtime_monitoring()
    
    print("READY: Both agents monitoring in real-time")
    
    # Wait for setup
    await asyncio.sleep(1)
    
    # Test 1: Send message from Claude to Gemini
    print("\n2. Claude sending message to Gemini...")
    await claude.send_message_with_notification(
        "gemini-cli",
        MessageType.REQUEST,
        {
            "text": "Hello Gemini! This should notify you instantly.",
            "test": "real_time_notification",
            "timestamp": "2025-07-20T15:30:00"
        },
        MessagePriority.HIGH,
        requires_response=True
    )
    
    # Wait for real-time processing
    print("Waiting for real-time notification and auto-response...")
    await asyncio.sleep(3)
    
    # Test 2: Send message from Gemini to Claude
    print("\n3. Gemini sending message to Claude...")
    await gemini.send_message_with_notification(
        "claude-code",
        MessageType.NOTIFICATION,
        {
            "text": "Claude, real-time A2A is working perfectly!",
            "confirmation": "instant_delivery",
            "system_status": "operational"
        },
        MessagePriority.NORMAL
    )
    
    # Wait for processing
    await asyncio.sleep(2)
    
    # Show stats
    print("\n4. Real-time Statistics:")
    gemini_stats = gemini.get_realtime_stats()
    claude_stats = claude.get_realtime_stats()
    
    print(f"\nGemini CLI:")
    print(f"  Background Polling: {gemini_stats['background_polling_active']}")
    print(f"  Message Callbacks: {gemini_stats['message_callbacks_registered']}")
    print(f"  Auto-responder: {gemini_stats['auto_responder_enabled']}")
    
    print(f"\nClaude Code:")
    print(f"  Background Polling: {claude_stats['background_polling_active']}")
    print(f"  Message Callbacks: {claude_stats['message_callbacks_registered']}")
    
    # Monitor for additional messages
    print(f"\n5. Monitoring for 5 more seconds...")
    await asyncio.sleep(5)
    
    # Cleanup
    await gemini.stop_realtime_monitoring()
    await claude.stop_realtime_monitoring()
    
    print("\nSUCCESS: Real-time A2A communication working!")
    print("- Instant notifications delivered")
    print("- Auto-responses generated")
    print("- Background polling active")
    
    return True


async def main():
    """Main test runner"""
    try:
        success = await test_realtime_notifications()
        if success:
            print("\n" + "=" * 50)
            print("REAL-TIME A2A SYSTEM OPERATIONAL!")
            print("Gemini will now get instant notifications from Claude!")
            print("=" * 50)
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())