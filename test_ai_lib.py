import google.generativeai as genai
import os

# Get key from .env or environment
api_key = os.getenv("GEMINI_API_KEY")
model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-pro")

if not api_key:
    print("FAILED: GEMINI_API_KEY is not set in environment.")
    raise SystemExit(1)

print(f"Testing Gemini via library with model: {model_name}")
try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name)
    response = model.generate_content("Is this API working? Answer in 5 words.")
    print("SUCCESS!")
    print("Response:", response.text)
except Exception as e:
    print(f"FAILED: {str(e)}")
