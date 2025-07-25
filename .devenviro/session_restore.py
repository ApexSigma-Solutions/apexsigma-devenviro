#!/usr/bin/env python3
"""
Session Restoration System for DevEnviro
Triggered by user greetings to restore previous context
"""
import sys
import re
from pathlib import Path
sys.path.append('.')

from devenviro.terminal_output import safe_print, print_success, print_error, print_info
from .chat_persistence import ChatPersistenceManager, ChatSession


class SessionRestorer:
    """Handles session context restoration on user greetings"""
    
    GREETING_PATTERNS = [
        r'\b(good\s+)?morning\b',
        r'\b(good\s+)?afternoon\b', 
        r'\b(good\s+)?evening\b',
        r'\bhello\b',
        r'\bhi\b',
        r'\bhey\b',
        r'\bamnesia\b',
        r'\bstart\s+fresh\b',
        r'\bback\s+again\b'
    ]
    
    def __init__(self):
        self.manager = ChatPersistenceManager()
        
    def detect_greeting(self, user_message: str) -> bool:
        """Detect if user message contains a greeting"""
        user_message_lower = user_message.lower()
        
        for pattern in self.GREETING_PATTERNS:
            if re.search(pattern, user_message_lower):
                return True
        return False
    
    def should_restore_context(self, user_message: str) -> bool:
        """Determine if we should restore previous session context"""
        # Always restore on greetings
        if self.detect_greeting(user_message):
            return True
            
        # Also restore if user mentions specific keywords
        keywords = ['previous', 'last session', 'continue', 'resume', 'where were we']
        user_message_lower = user_message.lower()
        
        for keyword in keywords:
            if keyword in user_message_lower:
                return True
                
        return False
    
    def restore_session_context(self) -> dict:
        """Restore and return previous session context"""
        try:
            context = self.manager.restore_session_context()
            
            if context.get("message") == "No previous sessions found":
                print_info("No previous sessions to restore")
                return {"restored": False, "message": "No previous sessions found"}
            
            # Format restoration message
            prev_session = context.get("previous_session", "unknown")
            total_exchanges = context.get("total_exchanges", 0)
            git_branch = context.get("git_branch", "unknown")
            
            print_success("Session context restored!")
            safe_print(f"  Previous session: {prev_session}")
            safe_print(f"  Git branch: {git_branch}")
            safe_print(f"  Total exchanges: {total_exchanges}")
            
            # Show recent conversation preview
            recent_convos = context.get("recent_conversations", [])
            if recent_convos:
                print_info("Recent conversation preview:")
                for i, exchange in enumerate(recent_convos[-2:]):  # Show last 2
                    timestamp = exchange.get("timestamp", "unknown")
                    user_msg = exchange.get("user_message", "")[:100]  # First 100 chars
                    safe_print(f"  [{timestamp[:10]}] User: {user_msg}...")
            
            return {
                "restored": True,
                "context": context,
                "session_id": prev_session
            }
            
        except Exception as e:
            print_error(f"Failed to restore session context: {e}")
            return {"restored": False, "error": str(e)}
    
    def create_greeting_response(self, user_message: str, context: dict) -> str:
        """Create an appropriate greeting response with context"""
        
        if not context.get("restored", False):
            return "Good morning! Starting fresh - no previous session found."
        
        session_context = context.get("context", {})
        prev_session = session_context.get("previous_session", "unknown")
        total_exchanges = session_context.get("total_exchanges", 0)
        
        # Customize response based on user message
        user_lower = user_message.lower()
        
        if "amnesia" in user_lower:
            response = f"Good morning! You're right - I start fresh each session. "
        elif "morning" in user_lower:
            response = "Good morning! "
        elif "hello" in user_lower or "hi" in user_lower:
            response = "Hello! "
        else:
            response = "Welcome back! "
        
        # Add context information
        response += f"I've restored context from your previous session ({prev_session}) "
        response += f"with {total_exchanges} exchanges. "
        
        # Check for ongoing work
        recent_convos = session_context.get("recent_conversations", [])
        if recent_convos:
            last_exchange = recent_convos[-1]
            last_user_msg = last_exchange.get("user_message", "").lower()
            
            # Detect what they were working on
            if any(word in last_user_msg for word in ["implement", "build", "create", "add"]):
                response += "I see you were working on implementation tasks. "
            elif any(word in last_user_msg for word in ["fix", "debug", "error", "issue"]):
                response += "I see you were troubleshooting issues. "
            elif any(word in last_user_msg for word in ["test", "check", "verify"]):
                response += "I see you were testing functionality. "
        
        response += "What would you like to work on today?"
        
        return response


def handle_user_greeting(user_message: str) -> tuple[bool, dict, str]:
    """
    Handle user greeting and return restoration info
    Returns: (is_greeting, context, suggested_response)
    """
    restorer = SessionRestorer()
    
    if restorer.should_restore_context(user_message):
        context = restorer.restore_session_context()
        suggested_response = restorer.create_greeting_response(user_message, context)
        return True, context, suggested_response
    
    return False, {}, ""


if __name__ == "__main__":
    # Test the greeting detection and restoration
    test_messages = [
        "good morning, im guessing you have amnesia again",
        "hello there",
        "hey, can you help me?",
        "what's the weather like?",  # Not a greeting
        "let's continue from where we left off"
    ]
    
    restorer = SessionRestorer()
    
    for msg in test_messages:
        print_info(f"Testing: '{msg}'")
        is_greeting, context, response = handle_user_greeting(msg)
        
        if is_greeting:
            print_success("Greeting detected!")
            safe_print(f"Response: {response}")
        else:
            safe_print("Not a greeting")
        safe_print("")  # Empty line