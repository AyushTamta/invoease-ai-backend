from fastapi import (
    FastAPI,
    UploadFile,
    File
)

import os
import requests
import base64
import json

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

    try:

        image_bytes = await file.read()

        base64_image = (
            base64.b64encode(
                image_bytes
            ).decode("utf-8")
        )

        prompt = """
        You are an intelligent invoice parser.

        Analyze this invoice or receipt image carefully.

        Extract:
        - store_name
        - total_amount
        - invoice_date
        - category
        - purchased_items

        Return ONLY valid JSON.

        Example:

        {
          "store_name": "Starbucks",
          "total_amount": "12.50",
          "invoice_date": "2026-05-13",
          "category": "Food & Beverage",
          "purchased_items": [
            "Latte",
            "Blueberry Muffin"
          ]
        }
        """

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={GEMINI_API_KEY}"

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
                                file.content_type,

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

        data = response.json()

        print(data)

        if "candidates" not in data:

            return {
                "error":
                "Gemini API failed",

                "full_response":
                data
            }

        text_response = data[
            "candidates"
        ][0]["content"]["parts"][0][
            "text"
        ]

        cleaned = (
            text_response
            .replace("```json", "")
            .replace("```", "")
            .strip()
        )

        parsed_json = json.loads(
            cleaned
        )

        return parsed_json

    except Exception as e:

        return {
            "error":
            "Could not parse invoice",

            "details": str(e)
        }