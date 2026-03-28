import urllib.request
import json
import os

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("FAILED: GEMINI_API_KEY is not set in environment.")
    raise SystemExit(1)

url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
data = {
    "contents": [{
        "parts": [{"text": "Is this API key working? Answer in 5 words."}]
    }]
}

print(f"Testing Gemini API key: {api_key[:10]}...")
req = urllib.request.Request(
    url, 
    data=json.dumps(data).encode('utf-8'), 
    headers={'Content-Type': 'application/json'},
    method='POST'
)

try:
    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read().decode('utf-8'))
        if 'candidates' in result:
            print("SUCCESS: API key is working!")
            print("Response:", result['candidates'][0]['content']['parts'][0]['text'])
        else:
            print("FAILED: Unexpected response format.")
            print(json.dumps(result, indent=2))
except Exception as e:
    print(f"FAILED: Error calling Gemini API: {str(e)}")
