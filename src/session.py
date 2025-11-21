from collections import defaultdict
from typing import Dict, List

# ============================================================================
# Session Management
# ============================================================================


class SessionManager:
    """In-memory session management for conversations"""

    def __init__(self):
        self.sessions: Dict[str, List[Dict[str, str]]] = defaultdict(list)

    def add_message(self, session_id: str, role: str, content: str):
        """Add a message to session history"""
        self.sessions[session_id].append({"role": role, "content": content})

    def get_messages(self, session_id: str) -> List[Dict[str, str]]:
        """Get all messages for a session"""
        return self.sessions[session_id]

    def clear_session(self, session_id: str):
        """Clear a session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
