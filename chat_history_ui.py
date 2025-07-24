# chat_history_ui.py
# Chat history UI components for Bedrock ChatBot

import streamlit as st
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from chat_history import get_chat_history_manager


def render_chat_history_sidebar():
    """Render chat history sidebar with session management"""
    chat_manager = get_chat_history_manager()
    
    # Chat History Header
    st.markdown("""
    <div class="sidebar-header">
        💬 Chat History
    </div>
    """, unsafe_allow_html=True)
    
    # Quick stats
    stats = chat_manager.get_session_stats()
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Sessions", stats["total_sessions"])
    with col2:
        st.metric("Messages", stats["total_messages"])
    
    # Session management buttons
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("💾 Save", use_container_width=True, help="Save current session"):
            save_current_session()
    
    with col2:
        if st.button("🆕 New", use_container_width=True, help="Start new session"):
            if st.session_state.get("current_session_id"):
                save_current_session()  # Auto-save before creating new
            start_new_session()
            st.rerun()
    
    with col3:
        if st.button("📊 Stats", use_container_width=True, help="View statistics"):
            st.session_state.show_stats = not st.session_state.get("show_stats", False)
            st.rerun()
    
    # Show stats if toggled
    if st.session_state.get("show_stats", False):
        render_session_stats(stats)
    
    st.markdown("---")
    
    # Session list
    sessions = chat_manager.list_chat_sessions()
    
    if sessions:
        st.markdown("#### 📜 Recent Sessions")
        
        # Search/filter
        search_term = st.text_input("🔍 Search sessions", key="history_search")
        
        # Filter sessions by search term
        if search_term:
            sessions = [s for s in sessions if search_term.lower() in s["title"].lower()]
        
        # Display sessions
        for session in sessions[:10]:  # Show max 10 sessions
            render_session_item(session, chat_manager)
    
    else:
        st.info("📝 No saved chat sessions yet")
        st.markdown("""
        Start chatting and click **Save** to preserve your conversations!
        """)


def render_session_item(session: Dict[str, Any], chat_manager):
    """Render individual session item"""
    session_id = session["session_id"]
    title = session["title"]
    created_at = session.get("created_at", "")
    message_count = session.get("message_count", 0)
    
    # Format timestamp
    try:
        created_dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        now = datetime.now()
        
        if (now - created_dt).days < 1:
            time_str = created_dt.strftime("%H:%M")
        elif (now - created_dt).days < 7:
            time_str = created_dt.strftime("%a %H:%M")
        else:
            time_str = created_dt.strftime("%m/%d")
    except:
        time_str = "Unknown"
    
    # Session container with improved styling
    with st.container():
        # Check if this is the current session
        is_current = st.session_state.get("current_session_id") == session_id
        
        # Session card styling
        card_style = """
        <div style="
            background: {}; 
            border-radius: 10px; 
            padding: 12px; 
            margin: 6px 0; 
            border: {}; 
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
        ">
        """.format(
            "linear-gradient(135deg, #4a90e2 0%, #357abd 100%)" if is_current else "rgba(255, 255, 255, 0.8)",
            "2px solid #4a90e2" if is_current else "1px solid #e9ecef"
        )
        
        st.markdown(card_style, unsafe_allow_html=True)
        
        # Session info
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Title with current session indicator
            title_color = "white" if is_current else "#2c3e50"
            st.markdown(f"""
            <div style="color: {title_color}; font-weight: {'bold' if is_current else 'normal'};">
                {'🟢 ' if is_current else ''}
                {title[:40]}{'...' if len(title) > 40 else ''}
            </div>
            <div style="color: {'rgba(255,255,255,0.8)' if is_current else '#6c757d'}; font-size: 0.8rem;">
                {time_str} • {message_count} messages
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            # Action buttons
            if st.button("📂", key=f"load_{session_id}", help="Load session"):
                load_session(session_id)
                st.rerun()
        
        # Session actions (only show for non-current sessions)
        if not is_current:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("✏️", key=f"edit_{session_id}", help="Rename"):
                    st.session_state[f"edit_title_{session_id}"] = True
                    st.rerun()
            
            with col2:
                if st.button("📥", key=f"export_{session_id}", help="Export"):
                    export_session(session_id)
            
            with col3:
                if st.button("🗑️", key=f"delete_{session_id}", help="Delete"):
                    if st.session_state.get(f"confirm_delete_{session_id}"):
                        delete_session(session_id)
                        st.rerun()
                    else:
                        st.session_state[f"confirm_delete_{session_id}"] = True
                        st.rerun()
        
        # Edit title interface
        if st.session_state.get(f"edit_title_{session_id}"):
            new_title = st.text_input(
                "New title:", 
                value=title, 
                key=f"new_title_{session_id}"
            )
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅", key=f"save_title_{session_id}"):
                    chat_manager.update_session_title(session_id, new_title)
                    st.session_state[f"edit_title_{session_id}"] = False
                    st.rerun()
            with col2:
                if st.button("❌", key=f"cancel_title_{session_id}"):
                    st.session_state[f"edit_title_{session_id}"] = False
                    st.rerun()
        
        # Delete confirmation
        if st.session_state.get(f"confirm_delete_{session_id}"):
            st.warning("⚠️ Delete this session?")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Yes", key=f"confirm_yes_{session_id}"):
                    delete_session(session_id)
                    st.rerun()
            with col2:
                if st.button("❌ No", key=f"confirm_no_{session_id}"):
                    st.session_state[f"confirm_delete_{session_id}"] = False
                    st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)


def render_session_stats(stats: Dict[str, Any]):
    """Render session statistics"""
    st.markdown("#### 📊 Session Statistics")
    
    # Model usage chart
    if stats["model_usage"]:
        st.markdown("**Model Usage:**")
        for model, count in stats["model_usage"].items():
            percentage = (count / stats["total_sessions"]) * 100
            st.write(f"• {model}: {count} sessions ({percentage:.1f}%)")
    
    # Recent activity
    if stats["recent_sessions"]:
        st.markdown("**Recent Activity:**")
        for session in stats["recent_sessions"][:3]:
            try:
                created_dt = datetime.fromisoformat(session["created_at"].replace('Z', '+00:00'))
                days_ago = (datetime.now() - created_dt).days
                
                if days_ago == 0:
                    time_str = "Today"
                elif days_ago == 1:
                    time_str = "Yesterday"
                else:
                    time_str = f"{days_ago} days ago"
                
                st.write(f"• {session['title'][:30]}... ({time_str})")
            except:
                st.write(f"• {session['title'][:30]}...")


def save_current_session():
    """Save current chat session"""
    if "messages" not in st.session_state or len(st.session_state.messages) <= 1:
        st.warning("⚠️ No conversation to save")
        return
    
    chat_manager = get_chat_history_manager()
    
    # Get current model configuration
    model_config = {
        "model_name": st.session_state.get("current_model_name", "Unknown"),
        "temperature": st.session_state.get("current_temperature", 1.0),
        "top_p": st.session_state.get("current_top_p", 1.0),
        "top_k": st.session_state.get("current_top_k", 500),
        "max_tokens": st.session_state.get("current_max_tokens", 4096),
        "role": st.session_state.get("selected_role", "Default")
    }
    
    # Generate or use existing session ID
    session_id = st.session_state.get("current_session_id")
    
    session_id = chat_manager.save_chat_session(
        messages=st.session_state.messages,
        session_id=session_id,
        model_config=model_config
    )
    
    st.session_state.current_session_id = session_id
    st.success("💾 Session saved successfully!")


def load_session(session_id: str):
    """Load a chat session"""
    chat_manager = get_chat_history_manager()
    session_data = chat_manager.load_chat_session(session_id)
    
    if session_data:
        # Save current session before loading new one
        if st.session_state.get("messages") and len(st.session_state.messages) > 1:
            save_current_session()
        
        # Load session data
        st.session_state.messages = session_data["messages"]
        st.session_state.current_session_id = session_id
        
        # Load model configuration if available
        model_config = session_data.get("model_config", {})
        if model_config:
            st.session_state.current_model_name = model_config.get("model_name")
            st.session_state.current_temperature = model_config.get("temperature", 1.0)
            st.session_state.current_top_p = model_config.get("top_p", 1.0)
            st.session_state.current_top_k = model_config.get("top_k", 500)
            st.session_state.current_max_tokens = model_config.get("max_tokens", 4096)
            if "role" in model_config:
                st.session_state.selected_role = model_config["role"]
        
        # Clear message history for fresh conversation
        if "msgs" in st.session_state:
            st.session_state.msgs.clear()
        
        st.success(f"📂 Loaded session: {session_data['title']}")
    else:
        st.error("❌ Failed to load session")


def start_new_session():
    """Start a new chat session"""
    # Clear current session data
    st.session_state.messages = []
    st.session_state.current_session_id = None
    
    # Clear message history
    if "msgs" in st.session_state:
        st.session_state.msgs.clear()
    
    # Reset to default greeting
    from app import get_role_greeting
    current_role = st.session_state.get("selected_role", "Default")
    greeting_msg = get_role_greeting(current_role)
    
    st.session_state.messages = [{
        "role": "assistant",
        "content": greeting_msg,
        "llm_content": f"Hello! I'm your {current_role} AI assistant. How can I help you today?"
    }]


def export_session(session_id: str):
    """Export session as markdown"""
    chat_manager = get_chat_history_manager()
    markdown_content = chat_manager.export_session_markdown(session_id)
    
    if markdown_content:
        session_data = chat_manager.load_chat_session(session_id)
        filename = f"chat_{session_id}.md"
        
        st.download_button(
            label="📥 Download",
            data=markdown_content,
            file_name=filename,
            mime="text/markdown",
            key=f"download_{session_id}"
        )
        st.success("📄 Export ready!")
    else:
        st.error("❌ Failed to export session")


def delete_session(session_id: str):
    """Delete a chat session"""
    chat_manager = get_chat_history_manager()
    
    if chat_manager.delete_chat_session(session_id):
        # Clear confirmation state
        if f"confirm_delete_{session_id}" in st.session_state:
            del st.session_state[f"confirm_delete_{session_id}"]
        
        # If deleting current session, start new one
        if st.session_state.get("current_session_id") == session_id:
            start_new_session()
        
        st.success("🗑️ Session deleted successfully!")
    else:
        st.error("❌ Failed to delete session")