"""
Session Manager - Handles AI conversation sessions
"""
import uuid
import json
from typing import Optional, Dict
from datetime import datetime, timedelta
from django.core.cache import cache
from ai_app.schemas import ChatSession, MessageRole
from ai_app.config import AIConfig


class SessionManager:
    """
    Manages chat sessions using Django's cache framework
    Supports Redis, Memcached, or Django's database cache
    """
    
    def __init__(self):
        """Initialize session manager"""
        self.cache_prefix = "ai_session:"
        self.timeout = AIConfig.SESSION_TIMEOUT_MINUTES * 60
    
    def create_session(self, user_id: Optional[str] = None) -> ChatSession:
        """Create a new chat session"""
        session_id = str(uuid.uuid4())
        session = ChatSession(
            session_id=session_id,
            user_id=user_id
        )
        
        session.add_message(
            role=MessageRole.SYSTEM,
            content=AIConfig.SYSTEM_PROMPT
        )
        
        self._save_session(session)
        return session
    
    def get_session(self, session_id: str) -> Optional[ChatSession]:
        """Retrieve a session by ID"""
        cache_key = f"{self.cache_prefix}{session_id}"
        session_data = cache.get(cache_key)
        
        if not session_data:
            return None
        
        return self._deserialize_session(session_data)
    
    def update_session(self, session: ChatSession):
        """Update an existing session"""
        session.last_activity = datetime.now()
        self._save_session(session)
    
    def delete_session(self, session_id: str):
        """Delete a session"""
        cache_key = f"{self.cache_prefix}{session_id}"
        cache.delete(cache_key)
    
    def _save_session(self, session: ChatSession):
        """Save session to cache"""
        cache_key = f"{self.cache_prefix}{session.session_id}"
        session_data = self._serialize_session(session)
        cache.set(cache_key, session_data, timeout=self.timeout)
    
    def _serialize_session(self, session: ChatSession) -> str:
        """Convert session to JSON string"""
        data = {
            "session_id": session.session_id,
            "user_id": session.user_id,
            "messages": [
                {
                    "role": msg.role.value,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat(),
                    "metadata": msg.metadata
                }
                for msg in session.messages
            ],
            "context": session.context,
            "created_at": session.created_at.isoformat(),
            "last_activity": session.last_activity.isoformat()
        }
        return json.dumps(data)
    
    def _deserialize_session(self, session_data: str) -> ChatSession:
        """Reconstruct session from JSON string"""
        from ai_app.schemas import ConversationMessage
        
        data = json.loads(session_data)
        
        session = ChatSession(
            session_id=data["session_id"],
            user_id=data.get("user_id"),
            context=data.get("context", {}),
            created_at=datetime.fromisoformat(data["created_at"]),
            last_activity=datetime.fromisoformat(data["last_activity"])
        )
        
        for msg_data in data["messages"]:
            message = ConversationMessage(
                role=MessageRole(msg_data["role"]),
                content=msg_data["content"],
                timestamp=datetime.fromisoformat(msg_data["timestamp"]),
                metadata=msg_data.get("metadata", {})
            )
            session.messages.append(message)
        
        return session
