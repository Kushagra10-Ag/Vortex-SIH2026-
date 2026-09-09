import os
import requests

API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

MODEL = "models/gemini-2.5-flash"

def generate_text(prompt: str):
    url = f"https://generativelanguage.googleapis.com/v1/{MODEL}:generateContent?key={API_KEY}"

    headers = {
        "Content-Type": "application/json"
    }

    data = {
        "contents": [
            {
                "parts": [{"text": prompt}]
            }
        ]
    }

    try:
        res = requests.post(url, headers=headers, json=data)
        res_json = res.json()

        print("🔍 RAW AI RESPONSE:", res_json)

        if "candidates" in res_json:
            parts = res_json["candidates"][0]["content"]["parts"]
            return parts[0].get("text", "")

        if "error" in res_json:
            return f"Error: {res_json['error']['message']}"

        return "No response from AI"

    except Exception as e:
        print("❌ ERROR calling Gemini:", e)
        return "AI service failed"