import os
from google import genai
from dotenv import load_dotenv

# Load your .env file so we get the GEMINI_API_KEY
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

print("🔍 Asking Google for your available models...")
for model in client.models.list():
    # Only print models that support generating content (not just embeddings)
    if 'generateContent' in model.supported_actions:
        print(f"✅ {model.name}")