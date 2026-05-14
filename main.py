from fastapi import (
    FastAPI,
    UploadFile,
    File
)

import os
import requests
import base64

from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY"
)

@app.get("/")
def home():

    return {
        "message":
        "InvoEase AI Backend Running"
    }

@app.post("/scan-invoice")
async def scan_invoice(
    file: UploadFile = File(...)
):

    image_bytes = await file.read()

    base64_image = base64.b64encode(
        image_bytes
    ).decode("utf-8")

    prompt = """
    Analyze this invoice or receipt.

    Extract:
    - store_name
    - total_amount
    - invoice_date
    - category
    - items

    Return ONLY valid JSON.
    """

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    },
                    {
                        "inline_data": {
                            "mime_type":
                            "image/jpeg",

                            "data":
                            base64_image
                        }
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