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

# AWS credentials are expected to be set by saml2aws (in ~/.aws/credentials)
# Optionally, you can set AWS_DEFAULT_REGION in your environment or .env file
# If you want to support .env for other custom config, you can use dotenv, but not for AWS keys

# Role prompts
ROLE_PROMPTS = {
    "Default": "You are a helpful AI assistant, eager to help users solve problems.",
    "Translator": "You are a professional translator. Please identify the source language and translate to the target language while preserving meaning, tone, and nuance. Ensure proper grammar and formatting.",
    "Writing Assistant": """You are an AI writing assistant. Your task is to improve written content by:\n1. Fixing grammar, punctuation, spelling, and style issues\n2. Providing specific improvement suggestions\n3. Offering better word choices and phrasing\n4. Ensuring consistent tone and voice\n5. Improving flow and organization\n6. Providing overall feedback\n7. Outputting a fully edited version\n\nKeep feedback constructive and insightful."""
}

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
    """Set Streamlit page configuration"""
    st.set_page_config(
        page_title="🤖 Bedrock ChatBot",
        layout="wide",
        page_icon="🤖"
    )
    st.title("🤖 Bedrock ChatBot")


def render_sidebar():
    """Render sidebar and return model parameters"""
    with st.sidebar:
        # Model selection
        model_name = st.selectbox(
            "Select Model",
            list(MODELS.keys()),
            key=f"{st.session_state.get('widget_key', 'default')}_model"
        )
        
        # Role selection
        role = st.selectbox(
            "Select Role",
            ["Custom"] + list(ROLE_PROMPTS.keys()),
            key=f"{st.session_state.get('widget_key', 'default')}_role"
        )
        
        # System prompt
        default_prompt = "" if role == "Custom" else ROLE_PROMPTS.get(role, "")
        system_prompt = st.text_area(
            "System Prompt",
            value=default_prompt,
            height=150,
            key=f"{st.session_state.get('widget_key', 'default')}_system_prompt"
        )
        
        # Model parameters
        st.subheader("Model Parameters")
        
        col1, col2 = st.columns(2)
        with col1:
            temperature = st.slider(
                "Temperature",
                min_value=0.0,
                max_value=2.0,
                value=1.0,
                step=0.1,
                key=f"{st.session_state.get('widget_key', 'default')}_temp"
            )
            top_p = st.slider(
                "Top-P",
                min_value=0.0,
                max_value=1.0,
                value=1.0,
                step=0.01,
                key=f"{st.session_state.get('widget_key', 'default')}_top_p"
            )
        
        with col2:
            top_k = st.slider(
                "Top-K",
                min_value=1,
                max_value=500,
                value=500,
                step=5,
                key=f"{st.session_state.get('widget_key', 'default')}_top_k"
            )
            max_tokens = st.slider(
                "Max Tokens",
                min_value=100,
                max_value=64000,
                value=4096,
                step=100,
                key=f"{st.session_state.get('widget_key', 'default')}_max_tokens"
            )
        
        # New chat button
        if st.button("🆕 New Chat", type="primary", use_container_width=True):
            new_chat()
            st.rerun()
    
    return {
        "model_name": model_name,
        "system_prompt": system_prompt,
        "temperature": temperature,
        "top_p": top_p,
        "top_k": top_k,
        "max_tokens": max_tokens
    }


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
    
    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = [{
            "role": "assistant",
            "content": "Hello! I'm your Bedrock AI assistant. How can I help you today?",
            "llm_content": "Hello! I'm your Bedrock AI assistant. How can I help you today?"
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


def new_chat():
    """Start new chat"""
    st.session_state["messages"] = [{
        "role": "assistant",
        "content": "Hello! I'm your Bedrock AI assistant. How can I help you today?",
        "llm_content": "Hello! I'm your Bedrock AI assistant. How can I help you today?"
    }]
    
    if "msgs" in st.session_state:
        st.session_state.msgs.clear()
    
    if "current_llm_text" in st.session_state:
        del st.session_state["current_llm_text"]
    if "current_display_text" in st.session_state:
        del st.session_state["current_display_text"]


def display_chat_messages():
    """Display chat messages"""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def main():
    """Main function"""
    set_page_config()
    
    # Generate unique widget key
    if "widget_key" not in st.session_state:
        st.session_state["widget_key"] = str(random.randint(1, 1000000))
    
    # Render sidebar
    params = render_sidebar()
    
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
    
    # User input
    if prompt := st.chat_input("Type your message..."):
        # Store and display user message
        store_message("user", prompt)
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate and display assistant response
        with st.chat_message("assistant"):
            response = generate_response(conversation, prompt)
            store_message("assistant", response)


if __name__ == "__main__":
    main() 