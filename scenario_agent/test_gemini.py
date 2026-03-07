import os
from google import genai

def get_api_key():
    with open(".env") as f:
        for line in f:
            if line.startswith("GOOGLE_API_KEY"):
                # Strip all quotes, spaces, and newline characters
                val = line.strip().split("=", 1)[1]
                val = val.strip().strip('"').strip("'")
                return val

api_key = get_api_key()
print(f"API Key Length: {len(api_key)}")
print(f"API Key ends with: {api_key[-5:]}")

client = genai.Client(api_key=api_key)
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents='Hi'
)
print("Response:", response.text)
