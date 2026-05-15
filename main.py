from fastapi import (
    FastAPI,
    UploadFile,
    File
)

import requests
import json

app = FastAPI()

OCR_API_KEY = "K82584264988957"

OPENROUTER_API_KEY = "YOUR_OPENROUTER_API_KEY"


@app.get("/")
def home():

    return {
        "message":
        "InvoEase AI Backend Running"
    }


# -------------------------
# OCR FUNCTION
# -------------------------

def run_ocr(
    image_bytes,
    filename,
    content_type,
):

    response = requests.post(
        "https://api.ocr.space/parse/image",

        files={
            "file": (
                filename,
                image_bytes,
                content_type,
            )
        },

        data={
            "apikey":
            OCR_API_KEY,

            "language":
            "eng",

            "OCREngine":
            "2",

            "scale":
            True,
        }
    )

    result = response.json()

    if (
        "ParsedResults"
        not in result
    ):

        return None

    return result[
        "ParsedResults"
    ][0]["ParsedText"]


# -------------------------
# AI EXTRACTION
# -------------------------

def extract_invoice_with_ai(
    raw_text
):

    prompt = f"""
You are an invoice AI parser.

Extract invoice information from this OCR text.

Return ONLY valid JSON.

Required fields:
- store_name
- invoice_date
- total_amount
- category
- payment_method
- tax
- items
- ai_summary

items must be array:
[
  {{
    "name": "...",
    "price": "..."
  }}
]

OCR TEXT:
{raw_text}
"""

    response = requests.post(

        url=
        "https://openrouter.ai/api/v1/chat/completions",

        headers={

            "Authorization":
            f"Bearer {OPENROUTER_API_KEY}",

            "Content-Type":
            "application/json",
        },

        json={

            "model":
            "mistralai/mistral-7b-instruct:free",

            "messages": [
                {
                    "role":
                    "user",

                    "content":
                    prompt
                }
            ]
        }
    )

    result = response.json()

    print(result)

    try:

        content = result[
            "choices"
        ][0][
            "message"
        ][
            "content"
        ]

        cleaned = (
            content
            .replace(
                "```json",
                ""
            )
            .replace(
                "```",
                ""
            )
            .strip()
        )

        return json.loads(
            cleaned
        )

    except Exception as e:

        print(e)

        return {
            "store_name":
            "Unknown",

            "invoice_date":
            "Unknown",

            "total_amount":
            "Unknown",

            "category":
            "General",

            "payment_method":
            "Unknown",

            "tax":
            "Unknown",

            "items":
            [],

            "ai_summary":
            "AI could not fully parse invoice.",

            "raw_text":
            raw_text,
        }


# -------------------------
# ASK AI
# -------------------------

def ask_invoice_ai(
    invoice,
    question,
):

    prompt = f"""
You are an intelligent invoice assistant.

INVOICE:
{json.dumps(invoice)}

QUESTION:
{question}

Answer naturally and professionally.
"""

    response = requests.post(

        url=
        "https://openrouter.ai/api/v1/chat/completions",

        headers={

            "Authorization":
            f"Bearer {OPENROUTER_API_KEY}",

            "Content-Type":
            "application/json",
        },

        json={

            "model":
            "mistralai/mistral-7b-instruct:free",

            "messages": [
                {
                    "role":
                    "user",

                    "content":
                    prompt
                }
            ]
        }
    )

    result = response.json()

    print(result)

    try:

        return result[
            "choices"
        ][0][
            "message"
        ][
            "content"
        ]

    except:

        return (
            "AI could not answer "
            "the question."
        )


# -------------------------
# SCAN INVOICE ROUTE
# -------------------------

@app.post("/scan-invoice")
async def scan_invoice(
    file: UploadFile = File(...)
):

    try:

        image_bytes = await file.read()

        raw_text = run_ocr(
            image_bytes,
            file.filename,
            file.content_type,
        )

        if not raw_text:

            return {
                "error":
                "OCR failed"
            }

        ai_invoice = (
            extract_invoice_with_ai(
                raw_text
            )
        )

        ai_invoice[
            "raw_text"
        ] = raw_text

        return ai_invoice

    except Exception as e:

        print(e)

        return {
            "error":
            str(e)
        }


# -------------------------
# ASK AI ROUTE
# -------------------------

@app.post("/ask-ai")
async def ask_ai(
    payload: dict
):

    try:

        invoice = payload[
            "invoice"
        ]

        question = payload[
            "question"
        ]

        answer = ask_invoice_ai(
            invoice,
            question,
        )

        return {
            "answer":
            answer
        }

    except Exception as e:

        return {
            "error":
            str(e)
        }