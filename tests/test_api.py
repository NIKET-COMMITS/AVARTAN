import os
from google import genai
from dotenv import load_dotenv

# Load your .env file
load_dotenv()

key = os.getenv("GEMINI_API_KEY")
if not key:
    print("❌ API Key not found in environment.")
    exit()

print("✅ Key loaded. Fetching allowed models...")
client = genai.Client(api_key=key)

try:
    for model in client.models.list():
        if "flash" in model.name.lower():
            print(f"- {model.name}")
except Exception as e:
    print(f"❌ Failed to list models: {e}")
    