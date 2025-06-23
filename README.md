# 🤖 Bedrock ChatBot

A streamlined chat bot based on AWS Bedrock, built with Streamlit and LangChain.

## ✨ Features

- 🚀 **Multi-Model Support**: Supports Claude 3.5 Haiku, Claude 3.7 Sonnet, and Claude 4 Sonnet
- 🎭 **Role System**: Built-in role prompts (Translator, Writing Assistant, etc.)
- ⚙️ **Adjustable Parameters**: Support for temperature, top-p, top-k, and max_tokens tuning
- 💬 **Streaming Responses**: Real-time AI response display
- 🧠 **Reasoning Mode**: Support for Claude's reasoning capabilities
- 📱 **Responsive Design**: Modern Streamlit interface

## 🛠️ Installation & Setup

### 1. Clone the project
```bash
git clone <your-repo-url>
cd simple-bedrock-chatbot
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up environment variables
Create a `.env` file and add the following content:
```env
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_DEFAULT_REGION=us-east-1
```

### 4. Configure AWS Bedrock permissions
Ensure your AWS account has permissions to access Bedrock services and has enabled the required models.

## 🚀 Run the application

```bash
streamlit run app.py
```

The application will start at `http://localhost:8501`.

## 📁 Project Structure

```
simple-bedrock-chatbot/
├── app.py              # Main application file
├── requirements.txt    # Python dependencies
└── README.md          # Project documentation
```

## 🎯 How to Use

1. **Select Model**: Choose your desired Bedrock model from the sidebar
2. **Set Role**: Select a predefined role or customize the system prompt
3. **Adjust Parameters**: Tune model parameters as needed
4. **Start Chatting**: Enter messages in the chat box and converse with the AI
5. **New Chat**: Click the "New Chat" button to start a fresh conversation

## 🔧 Customization

### Adding New Models
Add new model configurations to the `MODELS` dictionary in `app.py`:

```python
MODELS = {
    "Your Model Name": {
        "model_id": "your.model.id",
        "temperature": 1.0,
        "top_p": 1.0,
        "top_k": 500,
        "max_tokens": 4096,
    }
}
```

### Adding New Roles
Add new role prompts to the `ROLE_PROMPTS` dictionary:

```python
ROLE_PROMPTS = {
    "New Role": "Your role description..."
}
```

## 📝 Notes

- Ensure AWS credentials are properly configured
- Bedrock services may have usage limits and costs
- Recommended to use appropriate security measures in production

## 🤝 Contributing

Issues and Pull Requests are welcome!

## 📄 License

MIT License 