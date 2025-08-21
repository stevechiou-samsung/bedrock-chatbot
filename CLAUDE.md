# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Running the Application
```bash
# Option 1: Using streamlit directly (after activating virtual environment)
streamlit run app.py

# Option 2: Using uv run (recommended)
uv run --python=3.9 --prerelease=allow streamlit run app.py

# Option 3: Using uv run with isolated environment (no venv activation needed)
uv run --isolated --python=3.9 --prerelease=allow streamlit run app.py
```
The app will be available at `http://localhost:8501`.

### Environment Setup
```bash
# Install uv (if not installed)
# On macOS
brew install uv
# OR with pip
pip install uv

# Create virtual environment with uv (using Python 3.9)
uv venv --python=3.9

# Activate the virtual environment
source .venv/bin/activate  # On macOS/Linux
# OR
.venv\Scripts\activate     # On Windows
```

### Installing Dependencies
```bash
# Install dependencies with uv (recommended)
uv pip install -r requirements.txt

# Alternative: using pip
# pip install -r requirements.txt
```

### AWS Authentication
This project requires AWS credentials via saml2aws:
```bash
# Configure profile (first time only)
saml2aws configure

# Login and get credentials (required before each session)
saml2aws login
```

## Architecture Overview

This is a Streamlit-based AWS Bedrock ChatBot with the following key components:

### Core Files
- `app.py` - Main Streamlit application with UI and chat logic
- `models.py` - Model configurations for Claude 3.7 Sonnet and Claude 4 Sonnet
- `requirements.txt` - Python dependencies
- `.streamlit/config.toml` - Streamlit theme configuration (blue primary color)

### Architecture Pattern
- **Streamlit Frontend**: Chat interface with sidebar for model/parameter configuration
- **LangChain Integration**: Uses `ChatBedrockConverse` for AWS Bedrock API calls
- **Message History**: `StreamlitChatMessageHistory` maintains conversation state
- **Model Abstraction**: `ChatModel` dataclass wraps Bedrock model configuration

### Key Features
- Multi-model support (Claude 3.7 Sonnet, Claude 4 Sonnet)
- Built-in role system with predefined prompts (Default, Translator, Writing Assistant)
- Adjustable model parameters (temperature, top-p, top-k, max_tokens)
- Streaming responses with real-time display
- Session state management for chat history

### Configuration
- Models are defined in `MODELS` dictionary in `models.py`
- Role prompts are defined in `ROLE_PROMPTS` dictionary in `app.py`
- Claude 4 Sonnet is set as the default model
- AWS region can be set via `AWS_DEFAULT_REGION` environment variable

### Authentication & Security
- Uses AWS credentials from `~/.aws/credentials` (set by saml2aws)
- No API keys stored in code or environment files
- Requires appropriate AWS Bedrock permissions and enabled models