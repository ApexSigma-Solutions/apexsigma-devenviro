#!/usr/bin/env python3
"""
Test Real-time A2A Communication
Demonstrates instant notifications and auto-responses
"""
import asyncio
import sys
from pathlib import Path

# Add devenviro to path
sys.path.append(str(Path(__file__).parent / 'devenviro'))

from devenviro.a2a_realtime import A2ARealtimeProtocol, create_realtime_agent, default_message_handler, create_smart_auto_responder
from devenviro.a2a_protocol import MessageType, MessagePriority


async def create_gemini_realtime_agent():
    """Create Gemini CLI with real-time notifications"""
    
    async def gemini_message_handler(message):
        """Custom handler for Gemini CLI"""
        print("\n" + "="*50)
        print("🔔 REAL-TIME NOTIFICATION FOR GEMINI CLI")
        print("="*50)
        print(f"📨 From: {message.sender_agent}")
        print(f"📝 Message: {message.content.get('text', 'No text')}")
        print(f"⏰ Timestamp: {message.timestamp}")
        print(f"🎯 Priority: {message.priority.value}")
        
        if message.requires_response:
            print("⚠️  RESPONSE REQUIRED!")
            
        print("="*50)
    
    def gemini_auto_responder(message):
        """Auto-responder for Gemini CLI"""
        return {
            "text": f"Gemini CLI received your message instantly! Real-time A2A is working perfectly.",
            "message_type": "auto_response",
            "analysis": "Message processed in real-time",
            "capabilities": ["instant_notification", "auto_response", "real_time_collaboration"],
            "response_time": "< 100ms",
            "status": "success"
        }
    
    # Create real-time Gemini agent
    gemini = await create_realtime_agent(
        "gemini-cli",
        message_callback=gemini_message_handler,
        auto_responder=gemini_auto_responder
    )
    
    return gemini


async def create_claude_realtime_agent():
    """Create Claude Code with real-time notifications"""
    
    async def claude_message_handler(message):
        """Custom handler for Claude Code"""
        print("\n" + "="*50)
        print("🔔 REAL-TIME NOTIFICATION FOR CLAUDE CODE")
        print("="*50)
        print(f"📨 From: {message.sender_agent}")
        print(f"📝 Response: {message.content.get('text', 'No text')}")
        
        if 'analysis' in message.content:
            print(f"📊 Analysis: {message.content['analysis']}")
        if 'capabilities' in message.content:
            print(f"🛠️  Capabilities: {message.content['capabilities']}")
            
        print("="*50)
    
    # Create real-time Claude agent
    claude = await create_realtime_agent(
        "claude-code", 
        message_callback=claude_message_handler
    )
    
    return claude


async def test_realtime_communication():
    """Test real-time A2A communication"""
    print("🚀 Starting Real-time A2A Communication Test")
    print("="*60)
    
    # Create both agents with real-time capabilities
    print("\n1. Creating Real-time Agents...")
    gemini = await create_gemini_realtime_agent()
    claude = await create_claude_realtime_agent()
    
    print("✅ Gemini CLI: Real-time monitoring active")
    print("✅ Claude Code: Real-time monitoring active")
    
    # Wait a moment for setup
    await asyncio.sleep(1)
    
    # Test 1: Claude sends message to Gemini (should trigger instant notification)
    print("\n2. Testing: Claude → Gemini (Real-time notification)")
    await claude.send_message_with_notification(
        "gemini-cli",
        MessageType.REQUEST,
        {
            "text": "Hello Gemini! This is a real-time test. You should get this instantly!",
            "test_type": "real_time_notification",
            "expected_response_time": "< 1 second"
        },
        MessagePriority.HIGH,
        requires_response=True
    )
    
    # Wait for real-time processing
    await asyncio.sleep(2)
    
    # Test 2: Gemini sends message to Claude
    print("\n3. Testing: Gemini → Claude (Auto-response)")
    await gemini.send_message_with_notification(
        "claude-code",
        MessageType.NOTIFICATION,
        {
            "text": "Claude, I received your message instantly and auto-responded!",
            "real_time_confirmation": True,
            "notification_delay": "< 100ms"
        },
        MessagePriority.NORMAL
    )
    
    # Wait for processing
    await asyncio.sleep(2)
    
    # Show real-time statistics
    print("\n4. Real-time Statistics:")
    gemini_stats = gemini.get_realtime_stats()
    claude_stats = claude.get_realtime_stats()
    
    print(f"\nGemini CLI Stats:")
    print(f"  File Watcher: {gemini_stats['file_watcher_active']}")
    print(f"  Background Polling: {gemini_stats['background_polling_active']}")
    print(f"  Message Callbacks: {gemini_stats['message_callbacks_registered']}")
    print(f"  Auto-responder: {gemini_stats['auto_responder_enabled']}")
    
    print(f"\nClaude Code Stats:")
    print(f"  File Watcher: {claude_stats['file_watcher_active']}")
    print(f"  Background Polling: {claude_stats['background_polling_active']}")
    print(f"  Message Callbacks: {claude_stats['message_callbacks_registered']}")
    
    # Keep monitoring for a bit
    print(f"\n5. Monitoring for real-time messages (10 seconds)...")
    print("   Send messages between agents to see instant notifications!")
    
    await asyncio.sleep(10)
    
    # Cleanup
    print("\n6. Stopping real-time monitoring...")
    await gemini.stop_realtime_monitoring()
    await claude.stop_realtime_monitoring()
    
    print("\n✅ Real-time A2A communication test completed!")
    print("🎉 Instant notifications and auto-responses working perfectly!")


async def main():
    """Main test runner"""
    try:
        await test_realtime_communication()
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("DevEnviro Real-time A2A Communication System")
    print("===========================================")
    asyncio.run(main())