from fastapi import (
    FastAPI,
    UploadFile,
    File
)

import requests
import json

app = FastAPI()

# -------------------------
# API KEYS
# -------------------------

OCR_API_KEY = "K82584264988957"

OPENROUTER_API_KEY = "Ysk-or-v1-3f9f4e6c4dc330fcf0d26cb8dc46c3d11d7303a5d0823567a1cd180ab7f2251a"


# -------------------------
# HOME
# -------------------------

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

    print(result)

    if (
        "ParsedResults"
        not in result
    ):

        return None

    return result[
        "ParsedResults"
    ][0]["ParsedText"]


# -------------------------
# AI INVOICE EXTRACTION
# -------------------------

def extract_invoice_with_ai(
    raw_text
):

    prompt = f"""
You are an advanced invoice AI parser.

Extract invoice information from this OCR text.

Return ONLY valid JSON.

Required fields:
- store_name
- invoice_date
- total_amount
- category
- payment_method
- tax
- confidence_score
- items
- ai_summary

items format:
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

            "confidence_score":
            40,

            "items":
            [],

            "ai_summary":
            "AI could not fully parse invoice.",

            "raw_text":
            raw_text,
        }


# -------------------------
# ASK SINGLE INVOICE AI
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
# FINANCIAL INSIGHTS
# -------------------------

def generate_financial_insights(
    invoices
):

    prompt = f"""
You are a financial AI assistant.

Analyze these invoices and provide:
- spending patterns
- top category
- top merchant
- unusual trends
- financial insights

Keep response concise and professional.

INVOICES:
{json.dumps(invoices)}
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
            "Could not generate "
            "financial insights."
        )


# -------------------------
# FINANCE CHAT
# -------------------------

def finance_chat_ai(
    invoices,
    question,
):

    prompt = f"""
You are an intelligent personal finance AI assistant.

You help users understand:
- spending
- invoices
- merchants
- trends
- budgeting
- expense patterns

INVOICES:
{json.dumps(invoices)}

QUESTION:
{question}

Answer clearly and professionally.
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
            "Could not analyze "
            "financial data."
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


# -------------------------
# FINANCIAL INSIGHTS ROUTE
# -------------------------

@app.post("/financial-insights")
async def financial_insights(
    payload: dict
):

    try:

        invoices = payload[
            "invoices"
        ]

        insights = (
            generate_financial_insights(
                invoices
            )
        )

        return {
            "insights":
            insights
        }

    except Exception as e:

        return {
            "error":
            str(e)
        }


# -------------------------
# FINANCE CHAT ROUTE
# -------------------------

@app.post("/finance-chat")
async def finance_chat(
    payload: dict
):

    try:

        invoices = payload[
            "invoices"
        ]

        question = payload[
            "question"
        ]

        answer = finance_chat_ai(
            invoices,
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