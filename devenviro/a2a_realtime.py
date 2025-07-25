#!/usr/bin/env python3
"""
DevEnviro A2A Real-time Notification System
Provides instant notifications when messages arrive
"""
import asyncio
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime
import threading

# File system watching
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    # Create dummy class when watchdog not available
    class FileSystemEventHandler:
        pass
    class Observer:
        pass

from .a2a_protocol import A2AProtocol, MessageType, MessagePriority, A2AMessage
from .terminal_output import safe_print, print_success, print_error, print_info, print_warning


class MessageNotificationHandler(FileSystemEventHandler):
    """File system event handler for instant message notifications"""
    
    def __init__(self, agent_id: str, callback: Callable[[A2AMessage], None]):
        self.agent_id = agent_id
        self.callback = callback
        self.processed_files = set()
        
    def on_created(self, event):
        """Handle new message file creation"""
        if event.is_directory:
            return
            
        if event.src_path.endswith('.json') and event.src_path not in self.processed_files:
            self.processed_files.add(event.src_path)
            asyncio.create_task(self._process_new_message(event.src_path))
    
    async def _process_new_message(self, file_path: str):
        """Process newly arrived message"""
        try:
            # Small delay to ensure file is fully written
            await asyncio.sleep(0.1)
            
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Convert back to A2AMessage object
            data['message_type'] = MessageType(data['message_type'])
            data['priority'] = MessagePriority(data['priority'])
            message = A2AMessage(**data)
            
            # Trigger callback
            if self.callback:
                await self.callback(message)
                
        except Exception as e:
            print_error(f"Failed to process new message {file_path}: {e}")


class A2ARealtimeProtocol(A2AProtocol):
    """Enhanced A2A Protocol with real-time notifications"""
    
    def __init__(self, agent_id: str, devenviro_root: str = None):
        super().__init__(agent_id, devenviro_root)
        
        # Real-time components
        self.observer = None
        self.message_handler = None
        self.message_callbacks = []
        self.auto_responder = None
        self.background_tasks = []
        
        # Real-time configuration
        self.realtime_config = {
            "enable_file_watching": WATCHDOG_AVAILABLE,
            "enable_background_polling": True,
            "poll_interval_ms": 500,
            "enable_auto_response": False,
            "notification_sound": False,
            "log_all_notifications": True
        }
        
        print_success(f"A2A Real-time Protocol initialized for: {self.agent_id}")
    
    def add_message_callback(self, callback: Callable[[A2AMessage], None]):
        """Add callback function to be called when new messages arrive"""
        self.message_callbacks.append(callback)
        print_info(f"Added message callback for {self.agent_id}")
    
    def set_auto_responder(self, responder: Callable[[A2AMessage], Dict[str, Any]]):
        """Set automatic response function for incoming messages"""
        self.auto_responder = responder
        print_info(f"Auto-responder enabled for {self.agent_id}")
    
    async def start_realtime_monitoring(self):
        """Start real-time message monitoring"""
        print_info(f"Starting real-time monitoring for {self.agent_id}")
        
        # Start file system watcher
        if self.realtime_config["enable_file_watching"] and WATCHDOG_AVAILABLE:
            await self._start_file_watcher()
        
        # Start background polling as fallback
        if self.realtime_config["enable_background_polling"]:
            await self._start_background_polling()
        
        print_success(f"Real-time monitoring active for {self.agent_id}")
    
    async def _start_file_watcher(self):
        """Start file system watcher for instant notifications"""
        try:
            self.message_handler = MessageNotificationHandler(
                self.agent_id, 
                self._on_new_message
            )
            
            self.observer = Observer()
            self.observer.schedule(
                self.message_handler, 
                str(self.agent_queue_dir), 
                recursive=False
            )
            self.observer.start()
            
            print_info(f"File watcher started for {self.agent_queue_dir}")
            
        except Exception as e:
            print_error(f"Failed to start file watcher: {e}")
    
    async def _start_background_polling(self):
        """Start background polling as fallback notification method"""
        async def polling_worker():
            last_check = time.time()
            
            while True:
                try:
                    # Check for new messages since last poll
                    messages = await self.get_messages(unread_only=True)
                    
                    for message in messages:
                        # Check if message is newer than last check
                        msg_time = datetime.fromisoformat(message.timestamp).timestamp()
                        if msg_time > last_check:
                            await self._on_new_message(message)
                    
                    last_check = time.time()
                    
                except Exception as e:
                    print_error(f"Background polling error: {e}")
                
                # Wait for next poll
                await asyncio.sleep(self.realtime_config["poll_interval_ms"] / 1000)
        
        # Start background task
        task = asyncio.create_task(polling_worker())
        self.background_tasks.append(task)
        print_info(f"Background polling started (interval: {self.realtime_config['poll_interval_ms']}ms)")
    
    async def _on_new_message(self, message: A2AMessage):
        """Handle new message arrival"""
        try:
            # Log notification
            if self.realtime_config["log_all_notifications"]:
                print_info(f"📥 REAL-TIME: New message from {message.sender_agent}")
                print_info(f"   Type: {message.message_type.value.upper()}")
                print_info(f"   Priority: {message.priority.value}")
                print_info(f"   Content: {message.content.get('text', 'No text')[:100]}...")
            
            # Trigger all callbacks
            for callback in self.message_callbacks:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(message)
                    else:
                        callback(message)
                except Exception as e:
                    print_error(f"Message callback error: {e}")
            
            # Auto-respond if enabled
            if self.auto_responder and message.requires_response:
                await self._auto_respond(message)
                
        except Exception as e:
            print_error(f"Error handling new message: {e}")
    
    async def _auto_respond(self, message: A2AMessage):
        """Automatically respond to messages"""
        try:
            response_content = self.auto_responder(message)
            if response_content:
                await self.respond_to_message(message, response_content)
                print_info(f"🤖 AUTO-RESPONSE sent to {message.sender_agent}")
        except Exception as e:
            print_error(f"Auto-response failed: {e}")
    
    async def stop_realtime_monitoring(self):
        """Stop real-time monitoring"""
        # Stop file watcher
        if self.observer:
            self.observer.stop()
            self.observer.join()
            print_info("File watcher stopped")
        
        # Cancel background tasks
        for task in self.background_tasks:
            task.cancel()
        
        if self.background_tasks:
            await asyncio.gather(*self.background_tasks, return_exceptions=True)
        
        print_info(f"Real-time monitoring stopped for {self.agent_id}")
    
    async def send_message_with_notification(self, target_agent: str, msg_type: MessageType,
                                           content: Dict[str, Any], 
                                           priority: MessagePriority = MessagePriority.NORMAL,
                                           requires_response: bool = False,
                                           conversation_id: str = None) -> str:
        """Send message and trigger real-time notification on target"""
        message_id = await self.send_message(
            target_agent, msg_type, content, priority, 
            requires_response, conversation_id
        )
        
        # Enhanced logging for sent messages
        print_success(f"📤 SENT: Message to {target_agent} (ID: {message_id[:8]}...)")
        print_info(f"   Priority: {priority.value}, Response Required: {requires_response}")
        
        return message_id
    
    def get_realtime_stats(self) -> Dict[str, Any]:
        """Get real-time monitoring statistics"""
        return {
            "agent_id": self.agent_id,
            "file_watcher_active": self.observer is not None and self.observer.is_alive(),
            "background_polling_active": len(self.background_tasks) > 0,
            "message_callbacks_registered": len(self.message_callbacks),
            "auto_responder_enabled": self.auto_responder is not None,
            "realtime_config": self.realtime_config
        }


# Convenience functions for easy setup
async def create_realtime_agent(agent_id: str, 
                               message_callback: Callable[[A2AMessage], None] = None,
                               auto_responder: Callable[[A2AMessage], Dict[str, Any]] = None) -> A2ARealtimeProtocol:
    """Create and start a real-time A2A agent"""
    agent = A2ARealtimeProtocol(agent_id)
    
    if message_callback:
        agent.add_message_callback(message_callback)
    
    if auto_responder:
        agent.set_auto_responder(auto_responder)
    
    await agent.start_realtime_monitoring()
    return agent


# Default message handlers
async def default_message_handler(message: A2AMessage):
    """Default handler that prints message details"""
    print_success(f"\n🔔 NEW MESSAGE NOTIFICATION")
    print_info(f"From: {message.sender_agent}")
    print_info(f"Type: {message.message_type.value}")
    print_info(f"Priority: {message.priority.value}")
    print_info(f"Content: {message.content.get('text', 'No text content')}")
    
    if message.requires_response:
        print_warning("⚠️  This message requires a response!")


def create_smart_auto_responder(agent_id: str) -> Callable[[A2AMessage], Dict[str, Any]]:
    """Create a smart auto-responder based on agent type"""
    
    def auto_responder(message: A2AMessage) -> Dict[str, Any]:
        """Smart auto-response based on message content and agent capabilities"""
        
        # Common responses based on agent type
        if "claude" in agent_id.lower():
            return {
                "text": f"Claude Code received your message. I'll analyze and provide strategic guidance.",
                "agent_type": "claude-code",
                "capabilities": ["strategic_planning", "architecture", "code_review"],
                "status": "processing",
                "auto_response": True
            }
        
        elif "gemini-cli" in agent_id.lower():
            return {
                "text": f"Gemini CLI ready to assist! I can help with development and analysis.",
                "agent_type": "gemini-cli", 
                "capabilities": ["development", "analysis", "debugging"],
                "status": "ready",
                "auto_response": True
            }
        
        elif "gemini-memory" in agent_id.lower():
            return {
                "text": f"Gemini Memory Engine acknowledged. I can provide context and store this interaction.",
                "agent_type": "gemini-memory",
                "capabilities": ["memory_storage", "context_retrieval", "search"],
                "status": "stored",
                "auto_response": True
            }
        
        else:
            return {
                "text": f"Agent {agent_id} received your message and is processing it.",
                "agent_type": agent_id,
                "status": "acknowledged",
                "auto_response": True
            }
    
    return auto_responder


if __name__ == "__main__":
    # Example usage
    async def test_realtime():
        # Create real-time agent with callbacks
        agent = await create_realtime_agent(
            "test-agent",
            message_callback=default_message_handler,
            auto_responder=create_smart_auto_responder("test-agent")
        )
        
        print("Real-time agent running... Press Ctrl+C to stop")
        
        try:
            # Keep running
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            await agent.stop_realtime_monitoring()
            print("Real-time monitoring stopped")
    
    asyncio.run(test_realtime())