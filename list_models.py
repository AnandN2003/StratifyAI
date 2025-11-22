"""
List all available Gemini models for your API key.
"""
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("❌ GOOGLE_API_KEY not found in .env file!")
    exit(1)

print("=" * 60)
print("Listing Available Gemini Models")
print("=" * 60)
print(f"API Key: {api_key[:10]}...{api_key[-4:]}\n")

try:
    genai.configure(api_key=api_key)
    
    print("Available models:\n")
    for model in genai.list_models():
        if 'generateContent' in model.supported_generation_methods:
            print(f"✅ {model.name}")
            print(f"   Display Name: {model.display_name}")
            print(f"   Description: {model.description[:80]}...")
            print()
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("\nTroubleshooting:")
    print("1. Verify your API key at: https://makersuite.google.com/app/apikey")
    print("2. Make sure you're using a Gemini API key, not a Google Cloud API key")
    print("3. Check if the key has been activated (may take a few minutes)")
