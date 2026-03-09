import os
from google import genai
from dotenv import load_dotenv

# 1. Load your credentials from the .env file
load_dotenv()

# 2. Initialize the modern client
client = genai.Client()

# 3. List and print available models
print("--- Available Gemini Models (March 2026) ---")

# Using the new .list() method which returns Pydantic objects
for model in client.models.list():
    # In the new SDK, 'supported_actions' replaces 'supported_methods'
    # We want to find models that can 'generateContent'
    if 'generateContent' in model.supported_actions:
        print(f"Model ID: {model.name}")
        print(f"  > Display Name: {model.display_name}")
        print(f"  > Input Limit: {model.input_token_limit} tokens")
        print("-" * 30)