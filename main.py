from fastapi import FastAPI

import os
import requests

from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY"
)

@app.get("/")
def home():

    return {
        "message": "InvoEase AI Backend Running"
    }

@app.get("/test-gemini")
def test_gemini():

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": "Say hello from InvoEase AI backend"
                    }
                ]
            }
        ]
    }

    response = requests.post(
        url,
        json=payload
    )

    return response.json()