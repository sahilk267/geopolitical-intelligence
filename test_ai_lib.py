import google.generativeai as genai
import os

# Get key from .env or script
api_key = "AIzaSyCCkcMLUuArs5FQSWC9mswyCXvT_v9zf7Y"
model_name = "gemini-1.5-pro"

print(f"Testing Gemini via library with model: {model_name}")
try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name)
    response = model.generate_content("Is this API working? Answer in 5 words.")
    print("SUCCESS!")
    print("Response:", response.text)
except Exception as e:
    print(f"FAILED: {str(e)}")
