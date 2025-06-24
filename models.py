# models.py
# Model configurations for Bedrock ChatBot

MODELS = {
    "Claude 3.5 Sonnet": {
        "model_id": "anthropic.claude-3-5-sonnet-20241022-v1:0",
        "temperature": 1.0,
        "top_p": 1.0,
        "top_k": 500,
        "max_tokens": 4096,
    },
    "Claude 3.7 Sonnet": {
        "model_id": "us.anthropic.claude-3-7-sonnet-20250219-v1:0",
        "temperature": 1.0,
        "top_p": 1.0,
        "top_k": 500,
        "max_tokens": 64000,
    },
    "Claude 4 Sonnet": {
        "model_id": "us.anthropic.claude-sonnet-4-20250514-v1:0",
        "temperature": 1.0,
        "top_p": 1.0,
        "top_k": 500,
        "max_tokens": 32000,
    }
} 