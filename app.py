import os
import random
import re
from typing import Dict, Any, List, Union
from dataclasses import dataclass

import streamlit as st
from langchain_core.runnables import RunnableWithMessageHistory
from langchain.prompts.chat import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain_aws import ChatBedrockConverse
from models import MODELS  # <--- import MODELS here
from chat_history_ui import render_chat_history_sidebar, save_current_session
from app_sidebar import render_sidebar

# AWS credentials are expected to be set by saml2aws (in ~/.aws/credentials)
# Optionally, you can set AWS_DEFAULT_REGION in your environment or .env file
# If you want to support .env for other custom config, you can use dotenv, but not for AWS keys

# Role configurations with prompts and greetings
ROLE_CONFIG = {
    "Default": {
        "prompt": "You are a helpful AI assistant, eager to help users solve problems.",
        "greeting": """
        👋 Welcome to AWS Bedrock ChatBot!
        
        I'm powered by Claude and ready to assist you with:
        • 📝 Writing and editing
        • 🔄 Language translation
        • 💡 Creative brainstorming
        • 🚀 Technical discussions
        • 🎆 And much more!
        
        How can I help you today?
        """
    },
    "AdTech Strategist": {
        "prompt": """You are an expert AdTech strategist specializing in programmatic advertising, DSP (Demand-Side Platform), and SSP (Supply-Side Platform) operations. Your expertise includes:

• Campaign optimization and bidding strategies
• Audience targeting and segmentation
• Real-time bidding (RTB) mechanics and optimization
• Ad inventory management and yield optimization  
• Performance analytics and attribution modeling
• Privacy compliance (GDPR, CCPA, cookieless solutions)
• Header bidding and waterfall optimization
• Cross-platform campaign management

Provide actionable insights, data-driven recommendations, and industry best practices. Always consider ROI, scale, and compliance when making suggestions.""",
        "greeting": """
        📊 Welcome to AdTech Strategy Mode!
        
        I'm your specialized AdTech strategist, ready to help with:
        • 🎯 Campaign optimization and bidding strategies
        • 👥 Audience targeting and segmentation
        • ⚡ Real-time bidding (RTB) optimization
        • 📈 Performance analytics and attribution
        • 🔒 Privacy compliance (GDPR, CCPA)
        • 🔗 Header bidding and yield optimization
        
        What advertising challenge can I help you solve?
        """
    },
    "Performance Analyst": {
        "prompt": """You are a performance advertising analyst with deep expertise in campaign analysis, optimization, and reporting. Your specializations include:

• KPI analysis and performance metrics (CTR, CPC, CPM, ROAS, LTV)
• A/B testing methodology and statistical significance
• Attribution modeling and conversion tracking
• Audience insights and behavioral analysis
• Budget allocation and bid optimization strategies
• Creative performance analysis and recommendations
• Cross-channel performance comparison
• Forecasting and trend analysis

Provide detailed, data-driven analysis with clear recommendations. Always include specific metrics, benchmarks, and actionable next steps in your responses.""",
        "greeting": """
        📈 Welcome to Performance Analytics Mode!
        
        I'm your data-driven performance analyst, ready to help with:
        • 📊 KPI analysis (CTR, CPC, CPM, ROAS, LTV)
        • 🧪 A/B testing and statistical analysis
        • 🎯 Attribution modeling and conversion tracking
        • 💰 Budget allocation and bid optimization
        • 🎨 Creative performance analysis
        • 📉 Cross-channel performance comparison
        
        What performance data needs analysis today?
        """
    },
    "Ad Operations Expert": {
        "prompt": """You are an Ad Operations specialist with comprehensive knowledge of ad serving, trafficking, and technical implementation. Your expertise covers:

• Ad server setup and campaign trafficking (Google Ad Manager, Amazon DSP, etc.)
• Creative specifications and technical requirements
• Pixel implementation and tracking setup
• Header bidding configuration and troubleshooting
• Ad quality and fraud prevention measures
• Inventory management and yield optimization
• Technical troubleshooting and QA processes
• Integration with DSPs, SSPs, and third-party tools

Provide precise technical guidance, step-by-step instructions, and best practices. Focus on implementation details, common issues, and optimization techniques.""",
        "greeting": """
        ⚙️ Welcome to Ad Operations Mode!
        
        I'm your technical Ad Ops specialist, ready to help with:
        • 🖥️ Ad server setup and campaign trafficking
        • 🎨 Creative specifications and requirements
        • 📍 Pixel implementation and tracking
        • 🔗 Header bidding configuration
        • 🛡️ Ad quality and fraud prevention
        • 🔧 Technical troubleshooting and QA
        
        What technical challenge can I solve for you?
        """
    },
    "TensorFlow Expert": {
        "prompt": """You are a TensorFlow machine learning expert specializing in building, training, and deploying ML models for advertising and analytics use cases. Your expertise includes:

• Model architecture design (neural networks, deep learning, CNN, RNN, transformers)
• TensorFlow/Keras API usage and best practices
• Data preprocessing and feature engineering
• Model training, validation, and hyperparameter tuning
• TensorFlow Serving and model deployment
• Performance optimization and GPU acceleration
• MLOps workflows and model versioning
• Predictive modeling for advertising (CTR prediction, audience modeling, attribution)
• Time series forecasting and anomaly detection

Provide clear, executable code examples with explanations. Focus on practical implementations, debugging help, and performance optimization. Always include relevant imports and explain the reasoning behind architectural choices.""",
        "greeting": """
        🧠 Welcome to TensorFlow Expert Mode!
        
        I'm your ML engineering specialist, ready to help with:
        • 🏗️ Model architecture design and implementation
        • 📊 Data preprocessing and feature engineering
        • 🎯 Model training and hyperparameter tuning
        • 🚀 TensorFlow Serving and deployment
        • ⚡ Performance optimization and GPU acceleration
        • 🔄 MLOps workflows and model versioning
        
        What ML challenge shall we tackle together?
        """
    },
    "Snowflake SQL Expert": {
        "prompt": """You are a Snowflake SQL expert with deep knowledge of data warehousing, analytics, and performance optimization. Your specializations include:

• Advanced SQL query writing and optimization
• Snowflake-specific functions and features (QUALIFY, PIVOT, time travel, etc.)
• Data modeling and warehouse design patterns
• Performance tuning and query optimization
• Window functions and analytical queries
• Data transformation and ETL processes
• User-defined functions (UDFs) and stored procedures
• Role-based access control and security
• Cost optimization and resource management
• Integration with external tools and data sources

Provide optimized SQL queries with clear explanations. Focus on Snowflake best practices, performance considerations, and cost-effective solutions. Always explain query logic and suggest alternative approaches when applicable.""",
        "greeting": """
        🗄️ Welcome to Snowflake SQL Expert Mode!
        
        I'm your data warehouse specialist, ready to help with:
        • 📝 Advanced SQL query writing and optimization
        • ❄️ Snowflake-specific functions and features
        • 🏗️ Data modeling and warehouse design
        • ⚡ Performance tuning and optimization
        • 🔄 Data transformation and ETL processes
        • 💰 Cost optimization and resource management
        
        What data challenge can I help you solve?
        """
    },
    "Translator": {
        "prompt": "You are a professional translator. Please identify the source language and translate to the target language while preserving meaning, tone, and nuance. Ensure proper grammar and formatting.",
        "greeting": """
        🌐 Welcome to Translation Mode!
        
        I'm your professional translator, ready to help with:
        • 🔄 Multi-language translation
        • 📝 Tone and nuance preservation
        • ✅ Grammar and formatting accuracy
        • 🎯 Context-aware translations
        • 📖 Cultural adaptation
        • 🗣️ Natural language flow
        
        What would you like me to translate today?
        """
    },
    "Writing Assistant": {
        "prompt": """You are an AI writing assistant. Your task is to improve written content by:
1. Fixing grammar, punctuation, spelling, and style issues
2. Providing specific improvement suggestions
3. Offering better word choices and phrasing
4. Ensuring consistent tone and voice
5. Improving flow and organization
6. Providing overall feedback
7. Outputting a fully edited version

Keep feedback constructive and insightful.""",
        "greeting": """
        ✍️ Welcome to Writing Assistant Mode!
        
        I'm your professional writing coach, ready to help with:
        • ✅ Grammar, punctuation, and spelling
        • 🎨 Style and tone improvements
        • 🔄 Better word choices and phrasing
        • 📖 Flow and organization
        • 💡 Constructive feedback and suggestions
        • 📝 Content editing and refinement
        
        What writing project can I help you improve?
        """
    },
    "Custom": {
        "prompt": "",
        "greeting": """
        🎨 Welcome to Custom Mode!
        
        You're in control! Define your own AI personality with:
        • 🛠️ Custom system instructions
        • 🎯 Specialized behaviors
        • 📋 Tailored responses
        • 🎭 Unique personality traits
        • 💡 Creative configurations
        • 🔧 Personalized assistance
        
        Configure your custom AI assistant below!
        """
    }
}

# Backward compatibility - extract prompts for existing code
ROLE_PROMPTS = {role: config["prompt"] for role, config in ROLE_CONFIG.items()}


def get_role_greeting(role_name: str) -> str:
    """Get the greeting message for a specific role"""
    return ROLE_CONFIG.get(role_name, ROLE_CONFIG["Default"])["greeting"]

@dataclass
class ChatModel:
    """Simplified chat model class"""
    model_name: str
    model_kwargs: Dict[str, Any]
    
    def __post_init__(self):
        model_config = MODELS[self.model_name]
        self.model_id = model_config["model_id"]
        
        # Basic parameters
        base_kwargs = {
            "model": self.model_id,
            "temperature": self.model_kwargs.get("temperature", model_config["temperature"]),
            "top_p": self.model_kwargs.get("top_p", model_config["top_p"]),
            "max_tokens": self.model_kwargs.get("max_tokens", model_config["max_tokens"]),
        }
        
        # Add top_k configuration
        if "anthropic" in self.model_id:
            base_kwargs["additional_model_request_fields"] = {
                "top_k": self.model_kwargs.get("top_k", model_config["top_k"])
            }
        
        self.llm = ChatBedrockConverse(**base_kwargs)


def set_page_config():
    """Set Streamlit page configuration and add custom CSS"""
    st.set_page_config(
        page_title="AWS Bedrock ChatBot",
        layout="wide",
        page_icon="🤖",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS for enhanced UI
    st.markdown("""
    <style>
    /* Main container styling */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }
    
    /* Layout improvements */
    .main-content {
        max-width: 100%;
        padding: 0;
    }
    
    .chat-container {
        background: rgba(255, 255, 255, 0.8);
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 20px;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, #4a90e2 0%, #2c5aa0 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(74, 144, 226, 0.2);
        text-align: center;
    }
    
    .main-header h1 {
        color: white;
        font-size: 2.5rem;
        font-weight: bold;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
    }
    
    .main-header p {
        color: rgba(255, 255, 255, 0.9);
        font-size: 1.1rem;
        margin: 0.5rem 0 0 0;
    }
    
    /* Chat message styling */
    .stChatMessage {
        background: rgba(255, 255, 255, 0.8);
        border-radius: 15px;
        padding: 1rem;
        margin: 0.5rem 0;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    }
    
    .stChatMessage[data-testid="chat-message-user"] {
        background: linear-gradient(135deg, #4a90e2 0%, #357abd 100%);
        color: white;
    }
    
    .stChatMessage[data-testid="chat-message-assistant"] {
        background: linear-gradient(135deg, #6c757d 0%, #495057 100%);
        color: white;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
        width: 400px !important;
        max-height: 100vh;
        overflow-y: auto;
    }
    
    /* Sidebar sections */
    .sidebar-section {
        margin-bottom: 1.5rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid rgba(0, 0, 0, 0.1);
    }
    
    .sidebar-section:last-child {
        border-bottom: none;
    }
    
    /* Session item styling */
    .session-item {
        background: rgba(255, 255, 255, 0.9);
        border-radius: 8px;
        padding: 10px;
        margin: 5px 0;
        border: 1px solid #e9ecef;
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .session-item:hover {
        background: rgba(74, 144, 226, 0.1);
        border-color: #4a90e2;
        transform: translateX(2px);
    }
    
    .session-item.current {
        background: linear-gradient(135deg, #4a90e2 0%, #357abd 100%);
        color: white;
        border-color: #357abd;
    }
    
    /* Compact metrics */
    .metric-card {
        background: white;
        border-radius: 8px;
        padding: 8px 12px;
        text-align: center;
        border: 1px solid #e9ecef;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    
    .metric-number {
        font-size: 1.2rem;
        font-weight: bold;
        color: #4a90e2;
        margin-bottom: 2px;
    }
    
    .metric-label {
        font-size: 0.75rem;
        color: #6c757d;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .stSidebar .stSelectbox > div > div {
        background: white;
        border-radius: 10px;
        border: 2px solid #e9ecef;
        transition: all 0.3s ease;
    }
    
    .stSidebar .stSelectbox > div > div:hover {
        border-color: #4a90e2;
        box-shadow: 0 0 10px rgba(74, 144, 226, 0.3);
    }
    
    .stSidebar .stTextArea > div > div > textarea {
        background: white;
        border-radius: 10px;
        border: 2px solid #e9ecef;
        transition: all 0.3s ease;
    }
    
    .stSidebar .stTextArea > div > div > textarea:focus {
        border-color: #4a90e2;
        box-shadow: 0 0 10px rgba(74, 144, 226, 0.3);
    }
    
    /* Clean slider styling */
    .stSidebar .stSlider > div > div > div {
        background: linear-gradient(90deg, #4a90e2 0%, #357abd 100%);
        height: 4px;
        border-radius: 2px;
    }
    
    /* Slider thumb */
    .stSidebar .stSlider > div > div > div > div:last-child {
        background: white;
        border: 2px solid #4a90e2;
        width: 18px;
        height: 18px;
        border-radius: 50%;
        box-shadow: 0 2px 4px rgba(74, 144, 226, 0.3);
    }
    
    /* Parameter section styling */
    .parameter-section {
        background: rgba(255, 255, 255, 0.5);
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
        border: 1px solid rgba(74, 144, 226, 0.2);
    }
    
    .parameter-label {
        font-weight: 600;
        color: #2c3e50;
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .parameter-value {
        font-size: 0.9rem;
        color: #6c757d;
        font-weight: 500;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #4a90e2 0%, #357abd 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.5rem 2rem;
        font-weight: bold;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(74, 144, 226, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(74, 144, 226, 0.4);
    }
    
    /* Chat input styling */
    .stChatInput > div > div > input {
        background: white;
        border-radius: 25px;
        border: 2px solid #e9ecef;
        padding: 1rem 1.5rem;
        font-size: 1rem;
        transition: all 0.3s ease;
    }
    
    .stChatInput > div > div > input:focus {
        border-color: #4a90e2;
        box-shadow: 0 0 15px rgba(74, 144, 226, 0.3);
    }
    
    /* Animations */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .stChatMessage {
        animation: fadeIn 0.5s ease-out;
    }
    
    /* Scrollbar styling */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%);
    }
    
    /* Sidebar header */
    .sidebar-header {
        background: linear-gradient(135deg, #4a90e2 0%, #357abd 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        text-align: center;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Custom header
    st.markdown("""
    <div class="main-header">
        <h1>🤖 AWS Bedrock ChatBot</h1>
    </div>
    """, unsafe_allow_html=True)




def extract_reasoning_and_text(input_stream):
    """Process streaming responses and extract reasoning content"""
    in_reasoning_block = False
    current_text = ""
    display_text = ""
    
    for chunk in input_stream:
        content = chunk.content if hasattr(chunk, "content") else chunk
        
        if isinstance(content, list):
            for item in content:
                if item.get("type") == "reasoning_content":
                    reasoning_text = item.get("reasoning_content", {}).get("text", "")
                    if reasoning_text:
                        if not in_reasoning_block:
                            display_text += "```thinking\n"
                            yield "```thinking\n"
                            in_reasoning_block = True
                        display_text += reasoning_text
                        yield reasoning_text
                elif item.get("type") == "text" and (text := item.get("text")):
                    if in_reasoning_block:
                        display_text += "\n```\n"
                        yield "\n```\n"
                        in_reasoning_block = False
                    display_text += text
                    current_text += text
                    yield text
        else:
            if in_reasoning_block:
                display_text += "\n```\n"
                yield "\n```\n"
                in_reasoning_block = False
            display_text += content
            current_text += content
            yield content
    
    if in_reasoning_block:
        display_text += "\n```"
        yield "\n```"
    
    # Store cleaned text
    st.session_state["current_llm_text"] = current_text
    st.session_state["current_display_text"] = display_text


def store_message(role: str, content: str):
    """Store message in session state"""
    message = {"role": role}
    
    if role == "assistant" and "current_display_text" in st.session_state:
        message["content"] = st.session_state["current_display_text"]
        if "current_llm_text" in st.session_state:
            message["llm_content"] = st.session_state["current_llm_text"]
    else:
        message["content"] = content
        if role == "user":
            message["llm_content"] = re.sub(r'```thinking.*?```', '', content, flags=re.DOTALL)
        else:
            message["llm_content"] = content
    
    st.session_state.messages.append(message)


def init_conversation(system_prompt: str, chat_model: ChatModel):
    """Initialize conversation chain"""
    msgs = StreamlitChatMessageHistory()
    msgs.clear()
    
    conversation = (
        RunnableWithMessageHistory(
            ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                MessagesPlaceholder(variable_name="chat_history"),
                MessagesPlaceholder(variable_name="query"),
            ])
            | chat_model.llm,
            lambda session_id: msgs,
            input_messages_key="query",
            history_messages_key="chat_history",
        )
        | extract_reasoning_and_text
    )
    
    # Initialize session state with role-specific greeting
    if "messages" not in st.session_state:
        current_role = st.session_state.get("selected_role", "Default")
        greeting_msg = get_role_greeting(current_role)
        st.session_state.messages = [{
            "role": "assistant",
            "content": greeting_msg,
            "llm_content": f"Hello! I'm your {current_role} AI assistant. How can I help you today?"
        }]
    
    if "current_llm_text" not in st.session_state:
        st.session_state.current_llm_text = ""
    
    if "msgs" not in st.session_state:
        st.session_state.msgs = msgs
    
    return conversation


def generate_response(conversation, user_input: str):
    """Generate response"""
    msgs = st.session_state.msgs
    msgs.clear()
    
    # Add history messages (excluding current user message)
    for i, msg in enumerate(st.session_state.messages[:-1]):
        if i == 0:  # Skip initial greeting
            continue
        
        if msg["role"] == "user":
            msgs.add_user_message(msg["content"])
        elif msg["role"] == "assistant":
            clean_msg = re.sub(r'```thinking.*?```', '', msg["content"], flags=re.DOTALL)
            clean_msg = clean_msg.strip()
            if clean_msg:
                msgs.add_ai_message(clean_msg)
    
    # Clean input
    clean_input = re.sub(r'```thinking.*?```', '', user_input, flags=re.DOTALL)
    formatted_input = [{"role": "user", "content": clean_input}]
    
    # Stream response
    return st.write_stream(
        conversation.stream(
            {"query": formatted_input},
            config={"configurable": {"session_id": "streamlit_chat"}}
        )
    )


def new_chat(role_name: str = None):
    """Start new chat with role-specific greeting"""
    # Use current role if none specified
    if role_name is None:
        role_name = st.session_state.get("selected_role", "Default")
    
    # Get role-specific greeting
    greeting_msg = get_role_greeting(role_name)
    
    st.session_state["messages"] = [{
        "role": "assistant",
        "content": greeting_msg,
        "llm_content": f"Hello! I'm your {role_name} AI assistant. How can I help you today?"
    }]
    
    if "msgs" in st.session_state:
        st.session_state.msgs.clear()
    
    if "current_llm_text" in st.session_state:
        del st.session_state["current_llm_text"]
    if "current_display_text" in st.session_state:
        del st.session_state["current_display_text"]


def export_chat():
    """Export chat history"""
    if "messages" in st.session_state and len(st.session_state.messages) > 1:
        chat_content = ""
        for msg in st.session_state.messages:
            role = msg["role"].title()
            content = msg["content"]
            chat_content += f"**{role}:** {content}\n\n"
        
        st.download_button(
            label="📥 Download Chat History",
            data=chat_content,
            file_name=f"bedrock_chat_{st.session_state.get('widget_key', 'default')}.md",
            mime="text/markdown",
            use_container_width=True
        )
    else:
        st.warning("⚠️ No chat history to export")


def display_chat_messages():
    """Display chat messages with enhanced styling"""
    # Create a container for the chat messages
    with st.container():
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        
        for i, message in enumerate(st.session_state.messages):
            with st.chat_message(message["role"]):
                # Add message metadata for non-initial messages
                if i > 0:  # Skip initial greeting
                    timestamp = "Just now" if i == len(st.session_state.messages) - 1 else f"Message {i}"
                    role_icon = "👤" if message["role"] == "user" else "🤖"
                    st.caption(f"{role_icon} {message['role'].title()} • {timestamp}")
                
                st.markdown(message["content"])
        
        st.markdown('</div>', unsafe_allow_html=True)


def main():
    """Main function"""
    set_page_config()
    
    # Generate unique widget key
    if "widget_key" not in st.session_state:
        st.session_state["widget_key"] = str(random.randint(1, 1000000))
    
    # Main content area
    with st.container():
        # Render sidebar
        params = render_sidebar()
        
        # Main chat area
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Initialize chat model
            chat_model = ChatModel(
                model_name=params["model_name"],
                model_kwargs={
                    "temperature": params["temperature"],
                    "top_p": params["top_p"],
                    "top_k": params["top_k"],
                    "max_tokens": params["max_tokens"]
                }
            )
            
            # Initialize conversation
            conversation = init_conversation(params["system_prompt"], chat_model)
            
            # Display chat messages
            display_chat_messages()
            
            # Enhanced user input with placeholder
            if prompt := st.chat_input("💬 Ask me anything... (Press Enter to send)"):
                # Save session before processing new message
                if len(st.session_state.get("messages", [])) > 1:
                    save_current_session()
                
                # Store and display user message
                store_message("user", prompt)
                with st.chat_message("user"):
                    st.markdown(prompt)
                
                # Generate and display assistant response
                with st.chat_message("assistant"):
                    response = generate_response(conversation, prompt)
                    store_message("assistant", response)
        
        with col2:
            # Quick actions panel
            st.markdown("### 🚀 Quick Actions")
            
            if st.button("💾 Save Session", use_container_width=True, type="primary"):
                save_current_session()
            
            if st.button("📊 Session Stats", use_container_width=True):
                from chat_history import get_chat_history_manager
                manager = get_chat_history_manager()
                stats = manager.get_session_stats()
                
                st.metric("Total Sessions", stats["total_sessions"])
                st.metric("Total Messages", stats["total_messages"])
                
                if stats["model_usage"]:
                    st.markdown("**Model Usage:**")
                    for model, count in stats["model_usage"].items():
                        st.write(f"• {model}: {count}")
            
            # Current session info
            if st.session_state.get("current_session_id"):
                st.markdown("### 📋 Current Session")
                st.success("🟢 Session Active")
                st.write(f"ID: {st.session_state.current_session_id[:8]}...")
            else:
                st.markdown("### 📋 Current Session") 
                st.info("🔵 Unsaved Session")
                
            # Quick model info
            st.markdown("### 🤖 Current Model")
            current_model = params.get("model_name", "Unknown")
            st.write(f"**{current_model}**")
            st.write(f"🌡️ Temp: {params.get('temperature', 1.0)}")
            st.write(f"📊 Max Tokens: {params.get('max_tokens', 4096):,}")


if __name__ == "__main__":
    main() 