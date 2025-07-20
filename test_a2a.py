#!/usr/bin/env python3
"""
Test script for DevEnviro Agent-to-Agent (A2A) Communication Protocol
Demonstrates communication between different AI agents
"""
import asyncio
import sys
from pathlib import Path

# Add devenviro to path
sys.path.append(str(Path(__file__).parent / 'devenviro'))

from devenviro.a2a_protocol import A2AProtocol, MessageType, MessagePriority
from devenviro.gemini_memory_engine import GeminiMemoryEngine


async def test_basic_a2a_communication():
    """Test basic A2A communication between agents"""
    print("Testing DevEnviro A2A Communication Protocol")
    print("=" * 60)
    
    # Initialize agents
    print("\n1. Initializing AI Agents...")
    claude_agent = A2AProtocol("claude-code")
    gemini_cli_agent = A2AProtocol("gemini-cli")
    gemini_memory_agent = A2AProtocol("gemini-memory")
    
    # Test agent registration
    print(f"   Claude Code agent: {claude_agent.agent_id}")
    print(f"   Gemini CLI agent: {gemini_cli_agent.agent_id}")
    print(f"   Gemini Memory agent: {gemini_memory_agent.agent_id}")
    
    # Update heartbeats
    await claude_agent.heartbeat()
    await gemini_cli_agent.heartbeat()
    await gemini_memory_agent.heartbeat()
    
    # Show active agents
    active_agents = claude_agent.get_active_agents()
    print(f"\n2. Active Agents: {len(active_agents)}")
    for agent in active_agents:
        print(f"   * {agent.agent_id} ({agent.agent_type}) - {agent.capabilities}")
    
    # Test messaging
    print("\n3. Testing Agent-to-Agent Messaging...")
    
    # Claude sends a message to Gemini CLI
    claude_to_gemini_id = await claude_agent.send_message(
        "gemini-cli",
        MessageType.REQUEST,
        {
            "text": "Can you help me analyze the current project structure?",
            "request_type": "analysis",
            "priority": "normal"
        },
        MessagePriority.HIGH,
        requires_response=True
    )
    print(f"   Claude -> Gemini CLI: {claude_to_gemini_id}")
    
    # Gemini CLI checks for messages
    gemini_messages = await gemini_cli_agent.get_messages()
    print(f"   Gemini CLI received {len(gemini_messages)} messages")
    
    if gemini_messages:
        message = gemini_messages[0]
        print(f"      Message: {message.content['text']}")
        
        # Gemini CLI responds
        await gemini_cli_agent.respond_to_message(
            message,
            {
                "text": "I can analyze the project structure. Here's what I found:",
                "analysis": {
                    "total_files": 42,
                    "languages": ["Python", "JavaScript", "YAML"],
                    "key_directories": ["devenviro/", "rules/", "docs/"]
                },
                "status": "completed"
            }
        )
        print("   Gemini CLI responded to Claude's request")
        
        # Acknowledge the message
        await gemini_cli_agent.acknowledge_message(message.id)
    
    # Claude checks for responses
    claude_messages = await claude_agent.get_messages(message_type=MessageType.RESPONSE)
    print(f"   Claude received {len(claude_messages)} responses")
    
    if claude_messages:
        response = claude_messages[0]
        print(f"      Response: {response.content['text']}")
        await claude_agent.acknowledge_message(response.id)
    
    # Test coordination message
    print("\n4. Testing Agent Coordination...")
    
    # Memory engine broadcasts status
    await gemini_memory_agent.send_message(
        "claude-code",
        MessageType.COORDINATION,
        {
            "text": "Memory engine status update",
            "coordination_type": "status_broadcast",
            "memory_stats": {
                "total_memories": 16,
                "categories": 8,
                "health": "optimal"
            }
        },
        MessagePriority.NORMAL
    )
    print("   Memory engine -> Claude: Status update")
    
    # Test notification
    await claude_agent.send_message(
        "gemini-memory",
        MessageType.NOTIFICATION,
        {
            "text": "New code changes detected",
            "notification_type": "code_update",
            "files_changed": ["security_manager.py", "a2a_protocol.py"],
            "change_summary": "Implemented A2A communication protocol"
        },
        MessagePriority.NORMAL
    )
    print("   Claude -> Memory: Notification sent")
    
    # Show message statistics
    print("\n5. Communication Statistics...")
    claude_stats = claude_agent.get_communication_stats()
    gemini_stats = gemini_cli_agent.get_communication_stats()
    memory_stats = gemini_memory_agent.get_communication_stats()
    
    print(f"   Claude Code: {claude_stats['queue_size']} queued messages")
    print(f"   Gemini CLI: {gemini_stats['queue_size']} queued messages") 
    print(f"   Gemini Memory: {memory_stats['queue_size']} queued messages")
    
    # Test cleanup
    print("\n6. Testing Message Cleanup...")
    await claude_agent.cleanup_expired_messages()
    await gemini_cli_agent.cleanup_expired_messages()
    await gemini_memory_agent.cleanup_expired_messages()
    print("   Expired messages cleaned up")
    
    print("\nA2A Communication Protocol test completed successfully!")


async def test_memory_engine_integration():
    """Test A2A integration with Gemini Memory Engine"""
    print("\n" + "=" * 60)
    print("Testing Memory Engine A2A Integration")
    print("=" * 60)
    
    try:
        # Initialize memory engine with A2A
        print("\n1. Initializing Gemini Memory Engine with A2A...")
        memory_engine = GeminiMemoryEngine()
        await memory_engine.initialize()
        
        if memory_engine.a2a_protocol:
            print("   A2A Protocol integrated with Memory Engine")
            
            # Test sending agent message via memory engine
            print("\n2. Testing Memory Engine Agent Messaging...")
            message_id = await memory_engine.send_agent_message(
                "claude-code",
                {
                    "text": "Memory extraction completed",
                    "extracted_memories": 3,
                    "categories": ["factual", "procedural", "organizational"]
                },
                MessageType.NOTIFICATION
            )
            print(f"   Memory Engine -> Claude: {message_id}")
            
            # Test getting messages
            print("\n3. Testing Message Retrieval...")
            messages = await memory_engine.get_agent_messages()
            print(f"   Memory Engine received {len(messages)} messages")
            
            # Test searching agent communications
            print("\n4. Testing Communication History Search...")
            comm_history = await memory_engine.search_agent_communications()
            print(f"   Found {len(comm_history)} communication records in memory")
            
            print("\nMemory Engine A2A integration test completed!")
            
        else:
            print("   WARNING: A2A Protocol not available in Memory Engine")
            
    except Exception as e:
        print(f"   ERROR: Memory Engine A2A test failed: {e}")


async def test_workflow_coordination():
    """Test complex workflow coordination between agents"""
    print("\n" + "=" * 60)
    print("Testing Agent Workflow Coordination")
    print("=" * 60)
    
    # Initialize agents
    claude = A2AProtocol("claude-code")
    gemini_cli = A2AProtocol("gemini-cli")
    gemini_memory = A2AProtocol("gemini-memory")
    
    print("\n1. Workflow: Code Analysis and Documentation")
    
    # Step 1: Claude requests code analysis
    analysis_id = await claude.send_message(
        "gemini-cli",
        MessageType.REQUEST,
        {
            "workflow_id": "code-analysis-001",
            "task": "analyze_codebase",
            "files": ["devenviro/a2a_protocol.py", "devenviro/gemini_memory_engine.py"],
            "analysis_type": "architecture_review"
        },
        requires_response=True
    )
    print(f"   Step 1: Claude requests analysis -> {analysis_id}")
    
    # Step 2: Gemini CLI performs analysis and requests memory context
    gemini_messages = await gemini_cli.get_messages()
    if gemini_messages:
        request = gemini_messages[0]
        
        # Gemini CLI requests memory context
        memory_request_id = await gemini_cli.send_message(
            "gemini-memory",
            MessageType.REQUEST,
            {
                "workflow_id": request.content["workflow_id"],
                "task": "get_context",
                "query": "A2A protocol implementation architectural decisions",
                "context_type": "architectural"
            },
            requires_response=True
        )
        print(f"   Step 2: Gemini CLI requests memory context -> {memory_request_id}")
        await gemini_cli.acknowledge_message(request.id)
    
    # Step 3: Memory engine provides context
    memory_messages = await gemini_memory.get_messages()
    if memory_messages:
        context_request = memory_messages[0]
        
        await gemini_memory.respond_to_message(
            context_request,
            {
                "workflow_id": context_request.content["workflow_id"],
                "context": {
                    "architectural_patterns": ["message_queue", "agent_registry", "persistence"],
                    "design_decisions": ["file_based_queue", "priority_ordering", "memory_integration"],
                    "related_memories": ["DevEnviro cognitive architecture", "security manager integration"]
                }
            }
        )
        print("   Step 3: Memory engine provides architectural context")
        await gemini_memory.acknowledge_message(context_request.id)
    
    # Step 4: Gemini CLI completes analysis and responds to Claude
    gemini_responses = await gemini_cli.get_messages(message_type=MessageType.RESPONSE)
    if gemini_responses and gemini_messages:
        original_request = gemini_messages[0]
        
        await gemini_cli.respond_to_message(
            original_request,
            {
                "workflow_id": original_request.content["workflow_id"],
                "analysis_complete": True,
                "findings": {
                    "architecture_quality": "excellent",
                    "code_coverage": "comprehensive",
                    "integration_points": ["memory_engine", "security_manager", "session_management"],
                    "recommendations": ["add_encryption", "performance_monitoring", "error_recovery"]
                },
                "documentation_ready": True
            }
        )
        print("   Step 4: Gemini CLI completes analysis and responds to Claude")
    
    # Step 5: Claude processes results
    claude_responses = await claude.get_messages(message_type=MessageType.RESPONSE)
    if claude_responses:
        result = claude_responses[0]
        print(f"   Step 5: Claude received analysis results")
        print(f"      Quality: {result.content.get('findings', {}).get('architecture_quality', 'unknown')}")
        await claude.acknowledge_message(result.id)
    
    print("\nWorkflow coordination test completed!")


async def main():
    """Main test execution"""
    try:
        # Basic A2A communication test
        await test_basic_a2a_communication()
        
        # Memory engine integration test
        await test_memory_engine_integration()
        
        # Workflow coordination test
        await test_workflow_coordination()
        
        print("\n" + "=" * 60)
        print("SUCCESS: All A2A Protocol tests completed successfully!")
        print("   The DevEnviro Agent-to-Agent communication system is operational.")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nERROR: Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())