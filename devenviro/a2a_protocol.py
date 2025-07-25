#!/usr/bin/env python3
"""
DevEnviro Agent-to-Agent (A2A) Communication Protocol
Enables secure, persistent communication between AI agents
"""
import asyncio
import json
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from dataclasses import dataclass, asdict
from pathlib import Path

from .terminal_output import safe_print, print_success, print_error, print_info, print_warning


class MessageType(Enum):
    """A2A message types"""
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    COORDINATION = "coordination"
    HANDOFF = "handoff"
    STATUS = "status"
    ERROR = "error"


class MessagePriority(Enum):
    """Message priority levels"""
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4
    BACKGROUND = 5


class AgentStatus(Enum):
    """Agent status states"""
    ACTIVE = "active"
    IDLE = "idle"
    BUSY = "busy"
    OFFLINE = "offline"
    ERROR = "error"


@dataclass
class A2AMessage:
    """Agent-to-Agent message structure"""
    id: str
    sender_agent: str
    target_agent: str
    message_type: MessageType
    priority: MessagePriority
    content: Dict[str, Any]
    timestamp: str
    expires_at: Optional[str] = None
    conversation_id: Optional[str] = None
    requires_response: bool = False
    response_timeout: int = 300  # seconds
    delivery_attempts: int = 0
    max_delivery_attempts: int = 3
    delivered: bool = False
    acknowledged: bool = False

    @classmethod
    def create(cls, sender: str, target: str, msg_type: MessageType, 
               content: Dict[str, Any], priority: MessagePriority = MessagePriority.NORMAL,
               requires_response: bool = False, expires_in_minutes: int = 60,
               conversation_id: str = None) -> 'A2AMessage':
        """Create a new A2A message"""
        now = datetime.now()
        expires_at = (now + timedelta(minutes=expires_in_minutes)).isoformat() if expires_in_minutes else None
        
        return cls(
            id=str(uuid.uuid4()),
            sender_agent=sender,
            target_agent=target,
            message_type=msg_type,
            priority=priority,
            content=content,
            timestamp=now.isoformat(),
            expires_at=expires_at,
            conversation_id=conversation_id,
            requires_response=requires_response
        )


@dataclass
class AgentRegistration:
    """Agent registration information"""
    agent_id: str
    agent_type: str  # claude-code, gemini-cli, gemini-memory, etc.
    capabilities: List[str]
    status: AgentStatus
    last_heartbeat: str
    process_id: Optional[int] = None
    version: str = "1.0.0"
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class A2AProtocol:
    """Agent-to-Agent Communication Protocol Manager"""
    
    def __init__(self, agent_id: str, devenviro_root: str = None):
        self.agent_id = agent_id
        self.devenviro_root = Path(devenviro_root) if devenviro_root else Path.cwd() / '.devenviro'
        
        # A2A directories
        self.a2a_dir = self.devenviro_root / 'a2a'
        self.messages_dir = self.a2a_dir / 'messages'
        self.agents_dir = self.a2a_dir / 'agents'
        self.queues_dir = self.a2a_dir / 'queues'
        
        # Ensure A2A infrastructure exists
        for directory in [self.a2a_dir, self.messages_dir, self.agents_dir, self.queues_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        # Agent-specific paths
        self.agent_queue_dir = self.queues_dir / self.agent_id
        self.agent_queue_dir.mkdir(exist_ok=True)
        
        # Configuration
        self.config_file = self.a2a_dir / 'a2a_config.json'
        self.registry_file = self.agents_dir / 'agent_registry.json'
        
        # Load configuration
        self.config = self._load_config()
        self.agent_registry = self._load_agent_registry()
        
        # Register this agent
        self._register_agent()
        
        print_success(f"A2A Protocol initialized for agent: {self.agent_id}")

    def _load_config(self) -> Dict:
        """Load A2A configuration"""
        default_config = {
            "version": "1.0.0",
            "message_retention_days": 7,
            "heartbeat_interval_seconds": 30,
            "message_poll_interval_seconds": 2,
            "max_message_size_bytes": 1024 * 1024,  # 1MB
            "enable_encryption": False,
            "enable_compression": True,
            "agent_timeout_minutes": 5,
            "conversation_timeout_hours": 24,
            "auto_cleanup_enabled": True
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    # Merge with defaults
                    for key, value in default_config.items():
                        if key not in config:
                            config[key] = value
                    return config
            except Exception as e:
                print_error(f"Failed to load A2A config: {e}")
        
        # Save default config
        self._save_config(default_config)
        return default_config

    def _save_config(self, config: Dict):
        """Save A2A configuration"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print_error(f"Failed to save A2A config: {e}")

    def _load_agent_registry(self) -> Dict[str, AgentRegistration]:
        """Load agent registry"""
        if not self.registry_file.exists():
            return {}
        
        try:
            with open(self.registry_file, 'r') as f:
                data = json.load(f)
                registry = {}
                for agent_id, agent_data in data.items():
                    # Convert string back to enum
                    agent_data['status'] = AgentStatus(agent_data['status'])
                    registry[agent_id] = AgentRegistration(**agent_data)
                return registry
        except Exception as e:
            print_error(f"Failed to load agent registry: {e}")
            return {}

    def _save_agent_registry(self):
        """Save agent registry"""
        try:
            data = {}
            for agent_id, registration in self.agent_registry.items():
                reg_dict = asdict(registration)
                # Convert enum to string
                reg_dict['status'] = registration.status.value
                data[agent_id] = reg_dict
            
            with open(self.registry_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print_error(f"Failed to save agent registry: {e}")

    def _register_agent(self):
        """Register this agent in the registry"""
        agent_type = self._determine_agent_type()
        capabilities = self._determine_capabilities()
        
        registration = AgentRegistration(
            agent_id=self.agent_id,
            agent_type=agent_type,
            capabilities=capabilities,
            status=AgentStatus.ACTIVE,
            last_heartbeat=datetime.now().isoformat(),
            metadata={
                "startup_time": datetime.now().isoformat(),
                "devenviro_root": str(self.devenviro_root)
            }
        )
        
        self.agent_registry[self.agent_id] = registration
        self._save_agent_registry()
        
        print_info(f"Registered agent: {self.agent_id} ({agent_type})")

    def _determine_agent_type(self) -> str:
        """Determine agent type based on agent_id"""
        if "claude" in self.agent_id.lower():
            return "claude-code"
        elif "gemini-cli" in self.agent_id.lower():
            return "gemini-cli"
        elif "gemini-memory" in self.agent_id.lower():
            return "gemini-memory"
        elif "gemini-code" in self.agent_id.lower():
            return "gemini-code-assist"
        else:
            return "unknown"

    def _determine_capabilities(self) -> List[str]:
        """Determine agent capabilities based on type"""
        agent_type = self._determine_agent_type()
        
        capability_map = {
            "claude-code": ["code_generation", "file_editing", "analysis", "documentation"],
            "gemini-cli": ["chat", "code_assistance", "analysis", "debugging"],
            "gemini-memory": ["memory_management", "context_extraction", "search", "persistence"],
            "gemini-code-assist": ["code_completion", "suggestion", "refactoring", "optimization"],
            "unknown": ["general"]
        }
        
        return capability_map.get(agent_type, ["general"])

    async def send_message(self, target_agent: str, msg_type: MessageType, 
                          content: Dict[str, Any], priority: MessagePriority = MessagePriority.NORMAL,
                          requires_response: bool = False, conversation_id: str = None) -> str:
        """Send message to another agent"""
        try:
            # Create message
            message = A2AMessage.create(
                sender=self.agent_id,
                target=target_agent,
                msg_type=msg_type,
                content=content,
                priority=priority,
                requires_response=requires_response
            )
            
            if conversation_id:
                message.conversation_id = conversation_id
            
            # Save to target agent's queue
            await self._deliver_message(message)
            
            # Log the send
            self._log_message_activity("SENT", message)
            
            return message.id
            
        except Exception as e:
            print_error(f"Failed to send message to {target_agent}: {e}")
            return ""

    async def _deliver_message(self, message: A2AMessage):
        """Deliver message to target agent's queue"""
        target_queue_dir = self.queues_dir / message.target_agent
        target_queue_dir.mkdir(exist_ok=True)
        
        # Priority-based filename for ordering
        priority_prefix = f"{message.priority.value:02d}"
        timestamp_prefix = message.timestamp.replace(":", "").replace("-", "").replace(".", "")
        filename = f"{priority_prefix}_{timestamp_prefix}_{message.id}.json"
        
        message_file = target_queue_dir / filename
        
        # Convert message to JSON-serializable dict
        message_dict = asdict(message)
        message_dict['message_type'] = message.message_type.value
        message_dict['priority'] = message.priority.value
        
        with open(message_file, 'w') as f:
            json.dump(message_dict, f, indent=2)
        
        message.delivered = True
        print_info(f"Message delivered to {message.target_agent}: {message.id}")

    async def get_messages(self, unread_only: bool = True, 
                          message_type: MessageType = None) -> List[A2AMessage]:
        """Get messages for this agent"""
        messages = []
        
        try:
            # Get all message files in agent's queue
            message_files = sorted(self.agent_queue_dir.glob("*.json"))
            
            for message_file in message_files:
                try:
                    with open(message_file, 'r') as f:
                        data = json.load(f)
                    
                    # Convert string enums back to enum objects
                    data['message_type'] = MessageType(data['message_type'])
                    data['priority'] = MessagePriority(data['priority'])
                    
                    message = A2AMessage(**data)
                    
                    # Filter by read status and type
                    if unread_only and message.acknowledged:
                        continue
                    
                    if message_type and message.message_type != message_type:
                        continue
                    
                    # Check if message has expired
                    if message.expires_at:
                        expire_time = datetime.fromisoformat(message.expires_at)
                        if datetime.now() > expire_time:
                            # Remove expired message
                            message_file.unlink()
                            continue
                    
                    messages.append(message)
                    
                except Exception as e:
                    print_error(f"Failed to load message {message_file}: {e}")
                    
        except Exception as e:
            print_error(f"Failed to get messages: {e}")
        
        return messages

    async def acknowledge_message(self, message_id: str):
        """Acknowledge receipt of a message"""
        try:
            message_files = list(self.agent_queue_dir.glob(f"*_{message_id}.json"))
            
            for message_file in message_files:
                with open(message_file, 'r') as f:
                    data = json.load(f)
                
                data['acknowledged'] = True
                
                with open(message_file, 'w') as f:
                    json.dump(data, f, indent=2)
                
                self._log_message_activity("ACKNOWLEDGED", A2AMessage(**data))
                break
                
        except Exception as e:
            print_error(f"Failed to acknowledge message {message_id}: {e}")

    async def respond_to_message(self, original_message: A2AMessage, 
                               response_content: Dict[str, Any]):
        """Send response to a message"""
        if not original_message.requires_response:
            print_warning(f"Message {original_message.id} does not require response")
            return
        
        response_message = A2AMessage.create(
            sender=self.agent_id,
            target=original_message.sender_agent,
            msg_type=MessageType.RESPONSE,
            content={
                "original_message_id": original_message.id,
                "response": response_content
            },
            conversation_id=original_message.conversation_id
        )
        
        await self._deliver_message(response_message)
        self._log_message_activity("RESPONDED", response_message)

    def get_active_agents(self) -> List[AgentRegistration]:
        """Get list of currently active agents"""
        active_agents = []
        current_time = datetime.now()
        timeout_minutes = self.config.get("agent_timeout_minutes", 5)
        
        for agent_id, registration in self.agent_registry.items():
            if agent_id == self.agent_id:
                continue  # Skip self
                
            last_heartbeat = datetime.fromisoformat(registration.last_heartbeat)
            if current_time - last_heartbeat < timedelta(minutes=timeout_minutes):
                active_agents.append(registration)
        
        return active_agents

    async def heartbeat(self):
        """Update agent heartbeat"""
        if self.agent_id in self.agent_registry:
            self.agent_registry[self.agent_id].last_heartbeat = datetime.now().isoformat()
            self.agent_registry[self.agent_id].status = AgentStatus.ACTIVE
            self._save_agent_registry()

    def _log_message_activity(self, action: str, message: A2AMessage):
        """Log message activity for debugging"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "agent_id": self.agent_id,
            "message_id": message.id,
            "target_agent": message.target_agent,
            "message_type": message.message_type.value,
            "priority": message.priority.value
        }
        
        log_file = self.a2a_dir / "a2a_activity.log"
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + "\n")

    async def cleanup_expired_messages(self):
        """Clean up expired messages and old logs"""
        if not self.config.get("auto_cleanup_enabled", True):
            return
        
        retention_days = self.config.get("message_retention_days", 7)
        cutoff_time = datetime.now() - timedelta(days=retention_days)
        
        # Clean up messages in all agent queues
        for agent_queue in self.queues_dir.iterdir():
            if agent_queue.is_dir():
                for message_file in agent_queue.glob("*.json"):
                    try:
                        file_time = datetime.fromtimestamp(message_file.stat().st_mtime)
                        if file_time < cutoff_time:
                            message_file.unlink()
                    except Exception as e:
                        print_error(f"Failed to cleanup message {message_file}: {e}")

    def get_communication_stats(self) -> Dict[str, Any]:
        """Get A2A communication statistics"""
        stats = {
            "agent_id": self.agent_id,
            "active_agents": len(self.get_active_agents()),
            "total_registered_agents": len(self.agent_registry),
            "queue_size": len(list(self.agent_queue_dir.glob("*.json"))),
            "last_heartbeat": self.agent_registry.get(self.agent_id, {}).last_heartbeat if hasattr(self.agent_registry.get(self.agent_id, {}), 'last_heartbeat') else None
        }
        
        return stats


# Convenience functions for common operations
async def quick_send(sender_id: str, target_id: str, content: str, 
                    msg_type: MessageType = MessageType.NOTIFICATION) -> str:
    """Quick send text message between agents"""
    protocol = A2AProtocol(sender_id)
    return await protocol.send_message(target_id, msg_type, {"text": content})


async def request_response(sender_id: str, target_id: str, request: Dict[str, Any], 
                          timeout_seconds: int = 60) -> Optional[Dict[str, Any]]:
    """Send request and wait for response"""
    protocol = A2AProtocol(sender_id)
    
    # Send request
    conversation_id = str(uuid.uuid4())
    message_id = await protocol.send_message(
        target_id, MessageType.REQUEST, request, 
        requires_response=True, conversation_id=conversation_id
    )
    
    # Wait for response
    start_time = time.time()
    while time.time() - start_time < timeout_seconds:
        messages = await protocol.get_messages(unread_only=True, message_type=MessageType.RESPONSE)
        
        for message in messages:
            if (message.conversation_id == conversation_id and 
                message.content.get("original_message_id") == message_id):
                await protocol.acknowledge_message(message.id)
                return message.content.get("response")
        
        await asyncio.sleep(1)
    
    return None  # Timeout


if __name__ == "__main__":
    # Example usage
    async def main():
        # Initialize protocol for this agent
        protocol = A2AProtocol("claude-code-example")
        
        # Send a test message
        await protocol.send_message(
            "gemini-cli", 
            MessageType.NOTIFICATION,
            {"text": "Hello from Claude Code!", "timestamp": datetime.now().isoformat()}
        )
        
        # Check for messages
        messages = await protocol.get_messages()
        print(f"Received {len(messages)} messages")
        
        # Show stats
        stats = protocol.get_communication_stats()
        print(f"Communication stats: {stats}")
    
    asyncio.run(main())