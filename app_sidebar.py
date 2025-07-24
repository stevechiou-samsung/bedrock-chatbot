# app_sidebar.py
# Sidebar components for the main app

import streamlit as st
from models import MODELS
from chat_history_ui import render_chat_history_sidebar


def render_sidebar():
    """Render sidebar and return model parameters"""
    with st.sidebar:
        # Create tabs for different sections
        tab1, tab2 = st.tabs(["🎯 Config", "💬 History"])
        
        with tab1:
            config_params = render_config_section()
        
        with tab2:
            render_chat_history_sidebar()
    
    # Return current model parameters
    return config_params


def render_config_section():
    """Render model configuration section"""
    # Model selection with icon
    st.markdown("#### 🤖 AI Model")
    model_keys = list(MODELS.keys())
    default_model_index = model_keys.index("Claude 4 Sonnet")
    model_name = st.selectbox(
        "Choose your AI model",
        model_keys,
        index=default_model_index,
        key=f"{st.session_state.get('widget_key', 'default')}_model",
        help="Select the Claude model for your conversation"
    )
    
    # Display model info in a clean card
    model_info = MODELS[model_name]
    st.markdown(f"""
    <div class="parameter-section">
        <div class="parameter-label">📋 Model Information</div>
        <div class="parameter-value">
            • Max Tokens: {model_info['max_tokens']:,}<br>
            • Model ID: {model_info['model_id'].split('.')[-1]}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Role selection with elegant buttons
    st.markdown("#### 🎭 AI Role")
    
    # Initialize role in session state if not exists
    if "selected_role" not in st.session_state:
        st.session_state.selected_role = "Default"
    
    # Role button configuration with icons and short labels
    role_config = {
        "Default": {"icon": "🤖", "label": "Default", "color": "#4a90e2"},
        "AdTech Strategist": {"icon": "📊", "label": "AdTech", "color": "#28a745"},
        "Performance Analyst": {"icon": "📈", "label": "Analytics", "color": "#dc3545"},
        "Ad Operations Expert": {"icon": "⚙️", "label": "Ad Ops", "color": "#6f42c1"},
        "TensorFlow Expert": {"icon": "🧠", "label": "TensorFlow", "color": "#fd7e14"},
        "Snowflake SQL Expert": {"icon": "🗄️", "label": "Snowflake", "color": "#20c997"},
        "Translator": {"icon": "🌐", "label": "Translator", "color": "#6c757d"},
        "Writing Assistant": {"icon": "✍️", "label": "Writing", "color": "#e83e8c"},
        "Custom": {"icon": "🎨", "label": "Custom", "color": "#17a2b8"}
    }
    
    # Create role buttons in a 3-column grid
    cols = st.columns(3)
    role_keys = list(role_config.keys())
    
    for i, role_key in enumerate(role_keys):
        with cols[i % 3]:
            config = role_config[role_key]
            is_selected = st.session_state.selected_role == role_key
            
            if st.button(
                f"{config['icon']} {config['label']}",
                key=f"role_{role_key}_{st.session_state.get('widget_key', 'default')}",
                use_container_width=True,
                help=f"Switch to {role_key} mode",
                type="primary" if is_selected else "secondary"
            ):
                # Check if role is changing
                if st.session_state.selected_role != role_key:
                    # Import new_chat function
                    from app import new_chat
                    # Always update greeting when switching roles
                    new_chat(role_key)
                    
                    # Show notification about role switch
                    st.success(f"🔄 Switched to {role_key} mode!")
                
                st.session_state.selected_role = role_key
                st.rerun()
    
    role = st.session_state.selected_role
    
    # System prompt with enhanced styling
    st.markdown("#### 📝 System Instructions")
    
    # Import ROLE_PROMPTS
    from app import ROLE_PROMPTS
    
    if role == "Default":
        default_prompt = "You are a helpful, thoughtful, and knowledgeable assistant. Your job is to carefully analyze the user's questions, understand their underlying needs, and provide clear, accurate, and useful answers. You always ask clarifying questions if something is ambiguous, and you aim to make complex topics easy to understand. Your responses should be practical, well-structured, and tailored to the user's context whenever possible.\n\nStay professional but friendly, and ensure that your explanations are grounded in facts and logic. If a task requires multiple steps, break it down clearly. When appropriate, offer examples, comparisons, or step-by-step instructions to enhance clarity and usefulness."
    else:
        default_prompt = "" if role == "Custom" else ROLE_PROMPTS.get(role, "")
    
    system_prompt = st.text_area(
        "Customize AI behavior and personality",
        value=default_prompt,
        height=150,
        key=f"{st.session_state.get('widget_key', 'default')}_system_prompt",
        help="Define how the AI should behave and respond"
    )
    
    # Model parameters with enhanced styling
    st.markdown("#### ⚙️ Advanced Settings")
    
    with st.expander("🔧 Model Parameters", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            temperature = st.slider(
                "🌡️ Temperature",
                min_value=0.0,
                max_value=2.0,
                value=1.0,
                step=0.1,
                key=f"{st.session_state.get('widget_key', 'default')}_temp",
                help="Controls randomness: 0=focused, 2=creative"
            )
            top_p = st.slider(
                "🎯 Top-P",
                min_value=0.0,
                max_value=1.0,
                value=1.0,
                step=0.01,
                key=f"{st.session_state.get('widget_key', 'default')}_top_p",
                help="Nucleus sampling threshold"
            )
        
        with col2:
            top_k = st.slider(
                "🔢 Top-K",
                min_value=1,
                max_value=500,
                value=500,
                step=5,
                key=f"{st.session_state.get('widget_key', 'default')}_top_k",
                help="Limits vocabulary to top K tokens"
            )
            # Get model info for dynamic max tokens
            model_max_tokens = model_info["max_tokens"]
            
            max_tokens = st.slider(
                "📊 Max Tokens",
                min_value=100,
                max_value=model_max_tokens,
                value=min(4096, model_max_tokens),
                step=100,
                key=f"{st.session_state.get('widget_key', 'default')}_max_tokens",
                help=f"Maximum response length (Model limit: {model_max_tokens:,})"
            )
        
        # Current settings summary
        st.markdown(f"""
        <div class="parameter-section">
            <div class="parameter-label">⚡ Current Settings</div>
            <div class="parameter-value">
                🌡️ Temperature: {temperature}<br>
                🎯 Top-P: {top_p}<br>
                🔢 Top-K: {top_k}<br>
                📊 Max Tokens: {max_tokens:,}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Action buttons with enhanced styling
    st.markdown("---")
    st.markdown("#### 🚀 Actions")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🆕 New Chat", type="primary", use_container_width=True):
            from app import new_chat
            new_chat()
            st.rerun()
    
    with col2:
        if st.button("💾 Save Chat", use_container_width=True):
            save_current_session()
    
    # Store current model parameters in session state for chat history
    st.session_state.current_model_name = model_name
    st.session_state.current_temperature = temperature
    st.session_state.current_top_p = top_p
    st.session_state.current_top_k = top_k
    st.session_state.current_max_tokens = max_tokens
    
    return {
        "model_name": model_name,
        "system_prompt": system_prompt,
        "temperature": temperature,
        "top_p": top_p,
        "top_k": top_k,
        "max_tokens": max_tokens
    }