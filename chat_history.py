# chat_history.py
# Chat history management for Bedrock ChatBot

import json
import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
import streamlit as st


class ChatHistoryManager:
    """Manages chat history persistence and operations"""
    
    def __init__(self, storage_dir: str = "chat_history"):
        self.storage_dir = storage_dir
        self.ensure_storage_dir()
    
    def ensure_storage_dir(self):
        """Create storage directory if it doesn't exist"""
        if not os.path.exists(self.storage_dir):
            os.makedirs(self.storage_dir)
    
    def generate_session_id(self) -> str:
        """Generate unique session ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        return f"{timestamp}_{unique_id}"
    
    def save_chat_session(self, 
                         messages: List[Dict[str, Any]], 
                         session_title: str = None,
                         session_id: str = None,
                         model_config: Dict[str, Any] = None) -> str:
        """Save chat session to file"""
        if not session_id:
            session_id = self.generate_session_id()
        
        # Generate title from first user message if not provided
        if not session_title:
            user_messages = [msg for msg in messages if msg.get("role") == "user"]
            if user_messages:
                first_message = user_messages[0].get("content", "")
                session_title = first_message[:50] + "..." if len(first_message) > 50 else first_message
            else:
                session_title = "New Chat Session"
        
        session_data = {
            "session_id": session_id,
            "title": session_title,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "message_count": len(messages),
            "model_config": model_config or {},
            "messages": messages
        }
        
        file_path = os.path.join(self.storage_dir, f"{session_id}.json")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, ensure_ascii=False, indent=2)
        
        return session_id
    
    def load_chat_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Load chat session from file"""
        file_path = os.path.join(self.storage_dir, f"{session_id}.json")
        if not os.path.exists(file_path):
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return None
    
    def list_chat_sessions(self) -> List[Dict[str, Any]]:
        """List all chat sessions with metadata"""
        sessions = []
        
        if not os.path.exists(self.storage_dir):
            return sessions
        
        for filename in os.listdir(self.storage_dir):
            if filename.endswith('.json'):
                session_id = filename[:-5]  # Remove .json extension
                session_data = self.load_chat_session(session_id)
                if session_data:
                    sessions.append({
                        "session_id": session_id,
                        "title": session_data.get("title", "Untitled Chat"),
                        "created_at": session_data.get("created_at"),
                        "updated_at": session_data.get("updated_at"),
                        "message_count": session_data.get("message_count", 0),
                        "model_config": session_data.get("model_config", {})
                    })
        
        # Sort by updated_at descending (most recent first)
        sessions.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
        return sessions
    
    def delete_chat_session(self, session_id: str) -> bool:
        """Delete chat session file"""
        file_path = os.path.join(self.storage_dir, f"{session_id}.json")
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
        except OSError:
            pass
        return False
    
    def update_session_title(self, session_id: str, new_title: str) -> bool:
        """Update session title"""
        session_data = self.load_chat_session(session_id)
        if session_data:
            session_data["title"] = new_title
            session_data["updated_at"] = datetime.now().isoformat()
            
            file_path = os.path.join(self.storage_dir, f"{session_id}.json")
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(session_data, f, ensure_ascii=False, indent=2)
                return True
            except Exception:
                pass
        return False
    
    def export_session_markdown(self, session_id: str) -> Optional[str]:
        """Export session as markdown format"""
        session_data = self.load_chat_session(session_id)
        if not session_data:
            return None
        
        markdown_content = f"# {session_data.get('title', 'Chat Session')}\n\n"
        markdown_content += f"**Created:** {session_data.get('created_at', 'Unknown')}\n"
        markdown_content += f"**Model:** {session_data.get('model_config', {}).get('model_name', 'Unknown')}\n\n"
        markdown_content += "---\n\n"
        
        for msg in session_data.get("messages", []):
            role = msg.get("role", "").title()
            content = msg.get("content", "")
            markdown_content += f"## {role}\n\n{content}\n\n"
        
        return markdown_content
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get statistics about chat sessions"""
        sessions = self.list_chat_sessions()
        total_sessions = len(sessions)
        total_messages = sum(session.get("message_count", 0) for session in sessions)
        
        # Model usage stats
        model_usage = {}
        for session in sessions:
            model_name = session.get("model_config", {}).get("model_name", "Unknown")
            model_usage[model_name] = model_usage.get(model_name, 0) + 1
        
        return {
            "total_sessions": total_sessions,
            "total_messages": total_messages,
            "model_usage": model_usage,
            "recent_sessions": sessions[:5]  # 5 most recent
        }


def get_chat_history_manager() -> ChatHistoryManager:
    """Get or create chat history manager instance"""
    if "chat_history_manager" not in st.session_state:
        st.session_state.chat_history_manager = ChatHistoryManager()
    return st.session_state.chat_history_manager